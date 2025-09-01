# GitHub Issue Management Scripts

This directory contains scripts for managing and updating GitHub issues with enhanced automation features.

## Scripts

### `update_comprehensive_issues.sh`

Enhanced script that updates existing Sourcery issues with:
- ✅ **Clear, descriptive titles**
- 📋 **Comprehensive descriptions with context**
- 🏷️ **Organized labels for filtering and automation**
- 📂 **Direct links to affected files and line numbers**
- ✅ **Task lists for tracking progress**
- 🎯 **Acceptance criteria**
- 🔗 **Reference links to documentation**
- 📊 **Impact assessments**

## Setup

### 1. Generate GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select the following scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `write:discussion` (if using GitHub Discussions)
4. Copy the generated token

### 2. Set Environment Variable

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

For persistent setup, add to your shell profile:

```bash
# Add to ~/.zshrc, ~/.bashrc, or ~/.bash_profile
echo 'export GITHUB_TOKEN=ghp_your_token_here' >> ~/.zshrc
source ~/.zshrc
```

### 3. Run the Script

```bash
cd /path/to/podfeedfilter
./.github/scripts/update_comprehensive_issues.sh
```

## GitHub Features Utilized

### 🏷️ Labels for Organization
- `priority-high`, `priority-low` - For triage and prioritization
- `bug`, `code-quality`, `performance` - Issue categorization
- `sourcery-suggestion` - Tracks Sourcery AI recommendations
- `rss-handling`, `data-integrity` - Domain-specific tags

### ✅ Task Lists for Progress Tracking
Each issue includes interactive checkboxes that can be checked off as work progresses:
- [ ] Research phase tasks
- [ ] Implementation tasks  
- [ ] Testing and validation
- [ ] Documentation updates

### 📂 File Links with Line Numbers
Direct links to specific files and line numbers in the codebase:
- [`podfeedfilter/filterer.py:87`](https://github.com/jkdelauney/podfeedfilter/blob/main/podfeedfilter/filterer.py#L87)
- Easy navigation from issue to code

### 🎯 Acceptance Criteria
Clear, testable criteria for when an issue is "done"

### 📊 Impact Indicators
Visual indicators for the impact of each change:
- 🚨 CRITICAL - High priority issues
- ⬆️ Improved - Positive improvements
- 🔧 Example - Code examples and patterns

## Automation Features for Free GitHub Users

### 1. Issue Templates
After running this script, you can create issue templates in `.github/ISSUE_TEMPLATE/` to standardize future issues.

### 2. GitHub Projects (Beta)
Use the labels to organize issues in GitHub Projects:
1. Go to your repository → Projects → New project
2. Create columns like "Todo", "In Progress", "Done"
3. Use label filters to automatically sort issues

### 3. Milestone Tracking
Create a milestone for "Code Quality Improvements":
1. Go to Issues → Milestones → New milestone
2. Add relevant issues to track overall progress

### 4. GitHub Actions (Future)
The labels enable GitHub Actions automation:
```yaml
# Example: Auto-assign priority-high issues
on:
  issues:
    types: [labeled]
jobs:
  auto-assign:
    if: contains(github.event.label.name, 'priority-high')
    # Auto-assign to maintainer
```

## Issue Summary

| Issue | Priority | Type | Description |
|-------|----------|------|-------------|
| #4 | Low | Code Quality | Named expressions and list extend |
| #5 | Low | Performance | Replace for-loop with any() builtin |
| **#6** | **🚨 HIGH** | **Bug** | **Robust author field handling** |
| #7 | Low | Code Quality | Simplify control flow structure |
| #10 | Low | Code Quality | Remove unnecessary else clauses |

## Next Steps

1. **Prioritize Issue #6** - This is a potential crash bug
2. **Review updated issues** on GitHub
3. **Create a project board** to track progress
4. **Set up milestone** for "Code Quality Improvements"
5. **Consider automation** with GitHub Actions

## Benefits

✅ **Better Organization**: Labels and priority indicators make triage easier  
✅ **Clear Context**: Each issue has full context for implementation  
✅ **Progress Tracking**: Task lists show what's completed  
✅ **Easy Navigation**: Direct links to relevant code  
✅ **Standardization**: Consistent format across all issues  
✅ **Automation Ready**: Labels enable future automation  

This approach transforms generic Sourcery suggestions into actionable, well-documented GitHub issues that integrate seamlessly with GitHub's project management features.
