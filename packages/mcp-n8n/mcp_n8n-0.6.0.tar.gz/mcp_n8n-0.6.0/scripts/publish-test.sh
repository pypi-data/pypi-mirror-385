#!/usr/bin/env bash
# publish-test.sh - Publish to TestPyPI for validation
#
# Usage: ./scripts/publish-test.sh
#
# Publishes the package to TestPyPI (test.pypi.org) for validation before
# publishing to production PyPI.

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Publish to TestPyPI ===${NC}"
echo ""

# Check if twine is available
if ! python -c "import twine" 2>/dev/null; then
    echo -e "${RED}Error: 'twine' not found${NC}"
    echo ""
    echo "Install with:"
    echo "  pip install -e '.[release]'"
    exit 1
fi

# Check if dist/ exists and has files
if [ ! -d "dist" ] || [ -z "$(ls -A dist 2>/dev/null)" ]; then
    echo -e "${RED}Error: No distribution files found${NC}"
    echo ""
    echo "Build the package first:"
    echo "  just build"
    exit 1
fi

# Display what will be uploaded
echo "Distribution files to upload:"
for file in dist/*; do
    SIZE=$(du -h "$file" | cut -f1)
    echo "  - $(basename "$file") ($SIZE)"
done
echo ""

# Check for TestPyPI credentials
echo -e "${YELLOW}Checking TestPyPI credentials...${NC}"
echo ""

PYPIRC_FILE="$HOME/.pypirc"
HAS_TESTPYPI_CONFIG=false

if [ -f "$PYPIRC_FILE" ]; then
    if grep -q "\[testpypi\]" "$PYPIRC_FILE"; then
        HAS_TESTPYPI_CONFIG=true
        echo -e "${GREEN}✓${NC} Found TestPyPI configuration in ~/.pypirc"
    fi
fi

if [ "$HAS_TESTPYPI_CONFIG" = false ]; then
    echo -e "${YELLOW}⚠${NC} No TestPyPI configuration found in ~/.pypirc"
    echo ""
    echo "You can either:"
    echo ""
    echo "1. Configure ~/.pypirc with TestPyPI token:"
    echo "   [testpypi]"
    echo "   username = __token__"
    echo "   password = pypi-AgEIcH... (your TestPyPI API token)"
    echo ""
    echo "2. Set environment variable:"
    echo "   export TWINE_PASSWORD=pypi-AgEIcH..."
    echo ""
    echo "3. You'll be prompted for credentials during upload"
    echo ""
fi

# Confirm upload
read -p "Upload to TestPyPI? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted.${NC}"
    exit 0
fi

# Upload to TestPyPI
echo ""
echo -e "${YELLOW}Uploading to TestPyPI...${NC}"
echo ""

if twine upload --repository testpypi dist/*; then
    echo ""
    echo -e "${GREEN}✓ Successfully uploaded to TestPyPI${NC}"
else
    echo ""
    echo -e "${RED}✗ Upload failed${NC}"
    exit 1
fi

# Get package name and version
PACKAGE_NAME=$(grep "^name = " pyproject.toml | sed 's/name = "\(.*\)"/\1/')
VERSION=$(grep "^version = " pyproject.toml | sed 's/version = "\(.*\)"/\1/')

echo ""
echo -e "${GREEN}=== TestPyPI Upload Complete ===${NC}"
echo ""
echo "Package: $PACKAGE_NAME"
echo "Version: $VERSION"
echo ""
echo "View on TestPyPI:"
echo "  https://test.pypi.org/project/$PACKAGE_NAME/$VERSION/"
echo ""
echo "Test installation:"
echo ""
echo "  # Create clean test environment"
echo "  python -m venv test-venv"
echo "  source test-venv/bin/activate"
echo ""
echo "  # Install from TestPyPI"
echo "  pip install --index-url https://test.pypi.org/simple/ \\"
echo "    --extra-index-url https://pypi.org/simple/ \\"
echo "    $PACKAGE_NAME==$VERSION"
echo ""
echo "  # Test the package"
echo "  $PACKAGE_NAME --help"
echo ""
echo "  # Cleanup"
echo "  deactivate"
echo "  rm -rf test-venv"
echo ""
echo "If everything works, publish to production:"
echo "  just publish-prod"
