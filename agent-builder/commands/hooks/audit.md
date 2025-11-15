---
description: Security-focused bulk audit of all hooks.json files in repository
allowed-tools: Read, Bash
argument-hint: "[directory] [--verbose]"
model: claude-haiku-4-5
---

# Audit Hooks Command

Bulk security audit of all hooks.json files in a repository or directory.

## Usage

```bash
# Audit current directory
/agent-builder:hooks:audit

# Audit specific directory
/agent-builder:hooks:audit path/to/directory

# Verbose output with details
/agent-builder:hooks:audit . --verbose
```

## What This Does

1. **Finds all hooks.json files** in directory tree
   - Searches `*/hooks/hooks.json`
   - Searches `.claude/hooks.json`
   - Searches all subdirectories

2. **Validates each file**:
   - JSON syntax
   - Schema compliance
   - Security issues
   - Script existence

3. **Categorizes results**:
   - ✅ Valid: No issues
   - ⚠️  Warnings: Minor issues
   - ❌ Errors: Critical problems
   - ❌ Parse Errors: Invalid JSON

4. **Reports summary** with file-by-file breakdown

## Output

```
🔍 HOOKS AUDIT
Directory: /home/user/project

Found 3 hooks.json file(s)

==========================================================

self-improvement/hooks/hooks.json
✓ Valid

github-workflows/hooks/hooks.json
⚠️  2 warning(s)

agent-builder/hooks/hooks.json
❌ 1 critical error(s)

==========================================================

📊 AUDIT SUMMARY

Valid: 1
Warnings: 1
Errors: 1
Parse Errors: 0

Files with errors:
  ❌ agent-builder/hooks/hooks.json (1 critical, 2 warnings)

Files with warnings:
  ⚠️  github-workflows/hooks/hooks.json (2 warnings)

❌ Audit completed with errors
```

## Verbose Mode

Use `--verbose` to see detailed validation output for each file:

```bash
/agent-builder:hooks:audit --verbose
```

Shows:
- All validation findings
- Security warnings
- Schema issues
- Specific line numbers and details

## Security Focus

The audit specifically checks for:
- Dangerous command patterns
- Command injection vulnerabilities
- Missing input validation
- Unsafe script execution
- Permission issues

## Exit Codes

- **0**: All hooks valid or only warnings
- **1**: Critical errors or parse errors found

Useful for CI/CD pipelines:
```bash
# In GitHub Actions or pre-commit
/agent-builder:hooks:audit || exit 1
```

## Integration with CI/CD

Add to `.github/workflows/validate.yml`:

```yaml
- name: Audit Hooks
  run: |
    python3 agent-builder/skills/building-hooks/scripts/audit-hooks.py . --verbose
```

Or in pre-commit hook:

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Auditing hooks..."
python3 agent-builder/skills/building-hooks/scripts/audit-hooks.py .

if [ $? -ne 0 ]; then
  echo "❌ Hook audit failed. Fix errors before committing."
  exit 1
fi
```

## When to Use

- **Pre-commit**: Validate hooks before committing
- **CI/CD**: Automated security checks
- **Code Review**: Audit hooks in pull requests
- **Regular Audits**: Periodic security reviews
- **Onboarding**: Check inherited codebases

## What Gets Checked

For each hooks.json:
1. **JSON Validity**: Proper syntax, no parse errors
2. **Structure**: Top-level 'hooks' object, valid arrays
3. **Events**: Valid event names, proper matcher usage
4. **Security**: Dangerous patterns, injection risks
5. **Scripts**: File existence, executability
6. **Types**: Valid hook types, required fields

## Common Issues Found

**Critical Errors:**
- Invalid JSON syntax
- Invalid event names
- Missing required matchers
- Invalid hook types
- Security vulnerabilities

**Warnings:**
- Scripts not found
- Scripts not executable
- Relative paths
- Missing validation

## Bulk Operations

For large repositories with many hooks:
1. Run audit to identify all issues
2. Use `/agent-builder:hooks:enhance` on problem files
3. Fix critical security issues first
4. Use `/agent-builder:hooks:migrate` for automated fixes
5. Re-audit to verify fixes

## Output Files

The audit writes:
- Summary to stdout
- Detailed results in verbose mode
- Exit code for automation

No files are modified - this is read-only analysis.

**Security Best Practice**: Run audit before every commit to catch issues early.
