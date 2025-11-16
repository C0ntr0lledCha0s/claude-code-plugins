#!/usr/bin/env python3
"""
Validate research output quality.
Usage: python validate-research.py <research-output-file>
"""

import re
import sys
from pathlib import Path
from typing import Dict, List

def validate_research_output(text: str) -> Dict[str, bool]:
    """Check if research output meets quality standards."""
    checks = {
        'has_summary': bool(re.search(r'##?\s*(Summary|Overview)', text, re.IGNORECASE)),
        'has_file_references': bool(re.search(r'`[^`]+:\d+(-\d+)?`', text)),
        'has_evidence': any(keyword in text for keyword in ['Evidence:', 'Location:', 'Example:', 'Source:']),
        'has_recommendations': any(keyword in text.lower() for keyword in ['recommend', 'suggest', 'consider', 'should']),
        'has_structure': text.count('##') >= 3,  # At least 3 sections
        'sufficient_length': len(text) > 200,  # Minimum content
        'has_citations': bool(re.search(r'\[\d+\]|\bsource:', text, re.IGNORECASE)),
    }

    return checks

def print_results(checks: Dict[str, bool], filename: str):
    """Print validation results."""
    passed = sum(checks.values())
    total = len(checks)

    print(f"\n{'='*60}")
    print(f"Research Quality Validation: {filename}")
    print(f"{'='*60}\n")

    print(f"Overall Score: {passed}/{total} checks passed ({passed/total*100:.0f}%)\n")

    for check, result in checks.items():
        status = "✓" if result else "✗"
        check_name = check.replace('_', ' ').title()
        print(f"  {status} {check_name}")

    print(f"\n{'='*60}")

    if passed == total:
        print("✅ All quality checks passed!")
        return 0
    elif passed >= total * 0.7:
        print("⚠️  Most checks passed, but some improvements needed")
        return 0
    else:
        print("❌ Quality standards not met. Please improve the research output.")
        return 1

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-research.py <research-output-file>")
        print("\nValidates research output for quality standards:")
        print("  - Has summary/overview section")
        print("  - Includes file references with line numbers")
        print("  - Contains evidence or examples")
        print("  - Provides recommendations")
        print("  - Has structured sections")
        print("  - Sufficient content length")
        print("  - Includes citations/sources")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"Error: File '{filepath}' does not exist")
        sys.exit(1)

    try:
        content = filepath.read_text()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    checks = validate_research_output(content)
    exit_code = print_results(checks, filepath.name)

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
