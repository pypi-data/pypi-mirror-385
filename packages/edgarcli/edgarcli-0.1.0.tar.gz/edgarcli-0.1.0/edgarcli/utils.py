"""Utility functions for edgarcli."""

import sys
from functools import wraps
from typing import Any, Optional

import click
from edgar import Company, Filing


def handle_edgar_error(func):
    """Decorator to handle common edgar API errors.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except click.UsageError:
            # Re-raise UsageError as-is for Click to handle
            raise
        except ValueError as e:
            error_msg = str(e)
            if "ticker" in error_msg.lower() or "cik" in error_msg.lower():
                raise click.ClickException(
                    f"Company not found: {error_msg}\n\n"
                    "Please check that:\n"
                    "  - Ticker symbol is correct (e.g., AAPL, MSFT)\n"
                    "  - CIK number is valid (e.g., 320193 or 0000320193)"
                )
            else:
                raise click.ClickException(f"Invalid input: {e}")
        except ConnectionError as e:
            raise click.ClickException(
                f"Network error: {e}\n\n"
                "Please check your internet connection and try again.\n"
                "If the problem persists, the SEC EDGAR system may be down."
            )
        except PermissionError as e:
            raise click.ClickException(
                f"Permission error: {e}\n\n"
                "The SEC may have rate-limited your requests.\n"
                "Please wait a few minutes and try again."
            )
        except Exception as e:
            # Catch-all for unexpected errors
            error_type = type(e).__name__
            raise click.ClickException(
                f"Unexpected error ({error_type}): {e}\n\n"
                "Please report this issue at:\n"
                "https://github.com/yourusername/edgarcli/issues"
            )

    return wrapper


def launch_interactive_repl(banner: str, local_vars: dict) -> None:
    """Launch IPython REPL with given context.

    Args:
        banner: Welcome banner to display
        local_vars: Variables to inject into REPL namespace
    """
    try:
        from IPython import embed
        embed(banner1=banner, user_ns=local_vars, colors="neutral")
    except ImportError:
        # Fallback to standard Python REPL if IPython not available
        import code
        code.interact(banner=banner, local=local_vars)


def maybe_interactive(ctx: click.Context, result: Any, type_name: str) -> None:
    """Check if interactive mode requested and launch REPL.

    Args:
        ctx: Click context
        result: Result object to inject into REPL
        type_name: Name of the result type for banner message
    """
    if ctx.obj.get("interactive"):
        from edgar import (
            Company, Filing, Filings, get_filings,
            set_identity, get_identity
        )

        banner = f"""
edgarcli Interactive Mode
=========================
The {type_name} is available as: result

Available imports:
  - Company, Filing, Filings, get_filings
  - set_identity, get_identity

Example:
  result  # View the result object
  help(result)  # Get help on result methods
"""

        local_vars = {
            "result": result,
            "Company": Company,
            "Filing": Filing,
            "Filings": Filings,
            "get_filings": get_filings,
            "set_identity": set_identity,
            "get_identity": get_identity,
        }

        launch_interactive_repl(banner, local_vars)
