import pytest
import json
import csv
from datetime import datetime
from linkguard.reporter.exporter import Exporter
from linkguard.scanner.link_checker import LinkResult
from linkguard.scanner.rules import RuleViolation


@pytest.fixture
def sample_results():
    """Create sample LinkResult objects."""
    return [
        LinkResult(
            url="https://example.com",
            status_code=200,
            is_broken=False,
            file_path="test.md",
            line_number=5,
            error=None,
            response_time=0.123,
        ),
        LinkResult(
            url="https://broken.com",
            status_code=404,
            is_broken=True,
            file_path="test.md",
            line_number=10,
            error="Not Found",
            response_time=0.456,
        ),
    ]


@pytest.fixture
def sample_violations():
    """Create sample RuleViolation objects."""
    return [
        RuleViolation(
            url="http://localhost:3000",
            file_path="config.js",
            line_number=12,
            rule="no-localhost-in-prod",
            severity="error",
            message="Localhost URL found in production mode",
        )
    ]


def test_export_to_json(tmp_path, sample_results, sample_violations):
    """Test JSON export with metadata."""
    export_path = tmp_path / "report.json"
    metadata = {
        "directory": str(tmp_path),
        "mode": "prod",
        "timeout": 10,
        "concurrency": 50,
        "files_scanned": 5,
    }

    Exporter.export_to_json(sample_results, sample_violations, export_path, metadata)

    # Verify file exists
    assert export_path.exists()

    # Verify JSON structure
    with open(export_path, "r") as f:
        data = json.load(f)

    assert "metadata" in data
    assert "results" in data
    assert "violations" in data

    # Verify metadata (summary is part of metadata, not separate)
    assert data["metadata"]["mode"] == "prod"
    assert data["metadata"]["files_scanned"] == 5
    assert data["metadata"]["total_links"] == 2
    assert data["metadata"]["broken_links"] == 1
    assert data["metadata"]["violations"] == 1
    assert "timestamp" in data["metadata"]

    # Verify results
    assert len(data["results"]) == 2
    assert data["results"][0]["url"] == "https://example.com"
    assert data["results"][0]["status_code"] == 200
    assert data["results"][1]["status_code"] == 404

    # Verify violations
    assert len(data["violations"]) == 1
    assert data["violations"][0]["url"] == "http://localhost:3000"
    assert data["violations"][0]["rule"] == "no-localhost-in-prod"


def test_export_to_csv(tmp_path, sample_results, sample_violations):
    """Test CSV export format."""
    export_path = tmp_path / "report.csv"

    Exporter.export_to_csv(sample_results, sample_violations, export_path)

    # Verify file exists
    assert export_path.exists()

    # Read CSV
    with open(export_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Verify headers exist (actual header names from exporter.py)
    assert "URL" in rows[0]
    assert "Status Code" in rows[0]  # Not "Status"
    assert "File Path" in rows[0]  # Not "File"
    assert "Line Number" in rows[0]  # Not "Line"

    # Verify data rows (2 results)
    assert len(rows) == 2

    # Verify result data
    assert rows[0]["URL"] == "https://example.com"
    assert rows[0]["Status Code"] == "200"
    assert rows[1]["URL"] == "https://broken.com"
    assert rows[1]["Status Code"] == "404"


def test_export_to_markdown(tmp_path, sample_results, sample_violations):
    """Test Markdown export with tables."""
    export_path = tmp_path / "report.md"
    metadata = {"directory": str(tmp_path), "mode": "prod", "files_scanned": 5}

    Exporter.export_to_markdown(sample_results, sample_violations, export_path, metadata)

    # Verify file exists
    assert export_path.exists()

    # Read markdown content
    content = export_path.read_text(encoding="utf-8")

    # Verify structure (actual title from exporter.py is "Linkguard", not "LinkGuard")
    assert "# Linkguard Scan Report" in content
    assert "## Summary" in content

    # Verify metadata
    assert "**Mode:**" in content
    assert "prod" in content

    # Verify tables (check for pipe characters)
    assert "|" in content
    assert "|-----|" in content  # Actual separator format

    # Verify data presence
    assert "https://example.com" in content
    assert "https://broken.com" in content
    assert "http://localhost:3000" in content


def test_export_json_with_no_violations(tmp_path, sample_results):
    """Test JSON export when there are no violations."""
    export_path = tmp_path / "report.json"

    Exporter.export_to_json(sample_results, [], export_path, {})

    with open(export_path, "r") as f:
        data = json.load(f)

    assert data["violations"] == []
    # Summary is in metadata
    assert data["metadata"]["violations"] == 0


def test_export_csv_special_characters(tmp_path):
    """Test CSV export with special characters."""
    results = [
        LinkResult(
            url="https://example.com/path?query=value&key=123",
            status_code=200,
            is_broken=False,
            file_path="test,file.md",  # Comma in filename
            line_number=5,
            error=None,
            response_time=0.1,
        )
    ]

    export_path = tmp_path / "report.csv"
    Exporter.export_to_csv(results, [], export_path)

    # Verify CSV handles special characters
    with open(export_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert rows[0]["URL"] == "https://example.com/path?query=value&key=123"
    assert "test,file.md" in rows[0]["File Path"]  # Correct header name


def test_export_markdown_empty_results(tmp_path):
    """Test Markdown export with no results."""
    export_path = tmp_path / "report.md"

    Exporter.export_to_markdown([], [], export_path, {})

    content = export_path.read_text(encoding="utf-8")

    # Should still have basic structure
    assert "# Linkguard Scan Report" in content  # Actual title
    assert "## Summary" in content


def test_json_timestamp_format(tmp_path, sample_results):
    """Test that JSON timestamp is ISO 8601 formatted."""
    export_path = tmp_path / "report.json"

    Exporter.export_to_json(sample_results, [], export_path, {})

    with open(export_path, "r") as f:
        data = json.load(f)

    # Verify timestamp can be parsed
    timestamp = data["metadata"]["timestamp"]
    # Should be in ISO format (YYYY-MM-DDTHH:MM:SS)
    assert "T" in timestamp
    # Try parsing it
    datetime.fromisoformat(timestamp)  # Will raise if format is wrong


def test_csv_handles_none_values(tmp_path):
    """Test CSV export with None values."""
    results = [
        LinkResult(
            url="https://example.com",
            status_code=None,
            is_broken=True,
            file_path="test.md",
            line_number=None,
            error="Connection timeout",
            response_time=0.123,
        )
    ]

    export_path = tmp_path / "report.csv"
    Exporter.export_to_csv(results, [], export_path)

    with open(export_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Verify None values are handled (converted to "N/A")
    assert len(rows) == 1
    assert rows[0]["URL"] == "https://example.com"
    # Status should be "N/A" (actual implementation)
    assert rows[0]["Status Code"] == "N/A"


def test_markdown_table_formatting(tmp_path, sample_results):
    """Test that Markdown tables are properly formatted."""
    export_path = tmp_path / "report.md"

    Exporter.export_to_markdown(sample_results, [], export_path, {})

    content = export_path.read_text(encoding="utf-8")

    # Check for table separators (actual format from exporter.py)
    assert "|-----|" in content
    # Check for table headers
    assert "| URL |" in content
