"""Filing retrieval commands."""

import click
from edgar import Company, Filing
from rich import print as rprint
from rich.console import Console
from edgarcli.config import ensure_identity
from edgarcli.utils import handle_edgar_error


@click.command()
@click.argument("ticker_or_cik", required=False)
@click.option(
    "-a", "--accession-number",
    type=str,
    help="Get filing by accession number (e.g., 0001234567-23-000001)",
)
@click.option(
    "-f", "--form",
    type=str,
    help="Form type (e.g., 10-K, 10-Q, 8-K, Form 4, 20-F)",
)
@click.option(
    "--latest",
    is_flag=True,
    help="Get the latest filing of specified form type",
)
@click.option(
    "-n",
    type=int,
    help="Get N most recent filings of specified form type",
)
@click.option(
    "-t", "--text",
    is_flag=True,
    help="Display filing text content",
)
@click.pass_context
@handle_edgar_error
def filing(ctx, ticker_or_cik, accession_number, form, latest, n, text):
    """Get SEC filings with flexible access patterns.

    You can retrieve filings in three ways:

    1. By accession number alone (no ticker needed):
       edgarcli filing --accession-number 0001234567-23-000001

    2. Latest filing by ticker/CIK and form:
       edgarcli filing AAPL --form 10-K --latest

    3. Multiple filings by ticker/CIK and form:
       edgarcli filing TSLA --form 10-Q -n 5

    Examples:
        # Get specific filing by accession number
        edgarcli filing --accession-number 0001640147-22-000100

        # Get latest 10-K for Apple
        edgarcli filing AAPL --form 10-K --latest

        # Get latest 5 quarterly reports for Tesla
        edgarcli filing TSLA --form 10-Q -n 5

        # Show text instead of just metadata
        edgarcli filing AAPL --form 10-K --latest --text
    """
    ensure_identity(ctx)

    # Validate argument/option combinations
    if accession_number:
        # Pattern 1: By accession number
        if ticker_or_cik:
            raise click.UsageError(
                "Cannot specify both TICKER_OR_CIK and --accession-number.\n"
                "Use: edgarcli filing --accession-number <accession>"
            )
        if form or latest or n:
            raise click.UsageError(
                "Cannot use --form, --latest, or -n with --accession-number.\n"
                "Accession number uniquely identifies a filing."
            )

        # Get filing by accession number
        filing_obj = _get_filing_by_accession(accession_number)
        _display_filing(filing_obj, text)

    elif ticker_or_cik:
        # Pattern 2 & 3: By ticker/CIK + form
        if not form:
            raise click.UsageError(
                "Must specify --form when using TICKER_OR_CIK.\n"
                "Example: edgarcli filing AAPL --form 10-K --latest"
            )
        if not latest and not n:
            raise click.UsageError(
                "Must specify either --latest or -n with TICKER_OR_CIK and --form.\n"
                "Examples:\n"
                "  edgarcli filing AAPL --form 10-K --latest\n"
                "  edgarcli filing AAPL --form 10-Q -n 5"
            )
        if latest and n:
            raise click.UsageError(
                "Cannot use both --latest and -n together.\n"
                "Use --latest for one filing or -n N for multiple filings."
            )

        # Get company
        comp = Company(ticker_or_cik)

        if latest:
            # Pattern 2: Latest filing
            filings = comp.get_filings(form=form)
            if not filings or len(filings) == 0:
                raise click.ClickException(
                    f"No {form} filings found for {comp.name} (CIK: {comp.cik})"
                )
            filing_obj = filings.latest(1)
            _display_filing(filing_obj, text)

        else:  # n is specified
            # Pattern 3: N filings
            filings = comp.get_filings(form=form)
            if not filings or len(filings) == 0:
                raise click.ClickException(
                    f"No {form} filings found for {comp.name} (CIK: {comp.cik})"
                )

            latest_n = filings.latest(n)

            # Display header
            click.echo(f"Latest {n} {form} filings for {comp.name} (CIK: {comp.cik})")
            click.echo("=" * 80 + "\n")

            # Handle single filing vs collection
            if hasattr(latest_n, '__iter__') and not isinstance(latest_n, str):
                # It's a collection
                for idx, filing_obj in enumerate(latest_n, 1):
                    click.echo(f"\n[{idx}] Filing Date: {filing_obj.filing_date}")
                    click.echo(f"    Accession: {filing_obj.accession_no}")
                    click.echo(f"    Form: {filing_obj.form}")
                    if text:
                        click.echo("-" * 80)
                        _display_filing_content(filing_obj)
            else:
                # Single filing
                _display_filing(latest_n, text)

    else:
        # No arguments provided
        raise click.UsageError(
            "Must provide either TICKER_OR_CIK or --accession-number.\n\n"
            "Examples:\n"
            "  edgarcli filing --accession-number 0001234567-23-000001\n"
            "  edgarcli filing AAPL --form 10-K --latest\n"
            "  edgarcli filing TSLA --form 10-Q -n 5"
        )


def _get_filing_by_accession(accession_number: str):
    """Get a filing by accession number.

    Note: edgar-tools doesn't have a direct method to get filing by accession
    without knowing the CIK. We extract CIK from the accession number.
    Accession format: XXXXXXXXXX-YY-ZZZZZZ where X is CIK.
    """
    try:
        # Extract CIK from accession number (first part before dash)
        cik = accession_number.split("-")[0]

        # Get company and find filing
        comp = Company(int(cik))
        filings = comp.get_filings(accession_number=accession_number)

        if not filings or len(filings) == 0:
            raise click.ClickException(
                f"Filing not found: {accession_number}\n"
                f"Company: {comp.name} (CIK: {comp.cik})"
            )

        # Return the first (should be only) matching filing
        return filings[0]

    except (ValueError, IndexError) as e:
        raise click.ClickException(
            f"Invalid accession number format: {accession_number}\n"
            f"Expected format: 0001234567-23-000001"
        )


def _display_filing(filing_obj, show_content: bool = False):
    """Display a single filing's metadata and optionally its content."""
    # Display filing metadata with Rich formatting
    rprint(filing_obj)

    # Show content if requested
    if show_content:
        click.echo("\n" + "=" * 80)
        click.echo("FILING CONTENT")
        click.echo("=" * 80 + "\n")
        _display_filing_content(filing_obj)


def _display_filing_content(filing_obj: Filing):
    """Display filing content with constrained width."""
    try:
        # Get filing text and print with width constraint
        text_content = filing_obj.text()
        click.echo(text_content)
    except Exception as e:
        # Fallback to click.echo if there's an error
        click.echo(f"Error displaying filing content: {e}")
