# Development Guide

This guide provides deep technical information for developers working on mcp-n8n internals.

**Prerequisites:** Read [CONTRIBUTING.md](../CONTRIBUTING.md) first for general contribution guidelines.

---

## Table of Contents

- [Architecture Deep Dive](#architecture-deep-dive)
- [Code Organization](#code-organization)
- [Backend Integration](#backend-integration)
- [Testing Strategy](#testing-strategy)
- [Debugging Tips](#debugging-tips)
- [Performance Profiling](#performance-profiling)
- [Common Workflows](#common-workflows)

---

## Architecture Deep Dive

### Pattern P5: Gateway & Aggregator

mcp-n8n implements the **Meta-MCP Server** pattern (P5) from the MCP Server Patterns Catalog.

**Key characteristics:**
- **Single entry point** - AI clients connect to one MCP server
- **Backend aggregation** - Routes requests to multiple specialized backends
- **Tool namespacing** - Prevents name collisions (`chora:*`, `coda:*`)
- **Subprocess isolation** - Each backend runs in separate process

**Request Flow:**

```
1. AI Client sends tool call: chora:generate_content
   ↓
2. Gateway receives JSON-RPC request via STDIO
   ↓
3. ToolRouter parses namespace: "chora"
   ↓
4. BackendRegistry finds: ChoraComposerBackend
   ↓
5. Backend executes tool in subprocess
   ↓
6. Result returned to AI Client
```

### Component Overview

```
src/mcp_n8n/
├── gateway.py              # Main FastMCP server
├── config.py               # Configuration management
├── logging_config.py       # Structured logging
└── backends/
    ├── base.py             # Abstract backend interface
    ├── registry.py         # Backend lifecycle & routing
    ├── chora_composer.py   # Chora Composer backend
    └── coda_mcp.py         # Coda MCP backend
```

**Key classes:**

- **`FastMCP` (gateway.py)** - Main MCP server instance
- **`BackendRegistry` (registry.py)** - Manages backend lifecycle
- **`BaseBackend` (base.py)** - Abstract backend interface
- **`Config` (config.py)** - Pydantic configuration model

---

## Code Organization

### Module Structure

**`src/mcp_n8n/gateway.py`**
- Main entry point
- FastMCP server setup
- Tool routing logic
- Request/response handling

**`src/mcp_n8n/config.py`**
- `Config` - Main configuration model
- `BackendConfig` - Per-backend settings
- Environment variable loading
- Validation logic

**`src/mcp_n8n/logging_config.py`**
- `StructuredFormatter` - JSON log formatting
- `TraceLogger` - Trace context adapter
- Log setup and configuration

**`src/mcp_n8n/backends/base.py`**
- `BaseBackend` - Abstract base class
- Common backend interface
- Lifecycle methods (start, stop, health_check)

**`src/mcp_n8n/backends/registry.py`**
- `BackendRegistry` - Backend manager
- Add/remove/get backends
- Tool routing by namespace
- Lifecycle management

**`src/mcp_n8n/backends/chora_composer.py`**
- `ChoraComposerBackend` - Chora integration
- Subprocess management
- Tool namespace: `chora:*`

**`src/mcp_n8n/backends/coda_mcp.py`**
- `CodaMCPBackend` - Coda integration
- Subprocess management
- Tool namespace: `coda:*`

### Test Organization

```
tests/
├── conftest.py                  # Shared fixtures
├── test_config.py               # Configuration tests
├── test_registry.py             # Registry tests
└── smoke/
    ├── conftest.py              # Smoke test fixtures
    ├── test_gateway_startup.py  # Gateway initialization
    ├── test_chora_routing.py    # Chora tool routing
    ├── test_coda_routing.py     # Coda tool routing
    └── test_namespace_isolation.py  # Namespace validation
```

**Test categories:**

1. **Unit tests** - Test individual functions/classes
2. **Smoke tests** - Fast validation with mocks (<30 sec)
3. **Integration tests** - End-to-end with real backends (future)

---

## Backend Integration

### Adding a New Backend

Follow these steps to integrate a new MCP backend:

#### Step 1: Create Backend Class

Create `src/mcp_n8n/backends/your_backend.py`:

```python
from mcp_n8n.backends.base import BaseBackend
from typing import Any
import subprocess
import logging

logger = logging.getLogger(__name__)

class YourBackend(BaseBackend):
    """Backend for Your MCP Server."""

    def __init__(
        self,
        name: str,
        namespace: str,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ):
        super().__init__(name=name, namespace=namespace)
        self.command = command
        self.args = args or []
        self.env = env or {}
        self.process: subprocess.Popen | None = None

    async def start(self) -> None:
        """Start the backend subprocess."""
        logger.info(f"Starting backend: {self.name}")
        self.process = subprocess.Popen(
            [self.command, *self.args],
            env={**os.environ, **self.env},
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    async def stop(self) -> None:
        """Stop the backend subprocess."""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a tool call."""
        # Strip namespace
        local_name = tool_name.split(":", 1)[1]

        # Send JSON-RPC request to subprocess
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": local_name,
                "arguments": arguments,
            },
        }

        # Communicate with subprocess
        # (Implement your protocol here)

        return result

    async def list_tools(self) -> list[dict[str, Any]]:
        """List available tools."""
        # Query backend for tools
        # Add namespace prefix to each tool name
        tools = []  # Get from backend
        return [
            {**tool, "name": f"{self.namespace}:{tool['name']}"}
            for tool in tools
        ]

    async def health_check(self) -> bool:
        """Check if backend is healthy."""
        if not self.process or self.process.poll() is not None:
            return False
        return True
```

#### Step 2: Register Backend

In `src/mcp_n8n/gateway.py`, add:

```python
from mcp_n8n.backends.your_backend import YourBackend

# In setup_backends()
your_backend = YourBackend(
    name="your-backend",
    namespace="your",
    command="/path/to/your-mcp-server",
    env={"API_KEY": os.getenv("YOUR_API_KEY")},
)

registry.add(your_backend)
await your_backend.start()
```

#### Step 3: Add Configuration

In `src/mcp_n8n/config.py`, add:

```python
class Config(BaseSettings):
    # ... existing fields ...

    your_backend_path: str = Field(
        default="/path/to/your-backend",
        description="Path to Your MCP backend",
    )
    your_api_key: str = Field(
        default="",
        description="API key for Your backend",
    )
```

#### Step 4: Add Tests

Create `tests/smoke/test_your_routing.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_your_backend():
    backend = MagicMock()
    backend.name = "your-backend"
    backend.namespace = "your"
    backend.call_tool = AsyncMock(return_value={"result": "success"})
    backend.list_tools = AsyncMock(return_value=[
        {"name": "your:tool1", "description": "Tool 1"},
    ])
    return backend

async def test_your_tool_routing(mock_your_backend):
    """Test routing to Your backend."""
    result = await mock_your_backend.call_tool(
        "your:tool1",
        {"arg": "value"},
    )
    assert result["result"] == "success"
```

#### Step 5: Update Documentation

- Add backend to README.md
- Document tools in ARCHITECTURE.md
- Add configuration to .env.example

---

## Testing Strategy

### Unit Tests

Test individual components in isolation:

```python
def test_config_validation():
    """Test configuration model validation."""
    config = Config(
        log_level="INFO",
        anthropic_api_key="test-key",
    )
    assert config.log_level == "INFO"

def test_config_invalid_log_level():
    """Test invalid log level raises error."""
    with pytest.raises(ValueError):
        Config(log_level="INVALID")
```

### Smoke Tests

Fast validation with mocks:

```python
async def test_backend_registry_routing(mock_backend):
    """Smoke test: backend registry routes correctly."""
    registry = BackendRegistry()
    registry.add(mock_backend)

    backend = registry.get_backend_for_tool("test:tool1")
    assert backend == mock_backend
```

**Smoke test guidelines:**
- Use mocks, no real backends
- Test critical paths only
- Run in <30 seconds total
- Focus on routing, not functionality

### Integration Tests (Future)

End-to-end tests with real backends:

```python
@pytest.mark.integration
async def test_chora_generate_content_e2e():
    """Integration: Generate content via Chora Composer."""
    # Requires real Chora Composer backend
    result = await gateway.call_tool(
        "chora:generate_content",
        {"template": "test", "data": {}},
    )
    assert "content" in result
```

**Note:** Integration tests not yet implemented (Phase 5).

---

## Debugging Tips

### VSCode Debugging

1. **Set breakpoints** in source code
2. **Run debug configuration** (F5):
   - "Launch Gateway" - Normal mode
   - "Launch Gateway (Debug Mode)" - Verbose logging
   - "Run Smoke Tests" - Debug tests

3. **Common breakpoints:**
   - `src/mcp_n8n/gateway.py:main()` - Entry point
   - `src/mcp_n8n/backends/registry.py:get_backend_for_tool()` - Routing
   - Backend `call_tool()` methods - Tool execution

### Logging

Use structured logging for debugging:

```python
logger.debug("Tool call received", extra={
    "tool_name": tool_name,
    "arguments": arguments,
    "trace_id": trace_id,
})
```

**Log levels:**
- `DEBUG` - Detailed execution trace
- `INFO` - Normal operations
- `WARNING` - Recoverable issues
- `ERROR` - Failures requiring attention

**Set log level:**

```bash
export MCP_N8N_LOG_LEVEL=DEBUG
mcp-n8n
```

### Trace Context

Use trace IDs to correlate related events:

```bash
export CHORA_TRACE_ID=$(uuidgen)
mcp-n8n
```

Then grep logs:

```bash
grep "$CHORA_TRACE_ID" logs/mcp-n8n.log
```

### Common Debug Scenarios

**Problem: Tool not found**

```python
# Add breakpoint here:
def get_backend_for_tool(self, tool_name: str) -> BaseBackend | None:
    # Check:
    # - tool_name format (has namespace?)
    # - backends registered?
    # - namespace matches?
```

**Problem: Backend not responding**

```python
# Add breakpoint here:
async def call_tool(self, tool_name: str, arguments: dict):
    # Check:
    # - process running? (self.process.poll())
    # - stdin/stdout pipes working?
    # - request format correct?
```

---

## Performance Profiling

### Profiling Tool Calls

Use cProfile for performance analysis:

```bash
python -m cProfile -o profile.stats -m mcp_n8n.gateway
```

Analyze results:

```python
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative')
p.print_stats(20)  # Top 20 functions
```

### Async Profiling

For async code, use `asyncio` debugging:

```python
import asyncio
asyncio.get_event_loop().set_debug(True)
```

### Memory Profiling

Use `tracemalloc`:

```python
import tracemalloc
tracemalloc.start()

# ... run code ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

---

## Common Workflows

### Adding a Feature

1. Create feature branch: `git checkout -b feature/xyz`
2. Write tests first (TDD): `tests/test_xyz.py`
3. Implement feature: `src/mcp_n8n/xyz.py`
4. Run smoke tests: `just smoke`
5. Run full tests: `just test`
6. Update CHANGELOG.md
7. Create PR

### Fixing a Bug

1. Reproduce bug: Write failing test
2. Create bugfix branch: `git checkout -b bugfix/xyz`
3. Fix bug: Update source code
4. Verify test passes: `pytest tests/test_xyz.py -v`
5. Add regression test if needed
6. Run all tests: `just test`
7. Update CHANGELOG.md
8. Create PR

### Refactoring Code

1. Ensure 100% test coverage for code to refactor
2. Create refactor branch: `git checkout -b refactor/xyz`
3. Run tests before: `just test` (should pass)
4. Refactor code
5. Run tests after: `just test` (should still pass)
6. Verify no behavior change
7. Update documentation if needed
8. Create PR

### Updating Dependencies

1. Check for updates: `pip list --outdated`
2. Update in `pyproject.toml`
3. Test locally: `pip install -e ".[dev]"`
4. Run all tests: `just test`
5. Update `CHANGELOG.md`
6. Create PR

**Automated:** Dependabot creates PRs weekly.

### Releasing a Version

See [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) for full process.

**Quick version (NEW - Automated):**

```bash
# Single-command automated release
just release patch      # or: minor, major

# Monitor GitHub Actions (~5 min)
# Everything else happens automatically!
```

**Manual review version:**

```bash
# Prepare but don't push (for review)
just release-draft patch

# Review changes
git show HEAD

# Push when ready
git push origin main && git push origin vX.Y.Z
```

**Legacy manual workflow (rarely needed):**

```bash
# Prepare release
just prepare-release patch

# Build
just build

# Test on TestPyPI
just publish-test

# Publish to production
just publish-prod
```

---

## Best Practices

### Code Quality

- **Type hints** on all public functions
- **Docstrings** on all public APIs
- **Error handling** with specific exceptions
- **Logging** at appropriate levels
- **Testing** with ≥85% coverage

### Git Workflow

- **Small commits** with clear messages
- **Feature branches** for all changes
- **Rebase before merge** to keep history clean
- **Squash commits** if requested

### Documentation

- **Update docs** with code changes
- **Add examples** for new features
- **Explain "why"** not just "what"
- **Keep README current**

### Performance

- **Avoid blocking operations** in async code
- **Use connection pooling** for backends
- **Cache when appropriate**
- **Profile before optimizing**

---

## Resources

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - System architecture
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Problem solving
- **[MCP Specification](https://modelcontextprotocol.io)** - MCP protocol
- **[FastMCP Docs](https://github.com/jlowin/fastmcp)** - FastMCP library

---

**Last updated:** 2025-10-17
