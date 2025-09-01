# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Robust Author Handling**: Comprehensive support for various RSS feed author formats
  - Support for simple author strings (backward compatible)
  - Support for `"email (name)"` format parsing
  - Support for dictionary/object author formats with flexible key mapping
  - Support for multiple authors via lists
  - Support for alternative author field names (`authors`, `dc_creator`, `creator`)
  - New `author_utils.py` module with extensive type hints and documentation
- **Enhanced Testing**: Comprehensive test suite for author handling with 100+ test cases
- **CI/CD Improvements**: New GitHub Actions workflow for automated testing across Python 3.10-3.13

### Changed
- **Author Processing**: Updated `_copy_entry()` function to handle all author format variations
- **Test Coverage**: Expanded pytest configuration to include author_utils module
- **Code Quality**: Added descriptive function and variable naming throughout author utilities

### Fixed
- **Issue #6**: RSS feeds with non-string author fields no longer cause errors
- **Data Integrity**: Author information is now correctly extracted regardless of source format
- **Edge Cases**: Malformed or missing author data is gracefully handled without breaking feed processing

### Technical Details
- Added `podfeedfilter.author_utils` module with public APIs:
  - `extract_authors(entry)` - Extract all authors from a feedparser entry
  - `get_primary_author(entry)` - Get the first/primary author (backward compatibility)
  - `format_author_for_display(author)` - Format author for human-readable output
- Maintains 100% backward compatibility with existing configurations
- No migration required for existing users
- Extensive error handling and logging for debugging

### Migration Guide
**No action required** - This change is fully backward compatible. Your existing feed configurations will continue to work exactly as before.

If you want to take advantage of enhanced author support:
- RSS feeds with multiple authors will now show all authors instead of just the first
- Feeds with structured author data (dictionaries) will be processed correctly
- Feeds using alternative field names like 'authors' instead of 'author' will work properly

## [Previous Versions]
See git commit history for changes prior to this changelog.
