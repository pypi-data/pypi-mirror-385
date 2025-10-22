# Agent Memory Architecture

This directory contains the stateful memory infrastructure for AI coding agents working with mcp-n8n, implementing cross-session learning and knowledge persistence.

## Overview

The `.chora/memory/` structure enables agents to:
- **Learn from past executions** - Avoid repeating mistakes
- **Build knowledge incrementally** - Progressive capability improvement
- **Correlate related operations** - Track multi-step workflows via trace_id
- **Share context across sessions** - Single-developer multi-instance workflow support

## Architecture

### Memory Types

Following the Agentic Memory (A-MEM) principles from Agentic Coding Best Practices:

1. **Ephemeral Session Memory** - Current session only (not persisted)
2. **Event Log** - Append-only operation history with trace correlation
3. **Knowledge Graph** - Structured learnings, linked notes (Zettelkasten-inspired)
4. **Agent Profiles** - Per-agent capabilities, preferences, learned patterns

### Directory Structure

```
.chora/memory/
├── README.md                    # This file
├── events/                      # Event log storage
│   ├── 2025-01/                 # Monthly partitions
│   │   ├── events.jsonl         # Daily aggregated events
│   │   └── traces/              # Per-trace details
│   │       └── abc123.jsonl     # All events for trace_id=abc123
│   └── index.json               # Event index (searchable)
├── knowledge/                   # Knowledge graph
│   ├── notes/                   # Individual knowledge notes
│   │   ├── backend-timeout-fix.md
│   │   └── trace-context-pattern.md
│   ├── links.json               # Note connections
│   └── tags.json                # Tag index
├── profiles/                    # Agent-specific profiles
│   ├── claude-code.json         # Claude Code preferences
│   └── cursor-composer.json     # Cursor preferences
└── queries/                     # Saved queries (frequently accessed patterns)
    ├── recent-failures.sql
    └── trace-lookup.sql
```

## Event Log Format

### Event Structure

All events follow the Chora ecosystem event schema (v1.0):

```json
{
  "timestamp": "2025-01-17T12:00:00.123Z",
  "trace_id": "abc123",
  "status": "success",
  "schema_version": "1.0",
  "event_type": "gateway.tool_call",
  "source": "mcp-n8n",
  "metadata": {
    "tool_name": "chora:assemble_artifact",
    "backend": "chora-composer",
    "duration_ms": 1234
  }
}
```

### Event Types

**Gateway Events:**
- `gateway.started` - Gateway server started
- `gateway.stopped` - Gateway server stopped
- `gateway.tool_call` - Tool routed to backend
- `gateway.backend_registered` - New backend registered
- `gateway.backend_started` - Backend subprocess started
- `gateway.backend_failed` - Backend startup/operation failed

**Backend Events (from Chora Composer):**
- `chora.content_generated` - Content generation completed
- `chora.artifact_assembled` - Artifact assembly completed
- `chora.validation_completed` - Validation completed

### Trace Correlation

Events sharing the same `trace_id` represent a multi-step workflow:

```
trace_id=abc123:
  1. gateway.tool_call (chora:generate_content) → 100ms
  2. chora.content_generated (status=success) → 500ms
  3. gateway.tool_call (chora:assemble_artifact) → 120ms
  4. chora.artifact_assembled (status=success) → 1200ms

Total workflow: 1920ms
```

## Knowledge Graph Format

### Knowledge Notes

Markdown files with YAML frontmatter following **Zettelkasten best practices**.

#### Frontmatter Schema

All knowledge notes use standardized YAML frontmatter for machine-readable metadata:

**Required Fields:**
- `id` (string): Unique note identifier in kebab-case (e.g., `backend-timeout-fix`)
- `created` (ISO 8601): Creation timestamp (e.g., `2025-01-17T12:00:00Z`)
- `updated` (ISO 8601): Last modification timestamp
- `tags` (array[string]): Topical tags for search and organization (e.g., `[troubleshooting, backend]`)

**Optional Fields:**
- `confidence` (enum): Solution reliability - `low` | `medium` | `high`
  - `low`: Untested hypothesis or early exploration
  - `medium`: Tested in limited scenarios
  - `high`: Production-validated, multiple confirmations
- `source` (string): Knowledge origin - `agent-learning` | `human-curated` | `external` | `research`
- `linked_to` (array[string]): Related note IDs for bidirectional linking (knowledge graph)
- `status` (enum): Note lifecycle - `draft` | `validated` | `deprecated`
- `author` (string): Agent or human who created the note
- `related_traces` (array[string]): Trace IDs that led to this learning

**Standards Compliance:**
- ✅ Compatible with Obsidian, Zettlr, LogSeq, Foam
- ✅ Follows Zettelkasten methodology (atomic notes, bidirectional linking)
- ✅ Enables semantic search and confidence-based filtering
- ✅ Supports knowledge graph visualization and traversal

**Example:**

```markdown
---
id: backend-timeout-fix
created: 2025-01-17T12:00:00Z
updated: 2025-01-17T14:30:00Z
tags: [troubleshooting, backend, timeout]
confidence: high
source: agent-learning
linked_to: [trace-context-pattern, error-handling-best-practices]
status: validated
author: claude-code
related_traces: [abc123, def456]
---

# Backend Timeout Fix

## Problem
Backend subprocess fails to start within default 30s timeout when running on slow machines or during high system load.

## Solution
Increase `backend_timeout` configuration to 60s for development environments:

```env
MCP_N8N_BACKEND_TIMEOUT=60
```

## Evidence
- Trace abc123: Backend started successfully at 45s
- Trace def456: Backend started successfully at 52s
- Both would have failed with 30s timeout

## Learned Pattern
When backend startup failures occur, check:
1. System load (via `top` or Activity Monitor)
2. Backend logs for slow initialization steps
3. Increase timeout if startup is legitimately slow
```

### Links Graph

`links.json` structure:

```json
{
  "notes": [
    {
      "id": "backend-timeout-fix",
      "outgoing_links": [
        "trace-context-pattern",
        "error-handling-best-practices"
      ],
      "incoming_links": [
        "troubleshooting-checklist"
      ],
      "strength": 0.8
    }
  ],
  "clusters": [
    {
      "name": "backend-troubleshooting",
      "notes": [
        "backend-timeout-fix",
        "subprocess-communication-errors",
        "backend-crash-recovery"
      ]
    }
  ]
}
```

## Agent Profiles

### Profile Structure

`profiles/claude-code.json`:

```json
{
  "agent_name": "claude-code",
  "agent_version": "sonnet-4.5-20250929",
  "last_active": "2025-01-17T14:30:00Z",
  "session_count": 42,
  "capabilities": {
    "backend_management": {
      "skill_level": "advanced",
      "successful_operations": 128,
      "failed_operations": 5,
      "learned_patterns": [
        "backend-timeout-fix",
        "trace-context-pattern"
      ]
    },
    "artifact_creation": {
      "skill_level": "expert",
      "preferred_tool": "chora:assemble_artifact",
      "common_mistakes": [
        "Forgetting to validate content before assembly"
      ]
    }
  },
  "preferences": {
    "verbose_logging": true,
    "auto_retry_on_timeout": true,
    "preferred_backend_timeout": 60
  },
  "context_switches": {
    "total": 15,
    "last_handoff": {
      "to": "chora-composer",
      "timestamp": "2025-01-16T16:00:00Z",
      "trace_id": "xyz789"
    }
  }
}
```

## Usage Patterns for Agents

### 1. Query Recent Failures

```python
# Agent wants to learn from recent failures
failures = query_events(
    event_type="gateway.backend_failed",
    status="failure",
    since=datetime.now() - timedelta(days=7)
)

# Analyze patterns
for failure in failures:
    # Check if knowledge note exists
    note_id = f"failure-{failure['trace_id']}"
    if not knowledge_exists(note_id):
        # Create knowledge note
        create_knowledge_note(
            id=note_id,
            content=f"Backend {failure['metadata']['backend']} failed: {failure['metadata']['error']}",
            tags=["failure", "backend", failure['metadata']['backend']],
            linked_to=[related_notes]
        )
```

### 2. Trace Workflow Correlation

```python
# Agent wants to understand multi-step workflow
trace_id = "abc123"
events = get_events_by_trace(trace_id)

# Build workflow timeline
timeline = []
for event in events:
    timeline.append({
        "step": event["event_type"],
        "timestamp": event["timestamp"],
        "duration": event["metadata"].get("duration_ms", 0),
        "status": event["status"]
    })

# Identify bottlenecks
bottlenecks = [step for step in timeline if step["duration"] > 1000]
```

### 3. Learn from Successful Patterns

```python
# Agent wants to replicate successful workflow
successful_traces = query_events(
    event_type="chora.artifact_assembled",
    status="success",
    limit=10
)

# Extract common patterns
patterns = analyze_patterns(successful_traces)
# E.g., "Always validate before assembly", "Use batch_generate for multiple content pieces"

# Store as knowledge
create_knowledge_note(
    id="successful-artifact-patterns",
    content=patterns,
    tags=["best-practices", "artifact", "success-pattern"]
)
```

### 4. Context Switch Support

```python
# Agent preparing to hand off to chora-composer
handoff_context = {
    "from_agent": "claude-code-mcp-n8n",
    "to_project": "chora-composer",
    "trace_id": generate_trace_id(),
    "pending_tasks": get_pending_tasks(),
    "recent_failures": query_recent_failures(),
    "knowledge_updates": get_knowledge_updates_since_last_handoff()
}

# Store handoff event
emit_event(
    event_type="gateway.context_switch",
    trace_id=handoff_context["trace_id"],
    status="pending",
    metadata=handoff_context
)
```

## Query Interface

### Event Queries

Agents can query events using:

**Python API:**
```python
from mcp_n8n.memory import EventLog

log = EventLog()

# Query by trace ID
events = log.get_by_trace("abc123")

# Query by type and status
failures = log.query(event_type="gateway.backend_failed", status="failure")

# Query time range
recent = log.query(since=datetime.now() - timedelta(hours=24))

# Aggregate statistics
stats = log.aggregate(
    group_by="event_type",
    metric="count",
    since=datetime.now() - timedelta(days=7)
)
```

**CLI (for agents using bash):**
```bash
# Query recent failures
chora-memory query --type "gateway.backend_failed" --since "24h"

# Get trace timeline
chora-memory trace abc123

# Search knowledge notes
chora-memory knowledge search --tag "backend" --tag "timeout"

# Get agent profile
chora-memory profile claude-code
```

## Knowledge Management

### Creating Notes

```python
from mcp_n8n.memory import KnowledgeGraph

kg = KnowledgeGraph()

# Create new note
note_id = kg.create_note(
    title="Backend Timeout Fix",
    content="""...""",
    tags=["troubleshooting", "backend"],
    links=["trace-context-pattern"]
)

# Update existing note
kg.update_note(
    note_id,
    content_append="## New Finding\n...",
    links_add=["error-handling-best-practices"]
)

# Link notes
kg.link_notes("backend-timeout-fix", "error-handling-best-practices", strength=0.8)
```

### Searching Knowledge

```python
# Search by tags
notes = kg.search(tags=["backend", "timeout"])

# Search by content
notes = kg.search(text="subprocess timeout")

# Get related notes
related = kg.get_related("backend-timeout-fix", max_distance=2)

# Find clusters
clusters = kg.find_clusters(min_size=3)
```

## Retention Policy

**Event Log:**
- **Daily events:** Retained for 90 days
- **Trace details:** Retained for 30 days
- **Failure events:** Retained for 180 days (for learning)
- **Archived:** Compressed monthly archives kept for 1 year

**Knowledge Notes:**
- **Never deleted** - Cumulative learning
- **Confidence tracking** - Notes marked with confidence level
- **Deprecation** - Low-confidence notes marked as deprecated, not deleted

**Agent Profiles:**
- **Persistent** - Never deleted
- **Updated continuously** - Each session updates statistics
- **Versioned** - Profile snapshots taken monthly

## Privacy & Security

**No sensitive data:**
- ❌ API keys, tokens, credentials
- ❌ User-specific data (unless explicitly permitted)
- ❌ PII (personally identifiable information)

**Logged data:**
- ✅ Event types, timestamps, status
- ✅ Trace IDs (UUIDs, not user data)
- ✅ Tool names, backend names
- ✅ Performance metrics (duration, counts)
- ✅ Error types (sanitized messages)

**Git integration:**
- `.chora/memory/` is in `.gitignore` by default
- Agents can opt to commit knowledge notes (not event logs)
- Profiles can be committed for reproducibility

## Future Extensions

### Phase 4.6+ Enhancements

1. **Vector Database Integration**
   - Semantic search over knowledge notes
   - Similarity-based note clustering
   - Automatic link suggestion

2. **Cross-Project Memory**
   - Share learnings between mcp-n8n and chora-composer
   - Ecosystem-wide knowledge graph
   - Federated agent profiles

3. **Agent Collaboration**
   - Multi-agent coordination via shared memory
   - Conflict resolution for concurrent updates
   - Agent-to-agent knowledge transfer

4. **Advanced Analytics**
   - Workflow optimization suggestions
   - Anomaly detection in event patterns
   - Predictive failure alerts

---

**Version:** 1.0.0 (Phase 4.5)
**Last Updated:** 2025-01
**Compatible with:** mcp-n8n v0.1.0+, chora-composer v1.1.0+
