#!/bin/bash
# Advertise available plugin agents and their alternatives
# This script outputs agent information to make Claude aware of available capabilities

# Output format for SessionStart hooks
output_with_message() {
  local message="$1"
  printf '{"decision": "approve", "reason": "%s"}\n' "$message" | tr -d '\r'
}

PLUGIN_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Build agent registry from plugin agents
build_agent_registry() {
  local agents_info=""

  # Find all agent markdown files
  for agent_file in "$PLUGIN_DIR"/*/agents/*.md; do
    if [[ -f "$agent_file" ]]; then
      # Extract agent name from frontmatter
      local name=$(grep -m1 "^name:" "$agent_file" 2>/dev/null | sed 's/name:[[:space:]]*//' | tr -d '"')
      local description=$(grep -m1 "^description:" "$agent_file" 2>/dev/null | sed 's/description:[[:space:]]*//' | tr -d '"' | cut -c1-100)
      local plugin=$(echo "$agent_file" | sed "s|$PLUGIN_DIR/||" | cut -d'/' -f1)

      if [[ -n "$name" ]]; then
        agents_info="${agents_info}[${plugin}] @${name}: ${description}... "
      fi
    fi
  done

  echo "$agents_info"
}

# Check if we're in remote environment
if [[ "${CLAUDE_CODE_REMOTE:-}" == "true" ]]; then
  # In remote: advertise alternatives
  AGENTS=$(build_agent_registry)

  if [[ -n "$AGENTS" ]]; then
    output_with_message "Agents available (use skills/commands in remote): ${AGENTS}"
  else
    output_with_message "Plugin environment ready"
  fi
else
  # Local: agents work via @mention
  output_with_message "Local environment - agents available via @mention"
fi
