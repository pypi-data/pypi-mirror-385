"""
XML extraction utilities for PubMed articles.

This module provides functions to extract text from PubMed XML elements,
properly handling nested HTML tags that pymed-paperscraper fails to process.
"""


def extract_text_from_xml(xml_element, path: str, separator: str = "\n") -> str | None:
    """
    Generic function to extract text from XML element using XPath.

    This function properly handles nested HTML tags (e.g., <i>, <b>) that
    pymed-paperscraper's getContent() function fails to extract correctly.

    Args:
        xml_element: XML element to search in
        path: XPath expression to find elements
        separator: String to join multiple elements (default: newline)

    Returns:
        Complete text including nested tags, or None if not found
    """
    if xml_element is None:
        return None

    elements = xml_element.findall(path)
    if not elements:
        return None

    # Extract complete text from each element including nested tags
    texts = []
    for elem in elements:
        # itertext() returns all text including nested elements
        text = ''.join(elem.itertext()).strip()
        if text:
            texts.append(text)

    return separator.join(texts) if texts else None


def extract_abstract_from_xml(xml_element) -> str | None:
    """
    Extract abstract text directly from XML element.

    This function handles structured abstracts with labels (BACKGROUND, METHODS, etc.)
    and nested HTML tags that pymed-paperscraper fails to extract correctly.

    Args:
        xml_element: XML element from the PubMed article

    Returns:
        Complete abstract text with labels, or None if not found
    """
    if xml_element is None:
        return None

    # Find all AbstractText elements
    abstract_elements = xml_element.findall(".//AbstractText")
    if not abstract_elements:
        return None

    # Extract text including nested elements
    texts = []
    for elem in abstract_elements:
        # Get label if exists (e.g., BACKGROUND, METHODS, RESULTS, CONCLUSIONS)
        label = elem.get('Label')

        # Get complete text including nested tags using itertext()
        text = ''.join(elem.itertext()).strip()

        if text:
            # Add label prefix if exists for structured abstracts
            if label:
                texts.append(f"{label}: {text}")
            else:
                texts.append(text)

    return '\n'.join(texts) if texts else None
