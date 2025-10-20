"""Interactive viewer for post-run transcript exploration.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

try:  # pragma: no cover - optional dependency
    import questionary
    from questionary import Choice
except Exception:  # pragma: no cover - optional dependency
    questionary = None  # type: ignore[assignment]
    Choice = None  # type: ignore[assignment]

from glaip_sdk.cli.transcript.cache import suggest_filename
from glaip_sdk.icons import ICON_DELEGATE, ICON_TOOL_STEP
from glaip_sdk.rich_components import AIPPanel
from glaip_sdk.utils.rendering.renderer.debug import render_debug_event
from glaip_sdk.utils.rendering.renderer.panels import create_final_panel
from glaip_sdk.utils.rendering.renderer.progress import (
    format_elapsed_time,
    is_delegation_tool,
)

EXPORT_CANCELLED_MESSAGE = "[dim]Export cancelled.[/dim]"


@dataclass(slots=True)
class ViewerContext:
    """Runtime context for the viewer session."""

    manifest_entry: dict[str, Any]
    events: list[dict[str, Any]]
    default_output: str
    final_output: str
    stream_started_at: float | None
    meta: dict[str, Any]


class PostRunViewer:  # pragma: no cover - interactive flows are not unit tested
    """Simple interactive session for inspecting agent run transcripts."""

    def __init__(
        self,
        console: Console,
        ctx: ViewerContext,
        export_callback: Callable[[Path], Path],
    ) -> None:
        """Initialize viewer state for a captured transcript."""
        self.console = console
        self.ctx = ctx
        self._export_callback = export_callback
        self._view_mode = "default"

    def run(self) -> None:
        """Enter the interactive loop."""
        if not self.ctx.events and not (
            self.ctx.default_output or self.ctx.final_output
        ):
            return
        if self._view_mode == "transcript":
            self._render()
        self._print_command_hint()
        self._fallback_loop()

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def _render(self) -> None:
        try:
            if self.console.is_terminal:
                self.console.clear()
        except Exception:  # pragma: no cover - platform quirks
            pass

        header = (
            f"Agent transcript viewer · run {self.ctx.manifest_entry.get('run_id')}"
        )
        agent_label = self.ctx.manifest_entry.get("agent_name") or "unknown agent"
        model = self.ctx.manifest_entry.get("model") or self.ctx.meta.get("model")
        agent_id = self.ctx.manifest_entry.get("agent_id")
        subtitle_parts = [agent_label]
        if model:
            subtitle_parts.append(str(model))
        if agent_id:
            subtitle_parts.append(agent_id)

        if self._view_mode == "transcript":
            self.console.rule(header)
            if subtitle_parts:
                self.console.print(f"[dim]{' · '.join(subtitle_parts)}[/]")
            self.console.print()

        query = self._get_user_query()

        if self._view_mode == "default":
            self._render_default_view(query)
        else:
            self._render_transcript_view(query)

    def _render_default_view(self, query: str | None) -> None:
        if query:
            self._render_user_query(query)
        self._render_steps_summary()
        self._render_final_panel()

    def _render_transcript_view(self, query: str | None) -> None:
        if not self.ctx.events:
            self.console.print("[dim]No SSE events were captured for this run.[/dim]")
            return

        if query:
            self._render_user_query(query)

        self._render_steps_summary()
        self._render_final_panel()

        self.console.print("[bold]Transcript Events[/bold]")
        self.console.print(
            "[dim]────────────────────────────────────────────────────────[/dim]"
        )

        base_received_ts: datetime | None = None
        for event in self.ctx.events:
            received_ts = self._parse_received_timestamp(event)
            if base_received_ts is None and received_ts is not None:
                base_received_ts = received_ts
            render_debug_event(
                event,
                self.console,
                received_ts=received_ts,
                baseline_ts=base_received_ts,
            )
        self.console.print()

    def _render_final_panel(self) -> None:
        content = (
            self.ctx.final_output
            or self.ctx.default_output
            or "No response content captured."
        )
        title = "Final Result"
        duration_text = self._extract_final_duration()
        if duration_text:
            title += f" · {duration_text}"
        panel = create_final_panel(content, title=title, theme="dark")
        self.console.print(panel)
        self.console.print()

    # ------------------------------------------------------------------
    # Interaction loops
    # ------------------------------------------------------------------
    def _fallback_loop(self) -> None:
        while True:
            try:
                ch = click.getchar()
            except (EOFError, KeyboardInterrupt):
                break

            if ch in {"\r", "\n"}:
                break

            if ch == "\x14" or ch.lower() == "t":  # Ctrl+T or t
                self.toggle_view()
                continue

            if ch.lower() == "e":
                self.export_transcript()
                self._print_command_hint()
            else:
                continue

    def _handle_command(self, raw: str) -> bool:
        lowered = raw.lower()
        if lowered in {"exit", "quit", "q"}:
            return True
        if lowered in {"export", "e"}:
            self.export_transcript()
            self._print_command_hint()
            return False
        self.console.print("[dim]Commands: export, exit.[/dim]")
        return False

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def toggle_view(self) -> None:
        """Switch between default result view and verbose transcript."""
        self._view_mode = "transcript" if self._view_mode == "default" else "default"
        self._render()
        self._print_command_hint()

    def export_transcript(self) -> None:
        """Prompt user for a destination and export the cached transcript."""
        entry = self.ctx.manifest_entry
        default_name = suggest_filename(entry)
        default_path = Path.cwd() / default_name

        def _display_path(path: Path) -> str:
            raw = str(path)
            return raw if len(raw) <= 80 else f"…{raw[-77:]}"

        selection = self._prompt_export_choice(
            default_path, _display_path(default_path)
        )
        if selection is None:
            self._legacy_export_prompt(default_path, _display_path)
            return

        action, _ = selection
        if action == "cancel":
            self.console.print(EXPORT_CANCELLED_MESSAGE)
            return

        if action == "default":
            destination = default_path
        else:
            destination = self._prompt_custom_destination()
            if destination is None:
                self.console.print(EXPORT_CANCELLED_MESSAGE)
                return

        try:
            target = self._export_callback(destination)
            self.console.print(f"[green]Transcript exported to {target}[/green]")
        except FileNotFoundError as exc:
            self.console.print(f"[red]{exc}[/red]")
        except Exception as exc:  # pragma: no cover - unexpected IO failures
            self.console.print(f"[red]Failed to export transcript: {exc}[/red]")

    def _prompt_export_choice(
        self, default_path: Path, default_display: str
    ) -> tuple[str, Any] | None:
        """Render interactive export menu with numeric shortcuts."""
        if not self.console.is_terminal or questionary is None or Choice is None:
            return None

        try:
            answer = questionary.select(
                "Export transcript",
                choices=[
                    Choice(
                        title=f"Save to default ({default_display})",
                        value=("default", default_path),
                        shortcut_key="1",
                    ),
                    Choice(
                        title="Choose a different path",
                        value=("custom", None),
                        shortcut_key="2",
                    ),
                    Choice(
                        title="Cancel",
                        value=("cancel", None),
                        shortcut_key="3",
                    ),
                ],
                use_shortcuts=True,
                instruction="Press 1-3 (or arrows) then Enter.",
            ).ask()
        except Exception:
            return None

        if answer is None:
            return ("cancel", None)
        return answer

    def _prompt_custom_destination(self) -> Path | None:
        """Prompt for custom export path with filesystem completion."""
        if not self.console.is_terminal:
            return None

        try:
            response = questionary.path(
                "Destination path (Tab to autocomplete):",
                default="",
                only_directories=False,
            ).ask()
        except Exception:
            return None

        if not response:
            return None

        candidate = Path(response.strip()).expanduser()
        if not candidate.is_absolute():
            candidate = Path.cwd() / candidate
        return candidate

    def _legacy_export_prompt(
        self, default_path: Path, formatter: Callable[[Path], str]
    ) -> None:
        """Fallback export workflow when interactive UI is unavailable."""
        self.console.print("[dim]Export options (fallback mode)[/dim]")
        self.console.print(f"  1. Save to default ({formatter(default_path)})")
        self.console.print("  2. Choose a different path")
        self.console.print("  3. Cancel")

        try:
            choice = click.prompt(
                "Select option",
                type=click.Choice(["1", "2", "3"], case_sensitive=False),
                default="1",
                show_choices=False,
            )
        except (EOFError, KeyboardInterrupt):
            self.console.print(EXPORT_CANCELLED_MESSAGE)
            return

        if choice == "3":
            self.console.print(EXPORT_CANCELLED_MESSAGE)
            return

        if choice == "1":
            destination = default_path
        else:
            try:
                destination_str = click.prompt("Enter destination path", default="")
            except (EOFError, KeyboardInterrupt):
                self.console.print(EXPORT_CANCELLED_MESSAGE)
                return
            if not destination_str.strip():
                self.console.print(EXPORT_CANCELLED_MESSAGE)
                return
            destination = Path(destination_str.strip()).expanduser()
            if not destination.is_absolute():
                destination = Path.cwd() / destination

        try:
            target = self._export_callback(destination)
            self.console.print(f"[green]Transcript exported to {target}[/green]")
        except FileNotFoundError as exc:
            self.console.print(f"[red]{exc}[/red]")
        except Exception as exc:  # pragma: no cover - unexpected IO failures
            self.console.print(f"[red]Failed to export transcript: {exc}[/red]")

    def _print_command_hint(self) -> None:
        self.console.print(
            "[dim]Ctrl+T to toggle transcript · type `e` to export · press Enter to exit[/dim]"
        )
        self.console.print()

    def _get_user_query(self) -> str | None:
        meta = self.ctx.meta or {}
        manifest = self.ctx.manifest_entry or {}
        return (
            meta.get("input_message")
            or meta.get("query")
            or meta.get("message")
            or manifest.get("input_message")
        )

    def _render_user_query(self, query: str) -> None:
        panel = AIPPanel(
            Markdown(f"Query: {query}"),
            title="User Request",
            border_style="#d97706",
        )
        self.console.print(panel)
        self.console.print()

    def _render_steps_summary(self) -> None:
        panel_content = self._format_steps_summary(self._build_step_summary())
        panel = AIPPanel(
            Text(panel_content, style="dim"),
            title="Steps",
            border_style="blue",
        )
        self.console.print(panel)
        self.console.print()

    @staticmethod
    def _format_steps_summary(steps: list[dict[str, Any]]) -> str:
        if not steps:
            return "  No steps yet"

        lines = []
        for step in steps:
            icon = ICON_DELEGATE if step.get("is_delegate") else ICON_TOOL_STEP
            duration = step.get("duration")
            duration_str = f" [{duration}]" if duration else ""
            status = " ✓" if step.get("finished") else ""
            title = step.get("title") or step.get("name") or "Step"
            lines.append(f"  {icon} {title}{duration_str}{status}")
        return "\n".join(lines)

    @staticmethod
    def _extract_event_time(event: dict[str, Any]) -> float | None:
        metadata = event.get("metadata") or {}
        time_value = metadata.get("time")
        try:
            if isinstance(time_value, (int, float)):
                return float(time_value)
        except Exception:
            return None
        return None

    @staticmethod
    def _parse_received_timestamp(event: dict[str, Any]) -> datetime | None:
        value = event.get("received_at")
        if not value:
            return None
        if isinstance(value, str):
            try:
                normalised = value.replace("Z", "+00:00")
                parsed = datetime.fromisoformat(normalised)
            except ValueError:
                return None
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        return None

    def _extract_final_duration(self) -> str | None:
        for event in self.ctx.events:
            metadata = event.get("metadata") or {}
            if metadata.get("kind") == "final_response":
                time_value = metadata.get("time")
                try:
                    if isinstance(time_value, (int, float)):
                        return f"{float(time_value):.2f}s"
                except Exception:
                    return None
        return None

    def _build_step_summary(self) -> list[dict[str, Any]]:
        stored = self.ctx.meta.get("transcript_steps")
        if isinstance(stored, list) and stored:
            return [
                {
                    "title": entry.get("display_name") or entry.get("name") or "Step",
                    "is_delegate": entry.get("kind") == "delegate",
                    "finished": entry.get("status") == "finished",
                    "duration": self._format_duration_from_ms(entry.get("duration_ms")),
                }
                for entry in stored
            ]

        steps: dict[str, dict[str, Any]] = {}
        order: list[str] = []

        for event in self.ctx.events:
            metadata = event.get("metadata") or {}
            if not self._is_step_event(metadata):
                continue

            for name, info in self._iter_step_candidates(event, metadata):
                step = self._ensure_step_entry(steps, order, name)
                self._apply_step_update(step, metadata, info, event)

        return [steps[name] for name in order]

    @staticmethod
    def _format_duration_from_ms(value: Any) -> str | None:
        try:
            if value is None:
                return None
            duration_ms = float(value)
        except Exception:
            return None

        if duration_ms <= 0:
            return "<1ms"
        if duration_ms < 1000:
            return f"{int(duration_ms)}ms"
        return f"{duration_ms / 1000:.2f}s"

    @staticmethod
    def _is_step_event(metadata: dict[str, Any]) -> bool:
        kind = metadata.get("kind")
        return kind in {"agent_step", "agent_thinking_step"}

    def _iter_step_candidates(
        self, event: dict[str, Any], metadata: dict[str, Any]
    ) -> Iterable[tuple[str, dict[str, Any]]]:
        tool_info = metadata.get("tool_info") or {}

        yielded = False
        for candidate in self._iter_tool_call_candidates(tool_info):
            yielded = True
            yield candidate

        if yielded:
            return

        direct_tool = self._extract_direct_tool(tool_info)
        if direct_tool is not None:
            yield direct_tool
            return

        completed = self._extract_completed_name(event)
        if completed is not None:
            yield completed, {}

    @staticmethod
    def _iter_tool_call_candidates(
        tool_info: dict[str, Any],
    ) -> Iterable[tuple[str, dict[str, Any]]]:
        tool_calls = tool_info.get("tool_calls")
        if isinstance(tool_calls, list):
            for call in tool_calls:
                name = call.get("name")
                if name:
                    yield name, call

    @staticmethod
    def _extract_direct_tool(
        tool_info: dict[str, Any],
    ) -> tuple[str, dict[str, Any]] | None:
        if isinstance(tool_info, dict):
            name = tool_info.get("name")
            if name:
                return name, tool_info
        return None

    @staticmethod
    def _extract_completed_name(event: dict[str, Any]) -> str | None:
        content = event.get("content") or ""
        if isinstance(content, str) and content.startswith("Completed "):
            name = content.replace("Completed ", "").strip()
            if name:
                return name
        return None

    def _ensure_step_entry(
        self,
        steps: dict[str, dict[str, Any]],
        order: list[str],
        name: str,
    ) -> dict[str, Any]:
        if name not in steps:
            steps[name] = {
                "name": name,
                "title": name,
                "is_delegate": is_delegation_tool(name),
                "duration": None,
                "started_at": None,
                "finished": False,
            }
            order.append(name)
        return steps[name]

    def _apply_step_update(
        self,
        step: dict[str, Any],
        metadata: dict[str, Any],
        info: dict[str, Any],
        event: dict[str, Any],
    ) -> None:
        status = metadata.get("status")
        event_time = metadata.get("time")

        if (
            status == "running"
            and step.get("started_at") is None
            and isinstance(event_time, (int, float))
        ):
            try:
                step["started_at"] = float(event_time)
            except Exception:
                step["started_at"] = None

        if self._is_step_finished(metadata, event):
            step["finished"] = True

        duration = self._compute_step_duration(step, info, metadata)
        if duration is not None:
            step["duration"] = duration

    @staticmethod
    def _is_step_finished(metadata: dict[str, Any], event: dict[str, Any]) -> bool:
        status = metadata.get("status")
        return status == "finished" or bool(event.get("final"))

    def _compute_step_duration(
        self, step: dict[str, Any], info: dict[str, Any], metadata: dict[str, Any]
    ) -> str | None:
        """Calculate a formatted duration string for a step if possible."""
        event_time = metadata.get("time")
        started_at = step.get("started_at")
        duration_value: float | None = None

        if isinstance(event_time, (int, float)) and isinstance(
            started_at, (int, float)
        ):
            try:
                delta = float(event_time) - float(started_at)
                if delta >= 0:
                    duration_value = delta
            except Exception:
                duration_value = None

        if duration_value is None:
            exec_time = info.get("execution_time")
            if isinstance(exec_time, (int, float)):
                duration_value = float(exec_time)

        if duration_value is None:
            return None

        try:
            return format_elapsed_time(duration_value)
        except Exception:
            return None


def run_viewer_session(
    console: Console,
    ctx: ViewerContext,
    export_callback: Callable[[Path], Path],
) -> None:
    """Entry point for creating and running the post-run viewer."""
    viewer = PostRunViewer(console, ctx, export_callback)
    viewer.run()
