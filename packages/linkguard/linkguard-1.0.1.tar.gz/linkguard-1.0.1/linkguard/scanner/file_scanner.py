"""File scanner module for discovering files to scan for URLs.

This module provides the FileScanner class which recursively discovers
files in a directory tree based on file extensions and ignore patterns.
"""

from pathlib import Path
from typing import List, Set, Optional, Final
import fnmatch


class FileScanner:
    """Recursively discovers files to scan for links.

    The FileScanner walks through a directory tree and identifies files
    that should be scanned for URLs based on their file extensions. It
    respects ignore patterns to skip unwanted files and directories.

    Attributes:
        SUPPORTED_EXTENSIONS: Set of file extensions that will be scanned
        DEFAULT_IGNORE_PATTERNS: Set of default patterns to ignore
        root_dir: Root directory to start scanning from
        ignore_patterns: Combined set of ignore patterns

    Example:
        >>> scanner = FileScanner(Path("./docs"), {"draft-*", "*.backup"})
        >>> files = scanner.scan()
        >>> print(f"Found {len(files)} files to scan")
    """

    # File extensions we'll scan for URLs
    SUPPORTED_EXTENSIONS: Final[Set[str]] = {
        ".md",  # Markdown files
        ".html",  # HTML files
        ".htm",  # HTML files (alternative extension)
        ".json",  # JSON configuration files
        ".txt",  # Plain text files
        ".tsx",  # TypeScript React files
        ".jsx",  # JavaScript React files
        ".js",  # JavaScript files
    }

    DEFAULT_IGNORE_PATTERNS: Final[Set[str]] = {
        ".git",  # Git version control
        ".venv",  # Virtual environment
        "node_modules",  # Node.js dependencies
        "__pycache__",  # Python cache
        ".pytest_cache",  # Pytest cache
        ".idea",  # JetBrains IDE
        "dist",  # Distribution directory
        "build",  # Build directory
    }

    def __init__(self, root_dir: Path, ignore_patterns: Optional[Set[str]] = None) -> None:
        """Initialize the FileScanner.

        Args:
            root_dir: Root directory to start scanning from
            ignore_patterns: Additional patterns to ignore (merged with defaults)

        Raises:
            TypeError: If root_dir is not a Path object
        """
        if not isinstance(root_dir, Path):
            raise TypeError(f"root_dir must be a Path object, got {type(root_dir)}")

        self.root_dir: Path = Path(root_dir)
        self.ignore_patterns: Set[str] = ignore_patterns or set()
        # Merge with default patterns to create comprehensive ignore list
        self.ignore_patterns.update(self.DEFAULT_IGNORE_PATTERNS)

    def scan(self) -> List[Path]:
        """Recursively scan the root directory for supported files.

        Walks through the directory tree starting from root_dir and
        identifies all files with supported extensions that don't match
        ignore patterns or start with a dot (hidden files).

        Returns:
            List of Path objects representing files to scan for URLs.
            Returns empty list if no files found or root_dir doesn't exist.

        Example:
            >>> scanner = FileScanner(Path("./docs"))
            >>> files = scanner.scan()
            >>> markdown_files = [f for f in files if f.suffix == ".md"]
        """
        discovered_files: List[Path] = []

        for file_path in self.root_dir.rglob("*"):
            if file_path.is_file():
                # Check if file has supported extension
                if file_path.suffix in self.SUPPORTED_EXTENSIONS:
                    # Skip if matches ignore patterns
                    if not self._should_ignore(file_path):
                        # Skip hidden files (starting with .)
                        if not file_path.name.startswith("."):
                            discovered_files.append(file_path)

        return discovered_files

    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file path matches any ignore patterns.

        Args:
            file_path: File path to check against ignore patterns

        Returns:
            True if the file should be ignored, False otherwise

        Note:
            Uses fnmatch for pattern matching, which supports wildcards:
            - * matches any sequence of characters
            - ? matches any single character
            - [seq] matches any character in seq
        """
        parts: tuple = file_path.parts

        for pattern in self.ignore_patterns:
            # Check if any part of the path matches the ignore pattern
            for part in parts:
                if fnmatch.fnmatch(part, pattern):
                    return True

        return False
