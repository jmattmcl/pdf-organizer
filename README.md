# pdf-organizer

A CLI tool that scans a folder for PDFs, classifies them by document type, extracts institution names and dates, renames them intelligently, and logs all renames to CSV.

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```bash
# Preview renames without changing files
pdf-organizer --dry-run ./my-pdfs/

# Rename files and write log to rename_log.csv
pdf-organizer ./my-pdfs/

# Specify a custom CSV log path
pdf-organizer ./my-pdfs/ --output-csv results.csv
```

### Options

| Option | Description |
|---|---|
| `--dry-run` | Preview renames without modifying files |
| `--output-csv PATH` | CSV log path (default: `rename_log.csv`) |

## How It Works

### Document Classification

Files are classified into one of these types based on keyword matching:

- **Tax_Return** — 1040, W-2, W-4, IRS, adjusted gross
- **Bank_Statement** — statement, account summary, balance, deposits, withdrawals
- **Insurance** — policy, premium, coverage, deductible, insured
- **Invoice** — invoice, bill to, amount due, payment due
- **Receipt** — receipt, paid, transaction
- **Medical** — patient, diagnosis, prescription, medical, health
- **Contract** — agreement, terms and conditions, hereby, parties
- **Unknown** — fallback when no type matches

### Institution Detection

The first ~500 characters are scanned against a built-in list of known institutions (Chase, Bank of America, Wells Fargo, IRS, Aetna, etc.). If none match, a heuristic extracts the first capitalized multi-word phrase as a likely company name.

### Date Extraction

Dates are extracted via regex in these formats:

- `MM/DD/YYYY`, `MM-DD-YYYY`
- `Month DD, YYYY` (e.g., January 15, 2024)
- `YYYY-MM-DD`

When multiple dates are found, the most recent one is used. All dates are normalized to `YYYY-MM-DD`.

### Rename Format

```
{Type}_{Institution}_{Date}.pdf
```

- Institution and date segments are omitted when unknown
- Special characters are removed, spaces become underscores
- Collisions are resolved by appending `_2`, `_3`, etc.

### CSV Log

Columns: `original_name`, `new_name`, `doc_type`, `institution`, `date`

## Project Structure

```
pdf-organizer/
├── pyproject.toml
├── requirements.txt
├── src/
│   └── pdf_organizer/
│       ├── cli.py          # Click CLI entry point
│       ├── extractor.py    # PDF text extraction (pdfplumber)
│       ├── classifier.py   # Document type + institution + date detection
│       └── renamer.py      # File renaming + CSV logging
└── tests/
    ├── conftest.py
    ├── test_classifier.py
    ├── test_renamer.py
    └── test_cli.py
```

## Running Tests

```bash
pytest tests/
```
