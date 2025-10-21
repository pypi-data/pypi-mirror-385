---
title: "Build Event-Driven Workflows"
type: tutorial
audience: intermediate
estimated_time: "30 minutes"
prerequisites: ["mcp-n8n installed", "Gateway running", "Understanding of events"]
test_extraction: yes
source: "src/mcp_n8n/workflows/event_router.py, tests/features/sprint_5_workflows.feature"
last_updated: 2025-10-21
---

# Tutorial: Build Event-Driven Workflows

## What You'll Build

An **event-driven workflow system** that automatically triggers workflows in response to gateway events. You'll use the `EventWorkflowRouter` to route events like failed tool calls to error-handling workflows.

**What happens:**
```
Event occurs → Router matches pattern → Workflow triggered → Action taken
```

**Example:** When a tool call fails, automatically trigger an error alert workflow.

## What You'll Learn

- How to create event-to-workflow mappings in YAML
- How to use pattern matching to route events
- How to template workflow parameters from event data
- How to enable hot-reload for config changes
- How to handle multiple event patterns

## Prerequisites

- [x] mcp-n8n installed and gateway running
- [x] Understanding of [Event Schema](../reference/event-schema.md)
- [x] Completed [First Workflow tutorial](first-workflow.md) (recommended)
- [x] Text editor for YAML configuration

## Time Required

Approximately 30 minutes

---

## Step 1: Understand Event-Driven Workflows

**What we're doing:** Learn the event-driven workflow pattern

### Traditional vs Event-Driven

**Traditional (manual trigger):**
```python
# You manually call the workflow
result = await run_daily_report(...)
```

**Event-Driven (automatic trigger):**
```python
# Workflow runs automatically when event occurs
# Event: gateway.tool_call (status: failure)
# → Router detects pattern match
# → Triggers: error-alert-workflow
# → Action: Send notification, log error, retry
```

### Key Components

1. **Events** - Emitted by gateway when things happen
   - `gateway.tool_call` - Tool invocation
   - `gateway.backend_started` - Backend initialization
   - `workflow.failed` - Workflow error

2. **Event Router** - Matches events to workflows
   - Pattern matching (field-based rules)
   - Parameter templating (Jinja2)
   - Hot-reload (config changes without restart)

3. **Workflow** - Action to perform
   - Error handling
   - Notifications
   - Data processing

**Router location:** [src/mcp_n8n/workflows/event_router.py](../../src/mcp_n8n/workflows/event_router.py)

---

## Step 2: Create Event Mappings Configuration

**What we're doing:** Define which events trigger which workflows

**Instructions:**

1. Create config directory:
   ```bash
   mkdir -p config
   ```

2. Create `config/event_mappings.yaml`:
   ```yaml
   # Event-to-workflow mappings
   mappings:
     # Mapping 1: Failed tool calls → Error alert
     - event_pattern:
         type: "gateway.tool_call"
         status: "failure"
       workflow:
         id: "error-alert-workflow"
         namespace: "workflows"
         parameters:
           tool: "{{ event.metadata.tool_name }}"
           error: "{{ event.metadata.error }}"
           timestamp: "{{ event.timestamp }}"
   ```

3. Verify the file exists:
   ```bash
   cat config/event_mappings.yaml
   ```

**Expected output:**
```yaml
mappings:
  - event_pattern:
      type: "gateway.tool_call"
      status: "failure"
    workflow:
      id: "error-alert-workflow"
...
```

**Explanation:**
- `event_pattern` - Defines what events to match
- `workflow.id` - Which workflow to trigger
- `parameters` - Data to pass (using Jinja2 templates)

---

## Step 3: Initialize the Event Router

**What we're doing:** Create and configure EventWorkflowRouter in Python

**Instructions:**

Create `event_driven_example.py`:

```python
import asyncio
from pathlib import Path
from mcp_n8n.workflows.event_router import EventWorkflowRouter
from mcp_n8n.backends import BackendRegistry

async def main():
    # Initialize backend registry
    registry = BackendRegistry()

    # Create event router with config file
    router = EventWorkflowRouter(
        config_path="config/event_mappings.yaml",
        backend_registry=registry
    )

    # Load mappings from YAML
    mappings = await router.load_mappings()

    print(f"✓ Event router initialized")
    print(f"  Loaded {len(mappings)} mapping(s)")

    for i, mapping in enumerate(mappings, 1):
        pattern = mapping['event_pattern']
        workflow = mapping['workflow']
        print(f"\n  Mapping {i}:")
        print(f"    Pattern: {pattern}")
        print(f"    Workflow: {workflow['id']}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Run it:**
```bash
python event_driven_example.py
```

**Expected output:**
```
✓ Event router initialized
  Loaded 1 mapping(s)

  Mapping 1:
    Pattern: {'type': 'gateway.tool_call', 'status': 'failure'}
    Workflow: error-alert-workflow
```

**What just happened:**
- Router read the YAML configuration
- Validated the mapping structure
- Loaded 1 event-to-workflow mapping
- Router is now ready to match events

---

## Step 4: Test Pattern Matching

**What we're doing:** Match events against patterns to trigger workflows

**Instructions:**

Add to `event_driven_example.py`:

```python
async def test_pattern_matching():
    """Test matching events against patterns."""
    registry = BackendRegistry()
    router = EventWorkflowRouter(
        config_path="config/event_mappings.yaml",
        backend_registry=registry
    )
    await router.load_mappings()

    # Simulate a failed tool call event
    failed_event = {
        "timestamp": "2025-10-21T14:32:10.123456+00:00",
        "trace_id": "abc123",
        "type": "gateway.tool_call",
        "status": "failure",
        "metadata": {
            "tool_name": "chora:generate_content",
            "error": "Template not found",
            "duration_ms": 150
        }
    }

    # Try to match the event
    match = await router.match_event(failed_event)

    if match:
        print("✓ Event matched!")
        print(f"  Workflow: {match['workflow_id']}")
        print(f"  Parameters: {match['parameters']}")
    else:
        print("✗ No match found")

# Run the test
asyncio.run(test_pattern_matching())
```

**Expected output:**
```
✓ Event matched!
  Workflow: error-alert-workflow
  Parameters: {
    'tool': 'chora:generate_content',
    'error': 'Template not found',
    'timestamp': '2025-10-21T14:32:10.123456+00:00'
  }
```

**What just happened:**
1. We created a mock event with `type: "gateway.tool_call"` and `status: "failure"`
2. The router checked all patterns (1 in this case)
3. Pattern matched because both `type` and `status` fields matched
4. Router templated parameters using Jinja2
5. Returned workflow ID and templated parameters

---

## Step 5: Add Multiple Event Patterns

**What we're doing:** Configure multiple mappings for different event types

**Instructions:**

Update `config/event_mappings.yaml` to add more patterns:

```yaml
mappings:
  # Pattern 1: Failed tool calls → Error alert
  - event_pattern:
      type: "gateway.tool_call"
      status: "failure"
    workflow:
      id: "error-alert-workflow"
      namespace: "workflows"
      parameters:
        tool: "{{ event.metadata.tool_name }}"
        error: "{{ event.metadata.error }}"

  # Pattern 2: All tool calls → Logger (for analytics)
  - event_pattern:
      type: "gateway.tool_call"
    workflow:
      id: "tool-call-logger"
      namespace: "workflows"
      parameters:
        tool: "{{ event.metadata.tool_name }}"
        status: "{{ event.status }}"

  # Pattern 3: Backend registration → Notification
  - event_pattern:
      type: "gateway.backend_registered"
      status: "success"
    workflow:
      id: "backend-notification"
      namespace: "workflows"
      parameters:
        backend: "{{ event.metadata.backend_name }}"
        namespace: "{{ event.metadata.namespace }}"
```

**Test with different events:**

```python
async def test_multiple_patterns():
    """Test matching different event types."""
    registry = BackendRegistry()
    router = EventWorkflowRouter(
        config_path="config/event_mappings.yaml",
        backend_registry=registry
    )
    await router.load_mappings()

    # Test case 1: Failed tool call (matches Pattern 1)
    failed_event = {
        "type": "gateway.tool_call",
        "status": "failure",
        "metadata": {"tool_name": "chora:generate", "error": "Timeout"}
    }
    match1 = await router.match_event(failed_event)
    print(f"Failed tool call → {match1['workflow_id'] if match1 else 'No match'}")

    # Test case 2: Success tool call (matches Pattern 2 only)
    success_event = {
        "type": "gateway.tool_call",
        "status": "success",
        "metadata": {"tool_name": "gateway_status"}
    }
    match2 = await router.match_event(success_event)
    print(f"Success tool call → {match2['workflow_id'] if match2 else 'No match'}")

    # Test case 3: Backend registered (matches Pattern 3)
    backend_event = {
        "type": "gateway.backend_registered",
        "status": "success",
        "metadata": {"backend_name": "chora-composer", "namespace": "chora"}
    }
    match3 = await router.match_event(backend_event)
    print(f"Backend registered → {match3['workflow_id'] if match3 else 'No match'}")

asyncio.run(test_multiple_patterns())
```

**Expected output:**
```
Failed tool call → error-alert-workflow
Success tool call → tool-call-logger
Backend registered → backend-notification
```

**Explanation:**
- **Pattern order matters** - First matching pattern wins
- Failed tool call matches Pattern 1 (exact match on both fields)
- Success tool call matches Pattern 2 (partial match - only type specified)
- Backend registered matches Pattern 3 (exact match)

---

## Step 6: Use Jinja2 Parameter Templating

**What we're doing:** Extract data from events into workflow parameters

**Instructions:**

Understanding template syntax:

```yaml
parameters:
  # Simple field access
  tool: "{{ event.metadata.tool_name }}"

  # Nested field access
  error_message: "{{ event.metadata.error }}"

  # Multiple fields in one string
  description: "Tool {{ event.metadata.tool_name }} failed: {{ event.metadata.error }}"

  # Conditional values
  severity: "{{ 'high' if event.status == 'failure' else 'low' }}"
```

**Test parameter templating:**

```python
async def test_parameter_templating():
    """Test Jinja2 parameter templating."""
    # Update config with advanced templating
    config_content = """
mappings:
  - event_pattern:
      type: "gateway.tool_call"
      status: "failure"
    workflow:
      id: "error-alert-workflow"
      parameters:
        # Simple extraction
        tool: "{{ event.metadata.tool_name }}"
        error: "{{ event.metadata.error }}"

        # Computed values
        severity: "{{ 'critical' if 'timeout' in event.metadata.error.lower() else 'warning' }}"

        # String composition
        message: "ALERT: {{ event.metadata.tool_name }} failed with error: {{ event.metadata.error }}"

        # Timestamp formatting
        occurred_at: "{{ event.timestamp }}"
"""

    # Write config
    Path("config/event_mappings.yaml").write_text(config_content)

    # Initialize router
    registry = BackendRegistry()
    router = EventWorkflowRouter(
        config_path="config/event_mappings.yaml",
        backend_registry=registry
    )
    await router.load_mappings()

    # Test event
    event = {
        "timestamp": "2025-10-21T14:32:10Z",
        "type": "gateway.tool_call",
        "status": "failure",
        "metadata": {
            "tool_name": "chora:generate_content",
            "error": "Connection timeout after 30s"
        }
    }

    match = await router.match_event(event)

    print("Templated parameters:")
    for key, value in match['parameters'].items():
        print(f"  {key}: {value}")

asyncio.run(test_parameter_templating())
```

**Expected output:**
```
Templated parameters:
  tool: chora:generate_content
  error: Connection timeout after 30s
  severity: critical
  message: ALERT: chora:generate_content failed with error: Connection timeout after 30s
  occurred_at: 2025-10-21T14:32:10Z
```

---

## Step 7: Enable Hot-Reload

**What we're doing:** Auto-reload config when YAML file changes (no restart needed)

**Instructions:**

```python
import asyncio
from pathlib import Path
from mcp_n8n.workflows.event_router import EventWorkflowRouter
from mcp_n8n.backends import BackendRegistry

async def demo_hot_reload():
    """Demonstrate hot-reload functionality."""
    registry = BackendRegistry()
    router = EventWorkflowRouter(
        config_path="config/event_mappings.yaml",
        backend_registry=registry
    )
    await router.load_mappings()

    # Start file watching (hot-reload)
    await router.start_watching()
    print("✓ File watching started (hot-reload enabled)")
    print(f"  Watching: config/event_mappings.yaml")
    print(f"  Current mappings: {len(router.mappings)}")

    # Simulate config change
    print("\n📝 Modifying config file...")

    # Add a new mapping
    config_path = Path("config/event_mappings.yaml")
    current_content = config_path.read_text()
    new_mapping = """
  # Pattern 4: Workflow completed → Analytics
  - event_pattern:
      type: "workflow.completed"
    workflow:
      id: "analytics-logger"
      parameters:
        workflow: "{{ event.metadata.workflow_name }}"
        duration: "{{ event.metadata.duration_ms }}"
"""
    config_path.write_text(current_content + new_mapping)

    # Wait for file watcher to detect change
    print("  Waiting for auto-reload...")
    await asyncio.sleep(2)  # Give watcher time to detect and reload

    print(f"✓ Config reloaded!")
    print(f"  New mapping count: {len(router.mappings)}")

    # Stop watching
    await router.stop_watching()
    print("\n✓ File watching stopped")

asyncio.run(demo_hot_reload())
```

**Expected output:**
```
✓ File watching started (hot-reload enabled)
  Watching: config/event_mappings.yaml
  Current mappings: 3

📝 Modifying config file...
  Waiting for auto-reload...
✓ Config reloaded!
  New mapping count: 4

✓ File watching stopped
```

**What just happened:**
1. Router started with 3 mappings
2. File watcher monitors `event_mappings.yaml`
3. We modified the file (added 4th mapping)
4. Watcher detected change within 1 second
5. Router auto-reloaded config (no restart)
6. Router now has 4 mappings

**Implementation:** Uses `watchdog` library to monitor file system changes

---

## Step 8: Handle Edge Cases

**What we're doing:** Learn how router handles special cases

### Case 1: No Pattern Matches

```python
# Event that doesn't match any pattern
unmatched_event = {
    "type": "coda.document_updated",  # No pattern for this
    "status": "success"
}

match = await router.match_event(unmatched_event)
# match = None (no workflow triggered)

if match is None:
    print("No workflow found for this event type")
```

---

### Case 2: Partial Pattern Match

```python
# Pattern only specifies 'type', not 'status'
# Config:
# event_pattern:
#   type: "gateway.tool_call"
# (no status specified)

# Event with any status will match
event1 = {"type": "gateway.tool_call", "status": "success"}  # ✓ Matches
event2 = {"type": "gateway.tool_call", "status": "failure"}  # ✓ Matches
event3 = {"type": "gateway.tool_call", "status": "pending"}  # ✓ Matches
```

**Rule:** Pattern must be a subset of event (all pattern fields must match)

---

### Case 3: Invalid YAML Syntax

```python
# If config file has syntax errors
# Router keeps previous valid config

try:
    await router.load_mappings()
except yaml.YAMLError as e:
    print(f"Invalid YAML: {e}")
    print("Previous config still active")
```

---

### Case 4: Missing Template Variables

```python
# Config:
# parameters:
#   tool: "{{ event.metadata.tool_name }}"

# Event missing metadata.tool_name
event = {
    "type": "gateway.tool_call",
    "metadata": {}  # tool_name missing!
}

# Router handles gracefully
match = await router.match_event(event)
# match['parameters']['tool'] = "" (empty string)
```

---

## What You've Learned

Summary of skills acquired:

- ✅ You can now **create event-to-workflow mappings** in YAML
- ✅ You understand **pattern matching rules** (exact vs partial)
- ✅ You know how to **template parameters** with Jinja2
- ✅ You can **enable hot-reload** for config changes
- ✅ You understand **mapping priority** (first match wins)
- ✅ You can **handle edge cases** (no match, missing data)

## Next Steps

Where to go from here:

- [ ] **[How-To: Build Custom Workflow](../how-to/build-custom-workflow.md)**: Implement actual workflow logic
- [ ] **[How-To: Query Events](../how-to/query-events.md)**: Monitor workflow execution
- [ ] **[Reference: Event Schema](../reference/event-schema.md)**: Learn all event types
- [ ] **[Tutorial: First Workflow](first-workflow.md)**: Build the workflows that get triggered

## Real-World Patterns

### Pattern 1: Error Alerting System

```yaml
mappings:
  # Alert on any failure
  - event_pattern:
      status: "failure"
    workflow:
      id: "error-alert"
      parameters:
        event_type: "{{ event.type }}"
        error: "{{ event.metadata.error }}"
        severity: "{{ 'critical' if 'timeout' in event.metadata.error else 'warning' }}"
```

### Pattern 2: Performance Monitoring

```yaml
mappings:
  # Log slow tool calls
  - event_pattern:
      type: "gateway.tool_call"
    workflow:
      id: "performance-monitor"
      parameters:
        tool: "{{ event.metadata.tool_name }}"
        duration: "{{ event.metadata.duration_ms }}"
        slow: "{{ event.metadata.duration_ms > 5000 }}"
```

### Pattern 3: Workflow Orchestration

```yaml
mappings:
  # Trigger daily report when backend starts
  - event_pattern:
      type: "gateway.backend_registered"
      metadata:
        backend_name: "chora-composer"
    workflow:
      id: "daily-report-workflow"
      parameters:
        since_hours: 24

  # Trigger cleanup when workflow completes
  - event_pattern:
      type: "workflow.completed"
      metadata:
        workflow_name: "daily-report"
    workflow:
      id: "cleanup-workflow"
      parameters:
        report_path: "{{ event.metadata.report_path }}"
```

---

## Troubleshooting

### Problem: FileNotFoundError on initialization

**Symptoms:**
```
FileNotFoundError: Config file not found: config/event_mappings.yaml
```

**Solution:**
```bash
# Create config directory
mkdir -p config

# Create config file
cat > config/event_mappings.yaml <<EOF
mappings: []
EOF
```

---

### Problem: ValueError - Invalid config structure

**Symptoms:**
```
ValueError: Invalid config structure. Expected: mappings: ...
```

**Cause:** YAML structure is wrong

**Solution:**
```yaml
# ✓ Correct
mappings:
  - event_pattern:
      type: "..."
    workflow:
      id: "..."

# ✗ Wrong
- event_pattern:  # Missing "mappings:" key
```

---

### Problem: Event not matching pattern

**Symptoms:** `match = None` even though pattern looks right

**Debug steps:**
```python
# Print event structure
print("Event:", json.dumps(event, indent=2))

# Print pattern
print("Pattern:", mapping['event_pattern'])

# Check field-by-field
pattern = mapping['event_pattern']
for key, value in pattern.items():
    event_value = event.get(key)
    matches = event_value == value
    print(f"{key}: pattern={value}, event={event_value}, match={matches}")
```

---

**Source:** [src/mcp_n8n/workflows/event_router.py](../../src/mcp_n8n/workflows/event_router.py), [tests/features/sprint_5_workflows.feature](../../tests/features/sprint_5_workflows.feature)
**Test Extraction:** Yes
**Last Updated:** 2025-10-21
