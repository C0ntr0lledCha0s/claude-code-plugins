# Using Plugins in Remote/Web Environments

This guide explains how to use Claude Code plugins effectively in remote environments like Claude Code on the web.

## Quick Reference

| Feature | Local | Remote (Web) | Alternative in Remote |
|---------|-------|--------------|----------------------|
| **Agents (@mention)** | ✅ `@investigator` | ⚠️ Limited | Use skills/commands |
| **Skills (auto-invoke)** | ✅ Works | ✅ Works | Primary method |
| **Commands (/slash)** | ✅ Works | ✅ Works | Explicit invocation |
| **Task tool** | Built-in only | Built-in only | `Explore`, `Plan` |
| **GitHub CLI** | ✅ Works | ⚠️ Needs GH_TOKEN | Set env variable |

## Understanding the Limitation

### Why @mention Agents May Not Work

Custom agents defined in plugins (like `@investigator`, `@workflow-orchestrator`) require:
1. Plugin loader to register them
2. Agent discovery mechanism to index them
3. @mention parsing to invoke them

In remote environments, these mechanisms may not fully initialize.

### What Always Works

1. **Skills** - Auto-invoke based on context (description matching)
2. **Commands** - Explicitly invoked with `/command-name`
3. **Built-in Task agents** - `Explore`, `Plan`, `general-purpose`

## Plugin Capabilities Mapping

### research-agent Plugin

| Agent | Skill Equivalent | Command Equivalent |
|-------|------------------|-------------------|
| `@investigator` | `investigating-codebases` | `/investigate <target>` |
| - | `researching-best-practices` | `/research <topic>` |
| - | `analyzing-patterns` | `/best-practice <area>` |

**Usage in Remote:**
```bash
# Instead of: @investigator find auth implementation
# Use:
/investigate user authentication

# Or just ask - skills auto-invoke:
"How does authentication work in this codebase?"
```

### github-workflows Plugin

| Agent | Skill Equivalent | Command Equivalent |
|-------|------------------|-------------------|
| `@workflow-orchestrator` | `managing-commits` | `/commit-smart` |
| `@pr-reviewer` | `reviewing-pull-requests` | `/pr-review-request` |
| `@issue-manager` | `triaging-issues` | `/issue-triage` |
| `@release-manager` | - | `/release-prepare` |

**Usage in Remote:**
```bash
# Instead of: @workflow-orchestrator help with feature workflow
# Use:
/commit-smart
/pr-review-request

# Or ask directly - skills auto-invoke:
"Help me create a commit for these changes"
```

### self-improvement Plugin

| Agent | Skill Equivalent | Command Equivalent |
|-------|------------------|-------------------|
| `@self-critic` | `analyzing-response-quality` | `/quality-check` |
| - | `suggesting-improvements` | `/review-my-work` |

### agent-builder Plugin

| Agent | Skill Equivalent | Command Equivalent |
|-------|------------------|-------------------|
| `@meta-architect` | `building-agents` | `/agent-builder:agents:new` |
| - | `building-skills` | `/agent-builder:skills:new` |
| - | `building-commands` | `/agent-builder:commands:new` |
| - | `building-hooks` | `/agent-builder:hooks:new` |

## GitHub CLI in Remote Environments

The github-workflows plugin uses `gh` CLI extensively. In remote environments:

### Option 1: Set GH_TOKEN Environment Variable

```bash
export GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

Create a token at https://github.com/settings/tokens with scopes:
- `repo` - Issues, PRs, commits
- `read:project` - GitHub Projects v2
- `read:org` - Organization projects

### Option 2: Use gh auth with Token

```bash
echo "ghp_your_token" | gh auth login --with-token
```

### What Works Without gh

Even without GitHub CLI, these features work:
- `/commit-smart` - Commit message generation
- Branch naming conventions
- Git workflow guidance
- Code analysis and patterns

## SessionStart Hook

The repository includes a SessionStart hook that:
1. Checks environment (local vs remote)
2. Installs npm dependencies if needed
3. Advertises available agents and alternatives

Check hook output in: `.claude/hooks/session-start-debug.log`

## Troubleshooting

### "Agent not found" or @mention not working

**Cause:** Agent not registered in remote environment

**Solution:** Use the equivalent command instead:
- `@investigator` → `/investigate`
- `@workflow-orchestrator` → `/commit-smart` or `/workflow-status`
- `@self-critic` → `/quality-check`

### Skills not auto-invoking

**Cause:** Description may not match your query

**Solution:** Be explicit with your request:
- Instead of "check code" → "analyze code quality and suggest improvements"
- Instead of "commit" → "help me create a conventional commit message"

### GitHub operations failing

**Cause:** gh CLI not authenticated

**Solution:**
1. Set `GH_TOKEN` environment variable
2. Or ask Claude to help with the git operations directly

### Commands not available

**Cause:** Plugin may not be fully loaded

**Solution:**
1. Check `.claude/settings.json` has `enabledPlugins` configured
2. Verify plugin paths are correct
3. Check SessionStart hook ran successfully

## Best Practices for Remote

1. **Prefer Commands over Agents** - More reliable invocation
2. **Let Skills Auto-Invoke** - Just describe what you need
3. **Use Task tool wisely** - `Explore` for codebase research
4. **Set GH_TOKEN early** - If you need GitHub operations
5. **Check hook logs** - For debugging initialization issues

## Architecture Decision

The plugins are designed with a "graceful degradation" pattern:

```
Agent (highest capability)
  ↓ falls back to
Skill (auto-invokes on context)
  ↓ provides explicit
Command (user-triggered)
```

This ensures functionality is always available, even when some features are limited.

## Contributing

If you find a scenario where agents should work but don't, please:
1. Check the SessionStart debug log
2. Note which mechanism failed
3. Open an issue with reproduction steps

---

**Remember:** In remote environments, skills and commands are your primary tools. Agents are a bonus when available!
