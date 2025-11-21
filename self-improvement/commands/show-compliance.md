---
description: Display compliance statistics showing how often session advice is followed
allowed-tools: Bash, Read
---

# Show Compliance Statistics

Display statistics about how well advice from session start is being followed.

## Instructions

Run the compliance tracker stats command and present the results:

```bash
python3 ~/.claude/plugins/self-improvement/hooks/scripts/compliance-tracker.py stats
```

Present the results clearly:

1. **Overall Compliance Rate** - What percentage of advice is being followed
2. **Recent Trend** - Is compliance improving, declining, or stable
3. **Per-Pattern Breakdown** - Which patterns have low compliance (need attention)
4. **Recommendations** - Actionable suggestions based on the data

If there's no data yet, explain that compliance tracking requires multiple sessions with advice given at session start.

Format the output in a clear, readable way with:
- Percentages as "X%"
- Color-coded indicators (use emojis): ✅ for good (>70%), ⚠️ for moderate (40-70%), ❌ for low (<40%)
- Sort patterns by compliance rate (lowest first)
