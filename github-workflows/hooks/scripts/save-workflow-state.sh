#!/usr/bin/env bash
# Save current workflow state
# Captures branch, commits, open PRs for session continuity

set -euo pipefail

STATE_FILE=".claude/workflow-state.json"

# Create .claude directory if it doesn't exist
mkdir -p "$(dirname "$STATE_FILE")"

# Get current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

# Get recent commits as JSON array (without jq dependency)
COMMITS_RAW=$(git log --oneline -5 2>/dev/null || echo "")
COMMITS_JSON="["
if [ -n "$COMMITS_RAW" ]; then
    first=true
    while IFS= read -r line; do
        if [ "$first" = true ]; then
            first=false
        else
            COMMITS_JSON+=","
        fi
        # Escape quotes and backslashes in commit message
        escaped=$(echo "$line" | sed 's/\\/\\\\/g; s/"/\\"/g')
        COMMITS_JSON+="\"$escaped\""
    done <<< "$COMMITS_RAW"
fi
COMMITS_JSON+="]"

# Get open PRs (if gh available)
if command -v gh &> /dev/null; then
    OPEN_PRS=$(gh pr list --json number,title --limit 5 2>/dev/null || echo "[]")
else
    OPEN_PRS="[]"
fi

# Save state
cat > "$STATE_FILE" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "branch": "$BRANCH",
  "commits": $COMMITS_JSON,
  "open_prs": $OPEN_PRS
}
EOF

echo "✓ Workflow state saved to $STATE_FILE"
