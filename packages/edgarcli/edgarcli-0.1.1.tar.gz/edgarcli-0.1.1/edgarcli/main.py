"""Main CLI entry point for edgarcli."""

import click
from edgar import set_identity, get_identity
from edgarcli import __version__
from edgarcli.config import get_config, ensure_identity
from edgarcli.commands import company, filing, filings, statements
from edgarcli.commands import config as config_cmd
from edgarcli.utils import launch_interactive_repl


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="edgarcli")
@click.option(
    "--identity",
    envvar="EDGAR_IDENTITY",
    help="SEC EDGAR identity (Name email@example.com)",
)
@click.option(
    "-i", "--interactive",
    is_flag=True,
    help="Launch interactive Python REPL with edgar pre-configured",
)
@click.pass_context
def cli(ctx, identity, interactive):
    """edgarcli - CLI wrapper for SEC EDGAR data access.

    Provides command-line access to SEC filings, company information,
    and financial statements via the edgartools library.
    """
    ctx.ensure_object(dict)

    # Set identity from flag, config, or environment
    if identity:
        set_identity(identity)
        ctx.obj["identity"] = identity
    else:
        # Try to load from config
        config = get_config()
        if config.get("identity"):
            set_identity(config["identity"])
            ctx.obj["identity"] = config["identity"]
        else:
            ctx.obj["identity"] = None

    ctx.obj["interactive"] = False

    # Show help if no subcommand provided and not in interactive mode
    if ctx.invoked_subcommand is None and not interactive:
        click.echo(ctx.get_help())
        ctx.exit()

    # Handle standalone interactive mode
    if interactive:
        if ctx.invoked_subcommand is not None:
            raise click.UsageError(
                "Interactive mode (-i) should be used standalone, not with other commands.\n"
                "Usage: edgarcli -i"
            )

        # Ensure identity is set
        ensure_identity(ctx)

        # Launch interactive REPL with edgar pre-configured
        import edgar

        banner = """
edgarcli Interactive Mode
==========================
Edgar library loaded and identity configured.

Available modules and functions:
  - edgar (full module access)
  - Company, Filing, Filings, get_filings
  - set_identity, get_identity

Examples:
  edgar.Company("AAPL")
  edgar.get_filings(form="10-K")
  company = edgar.Company("TSLA")
  filings = company.get_filings(form="10-Q")
"""

        local_vars = {
            "edgar": edgar,
            "Company": edgar.Company,
            "Filing": edgar.Filing,
            "Filings": edgar.Filings,
            "get_filings": edgar.get_filings,
            "set_identity": edgar.set_identity,
            "get_identity": edgar.get_identity,
        }

        launch_interactive_repl(banner, local_vars)
        ctx.exit()


# Register command groups
cli.add_command(config_cmd.config)
cli.add_command(company.company)
cli.add_command(filing.filing)
cli.add_command(filings.filings)
cli.add_command(statements.statements)


if __name__ == "__main__":
    cli()
