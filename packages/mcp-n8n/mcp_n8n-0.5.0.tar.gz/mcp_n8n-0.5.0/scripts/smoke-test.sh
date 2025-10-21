#!/usr/bin/env bash
# smoke-test.sh - Quick smoke test suite (<30 seconds)
#
# Usage: ./scripts/smoke-test.sh

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=== Smoke Test Suite ==="
echo ""
echo "Running quick validation tests..."
echo ""

# Run pytest on smoke tests only
if pytest tests/smoke/ -v --tb=short --no-header --color=yes; then
    echo ""
    echo -e "${GREEN}✓ All smoke tests passed!${NC}"
    echo ""
    echo "Gateway core functionality validated:"
    echo "  - Module imports work"
    echo "  - Configuration loading works"
    echo "  - Namespace routing works (chora:*, coda:*)"
    echo "  - Backends are isolated"
    echo ""
    echo "Ready for development or deployment."
    exit 0
else
    echo ""
    echo -e "${RED}✗ Smoke tests failed${NC}"
    echo ""
    echo "One or more core functions are broken."
    echo "Fix issues before proceeding."
    echo ""
    echo "To debug:"
    echo "  pytest tests/smoke/ -vv --tb=long"
    exit 1
fi
