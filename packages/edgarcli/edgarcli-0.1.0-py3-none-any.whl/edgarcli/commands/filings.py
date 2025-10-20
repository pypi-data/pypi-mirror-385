"""Historical filings commands."""

import click
from edgar import Company
from rich import print as rprint
from edgarcli.config import ensure_identity
from edgarcli.utils import handle_edgar_error


@click.command()
@click.argument("ticker_or_cik")
@click.option(
    "-f", "--form",
    help="Filter by form type (e.g., 10-K, 10-Q, 8-K)",
)
@click.option(
    "-l", "--limit",
    type=int,
    default=20,
    help="Number of filings to display (default: 20)",
)
@click.option(
    "--latest",
    is_flag=True,
    help="Show only the most recent filing",
)
@click.pass_context
@handle_edgar_error
def filings(ctx, ticker_or_cik, form, limit, latest):
    """List historical filings for a company.

    TICKER_OR_CIK can be:
      - Ticker symbol (e.g., AAPL, MSFT)
      - CIK number (e.g., 320193)

    Examples:
        edgarcli filings AAPL
        edgarcli filings AAPL --form 10-K
        edgarcli filings AAPL --form 10-Q --limit 10
        edgarcli filings TSLA --latest
    """
    ensure_identity(ctx)

    # Look up company
    comp = Company(ticker_or_cik)

    click.echo(f"Filings for {comp.name} (CIK: {comp.cik})")
    click.echo("=" * 80 + "\n")

    # Get filings with optional form filter
    if form:
        filings_list = comp.get_filings(form=form)
        click.echo(f"Form type: {form}")
    else:
        filings_list = comp.get_filings()
        click.echo("All forms")

    # Apply latest filter if requested
    if latest:
        filings_list = filings_list.latest(1)
        click.echo("\nShowing: Latest filing")
    else:
        filings_list = filings_list.latest(limit)
        click.echo(f"\nShowing: {limit} most recent filings")

    click.echo()

    # Display filings with Rich formatting
    rprint(filings_list)

    # Show summary
    click.echo(f"\n{len(filings_list)} filing(s) displayed")
