# Correct Architecture for chora-compose Integration

**Date:** 2025-10-20
**Source:** chora-compose team response to change request
**Status:** Reference documentation for future Sprint 5 implementation

---

## Executive Summary

This document captures the **correct architecture** for integrating mcp-n8n workflows with chora-compose, based on clarifications from the chora-compose team.

**Key Insight:** chora-compose is a **framework/engine** (like Jinja2), not a template library. Each project creates its own templates and configs, then points chora-compose to them.

---

## Architecture Principles

### 1. Template/Config Ownership

```
✅ CORRECT:
mcp-n8n owns templates     → mcp-n8n/chora-configs/templates/
mcp-n8n owns configs       → mcp-n8n/chora-configs/content/
chora-compose loads them   → via CHORA_CONFIG_PATH env var

❌ WRONG:
Templates added to chora-compose repo
Configs added to chora-compose repo
```

**Analogy:**
- chora-compose is like Jinja2 (the template engine)
- You don't submit your Flask templates to the Jinja2 repository
- Similarly, mcp-n8n templates belong in mcp-n8n, not chora-compose

### 2. Tool Usage Pattern

#### generate_content Tool

**Signature:**
```python
generate_content(
    content_config_id: str,  # ID of content config (NOT template ID!)
    context: dict,           # Runtime context to merge with config context
    force: bool = False      # Force regeneration (ignore cache)
) -> dict
```

**What it does:**
1. Loads content config from `CHORA_CONFIG_PATH/content/{content_config_id}.json`
2. Content config references template via `generation.patterns[0].template` field
3. Merges runtime `context` with config's `generation_config.context`
4. Renders template using specified generator (jinja2, demonstration, etc.)
5. Stores result in ephemeral storage
6. Returns generated content + metadata

**Response format:**
```python
{
    "success": True,
    "content": "# Daily Report...",  # Rendered content
    "generator": "jinja2",
    "duration_ms": 45,
    "content_id": "daily-report",
    "timestamp": "2025-10-20T12:34:56Z"
}
```

#### assemble_artifact Tool

**When to use:**
- Only when combining **multiple content pieces** into one artifact
- Example: intro + body + conclusion from separate configs
- NOT needed for single-template reports

**Our daily report:** Single template → Use `generate_content` only

### 3. Ephemeral Storage

**Current behavior (v1.4.2):**
- ALL content from `generate_content` goes to ephemeral storage
- Retention: **30 days** (hardcoded, not configurable per-config)
- Location: `chora-compose/ephemeral/<content_id>/<timestamp>.txt`
- Auto-cleanup: Not implemented yet

**For custom retention (e.g., 7 days):**
```python
# After generating reports, clean up old ones
await backend.call_tool("cleanup_ephemeral", {
    "content_ids": ["daily-report"],
    "keep_days": 7,
    "dry_run": False
})
```

---

## Implementation Guide

### Step 1: Create Config Structure

```bash
mkdir -p chora-configs/content
mkdir -p chora-configs/templates
```

### Step 2: Create Content Config

**File:** `chora-configs/content/daily-report.json`

```json
{
  "type": "content",
  "id": "daily-report",
  "schemaRef": {
    "id": "content-schema",
    "version": "3.1"
  },
  "metadata": {
    "description": "Daily engineering report for mcp-n8n gateway",
    "version": "1.0.0",
    "output_format": "markdown"
  },
  "generation": {
    "patterns": [
      {
        "id": "daily-report-generation",
        "type": "jinja2",
        "template": "daily-report.md.j2",
        "generation_config": {
          "context": {
            "date": {"source": "runtime"},
            "generated_at": {"source": "runtime"},
            "since_hours": {"source": "runtime"},
            "commits": {"source": "runtime"},
            "stats": {"source": "runtime"}
          }
        }
      }
    ]
  }
}
```

**Key fields:**
- `id`: Used in `generate_content(content_config_id="daily-report")`
- `generation.patterns[0].template`: Path to Jinja2 template file
- `generation.patterns[0].type`: Generator to use (jinja2, demonstration, code_generation, etc.)
- `generation_config.context`: Declares what context variables template expects

### Step 3: Create Jinja2 Template

**File:** `chora-configs/templates/daily-report.md.j2`

```jinja2
# Daily Engineering Report - {{ date }}

## Summary

**Date:** {{ date }}
**Generated:** {{ generated_at }}
**Coverage:** Last {{ since_hours }} hours

### Key Metrics

- **Commits:** {{ commits | length }}
- **Events:** {{ stats.total_events }}
- **Tool Calls:** {{ stats.tool_usage | length }}
- **Success Rate:** {{ "%.1f" | format(stats.success_rate) }}%

## Recent Commits ({{ commits | length }})

{% for commit in commits %}
- **{{ commit.hash }}** ({{ commit.author }}): {{ commit.message }}
  - Time: {{ commit.timestamp }}
  - Files: {{ commit.files_changed }}
{% else %}
*No commits in this period*
{% endfor %}

## Gateway Activity

### Events by Type
{% if stats.by_type %}
{% for type, count in stats.by_type.items() %}
- {{ type }}: {{ count }}
{% endfor %}
{% else %}
*No events in this period*
{% endif %}

### Tool Usage
{% if stats.tool_usage %}
{% for tool, count in stats.tool_usage.items() %}
- {{ tool }}: {{ count }} calls
{% endfor %}
{% else %}
*No tool calls recorded*
{% endif %}

### Performance
- **Success Rate:** {{ "%.1f" | format(stats.success_rate) }}%
- **Backends Active:** {{ stats.by_backend | length }}
- **Total Events:** {{ stats.total_events }}

---

*Generated by mcp-n8n gateway + chora-compose*
```

### Step 4: Configure chora-compose

**Option A: Environment Variable**
```bash
export CHORA_CONFIG_PATH=/path/to/mcp-n8n/chora-configs
python -m chora_compose.mcp.server
```

**Option B: Backend Config (mcp-n8n)**
```python
# In src/mcp_n8n/config.py
chora_config = BackendConfig(
    name="chora-composer",
    command="python3.12",
    args=["-m", "chora_compose.mcp.server"],
    env={
        "CHORA_CONFIG_PATH": str(Path(__file__).parent.parent / "chora-configs"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", "")
    }
)
```

### Step 5: Update Workflow Code

**File:** `src/mcp_n8n/workflows/daily_report.py`

```python
async def run_daily_report(
    date: str | None = None,
    repository_path: str | None = None,
    since_hours: int = 24,
    output_format: Literal["markdown", "html"] = "markdown",
) -> DailyReportResult:
    """Generate a daily engineering report using chora-compose."""

    # 1. Gather data (mcp-n8n responsibility)
    commits = await get_recent_commits(repository_path, since_hours)

    from mcp_n8n.memory.event_log import EventLog
    event_log = EventLog()
    since_time = datetime.now(UTC) - timedelta(hours=since_hours)
    events = event_log.query(since=since_time, limit=1000)

    stats = aggregate_statistics(events)

    # 2. Prepare context for template
    context = {
        "date": date or datetime.now(UTC).date().isoformat(),
        "generated_at": datetime.now(UTC).isoformat(),
        "since_hours": since_hours,
        "commits": commits,
        "stats": stats
    }

    # 3. Get chora-compose backend
    from mcp_n8n.gateway import get_backend_registry
    registry = get_backend_registry()
    backend = registry.get_backend_by_namespace("chora")

    if not backend:
        raise RuntimeError("chora-compose backend not available")

    # 4. Generate content using chora-compose
    result = await backend.call_tool("generate_content", {
        "content_config_id": "daily-report",  # ← Matches config "id" field
        "context": context,                   # ← Runtime context
        "force": True                         # ← Force regeneration
    })

    # 5. Handle result
    if not result.get("success"):
        raise RuntimeError(f"Generation failed: {result.get('error')}")

    report_content = result["content"]

    # 6. Optionally write to file (content already in ephemeral storage)
    report_path = f"reports/daily-report-{context['date']}.md"
    Path(report_path).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text(report_content)

    return {
        "status": "success",
        "report_path": report_path,
        "summary": {
            "commit_count": len(commits),
            "event_count": stats["total_events"],
            "tool_calls": len(stats["tool_usage"]),
            "success_rate": stats["success_rate"],
            "backends_active": list(stats["by_backend"].keys())
        },
        "error": None
    }
```

**Key changes:**
1. ✅ Single `generate_content` call (not assemble_artifact)
2. ✅ Pass `content_config_id` parameter (not template_id)
3. ✅ Runtime context merged with config context
4. ✅ Result contains rendered content directly
5. ✅ Content automatically stored in ephemeral storage

---

## Common Mistakes to Avoid

### ❌ Wrong: Passing template_id
```python
# This parameter doesn't exist!
await backend.call_tool("generate_content", {
    "template_id": "daily-report",  # ← NO!
    "context": {...}
})
```

### ✅ Correct: Passing content_config_id
```python
await backend.call_tool("generate_content", {
    "content_config_id": "daily-report",  # ← YES!
    "context": {...}
})
```

### ❌ Wrong: Using assemble_artifact for single template
```python
# Don't use assemble_artifact unless combining multiple pieces!
content = await backend.call_tool("generate_content", {...})
artifact = await backend.call_tool("assemble_artifact", {
    "sections": [content]  # ← Unnecessary!
})
```

### ✅ Correct: Use generate_content directly
```python
# Single template = single generate_content call
result = await backend.call_tool("generate_content", {
    "content_config_id": "daily-report",
    "context": {...}
})
# result["content"] is the final markdown
```

### ❌ Wrong: Expecting per-config retention
```python
# This doesn't work! No retention_days field in configs
{
  "storage": {
    "type": "ephemeral",
    "retention_days": 7  # ← Doesn't exist!
  }
}
```

### ✅ Correct: Use cleanup_ephemeral tool
```python
# After generating, clean up old versions
await backend.call_tool("cleanup_ephemeral", {
    "content_ids": ["daily-report"],
    "keep_days": 7,
    "dry_run": False
})
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ mcp-n8n Repository                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  chora-configs/                     ← OUR templates/configs │
│  ├── content/                                               │
│  │   └── daily-report.json          Content config          │
│  │       • id: "daily-report"                               │
│  │       • template: "daily-report.md.j2"                   │
│  │       • generator: "jinja2"                              │
│  │                                                           │
│  └── templates/                                             │
│      └── daily-report.md.j2          Jinja2 template        │
│          • Variables: date, commits, stats                  │
│          • Loops, conditionals, filters                     │
│                                                             │
│  workflows/                                                 │
│  └── daily_report.py                 Workflow code          │
│      • Gather: commits, events                              │
│      • Call: generate_content(content_config_id, context)   │
│      • Save: result to file                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                        ↓
              MCP JSON-RPC (stdio)
              CHORA_CONFIG_PATH=/path/to/mcp-n8n/chora-configs
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ chora-compose (Framework)                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  MCP Server:                                                │
│  • Loads configs from CHORA_CONFIG_PATH                     │
│  • Exposes MCP tools via stdio                              │
│                                                             │
│  generate_content(content_config_id, context):              │
│  1. Load config: CHORA_CONFIG_PATH/content/{id}.json        │
│  2. Get template path from config                           │
│  3. Load template: CHORA_CONFIG_PATH/templates/{path}       │
│  4. Merge runtime context with config context               │
│  5. Render template with merged context                     │
│  6. Store in ephemeral/ (30-day retention)                  │
│  7. Return rendered content                                 │
│                                                             │
│  ephemeral/                          Auto-managed storage   │
│  └── daily-report/                                          │
│      ├── 2025-10-20T12:00:00.txt                            │
│      ├── 2025-10-20T18:00:00.txt                            │
│      └── ...                         (30-day retention)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Timeline

### Current State (Sprint 3)
- ✅ Workflow implemented with manual string generation
- ✅ 17/17 tests passing
- ✅ EventLog integration working
- ✅ JSON-RPC foundation complete

### Future Implementation (Sprint 5)
1. **Create config structure** (30 min)
   - `chora-configs/content/daily-report.json`
   - `chora-configs/templates/daily-report.md.j2`

2. **Update workflow code** (30 min)
   - Replace manual generation with `generate_content` call
   - Add backend lookup and error handling

3. **Configure backend** (15 min)
   - Set `CHORA_CONFIG_PATH` in backend config
   - Update tests to use real chora integration

4. **Test end-to-end** (30 min)
   - Verify content generation works
   - Verify ephemeral storage
   - Update tests if needed

**Total effort:** ~2 hours for full integration

### Why Defer to Sprint 5?
- Current implementation works (17/17 tests)
- Sprint 3 focused on validation and learning
- Sprint 5 focused on production workflows
- Better to refactor when building production features

---

## Related Documents

- [chora-compose-change-request-daily-report.md](chora-compose-change-request-daily-report.md) - Original (withdrawn) request
- [daily-report-api-reference.md](daily-report-api-reference.md) - Workflow API documentation
- [../change-requests/sprint-3-daily-report/completion-summary.md](../change-requests/sprint-3-daily-report/completion-summary.md) - Sprint 3 completion

---

## Questions for chora-compose Team

If you have questions during implementation:

1. **Config schema validation:** How to validate content config against schema?
2. **Template discovery:** Can we list available templates via MCP tool?
3. **Error handling:** What errors can `generate_content` return?
4. **Context merging:** Exactly how runtime context merges with config context?
5. **HTML output:** How to configure for HTML instead of Markdown?

**Contact:** File issue on chora-compose repository with tag `question`

---

**Status:** Reference documentation complete
**Next Action:** Implement in Sprint 5 production workflows
**Timeline:** 2 hours estimated for full integration
