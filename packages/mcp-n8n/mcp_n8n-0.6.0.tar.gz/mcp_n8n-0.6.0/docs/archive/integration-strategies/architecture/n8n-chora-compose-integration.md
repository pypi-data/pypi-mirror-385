# n8n + chora-compose Integration Architecture

**Date:** 2025-10-20
**Status:** Architecture Analysis
**Context:** Sprint 5 Planning - Workflow Development

---

## Executive Summary

This document clarifies the correct architectural relationship between mcp-n8n, n8n, and chora-compose based on analysis of the chora-compose architecture documentation. It corrects initial misunderstandings about chora-compose's role and provides concrete guidance for Sprint 5 workflow development.

---

## Critical Clarifications

### 1. chora-compose is a Template Engine (NOT a Storage System)

**Key Insight:** chora-compose is like **Jinja2** or **Flask**, NOT a database or storage layer.

**What This Means:**
- ✅ chora-compose **renders** templates to generate content
- ✅ Templates and configs live in **YOUR project** (mcp-n8n), not chora-compose
- ❌ chora-compose does **NOT** provide persistent storage for arbitrary data
- ❌ chora-compose does **NOT** have a query/search API for stored data

**Architecture Analogy:**
```
chora-compose : Templates :: Jinja2 : Templates
chora-compose : Storage :: Jinja2 : Storage  ← Both DON'T provide storage!
```

### 2. NO LLM Integration in Current Version (v1.4.2)

**Critical Correction:**
- Current generators: **Jinja2Generator** (template rendering only)
- NO automatic LLM calls to Claude/GPT
- LLM integration is **planned future** (v0.6.0+)
- Current workflow: YOU call LLM → Pass results to chora-compose template

### 3. Ephemeral Storage is Auto-Generated Content Cache (NOT User Data Storage)

**What Ephemeral Storage Does:**
- Stores **generated content output** (Markdown, HTML, etc.)
- 30-day retention for generated reports/docs
- NOT designed for storing workflow definitions, configs, or structured data

**Example:**
```python
# This generates Markdown report
result = await backend.call_tool("generate_content", {
    "content_config_id": "daily-report",
    "context": {"commits": [...]}
})

# Ephemeral storage holds: Generated Markdown text
# NOT: The commits data, workflow configs, or any input data
```

---

## Answers to Key Architecture Questions

### Q1: Should we use chora-compose to store n8n workflow definitions?

**Answer: NO (but YES for workflow *documentation*)**

**Why NOT for storage:**
1. chora-compose is a **template engine**, not a data store
2. No query/search API for retrieving stored definitions
3. Ephemeral storage designed for generated content, not source data
4. Would be architecturally misaligned

**What TO Use Instead:**
- **Git repositories** - Version-controlled workflow JSON
- **n8n database** - Runtime workflow storage (SQLite/Postgres)
- **Coda/Notion** - If you need structured workflow registry with search

**What chora-compose IS Perfect For:**
```yaml
# ✅ CORRECT USE: Generate workflow DOCUMENTATION from definitions
# Template: chora-configs/templates/workflow-docs.md.j2

# Workflow: {{ workflow.name }}

**Description:** {{ workflow.metadata.description }}
**Trigger:** {{ workflow.trigger.type }}
**Nodes:** {{ workflow.nodes | length }}

## Node Configuration
{% for node in workflow.nodes %}
### {{ node.name }}
- Type: {{ node.type }}
- Parameters: {{ node.parameters | tojson(indent=2) }}
{% endfor %}
```

**Recommended Workflow:**
1. Store workflow definitions in **git** (mcp-n8n/workflows/)
2. Use **chora-compose** to generate documentation from those definitions
3. Auto-update docs when workflows change (CI/CD)

### Q2: Should event-to-workflow mappings be stored in chora-compose?

**Answer: NO (but YES for mapping *documentation*)**

**Revised Architecture:**

```yaml
# ❌ WRONG: Store mappings as chora-compose "content"
# chora-compose has no query API to retrieve this at runtime!

# ✅ CORRECT: Store mappings as Python/YAML config in mcp-n8n
# File: mcp-n8n/config/event_workflow_mappings.yaml

mappings:
  - event_pattern:
      type: "gateway.tool_call"
      backend: "chora-composer"
      status: "success"
    workflow:
      id: "chora-success-notification"
      parameters:
        tool: "{{ event.data.tool_name }}"

  - event_pattern:
      type: "gateway.tool_call"
      status: "failure"
    workflow:
      id: "error-alert-workflow"
```

**Use chora-compose to DOCUMENT the mappings:**

```jinja2
{# templates/event-mappings-doc.md.j2 #}
# Event-to-Workflow Routing Documentation

## Configured Mappings

{% for mapping in mappings %}
### Mapping {{ loop.index }}: {{ mapping.workflow.id }}

**Triggers when:**
{% for key, value in mapping.event_pattern.items() %}
- {{ key }}: `{{ value }}`
{% endfor %}

**Executes workflow:** `{{ mapping.workflow.id }}`
**Parameters:** {{ mapping.workflow.parameters | tojson(indent=2) }}

---
{% endfor %}
```

**Generation:**
```python
# Read mappings from file
with open("config/event_workflow_mappings.yaml") as f:
    mappings = yaml.safe_load(f)

# Generate documentation
await backend.call_tool("generate_content", {
    "content_config_id": "event-mappings-docs",
    "context": {"mappings": mappings}
})
# Result: Beautiful Markdown documentation of routing logic
```

### Q3: Pattern Relevance - Revised Assessment

#### ✅ Pattern N3: n8n as MCP Client + chora-compose for Template-Based Reports

**HIGHLY RELEVANT** - This is the sweet spot!

```
n8n Workflow: "Generate Daily Report"
    ↓
1. Gather Data (git commits, events, metrics)
    ↓
2. Call chora:generate_content with data as context
    ↓
3. chora-compose renders Jinja2 template with data
    ↓
4. Returns formatted Markdown report
    ↓
5. Send to Slack / Save to docs/
```

**Why This Works:**
- n8n orchestrates data gathering
- chora-compose formats data into readable reports
- Templates ensure consistent report structure
- No LLM needed (pure template rendering)

#### ✅ Pattern N6: Event Processing + chora-compose for Event Summaries

**RELEVANT** - But architecture differs from initial proposal

**REVISED Architecture:**

```
Gateway Event → EventLog (append-only)
    ↓
EventWorkflowRouter (reads YAML config file)
    ↓
Match pattern → Trigger n8n workflow
    ↓
n8n workflow calls chora:generate_content
    ↓
Generate event summary report (template-based)
    ↓
Send notification / Log report
```

**Key Difference:**
- Mappings stored in **YAML config file** (not chora-compose)
- chora-compose generates **event summaries** (documentation)
- Router loads mappings from filesystem (not via MCP tool)

#### ❌ Pattern N7: Conversational Config Authoring - NOT APPLICABLE

**Why Not:**
- chora-compose v1.4.2 has NO LLM integration
- Cannot auto-generate workflow configs from conversation
- Would need external LLM orchestration (not chora-compose's role)

---

## Recommended Implementation Architecture

```
┌─────────────────────────────────────────────────────────┐
│ mcp-n8n + n8n + chora-compose Integration              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Layer 1: Data Storage (Git + Filesystem)               │
│   ├─ workflows/ (n8n workflow JSON definitions)        │
│   ├─ config/ (event-to-workflow mappings YAML)         │
│   └─ chora-configs/ (templates + content configs)      │
│          ↓                                              │
│ Layer 2: Event Source (EventLog)                       │
│   ├─ Emits events (gateway.tool_call, etc.)            │
│   └─ Monthly partitioned append-only files             │
│          ↓                                              │
│ Layer 3: Event Router (Python code)                    │
│   ├─ Loads mappings from config/event_mappings.yaml    │
│   ├─ Matches events against patterns                   │
│   └─ Triggers n8n workflows                            │
│          ↓                                              │
│ Layer 4: Workflow Execution (n8n)                      │
│   ├─ Loads workflow definitions from workflows/        │
│   ├─ Gathers data (git, APIs, EventLog)                │
│   ├─ Calls chora:generate_content for formatting       │
│   └─ Outputs reports/notifications                     │
│          ↓                                              │
│ Layer 5: Documentation Generation (chora-compose)      │
│   ├─ Templates render data → Markdown/HTML             │
│   ├─ NO LLM calls (pure Jinja2 rendering)              │
│   ├─ Ephemeral storage for generated docs (30 days)    │
│   └─ Returns formatted content to n8n                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Concrete Example: Daily Report

### File Structure
```
mcp-n8n/
├── workflows/
│   └── daily-report.json           # n8n workflow definition (git-tracked)
├── config/
│   └── event_mappings.yaml         # Event-to-workflow routing config
├── chora-configs/
│   ├── templates/
│   │   └── daily-report.md.j2      # Jinja2 template
│   └── content/
│       └── daily-report.json       # chora-compose content config
```

### n8n Workflow Definition
```json
{
  "name": "Daily Report Generator",
  "nodes": [
    {
      "name": "Get Git Commits",
      "type": "bash",
      "command": "git log --since='24h' --format='%H|%an|%s'"
    },
    {
      "name": "Get Gateway Events",
      "type": "bash",
      "command": "python -m mcp_n8n.memory.event_log query --since=24h"
    },
    {
      "name": "Format Report",
      "type": "mcp-tool-call",
      "mcp_server": "chora-compose",
      "tool": "generate_content",
      "args": {
        "content_config_id": "daily-report",
        "context": {
          "commits": "={{ $node['Get Git Commits'].json }}",
          "events": "={{ $node['Get Gateway Events'].json }}"
        }
      }
    },
    {
      "name": "Send to Slack",
      "type": "slack",
      "text": "={{ $node['Format Report'].json.content }}"
    }
  ]
}
```

### Event Mapping Config (YAML, not chora-compose)
```yaml
# config/event_mappings.yaml
mappings:
  - event_pattern:
      type: "manual.request"
      action: "generate_daily_report"
    workflow:
      id: "daily-report-generator"
      namespace: "n8n"
```

### chora-compose Template (Jinja2)
```jinja2
{# chora-configs/templates/daily-report.md.j2 #}
# Daily Report - {{ date }}

## Git Activity
- Total commits: {{ commits | length }}

{% for commit in commits[:10] %}
- `{{ commit.hash[:7] }}` {{ commit.message }} ({{ commit.author }})
{% endfor %}

## Gateway Events
- Total events: {{ events | length }}
- Tool calls: {{ events | selectattr('type', 'equalto', 'gateway.tool_call') | list | length }}
- Errors: {{ events | selectattr('status', 'equalto', 'error') | list | length }}
```

---

## Key Takeaways

1. **chora-compose = Template Engine, NOT Storage**
   - Use for: Generating documentation from data
   - NOT for: Storing workflow definitions or configs

2. **Store Configs in Git/Filesystem**
   - Workflow definitions: `workflows/*.json` (git)
   - Event mappings: `config/event_mappings.yaml` (git)
   - chora-compose configs: `chora-configs/` (git)

3. **Use chora-compose for Formatting, Not Orchestration**
   - n8n: Orchestrates workflows, gathers data
   - chora-compose: Formats data into readable reports
   - EventRouter: Routes events (reads YAML configs from filesystem)

4. **Dynamic Loading = Hot Reload Config Files**
   - Watch `config/event_mappings.yaml` for changes
   - Reload mappings without restarting gateway
   - Use filesystem watcher, not chora-compose storage

5. **Documentation Generation is the Killer Use Case**
   - Generate workflow documentation from definitions
   - Generate event routing documentation from configs
   - Generate daily/weekly reports from telemetry
   - Keep docs in sync via CI/CD triggers

---

## Implications for Sprint 5

### What TO Build
1. **EventWorkflowRouter** - Python class that reads YAML configs and routes events to n8n workflows
2. **n8n workflows** - JSON definitions stored in git, executed via n8n backend
3. **chora-compose templates** - Jinja2 templates for report formatting
4. **Config hot-reload** - Watch event_mappings.yaml for changes

### What NOT TO Build
1. ~~chora-compose storage layer for workflows~~ - Use git instead
2. ~~LLM-powered config generation~~ - Not supported in v1.4.2
3. ~~Query API for stored configs~~ - Use filesystem reads

### Architecture Wins
- **Separation of concerns** - Storage (git), orchestration (n8n), formatting (chora-compose)
- **Hot-reloadable configs** - Change mappings without code deployment
- **Version-controlled everything** - Workflows, mappings, templates all in git
- **Consistent documentation** - Auto-generate from source of truth

---

## References

- [n8n Integration Patterns](../ecosystem/n8n-solution-neutral-intent.md)
- [chora-compose Architecture](../ecosystem/chora-compose-architecture.md)
- [chora-compose Solution-Neutral Intent](../ecosystem/chora-compose-solution-neutral-intent.md)
- [Strategic Design Framework](../../AGENTS.md#strategic-design)

---

**Status:** Architecture validated ✅
**Next Steps:** Begin Sprint 5 implementation with correct architecture
**Decision:** Use chora-compose for **formatting only**, not storage
