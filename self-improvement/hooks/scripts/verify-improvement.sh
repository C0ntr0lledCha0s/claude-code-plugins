#!/usr/bin/env bash
#
# Verify Improvement Script
# Measures whether patterns are actually decreasing over time
#
# Usage:
#   verify-improvement.sh              # Show improvement report
#   verify-improvement.sh --json       # Output as JSON
#   verify-improvement.sh --pattern missing_tests  # Check specific pattern
#

set -uo pipefail

# Configuration
LOG_DIR="${HOME}/.claude/self-improvement"
PATTERNS_DB="${LOG_DIR}/patterns.json"
METRICS_DB="${LOG_DIR}/metrics.json"
IMPROVEMENT_LOG="${LOG_DIR}/improvement-history.json"

# Parse arguments
OUTPUT_FORMAT="text"
SPECIFIC_PATTERN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            OUTPUT_FORMAT="json"
            shift
            ;;
        --pattern)
            SPECIFIC_PATTERN="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Check dependencies
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 required" >&2
    exit 1
fi

# Ensure data directory exists
mkdir -p "${LOG_DIR}"

# Initialize improvement log if it doesn't exist
if [[ ! -f "${IMPROVEMENT_LOG}" ]]; then
    echo '{"snapshots": [], "trends": {}}' > "${IMPROVEMENT_LOG}"
fi

# Run analysis
python3 - "$PATTERNS_DB" "$METRICS_DB" "$IMPROVEMENT_LOG" "$OUTPUT_FORMAT" "$SPECIFIC_PATTERN" <<'EOF'
import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict

# Get arguments
patterns_file = sys.argv[1]
metrics_file = sys.argv[2]
improvement_file = sys.argv[3]
output_format = sys.argv[4]
specific_pattern = sys.argv[5] if len(sys.argv) > 5 else ""

def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Load data
patterns_data = load_json(patterns_file)
metrics_data = load_json(metrics_file)
improvement_data = load_json(improvement_file)

patterns = patterns_data.get('patterns', [])
sessions = metrics_data.get('sessions', [])
snapshots = improvement_data.get('snapshots', [])

# Calculate current state
now = datetime.now().isoformat()
current_snapshot = {
    "timestamp": now,
    "total_patterns": len(patterns),
    "pattern_counts": {},
    "total_sessions": len(sessions)
}

for pattern in patterns:
    pattern_type = pattern.get('type', 'unknown')
    current_snapshot["pattern_counts"][pattern_type] = pattern.get('count', 0)

# Analyze trends
results = {
    "timestamp": now,
    "summary": "",
    "patterns": [],
    "overall_trend": "unknown",
    "recommendations": []
}

if specific_pattern:
    # Analyze specific pattern
    pattern_data = next((p for p in patterns if p['type'] == specific_pattern), None)
    if pattern_data:
        count = pattern_data.get('count', 0)
        severity = pattern_data.get('severity', 'unknown')
        first_seen = pattern_data.get('first_seen', 'unknown')
        last_seen = pattern_data.get('last_seen', 'unknown')

        # Look at historical data
        historical_counts = []
        for snapshot in snapshots[-10:]:  # Last 10 snapshots
            if specific_pattern in snapshot.get('pattern_counts', {}):
                historical_counts.append(snapshot['pattern_counts'][specific_pattern])

        trend = "stable"
        if len(historical_counts) >= 3:
            recent = sum(historical_counts[-3:]) / 3
            older = sum(historical_counts[:3]) / 3 if len(historical_counts) >= 6 else historical_counts[0]
            if recent < older * 0.7:
                trend = "improving"
            elif recent > older * 1.3:
                trend = "worsening"

        results["patterns"].append({
            "type": specific_pattern,
            "count": count,
            "severity": severity,
            "trend": trend,
            "first_seen": first_seen,
            "last_seen": last_seen,
            "history": historical_counts[-10:]
        })
        results["summary"] = f"Pattern '{specific_pattern}': {count} occurrences, trend: {trend}"
    else:
        results["summary"] = f"Pattern '{specific_pattern}' not found"
        results["overall_trend"] = "not_found"
else:
    # Analyze all patterns
    improving = []
    worsening = []
    stable = []

    for pattern in patterns:
        pattern_type = pattern.get('type', 'unknown')
        count = pattern.get('count', 0)
        severity = pattern.get('severity', 'unknown')

        # Calculate trend from snapshots
        historical_counts = []
        for snapshot in snapshots[-10:]:
            if pattern_type in snapshot.get('pattern_counts', {}):
                historical_counts.append(snapshot['pattern_counts'][pattern_type])

        trend = "stable"
        if len(historical_counts) >= 3:
            recent_avg = sum(historical_counts[-3:]) / 3
            older_avg = sum(historical_counts[:3]) / 3 if len(historical_counts) >= 6 else historical_counts[0]
            if recent_avg < older_avg * 0.7:
                trend = "improving"
                improving.append(pattern_type)
            elif recent_avg > older_avg * 1.3:
                trend = "worsening"
                worsening.append(pattern_type)
            else:
                stable.append(pattern_type)
        else:
            stable.append(pattern_type)

        results["patterns"].append({
            "type": pattern_type,
            "count": count,
            "severity": severity,
            "trend": trend
        })

    # Determine overall trend
    if len(improving) > len(worsening) * 2:
        results["overall_trend"] = "improving"
        results["summary"] = f"Overall improving: {len(improving)} patterns decreasing, {len(worsening)} increasing"
    elif len(worsening) > len(improving) * 2:
        results["overall_trend"] = "worsening"
        results["summary"] = f"Needs attention: {len(worsening)} patterns increasing, {len(improving)} decreasing"
    else:
        results["overall_trend"] = "stable"
        results["summary"] = f"Stable: {len(improving)} improving, {len(worsening)} worsening, {len(stable)} stable"

    # Generate recommendations
    if worsening:
        for pattern_type in worsening[:3]:
            pattern = next((p for p in patterns if p['type'] == pattern_type), {})
            if pattern.get('severity') == 'critical':
                results["recommendations"].append(f"CRITICAL: Address increasing '{pattern_type}' pattern immediately")
            else:
                results["recommendations"].append(f"Review '{pattern_type}' pattern - occurrences increasing")

    if not improving and not worsening:
        results["recommendations"].append("Not enough historical data yet. Continue using the self-improvement system.")

    # Add positive reinforcement
    for pattern_type in improving[:2]:
        results["recommendations"].append(f"Good progress on '{pattern_type}' - keep it up!")

# Save current snapshot for future trend analysis
snapshots.append(current_snapshot)
# Keep only last 50 snapshots
if len(snapshots) > 50:
    snapshots = snapshots[-50:]

improvement_data['snapshots'] = snapshots

try:
    with open(improvement_file, 'w') as f:
        json.dump(improvement_data, f, indent=2)
except Exception:
    pass  # Don't fail if we can't write

# Output results
if output_format == "json":
    print(json.dumps(results, indent=2))
else:
    # Text format
    print("=" * 60)
    print("Self-Improvement Verification Report")
    print("=" * 60)
    print(f"\nTimestamp: {results['timestamp']}")
    print(f"Overall Trend: {results['overall_trend'].upper()}")
    print(f"\n{results['summary']}")

    if results['patterns']:
        print("\n" + "-" * 40)
        print("Pattern Details:")
        print("-" * 40)

        # Sort by severity then trend
        severity_order = {'critical': 0, 'important': 1, 'minor': 2}
        trend_order = {'worsening': 0, 'stable': 1, 'improving': 2}

        sorted_patterns = sorted(
            results['patterns'],
            key=lambda x: (severity_order.get(x['severity'], 3), trend_order.get(x['trend'], 1))
        )

        for p in sorted_patterns:
            trend_icon = {
                'improving': '↓',
                'worsening': '↑',
                'stable': '→'
            }.get(p['trend'], '?')

            severity_color = {
                'critical': '🔴',
                'important': '🟡',
                'minor': '🟢'
            }.get(p['severity'], '⚪')

            print(f"  {severity_color} {p['type']}: {p['count']}x {trend_icon} ({p['trend']})")

    if results['recommendations']:
        print("\n" + "-" * 40)
        print("Recommendations:")
        print("-" * 40)
        for rec in results['recommendations']:
            print(f"  • {rec}")

    print("\n" + "=" * 60)

EOF
