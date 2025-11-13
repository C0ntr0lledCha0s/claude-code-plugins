---
description: Analyze a command's quality and get AI-powered improvement suggestions
allowed-tools: Read, Bash
argument-hint: [command-name]
model: claude-haiku-4-5
---

# Enhance Command

Analyze and score the command named: **$1**

## Your Task

Run the command enhancement analyzer to get quality scores and recommendations.

## Arguments

- `$1` - The command name (without .md extension)

## Workflow

1. **Invoke Script**: Run the enhance-command.py script
   ```bash
   python3 {baseDir}/../scripts/enhance-command.py $1
   ```

2. **Script Analyzes**:
   - Schema compliance (naming, required fields)
   - Model configuration (version alias validation)
   - Argument handling (hint, documentation)
   - Security (Bash access, validation, dangerous patterns)
   - Content quality (examples, workflow, documentation)
   - Maintainability (structure, formatting)

3. **Script Returns**:
   - Overall score (0-10)
   - Detailed scores for each category
   - Specific findings (✅/⚠️/❌)
   - Prioritized recommendations (🔴 CRITICAL, 🟡 HIGH, 🟢 MEDIUM/LOW)
   - Next steps

4. **Present Results**: Show the user their command's score and recommendations

## Example Usage

```
/agent-builder:commands:enhance new-agent
```

## Scoring Categories

1. **Schema Compliance** (10 points)
   - Valid filename format
   - Action-oriented naming
   - Required fields present
   - Field value lengths

2. **Model Configuration** (10 points)
   - CRITICAL: No short aliases (haiku/sonnet/opus)
   - Valid version alias or full ID format
   - Starts with 'claude-'

3. **Argument Handling** (10 points)
   - argument-hint present if uses $1/$2/$ARGUMENTS
   - Brackets in hint
   - ## Arguments section documenting parameters

4. **Security** (10 points)
   - Bash access validated
   - No command injection patterns
   - No dangerous operations (rm -rf, eval)
   - No hardcoded secrets

5. **Content Quality** (10 points)
   - Has workflow/steps section
   - Has usage/examples section
   - Has arguments/parameters section
   - Multiple examples
   - Appropriate length

6. **Maintainability** (10 points)
   - Clear section headings
   - Uses lists for instructions
   - Code blocks for examples
   - Good formatting (bold, inline code)
   - Reasonable line lengths

## What to Do With Results

- **Score ≥ 8**: Excellent! Only minor improvements possible
- **Score 6-7**: Good command, some improvements recommended
- **Score < 6**: Needs improvement, address findings

Use `/agent-builder:commands:update <command-name>` to apply improvements.

## If Script Not Found

Script path: `agent-builder/skills/building-commands/scripts/enhance-command.py`
