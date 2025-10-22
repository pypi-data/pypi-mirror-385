---
title: "Understanding Integration Patterns"
type: explanation
audience: intermediate
category: design-patterns
source: "docs/archive/ecosystem/n8n-solution-neutral-intent.md, dev-docs/ARCHITECTURE.md"
last_updated: 2025-10-21
---

# Understanding Integration Patterns

## Overview

Integration patterns define **how different systems connect and coordinate** within the Chora ecosystem. This document explains the key patterns used in mcp-n8n and how they enable flexible, composable workflows.

**The core idea:** Instead of hardcoding integrations, use proven patterns that separate concerns, enable independent evolution, and make systems composable.

## Context

### Background: The Integration Problem

Modern AI-native development involves multiple specialized systems:
- **AI clients** (Claude Desktop, Cursor) that need tools
- **Tool providers** (Chora Composer, Coda MCP) that expose capabilities
- **Workflow orchestrators** (n8n, custom code) that coordinate multi-step processes
- **Data sources** (GitHub, Jira, databases) that provide context
- **Event systems** (webhooks, message queues) that trigger automation

**The problem:** Each pair of systems needs integration code. With N systems, you potentially need N×(N-1)/2 integration points—a combinatorial explosion.

### The Pattern Approach

Integration patterns solve this by:
1. **Standardizing interfaces** - Systems speak common protocols (MCP, HTTP, JSONL)
2. **Separating concerns** - Routing logic separate from business logic
3. **Enabling composition** - Patterns combine to solve complex problems
4. **Supporting evolution** - Systems can change independently

### Alternatives Considered

**1. Point-to-Point Integration**
- ❌ Every system directly calls every other system
- ❌ N×(N-1)/2 integration points
- ❌ Brittle (changes cascade)
- ✅ Simple for 2-3 systems

**2. Monolithic Platform**
- ❌ All capabilities in one codebase
- ❌ Tight coupling
- ❌ Slow coordinated change
- ✅ Unified interface

**3. Pattern-Based Integration (Chosen)**
- ✅ Standard interfaces (MCP protocol)
- ✅ Modular (add/remove systems easily)
- ✅ Composable (patterns combine)
- ⚠️ Requires learning patterns

---

## The Patterns

### Pattern P5: Gateway & Aggregator

**Intent:** Provide a **single unified interface** to multiple specialized backend servers, routing requests automatically based on tool names.

**Problem:** AI clients would need to connect separately to each MCP server (Chora Composer, Coda MCP, custom servers), managing multiple configurations and credentials.

**Solution:** One gateway server aggregates all backend tools, routes calls based on namespace prefixes.

**Architecture:**
```
┌─────────────────────────────────┐
│  AI Client (Claude Desktop)     │
│  "I need chora:assemble_artifact"│
└───────────────┬─────────────────┘
                │
                │ Single MCP connection
                ▼
┌───────────────────────────────────────────┐
│         mcp-n8n Gateway (P5)              │
│  ┌─────────────────────────────────────┐ │
│  │ Tool Catalog (Aggregated):          │ │
│  │  - chora:assemble_artifact          │ │
│  │  - chora:generate_content           │ │
│  │  - coda:list_docs                   │ │
│  │  - coda:create_rows                 │ │
│  │  - gateway_status                   │ │
│  └─────────────────────────────────────┘ │
└───────────┬───────────────┬───────────────┘
            │               │
            │ Routes by     │
            │ namespace     │
            ▼               ▼
    ┌──────────────┐  ┌──────────────┐
    │ chora-compose│  │   coda-mcp   │
    │  (Backend 1) │  │  (Backend 2) │
    └──────────────┘  └──────────────┘
```

**Key Decisions:**

1. **Tool Namespacing**
   - Each backend has a unique namespace (`chora:`, `coda:`)
   - Gateway parses `namespace:tool_name` and routes accordingly
   - Prevents name collisions between backends

2. **Subprocess Isolation**
   - Each backend runs as separate subprocess
   - Failures isolated (Coda crash won't affect Chora)
   - Process-level security boundary

3. **Capability Aggregation**
   - Gateway merges tool lists from all backends
   - Client sees one unified catalog
   - `tools/list` returns all namespaced tools

**Request Flow:**

```
1. Client → Gateway: tools/call("chora:assemble_artifact", args)
2. Gateway: Parse namespace "chora"
3. Gateway → Registry: route_tool_call("chora:assemble_artifact")
4. Registry: Lookup backend by namespace → finds ChoraBackend
5. Registry → ChoraBackend: call_tool("assemble_artifact", args)
6. ChoraBackend → subprocess: JSON-RPC over STDIO
7. subprocess → ChoraBackend: Return result
8. ChoraBackend → Gateway: Forward result
9. Gateway → Client: Return result
```

**Benefits:**
- ✅ **Simplified configuration:** One MCP server entry in Claude Desktop config
- ✅ **Automatic routing:** Client doesn't need to know which backend handles which tool
- ✅ **Centralized credentials:** All API keys in one `.env` file
- ✅ **Unified telemetry:** Single event log for all operations
- ✅ **Failure isolation:** Backend crashes don't cascade

**Limitations:**
- ⚠️ **Routing overhead:** ~10ms per request (negligible for most use cases)
- ❌ **Single-tenant only:** Current STDIO transport supports one client
- ⚠️ **Namespace required:** All tools must follow `namespace:name` convention

**When to use:**
- Multiple MCP servers needed (2+)
- Want simplified client configuration
- Need centralized monitoring
- Backends can operate independently

**Real Example (mcp-n8n):**
```python
# Gateway configuration
config.get_all_backend_configs()
# Returns: [chora-composer config, coda-mcp config]

# Gateway aggregates tools
registry.get_all_tools()
# Returns: [
#   {"name": "chora:assemble_artifact", ...},
#   {"name": "chora:generate_content", ...},
#   {"name": "coda:list_docs", ...},
#   {"name": "coda:create_rows", ...}
# ]

# Client calls tool
client.call("chora:assemble_artifact", {"config_id": "docs"})
# Gateway routes to chora-composer backend automatically
```

---

### Pattern N2: n8n as MCP Server

**Intent:** Expose n8n workflow executions as **MCP tools**, allowing AI agents to trigger complex multi-step automations on demand.

**Problem:** AI agents can only do what their tools allow. Creating a new tool requires coding a new MCP server. n8n already has 400+ integrations, but they're not accessible to AI.

**Solution:** Wrap n8n's REST API as an MCP server, exposing workflows as tools.

**Architecture:**
```
┌─────────────────────────────────┐
│  AI Client (Claude Desktop)     │
│  "Please generate sales report" │
└───────────────┬─────────────────┘
                │
                │ MCP protocol
                ▼
┌───────────────────────────────────────────┐
│         n8n MCP Server                    │
│  Tools:                                   │
│   - n8n:list_workflows                    │
│   - n8n:execute_workflow                  │
│   - n8n:get_execution_status              │
│   - n8n:get_execution_result              │
└───────────────┬───────────────────────────┘
                │
                │ n8n REST API
                ▼
┌───────────────────────────────────────────┐
│         n8n Workflow Engine               │
│  Workflow: "monthly-sales-report"         │
│    1. Fetch Salesforce data               │
│    2. Generate charts (Python)            │
│    3. Upload to Coda                      │
│    4. Return doc URL                      │
└───────────────────────────────────────────┘
```

**Tool Definitions:**

```typescript
// n8n:execute_workflow
{
  name: "n8n:execute_workflow",
  description: "Execute an n8n workflow by ID or name",
  inputSchema: {
    type: "object",
    properties: {
      workflow_id: { type: "string", description: "Workflow ID" },
      parameters: { type: "object", description: "Workflow input parameters" },
      wait_for_completion: { type: "boolean", default: true }
    },
    required: ["workflow_id"]
  }
}
```

**Interaction Pattern:**

```
1. AI Agent: "Generate monthly sales report"
2. Claude → MCP: n8n:execute_workflow("monthly-sales-report", {month: "October"})
3. n8n MCP Server → n8n API: POST /workflows/monthly-sales-report/execute
4. n8n: Executes workflow (may take seconds/minutes)
5. n8n → n8n MCP Server: Execution result + output data
6. n8n MCP Server → Claude: {"report_url": "https://coda.io/..."}
7. Claude → User: "Here's your report: [link]"
```

**Benefits:**
- ✅ **Instant AI access:** 400+ n8n integrations available to AI agents
- ✅ **No coding:** Expose workflows as tools via configuration
- ✅ **Visual debugging:** n8n UI shows execution history
- ✅ **Complex orchestration:** Workflows handle multi-step logic

**Limitations:**
- ❌ **Workflows must be pre-created:** AI can't generate new workflows dynamically
- ⚠️ **Async execution:** Long-running workflows require polling or webhooks
- ❌ **No type safety:** Parameter validation relies on n8n schemas

**When to use:**
- Have existing n8n workflows to expose
- Want AI agents to trigger business processes
- Need to integrate AI with legacy systems (via n8n connectors)

**Real Example:**
```python
# Workflow: "generate-weekly-report"
# Steps in n8n:
#   1. HTTP Request → GitHub API (commits)
#   2. HTTP Request → Jira API (tickets closed)
#   3. Function → Calculate metrics
#   4. Chora Composer → Generate markdown
#   5. Coda → Upload report

# AI Agent call:
client.call("n8n:execute_workflow", {
    "workflow_id": "generate-weekly-report",
    "parameters": {"week": "2025-W42"}
})

# Result: {"report_url": "https://coda.io/d/..."}
```

---

### Pattern N3: n8n as MCP Client

**Intent:** Allow n8n workflows to **consume MCP tools**, combining low-code automation with AI-powered capabilities.

**Problem:** n8n excels at integrating APIs and databases, but lacks AI-native capabilities (content generation, semantic analysis). MCP servers provide these, but n8n can't call them natively.

**Solution:** Custom n8n node that acts as MCP client, allowing workflows to invoke any MCP tool.

**Architecture:**
```
┌───────────────────────────────────────────┐
│         n8n Workflow                      │
│  "Create documentation from GitHub issue" │
│                                            │
│  1. GitHub Trigger (new issue)            │
│  2. ↓                                      │
│  3. MCP Tool Call Node                    │
│     └→ chora:generate_content             │
│  4. ↓                                      │
│  5. MCP Tool Call Node                    │
│     └→ chora:assemble_artifact            │
│  6. ↓                                      │
│  7. GitHub: Comment with doc link         │
└───────────────┬───────────────────────────┘
                │
                │ MCP protocol (STDIO or HTTP)
                ▼
┌───────────────────────────────────────────┐
│         MCP Servers                       │
│  - Chora Composer (content generation)   │
│  - Coda MCP (data storage)                │
│  - Filesystem MCP (file operations)       │
└───────────────────────────────────────────┘
```

**Custom Node: MCP Tool Call**

```javascript
// n8n custom node: @chora/mcp-tool-call
{
  displayName: "MCP Tool Call",
  name: "mcpToolCall",
  icon: "file:mcp.svg",
  group: ["transform"],
  version: 1,
  description: "Call a tool from an MCP server",
  defaults: {
    name: "MCP Tool Call"
  },
  inputs: ["main"],
  outputs: ["main"],
  properties: [
    {
      displayName: "MCP Server",
      name: "server",
      type: "options",
      options: [
        {name: "Chora Composer", value: "chora-composer"},
        {name: "Coda MCP", value: "coda-mcp"}
      ],
      default: "chora-composer"
    },
    {
      displayName: "Tool Name",
      name: "tool",
      type: "options",
      typeOptions: {
        loadOptionsMethod: "getToolsForServer"  // Dynamic loading
      }
    },
    {
      displayName: "Arguments",
      name: "arguments",
      type: "json",
      default: "{}"
    }
  ]
}
```

**Workflow Example:**

```
Trigger: GitHub issue labeled "needs-docs"
  ↓
Extract issue data: {title, body, labels}
  ↓
MCP Tool Call: chora:generate_content
  Input: {
    template: "issue-to-docs",
    context: {issue_title, issue_body}
  }
  Output: {content: "# Documentation\n\n..."}
  ↓
MCP Tool Call: chora:assemble_artifact
  Input: {
    config_id: "technical-docs",
    content_sections: [...]
  }
  Output: {artifact_path: "/docs/new-feature.md"}
  ↓
GitHub: Create pull request with new docs
GitHub: Comment on issue with PR link
```

**Benefits:**
- ✅ **AI capabilities in workflows:** Content generation, semantic analysis, etc.
- ✅ **Combine strengths:** n8n orchestration + MCP specialized tools
- ✅ **Visual workflow:** See entire pipeline in n8n UI
- ✅ **Reusable patterns:** Save workflow templates

**Limitations:**
- ❌ **Requires custom node:** Must develop and maintain `@chora/mcp-tool-call` node
- ⚠️ **MCP transport complexity:** STDIO (subprocess) vs HTTP (remote) requires different handling
- ❌ **Debugging complexity:** Errors can occur in n8n or MCP layers

**When to use:**
- Workflows need AI-powered content generation
- Want to combine n8n integrations with MCP capabilities
- Need visual representation of complex AI workflows

---

### Pattern N5: Artifact Assembly Pipeline

**Intent:** Use n8n to **orchestrate multi-stage artifact creation**, gathering data from multiple sources and coordinating Chora Composer calls.

**Problem:** Complex artifacts require data from many systems (GitHub, Jira, databases) and multiple generation steps. Coding these pipelines is time-consuming and hard to maintain.

**Solution:** Visual workflow in n8n that fetches data, calls Chora Composer for each section, assembles final artifact, and distributes results.

**Architecture:**
```
┌───────────────────────────────────────────┐
│  n8n Workflow: "Weekly Engineering Report"│
│                                            │
│  1. GitHub API → Fetch commits (7 days)   │
│  2. Jira API → Fetch tickets closed       │
│  3. DataDog API → Fetch metrics            │
│  4. ↓                                      │
│  5. FOR EACH data source:                 │
│      MCP: chora:generate_content          │
│        (template: section-template)       │
│  6. ↓                                      │
│  7. MCP: chora:assemble_artifact          │
│     (config: weekly-eng-report)           │
│  8. ↓                                      │
│  9. Coda API → Upload artifact metadata   │
│ 10. Slack API → Send notification         │
└───────────────┬───────────────────────────┘
                │
                │ Calls multiple systems
                ▼
┌─────────────┬──────────────┬──────────────┐
│   GitHub    │     Jira     │   DataDog    │
│  (commits)  │  (tickets)   │  (metrics)   │
└─────────────┴──────────────┴──────────────┘
                │
                │ MCP calls
                ▼
┌───────────────────────────────────────────┐
│       Chora Composer                      │
│  - generate_content (per section)         │
│  - assemble_artifact (final report)       │
└───────────────────────────────────────────┘
```

**Workflow Steps:**

```javascript
// n8n Workflow JSON (simplified)
{
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": { "interval": [{"field": "weeks", "value": 1}] }
      }
    },
    {
      "name": "Fetch GitHub Commits",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.github.com/repos/org/repo/commits",
        "qs": {
          "since": "={{$now.minus({days: 7}).toISO()}}"
        }
      }
    },
    {
      "name": "Generate Commit Summary",
      "type": "@chora/mcp-tool-call",
      "parameters": {
        "server": "chora-composer",
        "tool": "generate_content",
        "arguments": {
          "template": "commit-summary",
          "context": "={{$json}}"
        }
      }
    },
    // ... similar nodes for Jira, DataDog
    {
      "name": "Assemble Final Report",
      "type": "@chora/mcp-tool-call",
      "parameters": {
        "server": "chora-composer",
        "tool": "assemble_artifact",
        "arguments": {
          "config_id": "weekly-eng-report",
          "sections": "={{$json.sections}}"
        }
      }
    },
    {
      "name": "Send Slack Notification",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#engineering",
        "text": "Weekly report ready: {{$json.artifact_url}}"
      }
    }
  ]
}
```

**Benefits:**
- ✅ **Automate recurring reports:** Schedule weekly/monthly artifact generation
- ✅ **Integrate business data:** Pull from GitHub, Jira, Salesforce, databases
- ✅ **Visual pipeline:** See entire process in n8n canvas
- ✅ **Easy to modify:** Non-developers can adjust data sources or templates

**Limitations:**
- ⚠️ **Workflow complexity:** Many-stage pipelines hard to debug
- ❌ **Performance overhead:** n8n execution adds latency vs. custom code
- ⚠️ **Versioning challenges:** Workflow JSON harder to version control than code

**When to use:**
- Scheduled artifact generation (reports, newsletters, dashboards)
- Artifacts require data from 3+ different systems
- Want visual representation of data pipeline
- Team prefers low-code to custom Python/TypeScript

**Real Example:**
```
Use Case: Daily Sprint Report

Data Sources:
- Jira (tickets completed, in-progress, blocked)
- GitHub (PRs merged, commits)
- Slack (team messages, sentiment analysis)
- TestRail (test pass rate)

Workflow:
1. Fetch data from all 4 sources (parallel)
2. For each source, call chora:generate_content with source-specific template
3. Call chora:assemble_artifact to combine sections
4. Store in Coda for historical tracking
5. Post to Slack #daily-standup channel
6. Email report to stakeholders

Result: Automated daily report generated at 8 AM, no manual effort
```

---

## How Patterns Combine

**Scenario: AI-Driven Documentation Pipeline**

**Goal:** AI agent requests documentation, n8n orchestrates multi-source artifact creation.

**Pattern Combination:**

1. **P5 (Gateway):** AI client connects to mcp-n8n gateway
2. **N2 (n8n as MCP Server):** Gateway exposes `n8n:create_documentation` tool
3. **N5 (Artifact Pipeline):** n8n workflow orchestrates:
   - Fetch code from GitHub
   - Fetch specs from Coda
   - Call `chora:generate_content` (via **N3: n8n as MCP Client**)
   - Call `chora:assemble_artifact`
   - Store result back in Coda

**Architecture:**
```
AI Client (Claude)
    ↓ MCP
mcp-n8n Gateway (P5)
    ├→ chora:* tools (direct)
    └→ n8n:create_documentation (N2)
        ↓ (n8n workflow - N5)
        ├→ GitHub API (fetch code)
        ├→ Coda API (fetch specs)
        ├→ MCP: chora:generate_content (N3)
        ├→ MCP: chora:assemble_artifact (N3)
        └→ Coda API (store artifact)
```

**Result:** AI agent triggers complex multi-system workflow via single MCP tool call. Patterns compose to solve sophisticated automation needs.

---

## Comparison to Alternatives

### vs. Monolithic Integration

| Aspect | Patterns (Chosen) | Monolithic |
|--------|-------------------|------------|
| Flexibility | ✅ Add/remove backends easily | ❌ Requires codebase changes |
| Development Speed | ✅ Independent backend evolution | ❌ Coordinated releases |
| Failure Isolation | ✅ Backend failures isolated | ❌ Failures cascade |
| Complexity | ⚠️ Must learn patterns | ✅ Single codebase |

**When to use Monolithic:**
- Small team (2-3 developers)
- All capabilities tightly coupled
- Performance critical (no routing overhead)

### vs. Direct Point-to-Point

| Aspect | Patterns (Chosen) | Point-to-Point |
|--------|-------------------|----------------|
| Integration Points | ✅ O(N) via gateway | ❌ O(N²) direct connections |
| Configuration | ✅ Centralized | ❌ Scattered |
| Telemetry | ✅ Unified | ❌ Per-integration |
| Coupling | ✅ Loose (via MCP) | ❌ Tight |

**When to use Point-to-Point:**
- Only 2-3 systems
- Extremely low latency required (<1ms)
- Systems owned by same team

---

## Further Reading

**Internal Documentation:**
- [Explanation: Architecture](architecture.md) - Deep dive on P5 gateway implementation
- [How-To: Configure Backends](../how-to/configure-backends.md) - Add custom backends to gateway
- [How-To: Build Custom Workflow](../how-to/build-custom-workflow.md) - Implement N5-style pipelines
- [Tutorial: Event-Driven Workflow](../tutorials/event-driven-workflow.md) - Event routing patterns

**External Resources:**
- [MCP Specification](https://modelcontextprotocol.io/) - Protocol details
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/) - Classic integration patterns
- [n8n Documentation](https://docs.n8n.io/) - Workflow automation platform

---

## History

**Evolution of integration patterns in mcp-n8n:**

- **v0.1.0 (Sprint 1):** Single backend (Chora Composer only)
  - No patterns needed, direct integration

- **v0.2.0 (Sprint 2):** Pattern P5 introduced
  - Multiple backends (Chora + Coda)
  - Gateway pattern implemented
  - Namespace-based routing

- **v0.3.0 (Sprint 3):** Event monitoring added
  - Event-driven integration patterns
  - Webhook support for external events

- **v0.4.0 (Sprint 4):** Memory system integration
  - Telemetry patterns for observability
  - Cross-service tracing

- **v0.5.0 (Sprint 5):** Workflow orchestration
  - N5-style artifact pipelines (daily report workflow)
  - Event-driven workflow routing

- **Future:** N2, N3 patterns (n8n integration)
  - MCP Server wrapper for n8n
  - Custom n8n node for MCP client
  - Full N5 artifact pipeline support

---

**Source:** [docs/archive/ecosystem/n8n-solution-neutral-intent.md](../archive/ecosystem/n8n-solution-neutral-intent.md), [dev-docs/ARCHITECTURE.md](../../dev-docs/ARCHITECTURE.md)
**Last Updated:** 2025-10-21
