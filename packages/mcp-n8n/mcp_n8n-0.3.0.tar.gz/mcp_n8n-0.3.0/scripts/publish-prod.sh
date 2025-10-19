#!/usr/bin/env bash
# publish-prod.sh - Publish to production PyPI
#
# Usage: ./scripts/publish-prod.sh
#
# Publishes the package to production PyPI (pypi.org) and creates a git tag.
# This is the final step in the release process.

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Publish to Production PyPI ===${NC}"
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

# Get package info
PACKAGE_NAME=$(grep "^name = " pyproject.toml | sed 's/name = "\(.*\)"/\1/')
VERSION=$(grep "^version = " pyproject.toml | sed 's/version = "\(.*\)"/\1/')
TAG_NAME="v${VERSION}"

# Check if git tag already exists
if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
    echo -e "${RED}Error: Git tag '$TAG_NAME' already exists${NC}"
    echo ""
    echo "This version has already been released."
    echo ""
    echo "To release a new version:"
    echo "  1. Bump version: just prepare-release patch"
    echo "  2. Build: just build"
    echo "  3. Publish: just publish-prod"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠ Warning: Uncommitted changes detected${NC}"
    echo ""
    git status --short
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Aborted.${NC}"
        exit 0
    fi
fi

# Display what will be uploaded
echo "Package: $PACKAGE_NAME"
echo "Version: $VERSION"
echo "Git tag: $TAG_NAME"
echo ""
echo "Distribution files to upload:"
for file in dist/*; do
    SIZE=$(du -h "$file" | cut -f1)
    echo "  - $(basename "$file") ($SIZE)"
done
echo ""

# Final confirmation
echo -e "${RED}WARNING: This will publish to PRODUCTION PyPI!${NC}"
echo ""
echo "This action:"
echo "  1. Uploads package to pypi.org (IRREVERSIBLE)"
echo "  2. Creates git tag: $TAG_NAME"
echo "  3. Pushes tag to remote"
echo ""
read -p "Are you absolutely sure? Type 'yes' to confirm: " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Aborted.${NC}"
    exit 0
fi

# Upload to PyPI
echo ""
echo -e "${YELLOW}Uploading to PyPI...${NC}"
echo ""

if twine upload dist/*; then
    echo ""
    echo -e "${GREEN}✓ Successfully uploaded to PyPI${NC}"
else
    echo ""
    echo -e "${RED}✗ Upload failed${NC}"
    echo ""
    echo "The package was NOT published."
    echo "Fix the issue and try again."
    exit 1
fi

# Create git tag
echo ""
echo -e "${YELLOW}Creating git tag...${NC}"

if git tag -a "$TAG_NAME" -m "Release $VERSION"; then
    echo -e "  ${GREEN}✓${NC} Created tag: $TAG_NAME"
else
    echo -e "  ${RED}✗${NC} Failed to create tag"
    echo ""
    echo "WARNING: Package was published but tag creation failed."
    echo "Create tag manually:"
    echo "  git tag -a $TAG_NAME -m 'Release $VERSION'"
    exit 1
fi

# Push tag to remote
echo ""
echo -e "${YELLOW}Pushing tag to remote...${NC}"

if git push origin "$TAG_NAME"; then
    echo -e "  ${GREEN}✓${NC} Pushed tag to remote"
else
    echo -e "  ${RED}✗${NC} Failed to push tag"
    echo ""
    echo "WARNING: Package published and tag created, but push failed."
    echo "Push tag manually:"
    echo "  git push origin $TAG_NAME"
    exit 1
fi

# Summary
echo ""
echo -e "${GREEN}=== Production Release Complete ===${NC}"
echo ""
echo "Package: $PACKAGE_NAME"
echo "Version: $VERSION"
echo "Git tag: $TAG_NAME"
echo ""
echo "View on PyPI:"
echo "  https://pypi.org/project/$PACKAGE_NAME/$VERSION/"
echo ""
echo "Installation:"
echo "  pip install $PACKAGE_NAME==$VERSION"
echo ""
echo "Post-release tasks:"
echo ""
echo "  1. Create GitHub release (if applicable):"
echo "     https://github.com/yourusername/mcp-n8n/releases/new?tag=$TAG_NAME"
echo ""
echo "  2. Announce the release:"
echo "     - Update documentation"
echo "     - Post to relevant channels"
echo "     - Update project website"
echo ""
echo "  3. Start next development cycle:"
echo "     - Update CHANGELOG.md with [Unreleased] section"
echo "     - Plan next version features"
echo ""
echo "Congratulations! 🎉"
