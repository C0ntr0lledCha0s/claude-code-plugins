#!/usr/bin/env bash
# Integration tests for GitHub Workflows hooks

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

pass() {
    echo -e "${GREEN}✓ $1${NC}"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}✗ $1${NC}"
    ((TESTS_FAILED++))
}

info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

echo "=== Testing GitHub Workflows Hooks ==="
echo

# Test 1: Hooks JSON is valid
info "Test 1: Validating hooks.json syntax"
if python3 -m json.tool ../hooks/hooks.json > /dev/null 2>&1; then
    pass "hooks.json is valid JSON"
else
    fail "hooks.json has invalid JSON syntax"
fi

# Test 2: Hook scripts exist
info "Test 2: Checking hook script files exist"
if [ -f "../hooks/scripts/update-board-on-merge.sh" ]; then
    pass "update-board-on-merge.sh exists"
else
    fail "update-board-on-merge.sh not found"
fi

# Test 3: Hook scripts are executable
info "Test 3: Checking hook scripts are executable"
if [ -x "../hooks/scripts/update-board-on-merge.sh" ]; then
    pass "update-board-on-merge.sh is executable"
else
    fail "update-board-on-merge.sh is not executable"
    chmod +x ../hooks/scripts/update-board-on-merge.sh 2>/dev/null || true
fi

# Test 4: Hook uses ${PLUGIN_DIR} variable
info "Test 4: Checking for hardcoded paths"
if grep -q "github-workflows/hooks" ../hooks/hooks.json; then
    fail "Found hardcoded path in hooks.json"
else
    pass "No hardcoded paths found (using \${PLUGIN_DIR})"
fi

# Test 5: UserPromptSubmit hook is empty or conditional
info "Test 5: Checking UserPromptSubmit hook"
if grep -A3 "UserPromptSubmit" ../hooks/hooks.json | grep -q "\"UserPromptSubmit\": \[\]"; then
    pass "UserPromptSubmit is empty (no performance impact)"
elif grep -A3 "UserPromptSubmit" ../hooks/hooks.json | grep -q "matcher"; then
    pass "UserPromptSubmit has matcher (conditional execution)"
else
    fail "UserPromptSubmit may run on every message"
fi

# Test 6: Hook script handles errors
info "Test 6: Checking error handling in hook scripts"
if grep -q "set -euo pipefail" ../hooks/scripts/update-board-on-merge.sh; then
    pass "Hook script has proper error handling"
else
    fail "Hook script missing 'set -euo pipefail'"
fi

echo
echo "=== Test Summary ==="
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed${NC}"
    exit 1
fi
