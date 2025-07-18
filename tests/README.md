# Tests Directory

This directory contains test files and test data for the podfeedfilter project.

## Structure

- `conftest.py` - Shared pytest fixtures and helper functions
- `data/` - Static test data files
- `pytest.ini` - pytest configuration (located in project root)

## Test Data Files

### RSS/XML Files
- `sample_feed.xml` - Basic RSS feed with 5 episodes for general testing
- `complex_feed.xml` - Complex RSS feed with iTunes tags, edge cases, and various episode formats

### YAML Configuration Files
- `sample_config.yaml` - Complete configuration example with multiple feeds and all filter options
- `minimal_config.yaml` - Minimal configuration for testing edge cases

## Available Fixtures

The `conftest.py` file provides several useful fixtures:

### File and Directory Fixtures
- `test_data_dir` - Path to the test data directory
- `temp_config_file` - Temporary YAML configuration file
- `temp_directory` - Temporary directory for test files

### Data Fixtures
- `sample_rss_feed` - Content of `sample_feed.xml`
- `sample_yaml_config` - Parsed content of `sample_config.yaml`
- `mock_feeds_config` - Mock configuration dictionary
- `mock_rss_item` - Mock RSS item dictionary

### Helper Functions
- `create_test_rss_feed(title, items)` - Generate RSS XML from title and items list
- `create_test_yaml_config(config_dict)` - Generate YAML configuration from dictionary

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test markers
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run tests with coverage
pytest --cov=podfeedfilter
```

## Test Markers

Available test markers (defined in `pytest.ini`):
- `unit` - Unit tests
- `integration` - Integration tests  
- `slow` - Slow tests (can be skipped)
- `network` - Tests requiring network access

## Notes

- Network-related warnings are silenced in pytest configuration
- All deprecation warnings are filtered out for cleaner test output
- Test discovery is configured to find `test_*.py` files in the tests directory
- The pytest configuration enforces strict marker usage to prevent typos
