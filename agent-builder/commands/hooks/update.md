---
description: Interactively update a hook's configuration with security validation
allowed-tools: Read, Bash
argument-hint: "[hooks.json path]"
model: claude-haiku-4-5
---

# Update Hook Command

Interactively update hooks in a hooks.json file with security-focused validation.

## Usage

```bash
/agent-builder:hooks:update path/to/hooks.json
```

## What This Does

This command launches an interactive hook updater that:

1. **Lists all hooks** in the hooks.json file
2. **Lets you select** which hook to modify
3. **Interactive menus** for updating:
   - Event type (PreToolUse, PostToolUse, etc.)
   - Matcher pattern (for tool events)
   - Hook type (command or prompt)
   - Command or prompt text
4. **Security validation**:
   - Checks for dangerous command patterns
   - Validates matcher regex
   - Ensures event/matcher compatibility
5. **Shows diff** before applying changes
6. **Creates backup** before modifying

## Hook Structure

Hooks are defined in hooks.json:
- **Tool Events** (PreToolUse, PostToolUse): Require matcher patterns
- **Lifecycle Events** (UserPromptSubmit, Stop, SessionStart): No matchers
- **Hook Types**:
  - `command`: Execute bash script
  - `prompt`: LLM-based evaluation

## Security Features

The updater warns about:
- Command injection risks (eval, command substitution)
- Dangerous commands (rm -rf, dd, mkfs)
- Parameter usage without validation
- Relative paths without ${CLAUDE_PLUGIN_ROOT}

## Example Session

```
Select hook to update [1-5]: 1

Update Event Type
Current: PreToolUse

1. PreToolUse
2. PostToolUse
3. UserPromptSubmit
...

Update Matcher Pattern
Current: Write|Edit

Enter matcher (or keep current): Bash

Security warnings:
  ⚠️  Uses parameters without validation

Continue anyway? [y/N]: n

Changes Preview:
Event: PreToolUse (unchanged)
Matcher:
  - Write|Edit
  + Bash

Apply changes? [y/N]: y
```

## After Updating

The command suggests:
1. Review changes: `git diff hooks.json`
2. Validate: `python3 validate-hooks.py hooks.json`
3. Test by triggering the event

## When to Use

- Changing hook event type or matcher
- Updating hook commands or prompts
- Migrating hooks to different events
- Reviewing and improving existing hooks

**Security Note**: All changes are validated for common security issues before being applied.
