---
title: "How to Query Events"
type: how-to
audience: intermediate
category: workflows
tags: [events, telemetry, debugging, monitoring]
source: "src/mcp_n8n/memory/event_log.py, src/mcp_n8n/tools/event_query.py, src/mcp_n8n/cli/commands.py"
last_updated: 2025-10-21
---

# How to Query Events

## Problem

You need to query, filter, and analyze telemetry events from the mcp-n8n gateway for debugging, monitoring, or workflow development.

**Common scenarios:**
- Debug a failed workflow by viewing all events in its trace
- Find recent errors to identify system issues
- Analyze tool usage patterns over time
- Correlate events across gateway and backend boundaries
- Monitor system health metrics

## Solution Overview

mcp-n8n provides three ways to query events:
1. **MCP Tool** (`get_events`) - From Claude Desktop or other MCP clients
2. **CLI** (`chora-memory`) - From terminal for quick queries
3. **Python API** (`EventLog`) - Programmatic access in custom workflows

## Prerequisites

- [ ] mcp-n8n gateway installed and configured
- [ ] Events exist in `.chora/memory/events/` (gateway has run)
- [ ] For CLI approach: `chora-memory` command available

---

## Approach 1: Via MCP Tool (Recommended for Claude Desktop)

**When to use:** Querying events from within Claude Desktop or Cursor

**Pros:**
- ✅ No terminal required - works in chat interface
- ✅ Results displayed in readable format
- ✅ Works anywhere the gateway is configured

**Cons:**
- ❌ Limited to MCP client features
- ❌ Can't pipe results to other tools

### Steps

1. **Ensure gateway is running:**
   ```bash
   mcp-n8n
   ```

2. **Ask Claude to query events:**
   In Claude Desktop, type a natural language request like:

   > "Show me all failed events from the last hour"

   Claude will translate this to an MCP tool call:
   ```json
   {
     "tool": "get_events",
     "arguments": {
       "status": "failure",
       "since": "1h",
       "limit": 100
     }
   }
   ```

3. **Review the results:**
   Claude will display events in a readable format showing:
   - Timestamp
   - Event type
   - Status
   - Metadata (error details, tool names, etc.)

### Common Queries

**Get all events for a specific trace:**
> "Show me all events for trace ID abc123xyz"

**Find recent failures:**
> "What failures happened in the last 24 hours?"

**Tool usage analysis:**
> "Show me all gateway.tool_call events from today"

**Backend registration events:**
> "Show me when backends were registered"

### Verification

Check that events are returned:
- Events should be chronologically ordered
- Each event includes timestamp, event_type, status, metadata
- Limit (max 1000) is respected

---

## Approach 2: Via CLI (Best for Terminal Workflows)

**When to use:** Quick terminal queries, scripting, integration with other CLI tools

**Pros:**
- ✅ Fast and scriptable
- ✅ JSON output for piping to `jq`, `grep`, etc.
- ✅ Works without gateway running

**Cons:**
- ❌ Requires terminal access
- ❌ Less discoverable than MCP tool

### Steps

1. **Query recent events:**
   ```bash
   chora-memory query --since 24h
   ```

   **Expected output:**
   ```
   Found 42 events:

   [2025-10-21T14:32:10.123456+00:00] ✓ gateway.started (success)
     version: 0.4.0
     backend_count: 2

   [2025-10-21T14:32:11.234567+00:00] ✓ gateway.backend_registered (success)
     backend_name: chora-composer
     namespace: chora
   ```

2. **Filter by event type:**
   ```bash
   chora-memory query --type gateway.tool_call --since 1h
   ```

3. **Filter by status:**
   ```bash
   chora-memory query --status failure --since 7d
   ```

4. **Limit results:**
   ```bash
   chora-memory query --since 24h --limit 10
   ```

5. **Get JSON output for processing:**
   ```bash
   chora-memory query --type gateway.backend_started --json | jq '.[] | .metadata.backend_name'
   ```

   **Expected output:**
   ```
   "chora-composer"
   "coda-mcp"
   ```

### Trace-Specific Queries

**Show complete trace timeline:**
```bash
chora-memory trace 550e8400-e29b-41d4-a716-446655440000
```

**Expected output:**
```
Trace Timeline: 550e8400-e29b-41d4-a716-446655440000

Total events: 5

Duration: 1234ms

1. [2025-10-21T14:32:10+00:00] ⋯ workflow.started (pending)
  workflow_name: daily_report

2. [2025-10-21T14:32:10+00:00] ✓ gateway.tool_call (success)
  tool_name: chora:generate_content
  duration_ms: 450

3. [2025-10-21T14:32:11+00:00] ✓ gateway.tool_call (success)
  tool_name: get_events
  duration_ms: 120

4. [2025-10-21T14:32:11+00:00] ✓ workflow.completed (success)
  duration_ms: 1234
```

**Get trace as JSON:**
```bash
chora-memory trace abc123 --json
```

### Verification

Test the CLI is working:
```bash
chora-memory query --since 1h --limit 1
```

Expected: At least one event displayed (if gateway has run recently)

---

## Approach 3: Via Python API (For Custom Workflows)

**When to use:** Building custom workflows, advanced analytics, programmatic event processing

**Pros:**
- ✅ Full programmatic control
- ✅ Can integrate with workflow logic
- ✅ Supports complex filtering and aggregation

**Cons:**
- ❌ Requires Python coding
- ❌ More verbose than CLI/MCP approaches

### Steps

1. **Import EventLog:**
   ```python
   from mcp_n8n.memory import EventLog
   from datetime import datetime, timedelta, UTC
   ```

2. **Initialize EventLog:**
   ```python
   log = EventLog()
   ```

3. **Query events with filters:**
   ```python
   # Get events from last 24 hours
   since_time = datetime.now(UTC) - timedelta(hours=24)

   events = log.query(
       event_type="gateway.tool_call",
       status="success",
       since=since_time,
       limit=100
   )

   print(f"Found {len(events)} tool calls")
   for event in events:
       print(f"  {event['timestamp']}: {event['metadata'].get('tool_name')}")
   ```

4. **Get all events for a trace:**
   ```python
   trace_id = "550e8400-e29b-41d4-a716-446655440000"
   trace_events = log.get_by_trace(trace_id)

   print(f"Trace has {len(trace_events)} events")
   ```

5. **Aggregate statistics:**
   ```python
   # Count events by type in last 7 days
   since_time = datetime.now(UTC) - timedelta(days=7)

   stats = log.aggregate(
       group_by="event_type",
       metric="count",
       since=since_time
   )

   print("Events by type (last 7 days):")
   for event_type, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
       print(f"  {event_type}: {count}")
   ```

### Full Example: Workflow Event Analysis

```python
from mcp_n8n.memory import EventLog
from datetime import datetime, timedelta, UTC

def analyze_workflow_performance(workflow_name: str, days: int = 7) -> dict:
    """Analyze workflow performance metrics.

    Args:
        workflow_name: Name of the workflow (e.g., "daily_report")
        days: Number of days to analyze

    Returns:
        Performance metrics dictionary
    """
    log = EventLog()
    since = datetime.now(UTC) - timedelta(days=days)

    # Get all workflow events
    started_events = log.query(
        event_type=f"workflow.started",
        since=since
    )

    completed_events = log.query(
        event_type=f"workflow.completed",
        since=since
    )

    failed_events = log.query(
        event_type=f"workflow.failed",
        since=since
    )

    # Calculate metrics
    total_runs = len(started_events)
    successful_runs = len(completed_events)
    failed_runs = len(failed_events)
    success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0

    # Calculate average duration (from metadata)
    durations = [
        event.get("metadata", {}).get("duration_ms", 0)
        for event in completed_events
    ]
    avg_duration = sum(durations) / len(durations) if durations else 0

    return {
        "workflow": workflow_name,
        "period_days": days,
        "total_runs": total_runs,
        "successful": successful_runs,
        "failed": failed_runs,
        "success_rate": f"{success_rate:.1f}%",
        "avg_duration_ms": f"{avg_duration:.0f}"
    }

# Usage
metrics = analyze_workflow_performance("daily_report", days=7)
print(f"Workflow: {metrics['workflow']}")
print(f"Success Rate: {metrics['success_rate']}")
print(f"Avg Duration: {metrics['avg_duration_ms']}ms")
```

### Verification

Test the API:
```python
from mcp_n8n.memory import EventLog

log = EventLog()
events = log.query(limit=1)

assert len(events) <= 1, "Should return at most 1 event"
print(f"EventLog is working! Found {len(events)} event(s)")
```

---

## Common Filtering Patterns

### By Time Range

**Relative time:**
```bash
# Last hour
chora-memory query --since 1h

# Last 7 days
chora-memory query --since 7d

# Last 30 days
chora-memory query --since 30d
```

**Absolute time (ISO 8601):**
```bash
# From specific timestamp
chora-memory query --since "2025-10-21T00:00:00Z"
```

**Python API:**
```python
from datetime import datetime, timedelta, UTC

# Last 6 hours
since = datetime.now(UTC) - timedelta(hours=6)
events = log.query(since=since)

# Specific date
since = datetime(2025, 10, 21, tzinfo=UTC)
events = log.query(since=since)
```

---

### By Event Type

**Gateway events:**
```bash
# Gateway lifecycle
chora-memory query --type gateway.started
chora-memory query --type gateway.stopped

# Backend events
chora-memory query --type gateway.backend_registered
chora-memory query --type gateway.backend_started

# Tool calls
chora-memory query --type gateway.tool_call
```

**Workflow events:**
```bash
chora-memory query --type workflow.started
chora-memory query --type workflow.completed
chora-memory query --type workflow.failed
```

---

### By Status

**Find failures:**
```bash
# All failures in last 24 hours
chora-memory query --status failure --since 24h

# Failed tool calls
chora-memory query --type gateway.tool_call --status failure --since 7d
```

**Python API:**
```python
# Get all failures
failures = log.query(status="failure", since=since_time)

# Analyze failure patterns
for event in failures:
    error = event.get("metadata", {}).get("error", "Unknown")
    print(f"{event['event_type']}: {error}")
```

---

### Combining Filters

**MCP Tool:**
```json
{
  "tool": "get_events",
  "arguments": {
    "event_type": "gateway.tool_call",
    "status": "failure",
    "since": "24h",
    "limit": 50
  }
}
```

**CLI:**
```bash
chora-memory query \
  --type gateway.backend_started \
  --status success \
  --since 7d \
  --limit 10
```

**Python:**
```python
events = log.query(
    event_type="gateway.tool_call",
    status="failure",
    since=datetime.now(UTC) - timedelta(hours=24),
    limit=50
)
```

---

## Advanced Use Cases

### 1. Find Slow Tool Calls

```python
from mcp_n8n.memory import EventLog
from datetime import datetime, timedelta, UTC

log = EventLog()
since = datetime.now(UTC) - timedelta(days=7)

# Get all completed tool calls
tool_calls = log.query(
    event_type="gateway.tool_call",
    status="success",
    since=since
)

# Filter for slow calls (>5 seconds)
slow_calls = [
    event for event in tool_calls
    if event.get("metadata", {}).get("duration_ms", 0) > 5000
]

print(f"Found {len(slow_calls)} slow tool calls:")
for event in slow_calls:
    tool_name = event.get("metadata", {}).get("tool_name", "unknown")
    duration = event.get("metadata", {}).get("duration_ms", 0)
    print(f"  {tool_name}: {duration}ms")
```

---

### 2. Trace Correlation Across Services

```python
from mcp_n8n.memory import EventLog

def get_trace_timeline(trace_id: str) -> None:
    """Print complete timeline for a trace ID."""
    log = EventLog()
    events = log.get_by_trace(trace_id)

    if not events:
        print(f"No events found for trace: {trace_id}")
        return

    print(f"Trace: {trace_id}")
    print(f"Total events: {len(events)}\n")

    for i, event in enumerate(events, 1):
        timestamp = event["timestamp"]
        event_type = event["event_type"]
        status = event["status"]
        source = event.get("source", "unknown")

        print(f"{i}. [{timestamp}] {event_type} ({status})")
        print(f"   Source: {source}")

        # Print relevant metadata
        metadata = event.get("metadata", {})
        for key in ["tool_name", "backend_name", "error", "duration_ms"]:
            if key in metadata:
                print(f"   {key}: {metadata[key]}")
        print()

# Usage
get_trace_timeline("550e8400-e29b-41d4-a716-446655440000")
```

---

### 3. Daily Error Report

```bash
#!/bin/bash
# Script: daily_error_report.sh
# Generate daily error report

echo "=== Daily Error Report ==="
echo "Date: $(date)"
echo

echo "Failed Events (last 24 hours):"
chora-memory query --status failure --since 24h --limit 20

echo
echo "Failed Tool Calls:"
chora-memory query --type gateway.tool_call --status failure --since 24h

echo
echo "Failed Workflows:"
chora-memory query --type workflow.failed --since 24h
```

---

## Troubleshooting

### Problem: No events found

**Symptoms:**
```bash
$ chora-memory query --since 24h
No events found.
```

**Cause:** Gateway hasn't run or events directory doesn't exist

**Solution:**
```bash
# Check if events directory exists
ls -la .chora/memory/events/

# Run gateway to generate events
mcp-n8n

# Try again
chora-memory query --since 24h
```

---

### Problem: "EventLog not initialized" error

**Symptoms:**
```python
RuntimeError: EventLog not initialized. Call set_event_log() first.
```

**Cause:** Trying to use `get_events` MCP tool before gateway initialized EventLog

**Solution:** This error only occurs when calling the tool function directly. If using via MCP protocol, the gateway handles initialization automatically.

---

### Problem: Invalid time range format

**Symptoms:**
```bash
$ chora-memory query --since yesterday
Error: Invalid since format: yesterday. Use '24h', '7d', or '2025-01-17'
```

**Cause:** Unsupported time format

**Solution:** Use supported formats:
```bash
# Relative
chora-memory query --since 24h
chora-memory query --since 7d

# Absolute (ISO date)
chora-memory query --since "2025-10-21"
chora-memory query --since "2025-10-21T00:00:00Z"
```

---

### Problem: Too many events returned

**Symptoms:** Query returns thousands of events, overwhelming output

**Cause:** No filters or limit applied

**Solution:**
```bash
# Add limit
chora-memory query --since 30d --limit 50

# Add filters to narrow results
chora-memory query --type gateway.tool_call --status failure --since 7d
```

---

## Related Documentation

- [Event Schema Reference](../reference/event-schema.md) - Complete event structure
- [Tools Reference](../reference/tools.md#get_events) - get_events tool documentation
- [CLI Reference](../reference/cli-reference.md#chora-memory) - chora-memory CLI
- [Tutorial: Event-Driven Workflow](../tutorials/event-driven-workflow.md) - Using events in workflows

---

**Source:** [src/mcp_n8n/memory/event_log.py](../../src/mcp_n8n/memory/event_log.py), [src/mcp_n8n/tools/event_query.py](../../src/mcp_n8n/tools/event_query.py), [src/mcp_n8n/cli/commands.py](../../src/mcp_n8n/cli/commands.py)
**Last Updated:** 2025-10-21
