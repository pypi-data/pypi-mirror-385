# Testing Guide

This guide explains mcp-n8n's testing strategy, philosophy, and workflows.

---

## Table of Contents

- [Overview](#overview)
- [Testing Philosophy](#testing-philosophy)
- [Test Pyramid](#test-pyramid)
- [Test Categories](#test-categories)
- [BDD Workflow](#bdd-workflow)
- [TDD Workflow](#tdd-workflow)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Organization](#test-organization)
- [Best Practices](#best-practices)

---

## Overview

mcp-n8n uses a **multi-layered testing strategy** combining:

1. **Unit Tests** - Fast, isolated tests of individual components
2. **Smoke Tests** - Quick validation with mocks (<30 seconds)
3. **Integration Tests** - Real backends and I/O
4. **BDD Tests** - Cucumber-style acceptance criteria
5. **Workflow Tests** - Event-driven workflow validation

**Current Coverage:** ~19% (target: 85%)

**Test Framework:** pytest + pytest-bdd + pytest-asyncio

---

## Testing Philosophy

### Core Principles

**1. Test Behavior, Not Implementation**
```python
# ✅ GOOD: Test what it does
def test_gateway_routes_to_chora_backend():
    result = registry.route_tool_call("chora:assemble_artifact")
    assert result[0].namespace == "chora"

# ❌ BAD: Test how it does it
def test_gateway_calls_split_method():
    with mock.patch.object(str, 'split') as mock_split:
        registry.route_tool_call("chora:assemble_artifact")
        mock_split.assert_called_once()
```

**2. Tests as Living Documentation**
- Tests should be readable by non-developers
- Test names should describe behavior clearly
- BDD scenarios document acceptance criteria

**3. Fast Feedback Loop**
- Unit tests run in milliseconds
- Smoke tests complete in <30 seconds
- Integration tests run in CI only

**4. Test-Driven Development (TDD)**
- Write tests before implementation (red-green-refactor)
- Tests drive design decisions
- Refactor with confidence

---

## Test Pyramid

```
         ┌─────────────────┐
         │  BDD/E2E Tests  │  ← Few, slow, high-value
         │   (Features)    │     (sprint acceptance)
         └────────┬────────┘
                  │
         ┌────────┴────────────┐
         │ Integration Tests   │  ← Some, moderate speed
         │  (Real backends)    │     (backend communication)
         └─────────┬───────────┘
                   │
         ┌─────────┴──────────────┐
         │    Smoke Tests         │  ← More, fast with mocks
         │  (Critical paths)      │     (routing, lifecycle)
         └────────────┬───────────┘
                      │
         ┌────────────┴───────────────┐
         │      Unit Tests            │  ← Most, very fast
         │  (Pure functions)          │     (validation, parsing)
         └────────────────────────────┘
```

**Distribution:**
- 60% Unit tests (isolated, <10ms each)
- 25% Smoke tests (mocked, <100ms each)
- 10% Integration tests (real I/O, <1s each)
- 5% BDD/E2E tests (full workflows, <10s each)

---

## Test Categories

### 1. Unit Tests

**Location:** `tests/unit/`, `tests/test_*.py`

**Purpose:** Test individual functions/classes in isolation

**Characteristics:**
- Mock all external dependencies
- Fast (<10ms per test)
- Focus on edge cases and error handling
- 100% coverage target for critical modules

**Example:**
```python
# tests/test_config.py
def test_gateway_config_validates_log_level():
    """Config rejects invalid log levels."""
    with pytest.raises(ValidationError):
        GatewayConfig(log_level="INVALID")

def test_backend_config_requires_namespace():
    """BackendConfig requires namespace field."""
    with pytest.raises(ValidationError):
        BackendConfig(name="test", type=BackendType.STDIO_SUBPROCESS)
```

**Run:** `pytest tests/test_*.py tests/unit/`

---

### 2. Smoke Tests

**Location:** `tests/smoke/`

**Purpose:** Fast validation of critical paths with mocks

**Characteristics:**
- Use mocks for backends and external I/O
- Complete in <30 seconds total
- Test routing, namespace isolation, lifecycle
- Run on every commit

**Example:**
```python
# tests/smoke/test_chora_routing.py
async def test_chora_tool_routes_to_chora_backend(mock_registry):
    """Smoke: chora:* tools route to Chora backend."""
    result = mock_registry.route_tool_call("chora:assemble_artifact")

    assert result is not None
    backend, stripped_name = result
    assert backend.namespace == "chora"
    assert stripped_name == "assemble_artifact"
```

**Run:** `just smoke` or `pytest tests/smoke/`

---

### 3. Integration Tests

**Location:** `tests/integration/`

**Purpose:** Test with real backends and I/O

**Characteristics:**
- Use real subprocess backends (or test doubles)
- Slower (100ms - 1s per test)
- Test JSON-RPC communication
- Verify end-to-end flows
- Run in CI only (marked with `@pytest.mark.integration`)

**Example:**
```python
# tests/integration/test_backend_jsonrpc.py
@pytest.mark.integration
async def test_backend_subprocess_jsonrpc_communication():
    """Integration: Backend subprocess responds to JSON-RPC."""
    config = BackendConfig(
        name="test-backend",
        type=BackendType.STDIO_SUBPROCESS,
        command="python",
        args=["-m", "tests.integration.mock_mcp_server"],
        namespace="test",
    )

    backend = StdioSubprocessBackend(config)
    await backend.start()

    # Verify backend is running
    assert backend.status == BackendStatus.RUNNING

    await backend.stop()
```

**Run:** `pytest tests/integration/ -m integration`

---

### 4. BDD Tests (Cucumber-style)

**Location:** `tests/features/*.feature`, `tests/step_defs/*.py`

**Purpose:** Executable specifications in natural language

**Characteristics:**
- Written in Gherkin (Given/When/Then)
- Readable by non-developers
- Validate acceptance criteria
- Living documentation

**Example:**
```gherkin
# tests/features/sprint_5_workflows.feature
Feature: Event-Driven Workflows

  Scenario: Daily report workflow processes git commits
    Given the gateway is running with EventWorkflowRouter
    When a daily_report_requested event is emitted
    Then the DailyReportWorkflow is triggered
    And the workflow queries git commits from the last 24 hours
    And a report is generated with commit summaries
```

**Step definitions:**
```python
# tests/step_defs/test_sprint_5_workflow_steps.py
@when("a daily_report_requested event is emitted")
async def emit_daily_report_event(event_router):
    """Emit event to trigger workflow."""
    event = {
        "event_type": "daily_report_requested",
        "timestamp": datetime.now().isoformat(),
    }
    await event_router.route_event(event)

@then("the DailyReportWorkflow is triggered")
def verify_workflow_triggered(workflow_mock):
    """Assert workflow was called."""
    workflow_mock.run.assert_called_once()
```

**Run:** `pytest tests/step_defs/`

---

### 5. Workflow Tests

**Location:** `tests/workflows/`

**Purpose:** Test event-driven workflows

**Characteristics:**
- Test EventWorkflowRouter routing logic
- Validate workflow execution
- Mock external dependencies (git, n8n webhooks)

**Example:**
```python
# tests/workflows/test_daily_report.py
async def test_daily_report_workflow_queries_commits():
    """Daily report workflow retrieves git commits."""
    workflow = DailyReportWorkflow()

    report = await workflow.run(hours=24)

    assert "commits" in report
    assert len(report["commits"]) > 0
    assert all("sha" in c for c in report["commits"])
```

**Run:** `pytest tests/workflows/`

---

## BDD Workflow

**BDD (Behavior-Driven Development)** uses natural language scenarios to specify expected behavior.

### Process

**Step 1: Write Feature File**

Create `tests/features/{feature}.feature`:

```gherkin
Feature: Gateway Startup
  As a developer
  I want the gateway to start successfully
  So that I can use MCP tools

  Background:
    Given a valid configuration with API keys

  Scenario: Gateway starts with all backends
    When I start the gateway
    Then the gateway is running
    And the chora-composer backend is running
    And the coda-mcp backend is running
    And gateway_status tool is available
```

**Step 2: Implement Step Definitions**

Create `tests/step_defs/{feature}_steps.py`:

```python
from pytest_bdd import given, when, then, parsers

@given("a valid configuration with API keys")
def valid_config(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("CODA_API_KEY", "test-key")

@when("I start the gateway")
async def start_gateway(gateway_instance):
    """Start gateway server."""
    await gateway_instance.initialize_backends()

@then("the gateway is running")
def verify_gateway_running(gateway_instance):
    """Assert gateway is initialized."""
    assert gateway_instance.registry is not None
```

**Step 3: Run BDD Tests**

```bash
pytest tests/step_defs/ --gherkin-terminal-reporter -v
```

**Output:**
```
Feature: Gateway Startup
  Scenario: Gateway starts with all backends
    Given a valid configuration with API keys PASSED
    When I start the gateway PASSED
    Then the gateway is running PASSED
    And the chora-composer backend is running PASSED
```

**See:** [docs/process/bdd-workflow.md](../docs/process/bdd-workflow.md) for detailed BDD guide

---

## TDD Workflow

**TDD (Test-Driven Development)** means writing tests before implementation.

### Red-Green-Refactor Cycle

```
1. RED    → Write failing test (define behavior)
2. GREEN  → Write minimal code to pass
3. REFACTOR → Improve design (tests stay green)
4. REPEAT → Next behavior
```

### Example: Adding a New Tool

**Step 1: RED - Write Failing Test**

```python
# tests/test_new_tool.py
async def test_list_backends_tool_returns_all_backends():
    """New tool: list_backends returns all registered backends."""
    result = await gateway.list_backends()

    assert "backends" in result
    assert len(result["backends"]) == 2  # chora + coda
    assert any(b["namespace"] == "chora" for b in result["backends"])
```

**Run:** `pytest tests/test_new_tool.py -v`

**Output:** `AttributeError: module has no attribute 'list_backends'` ✅ (expected failure)

**Step 2: GREEN - Implement Tool**

```python
# src/mcp_n8n/gateway.py
@mcp.tool()
async def list_backends() -> dict[str, Any]:
    """List all registered backends and their status."""
    backends = []
    for name, backend in registry._backends.items():
        backends.append({
            "name": name,
            "namespace": backend.namespace,
            "status": backend.status.value,
        })
    return {"backends": backends}
```

**Run:** `pytest tests/test_new_tool.py -v`

**Output:** `PASSED` ✅

**Step 3: REFACTOR - Improve Design**

```python
# Extract to registry method for reusability
class BackendRegistry:
    def list_backends(self) -> list[dict[str, Any]]:
        """List all registered backends."""
        return [
            {
                "name": name,
                "namespace": backend.namespace,
                "status": backend.status.value,
                "tool_count": len(backend.get_tools()),
            }
            for name, backend in self._backends.items()
        ]

# Gateway tool delegates to registry
@mcp.tool()
async def list_backends() -> dict[str, Any]:
    """List all registered backends and their status."""
    return {"backends": registry.list_backends()}
```

**Run:** `pytest tests/test_new_tool.py -v`

**Output:** `PASSED` ✅ (still green after refactor)

**See:** [docs/process/tdd-workflow.md](../docs/process/tdd-workflow.md) for detailed TDD guide

---

## Running Tests

### Quick Commands

```bash
# All tests
just test

# Smoke tests only (fast)
just smoke

# With coverage
just test-coverage

# Specific test file
pytest tests/test_config.py -v

# Specific test function
pytest tests/test_config.py::test_gateway_config_loads_from_env -v

# BDD tests with Gherkin reporter
pytest tests/step_defs/ --gherkin-terminal-reporter -v

# Integration tests only
pytest -m integration

# Skip integration tests
pytest -m "not integration"

# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Verbose output
pytest -vv
```

### Coverage Reports

```bash
# Generate HTML coverage report
just test-coverage

# View in browser
open htmlcov/index.html

# Terminal summary
pytest --cov=mcp_n8n --cov-report=term
```

**Coverage Targets:**
- Overall: ≥15% (current), target: 85%
- Unit tests: ≥90%
- Integration tests: ≥80%
- Critical modules (gateway, registry): 95%

---

## Writing Tests

### Test Structure (AAA Pattern)

```python
async def test_backend_registry_routes_correctly():
    """Test that registry routes namespaced tools to correct backend."""

    # ARRANGE: Set up test data
    config = BackendConfig(
        name="test-backend",
        namespace="test",
        type=BackendType.STDIO_SUBPROCESS,
        command="echo",
    )
    registry = BackendRegistry()
    registry.register(config)

    # ACT: Perform action
    result = registry.route_tool_call("test:my_tool")

    # ASSERT: Verify outcome
    assert result is not None
    backend, stripped_name = result
    assert backend.namespace == "test"
    assert stripped_name == "my_tool"
```

### Naming Conventions

**Good test names:**
- `test_gateway_routes_namespaced_tools_to_backends`
- `test_config_rejects_invalid_log_level`
- `test_event_log_stores_events_in_jsonl_format`

**Bad test names:**
- `test_gateway` (too vague)
- `test_1`, `test_2` (meaningless)
- `test_it_works` (what works?)

### Using Fixtures

```python
# tests/conftest.py (shared fixtures)
@pytest.fixture
def mock_backend_config():
    """Fixture providing test backend configuration."""
    return BackendConfig(
        name="test-backend",
        namespace="test",
        type=BackendType.STDIO_SUBPROCESS,
        command="echo",
        enabled=True,
    )

@pytest.fixture
async def backend_registry(mock_backend_config):
    """Fixture providing initialized registry."""
    registry = BackendRegistry()
    registry.register(mock_backend_config)
    yield registry
    # Cleanup if needed

# tests/test_registry.py (using fixtures)
async def test_registry_tracks_backend_count(backend_registry):
    """Registry tracks number of registered backends."""
    assert len(backend_registry._backends) == 1
```

### Async Tests

```python
import pytest

# Mark test as async
@pytest.mark.asyncio
async def test_backend_starts_successfully():
    """Test async backend startup."""
    backend = StdioSubprocessBackend(config)
    await backend.start()

    assert backend.status == BackendStatus.RUNNING

    await backend.stop()
```

### Mocking

```python
from unittest.mock import AsyncMock, MagicMock, patch

async def test_gateway_handles_backend_failure():
    """Gateway continues when one backend fails."""

    # Mock backend that fails on start
    mock_backend = MagicMock()
    mock_backend.start = AsyncMock(side_effect=BackendError("Connection failed"))

    with patch.object(registry, '_backends', {'failing': mock_backend}):
        # Should not raise exception
        await registry.start_all()

        # Verify error was logged (not raised)
        mock_backend.start.assert_called_once()
```

### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("namespace,expected_backend", [
    ("chora", "chora-composer"),
    ("coda", "coda-mcp"),
])
async def test_registry_routes_to_correct_backend(namespace, expected_backend):
    """Test routing for multiple backends."""
    result = registry.route_tool_call(f"{namespace}:some_tool")

    assert result is not None
    backend, _ = result
    assert backend.name == expected_backend
```

---

## Test Organization

### Directory Structure

```
tests/
├── conftest.py                # Shared fixtures
├── __init__.py
│
├── test_config.py             # Unit: Configuration
├── test_registry.py           # Unit: Backend registry
├── test_memory.py             # Unit: Event system
│
├── smoke/                     # Smoke tests (fast, mocked)
│   ├── conftest.py
│   ├── test_gateway_startup.py
│   ├── test_chora_routing.py
│   ├── test_coda_routing.py
│   └── test_namespace_isolation.py
│
├── unit/                      # Unit tests (isolated)
│   ├── test_daily_report_workflow.py
│   ├── test_event_watcher.py
│   └── test_event_router.py
│
├── integration/               # Integration tests (real I/O)
│   ├── test_backend_jsonrpc.py
│   ├── test_chora_composer_e2e.py
│   ├── test_gateway_subprocess.py
│   └── mock_mcp_server.py
│
├── features/                  # BDD feature files (Gherkin)
│   ├── daily_report.feature
│   ├── event_monitoring.feature
│   └── sprint_5_workflows.feature
│
├── step_defs/                 # BDD step definitions
│   ├── test_daily_report_steps.py
│   ├── test_sprint_5_workflow_steps.py
│   └── event_monitoring_steps.py
│
└── workflows/                 # Workflow tests
    ├── test_daily_report.py
    └── test_event_router.py
```

### Test Files vs. Source Files

**Convention:** Mirror source structure in test structure

| Source File | Test File |
|-------------|-----------|
| `src/mcp_n8n/gateway.py` | `tests/test_gateway.py` (unit)<br/>`tests/smoke/test_gateway_startup.py` (smoke)<br/>`tests/integration/test_gateway_subprocess.py` (integration) |
| `src/mcp_n8n/backends/registry.py` | `tests/test_registry.py` |
| `src/mcp_n8n/config.py` | `tests/test_config.py` |
| `src/mcp_n8n/workflows/daily_report.py` | `tests/workflows/test_daily_report.py` |

---

## Best Practices

### ✅ DO

**1. Test Behavior, Not Implementation**
```python
# ✅ GOOD
def test_config_loads_api_key_from_environment():
    config = load_config()
    assert config.anthropic_api_key is not None

# ❌ BAD
def test_config_calls_os_getenv():
    with patch('os.getenv') as mock_getenv:
        load_config()
        mock_getenv.assert_called()
```

**2. Use Descriptive Names**
```python
# ✅ GOOD
def test_backend_registry_routes_namespaced_tools_to_correct_backend()

# ❌ BAD
def test_routing()
```

**3. Keep Tests Independent**
```python
# ✅ GOOD: Each test sets up own data
def test_registry_with_one_backend():
    registry = BackendRegistry()
    registry.register(config1)
    assert len(registry._backends) == 1

def test_registry_with_two_backends():
    registry = BackendRegistry()
    registry.register(config1)
    registry.register(config2)
    assert len(registry._backends) == 2

# ❌ BAD: Tests depend on execution order
global_registry = BackendRegistry()

def test_add_first_backend():
    global_registry.register(config1)
    assert len(global_registry._backends) == 1

def test_add_second_backend():  # Breaks if run alone!
    global_registry.register(config2)
    assert len(global_registry._backends) == 2
```

**4. Test Edge Cases**
```python
async def test_route_tool_call_with_missing_namespace():
    """Edge case: Tool name without namespace."""
    result = registry.route_tool_call("tool_without_namespace")
    assert result is None

async def test_route_tool_call_with_unknown_namespace():
    """Edge case: Unknown namespace prefix."""
    result = registry.route_tool_call("unknown:tool")
    assert result is None
```

**5. Use Fixtures for Setup**
```python
@pytest.fixture
def initialized_registry():
    """Fixture providing pre-configured registry."""
    registry = BackendRegistry()
    registry.register(chora_config)
    registry.register(coda_config)
    return registry

def test_registry_lists_all_backends(initialized_registry):
    """Test uses fixture for setup."""
    backends = initialized_registry.list_backends()
    assert len(backends) == 2
```

### ❌ DON'T

**1. Don't Test Framework Code**
```python
# ❌ BAD: Testing pytest itself
def test_fixture_works(mock_backend):
    assert mock_backend is not None

# ✅ GOOD: Test your code
def test_backend_starts_successfully(mock_backend):
    await mock_backend.start()
    assert mock_backend.status == BackendStatus.RUNNING
```

**2. Don't Write Tests Just for Coverage**
```python
# ❌ BAD: Meaningless test for coverage
def test_import():
    import mcp_n8n.gateway
    assert mcp_n8n.gateway is not None

# ✅ GOOD: Test actual behavior
def test_gateway_initializes_registry():
    from mcp_n8n.gateway import registry
    assert isinstance(registry, BackendRegistry)
```

**3. Don't Use Sleep in Tests**
```python
# ❌ BAD: Using sleep for timing
async def test_backend_startup():
    await backend.start()
    await asyncio.sleep(2)  # Wait for startup
    assert backend.status == BackendStatus.RUNNING

# ✅ GOOD: Use proper async waiting
async def test_backend_startup():
    await backend.start()  # Already waits for completion
    assert backend.status == BackendStatus.RUNNING
```

**4. Don't Ignore Flaky Tests**
```python
# ❌ BAD: Ignoring intermittent failures
@pytest.mark.skip("This test is flaky")
def test_sometimes_fails():
    ...

# ✅ GOOD: Fix the root cause
def test_previously_flaky():
    # Fixed by using proper mocks instead of real timing
    ...
```

---

## Resources

- **[BDD Workflow](../docs/process/bdd-workflow.md)** - Detailed BDD guide
- **[TDD Workflow](../docs/process/tdd-workflow.md)** - Detailed TDD guide
- **[pytest Documentation](https://docs.pytest.org/)** - pytest framework
- **[pytest-bdd](https://pytest-bdd.readthedocs.io/)** - BDD plugin
- **[pytest-asyncio](https://pytest-asyncio.readthedocs.io/)** - Async test support
- **[Coverage.py](https://coverage.readthedocs.io/)** - Coverage measurement

---

**Source Files:**
- [tests/](../tests/) - Test suite
- [docs/process/bdd-workflow.md](../docs/process/bdd-workflow.md)
- [docs/process/tdd-workflow.md](../docs/process/tdd-workflow.md)

**Last Updated:** 2025-10-21
