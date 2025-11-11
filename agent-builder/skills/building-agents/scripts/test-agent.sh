#!/usr/bin/env bash
#
# Agent Testing Script
# Tests that an agent file is valid and can be loaded
#

set -euo pipefail

usage() {
    cat <<EOF
Usage: $0 <agent-file.md>

Tests an agent file for common issues:
  - Valid YAML frontmatter
  - Required fields present
  - Naming conventions
  - File structure
  - Basic content checks

Example:
  $0 .claude/agents/code-reviewer.md

EOF
    exit 1
}

if [[ $# -lt 1 ]]; then
    usage
fi

AGENT_FILE="$1"

if [[ ! -f "${AGENT_FILE}" ]]; then
    echo "❌ Error: File not found: ${AGENT_FILE}"
    exit 1
fi

echo "🧪 Testing agent: ${AGENT_FILE}"
echo ""

# Test 1: Run validation script
echo "Test 1: Schema validation..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if python3 "${SCRIPT_DIR}/validate-agent.py" "${AGENT_FILE}"; then
    echo "✅ Schema validation passed"
else
    echo "❌ Schema validation failed"
    exit 1
fi

echo ""

# Test 2: Check for common content issues
echo "Test 2: Content quality checks..."

CONTENT=$(cat "${AGENT_FILE}")

# Check for placeholder text
if echo "${CONTENT}" | grep -q "\[.*\]"; then
    echo "⚠️  Warning: Found placeholder text in brackets [...]"
    echo "   Please replace placeholders with actual content"
fi

# Check for minimum body length
BODY_LINES=$(echo "${CONTENT}" | tail -n +10 | wc -l)
if [[ ${BODY_LINES} -lt 20 ]]; then
    echo "⚠️  Warning: Agent body is very short (${BODY_LINES} lines)"
    echo "   Consider adding more detail, examples, and guidelines"
fi

# Check for key sections
if ! echo "${CONTENT}" | grep -qi "## Your Capabilities\|## Capabilities"; then
    echo "⚠️  Warning: Missing 'Capabilities' section"
fi

if ! echo "${CONTENT}" | grep -qi "## Your Workflow\|## Workflow"; then
    echo "⚠️  Warning: Missing 'Workflow' section"
fi

if ! echo "${CONTENT}" | grep -qi "## Example"; then
    echo "⚠️  Warning: Missing 'Examples' section"
fi

echo "✅ Content quality checks complete"
echo ""

# Test 3: Check agent can be read
echo "Test 3: File readability..."
if [[ -r "${AGENT_FILE}" ]]; then
    echo "✅ File is readable"
else
    echo "❌ File is not readable"
    exit 1
fi

echo ""

# Summary
echo "=" * 50
echo "✅ All tests passed for ${AGENT_FILE}"
echo ""
echo "🚀 Ready to use! Invoke with:"
echo "   Task tool: 'Use the $(basename ${AGENT_FILE%.md}) agent to...'"
echo ""
