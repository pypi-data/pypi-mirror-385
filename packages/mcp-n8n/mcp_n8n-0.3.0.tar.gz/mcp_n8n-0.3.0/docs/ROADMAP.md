# mcp-n8n Roadmap

**Version:** 1.0.0
**Date:** 2025-10-17
**Status:** Active
**Document Type:** Implementation Roadmap
**Scope:** mcp-n8n Gateway & Aggregator Development Plan

---

## Executive Summary

This roadmap defines the **phased development plan** for mcp-n8n, an MCP Gateway & Aggregator (Pattern P5) that orchestrates multiple MCP servers with a focus on Chora Composer as the exclusive artifact creation mechanism.

**Key Insight:** mcp-n8n development is **tightly coupled** with chora-composer releases. This roadmap structures phases to:
1. **Validate integration assumptions** early (Phase 0)
2. **Inform chora-composer v1.2.0 design** through real-world usage (Phase 1)
3. **Consume chora-composer v1.2.0 capabilities** for production features (Phase 2)
4. **Prepare for ecosystem maturation** alongside chora v1.3.0 (Phase 3)

**Strategic Use Case:** The "Weekly Engineering Report" workflow (Pattern N5) serves as the primary validation vehicle, exercising the full integration stack from data gathering through artifact assembly to publication.

---

## Table of Contents

1. [Foundation & Context](#foundation--context)
2. [Dependency Model](#dependency-model)
3. [Phase 0: Foundation Validation](#phase-0-foundation-validation-week-1-2)
4. [Phase 1: Essential Gateway Capabilities](#phase-1-essential-gateway-capabilities-week-3-6)
5. [Phase 2: Advanced Gateway Features](#phase-2-advanced-gateway-features-week-7-10)
6. [Phase 3: Ecosystem Maturation](#phase-3-ecosystem-maturation-week-11-14)
7. [Cross-Phase Concerns](#cross-phase-concerns)
8. [Risk Management](#risk-management)
9. [Success Metrics](#success-metrics)
10. [Team Coordination](#team-coordination)

---

## Foundation & Context

### Current State (v0.1.0)

**What Exists:**
- ✅ Pattern P5 gateway infrastructure (FastMCP-based)
- ✅ Backend registry with tool namespacing (`chora:*`, `coda:*`)
- ✅ Chora Composer backend integration (subprocess-based)
- ✅ Coda MCP backend integration
- ✅ Configuration management (Pydantic + environment variables)
- ✅ Basic tests (configuration, registry routing)
- ✅ Comprehensive documentation (ARCHITECTURE.md, GETTING_STARTED.md)

**What's Missing:**
- ❌ Real-world workflow validation
- ❌ Production telemetry integration
- ❌ Event monitoring from chora-composer
- ❌ Gateway-aware capability discovery
- ❌ Preview workflow patterns
- ❌ Performance benchmarks
- ❌ n8n MCP server/client patterns

### Three-Layer Architecture

Understanding layer responsibility is critical for roadmap planning:

```
Layer 3: Capabilities (Consumption)
├─ mcp-n8n Gateway               ← THIS PROJECT
├─ n8n workflows (orchestration)
├─ AI agents (Claude, Cursor)
└─ Business applications
         ↑ MCP Protocol
         │
Layer 2: Platform (Distribution)
├─ chora-composer (atomic capabilities)
├─ coda-mcp (data operations)
└─ Future platform services
         ↑ Local Development
         │
Layer 1: Workspace (R&D)
└─ Individual developer repos
```

**mcp-n8n Responsibility:** Layer 3 orchestration
- Multi-backend workflow composition
- Event-driven automation
- Gateway routing and aggregation
- Cross-service coordination

**NOT mcp-n8n Responsibility:** Layer 2 capabilities
- Artifact generation logic → chora-composer
- Content validation → chora-composer
- Direct external service integration → dedicated MCP servers

---

## Dependency Model

### Synchronized Release Cadence

```
┌─────────────────┐
│ mcp-n8n Phase 0 │  Validate current integration
│   (Week 1-2)    │
└────────┬────────┘
         │ informs requirements
         ▼
┌─────────────────┐
│ chora-composer  │  Add generator deps, limits, events
│    v1.1.1       │  (Patch - 1 week)
│                 │
└────────┬────────┘
         │ enables
         ▼
┌─────────────────┐
│ mcp-n8n Phase 1 │  Build essential gateway features
│   (Week 3-6)    │  Weekly Engineering Report workflow
│                 │  Provide v1.2.0 feedback
└────────┬────────┘
         │ informs design
         ▼
┌─────────────────┐
│ chora-composer  │  Gateway context, preview, telemetry
│    v1.2.0       │  (Minor - 3-4 weeks)
│                 │
└────────┬────────┘
         │ enables
         ▼
┌─────────────────┐
│ mcp-n8n Phase 2 │  Consume gateway-aware features
│   (Week 7-10)   │  Production workflows
│                 │
└────────┬────────┘
         │ parallel development
         ▼
┌─────────────────┬────────────────┐
│ chora-composer  │  mcp-n8n       │
│    v1.3.0       │  Phase 3       │
│                 │  (Week 11-14)  │
│ Context Bus     │  Advanced      │
│ Integration     │  Patterns      │
└─────────────────┴────────────────┘
```

### Critical Path Items

**BLOCKING Dependencies:**
- Phase 1 cannot complete without chora-composer v1.1.1 (generator deps for credential validation)
- Phase 2 cannot start without chora-composer v1.2.0 (gateway-aware capabilities)

**INFORMING Dependencies:**
- chora-composer v1.2.0 design should incorporate feedback from Phase 1 Week 6
- chora-composer v1.3.0 context bus design should align with Phase 3 patterns

---

## Phase 0: Foundation Validation (Week 1-2)

**Status:** IMMEDIATE PRIORITY
**Goal:** Validate that current mcp-n8n implementation works with chora-composer v1.1.0 before either team invests in enhancements
**Release:** mcp-n8n v0.1.1 (patch with integration fixes)

### Deliverables

#### 1. Integration Smoke Tests (Week 1)

**Objective:** Prove end-to-end integration works

**Tasks:**
- [ ] Deploy mcp-n8n gateway locally with chora-composer v1.1.0 submodule
- [ ] Test `chora:generate_content` via gateway
  - Verify namespace routing works
  - Verify result passes through correctly
  - Document latency overhead
- [ ] Test `chora:assemble_artifact` via gateway
  - Complete artifact assembly workflow
  - Verify output files created
  - Check telemetry logs
- [ ] Test `coda:list_docs` and other Coda tools
  - Verify multi-backend routing
  - Test namespace isolation
- [ ] Document all integration issues found

**Success Criteria:**
- ✅ All tools callable through gateway
- ✅ Namespace routing works correctly
- ✅ No data corruption in forwarding
- ✅ Error messages surface correctly to client

**Risks:**
- May discover blocking issues requiring architecture changes
- Subprocess communication may need debugging

---

#### 2. "Hello World" Workflow (Week 1)

**Objective:** Prove simplest possible n8n workflow end-to-end

**Workflow Design:**
```
Manual Trigger
    ↓
HTTP Request (fetch sample data)
    ↓
MCP Tool Call: chora:assemble_artifact
    ↓
Slack Notification (or log output)
```

**Tasks:**
- [ ] Install n8n locally (`npx n8n`)
- [ ] Create workflow in n8n UI
- [ ] Configure mcp-n8n connection (if using custom node, or HTTP endpoint)
- [ ] Execute workflow manually
- [ ] Verify artifact created
- [ ] Document workflow JSON export
- [ ] Measure end-to-end execution time

**Success Criteria:**
- ✅ Workflow executes without errors
- ✅ Artifact created in expected location
- ✅ Execution time < 30 seconds
- ✅ Workflow JSON exported and committed

**Deliverable:** `workflows/hello-world.json`

---

#### 3. Submodule Management Process (Week 2)

**Objective:** Establish process for tracking chora-composer releases

**Tasks:**
- [ ] Document how to update chora-composer submodule
  ```bash
  # Update to latest commit
  git submodule update --remote chora-composer

  # Update to specific version
  cd chora-composer
  git checkout v1.1.1
  cd ..
  git add chora-composer
  git commit -m "Update chora-composer to v1.1.1"
  ```
- [ ] Create smoke test script (`scripts/test-composer-integration.sh`)
  - Run after composer updates
  - Validates basic tool calls
  - Checks for breaking changes
- [ ] Establish version compatibility matrix
  ```
  | mcp-n8n | chora-composer | Compatible? | Notes |
  |---------|----------------|-------------|-------|
  | v0.1.0  | v1.1.0         | ✅          | Initial |
  | v0.1.1  | v1.1.1         | ✅          | Generator deps |
  ```
- [ ] Document process in `docs/SUBMODULE_MANAGEMENT.md`

**Success Criteria:**
- ✅ Clear update procedure documented
- ✅ Smoke test catches breaking changes
- ✅ Compatibility matrix maintained
- ✅ Team can update composer confidently

---

#### 4. Baseline Telemetry (Week 2)

**Objective:** Establish what telemetry is currently captured

**Tasks:**
- [ ] Audit existing logging in mcp-n8n
- [ ] Identify what chora-composer emits (if anything in v1.1.0)
- [ ] Design telemetry schema for gateway
  ```json
  {
    "timestamp": "2025-10-17T12:00:00Z",
    "event_type": "tool_call",
    "backend": "chora-composer",
    "tool": "assemble_artifact",
    "duration_ms": 1234,
    "status": "success"
  }
  ```
- [ ] Implement structured logging to `var/telemetry/gateway.jsonl`
- [ ] Document telemetry schema

**Success Criteria:**
- ✅ All tool calls logged with structured data
- ✅ Latency metrics captured
- ✅ Error events logged
- ✅ Telemetry file format documented

---

### Phase 0 Exit Criteria

- ✅ Integration tests pass with chora-composer v1.1.0
- ✅ "Hello World" workflow works end-to-end
- ✅ Submodule management process documented
- ✅ Baseline telemetry implemented
- ✅ **No blocking issues** discovered (or issues resolved)
- ✅ Clear list of requirements for chora-composer v1.1.1

**Outcome:** Confidence to proceed with Phase 1 development

---

## Phase 1: Essential Gateway Capabilities (Week 3-6)

**Status:** BLOCKS chora-composer v1.2.0 design
**Goal:** Implement features that provide real-world usage feedback to inform chora-composer v1.2.0
**Release:** mcp-n8n v0.2.0 (minor with new capabilities)

### Strategic Focus: The "Weekly Engineering Report" Workflow

This workflow is the **primary validation vehicle** for Phase 1. All features should be justified by enabling or improving this workflow.

**Workflow Overview:**
```
Schedule (every Monday 9am)
    ↓
Fetch GitHub commits (last 7 days)
    ↓
Fetch Jira tickets closed (last 7 days)
    ↓
Fetch deployment metrics from DataDog API
    ↓
chora:generate_content(template="report-intro", context={...})
    ↓
chora:generate_content(template="github-summary", context={...})
    ↓
chora:generate_content(template="jira-summary", context={...})
    ↓
chora:generate_content(template="metrics-analysis", context={...})
    ↓
chora:assemble_artifact(config="weekly-eng-report", sections=[...])
    ↓
coda:create_row(table="Reports", values={...})
    ↓
Slack: Post to #engineering with report link
```

### Deliverables

#### 1. Credential Pre-Validation (Week 3)

**Objective:** Prevent tool call failures due to missing credentials

**Requirements Validated:**
- Does chora-composer v1.1.1's `generator_dependencies` metadata provide enough info?
- Can gateway detect credential issues before making backend calls?

**Tasks:**
- [ ] Implement credential checker in gateway startup
  ```python
  # pseudo-code
  if backend.name == "chora-composer":
      required_creds = backend.get_required_credentials()
      for cred in required_creds:
          if not env.get(cred):
              log.warning(f"Backend {backend.name} requires {cred}")
  ```
- [ ] Add credential status to `gateway_status` tool
  ```json
  {
    "backends": {
      "chora-composer": {
        "status": "running",
        "credentials": {
          "ANTHROPIC_API_KEY": "present",
          "GITHUB_TOKEN": "missing"
        }
      }
    }
  }
  ```
- [ ] Implement pre-flight check before routing to backend
- [ ] Test with missing credentials (should fail gracefully)
- [ ] Document credential requirements in `GETTING_STARTED.md`

**Success Criteria:**
- ✅ Gateway detects missing credentials on startup
- ✅ `gateway_status` shows credential state
- ✅ Tool calls fail fast with clear error messages
- ✅ **Feedback:** Are chora v1.1.1 generator deps sufficient?

**Deliverable:** Credential validation module + documentation

---

#### 2. Gateway Discovery Metadata (Week 4)

**Objective:** Document what gateway-specific metadata would improve routing

**Requirements Gathering for chora-composer v1.2.0:**

**Tasks:**
- [ ] Implement mock `?context=gateway` parameter handling
  ```python
  # What would we WANT to receive?
  capabilities = backend.get_capabilities(context="gateway")
  # vs
  capabilities = backend.get_capabilities()  # default
  ```
- [ ] Document ideal gateway view vs. direct client view
  ```
  Direct Client:
  - Includes local file paths
  - Shows all generators including experimental
  - Exposes internal tools (debug, config)

  Gateway View:
  - Hides local file paths (gateway manages routing)
  - Shows only stable generators
  - Excludes internal tools
  - Includes concurrency hints
  - Includes expected latency ranges
  ```
- [ ] Create mock response showing ideal metadata
- [ ] Test routing logic with mock data
- [ ] Write requirements document for chora v1.2.0
  - **File:** `docs/chora-composer-v1.2.0-requirements.md`

**Success Criteria:**
- ✅ Clear specification of gateway vs. direct metadata
- ✅ Mock implementation proves routing benefits
- ✅ Requirements document delivered to chora team by Week 4 end
- ✅ **Feedback:** Specific fields needed in gateway context

**Deliverable:** Requirements doc + mock implementation

---

#### 3. Event Monitoring Foundation (Week 5)

**Objective:** Consume chora-composer v1.1.1 event emissions

**Requirements Validated:**
- Is `var/telemetry/events.jsonl` format usable by gateway?
- Do events provide enough context for workflow coordination?

**Tasks:**
- [ ] Implement file watcher for `chora-composer/var/telemetry/events.jsonl`
  ```python
  # Tail the file, parse JSON lines
  async def watch_events():
      async for line in tail_file("chora-composer/var/telemetry/events.jsonl"):
          event = json.loads(line)
          handle_event(event)
  ```
- [ ] Parse event schema
  ```json
  {
    "timestamp": "2025-10-17T12:00:00Z",
    "event_type": "artifact_assembled",
    "artifact_config_id": "weekly-report",
    "trace_id": "abc123",
    "status": "success"
  }
  ```
- [ ] Implement event correlation (match requests to completion events)
- [ ] Expose events via gateway telemetry
- [ ] Test async workflow: trigger artifact → poll events → detect completion
- [ ] Document event consumption pattern

**Success Criteria:**
- ✅ Gateway detects artifact completion events
- ✅ Event correlation works (request → completion)
- ✅ Events forwarded to gateway telemetry
- ✅ **Feedback:** Event schema meets needs or needs changes?

**Deliverable:** Event monitoring module + documentation

---

#### 4. "Weekly Engineering Report" Workflow (Week 6) ⭐

**Objective:** Build and validate the complete Pattern N5 workflow

**This is the CRITICAL DELIVERABLE for Phase 1.**

**Tasks:**

**4.1. Workflow Infrastructure**
- [ ] Set up n8n instance (local or cloud)
- [ ] Configure mcp-n8n as available MCP server
- [ ] Create workflow skeleton in n8n UI

**4.2. Data Gathering Nodes**
- [ ] GitHub API node: Fetch commits from last 7 days
  - Endpoint: `/repos/{owner}/{repo}/commits?since={date}`
  - Parse commit messages, authors, file changes
- [ ] Jira API node: Fetch closed tickets
  - JQL query: `status=Done AND updated >= -7d`
  - Parse ticket summaries, assignees
- [ ] DataDog API node: Fetch deployment metrics
  - Query: deployment count, error rate, latency p95
  - Time range: last 7 days

**4.3. Chora Composer Integration**
- [ ] Create report templates in `chora-composer/configs/`
  - `weekly-report-intro.yaml` - Intro section template
  - `weekly-report-github.yaml` - GitHub summary template
  - `weekly-report-jira.yaml` - Jira summary template
  - `weekly-report-metrics.yaml` - Metrics analysis template
  - `weekly-report.yaml` - Main artifact config
- [ ] Call `chora:generate_content` for each section
  - Pass aggregated data as context
  - Collect generated content
- [ ] Call `chora:assemble_artifact` to combine sections
  - Config: `weekly-report`
  - Output: `output/weekly-report-{date}.md`

**4.4. Post-Assembly Actions**
- [ ] Coda integration: `coda:create_row`
  - Table: "Engineering Reports"
  - Columns: Date, Report Link, Commit Count, Tickets Closed
- [ ] Slack notification
  - Channel: #engineering
  - Message: "Weekly report ready: [link]"

**4.5. Testing & Validation**
- [ ] Run workflow manually first time
- [ ] Debug and fix issues
- [ ] Run 3 times to validate consistency
- [ ] Measure performance:
  - Total execution time
  - Per-step latency
  - Resource usage
- [ ] Document known limitations

**4.6. Documentation**
- [ ] Workflow JSON export: `workflows/weekly-engineering-report.json`
- [ ] Setup guide: `docs/workflows/weekly-report-setup.md`
- [ ] Template documentation in chora-composer repo
- [ ] Performance benchmarks

**Success Criteria:**
- ✅ Workflow executes successfully end-to-end
- ✅ Report generated with correct content
- ✅ Metadata stored in Coda
- ✅ Slack notification sent
- ✅ Execution time < 2 minutes (excluding API rate limits)
- ✅ **Feedback Document Created:** Learnings for chora v1.2.0

**Deliverable:** Working workflow + templates + comprehensive documentation

---

### Phase 1 Feedback Document

**Due:** End of Week 6
**Audience:** chora-composer team (for v1.2.0 design)
**File:** `docs/chora-composer-v1.2.0-feedback.md`

**Contents:**
1. **Credential Pre-Validation Learnings**
   - Were generator dependency tags sufficient?
   - What additional metadata would help?
   - Suggested format changes

2. **Gateway Metadata Requirements**
   - Specific fields needed in `?context=gateway` view
   - Examples of what to hide/show
   - Routing optimization opportunities

3. **Event Monitoring Learnings**
   - Event schema effectiveness
   - Missing event types
   - Correlation challenges
   - Suggestions for `capabilities://telemetry`

4. **Workflow Orchestration Insights**
   - Multi-step `generate_content` → `assemble_artifact` pattern
   - Context passing between steps
   - Error handling needs
   - **Request:** Preview artifact feature (dry-run before assembly)

5. **Performance Observations**
   - Latency measurements
   - Bottlenecks identified
   - Concurrency needs
   - Suggestions for limits exposure

**This document is CRITICAL INPUT to chora-composer v1.2.0 design.**

---

### Phase 1 Exit Criteria

- ✅ Credential validation implemented and tested
- ✅ Gateway metadata requirements documented
- ✅ Event monitoring working
- ✅ **"Weekly Engineering Report" workflow functional**
- ✅ Feedback document delivered to chora team
- ✅ mcp-n8n v0.2.0 released

**Outcome:** Real-world validation + actionable feedback for chora v1.2.0

---

## Phase 2: Advanced Gateway Features (Week 7-10)

**Status:** CONSUMES chora-composer v1.2.0
**Goal:** Build production-ready features leveraging chora v1.2.0 gateway-aware capabilities
**Release:** mcp-n8n v0.3.0 (minor with production features)

### Deliverables

#### 1. Context-Aware Discovery (Week 7)

**Objective:** Leverage `capabilities://server?context=gateway` from chora v1.2.0

**Prerequisites:**
- ✅ chora-composer v1.2.0 released
- ✅ Gateway context parameter implemented in chora

**Tasks:**
- [ ] Update backend initialization to request gateway context
  ```python
  # Request gateway-optimized view
  capabilities = await backend.get_capabilities(context="gateway")
  ```
- [ ] Implement routing logic based on gateway hints
  ```python
  # Example: Use concurrency limits from capabilities
  if backend.concurrency_limit and active_requests >= limit:
      return BackPressureError(...)
  ```
- [ ] Hide local-only features from tool lists
  - Filter out tools marked as `local_only: true`
  - Remove file path details that don't apply in gateway context
- [ ] Test with chora v1.2.0
- [ ] Document context-aware routing

**Success Criteria:**
- ✅ Gateway receives optimized capability metadata
- ✅ Routing decisions improved (fewer errors)
- ✅ Local-only features correctly hidden
- ✅ Documentation updated

**Deliverable:** Context-aware routing implementation

---

#### 2. Preview Workflow Integration (Week 8)

**Objective:** Add preview-before-assembly pattern using chora v1.2.0's `preview_artifact` tool

**Prerequisites:**
- ✅ chora-composer v1.2.0 `preview_artifact` tool available

**Tasks:**
- [ ] Update workflow template: Weekly Report with Preview
  ```
  [Data Gathering] → [Generate Sections]
         ↓
  chora:preview_artifact(config="weekly-report", context={...})
         ↓
  Show diff in Slack: "Report will have these changes: [diff]"
         ↓
  Slack Interactive Button: [Approve] [Reject]
         ↓ (if approved)
  chora:assemble_artifact(...)
  ```
- [ ] Implement diff display formatting
  - Parse section-level changes from preview result
  - Format for Slack (or other notification)
- [ ] Add approval gate workflow pattern
- [ ] Test preview accuracy (does assembly match preview?)
- [ ] Document preview workflow pattern

**Success Criteria:**
- ✅ Preview shows accurate diff before assembly
- ✅ Approval workflow prevents unwanted artifacts
- ✅ Preview → assemble consistency validated
- ✅ Pattern documented for other workflows

**Deliverable:** Preview workflow template + documentation

---

#### 3. Telemetry Schema Discovery (Week 9)

**Objective:** Consume `capabilities://telemetry` from chora v1.2.0

**Prerequisites:**
- ✅ chora-composer v1.2.0 `capabilities://telemetry` resource available

**Tasks:**
- [ ] Query `capabilities://telemetry` from chora backend
  ```json
  {
    "event_types": [
      {
        "name": "content_generated",
        "schema": {...},
        "frequency": "per_generation"
      },
      {
        "name": "artifact_assembled",
        "schema": {...},
        "frequency": "per_assembly"
      }
    ],
    "metrics": ["generation_duration_ms", "artifact_size_bytes"]
  }
  ```
- [ ] Validate event emissions match schema
- [ ] Auto-generate telemetry documentation from schema
- [ ] Forward events to centralized observability (if available)
- [ ] Create Grafana dashboard templates
  - Artifact assembly rate
  - Generation duration (p50, p95, p99)
  - Error rate by tool
  - Backend health status

**Success Criteria:**
- ✅ Telemetry schema discoverable
- ✅ Events validated against schema
- ✅ Dashboard templates created
- ✅ Documentation auto-generated

**Deliverable:** Telemetry integration + dashboards

---

#### 4. Production Workflows (Week 10)

**Objective:** Build 3-5 production-ready workflow templates

**Workflow 1: Event-Driven Documentation Updates**
```
GitHub Webhook (PR merged, files in /docs changed)
    ↓
Extract file paths and commit messages
    ↓
chora:preview_artifact(config="api-docs", context={...})
    ↓
Show preview in GitHub PR comment
    ↓
chora:assemble_artifact(config="api-docs")
    ↓
Create new PR with updated docs
```

**Workflow 2: Customer Onboarding Automation**
```
Stripe Webhook (customer.created)
    ↓
coda:create_doc (customer workspace)
    ↓
chora:generate_content(template="welcome-letter")
    ↓
chora:assemble_artifact(config="onboarding-guide")
    ↓
Upload to Coda doc
    ↓
SendGrid: Send welcome email
    ↓
Slack: Notify #sales
```

**Workflow 3: API Documentation Sync**
```
GitHub Webhook (openapi.yaml changed)
    ↓
Download new OpenAPI spec
    ↓
chora:generate_content(template="endpoint-docs", context=spec)
    ↓
chora:preview_artifact(config="api-docs")
    ↓
Slack approval
    ↓
chora:assemble_artifact(config="api-docs")
    ↓
Create PR with updated docs
```

**Tasks:**
- [ ] Build each workflow in n8n
- [ ] Test with real data
- [ ] Document setup and configuration
- [ ] Export workflow JSONs
- [ ] Measure performance and reliability
- [ ] Create troubleshooting guide

**Success Criteria:**
- ✅ 3+ workflows deployed and tested
- ✅ Documentation for each workflow
- ✅ Workflows run successfully 10+ times
- ✅ < 5% failure rate

**Deliverable:** Production workflow library

---

### Phase 2 Exit Criteria

- ✅ Context-aware routing implemented
- ✅ Preview workflows validated
- ✅ Telemetry integration complete
- ✅ 3+ production workflows deployed
- ✅ Performance benchmarks meet targets
- ✅ mcp-n8n v0.3.0 released
- ✅ Production deployment guide written

**Outcome:** Production-ready gateway with validated workflows

---

## Phase 3: Ecosystem Maturation (Week 11-14)

**Status:** PARALLEL with chora-composer v1.3.0
**Goal:** Advanced patterns and ecosystem integration preparation
**Release:** mcp-n8n v0.4.0 (minor with advanced features)

### Deliverables

#### 1. n8n as MCP Server (Pattern N2) - Week 11

**Objective:** Expose n8n workflows as MCP tools

**Architecture:**
```
AI Client (Claude Desktop)
    ↓ MCP
n8n MCP Server (new component)
    ↓ n8n REST API
n8n Workflow Engine
    ↓
External Systems (APIs, etc.)
```

**Tasks:**
- [ ] Build MCP server wrapper around n8n API
  - Tools: `n8n:list_workflows`, `n8n:execute_workflow`, `n8n:get_execution_status`
  - Use n8n REST API (`/workflows`, `/executions`)
- [ ] Implement async execution handling
  - Return `execution_id` immediately
  - Client polls for completion
- [ ] Add to mcp-n8n gateway as optional backend
  - Namespace: `n8n:*`
  - Enabled when `N8N_API_URL` and `N8N_API_KEY` present
- [ ] Test from Claude Desktop
  - "Execute the weekly report workflow"
  - Claude calls `n8n:execute_workflow`
- [ ] Document pattern

**Success Criteria:**
- ✅ AI agents can trigger n8n workflows via MCP
- ✅ Execution status queryable
- ✅ Error handling graceful
- ✅ Pattern documented with examples

**Deliverable:** n8n MCP server + integration

---

#### 2. n8n as MCP Client (Pattern N3) - Week 12

**Objective:** Allow n8n workflows to call MCP tools

**Architecture:**
```
n8n Workflow
    ↓
Custom MCP Client Node (@chora/mcp-tool-call)
    ↓ JSON-RPC/STDIO or HTTP
MCP Servers (chora-composer, coda-mcp, etc.)
```

**Tasks:**
- [ ] Develop custom n8n node: `@chora/mcp-tool-call`
  - Fields: MCP server selection (dropdown)
  - Fields: Tool selection (dynamic, fetched from server)
  - Fields: Arguments (JSON editor or auto-generated form)
- [ ] Support STDIO transport
  - Spawn MCP server as subprocess
  - Manage lifecycle per workflow execution
- [ ] Support HTTP transport (if MCP servers support it)
- [ ] Implement credential management
  - Custom credential type: `mcpServerCredential`
  - Fields: server_url, command, environment vars
- [ ] Test with chora-composer
  - n8n workflow calls `chora:assemble_artifact`
- [ ] Publish to npm: `@chora/mcp-tool-call`
- [ ] Document usage in n8n

**Success Criteria:**
- ✅ n8n workflows can call any MCP tool
- ✅ Dynamic tool discovery works
- ✅ Credentials managed securely
- ✅ Node published and installable
- ✅ Documentation with examples

**Deliverable:** Custom n8n node package

---

#### 3. Gateway Performance Optimization (Week 13)

**Objective:** Reduce latency and improve scalability

**Tasks:**

**3.1. Capability Caching**
- [ ] Cache backend capabilities on startup
  - Reduce repeated `tools/list` calls
  - Invalidate cache on backend restart
- [ ] Implement TTL for cache (configurable)
- [ ] Benchmark improvement

**3.2. Connection Pooling**
- [ ] Maintain persistent connections to backends
  - Avoid subprocess restart overhead
  - Implement keep-alive
- [ ] Pool size configuration

**3.3. Request Batching (if applicable)**
- [ ] Batch multiple tool calls to same backend
  - Reduce round-trip overhead
  - Requires MCP batch support

**3.4. Benchmarking**
- [ ] Baseline: Current p50, p95, p99 latency
- [ ] Optimize
- [ ] Measure improvement
- [ ] Document results

**Performance Targets:**
- ✅ Gateway routing overhead < 10ms p95
- ✅ Capability lookup < 5ms p95
- ✅ Startup time < 5 seconds

**Deliverable:** Performance optimization guide

---

#### 4. Context Bus Preparation (Week 14)

**Objective:** Design adapter for future context bus integration

**Background:**
- chora-composer v1.3.0 will integrate with platform context bus
- mcp-n8n should prepare for migration from file-based events

**Tasks:**
- [ ] Design event subscription interface
  ```python
  # Future API
  class EventSubscriber:
      async def subscribe(self, event_type: str, handler: Callable):
          pass

      async def publish(self, event: Event):
          pass
  ```
- [ ] Implement adapter pattern
  - Current: File-based (`var/telemetry/events.jsonl`)
  - Future: Context bus (message queue, event stream)
  - Adapter abstracts implementation
- [ ] Write integration specification
  - Event types to subscribe to
  - Event routing logic
  - Schema validation
- [ ] Prototype with mock context bus (Redis Pub/Sub or similar)
- [ ] Document migration path

**Success Criteria:**
- ✅ Adapter pattern designed
- ✅ Prototype validates approach
- ✅ Integration spec complete
- ✅ Ready to integrate when chora v1.3.0 available

**Deliverable:** Context bus integration spec + prototype

---

### Phase 3 Exit Criteria

- ✅ n8n MCP server working (Pattern N2)
- ✅ n8n MCP client node published (Pattern N3)
- ✅ Performance targets met
- ✅ Context bus adapter designed
- ✅ mcp-n8n v0.4.0 released
- ✅ Advanced patterns documented

**Outcome:** Ecosystem-ready gateway with advanced integration patterns

---

## Cross-Phase Concerns

### Documentation Strategy

**Living Documents (updated every phase):**
- [README.md](../README.md) - Overview, installation, quick start
- [ARCHITECTURE.md](../ARCHITECTURE.md) - P5 pattern implementation details
- [GETTING_STARTED.md](../GETTING_STARTED.md) - Setup guide

**Phase-Specific Documents:**
- Phase 0: `docs/SUBMODULE_MANAGEMENT.md`
- Phase 1: `docs/workflows/weekly-report-setup.md`, `docs/chora-composer-v1.2.0-feedback.md`
- Phase 2: `docs/workflows/` (production workflow guides), `docs/TELEMETRY.md`
- Phase 3: `docs/patterns/n8n-mcp-server.md`, `docs/patterns/n8n-mcp-client.md`

**API Reference (auto-generated):**
- Tool schemas
- Configuration options
- Telemetry events

### Testing Strategy

**Unit Tests (continuous):**
- Backend registration and routing
- Configuration validation
- Namespace parsing
- Credential checking

**Integration Tests (per phase):**
- Phase 0: Basic tool calls through gateway
- Phase 1: Multi-step workflows (weekly report)
- Phase 2: Preview workflows, context-aware routing
- Phase 3: n8n MCP patterns

**End-to-End Tests:**
- Weekly report workflow (automated run)
- Event-driven workflows (simulated webhooks)
- Performance benchmarks (latency, throughput)

**Test Coverage Target:** >80% (unit + integration)

### Security & Compliance

**Credential Management:**
- All secrets via environment variables
- No credentials in logs
- Credential rotation support
- Per-backend isolation

**Audit Logging:**
- All tool calls logged with user context
- Structured logs for compliance queries
- Retention policy configurable

**Vulnerability Scanning:**
- Dependency scanning (Dependabot)
- SBOM generation (future, aligns with ecosystem)
- Security advisories monitored

### Community & Communication

**Weekly Sync (During Overlapping Phases):**
- mcp-n8n + chora-composer teams
- Review integration issues
- Coordinate release timing
- Share learnings

**Release Notes:**
- Clear changelog for each version
- Migration guides for breaking changes
- Compatibility matrix updated

**Feedback Channels:**
- GitHub Issues for bug reports
- Discussions for feature requests
- Slack/Discord for real-time coordination

---

## Risk Management

### Risk 1: Chora-Composer Integration Breaks

**Likelihood:** Medium
**Impact:** High (blocks all phases)

**Mitigation:**
- Phase 0 validates integration early
- Smoke test script catches breaking changes
- Version pinning in submodule
- Compatibility matrix maintained

**Contingency:**
- Rollback to last known-good chora version
- File integration issue with chora team
- Delay phase until resolved

---

### Risk 2: Weekly Report Workflow Fails to Deliver Value

**Likelihood:** Low
**Impact:** High (undermines Phase 1 goals)

**Mitigation:**
- Start with simple data sources (reduce external dependencies)
- Mock data sources if APIs unavailable
- Focus on workflow mechanics, not data quality initially
- Iterative refinement based on feedback

**Contingency:**
- Simplify workflow scope
- Use alternative validation workflow
- Still deliver feedback to chora team

---

### Risk 3: Performance Unacceptable

**Likelihood:** Medium
**Impact:** Medium (limits production adoption)

**Mitigation:**
- Baseline performance in Phase 0
- Monitor latency throughout Phase 1
- Phase 3 dedicated to optimization
- Performance targets defined early

**Contingency:**
- Identify and remove bottlenecks
- Consider architectural changes (e.g., persistent connections)
- Document known limitations

---

### Risk 4: Chora v1.2.0 Delayed

**Likelihood:** Medium
**Impact:** High (blocks Phase 2)

**Mitigation:**
- Early feedback from Phase 1 reduces rework
- Regular coordination meetings
- Flexible Phase 2 schedule (can start later)

**Contingency:**
- Continue Phase 2 prep work (documentation, tests)
- Build against chora v1.2.0 beta if available
- Delay Phase 2 release if needed

---

### Risk 5: n8n Limitations Discovered

**Likelihood:** Medium
**Impact:** Medium (affects Phase 3 patterns)

**Mitigation:**
- Phase 0 tests basic n8n integration
- Phase 1 validates complex workflows
- Community n8n support available

**Contingency:**
- Use alternative workflow engine if needed
- Document n8n limitations
- Focus on MCP gateway (core value), de-emphasize n8n-specific patterns

---

## Success Metrics

### Phase 0 Metrics

**Integration Quality:**
- ✅ 100% of chora tools callable through gateway
- ✅ < 10ms routing overhead
- ✅ Zero data corruption incidents

**Process Maturity:**
- ✅ Submodule update process documented and tested
- ✅ Smoke test catches breaking changes

---

### Phase 1 Metrics

**Feature Delivery:**
- ✅ Credential validation prevents 90%+ of credential errors
- ✅ Event monitoring detects completion within 1 second
- ✅ Weekly report workflow completes successfully

**Feedback Quality:**
- ✅ Feedback document delivered on time
- ✅ Contains actionable requirements for chora v1.2.0
- ✅ chora team confirms value of feedback

**Performance:**
- ✅ Weekly report workflow: < 2 minutes end-to-end
- ✅ Gateway overhead: < 50ms p95

---

### Phase 2 Metrics

**Production Readiness:**
- ✅ Context-aware routing reduces errors by 50%
- ✅ Preview workflows prevent 100% of unwanted artifact changes
- ✅ 3+ production workflows deployed

**Reliability:**
- ✅ Workflow success rate > 95%
- ✅ MTTR (mean time to recovery) < 1 hour
- ✅ Uptime > 99%

**Observability:**
- ✅ All events captured and queryable
- ✅ Dashboards provide actionable insights
- ✅ Alerting catches issues before users report

---

### Phase 3 Metrics

**Advanced Patterns:**
- ✅ AI agents successfully trigger n8n workflows
- ✅ n8n workflows successfully call MCP tools
- ✅ Custom node installed and used by 3+ users

**Performance:**
- ✅ Gateway routing: < 10ms p95
- ✅ Capability lookup: < 5ms p95
- ✅ Startup time: < 5 seconds

**Ecosystem Readiness:**
- ✅ Context bus adapter designed and prototyped
- ✅ Integration spec complete
- ✅ Ready for chora v1.3.0 integration

---

## Team Coordination

### Roles & Responsibilities

**mcp-n8n Team:**
- Own orchestration layer (Layer 3)
- Build and maintain gateway
- Develop n8n workflows and patterns
- Provide feedback to chora team
- Manage mcp-n8n releases

**chora-composer Team:**
- Own artifact generation (Layer 2)
- Expose MCP tools and capabilities
- Implement gateway-aware features
- Incorporate mcp-n8n feedback
- Manage chora releases

**Shared:**
- Integration testing
- Documentation (cross-references)
- Ecosystem standards compliance
- Telemetry and observability

### Communication Cadence

**Weekly Sync (During Overlapping Phases):**
- Phase 1 (Week 3-6): Weekly sync critical for v1.2.0 coordination
- Phase 2-3: Bi-weekly sync sufficient

**Async Updates:**
- GitHub issues/PRs for technical discussion
- Slack/Discord for quick questions
- Shared roadmap document (this file) updated as single source of truth

**Release Coordination:**
- Pre-release: Beta testing, feedback
- Release: Coordinated announcements
- Post-release: Retrospective, lessons learned

### Decision-Making

**mcp-n8n Decisions (Autonomous):**
- Workflow design and implementation
- n8n-specific tooling choices
- Gateway routing logic (within MCP spec)
- Release timing (after dependencies met)

**chora-composer Decisions (Autonomous):**
- Tool interfaces and schemas
- Capability metadata format
- Internal architecture
- Release timing

**Joint Decisions (Coordination Required):**
- Telemetry schema and format
- Gateway context parameter specification
- Integration testing approach
- Ecosystem standards interpretation

---

## Appendix A: Workflow Templates

### Template: Weekly Engineering Report

**File:** `workflows/weekly-engineering-report.json`

**Description:** Automated weekly report combining GitHub, Jira, and deployment metrics

**Trigger:** Schedule (Monday 9am)

**Steps:**
1. Fetch GitHub commits (last 7 days)
2. Fetch Jira tickets (status=Done, last 7 days)
3. Fetch DataDog metrics
4. Generate intro section (`chora:generate_content`)
5. Generate GitHub summary (`chora:generate_content`)
6. Generate Jira summary (`chora:generate_content`)
7. Generate metrics analysis (`chora:generate_content`)
8. Assemble artifact (`chora:assemble_artifact`)
9. Store metadata (`coda:create_row`)
10. Send Slack notification

**Configuration:**
- GitHub repo: `{org}/{repo}`
- Jira project: `{project-key}`
- DataDog API key: `{env.DATADOG_API_KEY}`
- Output: `output/weekly-report-{date}.md`

**Performance:** ~90 seconds (excluding external API latency)

---

### Template: Event-Driven Docs Update

**File:** `workflows/event-driven-docs-update.json`

**Description:** Auto-update documentation when code changes

**Trigger:** GitHub webhook (PR merged, /docs files changed)

**Steps:**
1. Parse webhook payload
2. Extract changed files
3. Preview artifact (`chora:preview_artifact`)
4. Post preview as PR comment
5. If approved, assemble artifact (`chora:assemble_artifact`)
6. Create new PR with updated docs
7. Notify team in Slack

**Configuration:**
- GitHub repo: `{org}/{repo}`
- Docs path: `/docs`
- Artifact config: `api-documentation`

**Performance:** ~30 seconds (fast path, no user approval)

---

### Template: Customer Onboarding

**File:** `workflows/customer-onboarding.json`

**Description:** Automated onboarding when new customer signs up

**Trigger:** Stripe webhook (customer.created)

**Steps:**
1. Parse webhook (customer details)
2. Create Coda workspace (`coda:create_doc`)
3. Generate welcome letter (`chora:generate_content`)
4. Generate onboarding guide (`chora:assemble_artifact`)
5. Upload to Coda doc
6. Send email (SendGrid API)
7. Notify sales team (Slack)

**Configuration:**
- Stripe webhook secret: `{env.STRIPE_WEBHOOK_SECRET}`
- Coda folder: `{env.CODA_CUSTOMER_FOLDER}`
- SendGrid template: `onboarding-welcome`

**Performance:** ~45 seconds

---

## Appendix B: Compatibility Matrix

| mcp-n8n Version | chora-composer Version | Compatible? | Features | Notes |
|-----------------|------------------------|-------------|----------|-------|
| v0.1.0          | v1.1.0                 | ✅          | Basic gateway | Initial release |
| v0.2.0          | v1.1.0                 | ✅          | + Phase 0 validation, agent infrastructure | **RELEASED 2025-10-17** |
| v0.3.0          | v1.1.1                 | ✅          | + Event monitoring, weekly report | Phase 1 complete |
| v0.4.0          | v1.2.0                 | ✅ **REQUIRES** | + Context-aware routing, preview | Phase 2 complete |
| v0.5.0          | v1.2.0 or v1.3.0       | ✅          | + n8n MCP patterns, context bus prep | Phase 3 complete |

**Upgrade Path:**
- v0.1.0 → v0.2.0: No breaking changes, update environment variables (now accepts unprefixed ANTHROPIC_API_KEY)
- v0.2.0 → v0.3.0: No breaking changes, update submodule to chora v1.1.1 (when released)
- v0.3.0 → v0.4.0: **Requires chora v1.2.0**, update submodule
- v0.4.0 → v0.5.0: No breaking changes, optional upgrade to chora v1.3.0 for context bus

---

## Appendix C: Telemetry Event Catalog

### Event: `gateway.tool_call`

**Frequency:** Per tool call

**Schema:**
```json
{
  "timestamp": "2025-10-17T12:00:00Z",
  "event_type": "gateway.tool_call",
  "backend": "chora-composer",
  "namespace": "chora",
  "tool": "assemble_artifact",
  "arguments": {"artifact_config_id": "weekly-report"},
  "duration_ms": 1234,
  "status": "success",
  "trace_id": "abc123"
}
```

---

### Event: `gateway.backend_started`

**Frequency:** Per backend startup

**Schema:**
```json
{
  "timestamp": "2025-10-17T12:00:00Z",
  "event_type": "gateway.backend_started",
  "backend": "chora-composer",
  "status": "running",
  "tools_count": 17,
  "startup_duration_ms": 2345
}
```

---

### Event: `gateway.backend_failed`

**Frequency:** On backend failure

**Schema:**
```json
{
  "timestamp": "2025-10-17T12:00:00Z",
  "event_type": "gateway.backend_failed",
  "backend": "chora-composer",
  "error": "Process exited with code 1",
  "stderr": "..."
}
```

---

## Appendix D: Performance Benchmarks

### Baseline (Phase 0)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Gateway routing overhead | < 10ms p95 | TBD | Pending |
| Backend startup time | < 5s | TBD | Pending |
| Tool call latency (chora) | < 100ms p95 | TBD | Pending |
| Tool call latency (coda) | < 200ms p95 | TBD | Pending |

### Phase 1 (Weekly Report Workflow)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| End-to-end workflow time | < 2 minutes | TBD | Pending |
| Data gathering time | < 30s | TBD | Pending |
| Content generation time | < 60s | TBD | Pending |
| Artifact assembly time | < 10s | TBD | Pending |

### Phase 3 (Optimized)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Gateway routing overhead | < 5ms p95 | TBD | Pending |
| Capability lookup | < 5ms p95 | TBD | Pending |
| Startup time | < 3s | TBD | Pending |

---

## Document Metadata

**Version:** 1.0.0
**Status:** Active
**Last Updated:** 2025-10-17
**Next Review:** End of Phase 0 (Week 2)
**Owner:** mcp-n8n team
**Stakeholders:** chora-composer team, platform team

**Related Documents:**
- [n8n Solution-Neutral Intent](ecosystem/n8n-solution-neutral-intent.md)
- [chora-composer Roadmap Revision](../chora-composer/docs/ROADMAP_UPDATE_v2.md)
- [ARCHITECTURE.md](../ARCHITECTURE.md)
- [MCP Server Patterns Catalog](../MCP%20Server%20Patterns%20Catalog.pdf)

**Change Log:**
- 2025-10-17: Initial version based on chora-composer feedback and team proposals
