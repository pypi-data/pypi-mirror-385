#!/bin/bash
# mcp-tool.sh - Wrapper script for calling MCP tools from n8n workflows
#
# Usage: ./mcp-tool.sh <tool_name> <arguments_json>
#
# Example:
#   ./mcp-tool.sh "chora:list_generators" '{}'
#   ./mcp-tool.sh "chora:generate_content" '{"content_config_id":"welcome-message","context":{}}'

set -e  # Exit on error

TOOL_NAME="$1"
ARGUMENTS_JSON="${2:-{}}"

if [ -z "$TOOL_NAME" ]; then
    echo "Error: Tool name required" >&2
    echo "Usage: $0 <tool_name> <arguments_json>" >&2
    exit 1
fi

# Validate JSON arguments
if ! echo "$ARGUMENTS_JSON" | jq empty 2>/dev/null; then
    echo "Error: Invalid JSON in arguments" >&2
    exit 1
fi

# Construct JSON-RPC request
REQUEST=$(cat <<EOF
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "$TOOL_NAME",
    "arguments": $ARGUMENTS_JSON
  }
}
EOF
)

# Change to mcp-n8n directory
MCP_DIR="/Users/victorpiper/code/mcp-n8n"
cd "$MCP_DIR"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Call mcp-n8n via STDIO
# - Echo request to stdin
# - Run gateway in STDIO mode
# - Suppress stderr (startup messages)
# - Extract result using jq
echo "$REQUEST" | python -m mcp_n8n.gateway 2>/dev/null | jq -r '.result.content[0].text'
