"""SlashSession orchestrates the interactive command palette.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import importlib
import os
import shlex
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path
from typing import Any

import click
from rich.console import Console, Group
from rich.text import Text

from glaip_sdk.branding import (
    ACCENT_STYLE,
    ERROR_STYLE,
    HINT_COMMAND_STYLE,
    HINT_DESCRIPTION_COLOR,
    HINT_PREFIX_STYLE,
    INFO_STYLE,
    PRIMARY,
    SECONDARY_LIGHT,
    SUCCESS_STYLE,
    WARNING_STYLE,
    AIPBranding,
)
from glaip_sdk.cli.commands.configure import configure_command, load_config
from glaip_sdk.cli.commands.update import update_command
from glaip_sdk.cli.slash.agent_session import AgentRunSession
from glaip_sdk.cli.slash.prompt import (
    FormattedText,
    PromptSession,
    Style,
    patch_stdout,
    setup_prompt_toolkit,
    to_formatted_text,
)
from glaip_sdk.cli.transcript import (
    export_cached_transcript,
    normalise_export_destination,
    resolve_manifest_for_export,
    suggest_filename,
)
from glaip_sdk.cli.transcript.viewer import ViewerContext, run_viewer_session
from glaip_sdk.cli.update_notifier import maybe_notify_update
from glaip_sdk.cli.utils import (
    _fuzzy_pick_for_resources,
    command_hint,
    format_command_hint,
    get_client,
)
from glaip_sdk.rich_components import AIPGrid, AIPPanel, AIPTable

SlashHandler = Callable[["SlashSession", list[str], bool], bool]


@dataclass(frozen=True)
class SlashCommand:
    """Metadata for a slash command entry."""

    name: str
    help: str
    handler: SlashHandler
    aliases: tuple[str, ...] = ()


class SlashSession:
    """Interactive command palette controller."""

    def __init__(self, ctx: click.Context, *, console: Console | None = None) -> None:
        """Initialize the slash session.

        Args:
            ctx: The Click context
            console: Optional console instance, creates default if None
        """
        self.ctx = ctx
        self.console = console or Console()
        self._commands: dict[str, SlashCommand] = {}
        self._unique_commands: dict[str, SlashCommand] = {}
        self._contextual_commands: dict[str, str] = {}
        self._contextual_include_global: bool = True
        self._client: Any | None = None
        self.recent_agents: list[dict[str, str]] = []
        self.last_run_input: str | None = None
        self._should_exit = False
        self._interactive = bool(sys.stdin.isatty() and sys.stdout.isatty())
        self._config_cache: dict[str, Any] | None = None
        self._welcome_rendered = False
        self._active_renderer: Any | None = None
        self._current_agent: Any | None = None

        self._home_placeholder = "Start with / to browse commands"

        # Command string constants to avoid duplication
        self.STATUS_COMMAND = "/status"
        self.AGENTS_COMMAND = "/agents"

        self._ptk_session: PromptSession | None = None
        self._ptk_style: Style | None = None
        self._setup_prompt_toolkit()
        self._register_defaults()
        self._branding = AIPBranding.create_from_sdk()
        self._suppress_login_layout = False
        self._default_actions_shown = False
        self._update_prompt_shown = False
        self._update_notifier = maybe_notify_update
        self._home_hint_shown = False
        self._agent_transcript_ready: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Session orchestration
    # ------------------------------------------------------------------

    def _setup_prompt_toolkit(self) -> None:
        session, style = setup_prompt_toolkit(self, interactive=self._interactive)
        self._ptk_session = session
        self._ptk_style = style

    def run(self, initial_commands: Iterable[str] | None = None) -> None:
        """Start the command palette session loop."""
        ctx_obj = self.ctx.obj if isinstance(self.ctx.obj, dict) else None
        previous_session = None
        if ctx_obj is not None:
            previous_session = ctx_obj.get("_slash_session")
            ctx_obj["_slash_session"] = self

        try:
            if not self._interactive:
                self._run_non_interactive(initial_commands)
                return

            if not self._ensure_configuration():
                return

            self._maybe_show_update_prompt()
            self._render_header(initial=not self._welcome_rendered)
            if not self._default_actions_shown:
                self._show_default_quick_actions()
            self._run_interactive_loop()
        finally:
            if ctx_obj is not None:
                if previous_session is None:
                    ctx_obj.pop("_slash_session", None)
                else:
                    ctx_obj["_slash_session"] = previous_session

    def _run_interactive_loop(self) -> None:
        """Run the main interactive command loop."""
        while not self._should_exit:
            try:
                raw = self._prompt("› ", placeholder=self._home_placeholder)
            except EOFError:
                self.console.print("\n👋 Closing the command palette.")
                break
            except KeyboardInterrupt:
                self.console.print("")
                continue

            if not self._process_command(raw):
                break

    def _process_command(self, raw: str) -> bool:
        """Process a single command input. Returns False if should exit."""
        raw = raw.strip()
        if not raw:
            return True

        if raw == "/":
            self._render_home_hint()
            self._cmd_help([], invoked_from_agent=False)
            return True

        if not raw.startswith("/"):
            self.console.print(
                f"[{INFO_STYLE}]Hint:[/] start commands with `/`. Try `/agents` to select an agent."
            )
            return True

        return self.handle_command(raw)

    def _run_non_interactive(
        self, initial_commands: Iterable[str] | None = None
    ) -> None:
        """Run slash commands in non-interactive mode."""
        commands = list(initial_commands or [])
        if not commands:
            commands = [line.strip() for line in sys.stdin if line.strip()]

        for raw in commands:
            if not raw.startswith("/"):
                continue
            if not self.handle_command(raw):
                break

    def _ensure_configuration(self) -> bool:
        """Ensure the CLI has both API URL and credentials before continuing."""
        while not self._configuration_ready():
            self.console.print(
                f"[{WARNING_STYLE}]Configuration required.[/] Launching `/login` wizard..."
            )
            self._suppress_login_layout = True
            try:
                self._cmd_login([], False)
            except KeyboardInterrupt:
                self.console.print(
                    f"[{ERROR_STYLE}]Configuration aborted. Closing the command palette.[/]"
                )
                return False
            finally:
                self._suppress_login_layout = False

        return True

    def _configuration_ready(self) -> bool:
        """Check whether API URL and credentials are available."""
        config = self._load_config()
        api_url = self._get_api_url(config)
        if not api_url:
            return False

        api_key: str | None = None
        if isinstance(self.ctx.obj, dict):
            api_key = self.ctx.obj.get("api_key")

        api_key = api_key or config.get("api_key") or os.getenv("AIP_API_KEY")
        return bool(api_key)

    def handle_command(self, raw: str, *, invoked_from_agent: bool = False) -> bool:
        """Parse and execute a single slash command string."""
        verb, args = self._parse(raw)
        if not verb:
            self.console.print(f"[{ERROR_STYLE}]Unrecognised command[/]")
            return True

        command = self._commands.get(verb)
        if command is None:
            suggestion = self._suggest(verb)
            if suggestion:
                self.console.print(
                    f"[{WARNING_STYLE}]Unknown command '{verb}'. Did you mean '/{suggestion}'?[/]"
                )
            else:
                help_command = "/help"
                help_hint = format_command_hint(help_command) or help_command
                self.console.print(
                    f"[{WARNING_STYLE}]Unknown command '{verb}'. Type {help_hint} for a list of options.[/]"
                )
            return True

        should_continue = command.handler(self, args, invoked_from_agent)
        if not should_continue:
            self._should_exit = True
            return False
        return True

    # ------------------------------------------------------------------
    # Command handlers
    # ------------------------------------------------------------------
    def _cmd_help(self, _args: list[str], invoked_from_agent: bool) -> bool:
        try:
            if invoked_from_agent:
                self._render_agent_help()
            else:
                self._render_global_help()
        except Exception as exc:  # pragma: no cover - UI/display errors
            self.console.print(f"[{ERROR_STYLE}]Error displaying help: {exc}[/]")
            return False

        return True

    def _render_agent_help(self) -> None:
        table = AIPTable()
        table.add_column("Input", style=HINT_COMMAND_STYLE, no_wrap=True)
        table.add_column("What happens", style=HINT_DESCRIPTION_COLOR)
        table.add_row("<message>", "Run the active agent once with that prompt.")
        table.add_row("/details", "Show the full agent export and metadata.")
        table.add_row(self.STATUS_COMMAND, "Display connection status without leaving.")
        table.add_row("/export [path]", "Export the latest agent transcript as JSONL.")
        table.add_row("/exit (/back)", "Return to the slash home screen.")
        table.add_row("/help (/?)", "Display this context-aware menu.")

        panel_items = [table]
        if self.last_run_input:
            panel_items.append(
                Text.from_markup(f"[dim]Last run input:[/] {self.last_run_input}")
            )
        panel_items.append(
            Text.from_markup(
                "[dim]Global commands (e.g. `/login`, `/status`) remain available inside the agent prompt.[/dim]"
            )
        )

        self.console.print(
            AIPPanel(
                Group(*panel_items),
                title="Agent Context",
                border_style=PRIMARY,
            )
        )

    def _render_global_help(self) -> None:
        table = AIPTable()
        table.add_column("Command", style=HINT_COMMAND_STYLE, no_wrap=True)
        table.add_column("Description", style=HINT_DESCRIPTION_COLOR)

        for cmd in sorted(self._unique_commands.values(), key=lambda c: c.name):
            aliases = ", ".join(f"/{alias}" for alias in cmd.aliases if alias)
            verb = f"/{cmd.name}"
            if aliases:
                verb = f"{verb} ({aliases})"
            table.add_row(verb, cmd.help)

        tip = Text.from_markup(
            f"[{HINT_PREFIX_STYLE}]Tip:[/] {format_command_hint(self.AGENTS_COMMAND) or self.AGENTS_COMMAND} lets you jump into an agent run prompt quickly."
        )

        self.console.print(
            AIPPanel(
                Group(table, tip),
                title="Slash Commands",
                border_style=PRIMARY,
            )
        )

    def _cmd_login(self, _args: list[str], _invoked_from_agent: bool) -> bool:
        self.console.print(f"[{ACCENT_STYLE}]Launching configuration wizard...[/]")
        try:
            self.ctx.invoke(configure_command)
            self._config_cache = None
            if self._suppress_login_layout:
                self._welcome_rendered = False
                self._default_actions_shown = False
            else:
                self._render_header(initial=True)
                self._show_default_quick_actions()
        except click.ClickException as exc:
            self.console.print(f"[{ERROR_STYLE}]{exc}[/]")
        return True

    def _cmd_status(self, _args: list[str], _invoked_from_agent: bool) -> bool:
        ctx_obj = self.ctx.obj if isinstance(self.ctx.obj, dict) else None
        previous_console = None
        try:
            status_module = importlib.import_module("glaip_sdk.cli.main")
            status_command = getattr(status_module, "status")

            if ctx_obj is not None:
                previous_console = ctx_obj.get("_slash_console")
                ctx_obj["_slash_console"] = self.console

            self.ctx.invoke(status_command)

            hints: list[tuple[str, str]] = [
                (self.AGENTS_COMMAND, "Browse agents and run them")
            ]
            if self.recent_agents:
                top = self.recent_agents[0]
                label = top.get("name") or top.get("id")
                hints.append((f"/agents {top.get('id')}", f"Reopen {label}"))
            self._show_quick_actions(hints, title="Next actions")
        except click.ClickException as exc:
            self.console.print(f"[{ERROR_STYLE}]{exc}[/]")
        finally:
            if ctx_obj is not None:
                if previous_console is None:
                    ctx_obj.pop("_slash_console", None)
                else:
                    ctx_obj["_slash_console"] = previous_console
        return True

    def _cmd_agents(self, args: list[str], _invoked_from_agent: bool) -> bool:
        client = self._get_client_or_fail()
        if not client:
            return True

        agents = self._get_agents_or_fail(client)
        if not agents:
            return True

        picked_agent = self._resolve_or_pick_agent(client, agents, args)

        if not picked_agent:
            return True

        return self._run_agent_session(picked_agent)

    def _get_client_or_fail(self) -> Any:
        """Get client or handle failure and return None."""
        try:
            return self._get_client()
        except click.ClickException as exc:
            self.console.print(f"[{ERROR_STYLE}]{exc}[/]")
            return None

    def _get_agents_or_fail(self, client: Any) -> list:
        """Get agents list or handle failure and return empty list."""
        try:
            agents = client.list_agents()
            if not agents:
                self._handle_no_agents()
            return agents
        except Exception as exc:  # pragma: no cover - API failures
            self.console.print(f"[{ERROR_STYLE}]Failed to load agents: {exc}[/]")
            return []

    def _handle_no_agents(self) -> None:
        """Handle case when no agents are available."""
        hint = command_hint("agents create", slash_command=None, ctx=self.ctx)
        if hint:
            self.console.print(
                f"[{WARNING_STYLE}]No agents available. Use `{hint}` to add one.[/]"
            )
        else:
            self.console.print(f"[{WARNING_STYLE}]No agents available.[/]")

    def _resolve_or_pick_agent(self, client: Any, agents: list, args: list[str]) -> Any:
        """Resolve agent from args or pick interactively."""
        if args:
            picked_agent = self._resolve_agent_from_ref(client, agents, args[0])
            if picked_agent is None:
                self.console.print(
                    f"[{WARNING_STYLE}]Could not resolve agent '{args[0]}'. Try `/agents` to browse interactively.[/]"
                )
                return None
        else:
            picked_agent = _fuzzy_pick_for_resources(agents, "agent", "")

        return picked_agent

    def _run_agent_session(self, picked_agent: Any) -> bool:
        """Run agent session and show follow-up actions."""
        self._remember_agent(picked_agent)
        AgentRunSession(self, picked_agent).run()

        # Refresh the main palette header and surface follow-up actions
        self._render_header()

        self._show_agent_followup_actions(picked_agent)
        return True

    def _show_agent_followup_actions(self, picked_agent: Any) -> None:
        """Show follow-up action hints after agent session."""
        agent_id = str(getattr(picked_agent, "id", ""))
        agent_label = getattr(picked_agent, "name", "") or agent_id or "this agent"

        hints: list[tuple[str, str]] = []
        if agent_id:
            hints.append((f"/agents {agent_id}", f"Reopen {agent_label}"))
        hints.extend(
            [
                (self.AGENTS_COMMAND, "Browse agents"),
                (self.STATUS_COMMAND, "Check connection"),
            ]
        )

        self._show_quick_actions(hints, title="Next actions")

    def _cmd_exit(self, _args: list[str], invoked_from_agent: bool) -> bool:
        if invoked_from_agent:
            # Returning False would stop the full session; we only want to exit
            # the agent context. Raising a custom flag keeps the outer loop
            # running.
            return True

        self.console.print(f"[{ACCENT_STYLE}]Closing the command palette.[/]")
        return False

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    def _register_defaults(self) -> None:
        self._register(
            SlashCommand(
                name="help",
                help="Show available command palette commands.",
                handler=SlashSession._cmd_help,
                aliases=("?",),
            )
        )
        self._register(
            SlashCommand(
                name="login",
                help="Run `/login` (alias `/configure`) to set credentials.",
                handler=SlashSession._cmd_login,
                aliases=("configure",),
            )
        )
        self._register(
            SlashCommand(
                name="status",
                help="Display connection status summary.",
                handler=SlashSession._cmd_status,
            )
        )
        self._register(
            SlashCommand(
                name="agents",
                help="Pick an agent and enter a focused run prompt.",
                handler=SlashSession._cmd_agents,
            )
        )
        self._register(
            SlashCommand(
                name="exit",
                help="Exit the command palette.",
                handler=SlashSession._cmd_exit,
                aliases=("q",),
            )
        )
        self._register(
            SlashCommand(
                name="export",
                help="Export the most recent agent transcript.",
                handler=SlashSession._cmd_export,
            )
        )
        self._register(
            SlashCommand(
                name="update",
                help="Upgrade the glaip-sdk package to the latest version.",
                handler=SlashSession._cmd_update,
            )
        )

    def _register(self, command: SlashCommand) -> None:
        self._unique_commands[command.name] = command
        for key in (command.name, *command.aliases):
            self._commands[key] = command

    def open_transcript_viewer(self, *, announce: bool = True) -> None:
        """Launch the transcript viewer for the most recent run."""
        payload, manifest = self._get_last_transcript()
        if payload is None or manifest is None:
            if announce:
                self.console.print(
                    f"[{WARNING_STYLE}]No transcript is available yet. Run an agent first.[/]"
                )
            return

        run_id = manifest.get("run_id")
        if not run_id:
            if announce:
                self.console.print(
                    f"[{WARNING_STYLE}]Latest transcript is missing run metadata.[/]"
                )
            return

        viewer_ctx = ViewerContext(
            manifest_entry=manifest,
            events=list(getattr(payload, "events", []) or []),
            default_output=getattr(payload, "default_output", ""),
            final_output=getattr(payload, "final_output", ""),
            stream_started_at=getattr(payload, "started_at", None),
            meta=getattr(payload, "meta", {}) or {},
        )

        def _export(destination: Path) -> Path:
            return export_cached_transcript(destination=destination, run_id=run_id)

        try:
            run_viewer_session(self.console, viewer_ctx, _export)
        except Exception as exc:  # pragma: no cover - interactive failures
            if announce:
                self.console.print(
                    f"[{ERROR_STYLE}]Failed to launch transcript viewer: {exc}[/]"
                )

    def _get_last_transcript(self) -> tuple[Any | None, dict[str, Any] | None]:
        """Fetch the most recently stored transcript payload and manifest."""
        ctx_obj = getattr(self.ctx, "obj", None)
        if not isinstance(ctx_obj, dict):
            return None, None
        payload = ctx_obj.get("_last_transcript_payload")
        manifest = ctx_obj.get("_last_transcript_manifest")
        return payload, manifest

    def _cmd_export(self, args: list[str], _invoked_from_agent: bool) -> bool:
        """Slash handler for `/export` command."""
        path_arg = args[0] if args else None
        run_id = args[1] if len(args) > 1 else None

        manifest_entry = resolve_manifest_for_export(self.ctx, run_id)
        if manifest_entry is None:
            if run_id:
                self.console.print(
                    f"[{WARNING_STYLE}]No cached transcript found with run id {run_id!r}. Omit the run id to export the most recent run.[/]"
                )
            else:
                self.console.print(
                    f"[{WARNING_STYLE}]No cached transcripts available yet. Run an agent first.[/]"
                )
            return False

        destination = self._resolve_export_destination(path_arg, manifest_entry)
        if destination is None:
            return False

        try:
            exported = export_cached_transcript(
                destination=destination,
                run_id=manifest_entry.get("run_id"),
            )
        except FileNotFoundError as exc:
            self.console.print(f"[{ERROR_STYLE}]{exc}[/]")
            return False
        except Exception as exc:  # pragma: no cover - unexpected IO failures
            self.console.print(f"[{ERROR_STYLE}]Failed to export transcript: {exc}[/]")
            return False
        else:
            self.console.print(f"[{SUCCESS_STYLE}]Transcript exported to[/] {exported}")
            return True

    def _resolve_export_destination(
        self, path_arg: str | None, manifest_entry: dict[str, Any]
    ) -> Path | None:
        if path_arg:
            return normalise_export_destination(Path(path_arg))

        default_name = suggest_filename(manifest_entry)
        prompt = f"Save transcript to [{default_name}]: "
        try:
            response = self.console.input(prompt)
        except EOFError:
            self.console.print("[dim]Export cancelled.[/dim]")
            return None

        chosen = response.strip() or default_name
        return normalise_export_destination(Path(chosen))

    def _cmd_update(self, args: list[str], _invoked_from_agent: bool) -> bool:
        """Slash handler for `/update` command."""
        if args:
            self.console.print(
                "Usage: `/update` upgrades glaip-sdk to the latest published version."
            )
            return True

        try:
            self.ctx.invoke(update_command)
            return True
        except click.ClickException as exc:
            self.console.print(f"[{ERROR_STYLE}]{exc}[/]")
            # Return False for update command failures to indicate the command didn't complete successfully
            return False

    # ------------------------------------------------------------------
    # Agent run coordination helpers
    # ------------------------------------------------------------------
    def register_active_renderer(self, renderer: Any) -> None:
        """Register the renderer currently streaming an agent run."""
        self._active_renderer = renderer
        self._sync_active_renderer()

    def clear_active_renderer(self, renderer: Any | None = None) -> None:
        """Clear the active renderer if it matches the provided instance."""
        if renderer is not None and renderer is not self._active_renderer:
            return
        self._active_renderer = None

    def mark_agent_transcript_ready(self, agent_id: str, run_id: str | None) -> None:
        """Record that an agent has a transcript ready for the current session."""
        if not agent_id or not run_id:
            return
        self._agent_transcript_ready[agent_id] = run_id

    def clear_agent_transcript_ready(self, agent_id: str | None = None) -> None:
        """Reset transcript-ready state for an agent or for all agents."""
        if agent_id:
            self._agent_transcript_ready.pop(agent_id, None)
            return
        self._agent_transcript_ready.clear()

    def notify_agent_run_started(self) -> None:
        """Mark that an agent run is in progress."""
        self.clear_active_renderer()

    def notify_agent_run_finished(self) -> None:
        """Mark that the active agent run has completed."""
        self.clear_active_renderer()

    def _sync_active_renderer(self) -> None:
        """Ensure the active renderer stays in standard (non-verbose) mode."""
        renderer = self._active_renderer
        if renderer is None:
            return

        applied = False
        apply_verbose = getattr(renderer, "apply_verbosity", None)
        if callable(apply_verbose):
            try:
                apply_verbose(False)
                applied = True
            except Exception:
                pass

        if not applied and hasattr(renderer, "verbose"):
            try:
                renderer.verbose = False
            except Exception:
                pass

    def _parse(self, raw: str) -> tuple[str, list[str]]:
        try:
            tokens = shlex.split(raw)
        except ValueError:
            return "", []

        if not tokens:
            return "", []

        head = tokens[0]
        if head.startswith("/"):
            head = head[1:]

        return head, tokens[1:]

    def _suggest(self, verb: str) -> str | None:
        keys = [cmd.name for cmd in self._unique_commands.values()]
        match = get_close_matches(verb, keys, n=1)
        return match[0] if match else None

    def _convert_message(self, value: Any) -> Any:
        """Convert a message value to the appropriate format for display."""
        if FormattedText is not None and to_formatted_text is not None:
            return to_formatted_text(value)
        if FormattedText is not None:
            return FormattedText([("class:prompt", str(value))])
        return str(value)

    def _get_prompt_kwargs(self, placeholder: str | None) -> dict[str, Any]:
        """Get prompt kwargs with optional placeholder styling."""
        prompt_kwargs: dict[str, Any] = {"style": self._ptk_style}
        if placeholder:
            placeholder_text = (
                FormattedText([("class:placeholder", placeholder)])
                if FormattedText is not None
                else placeholder
            )
            prompt_kwargs["placeholder"] = placeholder_text
        return prompt_kwargs

    def _prompt_with_prompt_toolkit(
        self, message: str | Callable[[], Any], placeholder: str | None
    ) -> str:
        """Handle prompting with prompt_toolkit."""
        with patch_stdout():  # pragma: no cover - UI specific
            if callable(message):

                def prompt_text() -> Any:
                    return self._convert_message(message())
            else:
                prompt_text = self._convert_message(message)

            prompt_kwargs = self._get_prompt_kwargs(placeholder)

            try:
                return self._ptk_session.prompt(prompt_text, **prompt_kwargs)
            except (
                TypeError
            ):  # pragma: no cover - compatibility with older prompt_toolkit
                prompt_kwargs.pop("placeholder", None)
                return self._ptk_session.prompt(prompt_text, **prompt_kwargs)

    def _extract_message_text(self, raw_value: Any) -> str:
        """Extract text content from various message formats."""
        if isinstance(raw_value, str):
            return raw_value

        try:
            if FormattedText is not None and isinstance(raw_value, FormattedText):
                return "".join(text for _style, text in raw_value)
            elif isinstance(raw_value, list):
                return "".join(segment[1] for segment in raw_value)
            else:
                return str(raw_value)
        except Exception:
            return str(raw_value)

    def _prompt_with_basic_input(
        self, message: str | Callable[[], Any], placeholder: str | None
    ) -> str:
        """Handle prompting with basic input."""
        if placeholder:
            self.console.print(f"[dim]{placeholder}[/dim]")

        raw_value = message() if callable(message) else message
        actual_message = self._extract_message_text(raw_value)

        return input(actual_message)

    def _prompt(
        self, message: str | Callable[[], Any], *, placeholder: str | None = None
    ) -> str:
        """Main prompt function with reduced complexity."""
        if self._ptk_session and self._ptk_style and patch_stdout:
            return self._prompt_with_prompt_toolkit(message, placeholder)

        return self._prompt_with_basic_input(message, placeholder)

    def _get_client(self) -> Any:  # type: ignore[no-any-return]
        if self._client is None:
            self._client = get_client(self.ctx)
        return self._client

    def set_contextual_commands(
        self, commands: dict[str, str] | None, *, include_global: bool = True
    ) -> None:
        """Set context-specific commands that should appear in completions."""
        self._contextual_commands = dict(commands or {})
        self._contextual_include_global = include_global if commands else True

    def get_contextual_commands(self) -> dict[str, str]:  # type: ignore[no-any-return]
        """Return a copy of the currently active contextual commands."""
        return dict(self._contextual_commands)

    def should_include_global_commands(self) -> bool:
        """Return whether global slash commands should appear in completions."""
        return self._contextual_include_global

    def _remember_agent(self, agent: Any) -> None:  # type: ignore[no-any-return]
        agent_data = {
            "id": str(getattr(agent, "id", "")),
            "name": getattr(agent, "name", "") or "",
            "type": getattr(agent, "type", "") or "",
        }

        self.recent_agents = [
            a for a in self.recent_agents if a.get("id") != agent_data["id"]
        ]
        self.recent_agents.insert(0, agent_data)
        self.recent_agents = self.recent_agents[:5]

    def _render_header(
        self,
        active_agent: Any | None = None,
        *,
        focus_agent: bool = False,
        initial: bool = False,
    ) -> None:
        if focus_agent and active_agent is not None:
            self._render_focused_agent_header(active_agent)
            return

        full_header = initial or not self._welcome_rendered
        if full_header:
            self._render_branding_banner()
            self.console.rule(style=PRIMARY)
        self._render_main_header(active_agent, full=full_header)
        if full_header:
            self._welcome_rendered = True
            self.console.print()

    def _render_branding_banner(self) -> None:
        """Render the GL AIP branding banner."""
        banner = self._branding.get_welcome_banner()
        heading = "[bold]>_ GDP Labs AI Agents Package (AIP CLI)[/bold]"
        self.console.print(heading)
        self.console.print()
        self.console.print(banner)

    def _maybe_show_update_prompt(self) -> None:
        """Display update prompt once per session when applicable."""
        if self._update_prompt_shown:
            return

        self._update_notifier(
            self._branding.version,
            console=self.console,
            ctx=self.ctx,
            slash_command="update",
            style="panel",
        )
        self._update_prompt_shown = True

    def _render_focused_agent_header(self, active_agent: Any) -> None:
        """Render header when focusing on a specific agent."""
        agent_info = self._get_agent_info(active_agent)
        transcript_status = self._get_transcript_status(active_agent)

        header_grid = self._build_header_grid(agent_info, transcript_status)
        keybar = self._build_keybar()

        header_grid.add_row(keybar, "")
        self.console.print(
            AIPPanel(header_grid, title="Agent Session", border_style=PRIMARY)
        )

    def _get_agent_info(self, active_agent: Any) -> dict[str, str]:
        """Extract agent information for display."""
        agent_id = str(getattr(active_agent, "id", ""))
        return {
            "id": agent_id,
            "name": getattr(active_agent, "name", "") or agent_id,
            "type": getattr(active_agent, "type", "") or "-",
            "description": getattr(active_agent, "description", "") or "",
        }

    def _get_transcript_status(self, active_agent: Any) -> dict[str, Any]:
        """Get transcript status for the active agent."""
        agent_id = str(getattr(active_agent, "id", ""))
        payload, manifest = self._get_last_transcript()

        latest_agent_id = (manifest or {}).get("agent_id")
        has_transcript = bool(payload and manifest and manifest.get("run_id"))
        run_id = (manifest or {}).get("run_id")
        transcript_ready = (
            has_transcript
            and latest_agent_id == agent_id
            and self._agent_transcript_ready.get(agent_id) == run_id
        )

        return {
            "has_transcript": has_transcript,
            "transcript_ready": transcript_ready,
            "run_id": run_id,
        }

    def _build_header_grid(
        self, agent_info: dict[str, str], transcript_status: dict[str, Any]
    ) -> AIPGrid:
        """Build the main header grid with agent information."""
        header_grid = AIPGrid(expand=True)
        header_grid.add_column(ratio=3)
        header_grid.add_column(ratio=1, justify="right")

        primary_line = (
            f"[bold]{agent_info['name']}[/bold] · [dim]{agent_info['type']}[/dim] · "
            f"[{ACCENT_STYLE}]{agent_info['id']}[/]"
        )
        status_line = f"[{SUCCESS_STYLE}]ready[/]"
        status_line += (
            " · transcript ready"
            if transcript_status["transcript_ready"]
            else " · transcript pending"
        )
        header_grid.add_row(primary_line, status_line)

        if agent_info["description"]:
            description = agent_info["description"]
            if not transcript_status["transcript_ready"]:
                description = f"{description}  (transcript pending)"
            header_grid.add_row(f"[dim]{description}[/dim]", "")

        return header_grid

    def _build_keybar(self) -> AIPGrid:
        """Build the keybar with command hints."""
        keybar = AIPGrid(expand=True)
        keybar.add_column(justify="left", ratio=1)
        keybar.add_column(justify="left", ratio=1)
        keybar.add_column(justify="left", ratio=1)
        keybar.add_column(justify="left", ratio=1)

        keybar.add_row(
            format_command_hint("/help", "Show commands") or "",
            format_command_hint("/details", "Agent config") or "",
            format_command_hint("/exit", "Back") or "",
            "[bold]Alt+Enter[/bold] [dim]Line break[/dim]",
        )

        return keybar

    def _render_main_header(
        self, active_agent: Any | None = None, *, full: bool = False
    ) -> None:
        """Render the main AIP environment header."""
        config = self._load_config()

        api_url = self._get_api_url(config)
        status = "Configured" if config.get("api_key") else "Not configured"

        segments = [
            f"[dim]Base URL[/dim] • {api_url or 'Not configured'}",
            f"[dim]Credentials[/dim] • {status}",
        ]
        agent_info = self._build_agent_status_line(active_agent)
        if agent_info:
            segments.append(agent_info)

        rendered_line = "    ".join(segments)

        if full:
            self.console.print(rendered_line)
            return

        status_bar = AIPGrid(expand=True)
        status_bar.add_column(ratio=1)
        status_bar.add_row(rendered_line)
        self.console.print(
            AIPPanel(
                status_bar,
                border_style=PRIMARY,
                padding=(0, 1),
                expand=False,
            )
        )

    def _get_api_url(self, config: dict[str, Any]) -> str | None:
        """Get the API URL from various sources."""
        api_url = None
        if isinstance(self.ctx.obj, dict):
            api_url = self.ctx.obj.get("api_url")
        return api_url or config.get("api_url") or os.getenv("AIP_API_URL")

    def _build_agent_status_line(self, active_agent: Any | None) -> str | None:
        """Return a short status line about the active or recent agent."""
        if active_agent is not None:
            agent_id = str(getattr(active_agent, "id", ""))
            agent_name = getattr(active_agent, "name", "") or agent_id
            return f"[dim]Active[/dim]: {agent_name} ({agent_id})"
        if self.recent_agents:
            recent = self.recent_agents[0]
            label = recent.get("name") or recent.get("id") or "-"
            return f"[dim]Recent[/dim]: {label} ({recent.get('id', '-')})"
        return None

    def _show_default_quick_actions(self) -> None:
        hints: list[tuple[str | None, str]] = [
            (
                command_hint("status", slash_command="status", ctx=self.ctx),
                "Connection check",
            ),
            (
                command_hint("agents list", slash_command="agents", ctx=self.ctx),
                "Browse agents",
            ),
            (
                command_hint("help", slash_command="help", ctx=self.ctx),
                "Show all commands",
            ),
        ]
        filtered = [(cmd, desc) for cmd, desc in hints if cmd]
        if filtered:
            self._show_quick_actions(filtered, title="Quick actions")
        self._default_actions_shown = True

    def _render_home_hint(self) -> None:
        if self._home_hint_shown:
            return
        hint_lines = [
            f"[{HINT_PREFIX_STYLE}]Hint:[/]",
            f"  Type {format_command_hint('/') or '/'} to explore commands",
            "  Press [dim]Ctrl+C[/] to cancel the current entry",
            "  Press [dim]Ctrl+D[/] to quit",
        ]
        self.console.print("\n".join(hint_lines))
        self._home_hint_shown = True

    def _show_quick_actions(
        self,
        hints: Iterable[tuple[str, str]],
        *,
        title: str = "Quick actions",
        inline: bool = False,
    ) -> None:
        hint_list = [
            (command, description) for command, description in hints if command
        ]
        if not hint_list:
            return

        if inline:
            lines: list[str] = []
            for command, description in hint_list:
                formatted = format_command_hint(command, description)
                if formatted:
                    lines.append(formatted)
            if lines:
                self.console.print("\n".join(lines))
            return

        body_lines: list[Text] = []
        for command, description in hint_list:
            formatted = format_command_hint(command, description)
            if formatted:
                body_lines.append(Text.from_markup(formatted))

        panel_content = Group(*body_lines)
        self.console.print(
            AIPPanel(
                panel_content, title=title, border_style=SECONDARY_LIGHT, expand=False
            )
        )

    def _load_config(self) -> dict[str, Any]:
        if self._config_cache is None:
            try:
                self._config_cache = load_config() or {}
            except Exception:
                self._config_cache = {}
        return self._config_cache

    def _resolve_agent_from_ref(
        self, client: Any, available_agents: list[Any], ref: str
    ) -> Any | None:
        ref = ref.strip()
        if not ref:
            return None

        try:
            agent = client.get_agent_by_id(ref)
            if agent:
                return agent
        except Exception:  # pragma: no cover - passthrough
            pass

        matches = [a for a in available_agents if str(getattr(a, "id", "")) == ref]
        if matches:
            return matches[0]

        try:
            found = client.find_agents(name=ref)
        except Exception:  # pragma: no cover - passthrough
            found = []

        if len(found) == 1:
            return found[0]

        return None
