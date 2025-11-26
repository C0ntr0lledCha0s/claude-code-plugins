---
description: Create a PR with proper formatting, auto-generated description, and issue links
allowed-tools: Bash, Read, Grep
argument-hint: "[--title TITLE] [--draft]"
---

# PR Create

Create a pull request with automatically generated description from commits and proper formatting.

## Usage

```bash
/pr-create                          # Auto-detect title and generate description
/pr-create --title "Add auth"       # Custom title
/pr-create --draft                  # Create as draft PR
/pr-create --title "Fix bug" --draft
```

## Arguments

- **--title TITLE** (optional): PR title
  - If omitted, derives from first commit or branch name
  - Validates against conventional commit format

- **--draft** (optional): Create as draft PR
  - Use when PR needs more work before review

## What This Does

1. **Analyze branch**: Get commits and file changes since base branch
2. **Generate title**: From first commit or branch name
3. **Build description**:
   - Summary from commits
   - List of changes
   - Linked issues
   - Testing checklist
4. **Apply labels**: Based on file paths and commit types
5. **Create PR**: With gh pr create

## Workflow

When this command is invoked:

### Step 1: Get Branch Information

```bash
# Get current branch
BRANCH=$(git branch --show-current)

# Get base branch (main or develop)
BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")

# Get commits on this branch
COMMITS=$(git log $BASE..$BRANCH --pretty=format:"%s" --reverse)

# Get files changed
FILES=$(git diff --name-only $BASE...$BRANCH)
```

### Step 2: Generate Title

If title not provided:

```bash
# From branch name: feature/issue-42-auth → Add authentication (Closes #42)
# From first commit: feat(auth): add login → Add login

# Parse branch for issue number
ISSUE=$(echo "$BRANCH" | grep -oE '[0-9]+' | head -1)

# Use first commit subject
TITLE=$(git log $BASE..$BRANCH --pretty=format:"%s" --reverse | head -1)
```

### Step 3: Build Description

Generate PR body with:

```markdown
## Summary

[Auto-generated from commits]

## Changes

- List of commits grouped by type
- Files changed

## Testing

- [ ] Tests added/updated
- [ ] Manual testing completed
- [ ] No regressions

## Related Issues

Closes #N (if detected from branch name or commits)

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

### Step 4: Detect Labels

```bash
# From commit types
feat: → feature
fix: → bug
docs: → documentation

# From file paths
frontend/* → scope:frontend
backend/* → scope:backend
*.test.* → has-tests
```

### Step 5: Create PR

```bash
# Get any linked issues
ISSUES=$(echo "$COMMITS" | grep -oE '#[0-9]+' | sort -u | tr '\n' ' ')

# Create the PR
gh pr create \
  --title "$TITLE" \
  --body "$BODY" \
  --base "$BASE" \
  ${DRAFT:+--draft} \
  ${LABELS:+--label "$LABELS"}
```

### Step 6: Post-Creation

After PR is created:
- Display PR URL
- Show suggested reviewers
- Add to project board if configured

## Output Example

```
Creating PR for branch: feature/issue-42-auth

Branch Analysis:
- Base: main
- Commits: 3
- Files changed: 8

Generated Title: feat(auth): add user authentication

Generated Description:
## Summary
Add user authentication with JWT tokens...

Detected Labels: feature, scope:backend

Creating PR...
✓ PR created: https://github.com/owner/repo/pull/123

Suggested reviewers based on CODEOWNERS:
- @backend-team (src/api/*)
- @security-team (src/auth/*)

Add to project board?
```

## Integration

Works with:
- **pr-manager.py**: Uses auto-label and sync-board functions
- **reviewing-pull-requests skill**: For review workflow
- **issue-track**: Links to tracked issues

## Notes

- Validates branch is not main/master before creating
- Checks for uncommitted changes
- Validates conventional commit format for title
- Automatically links issues mentioned in commits
- Does not push - assumes branch is already pushed
