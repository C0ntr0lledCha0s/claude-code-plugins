#!/usr/bin/env python3
"""
Assess completeness of research output.
Usage: python assess-completeness.py <research-output-file> [--threshold <percentage>]
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

def assess_research_completeness(text: str) -> Dict[str, any]:
    """Assess how complete and thorough the research output is."""

    metrics = {}

    # 1. Section Completeness
    expected_sections = [
        r'##?\s*(Summary|Overview)',
        r'##?\s*(Background|Context)',
        r'##?\s*(Implementation|Approach|How)',
        r'##?\s*(Evidence|Examples|Findings)',
        r'##?\s*(Recommendations|Conclusions)',
    ]

    sections_found = sum(1 for pattern in expected_sections if re.search(pattern, text, re.IGNORECASE))
    metrics['section_coverage'] = (sections_found / len(expected_sections)) * 100

    # 2. Evidence Depth
    file_refs = len(re.findall(r'`[^`]+:\d+(-\d+)?`', text))
    code_blocks = len(re.findall(r'```[\s\S]*?```', text))
    metrics['evidence_count'] = file_refs + code_blocks
    metrics['has_strong_evidence'] = (file_refs >= 3 or code_blocks >= 2)

    # 3. Explanation Quality
    word_count = len(text.split())
    metrics['word_count'] = word_count
    metrics['sufficient_detail'] = word_count >= 500  # Minimum for thorough research

    # 4. Structural Elements
    bullet_points = len(re.findall(r'^\s*[-*+]\s', text, re.MULTILINE))
    numbered_lists = len(re.findall(r'^\s*\d+\.\s', text, re.MULTILINE))
    headings = len(re.findall(r'^#{1,6}\s', text, re.MULTILINE))

    metrics['has_organization'] = (bullet_points >= 5 or numbered_lists >= 3) and headings >= 3

    # 5. Actionability
    action_keywords = ['recommend', 'suggest', 'should', 'consider', 'next steps', 'todo', 'follow-up']
    action_count = sum(text.lower().count(keyword) for keyword in action_keywords)
    metrics['actionable'] = action_count >= 3

    # 6. Breadth vs Depth Balance
    unique_topics = len(set(re.findall(r'##\s*([^\n]+)', text)))
    avg_section_length = word_count / max(unique_topics, 1)
    metrics['unique_topics'] = unique_topics
    metrics['avg_section_length'] = int(avg_section_length)
    metrics['balanced_coverage'] = 100 <= avg_section_length <= 400  # Not too shallow, not too focused

    # 7. Technical Accuracy Indicators
    has_specifics = bool(re.search(r'(line \d+|version \d+|\d+ms|\d+%|bytes|KB|MB)', text))
    has_technical_terms = bool(re.search(r'(function|class|method|API|endpoint|database|query|cache)', text, re.IGNORECASE))
    metrics['technical_depth'] = has_specifics and has_technical_terms

    # Overall Completeness Score
    completeness_factors = [
        metrics['section_coverage'] >= 80,
        metrics['has_strong_evidence'],
        metrics['sufficient_detail'],
        metrics['has_organization'],
        metrics['actionable'],
        metrics['balanced_coverage'],
        metrics['technical_depth'],
    ]

    metrics['completeness_score'] = (sum(completeness_factors) / len(completeness_factors)) * 100

    return metrics

def categorize_completeness(score: float) -> Tuple[str, str]:
    """Categorize completeness level."""
    if score >= 85:
        return "Excellent", "✅"
    elif score >= 70:
        return "Good", "✓"
    elif score >= 50:
        return "Adequate", "⚠️"
    else:
        return "Incomplete", "❌"

def print_assessment(metrics: Dict, filename: str, threshold: float):
    """Print completeness assessment."""
    category, symbol = categorize_completeness(metrics['completeness_score'])

    print(f"\n{'='*60}")
    print(f"Research Completeness Assessment: {filename}")
    print(f"{'='*60}\n")

    print(f"Overall Completeness: {metrics['completeness_score']:.1f}% - {category} {symbol}\n")

    print("Detailed Metrics:")
    print(f"  • Section Coverage: {metrics['section_coverage']:.0f}%")
    print(f"  • Evidence Items: {metrics['evidence_count']} (Strong: {'Yes' if metrics['has_strong_evidence'] else 'No'})")
    print(f"  • Word Count: {metrics['word_count']} (Sufficient: {'Yes' if metrics['sufficient_detail'] else 'No'})")
    print(f"  • Organization: {'Well-structured' if metrics['has_organization'] else 'Needs improvement'}")
    print(f"  • Actionability: {'Yes' if metrics['actionable'] else 'No'}")
    print(f"  • Topics Covered: {metrics['unique_topics']}")
    print(f"  • Avg Section Length: {metrics['avg_section_length']} words")
    print(f"  • Balance: {'Good' if metrics['balanced_coverage'] else 'Too shallow/focused'}")
    print(f"  • Technical Depth: {'Yes' if metrics['technical_depth'] else 'No'}")

    print(f"\n{'='*60}")

    if metrics['completeness_score'] >= threshold:
        print(f"✅ Research meets completeness threshold ({threshold}%)")
        return 0
    else:
        print(f"❌ Research below completeness threshold ({threshold}%)")
        print("\nSuggestions for improvement:")

        if metrics['section_coverage'] < 80:
            print("  • Add missing sections (Background, Implementation, Evidence, Recommendations)")
        if not metrics['has_strong_evidence']:
            print("  • Include more file references and code examples")
        if not metrics['sufficient_detail']:
            print("  • Expand explanations and provide more context")
        if not metrics['has_organization']:
            print("  • Add bullet points, numbered lists, and clear headings")
        if not metrics['actionable']:
            print("  • Include recommendations and next steps")
        if not metrics['balanced_coverage']:
            print("  • Balance breadth and depth (aim for 100-400 words per section)")
        if not metrics['technical_depth']:
            print("  • Add specific technical details (line numbers, metrics, terminology)")

        return 1

def main():
    parser = argparse.ArgumentParser(description='Assess research output completeness')
    parser.add_argument('research_file', help='Research output file to assess')
    parser.add_argument('--threshold', type=float, default=70.0,
                       help='Minimum completeness percentage (default: 70)')
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

    metrics = assess_research_completeness(content)
    exit_code = print_assessment(metrics, filepath.name, args.threshold)

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
