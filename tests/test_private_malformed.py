"""Tests for malformed private value handling in configuration parsing.

Tests that the config parser properly handles and validates private field values
that are not valid boolean types or representations.
"""

from pathlib import Path  # noqa: F401

import pytest  # noqa: F401

from podfeedfilter.config import load_config


class TestPrivateMalformedValues:
    """Test malformed private value validation."""
    
    def test_private_empty_string_converts_to_false(self, tmp_path):
        """Test that private: "" converts to False (falsy value)."""
        config_content = """
feeds:
  - url: "http://example.com/feed.xml"
    output: "test.xml"
    private: ""
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        feeds = load_config(str(config_file))
        assert len(feeds) == 1
        assert feeds[0].private is False  # Empty string is falsy, bool("") == False
    
    def test_private_zero_converts_to_false(self, tmp_path):
        """Test that private: 0 converts to False."""
        config_content = """
feeds:
  - url: "http://example.com/feed.xml"
    output: "test.xml"
    private: 0
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        feeds = load_config(str(config_file))
        assert len(feeds) == 1
        assert feeds[0].private is False  # 0 is falsy, bool(0) == False
    
    def test_private_empty_list_converts_to_false(self, tmp_path):
        """Test that private: [] converts to False."""
        config_content = """
feeds:
  - url: "http://example.com/feed.xml"
    output: "test.xml"
    private: []
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        feeds = load_config(str(config_file))
        assert len(feeds) == 1
        assert feeds[0].private is False  # Empty list is falsy, bool([]) == False
    
    def test_private_non_empty_string_converts_to_true(self, tmp_path):
        """Test that private: "notabool" converts to True (truthy value)."""
        config_content = """
feeds:
  - url: "http://example.com/feed.xml"
    output: "test.xml"
    private: "notabool"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        feeds = load_config(str(config_file))
        assert len(feeds) == 1
        assert feeds[0].private is True  # Non-empty string is truthy, bool("notabool") == True
    
    def test_private_non_zero_number_converts_to_true(self, tmp_path):
        """Test that private: 42 converts to True."""
        config_content = """
feeds:
  - url: "http://example.com/feed.xml"
    output: "test.xml"
    private: 42
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        feeds = load_config(str(config_file))
        assert len(feeds) == 1
        assert feeds[0].private is True  # Non-zero number is truthy, bool(42) == True
    
    def test_private_non_empty_list_converts_to_true(self, tmp_path):
        """Test that private: [1, 2, 3] converts to True."""
        config_content = """
feeds:
  - url: "http://example.com/feed.xml"
    output: "test.xml"
    private: [1, 2, 3]
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        feeds = load_config(str(config_file))
        assert len(feeds) == 1
        assert feeds[0].private is True  # Non-empty list is truthy, bool([1, 2, 3]) == True
    
    def test_private_null_converts_to_false(self, tmp_path):
        """Test that private: null converts to False."""
        config_content = """
feeds:
  - url: "http://example.com/feed.xml"
    output: "test.xml"
    private: null
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        feeds = load_config(str(config_file))
        assert len(feeds) == 1
        assert feeds[0].private is False  # None/null is falsy, bool(None) == False

    def test_private_splits_malformed_values(self, tmp_path):
        """Test that splits also handle malformed private values correctly."""
        config_content = """
feeds:
  - url: "http://example.com/feed.xml"
    output: "main.xml"
    private: true
    splits:
      - output: "split1.xml"
        private: ""  # Empty string -> False
        include: ["tech"]
      - output: "split2.xml"
        private: "yes"  # Non-empty string -> True
        include: ["news"]
      - output: "split3.xml"
        private: 0  # Zero -> False
        include: ["misc"]
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        feeds = load_config(str(config_file))
        assert len(feeds) == 4  # 1 main + 3 splits
        assert feeds[0].private is True   # main: explicit true
        assert feeds[1].private is False  # split1: empty string
        assert feeds[2].private is True   # split2: non-empty string
        assert feeds[3].private is False  # split3: zero
