import pytest
from pathlib import Path
from linkguard.scanner.url_extractor import URLExtractor


@pytest.fixture
def extractor():
    return URLExtractor()


def test_extract_markdown_links(extractor, tmp_path: Path):
    content = """# Sample

[GitHub](https://github.com) link.
[Google](https://google.com) link."""

    md_file = tmp_path / "test.md"
    md_file.write_text(content)

    urls = extractor.extract_from_file(md_file)

    assert len(urls) >= 2
    assert any("github.com" in url["url"] for url in urls)
    assert any("google.com" in url["url"] for url in urls)


def test_extract_markdown_autolinks(extractor, tmp_path: Path):
    content = """Visit <https://example.com> for info.
Or check <http://test.local/page>."""

    md_file = tmp_path / "test.md"
    md_file.write_text(content)

    urls = extractor.extract_from_file(md_file)

    assert len(urls) >= 2
    assert any("example.com" in url["url"] for url in urls)
    assert any("test.local" in url["url"] for url in urls)


def test_extract_markdown_no_links(extractor, tmp_path: Path):
    content = """# Just Text
No links here."""

    md_file = tmp_path / "test.md"
    md_file.write_text(content)

    urls = extractor.extract_from_file(md_file)

    assert len(urls) == 0


def test_extract_html_links(extractor, tmp_path: Path):
    content = '<a href="https://example.com">Link</a>'

    html_file = tmp_path / "test.html"
    html_file.write_text(content)

    urls = extractor.extract_from_file(html_file)

    assert len(urls) == 1
    assert "example.com" in urls[0]["url"]


def test_extract_img_src_from_html(tmp_path, extractor):
    html_file = tmp_path / "page.html"
    html_file.write_text('<img src="https://example.com/image.png" alt="test">')

    urls = extractor.extract_from_file(html_file)

    assert len(urls) == 1
    assert "image.png" in urls[0]["url"]


def test_extract_script_src_from_html(tmp_path, extractor):
    html_file = tmp_path / "page.html"
    html_file.write_text('<script src="https://cdn.example.com/bundle.js"></script>')

    urls = extractor.extract_from_file(html_file)

    assert len(urls) == 1
    assert "cdn.example.com" in urls[0]["url"]


def test_extract_json_urls(extractor, tmp_path: Path):
    content = '{"api": "https://api.example.com/v1"}'

    json_file = tmp_path / "test.json"
    json_file.write_text(content)

    urls = extractor.extract_from_file(json_file)

    assert len(urls) >= 1
    assert any("api.example.com" in url["url"] for url in urls)


def test_extract_nested_json_urls(tmp_path, extractor):
    json_file = tmp_path / "config.json"
    json_content = """{
    "api": {
        "base": "https://api.example.com",
        "endpoints": {
            "users": "https://api.example.com/users"
        }
    },
    "links": ["https://github.com", "https://gitlab.com"]
}"""
    json_file.write_text(json_content)

    urls = extractor.extract_from_file(json_file)

    assert len(urls) >= 3
    assert any("api.example.com" in url["url"] for url in urls)
    assert any("github.com" in url["url"] for url in urls)


def test_invalid_json_returns_empty(tmp_path, extractor):
    json_file = tmp_path / "bad.json"
    json_file.write_text("{invalid json")

    urls = extractor.extract_from_file(json_file)

    assert urls == []


def test_extract_from_js_file(tmp_path, extractor):
    js_file = tmp_path / "app.js"
    js_file.write_text(
        'const API = "https://api.example.com/v1";\nfetch("https://github.com/api");'
    )

    urls = extractor.extract_from_file(js_file)

    assert len(urls) >= 2
    assert any("api.example.com" in url["url"] for url in urls)
    assert any("github.com" in url["url"] for url in urls)


def test_extract_from_tsx_file(tmp_path, extractor):
    tsx_file = tmp_path / "Component.tsx"
    tsx_file.write_text('<a href="https://example.com">Link</a>')

    urls = extractor.extract_from_file(tsx_file)

    assert len(urls) >= 1
    assert any("example.com" in url["url"] for url in urls)


def test_deduplicate_urls(extractor, tmp_path: Path):
    content = "[Link1](https://example.com)\n[Link2](https://example.com)"

    md_file = tmp_path / "test.md"
    md_file.write_text(content)

    urls = extractor.extract_from_file(md_file)

    assert len(urls) == 2
    assert urls[0]["url"] == urls[1]["url"]
    assert urls[0]["line_number"] != urls[1]["line_number"]


def test_ignore_relative_urls(extractor, tmp_path: Path):
    content = "[Local](/docs/guide)\n[External](https://github.com)"

    md_file = tmp_path / "test.md"
    md_file.write_text(content)

    urls = extractor.extract_from_file(md_file)

    assert len(urls) >= 1
    assert any("github.com" in url["url"] for url in urls)


def test_unsupported_file_type_returns_empty(tmp_path, extractor):
    pdf_file = tmp_path / "document.pdf"
    pdf_file.write_text("Some content")

    urls = extractor.extract_from_file(pdf_file)

    assert urls == []


def test_line_numbers_are_accurate(tmp_path, extractor):
    md_file = tmp_path / "test.md"
    md_file.write_text(
        "# Title\n\n[Link1](https://example.com)\n\nSome text\n\n[Link2](https://github.com)"
    )

    urls = extractor.extract_from_file(md_file)

    link1 = next(u for u in urls if "example.com" in u["url"])
    link2 = next(u for u in urls if "github.com" in u["url"])

    assert link1["line_number"] == 3
    assert link2["line_number"] == 7
