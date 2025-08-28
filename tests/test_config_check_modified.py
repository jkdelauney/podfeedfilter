"""Tests for check_modified configuration loading and inheritance.

Tests verify:
- Default behavior (check_modified=True when not specified)
- Explicit check_modified values in YAML
- Inheritance from parent to splits
- Override capability in individual splits
"""
from pathlib import Path
import tempfile
import yaml

import pytest

from podfeedfilter.config import load_config


class TestCheckModifiedConfig:
    """Test check_modified configuration loading from YAML."""

    def test_default_check_modified_true(self):
        """Test that check_modified defaults to True when not specified."""
        config_data = {
            "feeds": [
                {
                    "url": "https://example.com/feed.rss",
                    "output": "output.xml"
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            feeds = load_config(config_path)
            assert len(feeds) == 1
            assert feeds[0].check_modified is True
        finally:
            Path(config_path).unlink()

    def test_explicit_check_modified_false(self):
        """Test explicit check_modified: false in YAML."""
        config_data = {
            "feeds": [
                {
                    "url": "https://example.com/feed.rss",
                    "output": "output.xml",
                    "check_modified": False
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            feeds = load_config(config_path)
            assert len(feeds) == 1
            assert feeds[0].check_modified is False
        finally:
            Path(config_path).unlink()

    def test_explicit_check_modified_true(self):
        """Test explicit check_modified: true in YAML."""
        config_data = {
            "feeds": [
                {
                    "url": "https://example.com/feed.rss",
                    "output": "output.xml",
                    "check_modified": True
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            feeds = load_config(config_path)
            assert len(feeds) == 1
            assert feeds[0].check_modified is True
        finally:
            Path(config_path).unlink()

    def test_splits_inherit_parent_check_modified(self):
        """Test that splits inherit check_modified from parent feed."""
        config_data = {
            "feeds": [
                {
                    "url": "https://example.com/feed.rss",
                    "check_modified": False,  # Parent disables check_modified
                    "splits": [
                        {
                            "output": "split1.xml",
                            "include": ["tech"]
                        },
                        {
                            "output": "split2.xml",
                            "include": ["news"]
                        }
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            feeds = load_config(config_path)
            assert len(feeds) == 2  # Two splits
            assert feeds[0].check_modified is False  # Inherited from parent
            assert feeds[1].check_modified is False  # Inherited from parent
        finally:
            Path(config_path).unlink()

    def test_splits_inherit_parent_default(self):
        """Test that splits inherit default check_modified=True from parent."""
        config_data = {
            "feeds": [
                {
                    "url": "https://example.com/feed.rss",
                    # No check_modified specified (defaults to True)
                    "splits": [
                        {
                            "output": "split1.xml",
                            "include": ["tech"]
                        }
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            feeds = load_config(config_path)
            assert len(feeds) == 1
            assert feeds[0].check_modified is True  # Inherited default
        finally:
            Path(config_path).unlink()

    def test_split_overrides_parent_check_modified(self):
        """Test that individual splits can override parent check_modified."""
        config_data = {
            "feeds": [
                {
                    "url": "https://example.com/feed.rss",
                    "check_modified": True,  # Parent enables check_modified
                    "splits": [
                        {
                            "output": "split1.xml",
                            "include": ["tech"],
                            "check_modified": False  # Split overrides to disable
                        },
                        {
                            "output": "split2.xml",
                            "include": ["news"]
                            # No override, inherits True from parent
                        }
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            feeds = load_config(config_path)
            assert len(feeds) == 2
            assert feeds[0].check_modified is False  # Override
            assert feeds[1].check_modified is True   # Inherited
        finally:
            Path(config_path).unlink()

    def test_parent_and_splits_both_present(self):
        """Test configuration with both parent output and splits."""
        config_data = {
            "feeds": [
                {
                    "url": "https://example.com/feed.rss",
                    "output": "parent.xml",
                    "check_modified": False,  # Parent setting
                    "splits": [
                        {
                            "output": "split1.xml",
                            "include": ["tech"],
                            "check_modified": True  # Split override
                        }
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            feeds = load_config(config_path)
            assert len(feeds) == 2  # Parent + 1 split

            # Find parent and split by output filename
            parent_feed = next(f for f in feeds if f.output == "parent.xml")
            split_feed = next(f for f in feeds if f.output == "split1.xml")

            assert parent_feed.check_modified is False
            assert split_feed.check_modified is True  # Override
        finally:
            Path(config_path).unlink()

    def test_multiple_feeds_different_check_modified(self):
        """Test multiple feeds with different check_modified settings."""
        config_data = {
            "feeds": [
                {
                    "url": "https://feed1.com/rss",
                    "output": "feed1.xml",
                    "check_modified": True
                },
                {
                    "url": "https://feed2.com/rss",
                    "output": "feed2.xml",
                    "check_modified": False
                },
                {
                    "url": "https://feed3.com/rss",
                    "output": "feed3.xml"
                    # Default (True)
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name

        try:
            feeds = load_config(config_path)
            assert len(feeds) == 3

            feed1 = next(f for f in feeds if f.output == "feed1.xml")
            feed2 = next(f for f in feeds if f.output == "feed2.xml")
            feed3 = next(f for f in feeds if f.output == "feed3.xml")

            assert feed1.check_modified is True
            assert feed2.check_modified is False
            assert feed3.check_modified is True  # Default
        finally:
            Path(config_path).unlink()
