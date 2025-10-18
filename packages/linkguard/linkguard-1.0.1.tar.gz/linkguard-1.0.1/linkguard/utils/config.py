"""Configuration loading and management for LinkGuard.

This module handles configuration precedence across multiple sources:
1. CLI arguments (highest priority)
2. linkguard.config.json file
3. Default values (lowest priority)

It also supports ignore patterns from:
- .linkguardignore (explicit configuration, takes full priority)
- .gitignore files (fallback when .linkguardignore doesn't exist)

Classes:
    Config: Configuration manager with file loading, merging, and pattern matching.

Functions:
    load_config: Factory function to create Config with CLI overrides.

Example:
    >>> config = Config(Path("/path/to/project"))
    >>> config.merge_cli_config({"mode": "prod", "timeout": 15})
    >>> print(config.get("mode"))
    'prod'
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Final
import fnmatch


class Config:
    """Configuration manager with multi-source loading and pattern-based filtering.

    Manages configuration hierarchy: CLI args > config file > defaults.
    Supports ignore patterns from .linkguardignore (priority) or .gitignore (fallback).

    Attributes:
        project_root (Path): Root directory of the project being scanned.
        config_file (Path): Path to linkguard.config.json file.
        ignore_file (Path): Path to .linkguardignore file.
        config (Dict[str, Any]): Merged configuration dictionary.

    Class Attributes:
        DEFAULT_CONFIG (Dict[str, Any]): Default configuration values.

    Example:
        >>> config = Config(Path("/my/project"))
        >>> config.merge_cli_config({"timeout": 20})
        >>> if not config.should_ignore_path(Path("src/main.py")):
        ...     # Process file
    """

    # Default configuration values (class constant)
    DEFAULT_CONFIG: Final[Dict[str, Any]] = {
        "mode": "dev",
        "timeout": 10,
        "concurrency": 50,
        "ignore_patterns": [],
        "exclude_urls": [],
        "strict_ssl": False,
    }

    def __init__(self, project_root: Path):
        """Initialize configuration manager for a project.

        Loads configuration from linkguard.config.json and ignore patterns
        from .linkguardignore (or .gitignore files as fallback).

        Args:
            project_root: Root directory of the project to scan.
        """
        self.project_root = project_root
        self.config_file = project_root / "linkguard.config.json"
        self.ignore_file = project_root / ".linkguardignore"
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from linkguard.config.json and ignore files.

        Loads JSON config if present (merges with defaults), then loads ignore
        patterns from .linkguardignore (priority) or .gitignore files (fallback).
        Silently falls back to defaults on errors.
        """
        # Load JSON config if exists
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                    # Merge with default config
                    self.config.update(file_config)

            except (json.JSONDecodeError, PermissionError, IOError):
                # Silently fall back to defaults instead of raising
                pass
            except Exception:
                # Catch all other exceptions
                pass

        # Load ignore patterns with fallback logic:
        # 1. If .linkguardignore exists → use only that (explicit override)
        # 2. Otherwise → recursively collect all .gitignore files
        all_patterns: Set[str] = set()

        if self.ignore_file.exists():
            # .linkguardignore takes priority (explicit configuration)
            try:
                all_patterns = self._parse_ignore_file(self.ignore_file)
            except Exception:
                # Silently fall back if ignore file is unreadable
                all_patterns = set()
        else:
            # Fallback: Collect all .gitignore patterns recursively
            all_patterns = self._collect_gitignore_patterns()

        # Merge with existing patterns from JSON config
        existing = set(self.config.get("ignore_patterns", []))
        self.config["ignore_patterns"] = list(existing.union(all_patterns))

    def _collect_gitignore_patterns(self) -> Set[str]:
        """Recursively collect patterns from all .gitignore files in the project.

        Used as a fallback when .linkguardignore doesn't exist. Walks the project
        tree and aggregates all .gitignore patterns.

        Returns:
            Set of ignore patterns from all .gitignore files.
        """
        patterns: Set[str] = set()

        for gitignore_path in self.project_root.rglob(".gitignore"):
            try:
                patterns.update(self._parse_ignore_file(gitignore_path))
            except Exception:
                # Skip unreadable .gitignore files
                continue

        return patterns

    def _parse_ignore_file(self, ignore_path: Path) -> Set[str]:
        """Parse a .gitignore or .linkguardignore file.

        Extracts patterns from file, skipping comments and empty lines.
        Strips trailing slashes from directory patterns and handles
        negation patterns (for future enhancements).

        Args:
            ignore_path: Path to the ignore file.

        Returns:
            Set of ignore patterns.

        Raises:
            ValueError: If file cannot be read.
        """
        patterns: Set[str] = set()

        try:
            with open(ignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        continue

                    # Handle negation patterns (for future enhancements)
                    if line.startswith("!"):
                        # Remove negation for now, can be handled later
                        line = line[1:].strip()

                    # Remove trailing slashes for directory patterns
                    if line.endswith("/"):
                        line = line[:-1]

                    patterns.add(line)

        except Exception as e:
            # Re-raise to be caught by caller
            raise ValueError(f"Error reading ignore file {ignore_path}: {e}")

        return patterns

    def merge_cli_config(self, cli_config: Dict[str, Any]) -> None:
        """Merge command line configuration with existing config.

        CLI arguments override config file values. Ignore patterns are
        merged (union) rather than replaced to preserve file-based patterns.

        Args:
            cli_config: Dictionary of CLI argument overrides.

        Example:
            >>> config.merge_cli_config({"mode": "prod", "timeout": 20})
        """
        for key, value in cli_config.items():
            if key == "ignore_patterns" and value:
                # Merge ignore patterns from CLI with existing ones
                existing = set(self.config.get("ignore_patterns", []))
                self.config["ignore_patterns"] = list(existing.union(set(value)))
            else:
                # Override other values
                self.config[key] = value

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get a configuration value with optional default.

        Args:
            key: Configuration key to retrieve.
            default: Value to return if key not found.

        Returns:
            Configuration value or default.
        """
        return self.config.get(key, default)

    def should_ignore_path(self, file_path: Path) -> bool:
        """Check if a given path matches any ignore patterns.

        Uses fnmatch for glob-style pattern matching. Checks patterns against:
        - Individual path components (for directory matching)
        - Full path string
        - Filename only

        Args:
            file_path: Path to check against ignore patterns.

        Returns:
            True if path should be ignored, False otherwise.

        Example:
            >>> config.should_ignore_path(Path("dist/bundle.js"))
            True  # if "dist" is in ignore patterns
        """
        ignore_patterns = self.config.get("ignore_patterns", [])

        # Convert path to string for pattern matching
        path_str = str(file_path)
        path_parts = file_path.parts

        for pattern in ignore_patterns:
            # Handle directory patterns (with or without trailing slash)
            dir_pattern = pattern.rstrip("/")

            # Check if any part of the path matches the pattern
            for part in path_parts:
                if fnmatch.fnmatch(part, dir_pattern):
                    return True

            # Also check the full path
            if fnmatch.fnmatch(path_str, pattern):
                return True

            # Check relative path patterns
            if fnmatch.fnmatch(file_path.name, dir_pattern):
                return True

        return False

    def should_exclude_url(self, url: str) -> bool:
        """Check if a URL matches any exclusion patterns.

        Uses fnmatch for glob-style pattern matching. Useful for excluding
        known problematic domains or internal URLs from validation.

        Args:
            url: URL string to check.

        Returns:
            True if URL matches any exclude pattern, False otherwise.

        Example:
            >>> config.should_exclude_url("https://example.com/test")
            True  # if "*example.com*" in exclude_urls
        """
        exclude_patterns = self.config.get("exclude_urls", [])

        for pattern in exclude_patterns:
            if fnmatch.fnmatch(url, pattern):
                return True

        return False

    def get_ignore_patterns(self) -> List[str]:
        """Get the list of ignore patterns.

        Returns:
            List of file/directory patterns to exclude from scanning.
        """
        patterns = self.config.get("ignore_patterns", [])
        return list(patterns) if patterns else []

    def get_exclude_urls(self) -> List[str]:
        """Get the list of excluded URL patterns.

        Returns:
            List of URL patterns to skip during validation.
        """
        urls = self.config.get("exclude_urls", [])
        return list(urls) if urls else []

    def __repr__(self) -> str:
        return f"Config({self.config})"


def load_config(project_root: Path, cli_overrides: Optional[Dict[str, Any]] = None) -> Config:
    """Factory function to load configuration with optional CLI overrides.

    Creates a Config instance for the project and applies CLI argument
    overrides if provided. This is the recommended way to create Config
    objects in the CLI application.

    Args:
        project_root: Root directory of the project to scan.
        cli_overrides: Optional dictionary of CLI arguments to override config.

    Returns:
        Configured Config instance with all sources merged.

    Example:
        >>> config = load_config(
        ...     Path("/my/project"),
        ...     {"mode": "prod", "timeout": 15}
        ... )
        >>> print(config.get("mode"))
        'prod'
    """
    config = Config(project_root)

    if cli_overrides:
        config.merge_cli_config(cli_overrides)

    return config
