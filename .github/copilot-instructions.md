# GitHub Copilot Instructions

This project uses **AGENT.md** for comprehensive AI assistant documentation. Please reference AGENT.md for:

- Project architecture and design decisions
- Development guidelines and code style
- Testing procedures and coverage requirements
- Dependencies and Python version requirements
- Configuration format and usage patterns

## Key Points

- **Python 3.10+** required (modern type hints with union syntax)
- **100% test coverage** for core modules (config.py, filterer.py)
- Use **pytest** with coverage reporting
- **Mock external dependencies** (feedparser network calls)
- **Append-only behavior** for RSS feeds
- Support for **feed splitting and filtering**

## Project Structure

- `podfeedfilter/` - main package with config.py, filterer.py, __main__.py
- `tests/` - comprehensive test suite (8 test files, 127+ tests)
- `requirements.txt` - core dependencies with version constraints
- `requirements-dev.txt` - development dependencies
- `pytest.ini` - test configuration with coverage settings

## Dependencies

- feedparser>=6.0.0 - RSS/XML feed parsing
- feedgen>=1.0.0 - RSS feed generation with podcast extension
- PyYAML>=6.0.0 - configuration file parsing
- pytest>=7.0.0 - testing framework
- pytest-cov>=4.0.0 - coverage reporting

**See AGENT.md for complete documentation.**
