"""Company lookup commands."""

import click
from edgar import Company
from rich import print as rprint
from edgarcli.config import ensure_identity
from edgarcli.utils import handle_edgar_error


@click.command()
@click.argument("ticker_or_cik")
@click.pass_context
@handle_edgar_error
def company(ctx, ticker_or_cik):
    """Get company information by ticker or CIK.

    TICKER_OR_CIK can be:
      - Ticker symbol (e.g., AAPL, MSFT)
      - CIK number (e.g., 320193 or 0000320193)

    Examples:
        edgarcli company AAPL
        edgarcli company 320193
    """
    ensure_identity(ctx)

    # Look up company
    comp = Company(ticker_or_cik)

    # Display company info with Rich formatting
    rprint(comp)
