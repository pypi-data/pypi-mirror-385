# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Historical exchange rate queries
- Support for cryptocurrency conversion
- Command-line interface (CLI)
- Async API support
- Additional exchange rate providers

---

## [1.0.1] - 2025-10-21

### 🎉 Initial Release

#### Added
- Core currency conversion functionality
- Live exchange rate fetching via exchangerate-api.com
- Thread-safe caching mechanism with configurable TTL
- High-precision decimal arithmetic for accurate conversions
- Extensible provider system with base abstract class
- `CurrencyConverter` main class with the following methods:
  - `convert()` - Convert amounts between currencies
  - `get_rate()` - Get exchange rate between two currencies
  - `get_supported_currencies()` - List all supported currencies
  - `clear_cache()` - Clear cached exchange rates
- Custom exception hierarchy:
  - `FxConverterError` - Base exception
  - `InvalidCurrencyError` - Invalid currency code
  - `RateFetchError` - Rate fetching failures
  - `CacheError` - Cache operation errors
- Comprehensive test suite with pytest
- Full type hints support
- Documentation with examples
- PyPI package configuration
- MIT License

#### Features
- **Zero Configuration**: Works out of the box with sensible defaults
- **Smart Caching**: Automatic caching with 1-hour default TTL
- **Case Insensitive**: Currency codes work in any case (USD, usd, Usd)
- **Thread Safe**: Safe to use in multi-threaded applications
- **Precision Control**: Configurable decimal precision (default: 2 places)
- **Error Handling**: Clear, actionable error messages

#### Developer Experience
- Clean, modular architecture
- Follows PEP 8 style guidelines
- Comprehensive docstrings
- Easy to extend with custom providers
- Development dependencies included
- Pre-configured pytest, black, flake8, mypy

#### Performance
- Efficient caching reduces API calls
- Decimal arithmetic for precision without float errors
- Minimal dependencies (only requests)

#### Security
- No API keys required (uses free tier)
- Input validation for currency codes
- Safe error handling
- No sensitive data storage

---

## Release Guidelines

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Incompatible API changes
- **MINOR** (0.X.0): New features, backwards compatible
- **PATCH** (0.0.X): Bug fixes, backwards compatible

### Release Checklist

Before releasing a new version:

1. ✅ Update version in `src/fxconverter/__version__.py`
2. ✅ Update version in `pyproject.toml`
3. ✅ Update this CHANGELOG.md with release notes
4. ✅ Run full test suite: `pytest`
5. ✅ Check code quality: `black`, `flake8`, `mypy`
6. ✅ Build package: `python -m build`
7. ✅ Test package installation: `pip install dist/fxconverter-X.Y.Z.tar.gz`
8. ✅ Tag release: `git tag -a vX.Y.Z -m "Release X.Y.Z"`
9. ✅ Push tag: `git push origin vX.Y.Z`
10. ✅ Upload to PyPI: `twine upload dist/*`
11. ✅ Create GitHub release with notes

### Changelog Categories

Use these categories for organizing changes:

- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security improvements

### Example Future Entry

```markdown
## [1.1.0] - 2025-11-15

### Added
- Historical exchange rate queries with `get_historical_rate()`
- Support for 50+ cryptocurrency pairs
- Async methods: `convert_async()`, `get_rate_async()`

### Changed
- Improved caching algorithm for better memory efficiency
- Updated to exchangerate-api.com v7 API

### Fixed
- Fixed race condition in cache expiration check
- Corrected rounding behavior for JPY conversions

### Security
- Added rate limiting to prevent API abuse
- Improved input sanitization
```

---

## Links

- [PyPI Package](https://pypi.org/project/fxconverter/)
- [GitHub Repository](https://github.com/NtohnwiBih/fxconverter)
- [Issue Tracker](https://github.com/NtohnwiBih/fxconverter/issues)
- [Documentation](https://github.com/NtohnwiBih/fxconverter#readme)