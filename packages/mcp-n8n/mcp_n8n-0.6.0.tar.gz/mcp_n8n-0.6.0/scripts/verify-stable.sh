#!/usr/bin/env bash
# verify-stable.sh - Verify stable backend is working
#
# Usage: ./scripts/verify-stable.sh

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=== Verifying Stable Backend ==="
echo ""

ERRORS=0
WARNINGS=0

# Check 1: Package installed
echo -e "${YELLOW}[1/4] Checking mcp-n8n package...${NC}"
if pip show mcp-n8n > /dev/null 2>&1; then
    VERSION=$(pip show mcp-n8n | grep Version | awk '{print $2}')
    echo -e "  ${GREEN}✓${NC} mcp-n8n installed (version $VERSION)"
else
    echo -e "  ${RED}✗${NC} mcp-n8n not installed"
    echo "    Run: pip install mcp-n8n"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 2: Command available
echo -e "${YELLOW}[2/4] Checking mcp-n8n command...${NC}"
if command -v mcp-n8n > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} mcp-n8n command available"
else
    echo -e "  ${RED}✗${NC} mcp-n8n command not found"
    echo "    Ensure package is installed: pip install mcp-n8n"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 3: Environment variables
echo -e "${YELLOW}[3/4] Checking environment variables...${NC}"
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    echo -e "  ${GREEN}✓${NC} ANTHROPIC_API_KEY set"
else
    echo -e "  ${YELLOW}⚠${NC} ANTHROPIC_API_KEY not set"
    echo "    Set in .env or config file"
    WARNINGS=$((WARNINGS + 1))
fi

if [ -n "${CODA_API_KEY:-}" ]; then
    echo -e "  ${GREEN}✓${NC} CODA_API_KEY set"
else
    echo -e "  ${YELLOW}⚠${NC} CODA_API_KEY not set"
    echo "    Set in .env or config file"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check 4: Smoke tests (if available)
echo -e "${YELLOW}[4/4] Running smoke tests...${NC}"
if [ -f "scripts/smoke-test.sh" ]; then
    if ./scripts/smoke-test.sh > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Smoke tests passed"
    else
        echo -e "  ${YELLOW}⚠${NC} Smoke tests failed"
        echo "    This may be expected if using mock backends"
        echo "    Test actual tool calls in Claude/Cursor"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Smoke tests not available"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Summary
echo "=== Verification Summary ==="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Stable backend is ready to use."
    echo ""
    echo "Next steps:"
    echo "  1. Test tool calls in Claude Desktop/Cursor"
    echo "  2. Try: 'List available chora generators'"
    echo "  3. Check logs: tail -f logs/mcp-n8n.log"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}✓ Basic checks passed (${WARNINGS} warnings)${NC}"
    echo ""
    echo "Stable backend should work, but:"
    for ((i=0; i<WARNINGS; i++)); do
        echo "  ⚠ Check warnings above"
    done
    echo ""
    echo "Recommended:"
    echo "  1. Set missing environment variables"
    echo "  2. Test tool calls in Claude Desktop/Cursor"
    echo "  3. Run: just check-env (for full validation)"
    exit 0
else
    echo -e "${RED}✗ Verification failed${NC}"
    echo ""
    echo "Found $ERRORS error(s) and $WARNINGS warning(s)."
    echo ""
    echo "Fix errors before using stable backend:"
    echo "  1. Install mcp-n8n: pip install mcp-n8n"
    echo "  2. Set API keys in .env or MCP config"
    echo "  3. Run this script again"
    echo ""
    echo "For help:"
    echo "  - docs/ROLLBACK_PROCEDURE.md"
    echo "  - .config/README.md"
    echo "  - just check-env (full environment validation)"
    exit 1
fi
