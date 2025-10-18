from linkguard.scanner.rules import EnvironmentRules, RuleViolation


def test_dev_mode_allows_localhost():
    """Dev mode should NOT flag localhost URLs."""
    rules = EnvironmentRules(mode="dev")

    violation = rules.check_url(
        url="http://localhost:3000/api", file_path="test.md", line_number=10
    )

    assert violation is None


def test_prod_mode_flags_localhost():
    """Prod mode should flag localhost URLs."""
    rules = EnvironmentRules(mode="prod")

    violation = rules.check_url(
        url="http://localhost:3000/api", file_path="test.md", line_number=10
    )

    assert violation is not None
    assert isinstance(violation, RuleViolation)
    assert violation.rule == "no-localhost-in-prod"
    assert violation.severity == "error"
    assert "localhost" in violation.url


def test_prod_mode_flags_127001():
    """Prod mode should flag 127.0.0.1 URLs."""
    rules = EnvironmentRules(mode="prod")

    violation = rules.check_url(
        url="http://127.0.0.1:8080/test", file_path="config.json", line_number=5
    )

    assert violation is not None
    assert "127.0.0.1" in violation.url


def test_prod_mode_flags_private_network():
    """Prod mode should flag private network URLs."""
    rules = EnvironmentRules(mode="prod")

    test_urls = [
        "http://192.168.1.1/admin",
        "http://10.0.0.5/api",
        "http://test.local/page",
    ]

    for url in test_urls:
        violation = rules.check_url(url, "test.md", 1)
        assert violation is not None, f"Failed to flag {url}"


def test_prod_mode_allows_public_urls():
    """Prod mode should NOT flag public URLs."""
    rules = EnvironmentRules(mode="prod")

    public_urls = [
        "https://github.com/user/repo",
        "https://www.google.com",
        "https://api.example.com/v1",
    ]

    for url in public_urls:
        violation = rules.check_url(url, "test.md", 1)
        assert violation is None, f"Incorrectly flagged {url}"


def test_check_multiple_urls():
    """Test checking multiple URLs at once."""
    rules = EnvironmentRules(mode="prod")

    urls_data = [
        ("test.md", {"url": "http://localhost:3000", "line_number": 1}),
        ("test.md", {"url": "https://github.com", "line_number": 2}),
        ("config.json", {"url": "http://127.0.0.1:8080", "line_number": 5}),
    ]

    violations = rules.check_urls(urls_data)

    assert len(violations) == 2  # Only localhost and 127.0.0.1 should be flagged
    assert all(isinstance(v, RuleViolation) for v in violations)


def test_violation_contains_file_path():
    """Test that violations include file path information."""
    rules = EnvironmentRules(mode="prod")

    violation = rules.check_url(
        url="http://localhost:5000", file_path="docs/api.md", line_number=42
    )

    assert violation is not None
    assert violation.file_path == "docs/api.md"
    assert violation.line_number == 42


def test_ipv6_localhost():
    """Test IPv6 localhost detection."""
    rules = EnvironmentRules(mode="prod")

    violation = rules.check_url(url="http://[::1]:8080/api", file_path="test.md", line_number=1)

    assert violation is not None
