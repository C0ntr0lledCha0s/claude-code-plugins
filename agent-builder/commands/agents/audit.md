---
description: Audit all agents in the project for quality, security, and compliance issues
allowed-tools: Read, Grep, Glob, Bash
model: claude-sonnet-4-5
---

# Audit All Agents

Perform comprehensive audit of all agents in the current project.

## Your Task

Scan, analyze, and report on all agents across the project with quality and security scoring.

### 1. **Discovery Phase**

Find all agent files in the project:

```bash
# Project-level agents
find .claude/agents -name "*.md" -type f

# Plugin agents
find . -path "*/agents/*.md" -type f

# User-level agents (optional)
find ~/.claude/agents -name "*.md" -type f
```

Group findings by:
- **Project agents**: `.claude/agents/`
- **Plugin agents**: `<plugin-name>/agents/`
- **User agents**: `~/.claude/agents/`

### 2. **Validation Phase**

For each discovered agent, run:

```bash
python3 agent-builder/skills/building-agents/scripts/validate-agent.py <agent-path>
```

Collect validation results:
- ✅ Pass: Schema valid, no issues
- ⚠️ Warning: Valid but has recommendations
- ❌ Fail: Schema errors, critical issues

### 3. **Analysis Phase**

For each agent, analyze:

#### A. **Schema Compliance** (0-10 points)
- Valid YAML frontmatter (required)
- Name follows conventions
- Description present and clear
- Optional fields properly formatted

#### B. **Security Score** (0-10 points)
- Tool minimalism (fewer tools = higher score)
- No unnecessary Bash access
- No hardcoded secrets or credentials
- Input validation present
- Command injection prevention

#### C. **Content Quality** (0-10 points)
- Clear role definition
- Documented capabilities
- Step-by-step workflow
- Examples present
- Best practices included
- Error handling documented

#### D. **Maintainability** (0-10 points)
- Well-structured and organized
- Clear section headings
- Good documentation
- Easy to understand and modify
- Follows conventions

### 4. **Generate Audit Report**

Create comprehensive report:

```markdown
# Agent Audit Report
Generated: <timestamp>

## Executive Summary

**Total Agents Found**: X
**Passing**: X (✅)
**Warnings**: X (⚠️)
**Failing**: X (❌)

**Average Scores**:
- Schema Compliance: X.X/10
- Security: X.X/10
- Content Quality: X.X/10
- Maintainability: X.X/10
- **Overall**: X.X/10

## Critical Issues 🔴

1. **Agent: <name>** (Location: <path>)
   - Issue: <description>
   - Impact: <severity>
   - Fix: <recommended action>

## Warnings ⚠️

1. **Agent: <name>** (Location: <path>)
   - Warning: <description>
   - Recommendation: <improvement>

## Security Findings 🔒

### High Risk
- [Agent with unnecessary Bash access]
- [Agent with broad tool permissions]

### Medium Risk
- [Agent missing input validation]
- [Agent with unclear security boundaries]

### Low Risk
- [Minor security improvements possible]

## Quality Findings 📊

### Excellent Agents (9-10/10) ✅
- <agent-name>: <score> - <brief note>

### Good Agents (7-8/10) ✅
- <agent-name>: <score> - <brief note>

### Needs Improvement (5-6/10) ⚠️
- <agent-name>: <score> - <key issues>

### Poor Quality (0-4/10) ❌
- <agent-name>: <score> - <critical issues>

## Detailed Agent Analysis

### Project Agents

#### agent-name-1
**Location**: `.claude/agents/agent-name-1.md`
**Status**: ✅ Pass
**Scores**:
- Schema: 10/10
- Security: 8/10
- Quality: 9/10
- Maintainability: 9/10
- **Overall**: 9.0/10

**Findings**:
- ✅ Well-structured with clear workflow
- ✅ Minimal tool permissions
- ⚠️ Could add more examples
- 💡 Consider adding error handling section

**Recommendations**:
1. Add 2-3 concrete examples
2. Document edge cases

---

#### agent-name-2
**Location**: `.claude/agents/agent-name-2.md`
**Status**: ❌ Fail
**Scores**:
- Schema: 4/10
- Security: 3/10
- Quality: 5/10
- Maintainability: 4/10
- **Overall**: 4.0/10

**Critical Issues**:
- ❌ Invalid YAML frontmatter (missing description)
- ❌ Has Bash access but no input validation
- ❌ Missing workflow documentation
- ❌ No examples provided

**Required Actions**:
1. Fix YAML frontmatter syntax
2. Add input validation or remove Bash
3. Document step-by-step workflow
4. Add concrete examples

---

### Plugin Agents

[Similar detailed analysis for plugin agents]

## Compliance Summary

### Schema Compliance
- **Passing**: X/Y agents (Z%)
- **Common issues**:
  - Missing description field (X agents)
  - Invalid YAML syntax (X agents)
  - Name convention violations (X agents)

### Security Compliance
- **High security**: X agents (minimal tools)
- **Medium security**: X agents (standard tools)
- **Low security**: X agents (has Bash/Write)
- **At risk**: X agents (security issues)

### Best Practices Compliance
- **Exemplary**: X agents (follows all guidelines)
- **Good**: X agents (follows most guidelines)
- **Needs work**: X agents (missing key patterns)

## Recommendations by Priority

### Immediate Action Required 🔴
1. Fix invalid schemas (X agents)
2. Address security vulnerabilities (X agents)
3. Remove hardcoded secrets (X agents)

### High Priority 🟡
1. Add missing documentation (X agents)
2. Improve tool permissions (X agents)
3. Add error handling (X agents)

### Medium Priority 🟢
1. Add examples (X agents)
2. Improve descriptions (X agents)
3. Modernize to latest patterns (X agents)

### Low Priority ⚪
1. Formatting improvements (X agents)
2. Optional enhancements (X agents)

## Trends & Patterns

### Common Strengths
- Most agents have valid schema
- Good use of tool minimalism
- Clear role definitions

### Common Weaknesses
- Missing examples (X% of agents)
- Insufficient error handling (X% of agents)
- Over-permissioned tools (X% of agents)

### Evolution Opportunities
- Standardize on latest patterns
- Add comprehensive testing
- Improve documentation
- Enhance security validation

## Automated Fixes Available

The following issues can be auto-fixed:
- [ ] YAML formatting (X agents)
- [ ] Add missing required fields with defaults (X agents)
- [ ] Standardize section headings (X agents)
- [ ] Add template sections (X agents)

Run automated fixes? (y/n)

## Next Steps

1. **Fix critical issues immediately**
   - Use `/agent-builder:agents:update <name>` for each failing agent

2. **Address high priority items**
   - Review security findings
   - Add missing documentation

3. **Enhance overall quality**
   - Use `/agent-builder:agents:enhance <name>` for detailed suggestions
   - Apply best practices consistently

4. **Re-audit to track progress**
   - Run this audit again after fixes
   - Track score improvements over time

## Export Options

Save this report?
- [ ] Save as `agent-audit-report.md`
- [ ] Generate JSON for CI/CD integration
- [ ] Create GitHub issues for critical findings
- [ ] Send summary to stdout only (default)

```

### 5. **Optional: Automated Fixes**

If user opts in, automatically:
- Fix YAML formatting issues
- Add missing required fields with sensible defaults
- Standardize section headings
- Apply consistent formatting

Show diff and confirm before applying each fix.

### 6. **Scoring Algorithm**

```python
def calculate_schema_score(agent):
    score = 0
    if has_valid_yaml: score += 3
    if has_name_and_description: score += 3
    if name_follows_conventions: score += 2
    if description_is_clear: score += 2
    return min(score, 10)

def calculate_security_score(agent):
    score = 10
    if has_bash_without_validation: score -= 4
    if has_write_without_justification: score -= 2
    if has_hardcoded_secrets: score -= 5
    if overly_permissioned: score -= 2
    if missing_input_validation: score -= 1
    return max(score, 0)

def calculate_quality_score(agent):
    score = 0
    if has_role_definition: score += 2
    if has_capabilities: score += 2
    if has_workflow: score += 2
    if has_examples: score += 2
    if has_best_practices: score += 1
    if has_error_handling: score += 1
    return min(score, 10)

def calculate_maintainability_score(agent):
    score = 0
    if well_structured: score += 3
    if has_clear_sections: score += 2
    if good_documentation: score += 3
    if follows_conventions: score += 2
    return min(score, 10)

overall_score = (schema + security + quality + maintainability) / 4
```

## Integration Points

- **validate-agent.py**: Schema validation
- **enhance-agent.py**: Detailed analysis
- **building-agents skill**: Best practices reference
- **Git integration**: Track audit history over time

## Usage Examples

### Basic Audit
```bash
/agent-builder:agents:audit
# Generates full audit report
```

### Audit with Auto-Fix
```bash
/agent-builder:agents:audit
# Review report
> Apply automated fixes? y
# Fixes common issues automatically
```

### Audit + Export
```bash
/agent-builder:agents:audit
# Review report
> Save report? y
# Saves to agent-audit-report.md
```

### CI/CD Integration
```bash
/agent-builder:agents:audit
# Review report
> Generate JSON? y
# Outputs machine-readable JSON
# Can be used in pre-commit hooks or CI pipelines
```

## Related Commands

- `/agent-builder:agents:update [name]` - Fix individual agent issues
- `/agent-builder:agents:enhance [name]` - Get detailed improvement suggestions
- `/agent-builder:agents:compare [agent1] [agent2]` - Compare two agents

---

**Purpose**: This command provides project-wide visibility into agent quality, security, and compliance. Use it regularly to maintain high standards across all agents.
