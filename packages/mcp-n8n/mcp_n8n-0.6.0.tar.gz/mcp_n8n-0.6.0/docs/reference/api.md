---
title: "JSON-RPC API Reference"
type: reference
audience: advanced
version: 0.4.0
test_extraction: yes
category: api
source: "src/mcp_n8n/backends/base.py, tests/integration/test_backend_jsonrpc.py"
last_updated: 2025-10-21
---

# JSON-RPC API Reference

## Overview

Complete reference for the MCP (Model Context Protocol) JSON-RPC 2.0 API implemented by mcp-n8n gateway.

**Status:** ✅ Stable
**Protocol Version:** 2024-11-05
**JSON-RPC Version:** 2.0
**Last Updated:** 2025-10-21

---

## Protocol Information

### Transport

**Method:** STDIO (Standard Input/Output)

The gateway communicates exclusively via STDIO transport:
- **Input:** JSON-RPC requests on stdin (one per line)
- **Output:** JSON-RPC responses on stdout (one per line)
- **Logging:** Diagnostic messages on stderr (not part of protocol)

**Why STDIO?**
- Required by MCP protocol specification
- Works with Claude Desktop, Cursor, and other MCP clients
- Simple, stateless, process-based architecture

---

### Message Format

All messages follow JSON-RPC 2.0 specification:

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "method_name",
  "params": { ... }
}
```

**Response (success):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": { ... }
}
```

**Response (error):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32600,
    "message": "Error description",
    "data": { ... }
  }
}
```

**Notification (no response expected):**
```json
{
  "jsonrpc": "2.0",
  "method": "notification_name",
  "params": { ... }
}
```

---

## Error Codes

mcp-n8n uses standard JSON-RPC 2.0 error codes:

| Code | Name | Meaning |
|------|------|---------|
| -32700 | Parse error | Invalid JSON received |
| -32600 | Invalid Request | JSON-RPC structure invalid |
| -32601 | Method not found | Method does not exist |
| -32602 | Invalid params | Invalid method parameters |
| -32603 | Internal error | Server internal error |
| -32000 | Server error | Application-specific error |

**Example Error Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "error": {
    "code": -32601,
    "message": "Method not found: unknown_method"
  }
}
```

---

## Initialization Sequence

### 1. initialize

**Description:** Initialize MCP connection and negotiate capabilities

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "claude-desktop",
      "version": "1.0.0"
    }
  }
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `protocolVersion` | string | Yes | MCP protocol version (must be "2024-11-05") |
| `capabilities` | object | Yes | Client capabilities (can be empty) |
| `clientInfo` | object | Yes | Client identification |
| `clientInfo.name` | string | Yes | Client name |
| `clientInfo.version` | string | Yes | Client version |

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {}
    },
    "serverInfo": {
      "name": "mcp-n8n",
      "version": "0.4.0"
    }
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `protocolVersion` | string | MCP protocol version implemented by server |
| `capabilities` | object | Server capabilities (tools, resources, prompts) |
| `serverInfo` | object | Server identification |
| `serverInfo.name` | string | Server name ("mcp-n8n") |
| `serverInfo.version` | string | Server version (e.g., "0.4.0") |

**Implementation:** [base.py:301-312](../../src/mcp_n8n/backends/base.py#L301-L312)

**Must be called:** First, before any other method

---

### 2. initialized

**Description:** Notification from client that initialization is complete

**Notification:**
```json
{
  "jsonrpc": "2.0",
  "method": "initialized"
}
```

**Parameters:** None

**Response:** None (notification - no response)

**Purpose:** Signals to server that client has processed initialize response

---

## Tool Operations

### tools/list

**Description:** List all available tools from gateway and backends

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

**Parameters:** None (can be omitted or empty object)

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "gateway_status",
        "description": "Get status of the gateway and all backends",
        "inputSchema": {
          "type": "object",
          "properties": {},
          "required": []
        }
      },
      {
        "name": "get_events",
        "description": "Query telemetry events from gateway event log",
        "inputSchema": {
          "type": "object",
          "properties": {
            "trace_id": { "type": "string" },
            "event_type": { "type": "string" },
            "status": { "type": "string", "enum": ["success", "failure", "pending"] },
            "since": { "type": "string" },
            "limit": { "type": "integer", "default": 100 }
          },
          "required": []
        }
      },
      {
        "name": "chora:generate_content",
        "description": "Generate content from templates using Claude",
        "inputSchema": {
          "type": "object",
          "properties": {
            "generator_id": { "type": "string" },
            "variables": { "type": "object" }
          },
          "required": ["generator_id"]
        }
      }
    ]
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `tools` | array | List of tool definitions |
| `tools[].name` | string | Tool name (with namespace for backend tools) |
| `tools[].description` | string | Human-readable description |
| `tools[].inputSchema` | object | JSON Schema for tool parameters |

**Implementation:** [base.py:317-322](../../src/mcp_n8n/backends/base.py#L317-L322)

**Tool Namespacing:**
- Gateway tools: No namespace (e.g., "gateway_status")
- Backend tools: Prefixed with namespace (e.g., "chora:generate_content")

---

### tools/call

**Description:** Invoke a tool with arguments

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "gateway_status",
    "arguments": {}
  }
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Tool name (with namespace for backend tools) |
| `arguments` | object | Yes | Tool-specific arguments (can be empty) |

**Response (success):**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"gateway\": {\"name\": \"mcp-n8n\", \"version\": \"0.4.0\"}, ...}"
      }
    ]
  }
}
```

**Response (error):**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "error": {
    "code": -32601,
    "message": "Tool not found: unknown_tool"
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `content` | array | List of content items (MCP protocol structure) |
| `content[].type` | string | Content type ("text", "image", etc.) |
| `content[].text` | string | Text content (often JSON-encoded) |

**Implementation:** [base.py:224-299](../../src/mcp_n8n/backends/base.py#L224-L299)

**Content Parsing:**

The MCP protocol wraps tool results in a content structure. For text results containing JSON:

1. **Raw response:** `{"content": [{"type": "text", "text": "{\"key\": \"value\"}"}]}`
2. **Parsed result:** Client should parse `content[0].text` as JSON to get actual data

**Example: Calling Backend Tool**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "chora:generate_content",
    "arguments": {
      "generator_id": "python_script",
      "variables": {
        "script_name": "hello"
      }
    }
  }
}
```

---

## Resource Operations

### resources/list

**Description:** List available resources (future capability)

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "resources/list"
}
```

**Parameters:** None

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "resources": []
  }
}
```

**Status:** 🚧 Experimental - Resources planned for future release

**Implementation:** [base.py:328-336](../../src/mcp_n8n/backends/base.py#L328-L336)

---

### resources/read

**Description:** Read a specific resource (future capability)

**Status:** 🚧 Not yet implemented

---

## Prompt Operations

### prompts/list

**Description:** List available prompts (future capability)

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "prompts/list"
}
```

**Parameters:** None

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "prompts": []
  }
}
```

**Status:** 🚧 Experimental - Prompts planned for future release

**Implementation:** [base.py:339-347](../../src/mcp_n8n/backends/base.py#L339-L347)

---

### prompts/get

**Description:** Get a specific prompt (future capability)

**Status:** 🚧 Not yet implemented

---

## Connection Lifecycle

### Typical Session Flow

```
Client                           Gateway
  |                                 |
  |--- initialize ----------------->|
  |<-- initialize result -----------|
  |                                 |
  |--- initialized (notification) ->|
  |                                 |
  |--- tools/list ----------------->|
  |<-- tools/list result -----------|
  |                                 |
  |--- tools/call (gateway_status)->|
  |<-- result ---------------------|
  |                                 |
  |--- tools/call (chora:...) ----->|
  |     (gateway forwards to backend)
  |<-- result ---------------------|
  |                                 |
  |--- tools/call (get_events) ---->|
  |<-- result ---------------------|
  |                                 |
  (client exits - gateway terminates)
```

**Duration:** Session lasts for the lifetime of the gateway process

**Termination:** Gateway exits when stdin is closed (client disconnects)

---

## Complete Example: Full Session

### 1. Client Initialization

**Request:**
```json
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "claude-desktop", "version": "1.0.0"}}}
```

**Response:**
```json
{"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "mcp-n8n", "version": "0.4.0"}}}
```

---

### 2. Initialized Notification

**Request:**
```json
{"jsonrpc": "2.0", "method": "initialized"}
```

**Response:** (none - notification)

---

### 3. Discover Tools

**Request:**
```json
{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
```

**Response:**
```json
{"jsonrpc": "2.0", "id": 2, "result": {"tools": [{"name": "gateway_status", "description": "Get status of the gateway and all backends", "inputSchema": {"type": "object", "properties": {}, "required": []}}, {"name": "get_events", "description": "Query telemetry events", "inputSchema": {"type": "object", "properties": {"trace_id": {"type": "string"}, "limit": {"type": "integer"}}, "required": []}}, {"name": "chora:generate_content", "description": "Generate content from templates", "inputSchema": {"type": "object", "properties": {"generator_id": {"type": "string"}}, "required": ["generator_id"]}}]}}
```

---

### 4. Check Gateway Status

**Request:**
```json
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "gateway_status", "arguments": {}}}
```

**Response:**
```json
{"jsonrpc": "2.0", "id": 3, "result": {"content": [{"type": "text", "text": "{\"gateway\": {\"name\": \"mcp-n8n\", \"version\": \"0.4.0\", \"config\": {\"log_level\": \"INFO\", \"debug\": false, \"backend_timeout\": 30}}, \"backends\": {\"chora-composer\": {\"status\": \"running\", \"namespace\": \"chora\", \"tool_count\": 4}}}"}]}}
```

---

### 5. Call Backend Tool

**Request:**
```json
{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "chora:list_generators", "arguments": {}}}
```

**Response:**
```json
{"jsonrpc": "2.0", "id": 4, "result": {"content": [{"type": "text", "text": "{\"generators\": [{\"id\": \"python_script\", \"name\": \"Python Script\", \"category\": \"code\"}]}"}]}}
```

---

### 6. Query Events

**Request:**
```json
{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "get_events", "arguments": {"event_type": "gateway.started", "limit": 1}}}
```

**Response:**
```json
{"jsonrpc": "2.0", "id": 5, "result": {"content": [{"type": "text", "text": "[{\"timestamp\": \"2025-10-21T14:32:10.123456+00:00\", \"trace_id\": \"550e8400-e29b-41d4-a716-446655440000\", \"status\": \"success\", \"event_type\": \"gateway.started\", \"source\": \"mcp-n8n\"}]"}]}}
```

---

## Implementation Details

### Backend Forwarding

When a tool call targets a backend (e.g., `chora:generate_content`):

1. **Gateway receives:** `tools/call` with `name: "chora:generate_content"`
2. **Gateway strips namespace:** `"generate_content"`
3. **Gateway forwards to backend:** JSON-RPC `tools/call` to chora-composer subprocess
4. **Backend processes:** Returns result via stdout
5. **Gateway wraps result:** In MCP content structure
6. **Gateway responds:** To client with wrapped result

**Implementation:** [base.py:224-299](../../src/mcp_n8n/backends/base.py#L224-L299)

---

### Subprocess Communication

Each backend runs as a separate subprocess:

**Backend Process:**
```bash
python -m chora_compose.mcp.server
```

**Communication:**
- **stdin:** JSON-RPC requests (one per line)
- **stdout:** JSON-RPC responses (one per line)
- **stderr:** Backend logs (captured for debugging)

**Lifecycle:**
1. **Start:** Gateway spawns subprocess during initialization
2. **Initialize:** Gateway sends `initialize` JSON-RPC request
3. **Discover:** Gateway calls `tools/list`, `resources/list`, `prompts/list`
4. **Run:** Gateway forwards tool calls as needed
5. **Stop:** Gateway terminates subprocess on shutdown

**Implementation:** [base.py:158-203](../../src/mcp_n8n/backends/base.py#L158-L203)

---

## Testing JSON-RPC

### Manual Testing with stdio

You can test the gateway manually via command line:

```bash
# Start gateway
mcp-n8n

# Send initialize request (paste JSON + Enter)
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}

# Send initialized notification
{"jsonrpc": "2.0", "method": "initialized"}

# List tools
{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}

# Call gateway_status
{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "gateway_status", "arguments": {}}}

# Exit (Ctrl+D)
```

**Note:** Responses appear on stdout, logs on stderr

---

### Integration Tests

Automated tests verify JSON-RPC implementation:

**Location:** [tests/integration/test_backend_jsonrpc.py](../../tests/integration/test_backend_jsonrpc.py)

**Run tests:**
```bash
pytest tests/integration/test_backend_jsonrpc.py -v
```

**Test coverage:**
- Backend initialization
- Tool discovery
- Tool calls (success and failure)
- Sequential tool calls
- Error handling

---

## Related Documentation

- [Tools Reference](tools.md) - Available tools and parameters
- [Configuration Reference](configuration.md) - Backend configuration
- [CLI Reference](cli-reference.md) - Gateway startup
- [Event Schema Reference](event-schema.md) - Event structure for get_events tool
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/specification/) - Official MCP spec

---

**Source:** [src/mcp_n8n/backends/base.py](../../src/mcp_n8n/backends/base.py), [tests/integration/test_backend_jsonrpc.py](../../tests/integration/test_backend_jsonrpc.py)
**Test Extraction:** Yes (all examples from integration tests)
**Last Updated:** 2025-10-21
