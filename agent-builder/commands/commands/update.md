---
description: Interactively update a slash command's configuration with diff preview
allowed-tools: Read, Bash
argument-hint: [command-name]
model: claude-haiku-4-5
---

# Update Command

Update the slash command named: **$1**

## Your Task

Run the interactive command updater script to modify an existing command's configuration.

## Arguments

- `$1` - The command name (without .md extension)

## Workflow

1. **Invoke Script**: Run the update-command.py script
   ```bash
   python3 {baseDir}/../scripts/update-command.py $1
   ```

2. **Script Will**:
   - Find the command file
   - Show current configuration
   - Present interactive menu:
     1. Update description
     2. Update allowed-tools
     3. Update model (version alias or full ID)
     4. Update argument-hint
     5. Run validation
   - Show diff preview
   - Confirm before applying changes
   - Create backup (.md.bak)
   - Run validation after update

3. **Present Results**: Show the user what was changed

## Example Usage

```
/agent-builder:commands:update new-agent
```

## Important Notes

- Changes are previewed before applying
- Original file is backed up
- Validation runs automatically
- Model field must use version aliases (claude-haiku-4-5) NOT short aliases (haiku)

## If Script Not Found

If the script is not found, the user may need to check:
- They're in the correct directory
- The agent-builder plugin is installed
- Script path: `agent-builder/skills/building-commands/scripts/update-command.py`
