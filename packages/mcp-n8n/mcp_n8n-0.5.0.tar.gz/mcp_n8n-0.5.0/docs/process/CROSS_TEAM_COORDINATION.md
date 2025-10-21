# Cross-Team Coordination: chora-compose ↔ mcp-n8n

**Version:** 1.0
**Date:** 2025-10-17
**Status:** Active
**Purpose:** Define coordination protocols, shared deliverables, and decision-making frameworks for chora-compose (Layer 2 Platform) and mcp-n8n (Layer 3 Gateway) integration

---

## Executive Summary

This document establishes the coordination framework between chora-compose (Platform/Layer 2) and mcp-n8n (Gateway/Layer 3) teams. It defines:

1. **Shared Specifications** (event schema, generator dependencies)
2. **Coordination Schedule** (weekly check-ins, release alignment)
3. **Decision-Making Framework** (autonomous vs. joint decisions)
4. **Communication Protocols** (escalation paths, feedback loops)
5. **Success Metrics** (integration health, coordination effectiveness)

**Key Principle:** Maximize autonomy while ensuring tight integration through well-defined contracts and specifications.

---

## Table of Contents

1. [Coordination Model](#coordination-model)
2. [Shared Specifications](#shared-specifications)
3. [Coordination Schedule](#coordination-schedule)
4. [Decision-Making Framework](#decision-making-framework)
5. [Communication Protocols](#communication-protocols)
6. [Integration Health Metrics](#integration-health-metrics)

---

## Coordination Model

### Three-Layer Architecture Context

```
Layer 3: Capabilities (Consumption) ← mcp-n8n lives here
         ↑ MCP Protocol
         │ Integration Point (THIS DOCUMENT)
         ↓
Layer 2: Platform (Distribution)    ← chora-compose lives here
         ↑ Local MCP
         ↓
Layer 1: Workspace (R&D)
```

### Coordination Principles

1. **Loose Coupling, Tight Contracts**
   - Teams operate autonomously
   - Integration via well-defined specs (MCP protocol + shared schemas)
   - Minimal cross-team dependencies

2. **Shared Specifications, Separate Implementations**
   - Event schema: Jointly defined, separately implemented
   - Generator dependencies: Chora defines, mcp-n8n consumes
   - Integration contract: Jointly maintained

3. **Continuous Feedback, Phased Implementation**
   - Weekly check-ins during overlapping development
   - Early beta releases to unblock downstream work
   - Retrospectives after major milestones

4. **Compatibility First**
   - Backward compatibility maintained for 6 months
   - Breaking changes announced 1 version ahead
   - Migration guides provided

---

## Shared Specifications

### 1. Event Schema Specification

**File:** `specs/event-schema.md` (chora-compose repo)
**Owner:** Joint (both teams review and approve)
**Version:** 1.0 (updated per coordination)

#### Event Namespace Conventions

| Namespace | Owner | Purpose | Examples |
|-----------|-------|---------|----------|
| `chora.*` | chora-compose | Platform layer events | `chora.content_generated`, `chora.artifact_assembled` |
| `gateway.*` | mcp-n8n | Gateway layer events | `gateway.tool_call`, `gateway.backend_started` |
| `workflow.*` | Future (context bus) | Workflow lifecycle | `workflow.started`, `workflow.completed` |

#### Universal Required Fields

ALL events across all namespaces MUST include:

```json
{
  "timestamp": "2025-10-17T12:00:00Z",  // ISO 8601 UTC
  "trace_id": "abc123",                  // OpenTelemetry trace context
  "status": "success"                     // success | failure | pending | cancelled
}
```

#### Universal Optional Fields

Events SHOULD include when applicable:

```json
{
  "duration_ms": 1234,                   // Operation duration
  "error_code": "ERR_VALIDATION_FAILED", // Structured error code
  "error_message": "...",                // Human-readable message
  "metadata": {...}                      // Event-specific context
}
```

#### Event Correlation Patterns

**Pattern 1: Trace Context Propagation**
```
Gateway receives request → generates trace_id
    ↓ (trace_id passed to backend)
Backend operation → emits events with same trace_id
    ↓
Gateway correlates backend events with original request
```

**Pattern 2: Multi-Step Workflow**
```
generate_content(trace_id=abc) → chora.content_generated(trace_id=abc)
generate_content(trace_id=abc) → chora.content_generated(trace_id=abc)
assemble_artifact(trace_id=abc) → chora.artifact_assembled(trace_id=abc)
```

All events share trace_id, enabling end-to-end workflow tracking.

#### Versioning Strategy

- Events include `schema_version` field: `"schema_version": "1.0"`
- Minor version bump (1.0 → 1.1): Add optional fields (backward compatible)
- Major version bump (1.0 → 2.0): Change required fields or remove fields
- Consumers MUST handle unknown schema versions gracefully
- Backward compatibility maintained for 1 major version

#### Example Events

**chora.content_generated:**
```json
{
  "timestamp": "2025-10-17T12:00:00.123Z",
  "trace_id": "abc123",
  "status": "success",
  "schema_version": "1.0",
  "event_type": "chora.content_generated",
  "content_config_id": "weekly-report-intro",
  "generator_type": "jinja2",
  "duration_ms": 234,
  "size_bytes": 1024,
  "metadata": {
    "template": "report-intro.j2",
    "context_keys": ["week", "team"]
  }
}
```

**gateway.tool_call:**
```json
{
  "timestamp": "2025-10-17T12:00:00.000Z",
  "trace_id": "abc123",
  "status": "success",
  "schema_version": "1.0",
  "event_type": "gateway.tool_call",
  "backend": "chora-composer",
  "namespace": "chora",
  "tool": "generate_content",
  "duration_ms": 250,
  "metadata": {
    "arguments": {"content_config_id": "weekly-report-intro"},
    "result_size_bytes": 1024
  }
}
```

---

### 2. Generator Dependency Schema

**File:** `docs/reference/schemas/generator-dependencies.md` (chora-compose repo)
**Owner:** chora-compose (with mcp-n8n review)
**Version:** 1.0

#### Schema Definition

```python
from pydantic import BaseModel
from typing import Literal

class UpstreamDependencies(BaseModel):
    """
    External service dependencies required by generator.

    Enables gateways to:
    - Pre-validate credentials before routing
    - Estimate request latency
    - Make intelligent routing decisions
    """

    # Required external services
    services: list[str]
    # Example: ["anthropic", "openai", "langfuse"]

    # Credentials that must be present in environment
    credentials_required: list[str]
    # Example: ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]

    # Optional services (degraded functionality if missing)
    optional_services: list[str] = []
    # Example: ["langfuse"]  # telemetry works without it

    # Gateway routing hints
    expected_latency_ms: dict[str, int] = {}
    # Example: {"p50": 1000, "p95": 3000, "p99": 10000}

    # Stability indicator
    stability: Literal["stable", "beta", "experimental"] = "stable"

    # Concurrency safety
    concurrency_safe: bool = True
    # False if generator has global state or file locks
```

#### Examples for Builtin Generators

**DemonstrationGenerator:**
```python
UpstreamDependencies(
    services=[],
    credentials_required=[],
    optional_services=[],
    expected_latency_ms={"p50": 10, "p95": 50, "p99": 100},
    stability="stable",
    concurrency_safe=True
)
```

**CodeGenerationGenerator:**
```python
UpstreamDependencies(
    services=["anthropic"],
    credentials_required=["ANTHROPIC_API_KEY"],
    optional_services=["langfuse"],  # for telemetry
    expected_latency_ms={"p50": 2000, "p95": 5000, "p99": 10000},
    stability="stable",
    concurrency_safe=True
)
```

**Jinja2Generator:**
```python
UpstreamDependencies(
    services=[],
    credentials_required=[],
    optional_services=[],
    expected_latency_ms={"p50": 100, "p95": 500, "p99": 1000},
    stability="stable",
    concurrency_safe=True
)
```

#### Gateway Consumption Guide

**Use Case 1: Credential Pre-Validation**
```python
# Gateway startup check
for generator in capabilities.generators:
    deps = generator.upstream_dependencies
    for cred in deps.credentials_required:
        if cred not in os.environ:
            log.warning(f"Generator {generator.generator_type} requires {cred}")
```

**Use Case 2: Request Routing with Latency Hints**
```python
# Gateway routing decision
latency_budget_ms = 5000
generator = select_generator(user_request)
expected_latency = generator.upstream_dependencies.expected_latency_ms.get("p95", 1000)

if expected_latency > latency_budget_ms:
    return "Request may exceed latency budget, consider async execution"
```

**Use Case 3: Stability-Based Routing**
```python
# Gateway defaults to stable generators
if generator.upstream_dependencies.stability == "experimental":
    log.info("Using experimental generator, may have breaking changes")
```

---

### 3. Integration Contract

**File:** `chora-ecosystem-integration-tests/specs/integration-contract.md`
**Owner:** Joint
**Version:** 1.0

#### Guarantees from chora-compose

**Event Format Stability:**
- Event schema backward compatible for 6 months after major version bump
- New optional fields may be added in minor versions
- Required fields never removed without 6-month deprecation notice

**Capability Schema Versioning:**
- `capabilities://` resources follow semver
- Schema version included in response: `"schema_version": "1.0"`
- Consumers must handle unknown versions gracefully

**Tool Interface Contracts:**
- All tools follow MCP specification
- Tool signatures stable within major version
- New optional parameters may be added (backward compatible)

**Error Response Formats:**
- Structured errors with `error_code`, `error_message`, `details`
- Error codes stable across minor versions
- HTTP-style status codes where applicable (400s user error, 500s server error)

**Performance SLAs:**
- `capabilities://` resources: <100ms p95
- `generate_content` (demonstration): <1s p95
- `generate_content` (jinja2): <2s p95
- `generate_content` (code_generation): <5s p95
- `assemble_artifact`: <5s p95

#### Expectations from Gateways

**Namespace Adherence:**
- All tool calls prefixed: `chora:generate_content`, `chora:assemble_artifact`
- Gateway events use `gateway.*` namespace
- No namespace collisions

**Credential Management:**
- Gateway validates credentials before routing
- Credentials passed to backend via environment, NOT tool arguments
- No credential logging

**Trace Context Propagation:**
- Gateway generates `trace_id` for each request
- `trace_id` passed to backend (implementation-specific)
- Gateway correlates backend events via `trace_id`

**Error Handling:**
- Don't retry on 400-series errors (user error)
- Retry on 500-series errors with exponential backoff
- Respect 429 (rate limit) with backoff

**Rate Limiting Respect:**
- Honor `Retry-After` headers
- Respect concurrency limits from `capabilities://server`
- Implement gateway-level request queuing

#### Compatibility Matrix

| chora-compose | mcp-n8n | Compatible | Breaking Changes | Notes |
|---------------|---------|------------|------------------|-------|
| v1.1.0        | v0.1.0  | ✅         | None             | Basic gateway integration |
| v1.1.1        | v0.1.1+ | ✅         | None             | + Generator dependencies |
| v1.1.2        | v0.2.0+ | ✅         | None             | + Enhanced metadata |
| v1.2.0        | v0.3.0+ | ✅         | None             | + Context-aware capabilities |
| v1.3.0        | v0.4.0+ | ✅         | None             | + Dynamic discovery |

**Forward Compatibility:**
- chora v1.1.x can work with mcp-n8n v0.1.0 - v0.4.0 (gateways should handle missing features gracefully)
- mcp-n8n v0.3.0 REQUIRES chora v1.2.0+ (context-aware capabilities)

#### Breaking Change Policy

1. **Announcement:** 6 months before change
   - GitHub issue with `breaking-change` label
   - Deprecation warnings in logs
   - Migration guide published

2. **Transition Period:** 2 major versions
   - v1.x: Feature deprecated, warnings issued
   - v2.x: Feature still works, warnings intensified
   - v3.x: Feature removed

3. **Migration Support:**
   - Migration guide with code examples
   - Migration tool (if applicable)
   - Office hours for Q&A

---

## Coordination Schedule

### Week-by-Week Timeline

| Week | Chora Activity | mcp-n8n Activity | Coordination Event |
|------|---------------|------------------|-------------------|
| **1** | v1.1.1 dev | Phase 0 (foundation) | Mon: Kickoff, Wed: Schema review |
| **2** | v1.1.1 release | Phase 0 complete | Mon: Beta release, Fri: GA + checkpoint |
| **3** | v1.1.2 release | Phase 1 Week 1 | Fri: Enhanced metadata delivery |
| **4** | v1.2.0 design | Phase 1 Week 2 | Fri 2pm: Weekly check-in #1 |
| **5** | v1.2.0 design | Phase 1 Week 3 | Fri 2pm: Weekly check-in #2 |
| **6** | v1.2.0 design | Phase 1 Week 4 | Fri 2pm: Weekly check-in #3 + feedback doc review |
| **7** | v1.2.0-beta.1 | Phase 2 Week 1 | Mon: Beta release, Fri: Feedback session |
| **8** | v1.2.0-beta.2 dev | Phase 2 Week 2 | Bi-weekly check-in (optional) |
| **9** | v1.2.0-beta.2 | Phase 2 Week 3 | Mon: Beta release, Fri: Feedback session |
| **10** | v1.2.0 GA | Phase 2 Week 4 | Wed: GA release, Fri: Retrospective |
| **11-14** | v1.3.0 dev | Phase 3 | Bi-weekly check-ins + context bus design alignment |

### Recurring Meetings

#### Weekly Check-In (Week 3-6)
- **When:** Friday 2pm
- **Duration:** 30 minutes
- **Attendees:** Both team leads + 1-2 engineers
- **Agenda:**
  1. mcp-n8n integration updates (10 min)
  2. Blockers / questions (10 min)
  3. v1.2.0 requirements discussion (10 min)
- **Deliverable:** Meeting notes + action items

#### Beta Feedback Session (Week 7, 9)
- **When:** Friday after beta release
- **Duration:** 45 minutes
- **Attendees:** Both teams
- **Agenda:**
  1. Usage patterns observed (15 min)
  2. Issues discovered (15 min)
  3. Missing features / improvements (15 min)
- **Deliverable:** Prioritized feedback list

#### Retrospective (Week 10)
- **When:** Friday after v1.2.0 GA
- **Duration:** 60 minutes
- **Attendees:** Both teams
- **Agenda:**
  1. What went well (15 min)
  2. What to improve (15 min)
  3. Lessons learned (15 min)
  4. v1.3.0 / Phase 3 planning (15 min)
- **Deliverable:** Retrospective document

---

## Decision-Making Framework

### Autonomous Decisions (No Coordination Required)

**chora-compose Team:**
- Internal architecture choices
- Code organization and refactoring
- Tool implementation details (as long as MCP-compliant)
- Performance optimizations (as long as SLAs met)
- Test strategies
- Documentation structure
- Release timing (after dependency checkpoints met)

**mcp-n8n Team:**
- Gateway routing logic
- Workflow design and orchestration
- n8n-specific tooling
- Backend registry implementation
- Gateway performance optimizations
- Release timing (after chora dependencies available)

### Joint Decisions (Coordination Required)

**Schema Specifications:**
- Event schema (namespace, required fields, versioning)
- Generator dependency schema
- Integration contract

**Telemetry Format:**
- Event structure and fields
- Trace context format (OpenTelemetry compliance)
- Correlation patterns

**Integration Testing:**
- Test suite structure
- Ownership boundaries
- CI/CD integration

**Ecosystem Standards:**
- Interpretation of ecosystem-intent specs
- Compliance requirements (SBOM, SLSA)
- Breaking change policies

### Escalation Path

1. **Routine Coordination:** Weekly check-in (default venue)
2. **Technical Detail:** GitHub issue/discussion (async, public)
3. **Blocking Issue:** Ad-hoc sync meeting (scheduled within 24h)
4. **Standards Interpretation:** Ecosystem forum (if broader than 2 teams)

### Decision Documentation

All joint decisions documented in:
- This file (`CROSS_TEAM_COORDINATION.md`)
- Relevant spec files (`event-schema.md`, etc.)
- Meeting notes (in GitHub Discussions or wiki)

---

## Communication Protocols

### Primary Channels

1. **Scheduled Meetings:** Weekly check-ins, feedback sessions (see schedule)
2. **GitHub Issues:** Technical discussions, bug reports
3. **GitHub Discussions:** Design questions, RFC proposals
4. **Slack/Discord:** Quick questions, urgent coordination

### Communication Etiquette

**Response Time Expectations:**
- Slack/Discord: Best effort, no guarantee
- GitHub Issues: 48 hours (working days)
- Meeting invites: 24 hours

**Tagging:**
- `@chora-team` for chora-compose notifications
- `@mcp-n8n-team` for mcp-n8n notifications
- `urgent` label for blocking issues

**Meeting Norms:**
- Agenda shared 24h in advance
- Notes published within 24h
- Action items tracked in GitHub issues

### Conflict Resolution

If teams disagree on joint decision:

1. **Discussion:** Both sides present reasoning (async or sync)
2. **Compromise:** Look for middle ground
3. **Ecosystem Alignment:** Check if ecosystem-intent spec provides guidance
4. **Escalation:** If still unresolved, escalate to project stakeholders
5. **Document:** Record decision and rationale

---

## Integration Health Metrics

### Technical Metrics

**Integration Test Pass Rate:**
- Target: 100%
- Measured: Every release
- Alerting: Notify both teams on failure

**Event Schema Compliance:**
- Target: 100% of events match schema
- Measured: Via schema validator in tests
- Alerting: Fail CI/CD if non-compliant

**Performance SLAs:**
- Target: p95 latencies within contract
- Measured: Via integration benchmarks
- Alerting: Warn if within 10% of limit

**Backward Compatibility:**
- Target: Zero breaking changes without deprecation period
- Measured: Compatibility matrix validation
- Alerting: Block release if compatibility broken

### Coordination Effectiveness Metrics

**Meeting Attendance:**
- Target: 80%+ attendance at scheduled meetings
- Measured: Meeting notes
- Action: Reschedule if <80%

**Feedback Loop Latency:**
- Target: Feedback from mcp-n8n incorporated within 1 week
- Measured: Issue/PR close time
- Action: Escalate if >2 weeks

**Blocking Issues:**
- Target: Zero blocking issues >3 days
- Measured: Issue tracker (`blocking` label)
- Action: Daily check-ins if blocked

**Specification Drift:**
- Target: Zero instances of implementation diverging from spec
- Measured: Schema validation tests
- Action: Update spec or implementation to align

### Health Dashboard

Recommended metrics to track (optional, but helpful):

```
Integration Health Score:
├─ Test Pass Rate: 100% ✅
├─ Schema Compliance: 100% ✅
├─ Performance SLAs: 98% met ✅
├─ Meeting Attendance: 85% ✅
├─ Feedback Loop: 4 days avg ✅
└─ Blocking Issues: 0 open ✅

Overall: HEALTHY
```

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-17 | Initial version | chora-compose team |

---

## Approval

**chora-compose Team:** [ ] Approved
**mcp-n8n Team:** [ ] Approved

**Next Review:** Week 10 (v1.2.0 GA retrospective)
