#!/usr/bin/env python3
"""
PR Manager
Automates PR creation, labeling, and management
"""

import argparse
import json
import subprocess
import sys
import re

GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'


def run_gh(args):
    """Execute gh command"""
    try:
        result = subprocess.run(['gh'] + args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}", file=sys.stderr)
        return ""


def create_pr(branch):
    """Create PR with quality checks"""
    print(f"{BLUE}Creating PR for branch: {branch}{NC}\n")

    # Get branch changes
    diff_stat = subprocess.run(
        ['git', 'diff', '--stat', f'main...{branch}'],
        capture_output=True,
        text=True
    ).stdout

    print("Changes:")
    print(diff_stat)
    print()

    # Get commits
    commits = subprocess.run(
        ['git', 'log', '--oneline', f'main...{branch}'],
        capture_output=True,
        text=True
    ).stdout

    print("Commits:")
    print(commits)
    print()

    # Generate title (from first commit)
    first_commit = commits.split('\n')[0] if commits else ""
    title = first_commit.split(' ', 1)[1] if ' ' in first_commit else "Update"

    print(f"Suggested title: {title}")
    title = input("PR title (or press Enter to use suggested): ").strip() or title

    # Generate description
    description = f"""## Summary
Changes from branch {branch}

## Changes
{commits}

## Testing
- [ ] Tests added/updated
- [ ] Manual testing completed

## Related Issues
[Add issue references]
"""

    print("\nCreating PR...")
    result = run_gh(['pr', 'create', '--title', title, '--body', description])

    if result:
        print(f"\n{GREEN}✓ PR created{NC}")
        print(result)


def auto_label(pr_number):
    """Auto-apply labels based on PR content"""
    print(f"{BLUE}Auto-labeling PR #{pr_number}...{NC}\n")

    # Get PR details
    pr_data = run_gh(['pr', 'view', str(pr_number), '--json', 'title,files'])
    if not pr_data:
        return

    pr = json.loads(pr_data)
    title = pr['title'].lower()
    files = pr.get('files', [])

    labels = []

    # Type from title
    if any(word in title for word in ['feat', 'feature']):
        labels.append('feature')
    elif any(word in title for word in ['fix', 'bug']):
        labels.append('bug')
    elif 'docs' in title or 'documentation' in title:
        labels.append('documentation')

    # Scope from files
    file_paths = [f.get('path', '') for f in files]

    if any('frontend' in p or 'ui' in p for p in file_paths):
        labels.append('scope:frontend')
    if any('backend' in p or 'api' in p for p in file_paths):
        labels.append('scope:backend')
    if any('.md' in p or 'docs' in p for p in file_paths):
        labels.append('documentation')

    # Size by changes
    total_changes = sum(f.get('additions', 0) + f.get('deletions', 0) for f in files)

    if total_changes < 50:
        labels.append('size:s')
    elif total_changes < 200:
        labels.append('size:m')
    else:
        labels.append('size:l')

    if labels:
        print(f"Applying labels: {', '.join(labels)}")
        run_gh(['pr', 'edit', str(pr_number), '--add-label', ','.join(labels)])
        print(f"{GREEN}✓ Labels applied{NC}")
    else:
        print("No labels to apply")


def auto_assign(pr_number):
    """Auto-assign reviewers based on CODEOWNERS"""
    print(f"{BLUE}Auto-assigning reviewers for PR #{pr_number}...{NC}\n")

    # Get PR files
    pr_data = run_gh(['pr', 'view', str(pr_number), '--json', 'files'])
    if not pr_data:
        return

    pr = json.loads(pr_data)
    files = pr.get('files', [])

    # Simple heuristic: assign to team based on paths
    reviewers = set()

    for file in files:
        path = file.get('path', '')

        if 'frontend' in path or 'ui' in path:
            reviewers.add('frontend-team')
        if 'backend' in path or 'api' in path:
            reviewers.add('backend-team')

    if reviewers:
        print(f"Suggested reviewers: {', '.join(reviewers)}")
        # In practice, would use gh pr edit --add-reviewer
        print(f"{YELLOW}Note: Implement with gh pr edit --add-reviewer{NC}")
    else:
        print("No reviewers suggested")


def sync_board(pr_number):
    """Sync PR with project board"""
    print(f"{BLUE}Syncing PR #{pr_number} with project board...{NC}\n")

    # Get PR details
    pr_data = run_gh(['pr', 'view', str(pr_number), '--json', 'url,labels'])
    if not pr_data:
        return

    pr = json.loads(pr_data)
    url = pr['url']
    labels = [l['name'] for l in pr.get('labels', [])]

    print(f"PR: {url}")
    print(f"Labels: {', '.join(labels)}")

    # Add to board based on labels
    if 'priority:high' in labels:
        print(f"{YELLOW}Suggest: Add to 'Sprint Planning' board{NC}")
    if 'bug' in labels:
        print(f"{YELLOW}Suggest: Add to 'Bug Triage' board{NC}")

    print(f"{YELLOW}Note: Implement with gh project item-add{NC}")


def main():
    parser = argparse.ArgumentParser(description='PR Manager')
    subparsers = parser.add_subparsers(dest='command')

    # create
    create_parser = subparsers.add_parser('create', help='Create PR')
    create_parser.add_argument('--branch', required=True, help='Branch name')

    # auto-label
    label_parser = subparsers.add_parser('auto-label', help='Auto-apply labels')
    label_parser.add_argument('--pr', type=int, required=True, help='PR number')

    # auto-assign
    assign_parser = subparsers.add_parser('auto-assign', help='Auto-assign reviewers')
    assign_parser.add_argument('--pr', type=int, required=True, help='PR number')

    # sync-board
    sync_parser = subparsers.add_parser('sync-board', help='Sync with project board')
    sync_parser.add_argument('--pr', type=int, required=True, help='PR number')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'create':
        create_pr(args.branch)
    elif args.command == 'auto-label':
        auto_label(args.pr)
    elif args.command == 'auto-assign':
        auto_assign(args.pr)
    elif args.command == 'sync-board':
        sync_board(args.pr)


if __name__ == '__main__':
    main()
