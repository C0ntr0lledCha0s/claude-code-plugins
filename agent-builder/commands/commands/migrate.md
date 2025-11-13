---
description: Migrate command schema (e.g., short aliases to version aliases)
allowed-tools: Read, Bash
argument-hint: [command-name or --dry-run|--apply]
model: claude-haiku-4-5
---

# Migrate Command Schema

Migrate command(s) to current schema: **$1**

## Your Task

Run the command migration tool to automatically update command schemas.

## Arguments

- `$1` - Command name, `--dry-run` (preview all), or `--apply` (apply to all)
- `$2` - (optional) `--apply` flag for single command migration

## Common Migrations

1. **Short Alias → Version Alias** (MOST IMPORTANT)
   - `model: haiku` → `model: claude-haiku-4-5`
   - `model: sonnet` → `model: claude-sonnet-4-5`
   - `model: opus` → `model: claude-opus-4-5`
   - `model: inherit` → (field removed)

2. **Argument Hint Format**
   - Converts YAML lists to strings
   - Adds brackets if missing

3. **Field Renames**
   - `tools:` → `allowed-tools:` (if needed)

## Workflow

### Preview All Commands
```bash
python3 {baseDir}/../scripts/migrate-command.py --dry-run
```

Shows what would change without modifying files.

### Apply to All Commands
```bash
python3 {baseDir}/../scripts/migrate-command.py --apply
```

Applies migrations interactively with confirmation for each file.

### Migrate Single Command (Preview)
```bash
python3 {baseDir}/../scripts/migrate-command.py $1
```

### Migrate Single Command (Apply)
```bash
python3 {baseDir}/../scripts/migrate-command.py $1 --apply
```

## Example Usage

```
# Preview what needs migration
/agent-builder:commands:migrate --dry-run

# Apply to specific command
/agent-builder:commands:migrate new-agent --apply

# Apply to all commands
/agent-builder:commands:migrate --apply
```

## Script Behavior

- **Preview mode**: Shows changes without applying
- **Apply mode**: Shows diff and asks for confirmation
- **Backup**: Creates .md.bak before applying
- **Validation**: Recommends running validation after migration

## When to Use

- After upgrading Claude Code version
- When short alias errors occur (model not found)
- To standardize command format across repository
- Before committing commands to version control

## Migration Report

Script provides:
- Total commands found
- Number needing migration
- Number already up-to-date
- Specific changes for each file

## If Script Not Found

Script path: `agent-builder/skills/building-commands/scripts/migrate-command.py`
