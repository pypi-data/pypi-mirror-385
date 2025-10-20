"""Configuration commands for edgarcli."""

import click
from edgarcli.config import (
    get_config,
    set_config_value,
    get_config_path,
)


@click.group()
def config():
    """Manage edgarcli configuration."""
    pass


@config.command("set-identity")
@click.argument("identity")
def set_identity_cmd(identity):
    """Set default SEC EDGAR identity.

    IDENTITY should be in format: "Your Name your.email@example.com"

    Examples:
        edgarcli config set-identity "John Doe john@example.com"
        edgarcli config set-identity "john@example.com"
    """
    # Basic validation
    if "@" not in identity:
        raise click.BadParameter(
            "Identity must include an email address (e.g., 'Name email@example.com')"
        )

    set_config_value("identity", identity)
    click.echo(f"✓ Identity set to: {identity}")
    click.echo(f"✓ Saved to: {get_config_path()}")


@config.command("get-identity")
def get_identity_cmd():
    """Show current default identity."""
    config_data = get_config()
    identity = config_data.get("identity")

    if identity:
        click.echo(f"Current identity: {identity}")
        click.echo(f"Config file: {get_config_path()}")
    else:
        click.echo("No identity configured.")
        click.echo(f"Config file: {get_config_path()}")
        click.echo("\nSet identity with:")
        click.echo("  edgarcli config set-identity 'Name email@example.com'")


@config.command("show")
def show():
    """Show all configuration settings."""
    import json

    config_data = get_config()

    if config_data:
        click.echo(f"Configuration file: {get_config_path()}")
        click.echo("\nSettings:")
        click.echo(json.dumps(config_data, indent=2))
    else:
        click.echo("No configuration found.")
        click.echo(f"Config file would be: {get_config_path()}")


@config.command("path")
def path():
    """Show path to configuration file."""
    click.echo(get_config_path())
