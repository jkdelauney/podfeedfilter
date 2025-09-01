#!/bin/bash

# GitHub Labels Creation Script
# Run this script to create all necessary labels for issue organization

REPO="jkdelauney/podfeedfilter"

# Check if GitHub token is available
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is required"
    echo "Please set your GitHub token: export GITHUB_TOKEN=your_token_here"
    exit 1
fi

echo "Creating GitHub labels for $REPO..."

# Function to create a label
create_label() {
    local name=$1
    local color=$2
    local description=$3
    
    echo "Creating label: $name"
    curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/repos/$REPO/labels \
        -d "{\"name\":\"$name\",\"color\":\"$color\",\"description\":\"$description\"}" \
        | jq -r '.name // .errors[0].message // "Unknown error"'
}

# Create all necessary labels
create_label "sourcery-suggestion" "FFA500" "For all Sourcery-AI recommendations"
create_label "code-quality" "0075CA" "For code quality improvements"
create_label "testing" "C2E0C6" "For test-related issues"
create_label "enhancement" "A2EEEF" "For new features or improvements"
create_label "refactoring" "D4C5F9" "For code refactoring tasks"
create_label "robustness" "FBCA04" "For improving edge case handling"
create_label "performance" "FF6B6B" "For performance improvements"
create_label "priority-high" "D73A49" "Critical issues"
create_label "priority-medium" "FFA500" "Important but not urgent"
create_label "priority-low" "28A745" "Nice to have improvements"

echo "Label creation complete!"
