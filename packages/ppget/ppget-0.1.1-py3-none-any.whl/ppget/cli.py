import json
import csv
import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from pymed_paperscraper import PubMed

# Suppress debug logs from urllib3
logging.getLogger("urllib3").setLevel(logging.WARNING)


def search_pubmed(query: str, max_results: int = 100, email: str = "anonymous@example.com", quiet: bool = False) -> list[dict]:
    """
    Search PubMed and retrieve article data.

    Args:
        query: Search query
        max_results: Maximum number of results to retrieve
        email: Email address (for API rate limit relaxation)
        quiet: If True, suppress progress messages

    Returns:
        List of article data dictionaries
    """
    pubmed = PubMed(tool="pget", email=email)

    results = pubmed.query(query, max_results=max_results)

    articles = []
    for article in results:
        # Extract DOI - pymed-paperscraper has a bug where it includes reference DOIs
        # We only want the first DOI which is the article's own DOI
        doi_raw = getattr(article, 'doi', None)
        doi = doi_raw.split('\n')[0] if doi_raw else None

        # Use getattr with defaults to handle missing attributes
        article_data = {
            "pubmed_id": getattr(article, 'pubmed_id', None),
            "title": getattr(article, 'title', None),
            "abstract": getattr(article, 'abstract', None),
            "keywords": getattr(article, 'keywords', None) or [],
            "journal": getattr(article, 'journal', None),
            "publication_date": str(article.publication_date) if getattr(article, 'publication_date', None) else None,
            "authors": [
                {"firstname": author.get("firstname"), "lastname": author.get("lastname")}
                for author in (getattr(article, 'authors', None) or [])
            ],
            "doi": doi,
            "conclusions": getattr(article, 'conclusions', None),
            "methods": getattr(article, 'methods', None),
            "results": getattr(article, 'results', None),
            "copyrights": getattr(article, 'copyrights', None),
        }
        articles.append(article_data)

    return articles


def save_to_json(data: list[dict], output_path: Path):
    """
    Save article data to JSON format.

    Args:
        data: List of article data
        output_path: Output file path
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return output_path


def save_to_csv(data: list[dict], output_path: Path):
    """
    Save article data to CSV format.

    Args:
        data: List of article data
        output_path: Output file path
    """
    if not data:
        return output_path

    # CSV field definitions
    fieldnames = [
        "pubmed_id",
        "title",
        "abstract",
        "journal",
        "publication_date",
        "doi",
        "authors",
        "keywords",
        "conclusions",
        "methods",
        "results",
        "copyrights"
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for article in data:
            # Convert author list to string
            authors_str = "; ".join([
                f"{a.get('firstname', '')} {a.get('lastname', '')}".strip()
                for a in article.get("authors", [])
            ])

            # Convert keyword list to string
            keywords_str = "; ".join(article.get("keywords", []) or [])

            csv_row = {
                "pubmed_id": article.get("pubmed_id"),
                "title": article.get("title"),
                "abstract": article.get("abstract"),
                "journal": article.get("journal"),
                "publication_date": article.get("publication_date"),
                "doi": article.get("doi"),
                "authors": authors_str,
                "keywords": keywords_str,
                "conclusions": article.get("conclusions"),
                "methods": article.get("methods"),
                "results": article.get("results"),
                "copyrights": article.get("copyrights"),
            }
            writer.writerow(csv_row)

    return output_path


def save_metadata(query: str, retrieved_count: int, data_file_path: Path, search_date: str):
    """
    Save metadata to a .meta.txt file.

    Args:
        query: Search query
        retrieved_count: Number of retrieved results
        data_file_path: Path to the data file
        search_date: Search date and time
    """
    meta_content = f"""Query: {query}
Search Date: {search_date}
Retrieved Results: {retrieved_count}
Data File: {data_file_path.name}
"""

    meta_path = data_file_path.parent / f"{data_file_path.stem}.meta.txt"
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(meta_content)

    return meta_path


def validate_output_path(output_arg: str, format: str) -> Path:
    """
    Validate and determine the output path.

    Args:
        output_arg: Value specified with -o option
        format: Output format (csv/json)

    Returns:
        Output file path

    Raises:
        ValueError: If the file extension doesn't match the format
    """
    output_path = Path(output_arg)

    # If it has an extension, validate it
    if output_path.suffix:
        allowed_extensions = {'.csv', '.json'}
        if output_path.suffix.lower() not in allowed_extensions:
            raise ValueError(
                f"Invalid file extension '{output_path.suffix}'. "
                f"Allowed extensions: {', '.join(allowed_extensions)}"
            )

        # Check format consistency
        expected_ext = f".{format}"
        if output_path.suffix.lower() != expected_ext:
            raise ValueError(
                f"File extension '{output_path.suffix}' doesn't match format '{format}'. "
                f"Expected '{expected_ext}'"
            )

        return output_path
    else:
        # No extension = directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"pubmed_{timestamp}.{format}"
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path / default_filename


def determine_output_path(output_arg: str | None, format: str) -> Path:
    """
    Determine the output path based on user input.

    Args:
        output_arg: Value specified with -o option
        format: Output format (csv/json)

    Returns:
        Output file path
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"pubmed_{timestamp}.{format}"

    if output_arg is None:
        # No specification → default filename in current directory
        return Path(default_filename)

    return validate_output_path(output_arg, format)


def main():
    from ppget import __version__

    parser = argparse.ArgumentParser(
        description="A simple CLI tool to download PubMed articles"
    )
    parser.add_argument(
        "query",
        type=str,
        help="Search query (e.g., 'machine learning AND medicine')"
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=100,
        help="Maximum number of results to retrieve (default: 100)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output file path or directory (default: current directory)"
    )
    parser.add_argument(
        "-e", "--email",
        type=str,
        default="anonymous@example.com",
        help="Email address for API rate limit relaxation (default: anonymous@example.com)"
    )
    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["csv", "json"],
        default="csv",
        help="Output format (default: csv)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress progress messages (errors only)"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"pget {__version__}",
        help="Show version and exit"
    )

    args = parser.parse_args()

    # Start search
    if not args.quiet:
        print(f"Searching PubMed...")
        print(f"Query: '{args.query}'")
        print(f"Max results: {args.limit}")

    try:
        search_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        articles = search_pubmed(args.query, args.limit, args.email, args.quiet)

        if not args.quiet:
            print(f"✓ Found {len(articles)} articles")

        if not articles:
            if not args.quiet:
                print("No articles found for the given query")
            return 0

        # Determine output path
        output_path = determine_output_path(args.output, args.format)

        # Save data based on format
        if args.format == "json":
            save_to_json(articles, output_path)
        else:  # csv
            save_to_csv(articles, output_path)

        # Always save metadata to .meta.txt
        meta_path = save_metadata(args.query, len(articles), output_path, search_date)

        if not args.quiet:
            print(f"✓ Saved {len(articles)} articles to {output_path}")
            print(f"✓ Metadata saved to {meta_path}")
            print(f"\nSuccessfully downloaded {len(articles)} articles")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
