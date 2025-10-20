"""Financial statements commands."""

import click
from edgar import Company, Filing, Filings, get_filings, set_identity, get_identity
from rich import print as rprint
from edgarcli.config import ensure_identity
from edgarcli.utils import handle_edgar_error


STATEMENT_TYPES = ["income", "balance", "cashflow", "all"]


@click.command()
@click.argument("ticker_or_cik", required=False)
@click.option(
    "-a", "--accession-number",
    type=str,
    help="Get statements from specific filing by accession number",
)
@click.option(
    "-f", "--form",
    type=str,
    help="Form type (e.g., 10-K, 10-Q, 20-F). Defaults to 10-Q if not specified with --accession",
)
@click.option(
    "--latest",
    is_flag=True,
    default=True,
    help="Get statements from latest filing (default behavior)",
)
@click.option(
    "-s", "--statement",
    type=click.Choice(STATEMENT_TYPES, case_sensitive=False),
    default="income",
    help="Statement type (income, balance, cashflow, all)",
)
@click.pass_context
@handle_edgar_error
def statements(ctx, ticker_or_cik, accession_number, form, latest, statement):
    """Get financial statements from SEC filings.

    You can retrieve statements in two ways:

    1. By accession number alone:
       edgarcli statements --accession-number 0001234567-23-000001

    2. Latest filing by ticker/CIK and form:
       edgarcli statements AAPL --form 10-K --latest

    Examples:
        # Latest 10-Q income statement (default)
        edgarcli statements AAPL

        # Latest 10-K balance sheet
        edgarcli statements AAPL --form 10-K --statement balance

        # All statements from latest 20-F
        edgarcli statements TSM --form 20-F --statement all

        # Specific filing by accession
        edgarcli statements --accession-number 0001234567-23-000001
    """
    ensure_identity(ctx)

    # Validate argument/option combinations
    if accession_number:
        # Pattern 1: By accession number
        if ticker_or_cik:
            raise click.UsageError(
                "Cannot specify both TICKER_OR_CIK and --accession-number.\n"
                "Use: edgarcli statements --accession-number <accession>"
            )

        # Get filing by accession number
        filing_obj = _get_filing_by_accession(accession_number)

    elif ticker_or_cik:
        # Pattern 2: By ticker/CIK + form (latest)
        if not form:
            form = "10-Q"  # Default to 10-Q for backwards compatibility

        # Get company
        comp = Company(ticker_or_cik)

        # Get latest filing of specified form
        filings = comp.get_filings(form=form)
        if not filings or len(filings) == 0:
            raise click.ClickException(
                f"No {form} filings found for {comp.name} (CIK: {comp.cik})"
            )

        filing_obj = filings.latest(1)

    else:
        # No arguments provided
        raise click.UsageError(
            "Must provide either TICKER_OR_CIK or --accession-number.\n\n"
            "Examples:\n"
            "  edgarcli statements AAPL\n"
            "  edgarcli statements AAPL --form 10-K\n"
            "  edgarcli statements --accession-number 0001234567-23-000001"
        )

    # Display filing info
    click.echo(f"Financial Statements from {filing_obj.form} Filing")
    click.echo(f"Company: {filing_obj.company}")
    click.echo("=" * 80 + "\n")
    click.echo(f"Form: {filing_obj.form}")
    click.echo(f"Filing Date: {filing_obj.filing_date}")
    if hasattr(filing_obj, 'report_date') and filing_obj.report_date:
        click.echo(f"Report Date: {filing_obj.report_date}")
    click.echo()

    # Get financials (may be None for forms without XBRL data)
    # EntityFiling objects need .obj() to access the form-specific object with financials
    try:
        filing_data = filing_obj.obj() if hasattr(filing_obj, 'obj') else filing_obj
        financials = filing_data.financials if hasattr(filing_data, 'financials') else None
    except Exception:
        financials = None

    if not financials:
        click.echo(f"⚠️  This {filing_obj.form} filing does not contain financial statements.")
        click.echo("Financial statements are typically only available in forms like 10-K, 10-Q, and 20-F.")
        click.echo("\nTo view the full filing content, use:")
        click.echo(f"  edgarcli filing --accession-number {filing_obj.accession_no} --text")
        return

    # Display requested statement(s)
    statement_lower = statement.lower()

    if statement_lower == "income" or statement_lower == "all":
        click.echo("\nINCOME STATEMENT")
        click.echo("-" * 80)
        try:
            rprint(financials.income_statement())
        except Exception as e:
            click.echo(f"⚠️  Income statement not available: {e}")
        click.echo()

    if statement_lower == "balance" or statement_lower == "all":
        click.echo("\nBALANCE SHEET")
        click.echo("-" * 80)
        try:
            rprint(financials.balance_sheet())
        except Exception as e:
            click.echo(f"⚠️  Balance sheet not available: {e}")
        click.echo()

    if statement_lower == "cashflow" or statement_lower == "all":
        click.echo("\nCASH FLOW STATEMENT")
        click.echo("-" * 80)
        try:
            rprint(financials.cash_flow_statement())
        except Exception as e:
            click.echo(f"⚠️  Cash flow statement not available: {e}")
        click.echo()


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
