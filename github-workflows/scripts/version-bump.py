#!/usr/bin/env python3
"""
Version Bump Script
Bumps version numbers in package.json, plugin.json, and other version files.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

# Colors
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
RED = '\033[0;31m'
NC = '\033[0m'


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse semantic version string into tuple."""
    match = re.match(r'^v?(\d+)\.(\d+)\.(\d+)', version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def format_version(major: int, minor: int, patch: int) -> str:
    """Format version tuple as string."""
    return f"{major}.{minor}.{patch}"


def bump_version(current: str, bump_type: str) -> str:
    """Bump version according to type."""
    major, minor, patch = parse_version(current)

    if bump_type == 'major':
        return format_version(major + 1, 0, 0)
    elif bump_type == 'minor':
        return format_version(major, minor + 1, 0)
    elif bump_type == 'patch':
        return format_version(major, minor, patch + 1)
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_json_file(filepath: Path, version: str, dry_run: bool = False) -> bool:
    """Update version in a JSON file."""
    if not filepath.exists():
        return False

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        old_version = data.get('version', '0.0.0')
        data['version'] = version

        if dry_run:
            print(f"  {YELLOW}[DRY-RUN]{NC} Would update {filepath}: {old_version} → {version}")
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                f.write('\n')
            print(f"  {GREEN}✓{NC} Updated {filepath}: {old_version} → {version}")

        return True
    except (json.JSONDecodeError, IOError) as e:
        print(f"  {RED}✗{NC} Error updating {filepath}: {e}")
        return False


def find_version_files(root: Path) -> list[Path]:
    """Find all version files in the project."""
    version_files = []

    # Common version file patterns
    patterns = [
        'package.json',
        '**/plugin.json',
        '**/.claude-plugin/plugin.json',
        '**/marketplace.json',
    ]

    for pattern in patterns:
        for filepath in root.glob(pattern):
            if filepath.is_file() and not any(part.startswith('.git') for part in filepath.parts):
                version_files.append(filepath)

    return sorted(set(version_files))


def get_current_version(root: Path) -> Optional[str]:
    """Get current version from package.json or plugin.json."""
    for filename in ['package.json', '.claude-plugin/marketplace.json']:
        filepath = root / filename
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'version' in data:
                        return data['version']
            except (json.JSONDecodeError, IOError):
                continue
    return None


def main():
    parser = argparse.ArgumentParser(
        description='Bump version numbers in project files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s patch                    # 1.0.0 → 1.0.1
  %(prog)s minor                    # 1.0.0 → 1.1.0
  %(prog)s major                    # 1.0.0 → 2.0.0
  %(prog)s --set 2.5.0              # Set specific version
  %(prog)s patch --dry-run          # Show what would be changed
        '''
    )

    parser.add_argument('bump_type', nargs='?', choices=['major', 'minor', 'patch'],
                        help='Type of version bump')
    parser.add_argument('--set', dest='set_version', metavar='VERSION',
                        help='Set specific version (e.g., 2.0.0)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show changes without applying them')
    parser.add_argument('--root', type=Path, default=Path.cwd(),
                        help='Project root directory')

    args = parser.parse_args()

    if not args.bump_type and not args.set_version:
        parser.error("Either bump_type or --set is required")

    root = args.root.resolve()
    print(f"{BLUE}Version Bump{NC}")
    print(f"Project root: {root}\n")

    # Get current version
    current = get_current_version(root)
    if not current and not args.set_version:
        print(f"{RED}Error: Could not determine current version{NC}")
        print("Use --set to specify version explicitly")
        sys.exit(1)

    # Calculate new version
    if args.set_version:
        try:
            parse_version(args.set_version)  # Validate format
            new_version = args.set_version.lstrip('v')
        except ValueError as e:
            print(f"{RED}Error: {e}{NC}")
            sys.exit(1)
    else:
        new_version = bump_version(current, args.bump_type)

    print(f"Version: {current or 'unknown'} → {new_version}")
    if args.dry_run:
        print(f"{YELLOW}(dry run - no files will be modified){NC}")
    print()

    # Find and update version files
    version_files = find_version_files(root)

    if not version_files:
        print(f"{YELLOW}No version files found{NC}")
        sys.exit(0)

    print(f"Updating {len(version_files)} file(s):")
    updated = 0
    for filepath in version_files:
        if update_json_file(filepath, new_version, dry_run=args.dry_run):
            updated += 1

    print()
    if args.dry_run:
        print(f"{BLUE}Would update {updated} file(s){NC}")
    else:
        print(f"{GREEN}Updated {updated} file(s){NC}")

    # Output new version for scripting
    print(f"\nNew version: {new_version}")


if __name__ == '__main__':
    main()
