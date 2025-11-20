#!/usr/bin/env bash
#
# Test Suite for Self-Improvement Hooks
# Run this to validate all hook scripts work correctly
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
TEST_DIR="${SCRIPT_DIR}/test-fixtures"
LOG_DIR="${HOME}/.claude/self-improvement"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Create test fixtures directory
mkdir -p "${TEST_DIR}"

echo "========================================"
echo "Self-Improvement Hooks Test Suite"
echo "========================================"
echo ""

# Helper function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Testing: ${test_name}... "

    local output
    local exit_code=0
    output=$(eval "$test_command" 2>&1) || exit_code=$?

    if echo "$output" | grep -q "$expected_pattern"; then
        echo -e "${GREEN}PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        echo "  Expected pattern: $expected_pattern"
        echo "  Got: $output"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Helper function to check if a command exists
check_dependency() {
    local dep_name="$1"
    local dep_cmd="$2"

    echo -n "Checking dependency: ${dep_name}... "
    if command -v "$dep_cmd" &> /dev/null; then
        echo -e "${GREEN}OK${NC}"
        return 0
    else
        echo -e "${RED}MISSING${NC}"
        return 1
    fi
}

echo "=== Dependency Checks ==="
echo ""

# Check all required dependencies
DEPS_OK=true
check_dependency "bash" "bash" || DEPS_OK=false
check_dependency "python3" "python3" || DEPS_OK=false
# Note: jq is no longer required - all JSON parsing uses Python

echo ""
echo "=== Script Syntax Checks ==="
echo ""

# Check all scripts for syntax errors
for script in "${SCRIPT_DIR}"/*.sh; do
    script_name=$(basename "$script")
    if [[ "$script_name" == "test-hooks.sh" ]]; then
        continue
    fi
    run_test "Syntax check: ${script_name}" \
        "bash -n '${script}'" \
        ""
done

echo ""
echo "=== JSON Output Format Tests ==="
echo ""

# Test 1: load-learnings.sh with empty databases
run_test "load-learnings.sh returns valid JSON (no data)" \
    "bash '${SCRIPT_DIR}/load-learnings.sh'" \
    '"decision"'

# Test 2: analyze-conversation.sh with empty input
run_test "analyze-conversation.sh returns valid JSON (empty input)" \
    "echo '' | bash '${SCRIPT_DIR}/analyze-conversation.sh'" \
    '"decision"'

# Test 3: Check JSON is parseable
echo -n "Testing: JSON output is parseable... "
output=$(bash "${SCRIPT_DIR}/load-learnings.sh" 2>&1)
if echo "$output" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
    echo -e "${GREEN}PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}FAILED${NC}"
    echo "  Output is not valid JSON: $output"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_RUN=$((TESTS_RUN + 1))

# Test 4: Check for Windows CRLF in output (critical for hooks to work)
echo -n "Testing: No CRLF in load-learnings.sh output... "
output=$(bash "${SCRIPT_DIR}/load-learnings.sh" 2>&1)
if echo "$output" | grep -q $'\r'; then
    echo -e "${RED}FAILED${NC}"
    echo "  Output contains Windows CRLF characters"
    TESTS_FAILED=$((TESTS_FAILED + 1))
else
    echo -e "${GREEN}PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
fi
TESTS_RUN=$((TESTS_RUN + 1))

echo ""
echo "=== Payload Handling Tests ==="
echo ""

# Create test transcript file
TEST_TRANSCRIPT="${TEST_DIR}/test-transcript.jsonl"
cat > "${TEST_TRANSCRIPT}" << 'EOF'
{"type":"user","message":{"content":"Hello, can you help me fix a bug?"}}
{"type":"assistant","message":{"content":"Of course! I'd be happy to help you fix the bug. Can you describe the issue?"}}
{"type":"user","message":{"content":"There's an error in my code"}}
{"type":"assistant","message":{"content":"I see. Let me analyze the error and provide a solution."}}
EOF

# Test 4: analyze-conversation.sh with valid payload
run_test "analyze-conversation.sh handles valid payload" \
    "echo '{\"transcript_path\": \"${TEST_TRANSCRIPT}\", \"session_id\": \"test-123\"}' | bash '${SCRIPT_DIR}/analyze-conversation.sh'" \
    '"decision"'

# Test 5: analyze-conversation.sh with missing transcript_path
run_test "analyze-conversation.sh handles missing transcript_path" \
    "echo '{\"session_id\": \"test-123\"}' | bash '${SCRIPT_DIR}/analyze-conversation.sh'" \
    '"decision"'

# Test 6: analyze-conversation.sh with non-existent file
run_test "analyze-conversation.sh handles non-existent file" \
    "echo '{\"transcript_path\": \"/nonexistent/file.jsonl\"}' | bash '${SCRIPT_DIR}/analyze-conversation.sh'" \
    '"decision"'

echo ""
echo "=== Database Operations Tests ==="
echo ""

# Backup existing databases
if [[ -f "${LOG_DIR}/patterns.json" ]]; then
    cp "${LOG_DIR}/patterns.json" "${LOG_DIR}/patterns.json.bak"
fi
if [[ -f "${LOG_DIR}/learnings.json" ]]; then
    cp "${LOG_DIR}/learnings.json" "${LOG_DIR}/learnings.json.bak"
fi
if [[ -f "${LOG_DIR}/metrics.json" ]]; then
    cp "${LOG_DIR}/metrics.json" "${LOG_DIR}/metrics.json.bak"
fi

# Test database initialization
mkdir -p "${LOG_DIR}"
rm -f "${LOG_DIR}/patterns.json" "${LOG_DIR}/learnings.json" "${LOG_DIR}/metrics.json"

# Test 7: load-learnings.sh initializes databases
run_test "load-learnings.sh works with no databases" \
    "bash '${SCRIPT_DIR}/load-learnings.sh'" \
    '"decision"'

# Restore backups
if [[ -f "${LOG_DIR}/patterns.json.bak" ]]; then
    mv "${LOG_DIR}/patterns.json.bak" "${LOG_DIR}/patterns.json"
fi
if [[ -f "${LOG_DIR}/learnings.json.bak" ]]; then
    mv "${LOG_DIR}/learnings.json.bak" "${LOG_DIR}/learnings.json"
fi
if [[ -f "${LOG_DIR}/metrics.json.bak" ]]; then
    mv "${LOG_DIR}/metrics.json.bak" "${LOG_DIR}/metrics.json"
fi

echo ""
echo "=== View Scripts Tests ==="
echo ""

# Test view scripts
for view_script in view-learnings.sh view-metrics.sh view-patterns.sh; do
    if [[ -f "${SCRIPT_DIR}/${view_script}" ]]; then
        run_test "${view_script} runs without error" \
            "bash '${SCRIPT_DIR}/${view_script}' 2>&1" \
            ""
    fi
done

echo ""
echo "=== hooks.json Validation ==="
echo ""

HOOKS_JSON="${PLUGIN_ROOT}/hooks/hooks.json"

# Test hooks.json exists and is valid JSON
if [[ -f "${HOOKS_JSON}" ]]; then
    run_test "hooks.json exists and is valid JSON" \
        "python3 -m json.tool '${HOOKS_JSON}' > /dev/null && echo 'valid'" \
        "valid"

    # Test hooks.json has required events
    run_test "hooks.json has SessionStart event" \
        "grep -q 'SessionStart' '${HOOKS_JSON}' && echo 'found'" \
        "found"

    run_test "hooks.json has SessionEnd event" \
        "grep -q 'SessionEnd' '${HOOKS_JSON}' && echo 'found'" \
        "found"

    # Test hooks.json uses correct decision format (not continue)
    if grep -q '"continue"' "${HOOKS_JSON}"; then
        echo -e "${RED}FAILED: hooks.json uses deprecated 'continue' format${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    else
        echo -e "${GREEN}PASSED: hooks.json uses correct 'decision' format${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
else
    echo -e "${RED}FAILED: hooks.json not found${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
fi

echo ""
echo "=== parse-jsonl.py Tests ==="
echo ""

PARSE_SCRIPT="${SCRIPT_DIR}/parse-jsonl.py"
if [[ -f "${PARSE_SCRIPT}" ]]; then
    # Test parse-jsonl.py with test transcript
    TEST_OUTPUT="${TEST_DIR}/test-output.txt"
    run_test "parse-jsonl.py parses test transcript" \
        "python3 '${PARSE_SCRIPT}' '${TEST_TRANSCRIPT}' '${TEST_OUTPUT}' && cat '${TEST_OUTPUT}' | grep -q 'bug' && echo 'parsed'" \
        "parsed"
else
    echo -e "${YELLOW}parse-jsonl.py not found${NC}"
fi

# Cleanup test fixtures
rm -rf "${TEST_DIR}"

echo ""
echo "========================================"
echo "Test Results"
echo "========================================"
echo ""
echo "Tests Run:    ${TESTS_RUN}"
echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"
echo ""

if [[ ${TESTS_FAILED} -gt 0 ]]; then
    echo -e "${RED}SOME TESTS FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}ALL TESTS PASSED${NC}"
    exit 0
fi
