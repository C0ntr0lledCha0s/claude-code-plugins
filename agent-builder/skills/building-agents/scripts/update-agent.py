#!/usr/bin/env python3
"""
Update Agent Script - Interactive agent updater with diff preview
Part of the agent-builder plugin for Claude Code
"""

import sys
import os
import re
import yaml
import difflib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

def find_agent(agent_name: str) -> Optional[Path]:
    """Find agent file in common locations."""
    search_paths = [
        Path(".claude/agents"),
        Path.home() / ".claude" / "agents",
        Path("."),  # Search in current directory and subdirs
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Direct match
        agent_file = search_path / f"{agent_name}.md"
        if agent_file.exists():
            return agent_file

        # Search in subdirectories
        for agent_file in search_path.rglob(f"{agent_name}.md"):
            if agent_file.parent.name == "agents":
                return agent_file

    return None

def parse_agent(file_path: Path) -> Tuple[Dict, str]:
    """Parse agent file into frontmatter and body."""
    content = file_path.read_text()

    # Extract YAML frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if not match:
        raise ValueError("Invalid agent file: missing YAML frontmatter")

    frontmatter_text, body = match.groups()
    frontmatter = yaml.safe_load(frontmatter_text)

    return frontmatter, body

def validate_agent_name(name: str) -> bool:
    """Validate agent name follows conventions."""
    if not name:
        return False
    if len(name) > 64:
        return False
    if not re.match(r'^[a-z0-9-]+$', name):
        return False
    return True

def show_current_config(agent_name: str, frontmatter: Dict, file_path: Path):
    """Display current agent configuration."""
    print(f"\n{'='*60}")
    print(f"Current Configuration: {agent_name}")
    print(f"{'='*60}")
    print(f"Location: {file_path}")
    print(f"Description: {frontmatter.get('description', 'N/A')}")
    print(f"Tools: {frontmatter.get('tools', 'inherit (all tools)')}")
    print(f"Model: {frontmatter.get('model', 'inherit')}")
    print(f"{'='*60}\n")

def interactive_menu() -> List[int]:
    """Show interactive update menu and get user choices."""
    print("What would you like to update?\n")
    options = [
        "Description (when to invoke, purpose)",
        "Tools (add/remove tool permissions)",
        "Model (haiku/sonnet/opus)",
        "Run validation and show recommendations",
        "Cancel (no changes)"
    ]

    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    print("\nEnter numbers (comma-separated) or 'all':")
    choice = input("> ").strip().lower()

    if choice == 'all':
        return list(range(1, len(options)))
    elif choice == str(len(options)) or choice == 'cancel':
        return []

    try:
        choices = [int(c.strip()) for c in choice.split(',')]
        return [c for c in choices if 1 <= c < len(options)]
    except ValueError:
        print("Invalid input. Please enter numbers separated by commas.")
        return []

def update_description(frontmatter: Dict) -> Dict:
    """Update agent description."""
    print(f"\nCurrent description: {frontmatter.get('description', 'N/A')}")
    print("\nEnter new description (max 1024 chars):")
    new_desc = input("> ").strip()

    if len(new_desc) > 1024:
        print("⚠️  Description too long, truncating to 1024 characters")
        new_desc = new_desc[:1024]

    if new_desc:
        frontmatter['description'] = new_desc
        print("✓ Description updated")

    return frontmatter

def update_tools(frontmatter: Dict) -> Dict:
    """Update agent tool permissions."""
    current_tools = frontmatter.get('tools', 'inherit (all tools)')
    print(f"\nCurrent tools: {current_tools}")

    print("\nCommon tool presets:")
    print("1. Read, Grep, Glob (read-only, safest)")
    print("2. Read, Write, Edit, Grep, Glob (file modification)")
    print("3. Read, Write, Edit, Grep, Glob, Bash (full access)")
    print("4. Read, Grep, Glob, WebFetch, WebSearch (web access)")
    print("5. Custom (enter your own)")
    print("6. Inherit (remove tools field, use all)")

    choice = input("Select preset (1-6): ").strip()

    tool_presets = {
        '1': 'Read, Grep, Glob',
        '2': 'Read, Write, Edit, Grep, Glob',
        '3': 'Read, Write, Edit, Grep, Glob, Bash',
        '4': 'Read, Grep, Glob, WebFetch, WebSearch',
    }

    if choice in tool_presets:
        frontmatter['tools'] = tool_presets[choice]
        print(f"✓ Tools updated to: {tool_presets[choice]}")
    elif choice == '5':
        custom = input("Enter tools (comma-separated): ").strip()
        if custom:
            frontmatter['tools'] = custom
            print(f"✓ Tools updated to: {custom}")
    elif choice == '6':
        if 'tools' in frontmatter:
            del frontmatter['tools']
        print("✓ Tools set to inherit (all tools)")

    # Security warning
    if 'tools' in frontmatter and 'Bash' in frontmatter['tools']:
        print("⚠️  Security Warning: Bash access requires input validation!")

    return frontmatter

def update_model(frontmatter: Dict) -> Dict:
    """Update agent model selection."""
    current_model = frontmatter.get('model', 'inherit')
    print(f"\nCurrent model: {current_model}")

    print("\nModel options:")
    print("1. haiku (fastest, cheapest, simple tasks)")
    print("2. sonnet (balanced, default for most tasks)")
    print("3. opus (most capable, complex reasoning)")
    print("4. claude-sonnet-4-5 (specific version)")
    print("5. inherit (remove model field, use parent's)")

    choice = input("Select model (1-5): ").strip()

    models = {
        '1': 'haiku',
        '2': 'sonnet',
        '3': 'opus',
        '4': 'claude-sonnet-4-5',
    }

    if choice in models:
        frontmatter['model'] = models[choice]
        print(f"✓ Model updated to: {models[choice]}")
    elif choice == '5':
        if 'model' in frontmatter:
            del frontmatter['model']
        print("✓ Model set to inherit")

    return frontmatter

def show_diff(original_content: str, new_content: str, file_path: Path):
    """Show diff of changes."""
    print(f"\n{'='*60}")
    print(f"Proposed Changes to {file_path.name}")
    print(f"{'='*60}\n")

    diff = difflib.unified_diff(
        original_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"{file_path.name} (original)",
        tofile=f"{file_path.name} (updated)",
        lineterm=''
    )

    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            print(f"\033[92m{line}\033[0m", end='')  # Green
        elif line.startswith('-') and not line.startswith('---'):
            print(f"\033[91m{line}\033[0m", end='')  # Red
        elif line.startswith('@@'):
            print(f"\033[94m{line}\033[0m", end='')  # Blue
        else:
            print(line, end='')

    print(f"\n{'='*60}\n")

def reconstruct_agent(frontmatter: Dict, body: str) -> str:
    """Reconstruct agent file from frontmatter and body."""
    yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
    return f"---\n{yaml_str}---\n{body}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 update-agent.py <agent-name>")
        print("\nExample: python3 update-agent.py code-reviewer")
        sys.exit(1)

    agent_name = sys.argv[1].replace('.md', '')

    # Find agent
    print(f"Searching for agent: {agent_name}...")
    agent_path = find_agent(agent_name)

    if not agent_path:
        print(f"❌ Agent not found: {agent_name}")
        print("\nSearched in:")
        print("  - .claude/agents/")
        print("  - ~/.claude/agents/")
        print("  - Plugin directories")
        sys.exit(1)

    print(f"✓ Found: {agent_path}")

    # Parse agent
    try:
        frontmatter, body = parse_agent(agent_path)
        original_content = agent_path.read_text()
    except Exception as e:
        print(f"❌ Failed to parse agent: {e}")
        sys.exit(1)

    # Show current config
    show_current_config(agent_name, frontmatter, agent_path)

    # Interactive menu
    choices = interactive_menu()

    if not choices:
        print("\n✓ No changes made")
        sys.exit(0)

    # Apply updates
    print("\n" + "="*60)
    print("Applying Updates")
    print("="*60)

    for choice in choices:
        if choice == 1:
            frontmatter = update_description(frontmatter)
        elif choice == 2:
            frontmatter = update_tools(frontmatter)
        elif choice == 3:
            frontmatter = update_model(frontmatter)
        elif choice == 4:
            # Run validation
            print("\nRunning validation...")
            os.system(f"python3 {Path(__file__).parent / 'validate-agent.py'} {agent_path}")

    # Reconstruct file
    new_content = reconstruct_agent(frontmatter, body)

    # Show diff
    show_diff(original_content, new_content, agent_path)

    # Confirm
    confirm = input("Apply these changes? (y/n): ").strip().lower()

    if confirm == 'y':
        # Backup original
        backup_path = agent_path.with_suffix('.md.bak')
        agent_path.rename(backup_path)

        # Write new content
        agent_path.write_text(new_content)

        print(f"\n✅ Agent updated successfully!")
        print(f"   Original backed up to: {backup_path}")
        print(f"   Updated file: {agent_path}")

        # Run validation
        print("\n" + "="*60)
        print("Validation")
        print("="*60)
        os.system(f"python3 {Path(__file__).parent / 'validate-agent.py'} {agent_path}")
    else:
        print("\n✓ Changes cancelled")

if __name__ == '__main__':
    main()
