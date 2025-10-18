"""Environment rules module for detecting development URLs.

This module provides the EnvironmentRules class which validates URLs
against environment-specific rules. In production mode, it flags URLs
that point to localhost, private networks, or development domains.
"""

import re
from typing import Sequence, Dict, Any, Tuple, Union, Optional, List, Final, Pattern
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuleViolation:
    """Represents a rule violation found in a file.

    This dataclass is immutable (frozen=True) to ensure it cannot
    be accidentally modified after creation.

    Attributes:
        url: The URL that violated the rule
        rule: Rule identifier (e.g., 'no-localhost-in-prod')
        severity: Severity level ('error', 'warning', 'info')
        message: Human-readable description of the violation
        file_path: Path to file where violation was found
        line_number: Line number in file, or None if not applicable

    Example:
        >>> violation = RuleViolation(
        ...     url="http://localhost:3000",
        ...     rule="no-localhost-in-prod",
        ...     severity="error",
        ...     message="Localhost URL in production",
        ...     file_path="config.js",
        ...     line_number=15
        ... )
    """

    url: str
    rule: str
    severity: str
    message: str
    file_path: str
    line_number: Optional[int]


class EnvironmentRules:
    """Checks URLs against predefined environment rules.

    Validates URLs to detect development-only references that should
    not appear in production code. Supports two modes:
    - dev mode: Allows all URLs (permissive)
    - prod mode: Flags localhost and private network URLs

    Attributes:
        mode: Operating mode ('dev' or 'prod')
        LOCALHOST_PATTERNS: Regex patterns for localhost/dev URLs
        localhost_regex: Compiled regex combining all patterns

    Example:
        >>> rules = EnvironmentRules(mode="prod")
        >>> violation = rules.check_url(
        ...     "http://localhost:8000",
        ...     "app.js",
        ...     42
        ... )
        >>> if violation:
        ...     print(f"Rule violated: {violation.rule}")
    """

    # Patterns that indicate development or localhost URLs
    # Each pattern is designed to catch common development environments
    LOCALHOST_PATTERNS: Final[List[str]] = [
        r"localhost",  # Standard localhost name
        r"127\.0\.0\.1",  # IPv4 loopback address
        r"0\.0\.0\.0",  # Non-routable meta-address
        r"192\.168\.\d{1,3}\.\d{1,3}",  # Private network Class C
        r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}",  # Private network Class A
        r"::1",  # IPv6 localhost
        r"\.local(?:/|$)",  # .local TLD (mDNS)
        r"\.test(?:/|$)",  # .test TLD (reserved for testing)
    ]

    def __init__(self, mode: str = "dev") -> None:
        """Initialize environment rules checker.

        Args:
            mode: Operating mode, either 'dev' or 'prod' (default: 'dev')
                - dev: Permissive, allows all URLs
                - prod: Strict, flags localhost/private network URLs

        Raises:
            ValueError: If mode is not 'dev' or 'prod'
        """
        if mode not in {"dev", "prod"}:
            raise ValueError(f"Mode must be 'dev' or 'prod', got '{mode}'")

        self.mode: str = mode
        # Compile all patterns into a single regex for efficient matching
        self.localhost_regex: Pattern = re.compile("|".join(self.LOCALHOST_PATTERNS), re.IGNORECASE)

    def check_url(
        self, url: str, file_path: str, line_number: Optional[int]
    ) -> Optional[RuleViolation]:
        """Check a single URL against environment rules.

        In production mode, validates that URL doesn't point to:
        - localhost or loopback addresses
        - Private network IP ranges
        - Development-only TLDs (.local, .test)

        Args:
            url: The URL to validate
            file_path: File path where the URL was found
            line_number: Line number where URL was found, or None

        Returns:
            RuleViolation if a rule is violated in prod mode,
            None otherwise or if in dev mode

        Example:
            >>> rules = EnvironmentRules(mode="prod")
            >>> result = rules.check_url(
            ...     "http://192.168.1.100",
            ...     "config.json",
            ...     12
            ... )
            >>> assert result is not None
            >>> assert result.rule == "no-localhost-in-prod"
        """
        if self.mode == "prod":
            if self.localhost_regex.search(url):
                return RuleViolation(
                    url=url,
                    rule="no-localhost-in-prod",
                    severity="error",
                    message="Localhost/development URL found in " "production mode",
                    file_path=file_path,
                    line_number=line_number,
                )
        return None

    def check_urls(
        self, urls_data: Sequence[Tuple[Union[Path, str], Dict[str, Any]]]
    ) -> List[RuleViolation]:
        """Check multiple URLs against environment rules.

        Efficiently validates a batch of URLs by calling check_url
        for each one and collecting violations.

        Args:
            urls_data: Sequence of (file_path, url_info) tuples where
                url_info contains 'url' and optionally 'line_number'

        Returns:
            List of RuleViolation objects for URLs that violate rules.
            Empty list if no violations found or in dev mode.

        Example:
            >>> rules = EnvironmentRules(mode="prod")
            >>> urls = [
            ...     ("app.js", {"url": "http://localhost:3000", "line_number": 5}),
            ...     ("api.js", {"url": "https://api.example.com", "line_number": 10})
            ... ]
            >>> violations = rules.check_urls(urls)
            >>> assert len(violations) == 1  # Only localhost violates
        """
        violations: list[RuleViolation] = []

        for file_path, url_info in urls_data:
            violation = self.check_url(url_info["url"], str(file_path), url_info.get("line_number"))

            if violation:
                violations.append(violation)

        return violations
