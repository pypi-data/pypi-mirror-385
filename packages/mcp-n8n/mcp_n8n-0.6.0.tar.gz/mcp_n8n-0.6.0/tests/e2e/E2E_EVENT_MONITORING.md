# E2E Test Suite: Event Monitoring

**Version:** v1.0.0
**Duration:** 15-20 minutes
**Purpose:** Validate event monitoring, trace correlation, and telemetry queries
**Prerequisites:** Complete [E2E_BACKEND_ROUTING.md](E2E_BACKEND_ROUTING.md) first
**Last Updated:** October 21, 2025

---

## Overview

This suite validates **event monitoring and telemetry** - ensuring events are captured, queryable, and traceable across backend boundaries.

### What You'll Test

**Tools (1):**
- `get_events` - Query telemetry with various filters

**Event Types:**
- `gateway.started` - Gateway initialization
- `gateway.tool_call` - Tool execution tracking
- `gateway.backend_registered` - Backend registration
- `chora.*` events - From chora-composer backend
- Custom workflow events

**Key Concepts:**
- Trace context propagation
- Event correlation
- Time-range queries
- Status filtering
- Event log retention

---

## Test 1: Event Capture

### Step 1.1: Gateway Lifecycle Events

**Prompt:**
```
Use get_events with event_type="gateway.started" to find when the gateway was last started.
What information is captured in the startup event?
```

**Success Criteria:**
- [ ] At least one startup event found
- [ ] Event has timestamp, trace_id, status
- [ ] Contains version, backend_count in data
- [ ] event_monitoring_enabled = true

**Expected Event:**
```json
{
  "type": "gateway.started",
  "timestamp": "2025-10-21T14:00:00.123Z",
  "trace_id": "gateway_start_abc123",
  "status": "success",
  "data": {
    "version": "0.4.0",
    "backend_count": 1,
    "event_monitoring_enabled": true
  }
}
```

### Step 1.2: Tool Call Events

**Prompt:**
```
Use get_events with event_type="gateway.tool_call" limit=5.
Show me the last 5 tool calls made through the gateway.
```

**Success Criteria:**
- [ ] Returns tool call events
- [ ] Each has: tool_name, status, duration_ms
- [ ] Includes both success and failure statuses
- [ ] Trace IDs are unique per call

**Expected Event Structure:**
```json
{
  "type": "gateway.tool_call",
  "timestamp": "2025-10-21T14:05:00.456Z",
  "trace_id": "call_xyz789",
  "status": "success",
  "data": {
    "tool_name": "chora:list_generators",
    "backend": "chora-composer",
    "duration_ms": 245,
    "namespace": "chora"
  }
}
```

---

## Test 2: Trace Context Propagation

### Step 2.1: Follow a Multi-Step Workflow

**Prompt:**
```
1. Call chora:list_generators (note the trace_id from response or logs)
2. Use get_events with that trace_id to find all related events

How many events were captured for this single tool call?
```

**Success Criteria:**
- [ ] Multiple events share same trace_id
- [ ] Events ordered chronologically
- [ ] Includes: tool_call start, backend communication, completion
- [ ] Trace spans entire operation

**Expected Event Sequence:**
```json
[
  {
    "type": "gateway.tool_call_start",
    "trace_id": "trace_123",
    "data": {"tool_name": "chora:list_generators"}
  },
  {
    "type": "chora.generators_listed",
    "trace_id": "trace_123",
    "data": {"count": 17}
  },
  {
    "type": "gateway.tool_call_complete",
    "trace_id": "trace_123",
    "data": {"duration_ms": 245, "status": "success"}
  }
]
```

### Step 2.2: Cross-Backend Trace Correlation

**Prompt:**
```
If you have access to both chora and coda backends:
1. Make a tool call to each backend
2. Check if trace_id propagates to backend-emitted events

Do backend events include the gateway's trace_id?
```

**Success Criteria:**
- [ ] Trace ID propagated via environment variable
- [ ] Backend events include trace_id
- [ ] Can correlate gateway + backend events
- [ ] End-to-end traceability

---

## Test 3: Query Filtering

### Step 3.1: Filter by Event Type

**Prompt:**
```
Query events with these filters one at a time:
1. event_type="gateway.tool_call"
2. event_type="gateway.backend_registered"
3. event_type="chora.content_generated"

How many events of each type exist?
```

**Success Criteria:**
- [ ] Each filter returns correct event type
- [ ] No cross-contamination
- [ ] Counts are accurate
- [ ] Empty results for non-existent types

### Step 3.2: Filter by Status

**Prompt:**
```
Use get_events with status="failure" limit=10.
List any failures that have occurred.
What were the common failure causes?
```

**Success Criteria:**
- [ ] Only failure events returned
- [ ] Each has error information in data
- [ ] Status field = "failure"
- [ ] Useful for debugging

**Expected Failure Event:**
```json
{
  "type": "gateway.tool_call",
  "status": "failure",
  "trace_id": "fail_abc",
  "data": {
    "tool_name": "chora:generate_content",
    "error": "Template not found",
    "error_code": "template_not_found"
  }
}
```

### Step 3.3: Combined Filters

**Prompt:**
```
Use get_events with:
- event_type="gateway.tool_call"
- status="success"
- limit=20

How many successful tool calls in the last session?
```

**Success Criteria:**
- [ ] Both filters applied (AND logic)
- [ ] Only successful tool calls returned
- [ ] Correct event type
- [ ] Limit respected

---

## Test 4: Time-Range Queries

### Step 4.1: Recent Events (Relative Time)

**Prompt:**
```
Query events from the last hour using since="1h".
How many events were captured?
```

**Success Criteria:**
- [ ] Relative time parsing works ("1h", "24h", "7d")
- [ ] Only events within range returned
- [ ] Timestamps are within expected range
- [ ] Efficient query (< 500ms)

### Step 4.2: Absolute Timestamp

**Prompt:**
```
Use get_events with since="2025-10-21T14:00:00Z" (ISO format).
Returns all events after that specific time.
```

**Success Criteria:**
- [ ] ISO timestamp parsing works
- [ ] Timezone handling correct (UTC)
- [ ] Results chronologically ordered
- [ ] No events before cutoff time

### Step 4.3: Different Time Windows

**Prompt:**
```
Compare event counts for these windows:
- since="10m" (last 10 minutes)
- since="1h" (last hour)
- since="24h" (last day)

How does activity change over time?
```

**Success Criteria:**
- [ ] All time windows work
- [ ] Counts increase with larger windows
- [ ] No duplicate events
- [ ] Performance consistent across ranges

---

## Test 5: Event Correlation Analysis

### Step 5.1: Error Analysis

**Prompt:**
```
1. Find all failure events (status="failure")
2. For each failure, get its trace_id
3. Query all events for those trace_ids

Can you reconstruct what led to each failure?
```

**Success Criteria:**
- [ ] Trace ID links all related events
- [ ] Can see sequence: start → error → failure
- [ ] Error context preserved
- [ ] Timeline is clear

### Step 5.2: Performance Analysis

**Prompt:**
```
Get all tool_call events and analyze duration_ms.
What is the:
- Fastest call?
- Slowest call?
- Average duration?
```

**Success Criteria:**
- [ ] duration_ms captured for all calls
- [ ] Can aggregate across events
- [ ] Performance patterns visible
- [ ] Outliers identifiable

---

## Test 6: Limit and Pagination

### Step 6.1: Limit Enforcement

**Prompt:**
```
Use get_events with limit=5.
Verify only 5 events returned.
```

**Success Criteria:**
- [ ] Exactly 5 events returned
- [ ] Most recent events first
- [ ] No truncation of event data

### Step 6.2: Maximum Limit Clamping

**Prompt:**
```
Try get_events with limit=5000 (exceeds max of 1000).
How many events are actually returned?
```

**Success Criteria:**
- [ ] Limit clamped to 1000
- [ ] No error thrown
- [ ] Returns maximum allowed events
- [ ] Clear in documentation

---

## Test 7: Event Log Persistence

### Step 7.1: Cross-Session Persistence

**Prompt:**
```
Look for events from previous gateway sessions.
Can you find events older than the current session?
```

**Success Criteria:**
- [ ] Events persist across restarts
- [ ] Stored in .chora/memory/events/
- [ ] Queryable after restart
- [ ] Retention policy applied (7 days default)

### Step 7.2: Event File Structure

**Prompt:**
```
Check what event files exist in .chora/memory/events/.
Are they organized by date?
```

**Success Criteria:**
- [ ] JSONL format (one event per line)
- [ ] Daily rotation (events_YYYY-MM-DD.jsonl)
- [ ] Compressed old files
- [ ] Auto-cleanup after retention period

---

## Test 8: Webhook Forwarding (Optional)

**Note:** Requires n8n_event_webhook_url configuration.

### Step 8.1: Verify Webhook Configuration

**Prompt:**
```
Check gateway_status. Is webhook_configured = true?
If yes, events are being forwarded to n8n.
```

**Success Criteria:**
- [ ] webhook_configured shown in status
- [ ] EventWatcher is enabled
- [ ] Webhook URL configured

### Step 8.2: Event Delivery

**Prompt:**
```
Make a tool call, then check your n8n workflow.
Did the event arrive?
```

**Success Criteria:**
- [ ] Events delivered to webhook
- [ ] JSON format preserved
- [ ] Real-time delivery (< 1s latency)
- [ ] Failures don't block event storage

---

**Test Suite:** Event Monitoring
**Duration:** 15-20 minutes
**Tools Tested:** 1 (get_events with extensive filtering)
**Status:** ✅ Telemetry system validated

---

## Next Steps

After completing this monitoring test:

1. ✅ **All tests pass:** Proceed to [E2E_WORKFLOW_ORCHESTRATION.md](E2E_WORKFLOW_ORCHESTRATION.md)
2. ⚠️ **Event capture issues:** Check EventWatcher logs and .chora/memory permissions
3. 📝 **Document:** Note event patterns and query performance

## Troubleshooting

**No events found:**
- Check .chora/memory/events/ directory exists
- Verify EventWatcher started (gateway_status)
- Check file permissions on event directory

**Missing trace IDs:**
- Ensure CHORA_TRACE_ID env var is propagated
- Check backend supports trace context
- Review trace emission in logs

**Slow queries:**
- Event log may be large (check file sizes)
- Consider time-range filters to reduce scan
- Check index files are generated

**Webhook not delivering:**
- Verify n8n webhook URL is accessible
- Check network connectivity
- Review EventWatcher logs for delivery errors
