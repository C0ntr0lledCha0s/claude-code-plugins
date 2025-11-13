#!/usr/bin/env python3
"""
Agent Generator Script
Creates a new Claude Code agent from template with interactive prompts
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime


def validate_name(name):
    """Validate agent name follows conventions"""
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, "Name must be lowercase letters, numbers, and hyphens only"
    if len(name) > 64:
        return False, f"Name too long ({len(name)} chars, max 64)"
    if '_' in name:
        return False, "Use hyphens instead of underscores"
    return True, "Valid"


def prompt_user(question, default=None, required=True):
    """Prompt user for input"""
    if default:
        prompt = f"{question} [{default}]: "
    else:
        prompt = f"{question}: "

    while True:
        response = input(prompt).strip()
        if not response and default:
            return default
        if not response and not required:
            return ""
        if response or not required:
            return response
        print("This field is required. Please provide a value.")


def select_tools():
    """Interactive tool selection"""
    print("\n📋 Tool Selection")
    print("Select tools this agent needs (space-separated numbers, or 'all' for everything):")
    print("  1. Read")
    print("  2. Write")
    print("  3. Edit")
    print("  4. Grep")
    print("  5. Glob")
    print("  6. Bash")
    print("  7. WebFetch")
    print("  8. WebSearch")
    print("  9. All tools (omit tools field)")

    choice = input("\nYour selection: ").strip()

    if choice == '9' or choice.lower() == 'all':
        return None  # No tools field = inherit all

    tool_map = {
        '1': 'Read', '2': 'Write', '3': 'Edit',
        '4': 'Grep', '5': 'Glob', '6': 'Bash',
        '7': 'WebFetch', '8': 'WebSearch'
    }

    selected = []
    for num in choice.split():
        if num in tool_map:
            selected.append(tool_map[num])

    if not selected:
        # Default minimal set
        return "Read, Grep, Glob"

    return ", ".join(selected)


def select_model():
    """Interactive model selection"""
    print("\n🤖 Model Selection")
    print("  1. haiku  - Fast, simple tasks")
    print("  2. sonnet - Default, balanced (recommended)")
    print("  3. opus   - Complex reasoning")
    print("  4. inherit - Use parent model")

    choice = input("\nYour selection [2]: ").strip() or '2'

    model_map = {'1': 'haiku', '2': 'sonnet', '3': 'opus', '4': 'inherit'}
    return model_map.get(choice, 'sonnet')


def generate_agent(name, description, tools, model, purpose, capabilities_array, capabilities, workflow):
    """Generate agent markdown content"""

    # Build frontmatter
    frontmatter = [
        "---",
        f"name: {name}",
        f"description: {description}"
    ]

    # Add capabilities array to frontmatter
    if capabilities_array:
        import json
        frontmatter.append(f"capabilities: {json.dumps(capabilities_array)}")

    if tools:
        frontmatter.append(f"tools: {tools}")

    if model != 'inherit':
        frontmatter.append(f"model: {model}")

    frontmatter.append("---")

    # Build body
    agent_name_title = ' '.join(word.capitalize() for word in name.split('-'))

    body = f"""
# {agent_name_title} Agent

You are {purpose}

## Your Capabilities

{capabilities}

## Your Workflow

When invoked, follow these steps:

{workflow}

## Best Practices & Guidelines

- Provide clear, specific outputs
- Document your reasoning and decisions
- Follow established conventions and best practices
- Ask for clarification when requirements are ambiguous
- Verify your work before completing

## Examples

### Example 1: [Common Scenario]
When the user asks [specific request]:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected outcome: [Description]

### Example 2: [Another Scenario]
When handling [situation]:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected outcome: [Description]

## Important Reminders

- Focus on quality and accuracy
- Be thorough but concise
- Communicate clearly
- Provide actionable results
"""

    return '\n'.join(frontmatter) + body


def main():
    print("=" * 70)
    print("🤖 CLAUDE CODE AGENT GENERATOR")
    print("=" * 70)
    print()

    # Get agent name
    while True:
        name = prompt_user("Agent name (lowercase-hyphens, e.g., 'code-reviewer')")
        valid, message = validate_name(name)
        if valid:
            break
        print(f"❌ {message}")

    # Get description
    print("\n📝 Description (max 1024 chars)")
    print("Focus on WHEN to invoke this agent and what it does.")
    description = prompt_user("Description")

    if len(description) > 1024:
        print(f"⚠️  Description is {len(description)} chars, truncating to 1024...")
        description = description[:1024]

    # Get tools
    tools = select_tools()

    # Get model
    model = select_model()

    # Get purpose
    print("\n🎯 Agent Purpose")
    print("Describe the agent's role in one sentence (e.g., 'an expert code reviewer...')")
    purpose = prompt_user("Purpose")

    # Get capabilities array (for frontmatter)
    print("\n💪 Agent Capabilities (for frontmatter)")
    print("List specialized tasks this agent can perform (kebab-case).")
    print("Examples: analyze-code, review-security, generate-tests")
    print("Enter capabilities one per line, blank line when done.")
    capabilities_array = []
    count = 1
    while True:
        cap = input(f"  {count}. ").strip()
        if not cap:
            break
        # Convert to kebab-case if not already
        cap_kebab = re.sub(r'[^a-z0-9-]+', '-', cap.lower()).strip('-')
        capabilities_array.append(cap_kebab)
        count += 1

    if not capabilities_array:
        # Default capability based on name
        capabilities_array = [name]

    # Get capabilities description (for body)
    print("\n💪 Agent Capabilities Details (for documentation)")
    print("List key capabilities with descriptions, one per line. Enter blank line when done.")
    capabilities_list = []
    count = 1
    while True:
        cap = input(f"  {count}. ").strip()
        if not cap:
            break
        capabilities_list.append(f"{count}. **{cap.split(':')[0] if ':' in cap else f'Capability {count}'}**: {cap}")
        count += 1

    capabilities = '\n'.join(capabilities_list) if capabilities_list else "1. **Primary capability**: [Describe here]"

    # Get workflow
    print("\n🔄 Agent Workflow")
    print("List workflow steps, one per line. Enter blank line when done.")
    workflow_list = []
    count = 1
    while True:
        step = input(f"  {count}. ").strip()
        if not step:
            break
        workflow_list.append(f"{count}. **{step.split(':')[0] if ':' in step else f'Step {count}'}**: {step}")
        count += 1

    workflow = '\n'.join(workflow_list) if workflow_list else "1. **Analyze**: Understand the request\n2. **Execute**: Perform the task\n3. **Verify**: Check the results"

    # Generate agent content
    content = generate_agent(name, description, tools, model, purpose, capabilities_array, capabilities, workflow)

    # Determine output path
    output_dir = Path.cwd() / '.claude' / 'agents'
    if not output_dir.exists():
        output_dir = Path.cwd() / 'agents'

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{name}.md"

    # Preview
    print("\n" + "=" * 70)
    print("📄 GENERATED AGENT PREVIEW")
    print("=" * 70)
    print(content[:500] + "..." if len(content) > 500 else content)
    print("=" * 70)

    # Confirm
    save = prompt_user(f"\n💾 Save to {output_file}? (y/n)", "y")

    if save.lower() == 'y':
        output_file.write_text(content)
        print(f"\n✅ Agent created: {output_file}")
        print(f"\n📝 Next steps:")
        print(f"   1. Review and customize {output_file}")
        print(f"   2. Add examples and guidelines")
        print(f"   3. Validate: python validate-agent.py {output_file}")
        print(f"   4. Test invocation via Task tool")
    else:
        print("\n❌ Cancelled. Agent not saved.")

    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
