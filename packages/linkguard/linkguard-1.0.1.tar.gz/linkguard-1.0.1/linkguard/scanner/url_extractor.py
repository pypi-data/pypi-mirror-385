"""URL extraction module for parsing URLs from various file formats.

This module provides the URLExtractor class which extracts HTTP/HTTPS URLs
from different file types including Markdown, HTML, JSON, and JavaScript files.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Final, Set, Tuple, Optional
from bs4 import BeautifulSoup
import json


class URLExtractor:
    """Extract URLs from different file formats.

    Supports multiple file formats and extraction strategies:
    - Markdown: Extracts from [text](url) syntax and bare URLs
    - HTML: Extracts from href and src attributes using BeautifulSoup
    - JSON: Recursively searches for URL strings
    - JavaScript/TypeScript: Extracts bare URLs from code

    Attributes:
        URL_PATTERN: Compiled regex for matching HTTP/HTTPS URLs
        MD_LINK_PATTERN: Compiled regex for Markdown link syntax
        resolve_relative: Whether to resolve relative file paths to absolute file:// URLs

    Example:
        >>> extractor = URLExtractor(resolve_relative=True)
        >>> urls = extractor.extract_from_file(Path("README.md"))
        >>> for url_info in urls:
        ...     print(f"{url_info['url']} at line {url_info['line_number']}")
    """

    def __init__(self, resolve_relative: bool = False) -> None:
        """Initialize the URLExtractor.

        Args:
            resolve_relative: If True, resolve relative URLs (e.g., ../docs/api.md)
                to absolute file:// URLs. Default is False for backward compatibility.
        """
        self.resolve_relative = resolve_relative

    # URL regex pattern - matches http:// or https:// URLs
    # Modified to exclude trailing punctuation and capture complete URLs
    # Pattern breakdown:
    # - https?:// : Match http:// or https://
    # - (?:www\.)? : Optional www. prefix
    # - [-a-zA-Z0-9@:%._\+~#=]{1,256} : Domain characters
    # - \.[a-zA-Z0-9()]{1,6} : TLD (top-level domain)
    # - \b : Word boundary
    # - (?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*) : Path and query parameters
    URL_PATTERN: Final[re.Pattern] = re.compile(
        r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\."
        r"[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)"
    )

    # Markdown link pattern [text](url)
    # Captures: (link text, URL)
    MD_LINK_PATTERN: Final[re.Pattern] = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    def extract_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract URLs from a file based on its extension.

        Routes to appropriate extraction method based on file extension.
        Supported formats:
        - .md, .txt: Markdown and plain text extraction
        - .html, .htm: HTML attribute extraction
        - .json: Recursive JSON value extraction
        - .js, .jsx, .ts, .tsx: JavaScript/TypeScript extraction

        Args:
            file_path: Path to the file to extract URLs from

        Returns:
            List of dictionaries containing:
                - url (str): The extracted URL
                - line_number (int | None): Line number where URL was found
                - context (str): Surrounding context (truncated to 60 chars)

        Example:
            >>> extractor = URLExtractor()
            >>> results = extractor.extract_from_file(Path("docs/api.md"))
            >>> print(f"Found {len(results)} URLs")
        """
        suffix = file_path.suffix.lower()

        if suffix in {".md", ".txt"}:
            return self._extract_from_text(file_path)
        elif suffix in {".html", ".htm"}:
            return self._extract_from_html(file_path)
        elif suffix == ".json":
            return self._extract_from_json(file_path)
        elif suffix in {".js", ".jsx", ".tsx", ".ts"}:
            return self._extract_from_text(file_path)

        return []

    def _extract_from_text(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract URLs from plain text/markdown files.

        Extraction strategy:
        1. First extracts Markdown-style links [text](url)
        2. Then extracts bare URLs (http://... or https://...)
        3. Deduplicates URLs found on the same line

        Args:
            file_path: Path to text/markdown file

        Returns:
            List of URL dictionaries with url, line_number, and context

        Note:
            Ignores file encoding errors to handle binary or malformed files
            gracefully. Only includes URLs starting with http:// or https://
        """
        urls: List[Dict[str, Any]] = []
        seen_urls: Set[Tuple[str, int]] = set()  # (url, line_number) tuples for deduplication

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, start=1):
                # Find markdown-style links [text](url) FIRST
                md_matches = self.MD_LINK_PATTERN.findall(line)

                for text, url in md_matches:
                    # Resolve relative URLs if enabled
                    if self.resolve_relative:
                        resolved_url = self._resolve_relative_url(file_path, url)
                        if resolved_url is None:
                            # Relative path doesn't exist, skip it
                            continue
                        url = resolved_url

                    # Only include URLs starting with http://, https://, or file://
                    if url.startswith(("http://", "https://", "file://")):
                        # Clean URL and create unique key
                        clean_url = self._clean_url(url)
                        url_key = (clean_url, line_num)

                        if url_key not in seen_urls:
                            seen_urls.add(url_key)
                            urls.append(
                                {
                                    "url": clean_url,
                                    "line_number": line_num,
                                    "context": line.strip()[:60],
                                }
                            )

                # Find bare URLs (http:// or https://)
                # But skip them if they're part of markdown links
                url_matches = self.URL_PATTERN.findall(line)
                for url in url_matches:
                    clean_url = self._clean_url(url)
                    url_key = (clean_url, line_num)

                    # Only add if we haven't seen this URL on this line (avoids markdown duplicates)
                    if url_key not in seen_urls:
                        seen_urls.add(url_key)
                        urls.append(
                            {
                                "url": clean_url,
                                "line_number": line_num,
                                "context": line.strip()[:60],
                            }
                        )

        return urls

    def _clean_url(self, url: str) -> str:
        """Remove trailing punctuation from URLs.

        Strips common trailing punctuation that might be captured
        by the URL regex but isn't actually part of the URL.

        Args:
            url: Raw URL string

        Returns:
            Cleaned URL with trailing punctuation removed

        Example:
            >>> extractor._clean_url("https://example.com.")
            'https://example.com'
            >>> extractor._clean_url("https://example.com);")
            'https://example.com'
        """
        # Remove trailing ), ., ,, ;, etc.
        return url.rstrip(".,;:)")

    def _resolve_relative_url(self, base_file_path: Path, url: str) -> Optional[str]:
        """Resolve relative URLs to absolute file:// URLs.

        Converts relative file paths (e.g., ../docs/api.md, ./config.json)
        to absolute file:// URLs if the file exists on disk.

        Args:
            base_file_path: Path to the file containing the URL
            url: The URL to resolve (can be relative or absolute)

        Returns:
            Absolute file:// URL if relative path exists, original URL if absolute,
            or None if relative path doesn't exist

        Example:
            >>> extractor._resolve_relative_url(Path("/project/docs/api.md"), "../README.md")
            'file:///project/README.md'
            >>> extractor._resolve_relative_url(Path("/project/docs/api.md"), "https://example.com")
            'https://example.com'
        """
        # If it's already an absolute URL (http/https/ftp/etc), return as-is
        if url.startswith(("http://", "https://", "ftp://", "file://", "//")):
            return url

        # If it's an absolute path (starts with /), return as file:// URL
        if url.startswith("/"):
            abs_path = Path(url)
            if abs_path.exists():
                return f"file:///{abs_path.as_posix()}"
            return None

        # Try to resolve relative path
        try:
            # Resolve relative to the directory containing the source file
            resolved = (base_file_path.parent / url).resolve()

            # Check if the resolved path exists
            if resolved.exists():
                # Convert to file:// URL with forward slashes
                return f"file:///{resolved.as_posix()}"
            else:
                # Path doesn't exist, return None to skip it
                return None
        except (ValueError, OSError):
            # Invalid path, return None
            return None

    def _extract_from_html(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract URLs from HTML files using BeautifulSoup.

        Extracts URLs from common HTML attributes:
        - <a href="...">: Hyperlinks
        - <img src="...">: Images
        - <link href="...">: Stylesheets and resources
        - <script src="...">: JavaScript files

        Args:
            file_path: Path to HTML file

        Returns:
            List of URL dictionaries. Line numbers are None for HTML
            since BeautifulSoup doesn't track line numbers.

        Note:
            Only extracts absolute URLs (starting with http:// or https://).
            Relative URLs are ignored.
        """
        urls = []

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Extract from <a href="">
        for tag in soup.find_all("a", href=True):
            url = tag.get("href")
            if isinstance(url, str) and url.startswith(("http://", "https://")):
                urls.append(
                    {
                        "url": url,
                        "line_number": None,
                        "context": f'<a href="{url}">',
                    }
                )

        # Extract from <img src="">, <link href="">, <script src="">
        for tag in soup.find_all(["img", "link", "script"]):
            url = tag.get("src") or tag.get("href")

            if isinstance(url, str) and url.startswith(("http://", "https://")):
                urls.append(
                    {
                        "url": url,
                        "line_number": None,
                        "context": f'<{tag.name} src="{url}">',
                    }
                )

        return urls

    def _extract_from_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract URLs from JSON files.

        Recursively searches through JSON structure (objects, arrays, primitives)
        to find string values that are HTTP/HTTPS URLs.

        Args:
            file_path: Path to JSON file

        Returns:
            List of URL dictionaries. Context includes JSON path to the URL.

        Note:
            Gracefully handles invalid JSON by returning empty list.
        """
        urls: List[Dict[str, Any]] = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)

            self._search_json_for_urls(data, urls)
        except json.JSONDecodeError:
            # Return empty list for invalid JSON
            pass

        return urls

    def _search_json_for_urls(self, obj: Any, urls: List[Dict[str, Any]], path: str = "") -> None:
        """Recursively search JSON object for URL strings.

        Traverses the JSON structure and identifies string values that
        are HTTP/HTTPS URLs. Builds a JSON path for context.

        Args:
            obj: Current JSON object/value being searched
            urls: List to append found URLs to (modified in place)
            path: Current JSON path (e.g., '.config.apiUrl')

        Note:
            Uses depth-first search to traverse nested structures.
        """
        if isinstance(obj, dict):
            for key, value in obj.items():
                self._search_json_for_urls(value, urls, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._search_json_for_urls(item, urls, f"{path}[{i}]")
        elif isinstance(obj, str):
            # Only match strings that start with http:// or https://
            if obj.startswith(("http://", "https://")):
                urls.append(
                    {
                        "url": obj,
                        "line_number": None,
                        "context": f"JSON path: {path}",
                    }
                )
