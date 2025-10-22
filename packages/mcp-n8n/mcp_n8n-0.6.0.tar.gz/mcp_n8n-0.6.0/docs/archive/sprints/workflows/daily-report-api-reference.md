# Daily Report Workflow - API Reference

**Version:** 1.0.0
**Status:** DRAFT
**Sprint:** Sprint 5 - Production Workflows
**Category:** Reference Documentation (Diátaxis)

---

## Overview

This document defines the API contract for the Daily Report workflow. It specifies function signatures, parameters, return values, and usage examples following Documentation Driven Design (DDD) principles.

**Purpose:** Generate automated daily engineering reports aggregating:
- Recent Git commits from the repository
- Gateway telemetry events from the last 24 hours
- Tool usage statistics and performance metrics

**Storage:** Reports are stored using chora-compose ephemeral storage with 7-day retention.

---

## Core API

### `run_daily_report()`

Generate a daily engineering report for the specified date.

#### Signature

```python
async def run_daily_report(
    date: str | None = None,
    repository_path: str | None = None,
    since_hours: int = 24,
    output_format: Literal["markdown", "html"] = "markdown"
) -> DailyReportResult
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | `str \| None` | No | Today's date | ISO date string (YYYY-MM-DD) for the report date |
| `repository_path` | `str \| None` | No | Current working directory | Path to git repository for commit analysis |
| `since_hours` | `int` | No | `24` | Number of hours to look back for commits and events |
| `output_format` | `Literal["markdown", "html"]` | No | `"markdown"` | Output format for the generated report |

#### Returns

**Type:** `DailyReportResult` (TypedDict)

```python
class DailyReportResult(TypedDict):
    status: Literal["success", "failure"]
    report_path: str | None
    summary: ReportSummary
    error: str | None
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | `Literal["success", "failure"]` | Execution status |
| `report_path` | `str \| None` | Path to generated report (ephemeral storage), None if failed |
| `summary` | `ReportSummary` | Key metrics from the report |
| `error` | `str \| None` | Error message if status is "failure", None otherwise |

**`ReportSummary` schema:**

```python
class ReportSummary(TypedDict):
    commit_count: int
    event_count: int
    tool_calls: int
    success_rate: float  # Percentage (0-100)
    backends_active: list[str]
```

#### Example: Success

```python
result = await run_daily_report(
    date="2025-10-19",
    since_hours=24
)

# result = {
#     "status": "success",
#     "report_path": "/tmp/chora-ephemeral/daily-report-2025-10-19.md",
#     "summary": {
#         "commit_count": 5,
#         "event_count": 127,
#         "tool_calls": 42,
#         "success_rate": 95.2,
#         "backends_active": ["chora-composer", "coda-mcp"]
#     },
#     "error": None
# }
```

#### Example: Failure (No Git Repository)

```python
result = await run_daily_report(
    repository_path="/nonexistent/path"
)

# result = {
#     "status": "failure",
#     "report_path": None,
#     "summary": {
#         "commit_count": 0,
#         "event_count": 0,
#         "tool_calls": 0,
#         "success_rate": 0.0,
#         "backends_active": []
#     },
#     "error": "Git repository not found at /nonexistent/path"
# }
```

#### Behavior

1. **Data Gathering:**
   - Query git log for commits in the specified time range
   - Query gateway event log using `get_events()` tool
   - Aggregate statistics from events

2. **Content Generation:**
   - Call `chora:generate_content` with daily-report template
   - Pass context: date, commits, events, statistics

3. **Artifact Assembly:**
   - Call `chora:assemble_artifact` with ephemeral storage config
   - Use 7-day retention policy
   - Return path to ephemeral report file

4. **Error Handling:**
   - If git repository not found → status="failure", error message
   - If chora-compose not available → status="failure", error message
   - If event log not accessible → Continue with empty events, log warning

#### Edge Cases

| Scenario | Behavior |
|----------|----------|
| No commits in time range | Generate report with "No commits" section |
| No events in time range | Generate report with "No events" section |
| chora-compose not installed | Return failure with actionable error message |
| Invalid date format | Raise `ValueError` with example of valid format |
| Git repository not initialized | Return failure with git init suggestion |

---

## Data Gathering Functions

### `get_recent_commits()`

Retrieve commits from git repository in the specified time range.

#### Signature

```python
async def get_recent_commits(
    repository_path: str = ".",
    since_hours: int = 24,
    branch: str | None = None
) -> list[CommitInfo]
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `repository_path` | `str` | No | `"."` | Path to git repository |
| `since_hours` | `int` | No | `24` | Hours to look back |
| `branch` | `str \| None` | No | `None` | Branch name (None = current branch) |

#### Returns

**Type:** `list[CommitInfo]`

```python
class CommitInfo(TypedDict):
    hash: str
    author: str
    message: str
    timestamp: str  # ISO 8601 format
    files_changed: int
```

#### Example

```python
commits = await get_recent_commits(
    repository_path="/Users/victorpiper/code/mcp-n8n",
    since_hours=24
)

# commits = [
#     {
#         "hash": "d04ad52f",
#         "author": "Victor Piper",
#         "message": "feat(event-monitoring): Implement Phase 2.2",
#         "timestamp": "2025-10-19T14:23:00Z",
#         "files_changed": 12
#     },
#     ...
# ]
```

#### Error Handling

- **Git not installed:** Raise `RuntimeError` with installation instructions
- **Repository not found:** Raise `FileNotFoundError` with path
- **Invalid repository:** Raise `ValueError` with explanation

---

### `aggregate_statistics()`

Aggregate statistics from event list.

#### Signature

```python
def aggregate_statistics(
    events: list[dict[str, Any]]
) -> EventStatistics
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `events` | `list[dict[str, Any]]` | Yes | List of events from event log |

#### Returns

**Type:** `EventStatistics` (TypedDict)

```python
class EventStatistics(TypedDict):
    total_events: int
    by_type: dict[str, int]
    by_status: dict[str, int]
    by_backend: dict[str, int]
    tool_usage: dict[str, int]
    success_rate: float
```

#### Example

```python
statistics = aggregate_statistics(events)

# statistics = {
#     "total_events": 127,
#     "by_type": {
#         "gateway.tool_call": 42,
#         "chora.content_generated": 20,
#         "chora.artifact_assembled": 18
#     },
#     "by_status": {
#         "success": 121,
#         "failure": 6
#     },
#     "by_backend": {
#         "chora-composer": 38,
#         "coda-mcp": 4
#     },
#     "tool_usage": {
#         "chora:generate_content": 20,
#         "chora:assemble_artifact": 18,
#         "coda:list_docs": 4
#     },
#     "success_rate": 95.28
# }
```

---

## Chora-Compose Integration

### Ephemeral Storage Configuration

The Daily Report workflow uses chora-compose ephemeral storage for report artifacts.

#### Artifact Configuration

**File:** `chora-templates/daily-report-artifact.yaml` (to be created in chora-compose repo)

```yaml
artifact_type: "report"
storage_type: "ephemeral"
retention_days: 7
output:
  filename_template: "daily-report-{{ date }}.{{ format }}"
  formats:
    - markdown
    - html
metadata:
  report_type: "daily-engineering"
  generated_by: "mcp-n8n-gateway"
  workflow_version: "1.0.0"
```

#### Template Configuration

**File:** `chora-templates/daily-report.jinja2` (to be created in chora-compose repo)

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
{% for type, count in stats.by_type.items() %}
- {{ type }}: {{ count }}
{% endfor %}

### Tool Usage
{% for tool, count in stats.tool_usage.items() %}
- {{ tool }}: {{ count }} calls
{% endfor %}

### Performance
- **Success Rate:** {{ "%.1f" | format(stats.success_rate) }}%
- **Backends Active:** {{ stats.by_backend | length }}
- **Total Events:** {{ stats.total_events }}
```

---

## CLI Interface

### Command-Line Usage

```bash
# Generate report for today
python -m mcp_n8n.workflows.daily_report

# Generate report for specific date
python -m mcp_n8n.workflows.daily_report --date 2025-10-19

# Generate report with custom time range
python -m mcp_n8n.workflows.daily_report --since-hours 48

# HTML format output
python -m mcp_n8n.workflows.daily_report --format html

# Help
python -m mcp_n8n.workflows.daily_report --help
```

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success - Report generated |
| `1` | Failure - Git repository error |
| `2` | Failure - Chora-compose not available |
| `3` | Failure - Invalid parameters |
| `4` | Failure - Event log access error |

---

## Type Definitions

### Complete Type Hierarchy

```python
from typing import Any, Literal, TypedDict

class CommitInfo(TypedDict):
    hash: str
    author: str
    message: str
    timestamp: str
    files_changed: int

class EventStatistics(TypedDict):
    total_events: int
    by_type: dict[str, int]
    by_status: dict[str, int]
    by_backend: dict[str, int]
    tool_usage: dict[str, int]
    success_rate: float

class ReportSummary(TypedDict):
    commit_count: int
    event_count: int
    tool_calls: int
    success_rate: float
    backends_active: list[str]

class DailyReportResult(TypedDict):
    status: Literal["success", "failure"]
    report_path: str | None
    summary: ReportSummary
    error: str | None
```

---

## Dependencies

### Required

- **Python 3.11+**
- **Git** (installed and accessible in PATH)
- **chora-compose ≥1.3.0** (with ephemeral storage support)
- **mcp-n8n ≥0.3.0** (with event monitoring)

### Optional

- **n8n** (for workflow automation)

---

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Total execution time | <60 seconds | For 24-hour time range |
| Commit retrieval | <5 seconds | Local git log query |
| Event querying | <2 seconds | From local event log |
| Content generation | <30 seconds | chora-compose call |
| Artifact assembly | <20 seconds | chora-compose ephemeral storage |

---

## Security Considerations

### Sensitive Data

- **No credentials in reports:** Filter out API keys, tokens from commit messages
- **No PII exposure:** Redact email addresses if configured
- **Path sanitization:** Validate repository paths to prevent directory traversal

### Access Control

- **Repository access:** Workflow runs with same permissions as invoking user
- **Event log access:** Read-only access to gateway telemetry
- **Report storage:** Ephemeral reports auto-delete after 7 days

---

## Related Documentation

- [Daily Report Specification](./daily-report-spec.md) - High-level workflow design
- [Chora-Compose Storage Question](./chora-compose-storage-question.md) - Storage architecture discussion
- [Event Monitoring Tutorial](../tutorials/event-monitoring-tutorial.md) - Using get_events tool
- [UNIFIED_ROADMAP.md](../UNIFIED_ROADMAP.md) - Sprint 5 context

---

**Document Status:** DRAFT
**Next Step:** Define acceptance criteria for BDD scenarios
**Owner:** Victor Piper
**Last Updated:** 2025-10-19
