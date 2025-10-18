"""Link validation module for asynchronous HTTP checking.

This module provides the LinkChecker class which performs concurrent
HTTP requests to validate URLs using aiohttp. It implements smart
fallback strategies and respects concurrency limits.
"""

import asyncio
import aiohttp
from typing import Sequence, Dict, Any, Optional, Callable, Tuple, Union, List, Final
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LinkResult:
    """Result of checking a single link.

    This dataclass is immutable (frozen=True) to ensure thread safety
    and prevent accidental modifications.

    Attributes:
        url: The URL that was checked
        status_code: HTTP status code (200, 404, etc.) or None if failed
        is_broken: True if link is broken (4xx, 5xx, or error)
        error: Error message if request failed, None otherwise
        response_time: Time taken for the request in seconds
        file_path: Path to the file where URL was found
        line_number: Line number in file, or None if not applicable

    Example:
        >>> result = LinkResult(
        ...     url="https://example.com",
        ...     status_code=200,
        ...     is_broken=False,
        ...     error=None,
        ...     response_time=0.523,
        ...     file_path="docs/api.md",
        ...     line_number=42
        ... )
    """

    url: str
    status_code: Optional[int]
    is_broken: bool
    error: Optional[str]
    response_time: float
    file_path: str
    line_number: Optional[int]


class LinkChecker:
    """Asynchronously checks URLs for validity.

    Performs concurrent HTTP requests with configurable timeout and
    concurrency limits. Implements smart fallback strategies:
    1. Try HEAD request first (faster, less bandwidth)
    2. Fall back to GET if HEAD fails or returns 403/405
    3. Handle various error types gracefully

    Attributes:
        timeout: Request timeout in seconds
        max_concurrent: Maximum number of concurrent requests
        DEFAULT_HEADERS: Browser-like headers to avoid bot detection

    Example:
        >>> checker = LinkChecker(timeout=15, max_concurrent=100)
        >>> results = await checker.check_links(url_data)
        >>> broken = [r for r in results if r.is_broken]
        >>> print(f"Found {len(broken)} broken links")
    """

    # Browser-like headers to avoid bot detection
    # Note: Brotli encoding removed to avoid decode errors
    # These headers make requests appear to come from a real browser
    DEFAULT_HEADERS: Final[Dict[str, str]] = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    def __init__(self, timeout: int = 10, max_concurrent: int = 50, max_retries: int = 2) -> None:
        """Initialize the LinkChecker.

        Args:
            timeout: Request timeout in seconds (default: 10)
            max_concurrent: Maximum concurrent requests (default: 50)
                Higher values = faster but more resource intensive
                Recommended range: 10-200
            max_retries: Maximum number of retry attempts for failed requests (default: 2)
                Uses exponential backoff: 1s, 2s, 4s between retries

        Note:
            Setting max_concurrent too high may overwhelm servers
            or trigger rate limiting. Start conservative and increase
            if needed.
        """
        self.timeout: int = timeout
        self.max_concurrent: int = max_concurrent
        self.max_retries: int = max_retries

    async def check_links(
        self,
        url_data: Sequence[Tuple[Union[Path, str], Dict[str, Any]]],
        progress_callback: Optional[Callable[[int], None]] = None,
    ) -> List[LinkResult]:
        """Check a list of URLs concurrently.

        Performs asynchronous HTTP requests with semaphore-based
        concurrency control. Provides progress updates via callback.

        Args:
            url_data: Sequence of (file_path, url_info) tuples where
                url_info contains 'url', 'line_number', and 'context'
            progress_callback: Optional callback function called with
                completed count after each request finishes

        Returns:
            List of LinkResult objects, one for each URL checked.
            Results are returned in completion order, not input order.

        Example:
            >>> def on_progress(completed):
            ...     print(f"Progress: {completed} links checked")
            >>> results = await checker.check_links(urls, on_progress)

        Note:
            Uses asyncio.as_completed() for results as they finish,
            which provides better progress feedback but results are
            not in the original order.
        """

        semaphore = asyncio.Semaphore(self.max_concurrent)
        results: list[LinkResult] = []
        completed = 0

        # Create TCP connector
        connector = aiohttp.TCPConnector(
            ssl=False,  # Disable SSL verification for dev environments
            limit=self.max_concurrent,
            limit_per_host=10,  # Limit per host to avoid overwhelming servers
            ttl_dns_cache=300,  # Cache DNS for 5 minutes
        )

        async with aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers=self.DEFAULT_HEADERS,
        ) as session:
            tasks = [
                self._check_one_link(session, semaphore, file_path, url_info)
                for file_path, url_info in url_data
            ]

            # Process tasks as they complete to provide progress updates
            for coro in asyncio.as_completed(tasks):
                try:
                    result = await coro
                    results.append(result)
                    completed += 1
                    if progress_callback:
                        progress_callback(completed)
                except Exception:
                    # Handle unexpected exceptions
                    completed += 1
                    if progress_callback:
                        progress_callback(completed)

        return results

    async def _check_one_link(
        self,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        file_path: Union[Path, str],
        url_info: Dict[str, Any],
    ) -> LinkResult:
        """Check a single URL with retry logic and return Results.

        Implements exponential backoff retry strategy:
        - Retry 0: immediate
        - Retry 1: 1 second delay
        - Retry 2: 2 second delay
        - Retry 3: 4 second delay

        Args:
            session: Session Client
            semaphore: Semaphore for concurrency control
            file_path: File path where URL was found
            url_info: URL info dictionary

        Returns:
            LinkResult: Result of the single URL check
        """

        url = url_info["url"]

        async with semaphore:
            start_time = asyncio.get_event_loop().time()
            last_error = None

            # Retry loop with exponential backoff
            for attempt in range(self.max_retries + 1):
                try:
                    # Use HEAD request first (faster), fall back to GET if needed
                    async with session.head(
                        url,
                        allow_redirects=True,
                    ) as response:
                        response_time = asyncio.get_event_loop().time() - start_time

                        # Some servers return 403/405 for HEAD but work with GET
                        # If HEAD fails with 4xx, try GET as fallback
                        if response.status in {403, 405, 501}:
                            return await self._check_with_get(
                                session, url, file_path, url_info, start_time
                            )

                        return LinkResult(
                            url=url,
                            status_code=response.status,
                            is_broken=response.status >= 400,
                            error=None,
                            response_time=response_time,
                            file_path=str(file_path),
                            line_number=url_info.get("line_number"),
                        )

                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    last_error = e
                    # If this was the last attempt or it's a 4xx/5xx error from HEAD,
                    # try GET as fallback
                    if attempt == self.max_retries:
                        return await self._check_with_get(
                            session, url, file_path, url_info, start_time
                        )

                    # Exponential backoff: 2^attempt seconds (1s, 2s, 4s)
                    if attempt < self.max_retries:
                        await asyncio.sleep(2**attempt)
                    continue

                except Exception as e:
                    last_error = e  # type: ignore[assignment]
                    # Don't retry on unexpected errors
                    response_time = asyncio.get_event_loop().time() - start_time
                    return LinkResult(
                        url=url,
                        status_code=None,
                        is_broken=True,
                        error=f"Unexpected error: {str(e)[:50]}",
                        response_time=response_time,
                        file_path=str(file_path),
                        line_number=url_info.get("line_number"),
                    )

            # Should not reach here, but handle just in case
            response_time = asyncio.get_event_loop().time() - start_time
            return LinkResult(
                url=url,
                status_code=None,
                is_broken=True,
                error=f"Failed after {self.max_retries} retries: {str(last_error)[:50]}",
                response_time=response_time,
                file_path=str(file_path),
                line_number=url_info.get("line_number"),
            )

    async def _check_with_get(
        self,
        session: aiohttp.ClientSession,
        url: str,
        file_path: Union[Path, str],
        url_info: Dict[str, Any],
        start_time: float,
    ) -> LinkResult:
        """Fallback to GET request if HEAD fails, with retry logic."""
        last_error = None

        # Retry loop with exponential backoff
        for attempt in range(self.max_retries + 1):
            try:
                async with session.get(
                    url,
                    allow_redirects=True,
                ) as response:
                    response_time = asyncio.get_event_loop().time() - start_time

                    return LinkResult(
                        url=url,
                        status_code=response.status,
                        is_broken=response.status >= 400,
                        error=None,
                        response_time=response_time,
                        file_path=str(file_path),
                        line_number=url_info.get("line_number"),
                    )

            except asyncio.TimeoutError as e:
                last_error = e
                if attempt == self.max_retries:
                    response_time = asyncio.get_event_loop().time() - start_time
                    return LinkResult(
                        url=url,
                        status_code=None,
                        is_broken=True,
                        error=f"Timeout after {self.max_retries} retries",
                        response_time=response_time,
                        file_path=str(file_path),
                        line_number=url_info.get("line_number"),
                    )
                # Exponential backoff
                await asyncio.sleep(2**attempt)
                continue

            except aiohttp.ClientError as e:
                last_error = e  # type: ignore[assignment]
                if attempt == self.max_retries:
                    response_time = asyncio.get_event_loop().time() - start_time
                    return LinkResult(
                        url=url,
                        status_code=None,
                        is_broken=True,
                        error=f"Connection error after {self.max_retries} retries: {str(e)[:50]}",
                        response_time=response_time,
                        file_path=str(file_path),
                        line_number=url_info.get("line_number"),
                    )
                # Exponential backoff
                await asyncio.sleep(2**attempt)
                continue

            except Exception as e:
                # Don't retry on unexpected errors
                response_time = asyncio.get_event_loop().time() - start_time
                return LinkResult(
                    url=url,
                    status_code=None,
                    is_broken=True,
                    error=f"Unexpected error: {str(e)[:50]}",
                    response_time=response_time,
                    file_path=str(file_path),
                    line_number=url_info.get("line_number"),
                )

        # Should not reach here, but handle just in case
        response_time = asyncio.get_event_loop().time() - start_time
        return LinkResult(
            url=url,
            status_code=None,
            is_broken=True,
            error=f"Failed after {self.max_retries} retries: {str(last_error)[:50]}",
            response_time=response_time,
            file_path=str(file_path),
            line_number=url_info.get("line_number"),
        )
