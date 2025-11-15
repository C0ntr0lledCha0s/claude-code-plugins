---
description: Compare two hooks.json files side-by-side
allowed-tools: Read, Bash
argument-hint: "[hooks1.json] [hooks2.json]"
model: claude-haiku-4-5
---

# Compare Hooks Command

Side-by-side comparison of two hooks.json files showing differences in structure, events, and configuration.

## Usage

```bash
/agent-builder:hooks:compare path/to/hooks1.json path/to/hooks2.json

# Verbose mode with detailed diff
/agent-builder:hooks:compare hooks1.json hooks2.json --verbose
```

## What This Does

Compares two hooks.json files across multiple dimensions:

### 1. Structure Comparison
- Total number of events
- Total number of hooks
- Command vs prompt hooks
- Events present in each file

### 2. Event-by-Event Comparison
- Hook counts per event
- Differences in event configuration
- Added or removed events

### 3. Detailed Diff (Verbose)
- Line-by-line JSON comparison
- Highlighted additions and removals
- Unified diff format

### 4. Similarity Score
- Percentage similarity between files
- Based on common structure and content

## Output

```
⚖️  HOOKS COMPARISON

File 1: plugin-v1/hooks/hooks.json
File 2: plugin-v2/hooks/hooks.json

==========================================================

📊 Structure Comparison:

  Events only in file 1: Notification
  Events only in file 2: PreCompact
  Common events: PreToolUse, PostToolUse, UserPromptSubmit, Stop

  Total hooks: 5 vs 7
  Command hooks: 4 vs 5
  Prompt hooks: 1 vs 2

📋 Event-by-Event Comparison:

  PreToolUse: 2 vs 3 hooks
  PostToolUse: 1 hooks (same)
  UserPromptSubmit: 1 hooks (same)
  Stop: 1 hooks (same)

Similarity: 78.5%
```

## Verbose Mode

Add `--verbose` or `-v` for detailed line-by-line diff:

```bash
/agent-builder:hooks:compare hooks1.json hooks2.json -v
```

Shows:
```
📝 Detailed Differences:

  {
    "hooks": {
-     "PreToolUse": [
+     "PreToolUse": [
        {
-         "matcher": "Write",
+         "matcher": "Write|Edit",
          "hooks": [
```

## Use Cases

### 1. Version Comparison
Compare hooks before and after updates:
```bash
# Before update
cp hooks.json hooks.json.before

# Make changes...

# Compare
/agent-builder:hooks:compare hooks.json.before hooks.json
```

### 2. Plugin Comparison
Compare hooks across different plugins:
```bash
/agent-builder:hooks:compare \
  self-improvement/hooks/hooks.json \
  github-workflows/hooks/hooks.json
```

### 3. Migration Validation
Verify migration results:
```bash
# Before migration
cp hooks.json hooks.json.original

# Migrate
/agent-builder:hooks:migrate hooks.json

# Compare
/agent-builder:hooks:compare hooks.json.original hooks.json
```

### 4. Merge Conflict Resolution
Understand differences between branches:
```bash
# Compare current with other branch
git show other-branch:hooks.json > hooks-other.json
/agent-builder:hooks:compare hooks.json hooks-other.json
```

## Similarity Scoring

- **100%**: Files are identical
- **80-99%**: Very similar, minor differences
- **60-79%**: Moderately similar, some changes
- **40-59%**: Significantly different
- **<40%**: Major differences or restructuring

## Common Differences Detected

**Structural:**
- Added/removed events
- Changed hook counts
- Different hook types (command vs prompt)

**Configuration:**
- Modified matchers
- Changed commands or prompts
- Reordered hooks
- Updated script paths

**Content:**
- Different validation logic
- Modified security checks
- Updated error handling

## Integration with Workflows

**Pull Request Reviews:**
```bash
# In PR review
git diff main...feature -- '*/hooks.json' > /dev/null
if [ $? -eq 0 ]; then
  /agent-builder:hooks:compare \
    <(git show main:plugin/hooks/hooks.json) \
    plugin/hooks/hooks.json
fi
```

**Pre-Merge Validation:**
```bash
# Before merging branches
/agent-builder:hooks:compare \
  hooks.json \
  <(git show feature-branch:hooks.json)
```

## When to Use

- **Code Reviews**: Understand hook changes in PRs
- **Migrations**: Validate migration results
- **Version Control**: Compare branches or commits
- **Debugging**: Find what changed between working and broken states
- **Documentation**: Generate change summaries
- **Audits**: Compare production vs development hooks

## Output Interpretation

**Events only in file 1**:
- These events exist in the first file but not the second
- May indicate removed functionality

**Events only in file 2**:
- These events exist in the second file but not the first
- May indicate new functionality

**Hook count differences**:
- Shows added or removed hooks within same event
- Helps track feature additions/removals

**Similarity percentage**:
- High (>90%): Minor tweaks or updates
- Medium (60-90%): Moderate changes
- Low (<60%): Major refactoring or redesign

## Example Workflows

### Comparing Plugin Versions
```bash
# Extract from different versions
tar xf plugin-v1.0.tar.gz
tar xf plugin-v2.0.tar.gz

# Compare
/agent-builder:hooks:compare \
  plugin-v1.0/hooks/hooks.json \
  plugin-v2.0/hooks/hooks.json
```

### Finding Regression
```bash
# Compare with last known good version
git show HEAD~5:hooks.json > hooks-working.json
/agent-builder:hooks:compare hooks-working.json hooks.json --verbose
```

### Merging Changes
```bash
# See differences before manual merge
/agent-builder:hooks:compare hooks.json hooks.json.theirs
# Make informed decisions about which changes to keep
```

**Note**: This is a read-only comparison tool - no files are modified.
