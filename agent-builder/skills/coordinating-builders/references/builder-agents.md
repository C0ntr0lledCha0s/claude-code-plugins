# Builder Agents Reference

Quick reference for builder agents in the agent-builder plugin.

## agent-builder

**Purpose**: Create and maintain agent `.md` files

**Capabilities**:
- create-agents
- update-agents
- audit-agents
- enhance-agents
- migrate-agents
- compare-agents
- validate-agents

**Tools**: Read, Write, Edit, Grep, Glob, Bash

**Invocation Examples**:
```
Task → agent-builder: "Create agent 'code-reviewer' for code quality analysis"
Task → agent-builder: "Update agent 'test-runner' to add coverage capabilities"
Task → agent-builder: "Audit all agents in this project"
```

## skill-builder

**Purpose**: Create and maintain skill directories with SKILL.md

**Capabilities**:
- create-skills
- update-skills
- audit-skills
- validate-skills

**Tools**: Read, Write, Edit, Grep, Glob, Bash

**Invocation Examples**:
```
Task → skill-builder: "Create skill 'reviewing-code' for code review expertise"
Task → skill-builder: "Update skill 'building-agents' with new validation rules"
```

## command-builder

**Purpose**: Create and maintain slash command `.md` files

**Capabilities**:
- create-commands
- update-commands
- audit-commands
- validate-commands

**Tools**: Read, Write, Edit, Grep, Glob, Bash

**Invocation Examples**:
```
Task → command-builder: "Create command 'review' for code review workflow"
Task → command-builder: "Update command 'audit' to add parallel execution"
```

## hook-builder

**Purpose**: Create and maintain hooks.json (security-focused)

**Capabilities**:
- create-hooks
- update-hooks
- audit-hooks
- validate-hooks

**Tools**: Read, Write, Edit, Grep, Glob, Bash

**Invocation Examples**:
```
Task → hook-builder: "Create PreToolUse hook to validate Write operations"
Task → hook-builder: "Audit all hooks for security issues"
```

## plugin-builder

**Purpose**: Create plugin structures and manifests

**Capabilities**:
- create-plugin-structure
- generate-plugin-json
- update-marketplace-json
- generate-readme
- validate-plugin

**Tools**: Read, Write, Edit, Grep, Glob, Bash

**Invocation Examples**:
```
Task → plugin-builder: "Create plugin structure 'testing' with 2 agents, 1 command"
Task → plugin-builder: "Finalize README and register in marketplace.json"
Task → plugin-builder: "Validate plugin 'code-review'"
```

## Execution Order for Plugin Creation

```
1. plugin-builder (structure)    ← Must be first
2. agent-builder (agents)        ← Parallel
   skill-builder (skills)        ← Parallel
   command-builder (commands)    ← Parallel
   hook-builder (hooks)          ← Parallel
3. plugin-builder (finalize)     ← Must be last
```
