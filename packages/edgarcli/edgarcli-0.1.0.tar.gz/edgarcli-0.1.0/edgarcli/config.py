"""Configuration management for edgarcli."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import click


def get_config_dir() -> Path:
    """Get XDG config directory for edgarcli.

    Returns:
        Path to ~/.config/edgarcli/ (or XDG_CONFIG_HOME override)
    """
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        base_dir = Path(xdg_config)
    else:
        base_dir = Path.home() / ".config"

    config_dir = base_dir / "edgarcli"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """Get path to config.json file.

    Returns:
        Path to config.json
    """
    return get_config_dir() / "config.json"


def get_config() -> Dict[str, Any]:
    """Read configuration from disk.

    Returns:
        Configuration dict (empty if file doesn't exist)
    """
    config_path = get_config_path()

    if not config_path.exists():
        return {}

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        click.echo(f"Warning: Could not read config file: {e}", err=True)
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """Write configuration to disk.

    Args:
        config: Configuration dict to save
    """
    config_path = get_config_path()

    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    except OSError as e:
        raise click.ClickException(f"Could not write config file: {e}")


def set_config_value(key: str, value: Any) -> None:
    """Set a single configuration value.

    Args:
        key: Configuration key
        value: Value to set
    """
    config = get_config()
    config[key] = value
    save_config(config)


def get_config_value(key: str, default: Any = None) -> Any:
    """Get a single configuration value.

    Args:
        key: Configuration key
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    config = get_config()
    return config.get(key, default)


def ensure_identity(ctx: click.Context) -> str:
    """Ensure identity is configured.

    Args:
        ctx: Click context

    Returns:
        Identity string

    Raises:
        click.UsageError: If identity not configured
    """
    identity = ctx.obj.get("identity")

    if not identity:
        raise click.UsageError(
            "SEC EDGAR identity not configured.\n\n"
            "Please set your identity using one of:\n"
            "  1. edgarcli config set-identity 'Your Name your.email@example.com'\n"
            "  2. export EDGAR_IDENTITY='Your Name your.email@example.com'\n"
            "  3. --identity 'Your Name your.email@example.com' flag\n\n"
            "The SEC requires this information for API access."
        )

    return identity
