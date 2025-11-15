---
description: Analyze hook quality with comprehensive security-focused scoring
allowed-tools: Read, Bash
argument-hint: "[hooks.json path]"
model: claude-haiku-4-5
---

# Enhance Hook Command

Comprehensive quality and security analysis for hooks.json files.

## Usage

```bash
/agent-builder:hooks:enhance path/to/hooks.json
```

## What This Does

Analyzes hooks across 7 security-critical categories:

### 1. Schema Compliance (0-10)
- Valid JSON structure
- Correct event names
- Proper matcher requirements
- Valid hooks array structure

### 2. Security (0-10) ⚠️ CRITICAL
- Dangerous command patterns (eval, rm -rf, etc.)
- Command injection risks
- Parameter validation
- Error handling (set -euo pipefail)
- Absolute vs relative paths

### 3. Matcher Validity (0-10)
- Valid regex patterns
- Appropriate wildcards
- Escaped pipe usage
- Tool event requirements

### 4. Script Existence (0-10)
- Referenced scripts exist
- Scripts are executable
- Variable substitutions noted

### 5. Hook Types (0-10)
- Valid type fields (command/prompt)
- Required fields present
- Non-empty commands/prompts

### 6. Documentation (0-10)
- Top-level documentation
- Prompt clarity
- Decision keywords present

### 7. Maintainability (0-10)
- Hook count reasonable
- No duplicate commands
- Consistent path styles
- Clear organization

## Output

```
🔍 HOOK QUALITY ANALYSIS
File: plugin/hooks/hooks.json

==========================================================

Schema Compliance: 10/10
  ✅ Schema is fully compliant

Security: 6/10
  ❌ PreToolUse hook #1, item #1: Command substitution (injection risk)
  ⚠️  PreToolUse hook #1, item #1: Uses parameters without validation

Matcher Validity: 10/10
  ✅ All matchers are valid

...

Overall Score: 52/70 (74.3%) - Grade B

🎯 PRIORITY IMPROVEMENTS:
Security (Score: 6/10)
  • ❌ Command substitution (injection risk)
  • ⚠️  Uses parameters without validation
```

## Scoring System

- **Grade A** (80%+): Production ready, minor improvements
- **Grade B** (60-79%): Good, address warnings
- **Grade C** (<60%): Needs significant work

## Critical Failures

If critical security issues are found:
- Exit code 1
- Immediate attention required
- Blocks in CI/CD pipelines

## When to Use

- Before committing hooks changes
- Security audit of existing hooks
- Quality gate in PR reviews
- Identifying improvement opportunities
- Learning security best practices

## Example Findings

**Security Issues Detected:**
- `eval` command (arbitrary code execution)
- `rm -rf /` (system destruction)
- Command substitution without validation
- Piping wget/curl to bash
- Overly permissive permissions (chmod 777)

**Recommendations:**
- Add input validation with `[[ ]]` or `if` statements
- Use `set -euo pipefail` in bash scripts
- Use ${CLAUDE_PLUGIN_ROOT} for consistent paths
- Validate matcher regex patterns
- Ensure scripts exist and are executable

## Integration

Pair with other commands:
1. `/agent-builder:hooks:enhance` - Find issues
2. `/agent-builder:hooks:update` - Fix issues
3. `/agent-builder:hooks:migrate` - Apply migrations
4. Validate with hooks validation script
5. Test by triggering events

**Security First**: This command prioritizes security over all other quality factors.
