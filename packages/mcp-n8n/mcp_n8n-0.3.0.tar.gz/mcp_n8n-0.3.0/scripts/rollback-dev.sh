#!/usr/bin/env bash
# rollback-dev.sh - Quick rollback from dev to stable backend
#
# Usage: ./scripts/rollback-dev.sh

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=== Quick Rollback: Dev → Stable ==="
echo ""
echo -e "${RED}⚠️  WARNING: This will switch you to stable backend${NC}"
echo ""
echo "This script will:"
echo "  1. Backup your current MCP config"
echo "  2. Guide you through switching to stable"
echo "  3. Run verification tests"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Detect MCP client
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
CURSOR_CONFIG="$HOME/.cursor/mcp.json"

CONFIG_FILE=""
CLIENT=""

if [ -f "$CLAUDE_CONFIG" ]; then
    CONFIG_FILE="$CLAUDE_CONFIG"
    CLIENT="Claude Desktop"
elif [ -f "$CURSOR_CONFIG" ]; then
    CONFIG_FILE="$CURSOR_CONFIG"
    CLIENT="Cursor"
else
    echo -e "${RED}Error: No MCP config found${NC}"
    echo ""
    echo "Expected at:"
    echo "  - $CLAUDE_CONFIG"
    echo "  - $CURSOR_CONFIG"
    echo ""
    echo "Create config first using:"
    echo "  cp .config/claude-desktop.example.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json"
    exit 1
fi

echo ""
echo "Detected MCP client: $CLIENT"
echo "Config file: $CONFIG_FILE"
echo ""

# Backup current config
BACKUP_FILE="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
echo -e "${YELLOW}Backing up current config...${NC}"
cp "$CONFIG_FILE" "$BACKUP_FILE"
echo -e "${GREEN}✓ Backup saved: $BACKUP_FILE${NC}"
echo ""

# Instructions for manual edit (safer than auto-editing JSON)
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}MANUAL STEP REQUIRED:${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo ""
echo "Edit your MCP config to enable stable backend:"
echo ""
echo "  1. Open: $CONFIG_FILE"
echo "  2. Find the 'mcp-n8n-dev' section"
echo "  3. Comment it out or remove it completely"
echo "  4. Enable 'mcp-n8n-stable' or 'mcp-n8n' section"
echo "  5. Save the file"
echo ""
echo -e "${YELLOW}Example stable config:${NC}"
echo ""
cat <<'EOF'
{
  "mcpServers": {
    "mcp-n8n": {
      "command": "mcp-n8n",
      "args": [],
      "env": {
        "ANTHROPIC_API_KEY": "your_key",
        "CODA_API_KEY": "your_key"
      }
    }
  }
}
EOF
echo ""
echo -e "${YELLOW}Quick open commands:${NC}"
if [ "$CLIENT" = "Claude Desktop" ]; then
    echo "  open \"$CONFIG_FILE\""
else
    echo "  code \"$CONFIG_FILE\""
fi
echo ""
read -p "Press Enter after you've edited and saved the config..."

# Remind to restart
echo ""
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo -e "${YELLOW}RESTART YOUR MCP CLIENT:${NC}"
echo -e "${YELLOW}═══════════════════════════════════════${NC}"
echo ""
if [ "$CLIENT" = "Claude Desktop" ]; then
    echo "  - Quit Claude Desktop completely (Cmd+Q)"
    echo "  - Reopen Claude Desktop"
else
    echo "  - In Cursor: Cmd+Shift+P → 'Developer: Reload Window'"
fi
echo ""
read -p "Press Enter after restarting..."

# Run verification
echo ""
echo -e "${YELLOW}Running verification tests...${NC}"
echo ""

if ./scripts/verify-stable.sh; then
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ ROLLBACK COMPLETE!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    echo "You're now running stable backend."
    echo ""
    echo "Your config backup is at:"
    echo "  $BACKUP_FILE"
    echo ""
    echo "Next steps:"
    echo "  1. Test tool calls in $CLIENT"
    echo "  2. Document issue in KNOWN_ISSUES.md"
    echo "  3. Debug dev issue when not blocked"
    echo ""
    echo "To switch back to dev later, see:"
    echo "  .config/dev-vs-stable.md"
    exit 0
else
    echo ""
    echo -e "${RED}═══════════════════════════════════════${NC}"
    echo -e "${RED}⚠️  VERIFICATION FAILED${NC}"
    echo -e "${RED}═══════════════════════════════════════${NC}"
    echo ""
    echo "Stable backend verification failed."
    echo ""
    echo "Possible issues:"
    echo "  - mcp-n8n package not installed (run: pip install mcp-n8n)"
    echo "  - API keys not set in environment"
    echo "  - Config still points to dev backend"
    echo ""
    echo "Your config backup is at:"
    echo "  $BACKUP_FILE"
    echo ""
    echo "Get help:"
    echo "  - Check: docs/ROLLBACK_PROCEDURE.md"
    echo "  - Run: just check-env"
    exit 1
fi
