#!/usr/bin/env python3
"""
Enhance Agent Script - Deep analysis and improvement suggestions
Part of the agent-builder plugin for Claude Code
"""

import sys
import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional

def find_agent(agent_name: str) -> Optional[Path]:
    """Find agent file in common locations."""
    search_paths = [
        Path(".claude/agents"),
        Path.home() / ".claude" / "agents",
        Path("."),
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        agent_file = search_path / f"{agent_name}.md"
        if agent_file.exists():
            return agent_file

        for agent_file in search_path.rglob(f"{agent_name}.md"):
            if agent_file.parent.name == "agents":
                return agent_file

    return None

def parse_agent(file_path: Path) -> Tuple[Dict, str]:
    """Parse agent file into frontmatter and body."""
    content = file_path.read_text()

    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if not match:
        raise ValueError("Invalid agent file: missing YAML frontmatter")

    frontmatter_text, body = match.groups()
    frontmatter = yaml.safe_load(frontmatter_text)

    return frontmatter, body

def analyze_schema(frontmatter: Dict) -> Tuple[int, List[str]]:
    """Analyze schema compliance. Returns (score, issues)."""
    score = 0
    issues = []

    # Required fields
    if 'name' in frontmatter:
        score += 3
        if not re.match(r'^[a-z0-9-]+$', frontmatter['name']):
            issues.append("⚠️  Name doesn't follow lowercase-hyphen convention")
        if len(frontmatter['name']) > 64:
            issues.append("⚠️  Name exceeds 64 character limit")
    else:
        issues.append("❌ Missing required 'name' field")

    if 'description' in frontmatter:
        score += 3
        if len(frontmatter['description']) > 1024:
            issues.append("⚠️  Description exceeds 1024 character limit")
        if len(frontmatter['description']) < 20:
            issues.append("⚠️  Description too short, not actionable")
    else:
        issues.append("❌ Missing required 'description' field")

    # Optional fields
    if 'tools' in frontmatter:
        score += 2
    if 'model' in frontmatter:
        score += 2

    return min(score, 10), issues

def analyze_security(frontmatter: Dict, body: str) -> Tuple[int, List[str]]:
    """Analyze security. Returns (score, findings)."""
    score = 10
    findings = []

    tools = frontmatter.get('tools', '')

    # Check for Bash access
    if 'Bash' in tools:
        score -= 2
        if 'validation' not in body.lower() and 'sanitize' not in body.lower():
            score -= 2
            findings.append("❌ Has Bash access without input validation documentation")
        else:
            findings.append("⚠️  Has Bash access - ensure input validation is thorough")

    # Check for Write access
    if 'Write' in tools or 'Edit' in tools:
        if not any(word in body.lower() for word in ['validate', 'check', 'verify']):
            score -= 1
            findings.append("⚠️  Has write access - consider adding validation checks")

    # Check for hardcoded secrets
    secret_patterns = [
        r'api[_-]?key',
        r'password',
        r'secret',
        r'token',
        r'credential',
    ]

    for pattern in secret_patterns:
        if re.search(pattern, body, re.IGNORECASE):
            # Check if it's in a documentation context
            if not re.search(f'{pattern}.*example|{pattern}.*placeholder', body, re.IGNORECASE):
                score -= 3
                findings.append(f"❌ Possible hardcoded secret: '{pattern}' found in body")
                break

    # Tool minimalism
    if tools:
        tool_count = len([t.strip() for t in tools.split(',')])
        if tool_count > 6:
            score -= 1
            findings.append("⚠️  Many tools granted - consider minimizing permissions")

    if not findings:
        findings.append("✅ No security issues detected")

    return max(score, 0), findings

def analyze_content_quality(body: str) -> Tuple[int, List[str]]:
    """Analyze content quality. Returns (score, findings)."""
    score = 0
    findings = []

    sections = {
        'role': r'(?:role|you are)',
        'capabilities': r'capabilit(?:y|ies)',
        'workflow': r'workflow|steps?|process',
        'examples': r'example',
        'best practices': r'best practices|guidelines',
        'error handling': r'error|exception|fail',
    }

    for section_name, pattern in sections.items():
        if re.search(pattern, body, re.IGNORECASE):
            score += 1.5
        else:
            findings.append(f"⚠️  Missing or unclear '{section_name}' section")

    # Check for examples count
    example_count = len(re.findall(r'##\s*example', body, re.IGNORECASE))
    if example_count == 0:
        findings.append("❌ No examples provided - add 2-3 concrete examples")
    elif example_count == 1:
        findings.append("⚠️  Only one example - consider adding more")
    else:
        score += 1
        findings.append(f"✅ Has {example_count} examples")

    # Check word count
    word_count = len(body.split())
    if word_count < 100:
        findings.append("⚠️  Very brief content - consider adding more detail")
    elif word_count > 2000:
        findings.append("⚠️  Very lengthy content - consider condensing")

    if not [f for f in findings if f.startswith('⚠️') or f.startswith('❌')]:
        findings.append("✅ Content is well-structured")

    return min(score, 10), findings

def analyze_maintainability(body: str) -> Tuple[int, List[str]]:
    """Analyze maintainability. Returns (score, findings)."""
    score = 0
    findings = []

    # Check for clear headings
    heading_count = len(re.findall(r'^#{1,3}\s+\w+', body, re.MULTILINE))
    if heading_count >= 5:
        score += 3
    elif heading_count >= 3:
        score += 2
        findings.append("⚠️  Could use more section headings for clarity")
    else:
        score += 1
        findings.append("⚠️  Add more headings to organize content")

    # Check for lists and structure
    if re.search(r'^\s*[-*]\s+', body, re.MULTILINE):
        score += 2
    else:
        findings.append("⚠️  Consider using lists for better readability")

    # Check for code blocks
    if '```' in body:
        score += 2
    else:
        findings.append("⚠️  Consider adding code examples in code blocks")

    # Check for clear formatting
    if re.search(r'\*\*.*?\*\*', body):  # Bold text
        score += 1
    if re.search(r'`.*?`', body):  # Inline code
        score += 1

    # Check line length (readability)
    long_lines = [line for line in body.split('\n') if len(line) > 120]
    if len(long_lines) > body.count('\n') * 0.2:  # More than 20% long lines
        findings.append("⚠️  Many long lines - consider breaking them up for readability")

    if not [f for f in findings if f.startswith('⚠️')]:
        findings.append("✅ Well-formatted and maintainable")

    return min(score, 10), findings

def generate_recommendations(frontmatter: Dict, body: str, all_scores: Dict) -> List[str]:
    """Generate prioritized recommendations."""
    recommendations = []

    # Critical issues
    if all_scores['schema'] < 5:
        recommendations.append("🔴 CRITICAL: Fix schema issues immediately")

    if all_scores['security'] < 5:
        recommendations.append("🔴 CRITICAL: Address security vulnerabilities")

    # High priority
    if all_scores['quality'] < 6:
        recommendations.append("🟡 HIGH: Improve content quality (add examples, workflow)")

    if 'Bash' in frontmatter.get('tools', ''):
        recommendations.append("🟡 HIGH: Document input validation for Bash commands")

    # Medium priority
    if all_scores['maintainability'] < 7:
        recommendations.append("🟢 MEDIUM: Improve formatting and structure")

    # Model optimization
    model = frontmatter.get('model', 'inherit')
    if model == 'opus' and 'simple' in frontmatter.get('description', '').lower():
        recommendations.append("🟢 MEDIUM: Consider using 'haiku' model for simple tasks (faster, cheaper)")

    if model == 'haiku' and ('complex' in frontmatter.get('description', '').lower() or
                              'analysis' in frontmatter.get('description', '').lower()):
        recommendations.append("🟢 MEDIUM: Consider using 'sonnet' model for complex tasks")

    # Tool optimization
    tools = frontmatter.get('tools', '')
    if 'Write' in tools and 'Edit' in tools:
        recommendations.append("🟢 LOW: Both Write and Edit granted - choose one if possible")

    if not recommendations:
        recommendations.append("✅ No major improvements needed - agent is well-designed!")

    return recommendations

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 enhance-agent.py <agent-name>")
        print("\nExample: python3 enhance-agent.py code-reviewer")
        sys.exit(1)

    agent_name = sys.argv[1].replace('.md', '')

    # Find agent
    print(f"Analyzing agent: {agent_name}...\n")
    agent_path = find_agent(agent_name)

    if not agent_path:
        print(f"❌ Agent not found: {agent_name}")
        sys.exit(1)

    # Parse agent
    try:
        frontmatter, body = parse_agent(agent_path)
    except Exception as e:
        print(f"❌ Failed to parse agent: {e}")
        sys.exit(1)

    # Run analyses
    print("="*60)
    print(f"Enhancement Analysis: {agent_name}")
    print("="*60)
    print(f"Location: {agent_path}\n")

    schema_score, schema_issues = analyze_schema(frontmatter)
    security_score, security_findings = analyze_security(frontmatter, body)
    quality_score, quality_findings = analyze_content_quality(body)
    maintainability_score, maintainability_findings = analyze_maintainability(body)

    overall_score = (schema_score + security_score + quality_score + maintainability_score) / 4

    print(f"Overall Score: {overall_score:.1f}/10\n")

    # Display scores
    print("Detailed Scores:")
    print(f"  Schema Compliance:  {schema_score}/10")
    print(f"  Security:           {security_score}/10")
    print(f"  Content Quality:    {quality_score}/10")
    print(f"  Maintainability:    {maintainability_score}/10")
    print()

    # Display findings
    if schema_issues:
        print("Schema & Structure:")
        for issue in schema_issues:
            print(f"  {issue}")
        print()

    print("Security Analysis:")
    for finding in security_findings:
        print(f"  {finding}")
    print()

    print("Content Quality:")
    for finding in quality_findings:
        print(f"  {finding}")
    print()

    print("Maintainability:")
    for finding in maintainability_findings:
        print(f"  {finding}")
    print()

    # Generate recommendations
    all_scores = {
        'schema': schema_score,
        'security': security_score,
        'quality': quality_score,
        'maintainability': maintainability_score,
    }

    recommendations = generate_recommendations(frontmatter, body, all_scores)

    print("="*60)
    print("Recommendations (Prioritized)")
    print("="*60)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    print()

    # Next steps
    print("="*60)
    print("Next Steps")
    print("="*60)
    print("1. Review recommendations above")
    print(f"2. Run: python3 update-agent.py {agent_name}")
    print("3. Apply improvements interactively")
    print(f"4. Re-run: python3 enhance-agent.py {agent_name}")
    print("5. Verify score improved")
    print()

    # Exit with status
    if overall_score >= 8:
        print("✅ Excellent agent! Only minor improvements possible.")
        sys.exit(0)
    elif overall_score >= 6:
        print("✅ Good agent. Some improvements recommended.")
        sys.exit(0)
    else:
        print("⚠️  Agent needs improvement. Please address findings above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
