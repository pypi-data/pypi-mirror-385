# Tutorial: Event Monitoring with mcp-n8n

> **Learning Goal:** By the end of this tutorial, you'll understand how to monitor events from chora-compose in real-time and query them for debugging multi-step workflows.

## What You'll Build

By completing this tutorial, you'll have:
- A running EventWatcher that monitors chora-compose events
- Real-time event forwarding to n8n webhooks (optional)
- The ability to query events by trace_id for debugging
- A working example of trace_id propagation across gateway/backend boundaries

## Prerequisites

Before starting, ensure you have:
- [ ] mcp-n8n installed and configured
- [ ] chora-compose v1.3.0+ (with event emission support)
- [ ] Basic understanding of trace IDs and event correlation
- [ ] (Optional) n8n running locally for webhook testing

## Time Required

Approximately 20-30 minutes

---

## Part 1: Understanding Event Monitoring

### The Problem

When you call `chora:assemble_artifact` through mcp-n8n, several things happen:
1. The gateway receives your request
2. The gateway spawns a chora-compose subprocess
3. chora-compose generates content and assembles artifacts
4. chora-compose emits events to `var/telemetry/events.jsonl`

**Without event monitoring**, you can't:
- Track progress of long-running operations
- Debug failures in multi-step workflows
- React to completion events in n8n workflows

**With event monitoring**, you get:
- Real-time visibility into backend operations
- Event correlation via trace_id
- n8n webhook integration for event-driven workflows

### The Solution: EventWatcher

The `EventWatcher` class implements a **dual-consumption pattern**:
1. **Always** stores events in gateway telemetry (`.chora/memory/events/`)
2. **Optionally** forwards events to n8n webhook (fire-and-forget)

This gives you both historical querying and real-time reactions.

---

## Part 2: Basic Event Monitoring (Without Webhooks)

Let's start by monitoring events and storing them in the gateway's telemetry system.

### Step 1: Create EventWatcher

Create a Python script to test the EventWatcher:

**File:** `test_event_monitoring.py`

```python
import asyncio
from pathlib import Path
from mcp_n8n.event_watcher import EventWatcher
from mcp_n8n.memory.event_log import EventLog

async def main():
    # Initialize EventLog
    event_log = EventLog(base_dir=Path(".chora/memory/events"))

    # Create EventWatcher (no webhook)
    watcher = EventWatcher(
        event_log=event_log,
        events_file="var/telemetry/events.jsonl",
        n8n_webhook_url=None  # No webhook for now
    )

    print("Starting EventWatcher...")
    await watcher.start()

    # Keep running for 30 seconds
    print("Monitoring events for 30 seconds...")
    await asyncio.sleep(30)

    # Stop gracefully
    print("Stopping EventWatcher...")
    await watcher.stop()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
```

**Expected output:**
```
Starting EventWatcher...
Monitoring events for 30 seconds...
Stopping EventWatcher...
Done!
```

### Step 2: Generate Test Events

While the EventWatcher is running, generate some test events by calling chora-compose:

**In another terminal:**

```bash
# Generate a test event
echo '{"timestamp":"2025-10-19T10:00:00Z","trace_id":"test-001","status":"success","schema_version":"1.0","event_type":"chora.content_generated","metadata":{"generator":"test"}}' >> var/telemetry/events.jsonl
```

The EventWatcher will:
1. Detect the new event (within 50ms)
2. Store it in `.chora/memory/events/2025-10/events.jsonl`
3. Create a trace-specific file `.chora/memory/events/2025-10/traces/test-001.jsonl`

### Step 3: Query Events

After the EventWatcher has processed events, query them:

```python
from mcp_n8n.memory.event_log import EventLog

# Initialize EventLog
event_log = EventLog()

# Query all events for trace_id
events = event_log.get_by_trace("test-001")

print(f"Found {len(events)} events for trace test-001")
for event in events:
    print(f"  - {event['event_type']} at {event['timestamp']}")
```

**Expected output:**
```
Found 1 events for trace test-001
  - chora.content_generated at 2025-10-19T10:00:00Z
```

### Step 4: Verify Event Storage

Check that events are stored in the correct location:

```bash
# List monthly partitions
ls -la .chora/memory/events/

# View events for current month
cat .chora/memory/events/2025-10/events.jsonl

# View trace-specific file
cat .chora/memory/events/2025-10/traces/test-001.jsonl
```

**Success!** You've successfully monitored and stored events from chora-compose.

---

## Part 3: Event Monitoring with n8n Webhooks

Now let's add real-time event forwarding to n8n for event-driven workflows.

### Step 1: Create n8n Webhook

**In n8n (http://localhost:5678):**

1. Create a new workflow
2. Add a **Webhook** node with these settings:
   - HTTP Method: POST
   - Path: `chora-events`
   - Respond: Immediately

3. Add a **Function** node to display the event:
   ```javascript
   // Extract event details
   const event = $json;

   return {
     message: `Event received: ${event.event_type}`,
     trace_id: event.trace_id,
     status: event.status,
     timestamp: event.timestamp,
     metadata: event.metadata
   };
   ```

4. Activate the workflow

Your webhook URL will be: `http://localhost:5678/webhook/chora-events`

### Step 2: Configure EventWatcher with Webhook

Update your test script:

```python
import asyncio
from pathlib import Path
from mcp_n8n.event_watcher import EventWatcher
from mcp_n8n.memory.event_log import EventLog

async def main():
    # Initialize EventLog
    event_log = EventLog(base_dir=Path(".chora/memory/events"))

    # Create EventWatcher WITH webhook
    watcher = EventWatcher(
        event_log=event_log,
        events_file="var/telemetry/events.jsonl",
        n8n_webhook_url="http://localhost:5678/webhook/chora-events"
    )

    print("Starting EventWatcher with webhook...")
    await watcher.start()

    # Keep running
    print("Monitoring events... Press Ctrl+C to stop")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping EventWatcher...")
        await watcher.stop()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Test Webhook Forwarding

Generate a test event:

```bash
echo '{"timestamp":"2025-10-19T10:05:00Z","trace_id":"test-webhook-001","status":"success","schema_version":"1.0","event_type":"chora.artifact_assembled","metadata":{"artifact_id":"daily-report","output_path":"output/report.md"}}' >> var/telemetry/events.jsonl
```

**Expected result:**
- EventWatcher logs: "Event forwarded to webhook: test-webhook-001"
- n8n workflow executes and shows the event details
- Event is ALSO stored in `.chora/memory/events/` (dual consumption!)

### Step 4: Handle Webhook Failures Gracefully

Stop n8n and generate another event:

```bash
echo '{"timestamp":"2025-10-19T10:10:00Z","trace_id":"test-failure-001","status":"success","schema_version":"1.0","event_type":"chora.content_generated"}' >> var/telemetry/events.jsonl
```

**Expected result:**
- EventWatcher logs: "Webhook delivery failed: ..." (WARNING level)
- Event is STILL stored in `.chora/memory/events/` (graceful degradation!)
- No errors raised, EventWatcher keeps running

**Success!** Webhook failures don't prevent event storage.

---

## Part 4: Querying Events with get_events Tool

The `get_events` MCP tool provides powerful querying capabilities for debugging.

### Step 1: Query by Trace ID

```python
import asyncio
from mcp_n8n.tools.event_query import get_events, set_event_log
from mcp_n8n.memory.event_log import EventLog

async def main():
    # Initialize EventLog for queries
    event_log = EventLog()
    set_event_log(event_log)

    # Query all events for a specific trace
    events = await get_events(trace_id="test-001")

    print(f"Found {len(events)} events for trace test-001:")
    for event in events:
        print(f"  - {event['event_type']} ({event['status']})")

if __name__ == "__main__":
    asyncio.run(main())
```

**Expected output:**
```
Found 1 events for trace test-001:
  - chora.content_generated (success)
```

### Step 2: Query by Event Type

```python
# Get all artifact assembly events
events = await get_events(event_type="chora.artifact_assembled")

print(f"Found {len(events)} artifact assembly events:")
for event in events:
    print(f"  - {event['trace_id']} at {event['timestamp']}")
```

### Step 3: Query Recent Events

```python
# Get all events from last 24 hours
events = await get_events(since="24h")

print(f"Found {len(events)} events in last 24 hours")

# Get all failures from last hour
failures = await get_events(status="failure", since="1h")

print(f"Found {len(failures)} failures in last hour")
```

### Step 4: Limit Results

```python
# Get last 10 events
events = await get_events(limit=10)

print(f"Last 10 events:")
for event in events:
    print(f"  - {event['event_type']} @ {event['timestamp'][:19]}")
```

**Expected output:**
```
Last 10 events:
  - chora.content_generated @ 2025-10-19T10:00:00
  - chora.artifact_assembled @ 2025-10-19T10:05:00
  - chora.content_generated @ 2025-10-19T10:10:00
  ...
```

---

## Part 5: Trace ID Propagation (Gateway Integration)

The real power of event monitoring comes from trace ID propagation across the gateway/backend boundary.

### How It Works

```
1. User calls chora:assemble_artifact
   ↓
2. Gateway generates trace_id = "abc123"
   ↓
3. Gateway sets CHORA_TRACE_ID=abc123 in subprocess environment
   ↓
4. chora-compose reads CHORA_TRACE_ID from environment
   ↓
5. chora-compose emits events with trace_id="abc123"
   ↓
6. EventWatcher stores events with trace_id="abc123"
   ↓
7. You query get_events(trace_id="abc123") to see full workflow
```

### Example: Debugging a Multi-Step Workflow

**Scenario:** A workflow that generates content, then assembles an artifact

```python
# Simulate gateway generating trace_id
import os
import uuid

trace_id = str(uuid.uuid4())
os.environ["CHORA_TRACE_ID"] = trace_id

print(f"Starting workflow with trace_id: {trace_id}")

# Simulate backend operations (in real usage, this is chora-compose subprocess)
from mcp_n8n.memory.trace import emit_event

# Step 1: Generate content
emit_event(
    event_type="chora.content_generated",
    trace_id=trace_id,
    status="success",
    content_config_id="intro-section",
    duration_ms=234
)

# Step 2: Assemble artifact
emit_event(
    event_type="chora.artifact_assembled",
    trace_id=trace_id,
    status="success",
    artifact_config_id="daily-report",
    output_path="output/daily-report.md",
    section_count=4
)

# Now query the full workflow
events = await get_events(trace_id=trace_id)

print(f"\nWorkflow timeline for {trace_id}:")
for event in events:
    print(f"  {event['timestamp']}: {event['event_type']} - {event['status']}")
```

**Expected output:**
```
Starting workflow with trace_id: abc123-def456-789

Workflow timeline for abc123-def456-789:
  2025-10-19T10:15:00Z: chora.content_generated - success
  2025-10-19T10:15:02Z: chora.artifact_assembled - success
```

**Success!** You can now trace the complete lifecycle of a request across gateway and backend.

---

## What You Learned

Congratulations! You've completed the event monitoring tutorial. You now know how to:

- ✅ Set up EventWatcher to monitor chora-compose events
- ✅ Store events in gateway telemetry for historical queries
- ✅ Forward events to n8n webhooks for real-time reactions
- ✅ Handle webhook failures gracefully (fire-and-forget pattern)
- ✅ Query events by trace_id, event_type, status, and time range
- ✅ Understand trace ID propagation across process boundaries
- ✅ Debug multi-step workflows using event correlation

## Next Steps

Now that you understand event monitoring, you can:

1. **Build event-driven n8n workflows** - React to artifact completion, content generation, etc.
2. **Debug production issues** - Query events by trace_id to understand failures
3. **Monitor performance** - Track duration_ms across operations
4. **Implement advanced patterns** - Event aggregation, alerting, metrics

## Related Documentation

- [Event Schema Reference](../process/specs/event-schema.md) - Complete event format specification
- [n8n Integration Guide](../N8N_INTEGRATION_GUIDE.md) - Advanced n8n patterns
- [Sprint 3 Intent Document](../change-requests/sprint-3-event-monitoring/intent.md) - Original design decisions

## Troubleshooting

### EventWatcher not detecting events

**Problem:** Events written to `events.jsonl` but EventWatcher doesn't see them

**Solution:**
1. Check that EventWatcher is running (`_running` attribute should be `True`)
2. Verify events file path matches: `var/telemetry/events.jsonl`
3. Check file permissions (EventWatcher needs read access)
4. Ensure events are valid JSON (one event per line)

### Webhook returns 404

**Problem:** EventWatcher logs "Webhook returned status 404"

**Solution:**
1. Verify n8n workflow is activated
2. Check webhook URL is correct (should include `/webhook/` path)
3. Ensure n8n is running on the expected port (default: 5678)

### Events not stored in EventLog

**Problem:** `get_events()` returns empty list

**Solution:**
1. Check that EventLog base_dir exists and is writable
2. Verify events have valid timestamp (ISO 8601 format)
3. Check monthly partition exists (e.g., `.chora/memory/events/2025-10/`)
4. Look for errors in EventWatcher logs

### Trace ID not propagating

**Problem:** Backend events have different trace_id than gateway

**Solution:**
1. Ensure `CHORA_TRACE_ID` environment variable is set before spawning subprocess
2. Verify chora-compose v1.3.0+ (earlier versions don't support trace context)
3. Check that backend reads `os.getenv("CHORA_TRACE_ID")`

---

**Tutorial Version:** 1.0
**Last Updated:** 2025-10-19
**Tested With:** mcp-n8n v0.2.0, chora-compose v1.3.0
**Estimated Completion Time:** 20-30 minutes
