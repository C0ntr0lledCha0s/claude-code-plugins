#!/usr/bin/env bash
# Integration tests for GraphQL operations

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

echo "=== Testing GraphQL Operations ==="
echo

# Test 1: GraphQL script exists
info "Test 1: Checking graphql-queries.sh exists"
if [ -f "../skills/managing-projects/scripts/graphql-queries.sh" ]; then
    pass "graphql-queries.sh exists"
else
    fail "graphql-queries.sh not found"
fi

# Test 2: Script has retry logic
info "Test 2: Checking for retry logic"
if grep -q "retry_graphql" ../skills/managing-projects/scripts/graphql-queries.sh; then
    pass "Retry logic implemented"
else
    fail "Missing retry logic"
fi

# Test 3: Script has exponential backoff
info "Test 3: Checking for exponential backoff"
if grep -q "delay.*\*.*2" ../skills/managing-projects/scripts/graphql-queries.sh; then
    pass "Exponential backoff implemented"
else
    fail "Missing exponential backoff"
fi

# Test 4: Script has max delay cap
info "Test 4: Checking for max delay cap"
if grep -q "max_delay" ../skills/managing-projects/scripts/graphql-queries.sh; then
    pass "Max delay cap implemented"
else
    fail "Missing max delay cap"
fi

# Test 5: Script has error handling
info "Test 5: Checking error handling"
if grep -q "set -euo pipefail" ../skills/managing-projects/scripts/graphql-queries.sh; then
    pass "Proper error handling"
else
    fail "Missing 'set -euo pipefail'"
fi

# Test 6: Script has authentication check
info "Test 6: Checking GitHub authentication check"
if grep -q "check_gh_auth\|gh auth status" ../skills/managing-projects/scripts/graphql-queries.sh; then
    pass "Authentication check present"
else
    fail "Missing authentication check"
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
