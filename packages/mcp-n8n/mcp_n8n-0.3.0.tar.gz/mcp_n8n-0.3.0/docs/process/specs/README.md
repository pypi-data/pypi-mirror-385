# Ecosystem Specifications

This directory contains specifications for cross-team integration and ecosystem standards.

## Purpose

These specifications define contracts between chora-compose (Platform/Layer 2) and ecosystem consumers like mcp-n8n (Gateway/Layer 3). They ensure interoperability, enable independent development, and provide clear integration contracts.

## Specifications

### [event-schema.md](event-schema.md)
**Status:** Active (v1.0)
**Owner:** Joint (chora-compose + mcp-n8n)

Defines the unified event schema for cross-service observability:
- Event namespace conventions (`chora.*`, `gateway.*`, `workflow.*`)
- Universal required/optional fields
- Event correlation patterns (trace context)
- Trace context propagation (environment variable `CHORA_TRACE_ID`)
- Versioning strategy
- Implementation guidance

**Key for:** Event monitoring, workflow tracking, distributed tracing

---

### [telemetry-capabilities-schema.md](telemetry-capabilities-schema.md)
**Status:** DRAFT (for Sprint 4)
**Owner:** Joint (chora-compose + mcp-n8n)

Defines the schema for the `capabilities://telemetry` MCP resource:
- Event type catalog with JSON schemas
- Metrics list
- Sampling configuration
- Export configuration (format, location, rotation)
- Trace context configuration

**Key for:** Gateway telemetry discovery, auto-documentation, schema validation

---

### generator-dependencies.md *(Planned for Sprint 2)*
**Status:** Planned
**Owner:** chora-compose (with mcp-n8n review)

Defines the schema for generator upstream dependencies:
- External service requirements
- Credential requirements
- Gateway routing hints (latency, stability, concurrency)
- Examples for all builtin generators

**Key for:** Gateway credential pre-validation, intelligent routing

---

### integration-contract.md *(Planned for v1.1.1)*
**Status:** Planned
**Owner:** Joint

Defines the integration contract between chora-compose and gateways:
- Guarantees from chora-compose (event stability, capability schema, performance SLAs)
- Expectations from gateways (namespace adherence, credential management, trace propagation)
- Compatibility matrix
- Breaking change policy

**Key for:** Version compatibility, upgrade planning, contract testing

---

## Lifecycle

### Specification Development Process

1. **Proposal:** Team proposes new spec or changes (GitHub Discussion or issue)
2. **Review:** Both teams review and provide feedback
3. **Approval:** Both teams approve (checkboxes in spec document)
4. **Implementation:** Teams implement per spec
5. **Validation:** Integration tests verify compliance
6. **Maintenance:** Specs updated per versioning policy

### Versioning

Specifications follow semver:
- **Patch (1.0.1):** Clarifications, typo fixes (no implementation changes)
- **Minor (1.1.0):** Additive changes (backward compatible)
- **Major (2.0.0):** Breaking changes (requires coordination)

### Backward Compatibility Policy

- Specifications maintained for 1 major version
- Breaking changes announced 6 months in advance
- Transition period: 2 major versions

---

## Related Documents

- [CROSS_TEAM_COORDINATION.md](../docs/CROSS_TEAM_COORDINATION.md) - Coordination framework and schedule
- [ROADMAP_GATEWAY_INTEGRATION.md](../docs/ROADMAP_GATEWAY_INTEGRATION.md) - Gateway integration roadmap
- [ecosystem-intent.md](../docs/ecosystem/ecosystem-intent.md) - Ecosystem-wide standards

---

## Contributing

To propose changes to a specification:

1. Create GitHub issue with `spec-change` label
2. Describe rationale and impact
3. Tag both teams for review
4. If approved, submit PR with spec updates
5. Both teams review and approve PR
6. Update implementation per new spec

**Note:** Specification changes require approval from both chora-compose and affected consumer teams (e.g., mcp-n8n).
