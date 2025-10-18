import pytest
from pathlib import Path
from linkguard.scanner.file_scanner import FileScanner


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project structure."""
    # Create test files
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "readme.md").write_text("# Test")
    (tmp_path / "docs" / "guide.md").write_text("# Guide")

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "index.html").write_text("<a href='#'>Test</a>")
    (tmp_path / "src" / "app.js").write_text('const url = "https://example.com";')

    (tmp_path / "config.json").write_text('{"api": "https://api.example.com"}')

    # Create directories that should be ignored
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "pkg.json").write_text("{}")

    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("[core]")

    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "bundle.js").write_text("// compiled")

    return tmp_path


def test_scan_discovers_markdown_files(temp_project):
    """Test that scanner finds all markdown files."""
    scanner = FileScanner(temp_project)
    files = scanner.scan()

    md_files = [f for f in files if f.suffix == ".md"]
    assert len(md_files) == 2
    assert any(f.name == "readme.md" for f in md_files)
    assert any(f.name == "guide.md" for f in md_files)


def test_scan_discovers_html_files(temp_project):
    """Test that scanner finds HTML files."""
    scanner = FileScanner(temp_project)
    files = scanner.scan()

    html_files = [f for f in files if f.suffix in {".html", ".htm"}]
    assert len(html_files) >= 1
    assert any(f.name == "index.html" for f in html_files)


def test_scan_discovers_json_files(temp_project):
    """Test that scanner finds JSON files."""
    scanner = FileScanner(temp_project)
    files = scanner.scan()

    json_files = [f for f in files if f.suffix == ".json"]
    assert len(json_files) >= 1
    assert any(f.name == "config.json" for f in json_files)


def test_scan_excludes_node_modules(temp_project):
    """Test that node_modules is excluded by default."""
    scanner = FileScanner(temp_project)
    files = scanner.scan()

    # node_modules should be excluded by default
    node_files = [f for f in files if "node_modules" in f.parts]
    assert len(node_files) == 0


def test_scan_excludes_git_directory(temp_project):
    """Test that .git directory is excluded."""
    scanner = FileScanner(temp_project)
    files = scanner.scan()

    git_files = [f for f in files if ".git" in f.parts]
    assert len(git_files) == 0


def test_scan_excludes_dist_directory(temp_project):
    """Test that dist directory is excluded by default."""
    scanner = FileScanner(temp_project)
    files = scanner.scan()

    # Check that 'dist' is in the path parts (as a directory), not just in filename
    dist_files = [f for f in files if "dist" in f.parts]
    assert len(dist_files) == 0


def test_scan_respects_ignore_patterns(temp_project):
    """Test that custom ignore patterns are respected."""
    (temp_project / "test.draft.md").write_text("# Draft")
    (temp_project / "backup.md").write_text("# Backup")

    scanner = FileScanner(temp_project, ignore_patterns={"*.draft.md", "backup.md"})
    files = scanner.scan()

    draft_files = [f for f in files if "draft" in str(f)]
    backup_files = [f for f in files if "backup" in str(f)]

    assert len(draft_files) == 0
    assert len(backup_files) == 0


def test_scan_with_wildcard_patterns(temp_project):
    """Test wildcard patterns in ignore list."""
    (temp_project / "temp1.md").write_text("# Temp")
    (temp_project / "temp2.md").write_text("# Temp")
    (temp_project / "final.md").write_text("# Final")

    scanner = FileScanner(temp_project, ignore_patterns={"temp*.md"})
    files = scanner.scan()

    temp_files = [f for f in files if "temp" in f.name]
    final_files = [f for f in files if "final" in f.name]

    assert len(temp_files) == 0
    assert len(final_files) == 1


def test_scan_empty_directory(tmp_path):
    """Test scanning an empty directory."""
    scanner = FileScanner(tmp_path)
    files = scanner.scan()

    assert len(files) == 0


def test_scan_nested_directories(temp_project):
    """Test scanning deeply nested directories."""
    nested = temp_project / "docs" / "api" / "v1"
    nested.mkdir(parents=True)
    (nested / "endpoints.md").write_text("# API Endpoints")

    scanner = FileScanner(temp_project)
    files = scanner.scan()

    nested_files = [f for f in files if "endpoints.md" in str(f)]
    assert len(nested_files) == 1


def test_scan_returns_path_objects(temp_project):
    """Test that scan returns Path objects."""
    scanner = FileScanner(temp_project)
    files = scanner.scan()

    assert all(isinstance(f, Path) for f in files)


def test_scan_ignores_hidden_files(temp_project):
    """Test that hidden files (starting with .) are ignored by default."""
    (temp_project / ".hidden.md").write_text("# Hidden")
    (temp_project / "visible.md").write_text("# Visible")

    scanner = FileScanner(temp_project)
    files = scanner.scan()

    # Check for hidden files (files starting with . except .gitignore)
    hidden_files = [
        f for f in files if f.name.startswith(".") and f.suffix in FileScanner.SUPPORTED_EXTENSIONS
    ]
    visible_files = [f for f in files if f.name == "visible.md"]

    # Hidden markdown files should be excluded
    assert len(hidden_files) == 0
    # Visible file should be included
    assert len(visible_files) == 1
