#!/usr/bin/env python3
"""
Check that file references in research output exist and are valid.
Usage: python check-evidence.py <research-output-file> [--codebase-dir <dir>]
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple

def extract_file_references(text: str) -> List[Tuple[str, str]]:
    """Extract file references with line numbers from text."""
    # Pattern: `path/to/file.ext:42` or `path/to/file.ext:42-67`
    pattern = r'`([^`]+):(\d+(?:-\d+)?)`'
    matches = re.findall(pattern, text)

    return matches

def validate_file_reference(filepath: str, line_range: str, codebase_dir: Path) -> Tuple[bool, str]:
    """Validate that a file reference exists and line numbers are valid."""
    # Resolve file path
    file_path = codebase_dir / filepath

    if not file_path.exists():
        return False, f"File not found: {filepath}"

    # Parse line range
    if '-' in line_range:
        start, end = map(int, line_range.split('-'))
    else:
        start = end = int(line_range)

    # Check line numbers
    try:
        lines = file_path.read_text().splitlines()
        total_lines = len(lines)

        if start < 1 or end > total_lines:
            return False, f"Line range {line_range} exceeds file length ({total_lines} lines)"

        return True, "Valid"

    except Exception as e:
        return False, f"Error reading file: {e}"

def main():
    parser = argparse.ArgumentParser(description='Validate file references in research output')
    parser.add_argument('research_file', help='Research output file to validate')
    parser.add_argument('--codebase-dir', default='.', help='Root directory of codebase (default: current directory)')
    args = parser.parse_args()

    research_path = Path(args.research_file)
    codebase_dir = Path(args.codebase_dir).resolve()

    if not research_path.exists():
        print(f"Error: Research file '{research_path}' does not exist")
        sys.exit(1)

    if not codebase_dir.exists():
        print(f"Error: Codebase directory '{codebase_dir}' does not exist")
        sys.exit(1)

    # Read research output
    try:
        content = research_path.read_text()
    except Exception as e:
        print(f"Error reading research file: {e}")
        sys.exit(1)

    # Extract file references
    references = extract_file_references(content)

    print(f"\n{'='*60}")
    print(f"Evidence Validation: {research_path.name}")
    print(f"Codebase: {codebase_dir}")
    print(f"{'='*60}\n")

    if not references:
        print("⚠️  No file references found in research output")
        print("   Research should include file references like: `path/to/file.ts:42`")
        sys.exit(1)

    print(f"Found {len(references)} file reference(s)\n")

    valid_count = 0
    invalid_refs = []

    for filepath, line_range in references:
        is_valid, message = validate_file_reference(filepath, line_range, codebase_dir)

        if is_valid:
            valid_count += 1
            print(f"  ✓ `{filepath}:{line_range}` - {message}")
        else:
            invalid_refs.append((filepath, line_range, message))
            print(f"  ✗ `{filepath}:{line_range}` - {message}")

    print(f"\n{'='*60}")
    print(f"Results: {valid_count}/{len(references)} references valid ({valid_count/len(references)*100:.0f}%)")
    print(f"{'='*60}\n")

    if invalid_refs:
        print("❌ Some file references are invalid:")
        for filepath, line_range, message in invalid_refs:
            print(f"   • `{filepath}:{line_range}` - {message}")
        sys.exit(1)
    else:
        print("✅ All file references are valid!")
        sys.exit(0)

if __name__ == '__main__':
    main()
