"""Mock MCP server for integration testing.

This minimal MCP server simulates a backend (like chora-composer) to test
gateway subprocess communication, namespace routing, and error handling.
"""

import json
import sys
from typing import Any


def create_response(id: int | str, result: Any) -> dict[str, Any]:
    """Create JSON-RPC success response."""
    return {"jsonrpc": "2.0", "id": id, "result": result}


def create_error(id: int | str, code: int, message: str) -> dict[str, Any]:
    """Create JSON-RPC error response."""
    return {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    """Handle JSON-RPC request.

    Implements minimal MCP protocol responses for testing.
    """
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id", 0)

    # Initialize response (MCP initialize method)
    if method == "initialize":
        return create_response(
            request_id,
            {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "mock-mcp-server",
                    "version": "1.0.0",
                },
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {},
                },
            },
        )

    # List tools
    elif method == "tools/list":
        return create_response(
            request_id,
            {
                "tools": [
                    {
                        "name": "mock_generate",
                        "description": "Mock content generation tool",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"},
                            },
                            "required": ["content"],
                        },
                    },
                    {
                        "name": "mock_assemble",
                        "description": "Mock artifact assembly tool",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "pieces": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["pieces"],
                        },
                    },
                ]
            },
        )

    # Call tool
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "mock_generate":
            content = arguments.get("content", "default content")
            return create_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Generated: {content}",
                        }
                    ],
                    "isError": False,
                },
            )

        elif tool_name == "mock_assemble":
            pieces = arguments.get("pieces", [])
            return create_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"Assembled {len(pieces)} pieces: "
                                f"{', '.join(pieces)}"
                            ),
                        }
                    ],
                    "isError": False,
                },
            )

        elif tool_name == "mock_error":
            # Test error handling
            return create_error(request_id, -32000, "Mock error for testing")

        else:
            return create_error(request_id, -32601, f"Unknown tool: {tool_name}")

    # Unknown method
    else:
        return create_error(request_id, -32601, f"Unknown method: {method}")


def main() -> None:
    """Run mock MCP server on STDIO.

    Reads JSON-RPC requests from stdin, writes responses to stdout.
    Uses stderr for logging (not visible to client).
    """
    # Log startup
    print(f"Mock MCP server starting (pid={sys.argv})", file=sys.stderr, flush=True)

    try:
        while True:
            # Read request from stdin
            line = sys.stdin.readline()
            if not line:
                break  # EOF

            # Parse JSON-RPC request
            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e}", file=sys.stderr, flush=True)
                continue

            # Handle request
            response = handle_request(request)

            # Write response to stdout
            json.dump(response, sys.stdout)
            sys.stdout.write("\n")
            sys.stdout.flush()

    except KeyboardInterrupt:
        print("Mock MCP server stopped", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"Mock MCP server error: {e}", file=sys.stderr, flush=True)
        raise


if __name__ == "__main__":
    main()
