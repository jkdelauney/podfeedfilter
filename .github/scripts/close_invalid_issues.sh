#!/bin/bash

# Close Invalid/Duplicate Issues Script
# This script closes issues that are duplicates of PRs or already completed

REPO="jkdelauney/podfeedfilter"

# Check if GitHub token is available
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    echo "Please set your GitHub token: export GITHUB_TOKEN=your_token_here"
    exit 1
fi

echo "Closing invalid/duplicate issues for $REPO..."

# Function to close an issue
close_issue() {
    local issue_number=$1
    local reason=$2
    
    echo "Closing issue #$issue_number: $reason"
    
    # First, add a comment explaining why we're closing
    curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/repos/$REPO/issues/$issue_number/comments \
        -d "{\"body\":\"$reason\"}" > /dev/null
    
    # Then close the issue
    curl -s -X PATCH \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/repos/$REPO/issues/$issue_number \
        -d '{"state":"closed"}' \
        | jq -r '.state // .message // "Unknown result"'
}

# Close Issue #19 - Duplicate of PR #19
close_issue 19 "This issue was automatically created from PR #19. The actual work is tracked in the pull request itself. Closing this duplicate issue to avoid confusion."

# Close Issue #20 - Duplicate of PR #20  
close_issue 20 "This issue was automatically created from PR #20. The actual work is tracked in the pull request itself. Closing this duplicate issue to avoid confusion."

# Close Issue #11 - Already completed
close_issue 11 "This suggestion has been addressed in recent changes where we added comprehensive assertions for excluded episodes in performance tests. The filtering logic now properly validates that excluded content (like sports episodes) are omitted from the output.

Closing as completed."

echo "Issue closure complete!"
