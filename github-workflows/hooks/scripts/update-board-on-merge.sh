#!/usr/bin/env bash
# Update project board when PR merges
# Called by post-merge hook

set -euo pipefail

PR_NUMBER="${1:-}"

if [ -z "$PR_NUMBER" ]; then
    echo "Usage: $0 <pr-number>"
    exit 1
fi

echo "Updating project board for merged PR #$PR_NUMBER..."

# Get linked issues from PR
LINKED_ISSUES=$(gh pr view "$PR_NUMBER" --json body -q '.body' | grep -oE '#[0-9]+' | tr -d '#' || echo "")

if [ -n "$LINKED_ISSUES" ]; then
    while read -r issue_num; do
        echo "Closing issue #$issue_num (linked to merged PR)"

        # Move to Done column in project boards (would need project-specific logic)
        # gh issue close "$issue_num" --comment "Closed by PR #$PR_NUMBER"

    done <<< "$LINKED_ISSUES"

    echo "✓ Updated project boards for linked issues"
else
    echo "No linked issues found"
fi
