# Chora Compose Roadmap Revision: Gateway Integration & Platform Maturation

**Version:** 2.0
**Date:** 2025-10-17 (Updated after mcp-n8n roadmap review)
**Status:** Active
**Context:** Response to mcp-n8n integration proposals, ecosystem alignment review, and risk analysis
**Supersedes:** Portions of [ROADMAP_UPDATE_v2.md](ROADMAP_UPDATE_v2.md) related to v1.2.0+
**Coordination:** Synchronized with mcp-n8n roadmap (see [CROSS_TEAM_COORDINATION.md](CROSS_TEAM_COORDINATION.md))

---

## Executive Summary

This document revises the chora-compose roadmap to incorporate gateway integration patterns identified through collaboration with the mcp-n8n team and comprehensive review of ecosystem specifications. These revisions position chora-compose as a mature **Platform-layer capability** (Layer 2 per ADR-0008) that integrates seamlessly with orchestration gateways while maintaining its core focus on conversational workflow authoring.

**Key Insight:** The mcp-n8n proposals are not feature requests—they are **validation signals** that chora-compose's architecture aligns with ecosystem patterns. More critically, they reveal gaps between ecosystem specifications and current implementation.

---

## Table of Contents

1. [Background & Context](#background--context)
2. [Analysis of mcp-n8n Proposals](#analysis-of-mcp-n8n-proposals)
3. [Coordination Strategy](#coordination-strategy) **NEW**
4. [Revised Roadmap by Version](#revised-roadmap-by-version)
5. [Cross-Team Deliverables](#cross-team-deliverables) **NEW**
6. [Implementation Priorities](#implementation-priorities)
7. [Ecosystem Alignment](#ecosystem-alignment)
8. [Out of Scope](#out-of-scope)
9. [Migration & Compatibility](#migration--compatibility)
10. [Success Metrics](#success-metrics)

---

## Background & Context

### Three-Layer Architecture (ADR-0008)

```
Layer 3: Capabilities (Consumption)
         ↑ Integration Point
         │ MCP Protocol
         │ Gateway Aggregation (n8n, etc.)
         ↓
Layer 2: Platform (Distribution)  ← chora-compose moving here
         ↑
         │ Local MCP
         ↓
Layer 1: Workspace (R&D)          ← chora-compose originated here
```

**Transition:** Chora-compose is evolving from Layer 1 (Workspace/R&D tool) to Layer 2 (Platform capability consumable by orchestration systems).

### Current State (v1.1.0)

**Strengths:**
- ✅ 17 MCP tools for comprehensive workflow authoring
- ✅ 5 capability resources for agent self-configuration
- ✅ Conversational workflow authoring (draft/test/modify/save pattern)
- ✅ Plugin-aware generator registry
- ✅ Dynamic feature discovery

**Gaps Identified:**
- ⚠️ Generator dependency metadata not exposed (blocks gateway pre-validation)
- ⚠️ Concurrency limits specified but not surfaced via MCP
- ⚠️ Telemetry schema not discoverable
- ⚠️ No gateway-specific capability views
- ⚠️ No preview/diffing for artifacts (only configs have test_config)

### mcp-n8n Context

**What is mcp-n8n?**
A gateway/orchestrator that aggregates multiple MCP servers, enabling:
- Federated capability discovery across services
- Request routing based on capability matching
- Credential management and pre-validation
- Multi-backend workflow composition

**Why This Matters:**
As a gateway consumer of chora-compose, mcp-n8n's integration needs represent broader ecosystem patterns. Addressing these needs benefits all gateway integrations.

---

## Analysis of mcp-n8n Proposals

### Proposal 1: Gateway-Friendly Capability Surfacing
**Rating:** ⭐⭐⭐⭐ (upgraded from ⭐⭐⭐)
**Status:** Partially Implemented → Enhance in v1.2.0

**What They Need:**
- Namespace-aware capability overlays (e.g., `?context=gateway` parameter)
- Gateway-specific hints (e.g., exclude local-only features)
- Optimized capability descriptions for routing

**Ecosystem Alignment:**
- ecosystem-intent Part 8.4: "Discovery systems SHOULD support context-aware capability resolution"
- Already have capability resources, need context awareness

**Implementation:**
```
capabilities://server?context=gateway
→ Returns gateway-optimized view (excludes ephemeral storage paths, etc.)

capabilities://generators?context=gateway
→ Emphasizes upstream dependencies, concurrency hints
```

**Value:** Gateways get clean capability descriptions without local-only noise.

---

### Proposal 2: Composable Generator Catalogs (Dependency Tags)
**Rating:** ⭐⭐⭐⭐⭐ CRITICAL
**Status:** MISSING → Implement in v1.1.1 (patch)

**What They Need:**
Tag generators with upstream service dependencies:
```json
{
  "generator_type": "code_generation",
  "upstream_dependencies": {
    "services": ["anthropic"],
    "credentials_required": ["ANTHROPIC_API_KEY"],
    "optional_services": []
  }
}
```

**Ecosystem Alignment:**
- ecosystem-intent Part 7.3: "Manifests MUST include SBOM with all direct and transitive dependencies"
- **CRITICAL GAP:** Current `capabilities://generators` doesn't expose what external services each generator requires

**Current State:**
```python
# src/chora_compose/mcp/types.py (Line 85)
class GeneratorCapability(BaseModel):
    generator_type: str
    indicators: list[GeneratorIndicator]
    # MISSING: upstream_dependencies field
```

**Impact:**
- Gateways can't pre-validate credentials before routing requests
- Users don't know which API keys are needed until generation fails
- SBOM requirements not met per ecosystem spec

**Priority:** CRITICAL - Fills ecosystem compliance gap + immediate UX value

---

### Proposal 3: Incremental Assembly & Diffing
**Rating:** ⭐⭐⭐ (strong alignment)
**Status:** Partially Implemented → Extend in v1.2.0

**What They Need:**
Dry-run mode showing what will change before commit:
```bash
chora-compose preview-artifact my-artifact
→ Shows diff of changes without writing files
```

**Ecosystem Alignment:**
- v1.1.0 already implements this pattern for configs: `test_config` tool
- Perfect extension: `preview_artifact` tool

**Value Scenario:**
```
User: "Assemble the release notes but show me what will change first"
Agent: Uses preview_artifact → Shows diff → User approves → Uses assemble_artifact
```

**Implementation:** Extend conversational workflow authoring pattern to artifacts.

---

### Proposal 4: Delegated Orchestration Hooks
**Rating:** ⭐⭐ (ecosystem provides better solution)
**Status:** Use Context Bus pattern instead

**What They Initially Proposed:**
- Webhook callbacks when artifact generation completes
- Long-running job status endpoints

**Ecosystem Solution (ecosystem-intent Part 8.9):**
Instead of custom webhooks, emit structured events to **Context Bus**:
```jsonl
{"timestamp": "2025-10-17T12:00:00Z", "event_type": "artifact_completed", "artifact_id": "release-notes", "trace_id": "abc123"}
```

**Recommendation:**
- v1.1.x: Emit events to `var/telemetry/events.jsonl` (local file)
- v1.3.0+: Integrate with Context Bus when platform provides it

**Why Not Webhooks?**
- Adds statefulness to chora-compose (complexity)
- Context Bus is ecosystem-standard solution
- Already specified in ecosystem-intent Part 9

---

### Proposal 5: Gateway-Controlled Throttling
**Rating:** ⭐⭐⭐
**Status:** Specified but not exposed → Surface in v1.1.1

**What They Need:**
```json
{
  "limits": {
    "max_concurrent_generations": 5,
    "rate_limit_per_minute": 10
  }
}
```

**Current State:**
- Ecosystem manifest schema (star.yaml) already specifies this
- NOT surfaced in `capabilities://server` response

**Fix:** Add `limits` dict to ServerCapability response (trivial addition).

---

### Proposal 6: Multi-Backend Composition
**Rating:** ⭐ (out of scope)
**Status:** Layer 3 concern (n8n's responsibility)

**What They Proposed:**
Federated assembly instructions allowing generators to reference other MCP servers.

**Architecture Decision:**
Per ADR-0008 three-layer model:
- **Layer 2 (chora-compose):** Provides atomic capabilities (generate, assemble, validate)
- **Layer 3 (n8n/gateway):** Orchestrates multi-backend workflows

**Rationale:**
Chora-compose shouldn't know about other MCP servers. That's the gateway's job.

**Example:**
```
n8n workflow:
1. Call chora-compose.generate_content(intro)
2. Call external-api.fetch_data(metrics)
3. Call chora-compose.assemble_artifact(report, [intro, metrics])
```

Gateway orchestrates, chora-compose provides capabilities.

---

### Proposal 7: Telemetry Handshake
**Rating:** ⭐⭐⭐
**Status:** Specified but not implemented → Add in v1.2.0

**What They Need:**
Expose telemetry schema so gateways know what events to expect:
```
capabilities://telemetry
→ Returns event types, schema, retention policy
```

**Ecosystem Alignment:**
- ecosystem-intent Part 9: Specifies required event types, metrics, trace context
- NOT currently implemented in chora-compose

**Implementation:**
New capability resource with event catalog:
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
  "metrics": ["generation_duration_ms", "artifact_size_bytes"],
  "trace_context": "opentelemetry"
}
```

---

## Coordination Strategy

### Synchronized Timeline with mcp-n8n

**Critical Insight:** After reviewing the mcp-n8n roadmap, we've identified timing dependencies and feedback loops that require structured coordination.

### Week-by-Week Coordination Matrix

| Week | Chora-Compose | mcp-n8n | Coordination Points |
|------|---------------|---------|---------------------|
| **1-2** | v1.1.1 development & release | Phase 0: Foundation Validation | ✅ Schema review (Week 1)<br>✅ Joint integration tests (Week 2)<br>✅ v1.1.1 release checkpoint |
| **3** | v1.1.2 continuous feedback patch | Phase 1 Week 1: Integration smoke tests | ✅ Enhanced metadata delivery<br>✅ Preliminary gateway context |
| **4-6** | v1.2.0 design & feedback collection | Phase 1 Week 2-4: Weekly Report workflow | ✅ Weekly check-ins (Friday 2pm)<br>✅ Requirements gathering<br>✅ Week 6: Feedback document review |
| **7** | v1.2.0-beta.1 release | Phase 2 Week 1: Context-aware discovery | ✅ Beta validation<br>✅ Unblock Phase 2 early |
| **8-9** | v1.2.0-beta.2 development | Phase 2 Week 2-3: Preview workflows | ✅ Bi-weekly check-ins<br>✅ Beta feedback incorporation |
| **10** | v1.2.0 GA release | Phase 2 Week 4: Production workflows | ✅ Release coordination<br>✅ Joint retrospective |
| **11-14** | v1.3.0 development | Phase 3: Ecosystem maturation | ✅ Context bus design alignment<br>✅ Future roadmap planning |

### Blocking Dependencies

**CRITICAL PATH ITEMS:**

1. **mcp-n8n Phase 1 BLOCKS on chora v1.1.1**
   - Credential validation (Week 3) requires generator dependencies
   - **Mitigation:** v1.1.1 releases Week 2 end (before Phase 1 Week 3)

2. **mcp-n8n Phase 2 REQUIRES chora v1.2.0**
   - Context-aware routing (Week 7) requires gateway capabilities
   - **Mitigation:** v1.2.0-beta.1 releases Week 7 (unblocks Phase 2 immediately)

3. **chora v1.2.0 design INFORMED BY mcp-n8n Phase 1**
   - Week 6 feedback document informs v1.2.0 features
   - **Mitigation:** Continuous feedback (Week 4 prelim, Week 6 final)

### Feedback Loops

**Continuous Feedback (Week 3-6):**
- **Friday 2pm:** Weekly check-in
  - mcp-n8n shares integration learnings
  - chora team answers questions
  - Document v1.2.0 requirements

**Beta Feedback (Week 7, 9):**
- **Monday:** Beta release
- **Friday:** Feedback session
  - Usage patterns
  - Issues discovered
  - Missing features

**Retrospectives:**
- **Week 6 End:** Phase 1 → v1.2.0 design review
- **Week 10 End:** Phase 2 → v1.3.0 planning

### Decision-Making Framework

**Chora-Compose Autonomous Decisions:**
- Internal architecture
- Tool interfaces (within MCP spec)
- Release timing (after dependencies resolved)

**mcp-n8n Autonomous Decisions:**
- Workflow design
- Gateway routing logic
- n8n-specific tooling

**Joint Decisions (Require Coordination):**
- Schema specifications (generator deps, events)
- Telemetry format
- Integration testing approach
- Ecosystem standards interpretation

**Escalation Path:**
1. Weekly check-in (routine coordination)
2. Async GitHub issue/discussion (technical detail)
3. Ad-hoc sync meeting (blocking issue)
4. Ecosystem forum (standards interpretation)

---

## Revised Roadmap by Version

### v1.1.1 - Gateway Essentials (Patch Release)
**Target Date:** October 2025 (1 week)
**Focus:** Close critical gaps, 100% backward compatible

**Deliverables:**

1. **Generator Dependency Tags** ⭐⭐⭐⭐⭐ CRITICAL

   **Schema Specification (aligned with mcp-n8n expectations):**
   ```python
   class UpstreamDependencies(BaseModel):
       """External service dependencies required by generator."""
       services: list[str]  # e.g., ["anthropic", "openai"]
       credentials_required: list[str]  # e.g., ["ANTHROPIC_API_KEY"]
       optional_services: list[str] = []  # e.g., ["langfuse"]

       # Gateway routing hints
       expected_latency_ms: dict[str, int] = {}  # {"p50": 1000, "p95": 3000}
       stability: Literal["stable", "beta", "experimental"] = "stable"
       concurrency_safe: bool = True
   ```

   **Implementation:**
   - [ ] Add UpstreamDependencies model to `src/chora_compose/mcp/types.py`
   - [ ] Add field to GeneratorCapability: `upstream_dependencies: UpstreamDependencies | None`
   - [ ] Update all builtin generators:
     - DemonstrationGenerator: `services=[], credentials_required=[]`
     - Jinja2Generator: `services=[], credentials_required=[]`
     - TemplateFillGenerator: `services=[], credentials_required=[]`
     - CodeGenerationGenerator: `services=["anthropic"], credentials_required=["ANTHROPIC_API_KEY"]`
     - BDDScenarioGenerator: `services=[], credentials_required=[]`
   - [ ] Document in `docs/reference/api/resources/capabilities.md`
   - [ ] Tests: Extend test_capabilities_resources.py (+10 tests)

2. **Concurrency Limits Exposure** ⭐⭐⭐
   - [ ] Add `limits` dict to ServerCapability model
   - [ ] Default: `{"max_concurrent_generations": 5, "rate_limit_per_minute": 20}`
   - [ ] Source from config: `config.server.limits` (if provided)
   - [ ] Document in server capabilities reference
   - [ ] Tests: Server capability with limits (+3 tests)

3. **Event Emission Foundation** ⭐⭐

   **Event Schema Specification (aligned with ecosystem-intent Part 9):**
   ```json
   {
     "namespace": "chora",
     "event_types": {
       "content_generated": {
         "required_fields": ["timestamp", "trace_id", "content_config_id", "status"],
         "optional_fields": ["duration_ms", "generator_type", "size_bytes"]
       },
       "artifact_assembled": {
         "required_fields": ["timestamp", "trace_id", "artifact_config_id", "status"],
         "optional_fields": ["duration_ms", "section_count", "output_path"]
       },
       "validation_completed": {
         "required_fields": ["timestamp", "trace_id", "target_id", "status"],
         "optional_fields": ["duration_ms", "errors_count", "warnings_count"]
       }
     }
   }
   ```

   **Implementation:**
   - [ ] Create `src/chora_compose/telemetry/events.py` module
   - [ ] Emit events to `var/telemetry/events.jsonl` (append-only, JSONL format)
   - [ ] Add event emission to generate_content, assemble_artifact, validate_content tools
   - [ ] OpenTelemetry-compatible timestamp format (ISO 8601)
   - [ ] Document event schema in `specs/event-schema.md`
   - [ ] Tests: Event file creation, format validation, correlation (+7 tests)

4. **Joint Integration Test Setup** 🌟 NEW
   - [ ] Create `chora-ecosystem-integration-tests` repository (or directory)
   - [ ] Setup CI/CD pipeline (GitHub Actions)
   - [ ] Add smoke tests for mcp-n8n integration
   - [ ] Document integration contract in `specs/integration-contract.md`
   - [ ] Coordinate with mcp-n8n team on shared test ownership

5. **Schema Coordination** 🌟 NEW
   - [ ] Week 1 Monday: Schema review meeting with mcp-n8n team
   - [ ] Week 1 Wednesday: Finalize generator dependency schema
   - [ ] Week 2 Monday: Event schema review
   - [ ] Week 2 Wednesday: v1.1.1 beta release (mcp-n8n validation)
   - [ ] Week 2 Friday: v1.1.1 GA release

**Breaking Changes:** None
**Migration:** None required
**Test Coverage Target:** +20 tests (maintain >95%)

**Coordination Checkpoint:** Week 2 end - mcp-n8n Phase 0 complete validation

---

### v1.1.2 - Continuous Feedback (Patch Release) 🌟 NEW
**Target Date:** Week 3
**Focus:** Enable mcp-n8n Phase 1 feedback loop
**Purpose:** Provide enhanced metadata to inform v1.2.0 design

**Strategic Rationale:**
This patch release bridges v1.1.1 (gateway essentials) and v1.2.0 (full gateway integration) by providing enhanced metadata that enables mcp-n8n to give concrete feedback on what gateway-aware capabilities should look like in v1.2.0.

**Deliverables:**

1. **Enhanced Generator Metadata** ⭐⭐⭐
   - Add `expected_latency_ms` to all builtin generators
     ```python
     # Example for CodeGenerationGenerator
     expected_latency_ms={"p50": 2000, "p95": 5000, "p99": 10000}
     ```
   - Add `stability` indicator (stable/beta/experimental)
   - Populate `concurrency_safe` flag for all generators
   - Document metadata meaning in capabilities reference

2. **Event Schema v2** ⭐⭐
   - Add `duration_ms` to all events (SHOULD include per ecosystem-intent)
   - Add `validation_completed` event type (was planned for v1.1.1)
   - Document event correlation patterns (trace_id usage)
   - Example: Link content_generated → artifact_assembled via trace_id

3. **Preliminary Gateway Context** ⭐
   - Parse `?context=gateway` parameter (no-op behavior in v1.1.2)
   - Log gateway context requests for analysis
   - Return standard response (same as default, no filtering yet)
   - **Purpose:** Measure what gateways query, inform v1.2.0 optimization

4. **Feedback Collection Instrumentation** 🌟
   - Log which capabilities are queried most frequently
   - Track context parameter usage patterns
   - Survey mcp-n8n team: "What metadata would help routing?"
   - Document requirements for v1.2.0 design

**Breaking Changes:** None (pure additive)
**Migration:** None required
**Test Coverage Target:** +5 tests (lightweight patch)

**Coordination Checkpoint:** Week 3 end - mcp-n8n Phase 1 starts with enhanced metadata

---

### v1.2.0 - Gateway Integration (Minor Release)
**Target Date:** Week 7-10 (phased beta releases)
**Focus:** Gateway-aware features, preview workflows
**Strategy:** Split into 2 betas to unblock mcp-n8n Phase 2 early

#### v1.2.0-beta.1 (Week 7) - Core Gateway Features

**Goal:** Unblock mcp-n8n Phase 2 as early as possible

**Deliverables:**

1. **Gateway-Aware Capabilities** ⭐⭐⭐⭐ (Full Implementation)
   - Support `?context=gateway` parameter on all capability resources
   - Return optimized views:
     - Hide local-only features (e.g., ephemeral storage paths)
     - Emphasize upstream dependencies for routing
     - Add routing hints (latency, concurrency, stability)
   - Filter tool lists (exclude internal/debug tools)
   - Document context parameter usage
   - Tests: Context-aware capability resolution (+10 tests)

2. **Preview Artifact Tool** ⭐⭐⭐ (Basic Implementation)
   - New MCP tool: `preview_artifact`
   - Shows section-level diff of what will change
   - No file writes (dry-run only)
   - Extends test_config pattern to artifacts
   - Tests: Preview workflows, diff generation (+8 tests)

3. **Basic Documentation**
   - Tool reference for preview_artifact
   - Context parameter usage guide
   - Beta testing instructions

**Success Criteria:**
- ✅ mcp-n8n can start Phase 2 Week 7
- ✅ Context-aware routing reduces errors by 30%+
- ✅ Preview shows accurate section-level diffs

**Breaking Changes:** None
**Migration:** None required
**Test Coverage Target:** +18 tests

**Coordination Checkpoint:** Week 7 Monday - Beta release, mcp-n8n Phase 2 unblocked

---

#### v1.2.0-beta.2 (Week 9) - Enhanced Features

**Goal:** Incorporate feedback from mcp-n8n Phase 2 early usage

**Deliverables:**

1. **Telemetry Capabilities Resource** ⭐⭐⭐
   - New resource: `capabilities://telemetry`
   - Exposes event schema, metrics, trace context
   - Gateway-discoverable observability contract
   - Auto-generated documentation from schema
   - Tests: Telemetry schema validation (+5 tests)

2. **Multi-Step Preview Coordination** 🌟 NEW
   - New tool: `preview_workflow_step`
   - Allows gateway to preview individual content generations
   - Coordinate multiple previews before final assembly
   - Example: Preview each section before assembling weekly report
   - Tests: Multi-step preview workflows (+7 tests)

3. **Performance Optimizations**
   - Capability response caching headers (ETags, Cache-Control)
   - Reduced capability query latency (<50ms p95)
   - Optimized preview diff generation
   - Benchmark: Measure improvement vs. beta.1

4. **Enhanced Documentation**
   - Gateway integration guide (draft, 20+ pages)
   - Event catalog reference
   - Performance tuning guide

**Success Criteria:**
- ✅ Telemetry schema discoverable
- ✅ Multi-step preview pattern validated
- ✅ Performance targets met (<50ms capability lookup)

**Breaking Changes:** None
**Migration:** None required
**Test Coverage Target:** +12 tests

**Coordination Checkpoint:** Week 9 Friday - Beta feedback session

---

#### v1.2.0 GA (Week 10) - Production Release

**Goal:** Production-ready release with complete documentation

**Deliverables:**

1. **Complete Documentation** ⭐⭐⭐⭐⭐
   - Gateway integration guide (50+ pages complete)
   - API reference updates (all new tools and resources)
   - Migration guide (v1.1.x → v1.2.0, though no breaking changes)
   - mcp-n8n integration examples (3+ workflow patterns)
   - Performance tuning guide
   - Troubleshooting guide

2. **Feedback Incorporation** 🌟
   - All mcp-n8n Phase 2 feedback addressed
   - Community feedback from beta users
   - Performance optimizations based on real usage
   - Edge case fixes from beta testing

3. **Production Hardening**
   - Error handling improvements
   - Validation enhancements
   - Logging improvements
   - Security review complete

4. **Release Artifacts**
   - PyPI package published
   - Docker images updated
   - GitHub release with changelogs
   - Documentation site updated

**Breaking Changes:** None (per semver)
**Migration:** None required (100% backward compatible with v1.1.x)
**Test Coverage Target:** All features >95%

**Coordination Checkpoint:** Week 10 Wednesday - GA release, Week 10 Friday - Joint retrospective

---

### v1.3.0 - Dynamic Discovery & Context Bus (Minor Release)
**Target Date:** Week 11-14
**Focus:** Platform infrastructure integration + runtime extensibility
**Coordination:** Parallel with mcp-n8n Phase 3

**Deliverables:**

1. **Dynamic Capability Discovery** 🌟 NEW (Week 11-12)

   **Problem:** Currently capabilities are static until server restart. Plugin installations require gateway restart to discover new generators.

   **Solution:**
   ```python
   # Capability change events
   {
     "event_type": "capability_changed",
     "change_type": "generator_added",  # or generator_removed, tool_added, etc.
     "generator_type": "sql_generator",
     "timestamp": "2025-...",
     "trace_id": "..."
   }
   ```

   **Implementation:**
   - [ ] Emit capability_changed events when:
     - Plugin generator registered
     - Plugin generator unregistered
     - Tools added/removed dynamically
   - [ ] Gateway subscribes to capability_changed events
   - [ ] Event-driven cache invalidation
   - [ ] Hot-reload generators without server restart
   - [ ] Tests: Dynamic discovery workflows (+10 tests)

   **Benefits:**
   - True runtime extensibility
   - Better plugin ecosystem UX
   - No gateway restarts needed
   - Supports zero-downtime updates

2. **Workflow Coordination Primitives** 🌟 NEW (Week 12-13)

   **Problem:** Multi-step workflows (like weekly report) have no transaction support. If step 3 fails, steps 1-2 resources are wasted.

   **Solution - Workflow Context API:**
   ```python
   # Create workflow context
   context_id = await create_workflow_context(
       workflow_id="weekly-report",
       estimated_steps=4
   )

   # All operations in context
   await generate_content(..., workflow_context=context_id)
   await generate_content(..., workflow_context=context_id)
   await assemble_artifact(..., workflow_context=context_id)

   # Commit or rollback
   await commit_workflow_context(context_id)  # Success path
   # or
   await rollback_workflow_context(context_id)  # Failure path
   ```

   **Features:**
   - State checkpointing (save intermediate results)
   - Resume from checkpoint on failure
   - Rollback capabilities (undo partial execution)
   - Resource cleanup (ephemeral storage)
   - Tests: Transaction workflows (+12 tests)

   **Benefits:**
   - More reliable multi-step workflows
   - Resource efficiency (avoid re-generation)
   - Better error recovery
   - Supports long-running workflows

3. **Context Bus Integration** (Week 13-14, when platform provides it)
   - Replace local event emission with context bus publishing
   - Subscribe to relevant platform events
   - Distributed tracing integration (OpenTelemetry full support)
   - Cross-service event correlation
   - Tests: Context bus integration (+8 tests)

4. **SLSA Level 3 Provenance** (Week 14)
   - Build provenance generation
   - Artifact attestation
   - Supply chain security
   - SBOM enhancements

5. **Advanced Gateway Features** (Week 13-14)
   - Capability versioning and compatibility detection
   - Feature flag discovery
   - Deprecation signaling
   - Graceful degradation strategies

**Breaking Changes:**
- Workflow context API opt-in (existing tools work without it)
- Context bus integration opt-in via config

**Migration:**
- Workflow contexts: Optional adoption (backward compatible)
- Context bus: Config-driven (`telemetry.backend: "context_bus"`)

**Test Coverage Target:** +30 tests

**Coordination Checkpoint:** Week 14 end - mcp-n8n Phase 3 complete, joint future planning

---

## Cross-Team Deliverables

These are shared artifacts and specifications that both chora-compose and mcp-n8n teams contribute to and depend on.

### 1. Unified Event Schema Specification

**Owner:** Joint (chora + mcp-n8n)
**Timeline:** Week 1-2 (v1.1.1)
**Format:** Markdown document + JSON Schema
**Location:** `specs/event-schema.md` (chora-compose repo) + cross-referenced in mcp-n8n docs

**Contents:**
- **Event Namespace Conventions**
  - `chora.*` - Events emitted by chora-compose (platform layer)
  - `gateway.*` - Events emitted by mcp-n8n (orchestration layer)
  - `workflow.*` - Workflow lifecycle events (future, context bus)

- **Required Fields** (ALL events MUST include):
  ```json
  {
    "timestamp": "2025-10-17T12:00:00Z",  // ISO 8601 format
    "trace_id": "abc123",                  // OpenTelemetry trace context
    "status": "success"                     // success | failure | pending
  }
  ```

- **Optional Fields** (events SHOULD include when applicable):
  ```json
  {
    "duration_ms": 1234,         // Operation duration
    "error_code": "ERR_...",     // Error classification
    "error_message": "...",      // Human-readable error
    "metadata": {...}            // Event-specific context
  }
  ```

- **Event Correlation Patterns**
  - Use `trace_id` to link related events across services
  - Example: `content_generated` → `artifact_assembled` (same trace_id)
  - Gateway can correlate tool call with backend completion event

- **Versioning Strategy**
  - Schema version in event: `"schema_version": "1.0"`
  - Backward compatibility required for 1 major version
  - Deprecation warnings 6 months before removal

**Deliverable:** Published spec by Week 2, validated by both teams

---

### 2. Generator Dependency Schema Specification

**Owner:** Chora-compose (with mcp-n8n review)
**Timeline:** Week 1 (v1.1.1)
**Format:** Pydantic model + JSON Schema + documentation
**Location:** `docs/reference/schemas/generator-dependencies.md`

**Schema Definition:**
```python
class UpstreamDependencies(BaseModel):
    """External service dependencies required by generator."""
    services: list[str]
    credentials_required: list[str]
    optional_services: list[str] = []

    # Gateway routing hints
    expected_latency_ms: dict[str, int] = {}  # p50, p95, p99
    stability: Literal["stable", "beta", "experimental"] = "stable"
    concurrency_safe: bool = True
```

**Examples for Builtin Generators:**
- DemonstrationGenerator: `services=[], credentials_required=[]`
- CodeGenerationGenerator: `services=["anthropic"], credentials_required=["ANTHROPIC_API_KEY"]`

**Gateway Consumption Guide:**
- How to pre-validate credentials before routing
- How to interpret latency hints for request queuing
- How to handle missing optional services

**Deliverable:** Finalized schema Week 1 Wednesday, implemented in v1.1.1

---

### 3. Joint Integration Test Suite

**Owner:** Joint (shared CI/CD)
**Timeline:** Week 2-ongoing
**Format:** Python test suite + GitHub Actions workflow
**Location:** `chora-ecosystem-integration-tests/` (separate repo or monorepo subdirectory)

**Test Structure:**
```
chora-ecosystem-integration-tests/
  tests/
    gateway/                                    # mcp-n8n owns
      test_credential_validation.py
      test_context_aware_routing.py
      test_event_monitoring.py
    platform/                                   # chora owns
      test_generator_dependencies.py
      test_event_emission.py
      test_capability_discovery.py
    end_to_end/                                 # shared ownership
      test_hello_world_workflow.py
      test_weekly_report_workflow.py
      test_preview_workflow.py
  specs/
    event-schema.md
    generator-dependencies.md
    integration-contract.md
  .github/workflows/
    integration-tests.yml                      # runs on both repos
```

**CI/CD Strategy:**
- Run on every chora-compose release (pre-release validation)
- Run on every mcp-n8n release
- Both teams notified on failure
- Blocking: Integration tests must pass before GA release

**Integration Contract:**
- What chora-compose guarantees (event format, capability schema)
- What mcp-n8n expects (routing behavior, error handling)
- Compatibility matrix (which versions work together)

**Deliverable:** Test suite setup complete Week 2, tests added incrementally

---

### 4. Gateway Integration Guide

**Owner:** Chora-compose (with mcp-n8n case studies)
**Timeline:** Week 10 (v1.2.0 GA)
**Format:** Multi-page documentation (50+ pages)
**Location:** `docs/how-to/gateway-integration/`

**Contents:**

**Part 1: Gateway Integration Patterns**
- Overview of Layer 2 (Platform) ↔ Layer 3 (Gateway) interaction
- MCP protocol considerations
- Namespace conventions

**Part 2: Setup Guide**
- Installing chora-compose as gateway backend
- Configuration best practices
- Environment variable management
- Credential pre-validation setup

**Part 3: Capability Discovery**
- Using `capabilities://server?context=gateway`
- Interpreting generator dependencies
- Caching strategies
- Dynamic discovery (v1.3.0+)

**Part 4: Event Monitoring**
- Consuming events from `var/telemetry/events.jsonl`
- Event correlation patterns
- Building observability dashboards
- Alerting strategies

**Part 5: Performance Tuning**
- Latency optimization techniques
- Concurrency management
- Caching strategies
- Benchmarking tools

**Part 6: Case Studies**
- mcp-n8n integration (detailed walkthrough)
- Weekly Engineering Report workflow
- Event-driven documentation updates
- Custom gateway examples

**Deliverable:** Draft Week 9 (beta.2), complete Week 10 (GA)

---

### 5. Integration Contract Document

**Owner:** Joint
**Timeline:** Week 2
**Format:** Markdown specification
**Location:** `chora-ecosystem-integration-tests/specs/integration-contract.md`

**Contents:**

**Guarantees from chora-compose:**
- Event format stability (backward compatible for 6 months)
- Capability schema versioning
- Tool interface contracts (per MCP spec)
- Error response formats
- Performance SLAs (p95 latencies)

**Expectations from gateways:**
- Namespace adherence (`chora:*` prefix)
- Credential management (don't pass through credentials)
- Trace context propagation
- Error handling (don't retry generation on user error)
- Rate limiting respect (honor 429 responses)

**Compatibility Matrix:**
```
| chora-compose | mcp-n8n | Compatible | Notes |
|---------------|---------|------------|-------|
| v1.1.0        | v0.1.0  | ✅         | Basic gateway |
| v1.1.1        | v0.2.0  | ✅         | + Dependencies |
| v1.2.0        | v0.3.0  | ✅         | + Context-aware |
| v1.3.0        | v0.4.0  | ✅         | + Dynamic discovery |
```

**Breaking Change Policy:**
- Announce 6 months in advance
- Provide migration guide
- Support transition period (2 versions)

**Deliverable:** Published Week 2, updated per release

---

## Implementation Priorities

### Critical Path (v1.1.1)

**Priority 1: Generator Dependencies**
- **Why First:** Ecosystem compliance gap, immediate gateway value
- **Effort:** 1 day (small code change, big impact)
- **Risk:** Low (pure additive to existing capability resources)

**Priority 2: Limits Exposure**
- **Why Second:** Already specified, trivial to surface
- **Effort:** 2 hours
- **Risk:** None

**Priority 3: Event Emission**
- **Why Third:** Foundation for telemetry handshake
- **Effort:** 1 day (event formatting, file I/O, tests)
- **Risk:** Low (local file only, no external dependencies)

### Medium Term (v1.2.0)

**Priority 1: Gateway-Aware Capabilities**
- **Why First:** Enables context-specific discovery
- **Effort:** 2 days (parameter handling, view filtering)
- **Risk:** Low (doesn't change default behavior)

**Priority 2: Preview Artifact Tool**
- **Why Second:** Extends proven pattern, high user value
- **Effort:** 3 days (diff generation, MCP tool wrapper)
- **Risk:** Medium (need robust diff logic)

**Priority 3: Telemetry Resource**
- **Why Third:** Depends on event emission from v1.1.1
- **Effort:** 2 days (schema documentation, capability provider)
- **Risk:** Low

---

## Ecosystem Alignment

### Validated Against Ecosystem Specifications

| Proposal | Ecosystem Spec | Current State | Gap |
|----------|---------------|---------------|-----|
| Generator Dependencies | Part 7.3 (SBOM) | Missing | CRITICAL |
| Concurrency Limits | Manifest schema | Not exposed | Medium |
| Gateway Context | Part 8.4 (Discovery) | Not implemented | Medium |
| Telemetry Handshake | Part 9 (Observability) | Not implemented | Medium |
| Event Emission | Part 8.9 (Context Bus) | Not implemented | Low |

### Ecosystem Documents Reviewed

1. **ecosystem-intent.md** (2,482 lines)
   - Part 3: Manifest Requirements (star.yaml schema)
   - Part 7: Security Baseline (SBOM, vulnerability gating)
   - Part 8: Discovery Expectations (capability discovery, staleness detection)
   - Part 9: Observability Requirements (event types, metrics, trace context)

2. **n8n-integration.md** (2,910 lines)
   - Patterns N1-N7 (orchestration workflows)
   - Gateway aggregation patterns
   - Multi-backend composition

3. **chora-compose-solution-neutral-intent.md** (2,910 lines)
   - Pattern C7 (Conversational Config Development)
   - 3-layer architecture positioning
   - Integration patterns C1-C7

4. **conversational-workflow-authoring.md** (922 lines)
   - Principle 1: Ephemeral-First, Persistent-When-Ready
   - Principle 2: Test-Before-Persist
   - Proven pattern for draft/test/modify/save

---

## Out of Scope

### What We're NOT Doing (and Why)

**1. Multi-Backend Composition**
- **Proposal:** Federated assembly across MCP servers
- **Decision:** OUT OF SCOPE
- **Rationale:** Layer 3 orchestration concern (n8n's responsibility per ADR-0008)
- **Example:** n8n orchestrates calls to multiple servers, chora-compose provides atomic capabilities

**2. Custom Webhook System**
- **Proposal:** Callback URLs for completion events
- **Decision:** Use Context Bus pattern instead
- **Rationale:** Adds statefulness, ecosystem already specifies event bus solution

**3. Gateway-Specific Config Formats**
- **Proposal:** Special config schemas for gateway consumption
- **Decision:** Use context parameters on existing resources
- **Rationale:** Maintain single source of truth, avoid format proliferation

---

## Migration & Compatibility

### Backward Compatibility Guarantee

**v1.1.x (Patches):**
- ✅ 100% backward compatible
- ✅ No breaking changes to schemas, APIs, or MCP tools
- ✅ Pure additive enhancements

**v1.2.0 (Minor):**
- ✅ Backward compatible per semver
- ✅ New tools optional, existing workflows unaffected
- ✅ Context parameters optional (default behavior unchanged)

**v1.3.0+ (Future):**
- ⚠️ May include opt-in breaking changes
- ⚠️ Migration guides provided
- ⚠️ Deprecation warnings 1 version ahead

### Migration Paths

**No migration required for v1.1.x → v1.2.0:**
- Existing MCP clients continue working without changes
- New features opt-in via new tool calls or parameters

**Recommended adoption path:**
1. Upgrade to v1.1.1 (get dependency metadata, limits)
2. Gateway developers: Implement dependency pre-validation
3. Upgrade to v1.2.0 (gateway context, preview workflows)
4. Gateway developers: Use context-aware discovery
5. Monitor for v1.3.0 context bus integration

---

## Success Metrics

### v1.1.1 Success Criteria

**Technical:**
- ✅ All builtin generators have upstream_dependencies metadata
- ✅ capabilities://server includes limits dict
- ✅ Events emitted to var/telemetry/events.jsonl for all operations
- ✅ Test coverage >95% maintained

**Ecosystem:**
- ✅ SBOM compliance (Part 7.3)
- ✅ Manifest schema alignment
- ✅ OpenTelemetry event format

**Gateway Integration:**
- ✅ mcp-n8n can pre-validate credentials before routing
- ✅ Gateways discover concurrency limits
- ✅ Event log parseable by external tools

### v1.2.0 Success Criteria

**Technical:**
- ✅ Context parameter works on all capability resources
- ✅ preview_artifact returns accurate diffs
- ✅ capabilities://telemetry exposes complete event schema
- ✅ Test coverage >95% maintained

**User Experience:**
- ✅ Users can preview artifacts before committing
- ✅ Gateways get clean capability views without local-only noise
- ✅ Event schema discoverable without reading docs

**Ecosystem:**
- ✅ Context-aware discovery (Part 8.4)
- ✅ Observability contract (Part 9)
- ✅ Test-before-persist pattern extended to artifacts

### Community Impact Metrics

**Adoption:**
- 🎯 mcp-n8n integration documented with examples
- 🎯 3+ other gateway integrations (MCP ecosystem)
- 🎯 Community feedback: "chora-compose plays well with gateways"

**Documentation:**
- 🎯 Gateway integration guide (50+ pages)
- 🎯 Event catalog reference
- 🎯 mcp-n8n conversation examples

---

## Implementation Checklist

### v1.1.1 (Week 1)

**Generator Dependencies:**
- [ ] Add `upstream_dependencies` field to GeneratorCapability model
- [ ] Update DemonstrationGenerator (no external deps)
- [ ] Update Jinja2Generator (no external deps)
- [ ] Update TemplateFillGenerator (no external deps)
- [ ] Update CodeGenerationGenerator (ANTHROPIC_API_KEY)
- [ ] Update BDDScenarioGenerator (no external deps)
- [ ] Extend test_capabilities_resources.py (+10 tests)
- [ ] Update docs/reference/api/resources/capabilities.md

**Limits Exposure:**
- [ ] Add `limits` dict to ServerCapability response
- [ ] Source from config (hawf.yaml) or defaults
- [ ] Test server capability with limits
- [ ] Document in capabilities reference

**Event Emission:**
- [ ] Create event emission utility (src/chora_compose/telemetry/events.py)
- [ ] Emit content_generated events
- [ ] Emit artifact_assembled events
- [ ] Emit validation_completed events
- [ ] Tests: Event file creation, format validation
- [ ] Document event schema

### v1.2.0 (Weeks 2-4)

**Gateway Context:**
- [ ] Add context parameter to all capability providers
- [ ] Implement view filtering logic
- [ ] Test context=gateway vs default
- [ ] Document context usage

**Preview Artifact:**
- [ ] Implement diff generation utility
- [ ] Create preview_artifact MCP tool
- [ ] Tests: Diff accuracy, edge cases
- [ ] Document preview workflow

**Telemetry Resource:**
- [ ] Create capabilities://telemetry provider
- [ ] Document event catalog
- [ ] Tests: Schema validation
- [ ] Gateway integration guide

---

## Appendix A: Proposal Rating Methodology

**5 Stars (⭐⭐⭐⭐⭐):** CRITICAL - Fills ecosystem compliance gap or blocking issue
**4 Stars (⭐⭐⭐⭐):** HIGH - Strong ecosystem alignment, significant value
**3 Stars (⭐⭐⭐):** MEDIUM - Good alignment, extends existing patterns
**2 Stars (⭐⭐):** LOW - Valid but ecosystem has better solution
**1 Star (⭐):** OUT OF SCOPE - Wrong layer or architectural mismatch

---

## Appendix B: mcp-n8n Dialogue Summary

**Date:** 2025-10-17
**Participants:** mcp-n8n team, chora-compose maintainers
**Format:** Asynchronous proposal exchange

**Proposal Count:** 7 integration patterns
**Acceptance Rate:** 5/7 (2 out of scope due to layer mismatch)
**Critical Gaps Identified:** 1 (generator dependencies)

**Meta-Reflection:**
> "The biggest surprise wasn't what mcp-n8n proposed—it was realizing the ecosystem-intent doc already specified solutions for most of these problems. The mcp-n8n team independently arrived at the same architectural conclusions as the ecosystem specs. That's validation that we're on the right track."

**Key Takeaway:**
These aren't feature requests. They're signals that chora-compose's architecture resonates with real-world integration needs. The work is less about building new features and more about **exposing what we already have in gateway-friendly ways**.

---

## Appendix C: Related Documents

**Planning Documents:**
- [ROADMAP_UPDATE_v2.md](ROADMAP_UPDATE_v2.md) - Current roadmap (v0.8.0 → v1.0.0)
- [ROADMAP.md](../ROADMAP.md) - Original 20-week plan (archived)
- [RELEASE_TRAIN.md](planning/ROADMAP_RELEASE_SUMMARY.md) - Release planning

**Ecosystem Specifications:**
- [ecosystem-intent.md](ecosystem/ecosystem-intent.md) - Ecosystem-wide standards
- [n8n-integration.md](ecosystem/n8n-integration.md) - Gateway patterns
- [chora-compose-solution-neutral-intent.md](ecosystem/chora-compose-solution-neutral-intent.md) - Layer 2 positioning

**Architecture:**
- ADR-0008: Three-Layer Architecture (Workspace → Platform → Capabilities)
- [conversational-workflow-authoring.md](explanation/architecture/conversational-workflow-authoring.md) - Draft/test/modify/save pattern

---

**Document Version:** 1.0
**Status:** Active
**Last Updated:** 2025-10-17
**Next Review:** Post v1.1.1 release (validate assumptions)
**Approval:** Pending stakeholder review
