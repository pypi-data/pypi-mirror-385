# Event Monitoring for Sprint 3 Validation

**Change Request ID:** sprint-3-event-monitoring
**Type:** Feature (New Capability)
**Status:** Ready for DDD
**Sprint:** Sprint 3 (Validation Workflow)
**Estimated Effort:** 11-16 hours
**Priority:** High (blocks Sprint 3 validation)

---

## Business Context

### Problem Statement

Sprint 3's validation workflow (Daily GitHub Report) requires **real-time event monitoring** to:
- Track workflow progress across gateway and backend boundaries
- Correlate requests using trace_id for debugging
- Enable event-driven n8n workflows (react when artifacts complete)
- Validate that chora-compose v1.3.0 event emission works in production

**Current Situation:**
- ✅ chora-compose v1.3.0 emits events to `var/telemetry/events.jsonl` (production-ready)
- ✅ mcp-n8n has EventLog infrastructure (`.chora/memory/events/`)
- ✅ n8n is running locally and ready for integration
- ❌ No connection between chora-compose events and mcp-n8n telemetry
- ❌ No n8n integration for event-driven workflows

### Success Metrics

**Sprint 3 Validation Must Demonstrate:**
1. Events from chora-compose visible in mcp-n8n within 100ms
2. trace_id propagates: gateway request → backend subprocess → event log
3. n8n can react to events (webhook pattern)
4. n8n can query events (MCP tool pattern)
5. Performance: <100ms event latency, <50ms webhook delivery (best-effort)

**Long-term Value:**
- Foundation for all event-driven workflows (Sprints 4-5)
- Observability across gateway/backend boundary
- Debugging capability for multi-step workflows
- n8n becomes event-reactive (not just scheduled/manual)

### Why Option 4 (Hybrid)?

After exploring 4 design options (see `docs/DESIGN_OPTIONS_EVENT_MONITORING.md`), Option 4 provides:
- ✅ Immediate event reactions (n8n webhook)
- ✅ Powerful historical queries (MCP tool)
- ✅ Graceful degradation (works without n8n)
- ✅ Validates both integration patterns (webhook + MCP)
- ✅ Production-ready architecture

---

## User Stories

### Story 1: Event-Driven Workflow Author
```
As an n8n workflow author,
I want to react immediately when chora-compose completes an artifact,
So that I can trigger downstream actions (post to Slack, update Coda, send email)
Without polling or manual triggers.
```

**Acceptance Criteria:**
- n8n workflow triggered via webhook when `chora.artifact_assembled` event occurs
- Webhook payload includes full event details (trace_id, metadata, output_path)
- Workflow receives event within 50ms of emission (best-effort)

### Story 2: Workflow Debugger
```
As an mcp-n8n administrator,
I want to query all events for a specific trace_id,
So that I can debug failures in multi-step workflows
And understand the full request lifecycle.
```

**Acceptance Criteria:**
- MCP tool `get_events(trace_id="abc123")` returns all correlated events
- Events include timestamps, status, metadata from both gateway and backend
- Events are ordered chronologically
- Query completes in <10ms for recent events

### Story 3: Validation Workflow Builder
```
As a Sprint 3 validation developer,
I want the Daily GitHub Report workflow to demonstrate event correlation,
So that I can validate the architecture works end-to-end
And provide confidence for Sprint 5 production workflows.
```

**Acceptance Criteria:**
- Workflow generates trace_id at start
- All steps (GitHub API → generate_content → assemble_artifact) use same trace_id
- Final event log shows complete workflow timeline
- Performance meets targets (<60s end-to-end)

---

## Architecture Overview

### High-Level Flow

```
1. Gateway Request (user calls chora:assemble_artifact)
   → Gateway generates trace_id = "abc123"
   → Gateway sets CHORA_TRACE_ID=abc123 env var
   → Gateway spawns chora-compose subprocess

2. Backend Execution (chora-compose)
   → Reads CHORA_TRACE_ID from environment
   → Generates artifact
   → Emits event to var/telemetry/events.jsonl:
      {"trace_id": "abc123", "event_type": "chora.artifact_assembled", ...}

3. Event Monitoring (mcp-n8n EventWatcher)
   → Tails var/telemetry/events.jsonl
   → Detects new event
   → Stores in .chora/memory/events/ (via EventLog)
   → Forwards to n8n webhook (if configured)

4. Event Consumption
   → n8n webhook workflow reacts immediately (Pattern A)
   → OR n8n queries later via get_events MCP tool (Pattern B)
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                  AI Client / n8n Workflow               │
└────────────────────┬────────────────────────────────────┘
                     │ JSON-RPC / Execute Command
                     ↓
┌─────────────────────────────────────────────────────────┐
│                   mcp-n8n Gateway                       │
│                                                          │
│  ┌──────────────┐         ┌─────────────────┐          │
│  │ Gateway      │ trace_id│  EventWatcher   │          │
│  │ (FastMCP)    ├────────→│  - Tail events  │          │
│  │              │         │  - Store        │          │
│  │ Generates    │         │  - Forward      │          │
│  │ trace_id     │         │                 │          │
│  └──────┬───────┘         └────────┬────────┘          │
│         │ CHORA_TRACE_ID           │                    │
│         │ env var                  │                    │
└─────────┼──────────────────────────┼────────────────────┘
          ↓                          ↓
┌─────────────────────┐    ┌─────────────────────┐
│  chora-compose      │    │ .chora/memory/      │
│  Subprocess         │    │ events/             │
│                     │    │ (EventLog)          │
│  Emits events →     │    │                     │
│  var/telemetry/     │    │ get_events tool     │
│  events.jsonl       │    │ queries here        │
└─────────────────────┘    └────────┬────────────┘
                                    ↓
                          ┌─────────────────────┐
                          │ n8n Webhook         │
                          │ (optional)          │
                          │                     │
                          │ Event-driven        │
                          │ workflows           │
                          └─────────────────────┘
```

### Data Flow (Detailed)

**Step 1: Request Initiation**
```python
# mcp-n8n gateway receives request
trace_id = generate_trace_id()  # e.g., "abc123-def456-789"
logger.info(f"Starting request with trace_id={trace_id}")

# Spawn backend with trace context
subprocess.Popen(
    ["python", "-m", "chora_compose.mcp.server"],
    env={
        **os.environ,
        "CHORA_TRACE_ID": trace_id
    }
)
```

**Step 2: Event Emission (chora-compose)**
```python
# chora-compose reads trace_id from environment
trace_id = os.environ.get("CHORA_TRACE_ID")

# Emits event (v1.3.0 feature)
event = {
    "timestamp": "2025-10-19T10:00:00.123Z",
    "trace_id": trace_id,  # "abc123-def456-789"
    "status": "success",
    "schema_version": "1.0",
    "event_type": "chora.artifact_assembled",
    "metadata": {
        "artifact_config_id": "daily-report",
        "output_path": "output/daily-report-2025-10-19.md",
        "section_count": 4,
        "duration_ms": 234
    }
}

# Appends to var/telemetry/events.jsonl
with open("var/telemetry/events.jsonl", "a") as f:
    f.write(json.dumps(event) + "\n")
```

**Step 3: Event Detection (EventWatcher)**
```python
# EventWatcher tails the file
async for line in tail_file("var/telemetry/events.jsonl"):
    event = json.loads(line)

    # Store in gateway telemetry
    await event_log.emit(
        trace_id=event["trace_id"],
        event_type=event["event_type"],
        status=event["status"],
        metadata=event["metadata"]
    )

    # Forward to n8n (optional)
    if n8n_webhook_url:
        await forward_to_webhook(n8n_webhook_url, event)
```

**Step 4: Event Consumption (n8n)**

**Pattern A: Webhook-Driven**
```json
{
  "name": "Artifact Success Handler",
  "nodes": [
    {
      "type": "webhook",
      "parameters": {"path": "chora-events"}
    },
    {
      "type": "function",
      "code": "if ($json.event_type === 'chora.artifact_assembled' && $json.status === 'success') { return $json; }"
    },
    {
      "type": "slack",
      "parameters": {
        "message": "Artifact ready: {{$json.metadata.output_path}}"
      }
    }
  ]
}
```

**Pattern B: Query-Driven**
```bash
# n8n Execute Command node
mcp-tool.sh get_events --trace-id=abc123-def456-789 --format=json
# Returns: [{"trace_id": "abc123...", "event_type": "chora.artifact_assembled", ...}]
```

---

## API Reference (Draft)

### EventWatcher Class

**Module:** `src/mcp_n8n/event_watcher.py`

```python
class EventWatcher:
    """Monitor chora-compose events and forward to telemetry + n8n.

    Implements Option 4 (Hybrid) pattern:
    - Tails var/telemetry/events.jsonl
    - Stores in .chora/memory/events/ (always)
    - Forwards to n8n webhook (optional, fire-and-forget)
    """

    def __init__(
        self,
        event_log: EventLog,
        events_file: str | Path = "var/telemetry/events.jsonl",
        n8n_webhook_url: str | None = None
    ):
        """Initialize event watcher.

        Args:
            event_log: Existing EventLog instance for storage
            events_file: Path to chora-compose events file
            n8n_webhook_url: Optional n8n webhook URL (e.g.,
                "http://localhost:5678/webhook/chora-events")
        """

    async def start(self) -> None:
        """Start watching events.

        Runs continuously until stopped. Yields control to event loop
        every 100ms when no events detected.

        Raises:
            FileNotFoundError: If events_file parent directory doesn't exist
        """

    async def stop(self) -> None:
        """Stop watching events gracefully."""
```

### MCP Tool: get_events

**Module:** `src/mcp_n8n/tools/event_query.py`

```python
@mcp.tool()
async def get_events(
    trace_id: Annotated[str | None, "Filter by trace ID"] = None,
    event_type: Annotated[str | None, "Filter by event type (e.g., 'chora.artifact_assembled')"] = None,
    status: Annotated[Literal["success", "failure", "pending"] | None, "Filter by status"] = None,
    since: Annotated[str | None, "Time range start (ISO timestamp or relative like '24h')"] = None,
    limit: Annotated[int, "Maximum results"] = 100
) -> list[dict[str, Any]]:
    """Query events from gateway telemetry.

    Returns events matching filters, ordered chronologically (oldest first).
    Supports both chora-compose events and gateway-emitted events.

    Examples:
        # Get all events for a workflow
        events = await get_events(trace_id="abc123-def456-789")

        # Get recent artifact assemblies
        events = await get_events(
            event_type="chora.artifact_assembled",
            since="24h"
        )

        # Get failures in last hour
        events = await get_events(
            status="failure",
            since="1h",
            limit=10
        )

    Returns:
        List of event dictionaries with schema v1.0 format:
        [
            {
                "timestamp": "2025-10-19T10:00:00.123Z",
                "trace_id": "abc123-def456-789",
                "status": "success",
                "event_type": "chora.artifact_assembled",
                "schema_version": "1.0",
                "metadata": {...}
            }
        ]
    """
```

### Configuration

**Environment Variables:**

```bash
# Event monitoring configuration
MCP_N8N_EVENTS_FILE=var/telemetry/events.jsonl  # Path to chora-compose events
MCP_N8N_EVENT_WEBHOOK_URL=http://localhost:5678/webhook/chora-events  # Optional n8n webhook

# Existing gateway config
ANTHROPIC_API_KEY=sk-ant-...
CODA_API_KEY=...
```

**Gateway Startup Integration:**

```python
# src/mcp_n8n/gateway.py
async def startup():
    """Initialize gateway and start event monitoring."""
    # Initialize EventLog
    event_log = EventLog(base_dir=".chora/memory/events")

    # Start EventWatcher
    n8n_webhook = os.getenv("MCP_N8N_EVENT_WEBHOOK_URL")
    watcher = EventWatcher(
        event_log=event_log,
        events_file="var/telemetry/events.jsonl",
        n8n_webhook_url=n8n_webhook
    )

    # Run in background task
    asyncio.create_task(watcher.start())

    logger.info(f"Event monitoring started (webhook={'enabled' if n8n_webhook else 'disabled'})")
```

---

## Acceptance Criteria

### AC1: Event File Watching
**Given** chora-compose emits an event to `var/telemetry/events.jsonl`
**When** EventWatcher is running
**Then** the event appears in `.chora/memory/events/` within 100ms
**And** the event includes the trace_id from `CHORA_TRACE_ID` env var
**And** the event matches event schema v1.0

**Test:** Unit test with mock events file

---

### AC2: Trace ID Propagation
**Given** a gateway request with generated trace_id="test-123"
**When** the gateway spawns a chora-compose subprocess
**Then** `CHORA_TRACE_ID=test-123` is set in the subprocess environment
**And** all events emitted by chora-compose include `trace_id="test-123"`
**And** the EventLog stores events with correct trace_id

**Test:** Integration test with real chora-compose subprocess

---

### AC3: n8n Webhook Forwarding (Optional)
**Given** `N8N_WEBHOOK_URL` is configured
**When** an event is detected
**Then** a POST request is sent to the webhook URL within 50ms
**And** the request includes the full event payload as JSON
**And** the request header `Content-Type: application/json`
**And** failures are logged but don't stop event storage (fire-and-forget)

**Test:** Integration test with mock webhook server

---

### AC4: Graceful Degradation
**Given** `N8N_WEBHOOK_URL` is NOT configured OR points to unavailable endpoint
**When** an event is detected
**Then** the event is still stored in gateway telemetry
**And** no errors are raised (webhook is optional)
**And** a debug/warning log indicates webhook status

**Test:** Unit test with unavailable webhook

---

### AC5: MCP Tool Query
**Given** events exist in gateway telemetry with various trace_ids
**When** I call `get_events(trace_id="test-123")`
**Then** I receive all events with `trace_id="test-123"`
**And** events are ordered chronologically (oldest first)
**And** the query completes in <10ms for recent events

**Test:** Integration test with EventLog

---

### AC6: MCP Tool Filtering
**Given** events of different types and statuses
**When** I call `get_events(event_type="chora.artifact_assembled", status="success", since="24h")`
**Then** I receive only matching events
**And** events are limited to last 24 hours
**And** all returned events have the specified type and status

**Test:** Unit test with mock EventLog data

---

### AC7: n8n Execute Command Integration
**Given** an n8n workflow using Execute Command node
**When** it calls `mcp-tool.sh get_events --trace-id=test-123 --format=json`
**Then** it receives JSON-formatted events
**And** the output is parseable by n8n Function node
**And** the workflow can extract fields like `metadata.output_path`

**Test:** Manual test with real n8n workflow

---

## Out of Scope (Sprint 3)

### Explicitly NOT Included

1. **Event Schema Extensions**
   - Using existing event schema v1.0
   - No new event types beyond chora.* namespace
   - Gateway events (gateway.*) deferred to Sprint 5

2. **Authentication/Authorization**
   - n8n webhook requires no auth token
   - Assumes localhost/trusted network
   - Production security deferred to deployment guide

3. **Event Persistence Beyond EventLog**
   - Using existing `.chora/memory/events/` structure
   - No database backend
   - No event archival/rotation

4. **Advanced Webhook Features**
   - No retry logic for failed webhooks
   - No webhook queue
   - Fire-and-forget only

5. **Performance Optimization**
   - No batch processing
   - No event aggregation
   - Simple file tailing (good enough for Sprint 3)

6. **Multi-Backend Event Correlation**
   - Only monitoring chora-compose events
   - Coda MCP events not included
   - Multi-backend correlation deferred to Sprint 5

---

## Dependencies & Prerequisites

### Technical Dependencies

**Existing Infrastructure (Already Available):**
- ✅ `EventLog` class (`.chora/memory/event_log.py`)
- ✅ Event schema v1.0 (`docs/process/specs/event-schema.md`)
- ✅ chora-compose v1.3.0 with event emission
- ✅ n8n running locally (docker-compose.yml)
- ✅ Trace context infrastructure (`src/mcp_n8n/memory/trace.py`)

**New Dependencies (to be added):**
- `aiohttp` (for webhook POST) - already in dependencies
- `asyncio` (for file tailing) - stdlib

**External Services:**
- n8n webhook endpoint (optional, manual setup)
- chora-compose subprocess (already working)

### Process Prerequisites

**Before Starting Implementation:**
1. ✅ Read event-schema.md (understand v1.0 format)
2. ✅ Review EventLog implementation (understand storage)
3. ✅ Test chora-compose event emission manually
4. ✅ Create n8n webhook workflow (for testing)
5. ✅ Stakeholder approval of this intent document

**Ready for DDD Checklist:**
- ✅ Intent document reviewed
- ✅ API reference drafted
- ✅ Acceptance criteria defined
- ✅ Out of scope clarified
- ⏸️ Stakeholder sign-off (self-approved for Sprint 3)

---

## Risks & Mitigations

### Risk 1: File Watching Performance
**Risk:** Tailing events.jsonl may be slow or miss events
**Likelihood:** Low
**Impact:** High (events not detected = broken monitoring)
**Mitigation:**
- Use proven async file tailing pattern
- Test with high event volume (100+ events/sec)
- Add unit tests for edge cases (concurrent writes, file rotation)

### Risk 2: Webhook Reliability
**Risk:** n8n webhook may be unavailable or slow
**Likelihood:** Medium
**Impact:** Low (webhook is optional, fire-and-forget)
**Mitigation:**
- Fire-and-forget pattern (don't block on webhook)
- 2-second timeout on webhook POST
- Log warnings, don't raise errors
- Event still stored in telemetry regardless

### Risk 3: Trace ID Propagation Fails
**Risk:** `CHORA_TRACE_ID` env var not passed correctly to subprocess
**Likelihood:** Low
**Impact:** High (no event correlation)
**Mitigation:**
- Integration tests verify env var propagation
- Validate chora-compose receives trace_id
- Log trace_id at gateway startup

### Risk 4: Event Schema Incompatibility
**Risk:** chora-compose events don't match schema v1.0
**Likelihood:** Very Low (v1.3.0 is compliant)
**Impact:** Medium (parsing errors)
**Mitigation:**
- Validate events against schema in tests
- Add defensive parsing (handle missing fields)
- Log warnings for malformed events

---

## Testing Strategy

### Unit Tests (TDD)
**File:** `tests/unit/test_event_watcher.py`
- File tailing detects new lines
- Events stored in EventLog correctly
- Webhook POST sent with correct payload
- Webhook failures don't raise errors
- Trace ID propagation to subprocess

### Integration Tests (BDD + E2E)
**File:** `tests/integration/test_event_monitoring_e2e.py`
- End-to-end flow: chora emits → gateway stores → n8n receives
- Real chora-compose subprocess with CHORA_TRACE_ID
- Mock n8n webhook server
- EventLog query returns correct events

### BDD Scenarios (pytest-bdd)
**File:** `tests/features/event_monitoring.feature`
- Gherkin scenarios for all acceptance criteria
- Step definitions for event emission, detection, storage
- Validates full user stories

### Manual Testing (Validation)
**File:** `scripts/test-daily-report-workflow.py`
- Full Daily GitHub Report workflow
- Verify trace correlation end-to-end
- Measure performance metrics
- Test n8n webhook integration

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Event detection latency | <100ms | Time from write to events.jsonl to EventLog storage |
| Webhook delivery latency | <50ms | Time from event detection to webhook POST (best-effort) |
| Query latency (recent events) | <10ms | `get_events()` for last 24h |
| Query latency (by trace_id) | <5ms | `get_events(trace_id=...)` |
| Event storage overhead | <1MB/1000 events | Disk usage in `.chora/memory/events/` |
| Webhook failure impact | 0ms | Should not block event storage |

---

## Implementation Timeline

Based on DDD→BDD→TDD process:

| Phase | Duration | Artifacts |
|-------|----------|-----------|
| **DDD** | 2-3 hours | This document + API ref + acceptance criteria (DONE) |
| **BDD** | 1-2 hours | Gherkin scenarios + step definitions |
| **TDD** | 4-6 hours | Unit tests + EventWatcher implementation + refactoring |
| **Integration** | 2-3 hours | E2E tests + n8n webhook testing + validation script |
| **Documentation** | 1 hour | Update N8N_INTEGRATION_GUIDE.md + AGENTS.md |
| **CI/Review** | 1 hour | Automated tests + manual review |
| **TOTAL** | **11-16 hours** | Production-ready event monitoring |

---

## Next Steps

### Immediate (After Intent Approval)
1. ☐ Create BDD scenarios (`tests/features/event_monitoring.feature`)
2. ☐ Write step definitions (`tests/step_defs/event_monitoring_steps.py`)
3. ☐ Run BDD scenarios → RED (should fail)

### TDD Phase
4. ☐ Write unit tests (`tests/unit/test_event_watcher.py`) → RED
5. ☐ Implement `EventWatcher` class → GREEN
6. ☐ Refactor implementation → STILL GREEN
7. ☐ Implement `get_events` MCP tool

### Integration Phase
8. ☐ Write E2E tests (`tests/integration/test_event_monitoring_e2e.py`)
9. ☐ Create n8n webhook workflow for testing
10. ☐ Test with real chora-compose subprocess
11. ☐ Measure performance against targets

### Documentation & Release
12. ☐ Update `docs/N8N_INTEGRATION_GUIDE.md` with Option 4 patterns
13. ☐ Update `AGENTS.md` with event monitoring examples
14. ☐ Commit with conventional message: `feat(event-monitoring): implement hybrid event watcher`
15. ☐ Include in Sprint 3 validation milestone

---

## References

**Internal Documentation:**
- [Event Schema v1.0](../../process/specs/event-schema.md)
- [Event Monitoring Design Options](../../DESIGN_OPTIONS_EVENT_MONITORING.md) (to be created)
- [N8N Integration Guide](../../N8N_INTEGRATION_GUIDE.md)
- [UNIFIED_ROADMAP.md - Sprint 3](../../UNIFIED_ROADMAP.md#L356-L558)
- [Development Lifecycle](../../process/development-lifecycle.md)

**External References:**
- [chora-compose v1.3.0 Event Emission](https://github.com/liminalcommons/chora-compose/blob/main/docs/telemetry.md)
- [n8n Webhook Documentation](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [OpenTelemetry Trace Context](https://www.w3.org/TR/trace-context/)

---

**Status:** ✅ READY FOR DDD
**Next Phase:** BDD (Gherkin scenarios)
**Approver:** Self-approved for Sprint 3 validation
**Implementation Start:** Next session (fresh context)
