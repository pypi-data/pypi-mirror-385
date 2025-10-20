"""Utility helpers for checking and displaying SDK update notifications.

Author:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, Literal

import httpx
from packaging.version import InvalidVersion, Version
from rich import box
from rich.console import Console

from glaip_sdk.branding import (
    ACCENT_STYLE,
    SUCCESS_STYLE,
    WARNING_STYLE,
)
from glaip_sdk.cli.utils import command_hint, format_command_hint
from glaip_sdk.rich_components import AIPPanel

FetchLatestVersion = Callable[[], str | None]

PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"
DEFAULT_TIMEOUT = 1.5  # seconds


def _parse_version(value: str) -> Version | None:
    """Parse a version string into a `Version`, returning None on failure."""
    try:
        return Version(value)
    except InvalidVersion:
        return None


def _fetch_latest_version(package_name: str) -> str | None:
    """Fetch the latest published version from PyPI."""
    url = PYPI_JSON_URL.format(package=package_name)
    timeout = httpx.Timeout(DEFAULT_TIMEOUT)

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.get(url, headers={"Accept": "application/json"})
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError:
        return None
    except ValueError:
        return None

    info = payload.get("info") if isinstance(payload, dict) else None
    latest_version = info.get("version") if isinstance(info, dict) else None
    if isinstance(latest_version, str) and latest_version.strip():
        return latest_version.strip()
    return None


def _should_check_for_updates() -> bool:
    """Return False when update checks are explicitly disabled."""
    return os.getenv("AIP_NO_UPDATE_CHECK") is None


def _build_update_panel(
    current_version: str,
    latest_version: str,
    command_text: str,
) -> AIPPanel:
    """Create a Rich panel that prompts the user to update."""
    command_markup = format_command_hint(command_text) or command_text
    message = (
        f"[{WARNING_STYLE}]✨ Update available![/] "
        f"{current_version} → {latest_version}\n\n"
        "See the latest release notes:\n"
        f"https://pypi.org/project/glaip-sdk/{latest_version}/\n\n"
        f"[{ACCENT_STYLE}]Run[/] {command_markup} to install."
    )
    return AIPPanel(
        message,
        title=f"[{SUCCESS_STYLE}]AIP SDK Update[/]",
        box=box.ROUNDED,
        padding=(0, 3),
        expand=False,
    )


def maybe_notify_update(
    current_version: str,
    *,
    package_name: str = "glaip-sdk",
    console: Console | None = None,
    fetch_latest_version: FetchLatestVersion | None = None,
    ctx: Any | None = None,
    slash_command: str | None = None,
    style: Literal["panel", "inline"] = "panel",
) -> None:
    """Check PyPI for a newer version and display a prompt if one exists.

    This function deliberately swallows network errors to avoid impacting CLI
    startup time when offline or when PyPI is unavailable.
    """
    if not _should_check_for_updates():
        return

    fetcher = fetch_latest_version or (lambda: _fetch_latest_version(package_name))
    latest_version = fetcher()
    if not latest_version:
        return

    current = _parse_version(current_version)
    latest = _parse_version(latest_version)
    if current is None or latest is None or latest <= current:
        return

    command_text = command_hint("update", slash_command=slash_command, ctx=ctx)
    if command_text is None:
        return

    active_console = console or Console()
    if style == "inline":
        command_markup = format_command_hint(command_text) or command_text
        message = (
            f"[{WARNING_STYLE}]✨ Update[/] "
            f"{current_version} → {latest_version} "
            f"- {command_markup}"
        )
        active_console.print(message)
        return

    panel = _build_update_panel(current_version, latest_version, command_text)
    active_console.print(panel)


__all__ = ["maybe_notify_update"]
