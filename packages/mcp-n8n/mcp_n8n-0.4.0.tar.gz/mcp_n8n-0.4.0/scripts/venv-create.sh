#!/usr/bin/env bash
# venv-create.sh - Create and configure virtual environment
#
# Usage: ./scripts/venv-create.sh [--force]

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

FORCE=false
if [ "${1:-}" = "--force" ]; then
    FORCE=true
fi

echo "=== Virtual Environment Setup ==="
echo ""

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11.9"

if [ -f .python-version ]; then
    REQUIRED_VERSION=$(cat .python-version)
fi

echo -e "${YELLOW}Checking Python version...${NC}"
if ! python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo -e "${RED}Error: Python 3.11+ required. Current: ${PYTHON_VERSION}${NC}"
    echo "Install Python ${REQUIRED_VERSION} or higher"
    exit 1
fi
echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"
echo ""

# Check if venv already exists
if [ -d .venv ] && [ "$FORCE" = false ]; then
    echo -e "${YELLOW}Virtual environment already exists at .venv${NC}"
    echo "Use --force to recreate it"
    exit 0
fi

# Remove existing venv if force flag set
if [ -d .venv ] && [ "$FORCE" = true ]; then
    echo -e "${YELLOW}Removing existing virtual environment...${NC}"
    rm -rf .venv
    echo -e "${GREEN}✓ Removed${NC}"
    echo ""
fi

# Create venv
echo -e "${YELLOW}Creating virtual environment...${NC}"
python -m venv .venv
echo -e "${GREEN}✓ Virtual environment created${NC}"
echo ""

# Activate venv
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded to $(pip --version | awk '{print $2}')${NC}"
echo ""

# Install package with dev dependencies
echo -e "${YELLOW}Installing package with dev dependencies...${NC}"
pip install -e ".[dev]"
echo -e "${GREEN}✓ Package installed${NC}"
echo ""

# Verify installation
echo -e "${YELLOW}Verifying installation...${NC}"
EXPECTED_PACKAGES=("pytest" "mypy" "ruff" "black" "pre-commit")
ALL_FOUND=true

for pkg in "${EXPECTED_PACKAGES[@]}"; do
    if pip show "$pkg" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $pkg"
    else
        echo -e "  ${RED}✗${NC} $pkg (missing)"
        ALL_FOUND=false
    fi
done

if [ "$ALL_FOUND" = false ]; then
    echo ""
    echo -e "${RED}Some packages are missing. Installation may have failed.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Virtual environment ready!${NC}"
echo ""
echo "To activate:"
echo "  source .venv/bin/activate"
echo ""
echo "To deactivate:"
echo "  deactivate"
