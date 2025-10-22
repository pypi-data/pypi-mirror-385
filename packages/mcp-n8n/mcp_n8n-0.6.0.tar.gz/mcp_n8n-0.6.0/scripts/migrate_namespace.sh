#!/bin/bash
# migrate_namespace.sh - Migrate MCP server to new namespace
#
# This script updates all MCP tool names and resource URIs from one namespace
# to another, following Chora MCP Conventions v1.0.
#
# Usage:
#   ./scripts/migrate_namespace.sh <old_namespace> <new_namespace>
#   ./scripts/migrate_namespace.sh "" "mcpn8n"  # Add namespacing
#
# WARNING: This is a breaking change for clients using your MCP server.
#          Always increment major version after running this script.
#
# Reference:
#   https://github.com/liminalcommons/chora-base/blob/main/docs/standards/CHORA_MCP_CONVENTIONS_v1.0.md

set -e  # Exit on error

# === Configuration ===

OLD_NAMESPACE="$1"
NEW_NAMESPACE="$2"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# === Validation ===

if [ -z "$NEW_NAMESPACE" ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo ""
    echo "Usage: $0 <old_namespace> <new_namespace>"
    echo ""
    echo "Examples:"
    echo "  # Add namespacing (empty old namespace)"
    echo "  $0 \"\" \"mcpn8n\""
    echo ""
    echo "  # Change namespace"
    echo "  $0 \"oldname\" \"newname\""
    exit 1
fi

# Validate new namespace format (lowercase, alphanumeric, 3-20 chars)
if ! echo "$NEW_NAMESPACE" | grep -E '^[a-z][a-z0-9]{2,19}$' > /dev/null; then
    echo -e "${RED}Error: Invalid namespace format: ${NEW_NAMESPACE}${NC}"
    echo ""
    echo "Namespace must:"
    echo "  - Start with lowercase letter"
    echo "  - Be 3-20 characters"
    echo "  - Contain only lowercase letters and digits (no hyphens/underscores)"
    echo ""
    echo "Examples: chora, myproject, taskmaster"
    exit 1
fi

# === Confirmation ===

echo -e "${YELLOW}⚠️  WARNING: This will modify your codebase${NC}"
echo ""
if [ -z "$OLD_NAMESPACE" ]; then
    echo "  Adding namespacing:"
    echo "    tool_name → ${NEW_NAMESPACE}:tool_name"
    echo "    type://id → ${NEW_NAMESPACE}://type/id"
else
    echo "  Changing namespace:"
    echo "    ${OLD_NAMESPACE}:* → ${NEW_NAMESPACE}:*"
    echo "    ${OLD_NAMESPACE}://* → ${NEW_NAMESPACE}://*"
fi
echo ""
echo "  This is a BREAKING CHANGE for MCP clients."
echo "  You must:"
echo "    1. Increment major version"
echo "    2. Update client configurations"
echo "    3. Update ecosystem registry"
echo "    4. Document in CHANGELOG.md"
echo ""

# Check for uncommitted changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo -e "${RED}Error: You have uncommitted changes${NC}"
    echo "Please commit or stash your changes before migrating."
    git status --short
    exit 1
fi

read -p "Continue? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Migration cancelled."
    exit 0
fi

# === Migration ===

echo -e "${GREEN}Starting migration...${NC}"
echo ""

# Function to replace in files
replace_in_files() {
    local pattern="$1"
    local replacement="$2"
    local description="$3"

    echo "  $description"

    # Use different find syntax depending on platform
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        find src/ -name "*.py" -exec sed -i '' "s|${pattern}|${replacement}|g" {} \;
    else
        # Linux
        find src/ -name "*.py" -exec sed -i "s|${pattern}|${replacement}|g" {} \;
    fi
}

# Migrate tool names
if [ -z "$OLD_NAMESPACE" ]; then
    # Adding namespacing - this requires more careful handling
    echo "⚠️  Adding namespacing requires manual review"
    echo "  Automated replacement not safe (could match non-tool strings)"
    echo "  Please update tool names manually in:"
    echo "    - src/mcp_n8n/gateway.py"
    echo "    - Any tool call sites"
else
    # Changing namespace - safe to automate
    replace_in_files \
        "${OLD_NAMESPACE}:" \
        "${NEW_NAMESPACE}:" \
        "Updating tool names (${OLD_NAMESPACE}:* → ${NEW_NAMESPACE}:*)"

    replace_in_files \
        "${OLD_NAMESPACE}://" \
        "${NEW_NAMESPACE}://" \
        "Updating resource URIs (${OLD_NAMESPACE}://* → ${NEW_NAMESPACE}://*)"
fi

# Update MCP module configuration
if [ -f "src/mcp_n8n/mcp/__init__.py" ]; then
    echo "  Updating src/mcp_n8n/mcp/__init__.py"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/NAMESPACE = \"${OLD_NAMESPACE}\"/NAMESPACE = \"${NEW_NAMESPACE}\"/g" \
            src/mcp_n8n/mcp/__init__.py
    else
        sed -i "s/NAMESPACE = \"${OLD_NAMESPACE}\"/NAMESPACE = \"${NEW_NAMESPACE}\"/g" \
            src/mcp_n8n/mcp/__init__.py
    fi
fi

# Update README.md if it contains namespace references
if [ -f "README.md" ] && grep -q "$OLD_NAMESPACE" README.md 2>/dev/null; then
    echo "  Updating README.md"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/${OLD_NAMESPACE}:/${NEW_NAMESPACE}:/g" README.md
        sed -i '' "s/${OLD_NAMESPACE}:\/\//${NEW_NAMESPACE}:\/\//g" README.md
    else
        sed -i "s/${OLD_NAMESPACE}:/${NEW_NAMESPACE}:/g" README.md
        sed -i "s/${OLD_NAMESPACE}:\/\//${NEW_NAMESPACE}:\/\//g" README.md
    fi
fi

echo ""
echo -e "${GREEN}✅ Migration complete!${NC}"
echo ""

# === Post-Migration Checklist ===

echo -e "${YELLOW}📋 Post-migration checklist:${NC}"
echo ""
echo "1. Review changes:"
echo "   git diff"
echo ""
echo "2. Validate naming conventions:"
echo "   python scripts/validate_mcp_names.py"
echo ""
echo "3. Run tests:"
echo "   pytest"
echo ""
echo "4. Update version (BREAKING CHANGE):"
echo "   # Increment major version (e.g., 1.0.0 → 2.0.0)"
echo "   ./scripts/bump-version.sh major"
echo ""
echo "5. Update CHANGELOG.md:"
echo "   # Document namespace change as breaking change"
echo "   vim CHANGELOG.md"
echo ""
echo "6. Update client configurations:"
if [ -z "$OLD_NAMESPACE" ]; then
    echo "   # Update tool calls to use namespace prefix"
    echo "   # Example: 'tool_name' → '${NEW_NAMESPACE}:tool_name'"
else
    echo "   # Update tool calls with new namespace"
    echo "   # Example: '${OLD_NAMESPACE}:tool' → '${NEW_NAMESPACE}:tool'"
fi
echo ""
echo "7. Update ecosystem registry:"
echo "   # Submit PR to chora-base updating namespace registry"
echo "   # https://github.com/liminalcommons/chora-base"
echo ""
echo "8. Commit changes:"
echo "   git add -A"
echo "   git commit -m \"BREAKING CHANGE: Migrate namespace to ${NEW_NAMESPACE}\""
echo ""

# Show diff summary
echo "Changed files:"
git diff --stat
echo ""

echo -e "${YELLOW}⚠️  Remember: This is a breaking change!${NC}"
echo "Update documentation and notify users before releasing."
