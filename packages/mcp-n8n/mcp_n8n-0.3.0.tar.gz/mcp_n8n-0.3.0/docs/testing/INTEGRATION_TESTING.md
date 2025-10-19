# Integration Testing Framework

**Version:** 1.0
**Date:** 2025-10-17
**Status:** Active
**Purpose:** Document integration testing strategy and mock backend infrastructure

---

## Overview

The mcp-n8n integration testing framework validates gateway architecture, subprocess communication, and backend integration patterns. This document describes:

1. Mock Backend Infrastructure
2. Integration Test Organization
3. Testing Patterns
4. Test Coverage
5. Running Tests

---

## Mock Backend Infrastructure

### Purpose

The mock backend (`mock_mcp_server.py`) simulates an MCP server subprocess (like chora-composer or coda-mcp) to enable testing gateway architecture without requiring actual backend implementations.

### Mock Server Implementation

**Location:** [`tests/integration/mock_mcp_server.py`](../../tests/integration/mock_mcp_server.py)

**Capabilities:**
- Implements MCP JSON-RPC protocol over STDIO
- Responds to MCP protocol methods:
  - `initialize` - Protocol handshake
  - `tools/list` - List available tools
  - `tools/call` - Execute tool
- Provides mock tools:
  - `mock_generate` - Simulates content generation
  - `mock_assemble` - Simulates artifact assembly
- Error handling for unknown methods/tools

**Protocol Compliance:**
- MCP Protocol Version: `2024-11-05`
- JSON-RPC 2.0 compliant
- STDIO transport (stdin/stdout)

### Example: Mock Server Interaction

```bash
# Start mock server
$ python tests/integration/mock_mcp_server.py

# Send initialize request
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}

# Receive response
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "serverInfo": {"name": "mock-mcp-server", "version": "1.0.0"},
    "capabilities": {"tools": {}, "resources": {}, "prompts": {}}
  }
}
```

### Mock Server Architecture

```
┌────────────────────────────────────┐
│  StdioSubprocessBackend (Gateway)  │
└───────────┬────────────────────────┘
            │ subprocess.Popen
            │ stdin/stdout/stderr
            ▼
┌────────────────────────────────────┐
│  mock_mcp_server.py                │
│  ├─ JSON-RPC parser                │
│  ├─ MCP protocol handler           │
│  └─ Mock tool implementations      │
└────────────────────────────────────┘
```

---

## Integration Test Organization

### Test Structure

**Location:** [`tests/integration/test_gateway_subprocess.py`](../../tests/integration/test_gateway_subprocess.py)

**Test Classes:**

1. **`TestSubprocessCommunication`** - Subprocess lifecycle and communication
2. **`TestNamespaceRouting`** - Tool routing and namespace resolution
3. **`TestErrorHandling`** - Error scenarios and graceful failures

### Test Coverage

**Subprocess Communication (6 tests):**
- ✅ Mock server runs standalone
- ✅ Backend can start mock server
- ✅ Backend registry manages mock backend
- ✅ Error handling for nonexistent commands
- ⏭️ Timeout handling (skipped - not implemented)
- ✅ Multiple backends run concurrently

**Namespace Routing (3 tests):**
- ✅ Route tool call to correct backend
- ✅ Handle unknown namespace
- ✅ Handle missing namespace prefix

**Error Handling (2 tests):**
- ⏭️ Backend crash recovery (skipped - not implemented)
- ✅ Graceful shutdown of running backends

**Test Results:**
```bash
$ pytest tests/integration/test_gateway_subprocess.py -v
Results: 9 passed, 2 skipped in 0.15s
```

---

## Testing Patterns

### Pattern 1: Subprocess Lifecycle Testing

**Purpose:** Validate backend can start, run, and stop cleanly

**Example:**
```python
@pytest.mark.asyncio
async def test_backend_can_start_mock_server(self) -> None:
    """Test that StdioSubprocessBackend can start mock server."""
    config = BackendConfig(
        name="mock-backend",
        type=BackendType.STDIO_SUBPROCESS,
        command=sys.executable,
        args=[str(MOCK_SERVER)],
        enabled=True,
        namespace="mock",
        capabilities=["testing"],
        timeout=5,
    )

    backend = StdioSubprocessBackend(config)

    try:
        # Start backend
        await backend.start()

        # Check status
        assert backend.status == BackendStatus.RUNNING
        assert backend._process is not None
        assert backend._process.poll() is None  # Still running

    finally:
        # Stop backend
        await backend.stop()
        assert backend.status == BackendStatus.STOPPED
```

**Validates:**
- Backend starts successfully
- Process is spawned
- Status transitions (STARTING → RUNNING → STOPPED)

### Pattern 2: Namespace Routing Testing

**Purpose:** Validate tool calls are routed to correct backend

**Example:**
```python
@pytest.mark.asyncio
async def test_route_tool_call_success(self) -> None:
    """Test routing tool call to correct backend."""
    registry = BackendRegistry()

    config = BackendConfig(
        name="mock-backend",
        type=BackendType.STDIO_SUBPROCESS,
        command=sys.executable,
        args=[str(MOCK_SERVER)],
        enabled=True,
        namespace="mock",
        capabilities=["testing"],
        timeout=5,
    )

    try:
        registry.register(config)
        await registry.start_all()

        # Route namespaced tool call
        result = registry.route_tool_call("mock:generate_content")
        assert result is not None

        backend, tool_name = result
        assert backend.name == "mock-backend"
        assert tool_name == "generate_content"  # Namespace stripped

    finally:
        await registry.stop_all()
```

**Validates:**
- Namespace routing works (`mock:tool` → backend + `tool`)
- Unknown namespaces return None
- Missing namespace prefix returns None

### Pattern 3: Error Handling Testing

**Purpose:** Validate graceful failure for error conditions

**Example:**
```python
@pytest.mark.asyncio
async def test_subprocess_error_handling(self) -> None:
    """Test error handling when subprocess fails to start."""
    config = BackendConfig(
        name="bad-backend",
        type=BackendType.STDIO_SUBPROCESS,
        command="nonexistent_command_12345",  # Command doesn't exist
        args=[],
        enabled=True,
        namespace="bad",
        capabilities=[],
        timeout=5,
    )

    backend = StdioSubprocessBackend(config)

    # Starting should raise BackendError
    from mcp_n8n.backends.base import BackendError

    with pytest.raises(BackendError):
        await backend.start()

    # Check status is failed
    assert backend.status == BackendStatus.FAILED
    assert backend._process is None
```

**Validates:**
- Backend raises `BackendError` for nonexistent commands
- Status transitions to `FAILED`
- Process remains `None` (not started)

### Pattern 4: Concurrent Backend Testing

**Purpose:** Validate multiple backends run independently

**Example:**
```python
@pytest.mark.asyncio
async def test_multiple_backends_concurrent(self) -> None:
    """Test multiple backends can run concurrently."""
    registry = BackendRegistry()

    # Create two mock backends with different namespaces
    config1 = BackendConfig(
        name="mock-1",
        type=BackendType.STDIO_SUBPROCESS,
        command=sys.executable,
        args=[str(MOCK_SERVER)],
        enabled=True,
        namespace="mock1",
        capabilities=["testing"],
        timeout=5,
    )

    config2 = BackendConfig(
        name="mock-2",
        type=BackendType.STDIO_SUBPROCESS,
        command=sys.executable,
        args=[str(MOCK_SERVER)],
        enabled=True,
        namespace="mock2",
        capabilities=["testing"],
        timeout=5,
    )

    try:
        # Register both
        registry.register(config1)
        registry.register(config2)

        # Start all
        await registry.start_all()

        # Check both running
        status = registry.get_status()
        assert status["mock-1"]["status"] == "running"
        assert status["mock-2"]["status"] == "running"

        # Verify namespace isolation
        backend1 = registry.get_backend_by_namespace("mock1")
        backend2 = registry.get_backend_by_namespace("mock2")
        assert backend1 is not None
        assert backend2 is not None
        assert backend1.name != backend2.name

    finally:
        await registry.stop_all()
```

**Validates:**
- Multiple backends start independently
- Namespace isolation (mock1, mock2)
- Registry manages multiple backends
- Clean shutdown of all backends

---

## Running Tests

### Run All Integration Tests

```bash
# From repository root
pytest tests/integration/ -v

# Expected output:
# tests/integration/test_gateway_subprocess.py::TestSubprocessCommunication::test_mock_server_runs_standalone PASSED
# tests/integration/test_gateway_subprocess.py::TestSubprocessCommunication::test_backend_can_start_mock_server PASSED
# tests/integration/test_gateway_subprocess.py::TestSubprocessCommunication::test_backend_registry_with_mock PASSED
# tests/integration/test_gateway_subprocess.py::TestSubprocessCommunication::test_subprocess_error_handling PASSED
# tests/integration/test_gateway_subprocess.py::TestSubprocessCommunication::test_subprocess_timeout_handling SKIPPED
# tests/integration/test_gateway_subprocess.py::TestSubprocessCommunication::test_multiple_backends_concurrent PASSED
# tests/integration/test_gateway_subprocess.py::TestNamespaceRouting::test_route_tool_call_success PASSED
# tests/integration/test_gateway_subprocess.py::TestNamespaceRouting::test_route_tool_call_unknown_namespace PASSED
# tests/integration/test_gateway_subprocess.py::TestNamespaceRouting::test_route_tool_call_no_namespace PASSED
# tests/integration/test_gateway_subprocess.py::TestErrorHandling::test_backend_crash_recovery SKIPPED
# tests/integration/test_gateway_subprocess.py::TestErrorHandling::test_graceful_shutdown PASSED
#
# 9 passed, 2 skipped
```

### Run Specific Test Class

```bash
# Test subprocess communication only
pytest tests/integration/test_gateway_subprocess.py::TestSubprocessCommunication -v

# Test namespace routing only
pytest tests/integration/test_gateway_subprocess.py::TestNamespaceRouting -v

# Test error handling only
pytest tests/integration/test_gateway_subprocess.py::TestErrorHandling -v
```

### Run Single Test

```bash
# Test specific scenario
pytest tests/integration/test_gateway_subprocess.py::TestSubprocessCommunication::test_backend_can_start_mock_server -v
```

### Run with Coverage

```bash
# Generate coverage report
pytest tests/integration/ --cov=src/mcp_n8n --cov-report=term-missing

# Expected coverage:
# src/mcp_n8n/backends/base.py - StdioSubprocessBackend
# src/mcp_n8n/backends/registry.py - BackendRegistry
# src/mcp_n8n/config.py - BackendConfig
```

---

## Known Limitations

### Skipped Tests

**1. Startup Timeout Handling** (`test_subprocess_timeout_handling`)
- **Reason:** Backend doesn't implement timeout logic for slow subprocess initialization
- **Status:** Skipped with `@pytest.mark.skip`
- **Future Work:** Implement timeout in `StdioSubprocessBackend.start()`

**2. Crash Detection** (`test_backend_crash_recovery`)
- **Reason:** Backend doesn't monitor process health after startup
- **Status:** Skipped with `@pytest.mark.skip`
- **Future Work:** Implement process monitoring in `StdioSubprocessBackend`

### Mock vs Real Backend

**Mock Backend Limitations:**
- Does not implement actual MCP server capabilities (resources, prompts)
- Tool execution returns mock responses, not real results
- No persistence or state management
- No error injection for testing edge cases

**Real Backend Testing:**
- Requires actual chora-composer or coda-mcp installation
- See [`SPRINT_1_VALIDATION.md`](../SPRINT_1_VALIDATION.md) for integration blocker details
- Planned for Sprint 2 after chora-composer setup

---

## Future Enhancements

### Sprint 2: Real Backend Integration

1. **Chora-Composer Integration**
   - Set up chora-composer as subprocess
   - Test actual tool execution (`chora:generate_content`, `chora:assemble_artifact`)
   - Validate event emission and correlation

2. **Coda MCP Integration**
   - Configure coda-mcp backend
   - Test data operations (`coda:list_docs`, `coda:list_tables`)

### Sprint 3: Advanced Testing

1. **Performance Testing**
   - Backend startup latency benchmarks
   - Tool call overhead measurements
   - Concurrent backend load testing

2. **Reliability Testing**
   - Backend crash recovery
   - Startup timeout handling
   - Connection retry logic

3. **End-to-End Workflows**
   - Hello World workflow (generate + assemble)
   - Multi-backend coordination
   - Event correlation validation

---

## References

- [MCP Protocol Specification](https://modelcontextprotocol.io/specification/)
- [Sprint 1 Validation Report](../SPRINT_1_VALIDATION.md)
- [Event Schema Specification](../process/specs/event-schema.md)
- [Backend Architecture](../../ARCHITECTURE.md)

---

**Status:** ✅ Complete
**Test Coverage:** 9/11 passing (2 skipped - future work)
**Updated:** 2025-10-17
