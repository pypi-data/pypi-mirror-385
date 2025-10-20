"""Rich display utilities for enhanced output.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from typing import TYPE_CHECKING, Any

from glaip_sdk.branding import SUCCESS, SUCCESS_STYLE
from glaip_sdk.icons import ICON_AGENT

if TYPE_CHECKING:  # pragma: no cover - import-time typing helpers
    from rich.console import Console
    from rich.text import Text

    from glaip_sdk.rich_components import AIPPanel


def _check_rich_available() -> bool:
    """Check if Rich and our custom components can be imported."""
    try:
        __import__("rich.console")
        __import__("rich.text")
        __import__("glaip_sdk.rich_components")
        return True
    except Exception:
        return False


RICH_AVAILABLE = _check_rich_available()


def _create_console() -> "Console":
    """Return a Console instance with lazy import to ease mocking."""
    from rich.console import Console  # Local import for test friendliness

    return Console()


def _create_text(*args: Any, **kwargs: Any) -> "Text":
    """Return a Text instance with lazy import to ease mocking."""
    from rich.text import Text  # Local import for test friendliness

    return Text(*args, **kwargs)


def _create_panel(*args: Any, **kwargs: Any) -> "AIPPanel":
    """Return an AIPPanel instance with lazy import to ease mocking."""
    from glaip_sdk.rich_components import AIPPanel  # Local import for test friendliness

    return AIPPanel(*args, **kwargs)


def print_agent_output(output: str, title: str = "Agent Output") -> None:
    """Print agent output with rich formatting.

    Args:
        output: The agent's response text
        title: Title for the output panel
    """
    if RICH_AVAILABLE:
        console = _create_console()
        panel = _create_panel(
            _create_text(output, style=SUCCESS),
            title=title,
            border_style=SUCCESS,
        )
        console.print(panel)
    else:
        print(f"\n=== {title} ===")
        print(output)
        print("=" * (len(title) + 8))


def print_agent_created(agent: Any, title: str = f"{ICON_AGENT} Agent Created") -> None:
    """Print agent creation success with rich formatting.

    Args:
        agent: The created agent object
        title: Title for the output panel
    """
    if RICH_AVAILABLE:
        console = _create_console()
        panel = _create_panel(
            f"[{SUCCESS_STYLE}]✅ Agent '{agent.name}' created successfully![/]\n\n"
            f"ID: {agent.id}\n"
            f"Model: {getattr(agent, 'model', 'N/A')}\n"
            f"Type: {getattr(agent, 'type', 'config')}\n"
            f"Framework: {getattr(agent, 'framework', 'langchain')}\n"
            f"Version: {getattr(agent, 'version', '1.0')}",
            title=title,
            border_style=SUCCESS,
        )
        console.print(panel)
    else:
        print(f"✅ Agent '{agent.name}' created successfully!")
        print(f"ID: {agent.id}")
        print(f"Model: {getattr(agent, 'model', 'N/A')}")
        print(f"Type: {getattr(agent, 'type', 'config')}")
        print(f"Framework: {getattr(agent, 'framework', 'langchain')}")
        print(f"Version: {getattr(agent, 'version', '1.0')}")


def print_agent_updated(agent: Any) -> None:
    """Print agent update success with rich formatting.

    Args:
        agent: The updated agent object
    """
    if RICH_AVAILABLE:
        console = _create_console()
        console.print(
            f"[{SUCCESS_STYLE}]✅ Agent '{agent.name}' updated successfully[/]"
        )
    else:
        print(f"✅ Agent '{agent.name}' updated successfully")


def print_agent_deleted(agent_id: str) -> None:
    """Print agent deletion success with rich formatting.

    Args:
        agent_id: The deleted agent's ID
    """
    if RICH_AVAILABLE:
        console = _create_console()
        console.print(
            f"[{SUCCESS_STYLE}]✅ Agent deleted successfully (ID: {agent_id})[/]"
        )
    else:
        print(f"✅ Agent deleted successfully (ID: {agent_id})")
