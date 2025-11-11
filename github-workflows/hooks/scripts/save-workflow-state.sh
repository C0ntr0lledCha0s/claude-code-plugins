#!/usr/bin/env bash
# Save current workflow state
# Captures branch, commits, open PRs for session continuity

set -euo pipefail

STATE_FILE=".claude/workflow-state.json"

# Get current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

# Get recent commits
COMMITS=$(git log --oneline -5 2>/dev/null || echo "")

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
  "commits": $(echo "$COMMITS" | jq -R . | jq -s .),
  "open_prs": $OPEN_PRS
}
EOF

echo "✓ Workflow state saved to $STATE_FILE"
