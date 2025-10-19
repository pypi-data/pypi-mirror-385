#!/usr/bin/env bash
# prepare-release.sh - Automated release preparation
#
# Usage: ./scripts/prepare-release.sh <major|minor|patch>
#
# This script automates the release preparation process:
# 1. Bumps version in pyproject.toml
# 2. Updates CHANGELOG.md (moves [Unreleased] to [version])
# 3. Runs pre-merge checks
# 4. Creates release commit

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

BUMP_TYPE="${1:-}"

# Validate arguments
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Bump type required${NC}"
    echo ""
    echo "Usage: $0 <major|minor|patch>"
    echo ""
    echo "This script will:"
    echo "  1. Bump version in pyproject.toml"
    echo "  2. Update CHANGELOG.md"
    echo "  3. Run pre-merge verification"
    echo "  4. Create release commit"
    exit 1
fi

if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo -e "${RED}Error: Invalid bump type '$BUMP_TYPE'${NC}"
    echo "Must be one of: major, minor, patch"
    exit 1
fi

echo -e "${BLUE}=== Prepare Release: $BUMP_TYPE ===${NC}"
echo ""

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}Error: Uncommitted changes detected${NC}"
    echo ""
    echo "Please commit or stash your changes before preparing a release."
    echo ""
    git status --short
    exit 1
fi

# Step 1: Bump version
echo -e "${YELLOW}[1/4] Bumping version...${NC}"
CURRENT_VERSION=$(grep "^version = " pyproject.toml | sed 's/version = "\(.*\)"/\1/')

# Calculate new version (same logic as bump-version.sh)
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"
case "$BUMP_TYPE" in
    major)
        NEW_VERSION="$((MAJOR + 1)).0.0"
        ;;
    minor)
        NEW_VERSION="${MAJOR}.$((MINOR + 1)).0"
        ;;
    patch)
        NEW_VERSION="${MAJOR}.${MINOR}.$((PATCH + 1))"
        ;;
esac

echo "  Current: $CURRENT_VERSION → New: $NEW_VERSION"

# Update version in pyproject.toml
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i.bak "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    rm pyproject.toml.bak
else
    sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
fi

echo -e "  ${GREEN}✓${NC} Version bumped to $NEW_VERSION"
echo ""

# Step 2: Update CHANGELOG.md
echo -e "${YELLOW}[2/4] Updating CHANGELOG.md...${NC}"

if [ ! -f "CHANGELOG.md" ]; then
    echo -e "  ${RED}✗${NC} CHANGELOG.md not found"
    exit 1
fi

# Check if [Unreleased] section has entries
if ! grep -q "## \[Unreleased\]" CHANGELOG.md; then
    echo -e "  ${RED}✗${NC} No [Unreleased] section in CHANGELOG.md"
    exit 1
fi

# Get today's date
RELEASE_DATE=$(date +%Y-%m-%d)

# Create new CHANGELOG with:
# 1. Keep header
# 2. Add new empty [Unreleased] section
# 3. Convert old [Unreleased] to [NEW_VERSION]
# 4. Keep rest of file

# Use a temporary file for the update
TEMP_CHANGELOG=$(mktemp)

awk -v version="$NEW_VERSION" -v date="$RELEASE_DATE" '
BEGIN { unreleased_done = 0 }

# Print lines before [Unreleased]
/^## \[Unreleased\]/ && !unreleased_done {
    print "## [Unreleased]"
    print ""
    print "No unreleased changes yet."
    print ""
    print "## [" version "] - " date
    unreleased_done = 1
    next
}

# Print all other lines
{ print }
' CHANGELOG.md > "$TEMP_CHANGELOG"

# Replace original with updated version
mv "$TEMP_CHANGELOG" CHANGELOG.md

echo -e "  ${GREEN}✓${NC} CHANGELOG.md updated"
echo ""

# Step 3: Run pre-merge checks
echo -e "${YELLOW}[3/4] Running pre-merge checks...${NC}"
echo ""

if ! ./scripts/pre-merge.sh; then
    echo ""
    echo -e "${RED}✗ Pre-merge checks failed${NC}"
    echo ""
    echo "Please fix the issues and try again."
    echo ""
    echo "To rollback changes:"
    echo "  git checkout pyproject.toml CHANGELOG.md"
    exit 1
fi

echo ""
echo -e "  ${GREEN}✓${NC} All pre-merge checks passed"
echo ""

# Step 4: Create release commit
echo -e "${YELLOW}[4/4] Creating release commit...${NC}"

git add pyproject.toml CHANGELOG.md

git commit -m "$(cat <<EOF
Release v${NEW_VERSION}

Bump version to ${NEW_VERSION} and update CHANGELOG.

Release prepared with:
  ./scripts/prepare-release.sh ${BUMP_TYPE}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

echo -e "  ${GREEN}✓${NC} Release commit created"
echo ""

# Summary
echo -e "${GREEN}=== Release Preparation Complete ===${NC}"
echo ""
echo "Version: $NEW_VERSION"
echo "Release date: $RELEASE_DATE"
echo ""
echo "Next steps:"
echo ""
echo "  1. Review the changes:"
echo "     git show HEAD"
echo ""
echo "  2. Build and test the package:"
echo "     just build"
echo "     just publish-test  # Test on TestPyPI"
echo ""
echo "  3. Create release tag:"
echo "     git tag v${NEW_VERSION}"
echo ""
echo "  4. Push to remote:"
echo "     git push && git push --tags"
echo ""
echo "  5. Publish to PyPI:"
echo "     just publish-prod  # Production release"
echo ""
echo "Or follow the full checklist:"
echo "  docs/RELEASE_CHECKLIST.md"
