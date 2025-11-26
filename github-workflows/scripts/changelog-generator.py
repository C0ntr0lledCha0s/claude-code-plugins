#!/usr/bin/env python3
"""
Changelog Generator
Generates changelog entries from git commits using conventional commits format.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
RED = '\033[0;31m'
NC = '\033[0m'


def run_git(args: list[str]) -> str:
    """Execute git command and return output."""
    try:
        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return ""


def get_last_tag() -> Optional[str]:
    """Get the most recent git tag."""
    return run_git(['describe', '--tags', '--abbrev=0']) or None


def get_commits_since(tag: Optional[str]) -> list[dict]:
    """Get commits since the specified tag."""
    if tag:
        log_range = f"{tag}..HEAD"
    else:
        log_range = "HEAD"

    # Format: hash|subject|body
    format_str = "%H|%s|%b|||"
    output = run_git(['log', log_range, f'--pretty=format:{format_str}'])

    if not output:
        return []

    commits = []
    for entry in output.split('|||'):
        entry = entry.strip()
        if not entry:
            continue

        parts = entry.split('|', 2)
        if len(parts) >= 2:
            commits.append({
                'hash': parts[0][:7],
                'subject': parts[1],
                'body': parts[2] if len(parts) > 2 else ''
            })

    return commits


def parse_conventional_commit(subject: str) -> dict:
    """Parse conventional commit format."""
    # Pattern: type(scope)!: description
    pattern = r'^(\w+)(?:\(([^)]+)\))?(!)?: (.+)$'
    match = re.match(pattern, subject)

    if match:
        return {
            'type': match.group(1).lower(),
            'scope': match.group(2) or '',
            'breaking': bool(match.group(3)),
            'description': match.group(4)
        }

    # Not a conventional commit
    return {
        'type': 'other',
        'scope': '',
        'breaking': False,
        'description': subject
    }


def categorize_commits(commits: list[dict]) -> dict[str, list]:
    """Categorize commits by type."""
    categories = {
        'breaking': [],
        'feat': [],
        'fix': [],
        'docs': [],
        'perf': [],
        'refactor': [],
        'test': [],
        'ci': [],
        'chore': [],
        'other': []
    }

    for commit in commits:
        parsed = parse_conventional_commit(commit['subject'])

        # Check for breaking change in body
        if 'BREAKING CHANGE' in commit.get('body', ''):
            parsed['breaking'] = True

        entry = {
            'hash': commit['hash'],
            'scope': parsed['scope'],
            'description': parsed['description']
        }

        if parsed['breaking']:
            categories['breaking'].append(entry)

        commit_type = parsed['type']
        if commit_type in categories:
            categories[commit_type].append(entry)
        else:
            categories['other'].append(entry)

    return categories


def generate_changelog_section(version: str, categories: dict[str, list], date: Optional[str] = None) -> str:
    """Generate changelog section in Keep a Changelog format."""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')

    lines = [f"## [{version}] - {date}", ""]

    # Section mapping with emoji
    sections = [
        ('breaking', '⚠️ Breaking Changes'),
        ('feat', '✨ Features'),
        ('fix', '🐛 Bug Fixes'),
        ('perf', '⚡ Performance'),
        ('docs', '📚 Documentation'),
        ('refactor', '♻️ Refactoring'),
        ('test', '🧪 Tests'),
        ('ci', '🔧 CI/CD'),
        ('chore', '🏠 Maintenance'),
    ]

    for category_key, section_title in sections:
        items = categories.get(category_key, [])
        if items:
            lines.append(f"### {section_title}")
            lines.append("")
            for item in items:
                scope = f"**{item['scope']}**: " if item['scope'] else ""
                lines.append(f"- {scope}{item['description']} ({item['hash']})")
            lines.append("")

    # Handle uncategorized commits
    if categories.get('other'):
        lines.append("### Other Changes")
        lines.append("")
        for item in categories['other']:
            lines.append(f"- {item['description']} ({item['hash']})")
        lines.append("")

    return '\n'.join(lines)


def determine_version_bump(categories: dict[str, list]) -> str:
    """Determine version bump type from commits."""
    if categories.get('breaking'):
        return 'major'
    elif categories.get('feat'):
        return 'minor'
    else:
        return 'patch'


def main():
    parser = argparse.ArgumentParser(
        description='Generate changelog from git commits',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s 1.5.0                    # Generate changelog for version 1.5.0
  %(prog)s 1.5.0 --since v1.4.0     # Commits since specific tag
  %(prog)s 1.5.0 --output CHANGELOG.md  # Append to file
        '''
    )

    parser.add_argument('version', help='Version number for this release')
    parser.add_argument('--since', metavar='TAG',
                        help='Tag to start from (default: last tag)')
    parser.add_argument('--date', metavar='DATE',
                        help='Release date (default: today)')
    parser.add_argument('--output', '-o', type=Path, metavar='FILE',
                        help='Output file (appends after header)')
    parser.add_argument('--prepend', action='store_true',
                        help='Prepend to existing changelog instead of appending')
    parser.add_argument('--analyze', action='store_true',
                        help='Show commit analysis without generating changelog')

    args = parser.parse_args()

    # Get commits
    since_tag = args.since or get_last_tag()
    print(f"{BLUE}Changelog Generator{NC}")
    print(f"Version: {args.version}")
    print(f"Since: {since_tag or 'beginning'}\n")

    commits = get_commits_since(since_tag)

    if not commits:
        print(f"{YELLOW}No commits found{NC}")
        sys.exit(0)

    # Categorize commits
    categories = categorize_commits(commits)

    # Show analysis
    if args.analyze:
        print(f"Analyzed {len(commits)} commits:\n")

        for key, items in categories.items():
            if items:
                print(f"  {key}: {len(items)}")

        print(f"\nSuggested bump: {determine_version_bump(categories)}")
        sys.exit(0)

    # Generate changelog
    changelog = generate_changelog_section(
        args.version,
        categories,
        date=args.date
    )

    # Output
    if args.output:
        output_file = args.output

        if output_file.exists() and args.prepend:
            # Read existing content
            existing = output_file.read_text(encoding='utf-8')

            # Find where to insert (after header)
            header_end = existing.find('\n## ')
            if header_end == -1:
                # No existing sections, append after any header
                lines = existing.split('\n')
                header_lines = []
                for i, line in enumerate(lines):
                    if line.startswith('#') and not line.startswith('## ['):
                        header_lines.append(line)
                    elif line.strip() == '':
                        header_lines.append(line)
                    else:
                        break

                new_content = '\n'.join(header_lines) + '\n' + changelog + '\n'.join(lines[len(header_lines):])
            else:
                # Insert before first version section
                new_content = existing[:header_end] + '\n' + changelog + existing[header_end:]

            output_file.write_text(new_content, encoding='utf-8')
            print(f"{GREEN}✓ Prepended to {output_file}{NC}")
        elif output_file.exists():
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write('\n' + changelog)
            print(f"{GREEN}✓ Appended to {output_file}{NC}")
        else:
            # Create new file with header
            header = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
            output_file.write_text(header + changelog, encoding='utf-8')
            print(f"{GREEN}✓ Created {output_file}{NC}")
    else:
        print(changelog)


if __name__ == '__main__':
    main()
