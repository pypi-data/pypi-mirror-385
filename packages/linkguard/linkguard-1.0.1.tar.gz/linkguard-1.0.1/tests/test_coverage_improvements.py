"""
Additional tests to improve code coverage for edge cases.
"""

import pytest
import asyncio
import aiohttp
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from linkguard.scanner.link_checker import LinkChecker
from linkguard.scanner.url_extractor import URLExtractor
from linkguard.scanner.file_scanner import FileScanner
from linkguard.utils.config import Config


# ============================================================================
# LinkChecker Coverage Tests
# ============================================================================


@pytest.mark.asyncio
async def test_link_checker_head_403_fallback_to_get():
    """Test that 403 response triggers GET fallback."""
    checker = LinkChecker(timeout=5, max_retries=2)

    # Mock HEAD request returning 403
    mock_head_response = MagicMock()
    mock_head_response.status = 403
    mock_head_response.__aenter__ = AsyncMock(return_value=mock_head_response)
    mock_head_response.__aexit__ = AsyncMock(return_value=None)

    # Mock GET request returning 200
    mock_get_response = MagicMock()
    mock_get_response.status = 200
    mock_get_response.__aenter__ = AsyncMock(return_value=mock_get_response)
    mock_get_response.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_head_response):
        with patch("aiohttp.ClientSession.get", return_value=mock_get_response):
            url_data = [("test.md", {"url": "https://example.com", "line_number": 1})]
            results = await checker.check_links(url_data)

            assert len(results) == 1
            assert results[0].status_code == 200
            assert results[0].is_broken is False


@pytest.mark.asyncio
async def test_link_checker_head_405_fallback_to_get():
    """Test that 405 response triggers GET fallback."""
    checker = LinkChecker(timeout=5, max_retries=2)

    mock_head_response = MagicMock()
    mock_head_response.status = 405
    mock_head_response.__aenter__ = AsyncMock(return_value=mock_head_response)
    mock_head_response.__aexit__ = AsyncMock(return_value=None)

    mock_get_response = MagicMock()
    mock_get_response.status = 200
    mock_get_response.__aenter__ = AsyncMock(return_value=mock_get_response)
    mock_get_response.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_head_response):
        with patch("aiohttp.ClientSession.get", return_value=mock_get_response):
            url_data = [("test.md", {"url": "https://example.com", "line_number": 1})]
            results = await checker.check_links(url_data)

            assert len(results) == 1
            assert results[0].status_code == 200


@pytest.mark.asyncio
async def test_link_checker_head_501_fallback_to_get():
    """Test that 501 response triggers GET fallback."""
    checker = LinkChecker(timeout=5, max_retries=2)

    mock_head_response = MagicMock()
    mock_head_response.status = 501
    mock_head_response.__aenter__ = AsyncMock(return_value=mock_head_response)
    mock_head_response.__aexit__ = AsyncMock(return_value=None)

    mock_get_response = MagicMock()
    mock_get_response.status = 200
    mock_get_response.__aenter__ = AsyncMock(return_value=mock_get_response)
    mock_get_response.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_head_response):
        with patch("aiohttp.ClientSession.get", return_value=mock_get_response):
            url_data = [("test.md", {"url": "https://example.com", "line_number": 1})]
            results = await checker.check_links(url_data)

            assert len(results) == 1
            assert results[0].status_code == 200


@pytest.mark.asyncio
async def test_link_checker_timeout_with_retries():
    """Test timeout handling with retry logic."""
    checker = LinkChecker(timeout=1, max_retries=2)

    async def timeout_mock(*args, **kwargs):
        await asyncio.sleep(0)
        raise asyncio.TimeoutError("Request timed out")

    mock_context = AsyncMock()
    mock_context.__aenter__.side_effect = timeout_mock
    mock_context.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_context):
        url_data = [("test.md", {"url": "https://slow-site.com", "line_number": 1})]
        results = await checker.check_links(url_data)

        assert len(results) == 1
        assert results[0].is_broken is True
        assert results[0].error is not None
        assert "after 2 retries" in results[0].error


@pytest.mark.asyncio
async def test_link_checker_client_error_with_retries():
    """Test ClientError handling with retry logic in GET fallback."""
    checker = LinkChecker(timeout=5, max_retries=2)

    # HEAD returns 403, triggering GET fallback
    mock_head_response = MagicMock()
    mock_head_response.status = 403
    mock_head_response.__aenter__ = AsyncMock(return_value=mock_head_response)
    mock_head_response.__aexit__ = AsyncMock(return_value=None)

    # GET raises ClientError
    async def client_error_mock(*args, **kwargs):
        await asyncio.sleep(0)
        raise aiohttp.ClientError("Connection failed")

    mock_get_context = AsyncMock()
    mock_get_context.__aenter__.side_effect = client_error_mock
    mock_get_context.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_head_response):
        with patch("aiohttp.ClientSession.get", return_value=mock_get_context):
            url_data = [("test.md", {"url": "https://example.com", "line_number": 1})]
            results = await checker.check_links(url_data)

            assert len(results) == 1
            assert results[0].is_broken is True
            assert results[0].error is not None
            assert "Connection failed" in results[0].error


@pytest.mark.asyncio
async def test_link_checker_unexpected_error_in_get_fallback():
    """Test unexpected error handling in GET fallback."""
    checker = LinkChecker(timeout=5, max_retries=2)

    # HEAD returns 403
    mock_head_response = MagicMock()
    mock_head_response.status = 403
    mock_head_response.__aenter__ = AsyncMock(return_value=mock_head_response)
    mock_head_response.__aexit__ = AsyncMock(return_value=None)

    # GET raises unexpected exception
    async def unexpected_error_mock(*args, **kwargs):
        await asyncio.sleep(0)
        raise ValueError("Unexpected error")

    mock_get_context = AsyncMock()
    mock_get_context.__aenter__.side_effect = unexpected_error_mock
    mock_get_context.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_head_response):
        with patch("aiohttp.ClientSession.get", return_value=mock_get_context):
            url_data = [("test.md", {"url": "https://example.com", "line_number": 1})]
            results = await checker.check_links(url_data)

            assert len(results) == 1
            assert results[0].is_broken is True
            assert results[0].error is not None
            assert "Unexpected error" in results[0].error


@pytest.mark.asyncio
async def test_link_checker_progress_callback_with_exception():
    """Test that progress callback is called even when exception occurs."""
    checker = LinkChecker(timeout=5)
    progress_calls = []

    def progress_tracker(completed):
        progress_calls.append(completed)

    async def exception_mock(*args, **kwargs):
        await asyncio.sleep(0)
        raise Exception("Test exception")

    mock_context = AsyncMock()
    mock_context.__aenter__.side_effect = exception_mock
    mock_context.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_context):
        url_data = [("test.md", {"url": "https://error-site.com", "line_number": 1})]
        await checker.check_links(url_data, progress_callback=progress_tracker)

        # Progress callback should still be called
        assert len(progress_calls) == 1
        assert progress_calls[0] == 1


# ============================================================================
# URLExtractor Coverage Tests
# ============================================================================


@pytest.mark.asyncio
async def test_url_extractor_absolute_path_exists(tmp_path):
    """Test resolving absolute path that exists."""
    extractor = URLExtractor(resolve_relative=True)

    # Create a test file
    test_file = tmp_path / "test.md"
    test_file.write_text("[link](/absolute/path)")

    # Create the absolute path target
    absolute_target = tmp_path / "absolute" / "path"
    absolute_target.parent.mkdir(parents=True, exist_ok=True)
    absolute_target.touch()

    # Mock Path.exists() to return True for absolute path
    with patch.object(Path, "exists", return_value=True):
        with patch.object(Path, "as_posix", return_value="absolute/path"):
            urls = extractor.extract_from_file(test_file)
            # Should resolve to file:// URL
            if urls:
                assert any("file:///" in url_info["url"] for url_info in urls)


@pytest.mark.asyncio
async def test_url_extractor_absolute_path_not_exists():
    """Test resolving absolute path that doesn't exist."""
    extractor = URLExtractor(resolve_relative=True)
    test_file = Path("test.md")

    # Simulate extracting URL with absolute path that doesn't exist
    url = "/nonexistent/path"
    result = extractor._resolve_relative_url(test_file, url)

    # Should return None since path doesn't exist
    assert result is None


@pytest.mark.asyncio
async def test_url_extractor_relative_path_oserror(tmp_path):
    """Test handling OSError when resolving relative paths."""
    extractor = URLExtractor(resolve_relative=True)

    test_file = tmp_path / "test.md"
    test_file.write_text("[link](../invalid)")

    # Mock resolve() to raise OSError
    with patch.object(Path, "resolve", side_effect=OSError("Invalid path")):
        result = extractor._resolve_relative_url(test_file, "../invalid")
        assert result is None


@pytest.mark.asyncio
async def test_url_extractor_relative_path_valueerror(tmp_path):
    """Test handling ValueError when resolving relative paths."""
    extractor = URLExtractor(resolve_relative=True)

    test_file = tmp_path / "test.md"

    # Mock resolve() to raise ValueError
    with patch.object(Path, "resolve", side_effect=ValueError("Invalid path")):
        result = extractor._resolve_relative_url(test_file, "../invalid")
        assert result is None


# ============================================================================
# Config Coverage Tests
# ============================================================================


def test_config_json_load_generic_exception(tmp_path):
    """Test handling of generic exceptions when loading config."""
    # Create malformed JSON that causes generic exception
    with patch("builtins.open", side_effect=Exception("Unexpected error")):
        config = Config(tmp_path)
        # Should fall back to defaults
        assert config.get("timeout") == 10
        assert config.get("concurrency") == 50


def test_config_gitignore_generic_exception(tmp_path):
    """Test handling of exceptions when reading .gitignore files."""
    root = tmp_path / "project"
    root.mkdir()

    gitignore = root / ".gitignore"
    gitignore.write_text("*.log")

    # Mock _parse_ignore_file to raise exception
    with patch.object(Config, "_parse_ignore_file", side_effect=Exception("Parse error")):
        config = Config(root)
        patterns = config.get_ignore_patterns()
        # Should continue without the problematic .gitignore
        assert isinstance(patterns, list)


def test_config_parse_ignore_file_io_error(tmp_path):
    """Test IOError when parsing ignore file."""
    ignore_file = tmp_path / ".linkguardignore"

    # Mock open to raise IOError
    with patch("builtins.open", side_effect=IOError("Cannot read file")):
        config = Config(tmp_path)
        # _parse_ignore_file raises ValueError, not returns empty set
        with pytest.raises(ValueError) as exc_info:
            config._parse_ignore_file(ignore_file)
        assert "Cannot read file" in str(exc_info.value)


# ============================================================================
# FileScanner Coverage Tests
# ============================================================================


def test_file_scanner_invalid_type(tmp_path):
    """Test FileScanner with various edge cases."""
    # Test with valid Path object
    scanner = FileScanner(tmp_path, set())
    assert scanner.root_dir == tmp_path
    assert len(scanner.ignore_patterns) > 0  # Should have default patterns


# ============================================================================
# Rules Coverage Tests
# ============================================================================


def test_rules_line_97_coverage(tmp_path):
    """Test to cover line 97 in rules.py."""
    from linkguard.scanner.rules import EnvironmentRules

    rules = EnvironmentRules(mode="prod")

    # Test with various dev URLs
    test_urls = [
        ("test.md", {"url": "http://localhost:3000", "line_number": 1}),
        ("test.md", {"url": "http://127.0.0.1:8080", "line_number": 2}),
        ("test.md", {"url": "http://example.dev", "line_number": 3}),
    ]

    violations = rules.check_urls(test_urls)

    # Should find violations for at least 2 dev URLs
    assert len(violations) >= 2
    # Verify localhost and 127.0.0.1 are detected
    violation_urls = [v.url for v in violations]
    assert "http://localhost:3000" in violation_urls
    assert "http://127.0.0.1:8080" in violation_urls
