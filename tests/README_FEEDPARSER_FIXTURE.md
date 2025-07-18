# Feedparser Monkeypatch Fixture

This document describes how to use the `mock_feedparser_parse` fixture for testing feed processing functionality without making actual network requests.

## Overview

The `mock_feedparser_parse` fixture intercepts calls to `feedparser.parse(url)` and returns pre-parsed feed objects from static XML files when test URLs are used. This allows you to:

- Test feed processing logic without network I/O
- Use real RSS/podcast feed data from static files
- Exercise the actual feedparser parsing logic
- Create predictable, repeatable tests

## Usage

### Basic Usage

```python
def test_my_feed_processing(mock_feedparser_parse, test_feed_urls):
    """Test feed processing with mocked feedparser."""
    # Get a test URL that maps to a static XML file
    test_url = test_feed_urls['normal_feed']
    
    # This will use the static XML file instead of network request
    parsed_feed = feedparser.parse(test_url)
    
    # Now you can test against the known feed content
    assert parsed_feed.feed.title == "Test Podcast"
    assert len(parsed_feed.entries) == 3
```

### Available Test URLs

The fixture provides the following test URL mappings:

| Test URL | Static XML File | Description |
|----------|----------------|-------------|
| `http://test/feed1` | `normal_feed.xml` | A typical podcast feed with multiple episodes |
| `http://test/feed2` | `minimal_feed.xml` | A minimal feed with basic metadata |
| `http://test/feed3` | `empty_feed.xml` | An empty feed with no episodes |
| `http://test/feed4` | `malformed_feed.xml` | A feed with malformed XML |
| `http://test/feed5` | `future_episodes_feed.xml` | A feed with future-dated episodes |
| `http://test/complex` | `complex_feed.xml` | A complex feed with rich metadata |

### Using with `test_feed_urls` fixture

The `test_feed_urls` fixture provides a convenient mapping:

```python
def test_all_feeds(mock_feedparser_parse, test_feed_urls):
    """Test processing all available test feeds."""
    for feed_name, feed_url in test_feed_urls.items():
        parsed_feed = feedparser.parse(feed_url)
        
        # Each feed should have basic metadata
        assert parsed_feed.feed.title is not None
        assert hasattr(parsed_feed, 'entries')
```

### Testing with `process_feed` function

```python
def test_feed_filtering(mock_feedparser_parse, test_feed_urls, tmp_path):
    """Test the complete feed processing pipeline."""
    test_url = test_feed_urls['normal_feed']
    output_path = tmp_path / "filtered_feed.xml"
    
    # Create a config that uses the test URL
    config = FeedConfig(
        url=test_url,
        output=str(output_path),
        include=['tech'],  # Filter for tech episodes
        exclude=['politics']  # Exclude politics episodes
    )
    
    # Process the feed - uses mocked feedparser
    process_feed(config)
    
    # Verify the output
    assert output_path.exists()
    result_feed = feedparser.parse(str(output_path))
    
    # Test that filtering worked as expected
    titles = [entry.title for entry in result_feed.entries]
    assert "Latest Tech Trends 2024" in titles
    assert "Election Analysis: What Voters Really Want" not in titles
```

## How It Works

1. **Monkeypatch**: The fixture uses pytest's `monkeypatch` to replace `feedparser.parse`
2. **URL Mapping**: When `feedparser.parse(url)` is called with a test URL, it maps to a static XML file
3. **Static Files**: The XML files are stored in `tests/data/feeds/` directory
4. **Real Parsing**: The static files are parsed using the real feedparser logic
5. **Fallback**: Non-test URLs still use the original `feedparser.parse` function

## Benefits

- **No Network I/O**: Tests run faster and don't depend on external servers
- **Predictable**: Same test data every time, no changes in remote feeds
- **Real Parsing**: Still exercises the actual feedparser parsing logic
- **Flexible**: Easy to add new test feeds by adding XML files and URL mappings

## Adding New Test Feeds

To add a new test feed:

1. Create a new XML file in `tests/data/feeds/`
2. Add the URL mapping in the `mock_feedparser_parse` fixture
3. Optionally add it to the `test_feed_urls` fixture mapping

Example:
```python
# In mock_feedparser_parse fixture:
test_url_mapping = {
    'http://test/feed1': 'normal_feed.xml',
    'http://test/feed2': 'minimal_feed.xml',
    'http://test/mynewfeed': 'my_new_feed.xml',  # Add this
    # ... other mappings
}
```

## Limitations

- Only works with URLs that match the predefined test URL patterns
- Doesn't simulate network errors or timeouts
- Doesn't test HTTP headers, caching, or other network-specific behavior
- Static XML files must be manually maintained to reflect desired test scenarios
