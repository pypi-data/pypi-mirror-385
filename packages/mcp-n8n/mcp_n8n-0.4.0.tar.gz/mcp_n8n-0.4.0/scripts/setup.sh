#!/usr/bin/env bash
# setup.sh - One-command project setup for mcp-n8n
#
# Usage: ./scripts/setup.sh

set -euo pipefail

echo "=== mcp-n8n Setup Script ==="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if ! python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo -e "${RED}Error: Python 3.11+ is required. Current version: ${PYTHON_VERSION}${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"
echo ""

# Check for just command runner
echo -e "${YELLOW}Checking for 'just' command runner...${NC}"
if ! command -v just &> /dev/null; then
    echo -e "${YELLOW}Warning: 'just' not found. Install it for easier task automation:${NC}"
    echo "  brew install just  # macOS"
    echo "  cargo install just # Rust"
    echo "  https://github.com/casey/just"
    echo ""
else
    echo -e "${GREEN}✓ just found${NC}"
    echo ""
fi

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -e ".[dev]"
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Setup pre-commit hooks
echo -e "${YELLOW}Installing pre-commit hooks...${NC}"
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo -e "${GREEN}✓ Pre-commit hooks installed${NC}"
else
    echo -e "${YELLOW}Warning: pre-commit not found. Run 'pip install pre-commit' to enable git hooks.${NC}"
fi
echo ""

# Check for environment file
echo -e "${YELLOW}Checking environment configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found.${NC}"
    echo "  Copy .env.example to .env and configure:"
    echo "  cp .env.example .env"
    echo ""
    echo "  Required environment variables:"
    echo "  - ANTHROPIC_API_KEY (for Chora Composer backend)"
    echo "  - CODA_API_KEY (for Coda MCP backend)"
else
    echo -e "${GREEN}✓ .env file found${NC}"
fi
echo ""

# Run quality checks
echo -e "${YELLOW}Running quality checks...${NC}"
if command -v just &> /dev/null; then
    just check
else
    echo "Running linting..."
    ruff check src/mcp_n8n tests || true
    echo ""
    echo "Running type checking..."
    mypy src/mcp_n8n || true
fi
echo -e "${GREEN}✓ Quality checks complete${NC}"
echo ""

# Run tests
echo -e "${YELLOW}Running tests...${NC}"
pytest
echo -e "${GREEN}✓ Tests passed${NC}"
echo ""

# Summary
echo "=== Setup Complete ==="
echo ""
echo "Quick start commands:"
echo "  just run          # Start the gateway"
echo "  just test         # Run tests"
echo "  just verify       # Run all checks before committing"
echo "  just --list       # Show all available commands"
echo ""
echo -e "${GREEN}Ready to develop!${NC}"
