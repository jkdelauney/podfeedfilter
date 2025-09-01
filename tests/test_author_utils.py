"""Comprehensive tests for author_utils module.

Tests robust handling of various RSS feed author field formats including
strings, email formats, dictionaries, lists, and edge cases.
"""
import pytest
from unittest.mock import patch
from podfeedfilter.author_utils import (
    extract_authors,
    get_primary_author,
    format_author_for_display,
    _parse_email_author_format,
    _normalize_author_dict,
    _extract_single_author,
)


class TestParseEmailAuthorFormat:
    """Test parsing of email-based author strings."""

    @pytest.mark.parametrize("input_string,expected", [
        # Standard email (name) format
        ("john@example.com (John Doe)", {"name": "John Doe", "email": "john@example.com"}),
        ("editor@podcast.com (The Editor)", {"name": "The Editor", "email": "editor@podcast.com"}),
        
        # Email with extra spaces
        ("  test@email.com  ( Test User )  ", {"name": "Test User", "email": "test@email.com"}),
        
        # Just email addresses
        ("simple@example.com", {"email": "simple@example.com"}),
        ("user@domain.org", {"email": "user@domain.org"}),
        
        # Plain names (no email)
        ("Jane Smith", {"name": "Jane Smith"}),
        ("Dr. Robert Johnson", {"name": "Dr. Robert Johnson"}),
        ("  Spaced Name  ", {"name": "Spaced Name"}),
        
        # Complex names with punctuation
        ("Mary O'Connor", {"name": "Mary O'Connor"}),
        ("Jean-Claude Van Damme", {"name": "Jean-Claude Van Damme"}),
    ])
    def test_parse_email_author_format_valid_inputs(self, input_string, expected):
        """Test parsing of various valid author string formats."""
        result = _parse_email_author_format(input_string)
        assert result == expected

    def test_parse_email_author_format_edge_cases(self):
        """Test edge cases for email author format parsing."""
        # Empty strings should still return a name dict (will be filtered out upstream)
        result = _parse_email_author_format("")
        assert result == {"name": ""}
        
        result = _parse_email_author_format("   ")
        assert result == {"name": ""}


class TestNormalizeAuthorDict:
    """Test normalization of dictionary author objects."""

    def test_normalize_author_dict_standard_keys(self):
        """Test normalization with standard name/email keys."""
        author_dict = {"name": "John Doe", "email": "john@example.com"}
        result = _normalize_author_dict(author_dict)
        assert result == {"name": "John Doe", "email": "john@example.com"}

    def test_normalize_author_dict_alternative_keys(self):
        """Test normalization with alternative key names."""
        test_cases = [
            ({"title": "Jane Smith"}, {"name": "Jane Smith"}),
            ({"displayName": "Bob Wilson"}, {"name": "Bob Wilson"}),
            ({"full_name": "Alice Cooper"}, {"name": "Alice Cooper"}),
            ({"author_name": "Dr. Smith"}, {"name": "Dr. Smith"}),
            ({"email_address": "test@example.com"}, {"email": "test@example.com"}),
            ({"author_email": "author@site.com"}, {"email": "author@site.com"}),
            ({"mail": "user@domain.org"}, {"email": "user@domain.org"}),
        ]
        
        for input_dict, expected in test_cases:
            result = _normalize_author_dict(input_dict)
            assert result == expected

    def test_normalize_author_dict_priority_order(self):
        """Test that higher priority keys take precedence."""
        # 'name' should take priority over 'title'
        author_dict = {"name": "Primary Name", "title": "Secondary Title"}
        result = _normalize_author_dict(author_dict)
        assert result == {"name": "Primary Name"}
        
        # 'email' should take priority over 'email_address'
        author_dict = {"email": "primary@example.com", "email_address": "secondary@example.com"}
        result = _normalize_author_dict(author_dict)
        assert result == {"email": "primary@example.com"}

    def test_normalize_author_dict_invalid_inputs(self):
        """Test handling of invalid dictionary inputs."""
        invalid_inputs = [
            None,
            "not a dict",
            [],
            42,
            {},  # Empty dict
            {"irrelevant_key": "value"},  # No name or email keys
            {"name": "", "email": ""},  # Empty values
            {"name": None, "email": None},  # None values
        ]
        
        for invalid_input in invalid_inputs:
            result = _normalize_author_dict(invalid_input)
            assert result is None

    def test_normalize_author_dict_email_validation(self):
        """Test basic email validation in normalization."""
        # Valid email
        result = _normalize_author_dict({"email": "valid@example.com"})
        assert result == {"email": "valid@example.com"}
        
        # Invalid email (no @ symbol) should be filtered out
        result = _normalize_author_dict({"email": "not-an-email"})
        assert result is None


class TestExtractSingleAuthor:
    """Test extraction of author information from single values."""

    def test_extract_single_author_string_inputs(self):
        """Test extraction from string inputs."""
        test_cases = [
            ("John Doe", {"name": "John Doe"}),
            ("john@example.com (John Doe)", {"name": "John Doe", "email": "john@example.com"}),
            ("simple@example.com", {"email": "simple@example.com"}),
        ]
        
        for input_str, expected in test_cases:
            result = _extract_single_author(input_str)
            assert result == expected

    def test_extract_single_author_dict_inputs(self):
        """Test extraction from dictionary inputs."""
        test_cases = [
            ({"name": "Jane", "email": "jane@example.com"}, {"name": "Jane", "email": "jane@example.com"}),
            ({"title": "Dr. Smith"}, {"name": "Dr. Smith"}),
            ({"email": "test@example.com"}, {"email": "test@example.com"}),
        ]
        
        for input_dict, expected in test_cases:
            result = _extract_single_author(input_dict)
            assert result == expected

    def test_extract_single_author_other_types(self):
        """Test extraction from other data types."""
        # Numbers converted to strings
        result = _extract_single_author(42)
        assert result == {"name": "42"}
        
        # Boolean values are filtered out as non-useful
        result = _extract_single_author(True)
        assert result is None
        
        result = _extract_single_author(False)
        assert result is None

    def test_extract_single_author_invalid_inputs(self):
        """Test handling of invalid inputs."""
        invalid_inputs = [
            None,
            "",
            "   ",  # Whitespace only
            {},  # Empty dict
            [],  # Empty list (filtered out)
            True,  # Boolean (filtered out)
            False,  # Boolean (filtered out)
        ]
        
        for invalid_input in invalid_inputs:
            result = _extract_single_author(invalid_input)
            assert result is None

    @patch('podfeedfilter.author_utils.logger')
    def test_extract_single_author_conversion_error(self, mock_logger):
        """Test handling of string conversion errors."""
        # Create an object that raises an exception when converted to string
        class BadObject:
            def __str__(self):
                raise ValueError("Cannot convert to string")
        
        result = _extract_single_author(BadObject())
        assert result is None
        mock_logger.warning.assert_called_once()


class TestExtractAuthors:
    """Test extraction of authors from feedparser entries."""

    def test_extract_authors_simple_string(self):
        """Test extraction from simple author string."""
        entry = {"author": "John Doe"}
        result = extract_authors(entry)
        assert result == [{"name": "John Doe"}]

    def test_extract_authors_email_format(self):
        """Test extraction from email format string."""
        entry = {"author": "john@example.com (John Doe)"}
        result = extract_authors(entry)
        assert result == [{"name": "John Doe", "email": "john@example.com"}]

    def test_extract_authors_dict_format(self):
        """Test extraction from dictionary format."""
        entry = {"author": {"name": "Jane Smith", "email": "jane@example.com"}}
        result = extract_authors(entry)
        assert result == [{"name": "Jane Smith", "email": "jane@example.com"}]

    def test_extract_authors_list_format(self):
        """Test extraction from list of authors."""
        entry = {
            "authors": [
                "John Doe",
                "jane@example.com (Jane Smith)",
                {"name": "Bob Wilson", "email": "bob@example.com"}
            ]
        }
        result = extract_authors(entry)
        expected = [
            {"name": "John Doe"},
            {"name": "Jane Smith", "email": "jane@example.com"},
            {"name": "Bob Wilson", "email": "bob@example.com"}
        ]
        assert result == expected

    def test_extract_authors_alternative_field_names(self):
        """Test extraction from alternative author field names."""
        test_cases = [
            ({"authors": "Multiple Author"}, [{"name": "Multiple Author"}]),
            ({"dc_creator": "DC Creator"}, [{"name": "DC Creator"}]),
            ({"creator": "Generic Creator"}, [{"name": "Generic Creator"}]),
        ]
        
        for entry, expected in test_cases:
            result = extract_authors(entry)
            assert result == expected

    def test_extract_authors_field_priority(self):
        """Test that author fields are checked in priority order."""
        entry = {
            "author": "Primary Author",
            "authors": "Secondary Authors",
            "dc_creator": "DC Creator"
        }
        result = extract_authors(entry)
        # Should use 'author' field first
        assert result == [{"name": "Primary Author"}]

    def test_extract_authors_no_author_fields(self):
        """Test handling when no author fields are present."""
        entry = {"title": "Episode Title", "description": "Episode Description"}
        result = extract_authors(entry)
        assert result == []

    def test_extract_authors_empty_author_fields(self):
        """Test handling of empty author fields."""
        test_cases = [
            {"author": ""},
            {"author": None},
            {"authors": []},
            {"authors": ["", None]},
        ]
        
        for entry in test_cases:
            result = extract_authors(entry)
            assert result == []

    def test_extract_authors_mixed_valid_invalid(self):
        """Test handling of mixed valid and invalid authors in a list."""
        entry = {
            "authors": [
                "Valid Author",
                "",  # Empty string
                None,  # None value
                {"name": "Valid Dict Author"},
                {},  # Empty dict
                42  # Number (will be converted to string)
            ]
        }
        result = extract_authors(entry)
        expected = [
            {"name": "Valid Author"},
            {"name": "Valid Dict Author"},
            {"name": "42"}
        ]
        assert result == expected


class TestGetPrimaryAuthor:
    """Test getting primary (first) author from entries."""

    def test_get_primary_author_single(self):
        """Test getting primary author when there's only one."""
        entry = {"author": "Single Author"}
        result = get_primary_author(entry)
        assert result == {"name": "Single Author"}

    def test_get_primary_author_multiple(self):
        """Test getting primary author when there are multiple."""
        entry = {
            "authors": [
                "First Author",
                "Second Author",
                "Third Author"
            ]
        }
        result = get_primary_author(entry)
        assert result == {"name": "First Author"}

    def test_get_primary_author_none(self):
        """Test getting primary author when none exist."""
        entry = {"title": "No Author Episode"}
        result = get_primary_author(entry)
        assert result is None


class TestFormatAuthorForDisplay:
    """Test formatting authors for display purposes."""

    @pytest.mark.parametrize("author,expected", [
        ({"name": "John Doe", "email": "john@example.com"}, "John Doe <john@example.com>"),
        ({"name": "Jane Smith"}, "Jane Smith"),
        ({"email": "anonymous@example.com"}, "anonymous@example.com"),
        ({}, "Unknown Author"),
        ({"name": "", "email": ""}, "Unknown Author"),
    ])
    def test_format_author_for_display(self, author, expected):
        """Test various author formatting scenarios."""
        result = format_author_for_display(author)
        assert result == expected


class TestIntegrationWithFeedparser:
    """Integration tests simulating real feedparser entry structures."""

    def test_real_feedparser_entry_simple(self):
        """Test with a simple feedparser-style entry."""
        # Simulate feedparser.FeedParserDict structure
        entry = {
            "author": "podcast@example.com (Podcast Host)",
            "title": "Episode 1",
            "description": "First episode"
        }
        
        authors = extract_authors(entry)
        assert len(authors) == 1
        assert authors[0]["name"] == "Podcast Host"
        assert authors[0]["email"] == "podcast@example.com"

    def test_real_feedparser_entry_complex(self):
        """Test with a complex feedparser-style entry with multiple authors."""
        entry = {
            "authors": [
                {"name": "Host One", "email": "host1@example.com"},
                "guest@example.com (Special Guest)",
                "Co-host Name"
            ],
            "title": "Multi-author Episode",
            "description": "Episode with multiple contributors"
        }
        
        authors = extract_authors(entry)
        assert len(authors) == 3
        
        assert authors[0]["name"] == "Host One"
        assert authors[0]["email"] == "host1@example.com"
        
        assert authors[1]["name"] == "Special Guest"
        assert authors[1]["email"] == "guest@example.com"
        
        assert authors[2]["name"] == "Co-host Name"
        assert "email" not in authors[2]

    def test_backwards_compatibility(self):
        """Test that existing simple string authors still work."""
        # This simulates the original behavior that should still work
        entry = {"author": "Simple Author Name"}
        
        authors = extract_authors(entry)
        primary_author = get_primary_author(entry)
        
        assert len(authors) == 1
        assert authors[0] == {"name": "Simple Author Name"}
        assert primary_author == {"name": "Simple Author Name"}
        
        # Test that it formats correctly for feedgen
        formatted = format_author_for_display(primary_author)
        assert formatted == "Simple Author Name"

    def test_edge_case_malformed_data(self):
        """Test handling of various malformed author data."""
        malformed_entries = [
            {"author": {"weird_key": "weird_value"}},  # Dict with no recognized keys
            {"author": []},  # Empty list
            {"author": [None, "", {}]},  # List of invalid items
            {"authors": 42},  # Number instead of string/list
            {"author": {"name": None, "email": ""}},  # Dict with empty values
        ]
        
        for entry in malformed_entries:
            # Should not raise exceptions
            authors = extract_authors(entry)
            primary = get_primary_author(entry)
            
            # Results should be empty/None but not cause errors
            assert isinstance(authors, list)
            assert primary is None or isinstance(primary, dict)
