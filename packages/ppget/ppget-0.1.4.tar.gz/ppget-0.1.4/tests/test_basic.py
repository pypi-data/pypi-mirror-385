"""
Basic tests for ppget functionality.

These tests verify core functionality without requiring actual PubMed API calls.
Run with: pytest
"""

import pytest
from pathlib import Path
import tempfile
import json
import csv

from ppget.cli import validate_limit, validate_email
from ppget.output import save_to_json, save_to_csv, determine_output_path
from ppget.xml_extractor import extract_text_from_xml, extract_abstract_from_xml


class TestValidation:
    """Test input validation functions."""

    def test_validate_limit_positive(self):
        """Valid limit should not raise error."""
        validate_limit(100)
        validate_limit(1)
        validate_limit(10000)

    def test_validate_limit_zero(self):
        """Zero limit should raise ValueError."""
        with pytest.raises(ValueError, match="positive number"):
            validate_limit(0)

    def test_validate_limit_negative(self):
        """Negative limit should raise ValueError."""
        with pytest.raises(ValueError, match="positive number"):
            validate_limit(-1)

    def test_validate_limit_too_large(self):
        """Limit over 10000 should raise ValueError."""
        with pytest.raises(ValueError, match="cannot exceed 10000"):
            validate_limit(10001)

    def test_validate_email_valid(self):
        """Valid email should not raise error."""
        validate_email("test@example.com")
        validate_email("user.name+tag@example.co.jp")
        validate_email("anonymous@example.com")  # Default

    def test_validate_email_invalid(self):
        """Invalid email should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            validate_email("notanemail")
        with pytest.raises(ValueError, match="Invalid email format"):
            validate_email("missing@domain")
        with pytest.raises(ValueError, match="Invalid email format"):
            validate_email("@example.com")


class TestOutput:
    """Test output handling functions."""

    def test_save_to_json(self):
        """Test JSON file creation."""
        test_data = [
            {"pubmed_id": "12345", "title": "Test Article", "abstract": "Test abstract"}
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.json"
            save_to_json(test_data, output_path)

            assert output_path.exists()
            with open(output_path, encoding="utf-8") as f:
                loaded_data = json.load(f)
                assert loaded_data == test_data

    def test_save_to_json_empty_data(self):
        """Empty data should raise ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.json"
            with pytest.raises(ValueError, match="No data to save"):
                save_to_json([], output_path)

    def test_save_to_csv(self):
        """Test CSV file creation."""
        test_data = [
            {
                "pubmed_id": "12345",
                "title": "Test Article",
                "abstract": "Test abstract",
                "journal": "Test Journal",
                "publication_date": "2024-01-01",
                "doi": "10.1234/test",
                "authors": [{"firstname": "John", "lastname": "Doe"}],
                "keywords": ["test", "article"],
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.csv"
            save_to_csv(test_data, output_path)

            assert output_path.exists()
            with open(output_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 1
                assert rows[0]["pubmed_id"] == "12345"
                assert rows[0]["title"] == "Test Article"

    def test_save_to_csv_empty_data(self):
        """Empty data should raise ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.csv"
            with pytest.raises(ValueError, match="No data to save"):
                save_to_csv([], output_path)

    def test_determine_output_path_default(self):
        """Test default output path generation."""
        path = determine_output_path(None, "csv")
        assert path.suffix == ".csv"
        assert "pubmed_" in path.name

    def test_determine_output_path_with_file(self):
        """Test custom file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_path = f"{tmpdir}/custom.csv"
            path = determine_output_path(custom_path, "csv")
            assert str(path) == custom_path


class TestXMLExtractor:
    """Test XML extraction utilities."""

    def test_extract_text_from_xml_none(self):
        """None XML element should return None."""
        result = extract_text_from_xml(None, ".//test")
        assert result is None

    def test_extract_abstract_from_xml_none(self):
        """None XML element should return None."""
        result = extract_abstract_from_xml(None)
        assert result is None
