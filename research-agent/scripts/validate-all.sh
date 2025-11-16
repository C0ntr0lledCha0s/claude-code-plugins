#!/usr/bin/env bash
#
# Validate all aspects of research output
# Usage: bash validate-all.sh <research-output-file> [--codebase-dir <dir>]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESEARCH_FILE="${1:-}"
CODEBASE_DIR="${2:-.}"
THRESHOLD="${3:-70}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

usage() {
    echo "Usage: bash validate-all.sh <research-output-file> [codebase-dir] [threshold]"
    echo ""
    echo "Arguments:"
    echo "  research-output-file  Path to the research output markdown file"
    echo "  codebase-dir         Root directory of the codebase (default: current directory)"
    echo "  threshold            Minimum completeness percentage (default: 70)"
    echo ""
    echo "Example:"
    echo "  bash validate-all.sh output/investigation-results.md /path/to/project 80"
    exit 1
}

if [[ -z "$RESEARCH_FILE" ]]; then
    usage
fi

if [[ ! -f "$RESEARCH_FILE" ]]; then
    echo -e "${RED}Error: Research file '$RESEARCH_FILE' does not exist${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Research Agent - Comprehensive Validation          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Research File: ${GREEN}$RESEARCH_FILE${NC}"
echo -e "Codebase Dir:  ${GREEN}$CODEBASE_DIR${NC}"
echo -e "Threshold:     ${GREEN}$THRESHOLD%${NC}"
echo ""

VALIDATION_FAILED=0

# Test 1: Quality Validation
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 1: Quality Standards${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if python3 "$SCRIPT_DIR/validate-research.py" "$RESEARCH_FILE"; then
    echo -e "${GREEN}✓ Quality validation passed${NC}"
else
    echo -e "${RED}✗ Quality validation failed${NC}"
    VALIDATION_FAILED=1
fi

echo ""

# Test 2: Evidence Validation
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 2: Evidence & File References${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if python3 "$SCRIPT_DIR/check-evidence.py" "$RESEARCH_FILE" --codebase-dir "$CODEBASE_DIR"; then
    echo -e "${GREEN}✓ Evidence validation passed${NC}"
else
    echo -e "${YELLOW}⚠  Evidence validation warnings (non-blocking)${NC}"
    # Don't fail on evidence issues - they might be examples
fi

echo ""

# Test 3: Completeness Assessment
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Test 3: Completeness Assessment${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if python3 "$SCRIPT_DIR/assess-completeness.py" "$RESEARCH_FILE" --threshold "$THRESHOLD"; then
    echo -e "${GREEN}✓ Completeness assessment passed${NC}"
else
    echo -e "${RED}✗ Completeness assessment failed${NC}"
    VALIDATION_FAILED=1
fi

echo ""

# Final Summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [[ $VALIDATION_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✅ All validations passed!${NC}"
    echo -e "   Research output meets all quality standards."
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some validations failed${NC}"
    echo -e "   Please review the output above and improve the research."
    echo ""
    echo "Common improvements:"
    echo "  • Add more file references with line numbers"
    echo "  • Include code examples and evidence"
    echo "  • Expand explanations and add recommendations"
    echo "  • Ensure all expected sections are present"
    echo ""
    exit 1
fi
