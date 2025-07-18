#!/usr/bin/env python3
"""
Integration test for splits processing functionality.
This tests the step 10 requirements: splits producing 3 output files.

Test requirements:
1. Provide config with `splits` producing 3 output files
2. After processing, assert each file exists
3. Assert each contains correct subset per its include/exclude rules
4. Edge case: one split with only exclude list (no include patterns)
"""

import tempfile
import feedparser
from pathlib import Path
from podfeedfilter.config import FeedConfig
from podfeedfilter.filterer import process_feed


def test_splits_processing(mock_feedparser_parse):
    """Test processing with multiple splits producing separate outputs."""
    test_splits_config = {
        'splits': [
            {
                'name': "tech_episodes",
                'filter': {
                    'include_patterns': ['tech trends', 'technology'],
                    'exclude_patterns': ['advertisement']
                },
                'output_path': "tech_episodes.xml"
            },
            {
                'name': "politics_episodes",
                'filter': {
                    'include_patterns': ['election', 'voter'],
                    'exclude_patterns': ['tech']
                },
                'output_path': "politics_episodes.xml"
            },
            {
                'name': "non_ads",
                'filter': {
                    'exclude_patterns': ['advertisement', 'sponsored']
                },
                'output_path': "non_ads.xml"
            }
        ]
    }

    # Temporary output files
    output_paths = {}
    for split in test_splits_config['splits']:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            output_paths[split['name']] = Path(f.name)

    try:
        # Process each split
        for split in test_splits_config['splits']:
            config = FeedConfig(
                url='http://test/feed1',
                output=str(output_paths[split['name']]),
                include=split['filter'].get('include_patterns', []),
                exclude=split['filter'].get('exclude_patterns', []),
            )

            process_feed(config)

        # Check files created and contents
        for split_name, path in output_paths.items():
            assert path.exists(), f"Output file for {split_name} should exist"
            feed = feedparser.parse(str(path))
            print(f"\n{split_name} file has {len(feed.entries)} episodes:")
            for entry in feed.entries:
                print(f"  - {entry.title}")

            if split_name == "tech_episodes":
                # Should include tech episodes, exclude advertisements
                assert any('Tech Trends' in entry.title for entry in feed.entries), "Tech episodes file should include tech episodes"
                assert all('advertisement' not in entry.title.lower() and 'sponsored' not in entry.title.lower() for entry in feed.entries), "Tech episodes should exclude advertisements"
            elif split_name == "politics_episodes":
                # Should include politics episodes, exclude tech
                assert any('Election' in entry.title for entry in feed.entries), "Politics episodes file should include election episodes"
                assert all('tech' not in entry.title.lower() for entry in feed.entries), "Politics episodes should exclude tech"
            elif split_name == "non_ads":
                # Should exclude advertisements and sponsored content (edge case: only exclude list)
                assert all('advertisement' not in entry.title.lower() and 'sponsored' not in entry.title.lower() for entry in feed.entries), "Non-ads file should exclude advertisements and sponsored content"
                # Should include both tech and politics episodes
                assert len(feed.entries) >= 2, "Non-ads should include multiple episodes (tech and politics)"

        print("\n✅ SUCCESS: All split processing requirements met!")
        print("✓ 3 output files created successfully")
        print("✓ Each file contains correct subset per include/exclude rules")
        print("✓ Edge case handled: split with only exclude list (non_ads)")
        print("✓ Tech episodes split: includes tech content, excludes ads")
        print("✓ Politics episodes split: includes political content, excludes tech")
        print("✓ Non-ads split: excludes advertisements and sponsored content")

    finally:
        # Cleanup
        for path in output_paths.values():
            if path.exists():
                path.unlink()


if __name__ == "__main__":
    test_splits_processing()
