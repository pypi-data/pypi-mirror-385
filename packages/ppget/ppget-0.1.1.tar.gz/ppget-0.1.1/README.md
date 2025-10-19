# ppget

**A simple CLI tool to easily download PubMed articles**

[日本語版README](README_ja.md) | [English](README.md)

`ppget` is a command-line tool for searching and downloading literature data from PubMed. Unlike [EDirect](https://www.ncbi.nlm.nih.gov/books/NBK179288/), which requires complex setup, **you can start using it immediately**.

## ✨ Features

- 🚀 **No installation required** - Run instantly with `uvx`
- 📝 **CSV/JSON support** - Easy to use in spreadsheets or programs
- 🔍 **Flexible search** - Full support for PubMed search syntax (AND, OR, MeSH, etc.)
- 📊 **Automatic metadata** - Automatically records search queries and timestamps
- 🎯 **Simple API** - Clear and intuitive options

## 🚀 Quick Start

### Run without installation (Recommended)

If you have [uv](https://github.com/astral-sh/uv) installed, **you can run it instantly without installation**:

```bash
# Basic usage
uvx ppget "machine learning AND medicine"

# Specify number of results
uvx ppget "COVID-19 vaccine" -l 50

# Save as JSON
uvx ppget "cancer immunotherapy" -f json
```

### Install and use

For frequent use, you can install it:

```bash
# Install with pip
pip install ppget

# Install with uv
uv tool install ppget

# Run
ppget "your search query"
```

## 📖 Usage

### Basic usage

```bash
# Simple search (CSV format by default, up to 100 results)
ppget "diabetes treatment"

# Example output:
# Searching PubMed...
# Query: 'diabetes treatment'
# Max results: 100
# ✓ Found 100 articles
# ✓ Saved 100 articles to pubmed_20251018_143022.csv
# ✓ Metadata saved to pubmed_20251018_143022.meta.txt
```

### Options

```bash
ppget [query] [options]

Required:
  query                 Search query

Options:
  -l, --limit          Maximum number of results (default: 100)
  -o, --output         Output file or directory
  -f, --format         Output format: csv or json (default: csv)
  -e, --email          Email address (for API rate limit relaxation)
  -q, --quiet          Suppress progress messages (errors only)
  -v, --version        Show version and exit
  -h, --help           Show help message
```

### Advanced usage

#### 1. Change number of results

```bash
# Retrieve up to 200 results
ppget "machine learning healthcare" -l 200
```

#### 2. Specify output format

```bash
# Save as JSON
ppget "spine surgery" -f json

# Default is CSV (can be opened in Excel)
ppget "orthopedics" -f csv
```

#### 3. Specify filename

```bash
# Specify file path directly
ppget "cancer research" -o results/cancer_papers.csv

# Specify directory (filename is auto-generated)
ppget "neuroscience" -o ./data/

# Extension determines format
ppget "cardiology" -o heart_disease.json
```

#### 4. Specify email address (API rate limit relaxation)

NCBI's API has relaxed limits when you provide an email address:

```bash
ppget "genomics" -e your.email@example.com -l 500
```

#### 5. Use PubMed search syntax

```bash
# AND search
ppget "machine learning AND radiology"

# OR search
ppget "COVID-19 OR SARS-CoV-2"

# MeSH term search
ppget "Diabetes Mellitus[MeSH] AND Drug Therapy[MeSH]"

# Filter by year
ppget "cancer immunotherapy AND 2024[PDAT]"

# Search by author
ppget "Smith J[Author]"

# Complex search
ppget "(machine learning OR deep learning) AND (radiology OR imaging) AND 2023:2024[PDAT]"
```

## 📁 Output Format

### CSV format (default)

Easy to open in spreadsheets. A metadata file (`.meta.txt`) is also generated.

```
pubmed_20251018_143022.csv          # Article data
pubmed_20251018_143022.meta.txt     # Search metadata
```

**CSV columns:**
- `pubmed_id` - PubMed ID
- `title` - Title
- `abstract` - Abstract
- `journal` - Journal name
- `publication_date` - Publication date
- `doi` - DOI
- `authors` - Author list (semicolon-separated)
- `keywords` - Keywords (semicolon-separated)
- `conclusions` - Conclusions
- `methods` - Methods
- `results` - Results
- `copyrights` - Copyright information

### JSON format

Easy to process programmatically.

```json
[
  {
    "pubmed_id": "12345678",
    "title": "...",
    "abstract": "...",
    ...
  }
]
```

**Metadata file (.meta.txt):**
```
Query: machine learning
Search Date: 2025-10-18 14:30:22
Retrieved Results: 100
Data File: pubmed_20251018_143022.json
```

## 🆚 Comparison with EDirect

| Feature | ppget | EDirect |
|---------|------|---------|
| Installation | Not required (`uvx` instant run) | Complex setup required |
| Ease of use | Single command | Multiple command combinations |
| Output format | CSV/JSON | XML/Text |
| Metadata | Automatic | Manual management |
| Learning curve | Low | High |

### EDirect example (complex)

```bash
# Search with EDirect (multiple steps required)
esearch -db pubmed -query "machine learning" | \
efetch -format abstract | \
xtract -pattern PubmedArticle -element MedlineCitation/PMID,ArticleTitle
```

### ppget example (simple)

```bash
# With ppget, just one command
ppget "machine learning"
```

## 💡 Use Cases

### Collecting research papers

```bash
# Collect latest papers on a specific topic
ppget "CRISPR gene editing" -l 100 -o crispr_papers.csv

# Run multiple searches at once
ppget "diabetes treatment 2024[PDAT]" -o diabetes_2024.csv
ppget "cancer immunotherapy 2024[PDAT]" -o cancer_2024.csv
```

### For data analysis

```bash
# Retrieve in JSON format and analyze with Python
ppget "artificial intelligence healthcare" -f json -l 500 -o ai_health.json

# Example Python code to read
import json
with open('ai_health.json') as f:
    data = json.load(f)
    # Analysis...
```

### Literature review

```bash
# Retrieve in CSV and manage in Excel
ppget "systematic review AND meta-analysis" -l 200 -o reviews.csv

# → Open in Excel and review titles and abstracts
```

## 🤝 Contributing

Bug reports and feature requests are welcome at [Issues](https://github.com/masaki39/ppget/issues).

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

This tool uses [pymed-paperscraper](https://github.com/nils-herrmann/pymed-paperscraper).

---

**Start searching PubMed easily and quickly!**

```bash
uvx ppget "your research topic"
```
