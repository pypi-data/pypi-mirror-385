"""Helpers for storing and exporting agent run transcripts.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import json
import os
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_CACHE_ROOT = Path(
    os.getenv(
        "AIP_TRANSCRIPT_CACHE_DIR",
        Path.home() / ".config" / "glaip-sdk" / "transcripts",
    )
)
MANIFEST_FILENAME = "manifest.jsonl"


@dataclass(slots=True)
class TranscriptPayload:
    """Data bundle representing a captured agent run."""

    events: list[dict[str, Any]]
    default_output: str
    final_output: str
    agent_id: str | None
    agent_name: str | None
    model: str | None
    server_run_id: str | None
    started_at: float | None
    finished_at: float | None
    created_at: datetime
    source: str
    meta: dict[str, Any]
    run_id: str


@dataclass(slots=True)
class TranscriptStoreResult:
    """Result of writing a transcript to the local cache."""

    path: Path
    manifest_entry: dict[str, Any]
    pruned_entries: list[dict[str, Any]]


@dataclass(slots=True)
class TranscriptCacheStats:
    """Lightweight usage snapshot for the transcript cache."""

    cache_dir: Path
    entry_count: int
    total_bytes: int


def ensure_cache_dir(cache_dir: Path | None = None) -> Path:
    """Ensure the cache directory exists and return it."""
    directory = cache_dir or DEFAULT_CACHE_ROOT
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        return _fallback_cache_dir()

    if not os.access(directory, os.W_OK):
        return _fallback_cache_dir()

    return directory


def _fallback_cache_dir() -> Path:
    """Return a writable fallback cache directory under the current working tree."""
    fallback = Path.cwd() / ".glaip-transcripts"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def manifest_path(cache_dir: Path | None = None) -> Path:
    """Return the manifest file path."""
    return ensure_cache_dir(cache_dir) / MANIFEST_FILENAME


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def _load_manifest_entries(cache_dir: Path | None = None) -> list[dict[str, Any]]:
    path = manifest_path(cache_dir)
    entries: list[dict[str, Any]] = []
    if not path.exists():
        return entries

    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                entries.append(entry)
            except json.JSONDecodeError:
                continue
    return entries


def _json_default(value: Any) -> Any:
    """Ensure non-serialisable values degrade to readable strings."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Path):
        return str(value)
    return repr(value)


def _write_manifest(
    entries: Iterable[dict[str, Any]], cache_dir: Path | None = None
) -> None:
    path = manifest_path(cache_dir)
    with path.open("w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry, ensure_ascii=False, default=_json_default))
            fh.write("\n")


def store_transcript(
    payload: TranscriptPayload,
    *,
    cache_dir: Path | None = None,
) -> TranscriptStoreResult:
    """Persist a transcript to disk and update the manifest."""
    directory = ensure_cache_dir(cache_dir)
    filename = f"run-{payload.run_id}.jsonl"
    transcript_path = directory / filename

    meta_line = {
        "type": "meta",
        "run_id": payload.run_id,
        "agent_id": payload.agent_id,
        "agent_name": payload.agent_name,
        "model": payload.model,
        "created_at": payload.created_at.isoformat(),
        "default_output": payload.default_output,
        "final_output": payload.final_output,
        "server_run_id": payload.server_run_id,
        "started_at": payload.started_at,
        "finished_at": payload.finished_at,
        "meta": payload.meta,
        "source": payload.source,
    }

    def _write_transcript(path: Path) -> None:
        with path.open("w", encoding="utf-8") as fh:
            fh.write(json.dumps(meta_line, ensure_ascii=False, default=_json_default))
            fh.write("\n")
            for event in payload.events:
                fh.write(
                    json.dumps(
                        {"type": "event", "event": event},
                        ensure_ascii=False,
                        default=_json_default,
                    )
                )
                fh.write("\n")

    try:
        _write_transcript(transcript_path)
    except PermissionError:
        directory = _fallback_cache_dir()
        transcript_path = directory / filename
        _write_transcript(transcript_path)

    size_bytes = transcript_path.stat().st_size
    manifest_entry = {
        "run_id": payload.run_id,
        "agent_id": payload.agent_id,
        "agent_name": payload.agent_name,
        "created_at": payload.created_at.isoformat(),
        "cache_path": str(transcript_path),
        "size_bytes": size_bytes,
        "retained": True,
        "source": payload.source,
        "server_run_id": payload.server_run_id,
    }

    existing_entries = _load_manifest_entries(directory)
    existing_entries.append(manifest_entry)
    _write_manifest(existing_entries, directory)

    return TranscriptStoreResult(
        path=transcript_path,
        manifest_entry=manifest_entry,
        pruned_entries=[],
    )


def latest_manifest_entry(cache_dir: Path | None = None) -> dict[str, Any] | None:
    """Return the most recent manifest entry, if any."""
    entries = _load_manifest_entries(cache_dir)
    if not entries:
        return None
    return max(
        entries,
        key=lambda e: _parse_iso(e.get("created_at"))
        or datetime.min.replace(tzinfo=timezone.utc),
    )


def resolve_manifest_entry(
    run_id: str,
    cache_dir: Path | None = None,
) -> dict[str, Any] | None:
    """Find a manifest entry by run id."""
    entries = _load_manifest_entries(cache_dir)
    for entry in entries:
        if entry.get("run_id") == run_id:
            return entry
    return None


def export_transcript(
    *,
    destination: Path,
    run_id: str | None = None,
    cache_dir: Path | None = None,
) -> Path:
    """Copy a cached transcript to the requested destination path."""
    directory = ensure_cache_dir(cache_dir)
    entry = (
        resolve_manifest_entry(run_id, directory)
        if run_id
        else latest_manifest_entry(directory)
    )
    if entry is None:
        raise FileNotFoundError("No cached transcripts available for export.")

    cache_path = entry.get("cache_path")
    if not cache_path:
        raise FileNotFoundError("Cached transcript path missing from manifest.")

    cache_file = Path(cache_path)
    if not cache_file.exists():
        raise FileNotFoundError(f"Cached transcript file not found: {cache_file}")

    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        lines = cache_file.read_text(encoding="utf-8").splitlines()
        records = [json.loads(line) for line in lines if line.strip()]
    except json.JSONDecodeError as exc:
        raise FileNotFoundError(
            f"Cached transcript file is corrupted: {cache_file}"
        ) from exc

    with destination.open("w", encoding="utf-8") as fh:
        for idx, record in enumerate(records):
            json.dump(record, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
            if idx != len(records) - 1:
                fh.write("\n")

    return destination


def suggest_filename(entry: dict[str, Any] | None = None) -> str:
    """Return a friendly filename suggestion for exporting a transcript."""
    run_id = entry.get("run_id") if entry else uuid.uuid4().hex
    created_at = (
        entry.get("created_at") if entry else datetime.now(timezone.utc).isoformat()
    )
    timestamp = (
        created_at.replace(":", "").replace("-", "").replace("T", "_").split("+")[0]
    )
    return f"aip-run-{timestamp}-{run_id}.jsonl"


def build_payload(
    *,
    events: list[dict[str, Any]],
    renderer_output: str,
    final_output: str,
    agent_id: str | None,
    agent_name: str | None,
    model: str | None,
    server_run_id: str | None,
    started_at: float | None,
    finished_at: float | None,
    meta: dict[str, Any],
    source: str,
) -> TranscriptPayload:
    """Factory helper to prepare payload objects consistently."""
    return TranscriptPayload(
        events=events,
        default_output=renderer_output,
        final_output=final_output,
        agent_id=agent_id,
        agent_name=agent_name,
        model=model,
        server_run_id=server_run_id,
        started_at=started_at,
        finished_at=finished_at,
        created_at=datetime.now(timezone.utc),
        source=source,
        meta=meta,
        run_id=uuid.uuid4().hex,
    )


def get_transcript_cache_stats(
    cache_dir: Path | None = None,
) -> TranscriptCacheStats:
    """Return basic usage information about the transcript cache."""
    directory = ensure_cache_dir(cache_dir)
    entries = _load_manifest_entries(directory)

    total_bytes = 0
    for entry in entries:
        try:
            total_bytes += int(entry.get("size_bytes") or 0)
        except Exception:
            continue

    return TranscriptCacheStats(
        cache_dir=directory,
        entry_count=len(entries),
        total_bytes=total_bytes,
    )
