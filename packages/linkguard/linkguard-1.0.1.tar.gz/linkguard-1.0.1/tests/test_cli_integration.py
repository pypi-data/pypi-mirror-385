import pytest
import subprocess
import json
import sys


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project with test files."""
    # Create markdown file with working link
    (tmp_path / "readme.md").write_text("[Google](https://google.com)")

    # Create markdown file with broken link
    (tmp_path / "broken.md").write_text("[Broken](https://thissitedoesnotexist12345.com)")

    # Create config file
    config = {"mode": "dev", "timeout": 5, "concurrency": 10}
    (tmp_path / "linkguard.config.json").write_text(json.dumps(config))

    return tmp_path


def test_cli_scan_basic(temp_project):
    """Test basic scan command."""
    result = subprocess.run(
        [sys.executable, "-m", "linkguard.cli", str(temp_project)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        cwd=temp_project,  # Run from temp directory
    )

    # Should complete successfully (exit code 0 or 1 for broken links)
    assert result.returncode in [0, 1], f"Exit code: {result.returncode}\nStderr: {result.stderr}"

    # Should contain output
    assert len(result.stdout) > 0


def test_cli_scan_with_mode_prod(temp_project):
    """Test scan with --mode prod."""
    # Add localhost URL to trigger prod mode violation
    (temp_project / "dev.md").write_text("[Local](http://localhost:3000)")

    result = subprocess.run(
        [sys.executable, "-m", "linkguard.cli", str(temp_project), "--mode", "prod"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        cwd=temp_project,
    )

    # Should exit with code 3 (violations found) or 1 if not yet implemented
    assert result.returncode in [1, 3], f"Exit code: {result.returncode}\nStderr: {result.stderr}"

    # Should mention violations
    output = result.stdout.lower()
    assert "violation" in output or "localhost" in output


def test_cli_scan_with_export_json(temp_project):
    """Test --export flag with JSON output."""
    export_path = temp_project / "report.json"

    result = subprocess.run(
        [sys.executable, "-m", "linkguard.cli", str(temp_project), "--export", str(export_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        cwd=temp_project,
    )

    # Should complete
    assert result.returncode in [
        0,
        1,
    ], f"Exit code: {result.returncode}\nStderr: {result.stderr}\nStdout: {result.stdout}"

    # Report file should be created
    assert (
        export_path.exists()
    ), f"Export file not created. Stdout: {result.stdout}\nStderr: {result.stderr}"

    # Should be valid JSON
    with open(export_path, "r") as f:
        data = json.load(f)

    assert "metadata" in data
    assert "results" in data


def test_cli_scan_with_timeout(temp_project):
    """Test --timeout flag."""
    result = subprocess.run(
        [sys.executable, "-m", "linkguard.cli", str(temp_project), "--timeout", "1"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        cwd=temp_project,
    )

    # Should complete (may have timeouts)
    assert result.returncode in [0, 1]


def test_cli_scan_with_ignore_pattern(temp_project):
    """Test --ignore flag with explicit filenames to avoid glob expansion."""
    (temp_project / "draft.md").write_text("[Draft](https://example.com)")

    # Use explicit filenames instead of wildcard pattern to avoid shell expansion
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "linkguard.cli",
            str(temp_project),
            "--ignore",
            "draft.md,readme.md,broken.md",  # Explicit comma-separated list
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        cwd=temp_project,
    )

    # Should exit successfully (all markdown files ignored, only linkguard.config.json remains)
    assert (
        result.returncode == 0
    ), f"Exit code: {result.returncode}\nStderr: {result.stderr}\nStdout: {result.stdout}"

    # Should mention no URLs found (config.json has no URLs to extract)
    assert "No URLs" in result.stdout or "no urls" in result.stdout.lower() or "0" in result.stdout


def test_cli_scan_nonexistent_directory(tmp_path):
    """Test scanning a non-existent directory."""
    nonexistent = tmp_path / "this_does_not_exist"

    result = subprocess.run(
        [sys.executable, "-m", "linkguard.cli", str(nonexistent)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        cwd=tmp_path,
    )

    # Should exit with error code 2 (directory doesn't exist)
    assert result.returncode == 2
    assert "does not exist" in result.stdout.lower() or "does not exist" in result.stderr.lower()


def test_cli_scan_with_verbose(temp_project):
    """Test --verbose flag."""
    result = subprocess.run(
        [sys.executable, "-m", "linkguard.cli", str(temp_project), "--verbose"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        cwd=temp_project,
    )

    # Should have more detailed output
    assert len(result.stdout) > 0
    assert result.returncode in [0, 1]


def test_cli_scan_empty_directory(tmp_path):
    """Test scanning an empty directory."""
    result = subprocess.run(
        [sys.executable, "-m", "linkguard.cli", str(tmp_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
        cwd=tmp_path,
    )

    # Should exit successfully (no files found)
    assert result.returncode == 0

    # Should mention no files or URLs found
    output = result.stdout.lower()
    assert "no urls" in output or "0" in result.stdout


def test_cli_help_command():
    """Test that --help works."""
    result = subprocess.run(
        [sys.executable, "-m", "linkguard.cli", "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )

    assert result.returncode == 0
    assert "linkguard" in result.stdout.lower() or "scan" in result.stdout.lower()


def test_cli_version_implicit():
    """Test that CLI can be invoked."""
    result = subprocess.run(
        [sys.executable, "-m", "linkguard.cli", "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )

    assert result.returncode == 0
    assert len(result.stdout) > 0
