# mcp-n8n Architecture

## Overview

mcp-n8n implements **Pattern P5 (Gateway & Aggregator)** from the MCP Server Patterns Catalog, also known as the **Meta-MCP Server** pattern. It provides a unified MCP interface to multiple specialized backend servers, with **Chora Composer** as the exclusive mechanism for artifact creation.

## Pattern P5: Gateway & Aggregator

From the MCP Server Patterns Catalog:

> Rather than a single server providing one domain of tools, this pattern composes multiple MCP servers or routes connections in a flexible way. An MCP Gateway might sit in front of several tool-specific servers and present a unified interface, or dynamically load/unload servers.

### Key Characteristics

- **Single Entry Point**: AI clients connect once to get all capabilities
- **Tool Namespacing**: Tools prefixed by backend (e.g., `chora:`, `coda:`)
- **Capability Aggregation**: Merges tools/resources/prompts from multiple backends
- **Routing Logic**: Forwards requests to appropriate backend based on namespace
- **Centralized Auth**: Gateway manages credentials for all backends

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│         AI Client (Claude Desktop / Cursor)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ JSON-RPC 2.0 over STDIO
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              mcp-n8n Gateway Server                     │
│              (src/mcp_n8n/gateway.py)                   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │        FastMCP Server Instance                   │  │
│  │  - Handle initialize, tools/list, tools/call     │  │
│  │  - Expose gateway_status tool                    │  │
│  └──────────────────────────────────────────────────┘  │
│                        │                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │        Backend Registry                          │  │
│  │  (src/mcp_n8n/backends/registry.py)              │  │
│  │  - Manage backend lifecycle                      │  │
│  │  - Route tool calls by namespace                 │  │
│  │  - Aggregate capabilities                        │  │
│  └──────────────────────────────────────────────────┘  │
│                        │                                │
│         ┌──────────────┴──────────────┐                │
│         ▼                              ▼                │
│  ┌─────────────────┐          ┌─────────────────┐      │
│  │ Chora Composer  │          │   Coda MCP      │      │
│  │    Backend      │          │    Backend      │      │
│  │  (subprocess)   │          │  (subprocess)   │      │
│  └─────────────────┘          └─────────────────┘      │
└──────┬──────────────────────────────┬──────────────────┘
       │                              │
       ▼                              ▼
┌──────────────────┐          ┌──────────────────┐
│  chora-compose   │          │    coda-mcp      │
│   MCP Server     │          │   MCP Server     │
│  (subprocess)    │          │  (subprocess)    │
└────────┬─────────┘          └────────┬─────────┘
         │                              │
         ▼                              ▼
   Artifact Ops                    Coda API
   (generate,                      (docs, tables,
    assemble)                       rows)
```

## Component Descriptions

### Gateway Server (`gateway.py`)

The main entry point that:
- Initializes FastMCP server on STDIO transport
- Loads configuration from environment
- Registers and starts backend servers
- Exposes `gateway_status` tool for health monitoring
- Handles graceful shutdown

### Backend Registry (`backends/registry.py`)

Manages multiple backend servers:
- **Registration**: Register backends with unique names and namespaces
- **Lifecycle**: Start/stop all backends as a group
- **Routing**: Map namespaced tool names to backends
- **Aggregation**: Merge tools/resources/prompts from all backends
- **Status**: Track health of each backend

### Backend Base Classes (`backends/base.py`)

Abstract interfaces for backend integration:

- **`Backend`**: Abstract base class defining backend interface
- **`StdioSubprocessBackend`**: Implementation for subprocess-based backends
- **`BackendStatus`**: Enum for tracking backend state (STOPPED, STARTING, RUNNING, FAILED)
- **`BackendError`**: Exception type for backend failures

### Specialized Backends

#### Chora Composer Backend (`backends/chora_composer.py`)

Exclusive artifact creation mechanism:

**Tools** (namespaced as `chora:*`):
- `generate_content` - Generate content from templates
- `assemble_artifact` - **PRIMARY ARTIFACT ASSEMBLY TOOL**
- `list_generators` - List available generators
- `validate_content` - Validate configurations

**Key Behavior**:
- Enforces that ALL artifact operations go through Chora Composer
- Logs artifact assembly operations for telemetry
- Requires `ANTHROPIC_API_KEY` for AI-powered generation

#### Coda MCP Backend (`backends/coda_mcp.py`)

Data operations on Coda documents:

**Tools** (namespaced as `coda:*`):
- `list_docs` - List Coda documents
- `list_tables` - List tables in a document
- `list_rows` - List rows from a table
- `create_hello_doc_in_folder` - Create sample document

**Key Behavior**:
- Provides read/write access to Coda
- Requires `CODA_API_KEY` for all operations
- Can store artifact metadata in Coda tables

### Configuration (`config.py`)

Pydantic-based configuration management:

- **`GatewayConfig`**: Main gateway settings
- **`BackendConfig`**: Per-backend configuration
- **`BackendType`**: Enum for integration methods

Supports:
- Environment variables (`.env` file)
- Prefix: `MCP_N8N_*`
- Validation and type safety
- Default values

## Tool Namespacing

All tools are namespaced by backend to prevent conflicts:

| Namespace | Backend | Purpose | Example Tool |
|-----------|---------|---------|--------------|
| `chora:` | Chora Composer | Artifact creation | `chora:assemble_artifact` |
| `coda:` | Coda MCP | Data operations | `coda:list_docs` |

### Routing Algorithm

1. Client calls `tools/call` with namespaced name (e.g., `chora:assemble_artifact`)
2. Gateway parses namespace prefix (`chora`)
3. Registry looks up backend by namespace
4. Backend found → strip namespace, forward to backend
5. Backend not found → return error

## Request Flow

### Example: Artifact Assembly

```
1. Client → Gateway
   tools/call {
     name: "chora:assemble_artifact",
     arguments: {
       artifact_config_id: "user-documentation",
       output_path: "/output/docs.md"
     }
   }

2. Gateway → Registry
   route_tool_call("chora:assemble_artifact")
   → returns (ChoraComposerBackend, "assemble_artifact")

3. Gateway → Chora Composer Backend
   call_tool("assemble_artifact", {...})
   (strips namespace prefix)

4. Chora Composer Backend → chora-compose subprocess
   JSON-RPC over STDIO:
   {
     "jsonrpc": "2.0",
     "method": "tools/call",
     "params": {
       "name": "assemble_artifact",
       "arguments": {...}
     }
   }

5. chora-compose → Chora Composer Backend
   Returns result:
   {
     "success": true,
     "artifact_id": "user-documentation",
     "output_path": "/output/docs.md",
     "content_count": 5,
     "size_bytes": 15234
   }

6. Chora Composer Backend → Gateway
   Forwards result (no modification)

7. Gateway → Client
   Returns namespaced result
```

## Backend Lifecycle

### Startup Sequence

1. Load configuration from environment (`.env` file)
2. Create `BackendRegistry` instance
3. Register each enabled backend:
   - Chora Composer (if `ANTHROPIC_API_KEY` present)
   - Coda MCP (if `CODA_API_KEY` present)
4. Start all backends concurrently:
   - Spawn subprocess with command + args
   - Set environment variables
   - Wait for process to initialize
   - Discover capabilities (tools/resources/prompts)
5. Mark backends as RUNNING or FAILED
6. Log aggregated tool count

### Shutdown Sequence

1. Receive interrupt signal (Ctrl+C)
2. Call `registry.stop_all()`
3. For each backend:
   - Send terminate signal to subprocess
   - Wait 5 seconds for graceful shutdown
   - Force kill if still running
4. Mark backends as STOPPED
5. Exit gateway

## Configuration

### Environment Variables

```bash
# Gateway behavior
MCP_N8N_LOG_LEVEL=INFO        # Log level
MCP_N8N_DEBUG=0               # Debug mode
MCP_N8N_BACKEND_TIMEOUT=30    # Backend timeout (seconds)

# Chora Composer
ANTHROPIC_API_KEY=sk-...      # Required for Chora Composer

# Coda MCP
CODA_API_KEY=...              # Required for Coda MCP
CODA_FOLDER_ID=...            # Optional, for write operations
```

### Backend Configuration Model

```python
BackendConfig(
    name="chora-composer",         # Unique identifier
    type=BackendType.STDIO_SUBPROCESS,
    command="chora-compose",       # Executable command
    args=[],                       # Command arguments
    enabled=True,                  # Whether to start
    namespace="chora",             # Tool namespace prefix
    capabilities=["artifacts"],    # Capability tags
    env={"ANTHROPIC_API_KEY": "..."}, # Environment variables
    timeout=30                     # Operation timeout
)
```

## Security Model

### Credential Management

- **Gateway holds all credentials**: Backends receive via environment injection
- **No credentials in logs**: Sensitive values redacted
- **No credentials in errors**: Client-visible errors sanitized
- **Environment-based**: All secrets from `.env` or system environment

### Backend Isolation

- Each backend runs as separate subprocess
- No shared memory between backends
- Process-level isolation enforced by OS
- Subprocess failures don't crash gateway

### Artifact Path Validation

- Validate output paths before forwarding to Chora Composer
- Prevent path traversal attacks
- Enforce allowed directories (future enhancement)

## Extensibility

### Adding a New Backend

1. **Create backend class**:
   ```python
   class MyBackend(StdioSubprocessBackend):
       def __init__(self, config: BackendConfig):
           super().__init__(config)
   ```

2. **Implement `_initialize()`**:
   ```python
   async def _initialize(self):
       self._tools = [...]  # Discover tools
   ```

3. **Add configuration helper**:
   ```python
   def get_my_backend_config(self) -> BackendConfig:
       return BackendConfig(name="my-backend", ...)
   ```

4. **Register in `get_all_backend_configs()`**:
   ```python
   backends = [
       self.get_chora_composer_config(),
       self.get_coda_mcp_config(),
       self.get_my_backend_config(),  # Add here
   ]
   ```

### Supported Backend Types

- **STDIO_SUBPROCESS**: Spawn as subprocess (current implementation)
- **STDIO_EXTERNAL**: Connect to external process (future)
- **HTTP_SSE**: Connect via HTTP+SSE (future)

## Testing Strategy

### Unit Tests

- Configuration loading and validation
- Tool namespacing logic
- Routing algorithm
- Backend lifecycle state transitions

### Integration Tests

- Gateway ↔ Backend communication
- Mock backends for testing routing
- End-to-end tool call flow

### BDD Scenarios

Following DRSO principles:
- Scenario: Artifact creation routes to Chora Composer
- Scenario: Tool namespacing prevents conflicts
- Scenario: Backend failure isolation

## Performance Considerations

### Latency

- Gateway routing overhead: < 10ms
- Subprocess startup: ~1-2s per backend
- Tool call forwarding: < 5ms (after startup)

### Scalability

- Current: Single-tenant, local deployment
- Future: Multi-tenant with backend pooling
- Future: Remote backends via HTTP+SSE

### Resource Usage

- One subprocess per backend
- Memory: ~50MB per backend
- CPU: Minimal when idle

## Future Enhancements

### Phase 2: Advanced Routing

- Tool-level routing (not just namespace)
- Conditional routing based on arguments
- Load balancing across backend instances

### Phase 3: Dynamic Backend Management

- Add/remove backends at runtime
- Backend health checks and circuit breakers
- Automatic restart on failure

### Phase 4: Multi-Tenant Support

- Per-user backend instances
- OAuth integration (Pattern P4)
- User-scoped credentials

### Phase 5: Telemetry & Observability

- DRSO-aligned telemetry emission
- Change signals for backend state transitions
- OpenTelemetry integration

## References

- [MCP Server Patterns Catalog](../MCP%20Server%20Patterns%20Catalog.pdf) - Pattern P5
- [Chora Composer](../chora-composer/) - Artifact generation backend
- Coda MCP - Optional data operations backend
- [FastMCP Documentation](https://github.com/anthropics/mcp-python) - MCP SDK
