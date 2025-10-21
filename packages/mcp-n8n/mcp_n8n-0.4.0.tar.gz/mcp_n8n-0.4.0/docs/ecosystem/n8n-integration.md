# n8n Integration: Solution-Neutral Intent Document

**Version:** 1.1.0
**Date:** 2025-10-16
**Status:** Draft
**Document Type:** Solution-Neutral Intent
**Scope:** n8n Integration Patterns within Chora Ecosystem

---

## Executive Summary

This document defines the **solution-neutral intent** for integrating **n8n** as a modular workflow automation and event processing capability within the Chora ecosystem. n8n serves as a **multi-modal integration hub** that can function as:

1. **Workflow Orchestrator** - Coordinate multi-step processes across services
2. **Event Processor** - React to and transform events in real-time
3. **MCP Server** - Expose workflow execution as MCP tools
4. **MCP Client** - Consume other MCP servers within workflows
5. **Gateway & Aggregator** - Route and transform MCP requests
6. **Integration Bridge** - Connect legacy systems to modern MCP interfaces

The intent is to establish n8n as a **flexible, low-code orchestration layer** that enables rapid integration development while maintaining DRSO (Development → Release → Security → Operations) principles and alignment with the 3-layer Chora Platform architecture.

**Key Principles:**
- **Modularity:** Each n8n capability is independently deployable
- **Composability:** n8n workflows can invoke other workflows and MCP tools
- **Observability:** All executions flow through structured telemetry
- **Governance:** Workflows follow BDD-DRSO validation gates
- **Extensibility:** Custom nodes and integrations follow platform patterns

---

## 1. Foundation & Motivation

### 1.1 Problem Statement

Modern software ecosystems require **integration glue** to connect:
- AI agents (via MCP) with business systems (APIs, databases, SaaS)
- Event sources (webhooks, message queues) with processing pipelines
- User-facing tools (Claude Desktop, Cursor) with backend services
- Legacy systems with modern AI-native interfaces

**Current Gap:**
- Writing custom integration code for each connection is time-consuming
- MCP servers alone don't handle complex multi-step orchestration
- Event-driven architectures require infrastructure expertise
- No unified observability across integrations

### 1.2 n8n Value Proposition

**n8n** is an **open-source workflow automation platform** that provides:
- **Visual Workflow Builder** - Low-code interface for creating integrations
- **400+ Integrations** - Pre-built nodes for popular services (Slack, GitHub, Airtable, OpenAI, etc.)
- **Event-Driven Execution** - Trigger workflows via webhooks, schedules, or manual invocation
- **Self-Hosted or Cloud** - Deploy locally or use n8n.cloud
- **Extensible** - Custom JavaScript functions and community nodes
- **API & CLI** - Programmatic workflow management

**Strategic Fit:**
- **Accelerates Integration Development** - Build workflows in minutes vs. hours of coding
- **Democratizes Automation** - Non-developers can create integrations
- **Complements MCP** - Workflows can consume and expose MCP tools
- **Supports DRSO** - Workflows can be version-controlled, tested, and monitored
- **Aligns with 3-Layer Architecture** - Functions as Platform-layer capability

### 1.3 Scope of This Document

This document describes **what n8n integration should achieve** and **why**, not **how** to implement it technically. It covers:

✅ **In Scope:**
- Integration patterns and use cases
- Architectural role in Chora ecosystem
- DRSO alignment and governance requirements
- Value scenarios and success criteria
- Deployment models and lifecycle management

❌ **Out of Scope:**
- Specific workflow implementations (those belong in feature specs)
- n8n internal architecture (documented by n8n project)
- Detailed API specifications (those belong in ADRs)
- Vendor comparisons (Zapier, Make, etc.)

---

## 2. n8n Modular Capabilities

n8n can be integrated into the Chora ecosystem through **six distinct patterns**, each providing different value and complexity. These patterns are **modular** - implement them independently based on need.

### 2.1 Pattern N1: n8n as Standalone Workflow Orchestrator

**Intent:** Run n8n as an independent service for general-purpose workflow automation, separate from MCP concerns.

**Capabilities:**
- Schedule recurring tasks (data sync, report generation, backups)
- Respond to webhooks from external systems (Stripe payments, GitHub pushes)
- Chain API calls with conditional logic and error handling
- Transform and route data between systems

**Example Use Case:**
> **Workflow:** "When a new user signs up (webhook from Stripe), create a Coda doc, send a Slack notification, and trigger an onboarding email sequence."

**Architecture Position:**
```
External Systems (Stripe, Slack, Coda)
         ↕
    n8n Workflows
         ↕
    n8n Database (SQLite/Postgres)
```

**Value:**
- ✅ Rapid integration development without coding
- ✅ Existing n8n ecosystem (400+ nodes, community workflows)
- ✅ Visual debugging and execution history

**Limitations:**
- ❌ Not directly accessible by AI agents (no MCP interface)
- ❌ No integration with Chora Composer artifact creation
- ❌ Manual workflow management (no BDD-DRSO validation)

**When to Use:**
- Quick prototyping of integrations
- One-off automation tasks
- Teams with existing n8n expertise

---

### 2.2 Pattern N2: n8n as MCP Server

**Intent:** Expose n8n workflow executions as **MCP tools**, allowing AI agents to trigger workflows on demand.

**Capabilities:**
- List available workflows → `n8n:list_workflows`
- Execute workflow → `n8n:execute_workflow`
- Get execution status → `n8n:get_execution_status`
- Get execution result → `n8n:get_execution_result`

**Example Use Case:**
> **AI Agent:** "Please generate the monthly sales report."
> **Claude (via MCP):** Calls `n8n:execute_workflow` with `workflow_id: "monthly-sales-report"`
> **n8n:** Fetches data from Salesforce, generates charts, uploads to Coda, returns doc URL
> **Claude:** "Here's your report: [link]"

**Architecture Position:**
```
AI Client (Claude Desktop, Cursor)
         ↓ JSON-RPC/MCP
    n8n MCP Server
         ↓ n8n API
    n8n Workflow Engine
         ↓
    External Systems
```

**Implementation Requirements:**
- Build MCP server wrapper around n8n REST API
- Map workflow schemas to MCP tool definitions
- Handle async execution (workflows may take seconds/minutes)
- Stream execution logs as MCP resources

**Value:**
- ✅ AI agents can trigger complex multi-step processes
- ✅ Workflows become "skills" for AI agents
- ✅ Existing n8n workflows instantly AI-accessible

**Limitations:**
- ❌ Workflows must be pre-created in n8n UI
- ❌ No dynamic workflow generation by AI
- ❌ Limited parameter validation (relies on n8n schemas)

**When to Use:**
- Exposing existing n8n automations to AI agents
- Providing AI agents with business process execution capabilities
- Bridging AI agents to legacy systems via n8n

---

### 2.3 Pattern N3: n8n as MCP Client

**Intent:** Allow n8n workflows to **consume MCP tools** from other servers (Chora Composer, Coda MCP, filesystem, etc.).

**Capabilities:**
- Custom n8n node: "MCP Tool Call"
  - Select MCP server (from registry)
  - Select tool (dynamic dropdown)
  - Provide arguments (JSON or form fields)
  - Receive result and pass to next node
- Workflows can chain MCP tool calls with other integrations

**Example Use Case:**
> **Workflow:** "When GitHub issue labeled 'needs-docs', call `chora:generate_content` with issue description, then call `chora:assemble_artifact` to create docs, then comment on issue with artifact link."

**Architecture Position:**
```
n8n Workflow
    ↓
Custom MCP Client Node
    ↓ JSON-RPC/STDIO or HTTP
MCP Servers (Chora Composer, Coda MCP, etc.)
```

**Implementation Requirements:**
- Develop custom n8n node `@chora/mcp-tool-call`
- Support both STDIO (subprocess) and HTTP (SSE) MCP transports
- Dynamic schema fetching (tools/list) for UI autocomplete
- Error handling for MCP protocol errors
- Credential management for MCP server authentication

**Value:**
- ✅ Workflows can leverage AI-powered tools (Chora Composer)
- ✅ Centralize tool logic in MCP servers, orchestrate in n8n
- ✅ Combine low-code (n8n) with high-code (MCP) capabilities

**Limitations:**
- ❌ Requires custom node development
- ❌ MCP transport complexity (STDIO vs. HTTP)
- ❌ Debugging across n8n and MCP layers

**When to Use:**
- Workflows that need AI content generation (Chora Composer)
- Complex orchestrations requiring multiple specialized tools
- Bridging n8n's integration breadth with MCP's tool depth

---

### 2.4 Pattern N4: n8n as Gateway & Aggregator (MCP Meta-Server)

**Intent:** Use n8n itself as a **Pattern P5 Gateway** that routes MCP requests to multiple backend MCP servers, potentially transforming requests/responses.

**Capabilities:**
- Single MCP endpoint exposes tools from multiple backends
- n8n workflows implement routing logic
  - Example: `n8n:smart_search` routes to Coda, Notion, or Google Drive based on query
- Transform MCP requests (enrich context, split into sub-requests)
- Aggregate MCP responses (merge data from multiple sources)

**Example Use Case:**
> **AI Agent:** Calls `n8n:universal_create_document`
> **n8n Gateway:** Workflow determines target system based on doc type
> **n8n Gateway:** Routes to `coda:create_doc`, `notion:create_page`, or `gdrive:create_file`
> **n8n Gateway:** Returns standardized response to AI agent

**Architecture Position:**
```
AI Client
    ↓ MCP
n8n MCP Gateway (Pattern P5)
    ↓ (routing workflows)
    ├→ Chora Composer MCP
    ├→ Coda MCP
    ├→ Notion MCP
    └→ Google Drive MCP
```

**Implementation Requirements:**
- n8n MCP Server (Pattern N2) receives all tool calls
- Each tool maps to a workflow that routes to backends
- Workflows use MCP Client Node (Pattern N3) to call backends
- Complex routing logic (conditions, transformations) in workflows

**Value:**
- ✅ Visual gateway logic (vs. coded Python/TypeScript)
- ✅ Non-developers can modify routing rules
- ✅ Built-in retry, error handling, logging from n8n

**Limitations:**
- ❌ Performance overhead (workflow execution for each MCP call)
- ❌ Complexity of managing gateway workflows
- ❌ Potential for tight coupling between gateway and backends

**When to Use:**
- Need dynamic routing logic that changes frequently
- Want non-developers to manage gateway behavior
- Require complex transformation/aggregation beyond simple proxying

**Alternative:** Use coded gateway (mcp-n8n Python implementation) for performance-critical routing, n8n for edge cases.

---

### 2.5 Pattern N5: n8n Workflow as Artifact Assembly Pipeline

**Intent:** Use n8n to **orchestrate multi-stage artifact creation**, calling Chora Composer tools in sequence while integrating external data sources.

**Capabilities:**
- Workflow gathers content from multiple sources (APIs, databases, files)
- Calls `chora:generate_content` for each section
- Calls `chora:assemble_artifact` to combine sections
- Stores metadata in Coda, sends notifications, deploys artifact

**Example Use Case:**
> **Workflow:** "Generate Weekly Engineering Report"
> 1. Fetch GitHub commits (GitHub API)
> 2. Fetch Jira tickets closed (Jira API)
> 3. Fetch deployment metrics (DataDog API)
> 4. For each data source, call `chora:generate_content` with template
> 5. Call `chora:assemble_artifact` with config `weekly-eng-report`
> 6. Upload artifact to Coda docs
> 7. Send Slack notification with link

**Architecture Position:**
```
n8n Workflow
    ├→ External APIs (GitHub, Jira, DataDog)
    ├→ Chora Composer MCP (content generation)
    ├→ Coda MCP (metadata storage)
    └→ Notification Services (Slack, Email)
```

**Implementation Requirements:**
- Pattern N3 (n8n as MCP Client) for Chora Composer integration
- n8n nodes for data fetching (HTTP Request, Database, etc.)
- Workflow templates for common artifact pipelines
- Error handling and retry logic for multi-step pipelines

**Value:**
- ✅ Automate recurring documentation tasks
- ✅ Integrate artifact creation with business data sources
- ✅ Decouple orchestration (n8n) from content generation (Chora)

**Limitations:**
- ❌ Workflow complexity grows with pipeline stages
- ❌ Debugging multi-stage failures requires n8n expertise
- ❌ Performance depends on n8n execution speed

**When to Use:**
- Scheduled artifact generation (reports, dashboards, newsletters)
- Artifacts requiring data from multiple external systems
- Teams want visual pipeline representation

---

### 2.6 Pattern N6: n8n Event Processing for MCP Ecosystem

**Intent:** Use n8n to **process events from the ecosystem** and trigger MCP tool calls or workflows in response.

**Capabilities:**
- Listen to webhooks from external systems (GitHub, Stripe, Slack)
- Poll databases/APIs for changes
- Subscribe to message queues (RabbitMQ, Kafka, Redis)
- On event, call MCP tools or trigger other n8n workflows
- Implement event filtering, transformation, enrichment

**Example Use Case:**
> **Event:** GitHub PR merged
> **n8n Workflow:** Triggered by GitHub webhook
> **Workflow Actions:**
> 1. Extract PR metadata (files changed, author, description)
> 2. Call `chora:generate_content` with template `pr-summary`
> 3. Call `coda:create_row` in "PR Log" table
> 4. If files include `/docs`, call `chora:assemble_artifact` for docs rebuild
> 5. Send Slack notification to #engineering

**Architecture Position:**
```
Event Sources (Webhooks, Queues, Polls)
         ↓
    n8n Event Workflows
         ↓
    ├→ MCP Tools (Chora, Coda)
    ├→ Other n8n Workflows
    └→ External Systems (Slack, Email)
```

**Implementation Requirements:**
- n8n webhook endpoints for inbound events
- Pattern N3 (MCP Client) for calling tools
- Event schema validation and transformation
- Error handling and dead-letter queues
- Telemetry for event processing metrics

**Value:**
- ✅ Real-time reactivity to ecosystem events
- ✅ Decouple event producers from consumers
- ✅ Central event processing hub with visibility

**Limitations:**
- ❌ n8n webhook scalability (consider message queue for high volume)
- ❌ Event ordering guarantees depend on n8n queue config
- ❌ Debugging event flows across multiple workflows

**When to Use:**
- Need event-driven automation (not just scheduled)
- Want visual event processing logic
- Integrating multiple event sources

---

### 2.7 Pattern N7: n8n Orchestrates Conversational Config Authoring

**Intent:** Use n8n to **orchestrate the config lifecycle** for Chora Compose workflows, enabling iterative refinement through AI-assisted conversations.

**Capabilities:**
- Orchestrate draft → test → iterate → save workflow
- Call Chora Compose config lifecycle tools (v1.1.0+)
- Enable non-technical users to create workflows conversationally
- Integrate with Claude Desktop or other AI agents via MCP
- Automate config validation and testing loops

**Example Use Case:**
> **User:** "I need a weekly report that pulls data from Jira and formats it nicely"
> **n8n Workflow:**
> 1. Capture user intent via webhook or chat interface
> 2. Call `chora:draft_config` with user requirements
>    - Type: content
>    - Generator: jinja2
>    - Template: report template
>    - Inputs: Jira API configuration
> 3. Call `chora:test_config` to preview output
> 4. Show preview to user for feedback
> 5. If user approves → Call `chora:save_config`
> 6. If user requests changes → Call `chora:modify_config` and repeat
> 7. Schedule weekly execution using saved config

**Architecture Position:**
```
User Interface (Chat, Form, API)
         ↓
    n8n Orchestration Workflow
         ↓
    ├→ chora:draft_config (create ephemeral draft)
    ├→ chora:test_config (preview generation)
    ├→ User Feedback Loop
    │   ├→ chora:modify_config (iterate)
    │   └→ chora:test_config (re-preview)
    ├→ chora:save_config (persist to filesystem)
    └→ Schedule/Trigger Execution
```

**Implementation Requirements:**
- Chora Compose v1.1.0+ with config lifecycle tools
- n8n webhook or form for user input
- State management for draft configs during iteration
- User feedback mechanism (Slack, email, web form)
- Pattern N3 (MCP Client) to call Chora Compose tools

**Value:**
- ✅ Zero-friction workflow creation (no IDE required)
- ✅ Conversational iteration (natural language refinement)
- ✅ Non-technical users can create complex configs
- ✅ Automatic validation before persistence
- ✅ 30-day draft retention for experimentation

**Limitations:**
- ❌ Requires user feedback loop design
- ❌ Draft storage cleanup needed after 30 days
- ❌ Complex configs may still need manual JSON editing

**When to Use:**
- Democratizing workflow creation for non-developers
- Rapid prototyping of new content generators
- User-driven documentation generation workflows
- Iterative refinement scenarios with stakeholder feedback

**Example n8n Workflow JSON Snippet:**
```json
{
  "nodes": [
    {
      "name": "Receive User Request",
      "type": "webhook",
      "parameters": {
        "path": "create-workflow",
        "responseMode": "responseNode"
      }
    },
    {
      "name": "Draft Config",
      "type": "MCP Tool Call",
      "parameters": {
        "server": "chora-compose",
        "tool": "draft_config",
        "arguments": {
          "config_type": "content",
          "config_data": "={{ $json.userRequirements }}"
        }
      }
    },
    {
      "name": "Test Draft",
      "type": "MCP Tool Call",
      "parameters": {
        "server": "chora-compose",
        "tool": "test_config",
        "arguments": {
          "draft_id": "={{ $node['Draft Config'].json.draft_id }}"
        }
      }
    },
    {
      "name": "Send Preview",
      "type": "Slack",
      "parameters": {
        "channel": "#workflows",
        "text": "Preview ready! Check output and reply 'approve' or 'change: <feedback>'"
      }
    }
  ]
}
```

---

## 3. n8n in the 3-Layer Chora Architecture

The Chora ecosystem follows a **3-layer architecture**:

1. **Workspace Layer** (R&D) - Individual repos, local development, experimentation
2. **Platform Layer** (Distribution) - Shared capabilities, tooling, standards
3. **Capabilities Layer** (Consumption) - Deployments, end-user services, production

**n8n's Role:**

### 3.1 Workspace Layer

**n8n Development Workflows:**
- Developers create and test workflows locally (`n8n start`)
- Workflows stored as JSON in version control
- CI/CD validates workflow schemas and runs tests
- BDD scenarios describe workflow behavior

**Example:**
```
workspace-repos/
└── automation-workflows/
    ├── workflows/
    │   ├── github-pr-summary.json
    │   └── weekly-report.json
    ├── tests/
    │   └── workflows.test.ts
    └── README.md
```

### 3.2 Platform Layer

**n8n as Platform Capability:**
- Shared n8n instance deployed as platform service
- Workflow templates published to platform registry
- Custom nodes (`@chora/mcp-tool-call`) distributed via npm
- Platform team provides:
  - n8n deployment manifests (Docker Compose, Kubernetes)
  - Workflow linting and validation tools
  - Telemetry integration (OpenTelemetry export)
  - Authentication/authorization patterns

**Platform Artifacts:**
- `chora-platform/capabilities/n8n/` - Deployment configs
- `chora-platform/packages/@chora/n8n-mcp-node/` - Custom MCP node
- `chora-platform/templates/workflows/` - Reusable workflows

### 3.3 Capabilities Layer

**n8n Production Deployments:**
- Self-hosted n8n instance(s) serving production workflows
- Workflows consume production MCP servers
- Monitored via platform telemetry (Prometheus, Grafana)
- Workflows triggered by production events (webhooks, schedules)

**Deployment Models:**
- **Shared n8n Instance** - Single n8n deployment, multi-tenant workflows
- **Per-Service n8n** - Each capability has its own n8n instance
- **Hybrid** - Platform n8n + service-specific workflow runners

---

## 4. n8n-Specific DRSO Integration

n8n workflows must follow **DRSO (Development → Release → Security → Operations)** lifecycle:

### 4.1 Development

**Workflow as Code:**
- Workflows stored as JSON in git repositories
- Version controlled with semantic versioning
- BDD scenarios describe expected behavior
  ```gherkin
  Scenario: GitHub PR merged triggers documentation update
    Given a GitHub PR is merged with files in /docs
    When the webhook triggers the "pr-summary" workflow
    Then the workflow should call chora:generate_content
    And the workflow should call chora:assemble_artifact
    And the workflow should post a Slack notification
  ```

**Testing:**
- **Unit Tests** - Mock n8n nodes, assert workflow logic
- **Integration Tests** - Run workflow against test MCP servers
- **End-to-End Tests** - Trigger real webhooks, verify outcomes

**Tooling:**
- `n8n export:workflow` - Export workflow JSON
- `n8n import:workflow` - Import workflow JSON
- Custom linter for workflow validation

### 4.2 Release

**Workflow Deployment Pipeline:**
1. **Gate 1: Code Review** - PR review of workflow JSON changes
2. **Gate 2: Testing** - Automated tests pass in CI
3. **Gate 3: Staging Deploy** - Deploy to staging n8n instance
4. **Gate 4: Manual Validation** - Test in staging environment
5. **Gate 5: Production Deploy** - Deploy to production n8n

**Versioning:**
- Workflow tags: `v1.2.3`
- Changelog documents changes between versions
- Rollback procedure: revert to previous workflow version

**Deployment Methods:**
- **API-Based** - Use n8n API to update workflows programmatically
- **Database Migration** - Update n8n database directly (SQLite/Postgres)
- **Declarative** - GitOps approach (workflows as code → sync to n8n)

### 4.3 Security

**Workflow Security Considerations:**
- **Credential Management** - n8n credentials encrypted at rest, access-controlled
- **Input Validation** - Validate webhook payloads and user inputs
- **Rate Limiting** - Prevent webhook abuse and DoS
- **Audit Logging** - Log all workflow executions and MCP tool calls
- **Least Privilege** - Workflows only access required credentials/nodes

**Custom Node Security:**
- Code review for custom nodes (`@chora/mcp-tool-call`)
- Dependency scanning (npm audit)
- Sandboxing for Function nodes (limit `require()` access)

### 4.4 Operations

**Monitoring:**
- **Execution Metrics** - Success rate, duration, error rate per workflow
- **MCP Tool Metrics** - Call counts, latency, errors for each tool
- **Resource Metrics** - CPU, memory, queue depth for n8n instance
- **Alerting** - Notify on workflow failures, timeout, or spike in errors

**Telemetry Export:**
- n8n → OpenTelemetry Collector → Platform Telemetry Store
- Structured logs include:
  - `workflow_id`, `execution_id`
  - `mcp_server`, `mcp_tool`, `mcp_arguments`
  - `result`, `error`, `duration`

**Incident Response:**
- Workflow execution history viewable in n8n UI
- Re-run failed executions
- Pause workflows during incidents
- Debug mode for detailed logging

---

## 5. Integration Patterns & Examples

### 5.1 Example: AI-Triggered Report Generation (v1.1.0 Enhanced)

**Scenario:** User asks Claude to generate monthly sales report with ability to refine before saving.

**Pattern:** N2 (n8n as MCP Server) + N7 (Conversational Config Authoring)

**Flow:**
1. **User:** "Generate the monthly sales report for October."
2. **Claude:** Detects this is first-time request, calls `n8n:execute_workflow` with `workflow_id: "monthly-sales-report-draft"`
3. **n8n Workflow:**
   - Check if config exists using `chora:list_content_configs`
   - If not exists → Create draft:
     - Call `chora:draft_config` with report template
     - Call `chora:test_config` to preview with October data
     - Return preview to Claude
   - If exists → Proceed with generation:
     - Fetch sales data from Salesforce API
     - Fetch expense data from QuickBooks API
     - Call `chora:generate_content` with existing config
     - Call `chora:assemble_artifact` with config `monthly-sales-report`
     - Upload PDF to Coda Docs
     - Return Coda doc URL
4. **Claude (first time):** "I've created a draft report. The preview shows [summary]. Would you like to refine it or proceed?"
5. **User:** "Looks good, save it and generate for October."
6. **Claude:** Calls `chora:save_config` then regenerates → "Here's your October sales report: [link]"

**Value:**
- First-time: Conversational config creation with preview
- Subsequent: Fast generation with saved config
- Combines v1.1.0 config lifecycle with traditional workflow execution

---

### 5.2 Example: Event-Driven Documentation Updates

**Scenario:** Automatically update API docs when OpenAPI spec changes.

**Pattern:** N6 (n8n Event Processing)

**Flow:**
1. **Event:** GitHub push to `main` branch modifying `openapi.yaml`
2. **GitHub Webhook → n8n**
3. **n8n Workflow:**
   - Parse webhook payload, extract changed files
   - If `openapi.yaml` changed, download new spec
   - Call `chora:generate_content` with template `api-endpoint-docs`
   - Call `chora:assemble_artifact` with config `api-documentation`
   - Commit updated docs to `docs/` folder
   - Create PR with docs changes
   - Send Slack notification to #api-team
4. **Developer:** Reviews and merges docs PR

**Value:** Keeps documentation in sync with code automatically.

---

### 5.3 Example: Cross-MCP Workflow Orchestration

**Scenario:** Onboard new customer with multi-tool workflow.

**Pattern:** N3 (n8n as MCP Client) + N5 (Artifact Assembly)

**Flow:**
1. **Trigger:** Stripe webhook "customer.created"
2. **n8n Workflow:**
   - **Step 1:** Call `coda:create_doc` to create customer workspace
   - **Step 2:** Call `chora:generate_content` with template `welcome-letter`
   - **Step 3:** Call `chora:assemble_artifact` to create onboarding guide
   - **Step 4:** Upload artifact to customer Coda doc
   - **Step 5:** Call `sendgrid:send_email` with welcome message
   - **Step 6:** Call `slack:post_message` to #sales channel
   - **Step 7:** Call `hubspot:create_deal` to track onboarding progress

**Value:** Orchestrates 7 different tools (2 MCP, 5 external APIs) in single workflow.

---

### 5.4 Example: Dynamic Gateway Routing

**Scenario:** AI agent needs to search "documents" but source varies by user preference.

**Pattern:** N4 (n8n as Gateway)

**Flow:**
1. **User:** "Find all documents about pricing strategy."
2. **Claude:** Calls `n8n:search_documents` with `query: "pricing strategy"`
3. **n8n Gateway Workflow:**
   - Lookup user preferences (from Coda user profile)
   - **If** user prefers Notion → Call `notion:search`
   - **Else if** user prefers Coda → Call `coda:search_rows`
   - **Else if** user prefers Google Drive → Call `gdrive:search_files`
   - Normalize results to common format
   - Return aggregated results to Claude
4. **Claude:** "I found 5 documents..." (from user's preferred system)

**Value:** Single tool interface (`search_documents`) abstracts multiple backends.

---

## 6. Deployment Options

n8n can be deployed in multiple configurations based on scale, security, and operational requirements.

### 6.1 Local Development (STDIO)

**Use Case:** Developers testing workflows locally.

**Setup:**
```bash
n8n start --tunnel=false
# Runs on http://localhost:5678
```

**MCP Integration:**
- n8n MCP Server connects to local n8n via HTTP API
- Workflows tested in isolation before commit

**Pros:**
- ✅ Fast iteration
- ✅ No cloud dependencies

**Cons:**
- ❌ No production data access
- ❌ Manual setup for each developer

---

### 6.2 Self-Hosted (Docker Compose)

**Use Case:** Small teams, single-tenant deployments.

**Setup:**
```yaml
# docker-compose.yml
services:
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
    volumes:
      - n8n_data:/home/node/.n8n
      - ./workflows:/home/node/.n8n/custom
```

**MCP Integration:**
- n8n MCP Server deployed as separate container
- Communicates via n8n REST API (http://n8n:5678)

**Pros:**
- ✅ Full control over deployment
- ✅ Data stays on-premise

**Cons:**
- ❌ Manual scaling and backup management
- ❌ Requires ops expertise

---

### 6.3 Kubernetes (Production Scale)

**Use Case:** Large teams, high availability, multi-tenant.

**Setup:**
```yaml
# k8s/n8n-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: n8n
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: n8n
        image: n8nio/n8n:latest
        env:
        - name: DB_TYPE
          value: postgresdb
        - name: DB_POSTGRESDB_HOST
          value: postgres-service
```

**MCP Integration:**
- n8n MCP Server as Kubernetes Deployment
- Load balanced across multiple n8n pods
- Persistent volume for workflow storage

**Pros:**
- ✅ Horizontal scaling
- ✅ High availability
- ✅ Integrated with platform monitoring

**Cons:**
- ❌ Complex setup
- ❌ Higher operational overhead

---

### 6.4 n8n Cloud (Managed)

**Use Case:** Teams wanting zero infrastructure management.

**Setup:**
- Sign up at n8n.cloud
- Connect via API key

**MCP Integration:**
- n8n MCP Server connects to n8n.cloud API
- Workflows managed in cloud UI

**Pros:**
- ✅ Zero infrastructure
- ✅ Automatic updates and backups

**Cons:**
- ❌ Data in cloud (compliance considerations)
- ❌ Less control over execution environment
- ❌ Subscription cost

---

## 7. n8n as MCP Server (Pattern N2 Deep Dive)

### 7.1 Tool Schema

The n8n MCP Server exposes workflows as tools with dynamic schemas.

**Tool: `n8n:execute_workflow`**

```json
{
  "name": "n8n:execute_workflow",
  "description": "Execute an n8n workflow by ID or name",
  "inputSchema": {
    "type": "object",
    "properties": {
      "workflow_id": {
        "type": "string",
        "description": "The workflow ID or name to execute"
      },
      "parameters": {
        "type": "object",
        "description": "Input parameters for the workflow",
        "additionalProperties": true
      },
      "wait_for_completion": {
        "type": "boolean",
        "description": "Wait for workflow to complete before returning",
        "default": true
      }
    },
    "required": ["workflow_id"]
  }
}
```

**Tool: `n8n:list_workflows`**

```json
{
  "name": "n8n:list_workflows",
  "description": "List all available workflows",
  "inputSchema": {
    "type": "object",
    "properties": {
      "active_only": {
        "type": "boolean",
        "description": "Only list active workflows",
        "default": true
      }
    }
  }
}
```

**Tool: `n8n:get_execution_status`**

```json
{
  "name": "n8n:get_execution_status",
  "description": "Get the status of a workflow execution",
  "inputSchema": {
    "type": "object",
    "properties": {
      "execution_id": {
        "type": "string",
        "description": "The execution ID to check"
      }
    },
    "required": ["execution_id"]
  }
}
```

### 7.2 Execution Models

**Synchronous (Wait for Completion):**
- MCP client blocks until workflow finishes
- Suitable for fast workflows (<30s)
- Returns result directly in tool response

**Asynchronous (Fire and Forget):**
- MCP server returns `execution_id` immediately
- Client polls `n8n:get_execution_status` for result
- Suitable for long-running workflows (minutes/hours)

**Streaming (Future Enhancement):**
- MCP server streams execution progress as resources
- Client receives real-time updates
- Requires MCP resource subscription support

### 7.3 Error Handling

**Workflow Execution Failures:**
- MCP server returns error with workflow execution context
- Includes node that failed, error message, input data
- Client can retry or handle gracefully

**Example Error Response:**
```json
{
  "error": {
    "code": "WORKFLOW_EXECUTION_FAILED",
    "message": "Workflow 'monthly-report' failed at node 'Fetch Sales Data'",
    "details": {
      "execution_id": "exec-123",
      "failed_node": "Fetch Sales Data",
      "error_message": "API request timed out after 30s",
      "retry_allowed": true
    }
  }
}
```

### 7.4 Authentication

**n8n API Authentication:**
- Basic Auth (username/password)
- API Key (via header)
- OAuth (for n8n.cloud)

**MCP Server Configuration:**
```json
{
  "mcpServers": {
    "n8n": {
      "command": "n8n-mcp-server",
      "env": {
        "N8N_API_URL": "https://n8n.example.com",
        "N8N_API_KEY": "your-api-key"
      }
    }
  }
}
```

---

## 8. n8n as MCP Client (Pattern N3 Deep Dive)

### 8.1 Custom MCP Node Architecture

**Node: `@chora/mcp-tool-call`**

**Configuration:**
- **MCP Server Selection** - Dropdown of registered servers
- **Tool Selection** - Dynamic dropdown (fetched via `tools/list`)
- **Arguments** - JSON editor or auto-generated form fields
- **Transport** - STDIO or HTTP/SSE

**UI Flow:**
1. User drags `MCP Tool Call` node into workflow
2. Selects MCP server from dropdown (e.g., "chora-composer")
3. Node fetches tool list from server
4. User selects tool (e.g., "assemble_artifact")
5. Node fetches tool schema (inputSchema)
6. Node generates form fields for arguments
7. User fills in arguments or maps from previous node
8. Node executes, result flows to next node

### 8.2 Transport Implementations

**STDIO Transport:**
- Node spawns MCP server as subprocess
- Communicates via stdin/stdout (JSON-RPC)
- Subprocess lifecycle managed by node
- Suitable for local MCP servers

**HTTP/SSE Transport:**
- Node makes HTTP requests to remote MCP server
- Server-Sent Events for streaming responses
- Requires MCP server exposed via HTTP
- Suitable for remote/cloud MCP servers

### 8.3 Credential Management

**MCP Server Credentials in n8n:**
- Custom credential type: `mcpServerCredential`
- Fields: `server_url`, `api_key`, `transport_type`
- Encrypted storage via n8n credential system
- Referenced by MCP Tool Call node

**Example Credential:**
```json
{
  "name": "Chora Composer MCP",
  "type": "mcpServerCredential",
  "data": {
    "server_url": "http://localhost:3000",
    "transport_type": "stdio",
    "command": "chora-compose",
    "environment": {
      "ANTHROPIC_API_KEY": "sk-ant-..."
    }
  }
}
```

### 8.4 Error Handling in Workflows

**MCP Protocol Errors:**
- Node catches MCP errors and exposes as workflow errors
- Workflow can route to error path (n8n error handling)
- Retry logic configured per node

**Example Workflow Error Path:**
```
[Trigger] → [MCP: Chora Generate]
              ↓ Success
            [MCP: Chora Assemble]
              ↓ Error
            [Send Slack Alert]
              ↓
            [Create Error Log in Coda]
```

---

## 9. Telemetry & Observability

### 9.1 Metrics

**Workflow Execution Metrics:**
- `n8n_workflow_executions_total{workflow_id, status}` - Counter
- `n8n_workflow_execution_duration_seconds{workflow_id}` - Histogram
- `n8n_workflow_execution_errors_total{workflow_id, node}` - Counter

**MCP Tool Call Metrics:**
- `n8n_mcp_tool_calls_total{server, tool, status}` - Counter
- `n8n_mcp_tool_call_duration_seconds{server, tool}` - Histogram
- `n8n_mcp_tool_call_errors_total{server, tool, error_type}` - Counter

**System Metrics:**
- `n8n_active_workflows` - Gauge
- `n8n_queue_depth` - Gauge
- `n8n_worker_utilization` - Gauge

### 9.2 Logs

**Structured Logging Format:**
```json
{
  "timestamp": "2025-10-15T10:30:00Z",
  "level": "info",
  "service": "n8n",
  "workflow_id": "wf-123",
  "execution_id": "exec-456",
  "node": "MCP Tool Call",
  "mcp_server": "chora-composer",
  "mcp_tool": "assemble_artifact",
  "mcp_arguments": { "artifact_config_id": "user-docs" },
  "duration_ms": 1250,
  "result": "success",
  "message": "MCP tool call completed successfully"
}
```

**Log Levels:**
- **DEBUG** - Node-level execution details
- **INFO** - Workflow start/complete, tool calls
- **WARN** - Retries, slow executions
- **ERROR** - Failures, exceptions

### 9.3 Traces

**OpenTelemetry Integration:**
- n8n → OpenTelemetry Collector → Jaeger/Tempo
- Trace spans for:
  - Workflow execution (root span)
  - Each node execution (child span)
  - MCP tool calls (grandchild span)

**Example Trace:**
```
Workflow: monthly-sales-report (1200ms)
  ├─ Node: Fetch Sales Data (300ms)
  ├─ Node: MCP Tool Call (800ms)
  │   └─ MCP: chora:generate_content (750ms)
  └─ Node: Send Email (100ms)
```

### 9.4 Dashboards

**Grafana Dashboard: "n8n Workflows"**
- Workflow execution success rate (last 24h)
- Top 10 slowest workflows
- Error rate by workflow
- Queue depth over time

**Grafana Dashboard: "MCP Integration"**
- MCP tool call volume by server
- MCP tool call latency (p50, p95, p99)
- MCP error rate by tool
- Active MCP server connections

---

## 10. Value Scenarios

### 10.1 Scenario: Accelerated Integration Development

**Problem:** Team needs to integrate Slack notifications, Coda updates, and GitHub issue creation for a new feature.

**Without n8n:**
- Developer writes custom Python script
- Handles Slack API, Coda API, GitHub API manually
- Writes error handling, retries, logging
- Time: 4-6 hours

**With n8n:**
- Developer drags Slack, Coda, GitHub nodes into workflow
- Configures credentials and maps fields
- Tests in n8n UI
- Exports workflow JSON, commits to git
- Time: 30-45 minutes

**Value:** **~8x faster development** for integration tasks.

---

### 10.2 Scenario: Non-Developer Automation

**Problem:** Product manager wants to automate weekly report generation but can't code.

**Without n8n:**
- Request added to engineering backlog
- Waits weeks for developer availability
- Developer builds custom script
- PM has no visibility or control

**With n8n:**
- PM creates workflow in n8n UI
- Uses pre-built nodes for data sources
- Calls `chora:assemble_artifact` for formatting
- Schedules weekly execution
- Iterates on report format independently

**Value:** **Democratizes automation**, reduces engineering bottleneck.

---

### 10.3 Scenario: Event-Driven Documentation

**Problem:** API documentation gets out of sync with OpenAPI spec changes.

**Without n8n:**
- Manual process: developer updates spec, remembers to update docs
- Frequent drift between spec and docs
- Customer confusion and support tickets

**With n8n:**
- GitHub webhook triggers workflow on spec change
- Workflow calls `chora:generate_content` with new spec
- Workflow calls `chora:assemble_artifact` for docs
- Workflow creates PR with updated docs
- Developer reviews and merges

**Value:** **Automated documentation sync**, reduced drift, fewer support issues.

---

### 10.4 Scenario: Multi-System Orchestration

**Problem:** Customer onboarding requires 7 different tools (CRM, billing, docs, email, Slack, etc.).

**Without n8n:**
- Developer writes custom orchestration script
- Handles API authentication for 7 services
- Implements error handling and retries
- Difficult to debug and modify
- Time: 8-12 hours

**With n8n:**
- Workflow visually chains 7 nodes
- Each node uses pre-built integration
- Error handling via visual paths
- Easy to modify and debug in UI
- Time: 1-2 hours

**Value:** **~6x faster** for complex orchestrations, visual debugging.

---

### 10.5 Scenario: AI-Powered Workflows

**Problem:** Team wants AI agents to trigger business processes (report generation, data sync, notifications).

**Without n8n:**
- Build custom MCP server for each process
- Write code to handle parameters, errors, async execution
- Maintain multiple MCP server codebases

**With n8n + Pattern N2:**
- Build workflows in n8n UI (no code)
- n8n MCP Server auto-exposes workflows as tools
- AI agents call `n8n:execute_workflow`
- Workflows orchestrate business logic

**Value:** **AI-accessible business processes** without writing MCP server code.

---

## 11. Risks & Mitigations

### 11.1 Risk: n8n Vendor Lock-In

**Description:** Heavy reliance on n8n-specific features makes migration difficult.

**Mitigations:**
- ✅ Store workflows as JSON in git (portable format)
- ✅ Use standard nodes when possible (avoid n8n-only features)
- ✅ Abstract critical logic into MCP tools (can be called from other orchestrators)
- ✅ Monitor n8n project health and community activity

**Fallback:** Workflows can be migrated to code-based orchestrators (Airflow, Temporal) if needed.

---

### 11.2 Risk: Performance Bottlenecks

**Description:** n8n workflow execution overhead impacts latency-sensitive use cases.

**Mitigations:**
- ✅ Use async execution for long-running workflows
- ✅ Scale n8n horizontally (multiple workers)
- ✅ Use queue mode for high throughput
- ✅ Cache MCP tool schemas to reduce initialization time
- ✅ Implement circuit breakers for failing external services

**Fallback:** Critical-path operations use direct MCP calls (bypass n8n), n8n for non-critical orchestration.

---

### 11.3 Risk: Debugging Complexity

**Description:** Multi-layer architecture (AI → MCP → n8n → External APIs) makes debugging difficult.

**Mitigations:**
- ✅ Comprehensive telemetry (metrics, logs, traces)
- ✅ Distributed tracing across all layers
- ✅ n8n execution history with detailed logs
- ✅ Test workflows in isolation before integration
- ✅ Standard error codes and messages

**Tooling:** Grafana dashboards for end-to-end visibility, Jaeger for trace debugging.

---

### 11.4 Risk: Security Vulnerabilities

**Description:** n8n workflows have access to sensitive credentials and systems.

**Mitigations:**
- ✅ Least-privilege access (workflows only access required credentials)
- ✅ Credential encryption at rest
- ✅ Code review for custom nodes
- ✅ Input validation on webhook endpoints
- ✅ Rate limiting and authentication
- ✅ Regular security audits

**Compliance:** Follow platform security standards, conduct penetration testing.

---

### 11.5 Risk: Workflow Sprawl

**Description:** Uncontrolled workflow creation leads to duplication and maintenance burden.

**Mitigations:**
- ✅ Workflow templates and best practices documentation
- ✅ Code review process for new workflows
- ✅ Workflow linting and validation in CI/CD
- ✅ Centralized workflow registry
- ✅ Deprecation policy for unused workflows

**Governance:** Platform team maintains curated workflow library.

---

## 12. Release Roadmap

### Phase 1: Foundation (Q1 2025)

**Goal:** Establish n8n as standalone orchestrator and MCP server.

**Deliverables:**
- ✅ Self-hosted n8n deployment (Docker Compose)
- ✅ n8n MCP Server (Pattern N2) implemented
- ✅ 3-5 reference workflows demonstrating capabilities
- ✅ Documentation and getting started guide
- ✅ Basic telemetry (logs, metrics)

**Success Criteria:**
- Developers can trigger n8n workflows from Claude Desktop
- Workflows successfully call external APIs (GitHub, Slack, Coda)
- Execution history visible in n8n UI

**Risks:**
- n8n learning curve for team
- MCP Server implementation complexity

---

### Phase 2: MCP Client Integration (Q2 2025)

**Goal:** Enable n8n workflows to consume MCP tools.

**Deliverables:**
- ✅ Custom n8n node `@chora/mcp-tool-call`
- ✅ Support for STDIO and HTTP MCP transports
- ✅ Integration with Chora Composer and Coda MCP
- ✅ Example workflows combining n8n nodes + MCP tools
- ✅ Credential management for MCP servers

**Success Criteria:**
- Workflows can call `chora:assemble_artifact`
- Workflows can call `coda:create_row`
- MCP errors handled gracefully in workflows

**Risks:**
- MCP protocol complexity (STDIO vs. HTTP)
- Debugging MCP tool calls within n8n

---

### Phase 3: Event Processing & Automation (Q3 2025)

**Goal:** Implement event-driven workflows and production automation.

**Deliverables:**
- ✅ Webhook endpoints for external events
- ✅ GitHub integration (PR events, issue events)
- ✅ Scheduled workflows (cron, recurring)
- ✅ Event-driven documentation updates
- ✅ Production telemetry and monitoring

**Success Criteria:**
- GitHub PR merge triggers documentation workflow
- Weekly reports auto-generated via schedule
- Alerts triggered on workflow failures

**Risks:**
- Webhook security (authentication, validation)
- Event volume scaling

---

### Phase 4: Gateway & Platform Integration (Q4 2025)

**Goal:** Advanced patterns (gateway, aggregator) and platform-wide adoption.

**Deliverables:**
- ✅ Pattern N4 (n8n as Gateway) for select use cases
- ✅ Workflow templates library
- ✅ BDD-DRSO validation for workflows
- ✅ Kubernetes deployment for high availability
- ✅ Platform-wide telemetry integration

**Success Criteria:**
- 10+ production workflows in use
- <1% workflow failure rate
- Sub-second p95 latency for sync workflows
- Non-developers creating workflows independently

**Risks:**
- Gateway performance overhead
- Workflow governance and sprawl

---

## 13. Success Criteria

### 13.1 Technical Success Criteria

**Integration:**
- ✅ n8n MCP Server exposes ≥5 production workflows as tools
- ✅ n8n workflows successfully call ≥3 different MCP servers
- ✅ End-to-end latency: p95 < 2s for sync workflows
- ✅ Uptime: ≥99.5% for n8n service

**Observability:**
- ✅ All workflow executions emit structured logs
- ✅ Metrics exported to Prometheus
- ✅ Distributed traces visible in Jaeger
- ✅ Dashboards created in Grafana

**Quality:**
- ✅ ≥80% test coverage for custom nodes
- ✅ ≥95% workflow execution success rate
- ✅ Mean time to recovery (MTTR) < 1 hour

---

### 13.2 Business Success Criteria

**Adoption:**
- ✅ ≥10 production workflows deployed
- ✅ ≥3 teams actively using n8n
- ✅ ≥2 non-developers creating workflows

**Efficiency:**
- ✅ Integration development time reduced by ≥50%
- ✅ Documentation sync latency reduced from days to hours
- ✅ Support ticket volume for integration issues reduced by ≥30%

**Value:**
- ✅ ≥5 business processes automated via n8n
- ✅ ROI positive within 6 months (time saved > operational cost)

---

### 13.3 User Experience Success Criteria

**Developer Experience:**
- ✅ Workflow creation time: <1 hour for typical integration
- ✅ Debugging: root cause identified within 15 minutes
- ✅ Documentation: ≥90% developers rate as "helpful" or "very helpful"

**AI Agent Experience:**
- ✅ Workflow tool calls succeed ≥95% of the time
- ✅ Error messages provide actionable guidance
- ✅ Async workflows return status within 5 seconds

**Non-Developer Experience:**
- ✅ Workflow templates enable self-service automation
- ✅ UI intuitive enough for use with minimal training
- ✅ Workflow modification time: <30 minutes for simple changes

---

## 14. Conclusion

This document defines the **solution-neutral intent** for integrating **n8n** into the Chora ecosystem as a **modular, multi-pattern orchestration capability**.

### Key Takeaways:

1. **Six Integration Patterns** - From standalone orchestrator to MCP gateway, each serving different needs
2. **DRSO Alignment** - Workflows follow Development → Release → Security → Operations lifecycle
3. **3-Layer Architecture** - n8n functions as Platform-layer capability with Workspace and Capabilities deployments
4. **Complementary to MCP** - n8n orchestrates, MCP provides specialized tools; together they enable powerful workflows
5. **Phased Adoption** - Start simple (Pattern N1, N2), progressively adopt advanced patterns (N3-N6)

### Next Steps:

1. **Review & Approve** - Stakeholders validate this intent aligns with business goals
2. **Create ADRs** - Document technical decisions for each integration pattern
3. **Develop Features** - Implement Phase 1 deliverables (n8n MCP Server)
4. **Iterate** - Gather feedback, refine patterns, expand use cases

### Open Questions:

- **Governance:** Who owns workflow approval and maintenance?
- **Cost:** Self-hosted vs. n8n.cloud for production?
- **Scope:** Which integration patterns are highest priority?
- **Timeline:** Does the 4-phase roadmap align with business needs?

---

**Document Status:** Ready for review and approval.

**Next Document:** `n8n-mcp-server-adr.md` (Architecture Decision Record for Pattern N2 implementation).
