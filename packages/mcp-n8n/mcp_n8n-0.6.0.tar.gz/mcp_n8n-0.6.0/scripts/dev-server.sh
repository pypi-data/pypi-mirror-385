#!/usr/bin/env bash
# dev-server.sh - Development server with auto-reload
#
# Usage: ./scripts/dev-server.sh
#
# Starts the MCP gateway with:
# - Auto-reload on file changes
# - Verbose debug logging
# - Pretty-printed JSON-RPC
# - Error highlighting

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}=== MCP-N8N Development Server ===${NC}"
echo ""

# Check if watchdog is available (for auto-reload)
if ! python -c "import watchdog" 2>/dev/null; then
    echo -e "${YELLOW}⚠ watchdog not installed - auto-reload disabled${NC}"
    echo ""
    echo "Install for auto-reload:"
    echo "  pip install watchdog"
    echo ""
    USE_WATCHDOG=false
else
    USE_WATCHDOG=true
    echo -e "${GREEN}✓ Auto-reload enabled${NC}"
fi

# Set development environment variables
export MCP_N8N_LOG_LEVEL=DEBUG
export MCP_N8N_DEBUG=1
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"

# Generate trace ID for this session
TRACE_ID=$(uuidgen 2>/dev/null || python -c "import uuid; print(uuid.uuid4())")
export CHORA_TRACE_ID="$TRACE_ID"

echo -e "${CYAN}Session trace ID: $TRACE_ID${NC}"
echo ""
echo "Environment:"
echo "  - Log level: DEBUG"
echo "  - Debug mode: ON"
echo "  - PYTHONPATH: $PYTHONPATH"
echo ""

if [ "$USE_WATCHDOG" = true ]; then
    echo -e "${YELLOW}Watching for changes in: src/mcp_n8n/${NC}"
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    echo "---"
    echo ""

    # Use watchmedo for auto-reload
    watchmedo auto-restart \
        --directory=src/mcp_n8n \
        --pattern="*.py" \
        --recursive \
        -- python -m mcp_n8n.gateway
else
    echo "Starting server (no auto-reload)..."
    echo ""
    echo "Press Ctrl+C to stop"
    echo ""
    echo "---"
    echo ""

    # Run without auto-reload
    python -m mcp_n8n.gateway
fi
