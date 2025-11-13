---
description: Compare two commands side-by-side to see differences
allowed-tools: Read, Bash
argument-hint: '[command1] [command2]'
model: claude-haiku-4-5
---

# Compare Commands

Compare two commands side-by-side: **$1** vs **$2**

## Your Task

Run the command comparison tool to analyze differences between two command files.

## Arguments

- `$1` - First command name (without .md extension)
- `$2` - Second command name (without .md extension)

## Workflow

1. **Invoke Script**: Run the compare script
   ```bash
   python3 {baseDir}/../scripts/compare-commands.py $1 $2
   ```

2. **Script Compares**:
   - **Frontmatter**: Side-by-side field comparison
   - **Structure**: Document headings hierarchy
   - **Metrics**: Word count, headings, code blocks, list items
   - **Content**: Unified diff of body text

3. **Script Outputs**:
   - Field-by-field comparison table
   - Structural differences
   - Metric comparisons with differences
   - Line-by-line content diff (colored)
   - Similarity score

4. **Present Results**: Show the user the comparison report

## Example Usage

```
/agent-builder:commands:compare new-agent create-agent
```

## Comparison Sections

### 1. Frontmatter Comparison
```
Field                Command1                  Command2
--------------------------------------------------------------------
✓ description        Creates a new agent       Creates a new agent
⚠️ model             claude-haiku-4-5          claude-sonnet-4-5
✓ allowed-tools      Read, Write, Edit         Read, Write, Edit
```

### 2. Structure Comparison (Headings)
Shows the document outline for both commands:
- First-level headings
- Second-level headings (indented)
- Third-level headings (indented further)

### 3. Metrics Comparison
```
Metric               Command1          Command2          Difference
--------------------------------------------------------------------
word_count           234               456               +222
heading_count        5                 7                 +2
code_blocks          2                 3                 +1
list_items           8                 12                +4
```

### 4. Content Diff
Unified diff format with color coding:
- Green lines: Added in command2
- Red lines: Removed from command1
- Blue lines: Change location markers

### 5. Summary
- Frontmatter status: Identical or Different
- Content similarity: Percentage match

## Use Cases

1. **Reviewing Changes**: Compare before/after updates
2. **Understanding Variations**: See how similar commands differ
3. **Template Evaluation**: Check if new command follows pattern of existing ones
4. **Merge Decisions**: Decide if two commands should be combined
5. **Migration Verification**: Confirm migration changed only intended fields

## Comparing Versions

To compare a command before and after updates:
```bash
# Compare current version with backup
/agent-builder:commands:compare my-command my-command.md.bak
```

## If Script Not Found

Script path: `agent-builder/skills/building-commands/scripts/compare-commands.py`

## Related Commands

- `/agent-builder:commands:update <name>` - Update a command
- `/agent-builder:commands:enhance <name>` - Get quality score
- `/agent-builder:commands:audit` - Bulk validation
