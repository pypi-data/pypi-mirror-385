# Workflows Directory

This directory contains n8n workflow definitions in JSON format.

## Purpose

Store version-controlled n8n workflow definitions that can be:
1. Imported into n8n instances
2. Documented automatically via chora-compose
3. Tracked in git for version history
4. Shared across environments

## Directory Structure

```
workflows/
├── daily-report.json           # Daily engineering report workflow
├── error-alerts.json           # Error alert notifications (future)
└── README.md                   # This file
```

## Workflow Definitions

### daily-report.json

Daily engineering report generator that:
1. Gathers git commits from last 24 hours
2. Queries gateway events from EventLog
3. Calls chora:generate_content to format report
4. Outputs Markdown report or sends to Slack

**Trigger:** Manual or scheduled (daily at 9 AM)

**Tools Used:**
- Git (bash command)
- EventLog query (via mcp-n8n)
- chora:generate_content (via chora-compose backend)

**See:** [Daily Report Implementation](../src/mcp_n8n/workflows/daily_report.py)

## Using These Workflows

### Option 1: Import into n8n

```bash
# Export from n8n UI
n8n export:workflow --id=1 --output=workflows/my-workflow.json

# Import into n8n
n8n import:workflow --input=workflows/daily-report.json
```

### Option 2: Execute via mcp-n8n (Pattern N2)

If n8n is configured as an MCP backend:

```python
from mcp_n8n.backends import get_registry

registry = get_registry()
n8n_backend = registry.get_backend_by_namespace("n8n")

# Execute workflow
result = await n8n_backend.call_tool("n8n:execute_workflow", {
    "workflow_id": "daily-report-generator",
    "parameters": {
        "date": "2025-10-20",
        "since_hours": 24
    }
})
```

### Option 3: Execute via Python (Direct)

For workflows implemented in Python:

```python
from mcp_n8n.workflows.daily_report import run_daily_report

result = await run_daily_report(
    backend_registry=registry,
    event_log=event_log,
    repo_path=".",
    since_hours=24
)
```

## Creating New Workflows

### 1. Design Workflow in n8n UI

Create workflow with nodes and connections.

### 2. Export Workflow JSON

```bash
n8n export:workflow --id=<workflow-id> --output=workflows/my-workflow.json
```

### 3. Add Metadata

Edit JSON to add metadata:

```json
{
  "name": "My Workflow",
  "meta": {
    "description": "What this workflow does",
    "version": "1.0.0",
    "author": "mcp-n8n",
    "tags": ["automation", "reports"]
  },
  "nodes": [...],
  "connections": {...}
}
```

### 4. Document Workflow

Use chora-compose to auto-generate documentation:

```python
# Read workflow JSON
with open("workflows/my-workflow.json") as f:
    workflow_def = json.load(f)

# Generate docs
result = await backend.call_tool("generate_content", {
    "content_config_id": "workflow-docs",
    "context": {"workflow": workflow_def}
})

# Save docs
with open("docs/workflows/my-workflow.md", "w") as f:
    f.write(result["content"])
```

## Event-Driven Workflows

Workflows can be triggered automatically by events via EventWorkflowRouter.

**Configuration:** `config/event_mappings.yaml`

**Example:**
```yaml
mappings:
  - event_pattern:
      type: "gateway.tool_call"
      status: "failure"
    workflow:
      id: "error-alert-workflow"
      parameters:
        error: "{{ event.data.error }}"
```

**See:** [Event Routing Documentation](../docs/architecture/n8n-chora-compose-integration.md)

## Workflow Best Practices

1. **Version Control:** Commit workflow JSON to git
2. **Meaningful Names:** Use descriptive workflow IDs
3. **Add Metadata:** Include description, version, author
4. **Error Handling:** Add error handling nodes
5. **Logging:** Log workflow execution to EventLog
6. **Testing:** Test workflows with sample data before deploying
7. **Documentation:** Auto-generate docs from workflow JSON

## Related Documentation

- [n8n Integration Guide](../docs/N8N_INTEGRATION_GUIDE.md)
- [n8n + chora-compose Integration](../docs/architecture/n8n-chora-compose-integration.md)
- [Sprint 5 Intent](../docs/change-requests/sprint-5-workflows/intent.md)

---

**Note:** Workflow definitions are version-controlled. Export updated workflows after modifications.
