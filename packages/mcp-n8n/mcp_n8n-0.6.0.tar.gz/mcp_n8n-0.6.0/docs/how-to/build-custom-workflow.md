---
title: "How to Build a Custom Workflow"
type: how-to
audience: intermediate
category: workflows
tags: [workflows, development, integration]
source: "src/mcp_n8n/workflows/daily_report.py, src/mcp_n8n/workflows/event_router.py"
last_updated: 2025-10-21
---

# How to Build a Custom Workflow

## Problem

You need to create a custom workflow that automates tasks by orchestrating multiple tools, processing data, and generating outputs.

**Common scenarios:**
- Automated reporting workflows
- Data synchronization between systems
- Multi-step approval processes
- Event-driven automation
- Integration workflows

## Solution Overview

Three approaches to building workflows:
1. **Simple workflow** - Direct Python function (best for single-step tasks)
2. **Event-driven workflow** - Triggered by events (best for reactive automation)
3. **Multi-step workflow** - Orchestrates multiple tools (best for complex processes)

## Prerequisites

- [ ] mcp-n8n installed and gateway running
- [ ] Completed [First Workflow tutorial](../tutorials/first-workflow.md)
- [ ] Understanding of [Event Schema](../reference/event-schema.md)
- [ ] Python programming experience

---

## Approach 1: Simple Workflow (Direct Call)

**When to use:** Single-step tasks, manual triggers, simple automation

**Pros:**
- ✅ Easiest to implement
- ✅ Direct control flow
- ✅ No event dependencies

**Cons:**
- ❌ Manual triggering required
- ❌ No event integration

### Template

```python
import asyncio
from mcp_n8n.backends import BackendRegistry
from mcp_n8n.memory import EventLog, TraceContext, emit_event

async def my_simple_workflow(
    backend_registry: BackendRegistry,
    param1: str,
    param2: int = 10
) -> dict:
    """Simple workflow template.

    Args:
        backend_registry: Backend registry for tool calls
        param1: Required parameter
        param2: Optional parameter with default

    Returns:
        Result dictionary with status and data
    """
    # Start trace for event correlation
    with TraceContext() as trace_id:
        # Emit workflow started event
        emit_event(
            "workflow.started",
            trace_id=trace_id,
            workflow_name="my_simple_workflow",
            parameters={"param1": param1, "param2": param2}
        )

        try:
            # Your workflow logic here
            result_data = {
                "processed": param1.upper(),
                "count": param2
            }

            # Emit success event
            emit_event(
                "workflow.completed",
                trace_id=trace_id,
                workflow_name="my_simple_workflow",
                result=result_data
            )

            return {
                "status": "success",
                "data": result_data,
                "trace_id": trace_id
            }

        except Exception as e:
            # Emit failure event
            emit_event(
                "workflow.failed",
                trace_id=trace_id,
                workflow_name="my_simple_workflow",
                error=str(e)
            )

            return {
                "status": "failure",
                "error": str(e),
                "trace_id": trace_id
            }

# Usage
async def main():
    registry = BackendRegistry()
    result = await my_simple_workflow(registry, "test", 5)
    print(result)

asyncio.run(main())
```

### Example: Data Fetcher Workflow

```python
async def fetch_and_process_data(
    backend_registry: BackendRegistry,
    doc_id: str
) -> dict:
    """Fetch data from Coda and process it.

    Args:
        backend_registry: Backend registry
        doc_id: Coda document ID

    Returns:
        Processed data
    """
    with TraceContext() as trace_id:
        emit_event("workflow.started", trace_id=trace_id, workflow_name="fetch_and_process")

        try:
            # Get Coda backend
            coda_backend = backend_registry._namespace_map.get("coda")
            if not coda_backend:
                raise RuntimeError("Coda backend not available")

            # Call list_tables tool
            tables_result = await coda_backend.call_tool(
                "list_tables",
                {"doc_id": doc_id}
            )

            # Process results
            table_count = len(tables_result.get("tables", []))

            emit_event("workflow.completed", trace_id=trace_id, table_count=table_count)

            return {
                "status": "success",
                "table_count": table_count,
                "tables": tables_result.get("tables", [])
            }

        except Exception as e:
            emit_event("workflow.failed", trace_id=trace_id, error=str(e))
            return {"status": "failure", "error": str(e)}
```

---

## Approach 2: Event-Driven Workflow

**When to use:** Reactive automation, triggered by system events

**Pros:**
- ✅ Automatic triggering
- ✅ Decoupled from event source
- ✅ Scalable

**Cons:**
- ❌ Requires event mapping configuration
- ❌ More complex setup

### Steps

1. **Create workflow function:**
   ```python
   async def error_alert_workflow(
       backend_registry: BackendRegistry,
       event: dict,
       **parameters
   ) -> dict:
       """Workflow triggered by error events.

       Args:
           backend_registry: Backend registry
           event: Triggering event
           **parameters: Templated parameters from event mapping

       Returns:
           Workflow result
       """
       tool_name = parameters.get("tool")
       error_msg = parameters.get("error")

       print(f"ALERT: Tool {tool_name} failed: {error_msg}")

       # Send notification (pseudo-code)
       # await send_slack_message(f"Error in {tool_name}: {error_msg}")

       return {"status": "alert_sent", "tool": tool_name}
   ```

2. **Configure event mapping:**
   ```yaml
   # config/event_mappings.yaml
   mappings:
     - event_pattern:
         type: "gateway.tool_call"
         status: "failure"
       workflow:
         id: "error-alert-workflow"
         parameters:
           tool: "{{ event.metadata.tool_name }}"
           error: "{{ event.metadata.error }}"
   ```

3. **Register workflow with router:**
   ```python
   from mcp_n8n.workflows.event_router import EventWorkflowRouter

   async def setup_event_driven_workflows():
       registry = BackendRegistry()

       # Create router
       router = EventWorkflowRouter(
           config_path="config/event_mappings.yaml",
           backend_registry=registry
       )
       await router.load_mappings()

       # Router now automatically triggers workflows on matching events
       await router.start_watching()  # Enable hot-reload
   ```

### See Also

Complete example in [Event-Driven Workflow Tutorial](../tutorials/event-driven-workflow.md)

---

## Approach 3: Multi-Step Workflow

**When to use:** Complex processes, multiple tool orchestration

**Pros:**
- ✅ Handles complex logic
- ✅ Error handling per step
- ✅ Progress tracking

**Cons:**
- ❌ More code to maintain
- ❌ Longer execution time

### Template

```python
import asyncio
from typing import Any
from mcp_n8n.backends import BackendRegistry
from mcp_n8n.memory import EventLog, TraceContext, emit_event

async def multi_step_workflow(
    backend_registry: BackendRegistry,
    event_log: EventLog
) -> dict:
    """Multi-step workflow template.

    Steps:
    1. Fetch data from source
    2. Process/transform data
    3. Generate report
    4. Store result

    Returns:
        Workflow result with all step outputs
    """
    with TraceContext() as trace_id:
        emit_event("workflow.started", trace_id=trace_id, workflow_name="multi_step")

        results = {}

        try:
            # Step 1: Fetch data
            emit_event("workflow.step", trace_id=trace_id, step=1, name="fetch_data")
            data = await _fetch_data_step(backend_registry, trace_id)
            results["data"] = data

            # Step 2: Process data
            emit_event("workflow.step", trace_id=trace_id, step=2, name="process_data")
            processed = await _process_data_step(data, trace_id)
            results["processed"] = processed

            # Step 3: Generate report
            emit_event("workflow.step", trace_id=trace_id, step=3, name="generate_report")
            report = await _generate_report_step(backend_registry, processed, trace_id)
            results["report"] = report

            # Step 4: Store result
            emit_event("workflow.step", trace_id=trace_id, step=4, name="store_result")
            stored_path = await _store_result_step(report, trace_id)
            results["stored_path"] = stored_path

            # Success
            emit_event("workflow.completed", trace_id=trace_id, results=results)

            return {
                "status": "success",
                "trace_id": trace_id,
                **results
            }

        except Exception as e:
            emit_event("workflow.failed", trace_id=trace_id, error=str(e))
            return {
                "status": "failure",
                "error": str(e),
                "trace_id": trace_id,
                "partial_results": results
            }


# Step implementations
async def _fetch_data_step(registry: BackendRegistry, trace_id: str) -> dict:
    """Step 1: Fetch data from Coda."""
    coda = registry._namespace_map.get("coda")
    docs = await coda.call_tool("list_docs", {"limit": 10})
    return docs


async def _process_data_step(data: dict, trace_id: str) -> list:
    """Step 2: Process/transform data."""
    # Transform data
    processed = [
        {"name": doc.get("name"), "id": doc.get("id")}
        for doc in data.get("docs", [])
    ]
    return processed


async def _generate_report_step(
    registry: BackendRegistry,
    processed: list,
    trace_id: str
) -> str:
    """Step 3: Generate report using chora-compose."""
    chora = registry._namespace_map.get("chora")

    report = await chora.call_tool(
        "generate_content",
        {
            "generator_id": "report_template",
            "variables": {"items": processed}
        }
    )

    return report.get("content", "")


async def _store_result_step(report: str, trace_id: str) -> str:
    """Step 4: Store report to file."""
    from pathlib import Path
    from datetime import datetime

    path = Path(f"reports/workflow_{datetime.now().date()}.md")
    path.parent.mkdir(exist_ok=True)
    path.write_text(report)

    return str(path)
```

---

## Best Practices

### 1. Always Use TraceContext

**Why:** Enables event correlation across workflow execution

```python
# ✓ Good
with TraceContext() as trace_id:
    emit_event("workflow.started", trace_id=trace_id)
    # ... workflow logic
    emit_event("workflow.completed", trace_id=trace_id)

# ✗ Bad
emit_event("workflow.started")  # No trace correlation
```

### 2. Emit Events at Key Points

**What to track:**
- Workflow start/complete/failed
- Step boundaries
- Tool calls
- Errors

```python
# Start
emit_event("workflow.started", trace_id=trace_id, workflow_name="my_workflow")

# Steps
emit_event("workflow.step", trace_id=trace_id, step=1, name="fetch_data")

# Tool calls (automatic via TraceContext)

# Completion
emit_event("workflow.completed", trace_id=trace_id, duration_ms=1234)
```

### 3. Handle Errors Gracefully

```python
try:
    result = await risky_operation()
except TimeoutError as e:
    # Retry logic
    result = await risky_operation(timeout=60)
except ValueError as e:
    # Log and continue
    emit_event("workflow.warning", trace_id=trace_id, warning=str(e))
    result = default_value
except Exception as e:
    # Fatal error
    emit_event("workflow.failed", trace_id=trace_id, error=str(e))
    raise
```

### 4. Make Workflows Testable

```python
# ✓ Good - Dependencies injected
async def my_workflow(backend_registry: BackendRegistry, event_log: EventLog):
    pass

# ✗ Bad - Hard to test
async def my_workflow():
    backend_registry = BackendRegistry()  # Creates real backends
    event_log = EventLog()  # Writes to real files
```

---

## Workflow Patterns

### Pattern 1: Scheduled Report

```python
async def daily_summary_workflow():
    """Run daily at midnight via cron."""
    with TraceContext() as trace_id:
        # Fetch data from last 24 hours
        # Generate report
        # Email to team
        pass
```

**Cron:**
```bash
0 0 * * * cd /app && python -c "import asyncio; from workflows import daily_summary_workflow; asyncio.run(daily_summary_workflow())"
```

### Pattern 2: Webhook Trigger

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/trigger/workflow")
async def trigger_workflow(payload: dict):
    """HTTP endpoint to trigger workflow."""
    result = await my_workflow(payload)
    return result
```

### Pattern 3: Conditional Workflow

```python
async def conditional_workflow(data: dict):
    """Different paths based on data."""
    if data.get("type") == "urgent":
        return await urgent_workflow(data)
    elif data.get("type") == "standard":
        return await standard_workflow(data)
    else:
        return await default_workflow(data)
```

---

## Testing Workflows

### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_my_workflow():
    """Test workflow with mocked dependencies."""
    # Mock backend registry
    mock_registry = AsyncMock()
    mock_registry._namespace_map = {
        "coda": AsyncMock(call_tool=AsyncMock(return_value={"docs": []}))
    }

    # Run workflow
    result = await my_workflow(mock_registry)

    # Assertions
    assert result["status"] == "success"
    assert "data" in result
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_workflow_integration():
    """Test with real backends (requires credentials)."""
    registry = BackendRegistry()
    await registry.start_all()

    try:
        result = await my_workflow(registry)
        assert result["status"] == "success"
    finally:
        await registry.stop_all()
```

---

## Troubleshooting

### Problem: Workflow times out

**Solution:** Increase backend timeout or add retry logic

```python
# Option 1: Increase timeout
backend.config.timeout = 120

# Option 2: Retry with exponential backoff
for attempt in range(3):
    try:
        result = await tool_call()
        break
    except TimeoutError:
        await asyncio.sleep(2 ** attempt)  # 1s, 2s, 4s
```

### Problem: Events not correlated

**Solution:** Ensure TraceContext is used

```python
# Check trace_id is propagated
with TraceContext() as trace_id:
    print(f"Trace ID: {trace_id}")
    # All emitted events should have this trace_id
```

### Problem: Workflow fails silently

**Solution:** Add comprehensive error handling and logging

```python
import logging

logger = logging.getLogger(__name__)

try:
    result = await workflow()
except Exception as e:
    logger.error(f"Workflow failed: {e}", exc_info=True)
    emit_event("workflow.failed", error=str(e), stack_trace=traceback.format_exc())
    raise
```

---

## Related Documentation

- [Tutorial: First Workflow](../tutorials/first-workflow.md) - Basic workflow example
- [Tutorial: Event-Driven Workflow](../tutorials/event-driven-workflow.md) - Event routing
- [How-To: Query Events](query-events.md) - Monitor workflow execution
- [Reference: Event Schema](../reference/event-schema.md) - Event structure

---

**Source:** [src/mcp_n8n/workflows/daily_report.py](../../src/mcp_n8n/workflows/daily_report.py), [src/mcp_n8n/workflows/event_router.py](../../src/mcp_n8n/workflows/event_router.py)
**Last Updated:** 2025-10-21
