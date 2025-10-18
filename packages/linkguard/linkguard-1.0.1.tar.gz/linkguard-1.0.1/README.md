# 🛡️ LinkGuard

> **Fast, async link validation for developers. Catch broken links before your users do.**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.1-green.svg)](https://github.com/anubhabx/link-guard/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-91%20passing-brightgreen.svg)](tests/)
[![Test Coverage](https://img.shields.io/badge/coverage-71%25-yellow.svg)](htmlcov/index.html)
[![Status](https://img.shields.io/badge/status-production-success.svg)](RELEASE_NOTES.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

LinkGuard is a fast, async Python CLI tool that scans your project files for broken links and development URLs. Catch 404s before your users do, and ensure localhost references don't leak into production.

---

## ✨ Features

- 🚀 **Blazing Fast** - Async validation checks hundreds of links in seconds
- 🎯 **Environment-Aware** - Detect localhost/dev URLs that shouldn't reach production
- 🎨 **Beautiful CLI** - Rich progress bars and color-coded results
- 📊 **Multiple Exports** - JSON, CSV, and Markdown reports for automation
- 🔍 **Smart Extraction** - Supports Markdown, HTML, JSON, JS/TS, and plain text
- ⚙️ **Zero Config** - Works out of the box with sensible defaults
- 🛠️ **Configurable** - `.linkguardignore` and `linkguard.config.json` support
- ✅ **Production Ready** - 91 tests, 71% coverage, comprehensive documentation

---

## 📦 Installation

```bash
# Install from PyPI (coming soon)
pip install linkguard

# Or install from source
git clone https://github.com/anubhabx/link-guard.git
cd link-guard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

# Install in development mode (includes all dependencies)
pip install -e ".[dev]"
```

> **💡 Tip**: After installation with `pip install -e ".[dev]"`, you can use `linkguard` directly instead of `python -m linkguard.cli`

---

## 🚀 Quick Start

```bash
# Scan current directory
linkguard

# Scan specific directory
linkguard ./docs

# Production mode (flags localhost URLs as errors)
linkguard --mode prod

# Export results to JSON
linkguard --export report.json

# Custom timeout
linkguard --timeout 15
```

**Example Output:**

```
🔍 Scanning directory: ./docs
Mode: dev | Timeout: 10s

✓ Found 42 files to scan
✓ Extracted 156 URLs

🌐 Checking links...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 156/156

╭─ Scan Summary ─────────────╮
│ Files scanned       42     │
│ URLs found          156    │
│ Working links       152    │
│ Broken links        4      │
│ Rule violations     0      │
╰────────────────────────────╯
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| **[QUICKSTART.md](QUICKSTART.MD)** | Installation, basic usage, and common examples |
| **[FEATURES.md](FEATURES.MD)** | Complete feature list and capabilities |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Development setup, testing, and contribution guidelines |
| **[RELEASE_NOTES.md](RELEASE_NOTES.md)** | v1.0 release details and highlights |
| **[CHANGELOG.md](CHANGELOG.MD)** | Full version history and changes |

---

## ⚙️ Configuration

### Command-Line Options

```bash
linkguard [DIRECTORY] [OPTIONS]

Options:
  --mode, -m          dev|prod        Scanning mode (default: dev)
  --timeout, -t       INTEGER         Request timeout in seconds (default: 10)
  --export, -e        PATH            Export to JSON/CSV/Markdown
  --concurrency, -c   INTEGER         Max concurrent requests (default: 50)
  --ignore, -i        TEXT            Comma-separated ignore patterns
  --verbose, -v                       Detailed output
  --help                              Show help
```

### Configuration File

Create `linkguard.config.json` in your project root:

```json
{
  "mode": "prod",
  "timeout": 15,
  "concurrency": 100,
  "ignore_patterns": ["node_modules/**", "*.min.js"],
  "exclude_urls": ["https://example.local"],
  "strict_ssl": false
}
```

See [linkguard.config.json.example](linkguard.config.json.example) for all options.

### Ignore File

Create `.linkguardignore` (gitignore-style syntax):

```
# Ignore directories
node_modules/
dist/**
build/

# Ignore file patterns
*.draft.md
temp-*.json

# Ignore domains
*.internal.company.com
example.local
```

---

## 🏗️ Supported File Types

| Type | Extensions | What's Extracted |
|------|-----------|------------------|
| Markdown | `.md`, `.markdown` | `[text](url)` and bare URLs |
| HTML | `.html`, `.htm` | `href`, `src` attributes |
| JSON | `.json` | URL strings in values |
| JavaScript/TypeScript | `.js`, `.jsx`, `.ts`, `.tsx` | Bare URL patterns |
| Plain Text | `.txt` | HTTP/HTTPS URLs |

**Auto-excluded**: `.git`, `.venv`, `node_modules`, `__pycache__`, `dist`, `build`

---

## 🔧 CI/CD Integration

### GitHub Actions

```yaml
name: Link Validation

on: [push, pull_request]

jobs:
  check-links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install LinkGuard
        run: pip install linkguard
      - name: Check links
        run: linkguard --mode prod --export report.json
      - name: Upload report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: link-report
          path: report.json
```

**Exit Codes:**
- `0` - All links valid
- `1` - Broken links or rule violations found
- `2` - Configuration error

---

## 🎯 Use Cases

✅ **Documentation Sites** - Ensure all links work before publishing  
✅ **Open Source Projects** - Validate README and wiki links  
✅ **Marketing Sites** - Check landing pages and blog posts  
✅ **CI/CD Pipelines** - Automated link checking on every commit  
✅ **Pre-Production Checks** - Catch localhost URLs before deployment  
✅ **Content Migration** - Validate links after CMS migrations

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup and workflow
- Testing guidelines (91 tests, 71% coverage)
- Code style requirements (PEP 8, Black, type hints)
- Pull request process

**Quick Start:**

```bash
git clone https://github.com/anubhabx/link-guard.git
cd link-guard
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows
pip install -e ".[dev]"
pytest tests/ -v
```

---

## 🗺️ Roadmap

### ✅ v1.0 (Current - October 2025)
- Production-ready release
- Comprehensive documentation
- 91 passing tests with 71% coverage
- GitHub Actions CI/CD
- Published to PyPI

### 🚧 v1.1.0 (Planned)
- Retry logic with exponential backoff
- Custom HTTP headers support
- Relative URL resolution
- Enhanced performance optimizations

### 🔮 v2.0.0 (Future)
- Anchor link validation (`#section`)
- Browser automation (Playwright) for bot detection bypass
- Web dashboard for analytics
- Webhook notifications (Slack/Discord)

See [FEATURES.MD](FEATURES.MD) for complete roadmap.

---

## 📊 Performance

**Benchmarks** (typical projects):
- ✅ 100 links validated in ~2 seconds
- ✅ 1,000 links validated in ~5 seconds
- ✅ 10,000 files scanned in <30 seconds

**Architecture:**
- Async I/O with `aiohttp` for concurrent requests
- Semaphore-based concurrency control (default: 50)
- Memory-efficient streaming file reads
- HEAD request with smart GET fallback

---

## 🐛 Troubleshooting

**Valid links marked as broken?**
- Some servers block automated requests → Increase timeout: `--timeout 20`

**"Connection timeout" errors?**
- Network latency or slow servers → Try: `--timeout 30`

**Ignore specific files/URLs?**
- Use `.linkguardignore` or add to `linkguard.config.json`

**Command not found?**
- Ensure installed: `pip install -e ".[dev]"`
- Or use: `python -m linkguard.cli`

**SSL certificate errors?**
- LinkGuard skips SSL verification by default
- Coming soon: `--strict-ssl` flag

See [QUICKSTART.MD](QUICKSTART.MD) for more troubleshooting tips.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with these amazing tools:
- [aiohttp](https://docs.aiohttp.org/) - Async HTTP client
- [typer](https://typer.tiangolo.com/) - Modern CLI framework
- [rich](https://rich.readthedocs.io/) - Beautiful terminal formatting
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing

Special thanks to all [contributors](https://github.com/anubhabx/link-guard/graphs/contributors)! 🎉

---

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/anubhabx/link-guard/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/anubhabx/link-guard/discussions)
- 💡 **Feature Requests**: [Open an Issue](https://github.com/anubhabx/link-guard/issues/new)
- 📧 **Contact**: anubhabxdev@gmail.com

---

<div align="center">

**Made with ❤️ for the open-source community**

If you find LinkGuard useful, please give it a ⭐!

[Documentation](QUICKSTART.MD) • [Features](FEATURES.MD) • [Contributing](CONTRIBUTING.md) • [Changelog](CHANGELOG.MD)

</div>
