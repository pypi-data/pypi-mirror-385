import pytest
import asyncio
import ssl
from unittest.mock import AsyncMock, MagicMock, patch
from linkguard.scanner.link_checker import LinkChecker, LinkResult


@pytest.mark.asyncio
async def test_check_valid_url():
    """Test checking a valid URL that returns 200."""
    checker = LinkChecker(timeout=5)

    # Mock aiohttp response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_response):
        url_data = [("test.md", {"url": "https://example.com", "line_number": 1})]
        results = await checker.check_links(url_data)

        assert len(results) == 1
        assert results[0].status_code == 200
        assert results[0].is_broken is False
        assert results[0].url == "https://example.com"


@pytest.mark.asyncio
async def test_check_broken_url():
    """Test checking a broken URL that returns 404."""
    checker = LinkChecker(timeout=5)

    # Mock aiohttp response with 404
    mock_response = MagicMock()
    mock_response.status = 404
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_response):
        url_data = [("test.md", {"url": "https://example.com/404", "line_number": 1})]
        results = await checker.check_links(url_data)

        assert len(results) == 1
        assert results[0].status_code == 404
        assert results[0].is_broken is True


@pytest.mark.asyncio
async def test_check_timeout_error():
    """Test handling of timeout errors."""
    checker = LinkChecker(timeout=1)

    # Create an AsyncMock that raises TimeoutError
    async def async_timeout_side_effect(*args, **kwargs):
        """Async mock that simulates timeout."""
        await asyncio.sleep(0)  # Yield control to event loop
        raise asyncio.TimeoutError()

    # Mock the context manager
    mock_context = AsyncMock()
    mock_context.__aenter__.side_effect = async_timeout_side_effect
    mock_context.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_context):
        url_data = [("test.md", {"url": "https://slow-site.com", "line_number": 1})]
        results = await checker.check_links(url_data)

        assert len(results) == 1
        assert results[0].is_broken is True
        assert results[0].error is not None


@pytest.mark.asyncio
async def test_concurrent_checks():
    """Test concurrent checking of multiple URLs."""
    checker = LinkChecker(max_concurrent=10)

    # Mock aiohttp response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_response):
        urls = [
            ("test1.md", {"url": "https://google.com", "line_number": 1}),
            ("test2.md", {"url": "https://github.com", "line_number": 1}),
            ("test3.md", {"url": "https://example.com", "line_number": 1}),
        ]

        results = await checker.check_links(urls)
        assert len(results) == 3
        # Check that all URLs were processed successfully
        assert all(r.status_code == 200 for r in results)
        assert all(not r.is_broken for r in results)


@pytest.mark.asyncio
async def test_progress_callback():
    """Test that progress callback is called."""
    checker = LinkChecker(max_concurrent=5)
    progress_calls = []

    def progress_callback(completed: int):
        progress_calls.append(completed)

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_response):
        urls = [("test.md", {"url": f"https://example{i}.com", "line_number": 1}) for i in range(5)]

        await checker.check_links(urls, progress_callback)

        # Progress callback should have been called
        assert len(progress_calls) > 0
        assert max(progress_calls) == 5


@pytest.mark.asyncio
async def test_link_result_dataclass():
    """Test LinkResult dataclass attributes."""
    result = LinkResult(
        url="https://example.com",
        status_code=200,
        is_broken=False,
        file_path="test.md",
        line_number=10,
        error=None,
        response_time=0.123,
    )

    assert result.url == "https://example.com"
    assert result.status_code == 200
    assert result.is_broken is False
    assert result.file_path == "test.md"
    assert result.line_number == 10
    assert result.error is None


@pytest.mark.asyncio
async def test_multiple_urls_from_same_file():
    """Test checking multiple URLs from the same file."""
    checker = LinkChecker(timeout=5)

    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_response):
        urls = [
            ("readme.md", {"url": "https://github.com", "line_number": 5}),
            ("readme.md", {"url": "https://google.com", "line_number": 10}),
        ]

        results = await checker.check_links(urls)

        assert len(results) == 2
        assert all(r.file_path == "readme.md" for r in results)

        # Sort results by line number to handle async order
        results_sorted = sorted(results, key=lambda r: r.line_number or 0)
        assert results_sorted[0].line_number == 5
        assert results_sorted[1].line_number == 10
        assert results_sorted[0].url == "https://github.com"
        assert results_sorted[1].url == "https://google.com"


@pytest.mark.asyncio
async def test_ssl_certificate_error():
    """Test handling of SSL certificate errors."""
    checker = LinkChecker(timeout=5)

    async def ssl_error_mock(*args, **kwargs):
        """Mock SSL certificate error."""
        await asyncio.sleep(0)
        raise ssl.SSLError("Certificate verification failed")

    mock_context = AsyncMock()
    mock_context.__aenter__.side_effect = ssl_error_mock
    mock_context.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_context):
        url_data = [("test.md", {"url": "https://expired-cert-site.com", "line_number": 1})]
        results = await checker.check_links(url_data)

        assert len(results) == 1
        assert results[0].is_broken is True
        assert results[0].error is not None
        assert "ssl" in results[0].error.lower() or "certificate" in results[0].error.lower()


@pytest.mark.asyncio
async def test_connection_error():
    """Test handling of connection errors."""
    checker = LinkChecker(timeout=5)

    async def connection_error_mock(*args, **kwargs):
        """Mock connection error."""
        await asyncio.sleep(0)
        raise ConnectionError("Failed to connect")

    mock_context = AsyncMock()
    mock_context.__aenter__.side_effect = connection_error_mock
    mock_context.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_context):
        url_data = [("test.md", {"url": "https://unreachable-site.com", "line_number": 1})]
        results = await checker.check_links(url_data)

        assert len(results) == 1
        assert results[0].is_broken is True
        assert results[0].error is not None


@pytest.mark.asyncio
async def test_generic_exception_handling():
    """Test handling of generic exceptions."""
    checker = LinkChecker(timeout=5)

    async def generic_error_mock(*args, **kwargs):
        """Mock generic exception."""
        await asyncio.sleep(0)
        raise Exception("Unexpected error occurred")

    mock_context = AsyncMock()
    mock_context.__aenter__.side_effect = generic_error_mock
    mock_context.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession.head", return_value=mock_context):
        url_data = [("test.md", {"url": "https://error-site.com", "line_number": 1})]
        results = await checker.check_links(url_data)

        assert len(results) == 1
        assert results[0].is_broken is True
        assert results[0].error is not None
