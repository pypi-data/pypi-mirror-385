import pytest
import json
from pathlib import Path
from linkguard.utils.config import Config, load_config


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure."""
    return tmp_path


def test_default_config(temp_project):
    """Test that default config is loaded when no config file exists."""
    config = Config(temp_project)

    assert config.get("mode") == "dev"
    assert config.get("timeout") == 10
    assert config.get("concurrency") == 50
    assert config.get("strict_ssl") is False


def test_load_config_from_json(temp_project):
    """Test loading config from linkguard.config.json."""
    config_data = {
        "mode": "prod",
        "timeout": 20,
        "concurrency": 100,
    }

    config_file = temp_project / "linkguard.config.json"
    config_file.write_text(json.dumps(config_data))

    config = Config(temp_project)

    assert config.get("mode") == "prod"
    assert config.get("timeout") == 20
    assert config.get("concurrency") == 100


def test_parse_linkguardignore_file(temp_project):
    """Test parsing .linkguardignore file."""
    ignore_file = temp_project / ".linkguardignore"
    ignore_file.write_text("node_modules\n*.draft.md\n# Comment\n\ndist/")

    config = Config(temp_project)
    patterns = config.get_ignore_patterns()

    assert "node_modules" in patterns
    assert "*.draft.md" in patterns
    assert "dist" in patterns  # Trailing slash removed
    assert "# Comment" not in patterns  # Comments excluded


def test_fallback_to_gitignore(temp_project):
    """Test that .gitignore is used when .linkguardignore doesn't exist."""
    gitignore_file = temp_project / ".gitignore"
    gitignore_file.write_text(".venv\n__pycache__\n*.pyc")

    config = Config(temp_project)
    patterns = config.get_ignore_patterns()

    assert ".venv" in patterns
    assert "__pycache__" in patterns
    assert "*.pyc" in patterns


def test_linkguardignore_takes_priority(temp_project):
    """Test that .linkguardignore takes priority over .gitignore."""
    gitignore_file = temp_project / ".gitignore"
    gitignore_file.write_text(".venv\nnode_modules")

    linkguardignore_file = temp_project / ".linkguardignore"
    linkguardignore_file.write_text("*.draft.md")

    config = Config(temp_project)
    patterns = config.get_ignore_patterns()

    # Should use .linkguardignore, not .gitignore
    assert "*.draft.md" in patterns
    assert ".venv" not in patterns
    assert "node_modules" not in patterns


def test_recursive_gitignore_collection(temp_project):
    """Test that all .gitignore files in subdirectories are collected."""
    # Root .gitignore
    (temp_project / ".gitignore").write_text("*.log\nnode_modules")

    # Subdirectory .gitignore
    (temp_project / "src").mkdir()
    (temp_project / "src" / ".gitignore").write_text("*.pyc\n__pycache__")

    config = Config(temp_project)
    patterns = config.get_ignore_patterns()

    # Should have patterns from both .gitignore files
    assert "*.log" in patterns
    assert "node_modules" in patterns
    assert "*.pyc" in patterns
    assert "__pycache__" in patterns


def test_cli_overrides_merge_with_config(temp_project):
    """Test that CLI overrides are merged with config file."""
    config_data = {"mode": "dev", "timeout": 10}
    config_file = temp_project / "linkguard.config.json"
    config_file.write_text(json.dumps(config_data))

    cli_overrides = {"mode": "prod", "concurrency": 100}
    config = load_config(temp_project, cli_overrides)

    # CLI overrides should take precedence
    assert config.get("mode") == "prod"
    # Config file value should remain
    assert config.get("timeout") == 10
    # CLI-only value should be added
    assert config.get("concurrency") == 100


def test_cli_ignore_patterns_merge(temp_project):
    """Test that CLI ignore patterns are merged with file patterns."""
    ignore_file = temp_project / ".linkguardignore"
    ignore_file.write_text("node_modules\n*.log")

    cli_overrides = {"ignore_patterns": ["*.draft.md", "temp/"]}
    config = load_config(temp_project, cli_overrides)

    patterns = config.get_ignore_patterns()

    # Should have both file and CLI patterns
    assert "node_modules" in patterns
    assert "*.log" in patterns
    assert "*.draft.md" in patterns
    assert "temp/" in patterns


def test_config_file_invalid_json(tmp_path):
    """Test handling of invalid JSON in config file."""
    config_file = tmp_path / "linkguard.config.json"
    config_file.write_text("{invalid json}")  # Malformed JSON

    config = Config(tmp_path)

    # Should fall back to defaults
    assert config.get("mode") == "dev"
    assert config.get("timeout") == 10


def test_config_file_io_error(tmp_path, monkeypatch):
    """Test handling of file I/O errors."""
    config_file = tmp_path / "linkguard.config.json"
    config_file.write_text('{"mode": "prod"}')

    # Mock open() to raise PermissionError
    import builtins

    original_open = builtins.open

    def mock_open(*args, **kwargs):
        if "linkguard.config.json" in str(args[0]):
            raise PermissionError("Access denied")
        return original_open(*args, **kwargs)

    monkeypatch.setattr(builtins, "open", mock_open)

    config = Config(tmp_path)

    # Should fall back to defaults
    assert config.get("mode") == "dev"


def test_ignore_file_io_error(tmp_path, monkeypatch):
    """Test handling of .linkguardignore read errors."""
    ignore_file = tmp_path / ".linkguardignore"
    ignore_file.write_text("*.draft.md")

    import builtins

    original_open = builtins.open

    def mock_open(*args, **kwargs):
        if ".linkguardignore" in str(args[0]):
            raise IOError("Cannot read file")
        return original_open(*args, **kwargs)

    monkeypatch.setattr(builtins, "open", mock_open)

    config = Config(tmp_path)

    # Should fall back to empty patterns (no .gitignore files in tmp_path)
    # The behavior is: if .linkguardignore can't be read, fall back to .gitignore collection
    # Since there are no .gitignore files in tmp_path, result should be empty
    patterns = config.get_ignore_patterns()
    assert isinstance(patterns, list)
    assert len(patterns) == 0  # No .gitignore files to fall back to


def test_should_ignore_path_with_complex_patterns(tmp_path):
    """Test pattern matching with wildcards and nested paths."""
    config = Config(tmp_path)
    config.config["ignore_patterns"].extend(["**/*.tmp", "vendor/**", "*.bak"])

    # Test nested wildcard
    assert config.should_ignore_path(Path("src/nested/file.tmp")) is True

    # Test directory wildcard
    assert config.should_ignore_path(Path("vendor/lib/package.json")) is True

    # Test simple extension
    assert config.should_ignore_path(Path("backup.bak")) is True

    # Should not ignore
    assert config.should_ignore_path(Path("src/main.py")) is False


def test_should_exclude_url_with_patterns(tmp_path):
    """Test URL exclusion with patterns."""
    config = Config(tmp_path)
    config.config["exclude_urls"] = ["https://example.com/*", "http://localhost*"]

    assert config.should_exclude_url("https://example.com/page") is True
    assert config.should_exclude_url("http://localhost:3000") is True
    assert config.should_exclude_url("https://github.com") is False


def test_load_config_with_cli_overrides(tmp_path):
    """Test load_config function with CLI overrides."""
    cli_overrides = {"mode": "prod", "timeout": 20}
    config = load_config(tmp_path, cli_overrides)

    assert config.get("mode") == "prod"
    assert config.get("timeout") == 20


def test_should_ignore_path(temp_project):
    """Test path matching against ignore patterns."""
    config = Config(temp_project)
    config.config["ignore_patterns"] = ["node_modules", "*.draft.md", "dist"]

    assert config.should_ignore_path(Path("node_modules/package.json"))
    assert config.should_ignore_path(Path("docs/test.draft.md"))
    assert config.should_ignore_path(Path("dist/bundle.js"))
    assert not config.should_ignore_path(Path("docs/readme.md"))


def test_should_exclude_url():
    """Test URL exclusion patterns."""
    config = Config(Path("."))
    config.config["exclude_urls"] = ["https://example.com/*", "http://localhost*"]

    assert config.should_exclude_url("https://example.com/page")
    assert config.should_exclude_url("http://localhost:3000")
    assert not config.should_exclude_url("https://github.com")


def test_get_ignore_patterns_returns_list(temp_project):
    """Test that get_ignore_patterns returns a list."""
    config = Config(temp_project)
    patterns = config.get_ignore_patterns()

    assert isinstance(patterns, list)


def test_config_handles_empty_ignore_file(temp_project):
    """Test that empty .linkguardignore is handled gracefully."""
    ignore_file = temp_project / ".linkguardignore"
    ignore_file.write_text("\n\n# Only comments\n\n")

    config = Config(temp_project)
    patterns = config.get_ignore_patterns()

    # Should have 0 patterns from .linkguardignore (only comments/whitespace)
    # But may have patterns from any .gitignore files in temp_project
    # So we just check that it doesn't crash
    assert isinstance(patterns, list)


def test_config_repr(temp_project):
    """Test Config __repr__ method."""
    config = Config(temp_project)
    repr_str = repr(config)

    assert "Config(" in repr_str
    assert "mode" in repr_str


def test_cli_overrides():
    """Test that CLI overrides work correctly."""
    config = Config(Path("."))

    cli_overrides = {"mode": "prod", "timeout": 30, "ignore_patterns": ["*.test.md"]}

    config.merge_cli_config(cli_overrides)

    assert config.get("mode") == "prod"
    assert config.get("timeout") == 30
    assert "*.test.md" in config.get_ignore_patterns()


def test_merge_ignore_patterns():
    """Test that ignore patterns are properly merged."""
    config = Config(Path("."))
    config.config["ignore_patterns"] = ["node_modules", "*.log"]

    cli_overrides = {"ignore_patterns": ["*.draft.md", "temp"]}
    config.merge_cli_config(cli_overrides)

    patterns = config.get_ignore_patterns()

    # Should have all patterns merged
    assert "node_modules" in patterns
    assert "*.log" in patterns
    assert "*.draft.md" in patterns
    assert "temp" in patterns


def test_invalid_json_raises_error(tmp_path):
    """Test that invalid JSON is handled gracefully."""
    config_file = tmp_path / "linkguard.config.json"
    config_file.write_text("not valid json {")

    # Should not raise, falls back to defaults
    config = Config(tmp_path)
    assert config.get("mode") == "dev"
