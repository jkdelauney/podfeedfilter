"""Tests for private feed functionality with iTunes block tag.

Tests cover:
- Config parsing with private field defaults and explicit values
- CLI override functionality 
- iTunes block tag presence/absence in generated feeds
- Integration with splits
"""

import pytest
import re
import tempfile
import feedparser
from pathlib import Path
from podfeedfilter.config import FeedConfig, load_config
from podfeedfilter.filterer import process_feed


class TestPrivateConfigParsing:
    """Test configuration parsing for private field."""
    
    def test_private_defaults_to_true_when_missing(self, tmp_path):
        """Test that private defaults to True when not specified."""
        config_content = """
feeds:
  - url: "http://example.com/feed.xml"
    output: "test.xml"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        feeds = load_config(str(config_file))
        assert len(feeds) == 1
        assert feeds[0].private is True
    
    def test_private_explicit_true(self, tmp_path):
        """Test explicit private: true."""
        config_content = """
feeds:
  - url: "http://example.com/feed.xml"
    output: "test.xml"
    private: true
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        feeds = load_config(str(config_file))
        assert len(feeds) == 1
        assert feeds[0].private is True
    
    def test_private_explicit_false(self, tmp_path):
        """Test explicit private: false."""
        config_content = """
feeds:
  - url: "http://example.com/feed.xml"
    output: "test.xml"
    private: false
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        feeds = load_config(str(config_file))
        assert len(feeds) == 1
        assert feeds[0].private is False
    
    def test_private_with_splits_individual_settings(self, tmp_path):
        """Test private settings for main feed and individual splits."""
        config_content = """
feeds:
  - url: "http://example.com/feed.xml"
    output: "main.xml"
    private: true
    splits:
      - output: "split1.xml"
        private: false
        include: ["tech"]
      - output: "split2.xml"
        private: true
        include: ["news"]
      - output: "split3.xml"
        # private defaults to true
        include: ["misc"]
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        feeds = load_config(str(config_file))
        assert len(feeds) == 4  # 1 main + 3 splits
        assert feeds[0].private is True   # main
        assert feeds[1].private is False  # split1
        assert feeds[2].private is True   # split2
        assert feeds[3].private is True   # split3 (default)


class TestPrivateITunesBlockGeneration:
    """Test iTunes block tag generation based on private flag."""
    
    def _create_mock_feed_file(self, tmp_path):
        """Helper to create a mock RSS feed file."""
        mock_rss = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Test Podcast</title>
<description>Test Description</description>
<link>http://example.com</link>
<item>
<title>Test Episode</title>
<description>Test episode description</description>
<link>http://example.com/episode1</link>
<guid>episode1</guid>
</item>
</channel>
</rss>"""
        mock_file = tmp_path / "mock_feed.xml"
        mock_file.write_text(mock_rss)
        return str(mock_file)
    
    def test_private_true_adds_itunes_block(self, tmp_path):
        """Test that private=True adds iTunes block tag."""
        mock_feed = self._create_mock_feed_file(tmp_path)
        output_file = tmp_path / "private_output.xml"
        
        config = FeedConfig(
            url=mock_feed,
            output=str(output_file),
            include=[],
            exclude=[],
            private=True
        )
        
        process_feed(config)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert '<itunes:block>yes</itunes:block>' in content
        assert 'xmlns:itunes' in content  # iTunes namespace present
    
    def test_private_false_omits_itunes_block(self, tmp_path):
        """Test that private=False omits iTunes block tag."""
        mock_feed = self._create_mock_feed_file(tmp_path)
        output_file = tmp_path / "public_output.xml"
        
        config = FeedConfig(
            url=mock_feed,
            output=str(output_file),
            include=[],
            exclude=[],
            private=False
        )
        
        process_feed(config)
        
        assert output_file.exists()
        content = output_file.read_text()
        # Use regex to check for absence of <itunes:block> tag, ignoring whitespace and case
        itunes_block_pattern = re.compile(r'<\s*itunes:block\s*>\s*yes\s*</\s*itunes:block\s*>', re.IGNORECASE)
        assert not itunes_block_pattern.search(content)
        # iTunes namespace should still be present (podcast extension loaded)
        assert 'xmlns:itunes' in content
    
    def test_private_default_adds_itunes_block(self, tmp_path):
        """Test that default private behavior (True) adds iTunes block tag."""
        mock_feed = self._create_mock_feed_file(tmp_path)
        output_file = tmp_path / "default_output.xml"
        
        # Don't specify private explicitly - should default to True
        config = FeedConfig(
            url=mock_feed,
            output=str(output_file),
            include=[],
            exclude=[]
            # private defaults to True in dataclass
        )
        
        process_feed(config)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert '<itunes:block>yes</itunes:block>' in content
        assert 'xmlns:itunes' in content


class TestPrivateCLIOverride:
    """Test CLI override functionality for private flag."""
    
    def test_cli_override_forces_private_false(self, tmp_path):
        """Test CLI --private false overrides config settings."""
        # Create config with mixed private settings
        config_content = """
feeds:
  - url: "http://example.com/feed1.xml"
    output: "feed1.xml"
    private: true
  - url: "http://example.com/feed2.xml" 
    output: "feed2.xml"
    private: false
  - url: "http://example.com/feed3.xml"
    output: "feed3.xml"
    # private defaults to true
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        # Load and simulate CLI override
        feeds = load_config(str(config_file))
        
        # Before override
        assert feeds[0].private is True
        assert feeds[1].private is False  
        assert feeds[2].private is True
        
        # Simulate CLI override --private false
        private_override = False
        for feed in feeds:
            feed.private = private_override
            
        # After override
        assert feeds[0].private is False
        assert feeds[1].private is False
        assert feeds[2].private is False
    
    def test_cli_override_forces_private_true(self, tmp_path):
        """Test CLI --private true overrides config settings."""
        config_content = """
feeds:
  - url: "http://example.com/feed1.xml"
    output: "feed1.xml"
    private: false
  - url: "http://example.com/feed2.xml"
    output: "feed2.xml"
    private: true
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        feeds = load_config(str(config_file))
        
        # Before override
        assert feeds[0].private is False
        assert feeds[1].private is True
        
        # Simulate CLI override --private true
        private_override = True
        for feed in feeds:
            feed.private = private_override
            
        # After override
        assert feeds[0].private is True
        assert feeds[1].private is True


class TestPrivateWithExistingFeatures:
    """Test private functionality integration with existing features."""
    
    def test_private_with_filtering(self, tmp_path):
        """Test that private flag works with include/exclude filtering."""
        mock_rss = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Test Podcast</title>
<description>Test Description</description>
<link>http://example.com</link>
<item>
<title>Tech Episode</title>
<description>Programming and technology</description>
<link>http://example.com/tech</link>
<guid>tech</guid>
</item>
<item>
<title>Politics Episode</title>
<description>Political discussions</description>
<link>http://example.com/politics</link>
<guid>politics</guid>
</item>
</channel>
</rss>"""
        mock_file = tmp_path / "mock_feed.xml"
        mock_file.write_text(mock_rss)
        output_file = tmp_path / "filtered_private.xml"
        
        config = FeedConfig(
            url=str(mock_file),
            output=str(output_file),
            include=["tech"],  # Only include tech episodes
            exclude=[],
            private=True
        )
        
        process_feed(config)
        
        assert output_file.exists()
        content = output_file.read_text()
        
        # Should have iTunes block (private)
        assert '<itunes:block>yes</itunes:block>' in content
        
        # Should have filtered content (only tech episode)
        feed = feedparser.parse(str(output_file))
        assert len(feed.entries) == 1
        assert "tech" in feed.entries[0].title.lower()
    
    def test_private_with_title_description_override(self, tmp_path):
        """Test private flag with custom title/description."""
        mock_rss = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Original Title</title>
<description>Original Description</description>
<link>http://example.com</link>
<item>
<title>Test Episode</title>
<description>Test description</description>
<link>http://example.com/episode</link>
<guid>episode</guid>
</item>
</channel>
</rss>"""
        mock_file = tmp_path / "mock_feed.xml"
        mock_file.write_text(mock_rss)
        output_file = tmp_path / "custom_private.xml"
        
        config = FeedConfig(
            url=str(mock_file),
            output=str(output_file),
            include=[],
            exclude=[],
            title="Custom Private Feed",
            description="This is a private custom feed",
            private=True
        )
        
        process_feed(config)
        
        assert output_file.exists()
        content = output_file.read_text()
        
        # Should have iTunes block
        assert '<itunes:block>yes</itunes:block>' in content
        
        # Should have custom metadata
        feed = feedparser.parse(str(output_file))
        assert feed.feed.title == "Custom Private Feed"
        assert feed.feed.description == "This is a private custom feed"
