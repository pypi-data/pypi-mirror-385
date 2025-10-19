#!/usr/bin/env bash
# venv-clean.sh - Clean rebuild virtual environment when dependencies change
#
# Usage: ./scripts/venv-clean.sh

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=== Clean Virtual Environment Rebuild ==="
echo ""

# Check if venv exists
if [ ! -d .venv ]; then
    echo -e "${YELLOW}No virtual environment found.${NC}"
    echo "Creating new environment..."
    ./scripts/venv-create.sh
    exit $?
fi

# Warn user
echo -e "${YELLOW}This will delete and recreate your virtual environment.${NC}"
echo ""
echo "Current venv location: .venv/"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Remove venv
echo ""
echo -e "${YELLOW}Removing existing virtual environment...${NC}"
rm -rf .venv
echo -e "${GREEN}✓ Removed${NC}"
echo ""

# Recreate
echo -e "${YELLOW}Creating fresh virtual environment...${NC}"
./scripts/venv-create.sh

echo ""
echo -e "${GREEN}Clean rebuild complete!${NC}"
echo ""
echo "Don't forget to activate the new environment:"
echo "  source .venv/bin/activate"
