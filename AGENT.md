# AI Agent Documentation: podfeedfilter

*Comprehensive guide for AI coding assistants (Claude, Cursor, Copilot, Cline, etc.)*

## Project Overview

**podfeedfilter** is a mature, production-ready Python CLI tool for podcast feed filtering and splitting. This document provides AI assistants with comprehensive context for effective code assistance.

### Key Characteristics
- **Language**: Python 3.10+ (requires modern type hint syntax)
- **Architecture**: Clean 3-layer architecture (CLI → Config → Core)
- **Quality**: 100% test coverage on core modules, 172 tests total
- **Dependencies**: 4 core dependencies, well-chosen and stable
- **Codebase Size**: ~300 lines core code, ~3,800 lines tests
- **Maturity**: Production-ready with comprehensive error handling

## Architecture Overview

### Module Structure
```
podfeedfilter/
├── __init__.py          # Package metadata (8 lines)
├── __main__.py          # CLI entry point (43 lines)  
├── config.py            # Configuration parsing (75 lines)
└── filterer.py          # Core processing logic (186 lines)
```

### Data Flow
```
YAML Config → FeedConfig objects → process_feed() → Filtered RSS outputs
```

### Key Classes
- `FeedConfig`: Dataclass for feed configuration
- Functions: `load_config()`, `process_feed()`, `_text_matches()`, `_entry_passes()`

## Core Features

1. **RSS Feed Filtering**: Download and filter podcast episodes by keywords
2. **Feed Splitting**: Single source → multiple filtered outputs  
3. **HTTP Optimization**: Conditional requests with Last-Modified caching
4. **Privacy Control**: iTunes block tags for public/private feeds
5. **Append-only Processing**: Preserves existing episodes, adds only new ones
6. **Robust Error Handling**: Graceful degradation for network/parsing failures

## Development Guidelines

### Code Quality Standards

**Required Practices:**
- **Type Hints**: Complete type annotations using Python 3.10+ syntax (`str | None`, not `Optional[str]`)
- **Docstrings**: Comprehensive documentation for all functions/classes
- **Test Coverage**: 100% coverage required for core modules (config.py, filterer.py)
- **Error Handling**: Specific exception catching with graceful fallbacks
- **Modern Python**: Use dataclasses, pathlib, modern syntax

**Code Style Example:**
```python
@dataclass
class FeedConfig:
    """Configuration for a single podcast feed filtering task."""
    url: str
    output: str
    include: List[str] = field(default_factory=list)
    private: bool = True

def process_feed(cfg: FeedConfig, no_check_modified: bool = False) -> None:
    """Process a single feed: download, filter, and generate output."""
    # Implementation with proper error handling
```

### Testing Requirements

**Test Categories:**
- **Unit Tests**: Test individual functions in isolation
- **Integration Tests**: End-to-end workflow testing
- **Edge Case Tests**: Error conditions, malformed data, performance
- **Mock Strategy**: External dependencies (HTTP, file system) properly mocked

**Test Structure (Arrange-Act-Assert):**
```python
def test_entry_passes_with_include_keywords(self):
    """Test that entries pass when matching include keywords."""
    # Arrange
    entry = {'title': 'Python Tutorial', 'description': 'Learn Python'}
    include = ['python']
    exclude = []
    
    # Act  
    result = _entry_passes(entry, include, exclude)
    
    # Assert
    assert result is True
```

**Testing Tools:**
- **pytest**: Primary testing framework
- **responses**: HTTP request mocking  
- **freezegun**: Time-based testing
- **Coverage**: HTML and terminal reporting

### Configuration Format

**YAML Structure:**
```yaml
feeds:
  - url: "https://example.com/feed.rss"
    output: "filtered.xml"
    include: ["python", "programming"]
    exclude: ["advertisement"]  
    title: "Custom Title"
    private: true
    check_modified: true
    
    splits:
      - output: "split1.xml"
        include: ["beginner"]
        private: false
```

**Key Configuration Rules:**
- `url` and `output` are required fields
- `include`/`exclude` are optional keyword lists
- `private` defaults to `True`, supports bool() coercion
- `splits` inherit parent URL, override other settings
- `check_modified` enables HTTP conditional requests

## Dependencies and Environment

### Core Dependencies
```
feedparser>=6.0.0    # RSS parsing - industry standard
feedgen>=1.0.0       # RSS generation with podcast extensions  
PyYAML>=6.0.0        # YAML configuration parsing
requests>=2.31.0     # HTTP client with robust features
```

### Development Dependencies
```
pytest>=7.0.0        # Testing framework
pytest-cov>=4.0.0    # Coverage reporting
responses>=0.23.0    # HTTP mocking for tests
freezegun>=1.2.0     # Time manipulation for tests
pylint              # Code quality analysis
```

### Environment Requirements
- **Python 3.10+** (required for modern type hints)
- **Cross-platform**: Linux, macOS, Windows support
- **No external system dependencies**
- **Low resource usage**: < 100MB memory typical

## Common Development Tasks

### Running Tests
```bash
# Full test suite with coverage
pytest

# Specific test file
pytest tests/test_filterer.py

# With verbose output  
pytest -v

# Generate coverage report
pytest --cov-report=html
```

### Code Quality Checks
```bash
# Run pylint on all Python files
pylint $(git ls-files '*.py')

# Check specific module
pylint podfeedfilter/config.py
```

### Local Development
```bash
# Run with sample config
python -m podfeedfilter -c feeds.yaml

# Force refresh (bypass caching)
python -m podfeedfilter --no-check-modified

# Override privacy settings
python -m podfeedfilter --private false
```

## Error Handling Patterns

### Network Error Recovery
```python
try:
    content, timestamp = _conditional_fetch(url, since)
    if content is None:
        return  # 304 Not Modified, nothing to do
except (requests.RequestException, ValueError) as e:
    print(f"Warning: Conditional fetch failed: {e}")
    print("Falling back to regular fetch...")
    # Continue with fallback approach
```

### Graceful Degradation Philosophy
- Network failures don't crash the application
- Malformed data is processed with available information
- Missing configuration uses sensible defaults
- Clear error messages for user-facing issues

## Performance Considerations

### HTTP Optimization
- **Conditional Requests**: Uses `If-Modified-Since` headers
- **Smart Caching**: File timestamps reflect content changes
- **Timeout Handling**: 30-second request timeout
- **Fallback Strategy**: Degrade gracefully on cache failures

### Processing Efficiency  
- **Append-only Logic**: Process only new episodes
- **Early Exit**: Stop filtering on first exclude match
- **Memory Streaming**: Low memory footprint processing
- **No Unnecessary Copying**: Efficient data handling

### Performance Benchmarks (from tests)
- Large feeds (1,000 episodes): < 10 seconds
- Long keyword lists (10,000 keywords): < 30 seconds  
- Typical usage (50 episodes): < 2 seconds

## AI Assistant Context

### When Modifying Code

**Always Consider:**
1. **Maintain 100% test coverage** on modified core modules
2. **Add comprehensive tests** for new functionality  
3. **Update type hints** for all new functions/parameters
4. **Follow existing patterns** and architectural decisions
5. **Handle errors gracefully** with appropriate fallbacks
6. **Update docstrings** for modified functions

**Code Review Checklist:**
- [ ] Type hints complete and use modern syntax
- [ ] Tests cover new/modified functionality
- [ ] Error handling follows project patterns
- [ ] Docstrings updated/added
- [ ] Existing tests still pass
- [ ] Performance considerations addressed

### Common Modification Scenarios

**Adding New Filter Types:**
- Extend `_entry_passes()` function logic
- Add configuration validation in `config.py`
- Include comprehensive test coverage
- Update configuration documentation

**Adding New Output Formats:**
- Modify `process_feed()` to support new formats
- Maintain backwards compatibility
- Add format detection logic
- Test with various feed structures

**HTTP/Network Enhancements:**
- Preserve conditional request optimization
- Maintain fallback mechanisms
- Test network failure scenarios
- Consider caching implications

### Testing Strategy for Changes

**Required Test Types:**
1. **Unit Tests**: Test functions in isolation
2. **Integration Tests**: Test complete workflows
3. **Edge Cases**: Error conditions, boundary cases  
4. **Performance**: Verify no regressions with large datasets
5. **Mock Tests**: External dependencies properly mocked

**Test Data Strategy:**
- Use realistic RSS feed structures
- Test with various episode counts
- Include malformed/edge case data
- Test Unicode and special characters

## Architecture Decision Records

### HTTP Conditional Requests
**Decision**: Use If-Modified-Since headers for bandwidth optimization
**Rationale**: Reduces bandwidth usage and processing time
**Trade-offs**: Additional complexity, but significant performance benefit
**Implementation**: `_conditional_fetch()` with graceful fallback

### Append-Only Processing  
**Decision**: Preserve existing episodes, only add new ones
**Rationale**: Maintains user's existing feed structure and history
**Trade-offs**: More complex logic, but better user experience
**Implementation**: Episode ID tracking with set-based deduplication

### Privacy-First Defaults
**Decision**: Default `private=True` for all feeds
**Rationale**: Protect user privacy unless explicitly made public
**Trade-offs**: Extra step for public feeds, but safer default
**Implementation**: iTunes block tag generation in `process_feed()`

### Dataclass Configuration
**Decision**: Use dataclasses for configuration objects
**Rationale**: Type safety, clear structure, automatic methods
**Trade-offs**: Python 3.7+ requirement, but excellent developer experience
**Implementation**: `FeedConfig` dataclass with proper defaults

## Integration Examples

### Python API Usage
```python
from podfeedfilter.config import FeedConfig, load_config
from podfeedfilter.filterer import process_feed

# Direct configuration
config = FeedConfig(
    url="https://example.com/feed.rss",
    output="tech_episodes.xml", 
    include=["python", "programming"],
    private=False
)
process_feed(config)

# File-based configuration
feeds = load_config("feeds.yaml")
for feed in feeds:
    process_feed(feed)
```

### Command Line Usage
```bash
# Basic usage
python -m podfeedfilter -c feeds.yaml

# Advanced options
python -m podfeedfilter -c config.yaml --no-check-modified --private false
```

### Automation Integration
```bash
# Cron job
0 6 * * * cd /path/to/podfeedfilter && python -m podfeedfilter

# Docker
docker run --rm -v $(pwd):/app python:3.10 \
  sh -c "cd /app && pip install -r requirements.txt && python -m podfeedfilter"
```

## Debugging and Troubleshooting

### Common Issues
1. **Import Errors**: Check virtual environment activation
2. **Test Failures**: Run with `-v --tb=long` for details
3. **Coverage Issues**: Use `--cov-report=html` for visualization
4. **Network Issues**: Check `--no-check-modified` flag

### Debug Commands
```bash
# Verbose test output
pytest -v --tb=long tests/test_specific.py

# Debug specific functionality
python -c "from podfeedfilter.config import load_config; print(load_config('feeds.yaml'))"

# Coverage details
pytest --cov-report=term-missing --cov-report=html
```

## Future Enhancement Areas

### Short-term Opportunities
- Plugin architecture for custom filters
- JSON Schema validation for configurations
- Structured logging with configurable levels
- Performance monitoring and metrics

### Long-term Evolution  
- Web interface for non-technical users
- Real-time processing with webhooks
- Cloud-native deployment options
- Advanced analytics and usage statistics

This documentation provides comprehensive context for AI assistants working with **podfeedfilter**. The project maintains high standards for code quality, testing, and documentation while providing a robust, production-ready tool for podcast feed management.
