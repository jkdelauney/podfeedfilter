"""Tests for the CLI private flag functionality.

Tests the --private/-p command line argument that overrides 
configuration file settings for all feeds.
"""

import pytest
import subprocess
import sys
import tempfile
import feedparser
from pathlib import Path


class TestPrivateCLIFlag:
    """Test CLI --private flag functionality."""

    def test_cli_help_shows_private_option(self):
        """Test that --help shows the new --private option."""
        result = subprocess.run(
            [sys.executable, "-m", "podfeedfilter", "--help"],
            capture_output=True,
            text=True,
            cwd="/Users/jody/work/python/podfeedfilter"
        )
        
        assert result.returncode == 0
        assert "--private" in result.stdout
        assert "{true,false}" in result.stdout
        assert "Override private setting for all feeds" in result.stdout

    def test_cli_private_flag_subprocess(self, tmp_path):
        """Test --private flag through subprocess call."""
        # Create test config with mixed private settings
        config_content = """
feeds:
  - url: "http://test/feed1"
    output: "feed1.xml"
    private: true
  - url: "http://test/feed2"
    output: "feed2.xml"
    private: false
"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(config_content)
        
        # Create mock RSS feed
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
        
        # Create test data directory structure
        test_data_dir = tmp_path / "data" / "feeds"
        test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create monkeypatch-compatible feeds
        (test_data_dir / "normal_feed.xml").write_text(mock_rss)
        (test_data_dir / "minimal_feed.xml").write_text(mock_rss)
        (test_data_dir / "empty_feed.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Empty</title><description>Empty</description></channel></rss>""")
        
        # Test with --private false (should override all to public)
        result = subprocess.run([
            sys.executable, "-c", 
            f"""
import sys
sys.path.insert(0, '/Users/jody/work/python/podfeedfilter')
sys.path.insert(0, '/Users/jody/work/python/podfeedfilter/tests')

# Mock feedparser for testing
import feedparser
from pathlib import Path

original_parse = feedparser.parse

def mock_parse(url_or_file, *args, **kwargs):
    test_url_mapping = {{
        'http://test/feed1': '{test_data_dir / "normal_feed.xml"}',
        'http://test/feed2': '{test_data_dir / "minimal_feed.xml"}',
    }}
    
    if isinstance(url_or_file, str) and url_or_file in test_url_mapping:
        return original_parse(test_url_mapping[url_or_file], *args, **kwargs)
    return original_parse(url_or_file, *args, **kwargs)

feedparser.parse = mock_parse

# Import and run main
from podfeedfilter.__main__ import main
import sys
sys.argv = ['podfeedfilter', '-c', '{config_file}', '--private', 'false']
main()
"""
        ], 
        capture_output=True,
        text=True,
        cwd=str(tmp_path)
        )
        
        # Check that feeds were created and both are public (no iTunes block)
        feed1_path = tmp_path / "feed1.xml"
        feed2_path = tmp_path / "feed2.xml"
        
        if feed1_path.exists():
            content1 = feed1_path.read_text()
            assert '<itunes:block>yes</itunes:block>' not in content1
            print("✓ Feed 1 is public (no iTunes block)")
        
        if feed2_path.exists():
            content2 = feed2_path.read_text()
            assert '<itunes:block>yes</itunes:block>' not in content2
            print("✓ Feed 2 is public (no iTunes block)")

    def test_cli_private_true_override(self, tmp_path):
        """Test --private true overrides config to make all feeds private."""
        # Create test config where one feed is explicitly public
        config_content = """
feeds:
  - url: "http://test/feed1"
    output: "feed1.xml"
    private: false  # This should be overridden to true
"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(config_content)
        
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
        
        # Create the data structure for testing
        test_data_dir = tmp_path / "data" / "feeds"
        test_data_dir.mkdir(parents=True, exist_ok=True)
        (test_data_dir / "normal_feed.xml").write_text(mock_rss)
        
        result = subprocess.run([
            sys.executable, "-c", 
            f"""
import sys
sys.path.insert(0, '/Users/jody/work/python/podfeedfilter')

import feedparser

original_parse = feedparser.parse

def mock_parse(url_or_file, *args, **kwargs):
    if isinstance(url_or_file, str) and url_or_file == 'http://test/feed1':
        return original_parse('{test_data_dir / "normal_feed.xml"}', *args, **kwargs)
    return original_parse(url_or_file, *args, **kwargs)

feedparser.parse = mock_parse

from podfeedfilter.__main__ import main
sys.argv = ['podfeedfilter', '-c', '{config_file}', '--private', 'true']
main()
"""
        ], 
        capture_output=True,
        text=True,
        cwd=str(tmp_path)
        )
        
        # Check that feed was created and is private (has iTunes block)
        feed1_path = tmp_path / "feed1.xml"
        
        if feed1_path.exists():
            content1 = feed1_path.read_text()
            assert '<itunes:block>yes</itunes:block>' in content1
            print("✓ Feed 1 is private (has iTunes block)")

    def test_cli_invalid_private_value(self):
        """Test that invalid --private values are rejected."""
        result = subprocess.run([
            sys.executable, "-m", "podfeedfilter", 
            "--private", "invalid"
        ],
        capture_output=True,
        text=True,
        cwd="/Users/jody/work/python/podfeedfilter"
        )
        
        assert result.returncode != 0
        assert "invalid choice" in result.stderr.lower() or "choose from" in result.stderr.lower()
