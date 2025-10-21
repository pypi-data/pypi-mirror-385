---
title: "Understanding the Architecture"
type: explanation
audience: intermediate
category: architecture
source: "dev-docs/ARCHITECTURE.md, src/mcp_n8n/gateway.py"
last_updated: 2025-10-21
---

# Understanding the Architecture

## Overview

mcp-n8n is a **meta-MCP server** that acts as a unified gateway to multiple specialized MCP backends. Think of it as a single front door that gives AI clients access to multiple services without needing separate connections to each one.

**The core idea:** Instead of Claude Desktop connecting directly to 3-4 different MCP servers (each with its own configuration), it connects once to mcp-n8n, which routes requests to the appropriate backend server automatically.

## Context

### Background: The Multi-Server Problem

As you build MCP-enabled workflows, you quickly need multiple specialized servers:
- **Artifact generation** (chora-compose) for creating documents
- **Data operations** (coda-mcp) for spreadsheet/table access
- **Custom tools** (your own MCP servers) for domain-specific tasks

**The problem:** Managing multiple MCP server connections becomes unwieldy:
- Each server needs its own config entry in Claude Desktop
- Tool names can collide across servers
- Credentials scattered across multiple configs
- No unified monitoring or telemetry
- Difficult to coordinate operations across servers

### Alternatives Considered

**1. Direct Multi-Server Connection**
- ❌ Claude Desktop supports this, but configuration grows complex
- ❌ No tool namespacing → name collisions possible
- ❌ No centralized telemetry
- ❌ Each server manages its own lifecycle

**2. Custom Protocol Aggregator**
- ❌ Would require building custom client support
- ❌ Breaks MCP compatibility
- ✅ Full control over routing

**3. Pattern P5: Gateway & Aggregator (Chosen)**
- ✅ Maintains MCP compatibility
- ✅ Single client connection point
- ✅ Automatic tool namespacing
- ✅ Centralized credential management
- ✅ Unified telemetry and monitoring

### Constraints

1. **Must remain MCP-compliant:** Clients shouldn't know they're talking to a gateway
2. **Preserve backend isolation:** Backend failures shouldn't crash the gateway
3. **Performance:** Routing overhead must be minimal (<10ms)
4. **Compatibility:** Must work with existing MCP servers without modification

---

## The Solution

### High-Level Approach

mcp-n8n implements **Pattern P5 (Gateway & Aggregator)** from the MCP Server Patterns Catalog. It sits between AI clients and backend MCP servers, providing:

1. **Single entry point** - Clients connect once, get all tools
2. **Automatic routing** - Tool calls forwarded to correct backend based on namespace
3. **Tool aggregation** - All backend tools appear as one unified catalog
4. **Credential injection** - Gateway holds secrets, passes them to backends
5. **Centralized telemetry** - Every operation logged for debugging/analysis

```
┌─────────────────────────────────┐
│  AI Client (Claude Desktop)     │
│  "I need chora:assemble_artifact"│
└───────────────┬─────────────────┘
                │
                │ Single MCP connection
                ▼
┌───────────────────────────────────────────┐
│         mcp-n8n Gateway                   │
│  ┌─────────────────────────────────────┐ │
│  │ Tool Catalog (Aggregated):          │ │
│  │  - chora:assemble_artifact          │ │
│  │  - chora:generate_content           │ │
│  │  - coda:list_docs                   │ │
│  │  - coda:create_rows                 │ │
│  │  - gateway_status                   │ │
│  │  - get_events                       │ │
│  └─────────────────────────────────────┘ │
└───────────┬───────────────┬───────────────┘
            │               │
            │ Routes by     │
            │ namespace     │
            ▼               ▼
    ┌──────────────┐  ┌──────────────┐
    │ chora-compose│  │   coda-mcp   │
    │  (Backend 1) │  │  (Backend 2) │
    └──────────────┘  └──────────────┘
```

### Key Decisions

**Decision 1: Tool Namespacing**
- **Rationale:** Prevents name collisions between backends. If two backends both have a `list` tool, namespacing makes them `chora:list` vs `coda:list`.
- **Trade-offs:** Tool names become slightly longer, but clarity and collision prevention are worth it.
- **Implementation:** Gateway parses `namespace:tool_name` format and routes accordingly.

**Decision 2: Subprocess-Based Backends**
- **Rationale:** Each backend runs as a separate subprocess for isolation. If Coda MCP crashes, Chora Composer keeps working.
- **Trade-offs:** Slightly higher memory usage (~50MB per backend), but robust failure isolation.
- **Alternatives:** In-process backends (faster, but failures cascade) or remote HTTP backends (future enhancement).

**Decision 3: STDIO Transport**
- **Rationale:** MCP standard transport, works with all clients, simple and battle-tested.
- **Trade-offs:** Single-connection (not multi-tenant), but suitable for local desktop use.
- **Future:** HTTP+SSE transport for multi-user deployments.

**Decision 4: Chora Composer as Exclusive Artifact Mechanism**
- **Rationale:** Centralizing artifact creation through one backend ensures consistency and enables comprehensive telemetry.
- **Impact:** All document/artifact generation must go through `chora:*` tools.

---

## How It Works

### Component Breakdown

**1. Gateway Server** ([gateway.py](../../src/mcp_n8n/gateway.py))

The main entry point that AI clients connect to:

- **Responsibilities:**
  - Accept MCP connections via STDIO
  - Initialize and manage backend lifecycle
  - Expose gateway tools (`gateway_status`, `get_events`)
  - Emit telemetry events for all operations

- **Key Behaviors:**
  - Loads configuration from environment variables
  - Spawns backend subprocesses on startup
  - Handles graceful shutdown (Ctrl+C)
  - Routes tool calls to Backend Registry

**2. Backend Registry** ([backends/registry.py](../../src/mcp_n8n/backends/registry.py))

The routing engine that manages all backends:

- **Responsibilities:**
  - Register backends with unique namespaces
  - Route tool calls to correct backend
  - Aggregate tools from all running backends
  - Track backend health/status

- **Key Behaviors:**
  - Maintains two maps: `namespace → backend` and `name → backend`
  - Parses tool names like `chora:assemble_artifact` to extract namespace
  - Returns aggregated tool list for `tools/list` requests
  - Validates namespace uniqueness on registration

**3. Backend Implementations** ([backends/base.py](../../src/mcp_n8n/backends/base.py))

Abstract base class + concrete implementations:

- **Responsibilities:**
  - Spawn and manage subprocess lifecycle
  - Communicate via JSON-RPC 2.0 over STDIO
  - Discover tools/resources from backend
  - Handle errors and retry logic

- **Key Behaviors:**
  - `StdioSubprocessBackend` spawns command + args as subprocess
  - Sends initialization handshake to backend
  - Discovers capabilities (tools, resources, prompts)
  - Forwards tool calls as JSON-RPC messages

**4. Event System** ([memory/event_log.py](../../src/mcp_n8n/memory/event_log.py))

Centralized telemetry and observability:

- **Responsibilities:**
  - Persist all gateway/backend events to disk
  - Enable querying by trace, time, type, status
  - Monitor external event sources (chora-compose)
  - Provide debugging and analytics data

- **Key Behaviors:**
  - Stores events in `.chora/memory/events/<date>.jsonl`
  - `EventWatcher` monitors `var/telemetry/events.jsonl` for backend events
  - `TraceContext` generates correlation IDs for request tracking
  - Supports CLI queries (`chora-memory query`)

### Interaction Patterns

**Pattern 1: Tool Call Routing**

1. **Client requests tool:** Claude Desktop calls `chora:assemble_artifact`
2. **Gateway receives request:** MCP server accepts JSON-RPC call
3. **Registry parses namespace:** Extracts `chora` from `chora:assemble_artifact`
4. **Registry looks up backend:** Finds `chora-composer` backend via namespace map
5. **Gateway strips namespace:** Converts to `assemble_artifact` (backend doesn't need prefix)
6. **Backend forwards call:** Sends JSON-RPC to subprocess over STDIO
7. **Subprocess executes:** chora-compose runs the tool
8. **Result bubbles up:** subprocess → backend → gateway → client

**Pattern 2: Tool Discovery**

1. **Client requests tool list:** Claude Desktop calls `tools/list`
2. **Gateway queries registry:** Registry asks all running backends for their tools
3. **Backends report tools:** Each backend returns its tool catalog
4. **Registry namespaces tools:** Prefixes each tool with backend namespace
5. **Gateway aggregates:** Combines all namespaced tools into single list
6. **Client receives catalog:** Sees `chora:assemble_artifact`, `coda:list_docs`, etc.

**Pattern 3: Event Monitoring**

1. **Backend emits event:** chora-compose appends to `var/telemetry/events.jsonl`
2. **EventWatcher detects change:** File watcher triggers on modification
3. **EventWatcher reads new lines:** Parses JSONL event data
4. **EventLog stores event:** Writes to `.chora/memory/events/<date>.jsonl`
5. **Optional webhook:** POST event to n8n (if configured)
6. **Available for queries:** Event queryable via `get_events` tool or CLI

### Example Scenario: Assemble an Artifact

**User action:** "Create a design document from our architecture notes"

**Claude Desktop workflow:**

1. Claude calls `chora:assemble_artifact` with config and output path
2. Gateway emits `tool.call_received` event (telemetry)
3. Registry parses namespace → routes to Chora Composer backend
4. Backend sends JSON-RPC to chora-compose subprocess:
   ```json
   {
     "jsonrpc": "2.0",
     "method": "tools/call",
     "params": {
       "name": "assemble_artifact",
       "arguments": {
         "artifact_config_id": "design-doc",
         "output_path": "/output/design.md"
       }
     }
   }
   ```
5. chora-compose generates document, returns result
6. Backend emits `tool.call_completed` event
7. Gateway forwards result to Claude Desktop
8. Claude receives artifact path and success status

**Telemetry captured:**
- `tool.call_received` (gateway)
- `tool.call_completed` (backend)
- `content.generated` (chora-compose internal event)
- All events share same `trace_id` for correlation

---

## Benefits

**Advantages of this architecture:**

- ✅ **Simplified client configuration:** One MCP server entry in Claude Desktop config instead of 3-4
- ✅ **No tool name collisions:** Namespacing (`chora:`, `coda:`) prevents conflicts
- ✅ **Centralized credentials:** All API keys in one `.env` file, injected into backends
- ✅ **Unified telemetry:** Single event log for debugging across all backends
- ✅ **Backend isolation:** Subprocess failures don't crash gateway or other backends
- ✅ **Easy extensibility:** Add new backends without modifying existing code
- ✅ **Performance:** Routing overhead < 10ms, negligible compared to tool execution time

**When to use:**

- You need multiple MCP servers (artifact generation + data access + custom tools)
- You want centralized monitoring and debugging
- You need to coordinate operations across backends
- You want to simplify client configuration

---

## Limitations

**Constraints and trade-offs:**

- ❌ **Single-tenant only:** Current STDIO transport supports one client at a time
- ⚠️ **Subprocess overhead:** Each backend uses ~50MB memory + startup time (~1-2s)
- ❌ **No dynamic backend loading:** Backends configured at startup (restart required to change)
- ℹ️ **Namespace required:** Tool names must follow `namespace:tool_name` convention

**When NOT to use:**

- Single backend is sufficient for your use case
- Multi-tenant deployment required (use HTTP+SSE gateway instead)
- Backends need to share state (they're isolated by design)
- Sub-millisecond latency critical (subprocess communication adds ~5ms)

---

## Comparison to Alternatives

### vs. Direct Multi-Server Connection

| Aspect | Gateway (mcp-n8n) | Direct Connection |
|--------|-------------------|-------------------|
| Config complexity | ✅ One server entry | ❌ N server entries |
| Tool namespacing | ✅ Automatic | ⚠️ Manual (if supported) |
| Credential management | ✅ Centralized | ❌ Scattered |
| Telemetry | ✅ Unified | ❌ Per-server |
| Failure isolation | ✅ Gateway remains up | ⚠️ Client handles |
| Overhead | ~10ms routing | None |

**When to use Direct Connection instead:**
- Only using one MCP server
- Absolutely minimal latency required
- Client-side telemetry sufficient

### vs. Custom Protocol Aggregator

| Aspect | MCP Gateway | Custom Protocol |
|--------|-------------|-----------------|
| Client compatibility | ✅ Any MCP client | ❌ Custom client needed |
| Development effort | ✅ Low (use FastMCP) | ❌ High (build from scratch) |
| MCP compliance | ✅ Yes | ❌ No |
| Flexibility | ⚠️ MCP constraints | ✅ Full control |

**When to use Custom Protocol instead:**
- Need features beyond MCP spec
- Willing to build custom client
- MCP constraints too limiting

---

## Related Patterns

**Complementary Patterns:**

- **Pattern P4 (OAuth Integration):** Add user-scoped credentials for multi-tenant gateway
- **Pattern P2 (Agent Loop):** Use gateway as tool provider for autonomous agent workflows
- **Workflow Orchestration:** Build multi-step workflows that coordinate tools across backends

**Alternative Patterns:**

- **Pattern P1 (Simple Tool Provider):** Single backend server (no aggregation needed)
- **Pattern P3 (Data Pipeline):** Streaming data transformations (different problem space)

---

## Real-World Examples

### Example 1: Daily Engineering Report

**Context:** Generate a daily report combining git commits + telemetry events

**Application:**
1. Workflow calls `get_events` (gateway tool) to fetch telemetry
2. Workflow queries git log locally (no MCP tool needed)
3. Workflow calls `chora:generate_content` to create formatted report
4. All operations tracked under single `trace_id`

**Outcome:** Report generated from multiple data sources with full traceability

### Example 2: Documentation Pipeline

**Context:** Extract code examples → generate docs → store in Coda

**Application:**
1. Custom backend extracts code snippets (hypothetical)
2. `chora:assemble_artifact` generates formatted docs
3. `coda:create_rows` stores metadata in tracking table
4. Gateway telemetry logs entire pipeline

**Outcome:** Multi-backend coordination with centralized observability

### Example 3: Event-Driven Workflow Routing

**Context:** Failed tool call → generate error report → notify team

**Application:**
1. Backend emits `tool.call_failed` event
2. EventWatcher captures event
3. EventWorkflowRouter triggers error-alert workflow
4. Workflow calls `chora:generate_content` to create incident report
5. Result posted to Slack (via hypothetical notification backend)

**Outcome:** Automated incident response spanning multiple systems

---

## Further Reading

**Internal Documentation:**
- [Tutorial: Getting Started](../tutorials/getting-started.md) - Install and configure gateway
- [How-To: Configure Backends](../how-to/configure-backends.md) - Backend setup
- [How-To: Build Custom Workflow](../how-to/build-custom-workflow.md) - Multi-backend workflows
- [Reference: Tools](../reference/tools.md) - Complete tool catalog
- [Explanation: Memory System](memory-system.md) - Event storage and querying

**External Resources:**
- [MCP Specification](https://modelcontextprotocol.io/) - Protocol details
- [FastMCP Documentation](https://github.com/anthropics/fastmcp) - Python SDK
- [MCP Server Patterns Catalog](https://modelcontextprotocol.io/patterns) - Pattern P5 reference

---

## History

**Evolution of the architecture:**

- **v0.1.0 (Sprint 1):** Initial gateway with chora-compose backend only
  - Single backend, basic routing
  - STDIO transport established

- **v0.2.0 (Sprint 2):** Added Backend Registry pattern
  - Multi-backend support
  - Namespace-based routing
  - Coda MCP integration

- **v0.3.0 (Sprint 3):** Event monitoring system
  - EventLog persistence
  - EventWatcher for external events
  - TraceContext correlation

- **v0.4.0 (Sprint 4):** Memory system enhancements
  - Knowledge graph integration
  - Agent profile tracking
  - Enhanced event querying

- **v0.5.0 (Sprint 5):** Workflow orchestration
  - EventWorkflowRouter for event-driven automation
  - YAML-based workflow configuration
  - Hot-reload support

---

**Source:** [dev-docs/ARCHITECTURE.md](../../dev-docs/ARCHITECTURE.md), [src/mcp_n8n/gateway.py](../../src/mcp_n8n/gateway.py)
**Last Updated:** 2025-10-21
