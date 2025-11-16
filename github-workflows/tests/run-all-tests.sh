#!/usr/bin/env bash
# Run all integration tests for GitHub Workflows plugin

set -e

cd "$(dirname "$0")"

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}GitHub Workflows Plugin Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo

TOTAL_PASSED=0
TOTAL_FAILED=0
SUITES_PASSED=0
SUITES_FAILED=0

run_test_suite() {
    local test_file="$1"
    local suite_name="$2"

    echo -e "${BLUE}Running: $suite_name${NC}"
    echo "----------------------------------------"

    if bash "$test_file"; then
        ((SUITES_PASSED++))
        echo -e "${GREEN}✓ $suite_name passed${NC}"
    else
        ((SUITES_FAILED++))
        echo -e "${RED}✗ $suite_name failed${NC}"
    fi
    echo
}

# Run test suites
run_test_suite "test-hooks.sh" "Hook Tests"
run_test_suite "test-graphql.sh" "GraphQL Tests"

# Summary
echo "========================================"
echo -e "${BLUE}Final Summary${NC}"
echo "========================================"
echo "Test Suites Passed: $SUITES_PASSED"
echo "Test Suites Failed: $SUITES_FAILED"
echo

if [ "$SUITES_FAILED" -eq 0 ]; then
    echo -e "${GREEN}✓ All test suites passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some test suites failed${NC}"
    exit 1
fi
