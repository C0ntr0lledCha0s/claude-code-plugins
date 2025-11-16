#!/usr/bin/env bash
#
# Automated Conversation Analysis Script
# Triggers on Stop event (when conversation ends)
# Analyzes conversation for quality, patterns, issues, and learning opportunities
#

set -euo pipefail

# Cleanup trap for error handling
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log_analysis "ERROR: Script failed with exit code $exit_code"
        # Note: Database operations already use file locking, so no rollback needed
    fi
}
trap cleanup EXIT

# Configuration
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-${HOME}/.claude/plugins/self-improvement}"
LOG_DIR="${HOME}/.claude/self-improvement"
CONVERSATION_LOG="${LOG_DIR}/conversations.jsonl"
PATTERNS_DB="${LOG_DIR}/patterns.json"
METRICS_DB="${LOG_DIR}/metrics.json"
LEARNINGS_DB="${LOG_DIR}/learnings.json"
ANALYSIS_LOG="${LOG_DIR}/analysis.log"

# Create directories if they don't exist
mkdir -p "${LOG_DIR}"

# Timestamp for this analysis
TIMESTAMP=$(date -Iseconds)
SESSION_ID="${CLAUDE_SESSION_ID:-$(date +%s)}"

# Initialize databases if they don't exist
if [[ ! -f "${PATTERNS_DB}" ]]; then
    echo '{"patterns": []}' > "${PATTERNS_DB}"
fi

if [[ ! -f "${METRICS_DB}" ]]; then
    echo '{"sessions": []}' > "${METRICS_DB}"
fi

if [[ ! -f "${LEARNINGS_DB}" ]]; then
    echo '{"learnings": []}' > "${LEARNINGS_DB}"
fi

# Function to log analysis results
log_analysis() {
    echo "[${TIMESTAMP}] $*" >> "${ANALYSIS_LOG}"
}

log_analysis "=== Starting conversation analysis for session ${SESSION_ID} ==="

# Function to analyze conversation transcript
analyze_transcript() {
    local transcript_file="$1"

    if [[ ! -f "${transcript_file}" ]]; then
        log_analysis "No transcript file found, skipping analysis"
        return 0
    fi

    log_analysis "Analyzing transcript: ${transcript_file}"

    # Extract conversation statistics
    local total_turns=$(grep -c "User:\|Assistant:" "${transcript_file}" 2>/dev/null || echo "0")
    local user_turns=$(grep -c "^User:" "${transcript_file}" 2>/dev/null || echo "0")
    local assistant_turns=$(grep -c "^Assistant:" "${transcript_file}" 2>/dev/null || echo "0")
    local total_lines=$(wc -l < "${transcript_file}")

    log_analysis "Statistics: ${total_turns} total turns, ${user_turns} user, ${assistant_turns} assistant, ${total_lines} lines"

    # Analyze for keywords and patterns
    analyze_keywords "${transcript_file}"
    analyze_code_quality "${transcript_file}"
    analyze_errors "${transcript_file}"
    analyze_security "${transcript_file}"
    analyze_sentiment "${transcript_file}"

    # Store metrics
    store_session_metrics "${total_turns}" "${user_turns}" "${assistant_turns}" "${total_lines}"
}

# Analyze for important keywords
analyze_keywords() {
    local file="$1"

    log_analysis "--- Keyword Analysis ---"

    # Use more accurate pattern matching with negative lookarounds where possible
    # Count actual bug mentions (not "debug", "no bug", etc.)
    local bug_count=$(grep -cP "(?<!de)bug(?!ging)|(?:found|discovered|encounter(?:ed)?|has)\s+(?:a|an)?\s*(?:bug|error|issue)|(?:doesn't|does\s+not)\s+work|(?:is\s+)?broken|failing\s+test" "${file}" 2>/dev/null || echo "0")

    # Exclude false positives like "error handling", "no error"
    local error_count=$(grep -cP "(?<!no\s)(?<!handle\s)error(?!\s+handling)(?!\s+message)" "${file}" 2>/dev/null || echo "0")

    # Security keywords - be specific
    local security_count=$(grep -cP "(?:sql\s+)?injection|xss|cross-site\s+scripting|csrf|vulnerabilit(?:y|ies)|security\s+(?:issue|flaw|bug)|exploit|attack|malicious" "${file}" 2>/dev/null || echo "0")

    # Quality improvement mentions
    local quality_count=$(grep -ci "quality\|review\|improve\|optimize\|refactor" "${file}" 2>/dev/null || echo "0")

    # Help requests (user asking questions)
    local help_count=$(grep -ci "how\s+(?:do|to|can)|can\s+you|please\s+help|what\s+is|explain" "${file}" 2>/dev/null || echo "0")

    log_analysis "Keywords: bugs=${bug_count}, errors=${error_count}, security=${security_count}, quality=${quality_count}, help_requests=${help_count}"

    # Check for repeated issues with adjusted thresholds
    local total_issues=$((bug_count + error_count))
    if [[ ${total_issues} -gt 8 ]]; then
        track_pattern "high_bug_discussion" "Conversation had ${total_issues} bug/error mentions (bugs: ${bug_count}, errors: ${error_count})" "important"
    fi

    if [[ ${security_count} -gt 3 ]]; then
        track_pattern "security_focus" "Conversation had ${security_count} security-related mentions" "important"
    fi
}

# Analyze code quality indicators
analyze_code_quality() {
    local file="$1"

    log_analysis "--- Code Quality Analysis ---"

    # Look for code blocks
    local code_blocks=$(grep -c '```' "${file}" 2>/dev/null || echo "0")
    code_blocks=$((code_blocks / 2))  # Divide by 2 since each block has opening and closing

    # Quality indicators
    local test_mentions=$(grep -ci "test\|spec\|unittest\|pytest\|jest" "${file}" 2>/dev/null || echo "0")
    local validation_mentions=$(grep -ci "validat\|sanitiz\|check\|verify" "${file}" 2>/dev/null || echo "0")
    local error_handling=$(grep -ci "try\|catch\|except\|error handling" "${file}" 2>/dev/null || echo "0")

    log_analysis "Code Quality: ${code_blocks} code blocks, tests=${test_mentions}, validation=${validation_mentions}, error_handling=${error_handling}"

    # Track patterns
    if [[ ${code_blocks} -gt 0 && ${test_mentions} -eq 0 ]]; then
        track_pattern "missing_tests" "Code provided but no tests mentioned" "important"
    fi

    if [[ ${code_blocks} -gt 0 && ${validation_mentions} -eq 0 ]]; then
        track_pattern "missing_validation" "Code provided but no input validation mentioned" "important"
    fi
}

# Analyze for errors and issues
analyze_errors() {
    local file="$1"

    log_analysis "--- Error Analysis ---"

    # Error indicators - more precise patterns
    local syntax_errors=$(grep -cP "syntax\s+error|SyntaxError|parse\s+error|ParseError|unexpected\s+token" "${file}" 2>/dev/null || echo "0")
    local runtime_errors=$(grep -cP "runtime\s+error|RuntimeError|exception(?:\s+occurred)?|traceback|stack\s+trace|uncaught\s+exception" "${file}" 2>/dev/null || echo "0")
    local logic_errors=$(grep -cP "logic\s+error|incorrect\s+(?:result|output|behavior)|(?:doesn't|does\s+not)\s+work|not\s+working\s+as\s+expected" "${file}" 2>/dev/null || echo "0")

    log_analysis "Errors: syntax=${syntax_errors}, runtime=${runtime_errors}, logic=${logic_errors}"

    local total_errors=$((syntax_errors + runtime_errors + logic_errors))
    if [[ ${total_errors} -gt 3 ]]; then
        track_pattern "high_error_rate" "Multiple errors encountered in conversation (${total_errors} total)" "critical"
    fi
}

# Analyze security considerations
analyze_security() {
    local file="$1"

    log_analysis "--- Security Analysis ---"

    # Security issue indicators
    local sql_injection=$(grep -ci "sql injection\|parameterized query\|prepared statement" "${file}" 2>/dev/null || echo "0")
    local xss=$(grep -ci "xss\|cross-site scripting\|sanitize.*html\|escape.*html" "${file}" 2>/dev/null || echo "0")
    local auth_issues=$(grep -ci "authentication\|authorization\|access control\|permission" "${file}" 2>/dev/null || echo "0")
    local secret_exposure=$(grep -ci "api key\|password\|secret\|credential\|token" "${file}" 2>/dev/null || echo "0")

    log_analysis "Security: sql_injection=${sql_injection}, xss=${xss}, auth=${auth_issues}, secrets=${secret_exposure}"

    # Track security patterns
    if [[ ${sql_injection} -gt 0 ]]; then
        track_learning "sql_injection_discussed" "SQL injection topic came up - ensure parameterized queries used"
    fi

    if [[ ${xss} -gt 0 ]]; then
        track_learning "xss_discussed" "XSS topic came up - ensure proper input sanitization"
    fi
}

# Analyze sentiment and user satisfaction
analyze_sentiment() {
    local file="$1"

    log_analysis "--- Sentiment Analysis ---"

    # Positive indicators - look for genuine appreciation
    local positive=$(grep -cP "thank(?:s| you)|great(?:\s+job)?|perfect|excellent|awesome|helpful|(?:works?|working)\s+(?:great|perfectly|well)" "${file}" 2>/dev/null || echo "0")

    # Negative indicators - actual problems, not mentions of fixing them
    local negative=$(grep -cP "(?:is\s+)?wrong|incorrect(?:\s+result)?|(?:still\s+)?(?:doesn't|does\s+not)\s+work|not\s+working|confused|(?:very\s+)?unclear|frustrat(?:ed|ing)" "${file}" 2>/dev/null || echo "0")

    # Confusion indicators - actual confusion, not just questions
    local confusion=$(grep -cP "(?:I\s+)?don't\s+understand|unclear\s+(?:about|how|why)|confus(?:ed|ing)|what\s+do\s+you\s+mean|can\s+you\s+explain|not\s+sure\s+(?:what|how|why)" "${file}" 2>/dev/null || echo "0")

    log_analysis "Sentiment: positive=${positive}, negative=${negative}, confusion=${confusion}"

    # Calculate sentiment score
    local sentiment_score=$((positive - negative))

    if [[ ${sentiment_score} -lt -3 ]]; then
        track_pattern "negative_user_experience" "User expressed frustration or confusion (score: ${sentiment_score})" "critical"
    fi

    if [[ ${confusion} -gt 5 ]]; then
        track_pattern "unclear_communication" "User asked many clarifying questions (${confusion} instances)" "important"
    fi
}

# Track a pattern in the patterns database
track_pattern() {
    local pattern_type="$1"
    local description="$2"
    local severity="${3:-minor}"

    log_analysis "PATTERN DETECTED: [${severity}] ${pattern_type}: ${description}"

    # Update patterns database - using argument passing to prevent injection
    python3 - "$pattern_type" "$description" "$severity" "$TIMESTAMP" "$PATTERNS_DB" <<'EOF'
import json
import sys
import fcntl
from datetime import datetime

# Get arguments safely
pattern_type = sys.argv[1]
description = sys.argv[2]
severity = sys.argv[3]
timestamp = sys.argv[4]
patterns_file = sys.argv[5]

# Basic validation
if severity not in ['critical', 'important', 'minor']:
    print(f"WARNING: Invalid severity '{severity}', defaulting to 'minor'", file=sys.stderr)
    severity = 'minor'

def validate_patterns_data(data):
    """Basic validation of patterns data structure"""
    if not isinstance(data, dict):
        raise ValueError("Patterns data must be a dict")
    if 'patterns' not in data:
        raise ValueError("Patterns data must have 'patterns' key")
    if not isinstance(data['patterns'], list):
        raise ValueError("'patterns' must be a list")

    for pattern in data['patterns']:
        if not isinstance(pattern, dict):
            raise ValueError("Each pattern must be a dict")
        required_keys = ['type', 'description', 'severity', 'count']
        for key in required_keys:
            if key not in pattern:
                raise ValueError(f"Pattern missing required key: {key}")

    return True

try:
    # Open with read/write for atomic update with file locking
    with open(patterns_file, 'r+') as f:
        # Acquire exclusive lock
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

        try:
            f.seek(0)
            data = json.load(f)
            # Validate existing data
            validate_patterns_data(data)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"WARNING: Invalid patterns file, resetting: {e}", file=sys.stderr)
            data = {"patterns": []}

        # Find existing pattern or create new
        pattern_found = False
        for pattern in data['patterns']:
            if pattern['type'] == pattern_type:
                pattern['count'] = pattern.get('count', 0) + 1
                pattern['last_seen'] = timestamp
                pattern['severity'] = severity
                pattern['description'] = description  # Update description
                pattern_found = True
                break

        if not pattern_found:
            data['patterns'].append({
                'type': pattern_type,
                'description': description,
                'severity': severity,
                'count': 1,
                'first_seen': timestamp,
                'last_seen': timestamp
            })

        # Write atomically
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=2)

        # Lock automatically released when file closes

    print(f"Pattern tracked: {pattern_type}")
except FileNotFoundError:
    # File doesn't exist, create it
    data = {"patterns": [{
        'type': pattern_type,
        'description': description,
        'severity': severity,
        'count': 1,
        'first_seen': timestamp,
        'last_seen': timestamp
    }]}
    with open(patterns_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Pattern tracked: {pattern_type}")
except Exception as e:
    print(f"Error tracking pattern: {e}", file=sys.stderr)
    sys.exit(1)
EOF
}

# Track a learning point
track_learning() {
    local learning_key="$1"
    local learning_text="$2"

    log_analysis "LEARNING: ${learning_key}: ${learning_text}"

    # Update learnings database - using argument passing to prevent injection
    python3 - "$learning_key" "$learning_text" "$TIMESTAMP" "$LEARNINGS_DB" <<'EOF'
import json
import sys
import fcntl
from datetime import datetime

# Get arguments safely
learning_key = sys.argv[1]
learning_text = sys.argv[2]
timestamp = sys.argv[3]
learnings_file = sys.argv[4]

try:
    # Open with read/write for atomic update with file locking
    with open(learnings_file, 'r+') as f:
        # Acquire exclusive lock
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

        try:
            f.seek(0)
            data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            data = {"learnings": []}

        # Check if learning already exists
        learning_found = False
        for learning in data['learnings']:
            if learning['key'] == learning_key:
                learning['reinforced_count'] = learning.get('reinforced_count', 0) + 1
                learning['last_reinforced'] = timestamp
                learning['text'] = learning_text  # Update text
                learning_found = True
                break

        if not learning_found:
            data['learnings'].append({
                'key': learning_key,
                'text': learning_text,
                'learned_at': timestamp,
                'reinforced_count': 0
            })

        # Write atomically
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=2)

        # Lock automatically released when file closes

    print(f"Learning tracked: {learning_key}")
except FileNotFoundError:
    # File doesn't exist, create it
    data = {"learnings": [{
        'key': learning_key,
        'text': learning_text,
        'learned_at': timestamp,
        'reinforced_count': 0
    }]}
    with open(learnings_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Learning tracked: {learning_key}")
except Exception as e:
    print(f"Error tracking learning: {e}", file=sys.stderr)
    sys.exit(1)
EOF
}

# Store session metrics
store_session_metrics() {
    local total_turns="$1"
    local user_turns="$2"
    local assistant_turns="$3"
    local total_lines="$4"

    # Update metrics database - using argument passing and file locking
    python3 - "$SESSION_ID" "$TIMESTAMP" "$total_turns" "$user_turns" "$assistant_turns" "$total_lines" "$METRICS_DB" <<'EOF'
import json
import sys
import fcntl

# Get arguments safely
session_id = sys.argv[1]
timestamp = sys.argv[2]
total_turns = int(sys.argv[3])
user_turns = int(sys.argv[4])
assistant_turns = int(sys.argv[5])
total_lines = int(sys.argv[6])
metrics_file = sys.argv[7]

try:
    # Open with read/write for atomic update with file locking
    with open(metrics_file, 'r+') as f:
        # Acquire exclusive lock
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

        try:
            f.seek(0)
            data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            data = {"sessions": []}

        data['sessions'].append({
            'session_id': session_id,
            'timestamp': timestamp,
            'total_turns': total_turns,
            'user_turns': user_turns,
            'assistant_turns': assistant_turns,
            'total_lines': total_lines
        })

        # Keep only last 100 sessions
        if len(data['sessions']) > 100:
            data['sessions'] = data['sessions'][-100:]

        # Write atomically
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=2)

        # Lock automatically released when file closes

    print("Session metrics stored")
except FileNotFoundError:
    # File doesn't exist, create it
    data = {"sessions": [{
        'session_id': session_id,
        'timestamp': timestamp,
        'total_turns': total_turns,
        'user_turns': user_turns,
        'assistant_turns': assistant_turns,
        'total_lines': total_lines
    }]}
    with open(metrics_file, 'w') as f:
        json.dump(data, f, indent=2)
    print("Session metrics stored")
except Exception as e:
    print(f"Error storing metrics: {e}", file=sys.stderr)
    sys.exit(1)
EOF
}

# Generate summary report
generate_summary() {
    log_analysis "--- Generating Summary ---"

    python3 - <<EOF
import json
from collections import Counter

print("\n=== Self-Improvement Summary ===\n")

# Load patterns
try:
    with open("${PATTERNS_DB}", 'r') as f:
        patterns_data = json.load(f)

    if patterns_data.get('patterns'):
        print("🔍 Recurring Patterns Detected:")
        for pattern in sorted(patterns_data['patterns'], key=lambda x: x.get('count', 0), reverse=True)[:5]:
            severity_emoji = {'critical': '🔴', 'important': '🟡', 'minor': '🟢'}.get(pattern.get('severity'), '⚪')
            print(f"  {severity_emoji} {pattern['type']}: {pattern['description']} (seen {pattern.get('count', 0)} times)")
        print()
except:
    pass

# Load learnings
try:
    with open("${LEARNINGS_DB}", 'r') as f:
        learnings_data = json.load(f)

    if learnings_data.get('learnings'):
        print("📚 Active Learning Points:")
        for learning in learnings_data['learnings'][-5:]:
            reinforced = learning.get('reinforced_count', 0)
            status = f"(reinforced {reinforced}x)" if reinforced > 0 else "(new)"
            print(f"  • {learning['text']} {status}")
        print()
except:
    pass

# Load metrics
try:
    with open("${METRICS_DB}", 'r') as f:
        metrics_data = json.load(f)

    if metrics_data.get('sessions'):
        recent_sessions = metrics_data['sessions'][-10:]
        avg_turns = sum(s.get('total_turns', 0) for s in recent_sessions) / len(recent_sessions)
        print(f"📊 Recent Activity:")
        print(f"  • Average conversation length: {avg_turns:.1f} turns")
        print(f"  • Sessions analyzed: {len(metrics_data['sessions'])}")
        print()
except:
    pass

print("✓ Analysis complete. Data stored for continuous improvement.\n")
EOF
}

# Main execution
main() {
    local transcript_path=""
    local transcript_found=false

    # Try multiple locations to find conversation transcript
    local possible_paths=(
        "${CLAUDE_TRANSCRIPT:-}"
        "${CLAUDE_CONVERSATION_FILE:-}"
        "${HOME}/.claude/transcripts/current.txt"
        "${HOME}/.claude/transcripts/latest.txt"
        "${HOME}/.claude/conversations/current.txt"
        "${HOME}/.claude/conversations/latest.txt"
        "${CLAUDE_WORKSPACE:-}/.claude/transcript.txt"
        "${PWD}/.claude/transcript.txt"
    )

    log_analysis "Searching for conversation transcript..."

    for possible_path in "${possible_paths[@]}"; do
        # Skip empty paths
        if [[ -z "${possible_path}" ]]; then
            continue
        fi

        if [[ -f "${possible_path}" ]]; then
            transcript_path="${possible_path}"
            transcript_found=true
            log_analysis "Found transcript at: ${transcript_path}"
            break
        fi
    done

    if [[ "${transcript_found}" == true ]]; then
        # Transcript found - perform full analysis
        analyze_transcript "${transcript_path}"

        # Generate summary
        generate_summary

        log_analysis "=== Conversation analysis complete ==="

        # Return success
        echo '{"decision": "approve", "reason": "Conversation analyzed for continuous improvement"}'
    else
        # Transcript not found - log error and inform user
        log_analysis "ERROR: Cannot locate conversation transcript"
        log_analysis "Searched paths:"
        for path in "${possible_paths[@]}"; do
            if [[ -n "${path}" ]]; then
                log_analysis "  - ${path}"
            fi
        done

        # Store minimal metrics to record the attempt
        store_session_metrics 0 0 0 0

        # Return with user-visible warning
        echo '{
            "decision": "approve",
            "hookSpecificOutput": {
                "warning": "⚠️ Self-Improvement Analysis Failed\n\nCannot locate conversation transcript for automated analysis.\n\nPattern tracking and learning features are not working.\n\nTo fix:\n1. Check if CLAUDE_TRANSCRIPT environment variable is set\n2. Verify transcript storage location\n3. See: ~/.claude/self-improvement/analysis.log for details\n\nAlternatively, disable this hook if transcripts are not available."
            }
        }'
    fi

    exit 0
}

# Run main function
main "$@"
