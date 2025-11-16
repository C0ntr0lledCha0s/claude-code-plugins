# Comparative Analysis Framework Guide

How to use the weighted comparison framework for objective technology decision-making.

## Overview

The comparative analysis framework provides a structured, quantitative approach to technology decisions. Instead of subjective opinions, you systematically evaluate options against weighted criteria to make objective, defensible choices.

**Benefits**:
- **Objective**: Numbers-based, not gut-feel
- **Transparent**: Clear reasoning for decisions
- **Defensible**: Stakeholders can see trade-offs
- **Reproducible**: Consistent methodology
- **Sensitivity-Aware**: Shows how robust the decision is

---

## Quick Start

### 5-Step Process

1. **Define options**: What are you comparing?
2. **Select criteria**: Use the [decision-criteria-catalog.md](./decision-criteria-catalog.md)
3. **Assign weights**: Based on your priorities (must sum to 1.0)
4. **Rate each option**: Score 1-10 for each criterion
5. **Calculate scores**: Weighted average determines winner

### Example in 5 Minutes

**Question**: Redux vs Zustand for React state management?

**1. Options**: Redux, Zustand

**2. Criteria** (from catalog):
- Developer Experience
- Learning Curve
- Performance
- Type Safety
- DevTools

**3. Weights** (your priorities):
```
DX: 0.30 (most important - team productivity)
Learning: 0.25 (new team members joining)
Performance: 0.20 (need good UX)
TypeScript: 0.15 (already using TS)
DevTools: 0.10 (nice but not critical)
Total: 1.00 ✓
```

**4. Ratings**:
| Criterion | Redux | Zustand |
|-----------|-------|---------|
| DX | 6/10 | 9/10 |
| Learning | 5/10 | 9/10 |
| Performance | 8/10 | 9/10 |
| TypeScript | 8/10 | 8/10 |
| DevTools | 10/10 | 6/10 |

**5. Calculate**:
```
Redux:   (0.30×6) + (0.25×5) + (0.20×8) + (0.15×8) + (0.10×10) = 6.65/10
Zustand: (0.30×9) + (0.25×9) + (0.20×9) + (0.15×8) + (0.10×6)  = 8.55/10

Winner: Zustand (8.55 vs 6.65)
```

**Decision**: Choose Zustand - significantly better on our top priorities (DX, learning curve).

---

## Detailed Workflow

### Step 1: Define the Comparison

**Be Specific**:
- ❌ Bad: "Which framework?"
- ✅ Good: "React vs Vue for new e-commerce app"

**Document Context**:
- What are you building?
- What are your constraints?
- Who are the stakeholders?
- When do you need to decide?

**Template Section**: Executive Summary

---

### Step 2: Select Criteria

Use the [decision-criteria-catalog.md](./decision-criteria-catalog.md) to select relevant criteria.

**Guidelines**:
- Include 5-10 criteria (not too few, not too many)
- Cover different dimensions (performance, cost, DX, etc.)
- Be relevant to your specific use case
- Consider both short-term and long-term factors

**Common Criteria Sets**:

**General Tech Selection**:
- Performance
- Developer Experience
- Learning Curve
- Community Support
- Maturity
- Cost

**Framework/Library**:
- DX
- Learning Curve
- Ecosystem
- Performance
- Documentation
- Type Safety

**Architecture**:
- Complexity
- Scalability
- Flexibility
- Testability
- Team Familiarity
- Maintainability

**Template Section**: Decision Criteria table

---

### Step 3: Assign Weights

Weights represent how important each criterion is to YOUR situation.

**Rules**:
- Must sum to exactly 1.0
- Range: 0.05 to 0.40 per criterion
- Top priorities get 0.20-0.35
- Secondary factors get 0.10-0.20
- Nice-to-haves get 0.05-0.10

**Process**:

1. **Rank criteria by importance**
   ```
   1. Developer Experience (most important)
   2. Learning Curve
   3. Performance
   4. Community
   5. Cost
   ```

2. **Assign rough percentages**
   ```
   DX: ~35%
   Learning: ~25%
   Performance: ~20%
   Community: ~15%
   Cost: ~5%
   Total: 100%
   ```

3. **Convert to decimals** (divide by 100)
   ```
   DX: 0.35
   Learning: 0.25
   Performance: 0.20
   Community: 0.15
   Cost: 0.05
   Total: 1.00 ✓
   ```

**Validation**:
- [ ] Sum = 1.0
- [ ] No weight > 0.40
- [ ] Top 3 weights reflect priorities
- [ ] Stakeholders agree

**Use Presets**: See catalog for startup, enterprise, performance-critical profiles.

**Template Section**: Decision Criteria (Weight column)

---

### Step 4: Rate Each Option

Rate each option for each criterion on a 1-10 scale.

**Rating Scale**:
- **9-10**: Excellent, best-in-class
- **7-8**: Good, above average
- **4-6**: Adequate, meets basics
- **1-3**: Poor, below requirements

**Guidelines**:

**Be Objective**:
- Use benchmarks when available
- Cite evidence (documentation, benchmarks, examples)
- Compare to alternatives, not perfection
- Don't let bias influence scores

**Be Consistent**:
- Use same scale for all options
- Rate relative to each other
- Document reasoning for each score

**Be Honest**:
- No perfect 10s just because you like it
- Acknowledge weaknesses
- Half-point precision okay (7.5/10)

**Example Rating Process**:

**Criterion**: Developer Experience
**Option A** (Redux):
- Evidence: Verbose boilerplate, actions/reducers separation
- Comparison: More code than alternatives
- Score: 6/10 (adequate but clunky)
- Justification: "Functional but requires significant boilerplate for simple state updates"

**Option B** (Zustand):
- Evidence: Minimal API, direct state mutation
- Comparison: Much less code than Redux
- Score: 9/10 (excellent)
- Justification: "Intuitive API, minimal boilerplate, pleasant to use"

**Template Sections**:
- Decision Criteria table (score columns)
- Detailed Analysis (per-criterion justifications)

---

### Step 5: Calculate Weighted Scores

**Formula**:
```
Weighted Score = (Weight₁ × Score₁) + (Weight₂ × Score₂) + ... + (Weightₙ × Scoreₙ)
```

**Example**:
```
Option A:
= (0.30 × 6) + (0.25 × 5) + (0.20 × 8) + (0.15 × 8) + (0.10 × 10)
= 1.80 + 1.25 + 1.60 + 1.20 + 1.00
= 6.85/10

Option B:
= (0.30 × 9) + (0.25 × 9) + (0.20 × 9) + (0.15 × 8) + (0.10 × 6)
= 2.70 + 2.25 + 1.80 + 1.20 + 0.60
= 8.55/10

Winner: Option B (8.55 > 6.85)
Margin: 1.70 points (significant)
```

**Interpretation**:
- **> 1.5 difference**: Clear winner
- **0.5-1.5 difference**: Moderate preference
- **< 0.5 difference**: Too close to call

**Template Section**: Decision Criteria table (bottom row)

---

## Sensitivity Analysis

After calculating scores, test how robust your decision is.

### Why Sensitivity Analysis?

Weights are subjective. What if they're wrong? Sensitivity analysis shows:
- How confident you should be in the decision
- Which criteria are most influential
- What would change the outcome

### How to Perform

**Method 1: Weight Variation**

Pick your most uncertain weight and vary it:

```
Base case:
  Performance: 0.20 → Option A wins (7.2 vs 7.0)

If Performance weight = 0.30:
  Option A: 7.5
  Option B: 7.1
  Still winner ✓

If Performance weight = 0.10:
  Option A: 6.9
  Option B: 6.9
  Too close to call!
```

**Interpretation**: Decision is sensitive to performance weight. Need more confidence in performance assessment.

**Method 2: Scenario Testing**

Test different stakeholder perspectives:

```
Scenario 1: Developer emphasis
  DX: 0.40, Learning: 0.30, Performance: 0.15, ...
  → Option B wins decisively

Scenario 2: Performance emphasis
  Performance: 0.40, DX: 0.20, Learning: 0.20, ...
  → Option A wins narrowly

Scenario 3: Balanced
  All weights equal (0.20 each)
  → Option B wins narrowly
```

**Interpretation**: Option B is the robust choice - wins in most scenarios.

**Method 3: Critical Threshold**

Find the weight threshold where the decision flips:

```
Option B wins when DX weight > 0.XX
Option A wins when Performance weight > 0.XX
```

**Template Section**: Sensitivity Analysis

---

## Advanced Techniques

### Multi-Option Comparison (3+ options)

Same process, just more columns:

| Criterion | Weight | A | B | C |
|-----------|--------|---|---|---|
| DX | 0.30 | 6 | 9 | 7 |
| Speed | 0.25 | 8 | 7 | 9 |
| ... | ... | ... | ... | ... |
| **Score** | **1.00** | **7.1** | **8.0** | **7.8** |

**Winner**: B (8.0), with C close second (7.8)

### Hierarchical Criteria

Nest sub-criteria under main criteria:

```
Performance (0.30):
  - Speed (0.50 of performance) → 0.15 total
  - Memory (0.30 of performance) → 0.09 total
  - Latency (0.20 of performance) → 0.06 total
```

### Disqualifying Factors

Some criteria are pass/fail:

```
Security: Must be 8+/10
If Option A scores 6/10 → Disqualified regardless of other scores
```

### Uncertainty Ranges

If unsure about a score, use ranges:

```
Option A Performance: 7-9/10
Option B Performance: 8-10/10

Best case for A vs Worst case for B: 9 vs 8 → A wins
Worst case for A vs Best case for B: 7 vs 10 → B wins

Conclusion: Need more performance data
```

---

## Best Practices

### Do's ✅

1. **Document Everything**
   - Why each weight was chosen
   - Evidence for each score
   - Stakeholders consulted

2. **Be Honest**
   - No favorite gets a free pass
   - Acknowledge weaknesses
   - Use objective evidence

3. **Get Input**
   - Multiple perspectives
   - Domain experts
   - End users

4. **Review and Iterate**
   - Sense-check the results
   - Adjust if something feels off
   - Re-validate with stakeholders

5. **Consider Context**
   - Your specific situation
   - Team capabilities
   - Long-term implications

### Don'ts ❌

1. **Don't Game the System**
   - Adjusting weights to get desired outcome
   - Cherry-picking criteria
   - Inflating/deflating scores

2. **Don't Over-Engineer**
   - Too many criteria (> 15)
   - Excessive precision (7.42/10)
   - Complex hierarchies

3. **Don't Ignore Red Flags**
   - If the "winner" feels wrong, investigate
   - May have wrong weights or criteria
   - May be missing a criterion

4. **Don't Decide Once and Forget**
   - Revisit when circumstances change
   - Update as new information emerges
   - Schedule reviews (every 6-12 months)

---

## Common Pitfalls

### Problem: All scores are similar (7-8 range)
**Solution**: Use full scale. Spread scores more.

### Problem: Weights are all equal (0.20 each)
**Solution**: Forces prioritization. What REALLY matters?

### Problem: Winner changes with tiny weight adjustments
**Solution**: Decision is too close. Gather more data or accept either option.

### Problem: Unexpected winner
**Solution**: Double-check weights and scores. May have discovered something.

### Problem: Team disagrees on winner
**Solution**: Have them each do independent weighting. Compare.

---

## Templates

### Use These Templates

1. **[comparison-framework-template.md](./comparison-framework-template.md)**
   - Complete template with all sections
   - Copy and fill out

2. **[decision-criteria-catalog.md](./decision-criteria-catalog.md)**
   - Criteria library
   - Weight suggestions
   - Rating guides

### Example Comparisons

See `examples/` directory for complete worked examples:
- `rest-vs-graphql.md` - API pattern comparison
- `redux-vs-zustand.md` - State management comparison
- `postgres-vs-mongodb.md` - Database comparison

---

## Integration with Research Agent

### Before Research

1. **Identify need for comparison**
2. **Select template**
3. **Choose criteria from catalog**

### During Research

Use research commands to gather data:

```bash
/investigate [technology] # Implementation details
/best-practice [technology] # Industry standards
/research [technology] benchmark # Performance data
```

### After Research

1. **Fill in template** with findings
2. **Calculate scores**
3. **Run sensitivity analysis**
4. **Cache result** for future reference:
   ```bash
   python3 scripts/cache-manager.py add comparisons \
     "Redux vs Zustand comparison" \
     redux-vs-zustand-comparison.md \
     --tags "react,state,comparison"
   ```

---

## Validation Checklist

Before finalizing your comparison:

- [ ] All criteria are relevant to your use case
- [ ] Weights sum to 1.0
- [ ] Weights reflect your priorities
- [ ] Scores are evidence-based
- [ ] Scores use full 1-10 range
- [ ] Justifications provided for each score
- [ ] Calculation is correct
- [ ] Sensitivity analysis performed
- [ ] Result makes intuitive sense
- [ ] Stakeholders have reviewed
- [ ] Decision is documented
- [ ] Next review date set

---

## FAQ

**Q: Can I use this for non-technical decisions?**
A: Yes! Any decision with multiple options and criteria works.

**Q: How many criteria should I use?**
A: 5-10 is ideal. Fewer lacks nuance, more is overwhelming.

**Q: What if I can't decide on weights?**
A: Try preset profiles from catalog, or use equal weights as starting point.

**Q: Should I always choose the highest score?**
A: Usually, but consider: margin of victory, sensitivity, gut check.

**Q: Can I adjust scores later?**
A: Yes, as you learn more. Document the change and reasoning.

**Q: What if two options are tied?**
A: Either is fine! Pick based on secondary factors or flip a coin.

---

**Last Updated**: 2025-01-15
**Version**: 1.0.0
