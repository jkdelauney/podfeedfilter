#!/bin/bash

# Enhanced Issue Update Script for GitHub Repository
# Updates existing Sourcery issues with improved titles, descriptions, and labels
# Takes advantage of GitHub automation features for free users

REPO="jkdelauney/podfeedfilter"

# Check if GitHub token is available
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    echo "Please set your GitHub token: export GITHUB_TOKEN=your_token_here"
    echo "Token needs 'repo' scope to modify issues"
    exit 1
fi

echo "🚀 Updating issue metadata for $REPO..."

# Function to update issue with new title, body, and labels
update_issue() {
    local issue_number=$1
    local new_title="$2"
    local new_body="$3"
    shift 3
    local labels=("$@")
    
    # Convert labels array to JSON format
    local labels_json=$(printf '%s\n' "${labels[@]}" | jq -R . | jq -s .)
    
    # Escape quotes in title and body for JSON
    local escaped_title=$(echo "$new_title" | sed 's/"/\\"/g')
    local escaped_body=$(echo "$new_body" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')
    
    echo "📝 Updating Issue #$issue_number: $new_title"
    
    # Update issue title and body
    local update_response=$(curl -s -X PATCH \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/repos/$REPO/issues/$issue_number \
        -d "{\"title\":\"$escaped_title\",\"body\":\"$escaped_body\"}")
    
    # Add labels
    local label_response=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/repos/$REPO/issues/$issue_number/labels \
        -d "{\"labels\":$labels_json}")
    
    echo "✅ Updated issue #$issue_number with labels: ${labels[*]}"
}

# Issue #4: Named Expression and For-Append Improvements
update_issue 4 \
"Code Quality: Use Named Expressions and List Extend" \
"## 📋 Summary
Sourcery identified two code quality improvements that can make the codebase cleaner and more efficient.

## 🔍 Issues Found
- **Use named expression to simplify assignment** ([walrus operator](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/use-named-expression/))
- **Replace for-append loop with list extend** ([extend optimization](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/for-append-to-extend/))

## 📂 Affected Files
- [\`podfeedfilter/filterer.py\`](https://github.com/$REPO/blob/main/podfeedfilter/filterer.py) 
- Other modules (requires code search to identify exact locations)

## ✅ Task List
- [ ] Search codebase for assignment patterns that can use walrus operator (\`:=\`)
- [ ] Identify for-loop patterns that append to lists
- [ ] Refactor to use named expressions where appropriate
- [ ] Replace \`for item in items: list.append(item)\` with \`list.extend(items)\`
- [ ] Run tests to ensure functionality preserved
- [ ] Update any related documentation

## 🎯 Acceptance Criteria
- [ ] All walrus operator opportunities implemented
- [ ] All for-append loops converted to extend()
- [ ] Code passes existing test suite
- [ ] Performance improved (extend is faster than repeated append)

## 🔗 References
- [Python Walrus Operator Guide](https://realpython.com/python-walrus-operator/)
- [List extend() vs append() performance](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists)
- [Sourcery Rule Documentation](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/use-named-expression/)

## 📊 Impact
- **Code Readability**: ⬆️ Improved  
- **Performance**: ⬆️ Improved (extend over append)
- **Maintainability**: ⬆️ Enhanced

_Originally identified by [@sourcery-ai[bot]](https://github.com/sourcery-ai) in [PR #3](https://github.com/$REPO/pull/3#discussion_r2203551597)_" \
"code-quality" "sourcery-suggestion" "refactoring" "priority-low" "performance"

# Issue #5: Use any() Instead of For Loop
update_issue 5 \
"Performance: Replace For Loop with any() Builtin" \
"## 📋 Summary
Replace a manual for-loop with Python's built-in \`any()\` function for better performance and readability.

## 🔍 Issue Details
Current code uses a for-loop to check if any item in a sequence meets a condition. The \`any()\` builtin is more efficient and expressive for this pattern.

## 📂 Affected Files
- [\`podfeedfilter/filterer.py\`](https://github.com/$REPO/blob/main/podfeedfilter/filterer.py) - likely in \`_text_matches()\` or similar functions

## 🔍 Pattern to Find
\`\`\`python
# Current pattern (needs refactoring)
for item in items:
    if condition(item):
        return True
return False
\`\`\`

## ✅ Task List
- [ ] Locate the specific for-loop in the codebase
- [ ] Analyze the loop logic to ensure \`any()\` is appropriate
- [ ] Refactor to use \`any(condition(item) for item in items)\`
- [ ] Run performance benchmarks to confirm improvement
- [ ] Update tests if needed
- [ ] Verify edge cases (empty sequences, etc.)

## 🎯 Acceptance Criteria
- [ ] For-loop replaced with appropriate \`any()\` call
- [ ] Functionality remains identical
- [ ] Performance improved (benchmarked)
- [ ] Code is more readable and Pythonic

## 🔗 References
- [\`any()\` Documentation](https://docs.python.org/3/library/functions.html#any)
- [Sourcery Rule: use-any](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/use-any/)
- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)

## 📊 Expected Benefits
- **Performance**: ⬆️ Faster execution (C-level optimization)
- **Readability**: ⬆️ More concise and clear intent
- **Memory**: ⬆️ Generator expression reduces memory usage

_Originally identified by [@sourcery-ai[bot]](https://github.com/sourcery-ai) in [PR #3](https://github.com/$REPO/pull/3#discussion_r2203551597)_" \
"code-quality" "performance" "sourcery-suggestion" "priority-low" "python-builtin"

# Issue #6: Handle Author Field Edge Cases (HIGH PRIORITY)
update_issue 6 \
"🚨 Bug: Robust Author Field Handling in RSS Feeds" \
"## 📋 Summary
**CRITICAL**: The current implementation assumes the 'author' field is always a string, but RSS feeds can provide author information in various formats (dict, list, or different keys), causing potential crashes or data loss.

## 🔍 Problem Details
The code at [\`podfeedfilter/filterer.py:87\`](https://github.com/$REPO/blob/main/podfeedfilter/filterer.py#L87) assumes:
\`\`\`python
if \"author\" in entry:
    fe.author({\"name\": entry[\"author\"]})  # ⚠️ Assumes string
\`\`\`

## 🐛 Edge Cases That Break
1. **Dict Format**: \`{\"author\": {\"name\": \"John Doe\", \"email\": \"john@example.com\"}}\`
2. **List Format**: \`{\"author\": [{\"name\": \"John\"}, {\"name\": \"Jane\"}]}\`
3. **Authors Key**: \`{\"authors\": [\"John Doe\", \"Jane Smith\"]}\`
4. **Missing Author**: No author information available

## 📂 Affected Files
- [\`podfeedfilter/filterer.py\`](https://github.com/$REPO/blob/main/podfeedfilter/filterer.py#L74-L94) - \`_copy_entry()\` function

## ✅ Task List
- [ ] **URGENT**: Review RSS/Atom standards for author field formats
- [ ] Implement type checking for author field
- [ ] Handle string author format (current working case)
- [ ] Handle dict author format (extract name/email)
- [ ] Handle list author format (use first author)
- [ ] Handle 'authors' key as fallback
- [ ] Add comprehensive test cases for all formats
- [ ] Update error handling for malformed author data

## 🎯 Acceptance Criteria
- [ ] All author formats handled gracefully
- [ ] No crashes when encountering unexpected author formats
- [ ] Author information preserved in output feed when available
- [ ] Graceful degradation when author data is malformed
- [ ] Test coverage for all edge cases

## 💡 Suggested Implementation
\`\`\`python
def _extract_author(entry: feedparser.FeedParserDict) -> dict | None:
    \"\"\"Extract author information handling various RSS formats.\"\"\"
    # Handle various author formats: string, dict, list, or 'authors' key
    author_data = None
    if 'author' in entry:
        if isinstance(entry['author'], str):
            author_data = {'name': entry['author']}
        elif isinstance(entry['author'], dict):
            author_data = entry['author']
        elif isinstance(entry['author'], list) and entry['author']:
            # Use the first author in the list
            first_author = entry['author'][0]
            if isinstance(first_author, str):
                author_data = {'name': first_author}
            elif isinstance(first_author, dict):
                author_data = first_author
    elif 'authors' in entry and isinstance(entry['authors'], list) and entry['authors']:
        first_author = entry['authors'][0]
        if isinstance(first_author, str):
            author_data = {'name': first_author}
        elif isinstance(first_author, dict):
            author_data = first_author
    return author_data
\`\`\`

## 🔗 References
- [RSS 2.0 Specification](https://www.rss-board.org/rss-specification#ltauthorgt)
- [Atom Syndication Format](https://tools.ietf.org/html/rfc4287#section-4.2.1)
- [feedparser Documentation](https://feedparser.readthedocs.io/en/latest/)

## 📊 Impact Assessment
- **Reliability**: 🚨 CRITICAL - Prevents crashes
- **Data Integrity**: ⬆️ Preserves author information
- **Compatibility**: ⬆️ Works with more RSS feeds
- **User Experience**: ⬆️ More robust feed processing

_Originally identified by [@sourcery-ai[bot]](https://github.com/sourcery-ai) in [PR #3](https://github.com/$REPO/pull/3#discussion_r2203551593)_" \
"bug" "robustness" "sourcery-suggestion" "priority-high" "rss-handling" "data-integrity"

# Issue #7: Lift Code After Control Flow Jump
update_issue 7 \
"Code Quality: Simplify Control Flow Structure" \
"## 📋 Summary
Simplify code structure by lifting statements that appear after control flow jumps (return/break/continue) to reduce nesting and improve readability.

## 🔍 Issue Details
Code contains patterns where statements follow control flow jumps in a way that creates unnecessary nesting or complex flow. This can be simplified by restructuring the logic.

## 📂 Affected Files
- [\`podfeedfilter/filterer.py\`](https://github.com/$REPO/blob/main/podfeedfilter/filterer.py) - Multiple functions likely affected
- Other modules (requires investigation)

## 🔍 Pattern Examples
\`\`\`python
# Current pattern (needs refactoring)
if condition:
    if other_condition:
        return early_result
    else:
        # code here can be lifted
        normal_processing()
        return result

# Improved pattern
if condition and other_condition:
    return early_result

# Lifted code (reduced nesting)
if condition:
    normal_processing()
    return result
\`\`\`

## ✅ Task List
- [ ] Search codebase for complex nested control structures
- [ ] Identify opportunities to lift code after jumps
- [ ] Analyze control flow to ensure logic preservation
- [ ] Refactor nested conditions to reduce complexity
- [ ] Use guard clauses where appropriate
- [ ] Run tests to verify behavior unchanged
- [ ] Measure cyclomatic complexity improvement

## 🎯 Acceptance Criteria
- [ ] Reduced nesting levels in affected functions
- [ ] Maintained identical functional behavior
- [ ] Improved code readability
- [ ] Lower cyclomatic complexity metrics
- [ ] All tests continue to pass

## 🔗 References
- [Guard Clause Pattern](https://refactoring.guru/replace-nested-conditional-with-guard-clauses)
- [Sourcery Control Flow Rules](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/)
- [Clean Code Principles](https://blog.cleancoder.com/uncle-bob/2013/05/27/TheTransformationPriorityPremise.html)

## 📊 Benefits
- **Readability**: ⬆️ Less nested, easier to follow
- **Maintainability**: ⬆️ Simpler control flow
- **Debugging**: ⬆️ Clearer execution paths

_Originally identified by [@sourcery-ai[bot]](https://github.com/sourcery-ai) in [PR #3](https://github.com/$REPO/pull/3)_" \
"code-quality" "sourcery-suggestion" "refactoring" "priority-low" "readability"

# Issue #10: Remove Unnecessary Else After Guard Condition
update_issue 10 \
"Code Quality: Remove Unnecessary Else Clauses" \
"## 📋 Summary
Remove unnecessary \`else\` statements that follow guard conditions (early returns) to simplify code structure and improve readability.

## 🔍 Issue Details
Code contains \`if-else\` patterns where the \`if\` block contains a return statement, making the \`else\` clause unnecessary since code naturally continues to that point.

## 📂 Affected Files
- [\`podfeedfilter/filterer.py\`](https://github.com/$REPO/blob/main/podfeedfilter/filterer.py) - Multiple functions
- [\`podfeedfilter/config.py\`](https://github.com/$REPO/blob/main/podfeedfilter/config.py) - Configuration handling
- Test files may also have similar patterns

## 🔍 Pattern to Find
\`\`\`python
# Current pattern (needs refactoring)
if guard_condition:
    return early_value
else:
    # This else is unnecessary
    normal_processing()
    return normal_value

# Improved pattern (else removed)
if guard_condition:
    return early_value

# Code naturally continues here
normal_processing()
return normal_value
\`\`\`

## ✅ Task List
- [ ] Search codebase for \`if-else\` patterns with early returns
- [ ] Identify guard conditions that make else unnecessary
- [ ] Remove unnecessary else clauses
- [ ] Reduce indentation of code that was in else blocks
- [ ] Verify logic flow remains identical
- [ ] Run full test suite to confirm no regressions
- [ ] Check for any style guide compliance improvements

## 🎯 Acceptance Criteria
- [ ] All unnecessary else clauses removed
- [ ] Code indentation improved (less nested)
- [ ] Identical functional behavior preserved
- [ ] Improved code readability score
- [ ] All tests pass without modification

## 🔗 References
- [Guard Clause Refactoring](https://refactoring.guru/replace-nested-conditional-with-guard-clauses)
- [Sourcery: remove-unnecessary-else](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/remove-unnecessary-else/)
- [Python PEP 8 Style Guide](https://pep8.org/#programming-recommendations)

## 📊 Impact
- **Readability**: ⬆️ Less indentation, clearer flow
- **Maintainability**: ⬆️ Simpler conditional logic  
- **Code Quality**: ⬆️ More Pythonic structure

## 🔧 Example Locations
Based on common patterns, likely found in:
- Input validation functions
- Configuration parsing logic
- Feed processing conditionals
- Error handling code

_Originally identified by [@sourcery-ai[bot]](https://github.com/sourcery-ai) via [remove-unnecessary-else rule](https://docs.sourcery.ai/Reference/Default-Rules/refactorings/remove-unnecessary-else/)_" \
"code-quality" "sourcery-suggestion" "refactoring" "priority-low" "readability" "guard-clauses"

echo ""
echo "🎉 Issue update complete!"
echo ""
echo "📊 Summary of changes:"
echo "  • Issue #4: Named expressions and list extend optimization"
echo "  • Issue #5: Replace for-loop with any() builtin"
echo "  • Issue #6: 🚨 HIGH PRIORITY - Robust author field handling"
echo "  • Issue #7: Simplify control flow structure"
echo "  • Issue #10: Remove unnecessary else clauses"
echo ""
echo "💡 Next steps:"
echo "  1. Review the updated issues on GitHub"
echo "  2. Prioritize Issue #6 (HIGH PRIORITY bug fix)"
echo "  3. Use GitHub Projects to track progress"
echo "  4. Create milestone for \"Code Quality Improvements\""
echo ""
echo "🔗 GitHub Features Used:"
echo "  • Task lists for tracking progress"
echo "  • File links with line numbers"
echo "  • Labels for organization and filtering"
echo "  • Priority indicators"
echo "  • Rich markdown formatting"
echo "  • Cross-references to PRs and documentation"
