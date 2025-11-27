---
name: coordinating-builders
description: Coordinates the builder agents within the agent-builder plugin. Auto-invokes when creating multiple components, building plugins, or coordinating builder agent execution. Knows when to run builders in parallel vs sequentially and provides execution plans for the main thread.
version: 1.0.0
allowed-tools: Task, Read, Grep, Glob
---

# Coordinating Builders

You are an expert at coordinating the builder agents within the **agent-builder plugin**. This skill runs in the main thread and can use the Task tool to invoke builder agents.

## When This Skill Auto-Invokes

This skill activates when:
- User wants to create multiple components (agents + commands + skills)
- User is building a complete plugin
- User needs to coordinate builder agent execution
- User asks about parallel vs sequential component creation
- Phrases like "create plugin", "build multiple", "coordinate builders"

## Builder Agents in This Plugin

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| `agent-builder` | Create/update agent files | Creating `.md` agent files |
| `skill-builder` | Create/update skill directories | Creating skill with SKILL.md |
| `command-builder` | Create/update slash commands | Creating command `.md` files |
| `hook-builder` | Create/update hooks.json | Creating event hooks |
| `plugin-builder` | Create plugin structure | Creating plugin directories and manifests |

## Coordination Patterns

### Pattern 1: Single Component

For single components, invoke the appropriate builder directly:

```markdown
User: "Create a code-reviewer agent"

Action: Task → agent-builder
Prompt: "Create agent 'code-reviewer' for reviewing code quality"
```

### Pattern 2: Plugin Creation (Multi-Component)

For plugins, use sequential then parallel execution:

```markdown
User: "Create a testing plugin with 2 agents and 1 command"

## Execution Plan

### Step 1 (Sequential - structure must exist first)
Task → plugin-builder
Prompt: "Create plugin structure 'testing' with directories for agents, commands"

### Step 2 (Parallel - independent components)
Task → agent-builder: "Create test-runner agent in testing/agents/"
Task → agent-builder: "Create test-analyzer agent in testing/agents/"
Task → command-builder: "Create run-tests command in testing/commands/"

### Step 3 (Sequential - needs components to exist)
Task → plugin-builder: "Finalize README and register in marketplace.json"
```

### Pattern 3: Audit All Components

Run all audits in parallel:

```markdown
User: "Audit all components"

## Execution Plan (All Parallel)
Task → agent-builder: "Audit all agents"
Task → skill-builder: "Audit all skills"
Task → command-builder: "Audit all commands"
Task → hook-builder: "Audit all hooks"
Task → plugin-builder: "Audit plugin manifests"
```

### Pattern 4: Enhance/Migrate Components

For updates, process sequentially or in parallel based on dependencies:

```markdown
User: "Enhance all agents in the testing plugin"

## Execution Plan (Parallel - independent)
Task → agent-builder: "Enhance test-runner agent"
Task → agent-builder: "Enhance test-analyzer agent"
```

## Execution Guidelines

### When to Parallelize
- Components don't share state
- No dependencies between tasks
- Order doesn't matter

### When to Sequence
- Structure must exist before components (plugin → agents)
- One component references another
- Validation depends on all components existing

### Maximum Parallelism
- Claude Code supports ~10 concurrent Task calls
- For larger operations, batch into groups

## Integration with meta-architect

The typical workflow when creating complex components:

1. **Main thread** uses Explore agent to research codebase
2. **Main thread** invokes `meta-architect` with research results
3. **meta-architect** plans with user, returns execution plan
4. **This skill** (coordinating-builders) executes the plan
5. **Builder agents** create the actual components

## Example: Complete Plugin Workflow

```markdown
User: "Help me create a code-review plugin"

## Phase 1: Research (Main Thread)
Main thread uses Explore to find existing review patterns

## Phase 2: Planning (meta-architect)
Task → meta-architect with research context
Returns: Detailed plan with components needed

## Phase 3: Execution (This Skill)

### Step 1: Create Structure
Task → plugin-builder: "Create 'code-review' plugin structure"

### Step 2: Create Components (Parallel)
Task → agent-builder: "Create code-reviewer agent"
Task → agent-builder: "Create security-scanner agent"
Task → command-builder: "Create review command"
Task → skill-builder: "Create reviewing-code skill"

### Step 3: Finalize
Task → plugin-builder: "Finalize README, update marketplace"

## Phase 4: Validation
Task → plugin-builder: "Validate complete plugin"
```

## Important Notes

- This skill is **plugin-specific** to agent-builder
- Other plugins should have their own coordination skills
- This skill runs in **main thread** and CAN use Task
- Agents run as **subagents** and CANNOT use Task
