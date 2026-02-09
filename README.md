# Web Content Integrity Monitor

A tool that archives web pages as Markdown and **detects content changes via daily snapshot comparison**.  
It takes a URL list (CSV), fetches HTML, cleans and converts it, then stores date-stamped archives and compares today’s archive with N days ago to output a list of modified pages.

---

## Features

| Component | Description |
|-----------|-------------|
| **html2md** | Fetches HTML from URLs in the CSV, extracts main content, converts to Markdown (.md), and creates a tar.gz archive with a timestamp for the run |
| **diffcheck** | Extracts today’s and N-days-ago archives, normalizes body content, compares them, and prints title and URL of changed pages |

---

## Requirements

- **Python 3.10+**
- Dependencies: `beautifulsoup4`, `requests`  
  (`pytest` for running tests)

**Install (Conda):**

```bash
conda env create -f environment.yml
conda activate html-converter
```

**Install (pip):**

```bash
pip install -r requirements.txt
```

---

## Usage

### 1. Input CSV format

Three columns separated by pipe (`|`):

```
Title|URL|Date (YYYY-MM-DD)
```

Example:

```
Python (programming language)|https://en.wikipedia.org/wiki/Python_(programming_language)|2025-02-09
Web scraping|https://en.wikipedia.org/wiki/Web_scraping|2025-02-09
```

- Rows with a **date** later than today are skipped.

### 2. Fetch and archive (html2md)

```bash
./html2md <csv_file> <output_dir>
```

- Archives are written under `output_dir` as `YYYY-MM-DD_HH-MM-SS.tar.gz`.
- Each archive contains the converted `.md` files (filenames derived from titles).

**Example:**

```bash
./html2md sample_input.csv ./output
# Converted: Python (programming language) -> python_programming_language.md
# Archive created: ./output/2025-02-09_14-30-00.tar.gz
```

### 3. Compare changes over N days (diffcheck)

```bash
./diffcheck <N> <output_dir>
```

- Finds archives for **today** and **N days ago** in `output_dir` and compares them.
- Only pages present in both (same filename) are compared; only those with changed body text are printed.

**Example:**

```bash
./diffcheck 7 ./output
# The following web pages have been modified in the last 7 days:
# - Python (programming language) (https://en.wikipedia.org/wiki/...)
```

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with sample CSV (network required for real Wikipedia URLs)
./html2md sample_input.csv ./output

# Compare today vs 7 days ago (archives for those dates must exist)
./diffcheck 7 ./output
```

**Using the Makefile:**

```bash
make crawl      # html2md sample_input.csv output
make diff N=7   # diffcheck 7 output
```

---

## Scheduled runs with Cron

Running `html2md` at the same time every day builds daily snapshots; use `diffcheck` to see which pages changed in the last N days.

Example (see `cronjob.txt`):

```cron
30 03 * * * /usr/bin/python3 /path/to/html2md /path/to/input.csv /path/to/output_dir >> /path/to/downloads.log 2>&1
```

---

## Project structure

```
.
├── html2md           # Crawling + HTML→MD conversion + archiving
├── diffcheck         # Compare N-days-ago vs today archives
├── environment.yml   # Conda environment
├── requirements.txt  # pip dependencies
├── sample_input.csv  # Sample URL list
├── cronjob.txt       # Cron example
├── Makefile          # crawl / diff targets
├── docs/
│   └── DESIGN.md     # Design and technical notes
└── tests/
    ├── fixtures/     # minimal_mw.html for local tests
    ├── test_diffcheck.py
    └── test_html2md.py
```

---

## Tests

```bash
pytest tests/ -v
```

---

## License / Purpose

For education and portfolio use. When scraping real sites, respect their terms of use and robots.txt.
