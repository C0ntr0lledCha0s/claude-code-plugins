#!/usr/bin/env python3
"""
Compliance Tracker

Tracks whether session-start advice is actually followed during the session.
This closes the feedback loop by measuring if interventions are effective.

Usage:
    # Record advice given at session start
    compliance-tracker.py record <session_id> <advice_json>

    # Check compliance at session end
    compliance-tracker.py check <session_id> <patterns_found_json>

    # Get compliance statistics
    compliance-tracker.py stats
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


# Configuration
LOG_DIR = Path.home() / ".claude" / "self-improvement"
COMPLIANCE_DB = LOG_DIR / "compliance.json"
CURRENT_SESSION = LOG_DIR / "current-session-advice.json"


def ensure_db():
    """Ensure the compliance database exists."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not COMPLIANCE_DB.exists():
        COMPLIANCE_DB.write_text(json.dumps({
            "sessions": [],
            "aggregate": {
                "total_advice_given": 0,
                "total_advice_followed": 0,
                "by_pattern": {}
            }
        }, indent=2))


def record_advice(session_id: str, advice: list[str]) -> dict:
    """
    Record advice given at the start of a session.

    Args:
        session_id: Unique session identifier
        advice: List of pattern types that were warned about

    Returns:
        Status dict
    """
    ensure_db()

    # Save current session advice for later checking
    session_data = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "advice_given": advice,
        "status": "active"
    }

    CURRENT_SESSION.write_text(json.dumps(session_data, indent=2))

    return {
        "status": "recorded",
        "advice_count": len(advice),
        "patterns": advice
    }


def check_compliance(session_id: str, patterns_found: list[str]) -> dict:
    """
    Check if advice was followed by comparing against patterns found.

    Args:
        session_id: Unique session identifier
        patterns_found: List of patterns detected in the session

    Returns:
        Compliance report
    """
    ensure_db()

    # Load current session advice
    if not CURRENT_SESSION.exists():
        return {
            "status": "no_advice",
            "message": "No advice was recorded for this session"
        }

    try:
        session_data = json.loads(CURRENT_SESSION.read_text())
    except json.JSONDecodeError:
        return {"status": "error", "message": "Failed to read session data"}

    advice_given = set(session_data.get("advice_given", []))
    patterns_found_set = set(patterns_found)

    # Calculate compliance
    # Advice is "followed" if the pattern did NOT appear in the session
    advice_followed = advice_given - patterns_found_set
    advice_ignored = advice_given & patterns_found_set

    compliance_rate = len(advice_followed) / len(advice_given) if advice_given else 1.0

    # Build result
    result = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "advice_given": list(advice_given),
        "advice_followed": list(advice_followed),
        "advice_ignored": list(advice_ignored),
        "compliance_rate": round(compliance_rate, 2),
        "status": "checked"
    }

    # Update database
    update_compliance_db(result)

    # Clean up current session file
    if CURRENT_SESSION.exists():
        CURRENT_SESSION.unlink()

    return result


def update_compliance_db(result: dict):
    """Update the compliance database with session results."""
    try:
        data = json.loads(COMPLIANCE_DB.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        data = {"sessions": [], "aggregate": {"total_advice_given": 0, "total_advice_followed": 0, "by_pattern": {}}}

    # Add session result
    data["sessions"].append(result)

    # Keep only last 100 sessions
    if len(data["sessions"]) > 100:
        data["sessions"] = data["sessions"][-100:]

    # Update aggregates
    data["aggregate"]["total_advice_given"] += len(result["advice_given"])
    data["aggregate"]["total_advice_followed"] += len(result["advice_followed"])

    # Track per-pattern compliance
    for pattern in result["advice_given"]:
        if pattern not in data["aggregate"]["by_pattern"]:
            data["aggregate"]["by_pattern"][pattern] = {
                "given": 0,
                "followed": 0,
                "ignored": 0
            }

        data["aggregate"]["by_pattern"][pattern]["given"] += 1

        if pattern in result["advice_followed"]:
            data["aggregate"]["by_pattern"][pattern]["followed"] += 1
        else:
            data["aggregate"]["by_pattern"][pattern]["ignored"] += 1

    COMPLIANCE_DB.write_text(json.dumps(data, indent=2))


def get_stats() -> dict:
    """Get overall compliance statistics."""
    ensure_db()

    try:
        data = json.loads(COMPLIANCE_DB.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return {"status": "no_data", "message": "No compliance data yet"}

    aggregate = data.get("aggregate", {})
    total_given = aggregate.get("total_advice_given", 0)
    total_followed = aggregate.get("total_advice_followed", 0)

    overall_rate = total_followed / total_given if total_given > 0 else 0

    # Calculate per-pattern rates
    pattern_stats = []
    for pattern, stats in aggregate.get("by_pattern", {}).items():
        given = stats.get("given", 0)
        followed = stats.get("followed", 0)
        rate = followed / given if given > 0 else 0

        pattern_stats.append({
            "pattern": pattern,
            "times_advised": given,
            "times_followed": followed,
            "compliance_rate": round(rate, 2)
        })

    # Sort by compliance rate (lowest first - needs most attention)
    pattern_stats.sort(key=lambda x: x["compliance_rate"])

    # Recent sessions
    sessions = data.get("sessions", [])
    recent_rates = [s["compliance_rate"] for s in sessions[-10:]]
    recent_avg = sum(recent_rates) / len(recent_rates) if recent_rates else 0

    # Trend analysis
    if len(recent_rates) >= 5:
        first_half = sum(recent_rates[:len(recent_rates)//2]) / (len(recent_rates)//2)
        second_half = sum(recent_rates[len(recent_rates)//2:]) / (len(recent_rates) - len(recent_rates)//2)

        if second_half > first_half + 0.1:
            trend = "improving"
        elif second_half < first_half - 0.1:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    return {
        "status": "ok",
        "overall": {
            "total_advice_given": total_given,
            "total_advice_followed": total_followed,
            "overall_compliance_rate": round(overall_rate, 2)
        },
        "recent": {
            "sessions_analyzed": len(recent_rates),
            "average_compliance": round(recent_avg, 2),
            "trend": trend
        },
        "by_pattern": pattern_stats,
        "recommendations": generate_recommendations(pattern_stats)
    }


def generate_recommendations(pattern_stats: list) -> list[str]:
    """Generate recommendations based on compliance data."""
    recommendations = []

    for stat in pattern_stats:
        if stat["compliance_rate"] < 0.3 and stat["times_advised"] >= 3:
            recommendations.append(
                f"Pattern '{stat['pattern']}' has very low compliance ({stat['compliance_rate']*100:.0f}%). "
                f"Consider: stronger enforcement, better templates, or root cause analysis."
            )
        elif stat["compliance_rate"] < 0.5 and stat["times_advised"] >= 5:
            recommendations.append(
                f"Pattern '{stat['pattern']}' is frequently ignored ({stat['compliance_rate']*100:.0f}% compliance). "
                f"Review the actionable template for clarity."
            )

    if not recommendations:
        recommendations.append("Compliance rates look healthy. Keep monitoring for trends.")

    return recommendations[:3]  # Limit to top 3


def main():
    if len(sys.argv) < 2:
        print("Usage: compliance-tracker.py <record|check|stats> [args]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "record":
        if len(sys.argv) < 4:
            print("Usage: compliance-tracker.py record <session_id> <advice_json>", file=sys.stderr)
            sys.exit(1)

        session_id = sys.argv[2]
        try:
            advice = json.loads(sys.argv[3])
        except json.JSONDecodeError:
            advice = []

        result = record_advice(session_id, advice)
        print(json.dumps(result, indent=2))

    elif command == "check":
        if len(sys.argv) < 4:
            print("Usage: compliance-tracker.py check <session_id> <patterns_found_json>", file=sys.stderr)
            sys.exit(1)

        session_id = sys.argv[2]
        try:
            patterns = json.loads(sys.argv[3])
        except json.JSONDecodeError:
            patterns = []

        result = check_compliance(session_id, patterns)
        print(json.dumps(result, indent=2))

    elif command == "stats":
        result = get_stats()
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
