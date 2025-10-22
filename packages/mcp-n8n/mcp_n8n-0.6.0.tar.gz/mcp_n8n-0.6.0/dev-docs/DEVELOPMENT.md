# Development Guide

This guide provides deep technical information for developers working on mcp-n8n internals.

**Prerequisites:** Read [CONTRIBUTING.md](../CONTRIBUTING.md) first for general contribution guidelines.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Justfile Command Reference](#justfile-command-reference)
- [Architecture Deep Dive](#architecture-deep-dive)
- [Code Organization](#code-organization)
- [Backend Integration](#backend-integration)
- [Testing Strategy](#testing-strategy)
- [Debugging Tips](#debugging-tips)
- [Performance Profiling](#performance-profiling)
- [Common Workflows](#common-workflows)

---

## Quick Start

```bash
# Install just (task runner)
# macOS: brew install just
# Linux: cargo install just

# Show all available commands
just

# Full setup (install deps + hooks)
just setup

# Verify everything works
just verify
```

---

## Justfile Command Reference

**[justfile](../justfile)** is our task automation tool. Install with: `brew install just` or see https://github.com/casey/just

### Setup & Installation

| Command | Description |
|---------|-------------|
| `just install` | Install all dependencies (including dev) via pip |
| `just setup-hooks` | Install pre-commit hooks |
| `just setup` | Full setup: install + hooks + verification |

### Environment Management

| Command | Description |
|---------|-------------|
| `just venv-create` | Create virtual environment (runs `scripts/venv-create.sh`) |
| `just venv-clean` | Remove virtual environment (runs `scripts/venv-clean.sh`) |
| `just check-env` | Validate environment variables (runs `scripts/check-env.sh`) |
| `just info` | Show Python version, package info, and MCP_N8N_* env vars |

### Testing

| Command | Description | Typical Use |
|---------|-------------|-------------|
| `just test` | Run all tests via pytest | Before committing |
| `just smoke` | Run smoke tests only (fast, <30s) | Quick validation |
| `just test-coverage` | Run tests with coverage report (HTML + terminal) | Check coverage |
| `just verify` | Run pre-commit + smoke + all tests | Before pushing |

**Coverage reports** are generated in `htmlcov/index.html` when using `just test-coverage`.

### Code Quality

| Command | Description | When to Use |
|---------|-------------|-------------|
| `just lint` | Run ruff linter (check only) | Check for issues |
| `just lint-fix` | Run ruff with auto-fix | Fix trivial issues |
| `just format` | Run black code formatter | Format code |
| `just typecheck` | Run mypy type checker | Verify type safety |
| `just check` | Run lint + typecheck + format check | Pre-commit checks |
| `just pre-commit` | Run pre-commit on all files | Manual hook trigger |

### Running the Gateway

| Command | Description | Environment |
|---------|-------------|-------------|
| `just run` | Start gateway server (normal mode) | Production-like |
| `just run-debug` | Start gateway with DEBUG logging and debug mode | Development |

**Debug mode** sets:
- `MCP_N8N_LOG_LEVEL=DEBUG`
- `MCP_N8N_DEBUG=1`

### Development Tools

| Command | Description |
|---------|-------------|
| `just diagnose` | Run diagnostic checks (runs `scripts/diagnose.sh`) |
| `just dev-server` | Start development server (runs `scripts/dev-server.sh`) |
| `just docs` | Show available documentation |

### Version Management

| Command | Description | Example |
|---------|-------------|---------|
| `just bump-major` | Bump major version (breaking changes) | `0.4.0` → `1.0.0` |
| `just bump-minor` | Bump minor version (new features) | `0.4.0` → `0.5.0` |
| `just bump-patch` | Bump patch version (bug fixes) | `0.4.0` → `0.4.1` |

**Version bump scripts** update `pyproject.toml` and create a git commit.

### Release Management

| Command | Description | When to Use |
|---------|-------------|-------------|
| `just prepare-release TYPE` | Prepare release (bump + changelog) | Manual release prep |
| `just release-draft TYPE` | Prepare release locally (no push) | Review before release |
| `just release TYPE` | **Full automated release** (prepare + tag + push) | Production release |

**TYPE** must be one of: `major`, `minor`, `patch`

**Automated release flow** (`just release TYPE`):
1. Bumps version
2. Updates CHANGELOG.md
3. Creates git commit
4. Creates git tag
5. Pushes to GitHub
6. GitHub Actions builds and publishes to PyPI

### Build & Publish

| Command | Description | Environment |
|---------|-------------|-------------|
| `just build` | Build distribution packages (runs `scripts/build-dist.sh`) | Creates `dist/` |
| `just publish-test` | Publish to TestPyPI (runs `scripts/publish-test.sh`) | Staging |
| `just publish-prod` | Publish to production PyPI (runs `scripts/publish-prod.sh`) | Production |

**Note:** Prefer `just release TYPE` for automated releases.

### Safety & Recovery

| Command | Description | When to Use |
|---------|-------------|-------------|
| `just rollback` | Rollback to previous state (runs `scripts/rollback-dev.sh`) | After failed changes |
| `just verify-stable` | Verify stability (runs `scripts/verify-stable.sh`) | After major changes |
| `just pre-merge` | Pre-merge checks (runs `scripts/pre-merge.sh`) | Before merging PR |

### Cleanup

| Command | Description |
|---------|-------------|
| `just clean` | Remove build artifacts, caches, and generated files |

**Removes:**
- `build/`, `dist/`, `*.egg-info/`
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- `htmlcov/`, `__pycache__/` directories

### Common Workflows

```bash
# New feature development
just setup                    # One-time setup
just smoke                    # Quick validation
just run-debug                # Test manually
just verify                   # Before committing

# Before committing
just check                    # Lint + typecheck + format check
just smoke                    # Fast tests

# Before pushing
just verify                   # Pre-commit + smoke + all tests

# Release new version
just release patch            # Automated release (or minor/major)

# Troubleshooting
just info                     # Check environment
just diagnose                 # Run diagnostics
just clean && just install    # Clean reinstall
```

---

## Architecture Deep Dive

### Pattern P5: Gateway & Aggregator

mcp-n8n implements the **Meta-MCP Server** pattern (P5) from the MCP Server Patterns Catalog.

**For detailed architecture**, see [ARCHITECTURE.md](ARCHITECTURE.md).

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
3. BackendRegistry parses namespace: "chora"
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
├── event_watcher.py        # Event monitoring
├── memory/                 # Event system
│   ├── __init__.py        # TraceContext, emit_event
│   └── event_log.py       # EventLog (JSONL persistence)
├── tools/                  # Gateway tools
│   └── event_query.py     # get_events tool implementation
├── workflows/              # Event-driven workflows
│   ├── daily_report.py    # Daily report workflow
│   └── event_router.py    # EventWorkflowRouter
└── backends/
    ├── base.py             # Abstract backend interface
    ├── registry.py         # Backend lifecycle & routing
    ├── chora_composer.py   # Chora Composer backend
    └── coda_mcp.py         # Coda MCP backend
```

**Key classes:**

- **`FastMCP` (gateway.py)** - Main MCP server instance
- **`BackendRegistry` (registry.py)** - Manages backend lifecycle
- **`StdioSubprocessBackend` (base.py)** - Subprocess backend implementation
- **`GatewayConfig` (config.py)** - Pydantic configuration model
- **`EventLog` (memory/event_log.py)** - JSONL event persistence
- **`EventWatcher` (event_watcher.py)** - Monitor chora-compose events

---

## Code Organization

### Module Structure

**`src/mcp_n8n/gateway.py`** ([view](../src/mcp_n8n/gateway.py))
- Main entry point
- FastMCP server setup
- Backend initialization and lifecycle
- Gateway tools: `gateway_status`, `get_events`
- Event system initialization

**`src/mcp_n8n/config.py`**
- `GatewayConfig` - Main configuration model
- `BackendConfig` - Per-backend settings
- Environment variable loading
- Validation logic

**`src/mcp_n8n/logging_config.py`**
- `StructuredFormatter` - JSON log formatting
- Log setup and configuration
- Debug mode support

**`src/mcp_n8n/backends/base.py`**
- `Backend` - Abstract base class
- `StdioSubprocessBackend` - Subprocess implementation
- Lifecycle methods: `start()`, `stop()`, `call_tool()`
- `BackendStatus` enum: STOPPED, STARTING, RUNNING, FAILED

**`src/mcp_n8n/backends/registry.py`** ([view](../src/mcp_n8n/backends/registry.py))
- `BackendRegistry` - Backend manager
- Registration with namespace validation
- Tool routing by namespace
- Capability aggregation
- Status tracking

**`src/mcp_n8n/backends/chora_composer.py`**
- `ChoraComposerBackend` - Chora integration
- Subprocess management
- Tool namespace: `chora:*`
- Tools: generate_content, assemble_artifact, list_generators, validate_content

**`src/mcp_n8n/backends/coda_mcp.py`**
- `CodaMCPBackend` - Coda integration
- Subprocess management
- Tool namespace: `coda:*`
- Tools: list_docs, list_tables, list_rows, create_hello_doc_in_folder

**`src/mcp_n8n/memory/event_log.py`**
- JSONL event storage in `.chora/memory/events/<date>.jsonl`
- Query by trace_id, event_type, status, time range
- Correlation ID support for multi-step workflows

**`src/mcp_n8n/event_watcher.py`**
- Watch `var/telemetry/events.jsonl` from chora-compose
- Forward events to EventLog
- Optional n8n webhook integration

**`src/mcp_n8n/workflows/event_router.py`**
- `EventWorkflowRouter` - Map events to workflows
- Pattern-based routing
- Async workflow execution

### Test Organization

```
tests/
├── conftest.py                      # Shared fixtures
├── test_config.py                   # Configuration tests
├── test_registry.py                 # Registry tests
├── smoke/                           # Smoke tests (fast, with mocks)
│   ├── conftest.py
│   ├── test_gateway_startup.py
│   ├── test_chora_routing.py
│   ├── test_coda_routing.py
│   └── test_namespace_isolation.py
├── integration/                     # Integration tests (with real backends)
│   └── test_backend_jsonrpc.py
├── features/                        # BDD feature files
│   ├── daily_report.feature
│   └── sprint_5_workflows.feature
├── step_defs/                       # BDD step definitions
│   ├── test_daily_report_steps.py
│   └── test_sprint_5_workflow_steps.py
└── workflows/                       # Workflow tests
    ├── test_daily_report.py
    └── test_event_router.py
```

**Test categories:**

1. **Unit tests** - Test individual functions/classes (fast, no I/O)
2. **Smoke tests** - Fast validation with mocks (<30 sec)
3. **Integration tests** - Real backends, real I/O
4. **BDD tests** - Cucumber-style acceptance tests

---

## Backend Integration

### Adding a New Backend

Follow these steps to integrate a new MCP backend:

#### Step 1: Create Backend Class

Create `src/mcp_n8n/backends/your_backend.py`:

```python
from mcp_n8n.backends.base import StdioSubprocessBackend, BackendStatus
from mcp_n8n.config import BackendConfig
import logging

logger = logging.getLogger(__name__)

class YourBackend(StdioSubprocessBackend):
    """Backend for Your MCP Server."""

    def __init__(self, config: BackendConfig):
        super().__init__(config)
        # Add any backend-specific initialization
```

#### Step 2: Add Configuration Helper

In `src/mcp_n8n/config.py`, add:

```python
class GatewayConfig(BaseSettings):
    # ... existing fields ...

    your_api_key: str = Field(
        default="",
        env="YOUR_API_KEY",
        description="API key for Your backend",
    )

    def get_your_backend_config(self) -> BackendConfig | None:
        """Get Your backend configuration."""
        if not self.your_api_key:
            return None

        return BackendConfig(
            name="your-backend",
            type=BackendType.STDIO_SUBPROCESS,
            command="your-mcp-server",  # Must be in PATH
            args=[],
            enabled=True,
            namespace="your",  # Tool prefix: your:*
            capabilities=["capability1", "capability2"],
            env={"YOUR_API_KEY": self.your_api_key},
            timeout=self.backend_timeout,
        )

    def get_all_backend_configs(self) -> list[BackendConfig]:
        """Get all backend configurations."""
        configs = []

        if chora := self.get_chora_composer_config():
            configs.append(chora)
        if coda := self.get_coda_mcp_config():
            configs.append(coda)
        if your := self.get_your_backend_config():  # Add here
            configs.append(your)

        return configs
```

#### Step 3: Add Tests

Create `tests/smoke/test_your_routing.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_your_backend():
    backend = MagicMock()
    backend.name = "your-backend"
    backend.namespace = "your"
    backend.status = BackendStatus.RUNNING
    backend.call_tool = AsyncMock(return_value={"result": "success"})
    backend.get_tools = MagicMock(return_value=[
        {"name": "your:tool1", "description": "Tool 1"},
    ])
    return backend

async def test_your_tool_routing(mock_your_backend):
    """Test routing to Your backend."""
    result = await mock_your_backend.call_tool(
        "tool1",  # Without namespace (backend strips it)
        {"arg": "value"},
    )
    assert result["result"] == "success"
```

#### Step 4: Update Documentation

- Add backend to [README.md](../README.md)
- Document tools in [ARCHITECTURE.md](ARCHITECTURE.md)
- Add configuration to [.env.example](../.env.example)

#### Step 5: Update Configuration Examples

Add to `.config/claude-desktop.example.json`:

```json
{
  "mcpServers": {
    "mcp-n8n": {
      "command": "mcp-n8n",
      "env": {
        "ANTHROPIC_API_KEY": "your-key",
        "CODA_API_KEY": "your-key",
        "YOUR_API_KEY": "your-key"
      }
    }
  }
}
```

---

## Testing Strategy

### Unit Tests

Test individual components in isolation:

```python
def test_config_validation():
    """Test configuration model validation."""
    config = GatewayConfig(
        log_level="INFO",
        anthropic_api_key="test-key",
    )
    assert config.log_level == "INFO"

def test_config_invalid_log_level():
    """Test invalid log level raises error."""
    with pytest.raises(ValueError):
        GatewayConfig(log_level="INVALID")
```

**Run:** `pytest tests/test_config.py`

### Smoke Tests

Fast validation with mocks (<30 sec total):

```python
async def test_backend_registry_routing(mock_backend):
    """Smoke test: backend registry routes correctly."""
    registry = BackendRegistry()
    registry.register(mock_backend.config)

    backend = registry.get_backend_by_namespace("test")
    assert backend is not None
```

**Run:** `just smoke` or `pytest tests/smoke/`

**Smoke test guidelines:**
- Use mocks, no real backends
- Test critical paths only
- Run in <30 seconds total
- Focus on routing and lifecycle, not functionality

### Integration Tests

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

**Run:** `pytest tests/integration/`

### BDD Tests

Cucumber-style acceptance tests using pytest-bdd:

**Feature:** `tests/features/daily_report.feature`
```gherkin
Feature: Daily Report Workflow
  Scenario: Generate daily report
    Given the gateway is running
    When I request a daily report
    Then the report contains commit summaries
```

**Steps:** `tests/step_defs/test_daily_report_steps.py`

**Run:** `pytest tests/step_defs/`

---

## Debugging Tips

### VSCode Debugging

1. **Set breakpoints** in source code
2. **Run debug configuration** (F5):
   - "Launch Gateway" - Normal mode
   - "Launch Gateway (Debug Mode)" - Verbose logging
   - "Run Smoke Tests" - Debug tests

3. **Common breakpoints:**
   - [gateway.py:289](../src/mcp_n8n/gateway.py#L289) - `main()` entry point
   - [registry.py:124](../src/mcp_n8n/backends/registry.py#L124) - `route_tool_call()` routing
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

# OR use justfile
just run-debug
```

**Logs location:** `logs/mcp-n8n.log`

### Trace Context

Use trace IDs to correlate related events:

```python
from mcp_n8n.memory import TraceContext, emit_event

with TraceContext() as trace_id:
    emit_event("tool.call_started", trace_id=trace_id, tool_name="chora:assemble_artifact")
    # ... do work ...
    emit_event("tool.call_completed", trace_id=trace_id, status="success")
```

Query events by trace:

```python
from mcp_n8n.memory.event_log import EventLog

event_log = EventLog(base_dir=Path(".chora/memory/events"))
events = event_log.query(trace_id="abc123...")
```

### Common Debug Scenarios

**Problem: Tool not found**

```python
# Add breakpoint in registry.py:
def route_tool_call(self, tool_name: str) -> tuple[Backend, str] | None:
    # Check:
    # - tool_name format (has namespace?)
    # - backends registered?
    # - namespace matches?
```

**Problem: Backend not responding**

```python
# Add breakpoint in base.py:
async def call_tool(self, tool_name: str, arguments: dict):
    # Check:
    # - process running? (self.process.poll())
    # - stdin/stdout pipes working?
    # - request format correct?
```

**Problem: Events not appearing**

```python
# Check EventWatcher status
just run-debug
# Look for "EventWatcher started successfully" in logs
# Check var/telemetry/events.jsonl exists
# Check .chora/memory/events/<date>.jsonl
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

1. Ensure test coverage for code to refactor
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

See [RELEASE.md](RELEASE.md) for full process.

**Quick version (Automated):**

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

---

## Best Practices

### Code Quality

- **Type hints** on all public functions
- **Docstrings** on all public APIs (Google style)
- **Error handling** with specific exceptions
- **Logging** at appropriate levels
- **Testing** with ≥15% coverage (target: 85%)

### Git Workflow

- **Small commits** with clear messages
- **Feature branches** for all changes
- **Rebase before merge** to keep history clean
- **Conventional commits** format (optional but recommended)

### Documentation

- **Update docs** with code changes
- **Add examples** for new features
- **Explain "why"** not just "what"
- **Keep README current**

### Performance

- **Avoid blocking operations** in async code
- **Use subprocess for backends** (current approach)
- **Cache when appropriate**
- **Profile before optimizing**

---

## Resources

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture with diagrams
- **[TESTING.md](TESTING.md)** - Testing guide (coming soon)
- **[RELEASE.md](RELEASE.md)** - Release process (coming soon)
- **[TROUBLESHOOTING.md](../TROUBLESHOOTING.md)** - Problem solving
- **[MCP Specification](https://modelcontextprotocol.io)** - MCP protocol
- **[FastMCP Docs](https://github.com/jlowin/fastmcp)** - FastMCP library
- **[just Manual](https://just.systems/man/en/)** - Task runner documentation

---

**Last updated:** 2025-10-21
