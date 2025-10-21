# Event Schema Specification

**Version:** 1.0
**Date:** 2025-10-17
**Status:** Active
**Owner:** Joint (chora-compose + mcp-n8n teams)
**Purpose:** Define unified event schema for cross-service observability and coordination

---

## Overview

This specification defines the event schema for the chora ecosystem, enabling:
- Cross-service event correlation via trace context
- Gateway-to-backend observability
- Workflow tracking and debugging
- OpenTelemetry alignment

**Scope:** Events emitted by:
- chora-compose (Platform/Layer 2): `chora.*` namespace
- mcp-n8n (Gateway/Layer 3): `gateway.*` namespace
- Future context bus: `workflow.*` namespace

---

## Event Namespace Conventions

### Namespace: `chora.*`

**Owner:** chora-compose
**Purpose:** Platform-layer events (content generation, artifact assembly, validation)

**Event Types:**
- `chora.content_generated` - Content generation completed
- `chora.artifact_assembled` - Artifact assembly completed
- `chora.validation_completed` - Validation check completed
- `chora.capability_changed` - Capability updated (v1.3.0+, dynamic discovery)
- `chora.config_drafted` - Config draft created
- `chora.config_tested` - Config test completed
- `chora.config_saved` - Config persisted to filesystem

### Namespace: `gateway.*`

**Owner:** mcp-n8n
**Purpose:** Gateway-layer events (routing, backend lifecycle, orchestration)

**Event Types:**
- `gateway.tool_call` - Tool routed to backend
- `gateway.backend_started` - Backend process started
- `gateway.backend_failed` - Backend process failed
- `gateway.request_queued` - Request queued due to concurrency limit
- `gateway.workflow_started` - Multi-step workflow initiated
- `gateway.workflow_completed` - Workflow finished

### Namespace: `workflow.*`

**Owner:** Context Bus (future)
**Purpose:** Cross-service workflow lifecycle events

**Event Types:**
- `workflow.started` - Workflow execution started
- `workflow.step_completed` - Workflow step completed
- `workflow.completed` - Workflow finished
- `workflow.failed` - Workflow failed
- `workflow.cancelled` - Workflow cancelled by user

---

## Universal Schema

### Required Fields (ALL events MUST include)

```json
{
  "timestamp": "2025-10-17T12:00:00.123Z",
  "trace_id": "abc123def456",
  "status": "success"
}
```

**Field Specifications:**

| Field | Type | Format | Description |
|-------|------|--------|-------------|
| `timestamp` | string | ISO 8601 UTC | Event occurrence time, millisecond precision |
| `trace_id` | string | OpenTelemetry | Distributed trace identifier for correlation |
| `status` | string | enum | Event outcome: `success`, `failure`, `pending`, `cancelled` |

### Optional Fields (Events SHOULD include when applicable)

```json
{
  "schema_version": "1.0",
  "duration_ms": 1234,
  "error_code": "ERR_VALIDATION_FAILED",
  "error_message": "Template variable 'author' not found in context",
  "metadata": {
    "key": "value"
  }
}
```

**Field Specifications:**

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Event schema version (semver) |
| `duration_ms` | integer | Operation duration in milliseconds |
| `error_code` | string | Structured error code (e.g., `ERR_*`, `WARN_*`) |
| `error_message` | string | Human-readable error description |
| `metadata` | object | Event-specific context (schema varies by event type) |

---

## Event Correlation Patterns

### Pattern 1: Request-Response Correlation

**Use Case:** Gateway correlates backend operation completion with original request

```
1. Gateway receives user request
   → generates trace_id = "abc123"

2. Gateway routes to chora-compose
   → passes trace_id in request context

3. chora-compose generates content
   → emits event: chora.content_generated(trace_id="abc123")

4. Gateway receives event via file watching
   → correlates with original request via trace_id
   → returns result to user
```

**Implementation:**
- Gateway MUST generate trace_id for each incoming request
- Gateway MUST pass trace_id to backend (implementation-specific: env var, header, etc.)
- Backend MUST include trace_id in all emitted events

### Pattern 2: Multi-Step Workflow Tracking

**Use Case:** Track progress of multi-step workflow (e.g., weekly report)

```
workflow_id = "weekly-report-2025-10-17"
trace_id = "abc123"

Step 1: generate_content(intro)
  → chora.content_generated(trace_id="abc123", metadata={"step": 1, "workflow_id": "..."})

Step 2: generate_content(summary)
  → chora.content_generated(trace_id="abc123", metadata={"step": 2, "workflow_id": "..."})

Step 3: assemble_artifact(report)
  → chora.artifact_assembled(trace_id="abc123", metadata={"workflow_id": "..."})

All events share trace_id → enables end-to-end tracking
```

**Implementation:**
- Workflow orchestrator generates single trace_id for entire workflow
- All steps in workflow use same trace_id
- Optional: Include `workflow_id` in metadata for logical grouping

### Pattern 3: Error Propagation

**Use Case:** Backend error bubbles up to gateway with context

```
1. Gateway calls chora:generate_content
   trace_id = "abc123"

2. chora-compose encounters error (missing template variable)
   → emits event:
   {
     "event_type": "chora.content_generated",
     "trace_id": "abc123",
     "status": "failure",
     "error_code": "ERR_TEMPLATE_VARIABLE_MISSING",
     "error_message": "Template variable 'author' not found in context",
     "metadata": {
       "template": "report-intro.j2",
       "missing_variable": "author"
     }
   }

3. Gateway receives event
   → correlates with request via trace_id
   → returns structured error to user with full context
```

---

## Event Type Specifications

### Event: `chora.content_generated`

**Purpose:** Content generation operation completed

**Required Fields:** (in addition to universal required fields)
```json
{
  "event_type": "chora.content_generated",
  "content_config_id": "weekly-report-intro"
}
```

**Optional Fields (Metadata):**
```json
{
  "generator_type": "jinja2",
  "duration_ms": 234,
  "size_bytes": 1024,
  "metadata": {
    "template": "report-intro.j2",
    "context_keys": ["week", "team", "author"]
  }
}
```

**Example:**
```json
{
  "timestamp": "2025-10-17T12:00:00.123Z",
  "trace_id": "abc123",
  "status": "success",
  "schema_version": "1.0",
  "event_type": "chora.content_generated",
  "content_config_id": "weekly-report-intro",
  "generator_type": "jinja2",
  "duration_ms": 234,
  "size_bytes": 1024,
  "metadata": {
    "template": "report-intro.j2",
    "context_keys": ["week", "team"]
  }
}
```

---

### Event: `chora.artifact_assembled`

**Purpose:** Artifact assembly operation completed

**Required Fields:**
```json
{
  "event_type": "chora.artifact_assembled",
  "artifact_config_id": "weekly-report"
}
```

**Optional Fields (Metadata):**
```json
{
  "duration_ms": 1234,
  "section_count": 4,
  "output_path": "output/weekly-report-2025-10-17.md",
  "size_bytes": 5120,
  "metadata": {
    "sections": ["intro", "github", "jira", "metrics"]
  }
}
```

---

### Event: `chora.validation_completed`

**Purpose:** Validation check completed

**Required Fields:**
```json
{
  "event_type": "chora.validation_completed",
  "target_id": "weekly-report-intro"
}
```

**Optional Fields (Metadata):**
```json
{
  "duration_ms": 50,
  "errors_count": 0,
  "warnings_count": 2,
  "metadata": {
    "validators_run": ["presence", "format"],
    "warnings": ["Line length exceeded in 2 places"]
  }
}
```

---

### Event: `gateway.tool_call`

**Purpose:** Gateway routed tool call to backend

**Required Fields:**
```json
{
  "event_type": "gateway.tool_call",
  "backend": "chora-composer",
  "namespace": "chora",
  "tool": "generate_content"
}
```

**Optional Fields (Metadata):**
```json
{
  "duration_ms": 250,
  "metadata": {
    "arguments": {"content_config_id": "weekly-report-intro"},
    "result_size_bytes": 1024,
    "backend_version": "1.1.1"
  }
}
```

---

### Event: `chora.capability_changed` (v1.3.0+)

**Purpose:** Platform capability updated (dynamic discovery)

**Required Fields:**
```json
{
  "event_type": "chora.capability_changed",
  "change_type": "generator_added"
}
```

**Change Types:**
- `generator_added` - New generator registered
- `generator_removed` - Generator unregistered
- `tool_added` - New MCP tool added
- `tool_removed` - MCP tool removed

**Optional Fields (Metadata):**
```json
{
  "metadata": {
    "generator_type": "sql_generator",
    "plugin_name": "chora-sql-plugin",
    "plugin_version": "1.0.0"
  }
}
```

---

## Versioning Strategy

### Schema Version Format

Events include `schema_version` field: `"schema_version": "1.0"`

- Format: MAJOR.MINOR (semver without patch)
- Example: `"1.0"`, `"1.1"`, `"2.0"`

### Version Bump Rules

**Minor Version Bump (1.0 → 1.1):**
- Add optional fields (backward compatible)
- Add new event types
- Extend enum values (e.g., new `status` values)

**Major Version Bump (1.0 → 2.0):**
- Change required fields
- Remove fields
- Change field types
- Change field semantics

### Backward Compatibility Policy

- Consumers MUST handle unknown `schema_version` gracefully
- Consumers SHOULD log warning for unknown versions
- Consumers MUST NOT fail on unknown optional fields
- Backward compatibility maintained for 1 major version
  - v1.x and v2.x supported simultaneously for 6 months
  - v3.x release removes v1.x support

### Example: Handling Unknown Schema Version

```python
def parse_event(event_json: dict):
    schema_version = event_json.get("schema_version", "1.0")

    if not schema_version.startswith("1."):
        log.warning(f"Unknown schema version: {schema_version}, attempting best-effort parse")

    # Parse universal required fields (stable across versions)
    timestamp = event_json["timestamp"]
    trace_id = event_json["trace_id"]
    status = event_json["status"]

    # Parse optional fields (may not exist in all versions)
    duration_ms = event_json.get("duration_ms")
    error_code = event_json.get("error_code")

    return Event(
        timestamp=timestamp,
        trace_id=trace_id,
        status=status,
        duration_ms=duration_ms,
        error_code=error_code
    )
```

---

## Trace Context Propagation

### Overview

Trace context enables end-to-end correlation of events across the gateway (mcp-n8n) and backend (chora-composer). This section defines HOW trace_id propagates between systems.

**Decision (Sprint 1 Day 3):** Use environment variable `CHORA_TRACE_ID`

### Propagation Mechanism

#### Gateway → Backend (mcp-n8n → chora-composer)

**mcp-n8n implementation:**
```python
import uuid

def generate_trace_id() -> str:
    """Generate new trace ID for request"""
    return str(uuid.uuid4())

async def call_backend_tool(backend: Backend, tool: str, arguments: dict):
    """Call backend tool with trace context"""
    trace_id = generate_trace_id()

    # Pass trace_id via environment variable
    result = subprocess.run(
        [backend.command, tool],
        env={
            **os.environ,
            "CHORA_TRACE_ID": trace_id  # Propagate trace context
        },
        input=json.dumps(arguments),
        capture_output=True
    )

    # Store trace_id for event correlation
    active_traces[trace_id] = {
        "backend": backend.name,
        "tool": tool,
        "start_time": time.time()
    }

    return result
```

#### Backend → Events (chora-composer)

**chora-composer implementation:**
```python
import os
import uuid

def get_trace_id() -> str:
    """Get trace ID from environment or generate new one"""
    trace_id = os.getenv("CHORA_TRACE_ID")
    if trace_id:
        return trace_id
    else:
        # Fallback: generate new trace ID
        return str(uuid.uuid4())

def emit_event(event_type: str, status: str, **metadata):
    """Emit event with trace context"""
    trace_id = get_trace_id()  # Read from environment

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": trace_id,  # Include in event
        "status": status,
        "schema_version": "1.0",
        "event_type": event_type,
        **metadata
    }

    # Write to file
    with open("var/telemetry/events.jsonl", "a") as f:
        f.write(json.dumps(event) + "\n")
```

### Event Correlation (Gateway)

**mcp-n8n event monitoring:**
```python
async def watch_events(event_file: Path):
    """Tail events file and correlate with requests"""
    with event_file.open("r") as f:
        f.seek(0, 2)  # Seek to end

        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(0.1)
                continue

            event = json.loads(line)
            trace_id = event.get("trace_id")

            if trace_id and trace_id in active_traces:
                # Correlate event with original request
                request = active_traces[trace_id]
                print(f"Event for {request['tool']}: {event['event_type']}")

                # Clean up completed traces
                if event["status"] in ["success", "failure"]:
                    del active_traces[trace_id]
```

### Testing Trace Propagation

**Integration test (Sprint 2 Day 3):**
```python
def test_trace_context_propagation():
    """Verify trace_id propagates from gateway to events"""
    trace_id = "test-trace-123"

    # Gateway sets environment variable
    os.environ["CHORA_TRACE_ID"] = trace_id

    # Call chora-compose tool
    emit_event("chora.content_generated", trace_id=trace_id, status="success")

    # Verify event includes correct trace_id
    with open("var/telemetry/events.jsonl") as f:
        events = [json.loads(line) for line in f]
        assert events[-1]["trace_id"] == trace_id
```

### Alternative Propagation Methods (Not Used)

**Option B: Command-line argument**
```bash
# Gateway passes trace_id as CLI arg
chora-compose generate --trace-id abc123

# Backend reads from CLI arg
trace_id = args.trace_id
```
**Rejected because:** Requires CLI parsing, less flexible

**Option C: Temporary context file**
```python
# Gateway writes trace context to file
with open("/tmp/chora-trace-context.json", "w") as f:
    json.dump({"trace_id": "abc123"}, f)

# Backend reads from file
with open("/tmp/chora-trace-context.json") as f:
    trace_id = json.load(f)["trace_id"]
```
**Rejected because:** File I/O overhead, cleanup complexity

**Decision:** Environment variable is simplest, most flexible

---

## Implementation Guidance

### Event Emission (chora-compose)

```python
import json
from datetime import datetime, timezone
from pathlib import Path

def emit_event(event_type: str, trace_id: str, status: str, **metadata):
    """Emit event to var/telemetry/events.jsonl"""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": trace_id,
        "status": status,
        "schema_version": "1.0",
        "event_type": event_type,
        **metadata
    }

    event_file = Path("var/telemetry/events.jsonl")
    event_file.parent.mkdir(parents=True, exist_ok=True)

    with event_file.open("a") as f:
        f.write(json.dumps(event) + "\n")
```

### Event Consumption (mcp-n8n)

```python
import json
from pathlib import Path

async def watch_events(event_file: Path, handler: Callable):
    """Tail events file and handle new events"""
    with event_file.open("r") as f:
        # Seek to end (only process new events)
        f.seek(0, 2)

        while True:
            line = f.readline()
            if not line:
                await asyncio.sleep(0.1)  # Wait for new events
                continue

            try:
                event = json.loads(line)
                await handler(event)
            except json.JSONDecodeError:
                log.error(f"Invalid event JSON: {line}")
```

---

## Testing

### Schema Validation

Use JSON Schema validator to ensure events match specification:

```python
import jsonschema

EVENT_SCHEMA = {
    "type": "object",
    "required": ["timestamp", "trace_id", "status"],
    "properties": {
        "timestamp": {"type": "string", "format": "date-time"},
        "trace_id": {"type": "string"},
        "status": {"type": "string", "enum": ["success", "failure", "pending", "cancelled"]},
        "schema_version": {"type": "string"},
        "duration_ms": {"type": "integer", "minimum": 0},
        "error_code": {"type": "string"},
        "error_message": {"type": "string"},
        "metadata": {"type": "object"}
    }
}

def validate_event(event: dict):
    jsonschema.validate(event, EVENT_SCHEMA)
```

### Integration Tests

Test event correlation across services:

```python
async def test_event_correlation():
    """Test that gateway can correlate backend events via trace_id"""
    trace_id = generate_trace_id()

    # Gateway makes request
    result = await gateway.call_tool("chora:generate_content", trace_id=trace_id)

    # Wait for backend event
    event = await wait_for_event(event_type="chora.content_generated", trace_id=trace_id)

    # Validate correlation
    assert event["trace_id"] == trace_id
    assert event["status"] == "success"
```

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-17 | Initial specification | chora-compose team |

---

## Approval

**chora-compose Team:** [ ] Approved
**mcp-n8n Team:** [ ] Approved

**Next Review:** Week 2 (joint schema review meeting)
