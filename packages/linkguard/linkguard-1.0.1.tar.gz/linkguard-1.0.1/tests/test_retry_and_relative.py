"""Tests for retry logic and relative URL resolution features."""

import pytest
from pathlib import Path
import tempfile

from linkguard.scanner.link_checker import LinkChecker
from linkguard.scanner.url_extractor import URLExtractor


@pytest.mark.asyncio
async def test_retry_parameter_accepted():
    """Test that LinkChecker accepts max_retries parameter."""
    checker = LinkChecker(timeout=5, max_retries=3)
    assert checker.max_retries == 3

    checker_default = LinkChecker(timeout=5)
    assert checker_default.max_retries == 2  # Default value


def test_resolve_relative_url_markdown():
    """Test resolving relative URLs in markdown files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file structure
        base_dir = Path(tmpdir)
        docs_dir = base_dir / "docs"
        docs_dir.mkdir()

        # Create target file
        readme = base_dir / "README.md"
        readme.write_text("# Main readme")

        # Create source file with relative link
        api_doc = docs_dir / "api.md"
        api_doc.write_text("[Home](../README.md)")

        # Extract with relative resolution enabled
        extractor = URLExtractor(resolve_relative=True)
        urls = extractor.extract_from_file(api_doc)

        assert len(urls) == 1
        assert urls[0]["url"].startswith("file:///")
        assert "README.md" in urls[0]["url"]


def test_resolve_relative_url_nonexistent():
    """Test that nonexistent relative URLs are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        docs_dir = base_dir / "docs"
        docs_dir.mkdir()

        # Create source file with link to nonexistent file
        api_doc = docs_dir / "api.md"
        api_doc.write_text("[Broken](../NONEXISTENT.md)")

        # Extract with relative resolution enabled
        extractor = URLExtractor(resolve_relative=True)
        urls = extractor.extract_from_file(api_doc)

        # Should be empty since the file doesn't exist
        assert len(urls) == 0


def test_resolve_relative_disabled_by_default():
    """Test that relative URLs are ignored when resolution is disabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        docs_dir = base_dir / "docs"
        docs_dir.mkdir()

        # Create target file
        readme = base_dir / "README.md"
        readme.write_text("# Main readme")

        # Create source file with relative link
        api_doc = docs_dir / "api.md"
        api_doc.write_text("[Home](../README.md)\n[External](https://example.com)")

        # Extract WITHOUT relative resolution (default)
        extractor = URLExtractor(resolve_relative=False)
        urls = extractor.extract_from_file(api_doc)

        # Should only get the absolute URL, not the relative one
        assert len(urls) == 1
        assert urls[0]["url"] == "https://example.com"


def test_resolve_absolute_url_unchanged():
    """Test that absolute URLs are not modified when resolution is enabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)

        # Create source file with absolute URL
        test_file = base_dir / "test.md"
        test_file.write_text("[External](https://example.com)")

        # Extract with relative resolution enabled
        extractor = URLExtractor(resolve_relative=True)
        urls = extractor.extract_from_file(test_file)

        assert len(urls) == 1
        assert urls[0]["url"] == "https://example.com"


def test_resolve_mixed_urls():
    """Test resolving a mix of relative and absolute URLs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)

        # Create target file
        other = base_dir / "other.md"
        other.write_text("# Other file")

        # Create source file with mixed URLs
        test_file = base_dir / "test.md"
        test_file.write_text(
            "[Relative](./other.md)\n"
            "[Absolute](https://example.com)\n"
            "[HTTP](http://example.org)\n"
        )

        # Extract with relative resolution enabled
        extractor = URLExtractor(resolve_relative=True)
        urls = extractor.extract_from_file(test_file)

        assert len(urls) == 3

        # Check that relative was resolved to file://
        file_urls = [u for u in urls if u["url"].startswith("file://")]
        assert len(file_urls) == 1
        assert "other.md" in file_urls[0]["url"]

        # Check that absolute URLs are unchanged
        http_urls = [u for u in urls if u["url"].startswith(("http://", "https://"))]
        assert len(http_urls) == 2
        assert any("example.com" in u["url"] for u in http_urls)
        assert any("example.org" in u["url"] for u in http_urls)


def test_resolve_current_directory():
    """Test resolving relative URLs with ./ prefix."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)

        # Create target file in same directory
        other = base_dir / "other.md"
        other.write_text("# Other file")

        # Create source file with ./ link
        test_file = base_dir / "test.md"
        test_file.write_text("[Same Dir](./other.md)")

        # Extract with relative resolution enabled
        extractor = URLExtractor(resolve_relative=True)
        urls = extractor.extract_from_file(test_file)

        assert len(urls) == 1
        assert urls[0]["url"].startswith("file:///")
        assert "other.md" in urls[0]["url"]


def test_resolve_parent_directory():
    """Test resolving relative URLs with ../ prefix."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        sub_dir = base_dir / "sub"
        sub_dir.mkdir()

        # Create target file in parent directory
        parent_file = base_dir / "parent.md"
        parent_file.write_text("# Parent file")

        # Create source file in subdirectory
        test_file = sub_dir / "test.md"
        test_file.write_text("[Parent](../parent.md)")

        # Extract with relative resolution enabled
        extractor = URLExtractor(resolve_relative=True)
        urls = extractor.extract_from_file(test_file)

        assert len(urls) == 1
        assert urls[0]["url"].startswith("file:///")
        assert "parent.md" in urls[0]["url"]


def test_resolve_preserves_line_numbers():
    """Test that line numbers are preserved when resolving relative URLs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)

        # Create target file
        other = base_dir / "other.md"
        other.write_text("# Other file")

        # Create source file with multiple links
        test_file = base_dir / "test.md"
        test_file.write_text(
            "Line 1\n"
            "[Link on line 2](./other.md)\n"
            "Line 3\n"
            "[Link on line 4](https://example.com)\n"
        )

        # Extract with relative resolution enabled
        extractor = URLExtractor(resolve_relative=True)
        urls = extractor.extract_from_file(test_file)

        assert len(urls) == 2

        # Find the relative link
        relative_link = [u for u in urls if u["url"].startswith("file://")][0]
        assert relative_link["line_number"] == 2

        # Find the absolute link
        absolute_link = [u for u in urls if u["url"].startswith("https://")][0]
        assert absolute_link["line_number"] == 4
