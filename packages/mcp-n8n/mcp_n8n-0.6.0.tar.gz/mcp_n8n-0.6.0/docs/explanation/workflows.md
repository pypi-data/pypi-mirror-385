---
title: "Understanding Workflows"
type: explanation
audience: intermediate
category: concepts
source: "src/mcp_n8n/workflows/daily_report.py, src/mcp_n8n/workflows/event_router.py"
last_updated: 2025-10-21
---

# Understanding Workflows

## Overview

Workflows in mcp-n8n are **multi-step automation processes** that coordinate operations across backends, query telemetry, and produce artifacts. They enable repeatable, testable, and observable business logic.

**The core idea:** Instead of writing ad-hoc scripts for every automation task, define structured workflows with clear inputs, outputs, and error handling—making them reusable, testable, and maintainable.

## Context

### Background: The Automation Problem

As the gateway evolves, common patterns emerge:
- Generate daily/weekly reports from multiple data sources
- Respond to specific events with predefined actions
- Coordinate multi-step artifact creation
- Monitor system health and trigger alerts

**The problem with ad-hoc scripts:**
- Every team member writes their own version
- No consistent error handling
- Hard to test and validate
- No telemetry or traceability
- Difficult to modify and maintain

### The Workflow Approach

Workflows solve this by:
1. **Standardizing structure** - All workflows follow same pattern (inputs → processing → outputs)
2. **Enabling testability** - Workflows are pure functions (same inputs → same outputs)
3. **Providing observability** - Automatic trace correlation and event emission
4. **Supporting reuse** - Workflows are functions that can be called from multiple contexts

### Alternatives Considered

**1. Custom Scripts**
- ❌ No standardization
- ❌ Hard to test
- ❌ No telemetry
- ✅ Fastest to write initially

**2. External Orchestrator (n8n, Airflow)**
- ❌ Additional infrastructure to deploy
- ❌ Learning curve for new platform
- ✅ Visual workflow builder
- ✅ Rich integration ecosystem

**3. Python Workflow Functions (Chosen)**
- ✅ Standardized structure
- ✅ Type-safe and testable
- ✅ Integrated with gateway telemetry
- ✅ Version-controlled as code
- ⚠️ Requires Python knowledge

**Future:** Hybrid approach using Pattern N3 (n8n as MCP Client) for visual workflows while keeping core logic in Python.

---

## The Solution

### Workflow Types

mcp-n8n supports three types of workflows:

```
┌─────────────────────────────────────────────────────────┐
│                   Workflow Types                        │
│                                                          │
│  1. Scheduled Workflows                                 │
│     - Run on a timer (cron-like)                        │
│     - Example: Daily reports, weekly summaries          │
│                                                          │
│  2. Event-Driven Workflows                              │
│     - Triggered by events (gateway, backend, external)  │
│     - Example: Error alerts, PR automation              │
│                                                          │
│  3. On-Demand Workflows                                 │
│     - Invoked manually or by AI agents                  │
│     - Example: Custom reports, data exports             │
└─────────────────────────────────────────────────────────┘
```

All workflows share common patterns:
- **Trace Context:** Automatic correlation of all events
- **Error Handling:** Structured exception handling with telemetry
- **Result Objects:** Type-safe return values
- **Testability:** Pure functions with mocked dependencies

---

### Pattern 1: Scheduled Workflows

**Intent:** Execute workflows automatically on a recurring schedule (daily, weekly, monthly).

**Use Cases:**
- Daily engineering reports
- Weekly sprint summaries
- Monthly analytics dashboards
- Periodic health checks

**Example: Daily Report Workflow**

**Purpose:** Aggregate git commits and gateway telemetry from last 24 hours into a formatted markdown report.

**Architecture:**
```
┌───────────────────────────────────────────────────────┐
│          Daily Report Workflow                        │
│                                                        │
│  Inputs:                                              │
│   - repo_path: str (git repository location)         │
│   - since_hours: int (lookback window, default 24)   │
│   - backend_registry: BackendRegistry                │
│   - event_log: EventLog                              │
│                                                        │
│  ┌─────────────────────────────────────────────────┐ │
│  │ Step 1: Query Git Commits                       │ │
│  │  - Run git log --since="24h"                    │ │
│  │  - Parse commit hash, author, message, stats    │ │
│  │  - Return list of CommitInfo dicts              │ │
│  └─────────────────────────────────────────────────┘ │
│                      ↓                                 │
│  ┌─────────────────────────────────────────────────┐ │
│  │ Step 2: Query Gateway Events                    │ │
│  │  - EventLog.query(since=24h)                    │ │
│  │  - Filter by event types, status                │ │
│  │  - Count successes, failures                    │ │
│  └─────────────────────────────────────────────────┘ │
│                      ↓                                 │
│  ┌─────────────────────────────────────────────────┐ │
│  │ Step 3: Aggregate Statistics                    │ │
│  │  - Tool usage counts                            │ │
│  │  - Success rates by backend                     │ │
│  │  - Average duration per tool                    │ │
│  └─────────────────────────────────────────────────┘ │
│                      ↓                                 │
│  ┌─────────────────────────────────────────────────┐ │
│  │ Step 4: Generate Report                         │ │
│  │  - Call chora:generate_content (template)       │ │
│  │  - Format as markdown                           │ │
│  │  - Include commits, stats, trends               │ │
│  └─────────────────────────────────────────────────┘ │
│                      ↓                                 │
│  Outputs:                                             │
│   - content: str (markdown report)                   │
│   - commit_count: int                                │
│   - event_count: int                                 │
│   - statistics: dict (aggregated metrics)            │
│   - metadata: dict (timestamps, sources)             │
└───────────────────────────────────────────────────────┘
```

**Code Structure:**

```python
async def run_daily_report(
    backend_registry: BackendRegistry,
    event_log: EventLog,
    repo_path: str = ".",
    since_hours: int = 24
) -> DailyReportResult:
    """Generate daily engineering report.

    Returns:
        DailyReportResult with content, counts, and statistics
    """
    with TraceContext() as trace_id:
        emit_event("workflow.started", trace_id=trace_id,
                   workflow_name="daily_report")

        try:
            # Step 1: Get commits
            commits = await get_recent_commits(repo_path, since_hours)

            # Step 2: Query events
            since_time = datetime.now(UTC) - timedelta(hours=since_hours)
            events = event_log.query(since=since_time)

            # Step 3: Aggregate statistics
            stats = event_log.aggregate(
                group_by="event_type",
                metric="count",
                since=since_time
            )

            # Step 4: Generate report
            content = await generate_report(commits, events, stats)

            emit_event("workflow.completed", trace_id=trace_id,
                       result={"commit_count": len(commits)})

            return DailyReportResult(
                content=content,
                commit_count=len(commits),
                event_count=len(events),
                statistics=stats,
                metadata={"generated_at": datetime.now(UTC).isoformat()}
            )

        except Exception as e:
            emit_event("workflow.failed", trace_id=trace_id, error=str(e))
            raise
```

**Scheduling:**

```python
# Via cron
# 0 9 * * * cd /project && python -m mcp_n8n.workflows.daily_report

# Via Python scheduler
import schedule
import asyncio

async def job():
    result = await run_daily_report(registry, event_log)
    print(f"Report generated: {result.commit_count} commits")

schedule.every().day.at("09:00").do(lambda: asyncio.run(job()))

while True:
    schedule.run_pending()
    time.sleep(60)
```

**Benefits:**
- ✅ Consistent report format
- ✅ Automated execution (no manual effort)
- ✅ Full trace history in event log
- ✅ Testable with mocked git/event log

**Limitations:**
- ⚠️ Requires scheduler infrastructure (cron or similar)
- ⚠️ Fixed schedule (not event-driven)
- ⚠️ Report format hardcoded in template

---

### Pattern 2: Event-Driven Workflows

**Intent:** React to specific events by automatically triggering workflows, enabling real-time automation.

**Use Cases:**
- Error alerts when tool calls fail
- PR automation when code is merged
- Documentation updates when specs change
- Health checks when backends restart

**Example: EventWorkflowRouter**

**Purpose:** Route incoming events to appropriate workflows based on YAML-defined patterns.

**Architecture:**
```
┌───────────────────────────────────────────────────────┐
│          EventWorkflowRouter                          │
│                                                        │
│  Config: config/event_mappings.yaml                   │
│  ┌─────────────────────────────────────────────────┐ │
│  │ mappings:                                        │ │
│  │   - event_pattern:                               │ │
│  │       type: "gateway.tool_call"                  │ │
│  │       status: "failure"                          │ │
│  │     workflow:                                    │ │
│  │       id: "error-alert-workflow"                 │ │
│  │       namespace: "n8n"                           │ │
│  │       parameters:                                │ │
│  │         error: "{{ event.metadata.error }}"      │ │
│  │         tool: "{{ event.metadata.tool_name }}"   │ │
│  └─────────────────────────────────────────────────┘ │
│                                                        │
│  Process:                                             │
│  1. Event arrives (from EventLog, webhook, etc.)     │
│  2. Router loads mappings from YAML                  │
│  3. Router matches event against patterns            │
│  4. Router templates workflow parameters (Jinja2)    │
│  5. Router triggers workflow via backend registry    │
│  6. Workflow executes and returns result             │
└───────────────────────────────────────────────────────┘
```

**Pattern Matching:**

Events match patterns when all fields in the pattern exist in the event with the same values:

```yaml
# Pattern
event_pattern:
  type: "gateway.tool_call"
  status: "failure"

# Matches this event:
{
  "timestamp": "2025-10-21T10:00:00Z",
  "type": "gateway.tool_call",
  "status": "failure",
  "metadata": {
    "tool_name": "chora:assemble_artifact",
    "error": "Timeout after 30s"
  }
}

# Does NOT match (status is "success"):
{
  "type": "gateway.tool_call",
  "status": "success",
  "metadata": {...}
}
```

**Parameter Templating:**

Workflow parameters support Jinja2 syntax for extracting event data:

```yaml
workflow:
  id: "error-alert-workflow"
  parameters:
    error_message: "{{ event.metadata.error }}"
    tool_name: "{{ event.metadata.tool_name }}"
    timestamp: "{{ event.timestamp }}"
    backend: "{{ event.metadata.backend }}"
```

**Hot-Reload:**

The router uses file watching (watchdog) to automatically reload config when the YAML file changes:

```python
router = EventWorkflowRouter(
    config_path="config/event_mappings.yaml",
    backend_registry=registry
)

# Load initial config
await router.load_mappings()

# Start file watcher for hot-reload
await router.start_watching()

# Config changes automatically picked up (no restart required)
```

**Code Structure:**

```python
class EventWorkflowRouter:
    """Routes events to workflows based on YAML config."""

    async def route_event(self, event: dict[str, Any]) -> dict[str, Any] | None:
        """Route event to workflow if pattern matches.

        Returns:
            Workflow result if matched and executed, None if no match
        """
        for mapping in self.mappings:
            pattern = mapping["event_pattern"]

            if self._matches_pattern(event, pattern):
                workflow_config = mapping["workflow"]

                # Template parameters
                params = self._template_parameters(
                    workflow_config.get("parameters", {}),
                    event
                )

                # Trigger workflow
                result = await self._trigger_workflow(
                    workflow_id=workflow_config["id"],
                    namespace=workflow_config.get("namespace"),
                    parameters=params
                )

                return result

        return None  # No pattern matched
```

**Usage:**

```python
# Initialize router
router = EventWorkflowRouter(
    config_path="config/event_mappings.yaml",
    backend_registry=registry
)

# Route incoming event
event = {
    "type": "gateway.tool_call",
    "status": "failure",
    "metadata": {
        "tool_name": "chora:assemble_artifact",
        "error": "Timeout after 30s"
    }
}

result = await router.route_event(event)
# Triggers "error-alert-workflow" with templated parameters
```

**Benefits:**
- ✅ Real-time automation (no polling)
- ✅ Declarative config (YAML vs code)
- ✅ Hot-reload (no restart needed)
- ✅ Flexible pattern matching
- ✅ Jinja2 templating for parameters

**Limitations:**
- ⚠️ First-match-wins (order matters in config)
- ⚠️ Pattern must be exact (no regex/wildcards yet)
- ⚠️ Debugging requires checking YAML + event structure

---

### Pattern 3: On-Demand Workflows

**Intent:** Execute workflows manually or via AI agent invocation when needed.

**Use Cases:**
- Custom reports with user-specified parameters
- Data exports for specific time ranges
- One-off maintenance tasks
- AI-initiated multi-step operations

**Example: AI-Invoked Report**

```python
# Workflow callable directly or via MCP tool
async def run_custom_report(
    backend_registry: BackendRegistry,
    event_log: EventLog,
    start_date: str,
    end_date: str,
    include_metrics: list[str]
) -> dict[str, Any]:
    """Generate custom report for specified date range."""

    with TraceContext() as trace_id:
        emit_event("workflow.started", trace_id=trace_id,
                   workflow_name="custom_report")

        # Parse dates
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        # Query events in range
        events = event_log.query(since=start, until=end)

        # Filter by requested metrics
        filtered = [
            e for e in events
            if any(metric in e.get("metadata", {}) for metric in include_metrics)
        ]

        # Generate report
        content = await generate_custom_report(filtered, include_metrics)

        emit_event("workflow.completed", trace_id=trace_id)

        return {
            "content": content,
            "event_count": len(filtered),
            "date_range": f"{start_date} to {end_date}"
        }
```

**Invocation via AI:**

```
User: "Generate a report of all failed tool calls from October 15-20"

Claude (via MCP):
  tools/call("custom:run_custom_report", {
    start_date: "2025-10-15",
    end_date: "2025-10-20",
    include_metrics: ["tool_call_failed"]
  })

Result: "Here's your report covering 5 days with 12 failed calls..."
```

**Benefits:**
- ✅ Flexible parameters (user/AI-specified)
- ✅ Can be exposed as MCP tools
- ✅ No scheduling infrastructure needed
- ✅ Ideal for exploratory analysis

**Limitations:**
- ⚠️ Requires manual invocation (not automated)
- ⚠️ Parameters must be validated carefully
- ⚠️ No retry logic by default

---

## Workflow Design Principles

### 1. Trace Context Everywhere

**Principle:** All workflows use `TraceContext` to enable correlation across events.

```python
with TraceContext() as trace_id:
    emit_event("workflow.started", trace_id=trace_id)
    # All operations automatically tagged with trace_id
    emit_event("workflow.completed", trace_id=trace_id)
```

**Why:** Enables debugging multi-step workflows by querying `event_log.get_by_trace(trace_id)`.

### 2. Structured Results

**Principle:** Workflows return type-safe result objects, not dicts.

```python
@dataclass
class DailyReportResult:
    content: str
    commit_count: int
    event_count: int
    statistics: dict[str, Any]
    metadata: dict[str, Any]

# Type-safe access
result = await run_daily_report(...)
print(result.commit_count)  # IDE autocomplete works
```

**Why:** Catches errors at development time, not runtime.

### 3. Dependency Injection

**Principle:** Workflows accept dependencies as parameters, not globals.

```python
# Good: Dependencies injected
async def run_daily_report(
    backend_registry: BackendRegistry,  # Injected
    event_log: EventLog,               # Injected
    repo_path: str = "."
) -> DailyReportResult:
    ...

# Bad: Global dependencies
GLOBAL_REGISTRY = BackendRegistry()

async def run_daily_report(repo_path: str = "."):
    result = GLOBAL_REGISTRY.call(...)  # Hard to test
```

**Why:** Enables testing with mocked dependencies.

### 4. Error Telemetry

**Principle:** Always emit `workflow.failed` event on exceptions.

```python
try:
    result = await execute_workflow()
    emit_event("workflow.completed", trace_id=trace_id, result=result)
    return result
except Exception as e:
    emit_event("workflow.failed", trace_id=trace_id, error=str(e))
    raise  # Re-raise for caller to handle
```

**Why:** Ensures all failures captured in event log for debugging.

---

## Benefits

**For Developers:**
- ✅ **Reusable logic:** Workflows are functions that can be called from multiple contexts
- ✅ **Testable:** Pure functions with dependency injection enable unit testing
- ✅ **Maintainable:** Clear structure and type safety reduce bugs
- ✅ **Traceable:** Automatic correlation of all operations

**For Operations:**
- ✅ **Observable:** All workflow executions logged to event log
- ✅ **Debuggable:** Trace IDs enable root cause analysis
- ✅ **Auditable:** Complete history of when workflows ran and with what parameters

**For AI Agents:**
- ✅ **Invocable:** Workflows can be exposed as MCP tools
- ✅ **Discoverable:** Type hints and docstrings enable self-documentation
- ✅ **Composable:** Workflows can call other workflows

---

## Limitations

- ⚠️ **Python-only:** Workflows must be written in Python (vs. visual workflow builders)
- ❌ **No built-in retry:** Developers must implement retry logic manually
- ⚠️ **Synchronous by default:** Async workflows require `asyncio` knowledge
- ⚠️ **No workflow engine:** No centralized scheduler/orchestrator (must use cron or similar)

**Future:** Integration with n8n (Pattern N3) will enable visual workflow design while keeping Python for core logic.

---

## Further Reading

**Internal Documentation:**
- [Tutorial: First Workflow](../tutorials/first-workflow.md) - Build daily report workflow
- [Tutorial: Event-Driven Workflow](../tutorials/event-driven-workflow.md) - Build EventWorkflowRouter
- [How-To: Build Custom Workflow](../how-to/build-custom-workflow.md) - Workflow templates and patterns
- [Explanation: Memory System](memory-system.md) - EventLog and trace correlation

**External Resources:**
- [AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html) - Python async programming
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) - Template syntax for parameters
- [n8n Documentation](https://docs.n8n.io/) - Visual workflow platform (future integration)

---

## History

**Evolution of workflows in mcp-n8n:**

- **v0.1.0 (Sprint 1-3):** No structured workflows
  - Ad-hoc scripts for automation
  - No standardization or telemetry

- **v0.4.0 (Sprint 4):** Memory system foundation
  - EventLog enables workflow telemetry
  - TraceContext enables correlation

- **v0.5.0 (Sprint 5):** Production workflows introduced
  - Daily Report workflow (`run_daily_report`)
  - EventWorkflowRouter (event-driven automation)
  - YAML-based event mapping
  - Hot-reload support with watchdog
  - 49 unit tests covering core functionality

- **Future (Sprint 6+):** Enhanced workflow capabilities
  - n8n integration (Pattern N3)
  - Workflow versioning and deployment
  - Retry logic and circuit breakers
  - Parallel execution support

---

**Source:** [src/mcp_n8n/workflows/daily_report.py](../../src/mcp_n8n/workflows/daily_report.py), [src/mcp_n8n/workflows/event_router.py](../../src/mcp_n8n/workflows/event_router.py)
**Last Updated:** 2025-10-21
