"""Transcript utilities package for CLI.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from glaip_sdk.cli.transcript.cache import (
    TranscriptCacheStats,
    TranscriptPayload,
    TranscriptStoreResult,
    ensure_cache_dir,
    get_transcript_cache_stats,
    latest_manifest_entry,
    manifest_path,
    resolve_manifest_entry,
    store_transcript,
    suggest_filename,
)
from glaip_sdk.cli.transcript.cache import (
    export_transcript as export_cached_transcript,
)
from glaip_sdk.cli.transcript.capture import (
    StoredTranscriptContext,
    coerce_events,
    coerce_result_text,
    compute_finished_at,
    extract_server_run_id,
    register_last_transcript,
    store_transcript_for_session,
)
from glaip_sdk.cli.transcript.export import (
    normalise_export_destination,
    resolve_manifest_for_export,
)
from glaip_sdk.cli.transcript.launcher import (
    maybe_launch_post_run_viewer,
    should_launch_post_run_viewer,
)
from glaip_sdk.cli.transcript.viewer import (
    PostRunViewer,
    ViewerContext,
    run_viewer_session,
)

__all__ = [
    "TranscriptCacheStats",
    "TranscriptPayload",
    "TranscriptStoreResult",
    "ensure_cache_dir",
    "get_transcript_cache_stats",
    "manifest_path",
    "store_transcript",
    "suggest_filename",
    "latest_manifest_entry",
    "resolve_manifest_entry",
    "export_cached_transcript",
    "StoredTranscriptContext",
    "coerce_events",
    "coerce_result_text",
    "compute_finished_at",
    "extract_server_run_id",
    "register_last_transcript",
    "store_transcript_for_session",
    "resolve_manifest_for_export",
    "normalise_export_destination",
    "maybe_launch_post_run_viewer",
    "should_launch_post_run_viewer",
    "ViewerContext",
    "PostRunViewer",
    "run_viewer_session",
]
