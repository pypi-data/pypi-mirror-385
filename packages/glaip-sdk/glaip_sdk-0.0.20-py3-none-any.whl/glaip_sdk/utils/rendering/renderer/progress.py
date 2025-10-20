"""Progress and timing utilities for the renderer package.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from time import monotonic

from glaip_sdk.utils.rendering.formatting import get_spinner_char


def get_spinner() -> str:
    """Return the current animated spinner character for visual feedback."""
    return get_spinner_char()


def _resolve_elapsed_time(
    started_at: float | None,
    server_elapsed_time: float | None,
    streaming_started_at: float | None,
) -> float | None:
    """Return the elapsed seconds using server data when available."""
    if server_elapsed_time is not None and streaming_started_at is not None:
        return server_elapsed_time
    if started_at is None:
        return None
    try:
        return monotonic() - started_at
    except Exception:
        return None


def _format_elapsed_suffix(elapsed: float) -> str:
    """Return formatting suffix for elapsed timing."""
    if elapsed >= 1:
        return f"{elapsed:.2f}s"
    elapsed_ms = int(elapsed * 1000)
    return f"{elapsed_ms}ms" if elapsed_ms > 0 else "<1ms"


def format_working_indicator(
    started_at: float | None,
    server_elapsed_time: float | None = None,
    streaming_started_at: float | None = None,
) -> str:
    """Format a working indicator with elapsed time."""
    base_message = "Working..."

    if started_at is None and (
        server_elapsed_time is None or streaming_started_at is None
    ):
        return base_message

    spinner_chip = f"{get_spinner_char()} {base_message}"
    elapsed = _resolve_elapsed_time(
        started_at, server_elapsed_time, streaming_started_at
    )
    if elapsed is None:
        return spinner_chip

    suffix = _format_elapsed_suffix(elapsed)
    return f"{spinner_chip} ({suffix})"


def format_elapsed_time(elapsed_seconds: float) -> str:
    """Format elapsed time in a human-readable format.

    Args:
        elapsed_seconds: Time in seconds

    Returns:
        Formatted time string
    """
    if elapsed_seconds >= 60:
        minutes = int(elapsed_seconds // 60)
        seconds = elapsed_seconds % 60
        return f"{minutes}m {seconds:.1f}s"
    elif elapsed_seconds >= 1:
        return f"{elapsed_seconds:.2f}s"
    else:
        ms = int(elapsed_seconds * 1000)
        return f"{ms}ms" if ms > 0 else "<1ms"


def is_delegation_tool(tool_name: str) -> bool:
    """Check if a tool name indicates delegation functionality.

    Args:
        tool_name: The name of the tool to check

    Returns:
        True if this is a delegation tool
    """
    return (
        tool_name.startswith("delegate_to_")
        or tool_name.startswith("delegate_")
        or "sub_agent" in tool_name.lower()
    )


def _delegation_tool_title(tool_name: str) -> str | None:
    """Return delegation-aware title or ``None`` when not applicable."""
    if tool_name.startswith("delegate_to_"):
        sub_agent_name = tool_name.replace("delegate_to_", "", 1)
        return f"Sub-Agent: {sub_agent_name}"
    if tool_name.startswith("delegate_"):
        sub_agent_name = tool_name.replace("delegate_", "", 1)
        return f"Sub-Agent: {sub_agent_name}"
    return None


def _strip_path_and_extension(tool_name: str) -> str:
    """Return tool name without path segments or extensions."""
    filename = tool_name.rsplit("/", 1)[-1]
    base_name = filename.split(".", 1)[0]
    return base_name


def format_tool_title(tool_name: str) -> str:
    """Format tool name for panel title display.

    Args:
        tool_name: The full tool name (may include file paths)

    Returns:
        Formatted title string suitable for panel display
    """
    # Check if this is a delegation tool
    if is_delegation_tool(tool_name):
        delegation_title = _delegation_tool_title(tool_name)
        if delegation_title:
            return delegation_title

    # For regular tools, clean up the name
    # Remove file path prefixes if present
    clean_name = _strip_path_and_extension(tool_name)

    # Convert snake_case to Title Case
    return clean_name.replace("_", " ").title()
