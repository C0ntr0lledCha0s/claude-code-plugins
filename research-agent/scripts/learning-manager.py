#!/usr/bin/env python3
"""
Learning Log Manager

Manage personal learnings extracted from research to build a searchable knowledge base.

Usage:
    python learning-manager.py list [--recent N] [--tag TAG]
    python learning-manager.py search <query>
    python learning-manager.py show <learning-id>
    python learning-manager.py add <topic> [--tags TAGS] [--source SOURCE]
    python learning-manager.py stats
    python learning-manager.py review [--unapplied]
    python learning-manager.py mark-applied <learning-id>
"""

import os
import re
import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import Counter

# Learning log directory
LEARNING_DIR = Path(__file__).parent.parent / '.learning-log'
INDEX_FILE = LEARNING_DIR / 'index.json'
TAGS_FILE = LEARNING_DIR / 'tags.json'

class LearningEntry:
    """Represents a learning log entry"""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.metadata = {}
        self.content = ""
        self._load()

    def _load(self):
        """Load entry from file"""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Learning file not found: {self.filepath}")

        text = self.filepath.read_text()

        # Extract YAML frontmatter
        if text.startswith('---\n'):
            parts = text.split('---\n', 2)
            if len(parts) >= 3:
                try:
                    self.metadata = yaml.safe_load(parts[1])
                    self.content = parts[2].strip()
                except yaml.YAMLError as e:
                    print(f"Warning: Could not parse YAML frontmatter: {e}")
                    self.content = text
            else:
                self.content = text
        else:
            self.content = text

    @property
    def learning_id(self) -> str:
        """Get learning ID (filename without extension)"""
        return self.filepath.stem

    @property
    def topic(self) -> str:
        """Get topic from metadata or filename"""
        return self.metadata.get('topic', self.learning_id.replace('-', ' '))

    @property
    def date(self) -> Optional[datetime]:
        """Get date from metadata"""
        date_str = self.metadata.get('date')
        if date_str:
            try:
                return datetime.fromisoformat(str(date_str))
            except:
                pass
        return None

    @property
    def tags(self) -> List[str]:
        """Get tags from metadata"""
        return self.metadata.get('tags', [])

    @property
    def confidence(self) -> str:
        """Get confidence level"""
        return self.metadata.get('confidence', 'medium')

    @property
    def applied(self) -> bool:
        """Check if learning has been applied"""
        return self.metadata.get('applied', False)

    @property
    def source(self) -> str:
        """Get source of learning"""
        return self.metadata.get('source', 'manual')

    @property
    def reviewed_count(self) -> int:
        """Get number of times reviewed"""
        return self.metadata.get('reviewed_count', 0)

    @property
    def key_insight(self) -> str:
        """Extract key insight from content"""
        match = re.search(r'##\s*Key Insight\s*\n(.+?)(?=\n##)', self.content, re.DOTALL)
        if match:
            return match.group(1).strip()[:200]  # First 200 chars
        return ""

    def matches_query(self, query: str) -> bool:
        """Check if entry matches search query"""
        query_lower = query.lower()

        # Search in topic
        if query_lower in self.topic.lower():
            return True

        # Search in tags
        if any(query_lower in tag.lower() for tag in self.tags):
            return True

        # Search in content
        if query_lower in self.content.lower():
            return True

        return False


def list_learnings(tag: Optional[str] = None, recent: Optional[int] = None) -> List[LearningEntry]:
    """List all learning entries"""
    entries = []

    # Search all month directories
    for month_dir in sorted(LEARNING_DIR.glob('*-*'), reverse=True):
        if not month_dir.is_dir():
            continue

        for file in month_dir.glob('*.md'):
            try:
                entry = LearningEntry(file)

                # Filter by tag if specified
                if tag and tag not in entry.tags:
                    continue

                entries.append(entry)
            except Exception as e:
                print(f"Warning: Could not load {file}: {e}", file=sys.stderr)

    # Sort by date (newest first)
    entries.sort(key=lambda e: e.date or datetime.min, reverse=True)

    # Limit to recent N if specified
    if recent:
        entries = entries[:recent]

    return entries


def search_learnings(query: str) -> List[LearningEntry]:
    """Search learning entries by query"""
    all_entries = list_learnings()
    return [entry for entry in all_entries if entry.matches_query(query)]


def show_learning(learning_id: str) -> Optional[LearningEntry]:
    """Show a specific learning entry"""
    # Search in all month directories
    for month_dir in LEARNING_DIR.glob('*-*'):
        if not month_dir.is_dir():
            continue

        filepath = month_dir / f"{learning_id}.md"
        if filepath.exists():
            return LearningEntry(filepath)

    return None


def add_learning(topic: str, tags: List[str] = None, source: str = None, confidence: str = 'medium') -> Path:
    """Add a new learning entry"""
    # Generate learning ID
    date_str = datetime.now().strftime('%Y-%m-%d')
    topic_slug = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')
    learning_id = f"{topic_slug}-{date_str}"

    # Create month directory
    month_str = datetime.now().strftime('%Y-%m')
    month_dir = LEARNING_DIR / month_str
    month_dir.mkdir(parents=True, exist_ok=True)

    # Create learning file from template
    template_path = Path(__file__).parent.parent / 'assets' / 'learning-entry-template.md'
    if template_path.exists():
        template = template_path.read_text()
    else:
        template = """---
date: {date}
topic: {topic}
source: {source}
tags: {tags}
confidence: {confidence}
applied: false
reviewed_count: 0
last_reviewed: null
---

# What I Learned

## Key Insight
[Your key insight here]

## Why It Matters
[Why this is important]

## How to Apply
[Practical application]

## Related Learnings
[Related topics]

## Questions to Explore
[Follow-up questions]

## Status Checklist
- [ ] Understood concept
- [ ] Applied in code
- [ ] Reviewed and retained
"""

    # Fill template
    metadata = {
        'date': date_str,
        'topic': topic,
        'source': source or 'manual',
        'tags': tags or [],
        'confidence': confidence,
        'applied': False,
        'reviewed_count': 0,
        'last_reviewed': None
    }

    yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
    content = template.format(
        date=date_str,
        topic=topic,
        source=source or 'manual',
        tags=json.dumps(tags or []),
        confidence=confidence
    )

    # Write file
    learning_file = month_dir / f"{learning_id}.md"
    learning_file.write_text(f"---\n{yaml_str}---\n\n{content.split('---', 2)[2] if '---' in content else content}")

    # Update index
    update_index()

    return learning_file


def get_stats() -> Dict:
    """Get learning log statistics"""
    entries = list_learnings()

    stats = {
        'total': len(entries),
        'this_month': 0,
        'applied': 0,
        'high_confidence': 0,
        'by_tag': Counter(),
        'by_month': Counter(),
        'by_confidence': Counter()
    }

    current_month = datetime.now().strftime('%Y-%m')

    for entry in entries:
        # Count this month
        if entry.date and entry.date.strftime('%Y-%m') == current_month:
            stats['this_month'] += 1

        # Count applied
        if entry.applied:
            stats['applied'] += 1

        # Count high confidence
        if entry.confidence == 'high':
            stats['high_confidence'] += 1

        # Count by tag
        for tag in entry.tags:
            stats['by_tag'][tag] += 1

        # Count by month
        if entry.date:
            month_key = entry.date.strftime('%Y-%m')
            stats['by_month'][month_key] += 1

        # Count by confidence
        stats['by_confidence'][entry.confidence] += 1

    return stats


def mark_applied(learning_id: str) -> bool:
    """Mark a learning as applied"""
    entry = show_learning(learning_id)
    if not entry:
        return False

    # Update metadata
    text = entry.filepath.read_text()
    if text.startswith('---\n'):
        parts = text.split('---\n', 2)
        if len(parts) >= 3:
            metadata = yaml.safe_load(parts[1])
            metadata['applied'] = True
            yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
            entry.filepath.write_text(f"---\n{yaml_str}---\n{parts[2]}")
            return True

    return False


def review_unapplied() -> List[LearningEntry]:
    """Get learnings that haven't been applied yet"""
    entries = list_learnings()
    return [e for e in entries if not e.applied]


def update_index():
    """Update the master index file"""
    entries = list_learnings()

    index = {
        'last_updated': datetime.now().isoformat(),
        'total_learnings': len(entries),
        'learnings': []
    }

    for entry in entries:
        index['learnings'].append({
            'id': entry.learning_id,
            'topic': entry.topic,
            'date': entry.date.isoformat() if entry.date else None,
            'tags': entry.tags,
            'confidence': entry.confidence,
            'applied': entry.applied,
            'source': entry.source
        })

    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(index, indent=2))

    # Update tags index
    update_tags_index(entries)


def update_tags_index(entries: List[LearningEntry]):
    """Update the tags index file"""
    tags_data = {}

    for entry in entries:
        for tag in entry.tags:
            if tag not in tags_data:
                tags_data[tag] = {
                    'count': 0,
                    'learnings': [],
                    'related': set()
                }

            tags_data[tag]['count'] += 1
            tags_data[tag]['learnings'].append(entry.learning_id)

            # Find related tags (tags that appear together)
            for other_tag in entry.tags:
                if other_tag != tag:
                    tags_data[tag]['related'].add(other_tag)

    # Convert sets to lists for JSON serialization
    for tag in tags_data:
        tags_data[tag]['related'] = list(tags_data[tag]['related'])

    TAGS_FILE.write_text(json.dumps(tags_data, indent=2))


def print_learning_summary(entry: LearningEntry, detailed: bool = False):
    """Print a summary of a learning entry"""
    status = "✓ Applied" if entry.applied else "○ Not Applied"
    confidence_icon = {'high': '●', 'medium': '◐', 'low': '○'}.get(entry.confidence, '○')
    date_str = entry.date.strftime('%Y-%m-%d') if entry.date else "Unknown"

    print(f"{status} {confidence_icon} [{date_str}] {entry.topic}")
    print(f"   ID: {entry.learning_id}")

    if entry.tags:
        print(f"   Tags: {', '.join(entry.tags)}")

    if detailed:
        if entry.key_insight:
            print(f"   Insight: {entry.key_insight[:100]}...")
        print(f"   Source: {entry.source}")
        print(f"   Confidence: {entry.confidence}")
        print(f"   Reviewed: {entry.reviewed_count} times")

    print()


def cmd_list(args):
    """Handle list command"""
    entries = list_learnings(tag=args.tag, recent=args.recent)

    if not entries:
        print("No learning entries found.")
        return

    print(f"Found {len(entries)} learning entries:\n")
    for entry in entries:
        print_learning_summary(entry, detailed=args.verbose)


def cmd_search(args):
    """Handle search command"""
    entries = search_learnings(args.query)

    if not entries:
        print(f"No learnings found matching '{args.query}'")
        return

    print(f"Found {len(entries)} matching learnings:\n")
    for entry in entries:
        print_learning_summary(entry, detailed=args.verbose)


def cmd_show(args):
    """Handle show command"""
    entry = show_learning(args.learning_id)

    if not entry:
        print(f"Learning not found: {args.learning_id}")
        sys.exit(1)

    # Print metadata
    print(f"{'='*60}")
    print(f"Learning: {entry.topic}")
    print(f"{'='*60}\n")
    print(f"ID: {entry.learning_id}")
    print(f"Date: {entry.date.strftime('%Y-%m-%d') if entry.date else 'Unknown'}")
    print(f"Applied: {'Yes' if entry.applied else 'No'}")
    print(f"Confidence: {entry.confidence}")
    if entry.tags:
        print(f"Tags: {', '.join(entry.tags)}")
    print(f"Source: {entry.source}")
    print(f"Reviewed: {entry.reviewed_count} times")

    print(f"\n{'='*60}")
    print("Content:")
    print(f"{'='*60}\n")
    print(entry.content)


def cmd_add(args):
    """Handle add command"""
    learning_file = add_learning(
        topic=args.topic,
        tags=args.tags.split(',') if args.tags else None,
        source=args.source,
        confidence=args.confidence
    )

    print(f"✓ Learning entry created: {learning_file.stem}")
    print(f"  File: {learning_file}")
    print(f"\nEdit the file to add details, then mark as applied when used in code.")


def cmd_stats(args):
    """Handle stats command"""
    stats = get_stats()

    print(f"\n{'='*60}")
    print("Learning Log Statistics")
    print(f"{'='*60}\n")

    print(f"Total learnings: {stats['total']}")
    print(f"  This month: {stats['this_month']}")
    print(f"  Applied in code: {stats['applied']} ({stats['applied']/stats['total']*100:.0f}%)" if stats['total'] > 0 else "  Applied: 0")
    print(f"  High confidence: {stats['high_confidence']} ({stats['high_confidence']/stats['total']*100:.0f}%)\n" if stats['total'] > 0 else "  High confidence: 0\n")

    if stats['by_tag']:
        print("Top Topics:")
        for tag, count in stats['by_tag'].most_common(5):
            print(f"  {tag}: {count} learnings")
        print()

    if stats['by_month']:
        print("Learning Velocity (last 6 months):")
        for month, count in sorted(stats['by_month'].items(), reverse=True)[:6]:
            bar = '█' * count + '░' * (20 - min(count, 20))
            print(f"  {month}: {bar[:20]} {count} learnings")

    print(f"\n{'='*60}\n")


def cmd_review(args):
    """Handle review command"""
    if args.unapplied:
        entries = review_unapplied()
        print(f"\n{len(entries)} unapplied learnings:\n")
    else:
        entries = list_learnings(recent=10)
        print(f"\nRecent learnings for review:\n")

    for entry in entries:
        print_learning_summary(entry, detailed=True)


def cmd_mark_applied(args):
    """Handle mark-applied command"""
    if mark_applied(args.learning_id):
        print(f"✓ Marked learning as applied: {args.learning_id}")
    else:
        print(f"✗ Learning not found: {args.learning_id}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Manage learning log')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # List command
    list_parser = subparsers.add_parser('list', help='List learning entries')
    list_parser.add_argument('--tag', help='Filter by tag')
    list_parser.add_argument('--recent', type=int, help='Show only N most recent')
    list_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed info')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search learning entries')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed info')

    # Show command
    show_parser = subparsers.add_parser('show', help='Show a learning entry')
    show_parser.add_argument('learning_id', help='Learning entry ID')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add learning entry')
    add_parser.add_argument('topic', help='Learning topic')
    add_parser.add_argument('--tags', help='Comma-separated tags')
    add_parser.add_argument('--source', help='Source command or research')
    add_parser.add_argument('--confidence', default='medium', choices=['low', 'medium', 'high'], help='Confidence level')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show learning statistics')

    # Review command
    review_parser = subparsers.add_parser('review', help='Review learnings')
    review_parser.add_argument('--unapplied', action='store_true', help='Show only unapplied learnings')

    # Mark applied command
    mark_parser = subparsers.add_parser('mark-applied', help='Mark learning as applied')
    mark_parser.add_argument('learning_id', help='Learning entry ID')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    cmd_map = {
        'list': cmd_list,
        'search': cmd_search,
        'show': cmd_show,
        'add': cmd_add,
        'stats': cmd_stats,
        'review': cmd_review,
        'mark-applied': cmd_mark_applied,
    }

    cmd_map[args.command](args)


if __name__ == '__main__':
    main()
