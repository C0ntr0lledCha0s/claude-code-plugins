---
description: Migrate hooks.json to current schema with automated fixes
allowed-tools: Read, Bash
argument-hint: "[hooks.json path] [--dry-run]"
model: claude-haiku-4-5
---

# Migrate Hook Command

Automated schema migration for hooks.json files with security improvements.

## Usage

```bash
# Preview changes without modifying
/agent-builder:hooks:migrate path/to/hooks.json --dry-run

# Apply migrations
/agent-builder:hooks:migrate path/to/hooks.json
```

## Migrations Performed

### 1. Remove Invalid Events
- Detects and removes hooks with invalid event names
- Only keeps valid events: PreToolUse, PostToolUse, UserPromptSubmit, Stop, SessionStart, Notification, SubagentStop, PreCompact

### 2. Clean Empty Matchers
- Removes empty matchers from lifecycle events
- Lifecycle events (UserPromptSubmit, Stop, etc.) should not have matchers
- Warns if lifecycle events have non-empty matchers

### 3. Add Missing Matchers
- Adds default wildcard matcher ('*') to tool events missing matchers
- PreToolUse and PostToolUse require matchers
- Prevents validation errors

### 4. Validate Hook Types
- Fixes invalid hook types
- Ensures 'command' hooks have 'command' field
- Ensures 'prompt' hooks have 'prompt' field
- Reports errors for unfixable issues

### 5. Normalize Script Paths (Recommendations)
- Suggests using ${CLAUDE_PLUGIN_ROOT} for relative paths
- Improves portability across environments
- These are recommendations, not automatic changes

## Output

```
🔄 HOOK MIGRATION
File: plugin/hooks/hooks.json

Running migrations...

1. Checking for invalid event names...
   ✓ All event names are valid

2. Removing empty matchers from lifecycle events...
   ✓ Removed empty matcher from UserPromptSubmit hook #1

3. Adding missing matchers to tool events...
   ✓ All tool events have matchers

4. Validating hook types...
   ✓ Fixed type to 'command' for PreToolUse hook #1, item #1

5. Analyzing script paths...
   RECOMMEND: Use ${CLAUDE_PLUGIN_ROOT} for 'scripts/validate.sh'

📝 Migration Changes:
✓ Removed empty matcher from UserPromptSubmit hook #1
✓ Fixed type to 'command' for PreToolUse hook #1, item #1
ℹ️ RECOMMEND: Use ${CLAUDE_PLUGIN_ROOT} for 'scripts/validate.sh'

✓ Backup created: hooks.json.backup
✓ Migration applied successfully!
```

## Dry Run Mode

Use `--dry-run` to preview changes without modifying files:

```bash
/agent-builder:hooks:migrate hooks.json --dry-run
```

Shows what would change without saving. Useful for:
- Reviewing migrations before applying
- Understanding what needs to change
- Testing migration logic

## Safety Features

1. **Automatic Backup**: Creates `.json.backup` before modifying
2. **Validation**: Checks all changes before saving
3. **Error Recovery**: Restores from backup if write fails
4. **Dry Run**: Preview mode available

## Exit Codes

- **0**: Success or only recommendations
- **1**: Migration completed with errors requiring manual review

## When to Use

- After updating Claude Code version
- When validation reports schema errors
- Converting old hook formats
- Cleaning up deprecated patterns
- Preparing hooks for production

## Common Migrations

**Empty Matchers:**
```json
// Before
{
  "UserPromptSubmit": [{
    "matcher": "",
    "hooks": [...]
  }]
}

// After
{
  "UserPromptSubmit": [{
    "hooks": [...]
  }]
}
```

**Missing Matchers:**
```json
// Before
{
  "PreToolUse": [{
    "hooks": [...]
  }]
}

// After
{
  "PreToolUse": [{
    "matcher": "*",
    "hooks": [...]
  }]
}
```

**Invalid Types:**
```json
// Before
{
  "type": "bash",
  "command": "bash script.sh"
}

// After
{
  "type": "command",
  "command": "bash script.sh"
}
```

## After Migration

1. Review changes: `git diff hooks.json`
2. Validate: `python3 validate-hooks.py hooks.json`
3. Test hooks by triggering events
4. Commit if all looks good

**Note**: Manual review recommended for ERROR messages in migration output.
