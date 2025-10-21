# Question for chora-compose Team: Ephemeral Artifact Storage

**Date:** 2025-10-19
**Context:** Building Daily Report workflow for mcp-n8n Sprint 5
**Question Type:** Architecture / Design Pattern

---

## Background

We're building a **Daily Report workflow** in mcp-n8n that will:
1. Gather data (git commits, gateway events, tool usage stats)
2. Generate a daily engineering report via `chora:generate_content`
3. Assemble the report artifact via `chora:assemble_artifact`
4. Output/store the report for consumption

The workflow will run daily (scheduled in n8n) and produce a new report each day.

---

## Our Use Case

**Report Characteristics:**
- Generated daily (automated workflow)
- Contains time-bound data (commits from last 24 hours, events from last 24 hours)
- Typically consumed immediately or within a few hours
- May not need long-term persistence (value decreases over time)
- Expected size: 1-5 KB markdown file

**Current Workflow Pattern:**
```
Data Gathering → chora:generate_content → chora:assemble_artifact → ???
```

---

## The Question

**Is chora-compose designed to support ephemeral/temporary artifact storage for use cases like this?**

Specifically:

### Option 1: Ephemeral Storage (Our Preference)
```yaml
# Hypothetical artifact config
daily-report:
  output:
    path: /tmp/reports/daily/{{ date }}.md
    # OR
    ephemeral: true
    retention: 7_days  # Auto-cleanup after 7 days
```

**Benefits:**
- Prevents disk accumulation from daily reports
- Simpler management (no manual cleanup)
- Aligns with time-sensitive nature of data

**Questions:**
- Does chora-compose support output to `/tmp` or similar ephemeral locations?
- Is there a retention/cleanup mechanism for time-based artifacts?
- Can `assemble_artifact` be configured to skip persistent storage entirely (return content only)?

### Option 2: Persistent Storage (Fallback)
```yaml
# Standard artifact config
daily-report:
  output:
    path: reports/daily/{{ date }}.md
```

**Implications:**
- Reports accumulate in `reports/daily/` directory
- Requires external cleanup mechanism (cron job, workflow step)
- More disk management overhead

**Questions:**
- If we use persistent storage, should cleanup be external to chora-compose?
- Is there a recommended pattern for time-series artifacts (daily, weekly, etc.)?

### Option 3: Content-Only (No Storage)
```yaml
# Hypothetical
daily-report:
  output:
    storage: false  # Return content only, don't write to disk
```

**Use Case:**
- Workflow consumes the report content immediately (e.g., posts to Slack, sends email)
- No need to persist to disk at all

**Questions:**
- Can `assemble_artifact` return content without writing to disk?
- Is this an anti-pattern for chora-compose's design?

---

## Design Philosophy Question

**Broader question:** What is chora-compose's intended scope for artifact lifecycle management?

- **Scope A:** Generate and assemble artifacts, persist to disk (storage is caller's responsibility)
- **Scope B:** Generate, assemble, AND manage artifact lifecycle (retention, cleanup, etc.)
- **Scope C:** Generate and assemble, with flexible storage backends (disk, ephemeral, content-only, etc.)

Understanding this will help us design workflows that align with chora-compose's intended patterns.

---

## Our Current Assumption

We're currently assuming **Option 2 (Persistent Storage)** with external cleanup:

```python
# Workflow implementation
async def run_daily_report():
    # ... gather data ...

    # Assemble artifact (persists to disk)
    artifact = await chora_assemble_artifact(
        config_id="daily-report",
        content=content
    )
    # artifact["path"] = "reports/daily/2025-10-19.md"

    # Consume the report (post to Slack, etc.)
    await post_to_slack(artifact["path"])

    # External cleanup (optional)
    # cleanup_old_reports(older_than_days=30)
```

**Is this the recommended pattern?** Or should we be thinking about this differently?

---

## Related Considerations

1. **Template Location:**
   - We'll create the `daily-report.jinja2` template in chora-compose repo
   - Template will handle report formatting

2. **Artifact Config:**
   - We'll define artifact configuration (output path, metadata)
   - Need to understand best practices for time-series artifacts

3. **Workflow Integration:**
   - Daily report is one of 3-5 workflows we're building
   - Want to establish patterns that scale to other workflows

---

## Request

Could the chora-compose team provide guidance on:

1. **Is ephemeral storage supported/planned?** (Option 1)
2. **If not, what's the recommended pattern for time-series artifacts?** (Option 2)
3. **Can artifacts be content-only (no disk persistence)?** (Option 3)
4. **What's chora-compose's intended scope for artifact lifecycle management?**

This will help us design the Daily Report workflow (and future workflows) in alignment with chora-compose's architecture and design philosophy.

---

## Additional Context

**mcp-n8n Gateway Context:**
- We're building production workflow templates for mcp-n8n + chora-compose integration
- Daily Report is the first "validation workflow" (Sprint 5)
- Followed by 2-4 more production workflows
- Want to establish patterns that other teams can follow

**Timeline:**
- Implementing Daily Report workflow this week (Sprint 5, Day 1-3)
- Need to make architecture decisions about artifact storage

**Flexibility:**
- We're flexible on the approach
- Just want to align with chora-compose's intended design
- Happy to adjust workflow if our assumptions are off-base

---

## Thank You!

Any guidance from the chora-compose team would be greatly appreciated. We're excited to build workflows that showcase the power of mcp-n8n + chora-compose integration!

**Contact:** Victor Piper (via GitHub or mcp-n8n repo)
**Related:** [Daily Report Workflow Spec](./daily-report-spec.md)
