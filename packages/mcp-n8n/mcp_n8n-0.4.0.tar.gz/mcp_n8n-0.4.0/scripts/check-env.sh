#!/usr/bin/env bash
# check-env.sh - Pre-flight environment validation
#
# Usage: ./scripts/check-env.sh

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=== Environment Validation ==="
echo ""

ERRORS=0
WARNINGS=0

# Check 1: Python version
echo -e "${YELLOW}[1/8] Checking Python version...${NC}"
if [ -f .python-version ]; then
    REQUIRED=$(cat .python-version)
    CURRENT=$(python --version 2>&1 | awk '{print $2}')
    if [ "$CURRENT" = "$REQUIRED" ]; then
        echo -e "  ${GREEN}✓${NC} Python ${CURRENT} (matches .python-version)"
    else
        echo -e "  ${YELLOW}⚠${NC} Python ${CURRENT} (expected ${REQUIRED})"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "  ${YELLOW}⚠${NC} No .python-version file"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check 2: Virtual environment
echo -e "${YELLOW}[2/8] Checking virtual environment...${NC}"
if [ -n "${VIRTUAL_ENV:-}" ]; then
    echo -e "  ${GREEN}✓${NC} Active venv: ${VIRTUAL_ENV}"
elif [ -d .venv ]; then
    echo -e "  ${YELLOW}⚠${NC} venv exists but not activated"
    echo "    Run: source .venv/bin/activate"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "  ${RED}✗${NC} No virtual environment found"
    echo "    Run: ./scripts/venv-create.sh"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 3: Required packages
echo -e "${YELLOW}[3/8] Checking required packages...${NC}"
REQUIRED_PACKAGES=("fastmcp" "pydantic" "pytest" "mypy" "ruff")
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if python -c "import $pkg" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $pkg"
    else
        echo -e "  ${RED}✗${NC} $pkg (missing)"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# Check 4: Environment variables
echo -e "${YELLOW}[4/8] Checking environment variables...${NC}"
REQUIRED_VARS=("ANTHROPIC_API_KEY" "CODA_API_KEY")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -n "${!var:-}" ]; then
        echo -e "  ${GREEN}✓${NC} $var (set)"
    else
        echo -e "  ${RED}✗${NC} $var (not set)"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# Check 5: .env file
echo -e "${YELLOW}[5/8] Checking .env file...${NC}"
if [ -f .env ]; then
    echo -e "  ${GREEN}✓${NC} .env file exists"
else
    echo -e "  ${YELLOW}⚠${NC} No .env file"
    echo "    Copy from: cp .env.example .env"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check 6: pre-commit hooks
echo -e "${YELLOW}[6/8] Checking pre-commit hooks...${NC}"
if [ -f .git/hooks/pre-commit ]; then
    echo -e "  ${GREEN}✓${NC} pre-commit hooks installed"
else
    echo -e "  ${YELLOW}⚠${NC} pre-commit hooks not installed"
    echo "    Run: pre-commit install"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check 7: Git status
echo -e "${YELLOW}[7/8] Checking git status...${NC}"
if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} No uncommitted changes"
else
    echo -e "  ${YELLOW}⚠${NC} Uncommitted changes present"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check 8: Backend availability (quick check)
echo -e "${YELLOW}[8/8] Checking backend paths...${NC}"
CHORA_PATH="/Users/victorpiper/code/chora-compose"
CODA_PATH="/Users/victorpiper/code/mcp-server-coda"

if [ -d "$CHORA_PATH" ]; then
    echo -e "  ${GREEN}✓${NC} chora-compose found"
else
    echo -e "  ${YELLOW}⚠${NC} chora-compose not found at $CHORA_PATH"
    WARNINGS=$((WARNINGS + 1))
fi

if [ -d "$CODA_PATH" ]; then
    echo -e "  ${GREEN}✓${NC} coda-mcp found"
else
    echo -e "  ${YELLOW}⚠${NC} coda-mcp not found at $CODA_PATH"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Summary
echo "=== Summary ==="
echo ""
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Environment ready for development."
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ ${WARNINGS} warning(s)${NC}"
    echo ""
    echo "Environment usable but some issues detected."
    exit 0
else
    echo -e "${RED}✗ ${ERRORS} error(s), ${WARNINGS} warning(s)${NC}"
    echo ""
    echo "Please fix errors before proceeding."
    exit 1
fi
