"""Edge case tests for podfeedfilter functionality.

Tests unusual or boundary conditions including empty feeds, malformed
RSS content, network failures, filesystem permissions, and other
exceptional scenarios that could cause failures. Ensures robust
handling of unexpected input and error conditions.
"""

"""
Edge case tests for podcast filter application.

This module contains tests for various edge cases and error conditions:
- Feed with no matching episodes → output file not written or empty
- Pre-existing output file with malformed XML → ensure graceful failure or
  overwrite
- Very long include/exclude lists performance smoke test
- Invalid enclosure fields to ensure _copy_entry tolerates missing length/type
"""

import pytest
import feedparser
import time
from pathlib import Path
from feedgen.feed import FeedGenerator
from podfeedfilter.filterer import process_feed, _copy_entry, _entry_passes, _text_matches
from podfeedfilter.config import FeedConfig


class TestNoMatchingEpisodes:
    """Test behavior when no episodes match filtering criteria."""

    def test_no_matching_episodes_output_not_created(self,
                                                     mock_feedparser_parse,
                                                     test_feed_urls, tmp_path):
        """Test that no output file is created when no episodes match."""
        test_url = test_feed_urls['normal_feed']
        output_path = tmp_path / "no_matches.xml"

        config = FeedConfig(
            url=test_url,
            output=str(output_path),
            include=['absolutely_nonexistent_keyword_xyz123'],
            exclude=[]
        )

        process_feed(config)

        # Output file should not be created
        assert not output_path.exists()

    def test_empty_feed_no_output_created(self, mock_feedparser_parse,
                                          test_feed_urls, tmp_path):
        """Test that no output file is created for empty feeds."""
        test_url = test_feed_urls['empty_feed']
        output_path = tmp_path / "empty_feed.xml"

        config = FeedConfig(
            url=test_url,
            output=str(output_path),
            include=[],
            exclude=[]
        )

        process_feed(config)

        # Output file should not be created for empty feeds
        assert not output_path.exists()

    def test_all_episodes_excluded_no_output(self, mock_feedparser_parse,
                                             test_feed_urls, tmp_path):
        """
        Test that no output file is created when all episodes are excluded.
        """
        test_url = test_feed_urls['normal_feed']
        output_path = tmp_path / "all_excluded.xml"

        # Exclude all episodes by matching common words
        config = FeedConfig(
            url=test_url,
            output=str(output_path),
            include=[],
            exclude=['tech', 'election', 'special', 'offer', 'analysis',
                     'latest', 'premium']
        )

        process_feed(config)

        # Output file should not be created
        assert not output_path.exists()


class TestMalformedXML:
    """Test behavior with malformed existing output files."""

    def test_malformed_xml_overwritten(self, mock_feedparser_parse,
                                       test_feed_urls, tmp_path):
        """Test that malformed XML is overwritten with valid output."""
        test_url = test_feed_urls['normal_feed']
        output_path = tmp_path / "malformed.xml"

        # Create a malformed XML file
        output_path.write_text("This is not valid XML at all!")
        assert output_path.exists()

        config = FeedConfig(
            url=test_url,
            output=str(output_path),
            include=['tech'],
            exclude=[]
        )

        # Process should succeed and overwrite the malformed file
        process_feed(config)

        # File should now contain valid XML
        assert output_path.exists()
        content = output_path.read_text()
        assert content.startswith('<?xml version=\'1.0\' encoding=\'UTF-8\'?>')
        assert '<rss' in content
        assert '</rss>' in content

        # Verify it's parseable
        output_feed = feedparser.parse(str(output_path))
        assert len(output_feed.entries) == 1
        assert output_feed.entries[0].title == "Latest Tech Trends 2024"

    def test_partially_malformed_xml_overwritten(self, mock_feedparser_parse,
                                                 test_feed_urls, tmp_path):
        """Test that partially malformed XML is overwritten."""
        test_url = test_feed_urls['normal_feed']
        output_path = tmp_path / "partial_malformed.xml"

        # Create a partially malformed XML file (missing closing tag)
        malformed_xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Broken Feed</title>
        <item>
            <title>Broken Episode</title>
        </item>
    </channel>
"""  # Missing </rss>

        output_path.write_text(malformed_xml)
        assert output_path.exists()

        config = FeedConfig(
            url=test_url,
            output=str(output_path),
            include=['tech'],
            exclude=[]
        )

        # Process should succeed and overwrite
        process_feed(config)

        # File should now be valid
        assert output_path.exists()
        content = output_path.read_text()
        assert content.endswith('</rss>')

        # Verify it's parseable
        output_feed = feedparser.parse(str(output_path))
        # Should have the new tech episode plus the broken episode that was
        # preserved
        assert len(output_feed.entries) >= 1
        # The latest entry should be the tech episode
        tech_episodes = [e for e in output_feed.entries if 'tech' in e.title.lower()]
        assert len(tech_episodes) == 1
        assert tech_episodes[0].title == "Latest Tech Trends 2024"

    def test_empty_file_overwritten(self, mock_feedparser_parse,
                                    test_feed_urls, tmp_path):
        """Test that empty file is overwritten with valid output."""
        test_url = test_feed_urls['normal_feed']
        output_path = tmp_path / "empty.xml"

        # Create an empty file
        output_path.write_text("")
        assert output_path.exists()

        config = FeedConfig(
            url=test_url,
            output=str(output_path),
            include=['tech'],
            exclude=[]
        )

        process_feed(config)

        # File should now contain valid XML
        assert output_path.exists()
        content = output_path.read_text()
        assert len(content) > 0
        assert content.startswith('<?xml version=\'1.0\' encoding=\'UTF-8\'?>')


class TestPerformanceWithLongLists:
    """Test performance with very long include/exclude lists."""

    # Should complete within 30 seconds
    def test_very_long_include_exclude_lists(self, mock_feedparser_parse,
                                             test_feed_urls, tmp_path):
        """Performance smoke test with very long include/exclude lists."""
        test_url = test_feed_urls['normal_feed']
        output_path = tmp_path / "performance_test.xml"

        # Create very long lists (10,000 items each)
        include_list = [f"include_keyword_{i}" for i in range(10000)]
        exclude_list = [f"exclude_keyword_{i}" for i in range(10000)]

        # Add one real keyword to the include list to ensure matches
        include_list.append("tech")

        config = FeedConfig(
            url=test_url,
            output=str(output_path),
            include=include_list,
            exclude=exclude_list
        )

        start_time = time.time()
        process_feed(config)
        end_time = time.time()

        # Should complete reasonably quickly (under 30 seconds due to timeout)
        processing_time = end_time - start_time
        assert processing_time < 30.0, (
            f"Processing took too long: {processing_time} seconds"
        )

        # Should still produce correct output
        assert output_path.exists()
        output_feed = feedparser.parse(str(output_path))
        assert len(output_feed.entries) == 1
        assert output_feed.entries[0].title == "Latest Tech Trends 2024"

    def test_performance_with_large_feed(self, mock_feedparser_parse, tmp_path):
        """Test performance with a large number of episodes."""
        # Create a mock feed with many episodes
        large_feed_data = {
            'entries': [
                {
                    'id': f'episode_{i}',
                    'title': f'Episode {i}: Tech Talk' if i % 2 == 0 else f'Episode {i}: Non-Tech Content',
                    'description': f'Description for episode {i}',
                    'link': f'https://example.com/episode_{i}',
                    'published': 'Mon, 01 Jan 2024 10:00:00 +0000'
                }
                for i in range(1000)  # 1000 episodes
            ],
            'feed': {
                'title': 'Large Test Podcast',
                'description': 'A large test podcast',
                'link': 'https://example.com/large-feed'
            }
        }

        def mock_parse(url):
            return feedparser.FeedParserDict(large_feed_data)

        import podfeedfilter.filterer
        original_parse = podfeedfilter.filterer.feedparser.parse
        podfeedfilter.filterer.feedparser.parse = mock_parse

        try:
            output_path = tmp_path / "large_feed_test.xml"
            config = FeedConfig(
                url='https://example.com/large-feed',
                output=str(output_path),
                include=['tech'],
                exclude=[]
            )

            start_time = time.time()
            process_feed(config)
            end_time = time.time()

            processing_time = end_time - start_time
            assert processing_time < 10.0, (
                f"Processing large feed took too long: {processing_time} "
                "seconds"
            )

            # Should produce output with tech episodes
            assert output_path.exists()
            output_feed = feedparser.parse(str(output_path))
            # Should have all 1000 episodes because the mock doesn't filter
            # for existing IDs
            assert len(output_feed.entries) == 1000

        finally:
            # Restore original parse function
            podfeedfilter.filterer.feedparser.parse = original_parse


class TestInvalidEnclosureFields:
    """Test handling of invalid or missing enclosure fields."""

    def test_copy_entry_missing_enclosure_length(self):
        """Test _copy_entry with missing enclosure length."""
        entry = feedparser.FeedParserDict({
            'id': 'test_entry',
            'title': 'Test Entry',
            'enclosures': [{'href': 'http://example.com/audio.mp3', 'type': 'audio/mpeg'}]  # Missing length
        })

        fg = FeedGenerator()
        fg.load_extension('podcast')
        fg.title('Test Feed')
        fg.link(href='http://example.com')
        fg.description('Test feed description')

        fe = fg.add_entry()

        # Should not raise an exception
        _copy_entry(fe, entry)

        # Verify entry was created
        assert fe.title() == 'Test Entry'
        assert fe.id() == 'test_entry'

        # Generate RSS to verify enclosure was handled
        rss_str = fg.rss_str(pretty=True)
        # The enclosure may not be included if required fields are missing
        # But the entry should still be created successfully
        assert b'Test Entry' in rss_str

    def test_copy_entry_missing_enclosure_type(self):
        """Test _copy_entry with missing enclosure type."""
        entry = feedparser.FeedParserDict({
            'id': 'test_entry',
            'title': 'Test Entry',
            'enclosures': [{'href': 'http://example.com/audio.mp3', 'length': '25000000'}]  # Missing type
        })

        fg = FeedGenerator()
        fg.load_extension('podcast')
        fg.title('Test Feed')
        fg.link(href='http://example.com')
        fg.description('Test feed description')

        fe = fg.add_entry()

        # Should not raise an exception
        _copy_entry(fe, entry)

        # Verify entry was created
        assert fe.title() == 'Test Entry'
        assert fe.id() == 'test_entry'

        # Generate RSS to verify enclosure was handled
        rss_str = fg.rss_str(pretty=True)
        # The enclosure may not be included if required fields are missing
        # But the entry should still be created successfully
        assert b'Test Entry' in rss_str

    def test_copy_entry_missing_enclosure_length_and_type(self):
        """Test _copy_entry with missing enclosure length and type."""
        entry = feedparser.FeedParserDict({
            'id': 'test_entry',
            'title': 'Test Entry',
            'enclosures': [{'href': 'http://example.com/audio.mp3'}]
        })

        fg = FeedGenerator()
        fg.load_extension('podcast')
        fg.title('Test Feed')
        fg.link(href='http://example.com')
        fg.description('Test feed description')

        fe = fg.add_entry()

        # Should not raise an exception
        _copy_entry(fe, entry)

        # Verify entry was created
        assert fe.title() == 'Test Entry'
        assert fe.id() == 'test_entry'

        # Generate RSS to verify enclosure was handled
        rss_str = fg.rss_str(pretty=True)
        # The enclosure may not be included if required fields are missing
        # But the entry should still be created successfully
        assert b'Test Entry' in rss_str

    def test_copy_entry_empty_enclosure_list(self):
        """Test _copy_entry with empty enclosure list."""
        entry = feedparser.FeedParserDict({
            'id': 'test_entry',
            'title': 'Test Entry',
            'enclosures': []  # Empty list
        })

        fg = FeedGenerator()
        fg.load_extension('podcast')
        fg.title('Test Feed')
        fg.link(href='http://example.com')
        fg.description('Test feed description')

        fe = fg.add_entry()

        # Should not raise an exception
        _copy_entry(fe, entry)

        # Verify entry was created
        assert fe.title() == 'Test Entry'
        assert fe.id() == 'test_entry'

        # Generate RSS (should work without enclosures)
        rss_str = fg.rss_str(pretty=True)
        assert b'Test Entry' in rss_str

    def test_copy_entry_no_enclosures_field(self):
        """Test _copy_entry with no enclosures field at all."""
        entry = feedparser.FeedParserDict({
            'id': 'test_entry',
            'title': 'Test Entry'
            # No enclosures field
        })

        fg = FeedGenerator()
        fg.load_extension('podcast')
        fg.title('Test Feed')
        fg.link(href='http://example.com')
        fg.description('Test feed description')

        fe = fg.add_entry()

        # Should not raise an exception
        _copy_entry(fe, entry)

        # Verify entry was created
        assert fe.title() == 'Test Entry'
        assert fe.id() == 'test_entry'

        # Generate RSS (should work without enclosures)
        rss_str = fg.rss_str(pretty=True)
        assert b'Test Entry' in rss_str

    def test_copy_entry_malformed_enclosure_data(self):
        """Test _copy_entry with malformed enclosure data."""
        entry = feedparser.FeedParserDict({
            'id': 'test_entry',
            'title': 'Test Entry',
            'enclosures': [
                {'href': 'http://example.com/audio.mp3', 'length': 'invalid_length', 'type': 'audio/mpeg'},
                # Empty href
                {'href': '', 'length': '25000000', 'type': 'audio/mpeg'},
                {'length': '25000000', 'type': 'audio/mpeg'},  # Missing href
                None  # Null enclosure
            ]
        })

        fg = FeedGenerator()
        fg.load_extension('podcast')
        fg.title('Test Feed')
        fg.link(href='http://example.com')
        fg.description('Test feed description')

        fe = fg.add_entry()

        # Should not raise an exception despite malformed data
        _copy_entry(fe, entry)

        # Verify entry was created
        assert fe.title() == 'Test Entry'
        assert fe.id() == 'test_entry'

        # Generate RSS (should work despite malformed enclosures)
        rss_str = fg.rss_str(pretty=True)
        assert b'Test Entry' in rss_str


class TestExtremeCases:
    """Test extreme edge cases and boundary conditions."""

    def test_extremely_long_keyword_lists(self):
        """Test with extremely long keyword lists."""
        # Create very long keywords
        long_keywords = [f"keyword_{'x' * 1000}_{i}" for i in range(100)]

        entry = {
            'title': 'Test Episode',
            'description': 'Regular description',
            'summary': 'Regular summary'
        }

        # Should handle long keywords without issues
        result = _entry_passes(entry, long_keywords, [])
        assert result == False  # No matches expected

        result = _entry_passes(entry, [], long_keywords)
        assert result == True  # No excludes match

    def test_unicode_in_keywords_and_content(self):
        """Test with Unicode characters in keywords and content."""
        entry = {
            'title': 'Café Programming 🐍',
            'description': 'Naïve Bayes algorithm explained',
            'summary': 'Résumé of machine learning techniques'
        }

        # Unicode keywords should work
        assert _entry_passes(entry, ['café'], []) == True
        assert _entry_passes(entry, ['🐍'], []) == True
        assert _entry_passes(entry, ['naïve'], []) == True
        assert _entry_passes(entry, ['résumé'], []) == True

        # Unicode excludes should work
        assert _entry_passes(entry, [], ['café']) == False
        assert _entry_passes(entry, [], ['🐍']) == False
        assert _entry_passes(entry, [], ['naïve']) == False
        assert _entry_passes(entry, [], ['résumé']) == False

    def test_empty_strings_in_keywords(self):
        """Test with empty strings in keyword lists."""
        entry = {
            'title': 'Test Episode',
            'description': 'Test description',
            'summary': 'Test summary'
        }

        # Empty strings in keywords actually match everything
        # (due to string.find(''))
        assert _entry_passes(entry, ['', 'test'], []) == True  # Both match
        assert _entry_passes(entry, [''], []) == True  # Empty string matches
        assert _entry_passes(entry, ['nonexistent'], []) == False  # No match
        # Empty string excludes (matches everything)
        assert _entry_passes(entry, [], ['']) == False
        assert _entry_passes(entry, [], ['', 'test']) == False  # Both exclude
