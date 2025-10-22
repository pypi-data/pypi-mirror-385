---
title: "Understanding the Memory System"
type: explanation
audience: intermediate
category: concepts
source: "docs/PHASE_4.5_SUMMARY.md, docs/PHASE_4.6_SUMMARY.md, src/mcp_n8n/memory/"
last_updated: 2025-10-21
---

# Understanding the Memory System

## Overview

The mcp-n8n memory system provides **persistent, queryable telemetry and knowledge storage** that enables both humans and AI agents to learn from past operations, track workflows, and accumulate domain expertise over time.

**The core idea:** Instead of every session starting from scratch, the system remembers what happened before—successful patterns, failure modes, and learned solutions—making debugging easier and enabling progressive capability improvement.

## Context

### Background: The Stateless Agent Problem

Traditional AI coding agents are stateless:
- Each new chat session starts with no memory of previous work
- Same mistakes repeated across sessions
- No accumulation of project-specific knowledge
- Debugging requires manually reviewing logs
- Workflow failures leave no structured trace

**For humans:**
- Tribal knowledge lives in heads or scattered documents
- Hard to correlate events across multiple backends
- No unified audit trail for debugging
- Error patterns not automatically detected

### The A-MEM Vision

From **Agentic Coding Best Practices** research (A-MEM: Agent Memory):

> Stateful memory enables agents to learn cumulatively, improving their capabilities over time by remembering successes, learning from failures, and accumulating domain expertise.

**Three memory types needed:**
1. **Event Log** - What happened (telemetry, traces, operations)
2. **Knowledge Graph** - What we learned (solutions, patterns, best practices)
3. **Agent Profiles** - How capable am I (skill tracking, preferences)

### Alternatives Considered

**1. Log Files Only**
- ❌ Difficult to query programmatically
- ❌ No structured schema
- ❌ Hard to correlate events across services
- ✅ Simple and familiar

**2. External Database (PostgreSQL, MongoDB)**
- ❌ Adds deployment complexity
- ❌ Not local-first (network required)
- ❌ Privacy concerns (data leaves machine)
- ✅ Powerful querying

**3. Stateful Memory System (Chosen)**
- ✅ Local-first (no network, privacy-safe)
- ✅ Structured schema (event v1.0, JSONL)
- ✅ Queryable (Python API + CLI)
- ✅ Trace correlation (CHORA_TRACE_ID)
- ⚠️ Not suitable for multi-GB datasets

### Constraints

1. **Privacy-first:** No credentials, tokens, or PII ever stored
2. **Local-only:** All data stays on developer's machine
3. **Lightweight:** Append-only files, no database server
4. **Cross-session:** Must persist across restarts
5. **Agent-accessible:** Queryable via CLI (bash commands)

---

## The Solution

### High-Level Approach

The memory system consists of three complementary subsystems:

```
┌─────────────────────────────────────────────────────────┐
│                   Memory System                         │
│                (.chora/memory/)                         │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  1. Event Log (Telemetry)                       │   │
│  │     - What operations occurred?                 │   │
│  │     - When did they happen?                     │   │
│  │     - Were they successful?                     │   │
│  │     - How long did they take?                   │   │
│  │                                                  │   │
│  │  Storage: events/<month>/events.jsonl          │   │
│  │  Indexed: traces/<trace_id>.jsonl              │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  2. Knowledge Graph (Learnings)                 │   │
│  │     - What did we learn from failures?          │   │
│  │     - What patterns led to success?             │   │
│  │     - How are concepts related?                 │   │
│  │                                                  │   │
│  │  Storage: knowledge/notes/*.md                  │   │
│  │  Indexed: knowledge/links.json, tags.json      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  3. Agent Profiles (Capabilities)               │   │
│  │     - What am I good at?                        │   │
│  │     - What mistakes do I commonly make?         │   │
│  │     - What preferences do I have?               │   │
│  │                                                  │   │
│  │  Storage: profiles/<agent_name>.json           │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Key Decisions

**Decision 1: JSONL for Event Storage**
- **Rationale:** Append-only, human-readable, no database server needed. Each line is a complete JSON event, making it easy to process with standard tools (jq, grep, etc.).
- **Trade-offs:** Not suitable for multi-GB datasets, but perfect for local development telemetry.
- **Alternatives:** SQLite (query overhead), plain logs (hard to parse).

**Decision 2: Monthly Partitioning**
- **Rationale:** Keeps individual files manageable. Queries can skip partitions outside time range.
- **Implementation:** Events stored in `events/2025-10/events.jsonl`, `events/2025-11/events.jsonl`, etc.
- **Trade-offs:** Queries spanning many months slower, but single-month queries very fast.

**Decision 3: Trace-Based Indexing**
- **Rationale:** Workflows often span multiple events across services. Trace IDs enable correlating the entire flow.
- **Implementation:** Each event gets a `trace_id`. Events with same trace ID copied to `traces/<trace_id>.jsonl` for O(1) lookup.
- **Ecosystem Alignment:** Uses `CHORA_TRACE_ID` environment variable (compatible with chora-compose).

**Decision 4: Zettelkasten-Style Knowledge Notes**
- **Rationale:** Proven knowledge management pattern. Bidirectional links enable knowledge graph traversal.
- **Trade-offs:** Manual note creation required (agents must decide what to remember).
- **Format:** Markdown with YAML frontmatter (human and machine readable).

**Decision 5: Per-Agent Profiles**
- **Rationale:** Different agents (Claude Code, cursor, etc.) have different capabilities. Track separately.
- **Implementation:** One JSON file per agent (`profiles/claude-code.json`, etc.).
- **Future:** Enable agents to share learnings across sessions.

---

## How It Works

### Component 1: Event Log

**Purpose:** Record all gateway and workflow operations for debugging and analytics.

**Storage Structure:**
```
.chora/memory/events/
├── 2025-10/
│   ├── events.jsonl          # All events from October 2025
│   └── traces/
│       ├── abc123.jsonl      # All events for trace abc123
│       └── def456.jsonl      # All events for trace def456
├── 2025-11/
│   ├── events.jsonl
│   └── traces/
└── ...
```

**Event Schema (v1.0):**
```json
{
  "timestamp": "2025-10-21T12:00:00.123Z",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "gateway.tool_call",
  "status": "success",
  "source": "mcp-n8n",
  "metadata": {
    "tool_name": "chora:assemble_artifact",
    "duration_ms": 1234,
    "backend": "chora-composer"
  }
}
```

**Event Types:**
- `gateway.started` - Gateway server started
- `gateway.stopped` - Gateway server stopped
- `gateway.backend_registered` - Backend registered with gateway
- `gateway.backend_started` - Backend subprocess initialized
- `gateway.backend_failed` - Backend startup or operation failed
- `gateway.tool_call` - Tool call routed to backend
- `workflow.started` - Workflow execution started
- `workflow.completed` - Workflow execution succeeded
- `workflow.failed` - Workflow execution failed

**Querying Events:**

Via Python API:
```python
from mcp_n8n.memory import EventLog
from datetime import datetime, timedelta, UTC

log = EventLog()

# Get failures from last 24 hours
since = datetime.now(UTC) - timedelta(hours=24)
failures = log.query(status="failure", since=since)

# Get all events for a workflow
trace_events = log.get_by_trace("550e8400-e29b-41d4-a716-446655440000")

# Aggregate statistics
stats = log.aggregate(group_by="event_type", metric="count", since=since)
```

Via CLI:
```bash
# Query failures
chora-memory query --status failure --since 24h

# Show workflow timeline
chora-memory trace 550e8400-e29b-41d4-a716-446655440000

# Get statistics
chora-memory stats --since 7d
```

**Trace Context Propagation:**

The `TraceContext` context manager generates and propagates trace IDs:

```python
from mcp_n8n.memory import TraceContext, emit_event

# Automatic trace ID generation
with TraceContext() as trace_id:
    emit_event("workflow.started", trace_id=trace_id)
    # Do work...
    emit_event("workflow.completed", trace_id=trace_id)

# All events share same trace_id for correlation
```

The trace ID is automatically propagated to backend subprocesses via `CHORA_TRACE_ID` environment variable, enabling correlation across gateway and backend boundaries.

---

### Component 2: Knowledge Graph

**Purpose:** Capture learned patterns, solutions, and domain expertise in a queryable, linkable format.

**Storage Structure:**
```
.chora/memory/knowledge/
├── notes/
│   ├── backend-timeout-fix.md
│   ├── trace-context-pattern.md
│   └── successful-artifact-patterns.md
├── links.json                # Bidirectional link index
└── tags.json                 # Tag index for fast lookup
```

**Note Format:**
```markdown
---
id: backend-timeout-fix
created: 2025-10-21T12:00:00Z
updated: 2025-10-21T14:30:00Z
tags: [troubleshooting, backend, timeout]
confidence: high
source: agent-learning
linked_to: [trace-context-pattern]
---

# Backend Timeout Fix

## Problem
Backend subprocess fails to start within 30s timeout.

## Root Cause
Large chora-compose installations take >30s to initialize.

## Solution
Increase timeout via environment variable:

```bash
export MCP_N8N_BACKEND_TIMEOUT=60
```

## Related Patterns
- trace-context-pattern: Use trace IDs to debug slow startups
- backend-health-checks: Monitor backend initialization progress

## Evidence
- Trace ID: abc123 (failed with 30s timeout)
- Trace ID: def456 (succeeded with 60s timeout)
```

**Creating Knowledge Notes:**

Via Python API:
```python
from mcp_n8n.memory import KnowledgeGraph

kg = KnowledgeGraph()

note_id = kg.create_note(
    title="Backend Timeout Fix",
    content="Increase MCP_N8N_BACKEND_TIMEOUT=60",
    tags=["troubleshooting", "backend", "timeout"],
    links=["trace-context-pattern"],
    confidence="high"
)
```

Via CLI:
```bash
# Create note from stdin
echo "Solution content..." | chora-memory knowledge create "Backend Timeout Fix" \
    --tag troubleshooting --tag backend \
    --confidence high

# Search notes
chora-memory knowledge search --tag timeout --confidence high

# Show note details
chora-memory knowledge show backend-timeout-fix
```

**Bidirectional Linking:**

When you link note A → B, the system automatically creates the reverse link B → A. This enables knowledge graph traversal:

```python
# Get related notes (distance=1: direct links)
related = kg.get_related_notes("backend-timeout-fix", distance=1)
# Returns: ["trace-context-pattern", "backend-health-checks"]

# Get broader context (distance=2: links + links-of-links)
broader = kg.get_related_notes("backend-timeout-fix", distance=2)
# Returns: All notes within 2 hops of the original
```

---

### Component 3: Agent Profiles

**Purpose:** Track agent capabilities, skill progression, and preferences across sessions.

**Storage Structure:**
```
.chora/memory/profiles/
├── claude-code.json
├── cursor.json
└── roo-code.json
```

**Profile Format:**
```json
{
  "agent_name": "claude-code",
  "agent_version": "sonnet-4.5-20250929",
  "last_active": "2025-10-21T14:30:00Z",
  "session_count": 42,
  "capabilities": {
    "backend_management": {
      "skill_level": "advanced",
      "successful_operations": 128,
      "failed_operations": 5,
      "learned_patterns": ["backend-timeout-fix", "trace-context-pattern"]
    },
    "artifact_creation": {
      "skill_level": "expert",
      "successful_operations": 256,
      "failed_operations": 2,
      "learned_patterns": ["successful-artifact-patterns"]
    }
  },
  "preferences": {
    "verbose_logging": true,
    "auto_retry_on_timeout": true,
    "preferred_backend_timeout": 60
  }
}
```

**Updating Profiles:**

Via Python API:
```python
from mcp_n8n.memory.profiles import AgentProfileManager

manager = AgentProfileManager()
profile = manager.get_or_create_profile("claude-code", "sonnet-4.5")

# Track successful operation
profile.update_capability(
    "backend_management",
    skill_level="advanced",
    successful_operation=True,
    learned_pattern="backend-timeout-fix"
)

# Set preference
profile.set_preference("preferred_backend_timeout", 60)

# Save profile
manager.save_profile(profile)
```

Via CLI:
```bash
# Show agent profile
chora-memory profile show claude-code

# Output:
# Agent: claude-code
# Version: sonnet-4.5-20250929
# Last Active: 2025-10-21T14:30:00Z
# Session Count: 42
#
# Capabilities:
#   backend_management:
#     Skill Level: advanced
#     Success Rate: 128/133
```

**Skill Level Progression:**

Skills progress through three levels:
- **novice** (0-10 successful operations) - Learning the basics
- **intermediate** (10-50 successful operations) - Competent execution
- **advanced** (50+ successful operations) - Expert-level proficiency

Agents can manually promote skill levels or let them progress automatically based on success count.

---

## How Components Work Together

### Example Scenario: Learning from a Backend Timeout

**1. Failure Occurs:**

```python
# Gateway tries to start backend, times out
with TraceContext() as trace_id:
    emit_event(
        "gateway.backend_failed",
        trace_id=trace_id,
        status="failure",
        backend_name="chora-composer",
        error="Timeout after 30s"
    )
```

**Event stored:**
```json
{
  "timestamp": "2025-10-21T10:15:23Z",
  "trace_id": "abc123",
  "event_type": "gateway.backend_failed",
  "status": "failure",
  "metadata": {
    "backend_name": "chora-composer",
    "error": "Timeout after 30s"
  }
}
```

**2. Agent Investigates:**

```bash
# Query recent failures
chora-memory query --type gateway.backend_failed --status failure --since 24h

# Output shows pattern: all failures are timeouts
```

**3. Agent Creates Knowledge Note:**

```bash
echo "Backend timeout fix: Increase MCP_N8N_BACKEND_TIMEOUT=60" | \
chora-memory knowledge create "Backend Timeout Fix" \
    --tag troubleshooting --tag backend --confidence high
```

**4. Agent Updates Profile:**

```python
profile.update_capability(
    "backend_management",
    skill_level="intermediate",  # Promoted from novice
    successful_operation=False,  # This was a failure
    learned_pattern="backend-timeout-fix"
)
```

**5. Next Session, Agent Avoids Issue:**

```bash
# Agent searches knowledge before starting
chora-memory knowledge search --tag backend --tag timeout

# Finds: backend-timeout-fix
# Applies solution: export MCP_N8N_BACKEND_TIMEOUT=60

# Backend starts successfully this time!
```

**6. Success Recorded:**

```python
with TraceContext() as trace_id:
    emit_event(
        "gateway.backend_started",
        trace_id=trace_id,
        status="success",
        backend_name="chora-composer",
        duration_ms=45000  # 45 seconds (within 60s timeout)
    )

profile.update_capability(
    "backend_management",
    successful_operation=True  # Success!
)
```

**Result:** Agent learned from failure, captured solution in knowledge graph, and successfully applied it in next session.

---

## Benefits

**For AI Agents:**

- ✅ **Cumulative Learning:** Knowledge persists across sessions, enabling progressive improvement
- ✅ **Self-Debugging:** Query event log to understand past failures
- ✅ **Pattern Recognition:** Aggregate events to detect recurring issues
- ✅ **Workflow Correlation:** Trace IDs link events across multi-step operations
- ✅ **Capability Tracking:** Profiles show skill progression over time
- ✅ **Bash-Accessible:** CLI tools enable memory queries without writing Python code

**For Human Developers:**

- ✅ **Audit Trail:** Complete history of gateway/workflow operations
- ✅ **Debugging:** Trace timelines show exact sequence of events
- ✅ **Knowledge Base:** Captured tribal knowledge in searchable format
- ✅ **Performance Analytics:** Aggregate statistics on tool calls, success rates
- ✅ **Privacy-Safe:** No credentials or PII ever logged

**When to use:**

- Multi-session development (agents learning over weeks/months)
- Complex workflows requiring debugging across services
- Teams wanting to capture and share tribal knowledge
- Projects with recurring failure patterns worth documenting

---

## Limitations

**Constraints and trade-offs:**

- ❌ **Not for large-scale telemetry:** JSONL files work well up to millions of events, not billions
- ⚠️ **Manual knowledge curation:** Agents must decide what to remember (not automatic)
- ❌ **Single-machine only:** Memory not shared across machines (by design for privacy)
- ℹ️ **Retention policy required:** Events accumulate over time, periodic cleanup needed (default: 90 days)

**When NOT to use:**

- High-volume production telemetry (use OpenTelemetry instead)
- Multi-tenant applications (memory is per-machine)
- Real-time alerting (query API not optimized for low latency)
- Compliance requiring immutable audit logs (JSONL files can be modified)

---

## Retention Policy

**Event Log:**
- **Ephemeral events:** 30 days (e.g., `gateway.started`)
- **Workflow events:** 90 days (e.g., `workflow.completed`)
- **Trace files:** 180 days (for long-running investigations)

**Knowledge Graph:**
- **Never deleted** (knowledge is cumulative)
- Agents can archive low-confidence notes manually

**Agent Profiles:**
- **Persistent** (profiles track long-term skill progression)
- Archived only when agent permanently retired

**Implementation:**

Retention enforced by periodic cleanup script (future):
```bash
# Cleanup old events (manual for now)
find .chora/memory/events -name "events.jsonl" -mtime +90 -delete
```

---

## Privacy & Security

**What is stored:**
- ✅ Event types (e.g., `gateway.tool_call`)
- ✅ Timestamps (when operations occurred)
- ✅ Status (success/failure/pending)
- ✅ Metadata (tool names, durations, counts)

**What is NEVER stored:**
- ❌ API keys, tokens, passwords
- ❌ Personally Identifiable Information (PII)
- ❌ File contents or artifact data
- ❌ Environment variable values (except trace IDs)

**Storage location:**
- All data in `.chora/memory/` (local machine only)
- Directory in `.gitignore` by default (not committed to repos)
- Agents can opt to commit knowledge notes for team sharing

---

## Real-World Examples

### Example 1: Debugging a Multi-Step Workflow

**Problem:** Daily report workflow fails intermittently.

**Debugging with memory:**

1. **Find failing trace:**
   ```bash
   chora-memory query --type workflow.failed --since 7d
   # Returns trace ID: abc123
   ```

2. **Show trace timeline:**
   ```bash
   chora-memory trace abc123
   ```

   **Output:**
   ```
   Trace Timeline: abc123
   Total events: 5
   Duration: 8234ms

   1. [10:15:00] ✓ workflow.started (success)
   2. [10:15:01] ✓ gateway.tool_call (success) - get_events (120ms)
   3. [10:15:02] ✓ gateway.tool_call (success) - chora:generate_content (7800ms)
   4. [10:15:10] ✗ workflow.failed (failure)
      error: "ConnectionTimeout: chora-compose not responding"
   ```

3. **Root cause identified:** Backend timeout after long operation.

4. **Create knowledge note:**
   ```bash
   chora-memory knowledge create "Workflow Timeout Pattern" \
       --content "Long chora:generate_content calls can timeout. Use async workflow pattern." \
       --tag workflow --tag timeout
   ```

### Example 2: Agent Skill Progression

**Week 1:** Agent attempts backend configuration, fails multiple times.

```bash
chora-memory profile show claude-code
# Capabilities:
#   backend_management:
#     Skill Level: novice
#     Success Rate: 2/8
```

**Week 4:** After learning from knowledge notes, agent succeeds consistently.

```bash
chora-memory profile show claude-code
# Capabilities:
#   backend_management:
#     Skill Level: intermediate
#     Success Rate: 42/50
#     Learned Patterns: [backend-timeout-fix, trace-context-pattern]
```

**Result:** Profile shows clear progression from novice → intermediate through experience.

### Example 3: Knowledge Graph Traversal

**Starting point:** Backend timeout issue.

**Knowledge graph:**
```
backend-timeout-fix
  ├─→ trace-context-pattern (linked)
  ├─→ backend-health-checks (linked)
  └─→ async-workflow-pattern (via backend-health-checks)
```

**Query:**
```python
kg = KnowledgeGraph()
related = kg.get_related_notes("backend-timeout-fix", distance=2)
# Returns all notes within 2 hops
```

**Result:** Agent discovers `async-workflow-pattern` which solves the broader problem of long-running operations.

---

## Further Reading

**Internal Documentation:**
- [How-To: Query Events](../how-to/query-events.md) - Complete event querying guide
- [Tutorial: Event-Driven Workflow](../tutorials/event-driven-workflow.md) - Using events to trigger workflows
- [Reference: Event Schema](../reference/event-schema.md) - Complete event structure
- [Reference: CLI Reference](../reference/cli-reference.md) - chora-memory command reference
- [Explanation: Architecture](architecture.md) - How memory integrates with gateway

**External Resources:**
- [Zettelkasten Method](https://zettelkasten.de/) - Knowledge linking inspiration
- [OpenTelemetry](https://opentelemetry.io/) - Industry-standard distributed tracing
- [Agentic Coding Best Practices](https://www.anthropic.com/) - A-MEM principles

---

## History

**Evolution of the memory system:**

- **v0.1.0 (Sprint 1-3):** No persistent memory
  - Each session independent
  - Manual log inspection required

- **v0.4.0 (Phase 4.5):** Memory infrastructure introduced
  - Event log with JSONL storage
  - Knowledge graph with Zettelkasten-style linking
  - Trace context propagation (CHORA_TRACE_ID)
  - Agent profiles (capability tracking)

- **v0.4.1 (Phase 4.6):** CLI tools added
  - `chora-memory` command for bash access
  - Query, trace, knowledge, stats, profile subcommands
  - JSON output mode for scripting
  - Human-readable formatting

- **v0.5.0 (Sprint 5):** Workflow integration
  - Daily report workflow uses event log
  - EventWorkflowRouter emits workflow events
  - Trace correlation across workflow steps

---

**Source:** [docs/PHASE_4.5_SUMMARY.md](../../docs/PHASE_4.5_SUMMARY.md), [docs/PHASE_4.6_SUMMARY.md](../../docs/PHASE_4.6_SUMMARY.md), [src/mcp_n8n/memory/](../../src/mcp_n8n/memory/)
**Last Updated:** 2025-10-21
