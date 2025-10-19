"""
Output handling for PubMed article data.

This module provides functions to save article data in various formats
(JSON, CSV) and manage output file paths.
"""

import json
import csv
from datetime import datetime
from pathlib import Path


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
