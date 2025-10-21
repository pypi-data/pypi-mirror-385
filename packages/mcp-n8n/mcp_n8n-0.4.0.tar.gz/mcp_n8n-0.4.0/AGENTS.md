# AGENTS.md

This file provides machine-readable instructions for AI coding agents working with mcp-n8n.

---

## Project Overview

**mcp-n8n** is a **Pattern P5 (Gateway & Aggregator)** MCP server that provides a unified interface to multiple specialized MCP servers, implementing the Meta-MCP Server pattern from the MCP Server Patterns Catalog.

**Core Architecture:** Gateway & Aggregator
- Aggregate multiple backend MCP servers under a single interface
- Route tool calls based on namespace prefixes (e.g., `chora:*`, `coda:*`)
- Enforce **Chora Composer as exclusive artifact creation mechanism**
- Support subprocess-based backend integration with STDIO transport
- Provide lifecycle management for all backends

**Key Components:**
- **Gateway Server** (`gateway.py`) - FastMCP-based main server
- **Backend Registry** (`backends/registry.py`) - Backend lifecycle and routing
- **Backend Implementations** - Chora Composer, Coda MCP, extensible for future backends
- **Configuration System** (`config.py`) - Pydantic-based type-safe configuration
- **Structured Logging** (`logging_config.py`) - JSON logging with rotation
- **Event Monitoring** (`event_watcher.py`) - Real-time event monitoring and n8n webhook integration

**Backends:**
- **Chora Composer** (`chora:*`) - Exclusive artifact creation, content generation
- **Coda MCP** (`coda:*`) - Data operations on Coda documents

**Event Monitoring:**
- **EventWatcher** - Monitors chora-compose events, stores in gateway telemetry, forwards to n8n (optional)
- **get_events Tool** - MCP tool for querying events by trace_id, event_type, status, time range
- **EventLog** - Append-only event storage with monthly partitioning

### Strategic Context

**Current Priority:** Sprint 3 complete, proceeding to Sprint 5 (Production Workflows)
- See [docs/UNIFIED_ROADMAP.md](docs/UNIFIED_ROADMAP.md) and [docs/SPRINT_STATUS.md](docs/SPRINT_STATUS.md) for committed work
- Focus: Build production workflow templates, performance tuning, v0.3.0 release

**Long-Term Vision:** Multi-backend MCP gateway with rich telemetry and workflow orchestration
- See [docs/ROADMAP.md](docs/ROADMAP.md) for evolutionary direction
- Capabilities: Event monitoring (✅ complete), workflow templates (in progress), multi-backend orchestration

**Design Principle:** Deliver current commitments while keeping future doors open.
- Don't build future features now
- Do design extension points and document decisions
- Do refactor when it serves both present and future

---

## Dev Environment Tips

### Prerequisites
- **Python 3.11+** required (3.12+ recommended)
- **Git** for version control and submodule management
- **just** (optional but recommended) - Task runner for common commands
- **Chora Composer** - Required as submodule at `chora-composer/`
- **Coda MCP** - Optional backend (not included in this repository)

### Installation

```bash
# Clone repository with submodules
git clone --recursive https://github.com/yourusername/mcp-n8n.git
cd mcp-n8n

# If already cloned, initialize submodules
git submodule update --init --recursive

# One-command setup (recommended)
./scripts/setup.sh

# Manual setup alternative
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
pre-commit install
```

### Environment Variables

Create a `.env` file in project root:

```env
# Gateway configuration
MCP_N8N_LOG_LEVEL=INFO     # DEBUG, INFO, WARNING, ERROR, CRITICAL
MCP_N8N_DEBUG=0             # Set to 1 for debug mode

# Backend: Chora Composer (required for artifact operations)
ANTHROPIC_API_KEY=your_anthropic_key_here

# Backend: Coda MCP (optional for data operations)
CODA_API_KEY=your_coda_key_here
CODA_FOLDER_ID=your_folder_id_here  # Optional, for write operations

# Event Monitoring (optional for n8n integration)
N8N_EVENT_WEBHOOK_URL=http://localhost:5678/webhook/chora-events
```

### Client Configuration

#### Claude Desktop (macOS)

**Development Mode (Editable Install):**
```json
{
  "mcpServers": {
    "mcp-n8n-dev": {
      "command": "/path/to/mcp-n8n/.venv/bin/python",
      "args": ["-m", "mcp_n8n.gateway"],
      "cwd": "/path/to/mcp-n8n",
      "env": {
        "ANTHROPIC_API_KEY": "your_key",
        "CODA_API_KEY": "your_key",
        "MCP_N8N_DEBUG": "1"
      }
    }
  }
}
```

**Production Mode (Installed Package):**
```json
{
  "mcpServers": {
    "mcp-n8n": {
      "command": "mcp-n8n",
      "args": [],
      "env": {
        "ANTHROPIC_API_KEY": "your_key",
        "CODA_API_KEY": "your_key"
      }
    }
  }
}
```

**Config file location:** `~/Library/Application Support/Claude/claude_desktop_config.json`

#### Cursor

See [.config/cursor-mcp.example.json](.config/cursor-mcp.example.json) for complete examples.

**Config file location:** `~/.cursor/mcp.json`

### Available Gateway Tools

**Gateway Management:**
- `gateway_status` - Get status of gateway and all backends (health, tool counts, configuration, event monitoring status)

**Event Monitoring & Debugging:**
- `get_events` - Query gateway telemetry events for debugging and workflow analysis
  - **Query by trace_id:** `get_events(trace_id="abc123")` - Get all events for a workflow
  - **Query by event_type:** `get_events(event_type="chora.artifact_assembled")` - Find specific event types
  - **Query by status:** `get_events(status="failure", since="1h")` - Find recent failures
  - **Time ranges:** Supports "24h", "7d", ISO timestamps
  - **Use case:** Debug multi-step workflows, trace requests across gateway/backend boundaries
  - **Tutorial:** See [`docs/tutorials/event-monitoring-tutorial.md`](docs/tutorials/event-monitoring-tutorial.md)

**Backend Tools (Namespaced):**

All backend tools are automatically namespaced. The gateway currently does NOT dynamically expose backend tools. Agents should call backend tools directly through the backend's MCP server or reference the backend documentation.

**Expected Backend Tools (as of current implementation):**

**Chora Composer (`chora:*`):**
- `chora:generate_content` - Generate content from templates
- `chora:assemble_artifact` - Assemble artifacts from content pieces
- `chora:list_generators` - List available content generators
- `chora:validate_content` - Validate content configurations
- See [chora-composer/AGENTS.md](chora-composer/AGENTS.md) for complete tool reference

**Coda MCP (`coda:*`):**
- `coda:list_docs` - List Coda documents
- `coda:list_tables` - List tables in a document
- `coda:list_rows` - List rows from a table
- `coda:create_hello_doc_in_folder` - Create sample document
- See Coda MCP documentation for details

---

## Testing Instructions

### Run All Tests

```bash
# Using just (recommended)
just test

# Direct pytest
pytest

# With coverage report
just test-coverage
# OR
pytest --cov=mcp_n8n --cov-report=term-missing
```

### Smoke Tests (Quick Validation)

```bash
# Fast smoke tests (<30 seconds)
just smoke

# Direct pytest
pytest tests/smoke/ -v
```

### Test Categories

```bash
# Unit tests only
pytest tests/ -k "not integration and not smoke" -v

# Integration tests
pytest tests/integration/ -v

# Specific test file
pytest tests/test_config.py -v

# Specific test function
pytest tests/test_config.py::test_load_config -v
```

### Pre-Commit Hooks

```bash
# Run all pre-commit checks
just pre-commit
# OR
pre-commit run --all-files

# Install hooks (one-time setup)
pre-commit install

# Run specific hook
pre-commit run ruff --all-files
pre-commit run mypy --all-files
```

### Linting & Type Checking

```bash
# All quality checks (lint + typecheck + format)
just check

# Individual checks
just lint       # Ruff linting
just typecheck  # Mypy type checking
just format     # Ruff formatting

# Manual commands
ruff check src/mcp_n8n tests/
mypy src/mcp_n8n
ruff format src/mcp_n8n tests/

# Auto-fix linting issues
ruff check --fix src/mcp_n8n tests/
```

### Coverage Requirements

- **Overall coverage:** ≥85%
- **Critical paths:** 100% (config loading, backend registration, tool routing)
- **Backend lifecycle:** ≥90% (start/stop, error handling)
- **Unit tests:** ≥90%

### Pre-Merge Verification

```bash
# Full verification before submitting PR
just pre-merge

# Equivalent to:
# - pre-commit run --all-files
# - pytest (smoke + full test suite)
# - coverage check
```

---

## PR Instructions

### Branch Naming

```
feature/descriptive-name     # New features (e.g., feature/add-n8n-backend)
fix/issue-description        # Bug fixes (e.g., fix/backend-timeout-handling)
hotfix/critical-fix          # Production hotfixes
docs/documentation-update    # Documentation only
refactor/code-improvement    # Refactoring
```

### Commit Message Format

Follow **Conventional Commits** style:

```
type(scope): brief description

Detailed explanation of changes (if needed)

Closes #issue-number
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`

**Scopes:** `gateway`, `backends`, `config`, `logging`, `tests`, `ci`, `docs`

**Examples:**
```
feat(backends): add n8n workflow execution backend

Implement n8n backend with HTTP+SSE transport for workflow
execution. Includes retry logic and comprehensive error handling.

Closes #23

---

fix(gateway): handle missing backend gracefully

When a backend fails to start, gateway now continues with
remaining backends and logs clear warning message.

Fixes #45

---

docs: add AGENTS.md for LLM agent guidance

Implements OpenAI/Google/Sourcegraph AGENTS.md standard
to provide machine-readable project instructions.
```

### PR Checklist

**Before opening PR:**
- [ ] Branch is up to date with `main`
- [ ] All tests pass locally (`just test` or `pytest`)
- [ ] Coverage maintained or improved (≥85%)
- [ ] Linting passes (`just lint` or `ruff check`)
- [ ] Type checking passes (`just typecheck` or `mypy src/`)
- [ ] Pre-commit hooks pass (`just pre-commit`)
- [ ] Code formatted (`just format` or `ruff format`)

**Documentation (if applicable):**
- [ ] README.md updated (if user-facing changes)
- [ ] AGENTS.md updated (if agent workflow changes)
- [ ] API reference docs updated (if new tools/capabilities)
- [ ] CHANGELOG.md entry added (for releases)

**Testing:**
- [ ] Unit tests added/updated
- [ ] Integration tests added (if applicable)
- [ ] Smoke tests pass (`just smoke`)
- [ ] Manual testing completed in Claude Desktop/Cursor

**Review:**
- [ ] Self-review completed
- [ ] Code follows project style guide
- [ ] No debug code or commented-out code
- [ ] Error messages are clear and actionable
- [ ] Logging statements use appropriate levels

### Quality Gates (must pass)

1. **Lint:** `ruff check` → No errors
2. **Format:** `ruff format --check` → Formatted
3. **Types:** `mypy` → Type safe
4. **Tests:** All tests pass
5. **Coverage:** ≥85%
6. **Pre-commit:** All hooks pass

### PR Review Process

- **Required approvals:** 1+ reviewer (single-developer project: self-review acceptable)
- **Merge strategy:** Squash and merge (clean history)
- **CI/CD:** All quality gates must pass
- **Timeline:** Most PRs reviewed within 24-48 hours

---

## Architecture Overview

### P5 Gateway & Aggregator Pattern

```
┌─────────────────────────────────────────────┐
│   AI Client (Claude Desktop / Cursor)       │
│   - Sees single MCP server                  │
│   - Tools namespaced by backend             │
└──────────────────┬──────────────────────────┘
                   │ JSON-RPC / STDIO
                   ▼
┌─────────────────────────────────────────────┐
│  mcp-n8n Gateway (FastMCP Server)           │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │  Backend Registry                      │ │
│  │  - Lifecycle management (start/stop)   │ │
│  │  - Tool routing (namespace-based)      │ │
│  │  - Capability aggregation              │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  Routes by namespace:                        │
│  - chora:* → Chora Composer                 │
│  - coda:*  → Coda MCP                       │
│  - gateway_status → Gateway itself          │
└───────┬──────────────────┬──────────────────┘
        │                  │
        ▼                  ▼
┌───────────────┐   ┌─────────────┐
│ Chora         │   │ Coda MCP    │
│ Composer      │   │ Server      │
│ (Subprocess)  │   │ (Subprocess)│
└───────────────┘   └─────────────┘
```

### Backend Integration Architecture

```
Backend Registry
    ↓
    ├─ Backend (Abstract Interface)
    │   ├─ start() / stop()
    │   ├─ get_tools() / get_resources()
    │   └─ status management
    │
    ├─ StdioSubprocessBackend (Implementation)
    │   ├─ Spawns subprocess
    │   ├─ Manages lifecycle
    │   ├─ Handles stdio communication
    │   └─ Error handling & recovery
    │
    └─ Future: HttpSseBackend, StdioExternalBackend, etc.
```

### Key Design Patterns

- **Registry Pattern:** `BackendRegistry` manages backend instances
- **Abstract Factory:** Backend creation based on `BackendType` enum
- **Strategy Pattern:** Different backend integration methods (STDIO subprocess, HTTP+SSE)
- **Facade Pattern:** Gateway provides unified interface to multiple backends
- **Observer Pattern:** Status monitoring and health checks
- **Dependency Injection:** Configuration-driven backend instantiation

### Configuration Management

```
GatewayConfig (Pydantic Settings)
    ├─ Environment variables (MCP_N8N_*)
    ├─ .env file loading
    ├─ Type-safe validation
    └─ Backend factory methods
        ├─ get_chora_composer_config()
        ├─ get_coda_mcp_config()
        └─ get_all_backend_configs()

BackendConfig (Pydantic Model)
    ├─ name: str
    ├─ type: BackendType (enum)
    ├─ command: str | None
    ├─ args: list[str]
    ├─ enabled: bool
    ├─ namespace: str
    ├─ capabilities: list[str]
    ├─ env: dict[str, str]
    └─ timeout: int
```

---

## Key Constraints & Design Decisions

### Target Audience

**CRITICAL:** mcp-n8n is designed for **LLM-intelligent MCP clients** (Claude Desktop, Cursor, Roo Code).

- ✅ **FOR LLM agents** - Claude Desktop, Cursor, custom MCP clients
- ✅ **FOR programmatic use** - Python API, automation workflows
- ❌ **NOT for human CLI users** - No interactive wizards or watch modes

**Implication:** All features prioritize agent ergonomics over human UX.

### Backend Namespacing

- **Mandatory namespace prefixes** - All backend tools MUST be namespaced (e.g., `chora:`, `coda:`)
- **No namespace collisions** - Registry enforces unique namespaces
- **Gateway tools unnamespaced** - Gateway's own tools (like `gateway_status`) have no prefix
- **Routing by prefix** - Tool calls are routed to backends based on namespace prefix

### Backend Integration Method

- **STDIO subprocess primary** - Default integration via subprocess + STDIO
- **Process isolation** - Each backend runs in independent process
- **Lifecycle management** - Gateway controls backend start/stop
- **Future extensibility** - HTTP+SSE and external STDIO planned for future

### Chora Composer as Exclusive Artifact Creator

- **Design principle** - All artifact creation MUST go through Chora Composer
- **No direct file writing** - Gateway and other backends MUST NOT create artifacts
- **Enforced via architecture** - Only Chora Composer has artifact creation capabilities
- **Data vs. Artifacts** - Coda MCP handles data operations, NOT artifact creation

### Error Handling

- **Graceful degradation** - If one backend fails, others continue
- **Detailed logging** - All errors logged with context (backend name, operation, error)
- **Status reporting** - `gateway_status` tool provides health of all backends
- **No silent failures** - All errors propagated to calling agent

### Performance Targets

- **Gateway startup:** <5s with all backends
- **Backend startup:** <3s per backend
- **Tool routing:** <10ms overhead
- **Backend timeout:** Configurable (default 30s)

---

## Strategic Design

### Balancing Current Priorities with Future Vision

**The Balance:**
- ✅ **Deliver:** Ship current commitments on time
- ✅ **Design for evolution:** Keep future doors open (extension points)
- ✅ **Refactor strategically:** When it serves both present and future
- ❌ **NOT:** Premature optimization, gold plating, scope creep

**Key Insight:** Build for today, design for tomorrow. Don't implement Sprint 5 features in Sprint 3, but don't paint yourself into corners either.

### Vision-Aware Implementation Pattern

**When implementing features, ask:**

1. **Architecture Check:** "Does this design block future capabilities in [docs/ROADMAP.md](docs/ROADMAP.md)?"
   - ✅ YES → Refactor before implementing
   - ✅ NO → Proceed

2. **Refactoring Signal:** "Should I refactor this now?"
   ```
   ┌─────────────────────────────────────────────────────┐
   │ Does it help current work (current sprint)?         │
   │   NO → DEFER (focus on current deliverables)       │
   │   YES → Continue ↓                                  │
   ├─────────────────────────────────────────────────────┤
   │ Does it unblock future capabilities?                │
   │   YES → LIKELY REFACTOR (strategic investment)     │
   │   NO → Continue ↓                                   │
   ├─────────────────────────────────────────────────────┤
   │ Cost vs. benefit?                                    │
   │   HIGH COST → DEFER (wait for future sprint)       │
   │   LOW COST → REFACTOR (small prep, big payoff)     │
   └─────────────────────────────────────────────────────┘
   ```

3. **Decision Documentation:** Where to record decisions
   - **Knowledge notes:** `mcp-n8n-memory knowledge create "Decision: [topic]"`
   - **Tags:** Use `architecture`, `vision`, `sprint-N` tags for discoverability

### Practical Example: MCP Server Gateway

**Scenario:** Sprint 3 needs event monitoring. Sprint 5 roadmap includes multi-backend orchestration.

**❌ DON'T (Premature Optimization):**
```python
# DON'T build full orchestration system now
class Gateway:
    async def route_tool(self, tool: str):
        # Implements complex cross-backend workflows (Sprint 5 feature)
        return await self.orchestrator.execute_workflow([
            ("chora", "generate"),
            ("coda", "store")
        ])  # Not needed yet!
```

**✅ DO (Extension Point):**
```python
# DO emit events (enables future orchestration)
class Gateway:
    async def route_tool(self, tool: str):
        """Route tool call to backend (extensible for Sprint 5)."""
        backend = self.registry.get_backend(tool)
        result = await backend.call_tool(tool)

        # Emit event (hook for future orchestration)
        await emit_event(
            "gateway.tool_call",
            backend=backend.name,
            tool=tool,
            status="success"
        )
        return result
        # Sprint 5 can add: orchestration triggers on events
```

### Refactoring Decision Framework

**Use this checklist before refactoring:**

- [ ] **Current Work:** Does this help current sprint deliverables?
- [ ] **Future Vision:** Check [docs/ROADMAP.md](docs/ROADMAP.md) and [docs/UNIFIED_ROADMAP.md](docs/UNIFIED_ROADMAP.md) - does this prepare for next sprint?
- [ ] **Cost Assessment:** Low cost (<2 hours) or high cost (>1 day)?
- [ ] **Decision:** Apply framework above → Refactor now or defer?
- [ ] **Documentation:** Record decision (knowledge note with tags: `architecture`, `vision`)

### Capturing Knowledge for Future Agents

**Use A-MEM (Agentic Memory) patterns:**

1. **Emit Events:** Track architectural decisions
   ```python
   from mcp_n8n.memory import emit_event

   emit_event(
       event_type="architecture.decision",
       metadata={
           "decision": "Use event emission for extensibility",
           "rationale": "Enables Sprint 5 orchestration",
           "sprint": "sprint-5-preparation"
       },
       status="success"
   )
   ```

2. **Create Knowledge Notes:**
   ```bash
   echo "Decision: Event-Based Extension Points

   Context: Sprint 3 event monitoring, Sprint 5 vision includes orchestration.

   Decision: Emit events at all gateway operations.

   Rationale:
   - Low cost refactor (1 hour)
   - Unblocks Sprint 5 orchestration
   - Backward compatible

   Tags: architecture, vision, sprint-5, events
   " | mcp-n8n-memory knowledge create "Event Extension Points"
   ```

3. **Link to Roadmap:**
   - Reference sprint/phase in knowledge notes
   - Tag notes with `sprint-N` for future discoverability
   - Query past decisions: `mcp-n8n-memory knowledge search --tag sprint-5`

### Quick Reference: Strategic Design Checklist

**Before implementing any feature:**

1. ✅ **Check ROADMAP:** Is this in current committed work?
2. ✅ **Check SPRINT_STATUS:** Does this align with current sprint?
3. ✅ **Apply framework:** Refactor now or defer? (use flowchart above)
4. ✅ **Document:** Record decision for future agents
5. ✅ **Code:** Implement with extension points, not future features

**Remember:** Deliver today, design for tomorrow. No gold plating!

---

## Common Tasks for Agents

### Task 1: Check Gateway Status

```python
# Get comprehensive status
result = await mcp_client.call_tool("gateway_status", {})

# Result includes:
# - gateway: {name, version, config}
# - backends: {backend_name: {status, namespace, tool_count}}
# - capabilities: {tools, resources, prompts} counts

# Check if specific backend is running
if result["backends"]["chora-composer"]["status"] == "running":
    # Backend is ready for artifact operations
    pass
```

### Task 2: Create Artifact via Chora Composer

```python
# Step 1: Verify Chora Composer is available
status = await mcp_client.call_tool("gateway_status", {})
if status["backends"]["chora-composer"]["status"] != "running":
    raise Error("Chora Composer backend not available")

# Step 2: Call namespaced tool
# NOTE: Currently backends are not dynamically exposed, so this is
# illustrative. In practice, you would call the backend directly.
result = await mcp_client.call_tool("chora:assemble_artifact", {
    "artifact_config": {
        "type": "artifact",
        "name": "api-documentation",
        "content_refs": ["content-1", "content-2"],
        "output": {
            "file_path": "output/API_DOCS.md",
            "format": "markdown"
        }
    }
})

# For actual Chora Composer operations, see chora-composer/AGENTS.md
```

### Task 3: Handle Backend Failures

```python
# Check gateway status
status = await mcp_client.call_tool("gateway_status", {})

# Identify failed backends
failed_backends = [
    name for name, info in status["backends"].items()
    if info["status"] in ["failed", "stopped"]
]

if failed_backends:
    # Log warning
    print(f"Warning: {len(failed_backends)} backends unavailable: {failed_backends}")

    # Check if required backend is available
    if "chora-composer" in failed_backends:
        print("ERROR: Cannot perform artifact operations (Chora Composer unavailable)")
        # Suggest remediation
        print("Solution: Check ANTHROPIC_API_KEY environment variable")
```

### Task 4: Add New Backend (Development)

```python
# Step 1: Create backend configuration
# Edit src/mcp_n8n/config.py:

def get_new_backend_config(self) -> BackendConfig:
    return BackendConfig(
        name="new-backend",
        type=BackendType.STDIO_SUBPROCESS,
        command="new-backend-command",
        args=[],
        enabled=True,  # Or conditional on env var
        namespace="newbackend",
        capabilities=["new_capability"],
        env={"API_KEY": os.getenv("NEW_BACKEND_API_KEY", "")},
        timeout=self.backend_timeout,
    )

# Step 2: Add to get_all_backend_configs()
def get_all_backend_configs(self) -> list[BackendConfig]:
    backends = [
        self.get_chora_composer_config(),
        self.get_coda_mcp_config(),
        self.get_new_backend_config(),  # Add here
    ]
    return [b for b in backends if b.enabled]

# Step 3: Write tests
# tests/test_config.py:
def test_new_backend_config():
    config = GatewayConfig()
    backend = config.get_new_backend_config()
    assert backend.name == "new-backend"
    assert backend.namespace == "newbackend"

# Step 4: Update documentation
# - README.md: Add to "Available Tools" section
# - AGENTS.md: Add to "Available Gateway Tools" section
# - .env.example: Add new environment variables
```

### Task 5: Debug Backend Communication Issues

```bash
# Step 1: Enable debug mode
export MCP_N8N_DEBUG=1
export MCP_N8N_LOG_LEVEL=DEBUG

# Step 2: Run gateway with verbose output
just run-debug
# OR
./scripts/dev-server.sh

# Step 3: Check logs
tail -f logs/mcp-n8n.log

# Step 4: Look for specific error patterns:
# - "Failed to start backend" → Command not found or env var missing
# - "Timeout waiting for backend" → Backend startup too slow
# - "No backend found for namespace" → Namespace mismatch in tool call
# - "Backend status: failed" → Backend crashed or exited

# Step 5: Test backend in isolation
# For Chora Composer:
cd chora-composer
poetry run fastmcp run src/chora_compose/mcp/server.py

# For Coda MCP:
# Coda MCP is an optional backend, install separately if needed
# (follow their testing instructions)
```

### Task 6: Release Workflow (Maintainers Only)

**IMPORTANT:** This task is for project maintainers only. Contributors should focus on features and bug fixes.

**Fully Automated Release (Recommended):**

```bash
# Prerequisites
just check-env          # Ensure clean environment
just pre-merge          # All tests must pass
git status              # No uncommitted changes

# Single-command release
just release patch      # or: minor, major

# Monitor GitHub Actions
# https://github.com/YOUR_USERNAME/mcp-n8n/actions
# ~5 minutes total (build, test, publish to PyPI, create GitHub release)
```

**Manual Review Release:**

```bash
# Prepare release but don't push (for review)
just release-draft patch

# Review changes
git show HEAD
git diff HEAD~1

# Push when ready
git push origin main && git push origin vX.Y.Z
# GitHub Actions will automatically handle the rest
```

**What happens automatically:**
1. Version bump in pyproject.toml
2. CHANGELOG.md update (moves [Unreleased] → [version])
3. Pre-merge validation (tests, linting, coverage)
4. Release commit creation
5. Git tag creation (`vX.Y.Z`)
6. Push to GitHub (if using `just release`, not `just release-draft`)
7. GitHub Actions triggers:
   - Build distribution packages
   - Run tests on Python 3.12
   - Publish to PyPI
   - Create GitHub release with CHANGELOG notes

**See also:** [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) for detailed process.

**Rollback if needed:**

```bash
# If release preparation fails before push
git checkout pyproject.toml CHANGELOG.md

# If already pushed to PyPI (cannot delete, only yank)
twine yank mcp-n8n <version> --reason "Critical bug"
```

---

## Project Structure

```
mcp-n8n/
├── src/mcp_n8n/              # Main source code
│   ├── __init__.py              # Package metadata (__version__)
│   ├── gateway.py               # FastMCP server, main entry point
│   ├── config.py                # Configuration management (Pydantic)
│   ├── logging_config.py        # Structured logging setup
│   └── backends/                # Backend implementations
│       ├── __init__.py
│       ├── base.py              # Abstract Backend interface
│       ├── registry.py          # BackendRegistry (lifecycle, routing)
│       ├── chora_composer.py    # Chora Composer backend (future)
│       └── coda_mcp.py          # Coda MCP backend (future)
├── tests/                    # Test suite
│   ├── smoke/                   # Smoke tests (<30s)
│   ├── integration/             # Integration tests
│   ├── test_config.py           # Configuration tests
│   ├── test_registry.py         # Registry tests
│   └── fixtures/                # Test fixtures
├── scripts/                  # Automation scripts
│   ├── setup.sh                 # One-command setup
│   ├── venv-create.sh           # Create virtual environment
│   ├── integration-test.sh      # Integration test workflow
│   ├── handoff.sh               # Context switch handoff
│   ├── diagnose.sh              # Automated diagnostics
│   └── dev-server.sh            # Development server (auto-reload)
├── docs/                     # Documentation
│   ├── DEVELOPMENT.md           # Developer deep dive
│   ├── TROUBLESHOOTING.md       # Problem-solution guide
│   ├── RELEASE_CHECKLIST.md     # Release process
│   ├── UNIFIED_ROADMAP.md       # Multi-instance workflow roadmap
│   ├── ecosystem/               # Ecosystem documentation
│   └── process/                 # Process documentation (DDD/BDD/TDD)
├── chora-composer/           # Chora Composer submodule
│   └── AGENTS.md                # Chora Composer agent instructions
├── vendors/                  # Vendor dependencies
│   ├── chora-platform/          # Shared platform tooling
│   └── mcp-server-coda/         # Coda MCP server
├── .config/                  # Client configurations
│   ├── README.md                # Configuration guide
│   ├── claude-desktop.example.json
│   ├── cursor-mcp.example.json
│   └── dev-vs-stable.md         # Toggle guide
├── .github/workflows/        # CI/CD pipelines
│   ├── test.yml                 # Test workflow
│   └── lint.yml                 # Lint workflow
├── .vscode/                  # VSCode configuration
│   ├── launch.json              # Debug configurations (7 configs)
│   ├── settings.json            # Project settings
│   ├── tasks.json               # Build/test tasks (14 tasks)
│   └── extensions.json          # Recommended extensions
├── pyproject.toml            # Python packaging & tool config
├── justfile                  # Task runner commands
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore patterns
├── README.md                 # Human-readable project overview
├── AGENTS.md                 # This file (machine-readable instructions)
├── CONTRIBUTING.md           # Contribution guidelines (700+ lines)
├── ARCHITECTURE.md           # P5 pattern implementation details
└── LICENSE                   # MIT license
```

### Knowledge Note Metadata Standards

Knowledge notes (`.chora/memory/knowledge/notes/*.md`) use **YAML frontmatter** following Zettelkasten best practices for machine-readable metadata.

**Required Frontmatter Fields:**
- `id`: Unique note identifier (kebab-case)
- `created`: ISO 8601 timestamp
- `updated`: ISO 8601 timestamp
- `tags`: Array of topic tags for search/organization

**Optional Frontmatter Fields:**
- `confidence`: `low` | `medium` | `high` - Solution reliability
- `source`: `agent-learning` | `human-curated` | `external` | `research`
- `linked_to`: Array of related note IDs (bidirectional linking)
- `status`: `draft` | `validated` | `deprecated`
- `author`: Agent or human creator
- `related_traces`: Array of trace IDs that led to this knowledge

**Example Knowledge Note:**

```markdown
---
id: backend-timeout-solution
created: 2025-01-17T10:00:00Z
updated: 2025-01-17T12:30:00Z
tags: [troubleshooting, backend, performance]
confidence: high
source: agent-learning
linked_to: [trace-context-pattern, error-handling-best-practices]
status: validated
author: claude-code
related_traces: [abc123, def456]
---

# Backend Timeout Solution

## Problem
Backend subprocess fails to start within default 30s timeout...

## Solution
Increase `backend_timeout` configuration to 60s for development:

```env
MCP_N8N_BACKEND_TIMEOUT=60
```

## Evidence
- Trace abc123: Backend started successfully at 45s
- Trace def456: Backend started successfully at 52s
- Both would have failed with 30s timeout
```

**Why YAML Frontmatter?**
- ✅ **Semantic Search**: Query by confidence, tags, or date (`grep "confidence: high"`)
- ✅ **Tool Compatibility**: Works with Obsidian, Zettlr, LogSeq, Foam
- ✅ **Knowledge Graph**: Enables bidirectional linking and visualization
- ✅ **Agent Decision-Making**: Filter by confidence level for solution reliability

**Reference:** See [.chora/memory/README.md](.chora/memory/README.md) for complete schema documentation.

---

## Documentation Philosophy

### Diátaxis Framework

All documentation follows the [Diátaxis framework](https://diataxis.fr/):

1. **Tutorials** (learning-oriented) - Step-by-step lessons for newcomers
2. **How-To Guides** (task-oriented) - Recipes for specific tasks
3. **Reference** (information-oriented) - Technical specifications
4. **Explanation** (understanding-oriented) - Conceptual background

**For agents:** Reference docs are most useful (AGENTS.md, API docs). Tutorials are for humans.

### Documentation Hierarchy

- **README.md** - Human-readable overview, quick start, high-level features
- **AGENTS.md** - Machine-readable instructions for AI agents (this file)
- **CONTRIBUTING.md** - Human contributor guide (code style, PR process)
- **DEVELOPMENT.md** - Developer deep dive (architecture, debugging, testing)
- **TROUBLESHOOTING.md** - Problem-solution guide (common issues)
- **ARCHITECTURE.md** - P5 pattern implementation details

### DDD/BDD/TDD Workflow

This project uses the Chora ecosystem's integrated DDD/BDD/TDD workflow:

1. **DDD Phase** - Write API reference docs FIRST (documentation-driven design)
2. **BDD Phase** - Write Gherkin scenarios SECOND (behavior-driven development)
3. **TDD Phase** - Red-Green-Refactor THIRD (test-driven development)
4. **CI Phase** - Automated quality gates
5. **Merge & Release** - Semantic versioning

See [docs/process/development-lifecycle.md](docs/process/development-lifecycle.md) for details.

---

## Troubleshooting

### Gateway Won't Start

```bash
# Check Python version
python --version  # Must be 3.11+

# Check virtual environment
which python  # Should be .venv/bin/python

# Reinstall dependencies
./scripts/venv-create.sh

# Check environment variables
cat .env
# Ensure ANTHROPIC_API_KEY and/or CODA_API_KEY are set

# Test gateway directly
python -m mcp_n8n.gateway

# Check for port conflicts (if using HTTP in future)
# lsof -i :8080
```

### Backend Fails to Start

```bash
# Check backend is installed
which chora-compose  # Should be in PATH or .venv
which coda-mcp

# Test backend in isolation
cd chora-composer
poetry run fastmcp run src/chora_compose/mcp/server.py

# Check backend logs
tail -f logs/mcp-n8n.log | grep "chora-composer"

# Verify environment variables
echo $ANTHROPIC_API_KEY  # Should not be empty

# Increase timeout (if backend startup is slow)
export MCP_N8N_BACKEND_TIMEOUT=60
```

### Submodule Issues

```bash
# Initialize/update submodules
git submodule update --init --recursive

# Reset submodule to tracked commit
cd chora-composer
git checkout main  # or specific commit
cd ..

# Check submodule status
git submodule status

# Update submodule to latest
cd chora-composer
git pull origin main
cd ..
git add chora-composer
git commit -m "chore: update chora-composer submodule"
```

### Test Failures

```bash
# Run specific test with verbose output
pytest tests/test_config.py::test_load_config -vvs

# Show full error trace
pytest --tb=long

# Run with debugger
pytest --pdb

# Check test coverage
pytest --cov=mcp_n8n --cov-report=term-missing

# Clean test cache
pytest --cache-clear
rm -rf .pytest_cache __pycache__
```

### Type Checking Errors

```bash
# Run mypy with verbose output
mypy src/mcp_n8n --show-error-codes --pretty

# Check specific file
mypy src/mcp_n8n/gateway.py

# Ignore specific error (if intentional)
# Add to line:
# type: ignore[error-code]

# Update mypy configuration
# Edit [tool.mypy] in pyproject.toml
```

### Coverage Drop

```bash
# Show missing coverage lines
pytest --cov=mcp_n8n --cov-report=term-missing

# Generate HTML report
pytest --cov=mcp_n8n --cov-report=html
open htmlcov/index.html

# Check coverage for specific module
pytest --cov=mcp_n8n.backends --cov-report=term-missing

# Identify untested code
coverage report --show-missing
```

### Pre-Commit Hook Failures

```bash
# Run specific hook
pre-commit run ruff --all-files
pre-commit run mypy --all-files

# Update hook versions
pre-commit autoupdate

# Bypass hooks (emergency only, NOT recommended)
git commit --no-verify

# Clear pre-commit cache
pre-commit clean
```

---

## Agent Memory System (Phase 4.5)

### Overview

mcp-n8n includes a stateful memory infrastructure for cross-session learning and knowledge persistence, implementing A-MEM (Agentic Memory) principles.

**Memory capabilities:**
- **Event Log** - Append-only operation history with trace correlation
- **Knowledge Graph** - Structured learnings with Zettelkasten-style linking
- **Trace Context** - Multi-step workflow tracking via `CHORA_TRACE_ID`
- **Cross-Session Learning** - Avoid repeating mistakes across sessions

### Memory Location

All memory data stored in `.chora/memory/`:

```
.chora/memory/
├── README.md                    # Memory architecture documentation
├── events/                      # Event log storage (monthly partitions)
│   ├── 2025-01/
│   │   ├── events.jsonl         # Daily aggregated events
│   │   └── traces/              # Per-trace details
│   │       └── abc123.jsonl     # All events for trace_id=abc123
│   └── index.json               # Event index (searchable)
├── knowledge/                   # Knowledge graph
│   ├── notes/                   # Individual knowledge notes
│   │   └── backend-timeout-fix.md
│   ├── links.json               # Note connections
│   └── tags.json                # Tag index
├── profiles/                    # Agent-specific profiles
│   └── claude-code.json         # Per-agent learned patterns
└── queries/                     # Saved queries
```

**Privacy:** Memory directory is in `.gitignore` by default (contains ephemeral learning data, not source code).

### Event Log Usage

**Emit events during operations:**

```python
from mcp_n8n.memory import emit_event, TraceContext

# Start workflow with trace context
with TraceContext() as trace_id:
    # Emit operation events
    emit_event(
        "gateway.tool_call",
        trace_id=trace_id,
        status="success",
        tool_name="chora:assemble_artifact",
        duration_ms=1234
    )
```

**Query recent failures:**

```python
from mcp_n8n.memory import query_events

# Find backend failures in last 24 hours
failures = query_events(
    event_type="gateway.backend_failed",
    status="failure",
    since_hours=24
)

# Analyze patterns
for failure in failures:
    backend = failure["metadata"]["backend"]
    error = failure["metadata"]["error"]
    print(f"Backend {backend} failed: {error}")
```

**Trace workflow correlation:**

```python
from mcp_n8n.memory import EventLog

log = EventLog()

# Get all events for multi-step workflow
events = log.get_by_trace("abc123")

# Build timeline
for event in events:
    print(f"{event['timestamp']}: {event['event_type']} ({event['status']})")
```

### Knowledge Graph Usage

**Create learning notes:**

```python
from mcp_n8n.memory import KnowledgeGraph

kg = KnowledgeGraph()

# Create note from learned pattern
note_id = kg.create_note(
    title="Backend Timeout Fix",
    content="""
## Problem
Backend subprocess fails to start within 30s timeout.

## Solution
Increase MCP_N8N_BACKEND_TIMEOUT=60

## Evidence
- Trace abc123: Backend started at 45s (would have failed)
- Trace def456: Backend started at 52s (would have failed)
    """,
    tags=["troubleshooting", "backend", "timeout"],
    confidence="high"
)
```

**Search knowledge:**

```python
# Find notes by tag
notes = kg.search(tags=["backend", "timeout"])

# Find notes by content
notes = kg.search(text="subprocess")

# Get related notes
related = kg.get_related("backend-timeout-fix", max_distance=2)
```

**Update knowledge:**

```python
# Add new findings to existing note
kg.update_note(
    "backend-timeout-fix",
    content_append="## Update\nAlso affects Chora Composer backend.",
    tags_add=["chora-composer"],
    links_add=["chora-composer-troubleshooting"]
)
```

### Trace Context Propagation

**CHORA_TRACE_ID environment variable:**

```python
# Gateway generates trace ID for each tool call
with TraceContext() as trace_id:
    # Trace ID automatically propagates to subprocesses
    subprocess.run(
        ["chora-compose", "generate-content"],
        env={"CHORA_TRACE_ID": trace_id}
    )

# Backend reads trace ID
trace_id = os.getenv("CHORA_TRACE_ID", generate_uuid())
emit_event("chora.content_generated", trace_id=trace_id)
```

**Workflow correlation:**

All events with the same `trace_id` represent a multi-step workflow:

```
trace_id=abc123:
  1. gateway.tool_call (chora:generate_content) → 100ms
  2. chora.content_generated (status=success) → 500ms
  3. gateway.tool_call (chora:assemble_artifact) → 120ms
  4. chora.artifact_assembled (status=success) → 1200ms

Total workflow: 1920ms
```

### Agent Self-Improvement Patterns

**Pattern 1: Learn from Failures**

```python
# Query recent failures
failures = query_events(
    event_type="gateway.backend_failed",
    status="failure",
    since_days=7
)

# Group by error type
error_types = {}
for failure in failures:
    error = failure["metadata"]["error"]
    error_types[error] = error_types.get(error, 0) + 1

# Create knowledge note for common errors
for error, count in error_types.items():
    if count >= 3:  # Recurring error
        kg.create_note(
            title=f"Recurring Error: {error}",
            content=f"Occurred {count} times in last 7 days...",
            tags=["error", "recurring"],
            confidence="high"
        )
```

**Pattern 2: Replicate Success**

```python
# Find successful artifact workflows
successful = query_events(
    event_type="chora.artifact_assembled",
    status="success",
    since_days=30
)

# Analyze common patterns
log = EventLog()
patterns = []
for event in successful[:10]:  # Analyze top 10
    trace_events = log.get_by_trace(event["trace_id"])
    patterns.append(extract_workflow_pattern(trace_events))

# Store as knowledge
kg.create_note(
    title="Successful Artifact Patterns",
    content=summarize_patterns(patterns),
    tags=["best-practices", "artifact"],
    confidence="high"
)
```

**Pattern 3: Context Switch Support**

```python
# Prepare handoff to chora-composer
handoff_context = {
    "from_agent": "claude-code-mcp-n8n",
    "to_project": "chora-composer",
    "trace_id": generate_trace_id(),
    "pending_tasks": get_pending_tasks(),
    "recent_failures": query_events(status="failure", since_hours=24),
    "knowledge_updates": kg.search(tags=["recent-learning"])
}

# Emit handoff event
emit_event(
    "gateway.context_switch",
    trace_id=handoff_context["trace_id"],
    status="pending",
    **handoff_context
)
```

### Memory Retention Policy

**Event Log:**
- Daily events: 90 days
- Trace details: 30 days
- Failure events: 180 days (for learning)

**Knowledge Notes:**
- Never deleted (cumulative learning)
- Confidence tracked (low/medium/high)
- Deprecated notes marked, not deleted

**Privacy:**
- No API keys, tokens, credentials logged
- No PII (personally identifiable information)
- Only operation metadata, performance metrics

### CLI Tools for Agents (Phase 4.6)

**Query events via bash:**

```bash
# Find recent failures
chora-memory query --type "gateway.backend_failed" --status failure --since "24h"

# Get all events from last 7 days
chora-memory query --since "7d" --limit 100

# Get events as JSON for processing
chora-memory query --type "gateway.started" --json
```

**Get trace timeline:**

```bash
# Show workflow timeline
chora-memory trace abc123

# Get trace as JSON
chora-memory trace abc123 --json
```

**Search and manage knowledge:**

```bash
# Find notes about backend troubleshooting
chora-memory knowledge search --tag backend --tag troubleshooting

# Search for timeout issues
chora-memory knowledge search --text timeout

# Create knowledge note
echo "Fix: Increase timeout to 60s" | chora-memory knowledge create "Backend Timeout Fix" --tag troubleshooting --tag backend --confidence high

# Show note details
chora-memory knowledge show backend-timeout-fix
```

**View statistics:**

```bash
# Stats for last 7 days
chora-memory stats

# Stats for last 24 hours with JSON output
chora-memory stats --since 24h --json
```

**Manage agent profiles:**

```bash
# Show agent profile
chora-memory profile show claude-code

# List all profiles
chora-memory profile list
```

**Installation:** CLI tools automatically available after `pip install mcp-n8n`

### Integration with Single-Developer Multi-Instance Workflow

Memory system supports context switching between mcp-n8n and chora-composer:

1. **Session start** - Agent reads knowledge notes for recent learnings
2. **During work** - Agent emits events for all operations
3. **Before handoff** - Agent creates summary knowledge note
4. **Context switch** - Handoff event emitted with trace_id
5. **Resume session** - Agent queries events since last session

See [.chora/memory/README.md](.chora/memory/README.md) for complete memory architecture documentation.

---

## Related Resources

- **Repository:** https://github.com/yourusername/mcp-n8n
- **Chora Composer:** [chora-composer/README.md](chora-composer/README.md) | [chora-composer/AGENTS.md](chora-composer/AGENTS.md)
- **Coda MCP:** Optional backend (see Coda MCP documentation)
- **Unified Roadmap:** [docs/UNIFIED_ROADMAP.md](docs/UNIFIED_ROADMAP.md)
- **Ecosystem Intent:** [docs/ecosystem/ecosystem-intent.md](docs/ecosystem/ecosystem-intent.md)
- **Development Lifecycle:** [docs/process/development-lifecycle.md](docs/process/development-lifecycle.md)
- **MCP Specification:** https://modelcontextprotocol.io/

---

**Version:** 0.1.0
**Last Updated:** 2025-01
**Format:** AGENTS.md standard (OpenAI/Google/Sourcegraph)
**Part of:** Chora Ecosystem - Phase 4.5 (LLM-Intelligent Developer Experience)
