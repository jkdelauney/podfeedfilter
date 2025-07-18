# AGENT.md - PodFeedFilter Project Documentation

## Project Overview

**PodFeedFilter** is a Python-based podcast feed filtering and processing tool that collects episodes from multiple podcast RSS feeds, filters them according to configurable keyword rules, and generates new RSS files. The tool is designed for automated operation via command line or cron jobs.

### Key Features
- **Multi-feed processing**: Handle multiple podcast feeds simultaneously
- **Keyword filtering**: Include/exclude episodes based on title and description content
- **Feed splitting**: Create multiple filtered outputs from a single source feed
- **Append-only operation**: Safely add new episodes without duplication
- **Metadata customization**: Override feed titles and descriptions
- **Cron-friendly**: Safe for automated scheduled execution

## Architecture

### Core Components

1. **Configuration System** (`config.py`)
   - YAML-based configuration parsing
   - Support for multiple feeds and split outputs
   - Dataclass-based configuration objects

2. **Feed Processing Engine** (`filterer.py`)
   - RSS feed parsing and processing
   - Episode filtering logic
   - RSS generation and file management
   - Duplicate detection and prevention

3. **CLI Interface** (`__main__.py`)
   - Command-line argument parsing
   - Configuration loading and feed processing orchestration

### Data Flow

```
YAML Config → FeedConfig Objects → RSS Parsing → Filter Logic → RSS Generation → File Output
```

## File Structure

```
podfeedfilter/
├── podfeedfilter/          # Main package
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # CLI entry point
│   ├── config.py           # Configuration management
│   └── filterer.py         # Core filtering logic
├── tests/                  # Test suite (8 test files, 127+ tests)
│   ├── conftest.py         # Pytest fixtures and monkeypatching
│   ├── data/               # Test data files
│   │   ├── configs/        # Test configuration files
│   │   └── feeds/          # Mock RSS feed files
│   ├── test_config_*.py    # Configuration tests
│   ├── test_filterer.py    # Filtering logic tests
│   ├── test_process_feed_integration.py  # Integration tests
│   ├── test_splits_integration.py        # Splits functionality tests
│   ├── test_cli.py         # CLI interface tests
│   └── test_edge_cases.py  # Edge case and error handling tests
├── feeds.yaml              # Sample configuration
├── requirements.txt        # Core dependencies
├── requirements-dev.txt    # Development dependencies
├── pytest.ini            # Test configuration with coverage
├── AGENT.md               # AI agent documentation
├── EDGE_CASE_TESTS.md     # Edge case testing documentation
└── README.md              # User documentation
```

## Key Classes and Functions

### `FeedConfig` (config.py)
```python
@dataclass
class FeedConfig:
    url: str                    # Source RSS feed URL
    output: str                 # Output file path
    include: List[str]          # Include keywords
    exclude: List[str]          # Exclude keywords
    title: str | None           # Custom feed title
    description: str | None     # Custom feed description
```

### `process_feed()` (filterer.py)
Core function that:
1. Loads existing output file (if exists)
2. Fetches and parses source RSS feed
3. Filters episodes based on include/exclude rules
4. Appends new episodes to existing ones
5. Generates updated RSS file

### Key Filtering Logic
- **Include Logic**: If include list provided, episode must contain at least one keyword
- **Exclude Logic**: Episode must not contain any exclude keywords
- **Case Insensitive**: All keyword matching is case-insensitive
- **Content Matching**: Searches in episode title, description, and summary fields

## Configuration Format

### Basic Configuration
```yaml
feeds:
  - url: "https://example.com/podcast.rss"
    output: "filtered_podcast.xml"
    include: ["tech", "programming"]
    exclude: ["politics", "ads"]
    title: "Tech Podcast Filtered"
    description: "Only tech episodes"
```

### Advanced Configuration with Splits
```yaml
feeds:
  - url: "https://example.com/podcast.rss"
    output: "main_filtered.xml"
    exclude: ["politics"]
    splits:
      - output: "tech_only.xml"
        title: "Tech Episodes Only"
        include: ["tech", "programming"]
      - output: "no_ads.xml"
        exclude: ["advertisement", "sponsored"]
```

## Testing Framework

### Test Structure
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end process_feed testing
- **Fixture-based**: Comprehensive test data and mocking

### Key Test Features
- **Monkeypatched Feeds**: Mock RSS feeds for testing without network I/O
- **Comprehensive Coverage**: 15+ integration tests covering all major scenarios
- **Append Testing**: Specific tests for episode appending behavior
- **Edge Cases**: Empty feeds, malformed data, missing files

### Test Data
- **Mock RSS Feeds**: Pre-built XML files with various episode types
- **Configuration Fixtures**: YAML files for testing different configurations
- **Temporary Files**: Safe temporary file handling for output testing

### Running Tests
```bash
# All tests
pytest

# Integration tests only
pytest tests/test_process_feed_integration.py

# With coverage
pytest --cov=podfeedfilter

# Specific test markers
pytest -m integration
pytest -m unit
```

## Usage Patterns

### Command Line Usage
```bash
# Basic usage
python -m podfeedfilter -c feeds.yaml

# Custom config file
python -m podfeedfilter -c /path/to/config.yaml

# Cron job friendly (no output unless errors)
python -m podfeedfilter -c feeds.yaml >/dev/null 2>&1
```

### Programmatic Usage
```python
from podfeedfilter.config import FeedConfig
from podfeedfilter.filterer import process_feed

config = FeedConfig(
    url="https://example.com/feed.rss",
    output="filtered.xml",
    include=["tech"],
    exclude=["ads"]
)

process_feed(config)
```

## Dependencies

### Core Dependencies
- **feedparser>=6.0.0**: RSS/XML feed parsing
- **feedgen>=1.0.0**: RSS feed generation with podcast extension
- **PyYAML>=6.0.0**: Configuration file parsing

### Development Dependencies
- **pytest>=7.0.0**: Testing framework
- **pytest-cov>=4.0.0**: Coverage reporting

### Python Version
- **Python 3.10+**: Required for modern type hint syntax (union operators, generics)

## Development Guidelines

### Code Style
- Python 3.10+ features (modern type hints with union syntax, dataclasses)
- Clear separation of concerns
- Comprehensive error handling
- Extensive test coverage (100% for core modules)

### Testing Principles
- Mock external dependencies (network calls)
- Test both success and failure cases
- Integration tests for end-to-end workflows
- Fixture-based test data management

### Key Design Decisions
1. **Append-only behavior**: Never overwrites existing episodes
2. **Duplicate prevention**: Uses episode ID/link for uniqueness
3. **Order preservation**: Maintains feed order with new episodes appended
4. **Safe file operations**: Creates directories as needed
5. **Flexible configuration**: Supports both simple and complex filtering rules

## Common Operations

### Adding New Episodes
The system automatically handles new episodes:
1. Existing episodes are preserved
2. New episodes are detected by ID/link
3. Only new episodes are appended
4. No duplication occurs

### Debugging
- Check output files exist and contain expected episodes
- Verify feed URLs are accessible
- Review include/exclude keyword matching
- Use integration tests to validate behavior

### Maintenance
- Output files can be safely deleted (will be recreated)
- Configuration changes take effect immediately
- Safe to run multiple times (idempotent)
- Suitable for automated scheduling

## Integration Points

### External Systems
- **RSS Feeds**: Standard RSS 2.0 and iTunes podcast formats
- **File System**: Local file storage for output feeds
- **Cron/Scheduling**: Designed for automated execution

### Monitoring
- Silent operation (no output unless errors)
- File-based state management
- Suitable for log monitoring and alerting

## Future Considerations

### Potential Enhancements
- Database backend for episode tracking
- Web interface for configuration management
- Advanced filtering rules (date ranges, duration)
- Notification system for new episodes
- Performance optimization for large feeds

### Scalability
- Current design handles moderate numbers of feeds
- File-based storage suitable for typical use cases
- Memory efficient processing (streaming where possible)
