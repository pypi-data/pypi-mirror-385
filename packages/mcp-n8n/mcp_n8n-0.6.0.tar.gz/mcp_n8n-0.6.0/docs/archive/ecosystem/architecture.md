---
title: Chora Ecosystem Architecture – Intent & Requirements
status: draft
version: 2.0.0
last_updated: 2025-10-14
supersedes: docs/ecosystem/solution-neutral-intent.md (v0.1.0)
complements: docs/ecosystem/drso-integrated-intent.md
related:
  - docs/reference/architecture/ADR-0008-modularization-boundaries.md
  - docs/reference/architecture-integration-map.md
---

# Chora Ecosystem Architecture – Intent & Requirements

This document captures the **problem framing, architectural intent, and requirements** for the Chora developer tooling ecosystem. It describes **why an ecosystem is needed, what outcomes it must enable, and what systemic properties are required**—independent of specific workflow implementations.

This document focuses on **ecosystem architecture**: how capabilities are discovered, how projects coordinate, how manifests are structured, and how governance operates. For **development workflow specifics** (how code flows from conception to release), see [DRSO-Integrated Intent](drso-integrated-intent.md).

**Version 2.0.0 Changes:**
- Offloaded DRSO workflow details to `drso-integrated-intent.md`
- Updated with 3-layer architecture (ADR-0008)
- Enhanced with BDD terminology alignment (ADR-0009)
- Added context bus and virtuous cycle architecture principles
- Refined based on system evolution since v0.1.0

---

## Executive Summary

Development teams work across multiple projects that share concepts (release management, environment control, runtime services) yet evolve independently. The Chora ecosystem provides **shared infrastructure for discovery, coordination, and interoperability** while preserving project autonomy.

### Core Problems Addressed

1. **Duplication of tooling** and inconsistent practices increase onboarding time
2. **Security variance** across projects creates compliance gaps
3. **Slow coordinated change** when capabilities span multiple repositories
4. **Unclear capability discovery** makes it hard to know "who provides what"
5. **Manual coordination** prone to missed notifications and stale information
6. **Disconnected governance** where decisions are scattered across tools

### Ecosystem Approach

Rather than mandating monolithic platforms, the Chora ecosystem provides:

- **Manifested Capabilities** - Every reusable asset declares metadata (purpose, interfaces, dependencies, status)
- **Discovery Infrastructure** - Participants can query "who provides X?" or "is there a capability covering Y?"
- **Change Signaling** - Structured notifications drive coordination with SLA tracking
- **Integration Contracts** - Automated checks enforce compatibility across boundaries
- **Governance Processes** - Decision flows with RACI clarity and appeal mechanisms
- **Observability Foundation** - Telemetry reveals usage patterns and guides investment

### Relationship to DRSO

The ecosystem architecture is **workflow-agnostic**—it defines **what capabilities exist and how they coordinate**, not **how they're developed**. The [DRSO-Integrated Intent](drso-integrated-intent.md) describes one specific workflow implementation (Development → Release → Security → Operations) that operates **within** this ecosystem architecture.

```
Ecosystem Architecture (this document)
    ↓ implemented by
DRSO Workflow (drso-integrated-intent.md)
    ↓ guided by
Architectural Decisions (ADRs)
    ↓ executed via
Change Requests (CRs)
```

---

## Part 1: Foundation

### 1.1 Motivation

Development teams work across several projects that share concepts (release management, environment control, runtime services) yet evolve independently. Traditional approaches create several problems:

#### Problems with Ad Hoc Coordination

- **Duplication:** Teams reimplement similar tooling (CLI frameworks, validation scripts, telemetry) because discovery is hard
- **Inconsistency:** Each project has unique release processes, documentation structures, and quality gates
- **Coordination Failures:** Breaking changes surprise downstream consumers; security patches propagate slowly
- **Onboarding Friction:** New contributors struggle to understand "where to find what"
- **Governance Gaps:** Decisions made in Slack/email without traceability or appeals

#### What Ecosystems Enable

- **Shared Understanding** - Common vocabulary for lifecycle stages and artifact types
- **Composable Tooling** - Projects adopt shared components without central bottlenecks
- **Coordinated Change** - Cross-project needs surface early with transparent ownership
- **Runtime Interop** - Services discover and consume each other dynamically
- **Trust & Governance** - Security, compatibility, and quality maintained through automated contracts

### 1.2 Primary Objectives

1. **Shared Understanding**
   - Common vocabulary for lifecycle stages (plan, build, validate, release, operate)
   - Unified artifact types (manifests, behaviors, contracts) recognized across projects
   - Terminology alignment (see ADR-0009 for BDD integration)

2. **Composable Tooling**
   - Projects adopt shared components via versioned package dependencies
   - Capability providers contribute without central bottlenecks
   - 3-layer architecture (ADR-0008): workspace (R&D) → platform (distribution) → capabilities (consumption)

3. **Coordinated Change**
   - Change signals surface cross-project needs early
   - Ownership assigned transparently (RACI matrix)
   - Decisions communicated back to all participants

4. **Runtime Interop**
   - Services expose standardized metadata (manifests)
   - Dynamic discovery via indexes and APIs
   - Compatibility checked at runtime (not just build-time)

5. **Trust & Governance**
   - Security baselines enforced via integration contracts
   - Compatibility matrices prevent breaking changes
   - Quality validated through automated checks
   - Governance council mediates disputes with appeals process

### 1.3 Actors & Roles

**Project Maintainers** - Steward individual repositories; need clarity on ecosystem expectations and support when changes affect others

**Developers** - Consume tooling during day-to-day work; prefer predictable UX and self-serve documentation

**Automation/Agents** - Execute scripts, tests, or operations; require machine-readable manifests, deterministic interfaces, and auditable behavior

**Coordinators/Stewards** - Mediate cross-project topics, maintain shared infrastructure, and record decisions

**Stakeholders** - Validate that capabilities deliver value; provide approval for releases; guide prioritization

---

## Part 2: Ecosystem Capabilities

### 2.1 Lifecycle Alignment

**Principle:** Each project maps its workflows to shared lifecycle stages for consistency.

**Shared Lifecycle Stages:**
- **Plan** - Identify needs, define requirements, draft designs
- **Build** - Implement capabilities, write tests, create artifacts
- **Validate** - Run automated checks, integration tests, security scans
- **Release** - Publish versioned artifacts with evidence (manifests, SBOMs, coverage)
- **Operate** - Deploy to runtime, monitor health, collect feedback
- **Retire** - Deprecate, migrate users, archive artifacts

**Implementation Note:** The DRSO workflow (see drso-integrated-intent.md) implements these stages as 4 phases with 5 validation gates. Other workflows are possible.

**Tooling Support:** `chora-cli` can query stage-appropriate actions:
```bash
chora-cli lifecycle stage-actions --stage validate
# Returns: integration contracts, security scans, coverage checks
```

### 2.2 Manifested Capabilities

**Principle:** Every reusable asset (CLI command, behavior spec, runtime service) declares metadata describing its purpose, interfaces, dependencies, and status.

**Manifest Format:** `star.yaml` or `manifests/star.yaml` in repository root

**Core Fields:** (See Part 3 for detailed schema)
- Identity (id, version, owner)
- Lifecycle (stage, stability)
- Interfaces (inputs, outputs)
- Dependencies (required capabilities, external services)
- Security (tier, required secrets)
- Governance (ADR links, validation status)
- Features (user-testable scenarios with automation)
- Telemetry (signals, usage metrics)

**Discovery Hints:**
Manifests should declare CLI commands, MCP endpoints, and documentation references so automation knows how to invoke the capability after discovery:
```yaml
discovery:
  cli_commands:
    - chora-cli drso sbom --help
  mcp_endpoints:
    - protocol: mcp
      url: http://localhost:8080/mcp
  docs:
    - type: tutorial
      url: docs/tutorials/first-sbom.md
```

### 2.3 Capability Discovery

**Architecture:** Hybrid approach—authoritative manifests stay with owning repositories; central indices mirror metadata for search and caching via documented APIs.

**Location & Distribution:**
- **Required:** Manifests in repo roots (star.yaml)
- **Required:** Manifests in release artifacts (GitHub releases)
- **Optional:** Expose via HTTPS endpoint for runtime discovery

**Central Index (Future):**
- Mirrors manifests for search/caching
- Uses ETag/If-Modified-Since to synchronize
- Refresh cadence configurable (default: daily)
- Manifests supply `updated_at` and optional `ttl`

**Discovery Queries:**
```bash
# Who provides SBOM generation?
chora-cli discovery search --capability sbom

# Is there a behavior covering MCP registry management?
chora-cli discovery behaviors --query "mcp registry"

# Show all capabilities in 'operate' lifecycle stage
chora-cli discovery list --lifecycle-stage operate
```

**Cache & Refresh:**
- Index refresh cadence: daily (configurable)
- Clients warn when TTL exceeded
- Staleness detection: compare manifest timestamps vs. latest release tags

**Offline Operation:**
Export/import commands create signed bundles (manifest + SBOM + behaviors) for air-gapped use. Mirror servers verify signatures and manifest versions before syncing.

### 2.4 Documentation & Templates

**Principle:** Every capability exposes Diataxis-aligned documentation and reusable templates.

**Diataxis Quadrants:**
- **Tutorial** - Guided learning for newcomers (step-by-step onboarding)
- **How-to** - Task-focused instructions (deployment, troubleshooting)
- **Reference** - Factual resources (APIs, schemas, CLI commands)
- **Explanation** - Conceptual understanding (architecture, rationale, tradeoffs)

**Templates Provided:**
- CLI help (auto-generated from manifests)
- AGENTS snippets (MCP server configuration)
- CI workflows (GitHub Actions, GitLab CI templates)
- Value scenario templates (user-testable scenarios with automation)

**Documentation Requirements:**
Every capability manifest should link to documentation in all four quadrants:
```yaml
documentation:
  tutorial: docs/tutorials/first-deployment.md
  how_to: docs/how-to/troubleshoot-errors.md
  reference: docs/reference/api-spec.yaml
  explanation: docs/explanation/architecture-rationale.md
```

**Implementation Note:** The DRSO workflow (drso-integrated-intent.md) maps Diataxis quadrants to specific validation gates. This ecosystem architecture only requires that documentation exists and is discoverable.

### 2.5 Value Scenarios

**Principle:** Each capability publishes user-testable scenarios with manual and automated verification paths, linked to change signals and telemetry.

**Definition:** A **value scenario** (also called a "Feature" in BDD terminology per ADR-0009) describes user-facing value that can be demonstrated and validated.

**Format:**
```markdown
## Feature: MCP Server Registration

**As a** developer
**I want** to register my MCP server with the ecosystem
**So that** other projects can discover and use it

**Scenarios:**
- Scenario: Register new server via CLI
- Scenario: Validate server manifest schema
- Scenario: Server appears in discovery index
- Scenario: Downstream project consumes server

**Manual Verification:**
1. Run `chora-cli mcp register --manifest server.yaml`
2. Verify server appears in `chora-cli discovery list`
3. Confirm downstream project can connect

**Automated Test:** `tests/value-scenarios/test_mcp_registration.py`
```

**Manifest Integration:**
```yaml
features:
  - id: mcp.registry.register
    description: Register MCP server with ecosystem
    scenarios: 4
    automated_test: tests/value-scenarios/test_mcp_registration.py
    how_to_guide: docs/how-to/register-server.md
```

**Value Scenario Catalog (Future):**
Generate a catalog of all Features with Scenarios for validation:
```bash
chora-cli discovery scenarios --output docs/capabilities/scenarios.md
```

**Implementation Note:** The DRSO workflow (drso-integrated-intent.md) defines how value scenarios flow through validation gates. This ecosystem architecture only requires that scenarios are documented and testable.

### 2.6 Repository Overview

**Principle:** Every repository publishes an autogenerated overview (front page) summarizing current capabilities, value scenarios, signals, and telemetry.

**Purpose:**
- **Humans:** Orient quickly ("what does this repo do?")
- **LLM Agents:** Navigate without manual restatement

**Generation:**
```bash
chora-cli repo-overview generate --output README.md
```

**Content:**
- Repository identity (name, owner, lifecycle stage)
- Capabilities provided (from manifest)
- Value scenarios (features with test status)
- Active change signals (proposals, in-review)
- Recent telemetry summary (usage, health)
- Documentation links (Diataxis quadrants)
- Dependencies (upstream, downstream)

**Example Output:**
```markdown
# chora-platform

**Owner:** Platform Team | **Lifecycle:** Operate | **Stability:** Stable

## Capabilities

- **DRSO Tooling** - CLI commands for development, release, security, operations
- **Telemetry** - Event collection and aggregation
- **Context Bus** - Shared event bus for human/agent awareness
- **Repo Overview** - Auto-generated repository front pages

## Features (Value Scenarios)

- ✅ **VS-PLAT-005**: SBOM generation (6 scenarios, all passing)
- ✅ **VS-PLAT-004**: Coverage reporting (3 scenarios, all passing)
- 🚧 **VS-PLAT-006**: Threat modeling (in progress)

## Active Signals

- **SIG-2025-0015**: Add dependency graph visualization (proposal)

## Telemetry (Last 7 Days)

- 1,247 CLI invocations
- 95.3% success rate
- 12 unique users

## Documentation

- Tutorial: [Getting Started with DRSO](docs/tutorials/first-drso-workflow.md)
- How-to: [Generate SBOM](docs/how-to/generate-sbom.md)
- Reference: [CLI Commands](docs/reference/cli-reference.md)
- Explanation: [DRSO Architecture](docs/explanation/drso-rationale.md)

## Dependencies

- Upstream: None (platform layer)
- Downstream: mcp-orchestration, chora-liminal (17 total consumers)
```

### 2.7 Liminal Capability

**Principle:** Operators may run a personal or shared control capability (`chora-liminal`) that consumes manifests, signals, and telemetry from the platform and composes other Chora capabilities.

**Definition:** "Liminal" = threshold/boundary—the capability sits at the boundary between human and ecosystem, providing personal control over how the ecosystem is experienced.

**Functions:**
- Signal adapters (filter/route change signals to personal preferences)
- Privacy controls (opt-in telemetry, anonymization policies)
- Voice interfaces (speech-to-text for commands, text-to-speech for notifications)
- HUD modules (visual dashboards for ecosystem status)
- Personal automation (scripts triggered by signals/telemetry)

**Architecture:**
```
chora-liminal (personal control)
    ├─ Consumes: chora-platform (manifests, signals, telemetry)
    ├─ Composes: mcp-orchestration (MCP servers)
    └─ Exposes: Voice, HUD, automation APIs
```

**Standards Compliance:**
Liminal capabilities must follow the same standards as other capabilities:
- Publish `star.yaml` manifest
- Provide value scenarios with automated tests
- Respect privacy requirements (document data handling)
- Support offline/air-gapped operation

**Example Use Case:**
```yaml
# .liminal/preferences.yaml
signal_filters:
  - pattern: "SIG-.*-security"
    route: voice_notification
    priority: high
  - pattern: "SIG-.*-documentation"
    route: email_digest
    priority: low

privacy:
  telemetry_opt_in: true
  anonymize_user_id: true
  data_retention_days: 30

voice:
  enabled: true
  wake_word: "hey chora"
  language: en-US
```

### 2.8 Change Signaling

**Principle:** Needs, risks, and proposals flow through a structured channel that captures scope, impact, and resolution status.

**Purpose:** Coordinate cross-project changes with transparency and SLA accountability.

**States:**
```
proposal → review → decision → rollout → closed (or superseded)
```

**Attributes:**
- `id` - Unique identifier (SIG-YYYY-NNNN)
- `title` - Brief description
- `capabilities` - Affected capability IDs
- `state` - Current workflow state
- `priority` - P0 (critical) → P3 (low)
- `impact` - breaking, deprecation, enhancement, bugfix
- `owner` - Originating team/individual
- `stewards` - Responsible for review/approval
- `sla` - Timestamps for acknowledgement, review, decision

**Workflow:** (See Part 4 for detailed process)

**Example:**
```yaml
id: SIG-2025-0012
title: Deprecate legacy MCP registry format
capabilities: ["MCP.REGISTRY.MANAGE"]
state: decision
priority: high
impact: breaking
owner: aurora-mcp-team
stewards: [ecosystem-council]
created_at: 2025-09-29T18:30:00Z
sla:
  acknowledge_by: 2025-10-01T18:30:00Z  # Met
  decide_by: 2025-10-06T18:30:00Z        # Met
decision:
  approved: true
  rationale: Old format lacks security features; migration path provided
```

**Deduplication & Prioritization:**
Signals must include manifest IDs, capability tags, and impact category. Automation groups duplicates and enforces prioritization: security > reliability > functionality > documentation.

**Modular Accountability:**
Every signal identifies the emitting repo's role (platform, capability, server/product, tooling) per 3-layer architecture (ADR-0008).

**Implementation Note:** The DRSO workflow (drso-integrated-intent.md) describes how change signals trigger Change Requests (CRs) that flow through validation gates.

### 2.9 Integration Contracts

**Principle:** Automated checks ensure manifests, behaviors, and runtime interfaces remain compatible as projects evolve.

**Contract Types:**

1. **Manifest Contracts** - Schema validation for star.yaml
   ```bash
   chora-cli validate manifest --schema docs/standards/manifest-schema.json
   ```

2. **Behavior Contracts** - Protocol tests for runtime interfaces
   ```bash
   chora-cli validate behavior --spec docs/capabilities/behaviors/mcp-registry.feature
   ```

3. **Dependency Contracts** - Version compatibility matrices
   ```bash
   chora-cli validate dependencies --matrix docs/reference/compat-matrix.yaml
   ```

**Enforcement:**
- Pre-merge CI checks (GitHub Actions, GitLab CI)
- Automated contract suites run across dependency matrices
- Failures auto-open high-priority change signals
- Release blocked until resolved or waiver granted

**Compatibility Matrix:**
```yaml
# docs/reference/compat-matrix.yaml
providers:
  chora-platform:
    - version: 0.6.0
      compatible_with:
        mcp-orchestration: ">=0.3.0, <0.5.0"
        chora-liminal: ">=0.2.0"

consumers:
  mcp-orchestration:
    - version: 0.4.0
      requires:
        chora-platform: ">=0.6.0, <1.0.0"
```

**Break Detection:**
Automated suites verify:
- Backward compatibility (new version works with old consumers)
- Forward compatibility (old consumers tolerate new providers where possible)

**Waiver Process:** (See Part 6.5)

### 2.10 Security & Compliance

**Principle:** Common baselines for dependency audits, secret handling, logging separation, and release approval.

**Threat Model:**
- **Adversaries:** External attackers, insider threats, supply chain compromise
- **Attack Surfaces:** CLI plugins, manifests, runtime services, observability feeds, dependencies

**Security Baseline:** (See Part 7 for detailed requirements)
- SBOM generation (CycloneDX or SPDX)
- Dependency vulnerability scanning (pip-audit, osv-scanner)
- Secret externalization (no hardcoded credentials)
- Provenance & signing (target: SLSA Level 3)
- Audit logging (≥12 months retention)
- Incident response playbooks

**Threat Model Evolution:**
- Agents draft threat model updates based on change signals and value scenarios
- Humans confirm high-risk decisions
- ADRs capture rationale for future audits

**Compliance Frameworks:**
- NIST SSDF (Secure Software Development Framework)
- OWASP SAMM (Software Assurance Maturity Model)
- SLSA (Supply chain Levels for Software Artifacts)

**Implementation Note:** The DRSO workflow (drso-integrated-intent.md) implements security validation through Gate 3. This ecosystem architecture defines the baseline requirements.

### 2.11 Observability & Feedback

**Principle:** Metrics and qualitative signals reveal which tools are used, which fail, and where to focus investment.

**Event Types:**
- `cli_usage` - Command invocations
- `behavior_validation` - Test execution
- `change_signal_transition` - Signal state changes
- `runtime_invocation` - Service calls
- `incident` - Errors, alerts, failures

**Metrics:**
- Usage counts (invocations per capability, version, user)
- Success rates (pass/fail ratio for behaviors)
- Latencies (command duration, validation duration)
- Adoption (capability usage over time, unique users)

**Trace Context:**
- OpenTelemetry alignment (`trace_id`, `span_id`)
- Change signals carry `correlation_id` across systems
- Distributed tracing (future)

**Retention & Privacy:**
- Operational metrics: 90 days
- Audit logs: ≥12 months
- PII prohibited; anonymize if unavoidable

**Access & Tooling:**
- CLI: `chora-cli inbox` for operational signals
- Dashboards (future): Web UI for metrics visualization
- Exports: JSON/CSV for offline analysis
- RBAC: Role-based access for sensitive telemetry

**Implementation Note:** The DRSO workflow (drso-integrated-intent.md) describes how telemetry flows through Gate 5 (Acknowledgement). This ecosystem architecture defines observability principles.

### 2.12 Modular Boundaries (3-Layer Architecture)

**Principle:** Platform, capability, and workspace repositories carry distinct responsibilities (per ADR-0008).

**Layer 1: Development Workspace (`chora-workspace`)**
- **Role:** Integration lab, DRSO R&D, standards development
- **Contains:** `.drso/` infrastructure, working drafts of standards, integration tests
- **Does NOT contain:** Released capabilities, stable standards (→ Layer 2)
- **DRSO:** Dogfoods DRSO on itself (self-hosting for validation)

**Layer 2: Platform Distribution (`chora-platform`)**
- **Role:** Stable tooling, versioned standards, templates
- **Contains:** `chora_platform_tools`, `chora_cli`, stable docs, templates
- **Published as:** PyPI package `chora-platform>=0.2.0`
- **Does NOT contain:** Development/experimental code, capability implementations

**Layer 3: Capability Repos (`mcp-*`, `chora-*`)**
- **Role:** Self-contained, validated capabilities
- **Contains:** Capability implementation, manifest, tests, evidence
- **Dependencies:** `chora-platform` (as package dependency)
- **Does NOT contain:** Duplicated platform tools, other capabilities

**Flow:** R&D (Layer 1) → Stabilization (Layer 2) → Consumption (Layer 3)

**Responsibility Matrix:**

| Concern | Layer 1 (Workspace) | Layer 2 (Platform) | Layer 3 (Capability) |
|---------|---------------------|---------------------|----------------------|
| **DRSO R&D** | ✓ Develops workflow | Distributes tooling | Consumes tooling |
| **Standards** | ✓ Drafts standards | ✓ Releases standards | Adopts standards |
| **Capabilities** | Integrates (submodules) | Provides examples | ✓ Implements |
| **Validation** | Dogfoods DRSO | Releases via DRSO | Validates via DRSO |
| **Distribution** | Not distributed | ✓ PyPI package | Varies by capability |

**Implementation Note:** The DRSO workflow (drso-integrated-intent.md Part 4) describes detailed DRSO responsibilities for each layer.

---

## Part 3: Manifest Requirements

### 3.1 Minimum Manifest Schema

Every `star.yaml` or `manifests/star.yaml` must include these fields for ecosystem participation:

```yaml
# === IDENTITY ===
id: CAPABILITY.DOMAIN.ACTION  # Globally unique (e.g., MCP.REGISTRY.MANAGE)
version: 0.3.1                # Semantic versioning
owner: team-name              # Accountable team/individual with contact info

# === LIFECYCLE ===
lifecycle_stage: operate      # plan, build, validate, release, operate, retired
stability: stable             # experimental, beta, stable, deprecated

# === INTERFACES ===
inputs:
  - registry_path
  - server_manifest
outputs:
  - registry_state

# === DEPENDENCIES ===
dependencies:
  - chora-platform@>=0.6.0
  - external-service@1.x

# === SECURITY ===
security_tier: moderate       # low, moderate, high, critical
secrets_required:
  - API_KEY                   # Document required secrets (values in .env, not manifest)

# === GOVERNANCE ===
adr_links:
  - docs/reference/architecture/ADR-0008.md

# === VALIDATION ===
# Optional: Include validation status if using DRSO workflow
validation_status:
  last_run: 2025-10-14T12:15:00Z
  passed: true
  # For DRSO specifics, see drso-integrated-intent.md
```

### 3.2 Optional Manifest Extensions

**Features (Value Scenarios):**
```yaml
features:
  - id: mcp.registry.manage.create-doc
    description: Create documentation for MCP servers
    scenarios: 3
    automated_test: tests/value-scenarios/test_create_doc.py
    how_to_guide: docs/how-to/create-doc.md
```

**Discovery Hints:**
```yaml
discovery:
  cli_commands:
    - chora-cli mcp register --help
  mcp_endpoints:
    - protocol: mcp
      url: http://localhost:8080/mcp
  docs:
    - type: tutorial
      url: docs/tutorials/getting-started.md
    - type: reference
      url: docs/reference/api-spec.yaml
```

**Telemetry:**
```yaml
telemetry:
  signals:
    - name: chora.feature.mcp.registry.manage.create_doc
      status: operational
      events_24h: 47
```

**Compatibility:**
```yaml
compatibility:
  backward_compatible_with: ["0.3.0", "0.2.5"]
  breaks_compatibility_with: ["0.1.x"]
  tested_consumers:
    - mcp-orchestration@0.4.0
    - chora-liminal@0.2.1
```

### 3.3 Manifest Validation

**Schema Location:** `docs/standards/manifest-schema.json` (JSON Schema)

**Validation Command:**
```bash
chora-cli validate manifest --schema docs/standards/manifest-schema.json
```

**CI Integration:**
```yaml
# .github/workflows/validate-manifest.yml
- name: Validate manifest
  run: chora-cli validate manifest
```

**Validation Rules:**
- All required fields present
- Valid semantic versions
- Capability IDs follow naming convention (Part 10)
- Secret references exist in `.env.example`
- ADR links resolve to actual files
- Feature test files exist

**Failure Actions:**
- Block PR merge if manifest invalid
- Auto-open change signal for schema violations

### 3.4 Manifest Discovery & Indexing

**Authoritative Location:** Repository root (star.yaml or manifests/star.yaml)

**Central Index (Future):**
- Polls repositories for manifest updates (daily or on webhook)
- Caches manifests for search performance
- Exposes API for discovery queries:
  ```bash
  GET /api/v1/capabilities?lifecycle_stage=operate
  GET /api/v1/capabilities/{id}
  GET /api/v1/capabilities/search?q=sbom
  ```

**Offline Bundles:**
```bash
# Export manifest bundle for air-gapped environments
chora-cli manifest export --bundle manifests.tar.gz --sign

# Import signed bundle
chora-cli manifest import --bundle manifests.tar.gz --verify-signature
```

---

## Part 4: Change Signal Workflow

### 4.1 Workflow States

```
proposal → review → decision → rollout → closed (or superseded)
```

Each state captures timestamps for SLA tracking.

**State Descriptions:**

- **proposal** - Signal created; awaiting acknowledgement
- **review** - Stewards and affected owners assess impact
- **decision** - Approved (create work) or rejected (document rationale)
- **rollout** - Work in progress (e.g., DRSO workflow underway)
- **closed** - Work completed and deployed
- **superseded** - Replaced by newer signal

### 4.2 RACI Matrix

| Role | Responsible | Accountable | Consulted | Informed |
|------|-------------|-------------|-----------|----------|
| **Originator** | Draft signal | - | - | - |
| **Stewards** | - | Review/Approve | - | - |
| **Affected Owners** | - | Implement | - | - |
| **Coordinators** | Track SLAs | - | Provide context | - |
| **Stakeholders** | - | - | - | Receive updates |

### 4.3 SLAs

**Acknowledgement:** 2 business days (signal received → initial response)
- Coordinator acknowledges receipt
- Assigns to appropriate steward(s)
- Sets priority (P0-P3)

**Review:** 5 business days (review started → review concluded)
- Stewards assess impact
- Affected owners consulted
- Documented in signal comments

**Decision:** 2 business days (review concluded → decision recorded)
- Approved: Work assigned, rollout plan created
- Rejected: Rationale documented, originator notified

**Rollout Plan:** Defined before executing (for breaking changes)
- Migration timeline
- Fallback procedures
- Communication strategy

**SLA Breaches:**
- **First breach:** Coordinator sends reminder
- **Second breach (or P0 signal):** Escalate to ecosystem council chair
- **Emergency:** Council chair can convene emergency meeting within 24 hours

### 4.4 Signal Schema

```yaml
# Minimal signal template
id: SIG-YYYY-NNNN
title: Brief description of the change
created_at: 2025-10-14T12:00:00Z
state: proposal
priority: medium          # P0 (critical), P1 (high), P2 (medium), P3 (low)
impact: enhancement       # breaking, deprecation, enhancement, bugfix, documentation
owner: originating-team
stewards: [ecosystem-council]

# Affected capabilities
capabilities:
  - CAPABILITY.ID.1
  - CAPABILITY.ID.2

# SLA tracking
sla:
  acknowledge_by: 2025-10-16T12:00:00Z
  review_conclude_by: 2025-10-21T12:00:00Z
  decide_by: 2025-10-23T12:00:00Z

# Links
manifests:
  - path/to/star.yaml
behaviors:
  - CAPABILITY.BEHAVIOR.ID
adr:
  - ADR-NNNN

# Decision (populated in 'decision' state)
decision:
  approved: true/false
  decision_date: 2025-10-23
  rationale: |
    Detailed explanation of decision
  assigned_to: implementation-team

# Rollout (populated in 'rollout' state)
rollout:
  work_item: CR-2025-10-23-implementation-name
  timeline:
    start: 2025-10-24
    target_completion: 2025-11-15
  migration_plan: docs/migration/SIG-YYYY-NNNN.md

# Closure (populated in 'closed' state)
closed_at: 2025-11-15T10:00:00Z
closed_by: implementation-team
closure_notes: |
  Implementation completed, released in v0.7.0
```

### 4.5 Deduplication & Prioritization

**Deduplication:**
- Automation compares new signals to existing via:
  - Capability IDs (exact match)
  - Title similarity (fuzzy matching)
  - Originator (same team filing similar requests)
- Coordinator reviews suggested duplicates
- Duplicates marked as `superseded` with link to canonical signal

**Prioritization Rules:**
1. **Security** (P0-P1) - Critical vulnerabilities, security patches
2. **Reliability** (P1-P2) - Service outages, data loss risks
3. **Functionality** (P2-P3) - Feature requests, enhancements
4. **Documentation** (P3) - Docs improvements, clarifications

**Impact Category:**
- **breaking** - Incompatible change requiring consumer updates
- **deprecation** - Feature marked for future removal
- **enhancement** - New functionality, backward-compatible
- **bugfix** - Fixes incorrect behavior
- **documentation** - Docs-only change

### 4.6 Publication & Escalation

**Publication:**
- Signals stored in `.drso/signals/` or centralized registry (future)
- State transitions broadcast via:
  - Context bus (future)
  - Email notifications (current)
  - Slack/Discord webhooks (optional)

**Visibility:**
- Dashboards show signal counts by state, priority
- CLI: `chora-cli signals list --state review`
- Repository overviews include active signals

**Escalation Triggers:**
- SLA missed twice
- P0 (critical) signal lacks action within 2 hours
- Dispute between stewards and owners

**Escalation Path:**
1. Coordinator escalates to ecosystem council chair
2. Chair reviews within 1 business day
3. Chair convenes emergency council meeting if needed (within 24 hours)
4. Council decision is binding (appeals process available)

### 4.7 Appeals

**Appeal Triggers:**
- Affected owner disagrees with decision
- Believes impact assessment incorrect
- Alternative solution proposed

**Appeal Process:**
1. Owner files appeal via `chora-cli signals appeal SIG-YYYY-NNNN`
2. Coordinator adds to next council meeting agenda (within 3 business days)
3. Council hears both sides
4. Council votes (simple majority)
5. Decision recorded with dissent notes

**Appeal Outcomes:**
- **Upheld:** Original decision stands
- **Reversed:** New decision recorded, work reassigned
- **Modified:** Decision adjusted based on new information

**Appeals Log:**
All appeals archived with:
- Original decision rationale
- Appeal justification
- Council discussion summary
- Final outcome

---

## Part 5: Governance & Decision Flow

### 5.1 Council Cadence

**Regular Meetings:**
- Bi-weekly synchronous meetings (2 hours)
- Asynchronous voting for non-controversial items (3 business days minimum)
- Emergency meetings for P0 signals (within 24 hours)

**Agenda:**
- Review change signals in 'review' state
- Appeals from previous cycle
- ADR proposals (architectural decisions)
- Standards updates
- Working group reports

**Decision Recording:**
- All decisions documented in meeting notes
- Links to related signals, ADRs, manifests
- Dissent notes captured (minority opinions preserved)
- Action items with owners and due dates

### 5.2 Quorum & Voting

**Quorum:**
- Simple majority of stewards (≥50% + 1)
- Plus representation from affected projects (at least 1 maintainer per affected repo)

**Voting:**
- Simple majority of present stewards
- Tie-breaker: Council chair
- Abstentions counted for quorum, not for majority

**Voting Methods:**
- **Synchronous:** Show of hands in meeting (recorded in notes)
- **Asynchronous:** GitHub/GitLab comment voting (recorded in issue)

**Vote Recording:**
```yaml
# Example decision record
decision_id: DEC-2025-10-23-01
signal: SIG-2025-0012
topic: Deprecate legacy MCP registry format
vote_date: 2025-10-23
quorum_met: true (7/10 stewards present)
votes:
  in_favor: 6
  against: 1
  abstain: 0
outcome: approved
dissent:
  - steward: alice@example.com
    rationale: Migration timeline too aggressive; suggest 6-month extension
action_items:
  - owner: bob@example.com
    action: Create migration guide
    due: 2025-11-01
```

### 5.3 Working Groups

**Purpose:** Temporary groups chartered for focused topics (e.g., security baseline, runtime discovery authentication).

**Charter Requirements:**
- **Deliverables:** What will the group produce?
- **Timeline:** Start and target completion dates
- **Sunset Criteria:** When does the group disband?
- **Participants:** Who is included (open vs. invitation-only)?
- **Decision Authority:** Does the group decide, or recommend to council?

**Example Charter:**
```yaml
working_group_id: WG-2025-10-SECURITY
title: Security Baseline Refresh
created: 2025-10-14
deliverables:
  - Updated threat model (docs/reference/threat-model.md)
  - Revised security baseline (docs/standards/security-baseline.md)
  - SLSA Level 3 roadmap (docs/roadmap/slsa-l3.md)
timeline:
  start: 2025-10-20
  target_completion: 2025-12-15
sunset_criteria:
  - All deliverables published
  - Council approves final recommendations
participants:
  - alice@example.com (security specialist)
  - bob@example.com (platform maintainer)
  - Open to ecosystem contributors (announce via signals)
decision_authority: recommend
  # Working group recommends; council approves
```

**Reporting:**
- Weekly async updates (comment on working group issue)
- Bi-weekly council briefings (5-minute slot)
- Final presentation (30 minutes)

### 5.4 RACI Summary

| Role | Responsible | Accountable | Consulted | Informed |
|------|-------------|-------------|-----------|----------|
| **Stewards** | Maintain standards | Approve breaking changes | - | - |
| **Project Maintainers** | Implement changes | - | - | Change signal updates |
| **Coordinators** | Track SLAs | - | Ensure communication | - |
| **Contributors** | - | - | - | Via signals, docs |
| **Working Groups** | Research/recommend | - | Subject matter experts | - |
| **Council Chair** | Facilitate meetings | Break ties | - | - |

### 5.5 Appeal & Escalation

**Appeal Process:** (See Part 4.7)

**Escalation Triggers:**
- Appeals unresolved within 5 business days
- Disputes between stewards and project maintainers
- P0 signals without action

**Escalation Path:**
1. Council chair review (1 business day)
2. Emergency council meeting if needed (within 24 hours)
3. If unresolved: Escalate to executive sponsor or governance board

**Executive Sponsor:**
- Final authority for unresolvable disputes
- Reviews council decisions on appeal
- Convenes governance board for systemic issues

**Governance Board:**
- Composed of senior leadership from participating organizations
- Meets quarterly (or ad hoc for escalations)
- Sets strategic direction, resolves major disputes
- Approves changes to governance model itself

### 5.6 Decision Log

**Location:** `.drso/decisions/` or centralized registry (future)

**Schema:**
```yaml
decision_id: DEC-YYYY-MM-DD-NN
date: 2025-10-23
type: change_signal_decision  # or: adr_approval, standard_update, working_group_charter
related_items:
  signals: [SIG-2025-0012]
  adrs: [ADR-0010]
  manifests: [chora-platform/star.yaml]
outcome: approved
votes:
  in_favor: 6
  against: 1
  abstain: 0
dissent:
  - steward: alice@example.com
    rationale: Timeline concerns
action_items:
  - owner: bob@example.com
    action: Create migration guide
    due: 2025-11-01
    status: in_progress
```

**Access:**
```bash
chora-cli decisions list --date-range 2025-10-01:2025-10-31
chora-cli decisions show DEC-2025-10-23-01
```

---

## Part 6: Compatibility Policy

### 6.1 Versioning Rules

**Semantic Versioning (semver):**
- `MAJOR.MINOR.PATCH` (e.g., `0.6.2`)
- **MAJOR:** Breaking changes (incompatible API changes)
- **MINOR:** Backward-compatible new features
- **PATCH:** Backward-compatible bug fixes

**Pre-1.0 Warning:**
- Versions `0.x.y` are considered unstable
- MINOR bumps may include breaking changes (documented in changelog)
- Once stable: Bump to `1.0.0`

**Council Approval:**
- MAJOR bumps require council approval + migration plan
- MINOR/PATCH bumps reviewed by maintainers only

### 6.2 Backward/Forward Compatibility

**Backward Compatibility:**
Automated suites verify new version works with previous MAJOR.MINOR consumers.

**Test Approach:**
```bash
# Test chora-platform@0.7.0 with consumers expecting 0.6.x
chora-cli test compatibility --provider chora-platform@0.7.0 --consumers 0.6.x
```

**Forward Compatibility:**
Where possible, older consumers should tolerate newer providers (e.g., ignore unknown manifest fields).

**Compatibility Matrix:**
```yaml
# docs/reference/compat-matrix.yaml
chora-platform:
  0.7.0:
    backward_compatible: [0.6.x]
    forward_compatible: [0.8.x]  # 0.6.x consumers may work with 0.8.x providers
    tested_consumers:
      - mcp-orchestration@0.4.0: pass
      - chora-liminal@0.2.1: pass
```

### 6.3 Grace Periods

**Breaking Changes:**
- Must provide migration plan
- At least **2 release cycles** notice (unless critical security issue)
- Deprecation warnings in previous release

**Migration Plan Requirements:**
- **Timeline:** When will old version stop working?
- **Fallback:** Can users delay migration?
- **Communication:** How will users be notified?
- **Automation:** Can migration be scripted?

**Example:**
```markdown
# Migration Plan: Legacy MCP Registry Format Deprecation

## Timeline
- **v0.7.0 (2025-11-15):** Deprecation warning added
- **v0.8.0 (2026-01-15):** Legacy format still works, warning louder
- **v0.9.0 (2026-03-15):** Legacy format removed

## Fallback
Users can pin to `chora-platform@0.8.x` if they need more time.

## Communication
- Announcement: Change signal SIG-2025-0012
- Docs: Migration guide (docs/migration/legacy-registry.md)
- CLI warning: `chora-cli mcp register` detects old format, prints warning

## Automation
Migration script provided:
```bash
chora-cli mcp migrate-registry --from legacy --to v2
```
```

### 6.4 Automated Break Detection

**Integration Contracts:** (See Part 2.9)

**Smoke Suites:**
Run lightweight tests across dependency matrices:
```bash
chora-cli test smoke --matrix docs/reference/compat-matrix.yaml
```

**Failure Actions:**
- Auto-open high-priority change signal
- Block release until:
  - Incompatibility fixed, OR
  - Waiver granted, OR
  - Affected consumer updated

### 6.5 Waiver Process

**When Needed:**
- Known incompatibility that's acceptable (e.g., consumer plans to update soon)
- Breaking change for critical security fix (no time for grace period)

**Waiver Requirements:**
- **Justification:** Why is incompatibility acceptable?
- **Mitigation:** What steps reduce risk?
- **Owner:** Who is responsible?
- **Expiry Date:** When must issue be resolved?

**Waiver Schema:**
```yaml
waiver_id: WAIVER-2025-10-23-01
type: compatibility_break
related_signal: SIG-2025-0012
justification: |
  mcp-orchestration@0.4.0 has breaking change with chora-platform@0.7.0,
  but mcp-orchestration maintainer confirms v0.4.1 will fix within 2 weeks.
mitigation: |
  - Document incompatibility in release notes
  - Pin chora-platform@0.6.x in mcp-orchestration for now
  - Track mcp-orchestration@0.4.1 release (due 2025-11-06)
owner: alice@example.com
expires: 2025-11-06
status: active  # active, expired, resolved
```

**Expiry Handling:**
- **7 days before expiry:** Automated reminder to owner
- **On expiry:** Waiver status → `expired`
- **After expiry:** Default to enforcement (block incompatible releases)

**Waiver Review:**
Council reviews all active waivers monthly:
- Are they still justified?
- Should they be extended?
- Can they be resolved early?

### 6.6 Deprecation Playbook

**Steps:**
1. **Mark as Deprecated** - Update manifest: `stability: deprecated`
2. **Reference Replacement** - Point to alternative capability
3. **Track Usage** - Monitor telemetry for adopters
4. **Schedule Removal** - Set explicit date (at least 2 release cycles)
5. **Change Signal** - Coordinate decommissioning

**Manifest Update:**
```yaml
id: OLD.CAPABILITY.ID
stability: deprecated
deprecated_since: 0.6.0
deprecated_date: 2025-10-14
replacement: NEW.CAPABILITY.ID
removal_planned: 2026-03-15
removal_version: 0.9.0
```

**Telemetry Tracking:**
```bash
chora-cli telemetry deprecated --capability OLD.CAPABILITY.ID
# Shows: 47 users still using; top 5 consumers listed
```

**Communication:**
- Deprecation notice in release notes
- CLI warning when deprecated capability invoked
- Email to known users (if contact info available)

---

## Part 7: Security Baseline

### 7.1 Threat Model

**Adversaries:**
- **External Attackers** - Exploit vulnerabilities in public-facing services
- **Insider Threats** - Malicious or negligent insiders with access
- **Supply Chain Compromise** - Compromised dependencies or build tooling

**Attack Surfaces:**
- **CLI Plugins** - Malicious code in extensions
- **Manifests** - Malicious manifests with code execution
- **Runtime Services** - Exploitable service endpoints
- **Observability Feeds** - Poisoned telemetry data
- **Dependencies** - Vulnerable or malicious packages

**Threat Scenarios:**
- **Dependency Confusion** - Attacker publishes malicious package with same name
- **Manifest Injection** - Malicious manifest triggers code execution during parsing
- **Credential Harvesting** - CLI plugin exfiltrates environment variables
- **Telemetry Poisoning** - Attacker floods telemetry with fake events
- **Man-in-the-Middle** - Attacker intercepts manifest downloads

### 7.2 Provenance & Signing

**Current State:**
- Git commit signatures (GPG)
- PyPI package checksums (SHA-256)

**Target: SLSA Level 3**
- **Build Provenance:** Cryptographic proof of build inputs/outputs
- **Signing:** Sigstore (Cosign/Fulcio/Rekor) for artifact signing
- **Verification:** Consumers verify signatures before use

**Implementation Roadmap:**
1. Phase 1 (Current): Git commit signatures
2. Phase 2 (Q1 2026): PyPI package signing via Sigstore
3. Phase 3 (Q2 2026): Build provenance attestations
4. Phase 4 (Q3 2026): Full SLSA L3 compliance

**Verification:**
```bash
# Verify signed manifest
chora-cli manifest verify --file star.yaml --signature star.yaml.sig

# Verify signed release artifact
chora-cli release verify --artifact chora-platform-0.7.0.tar.gz
```

### 7.3 SBOM & Vulnerability Gating

**SBOM Requirements:**
- **Format:** CycloneDX (primary), SPDX (future support)
- **Generation:** Automated via `chora-cli drso sbom` (or equivalent)
- **Scope:** All direct and transitive dependencies

**Scanners:**
- **Python:** pip-audit, osv-scanner
- **Multi-language:** osv-scanner, Grype (future)

**Blocking Rules:**
- **Critical CVEs:** Block release (no exceptions)
- **High-severity CVEs:** Block release (waiver required)
- **Medium/low CVEs:** Allow with documentation

**Waiver Process:** (See Part 6.5)

**Example SBOM:**
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "version": 1,
  "metadata": {
    "component": {
      "type": "application",
      "name": "chora-platform",
      "version": "0.7.0"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "pydantic",
      "version": "2.8.2",
      "purl": "pkg:pypi/pydantic@2.8.2",
      "licenses": [{"license": {"id": "MIT"}}]
    }
  ]
}
```

### 7.4 Policy-as-Code (Future)

**Target:** OPA/Conftest for automated policy enforcement

**Policies:**
- **Dependency Policies:** Allowed/blocked package sources, version constraints
- **Secret Policies:** No hardcoded credentials, approved secret managers
- **Runtime Auth:** Required authentication methods per security tier

**Enforcement:**
- Pre-merge CI checks
- DRSO gate validation (see drso-integrated-intent.md Gate 3)
- Runtime admission control (future)

**Example Policy (OPA Rego):**
```rego
# deny_hardcoded_secrets.rego
package security

deny[msg] {
  input.file_content =~ "password\\s*=\\s*['\"]"
  msg := sprintf("Hardcoded password found in %s", [input.file_path])
}
```

### 7.5 Secret Handling

**Secret Tiers:**
- **Developer:** Local `.env` file (not committed)
- **Project:** Repository secrets (GitHub/GitLab)
- **Shared:** Organization secrets (centralized vault)

**Manifest Declaration:**
```yaml
secrets_required:
  - name: API_KEY
    tier: project
    purpose: External service authentication
    documented: .env.example
```

**Best Practices:**
- **Just-in-time Issuance:** Request secrets only when needed
- **Never Embed:** No secrets in code, manifests, or logs
- **Rotation:** Secrets rotated regularly (automated where possible)
- **Scope Minimization:** Secrets scoped to smallest necessary access

**Validation:**
```bash
# Check for hardcoded secrets (via bandit or custom scanner)
chora-cli security scan-secrets --dir src/
```

### 7.6 Service Identity & Auth

**Current:**
- **API Keys:** Externalized to environment variables
- **Token-based:** Short-lived tokens where supported

**Target:**
- **Workload Identities:** OIDC (cloud-native), SPIFFE (on-prem)
- **Mutual TLS:** Service-to-service auth
- **Deprecate Static Tokens:** Phase out in favor of dynamic credentials

**Security Tier Mapping:**
| Tier | Auth Method | Example |
|------|-------------|---------|
| **Low** | API keys (env vars) | Internal dev tools |
| **Moderate** | Short-lived tokens | Public APIs |
| **High** | Mutual TLS | Financial services |
| **Critical** | Workload identities + MFA | Healthcare, PII handling |

### 7.7 Audit & Logging

**Retention:**
- **Operational Logs:** 90 days
- **Audit Logs:** ≥12 months
- **Compliance Logs:** Per regulatory requirements (GDPR, HIPAA, etc.)

**Logged Events:**
- CLI usage (command, user, timestamp)
- Manifest changes (who, what, when)
- Change signal transitions (state changes)
- Runtime access (service calls, authentication)
- Security events (failed logins, policy violations)

**Access Control:**
- RBAC for log access
- Read-only for most users
- Write access only to logging infrastructure
- Audit log access itself logged

**Log Format (Structured JSON):**
```json
{
  "timestamp": "2025-10-14T12:00:00Z",
  "event_type": "cli_usage",
  "user_id": "alice@example.com",
  "command": "chora-cli drso sbom",
  "repo": "chora-workspace",
  "result": "success",
  "trace_id": "abc123"
}
```

### 7.8 Incident Response

**Playbooks:**
Map capabilities to response owners:
```yaml
# docs/security/incident-response-playbook.yaml
capabilities:
  MCP.REGISTRY.MANAGE:
    owner: aurora-mcp-team
    on_call: +1-555-0100
    escalation: security-team@example.com
    runbook: docs/security/runbooks/mcp-registry-incident.md
```

**Drills:**
- **Frequency:** Quarterly (recommended)
- **Scope:** Tabletop exercises, simulated incidents
- **Documentation:** Capture lessons learned in retrospectives

**Lessons Learned:**
- Documented in ADRs or retrospective docs
- Action items tracked via change signals
- Updates to playbooks/runbooks

**Incident Workflow:**
1. **Detection:** Alert triggered (monitoring, user report)
2. **Triage:** On-call responds, assesses severity
3. **Escalation:** High-severity → security team, council
4. **Mitigation:** Fix deployed, patch released
5. **Postmortem:** Root cause analysis, lessons learned
6. **Follow-up:** Action items tracked to completion

---

## Part 8: Discovery Expectations

### 8.1 Architecture

**Hybrid Approach:**
- **Authoritative Manifests:** Stay with owning repositories (star.yaml)
- **Central Index:** Mirrors metadata for search/caching (future)
- **APIs:** Documented interfaces for programmatic discovery

**Benefits:**
- **Decentralization:** No single point of failure
- **Performance:** Cached index for fast queries
- **Flexibility:** Projects can self-publish without central approval

**Tradeoffs:**
- **Staleness:** Index may lag behind repo changes (mitigated by TTL)
- **Coordination:** Index must poll or receive webhooks
- **Offline:** Requires bundle export/import for air-gapped environments

### 8.2 Location & Distribution

**Manifest Location:**
- **Required:** `star.yaml` or `manifests/star.yaml` in repo root
- **Required:** Manifest in GitHub/GitLab release artifacts
- **Optional:** HTTPS endpoint for runtime discovery (e.g., `https://example.com/.well-known/chora-manifest.yaml`)

**Release Artifacts:**
Include manifest in every release:
```bash
gh release create v0.7.0 \
  --files "star.yaml,sbom.json,coverage-report.html"
```

**HTTPS Discovery (Optional):**
```yaml
# Served at https://example.com/.well-known/chora-manifest.yaml
# Allows runtime discovery without cloning repo
```

### 8.3 Cache & Refresh

**Index Refresh:**
- **Cadence:** Daily (configurable)
- **Trigger:** Git tag webhook (push), scheduled poll (pull)
- **Protocol:** ETag/If-Modified-Since for efficiency

**Manifest TTL:**
```yaml
# star.yaml
updated_at: 2025-10-14T12:00:00Z
ttl: 86400  # 24 hours in seconds
```

**Client Behavior:**
- Warn when TTL exceeded
- Re-fetch from authoritative source
- Fallback to cached version if authoritative unavailable

**Staleness Detection:**
- Compare `updated_at` vs. latest git tag timestamp
- Flag manifests >7 days stale
- Emit change signal if >30 days stale

### 8.4 Authentication & Authorization

**Index Queries:**
- Default: SSO-authenticated users
- API keys for automation (scoped, rotated)
- Public read for non-sensitive capabilities

**Security Tiers:**
- **Low:** Public discovery
- **Moderate:** Authenticated discovery
- **High/Critical:** RBAC-controlled discovery (only approved users)

**Access Events:**
- All index queries logged (user, query, timestamp)
- Audit trail for sensitive capability discovery

### 8.5 Staleness Detection

**Staleness Indicators:**
- `updated_at` timestamp vs. latest git tag
- `validation_status.last_run` vs. current date
- TTL expiration

**Automated Actions:**
- **7 days stale:** Warn in index results
- **30 days stale:** Open change signal for maintainer
- **90 days stale:** Mark as potentially unmaintained

**Staleness Query:**
```bash
chora-cli discovery stale --threshold 30
# Lists capabilities not updated in 30+ days
```

### 8.6 Offline / Air-Gapped Operation

**Bundle Export:**
```bash
chora-cli manifest export --bundle manifests.tar.gz --sign
```

**Bundle Contents:**
- All manifests from indexed capabilities
- SBOMs
- Behaviors (BDD specs)
- Signatures (Sigstore or GPG)
- Checksum file

**Bundle Import:**
```bash
chora-cli manifest import --bundle manifests.tar.gz --verify-signature
```

**Sync Policies:**
- Require signature verification
- Require checksum match
- Approval step before import (for high-security environments)

**Telemetry Backfill:**
- Offline environments queue telemetry events locally
- Replay when connectivity restored
- Preserve `correlation_id` for traceability

### 8.7 Capability Catalog

**Generation:**
```bash
chora-cli discovery catalog --output docs/capabilities/index.md
```

**Content:**
```markdown
# Capability Catalog

## MCP.REGISTRY.MANAGE

**Owner:** aurora-mcp-team
**Lifecycle:** Operate | **Stability:** Stable

**Description:** Manage MCP server registrations and metadata

**Features:**
- Register new MCP servers
- Validate server manifests
- Query registered servers

**Dependencies:**
- chora-platform@>=0.6.0

**Documentation:**
- Tutorial: [Getting Started](docs/tutorials/mcp-registry.md)
- How-to: [Register Server](docs/how-to/register-server.md)
- Reference: [API Spec](docs/reference/mcp-registry-api.yaml)

**Telemetry (Last 7 Days):**
- 234 registrations
- 98.7% success rate
```

### 8.8 Value Scenario Catalog

**Generation:**
```bash
chora-cli discovery scenarios --output docs/capabilities/scenarios.md
```

**Content:**
```markdown
# Value Scenario Catalog

## VS-PLAT-005: SBOM Generation

**Capability:** chora-platform
**Scenarios:** 6
**Status:** ✅ All passing

**Scenarios:**
1. Generate SBOM in CycloneDX format
2. Validate SBOM structure
3. Verify all dependencies catalogued
4. Scan SBOM for vulnerabilities
5. Check license compliance
6. Validate version accuracy

**Automated Tests:** `tests/value-scenarios/test_VS_PLAT_005_sbom.py`
**How-to Guide:** [Generate SBOM](docs/how-to/generate-sbom.md)
**Tutorial:** [First SBOM](docs/tutorials/first-sbom.md)

**Last Validated:** 2025-10-14T12:15:00Z
```

### 8.9 Context Bus (Future)

**Purpose:** Shared event bus for human dialogue, automation prompts, telemetry, and change signals.

**Benefits:**
- Humans and agents maintain same situational awareness
- No manual restatement of context
- Audit trail for decisions
- Real-time coordination

**Event Types:**
- Human dialogue (chat messages, voice commands)
- Automation prompts (agent requests, tool invocations)
- Telemetry events (CLI usage, runtime invocations)
- Change signals (state transitions)

**Architecture:**
```
Context Bus (message queue)
    ├─ Publishers: Humans, agents, services, gates
    ├─ Subscribers: Dashboards, notifications, logs
    └─ Storage: Event log (append-only, tamper-evident)
```

**Example Event:**
```json
{
  "timestamp": "2025-10-14T12:00:00Z",
  "event_type": "change_signal_transition",
  "signal_id": "SIG-2025-0012",
  "from_state": "review",
  "to_state": "decision",
  "actor": "alice@example.com",
  "context": {
    "decision": "approved",
    "rationale": "Migration plan adequate"
  },
  "trace_id": "abc123"
}
```

---

## Part 9: Observability Requirements

### 9.1 Events

**Required Event Types:**
- `cli_usage` - CLI command invocations
- `behavior_validation` - Test execution results
- `change_signal_transition` - Signal state changes
- `runtime_invocation` - Service calls (for runtime capabilities)
- `incident` - Errors, alerts, failures

**Event Schema (Minimal):**
```json
{
  "timestamp": "2025-10-14T12:00:00Z",
  "event_type": "cli_usage",
  "capability_id": "chora.platform.drso.sbom",
  "version": "0.6.0",
  "user_id": "victor.piper@example.com",
  "status": "success",
  "duration_ms": 1234,
  "trace_id": "abc123",
  "metadata": {
    "repo": "chora-workspace",
    "components": 47
  }
}
```

**Storage:**
- Local: `var/telemetry/events.jsonl` (JSONL format, one event per line)
- Centralized (future): Event aggregation service

### 9.2 Metrics

**Required Metrics:**
- **Usage Counts:** Invocations per capability, version, user
- **Success Rates:** Pass/fail ratio for behaviors
- **Latencies:** Command duration (p50, p95, p99)
- **Adoption:** Capability usage over time, unique users

**Aggregation:**
- Daily rollups for trend analysis
- Weekly summaries for reports
- Monthly dashboards for governance

**Metrics API (Future):**
```bash
GET /api/v1/metrics/usage?capability=chora.platform.drso.sbom&range=7d
GET /api/v1/metrics/success-rate?capability_id=*&range=30d
```

### 9.3 Trace Context

**OpenTelemetry Alignment:**
- `trace_id` - Unique ID for entire workflow
- `span_id` - Unique ID for individual operation
- `parent_span_id` - Link to parent operation

**Correlation:**
- Change signals carry `correlation_id` across systems
- Telemetry events reference `signal_id` when applicable
- Allows tracing from signal → work → release → operations

**Example:**
```json
{
  "trace_id": "abc123",
  "span_id": "def456",
  "parent_span_id": "ghi789",
  "signal_id": "SIG-2025-0012",
  "correlation_id": "cor-2025-0012-workflow"
}
```

### 9.4 Retention & Privacy

**Retention:**
- **Operational Metrics:** 90 days
- **Audit Logs:** ≥12 months
- **Compliance Logs:** Per regulatory requirements

**Privacy:**
- **PII Prohibited:** Do not log email addresses, names (use anonymized IDs)
- **Anonymization:** Hash user IDs before storage (where PII unavoidable)
- **Documentation:** Privacy policy documents data handling

**Data Handling:**
```yaml
# Privacy policy (docs/privacy/telemetry-policy.md)
pii_handling:
  email: hashed_with_salt
  user_id: hashed_with_salt
  ip_address: not_collected
retention:
  operational: 90_days
  audit: 12_months
opt_out:
  available: true
  method: Set CHORA_TELEMETRY_OPT_OUT=1
```

### 9.5 Access & Tooling

**CLI:**
```bash
chora-cli inbox                          # Show operational signals
chora-cli metrics usage --range 7d       # Usage stats
chora-cli metrics success-rate --range 30d  # Success rates
```

**Dashboards (Future):**
- Web UI for metrics visualization
- Real-time signal tracking
- Capability health overview

**Exports:**
```bash
chora-cli telemetry export --format json --range 30d --output metrics.json
chora-cli telemetry export --format csv --range 90d --output metrics.csv
```

**RBAC:**
- **Read:** All authenticated users (for public capabilities)
- **Write:** Only logging infrastructure
- **Admin:** Coordinators, stewards (for sensitive telemetry)

---

## Part 10: Standards Alignment

Leverage existing standards to reduce custom tooling and vendor lock-in:

### 10.1 Service Interfaces

**OpenAPI / AsyncAPI:**
- Document REST APIs via OpenAPI 3.x
- Document event-driven APIs via AsyncAPI 2.x
- Generate client SDKs from specs
- Validate requests/responses in integration contracts

**Example:**
```yaml
# docs/reference/api/mcp-registry-api.yaml (OpenAPI)
openapi: 3.0.0
info:
  title: MCP Registry API
  version: 0.3.1
paths:
  /servers:
    post:
      summary: Register MCP server
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ServerManifest'
```

### 10.2 SBOMs

**CycloneDX (Primary):**
- Widely supported (GitHub, GitLab, Snyk, etc.)
- Rich metadata (licenses, vulnerabilities, dependencies)
- Python tools: `cyclonedx-py`

**SPDX (Future Support):**
- Linux Foundation standard
- Broader ecosystem adoption
- Python tools: `spdx-tools`

**Validation:**
```bash
# Validate against CycloneDX schema
chora-cli sbom validate --file sbom.json --spec cyclonedx-1.6
```

### 10.3 Security Maturity

**NIST SSDF (Secure Software Development Framework):**
- Guidance for secure development practices
- Maps to DRSO workflow (see drso-integrated-intent.md)

**OWASP SAMM (Software Assurance Maturity Model):**
- Maturity levels for security practices
- Self-assessment questionnaire
- Roadmap for improvement

**Benchmarking:**
```bash
chora-cli security benchmark --framework nist-ssdf
# Outputs: Maturity level, gaps, recommendations
```

### 10.4 Observability

**OpenTelemetry:**
- Standard for metrics, traces, logs
- Language-agnostic instrumentation
- Vendor-neutral backends (Prometheus, Jaeger, etc.)

**Instrumentation:**
```python
# Example: OpenTelemetry instrumentation in chora-cli
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("chora-cli-sbom"):
    generate_sbom(repo_path, output_path)
```

### 10.5 Behavior Specs

**Gherkin / Cucumber:**
- BDD standard for behavior specifications
- Human-readable, automation-friendly
- Tools: pytest-bdd, behave

**Example:**
```gherkin
# docs/capabilities/behaviors/mcp-registry.feature
@capability:MCP.REGISTRY.MANAGE
Feature: MCP Server Registration

  Scenario: Register new server
    Given a valid server manifest
    When I run `chora-cli mcp register --manifest server.yaml`
    Then the server is registered in the index
    And I can query it via `chora-cli discovery list`
```

### 10.6 Change Management

**ITIL / DevOps:**
- Borrow concepts where beneficial (change approval, rollback)
- Automate wherever possible (no manual change boards)

**Alignment:**
- Change signals = ITIL "Request for Change"
- SLAs = ITIL "Service Level Agreements"
- Appeals = ITIL "Change Advisory Board escalation"

---

## Part 11: Adoption & Success

### 11.1 Anti-Goals

DRSO explicitly does NOT aim to:

- ❌ **Mandate monorepo** - Projects remain independent repositories
- ❌ **Force technology stacks** - Language/framework choice remains with projects
- ❌ **Centralize decision making** - Projects retain autonomy within standards
- ❌ **Replace project governance** - Ecosystem augments, not replaces, existing processes
- ❌ **Build proprietary tooling** - Leverage open standards (OpenTelemetry, CycloneDX, Gherkin, etc.)
- ❌ **Require "big bang" adoption** - Progressive pathway allows incremental value
- ❌ **Create bureaucracy** - Automation reduces overhead; SLAs prevent delays

### 11.2 Constraints & Non-Goals

**Autonomy:**
Projects retain independent roadmaps; ecosystem guidelines enable but do not monopolize decision making.

**Incremental Adoption:**
New capabilities must be adoptable piecewise. Avoid all-or-nothing migrations.

**Tool Diversity:**
The ecosystem supports multiple languages or frameworks; specifications focus on interfaces, not implementation detail.

**Minimal Bureaucracy:**
Coordination mechanisms should minimize overhead while ensuring traceability of major decisions.

### 11.3 Adoption Pathways

Projects can adopt ecosystem participation incrementally:

#### Phase 1: Documentation Alignment

**Goal:** Map existing workflows to ecosystem vocabulary

**Actions:**
1. Create `star.yaml` manifest with minimum required fields
2. Map current stages to ecosystem lifecycle (plan, build, validate, release, operate)
3. Identify existing capabilities (user-facing features)
4. Document current validation practices

**Acceptance:**
- ✓ Manifest includes minimum fields (Part 3)
- ✓ Lifecycle mapping reviewed by maintainers
- ✓ Capabilities catalogued (at least high-level list)

**Duration:** 1-2 weeks

**Benefit:** Visibility into ecosystem without changing current practices

---

#### Phase 2: Validation Integration

**Goal:** Adopt shared validation (integration contracts) alongside existing tests

**Actions:**
1. Install chora-platform: `pip install chora-platform>=0.6.0`
2. Define integration contracts (manifest schema, behavior specs)
3. Add contract validation to CI/CD
4. Include validation results in manifest (`validation_status`)

**Acceptance:**
- ✓ CI includes contract suite
- ✓ Build fails on contract violations (or with waivers)
- ✓ Validation status in manifest

**Duration:** 2-4 weeks

**Benefit:** Automated quality/security validation without rewriting tests

---

#### Phase 3: Coordination Participation

**Goal:** Emit and respond to change signals

**Actions:**
1. Subscribe to ecosystem change signal notifications
2. Emit change signals for breaking changes
3. Respond to signals from dependencies
4. Track SLA compliance

**Acceptance:**
- ✓ Change signals follow standardized workflow (Part 4)
- ✓ SLA compliance tracked
- ✓ At least one signal processed (emitted or responded)

**Duration:** 1-2 months

**Benefit:** Coordinated change across ecosystem, early warning of breaking changes

---

#### Phase 4: Runtime Interoperability (Optional)

**Goal:** Expose runtime discovery metadata for service-based capabilities

**Actions:**
1. Add `discovery` section to manifest (CLI commands, MCP endpoints)
2. Expose health check endpoints
3. Publish runtime telemetry
4. Validate compatibility with dependent projects

**Acceptance:**
- ✓ At least one dependent project successfully consumes runtime metadata
- ✓ Compatibility checks automated in CI
- ✓ Runtime health monitored

**Duration:** 2-4 months

**Benefit:** Dynamic service discovery, runtime interoperability

---

### 11.4 Success Criteria (Qualitative)

The ecosystem succeeds when:

**For New Contributors:**
- Orient within hours using generated documentation and manifests
- Understand capability discovery through catalog and tutorials
- Can query "who provides X?" via CLI

**For Cross-Project Changes:**
- Changes are anticipated and coordinated (change signals surface early)
- Surprise breakages eliminated (integration contracts catch incompatibilities)
- Rollout plans documented and followed

**For Automation:**
- Lifecycle tasks run without bespoke scripts per repository
- Manifests provide enough metadata for agent navigation
- Telemetry flows to centralized observability (future)

**For Runtime Consumers:**
- Connect to services using standard discovery information
- Compatibility checks prevent breaking changes
- Runtime metadata accurate and up-to-date

**For Governance:**
- Decisions, standards, compatibility matrices accessible and current
- ADRs trace rationale for architectural choices
- Change signals archived with outcomes

### 11.5 Success Metrics (Illustrative)

To evaluate whether intent is being realized:

**Routing Latency:**
- **Metric:** Time from change signal creation to owner identification
- **Baseline:** Measure current average
- **Target:** 50% reduction within 2 release cycles

**Metadata Coverage:**
- **Metric:** % of capabilities with up-to-date manifests and passing validation
- **Baseline:** Existing coverage (if any)
- **Target:** ≥90% within 1 release cycle

**Cross-Project Incidents:**
- **Metric:** Count of incompatibilities causing breakage
- **Baseline:** Establish quarterly baseline
- **Target:** <1 major incident per quarter

**Integration Time:**
- **Metric:** Mean time to integrate a new project into ecosystem
- **Baseline:** Measure first adopter
- **Target:** <2 weeks once tooling available

**Runtime Discovery Adoption:**
- **Metric:** Fraction of services exposing standardized endpoints
- **Baseline:** 0% (new capability)
- **Target:** 60% by end of Phase 4 adoption

### 11.6 Ecosystem Interactions

Three recurring interaction loops ground the intent:

**Plan-to-Build Loop:**
A change request surfaces (human or agent) → Consult capability discovery to determine if existing functionality satisfies → If not, draft new behaviors and manifests → Create traceable work items.

**Build-to-Validate Loop:**
Implementations publish updated metadata → Execute shared validation suites → Integration contracts flag incompatibilities early across project graph.

**Release-to-Operate Loop:**
Runtime assets register themselves for discovery → Operational tooling monitors health → Observations feed back into planning.

These loops overlap; short feedback cycles reduce systemic risk and keep metadata synchronized with reality.

### 11.7 Quality Attributes

The ecosystem must exhibit these qualities independent of technical stack:

**Reliability:**
Shared tooling continues to function when individual projects change. Version negotiation and graceful degradation required.

**Scalability:**
Adding new projects or capabilities does not exponentially increase coordination costs. Metadata and automation scale with constellation count.

**Observability:**
Operators can inspect state (who provides what, which behaviors pass, which signals unresolved) without manual spelunking.

**Security & Privacy:**
Secrets remain scoped, logs respect boundaries, third-party contributions cannot subvert shared tooling.

**Extensibility:**
New lifecycle stages or artifact types can be introduced without rewiring the ecosystem. Interfaces focus on contracts rather than implementations.

---

## Part 12: Open Questions & Future Work

### 12.1 Governance Cadence

**Question:** What governance cadence balances responsiveness with workload?

**Options:**
- Bi-weekly council meetings with asynchronous voting (current proposal)
- Weekly sync meetings for active change signals
- Fully asynchronous with SLA-driven escalation

**Considerations:**
- Need emergency path for P0 signals
- Avoid meeting fatigue
- Ensure decisions documented regardless of sync/async

### 12.2 Runtime Discovery Authentication

**Question:** How should runtime discovery authenticate services in multi-tenant or remote scenarios?

**Options:**
- OIDC workload identities (preferred for cloud-native)
- Mutual TLS (preferred for on-prem/air-gapped)
- API keys (current, simple but less secure)

**Considerations:**
- Security tier (high/critical services require stronger auth)
- Operational complexity (key rotation, certificate management)
- Compatibility with existing infrastructure

### 12.3 Minimum Metadata for Humans and Agents

**Question:** What minimum metadata should manifests expose to satisfy both human and agent needs?

**Current Minimum (Part 3):**
id, version, owner, lifecycle_stage, stability, inputs, outputs, dependencies, security_tier, adr_links, validation_status

**Agent-Specific Needs:**
- `discovery.cli_commands` - How to invoke capability
- `discovery.mcp_endpoints` - Runtime service endpoints
- `discovery.docs` - Documentation links for learning
- `features` - User-testable scenarios

**Human-Specific Needs:**
- `description` - Plain-language explanation
- `how_to_links` - Getting started guides
- `tutorial_links` - Onboarding walkthroughs

**Proposal:** Extend current minimum with `discovery` and `features` sections (as shown in Part 3.2)

### 12.4 Central vs. Distributed Artifacts

**Question:** Which artifacts belong in a central repository versus remaining in individual projects?

**Current Model:**
- **Central (chora-workspace):** DRSO infrastructure, standards (working drafts), integration tests
- **Central (chora-platform):** Stable tools, released standards, templates
- **Distributed (capability repos):** Capability implementations, manifests, tests, evidence

**Proposed Additions:**
- **Central:** Discovery index (aggregated manifests)
- **Central:** Capability catalog (aggregated capabilities/scenarios)
- **Central:** Change signal registry (all signals)
- **Distributed:** Validation evidence (stays with repo for auditability)

### 12.5 Offline/Air-Gapped Feedback Loops

**Question:** How will feedback loops function when some projects operate in offline or restricted environments?

**Challenges:**
- Telemetry cannot stream to central observability
- Change signals cannot propagate in real-time
- Manifest updates lag behind online ecosystem

**Solutions:**
- **Bundle Export/Import:** Offline environments export telemetry bundles periodically
- **Queued Sync:** Events queued locally, replayed when connectivity restored
- **Correlation IDs:** Maintain trace IDs across sync boundaries
- **Signed Bundles:** Verify integrity when importing manifests/signals

### 12.6 Escalation for Urgent Local Changes

**Question:** What escalation path exists when shared standards block urgent local changes?

**Scenario:** Critical security patch needed immediately, but ecosystem policy blocks release due to breaking change.

**Proposed Escalation Path:**
1. **Emergency Waiver:** Maintainer documents justification, mitigation, expiry (Part 6.5)
2. **Immediate Deploy:** Deploy with waiver, bypass normal approval
3. **Post-Deployment Review:** Escalate to council within 24 hours
4. **Retrospective:** Document lessons learned, update standards if needed

---

## Part 13: Naming Guidelines

### 13.1 Repository Naming

- **Platform/Shared:** `chora-<domain>` (e.g., `chora-platform`, `chora-workspace`)
- **Capabilities:** `<domain>-<capability>` (e.g., `mcp-orchestration`, `chora-liminal`)
- **Product Bundles:** `<domain>-<product>` (e.g., `mcp-n8n` bundles MCP + n8n workflows)

### 13.2 Capability IDs

**Format:** `<domain>.<capability>.<action>`

**Examples:**
- `mcp.registry.manage`
- `chora.platform.telemetry.aggregate`
- `chora.liminal.voice.transcribe`

**Versioning:** Add suffix if multiple versions coexist: `mcp.registry.manage.v2`

### 13.3 Change Signal IDs

**Format:** `SIG-<YYYY>-<NNNN>` (sequential) OR `SIG.<scope>.<subject>` (descriptive)

**Examples:**
- `SIG-2025-0012` (sequential)
- `SIG.capability.mcp.registry.update` (descriptive)

**File Location:** `.drso/signals/` or centralized registry (future)

### 13.4 Documentation Paths

**Diataxis-Aligned:**
- **Explanation:** `docs/explanation/<topic>.md`
- **Reference:** `docs/reference/<topic>.md`
- **How-to:** `docs/how-to/<task>.md`
- **Tutorial:** `docs/tutorials/<walkthrough>.md`

**Ecosystem-Specific:**
- **ADRs:** `docs/reference/architecture/ADR-<NNNN>-<title>.md`
- **Standards:** `docs/standards/<standard-name>.md`
- **Manifests:** `star.yaml` or `manifests/star.yaml`

### 13.5 Templates & Workflows

**Templates:**
- **CI Workflows:** `.github/workflows/chora-ci.yml`
- **Manifest Template:** `.chora/templates/star.yaml`
- **AGENTS Snippets:** `docs/templates/agents/<snippet>.yaml`

**Naming Consistency:**
Changes to naming conventions should be recorded through change signals to maintain consistency across projects.

---

## Appendix A: Relationship to DRSO Workflow

This ecosystem intent document is **complementary** to the [DRSO-Integrated Intent](drso-integrated-intent.md). Here's how they relate:

### Ecosystem Intent (This Document)

**Focus:** What the ecosystem provides (architecture, not workflow)

**Covers:**
- Capability discovery (how to find capabilities)
- Manifests (how to describe capabilities)
- Change signals (how to coordinate changes)
- Governance (how to make decisions)
- Security baseline (what security requirements exist)
- Observability (what telemetry is needed)
- Standards (what external standards to align with)

**Does NOT Cover:**
- How to develop code (→ DRSO Intent)
- How to validate releases (→ DRSO Intent)
- Gate-specific requirements (→ DRSO Intent)
- Artifact flow through workflow (→ DRSO Intent)

### DRSO Intent (drso-integrated-intent.md)

**Focus:** How to develop, release, secure, and operate capabilities

**Covers:**
- 4-phase DRSO lifecycle (Development → Release → Security → Operations)
- 5 validation gates (Status, Coverage, Security, Release, Acknowledgement)
- Artifact lifecycle (ADR → CR → Feature → Code → Release)
- Documentation-Driven Design (Diataxis → Gate mapping)
- End-to-end release process (13 steps)
- Virtuous cycles (self-validation patterns)

**References Ecosystem Intent For:**
- Manifest schema (Part 3)
- Change signal structure (Part 4)
- Governance processes (Part 5)
- Security baseline (Part 7)
- Discovery expectations (Part 8)

### Use Together

**Scenario:** Implementing a new capability

1. **Ecosystem Intent:** Defines what manifest fields are required (Part 3)
2. **DRSO Intent:** Defines how to validate the manifest (Gate 4)
3. **Ecosystem Intent:** Defines change signal workflow (Part 4)
4. **DRSO Intent:** Defines how change signals trigger Change Requests (Part 5)
5. **Ecosystem Intent:** Defines security baseline requirements (Part 7)
6. **DRSO Intent:** Defines how to validate security (Gate 3)

**Both documents** are necessary for a complete understanding of the Chora ecosystem.

---

## Appendix B: Glossary of Terms

**Capability** - A unit of value exposed to ecosystem participants (e.g., "MCP server orchestration"). Traceable through manifests, features, and telemetry.

**Manifest (star.yaml)** - Machine-readable metadata describing repository capabilities, interfaces, dependencies, lifecycle state, and ownership. Required for discovery.

**Change Signal** - Structured notification that a capability, contract, or dependency needs attention. Drives coordination across teams. States: proposal → review → decision → rollout → closed.

**Integration Contract** - Automated checks enforcing compatibility across project boundaries. Schema validation, protocol tests, compatibility matrices.

**Behavior** - Verified specification (BDD scenario) proving a capability functions as intended. Implemented as automated test.

**Value Scenario** - User-testable capability with manual and automated verification paths. Also called "Feature" in BDD terminology (see ADR-0009).

**Lifecycle Stage** - Current phase in capability development: plan, build, validate, release, operate, retired.

**Security Tier** - Classification indicating sensitivity: low, moderate, high, critical. Determines required security controls.

**Stability** - Qualitative status: experimental, beta, stable, deprecated. Indicates maturity and change risk.

**Discovery** - Process of finding capabilities via manifests and central index. Supports queries like "who provides X?"

**Context Bus** - Shared event bus for human dialogue, automation prompts, telemetry, and change signals. Maintains shared situational awareness.

**Liminal Capability** - Personal control capability (chora-liminal) that sits at boundary between human and ecosystem, providing voice, HUD, privacy controls.

**3-Layer Architecture** - Separation: workspace (R&D) → platform (distribution) → capabilities (consumption). See ADR-0008.

**For DRSO-Specific Terms:** See [DRSO-Integrated Intent Glossary](drso-integrated-intent.md#72-glossary-drso-aligned)

---

## Appendix C: References

### Related Documents

- **DRSO-Integrated Intent:** [docs/ecosystem/drso-integrated-intent.md](drso-integrated-intent.md) - Development workflow implementation
- **ADR-0008:** [Modularization Boundaries](../reference/architecture/ADR-0008-modularization-boundaries.md) - 3-layer architecture
- **ADR-0009:** [DRSO-BDD Terminology Alignment](../reference/architecture/ADR-0009-drso-bdd-terminology-alignment.md) - Feature/Scenario terminology
- **Architecture Integration Map:** [docs/reference/architecture-integration-map.md](../reference/architecture-integration-map.md) - Artifact traceability

### External Standards

- **Diataxis Framework:** https://diataxis.fr/ - Documentation structure
- **OpenAPI:** https://spec.openapis.org/ - REST API specification
- **AsyncAPI:** https://www.asyncapi.com/ - Event-driven API specification
- **CycloneDX:** https://cyclonedx.org/ - SBOM format (primary)
- **SPDX:** https://spdx.dev/ - SBOM format (future support)
- **OpenTelemetry:** https://opentelemetry.io/ - Observability standard
- **SLSA:** https://slsa.dev/ - Supply chain security framework
- **Sigstore:** https://www.sigstore.dev/ - Artifact signing
- **NIST SSDF:** https://csrc.nist.gov/projects/ssdf - Secure software development
- **OWASP SAMM:** https://owaspsamm.org/ - Security maturity model
- **Gherkin/Cucumber:** https://cucumber.io/docs/gherkin/ - BDD specification

### Example Implementations

- **chora-platform manifest:** [chora-platform/star.yaml](../../chora-platform/star.yaml)
- **Change signal example:** [.drso/signals/](../../.drso/signals/) (future)
- **Capability catalog:** [docs/capabilities/](../capabilities/) (generated)

---

**END OF DOCUMENT**

**Document ID:** ECOSYSTEM-INT-2025-10-14
**Version:** 2.0.0
**Status:** Draft
**Last Updated:** 2025-10-14
**Supersedes:** solution-neutral-intent.md (v0.1.0)
**Complements:** drso-integrated-intent.md (v1.0.0)
**Maintained by:** Chora Ecosystem Council
**Feedback:** Submit change signals or create issues in chora-workspace repository
