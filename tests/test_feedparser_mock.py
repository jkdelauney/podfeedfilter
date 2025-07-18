"""
Test file demonstrating the usage of the mock_feedparser_parse fixture.

This test file shows how to use the mock_feedparser_parse fixture to test
feed processing functionality without making actual network requests.
"""
import pytest
import feedparser
from podfeedfilter.filterer import process_feed
from podfeedfilter.config import FeedConfig


def test_mock_feedparser_parse_basic(mock_feedparser_parse, test_feed_urls):
    """Test that the mock_feedparser_parse fixture works with basic feed parsing."""
    # Use one of the test URLs
    test_url = test_feed_urls['normal_feed']
    
    # Parse the feed - this should use the static XML file instead of network request
    parsed_feed = feedparser.parse(test_url)
    
    # Verify the feed was parsed correctly
    assert parsed_feed.feed.title == "Test Podcast"
    assert parsed_feed.feed.description == "A test podcast with various episode types"
    assert len(parsed_feed.entries) == 3
    
    # Verify the first entry
    first_entry = parsed_feed.entries[0]
    assert first_entry.title == "Latest Tech Trends 2024"
    assert "technology trends" in first_entry.description.lower()


def test_mock_feedparser_parse_minimal_feed(mock_feedparser_parse, test_feed_urls):
    """Test parsing a minimal feed using the mock fixture."""
    test_url = test_feed_urls['minimal_feed']
    
    parsed_feed = feedparser.parse(test_url)
    
    assert parsed_feed.feed.title == "Minimal Test Podcast"
    assert len(parsed_feed.entries) == 2
    
    # Verify entries
    assert parsed_feed.entries[0].title == "Episode One"
    assert parsed_feed.entries[1].title == "Episode Two"


def test_mock_feedparser_parse_empty_feed(mock_feedparser_parse, test_feed_urls):
    """Test parsing an empty feed using the mock fixture."""
    test_url = test_feed_urls['empty_feed']
    
    parsed_feed = feedparser.parse(test_url)
    
    # Empty feed should still have feed metadata but no entries
    assert parsed_feed.feed.title is not None
    assert len(parsed_feed.entries) == 0


def test_mock_feedparser_parse_nonexistent_mapping(mock_feedparser_parse):
    """Test that non-test URLs still work with the original feedparser."""
    # This should not be intercepted and will use the original feedparser
    # Since we can't make actual network requests in tests, we'll just verify
    # that the mock doesn't interfere with local file parsing
    test_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Direct XML Test</title>
    <description>Test parsing direct XML</description>
    <item>
      <title>Direct Item</title>
      <description>Direct description</description>
    </item>
  </channel>
</rss>'''
    
    parsed_feed = feedparser.parse(test_xml)
    assert parsed_feed.feed.title == "Direct XML Test"
    assert len(parsed_feed.entries) == 1
    assert parsed_feed.entries[0].title == "Direct Item"


def test_mock_feedparser_parse_with_process_feed(mock_feedparser_parse, test_feed_urls, tmp_path):
    """Test that the process_feed function works with the mocked feedparser."""
    # Create a test config that uses one of our test URLs
    test_url = test_feed_urls['normal_feed']
    output_path = tmp_path / "test_output.xml"
    
    # Create a FeedConfig object
    config = FeedConfig(
        url=test_url,
        output=str(output_path),
        include=['tech'],  # Should match "Latest Tech Trends 2024"
        exclude=['politics']  # Should exclude "Election Analysis"
    )
    
    # Process the feed - this will use our mocked feedparser
    process_feed(config)
    
    # Verify the output file was created
    assert output_path.exists()
    
    # Parse the output to verify filtering worked
    output_feed = feedparser.parse(str(output_path))
    assert len(output_feed.entries) >= 1
    
    # Should include the tech episode but not the politics one
    titles = [entry.title for entry in output_feed.entries]
    assert "Latest Tech Trends 2024" in titles
    assert "Election Analysis: What Voters Really Want" not in titles


def test_all_test_feed_urls(mock_feedparser_parse, test_feed_urls):
    """Test that all test feed URLs work correctly."""
    for feed_name, feed_url in test_feed_urls.items():
        parsed_feed = feedparser.parse(feed_url)
        
        # Each feed should have basic metadata
        assert parsed_feed.feed.title is not None
        assert hasattr(parsed_feed, 'entries')
        
        # Print some info for debugging (optional)
        print(f"Feed: {feed_name}")
        print(f"  Title: {parsed_feed.feed.title}")
        print(f"  Entries: {len(parsed_feed.entries)}")
        if parsed_feed.entries:
            print(f"  First entry: {parsed_feed.entries[0].title}")
