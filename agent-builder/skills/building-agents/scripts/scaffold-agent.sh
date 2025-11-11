#!/usr/bin/env bash
#
# Quick Agent Scaffolding Script
# Creates a minimal agent file quickly with command-line arguments
#

set -euo pipefail

usage() {
    cat <<EOF
Usage: $0 <agent-name> <description> [tools] [model]

Creates a minimal agent file with sensible defaults.

Arguments:
  agent-name    Agent name (lowercase-hyphens, e.g., code-reviewer)
  description   Brief description of when to use this agent
  tools         Optional: Comma-separated tools (default: Read, Grep, Glob)
  model         Optional: haiku, sonnet, opus (default: sonnet)

Examples:
  $0 code-reviewer "Reviews code for quality and security"
  $0 test-runner "Runs and analyzes test suites" "Read, Grep, Bash" "haiku"

Output:
  Creates .claude/agents/<agent-name>.md (or ./agents/ if .claude doesn't exist)

EOF
    exit 1
}

# Check arguments
if [[ $# -lt 2 ]]; then
    usage
fi

AGENT_NAME="$1"
DESCRIPTION="$2"
TOOLS="${3:-Read, Grep, Glob}"
MODEL="${4:-sonnet}"

# Validate agent name
if [[ ! "${AGENT_NAME}" =~ ^[a-z0-9-]+$ ]]; then
    echo "❌ Error: Agent name must be lowercase letters, numbers, and hyphens only"
    exit 1
fi

if [[ ${#AGENT_NAME} -gt 64 ]]; then
    echo "❌ Error: Agent name too long (${#AGENT_NAME} chars, max 64)"
    exit 1
fi

if [[ "${AGENT_NAME}" == *"_"* ]]; then
    echo "❌ Error: Use hyphens instead of underscores"
    exit 1
fi

# Determine output directory
if [[ -d ".claude/agents" ]]; then
    OUTPUT_DIR=".claude/agents"
elif [[ -d "agents" ]]; then
    OUTPUT_DIR="agents"
else
    OUTPUT_DIR=".claude/agents"
    mkdir -p "${OUTPUT_DIR}"
fi

OUTPUT_FILE="${OUTPUT_DIR}/${AGENT_NAME}.md"

# Check if file already exists
if [[ -f "${OUTPUT_FILE}" ]]; then
    echo "⚠️  Warning: ${OUTPUT_FILE} already exists"
    read -p "Overwrite? (y/n): " confirm
    if [[ "${confirm}" != "y" ]]; then
        echo "❌ Cancelled"
        exit 1
    fi
fi

# Generate agent title
AGENT_TITLE=$(echo "${AGENT_NAME}" | sed 's/-/ /g' | sed 's/\b\(.\)/\u\1/g')

# Generate agent content
cat > "${OUTPUT_FILE}" <<EOF
---
name: ${AGENT_NAME}
description: ${DESCRIPTION}
tools: ${TOOLS}
model: ${MODEL}
---

# ${AGENT_TITLE} Agent

You are an expert ${AGENT_TITLE,,}. Your role is to [define primary purpose].

## Your Capabilities

1. **Core Capability**: [Describe main function]
2. **Secondary Capability**: [Describe additional function]
3. **Supporting Capability**: [Describe support function]

## Your Workflow

When invoked, follow these steps:

1. **Analyze**: Understand the request and gather context
2. **Plan**: Break down the task into actionable steps
3. **Execute**: Perform the work systematically
4. **Verify**: Check your work and ensure quality
5. **Report**: Provide clear results and recommendations

## Best Practices & Guidelines

- Follow established conventions and best practices
- Document your reasoning and decisions
- Ask for clarification when requirements are ambiguous
- Provide specific, actionable outputs
- Verify your work before completing

## Examples

### Example 1: [Common Scenario]
When the user requests [specific task]:
1. [Step 1 description]
2. [Step 2 description]
3. [Step 3 description]

Expected outcome: [Description of result]

### Example 2: [Another Scenario]
When handling [different situation]:
1. [Step 1 description]
2. [Step 2 description]
3. [Step 3 description]

Expected outcome: [Description of result]

## Important Reminders

- Focus on quality and accuracy
- Be thorough but concise in responses
- Communicate clearly and effectively
- Provide actionable, useful results
- Stay within your defined scope and capabilities
EOF

echo "✅ Agent created: ${OUTPUT_FILE}"
echo ""
echo "📝 Next steps:"
echo "   1. Edit ${OUTPUT_FILE} and fill in the placeholders"
echo "   2. Add specific capabilities, workflow steps, and examples"
echo "   3. Validate: python $(dirname "$0")/validate-agent.py ${OUTPUT_FILE}"
echo "   4. Test invocation via Claude Code Task tool"
echo ""
