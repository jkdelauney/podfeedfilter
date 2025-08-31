"""Tests for conditional fetching functionality using Last-Modified headers.

Tests verify:
- HTTP 304 Not Modified responses skip feed processing
- HTTP 200 responses with Last-Modified headers update feeds and timestamps
- CLI --no-check-modified flag disables conditional fetching
- Per-feed check_modified configuration option
- Error handling and fallback to regular fetching
"""
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch
import shutil

import pytest
import responses
from freezegun import freeze_time

from podfeedfilter.config import FeedConfig
from podfeedfilter.filterer import process_feed, _conditional_fetch


# Sample RSS feed content for testing
SAMPLE_RSS_CONTENT = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Podcast</title>
    <link>https://example.com/podcast</link>
    <description>A test podcast</description>

    <item>
      <title>Episode 1: Introduction</title>
      <link>https://example.com/ep1</link>
      <guid>ep1</guid>
      <description>The first episode</description>
      <pubDate>Mon, 01 Jan 2024 10:00:00 GMT</pubDate>
      <enclosure url="https://example.com/ep1.mp3" length="5000000" type="audio/mpeg"/>
    </item>
  </channel>
</rss>"""

UPDATED_RSS_CONTENT = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Podcast</title>
    <link>https://example.com/podcast</link>
    <description>A test podcast</description>

    <item>
      <title>Episode 2: Second Episode</title>
      <link>https://example.com/ep2</link>
      <guid>ep2</guid>
      <description>The second episode</description>
      <pubDate>Tue, 02 Jan 2024 10:00:00 GMT</pubDate>
      <enclosure url="https://example.com/ep2.mp3" length="6000000" type="audio/mpeg"/>
    </item>

    <item>
      <title>Episode 1: Introduction</title>
      <link>https://example.com/ep1</link>
      <guid>ep1</guid>
      <description>The first episode</description>
      <pubDate>Mon, 01 Jan 2024 10:00:00 GMT</pubDate>
      <enclosure url="https://example.com/ep1.mp3" length="5000000" type="audio/mpeg"/>
    </item>
  </channel>
</rss>"""


class TestConditionalFetch:
    """Test the _conditional_fetch helper function."""

    @responses.activate
    def test_conditional_fetch_304_not_modified(self):
        """Test that 304 Not Modified returns None."""
        url = "https://example.com/feed.rss"
        since = 1704110400.0  # Jan 1, 2024 12:00:00 GMT

        responses.add(
            responses.GET,
            url,
            status=304
        )

        content, last_modified = _conditional_fetch(url, since)

        assert content is None
        assert last_modified is None
        assert len(responses.calls) == 1
        assert "If-Modified-Since" in responses.calls[0].request.headers

    @responses.activate
    def test_conditional_fetch_200_with_last_modified(self):
        """Test successful fetch with Last-Modified header."""
        url = "https://example.com/feed.rss"
        since = 1704110400.0  # Jan 1, 2024 12:00:00 GMT
        last_modified_str = "Mon, 02 Jan 2024 12:00:00 GMT"

        responses.add(
            responses.GET,
            url,
            body=SAMPLE_RSS_CONTENT,
            headers={"Last-Modified": last_modified_str},
            status=200
        )

        content, last_modified = _conditional_fetch(url, since)

        assert content == SAMPLE_RSS_CONTENT
        assert last_modified == 1704196800.0  # Jan 2, 2024 12:00:00 GMT
        assert len(responses.calls) == 1

    @responses.activate
    def test_conditional_fetch_200_without_last_modified(self):
        """Test successful fetch without Last-Modified header."""
        url = "https://example.com/feed.rss"
        since = 1704110400.0

        responses.add(
            responses.GET,
            url,
            body=SAMPLE_RSS_CONTENT,
            status=200
        )

        content, last_modified = _conditional_fetch(url, since)

        assert content == SAMPLE_RSS_CONTENT
        assert last_modified is None

    @responses.activate
    def test_conditional_fetch_no_since_parameter(self):
        """Test fetch without If-Modified-Since header when since is None."""
        url = "https://example.com/feed.rss"

        responses.add(
            responses.GET,
            url,
            body=SAMPLE_RSS_CONTENT,
            status=200
        )

        content, last_modified = _conditional_fetch(url, None)

        assert content == SAMPLE_RSS_CONTENT
        assert "If-Modified-Since" not in responses.calls[0].request.headers

    @responses.activate
    def test_conditional_fetch_invalid_last_modified(self):
        """Test handling of invalid Last-Modified header."""
        url = "https://example.com/feed.rss"

        responses.add(
            responses.GET,
            url,
            body=SAMPLE_RSS_CONTENT,
            headers={"Last-Modified": "invalid-date-string"},
            status=200
        )

        content, last_modified = _conditional_fetch(url, None)

        assert content == SAMPLE_RSS_CONTENT
        assert last_modified is None  # Should be None due to parse error


class TestProcessFeedConditional:
    """Test process_feed with conditional fetching enabled/disabled."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.output_path = self.temp_dir / "test_feed.xml"
        self.url = "https://example.com/feed.rss"

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @responses.activate
    def test_process_feed_304_not_modified_early_return(self):
        """Test that 304 Not Modified causes early return without processing."""
        # Create an existing output file with a known timestamp
        self.output_path.write_text("<?xml version='1.0'?><rss><channel></channel></rss>")
        file_time = 1704110400.0  # Jan 1, 2024
        os.utime(self.output_path, (file_time, file_time))

        # Mock 304 Not Modified response
        responses.add(
            responses.GET,
            self.url,
            status=304
        )

        config = FeedConfig(
            url=self.url,
            output=str(self.output_path),
            check_modified=True
        )

        # Store original content to verify it's unchanged
        original_content = self.output_path.read_text()
        original_mtime = self.output_path.stat().st_mtime

        process_feed(config)

        # Verify no changes were made
        assert self.output_path.read_text() == original_content
        assert self.output_path.stat().st_mtime == original_mtime
        assert len(responses.calls) == 1

    @responses.activate
    @freeze_time("2024-01-02 15:00:00")
    def test_process_feed_200_with_new_content(self):
        """Test successful processing with new content and timestamp update."""
        # Create existing output file
        self.output_path.write_text("<?xml version='1.0'?><rss><channel></channel></rss>")
        file_time = 1704110400.0  # Jan 1, 2024
        os.utime(self.output_path, (file_time, file_time))

        last_modified_str = "Tue, 02 Jan 2024 12:00:00 GMT"
        last_modified_timestamp = 1704196800.0

        responses.add(
            responses.GET,
            self.url,
            body=UPDATED_RSS_CONTENT,
            headers={"Last-Modified": last_modified_str},
            status=200
        )

        config = FeedConfig(
            url=self.url,
            output=str(self.output_path),
            check_modified=True
        )

        process_feed(config)

        # Verify file was updated with new timestamp
        assert self.output_path.stat().st_mtime == last_modified_timestamp
        assert "Episode 2: Second Episode" in self.output_path.read_text()

    def test_process_feed_no_check_modified_config(self):
        """Test that check_modified=False disables conditional fetching."""
        # Create existing output file
        self.output_path.write_text("<?xml version='1.0'?><rss><channel></channel></rss>")

        config = FeedConfig(
            url=self.url,
            output=str(self.output_path),
            check_modified=False  # Disable conditional fetching
        )

        # Mock feedparser.parse since check_modified=False uses regular feedparser
        with patch('podfeedfilter.filterer.feedparser.parse') as mock_parse:
            # Create mock feed with some content
            mock_parse.return_value.feed = {
                'title': 'Test Podcast',
                'description': 'A test podcast',
                'link': 'https://example.com'
            }
            mock_parse.return_value.entries = [
                {
                    'id': 'ep1',
                    'title': 'Episode 1',
                    'link': 'https://example.com/ep1',
                    'description': 'First episode'
                }
            ]

            process_feed(config)

            # Verify feedparser.parse was called with the URL (not conditional fetch)
            mock_parse.assert_called_with(self.url)

    def test_process_feed_cli_no_check_modified_override(self):
        """Test that CLI --no-check-modified overrides config setting."""
        # Create existing output file
        self.output_path.write_text("<?xml version='1.0'?><rss><channel></channel></rss>")

        config = FeedConfig(
            url=self.url,
            output=str(self.output_path),
            check_modified=True  # Config enables it
        )

        # Mock feedparser.parse since CLI override disables conditional fetch
        with patch('podfeedfilter.filterer.feedparser.parse') as mock_parse:
            mock_parse.return_value.feed = {
                'title': 'Test Podcast',
                'description': 'A test podcast',
                'link': 'https://example.com'
            }
            mock_parse.return_value.entries = [
                {
                    'id': 'ep1',
                    'title': 'Episode 1',
                    'link': 'https://example.com/ep1',
                    'description': 'First episode'
                }
            ]

            # CLI flag disables conditional fetch
            process_feed(config, no_check_modified=True)

            # Verify feedparser.parse was called directly (not conditional fetch)
            mock_parse.assert_called_with(self.url)

    @responses.activate
    def test_process_feed_fallback_on_request_error(self):
        """Test fallback to regular feedparser when conditional fetch fails."""
        # Create existing output file
        self.output_path.write_text("<?xml version='1.0'?><rss><channel></channel></rss>")
        file_time = 1704110400.0
        os.utime(self.output_path, (file_time, file_time))

        # Mock request failure for conditional fetch
        responses.add(
            responses.GET,
            self.url,
            body="Server Error",
            status=500
        )

        config = FeedConfig(
            url=self.url,
            output=str(self.output_path),
            check_modified=True
        )

        # Mock feedparser.parse as fallback (using patch to avoid actual network call)
        with patch('podfeedfilter.filterer.feedparser.parse') as mock_parse:
            mock_parse.return_value.feed = {'title': 'Test', 'description': 'Test'}
            mock_parse.return_value.entries = []

            with patch('builtins.print') as mock_print:
                process_feed(config)

                # Verify warning was printed
                mock_print.assert_called()
                warning_call = mock_print.call_args_list[0]
                assert "Warning: Conditional fetch failed" in str(warning_call)

                # Verify fallback was used
                mock_parse.assert_called_with(self.url)

    @responses.activate
    def test_process_feed_without_existing_file(self):
        """Test initial fetch when no output file exists."""
        responses.add(
            responses.GET,
            self.url,
            body=SAMPLE_RSS_CONTENT,
            headers={"Last-Modified": "Mon, 01 Jan 2024 12:00:00 GMT"},
            status=200
        )

        config = FeedConfig(
            url=self.url,
            output=str(self.output_path),
            check_modified=True
        )

        process_feed(config)

        # Verify file was created and timestamped
        assert self.output_path.exists()
        assert self.output_path.stat().st_mtime == 1704110400.0  # Jan 1, 2024 12:00:00 GMT
        assert "Episode 1: Introduction" in self.output_path.read_text()

        # Verify no If-Modified-Since header was sent (no existing file)
        assert "If-Modified-Since" not in responses.calls[0].request.headers

    @responses.activate
    def test_process_feed_timestamp_preserved_when_no_new_episodes(self):
        """Test that timestamp is preserved when feed updates but no new episodes match filters."""
        # Create existing output file with existing episode
        existing_feed_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Podcast</title>
    <description>A test podcast</description>

    <item>
      <title>Episode 1: Tech Discussion</title>
      <link>https://example.com/ep1</link>
      <guid>ep1</guid>
      <description>A tech episode</description>
    </item>
  </channel>
</rss>'''
        self.output_path.write_text(existing_feed_xml)
        original_time = 1704110400.0  # Jan 1, 2024 12:00:00 GMT
        os.utime(self.output_path, (original_time, original_time))

        # Remote feed has a new episode, but it doesn't match our filter
        updated_feed_content = b'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Podcast</title>
    <link>https://example.com/podcast</link>
    <description>A test podcast</description>

    <item>
      <title>Episode 2: Sports Talk</title>
      <link>https://example.com/ep2</link>
      <guid>ep2</guid>
      <description>A sports episode</description>
    </item>

    <item>
      <title>Episode 1: Tech Discussion</title>
      <link>https://example.com/ep1</link>
      <guid>ep1</guid>
      <description>A tech episode</description>
    </item>
  </channel>
</rss>'''

        responses.add(
            responses.GET,
            self.url,
            body=updated_feed_content,
            headers={"Last-Modified": "Mon, 02 Jan 2024 12:00:00 GMT"},
            status=200
        )

        config = FeedConfig(
            url=self.url,
            output=str(self.output_path),
            include=["tech"],  # Only tech episodes - sports episode won't match
            check_modified=True
        )

        process_feed(config)

        # File should be updated (rewritten) but timestamp should NOT be set to Last-Modified
        # because no new episodes were actually added to this filtered feed
        assert self.output_path.exists()
        # Timestamp should NOT be the Last-Modified time since no new episodes were added
        last_modified_timestamp = 1704196800.0  # Jan 2, 2024 12:00:00 GMT
        assert self.output_path.stat().st_mtime != last_modified_timestamp
        # File was rewritten so timestamp changed from original, but not set to Last-Modified
        assert self.output_path.stat().st_mtime != original_time

        # Verify content is still the same (only tech episode)
        content = self.output_path.read_text()
        assert "Episode 1: Tech Discussion" in content
        assert "Episode 2: Sports Talk" not in content  # Filtered out

    @responses.activate
    def test_process_feed_conditional_with_filtering(self):
        """Test that conditional fetching works with content filtering."""
        # Create existing output file
        self.output_path.write_text("<?xml version='1.0'?><rss><channel></channel></rss>")
        file_time = 1704110400.0
        os.utime(self.output_path, (file_time, file_time))

        responses.add(
            responses.GET,
            self.url,
            body=UPDATED_RSS_CONTENT,
            headers={"Last-Modified": "Tue, 02 Jan 2024 12:00:00 GMT"},
            status=200
        )

        config = FeedConfig(
            url=self.url,
            output=str(self.output_path),
            include=["Second"],  # Only include episodes with "Second" in title
            check_modified=True
        )

        process_feed(config)

        # Verify filtering was applied and file was updated
        content = self.output_path.read_text()
        assert "Episode 2: Second Episode" in content
        assert "Episode 1: Introduction" not in content


class TestConfigurationLoading:
    """Test that check_modified configuration is properly loaded."""

    def test_check_modified_default_true(self):
        """Test that check_modified defaults to True."""
        config = FeedConfig(url="https://example.com", output="output.xml")
        assert config.check_modified is True

    def test_check_modified_explicit_false(self):
        """Test that check_modified can be set to False."""
        config = FeedConfig(
            url="https://example.com",
            output="output.xml",
            check_modified=False
        )
        assert config.check_modified is False
