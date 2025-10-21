#!/usr/bin/env bash
# diagnose.sh - Automated diagnostics for mcp-n8n
#
# Usage: ./scripts/diagnose.sh [--save-report]
#
# Runs comprehensive diagnostics and generates a report.

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

SAVE_REPORT=false
if [ "${1:-}" = "--save-report" ]; then
    SAVE_REPORT=true
    REPORT_FILE="diagnostic-report-$(date +%Y%m%d-%H%M%S).txt"
fi

echo -e "${BLUE}=== MCP-N8N Diagnostics ===${NC}"
echo ""
echo "Running comprehensive system checks..."
echo ""

ERRORS=0
WARNINGS=0

# Helper function to check and report
check_item() {
    local name="$1"
    local command="$2"
    local expected="$3"

    echo -n "Checking $name... "

    if output=$(eval "$command" 2>&1); then
        if [ -n "$expected" ] && [[ ! "$output" =~ $expected ]]; then
            echo -e "${YELLOW}⚠${NC} Unexpected: $output"
            WARNINGS=$((WARNINGS + 1))
        else
            echo -e "${GREEN}✓${NC}"
        fi
        if [ "$SAVE_REPORT" = true ]; then
            echo "$name: $output" >> "$REPORT_FILE"
        fi
    else
        echo -e "${RED}✗${NC} Failed: $output"
        ERRORS=$((ERRORS + 1))
        if [ "$SAVE_REPORT" = true ]; then
            echo "$name: FAILED - $output" >> "$REPORT_FILE"
        fi
    fi
}

# Section 1: Python Environment
echo -e "${YELLOW}[1/8] Python Environment${NC}"

check_item "Python version" "python --version" "3\.(11|12|13)"
check_item "Virtual environment" "echo \$VIRTUAL_ENV" ""
check_item "pip version" "pip --version" ""
check_item "Package installed" "pip show mcp-n8n | head -1" ""

echo ""

# Section 2: Dependencies
echo -e "${YELLOW}[2/8] Dependencies${NC}"

check_item "pytest" "python -c 'import pytest; print(pytest.__version__)'" ""
check_item "fastmcp" "python -c 'import fastmcp; print(\"OK\")'" "OK"
check_item "pydantic" "python -c 'import pydantic; print(pydantic.__version__)'" ""
check_item "python-dotenv" "python -c 'import dotenv; print(\"OK\")'" "OK"

echo ""

# Section 3: Environment Variables
echo -e "${YELLOW}[3/8] Environment Variables${NC}"

check_item "ANTHROPIC_API_KEY" "[ -n \"\${ANTHROPIC_API_KEY:-}\" ] && echo 'Set' || echo 'Not set'" "Set"
check_item "CODA_API_KEY" "[ -n \"\${CODA_API_KEY:-}\" ] && echo 'Set' || echo 'Not set'" ""
check_item ".env file exists" "[ -f .env ] && echo 'Yes' || echo 'No'" ""

echo ""

# Section 4: File Structure
echo -e "${YELLOW}[4/8] File Structure${NC}"

check_item "pyproject.toml" "[ -f pyproject.toml ] && echo 'Exists' || echo 'Missing'" "Exists"
check_item "src/ directory" "[ -d src/mcp_n8n ] && echo 'Exists' || echo 'Missing'" "Exists"
check_item "tests/ directory" "[ -d tests ] && echo 'Exists' || echo 'Missing'" "Exists"
check_item "logs/ directory" "[ -d logs ] && echo 'Exists' || echo 'Missing'" "Exists"

echo ""

# Section 5: Backend Paths
echo -e "${YELLOW}[5/8] Backend Paths${NC}"

if [ -f .env ]; then
    # Check Chora Composer
    CHORA_PATH=$(grep "^CHORA_COMPOSER_PATH=" .env 2>/dev/null | cut -d= -f2 || echo "")
    if [ -n "$CHORA_PATH" ]; then
        check_item "Chora Composer path" "[ -d \"$CHORA_PATH\" ] && echo 'Valid' || echo 'Invalid'" "Valid"
    else
        echo -e "  ${YELLOW}⚠${NC} CHORA_COMPOSER_PATH not set in .env"
        WARNINGS=$((WARNINGS + 1))
    fi

    # Check Coda MCP
    CODA_PATH=$(grep "^CODA_MCP_PATH=" .env 2>/dev/null | cut -d= -f2 || echo "")
    if [ -n "$CODA_PATH" ]; then
        check_item "Coda MCP path" "[ -d \"$CODA_PATH\" ] && echo 'Valid' || echo 'Invalid'" "Valid"
    else
        echo -e "  ${YELLOW}⚠${NC} CODA_MCP_PATH not set in .env"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "  ${RED}✗${NC} .env file not found - cannot check backend paths"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# Section 6: Git Status
echo -e "${YELLOW}[6/8] Git Status${NC}"

check_item "Git repository" "git rev-parse --git-dir" ""
check_item "Current branch" "git branch --show-current" ""
check_item "Uncommitted changes" "git status --porcelain | wc -l | tr -d ' '" ""

echo ""

# Section 7: Pre-commit Hooks
echo -e "${YELLOW}[7/8] Pre-commit Hooks${NC}"

check_item "pre-commit installed" "which pre-commit" ""
check_item "Hooks active" "[ -f .git/hooks/pre-commit ] && echo 'Yes' || echo 'No'" "Yes"

echo ""

# Section 8: Logs & Recent Errors
echo -e "${YELLOW}[8/8] Logs & Errors${NC}"

if [ -f logs/mcp-n8n.log ]; then
    LOG_SIZE=$(du -h logs/mcp-n8n.log | cut -f1)
    echo -e "  Log file size: $LOG_SIZE"

    # Check for recent errors
    ERROR_COUNT=$(grep -c "ERROR" logs/mcp-n8n.log 2>/dev/null || echo "0")
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo -e "  ${YELLOW}⚠${NC} Found $ERROR_COUNT ERROR entries in log"
        echo -e "  ${BLUE}Recent errors:${NC}"
        grep "ERROR" logs/mcp-n8n.log | tail -3 | sed 's/^/    /'
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "  ${GREEN}✓${NC} No ERROR entries in log"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} No log file found at logs/mcp-n8n.log"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# Summary
echo -e "${BLUE}=== Diagnostic Summary ===${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Your environment is healthy."
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ Checks passed with $WARNINGS warning(s)${NC}"
    echo ""
    echo "Your environment is mostly healthy, but some items need attention."
else
    echo -e "${RED}✗ Diagnostics failed${NC}"
    echo ""
    echo "Found $ERRORS error(s) and $WARNINGS warning(s)."
    echo ""
    echo "Common fixes:"
    echo "  1. Ensure virtual environment is activated"
    echo "  2. Install dependencies: pip install -e '.[dev]'"
    echo "  3. Create .env file: cp .env.example .env"
    echo "  4. Set API keys in .env file"
    echo "  5. Run: just check-env"
fi

# Save report
if [ "$SAVE_REPORT" = true ]; then
    echo ""
    echo -e "${BLUE}Diagnostic report saved: $REPORT_FILE${NC}"
    echo ""
    echo "Include this file when reporting issues:"
    echo "  https://github.com/yourusername/mcp-n8n/issues/new"
fi

echo ""
echo "For more help, see:"
echo "  - docs/TROUBLESHOOTING.md"
echo "  - just check-env (environment validation)"
echo "  - just smoke (quick health check)"

exit $ERRORS
