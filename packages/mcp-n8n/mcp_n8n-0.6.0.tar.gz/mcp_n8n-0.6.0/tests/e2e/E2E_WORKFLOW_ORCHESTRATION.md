# E2E Test Suite: Workflow Orchestration

**Version:** v1.0.0
**Duration:** 20-25 minutes
**Purpose:** Validate Sprint 5 event-driven workflow orchestration features
**Prerequisites:** Complete [E2E_EVENT_MONITORING.md](E2E_EVENT_MONITORING.md) first
**Last Updated:** October 21, 2025

---

## Overview

This suite validates **Sprint 5 workflow orchestration** - event-to-workflow routing, pattern matching, parameter templating, and the Daily Report workflow.

### What You'll Test

**Components:**
- EventWorkflowRouter - Event pattern matching and routing
- Daily Report Workflow - Git + telemetry aggregation
- Config hot-reload - Dynamic configuration updates

**Configuration:**
- `config/event_mappings.yaml` - Event-to-workflow mappings
- `chora-configs/templates/` - Report templates

**Key Features:**
- Pattern-based event matching
- Jinja2 parameter templating
- Hot-reload without restart
- Template-based reporting

---

## Test 1: EventWorkflowRouter - Pattern Matching

### Step 1.1: Exact Pattern Match

**Prompt:**
```
Looking at config/event_mappings.yaml, find the pattern for:
  event_pattern:
    type: "gateway.tool_call"
    status: "failure"

If a tool call fails, what workflow is triggered?
```

**Success Criteria:**
- [ ] Pattern matches only when both type AND status match
- [ ] workflow_id = "error-alert-workflow"
- [ ] namespace = "n8n"
- [ ] Parameters are templated from event

**Expected Mapping:**
```yaml
event_pattern:
  type: "gateway.tool_call"
  status: "failure"
workflow:
  id: "error-alert-workflow"
  namespace: "n8n"
  parameters:
    error: "{{ event.data.error }}"
    tool: "{{ event.data.tool_name }}"
```

### Step 1.2: Partial Pattern Match

**Prompt:**
```
Find the pattern that matches ANY tool call:
  event_pattern:
    type: "gateway.tool_call"

What is different about this pattern compared to Step 1.1?
```

**Success Criteria:**
- [ ] Pattern matches with only type field
- [ ] Accepts any status value
- [ ] workflow_id = "tool-call-logger"
- [ ] First matching pattern wins (order matters!)

**Key Insight:** Event with status="failure" matches BOTH patterns, but first one wins.

### Step 1.3: Nested Field Patterns

**Prompt:**
```
Find the pattern for backend status changes:
  event_pattern:
    type: "gateway.backend_status"
    backend: "chora-composer"

Does this match events for other backends?
```

**Success Criteria:**
- [ ] Matches only chora-composer backend events
- [ ] Other backends ignored
- [ ] Supports nested field matching
- [ ] workflow_id = "chora-status-monitor"

---

## Test 2: Parameter Templating

### Step 2.1: Simple Template Substitution

**Prompt:**
```
Given this event:
{
  "type": "gateway.tool_call",
  "status": "failure",
  "data": {
    "tool_name": "generate_content",
    "error": "Template not found"
  },
  "trace_id": "abc123",
  "timestamp": "2025-10-21T14:00:00Z"
}

And this parameter template:
  error: "{{ event.data.error }}"
  tool: "{{ event.data.tool_name }}"

What are the resolved parameter values?
```

**Success Criteria:**
- [ ] error = "Template not found"
- [ ] tool = "generate_content"
- [ ] Jinja2 syntax processed correctly
- [ ] Nested fields accessed (event.data.*)

**Expected Output:**
```json
{
  "error": "Template not found",
  "tool": "generate_content",
  "trace_id": "abc123",
  "timestamp": "2025-10-21T14:00:00Z"
}
```

### Step 2.2: Missing Field Handling

**Prompt:**
```
What happens if the template references a field that doesn't exist?
Example: "{{ event.data.nonexistent_field }}"
```

**Success Criteria:**
- [ ] Missing fields result in empty string or None
- [ ] No error thrown
- [ ] Workflow still triggers
- [ ] Graceful degradation

### Step 2.3: List/Array Templating

**Prompt:**
```
Can parameter templates handle lists?
Example template:
  items: "{{ event.data.items }}"

With event.data.items = ["a", "b", "c"]
```

**Success Criteria:**
- [ ] Lists preserved as JSON
- [ ] Each item accessible
- [ ] Can iterate in workflow
- [ ] Structure maintained

---

## Test 3: Daily Report Workflow

### Step 3.1: Generate Basic Report

**Prompt:**
```
How would you trigger the Daily Report workflow to generate a report for the last 24 hours?
(Note: May require CLI or direct function call - check implementation)

What information is included in the report?
```

**Success Criteria:**
- [ ] Report generated successfully
- [ ] Includes git commits from last 24h
- [ ] Includes gateway events from last 24h
- [ ] Statistics aggregated (tool calls, success rate)
- [ ] Rendered using chora-compose template

**Expected Report Sections:**
1. **Git Activity:**
   - Commit count
   - Authors
   - File changes
   - Commit messages (summary)

2. **Gateway Telemetry:**
   - Total tool calls
   - Success/failure breakdown
   - Average duration
   - Most used tools

3. **Events Timeline:**
   - Key events from period
   - Trace correlation
   - Error summary

### Step 3.2: Custom Time Range

**Prompt:**
```
Generate a report for:
- Last 12 hours (since_hours=12)
- Last 7 days (since_hours=168)

How does the report content change?
```

**Success Criteria:**
- [ ] Time range parameter honored
- [ ] Git commits filtered correctly
- [ ] Events filtered by timestamp
- [ ] Statistics recalculated for range

### Step 3.3: Report Output Format

**Prompt:**
```
What format is the Daily Report output in?
Is it Markdown, HTML, JSON, or something else?
```

**Success Criteria:**
- [ ] Output format is Markdown
- [ ] Uses chora-compose template rendering
- [ ] Stored in ephemeral storage (7-day retention)
- [ ] Includes metadata (generation time, parameters)

**Expected Output Structure:**
```json
{
  "content": "# Daily Engineering Report\n\n## Git Activity\n...",
  "commit_count": 15,
  "event_count": 234,
  "statistics": {
    "tool_calls": 45,
    "success_rate": 0.95,
    "avg_duration_ms": 320
  },
  "metadata": {
    "generated_at": "2025-10-21T14:30:00Z",
    "time_range": "24h",
    "trace_id": "report_xyz"
  }
}
```

---

## Test 4: Git Integration

### Step 4.1: Commit Retrieval

**Prompt:**
```
The Daily Report workflow calls get_recent_commits().
What git information is extracted from each commit?
```

**Success Criteria:**
- [ ] Hash (SHA)
- [ ] Author name
- [ ] Commit message
- [ ] Timestamp (ISO 8601)
- [ ] Files changed count

**Expected Commit Structure:**
```json
{
  "hash": "abc123def456",
  "author": "John Doe",
  "message": "feat: Add new feature",
  "timestamp": "2025-10-21T13:45:00Z",
  "files_changed": 5
}
```

### Step 4.2: Branch Filtering

**Prompt:**
```
Can the Daily Report be generated for a specific branch?
Or does it always use the current branch?
```

**Success Criteria:**
- [ ] Supports branch parameter (optional)
- [ ] Defaults to current branch
- [ ] Branch name included in report
- [ ] Accurate commit filtering

---

## Test 5: Statistics Aggregation

### Step 5.1: Tool Usage Stats

**Prompt:**
```
The report aggregates tool usage statistics.
What metrics are calculated?
```

**Success Criteria:**
- [ ] Total tool calls
- [ ] Success count / failure count
- [ ] Success rate percentage
- [ ] Tool calls by backend
- [ ] Tool calls by type
- [ ] Average duration

**Expected Statistics:**
```json
{
  "total_calls": 45,
  "successful": 43,
  "failed": 2,
  "success_rate": 0.956,
  "by_backend": {
    "chora-composer": 38,
    "coda-mcp": 7
  },
  "by_tool": {
    "chora:generate_content": 25,
    "chora:list_generators": 13,
    "coda:list_docs": 7
  },
  "avg_duration_ms": 320,
  "min_duration_ms": 15,
  "max_duration_ms": 4500
}
```

### Step 5.2: Event Type Distribution

**Prompt:**
```
Are event types aggregated and counted in the report?
Which event types are most common?
```

**Success Criteria:**
- [ ] Event types counted
- [ ] Sorted by frequency
- [ ] Includes percentage of total
- [ ] Top 10 event types shown

---

## Test 6: Template Rendering

### Step 6.1: chora-compose Integration

**Prompt:**
```
The Daily Report uses chora-compose for template rendering.
Where is the template stored?
```

**Success Criteria:**
- [ ] Template in chora-configs/templates/
- [ ] File: daily-report.md.j2
- [ ] Jinja2 syntax
- [ ] Context data passed from workflow

**Template Location:**
```
chora-configs/templates/daily-report.md.j2
```

### Step 6.2: Template Variables

**Prompt:**
```
What variables are available to the template?
```

**Success Criteria:**
- [ ] commits - List of git commits
- [ ] events - List of events
- [ ] statistics - Aggregated metrics
- [ ] metadata - Report generation info
- [ ] time_range - Report period

**Template Context:**
```python
{
  "commits": [...],
  "events": [...],
  "statistics": {...},
  "metadata": {
    "generated_at": "...",
    "report_date": "...",
    "time_range_hours": 24
  }
}
```

---

## Test 7: Config Hot-Reload

### Step 7.1: Modify Event Mappings

**Prompt:**
```
While the gateway is running:
1. Open config/event_mappings.yaml
2. Add a new mapping or modify an existing one
3. Save the file

Does the EventWorkflowRouter automatically reload the config?
```

**Success Criteria:**
- [ ] File modification detected (watchdog)
- [ ] Config reloaded automatically
- [ ] No gateway restart needed
- [ ] Log message confirms reload
- [ ] New mappings active immediately

**Expected Log:**
```
INFO: Config file modified: config/event_mappings.yaml
INFO: Reloading event mappings config
INFO: Successfully loaded 4 event mappings
```

### Step 7.2: Invalid Config Handling

**Prompt:**
```
Edit config/event_mappings.yaml and introduce a syntax error (invalid YAML).
What happens?
```

**Success Criteria:**
- [ ] Error detected during reload
- [ ] Previous config preserved (rollback)
- [ ] Error logged with details
- [ ] Gateway continues with old config
- [ ] No service disruption

**Expected Behavior:**
```
ERROR: Failed to reload config: YAML syntax error at line 15
INFO: Keeping previous configuration
```

### Step 7.3: Validate Reload Performance

**Prompt:**
```
How long does config reload take?
Is there any service interruption during reload?
```

**Success Criteria:**
- [ ] Reload completes in < 100ms
- [ ] No dropped events during reload
- [ ] Thread-safe reload operation
- [ ] Zero downtime

---

## Test 8: Workflow Trigger Integration

### Step 8.1: Manual Workflow Trigger

**Prompt:**
```
Can workflows be triggered manually (outside of events)?
Or are they event-driven only?
```

**Success Criteria:**
- [ ] Workflows can be triggered manually via backend
- [ ] Parameters can be provided directly
- [ ] No event required
- [ ] Useful for testing/debugging

### Step 8.2: Workflow Execution Tracking

**Prompt:**
```
When a workflow is triggered by an event:
1. Are workflow execution events captured?
2. Can you trace from trigger event → workflow → completion?
```

**Success Criteria:**
- [ ] Workflow execution events emitted
- [ ] trace_id links trigger → execution → result
- [ ] Can query workflow execution history
- [ ] Duration tracked

---

**Test Suite:** Workflow Orchestration
**Duration:** 20-25 minutes
**Components Tested:** EventWorkflowRouter, Daily Report, Hot-reload
**Status:** ✅ Sprint 5 features validated

---

## Next Steps

After completing this orchestration test:

1. ✅ **All tests pass:** Proceed to [E2E_ERROR_HANDLING.md](E2E_ERROR_HANDLING.md)
2. ⚠️ **Pattern matching issues:** Review event_mappings.yaml syntax
3. ⚠️ **Report generation fails:** Check chora-compose backend and templates
4. 📝 **Document:** Note workflow patterns and template customizations

## Troubleshooting

**Patterns not matching:**
- Check event structure matches pattern exactly
- Verify field names and nesting
- Remember: first matching pattern wins
- Review logs for pattern evaluation details

**Template rendering errors:**
- Ensure chora-compose backend is running
- Verify template file exists in chora-configs/
- Check template syntax (Jinja2)
- Review context data passed to template

**Hot-reload not working:**
- Verify watchdog library is installed
- Check file system events are supported
- Review EventWorkflowRouter logs
- Ensure config file path is correct

**Daily Report fails:**
- Check git repository is initialized
- Verify .chora/memory/events/ has data
- Ensure ANTHROPIC_API_KEY is set
- Review chora-compose backend logs
