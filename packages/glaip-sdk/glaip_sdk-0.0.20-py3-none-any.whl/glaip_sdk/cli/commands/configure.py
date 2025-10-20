"""Configuration management commands.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import getpass

import click
from rich.console import Console
from rich.text import Text

from glaip_sdk import Client
from glaip_sdk._version import __version__ as _SDK_VERSION
from glaip_sdk.branding import (
    ACCENT_STYLE,
    ERROR_STYLE,
    INFO,
    PRIMARY,
    SUCCESS,
    SUCCESS_STYLE,
    WARNING_STYLE,
    AIPBranding,
)
from glaip_sdk.cli.config import CONFIG_FILE, load_config, save_config
from glaip_sdk.cli.rich_helpers import markup_text
from glaip_sdk.cli.utils import command_hint, format_command_hint
from glaip_sdk.icons import ICON_TOOL
from glaip_sdk.rich_components import AIPTable

console = Console()


@click.group()
def config_group() -> None:
    """Configuration management operations."""
    pass


@config_group.command("list")
def list_config() -> None:
    """List current configuration."""
    config = load_config()

    if not config:
        _print_missing_config_hint()
        return

    _render_config_table(config)


@config_group.command("set")
@click.argument("key")
@click.argument("value")
def set_config(key: str, value: str) -> None:
    """Set a configuration value."""
    valid_keys = ["api_url", "api_key"]

    if key not in valid_keys:
        console.print(
            f"[{ERROR_STYLE}]Error: Invalid key '{key}'. Valid keys are: {', '.join(valid_keys)}[/]"
        )
        raise click.ClickException(f"Invalid configuration key: {key}")

    config = load_config()
    config[key] = value
    save_config(config)

    if key == "api_key":
        console.print(
            Text(f"✅ Set {key} = {_mask_api_key(value)}", style=SUCCESS_STYLE)
        )
    else:
        console.print(Text(f"✅ Set {key} = {value}", style=SUCCESS_STYLE))


@config_group.command("get")
@click.argument("key")
def get_config(key: str) -> None:
    """Get a configuration value."""
    config = load_config()

    if key not in config:
        console.print(
            markup_text(f"[{WARNING_STYLE}]Configuration key '{key}' not found.[/]")
        )
        raise click.ClickException(f"Configuration key not found: {key}")

    value = config[key]

    if key == "api_key":
        console.print(_mask_api_key(value))
    else:
        console.print(value)


@config_group.command("unset")
@click.argument("key")
def unset_config(key: str) -> None:
    """Remove a configuration value."""
    config = load_config()

    if key not in config:
        console.print(
            markup_text(f"[{WARNING_STYLE}]Configuration key '{key}' not found.[/]")
        )
        return

    del config[key]
    save_config(config)

    console.print(Text(f"✅ Removed {key} from configuration", style=SUCCESS_STYLE))


@config_group.command("reset")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def reset_config(force: bool) -> None:
    """Reset all configuration to defaults."""
    if not force:
        console.print(f"[{WARNING_STYLE}]This will remove all AIP configuration.[/]")
        confirm = input("Are you sure? (y/N): ").strip().lower()
        if confirm not in ["y", "yes"]:
            console.print("Cancelled.")
            return

    config_data = load_config()
    file_exists = CONFIG_FILE.exists()

    if not file_exists and not config_data:
        console.print(f"[{WARNING_STYLE}]No configuration found to reset.[/]")
        console.print(
            Text("✅ Configuration reset (nothing to remove).", style=SUCCESS_STYLE)
        )
        return

    if file_exists:
        try:
            CONFIG_FILE.unlink()
        except FileNotFoundError:  # pragma: no cover - defensive cleanup
            pass
    else:
        # In-memory configuration (e.g., tests) needs explicit clearing
        save_config({})

    hint = command_hint("config configure", slash_command="login")
    message = Text("✅ Configuration reset.", style=SUCCESS_STYLE)
    if hint:
        message.append(f" Run '{hint}' to set up again.")
    console.print(message)


def _configure_interactive() -> None:
    """Shared configuration logic for both configure commands."""
    _render_configuration_header()
    config = load_config()
    _prompt_configuration_inputs(config)
    _save_configuration(config)
    _test_and_report_connection(config)
    _print_post_configuration_hints()


@config_group.command()
def configure() -> None:
    """Configure AIP CLI credentials and settings interactively."""
    _configure_interactive()


# Alias command for backward compatibility
@click.command()
def configure_command() -> None:
    """Configure AIP CLI credentials and settings interactively.

    This is an alias for 'aip config configure' for backward compatibility.
    """
    # Delegate to the shared function
    _configure_interactive()


# Note: The config command group should be registered in main.py


def _mask_api_key(value: str | None) -> str:
    if not value:
        return ""
    return "***" + value[-4:] if len(value) > 4 else "***"


def _print_missing_config_hint() -> None:
    hint = command_hint("config configure", slash_command="login")
    if hint:
        console.print(
            f"[{WARNING_STYLE}]No configuration found.[/] Run {format_command_hint(hint) or hint} to set up."
        )
    else:
        console.print(f"[{WARNING_STYLE}]No configuration found.[/]")


def _render_config_table(config: dict[str, str]) -> None:
    table = AIPTable(title=f"{ICON_TOOL} AIP Configuration")
    table.add_column("Setting", style=INFO, width=20)
    table.add_column("Value", style=SUCCESS)

    for key, value in config.items():
        table.add_row(key, _mask_api_key(value) if key == "api_key" else str(value))

    console.print(table)
    console.print(Text(f"\n📁 Config file: {CONFIG_FILE}"))


def _render_configuration_header() -> None:
    branding = AIPBranding.create_from_sdk(
        sdk_version=_SDK_VERSION, package_name="glaip-sdk"
    )
    heading = "[bold]>_ GDP Labs AI Agents Package (AIP CLI)[/bold]"
    console.print(heading)
    console.print()
    console.print(branding.get_welcome_banner())
    console.rule("[bold]AIP Configuration[/bold]", style=PRIMARY)


def _prompt_configuration_inputs(config: dict[str, str]) -> None:
    console.print("\n[bold]Enter your AIP configuration:[/bold]")
    console.print("(Leave blank to keep current values)")
    console.print("─" * 50)

    _prompt_api_url(config)
    _prompt_api_key(config)


def _prompt_api_url(config: dict[str, str]) -> None:
    current_url = config.get("api_url", "")
    suffix = f"(current: {current_url})" if current_url else ""
    console.print(f"\n[{ACCENT_STYLE}]AIP API URL[/] {suffix}:")
    new_url = input("> ").strip()
    if new_url:
        config["api_url"] = new_url
    elif not current_url:
        config["api_url"] = "https://your-aip-instance.com"


def _prompt_api_key(config: dict[str, str]) -> None:
    current_key_masked = _mask_api_key(config.get("api_key"))
    suffix = f"(current: {current_key_masked})" if current_key_masked else ""
    console.print(f"\n[{ACCENT_STYLE}]AIP API Key[/] {suffix}:")
    new_key = getpass.getpass("> ")
    if new_key:
        config["api_key"] = new_key


def _save_configuration(config: dict[str, str]) -> None:
    save_config(config)
    console.print(
        Text(f"\n✅ Configuration saved to: {CONFIG_FILE}", style=SUCCESS_STYLE)
    )


def _test_and_report_connection(config: dict[str, str]) -> None:
    console.print("\n🔌 Testing connection...")
    client: Client | None = None
    try:
        client = Client(api_url=config["api_url"], api_key=config["api_key"])
        try:
            agents = client.list_agents()
            console.print(
                Text(
                    f"✅ Connection successful! Found {len(agents)} agents",
                    style=SUCCESS_STYLE,
                )
            )
        except Exception as exc:  # pragma: no cover - API failures depend on network
            console.print(
                Text(
                    f"⚠️  Connection established but API call failed: {exc}",
                    style=WARNING_STYLE,
                )
            )
            console.print(
                "   You may need to check your API permissions or network access"
            )
    except Exception as exc:
        console.print(Text(f"❌ Connection failed: {exc}"))
        console.print("   Please check your API URL and key")
        hint_status = command_hint("status", slash_command="status")
        if hint_status:
            console.print(
                f"   You can run {format_command_hint(hint_status) or hint_status} later to test again"
            )
    finally:
        if client is not None:
            client.close()


def _print_post_configuration_hints() -> None:
    console.print("\n💡 You can now use AIP CLI commands!")
    hint_status = command_hint("status", slash_command="status")
    if hint_status:
        console.print(
            f"   • Run {format_command_hint(hint_status) or hint_status} to check connection"
        )
    hint_agents = command_hint("agents list", slash_command="agents")
    if hint_agents:
        console.print(
            f"   • Run {format_command_hint(hint_agents) or hint_agents} to see your agents"
        )
