"""
Unit tests for filterer helper functions.

Tests the _text_matches and _entry_passes functions with parametrized cases
verifying case-insensitive matching, include-only/exclude-only/combined rules,
and proper rejection when both include and exclude lists are present.

Test Coverage:
- Case-insensitive matching for both functions
- Include-only filtering rules
- Exclude-only filtering rules
- Combined include/exclude rules
- Proper rejection when both include and exclude lists are present
- Edge cases (empty lists, missing fields, whitespace handling)
- Content aggregation across title, description, and summary fields
- Unicode and special character handling
- Multiple keyword matching (any match should pass for includes)
"""
import pytest
import feedparser
from feedgen.feed import FeedGenerator
from podfeedfilter.filterer import _text_matches, _entry_passes, _copy_entry


## pylint: disable=C0121
class TestTextMatches:
    """Test cases for _text_matches function."""

    @pytest.mark.parametrize("text,keywords,expected", [
        # Case-insensitive matching
        ("Hello World", ["hello"], True),
        ("Hello World", ["HELLO"], True),
        ("Hello World", ["HeLLo"], True),
        ("HELLO WORLD", ["hello"], True),
        ("hello world", ["HELLO"], True),

        # Multiple keywords - any match should return True
        ("Python programming", ["python"], True),
        ("Python programming", ["java"], False),
        ("Python programming", ["python", "java"], True),
        ("Python programming", ["ruby", "java"], False),

        # Partial matching
        ("Introduction to Python", ["intro"], True),
        ("Introduction to Python", ["python"], True),
        ("Introduction to Python", ["javascript"], False),

        # Special characters and numbers
        ("Episode 123: Tech Talk", ["123"], True),
        ("Episode 123: Tech Talk", ["tech"], True),
        ("Episode 123: Tech Talk", ["456"], False),

        # Empty and edge cases
        ("", ["anything"], False),
        ("Something", [], False),
        ("", [], False),

        # Whitespace handling
        ("  spaced  content  ", ["spaced"], True),
        ("  spaced  content  ", ["CONTENT"], True),
        ("  spaced  content  ", ["missing"], False),

        # Unicode and special characters
        ("Café discussion", ["café"], True),
        ("Café discussion", ["CAFÉ"], True),
        ("Hello! How are you?", ["hello"], True),
        ("Hello! How are you?", ["how"], True),
        ("Hello! How are you?", ["goodbye"], False),
    ])
    def test_text_matches_cases(self, text, keywords, expected):
        """Test _text_matches with various text and keyword combinations."""
        assert _text_matches(text, keywords) == expected

    def test_text_matches_multiple_keywords(self):
        """Test _text_matches with multiple keywords - comprehensive cases."""
        text = "Python programming tutorial for beginners"

        # Any keyword matches
        assert _text_matches(text, ["python", "java"]) == True
        assert _text_matches(text, ["ruby", "programming"]) == True
        assert _text_matches(text, ["tutorial", "advanced"]) == True
        assert _text_matches(text, ["beginners", "experts"]) == True

        # No keywords match
        assert _text_matches(text, ["java", "ruby", "javascript"]) == False

        # Case insensitive with multiple keywords
        assert _text_matches(text, ["PYTHON", "JAVA"]) == True
        assert _text_matches(text, ["RUBY", "PROGRAMMING"]) == True

    def test_text_matches_edge_cases(self):
        """Test _text_matches edge cases."""
        # Empty keyword list
        assert _text_matches("any text", []) == False

        # Empty text
        assert _text_matches("", ["keyword"]) == False

        # Both empty
        assert _text_matches("", []) == False

        # Keywords with spaces
        assert _text_matches("machine learning tutorial", ["machine learning"]) == True
        assert _text_matches("machine learning tutorial", ["deep learning"]) == False


class TestEntryPasses:
    """Test cases for _entry_passes function."""

    @pytest.fixture
    def sample_entry(self):
        """Create a sample feedparser entry for testing."""
        return {
            'title': 'Python Programming Tips',
            'description': 'Learn advanced Python techniques',
            'summary': 'A comprehensive guide to Python programming',
        }

    @pytest.fixture
    def minimal_entry(self):
        """Create a minimal feedparser entry for testing."""
        return {
            'title': 'Tech Talk',
        }

    @pytest.fixture
    def empty_entry(self):
        """Create an empty feedparser entry for testing."""
        return {}

    def test_entry_passes_include_only(self, sample_entry):
        """Test _entry_passes with include-only rules."""
        # Include matches title
        assert _entry_passes(sample_entry, ["python"], []) == True

        # Include matches description
        assert _entry_passes(sample_entry, ["advanced"], []) == True

        # Include matches summary
        assert _entry_passes(sample_entry, ["comprehensive"], []) == True

        # Include doesn't match
        assert _entry_passes(sample_entry, ["java"], []) == False

        # Multiple includes - any match passes
        assert _entry_passes(sample_entry, ["python", "java"], []) == True
        assert _entry_passes(sample_entry, ["ruby", "javascript"], []) == False

    def test_entry_passes_exclude_only(self, sample_entry):
        """Test _entry_passes with exclude-only rules."""
        # Exclude matches title - should be rejected
        assert _entry_passes(sample_entry, [], ["python"]) == False

        # Exclude matches description - should be rejected
        assert _entry_passes(sample_entry, [], ["advanced"]) == False

        # Exclude matches summary - should be rejected
        assert _entry_passes(sample_entry, [], ["comprehensive"]) == False

        # Exclude doesn't match - should pass
        assert _entry_passes(sample_entry, [], ["java"]) == True

        # Multiple excludes - any match rejects
        assert _entry_passes(sample_entry, [], ["python", "java"]) == False
        assert _entry_passes(sample_entry, [], ["ruby", "javascript"]) == True

    def test_entry_passes_combined_rules(self, sample_entry):
        """Test _entry_passes with both include and exclude rules."""
        # Include matches, exclude doesn't match - should pass
        assert _entry_passes(sample_entry, ["python"], ["java"]) == True

        # Include matches, exclude also matches - should be rejected
        assert _entry_passes(sample_entry, ["python"], ["programming"]) == False

        # Include doesn't match, exclude doesn't match - should be rejected
        assert _entry_passes(sample_entry, ["java"], ["ruby"]) == False

        # Include doesn't match, exclude matches - should be rejected
        assert _entry_passes(sample_entry, ["java"], ["python"]) == False

    def test_entry_passes_case_insensitive(self, sample_entry):
        """Test _entry_passes case-insensitive matching."""
        # Case insensitive include
        assert _entry_passes(sample_entry, ["PYTHON"], []) == True
        assert _entry_passes(sample_entry, ["python"], []) == True
        assert _entry_passes(sample_entry, ["PyThOn"], []) == True

        # Case insensitive exclude
        assert _entry_passes(sample_entry, [], ["PYTHON"]) == False
        assert _entry_passes(sample_entry, [], ["python"]) == False
        assert _entry_passes(sample_entry, [], ["PyThOn"]) == False

    @pytest.mark.parametrize("include,exclude,expected", [
        # Include-only cases
        (["python"], [], True),
        (["java"], [], False),
        (["python", "java"], [], True),
        (["ruby", "javascript"], [], False),

        # Exclude-only cases
        ([], ["python"], False),
        ([], ["java"], True),
        ([], ["python", "java"], False),
        ([], ["ruby", "javascript"], True),

        # Combined cases
        (["python"], ["java"], True),        # Include match, exclude no match
        (["python"], ["programming"], False), # Include match, exclude match
        (["java"], ["ruby"], False),         # Include no match, exclude no match
        (["java"], ["python"], False),       # Include no match, exclude match

        # Empty lists
        ([], [], True),  # No filters - should pass
    ])
    def test_entry_passes_parametrized(self, sample_entry, include, exclude, expected):
        """Test _entry_passes with parametrized include/exclude combinations."""
        assert _entry_passes(sample_entry, include, exclude) == expected

    def test_entry_passes_missing_fields(self, minimal_entry, empty_entry):
        """Test _entry_passes with entries missing some fields."""
        # Minimal entry (only title)
        assert _entry_passes(minimal_entry, ["tech"], []) == True
        assert _entry_passes(minimal_entry, ["python"], []) == False
        assert _entry_passes(minimal_entry, [], ["tech"]) == False
        assert _entry_passes(minimal_entry, [], ["python"]) == True

        # Empty entry (no fields)
        assert _entry_passes(empty_entry, ["anything"], []) == False
        assert _entry_passes(empty_entry, [], ["anything"]) == True
        assert _entry_passes(empty_entry, [], []) == True

def test_entry_passes_content_aggregation():
    """Test that _entry_passes properly aggregates title, description, and summary."""
    entry = {
        'title': 'Episode 1',
        'description': 'Python tutorial',
        'summary': 'JavaScript basics',
    }

    # Should find keywords in any of the fields
    assert _entry_passes(entry, ["episode"], []) == True     # from title
    assert _entry_passes(entry, ["python"], []) == True      # from description
    assert _entry_passes(entry, ["javascript"], []) == True  # from summary
    assert _entry_passes(entry, ["ruby"], []) == False       # in none

    # Exclude should work across all fields
    assert _entry_passes(entry, [], ["episode"]) == False    # from title
    assert _entry_passes(entry, [], ["python"]) == False     # from description
    assert _entry_passes(entry, [], ["javascript"]) == False # from summary
    assert _entry_passes(entry, [], ["ruby"]) == True        # in none


def test_copy_entry_with_invalid_enclosure_fields():
    """Test _copy_entry tolerates missing length/type in enclosures."""
    entry = feedparser.FeedParserDict({
        'id': 'entry1',
        'title': 'Test Entry',
        'enclosures': [{'href': 'http://example.com/audio.mp3'}]  # Missing length/type
    })

    fg = FeedGenerator()
    fg.load_extension('podcast')
    fg.title('Test Feed')
    fg.link(href='http://example.com')
    fg.description('Test feed description')

    fe = fg.add_entry()
    _copy_entry(fe, entry)

    # Verify entry was created without errors
    assert fe.title() == 'Test Entry'
    assert fe.id() == 'entry1'

    # Generate RSS to verify enclosures were handled
    rss_str = fg.rss_str(pretty=True)
    # The enclosure may not be included if required fields are missing
    # But the entry should still be created successfully
    assert b'Test Entry' in rss_str


class TestEntryWhitespaceHandling:
    """Test _entry_passes with whitespace in content."""

    def test_entry_passes_whitespace_handling(self):
        """Test _entry_passes with whitespace in content."""
        entry = {
            'title': '  Python   Programming  ',
            'description': '\t\nAdvanced techniques\n\t',
            'summary': 'Comprehensive  guide',
        }

        assert _entry_passes(entry, ["python"], []) == True
        assert _entry_passes(entry, ["programming"], []) == True
        assert _entry_passes(entry, ["advanced"], []) == True
        assert _entry_passes(entry, ["comprehensive"], []) == True

        assert _entry_passes(entry, [], ["python"]) == False
        assert _entry_passes(entry, [], ["programming"]) == False
        assert _entry_passes(entry, [], ["advanced"]) == False
        assert _entry_passes(entry, [], ["comprehensive"]) == False

    def test_entry_passes_empty_lists_combinations(self):
        """Test _entry_passes with various empty list combinations."""
        entry = {
            'title': 'Test Episode',
            'description': 'Test content',
        }

        # Both empty - should pass (no filtering)
        assert _entry_passes(entry, [], []) == True

        # Include empty, exclude has items - only exclude filtering
        assert _entry_passes(entry, [], ["test"]) == False
        assert _entry_passes(entry, [], ["nonexistent"]) == True

        # Include has items, exclude empty - only include filtering
        assert _entry_passes(entry, ["test"], []) == True
        assert _entry_passes(entry, ["nonexistent"], []) == False
## pylint: enable=C0321
