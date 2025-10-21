#!/usr/bin/env bash
# bump-version.sh - Semantic version bumping for mcp-n8n
#
# Usage: ./scripts/bump-version.sh <major|minor|patch> [--dry-run]
#
# Bumps the version in pyproject.toml according to semantic versioning.

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

PYPROJECT_FILE="pyproject.toml"

# Parse arguments
BUMP_TYPE="${1:-}"
DRY_RUN=false

if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Bump type required${NC}"
    echo ""
    echo "Usage: $0 <major|minor|patch> [--dry-run]"
    echo ""
    echo "Examples:"
    echo "  $0 patch          # 0.1.0 → 0.1.1"
    echo "  $0 minor          # 0.1.0 → 0.2.0"
    echo "  $0 major          # 0.1.0 → 1.0.0"
    echo "  $0 patch --dry-run  # Preview without changing"
    exit 1
fi

if [ "${2:-}" = "--dry-run" ]; then
    DRY_RUN=true
fi

# Validate bump type
if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo -e "${RED}Error: Invalid bump type '$BUMP_TYPE'${NC}"
    echo "Must be one of: major, minor, patch"
    exit 1
fi

# Check if pyproject.toml exists
if [ ! -f "$PYPROJECT_FILE" ]; then
    echo -e "${RED}Error: $PYPROJECT_FILE not found${NC}"
    exit 1
fi

# Extract current version
CURRENT_VERSION=$(grep "^version = " "$PYPROJECT_FILE" | sed 's/version = "\(.*\)"/\1/')

if [ -z "$CURRENT_VERSION" ]; then
    echo -e "${RED}Error: Could not find version in $PYPROJECT_FILE${NC}"
    exit 1
fi

# Validate version format (semver: X.Y.Z)
if [[ ! "$CURRENT_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}Error: Invalid version format '$CURRENT_VERSION'${NC}"
    echo "Expected semver format: X.Y.Z (e.g., 0.1.0)"
    exit 1
fi

# Parse version components
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Calculate new version
case "$BUMP_TYPE" in
    major)
        NEW_MAJOR=$((MAJOR + 1))
        NEW_MINOR=0
        NEW_PATCH=0
        ;;
    minor)
        NEW_MAJOR=$MAJOR
        NEW_MINOR=$((MINOR + 1))
        NEW_PATCH=0
        ;;
    patch)
        NEW_MAJOR=$MAJOR
        NEW_MINOR=$MINOR
        NEW_PATCH=$((PATCH + 1))
        ;;
esac

NEW_VERSION="${NEW_MAJOR}.${NEW_MINOR}.${NEW_PATCH}"

# Display version change
echo -e "${BLUE}=== Version Bump: $BUMP_TYPE ===${NC}"
echo ""
echo -e "Current version: ${YELLOW}$CURRENT_VERSION${NC}"
echo -e "New version:     ${GREEN}$NEW_VERSION${NC}"
echo ""

# Dry-run mode
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}[DRY RUN] Would update $PYPROJECT_FILE${NC}"
    echo ""
    echo "To apply this change, run:"
    echo "  $0 $BUMP_TYPE"
    exit 0
fi

# Confirm before updating
read -p "Update version in $PYPROJECT_FILE? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted.${NC}"
    exit 0
fi

# Update version in pyproject.toml
# Use portable sed syntax that works on both macOS and Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS requires -i with backup extension
    sed -i.bak "s/^version = \".*\"/version = \"$NEW_VERSION\"/" "$PYPROJECT_FILE"
    rm "${PYPROJECT_FILE}.bak"
else
    # Linux
    sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" "$PYPROJECT_FILE"
fi

# Verify the change
UPDATED_VERSION=$(grep "^version = " "$PYPROJECT_FILE" | sed 's/version = "\(.*\)"/\1/')

if [ "$UPDATED_VERSION" = "$NEW_VERSION" ]; then
    echo -e "${GREEN}✓ Successfully bumped version${NC}"
    echo ""
    echo "Updated: $PYPROJECT_FILE"
    echo ""
    echo "Next steps:"
    echo "  1. Review the change: git diff $PYPROJECT_FILE"
    echo "  2. Update CHANGELOG.md with release notes"
    echo "  3. Commit: git add $PYPROJECT_FILE CHANGELOG.md"
    echo "  4. Or use: just prepare-release $BUMP_TYPE (automates steps 1-3)"
else
    echo -e "${RED}✗ Version update failed${NC}"
    echo "Expected: $NEW_VERSION"
    echo "Got: $UPDATED_VERSION"
    exit 1
fi
