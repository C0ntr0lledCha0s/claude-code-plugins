---
name: skill-name
description: Brief description of what this skill does and when Claude should automatically use it (be very specific about triggers)
version: 1.0.0
allowed-tools: Read, Grep, Glob
---

# Skill Name

You are an expert in [domain]. This skill provides [type of expertise] to enhance Claude's capabilities.

## Your Capabilities

1. **Capability 1**: Description of what you can do
2. **Capability 2**: Description of what you can do
3. **Capability 3**: Description of what you can do

## When to Use This Skill

Claude should automatically invoke this skill when:
- The user asks about [specific topic or domain]
- The task involves [specific type of work]
- The conversation requires [specific expertise]
- Files matching [specific patterns] are encountered

## How to Use This Skill

When this skill is activated:

1. **Access Resources**: Use `{baseDir}` to reference files in this skill directory
   - Scripts: `{baseDir}/scripts/`
   - Documentation: `{baseDir}/references/`
   - Templates: `{baseDir}/assets/`

2. **Progressive Disclosure**: Start with core expertise, discover resources as needed

3. **Provide Context**: Offer relevant information and guidance automatically

## Resources Available

### Scripts
Located in `{baseDir}/scripts/`:
- **helper.py**: Description of script functionality
- **processor.sh**: Description of script functionality

Usage example:
```bash
python {baseDir}/scripts/helper.py --input data.csv
```

### References
Located in `{baseDir}/references/`:
- **guide.md**: Comprehensive guide to [topic]
- **api-reference.md**: API documentation and examples

### Assets
Located in `{baseDir}/assets/`:
- **template.json**: Template for [use case]
- **config.yaml**: Configuration template

## Examples

### Example 1: [Common Scenario]
When the user [specific action or request]:

1. Automatically recognize the need for this skill
2. [Step-by-step approach]
3. Reference relevant documentation from `{baseDir}/references/`
4. Provide actionable guidance

### Example 2: [Another Scenario]
When encountering [specific situation]:

1. Invoke this skill automatically
2. [Step-by-step approach]
3. Use scripts from `{baseDir}/scripts/` if needed
4. Deliver results with context

## Best Practices

- Always [important guideline]
- Prefer [recommended approach]
- Avoid [what to avoid]
- Consider [important considerations]

## Important Notes

- This skill is automatically invoked by Claude when relevant
- Resources are discovered progressively as needed
- Use `{baseDir}` variable to reference skill resources
- Scripts should be executable and well-documented
