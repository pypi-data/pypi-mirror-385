---
title: "Tools Reference"
type: reference
audience: all
version: 0.4.0
test_extraction: yes
category: tools
source: "src/mcp_n8n/gateway.py, src/mcp_n8n/backends/chora_composer.py, tests/features/"
last_updated: 2025-10-21
---

# Tools Reference

## Overview

Complete reference for all MCP tools available through the mcp-n8n gateway.

**Status:** ✅ Stable
**Version:** 0.4.0
**Last Updated:** 2025-10-21

---

## Tool Namespacing

All backend tools are namespaced to prevent conflicts:

**Format:** `{namespace}:{tool_name}`

**Namespaces:**
- **(no namespace)** - Gateway-level tools (status, events)
- `chora` - Chora Composer tools (artifact creation)
- `coda` - Coda MCP tools (document operations)

**Example:**
```json
{
  "tool": "chora:generate_content",
  "arguments": {...}
}
```

---

## Gateway Tools

### gateway_status

**Namespace:** None (gateway-level tool)
**Description:** Get status of the gateway and all backends
**Implementation:** [gateway.py:152-178](../../src/mcp_n8n/gateway.py#L152-L178)

**Parameters:** None

**Returns:**
```typescript
{
  gateway: {
    name: string;              // "mcp-n8n"
    version: string;           // e.g., "0.4.0"
    config: {
      log_level: string;       // "INFO", "DEBUG", etc.
      debug: boolean;
      backend_timeout: number; // seconds
    };
    event_monitoring: {
      enabled: boolean;
      webhook_configured: boolean;
    };
  };
  backends: {
    [backend_name: string]: {
      status: "running" | "stopped" | "error";
      namespace: string;
      tool_count: number;
    };
  };
  capabilities: {
    tools: number;     // Total tool count
    resources: number; // Total resource count
    prompts: number;   // Total prompt count
  };
}
```

**Example Request:**
```json
{
  "tool": "gateway_status",
  "arguments": {}
}
```

**Example Response:**
```json
{
  "gateway": {
    "name": "mcp-n8n",
    "version": "0.4.0",
    "config": {
      "log_level": "INFO",
      "debug": false,
      "backend_timeout": 30
    },
    "event_monitoring": {
      "enabled": true,
      "webhook_configured": true
    }
  },
  "backends": {
    "chora-composer": {
      "status": "running",
      "namespace": "chora",
      "tool_count": 4
    },
    "coda-mcp": {
      "status": "running",
      "namespace": "coda",
      "tool_count": 4
    }
  },
  "capabilities": {
    "tools": 10,
    "resources": 2,
    "prompts": 0
  }
}
```

**Use Cases:**
- Health checks
- Debugging connectivity issues
- Discovering available tools
- Monitoring backend status

---

### get_events

**Namespace:** None (gateway-level tool)
**Description:** Query telemetry events from gateway event log
**Implementation:** [gateway.py:182-226](../../src/mcp_n8n/gateway.py#L182-L226)

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `trace_id` | string | No | `null` | Filter by trace ID (returns all events for this trace) |
| `event_type` | string | No | `null` | Filter by event type (e.g., "gateway.started") |
| `status` | string | No | `null` | Filter by status ("success", "failure", "pending") |
| `since` | string | No | `null` | Time range (e.g., "24h", "7d", ISO timestamp) |
| `limit` | integer | No | `100` | Maximum events to return (max: 1000) |

**Returns:**
```typescript
Array<{
  timestamp: string;        // ISO 8601 format
  trace_id: string;         // UUID v4
  status: "success" | "failure" | "pending";
  schema_version: string;   // "1.0"
  event_type: string;       // e.g., "gateway.started"
  source: string;           // e.g., "mcp-n8n"
  metadata: object;         // Event-specific data
}>
```

**Example 1: Get All Events for a Trace**
```json
{
  "tool": "get_events",
  "arguments": {
    "trace_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Response:**
```json
[
  {
    "timestamp": "2025-10-21T14:32:10.123456+00:00",
    "trace_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "success",
    "schema_version": "1.0",
    "event_type": "gateway.started",
    "source": "mcp-n8n",
    "metadata": {
      "version": "0.4.0",
      "backend_count": 2
    }
  }
]
```

**Example 2: Get Recent Failures**
```json
{
  "tool": "get_events",
  "arguments": {
    "status": "failure",
    "since": "1h",
    "limit": 10
  }
}
```

**Example 3: Get Backend Registration Events**
```json
{
  "tool": "get_events",
  "arguments": {
    "event_type": "gateway.backend_registered",
    "since": "24h"
  }
}
```

**Time Range Formats:**
- Relative: `"1h"`, `"24h"`, `"7d"`, `"30d"`, `"1y"`
- ISO 8601: `"2025-10-21T00:00:00Z"`

**Use Cases:**
- Debugging multi-step workflows
- Correlating requests across gateway/backend boundaries
- Performance monitoring
- Error analysis
- Usage analytics

**See Also:** [Event Schema Reference](event-schema.md)

---

## Chora Composer Tools

**Namespace:** `chora`
**Backend:** chora-composer
**Documentation:** Chora Composer MCP server docs (in chora-compose package)

All Chora Composer tools are prefixed with `chora:` namespace.

### chora:generate_content

**Description:** Generate content from templates using Claude
**Category:** Content Generation

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `generator_id` | string | Yes | Generator identifier (e.g., "python_script", "markdown_doc") |
| `variables` | object | No | Template variables (key-value pairs) |
| `config` | object | No | Generator-specific configuration |

**Returns:**
```typescript
{
  content: string;           // Generated content
  generator_id: string;      // Generator used
  metadata: object;          // Generation metadata (tokens, model, etc.)
}
```

**Example:**
```json
{
  "tool": "chora:generate_content",
  "arguments": {
    "generator_id": "python_script",
    "variables": {
      "script_name": "data_processor",
      "description": "Process CSV data"
    }
  }
}
```

**Use Cases:**
- Generate code from templates
- Create documentation
- Scaffold new files
- Apply code patterns

---

### chora:assemble_artifact

**Description:** Assemble multi-file artifacts from generated content pieces
**Category:** Artifact Creation

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `artifact_config_id` | string | Yes | Artifact configuration identifier |
| `variables` | object | No | Variables to pass to all generators |
| `output_path` | string | No | Output directory path (default: temp) |

**Returns:**
```typescript
{
  artifact_id: string;       // Unique artifact identifier
  files: Array<{
    path: string;            // Relative file path
    content: string;         // File content
  }>;
  output_path: string;       // Where artifact was written
  metadata: object;          // Assembly metadata
}
```

**Example:**
```json
{
  "tool": "chora:assemble_artifact",
  "arguments": {
    "artifact_config_id": "python_package",
    "variables": {
      "package_name": "my_package",
      "version": "0.1.0"
    },
    "output_path": "./output"
  }
}
```

**Use Cases:**
- Scaffold projects (Python packages, React apps, etc.)
- Generate multi-file codebases
- Create documentation sites
- Build configuration bundles

---

### chora:list_generators

**Description:** List all available content generators
**Category:** Discovery

**Parameters:** None

**Returns:**
```typescript
Array<{
  id: string;                // Generator identifier
  name: string;              // Human-readable name
  description: string;       // What the generator creates
  category: string;          // Generator category
  variables: Array<{
    name: string;
    description: string;
    required: boolean;
    default?: any;
  }>;
}>
```

**Example Request:**
```json
{
  "tool": "chora:list_generators",
  "arguments": {}
}
```

**Example Response:**
```json
[
  {
    "id": "python_script",
    "name": "Python Script",
    "description": "Generate a Python script with argparse CLI",
    "category": "code",
    "variables": [
      {
        "name": "script_name",
        "description": "Name of the script",
        "required": true
      },
      {
        "name": "description",
        "description": "Script description",
        "required": false,
        "default": ""
      }
    ]
  }
]
```

**Use Cases:**
- Discover available generators
- Understand generator capabilities
- Build generator selection UIs
- Validate generator IDs before calling

---

### chora:validate_content

**Description:** Validate generated content or configurations
**Category:** Validation

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `content_type` | string | Yes | Type of content to validate (e.g., "python", "json", "yaml") |
| `content` | string | Yes | Content to validate |
| `strict` | boolean | No | Strict validation mode (default: true) |

**Returns:**
```typescript
{
  valid: boolean;            // Whether content is valid
  errors: Array<{
    line: number;
    column: number;
    message: string;
    severity: "error" | "warning";
  }>;
  suggestions: string[];     // Improvement suggestions
}
```

**Example:**
```json
{
  "tool": "chora:validate_content",
  "arguments": {
    "content_type": "python",
    "content": "def hello():\n  print('Hello, world!')\n"
  }
}
```

**Use Cases:**
- Validate generated code
- Check configuration files
- Lint content before saving
- Pre-commit validation

---

## Coda MCP Tools

**Namespace:** `coda`
**Backend:** coda-mcp
**Documentation:** Coda MCP server docs

All Coda MCP tools are prefixed with `coda:` namespace.

### coda:list_docs

**Description:** List Coda documents accessible with the API key
**Category:** Document Discovery

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `limit` | integer | No | `100` | Maximum documents to return |

**Returns:**
```typescript
Array<{
  id: string;                // Document ID
  type: string;              // "doc"
  href: string;              // API URL
  browserLink: string;       // Web URL
  name: string;              // Document name
  createdAt: string;         // ISO 8601 timestamp
  updatedAt: string;         // ISO 8601 timestamp
}>
```

**Example:**
```json
{
  "tool": "coda:list_docs",
  "arguments": {
    "limit": 10
  }
}
```

**Use Cases:**
- Discover available Coda documents
- Build document selection menus
- Verify document access

---

### coda:list_tables

**Description:** List tables in a Coda document
**Category:** Data Discovery

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `doc_id` | string | Yes | Coda document ID |

**Returns:**
```typescript
Array<{
  id: string;                // Table ID
  type: string;              // "table"
  href: string;              // API URL
  browserLink: string;       // Web URL
  name: string;              // Table name
  parent: object;            // Parent document info
}>
```

**Example:**
```json
{
  "tool": "coda:list_tables",
  "arguments": {
    "doc_id": "abc123xyz"
  }
}
```

**Use Cases:**
- Discover tables in a document
- Build table selection UIs
- Validate table IDs

---

### coda:list_rows

**Description:** List rows from a Coda table
**Category:** Data Retrieval

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `doc_id` | string | Yes | – | Coda document ID |
| `table_id` | string | Yes | – | Coda table ID or name |
| `limit` | integer | No | `100` | Maximum rows to return |

**Returns:**
```typescript
Array<{
  id: string;                // Row ID
  type: string;              // "row"
  href: string;              // API URL
  browserLink: string;       // Web URL
  name: string;              // Row name
  index: number;             // Row index
  createdAt: string;         // ISO 8601 timestamp
  updatedAt: string;         // ISO 8601 timestamp
  values: object;            // Column values
}>
```

**Example:**
```json
{
  "tool": "coda:list_rows",
  "arguments": {
    "doc_id": "abc123xyz",
    "table_id": "grid-xyz",
    "limit": 50
  }
}
```

**Use Cases:**
- Read data from Coda tables
- Extract structured data
- Build reports from Coda
- Sync Coda data to other systems

---

### coda:create_hello_doc_in_folder

**Description:** Create a sample "Hello World" document in a Coda folder
**Category:** Document Creation

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `folder_id` | string | No | Coda folder ID (uses default from config if not provided) |

**Returns:**
```typescript
{
  id: string;                // Created document ID
  type: string;              // "doc"
  href: string;              // API URL
  browserLink: string;       // Web URL
  name: string;              // Document name
  createdAt: string;         // ISO 8601 timestamp
}
```

**Example:**
```json
{
  "tool": "coda:create_hello_doc_in_folder",
  "arguments": {
    "folder_id": "fl_abc123"
  }
}
```

**Use Cases:**
- Test Coda write permissions
- Verify folder access
- Create sample documents
- Bootstrap new Coda workspaces

---

## Tool Discovery

### Via gateway_status

Use `gateway_status` to discover available tools dynamically:

```json
{
  "tool": "gateway_status",
  "arguments": {}
}
```

The response includes tool counts per backend:
```json
{
  "backends": {
    "chora-composer": {
      "status": "running",
      "namespace": "chora",
      "tool_count": 4
    }
  }
}
```

### Via Backend Introspection

Tools are dynamically discovered from backends during initialization. The actual tools available depend on:

1. **Backend Version** - Newer versions may add tools
2. **Configuration** - Some tools may be conditionally enabled
3. **Credentials** - Tools requiring auth won't load without credentials

**Authoritative Source:** Call `chora:list_generators` for Chora tools, `coda:list_docs` to verify Coda access.

---

## Error Handling

### Tool Not Found

**Error:**
```json
{
  "error": {
    "code": -32601,
    "message": "Tool not found: unknown_tool"
  }
}
```

**Cause:** Tool name misspelled or backend not loaded

**Solution:** Check `gateway_status` for available backends and tools

---

### Backend Not Available

**Error:**
```json
{
  "error": {
    "code": -32000,
    "message": "Backend 'chora-composer' is not running"
  }
}
```

**Cause:** Backend failed to start (missing credentials, subprocess error)

**Solution:**
1. Check `gateway_status` for backend status
2. Verify API keys are set (ANTHROPIC_API_KEY, CODA_API_KEY)
3. Check logs for backend startup errors

---

### Invalid Arguments

**Error:**
```json
{
  "error": {
    "code": -32602,
    "message": "Invalid params: 'generator_id' is required"
  }
}
```

**Cause:** Missing or invalid tool parameters

**Solution:** Check tool parameter requirements in this reference

---

### Tool Timeout

**Error:**
```json
{
  "error": {
    "code": -32000,
    "message": "Tool execution timeout (30s)"
  }
}
```

**Cause:** Backend operation exceeded timeout

**Solution:**
- Increase `MCP_N8N_BACKEND_TIMEOUT` for slow operations
- Check backend logs for performance issues
- Simplify complex tool arguments

---

## Best Practices

### 1. Always Check Backend Status First

Before calling backend tools, verify the backend is running:

```json
// ✅ Good
{"tool": "gateway_status", "arguments": {}}
// Check that backends.chora-composer.status === "running"
{"tool": "chora:generate_content", "arguments": {...}}

// ❌ Bad
{"tool": "chora:generate_content", "arguments": {...}}
// May fail if backend not running
```

### 2. Use Trace IDs for Multi-Step Workflows

Correlate events across tool calls using trace IDs:

```python
from mcp_n8n.memory import TraceContext, emit_event

with TraceContext() as trace_id:
    # All tool calls within this context share the same trace_id
    result1 = await call_tool("chora:generate_content", {...})
    result2 = await call_tool("chora:assemble_artifact", {...})

    # Query events for this trace
    events = await call_tool("get_events", {"trace_id": trace_id})
```

### 3. Handle Timeouts Gracefully

Set appropriate timeouts based on operation complexity:

```bash
# For quick operations (default)
export MCP_N8N_BACKEND_TIMEOUT=30

# For slow operations (artifact assembly, large Coda queries)
export MCP_N8N_BACKEND_TIMEOUT=120
```

### 4. Query Events for Debugging

When tool calls fail, check event log for detailed error context:

```json
{
  "tool": "get_events",
  "arguments": {
    "status": "failure",
    "since": "1h"
  }
}
```

---

## Related Documentation

- [API Reference](api.md) - JSON-RPC protocol details
- [Event Schema Reference](event-schema.md) - Event structure for get_events
- [Configuration Reference](configuration.md) - Backend configuration
- [How-To: Build Custom Workflow](../how-to/build-custom-workflow.md) - Tool orchestration
- [CLI Reference](cli-reference.md) - Gateway management

---

**Source:** [src/mcp_n8n/gateway.py](../../src/mcp_n8n/gateway.py), [src/mcp_n8n/backends/chora_composer.py](../../src/mcp_n8n/backends/chora_composer.py), BDD features
**Test Extraction:** Yes (all examples from BDD features and integration tests)
**Last Updated:** 2025-10-21
