# Daily Report Workflow Specification

**Version:** 1.0
**Date:** 2025-10-19
**Status:** DRAFT
**Sprint:** Sprint 5 - Production Workflows

---

## Overview

The Daily Report workflow demonstrates mcp-n8n + chora-compose integration by generating a daily engineering report that aggregates:
- Recent GitHub commits
- Recent events from the gateway telemetry
- Summary of tool usage and performance

This is a **validation workflow** designed to:
- De-risk the full stack integration
- Test event monitoring in a real workflow
- Validate artifact creation end-to-end
- Build confidence before complex production workflows

---

## Workflow Specification

### Inputs

| Input | Type | Source | Required | Default |
|-------|------|--------|----------|---------|
| `date` | ISO date string | Parameter or `today` | No | Today's date |
| `repository` | string | Parameter | No | "liminalcommons/mcp-n8n" |
| `since_hours` | integer | Parameter | No | 24 |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `report_path` | string | Path to generated markdown report |
| `summary` | object | Key metrics (commits, events, tools used) |
| `status` | string | "success" or "failure" |

### Workflow Steps

```
┌─────────────────────────────────────────────────────────────────┐
│ Daily Report Workflow                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Gather Data                                                  │
│     ├─ Get recent commits (GitHub API or git log)               │
│     ├─ Query gateway events (get_events tool)                   │
│     └─ Aggregate statistics                                     │
│         └─ Tool usage counts                                    │
│         └─ Event types                                          │
│         └─ Success/failure rates                                │
│                                                                  │
│  2. Generate Content                                             │
│     ├─ Call chora:generate_content                              │
│     │   └─ template: "daily-report"                             │
│     │   └─ context: { commits, events, stats }                  │
│     └─ Receive generated markdown sections                      │
│                                                                  │
│  3. Assemble Artifact                                            │
│     ├─ Call chora:assemble_artifact                             │
│     │   └─ config_id: "daily-report"                            │
│     │   └─ content: generated sections                          │
│     └─ Receive artifact path                                    │
│                                                                  │
│  4. Emit Event & Return                                          │
│     ├─ Emit workflow completion event                           │
│     └─ Return report path and summary                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Sources

### 1. GitHub Commits (Past 24 Hours)

**Method:** Git log (local) or GitHub API (if available)

**Local Git Command:**
```bash
git log --since="24 hours ago" --pretty=format:"%h|%an|%s|%ai" --no-merges
```

**Output Format:**
```python
commits = [
    {
        "hash": "abc1234",
        "author": "Victor Piper",
        "message": "feat: Add event monitoring",
        "timestamp": "2025-10-19T10:30:00Z"
    },
    ...
]
```

### 2. Gateway Events (Past 24 Hours)

**Method:** Use `get_events` MCP tool

**Query:**
```python
events = await get_events(
    since="24h",
    limit=100
)
```

**Event Aggregation:**
```python
stats = {
    "total_events": len(events),
    "by_type": Counter(e["event_type"] for e in events),
    "by_status": Counter(e["status"] for e in events),
    "by_backend": Counter(e.get("metadata", {}).get("backend") for e in events)
}
```

### 3. Tool Usage Statistics

**Method:** Filter events for "gateway.tool_call" type

```python
tool_calls = [e for e in events if e["event_type"] == "gateway.tool_call"]
tool_usage = Counter(e["metadata"]["tool"] for e in tool_calls)
```

---

## Chora-Compose Integration

### Content Generation

**Template:** `daily-report`

**Template Structure:**
```jinja2
# Daily Engineering Report - {{ date }}

## Summary

{{ summary }}

## Recent Commits ({{ commits | length }})

{% for commit in commits %}
- **{{ commit.hash }}** ({{ commit.author }}): {{ commit.message }}
  - Time: {{ commit.timestamp }}
{% endfor %}

## Gateway Activity

**Total Events:** {{ stats.total_events }}

### Events by Type
{% for type, count in stats.by_type.items() %}
- {{ type }}: {{ count }}
{% endfor %}

### Tool Usage
{% for tool, count in tool_usage.items() %}
- {{ tool }}: {{ count }} calls
{% endfor %}

## Performance

- Success Rate: {{ stats.success_rate }}%
- Backends Active: {{ stats.backends_active }}
```

**Context Data:**
```python
context = {
    "date": "2025-10-19",
    "summary": "Generated report summary...",
    "commits": commits_data,
    "stats": aggregated_stats,
    "tool_usage": tool_usage_counts
}
```

### Artifact Assembly

**Config ID:** `daily-report`

**Output Specification:**
```yaml
artifact_type: "markdown"
output_path: "reports/daily/{{ date }}.md"
metadata:
  report_date: "{{ date }}"
  generated_at: "{{ timestamp }}"
  workflow: "daily-report"
```

---

## Implementation Options

### Option 1: Python Script (Recommended for MVP)

**Why:** Simplest to implement, test, and debug

**Structure:**
```python
# workflows/daily_report.py

async def run_daily_report(date: str = None) -> dict:
    """Generate daily engineering report."""
    # 1. Gather data
    commits = await get_recent_commits(since_hours=24)
    events = await get_events(since="24h")
    stats = aggregate_statistics(events)

    # 2. Generate content
    content = await chora_generate_content(
        template="daily-report",
        context={"date": date, "commits": commits, "stats": stats}
    )

    # 3. Assemble artifact
    artifact = await chora_assemble_artifact(
        config_id="daily-report",
        content=content
    )

    # 4. Return summary
    return {
        "status": "success",
        "report_path": artifact["path"],
        "summary": stats
    }
```

**Benefits:**
- Easy to test (pytest)
- Can reuse existing mcp-n8n infrastructure
- Good for documentation/tutorial
- Validates integration without n8n dependency

### Option 2: n8n Workflow JSON

**Why:** Production-ready, visual workflow editor

**Structure:**
```json
{
  "name": "Daily Engineering Report",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "value": 24}]
        }
      }
    },
    {
      "name": "Get Commits",
      "type": "n8n-nodes-base.executeCommand",
      "parameters": {
        "command": "git log --since='24 hours ago' ..."
      }
    },
    {
      "name": "Query Events (MCP)",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "{{ $env.MCP_GATEWAY_URL }}/tools/get_events",
        "method": "POST",
        "body": {"since": "24h"}
      }
    },
    {
      "name": "Generate Report (Chora)",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "{{ $env.MCP_GATEWAY_URL }}/tools/chora:generate_content",
        "method": "POST",
        "body": {
          "template": "daily-report",
          "context": "{{ $json }}"
        }
      }
    },
    {
      "name": "Assemble Artifact (Chora)",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "{{ $env.MCP_GATEWAY_URL }}/tools/chora:assemble_artifact",
        "method": "POST",
        "body": {
          "config_id": "daily-report",
          "content": "{{ $json.content }}"
        }
      }
    }
  ]
}
```

**Benefits:**
- Visual workflow
- Easy to modify
- Production-ready scheduling
- Demonstrates real-world usage

### Option 3: Both (Recommended)

**Approach:**
1. Build Python script first (easy to test, validate integration)
2. Convert to n8n JSON once working (production deployment)
3. Document both approaches (maximum utility)

**Timeline:**
- Day 1: Python script implementation
- Day 2: n8n JSON conversion + testing
- Day 3: Documentation + tutorial

---

## Testing Strategy

### Unit Tests

```python
# tests/workflows/test_daily_report.py

def test_aggregate_statistics(sample_events):
    """Test event aggregation logic."""
    stats = aggregate_statistics(sample_events)
    assert stats["total_events"] == len(sample_events)
    assert "by_type" in stats
    assert "success_rate" in stats

@pytest.mark.asyncio
async def test_get_recent_commits():
    """Test commit retrieval."""
    commits = await get_recent_commits(since_hours=24)
    assert isinstance(commits, list)
    for commit in commits:
        assert "hash" in commit
        assert "author" in commit
        assert "message" in commit
```

### Integration Tests

```python
@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_end_to_end():
    """Test full workflow end-to-end."""
    result = await run_daily_report()

    assert result["status"] == "success"
    assert "report_path" in result
    assert Path(result["report_path"]).exists()

    # Verify report content
    content = Path(result["report_path"]).read_text()
    assert "# Daily Engineering Report" in content
    assert "## Recent Commits" in content
    assert "## Gateway Activity" in content
```

### Manual Testing

1. **Run workflow locally:**
   ```bash
   python -m workflows.daily_report
   ```

2. **Verify output:**
   - Check report file exists in `reports/daily/`
   - Review generated content
   - Validate all sections populated

3. **Test with n8n:**
   - Import workflow JSON
   - Configure endpoints
   - Execute manually
   - Verify output

---

## Deliverables

1. **Python Implementation:**
   - `src/mcp_n8n/workflows/daily_report.py`
   - Unit tests in `tests/workflows/`
   - Integration tests

2. **n8n Workflow:**
   - `workflows/n8n/daily-report.json`
   - Import instructions
   - Configuration guide

3. **Documentation:**
   - This spec document
   - Tutorial: "Building Your First Workflow"
   - How-to guide: "Customizing the Daily Report"

4. **Chora Template:**
   - `templates/daily-report.jinja2` (in chora-compose)
   - Artifact configuration

---

## Success Criteria

- [ ] Python script runs successfully
- [ ] All tests passing (unit + integration)
- [ ] Report generated with actual data
- [ ] n8n workflow imports and runs
- [ ] Documentation complete
- [ ] Tutorial validated by fresh user
- [ ] Performance <5s total workflow time

---

## Timeline

**Total:** 2-3 days

**Day 1:** Python implementation + tests
- Morning: Data gathering functions
- Afternoon: Chora integration
- Evening: End-to-end test

**Day 2:** n8n conversion + validation
- Morning: Convert to n8n JSON
- Afternoon: Test in n8n
- Evening: Refinements

**Day 3:** Documentation + polish
- Morning: Write tutorial
- Afternoon: Test with fresh eyes
- Evening: Final review

---

## Next Steps

1. ✅ Review this spec
2. Create chora-compose template (`daily-report.jinja2`)
3. Implement Python workflow
4. Write tests
5. Convert to n8n JSON
6. Document everything

---

**Questions/Clarifications Needed:**

1. Should we use GitHub API or just local git log?
2. Where should chora-compose templates live? (assuming in chora-compose repo)
3. Should the workflow be scheduled or manual trigger initially?
4. Any specific metrics/data points to include beyond commits and events?
