#!/usr/bin/env bash
# pre-merge.sh - Pre-merge verification checks
#
# Usage: ./scripts/pre-merge.sh
#
# Runs comprehensive checks before merging to ensure code quality.

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=== Pre-Merge Verification ==="
echo ""
echo "Running comprehensive checks before merge..."
echo ""

ERRORS=0
WARNINGS=0

# Check 1: Pre-commit hooks
echo -e "${YELLOW}[1/6] Running pre-commit hooks...${NC}"
if pre-commit run --all-files; then
    echo -e "  ${GREEN}✓${NC} All pre-commit hooks passed"
else
    echo -e "  ${RED}✗${NC} Pre-commit hooks failed"
    echo "    Fix issues and try again"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 2: Smoke tests
echo -e "${YELLOW}[2/6] Running smoke tests...${NC}"
if ./scripts/smoke-test.sh > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Smoke tests passed"
else
    echo -e "  ${RED}✗${NC} Smoke tests failed"
    echo "    Run: just smoke (for details)"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 3: Full test suite with coverage
echo -e "${YELLOW}[3/6] Running full test suite with coverage...${NC}"
if pytest tests/ --cov=src/mcp_n8n --cov-report=term-missing --cov-fail-under=85 > /dev/null 2>&1; then
    COVERAGE=$(pytest tests/ --cov=src/mcp_n8n --cov-report=term 2>/dev/null | grep "TOTAL" | awk '{print $4}' || echo "unknown")
    echo -e "  ${GREEN}✓${NC} Tests passed with $COVERAGE coverage"
else
    echo -e "  ${RED}✗${NC} Tests failed or coverage below 85%"
    echo "    Run: pytest tests/ --cov=src/mcp_n8n --cov-report=term-missing"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 4: CHANGELOG.md has [Unreleased] entries
echo -e "${YELLOW}[4/6] Checking CHANGELOG.md...${NC}"
if [ -f "CHANGELOG.md" ]; then
    if grep -q "## \[Unreleased\]" CHANGELOG.md; then
        # Check if there are any entries under [Unreleased]
        if awk '/## \[Unreleased\]/,/## \[/ {if (/^### (Added|Changed|Deprecated|Removed|Fixed|Security)/ && getline && NF > 0) exit 0} END {exit 1}' CHANGELOG.md; then
            echo -e "  ${GREEN}✓${NC} CHANGELOG.md has unreleased entries"
        else
            echo -e "  ${YELLOW}⚠${NC} CHANGELOG.md [Unreleased] section is empty"
            echo "    Add entries describing your changes"
            WARNINGS=$((WARNINGS + 1))
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} CHANGELOG.md missing [Unreleased] section"
        echo "    Add entries describing your changes"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "  ${RED}✗${NC} CHANGELOG.md not found"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 5: Uncommitted changes
echo -e "${YELLOW}[5/6] Checking for uncommitted changes...${NC}"
if [ -z "$(git status --porcelain)" ]; then
    echo -e "  ${GREEN}✓${NC} No uncommitted changes"
else
    echo -e "  ${YELLOW}⚠${NC} Uncommitted changes detected"
    echo "    Consider committing or stashing before merge"
    git status --short
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check 6: Version bump (if applicable)
echo -e "${YELLOW}[6/6] Checking version...${NC}"
if [ -f "pyproject.toml" ]; then
    CURRENT_VERSION=$(grep "^version = " pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    echo -e "  ${GREEN}✓${NC} Current version: $CURRENT_VERSION"

    # Check if this is a release commit (has version tag in git history)
    if git log --oneline -1 | grep -qE "v?[0-9]+\.[0-9]+\.[0-9]+"; then
        echo "    This appears to be a release commit"
        echo "    Ensure version was bumped appropriately"
    else
        echo "    Version bump will be needed for next release"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} pyproject.toml not found"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Summary
echo "=== Verification Summary ==="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Ready to merge."
    echo ""
    echo "Next steps:"
    echo "  1. Review your changes one last time"
    echo "  2. Merge to main branch"
    echo "  3. Tag release if needed: git tag v<version>"
    echo "  4. Push: git push && git push --tags"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}✓ Critical checks passed (${WARNINGS} warnings)${NC}"
    echo ""
    echo "Safe to merge, but consider addressing warnings:"
    for ((i=0; i<WARNINGS; i++)); do
        echo "  ⚠ Check warnings above"
    done
    echo ""
    echo "Recommended:"
    echo "  1. Address CHANGELOG.md entries"
    echo "  2. Commit outstanding changes"
    echo "  3. Run this script again"
    exit 0
else
    echo -e "${RED}✗ Verification failed${NC}"
    echo ""
    echo "Found $ERRORS error(s) and $WARNINGS warning(s)."
    echo ""
    echo "DO NOT merge until all errors are fixed:"
    echo "  1. Fix pre-commit issues: pre-commit run --all-files"
    echo "  2. Fix test failures: pytest tests/ -v"
    echo "  3. Update CHANGELOG.md with your changes"
    echo "  4. Run this script again"
    echo ""
    echo "For help:"
    echo "  - just test (run full test suite)"
    echo "  - just smoke (quick validation)"
    echo "  - CHANGELOG.md (see format examples)"
    exit 1
fi
