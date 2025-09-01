#!/bin/bash

# Update Existing Issues with Labels Script
# This script adds appropriate labels to existing Sourcery issues

REPO="jkdelauney/podfeedfilter"

# Check if GitHub token is available
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    echo "Please set your GitHub token: export GITHUB_TOKEN=your_token_here"
    exit 1
fi

echo "Updating issue labels for $REPO..."

# Function to add labels to an issue
add_labels() {
    local issue_number=$1
    shift
    local labels=("$@")
    
    # Convert labels array to JSON format
    local labels_json=$(printf '%s\n' "${labels[@]}" | jq -R . | jq -s .)
    
    echo "Adding labels to issue #$issue_number: ${labels[*]}"
    
    curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/repos/$REPO/issues/$issue_number/labels \
        -d "{\"labels\":$labels_json}" \
        | jq -r 'if type == "array" then .[].name else .message end' 2>/dev/null || echo "Added labels successfully"
}

# Update Issue #4: Use named expression to simplify assignment
add_labels 4 "code-quality" "sourcery-suggestion" "refactoring" "priority-low"

# Update Issue #5: Use any() instead of for loop
add_labels 5 "code-quality" "performance" "sourcery-suggestion" "priority-low"

# Update Issue #6: Handle 'author' field edge cases  
add_labels 6 "bug" "robustness" "sourcery-suggestion" "priority-high"

# Update Issue #7: Lift code into else after jump in control flow
add_labels 7 "code-quality" "sourcery-suggestion" "refactoring" "priority-low"

# Update Issue #10: Remove unnecessary else after guard condition
add_labels 10 "code-quality" "sourcery-suggestion" "refactoring" "priority-low"

echo "Issue label update complete!"
