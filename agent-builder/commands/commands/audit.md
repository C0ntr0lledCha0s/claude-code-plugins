---
description: Audit all commands in repository for quality and compliance
allowed-tools: Read, Bash
argument-hint: [--verbose]
model: claude-haiku-4-5
---

# Audit All Commands

Run comprehensive quality audit on all commands in the repository.

## Your Task

Execute the bulk command audit tool to validate all commands and generate a report.

## Arguments

- `$1` - (optional) `--verbose` or `-v` to show warnings and recommendations

## Workflow

1. **Run Audit**: Execute audit script
   ```bash
   python3 {baseDir}/../scripts/audit-commands.py $ARGUMENTS
   ```

2. **Script Scans**:
   - `.claude/commands/` directory
   - Plugin `commands/` directories
   - All subdirectories (namespaced commands)

3. **Script Validates Each Command**:
   - Filename format (lowercase-hyphens)
   - Required fields (description)
   - Model field (NO short aliases allowed)
   - Tool permissions (valid tools only)
   - Security (Bash validation, dangerous patterns)
   - Argument handling (hint, documentation)

4. **Script Generates Report**:
   - Total command count
   - Status breakdown:
     - ✅ Valid (no issues)
     - ⚠️ Warnings (improvements recommended)
     - ❌ Errors (critical issues, blocks commit)
     - 💥 Parse Errors (invalid YAML/structure)
   - Lists all commands with errors
   - Shows warnings (if --verbose)
   - Provides remediation guidance

5. **Present Results**: Show the user the audit report

## Example Usage

```
# Basic audit (errors only)
/agent-builder:commands:audit

# Detailed audit (includes warnings)
/agent-builder:commands:audit --verbose
```

## Report Sections

1. **Summary**
   - Total commands
   - Count by status

2. **Commands with Errors** (always shown)
   - Lists each command with critical issues
   - Shows specific error messages
   - Blocks git commit if pre-commit hook enabled

3. **Commands with Warnings** (--verbose only)
   - Lists commands with recommended improvements
   - Non-blocking, but should be addressed

4. **Recommendations**
   - Suggested next actions
   - Links to fix tools

## Exit Codes

- `0` - All commands valid or only warnings
- `1` - Critical errors found (blocks commit)

## Common Issues Found

- **Model Field Errors**: Short aliases (haiku/sonnet/opus) instead of version aliases
- **Security Issues**: Bash access without validation documentation
- **Missing Fields**: No description
- **Naming Issues**: Uppercase, underscores, too long
- **Dangerous Patterns**: Command injection risks, rm -rf $var, eval $var

## What to Do With Results

1. **Fix Critical Errors First** (❌)
   - Use `/agent-builder:commands:update <name>` or `/agent-builder:commands:migrate <name> --apply`

2. **Address Warnings** (⚠️)
   - Use `/agent-builder:commands:enhance <name>` to see specific improvements

3. **Re-run Audit**
   - Verify improvements: `/agent-builder:commands:audit`

## Integration with Pre-Commit Hooks

If pre-commit hook is configured, this audit runs automatically before commits and blocks commits with errors.

## If Script Not Found

Script path: `agent-builder/skills/building-commands/scripts/audit-commands.py`
