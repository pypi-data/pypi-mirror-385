"""Main CLI entry point for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import os
import subprocess
import sys
from typing import Any

import click
from rich.console import Console

from glaip_sdk import Client
from glaip_sdk._version import __version__ as _SDK_VERSION
from glaip_sdk.branding import (
    ERROR,
    ERROR_STYLE,
    INFO,
    INFO_STYLE,
    NEUTRAL,
    SUCCESS,
    SUCCESS_STYLE,
    WARNING,
    WARNING_STYLE,
    AIPBranding,
)
from glaip_sdk.cli.commands.agents import agents_group
from glaip_sdk.cli.commands.configure import (
    config_group,
    configure_command,
)
from glaip_sdk.cli.commands.mcps import mcps_group
from glaip_sdk.cli.commands.models import models_group
from glaip_sdk.cli.commands.tools import tools_group
from glaip_sdk.cli.commands.update import update_command
from glaip_sdk.cli.config import load_config
from glaip_sdk.cli.transcript import get_transcript_cache_stats
from glaip_sdk.cli.update_notifier import maybe_notify_update
from glaip_sdk.cli.utils import in_slash_mode, spinner_context, update_spinner
from glaip_sdk.config.constants import (
    DEFAULT_AGENT_RUN_TIMEOUT,
)
from glaip_sdk.icons import ICON_AGENT
from glaip_sdk.rich_components import AIPPanel, AIPTable

# Import SlashSession for potential mocking in tests
try:
    from glaip_sdk.cli.slash import SlashSession
except ImportError:  # pragma: no cover - optional slash dependencies
    # Slash dependencies might not be available in all environments
    SlashSession = None

# Constants
AVAILABLE_STATUS = "✅ Available"


def _format_size(num: int) -> str:
    """Return a human-readable byte size."""
    if num <= 0:
        return "0B"

    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(num)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if value >= 100 or unit == "B":
                return f"{value:.0f}{unit}"
            if value >= 10:
                return f"{value:.1f}{unit}"
            return f"{value:.2f}{unit}"
        value /= 1024
    return f"{value:.1f}TB"  # pragma: no cover - defensive fallback


@click.group(invoke_without_command=True)
@click.version_option(version=_SDK_VERSION, prog_name="aip")
@click.option(
    "--api-url",
    envvar="AIP_API_URL",
    help="AIP API URL (primary credential for the CLI)",
)
@click.option(
    "--api-key",
    envvar="AIP_API_KEY",
    help="AIP API Key (CLI requires this together with --api-url)",
)
@click.option("--timeout", default=30.0, help="Request timeout in seconds")
@click.option(
    "--view",
    "view",
    type=click.Choice(["rich", "plain", "json", "md"]),
    default="rich",
    help="Output view format",
)
@click.option("--no-tty", is_flag=True, help="Disable TTY renderer")
@click.pass_context
def main(
    ctx: Any,
    api_url: str | None,
    api_key: str | None,
    timeout: float | None,
    view: str | None,
    no_tty: bool,
) -> None:
    r"""GL AIP SDK Command Line Interface.

    A comprehensive CLI for managing GL AIP resources including
    agents, tools, MCPs, and more.

    \b
    Examples:
      aip version                     # Show detailed version info
      aip configure                   # Configure credentials
      aip agents list                 # List all agents
      aip tools create my_tool.py     # Create a new tool
      aip agents run my-agent "Hello world"  # Run an agent
    """
    # Store configuration in context
    ctx.ensure_object(dict)
    ctx.obj["api_url"] = api_url
    ctx.obj["api_key"] = api_key
    ctx.obj["timeout"] = timeout
    ctx.obj["view"] = view

    ctx.obj["tty"] = not no_tty

    launching_slash = (
        ctx.invoked_subcommand is None
        and not ctx.resilient_parsing
        and _should_launch_slash(ctx)
        and SlashSession is not None
    )

    if not ctx.resilient_parsing and ctx.obj["tty"] and not launching_slash:
        console = Console()
        maybe_notify_update(
            _SDK_VERSION,
            console=console,
            ctx=ctx,
            slash_command="update",
        )

    if ctx.invoked_subcommand is None and not ctx.resilient_parsing:
        if launching_slash:
            session = SlashSession(ctx)
            session.run()
            ctx.exit()
        else:
            click.echo(ctx.get_help())
            ctx.exit()


# Add command groups
main.add_command(agents_group)
main.add_command(config_group)
main.add_command(tools_group)
main.add_command(mcps_group)
main.add_command(models_group)

# Add top-level commands
main.add_command(configure_command)
main.add_command(update_command)


# Tip: `--version` is provided by click.version_option above.


def _should_launch_slash(ctx: click.Context) -> bool:
    """Determine whether to open the command palette automatically."""
    ctx_obj = ctx.obj or {}
    if not bool(ctx_obj.get("tty", True)):
        return False

    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return False

    return True


def _load_and_merge_config(ctx: click.Context) -> dict:
    """Load configuration from multiple sources and merge them."""
    # Load config from file and merge with context
    file_config = load_config()
    context_config = ctx.obj or {}

    # Load environment variables (middle priority)
    env_config = {}
    if os.getenv("AIP_API_URL"):
        env_config["api_url"] = os.getenv("AIP_API_URL")
    if os.getenv("AIP_API_KEY"):
        env_config["api_key"] = os.getenv("AIP_API_KEY")

    # Filter out None values from context config to avoid overriding other configs
    filtered_context = {k: v for k, v in context_config.items() if v is not None}

    # Merge configs: file (low) -> env (mid) -> CLI args (high)
    return {**file_config, **env_config, **filtered_context}


def _validate_config_and_show_error(config: dict, console: Console) -> None:
    """Validate configuration and show error if incomplete."""
    if not config.get("api_url") or not config.get("api_key"):
        console.print(
            AIPPanel(
                f"[{ERROR_STYLE}]❌ Configuration incomplete[/]\n\n"
                f"🔍 Current config:\n"
                f"   • API URL: {config.get('api_url', 'Not set')}\n"
                f"   • API Key: {'***' + config.get('api_key', '')[-4:] if config.get('api_key') else 'Not set'}\n\n"
                f"💡 To fix this:\n"
                f"   • Run 'aip configure' to set up credentials\n"
                f"   • Or run 'aip config list' to see current config",
                title="❌ Configuration Error",
                border_style=ERROR,
            )
        )
        console.print(
            f"\n[{SUCCESS_STYLE}]✅ AIP - Ready[/] (SDK v{_SDK_VERSION}) - Configure to connect"
        )
        sys.exit(1)


def _resolve_status_console(ctx: Any) -> tuple[Console, bool]:
    """Return the console to use and whether we are in slash mode."""
    ctx_obj = ctx.obj if isinstance(ctx.obj, dict) else None
    console_override = ctx_obj.get("_slash_console") if ctx_obj else None
    console = console_override or Console()
    slash_mode = in_slash_mode(ctx)
    return console, slash_mode


def _render_status_heading(console: Console, slash_mode: bool) -> None:
    """Print the status heading/banner."""
    del slash_mode  # heading now consistent across invocation contexts
    console.print(f"[{INFO_STYLE}]GL AIP status[/]")
    console.print()
    console.print(f"[{SUCCESS_STYLE}]✅ GL AIP ready[/] (SDK v{_SDK_VERSION})")


def _collect_cache_summary() -> tuple[str | None, str | None]:
    """Collect transcript cache summary and optional note."""
    try:
        cache_stats = get_transcript_cache_stats()
    except Exception:
        return "[dim]Saved run history[/dim]: unavailable", None

    runs_text = f"{cache_stats.entry_count} runs saved"
    if cache_stats.total_bytes:
        size_part = f" · {_format_size(cache_stats.total_bytes)} used"
    else:
        size_part = ""

    cache_line = (
        f"[dim]Saved run history[/dim]: {runs_text}{size_part}"
        f" · {cache_stats.cache_dir}"
    )
    return cache_line, None


def _display_cache_summary(
    console: Console, slash_mode: bool, cache_line: str | None, cache_note: str | None
) -> None:
    """Render the cache summary details."""
    if cache_line:
        console.print(cache_line)
    if cache_note and not slash_mode:
        console.print(cache_note)


def _create_and_test_client(
    config: dict, console: Console, *, compact: bool = False
) -> Client:
    """Create client and test connection by fetching resources."""
    # Try to create client
    client = Client(
        api_url=config["api_url"],
        api_key=config["api_key"],
        timeout=config.get("timeout", 30.0),
    )

    # Test connection by listing resources
    try:
        with spinner_context(
            None,  # We'll pass ctx later
            "[bold blue]Checking GL AIP status…[/bold blue]",
            console_override=console,
            spinner_style=INFO,
        ) as status_indicator:
            update_spinner(status_indicator, "[bold blue]Fetching agents…[/bold blue]")
            agents = client.list_agents()

            update_spinner(status_indicator, "[bold blue]Fetching tools…[/bold blue]")
            tools = client.list_tools()

            update_spinner(status_indicator, "[bold blue]Fetching MCPs…[/bold blue]")
            mcps = client.list_mcps()

        # Create status table
        table = AIPTable(title="🔗 GL AIP Status")
        table.add_column("Resource", style=INFO, width=15)
        table.add_column("Count", style=NEUTRAL, width=10)
        table.add_column("Status", style=SUCCESS_STYLE, width=15)

        table.add_row("Agents", str(len(agents)), AVAILABLE_STATUS)
        table.add_row("Tools", str(len(tools)), AVAILABLE_STATUS)
        table.add_row("MCPs", str(len(mcps)), AVAILABLE_STATUS)

        if compact:
            connection_summary = "GL AIP reachable"
            console.print(
                f"[dim]• Base URL[/dim]: {client.api_url} ({connection_summary})"
            )
            console.print(f"[dim]• Agent timeout[/dim]: {DEFAULT_AGENT_RUN_TIMEOUT}s")
            console.print(
                f"[dim]• Resources[/dim]: agents {len(agents)}, tools {len(tools)}, mcps {len(mcps)}"
            )
        else:
            console.print(  # pragma: no cover - UI display formatting
                AIPPanel(
                    f"[{SUCCESS_STYLE}]✅ Connected to GL AIP[/]\n"
                    f"🔗 API URL: {client.api_url}\n"
                    f"{ICON_AGENT} Agent Run Timeout: {DEFAULT_AGENT_RUN_TIMEOUT}s",
                    title="🚀 Connection Status",
                    border_style=SUCCESS,
                )
            )

            console.print(table)  # pragma: no cover - UI display formatting

    except Exception as e:
        # Show AIP Ready status even if connection fails
        if compact:
            status_text = "API call failed"
            console.print(f"[dim]• Base URL[/dim]: {client.api_url} ({status_text})")
            console.print(f"[{ERROR_STYLE}]• Error[/]: {e}")
            console.print(
                "[dim]• Tip[/dim]: Check network connectivity or API permissions and try again."
            )
            console.print("[dim]• Resources[/dim]: unavailable")
        else:
            console.print(
                AIPPanel(
                    f"[{WARNING_STYLE}]⚠️  Connection established but API call failed[/]\n"
                    f"🔗 API URL: {client.api_url}\n"
                    f"❌ Error: {e}\n\n"
                    f"💡 This usually means:\n"
                    f"   • Network connectivity issues\n"
                    f"   • API permissions problems\n"
                    f"   • Backend service issues",
                    title="⚠️  Partial Connection",
                    border_style=WARNING,
                )
            )

    return client


def _handle_connection_error(config: dict, console: Console, error: Exception) -> None:
    """Handle connection errors and show troubleshooting information."""
    console.print(
        AIPPanel(
            f"[{ERROR_STYLE}]❌ Connection failed[/]\n\n"
            f"🔍 Error: {error}\n\n"
            f"💡 Troubleshooting steps:\n"
            f"   • Verify your API URL and key are correct\n"
            f"   • Check network connectivity to {config.get('api_url', 'your API')}\n"
            f"   • Run 'aip configure' to update credentials\n"
            f"   • Run 'aip config list' to check configuration",
            title="❌ Connection Error",
            border_style=ERROR,
        )
    )
    sys.exit(1)


@main.command()
@click.pass_context
def status(ctx: Any) -> None:
    """Show connection status and basic info."""
    config: dict = {}
    console: Console | None = None
    try:
        console, slash_mode = _resolve_status_console(ctx)
        _render_status_heading(console, slash_mode)

        cache_line, cache_note = _collect_cache_summary()
        _display_cache_summary(console, slash_mode, cache_line, cache_note)

        # Load and merge configuration
        config = _load_and_merge_config(ctx)

        # Validate configuration
        _validate_config_and_show_error(config, console)

        # Create and test client connection using unified compact layout
        client = _create_and_test_client(config, console, compact=True)
        client.close()

    except Exception as e:
        # Handle any unexpected errors during the process
        fallback_console = console or Console()
        _handle_connection_error(config or {}, fallback_console, e)


@main.command()
def version() -> None:
    """Show version information."""
    branding = AIPBranding.create_from_sdk(
        sdk_version=_SDK_VERSION, package_name="glaip-sdk"
    )
    branding.display_version_panel()


@main.command()
@click.option(
    "--check-only", is_flag=True, help="Only check for updates without installing"
)
@click.option(
    "--force",
    is_flag=True,
    help="Force reinstall even if already up-to-date (adds --force-reinstall)",
)
def update(check_only: bool, force: bool) -> None:
    """Update AIP SDK to the latest version from PyPI."""
    try:
        console = Console()

        if check_only:
            console.print(
                AIPPanel(
                    "[bold blue]🔍 Checking for updates...[/bold blue]\n\n"
                    "💡 To install updates, run: aip update",
                    title="📋 Update Check",
                    border_style="blue",
                )
            )
            return

        console.print(
            AIPPanel(
                "[bold blue]🔄 Updating AIP SDK...[/bold blue]\n\n"
                "📦 This will update the package from PyPI\n"
                "💡 Use --check-only to just check for updates",
                title="Update Process",
                border_style="blue",
                padding=(0, 1),
            )
        )

        # Update using pip
        try:
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "glaip-sdk",
            ]
            if force:
                cmd.insert(5, "--force-reinstall")
            subprocess.run(cmd, capture_output=True, text=True, check=True)

            console.print(
                AIPPanel(
                    f"[{SUCCESS_STYLE}]✅ Update successful![/]\n\n"
                    "🔄 AIP SDK has been updated to the latest version\n"
                    "💡 Restart your terminal or run 'aip --version' to verify",
                    title="🎉 Update Complete",
                    border_style=SUCCESS,
                    padding=(0, 1),
                )
            )

            # Show new version
            version_result = subprocess.run(
                [sys.executable, "-m", "glaip_sdk.cli.main", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            console.print(f"📋 New version: {version_result.stdout.strip()}")

        except subprocess.CalledProcessError as e:
            console.print(
                AIPPanel(
                    f"[{ERROR_STYLE}]❌ Update failed[/]\n\n"
                    f"🔍 Error: {e.stderr}\n\n"
                    "💡 Troubleshooting:\n"
                    "   • Check your internet connection\n"
                    "   • Try running: pip install --upgrade glaip-sdk\n"
                    "   • Check if you have write permissions",
                    title="❌ Update Error",
                    border_style=ERROR,
                    padding=(0, 1),
                )
            )
            sys.exit(1)

    except ImportError:
        console.print(
            AIPPanel(
                f"[{ERROR_STYLE}]❌ Rich library not available[/]\n\n"
                "💡 Install rich: pip install rich\n"
                "   Then try: aip update",
                title="❌ Missing Dependency",
                border_style=ERROR,
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
