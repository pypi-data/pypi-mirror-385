#!/usr/bin/env bash
# build-dist.sh - Build distribution packages for PyPI
#
# Usage: ./scripts/build-dist.sh
#
# Builds wheel and source distribution (sdist) for publishing to PyPI.

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Build Distribution ===${NC}"
echo ""

# Check if build module is available
if ! python -c "import build" 2>/dev/null; then
    echo -e "${RED}Error: 'build' module not found${NC}"
    echo ""
    echo "Install with:"
    echo "  pip install -e '.[release]'"
    echo ""
    echo "Or install just the build tool:"
    echo "  pip install build"
    exit 1
fi

# Step 1: Clean old artifacts
echo -e "${YELLOW}[1/4] Cleaning old build artifacts...${NC}"

rm -rf build/ dist/ *.egg-info/

echo -e "  ${GREEN}✓${NC} Cleaned: build/, dist/, *.egg-info/"
echo ""

# Step 2: Build packages
echo -e "${YELLOW}[2/4] Building wheel and source distribution...${NC}"
echo ""

if python -m build; then
    echo ""
    echo -e "  ${GREEN}✓${NC} Build completed"
else
    echo ""
    echo -e "  ${RED}✗${NC} Build failed"
    exit 1
fi
echo ""

# Step 3: Verify build outputs
echo -e "${YELLOW}[3/4] Verifying build outputs...${NC}"

if [ ! -d "dist" ]; then
    echo -e "  ${RED}✗${NC} dist/ directory not found"
    exit 1
fi

WHEEL_COUNT=$(find dist -name "*.whl" | wc -l | tr -d ' ')
SDIST_COUNT=$(find dist -name "*.tar.gz" | wc -l | tr -d ' ')

if [ "$WHEEL_COUNT" -eq 0 ]; then
    echo -e "  ${RED}✗${NC} No wheel (.whl) files found"
    exit 1
fi

if [ "$SDIST_COUNT" -eq 0 ]; then
    echo -e "  ${RED}✗${NC} No source distribution (.tar.gz) files found"
    exit 1
fi

echo -e "  ${GREEN}✓${NC} Found $WHEEL_COUNT wheel(s)"
echo -e "  ${GREEN}✓${NC} Found $SDIST_COUNT source distribution(s)"
echo ""

# List contents
echo "  Build artifacts:"
for file in dist/*; do
    SIZE=$(du -h "$file" | cut -f1)
    echo "    - $(basename "$file") ($SIZE)"
done
echo ""

# Step 4: Check package with twine
echo -e "${YELLOW}[4/4] Checking package with twine...${NC}"

if ! python -c "import twine" 2>/dev/null; then
    echo -e "  ${YELLOW}⚠${NC} twine not found (optional check skipped)"
    echo ""
    echo "  Install with: pip install -e '.[release]'"
else
    echo ""
    if twine check dist/*; then
        echo ""
        echo -e "  ${GREEN}✓${NC} Package checks passed"
    else
        echo ""
        echo -e "  ${RED}✗${NC} Package validation failed"
        exit 1
    fi
fi
echo ""

# Summary
echo -e "${GREEN}=== Build Complete ===${NC}"
echo ""
echo "Distribution packages ready in: dist/"
echo ""
echo "Next steps:"
echo ""
echo "  1. Test install locally:"
echo "     pip install dist/*.whl"
echo ""
echo "  2. Publish to TestPyPI (recommended first):"
echo "     just publish-test"
echo ""
echo "  3. Publish to production PyPI:"
echo "     just publish-prod"
echo ""
echo "  4. Or follow the release checklist:"
echo "     docs/RELEASE_CHECKLIST.md"
