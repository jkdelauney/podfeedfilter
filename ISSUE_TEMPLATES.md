# GitHub Issue Templates

## Issue 1: Add Edge Case Tests for Episodes with Missing or Duplicate GUIDs

**Title:** `Add edge case tests for episodes with missing or duplicate GUIDs`

**Labels:** `testing`, `enhancement`, `sourcery-suggestion`

**Body:**
```markdown
## Issue Type
**Testing Enhancement**

## Description
Sourcery-AI suggested adding comprehensive edge case tests for episodes with missing, empty, or duplicate GUIDs to verify the filterer correctly excludes them.

## Current State
The filterer currently handles basic GUID processing, but we lack comprehensive tests for edge cases that could cause issues in production.

## Suggested Implementation
Add tests for the following edge cases:

### 1. Missing GUID
Episodes without a GUID field should be handled gracefully.

### 2. Empty GUID
Episodes with empty string GUID (`""`) should be excluded or handled appropriately.

### 3. Duplicate GUID
Multiple episodes with the same GUID should be handled (usually by excluding duplicates).

## Acceptance Criteria
- [ ] Add test for episodes with missing GUID field
- [ ] Add test for episodes with empty GUID (`""`)
- [ ] Add test for episodes with duplicate GUIDs
- [ ] Verify filterer correctly excludes episodes with invalid GUIDs
- [ ] Ensure proper assertions validate expected behavior
- [ ] Use existing `create_mock_rss()` helper function
- [ ] Add tests to `tests/test_private_functionality.py`

## Implementation Notes
```python
# Example test structure
def test_episodes_with_invalid_guids(self, tmp_path):
    # Test missing GUID
    episodes_missing_guid = [
        {'title': 'Episode 1', 'description': 'No GUID', 'link': 'http://example.com/1'},
        {'title': 'Episode 2', 'description': 'Has GUID', 'link': 'http://example.com/2', 'guid': 'ep2'}
    ]
    
    # Test empty GUID
    episodes_empty_guid = [
        {'title': 'Episode 3', 'description': 'Empty GUID', 'link': 'http://example.com/3', 'guid': ''},
        {'title': 'Episode 4', 'description': 'Valid GUID', 'link': 'http://example.com/4', 'guid': 'ep4'}
    ]
    
    # Test duplicate GUIDs
    episodes_duplicate_guid = [
        {'title': 'Episode 5', 'description': 'Duplicate GUID', 'link': 'http://example.com/5', 'guid': 'dup'},
        {'title': 'Episode 6', 'description': 'Also Duplicate GUID', 'link': 'http://example.com/6', 'guid': 'dup'},
        {'title': 'Episode 7', 'description': 'Unique GUID', 'link': 'http://example.com/7', 'guid': 'unique'}
    ]
    # Add assertions to verify expected behavior
```

## Priority
**Medium** - Improves test coverage and robustness

## Related Issues
- Part of improving overall test coverage
- Addresses Sourcery-AI suggestions for better edge case handling

## Origin
Sourcery-AI suggestion from PR review
```

---

## Issue 2: Add Test for Private Feeds with No Episodes

**Title:** `Add test for private feeds with no episodes`

**Labels:** `testing`, `enhancement`, `sourcery-suggestion`

**Body:**
```markdown
## Issue Type
**Testing Enhancement**

## Description
Add a test case to verify correct handling of private feeds that contain no episodes. This ensures our private flag functionality works correctly even when there are no episodes to process.

## Current State
We have tests for private feeds with episodes, but no coverage for the edge case of empty feeds.

## Acceptance Criteria
- [ ] Create test with empty episodes list (`[]`)
- [ ] Verify feed parsing works correctly for empty feeds
- [ ] Ensure private flag behavior is maintained
- [ ] Validate feed metadata (title, description) is preserved
- [ ] Confirm no errors occur when processing empty private feeds

## Implementation Notes
```python
def test_private_feed_no_episodes(self, tmp_path):
    """Test that private feeds with no episodes are handled correctly."""
    episodes = []  # Empty episodes list
    mock_rss = create_mock_rss(
        title="Private Feed", 
        description="No episodes", 
        episodes=episodes
    )
    mock_file = tmp_path / "private_feed_no_episodes.xml"
    mock_file.write_text(mock_rss)
    
    config = FeedConfig(
        url=str(mock_file),
        output=str(tmp_path / "output.xml"),
        include=[],
        exclude=[],
        private=True
    )
    
    # Process and verify
    process_feed(config)
    
    # Add assertions to verify:
    # - Feed parses without errors
    # - Private flag is respected
    # - Metadata is preserved
    # - Output file is created (or not, depending on expected behavior)
```

## Priority
**Low** - Nice to have for comprehensive coverage

## Related Issues
- Part of improving private flag test coverage
- Complements existing private flag functionality tests

## Origin
Sourcery-AI suggestion from PR review
```

---

## Cleanup Actions for Existing Issues

### Close These Issues:
- **Issue #19**: This is actually PR #19, not a separate issue
- **Issue #20**: This is actually PR #20, not a separate issue  
- **Issue #11**: Already addressed in recent changes (performance test assertion added)

### Update Labels for Existing Issues:
- **Issue #4**: Add labels `code-quality`, `sourcery-suggestion`, `refactoring`, `priority-low`
- **Issue #5**: Add labels `code-quality`, `performance`, `sourcery-suggestion`, `priority-low`
- **Issue #6**: Add labels `bug`, `robustness`, `sourcery-suggestion`, `priority-medium`
- **Issue #7**: Add labels `code-quality`, `sourcery-suggestion`, `refactoring`, `priority-low`
- **Issue #10**: Add labels `code-quality`, `sourcery-suggestion`, `refactoring`, `priority-low`

### Create These Labels (if they don't exist):
- `sourcery-suggestion`
- `code-quality`
- `testing`
- `enhancement`
- `refactoring`
- `robustness`
- `performance`
- `priority-high`
- `priority-medium`
- `priority-low`

### Create These Milestones:
- **Code Quality Improvements** - For grouping Sourcery suggestions
- **Test Coverage Enhancement** - For testing improvements
- **v1.1 Robustness** - For edge case and robustness fixes
