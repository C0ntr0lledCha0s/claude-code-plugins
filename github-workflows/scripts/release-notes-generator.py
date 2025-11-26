#!/usr/bin/env python3
"""
Release Notes Generator
Generates user-friendly release notes from git commits.
"""

import argparse
import json
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
    except subprocess.CalledProcessError:
        return ""


def run_gh(args: list[str]) -> str:
    """Execute gh command and return output."""
    try:
        result = subprocess.run(
            ['gh'] + args,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def get_last_tag() -> Optional[str]:
    """Get the most recent git tag."""
    return run_git(['describe', '--tags', '--abbrev=0']) or None


def get_repo_info() -> dict:
    """Get repository information."""
    remote = run_git(['remote', 'get-url', 'origin'])
    match = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', remote)

    if match:
        return {
            'owner': match.group(1),
            'repo': match.group(2)
        }
    return {'owner': '', 'repo': ''}


def get_commits_since(tag: Optional[str]) -> list[dict]:
    """Get commits since the specified tag."""
    if tag:
        log_range = f"{tag}..HEAD"
    else:
        log_range = "HEAD"

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
                'hash': parts[0],
                'subject': parts[1],
                'body': parts[2] if len(parts) > 2 else ''
            })

    return commits


def parse_conventional_commit(subject: str) -> dict:
    """Parse conventional commit format."""
    pattern = r'^(\w+)(?:\(([^)]+)\))?(!)?: (.+)$'
    match = re.match(pattern, subject)

    if match:
        return {
            'type': match.group(1).lower(),
            'scope': match.group(2) or '',
            'breaking': bool(match.group(3)),
            'description': match.group(4)
        }

    return {
        'type': 'other',
        'scope': '',
        'breaking': False,
        'description': subject
    }


def extract_issue_refs(commits: list[dict]) -> list[int]:
    """Extract issue references from commits."""
    issues = set()

    for commit in commits:
        text = commit['subject'] + ' ' + commit.get('body', '')
        refs = re.findall(r'#(\d+)', text)
        issues.update(int(ref) for ref in refs)

    return sorted(issues)


def get_contributors(tag: Optional[str]) -> list[str]:
    """Get list of contributors since tag."""
    if tag:
        log_range = f"{tag}..HEAD"
    else:
        log_range = "HEAD"

    output = run_git(['log', log_range, '--format=%aN'])
    if not output:
        return []

    return sorted(set(output.split('\n')))


def categorize_commits(commits: list[dict]) -> dict:
    """Categorize commits for release notes."""
    categories = {
        'breaking': [],
        'features': [],
        'fixes': [],
        'improvements': [],
        'other': []
    }

    for commit in commits:
        parsed = parse_conventional_commit(commit['subject'])

        if 'BREAKING CHANGE' in commit.get('body', ''):
            parsed['breaking'] = True

        entry = {
            'description': parsed['description'],
            'scope': parsed['scope']
        }

        if parsed['breaking']:
            categories['breaking'].append(entry)
        elif parsed['type'] == 'feat':
            categories['features'].append(entry)
        elif parsed['type'] == 'fix':
            categories['fixes'].append(entry)
        elif parsed['type'] in ['perf', 'refactor', 'docs']:
            categories['improvements'].append(entry)
        else:
            categories['other'].append(entry)

    return categories


def generate_release_notes(
    version: str,
    categories: dict,
    contributors: list[str],
    issue_refs: list[int],
    repo_info: dict
) -> str:
    """Generate formatted release notes."""
    lines = [
        f"# Release v{version}",
        "",
        f"Released: {datetime.now().strftime('%B %d, %Y')}",
        "",
    ]

    # Highlights section
    lines.append("## Highlights")
    lines.append("")

    if categories['breaking']:
        lines.append(f"**⚠️ Breaking Changes**: This release includes {len(categories['breaking'])} breaking change(s). Please review the migration notes below.")
        lines.append("")

    if categories['features']:
        lines.append(f"This release introduces {len(categories['features'])} new feature(s):")
        for item in categories['features'][:3]:  # Top 3
            scope = f"({item['scope']}) " if item['scope'] else ""
            lines.append(f"- {scope}{item['description']}")
        if len(categories['features']) > 3:
            lines.append(f"- ...and {len(categories['features']) - 3} more")
        lines.append("")

    if categories['fixes']:
        lines.append(f"Includes {len(categories['fixes'])} bug fix(es) and {len(categories['improvements'])} improvement(s).")
        lines.append("")

    # Breaking Changes
    if categories['breaking']:
        lines.append("## ⚠️ Breaking Changes")
        lines.append("")
        for item in categories['breaking']:
            scope = f"**{item['scope']}**: " if item['scope'] else ""
            lines.append(f"- {scope}{item['description']}")
        lines.append("")
        lines.append("### Migration Guide")
        lines.append("")
        lines.append("<!-- Add migration instructions for each breaking change -->")
        lines.append("")

    # New Features
    if categories['features']:
        lines.append("## ✨ New Features")
        lines.append("")
        for item in categories['features']:
            scope = f"**{item['scope']}**: " if item['scope'] else ""
            lines.append(f"- {scope}{item['description']}")
        lines.append("")

    # Bug Fixes
    if categories['fixes']:
        lines.append("## 🐛 Bug Fixes")
        lines.append("")
        for item in categories['fixes']:
            scope = f"**{item['scope']}**: " if item['scope'] else ""
            lines.append(f"- {scope}{item['description']}")
        lines.append("")

    # Improvements
    if categories['improvements']:
        lines.append("## 🔧 Improvements")
        lines.append("")
        for item in categories['improvements']:
            scope = f"**{item['scope']}**: " if item['scope'] else ""
            lines.append(f"- {scope}{item['description']}")
        lines.append("")

    # Installation/Upgrade
    lines.append("## 📦 Installation")
    lines.append("")
    if repo_info.get('repo'):
        lines.append("```bash")
        lines.append(f"# Clone the repository")
        lines.append(f"git clone https://github.com/{repo_info['owner']}/{repo_info['repo']}.git")
        lines.append("")
        lines.append(f"# Or update to this version")
        lines.append(f"git fetch origin")
        lines.append(f"git checkout v{version}")
        lines.append("```")
    else:
        lines.append("See repository README for installation instructions.")
    lines.append("")

    # Related Issues
    if issue_refs:
        lines.append("## 🔗 Related Issues")
        lines.append("")
        for issue in issue_refs[:10]:  # Limit to 10
            if repo_info.get('owner'):
                lines.append(f"- [{repo_info['owner']}/{repo_info['repo']}#{issue}](https://github.com/{repo_info['owner']}/{repo_info['repo']}/issues/{issue})")
            else:
                lines.append(f"- #{issue}")
        if len(issue_refs) > 10:
            lines.append(f"- ...and {len(issue_refs) - 10} more")
        lines.append("")

    # Contributors
    if contributors:
        lines.append("## 👥 Contributors")
        lines.append("")
        lines.append("Thank you to everyone who contributed to this release:")
        lines.append("")
        for contributor in contributors:
            lines.append(f"- {contributor}")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("**Full Changelog**: " + (
        f"https://github.com/{repo_info['owner']}/{repo_info['repo']}/compare/{get_last_tag() or 'initial'}...v{version}"
        if repo_info.get('owner') else "See git history"
    ))

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate release notes from git commits',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s 1.5.0                    # Generate notes for version 1.5.0
  %(prog)s 1.5.0 --since v1.4.0     # Commits since specific tag
  %(prog)s 1.5.0 -o RELEASE.md      # Output to file
        '''
    )

    parser.add_argument('version', help='Version number for this release')
    parser.add_argument('--since', metavar='TAG',
                        help='Tag to start from (default: last tag)')
    parser.add_argument('--output', '-o', type=Path, metavar='FILE',
                        help='Output file')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')

    args = parser.parse_args()

    # Get commits
    since_tag = args.since or get_last_tag()
    print(f"{BLUE}Release Notes Generator{NC}", file=sys.stderr)
    print(f"Version: {args.version}", file=sys.stderr)
    print(f"Since: {since_tag or 'beginning'}\n", file=sys.stderr)

    commits = get_commits_since(since_tag)

    if not commits:
        print(f"{YELLOW}No commits found{NC}", file=sys.stderr)
        sys.exit(0)

    # Gather information
    categories = categorize_commits(commits)
    contributors = get_contributors(since_tag)
    issue_refs = extract_issue_refs(commits)
    repo_info = get_repo_info()

    print(f"Commits: {len(commits)}", file=sys.stderr)
    print(f"Contributors: {len(contributors)}", file=sys.stderr)
    print(f"Issue refs: {len(issue_refs)}\n", file=sys.stderr)

    if args.json:
        output = {
            'version': args.version,
            'date': datetime.now().isoformat(),
            'categories': categories,
            'contributors': contributors,
            'issues': issue_refs,
            'repository': repo_info
        }
        result = json.dumps(output, indent=2)
    else:
        result = generate_release_notes(
            args.version,
            categories,
            contributors,
            issue_refs,
            repo_info
        )

    # Output
    if args.output:
        args.output.write_text(result, encoding='utf-8')
        print(f"{GREEN}✓ Saved to {args.output}{NC}", file=sys.stderr)
    else:
        print(result)


if __name__ == '__main__':
    main()
