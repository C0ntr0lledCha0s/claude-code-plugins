# Research Output with Citations Template

A template for creating well-cited research outputs with proper source attribution.

---

# Investigation/Research: [Topic Name]

**Date**: YYYY-MM-DD
**Researcher**: [Your name or "Claude (research-agent)"]
**Project**: [Project name]

---

## Summary

[1-2 paragraph overview of findings]

Key findings:
- [Finding 1] [1]
- [Finding 2] [2]
- [Finding 3] [3]

---

## Background

[Context and background information]

[Include citations for any claims or external information]

---

## Findings

### [Finding Category 1]

[Detailed explanation]

**Evidence**:
- File reference: `path/to/file.ts:line-numbers`
- Documentation: [description] [citation number]
- Code example:

```language
// From path/to/file.ts:lines
code snippet here
```

Source: `path/to/file.ts:lines`

**Analysis**:
[Your analysis of this finding]

---

### [Finding Category 2]

[Repeat structure for each major finding]

---

## Code References

All file paths are relative to project root `[project-name]`:

| File | Lines | Description |
|------|-------|-------------|
| `src/component.ts` | 42-88 | Main implementation |
| `src/utils.ts` | 15-30 | Helper functions |
| `tests/component.test.ts` | 10-50 | Test coverage |

---

## Best Practices Analysis

Comparing implementation against industry best practices:

| Practice | Status | Implementation | Reference |
|----------|--------|----------------|-----------|
| [Practice 1] | ✓ | `file.ts:lines` | [citation] |
| [Practice 2] | ⚠ | Partially implemented | [citation] |
| [Practice 3] | ✗ | Not implemented | [citation] |

---

## Patterns Identified

### [Pattern Name]
**Type**: [Creational/Structural/Behavioral/Architectural]
**Location**: `path/to/implementation.ts:lines`
**Reference**: [Pattern definition source] [citation number]

**Purpose**: [Why this pattern is used here]

**Implementation**:
```typescript
// Simplified from path/to/file.ts:lines
code example
```

---

## Dependencies

| Package | Version | Purpose | Documentation |
|---------|---------|---------|---------------|
| [package-1] | vX.Y.Z | [purpose] | [docs link] |
| [package-2] | vX.Y.Z | [purpose] | [docs link] |

---

## Recommendations

### High Priority
1. **[Recommendation 1]** [citation if based on best practice]
   - Rationale: [why this is important]
   - Implementation: [how to implement]
   - Effort: [low/medium/high]

2. **[Recommendation 2]**
   - [Similar structure]

### Medium Priority
[Continue with medium priority items]

### Low Priority / Nice to Have
[Continue with low priority items]

---

## Security Considerations

[Security-related findings with citations to OWASP or security best practices]

- ✓ [Security measure implemented] - `file.ts:lines` [citation]
- ⚠ [Potential concern] [citation]
- ✗ [Missing security measure] [citation]

---

## Performance Considerations

[Performance-related findings with citations to benchmarks or documentation]

- [Performance aspect] - `file.ts:lines` [citation]

---

## Next Steps

- [ ] [Action item 1]
- [ ] [Action item 2]
- [ ] [Action item 3]

---

## References

### Web Sources
[1] [Description] - [Full URL] (accessed YYYY-MM-DD)
[2] [Description] - [Full URL]
[3] [Description] - [Full URL]

### Documentation
[4] [Tool/Framework Name] Documentation - [URL]
[5] [Package Name] (vX.Y.Z) - [URL]

### Books/Articles
[6] [Author Name] - "[Title]" - [Publisher/Website] - [URL if available]

### Code References
All file references are documented inline using backtick format:
- `` `path/to/file.ts:42` ``
- `` `path/to/file.ts:42-88` ``

---

## Appendix

### Validation

This research output has been validated using:

```bash
# File reference validation
python3 scripts/check-evidence.py this-document.md --codebase-dir /path/to/project

# Quality validation
python3 scripts/validate-research.py this-document.md

# Completeness assessment
python3 scripts/assess-completeness.py this-document.md
```

**Results**:
- File references: [X/Y valid]
- Quality score: [X/Y checks passed]
- Completeness: [X%]

### Related Research
- [Link to related investigation]
- [Link to related best practice doc]

### Changelog
- YYYY-MM-DD: Initial research
- YYYY-MM-DD: Updated based on feedback

---

**Generated with**: [Claude Code research-agent plugin](https://github.com/C0ntr0lledCha0s/claude-code-plugin-automations)
