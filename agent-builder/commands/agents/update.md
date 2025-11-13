---
description: Update an existing Claude Code agent with interactive workflow
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
argument-hint: [agent-name]
model: claude-sonnet-4-5
---

# Update Existing Agent

Update the Claude Code agent named: **$1**

## Your Task

Follow this interactive workflow to update an existing agent:

### 1. **Locate the Agent**
- Search for the agent file in common locations:
  - `.claude/agents/$1.md` (project-level)
  - `~/.claude/agents/$1.md` (user-level)
  - Plugin directories: `*/agents/$1.md`
- If not found, search by pattern for similar names
- If $1 is empty, list available agents and ask user to specify

### 2. **Analyze Current State**
- Read the existing agent file
- Parse YAML frontmatter (name, description, tools, model)
- Analyze the agent body content
- Run validation script: `python3 agent-builder/skills/building-agents/scripts/validate-agent.py <path>`
- Identify potential issues or outdated patterns

### 3. **Present Current Configuration**
Show the user:
```
Current Agent: $1
Location: <path>
Description: <current description>
Tools: <current tools>
Model: <current model>
Status: <validation results>
```

### 4. **Interactive Update Menu**
Present options to the user:
```
What would you like to update?

1. Description (when to invoke, purpose)
2. Tools (add/remove tool permissions)
3. Model (haiku/sonnet/opus)
4. Capabilities section (what the agent can do)
5. Workflow section (step-by-step process)
6. Best practices & guidelines
7. Examples (add/update examples)
8. Apply security best practices
9. Modernize to latest patterns
10. Run full analysis and suggest improvements
11. Cancel (no changes)

Enter numbers (comma-separated) or 'all':
```

### 5. **Apply Updates**
Based on user selection:
- **Description**: Ask for new description, validate length (max 1024 chars)
- **Tools**: Show current tools, suggest minimal set, validate security
- **Model**: Explain trade-offs (speed/cost/capability)
- **Content sections**: Use Edit tool to update specific sections
- **Modernization**: Apply current best practices from building-agents skill
- **Analysis**: Run enhance-agent.py script if available

### 6. **Show Diff Preview**
Before applying:
- Show a clear diff of proposed changes
- Highlight what's being added/removed/modified
- Explain the impact of each change
- Ask for confirmation: "Apply these changes? (y/n)"

### 7. **Apply and Validate**
If user confirms:
- Apply changes using Edit or Write tool
- Run validation script again
- Verify YAML syntax is valid
- Check naming conventions
- Validate tool permissions

### 8. **Provide Summary**
After successful update:
```
✅ Agent updated successfully!

Changes made:
- <list of changes>

Location: <path>
Status: ✓ Valid

Next steps:
- Test the agent: Use Task tool to invoke it
- Review behavior: Ensure it works as expected
- Commit changes: git add <path> && git commit
```

## Update Strategies

### Quick Updates (Single Field)
```
/agent-builder:agents:update my-agent
> What would you like to update? 2 (tools)
> Current: Read, Grep, Glob
> Add tools: Write, Edit
> Confirm? y
✅ Tools updated
```

### Comprehensive Updates (Multiple Fields)
```
/agent-builder:agents:update my-agent
> What would you like to update? 1,2,4,7 (description, tools, capabilities, examples)
[Interactive prompts for each]
[Show combined diff]
> Confirm all changes? y
✅ Agent updated with 4 changes
```

### Automated Modernization
```
/agent-builder:agents:update my-agent
> What would you like to update? 9 (modernize)
[Analyzes agent against current best practices]
[Suggests improvements automatically]
[Shows diff of all modernization changes]
> Apply all improvements? y
✅ Agent modernized
```

## Security Considerations

When updating tool permissions:
1. **Removing tools**: Always safe, may break functionality
2. **Adding read-only tools**: Generally safe (Read, Grep, Glob, WebFetch, WebSearch)
3. **Adding write tools**: Requires justification (Write, Edit)
4. **Adding Bash**: Highest risk, validate all commands for injection vulnerabilities

Always ask: "Why does this agent need this tool?"

## Validation Checks

After updates, automatically verify:
- [ ] YAML frontmatter is valid
- [ ] Name follows conventions (lowercase-hyphens, max 64 chars)
- [ ] Description is clear and actionable (max 1024 chars)
- [ ] Tools are minimal and necessary
- [ ] No security anti-patterns
- [ ] Content sections are complete
- [ ] Examples are present and helpful

## Error Handling

**If agent not found:**
- Search for similar names
- List available agents in common locations
- Ask user to specify correct name or path

**If validation fails after update:**
- Show validation errors clearly
- Offer to fix common issues automatically
- Allow user to revert changes
- Provide guidance on fixing errors manually

**If file is read-only or locked:**
- Check file permissions
- Inform user of permission issues
- Suggest solutions (chmod, sudo, different location)

## Integration with building-agents Skill

This command leverages the `building-agents` skill for:
- Schema validation and best practices
- Template structures and patterns
- Security guidelines
- Tool permission strategies
- Naming conventions and standards

The skill auto-invokes when you run this command to provide expert guidance.

## Related Commands

- `/agent-builder:agents:new [name]` - Create a new agent
- `/agent-builder:agents:enhance [name]` - AI-powered enhancement suggestions
- `/agent-builder:agents:audit` - Audit all agents for issues
- `/agent-builder:agents:compare [agent1] [agent2]` - Compare two agents

---

**Note**: This command creates an interactive, user-friendly workflow for updating agents. It prevents breaking changes by showing diffs and requiring confirmation.
