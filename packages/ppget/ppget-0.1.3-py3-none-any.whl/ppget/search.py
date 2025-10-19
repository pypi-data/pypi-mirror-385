"""
PubMed search functionality.

This module handles searching PubMed and extracting article data,
with XML fallback for fields that may have parsing issues.
"""

from pymed_paperscraper import PubMed

from .xml_extractor import extract_text_from_xml, extract_abstract_from_xml, extract_article_doi_from_xml


def search_pubmed(query: str, max_results: int = 100, email: str = "anonymous@example.com", quiet: bool = False) -> list[dict]:
    """
    Search PubMed and retrieve article data.

    This function uses pymed-paperscraper for the initial data extraction,
    with XML fallback for fields that may contain nested HTML tags or
    have other parsing issues.

    Args:
        query: Search query
        max_results: Maximum number of results to retrieve
        email: Email address (for API rate limit relaxation)
        quiet: If True, suppress progress messages

    Returns:
        List of article data dictionaries

    Raises:
        RuntimeError: If PubMed query fails
        ValueError: If query is empty or invalid
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")

    pubmed = PubMed(tool="ppget", email=email)

    try:
        results = pubmed.query(query, max_results=max_results)
    except Exception as e:
        raise RuntimeError(f"PubMed query failed: {e}") from e

    articles = []
    for article in results:
        xml_element = getattr(article, 'xml', None)

        # Extract all fields from pymed-paperscraper first
        title = getattr(article, 'title', None)
        abstract = getattr(article, 'abstract', None)
        journal = getattr(article, 'journal', None)
        doi_raw = getattr(article, 'doi', None)

        # XML fallback for fields that may have nested HTML tags
        # This ensures we don't lose data due to pymed-paperscraper's parsing limitations
        if xml_element is not None:
            # Title: May contain italic tags for species names, etc.
            if not title:
                title = extract_text_from_xml(xml_element, ".//ArticleTitle")

            # Abstract: Handles structured abstracts and nested tags
            if not abstract:
                abstract = extract_abstract_from_xml(xml_element)

            # Journal: Usually simple text, but check just in case
            if not journal:
                journal = extract_text_from_xml(xml_element, ".//Journal/Title")

            # DOI: Extract article DOI only (excluding reference DOIs)
            if not doi_raw:
                doi_raw = extract_article_doi_from_xml(xml_element)

        # Use DOI directly (extract_article_doi_from_xml returns single DOI)
        doi = doi_raw

        # Build article data dictionary
        article_data = {
            "pubmed_id": getattr(article, 'pubmed_id', None),
            "title": title,
            "abstract": abstract,
            "keywords": getattr(article, 'keywords', None) or [],
            "journal": journal,
            "publication_date": str(article.publication_date) if getattr(article, 'publication_date', None) else None,
            "authors": [
                {"firstname": author.get("firstname"), "lastname": author.get("lastname")}
                for author in (getattr(article, 'authors', None) or [])
            ],
            "doi": doi,
        }
        articles.append(article_data)

    return articles
