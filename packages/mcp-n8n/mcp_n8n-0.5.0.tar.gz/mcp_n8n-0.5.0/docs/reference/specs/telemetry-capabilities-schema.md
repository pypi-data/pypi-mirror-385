# Telemetry Capabilities Schema Specification

**Version:** 1.0.0-draft
**Status:** DRAFT (for Sprint 4 implementation)
**Last Updated:** 2025-10-17
**Owner:** Joint (mcp-n8n + chora-composer)

---

## Purpose

This document defines the schema for the `capabilities://telemetry` MCP resource that chora-composer will expose in v1.2.0. This resource enables gateways (like mcp-n8n) to discover:

1. **What events** the backend emits
2. **Event schemas** for validation
3. **Sampling configuration** for performance tuning
4. **Export format and location** for file-based consumption

**Why This Matters:**
- Prevents "I wish this had X" moment in Sprint 5
- Enables auto-generation of telemetry documentation
- Supports forward compatibility (new event types discoverable)

---

## Resource URI

```
capabilities://telemetry
```

**MCP Protocol:**
```json
{
  "method": "resources/read",
  "params": {
    "uri": "capabilities://telemetry"
  }
}
```

---

## Schema

### Response Format

```json
{
  "uri": "capabilities://telemetry",
  "mimeType": "application/json",
  "contents": {
    "event_types": [...],
    "metrics": [...],
    "sampling_config": {...},
    "export_config": {...},
    "trace_context": {...}
  }
}
```

### Field Definitions

#### `event_types` (required)

Array of event type definitions:

```json
{
  "event_types": [
    {
      "name": "chora.content_generated",
      "description": "Content generation operation completed",
      "frequency": "per_operation",
      "schema": {
        "type": "object",
        "required": ["content_config_id"],
        "properties": {
          "content_config_id": {"type": "string"},
          "generator_type": {"type": "string"},
          "duration_ms": {"type": "integer"},
          "size_bytes": {"type": "integer"}
        }
      }
    }
  ]
}
```

**Field Specifications:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Event type identifier (namespaced, e.g., `chora.content_generated`) |
| `description` | string | Human-readable description |
| `frequency` | enum | `per_operation`, `periodic`, `on_change` |
| `schema` | object | JSON Schema for event-specific payload fields |

---

#### `metrics` (optional)

Array of metric names that may appear in event metadata:

```json
{
  "metrics": [
    "generation_duration_ms",
    "artifact_size_bytes",
    "validation_errors_count"
  ]
}
```

**Purpose:** Helps consumers know what numeric values to aggregate/visualize.

---

#### `sampling_config` (optional)

Sampling configuration for performance tuning:

```json
{
  "sampling_config": {
    "sampling_rate": 1.0,
    "adaptive_sampling": false,
    "excluded_event_types": []
  }
}
```

**Field Specifications:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sampling_rate` | float | 1.0 | Fraction of events to emit (0.0-1.0) |
| `adaptive_sampling` | boolean | false | Whether sampling rate adjusts based on load |
| `excluded_event_types` | array | [] | Event types never emitted (optimization) |

---

#### `export_config` (required)

Configuration for how events are exported:

```json
{
  "export_config": {
    "format": "jsonl",
    "location": "var/telemetry/events.jsonl",
    "rotation_policy": {
      "max_size_bytes": 10_485_760,
      "max_age_days": 90
    },
    "compression": "none"
  }
}
```

**Field Specifications:**

| Field | Type | Description |
|-------|------|-------------|
| `format` | enum | `jsonl`, `json`, `csv` (currently only `jsonl`) |
| `location` | string | Relative path from chora-compose root |
| `rotation_policy` | object | File rotation configuration |
| `compression` | enum | `none`, `gzip`, `bzip2` |

---

#### `trace_context` (required)

Trace context configuration for distributed tracing:

```json
{
  "trace_context": {
    "propagation_method": "environment_variable",
    "environment_variable_name": "CHORA_TRACE_ID",
    "format": "uuid",
    "opentelemetry_compatible": true
  }
}
```

**Field Specifications:**

| Field | Type | Description |
|-------|------|-------------|
| `propagation_method` | enum | `environment_variable`, `cli_argument`, `http_header` |
| `environment_variable_name` | string | Name of env var (if applicable) |
| `format` | enum | `uuid`, `hex32`, `opentelemetry` |
| `opentelemetry_compatible` | boolean | Whether trace IDs follow OpenTelemetry spec |

---

## Complete Example

```json
{
  "uri": "capabilities://telemetry",
  "mimeType": "application/json",
  "contents": {
    "event_types": [
      {
        "name": "chora.content_generated",
        "description": "Content generation operation completed",
        "frequency": "per_operation",
        "schema": {
          "type": "object",
          "required": ["content_config_id"],
          "properties": {
            "content_config_id": {"type": "string"},
            "generator_type": {"type": "string"},
            "duration_ms": {"type": "integer"},
            "size_bytes": {"type": "integer"},
            "metadata": {"type": "object"}
          }
        }
      },
      {
        "name": "chora.artifact_assembled",
        "description": "Artifact assembly operation completed",
        "frequency": "per_operation",
        "schema": {
          "type": "object",
          "required": ["artifact_config_id"],
          "properties": {
            "artifact_config_id": {"type": "string"},
            "output_path": {"type": "string"},
            "section_count": {"type": "integer"},
            "size_bytes": {"type": "integer"},
            "duration_ms": {"type": "integer"},
            "metadata": {"type": "object"}
          }
        }
      },
      {
        "name": "chora.validation_completed",
        "description": "Validation check completed",
        "frequency": "per_operation",
        "schema": {
          "type": "object",
          "required": ["target_id"],
          "properties": {
            "target_id": {"type": "string"},
            "errors_count": {"type": "integer"},
            "warnings_count": {"type": "integer"},
            "duration_ms": {"type": "integer"}
          }
        }
      }
    ],
    "metrics": [
      "generation_duration_ms",
      "artifact_size_bytes",
      "validation_errors_count",
      "section_count"
    ],
    "sampling_config": {
      "sampling_rate": 1.0,
      "adaptive_sampling": false,
      "excluded_event_types": []
    },
    "export_config": {
      "format": "jsonl",
      "location": "var/telemetry/events.jsonl",
      "rotation_policy": {
        "max_size_bytes": 10485760,
        "max_age_days": 90
      },
      "compression": "none"
    },
    "trace_context": {
      "propagation_method": "environment_variable",
      "environment_variable_name": "CHORA_TRACE_ID",
      "format": "uuid",
      "opentelemetry_compatible": true
    }
  }
}
```

---

## Usage Examples

### Consumer: mcp-n8n Gateway

#### Sprint 4: Discover Event Types

```python
# Query telemetry capabilities
response = await backend.get_resource("capabilities://telemetry")
telemetry_caps = response["contents"]

# Extract event types
event_types = [et["name"] for et in telemetry_caps["event_types"]]
print(event_types)
# ['chora.content_generated', 'chora.artifact_assembled', 'chora.validation_completed']

# Get schema for specific event type
content_gen_schema = next(
    et["schema"] for et in telemetry_caps["event_types"]
    if et["name"] == "chora.content_generated"
)
```

#### Sprint 5: Auto-Generate Telemetry Documentation

```python
# Build Grafana dashboard from telemetry capabilities
for event_type in telemetry_caps["event_types"]:
    schema = event_type["schema"]
    metrics = [
        prop for prop, spec in schema["properties"].items()
        if spec["type"] in ["integer", "number"]
    ]

    print(f"Event: {event_type['name']}")
    print(f"  Metrics: {metrics}")
    # Event: chora.content_generated
    #   Metrics: ['duration_ms', 'size_bytes']
```

#### Sprint 5: Validate Incoming Events

```python
import jsonschema

# Load telemetry capabilities
telemetry_caps = await backend.get_resource("capabilities://telemetry")

# Parse incoming event
event = json.loads(event_line)

# Find schema for event type
event_schema = next(
    et["schema"] for et in telemetry_caps["event_types"]
    if et["name"] == event["event_type"]
)

# Validate event payload
jsonschema.validate(event, event_schema)
# Raises ValidationError if invalid
```

---

## Implementation Guidance (Sprint 4)

### chora-composer Implementation

**File:** `src/chora_compose/mcp/resources/telemetry.py`

```python
from pathlib import Path

async def get_telemetry_capabilities() -> dict[str, Any]:
    """Return telemetry capabilities for gateway discovery"""
    return {
        "event_types": [
            {
                "name": "chora.content_generated",
                "description": "Content generation operation completed",
                "frequency": "per_operation",
                "schema": {
                    "type": "object",
                    "required": ["content_config_id"],
                    "properties": {
                        "content_config_id": {"type": "string"},
                        "generator_type": {"type": "string"},
                        "duration_ms": {"type": "integer"},
                        "size_bytes": {"type": "integer"},
                        "metadata": {"type": "object"}
                    }
                }
            },
            # ... other event types
        ],
        "metrics": [
            "generation_duration_ms",
            "artifact_size_bytes",
            "validation_errors_count"
        ],
        "sampling_config": {
            "sampling_rate": 1.0,
            "adaptive_sampling": False,
            "excluded_event_types": []
        },
        "export_config": {
            "format": "jsonl",
            "location": "var/telemetry/events.jsonl",
            "rotation_policy": {
                "max_size_bytes": 10_485_760,  # 10MB
                "max_age_days": 90
            },
            "compression": "none"
        },
        "trace_context": {
            "propagation_method": "environment_variable",
            "environment_variable_name": "CHORA_TRACE_ID",
            "format": "uuid",
            "opentelemetry_compatible": True
        }
    }
```

**Registration:**
```python
# In MCP server initialization
mcp.resource("capabilities://telemetry")(get_telemetry_capabilities)
```

---

## Versioning

### Schema Version

Include schema version in response for future evolution:

```json
{
  "schema_version": "1.0",
  "event_types": [...]
}
```

### Evolution Strategy

**Minor version bump (1.0 → 1.1):**
- Add new event types
- Add optional fields to existing schemas
- Add new metrics

**Major version bump (1.0 → 2.0):**
- Remove event types
- Change required fields
- Change field semantics

---

## Open Questions (For Review)

**Q1:** Should we include event examples in the schema?
- **Pro:** Helps developers understand event structure
- **Con:** Increases response size
- **Proposal:** Add optional `example` field to each event type

**Q2:** Should sampling_rate be configurable at runtime?
- **Pro:** Allows dynamic performance tuning
- **Con:** Adds complexity
- **Proposal:** Defer to v1.3.0 (context bus integration)

**Q3:** Should we expose event emission statistics?
- **Pro:** Helps diagnose sampling/volume issues
- **Con:** Adds overhead
- **Proposal:** Add optional `statistics` field (events_emitted, events_dropped)

---

## Approval

**chora-compose Team:** [ ] Approved (sign off before Sprint 4)
**mcp-n8n Team:** [ ] Approved (sign off before Sprint 4)

**Next Review:** Sprint 5 (after consumption in mcp-n8n)

---

## Document Metadata

**Version:** 1.0.0-draft
**Status:** DRAFT
**Authors:** mcp-n8n team (spec author), chora-composer team (implementer)
**Approval Date:** TBD
**Next Review:** Sprint 5 (validate against real usage)

**Related Documents:**
- [event-schema.md](event-schema.md) - Event format specification
- [UNIFIED_ROADMAP.md](../../UNIFIED_ROADMAP.md) - Sprint 1 Day 3, Sprint 4 Day 3
- [CROSS_TEAM_COORDINATION.md](../CROSS_TEAM_COORDINATION.md) - Spec approval process

**Change Log:**
- 2025-10-17: Initial draft based on Sprint 1 requirements gathering
