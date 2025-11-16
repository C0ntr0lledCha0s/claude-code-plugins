#!/usr/bin/env python3
"""
Extract and analyze citations from research output.
Usage: python extract-citations.py <research-file> [--format json|text] [--validate]
"""

import re
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from urllib.parse import urlparse

def extract_file_citations(text: str) -> List[Dict[str, str]]:
    """Extract file references like `path/to/file.ts:42` or `path/to/file.ts:42-67`."""
    pattern = r'`([^`]+):(\d+(?:-\d+)?)`'
    matches = re.findall(pattern, text)

    citations = []
    for filepath, line_range in matches:
        citations.append({
            'type': 'file',
            'path': filepath,
            'lines': line_range,
            'reference': f'`{filepath}:{line_range}`'
        })

    return citations

def extract_web_citations(text: str) -> List[Dict[str, str]]:
    """Extract numbered citations like [1], [2] and their corresponding URLs."""
    # Find citation markers like [1], [2]
    markers = re.findall(r'\[(\d+)\]', text)

    # Find URLs in references section
    # Match patterns like:
    # [1] Description - https://url.com
    # [1] https://url.com
    url_pattern = r'\[(\d+)\]\s*(?:.*?-\s*)?(https?://[^\s\)]+)'

    url_matches = re.findall(url_pattern, text, re.MULTILINE)

    # Build citation map
    citation_map = {}
    for num, url in url_matches:
        # Extract description if present
        desc_pattern = rf'\[{num}\]\s*([^-\n]+?)(?:\s*-\s*https?://|$)'
        desc_match = re.search(desc_pattern, text)
        description = desc_match.group(1).strip() if desc_match else ''

        citation_map[num] = {
            'type': 'web',
            'number': int(num),
            'url': url,
            'description': description,
            'domain': urlparse(url).netloc
        }

    # Find all citation usage in text
    citations = []
    seen = set()

    for marker in markers:
        if marker in citation_map and marker not in seen:
            citations.append(citation_map[marker])
            seen.add(marker)

    return citations

def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract code blocks with their language and source citations."""
    # Match code blocks: ```language\ncode\n```
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)

    code_blocks = []
    for language, code in matches:
        # Look for source citation near this code block
        # Pattern: Source: `path/to/file.ts:lines`
        source_pattern = r'Source:\s*`([^`]+:\d+(?:-\d+)?)`'

        # Search for source citation after the code block
        code_index = text.find(f'```{language}\n{code}```')
        if code_index != -1:
            # Look in next 200 characters for source citation
            snippet = text[code_index:code_index + 300]
            source_match = re.search(source_pattern, snippet)

            source = source_match.group(1) if source_match else None
        else:
            source = None

        code_blocks.append({
            'type': 'code_block',
            'language': language or 'unknown',
            'lines': len(code.strip().split('\n')),
            'source': source
        })

    return code_blocks

def extract_package_citations(text: str) -> List[Dict[str, str]]:
    """Extract package/dependency references."""
    # Match patterns like:
    # - **package-name** (vX.Y.Z)
    # - package-name (vX.Y.Z) - [docs](url)
    pattern = r'[-*]\s*\*\*([^*]+)\*\*\s*\(v?([\d.]+)\)'

    matches = re.findall(pattern, text)

    packages = []
    for package, version in matches:
        packages.append({
            'type': 'package',
            'name': package.strip(),
            'version': version
        })

    return packages

def analyze_citation_quality(citations: Dict[str, List]) -> Dict[str, any]:
    """Analyze citation quality and coverage."""
    total_citations = sum(len(cits) for cits in citations.values())

    quality = {
        'total_citations': total_citations,
        'file_citations': len(citations['files']),
        'web_citations': len(citations['web']),
        'code_blocks': len(citations['code_blocks']),
        'packages': len(citations['packages']),
        'has_references_section': len(citations['web']) > 0,
        'code_blocks_with_sources': sum(1 for cb in citations['code_blocks'] if cb.get('source')),
        'unique_domains': len(set(c['domain'] for c in citations['web'])),
    }

    # Calculate quality score
    score = 0
    max_score = 0

    # File citations present (0-25 points)
    max_score += 25
    if quality['file_citations'] > 0:
        score += min(quality['file_citations'] * 5, 25)

    # Web citations present (0-25 points)
    max_score += 25
    if quality['web_citations'] > 0:
        score += min(quality['web_citations'] * 5, 25)

    # Code blocks have sources (0-25 points)
    max_score += 25
    if quality['code_blocks'] > 0:
        source_ratio = quality['code_blocks_with_sources'] / quality['code_blocks']
        score += source_ratio * 25

    # Diverse sources (0-25 points)
    max_score += 25
    if quality['unique_domains'] > 0:
        score += min(quality['unique_domains'] * 5, 25)

    quality['quality_score'] = (score / max_score * 100) if max_score > 0 else 0

    return quality

def validate_citations(citations: Dict[str, List], codebase_dir: Path) -> Dict[str, List]:
    """Validate that file citations exist and URLs are accessible."""
    validation = {
        'valid_files': [],
        'invalid_files': [],
        'web_status': []
    }

    # Validate file citations
    for file_cit in citations['files']:
        filepath = codebase_dir / file_cit['path']
        if filepath.exists():
            validation['valid_files'].append(file_cit)
        else:
            validation['invalid_files'].append(file_cit)

    return validation

def print_text_report(citations: Dict, quality: Dict, validation: Dict = None):
    """Print human-readable citation report."""
    print(f"\n{'='*60}")
    print("Citation Analysis Report")
    print(f"{'='*60}\n")

    print(f"Total Citations: {quality['total_citations']}")
    print(f"Quality Score: {quality['quality_score']:.1f}/100\n")

    # File Citations
    if citations['files']:
        print(f"File References ({len(citations['files'])}):")
        for fc in citations['files'][:10]:  # Show first 10
            print(f"  • `{fc['path']}:{fc['lines']}`")
        if len(citations['files']) > 10:
            print(f"  ... and {len(citations['files']) - 10} more")
        print()

    # Web Citations
    if citations['web']:
        print(f"Web Citations ({len(citations['web'])}):")
        for wc in citations['web']:
            desc = wc['description'][:50] + '...' if len(wc['description']) > 50 else wc['description']
            print(f"  [{wc['number']}] {desc}")
            print(f"      {wc['url']}")
        print()

    # Code Blocks
    if citations['code_blocks']:
        print(f"Code Examples ({len(citations['code_blocks'])}):")
        for cb in citations['code_blocks']:
            source = cb.get('source', 'No source')
            print(f"  • {cb['language']} ({cb['lines']} lines) - Source: {source}")
        print()

    # Packages
    if citations['packages']:
        print(f"Dependencies ({len(citations['packages'])}):")
        for pkg in citations['packages']:
            print(f"  • {pkg['name']} (v{pkg['version']})")
        print()

    # Quality Metrics
    print("Citation Quality Metrics:")
    print(f"  • File citations: {quality['file_citations']}")
    print(f"  • Web citations: {quality['web_citations']}")
    print(f"  • Code blocks with sources: {quality['code_blocks_with_sources']}/{quality['code_blocks']}")
    print(f"  • Unique domains: {quality['unique_domains']}")
    print(f"  • References section: {'Yes' if quality['has_references_section'] else 'No'}")

    # Validation results
    if validation:
        print("\nValidation:")
        if validation['valid_files']:
            print(f"  ✓ Valid file references: {len(validation['valid_files'])}")
        if validation['invalid_files']:
            print(f"  ✗ Invalid file references: {len(validation['invalid_files'])}")
            for fc in validation['invalid_files'][:5]:
                print(f"      • {fc['path']} (not found)")

    print(f"\n{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(description='Extract and analyze citations from research output')
    parser.add_argument('research_file', help='Research output file to analyze')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format (default: text)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate file citations exist')
    parser.add_argument('--codebase-dir', default='.',
                       help='Root directory of codebase for validation (default: current directory)')
    args = parser.parse_args()

    filepath = Path(args.research_file)

    if not filepath.exists():
        print(f"Error: File '{filepath}' does not exist")
        sys.exit(1)

    try:
        content = filepath.read_text()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Extract all citation types
    citations = {
        'files': extract_file_citations(content),
        'web': extract_web_citations(content),
        'code_blocks': extract_code_blocks(content),
        'packages': extract_package_citations(content)
    }

    # Analyze quality
    quality = analyze_citation_quality(citations)

    # Validate if requested
    validation = None
    if args.validate:
        codebase_dir = Path(args.codebase_dir).resolve()
        validation = validate_citations(citations, codebase_dir)

    # Output results
    if args.format == 'json':
        output = {
            'citations': citations,
            'quality': quality,
            'validation': validation
        }
        print(json.dumps(output, indent=2))
    else:
        print_text_report(citations, quality, validation)

    # Exit code based on quality
    if quality['total_citations'] == 0:
        print("⚠️  Warning: No citations found in document")
        sys.exit(1)
    elif quality['quality_score'] < 50:
        print("⚠️  Warning: Low citation quality score")
        sys.exit(1)
    else:
        print("✅ Citations look good!")
        sys.exit(0)

if __name__ == '__main__':
    main()
