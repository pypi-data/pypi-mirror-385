"""Configuration management utilities.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import os
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path.home() / ".aip"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
_ALLOWED_KEYS = {"api_url", "api_key", "timeout"}


def _sanitize_config(data: dict[str, Any] | None) -> dict[str, Any]:
    """Return config filtered to allowed keys only."""
    if not data:
        return {}
    return {k: v for k, v in data.items() if k in _ALLOWED_KEYS}


def load_config() -> dict[str, Any]:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE) as f:
            loaded = yaml.safe_load(f) or {}
            return _sanitize_config(loaded)
    except yaml.YAMLError:
        return {}


def save_config(config: dict[str, Any]) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(exist_ok=True)

    sanitized = _sanitize_config(config)

    with open(CONFIG_FILE, "w") as f:
        yaml.dump(sanitized, f, default_flow_style=False)

    # Set secure file permissions
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except (
        OSError
    ):  # pragma: no cover - permission errors are expected in some environments
        pass
