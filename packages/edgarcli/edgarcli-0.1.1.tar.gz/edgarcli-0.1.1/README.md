# edgarcli

A CLI wrapper around [edgartools](https://github.com/dgunning/edgartools) by Dwight Gunning - access SEC EDGAR data from the command line.

## Installation

```bash
uvx edgarcli --help
```

## Quick Start

```bash
# Set your identity (required by SEC)
edgarcli config set-identity "Your Name your.email@example.com"

# Get company info
edgarcli company AAPL

# View recent filings
edgarcli filings AAPL --form 10-K --limit 5

# Get a specific filing
edgarcli filing AAPL --form 10-K --latest

# Get financial statements
edgarcli statements AAPL --form 10-Q --statement income

# Interactive mode - drop into Python REPL with edgar pre-configured
edgarcli -i
```

## Commands

- `config` - Manage configuration (identity, paths)
- `company` - Get company information by ticker/CIK
- `filing` - Get specific SEC filing(s)
- `filings` - List historical filings for a company
- `statements` - Get financial statements from filings

All commands support `--help` for detailed options.

## Interactive Mode

Use `edgarcli -i` to launch an IPython REPL with the edgar library pre-configured:

```bash
edgarcli -i
```

The interactive environment includes:
- Full `edgar` module access
- Identity automatically configured
- Convenient imports: `Company`, `Filing`, `Filings`, `get_filings`

Example session:
```python
>>> company = Company("AAPL")
>>> filings = company.get_filings(form="10-K")
>>> filing = filings.latest()
>>> filing.financials
```

## Configuration

Identity can be set via config file (`~/.config/edgarcli/config.json`), environment variable (`EDGAR_IDENTITY`), or `--identity` flag.

## Credits

Built on [edgartools](https://github.com/dgunning/edgartools) by Dwight Gunning.

## License

MIT
