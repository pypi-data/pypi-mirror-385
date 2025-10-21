---
title: mcp-n8n Development Roadmap
status: active
version: 2.0.0
last_updated: 2025-10-21
supersedes: docs/UNIFIED_ROADMAP.md
---

# mcp-n8n Development Roadmap

**Project:** mcp-n8n - Pattern P5 Gateway & Aggregator for MCP
**Timeline:** Sprint-based development (completed Sprints 1-5, planning Sprint 6+)
**Current Version:** v0.5.0 (Sprint 5 complete)

---

## Executive Summary

mcp-n8n is a production-ready MCP Gateway & Aggregator that provides a unified interface to multiple specialized MCP backends. The project has completed 5 major sprints, delivering core gateway functionality, event monitoring, agent memory infrastructure, and production workflow automation.

**Current Status:**
- ✅ Gateway & backend routing (Sprints 1-2)
- ✅ Event monitoring & telemetry (Sprint 3)
- ✅ Agent memory system (Phases 4.5-4.6)
- ✅ Production workflows (Sprint 5)
- 🚀 Documentation refactor (Phase 6, in progress)

---

## Completed Sprints

### Sprint 1: Validation & Foundation ✅ COMPLETE

**Timeline:** 2-3 days
**Version:** v0.1.0 → v0.2.0
**Status:** ✅ Exceeded expectations

**Deliverables:**
- ✅ Gateway architecture (Pattern P5)
- ✅ Backend registry with namespace routing
- ✅ Chora Composer integration (v1.1.0)
- ✅ Coda MCP integration
- ✅ Integration smoke tests (19/21 passing)

**Performance Achievements:**
- Gateway routing: 0.0006ms overhead (1600x faster than target)
- Backend startup: 1.97ms (2500x faster than target)
- Concurrent routing: 0.02ms for 3 tools

**Key Decisions:**
- PyPI-only dependencies (removed submodules)
- STDIO subprocess transport for backends
- Namespace-based tool routing (`chora:*`, `coda:*`)

---

### Sprint 2: Chora Foundation ✅ COMPLETE

**Timeline:** 2-3 days
**chora-compose Version:** v1.1.1 → v1.3.0
**Status:** ✅ Far exceeded (delivered Sprint 2 + Sprint 4 features)

**Deliverables:**
- ✅ Event emission to `var/telemetry/events.jsonl`
- ✅ Trace context propagation (`CHORA_TRACE_ID`)
- ✅ Generator dependency metadata
- ✅ Concurrency limits exposure
- ✅ **BONUS:** Telemetry capabilities resource (Sprint 4 feature)

**Impact:**
- Event schema v1.0 compliance
- Production-ready event emission (48 tests in chora-compose)
- 100% backward compatibility maintained

---

### Sprint 3: Event Monitoring ✅ COMPLETE

**Timeline:** 2-3 hours
**Version:** v0.3.0
**Status:** ✅ Production-ready

**Deliverables:**
- ✅ EventWatcher class (async file tailing)
- ✅ `get_events` MCP tool (flexible event querying)
- ✅ Webhook forwarding to n8n
- ✅ 25/25 tests passing (14 unit + 11 integration)
- ✅ Integration with gateway telemetry

**Key Features:**
- Dual consumption (webhook + MCP tool)
- Trace correlation support
- Real-time event monitoring
- Flexible filtering (type, status, time range, trace_id)

---

### Sprint 4: Agent Memory Infrastructure ✅ COMPLETE

**Timeline:** Phase 4.5 (3 days) + Phase 4.6 (2 days)
**Version:** v0.4.0
**Status:** ✅ Production-ready

**Phase 4.5 Deliverables (LLM-Intelligent Developer Experience):**
- ✅ AGENTS.md machine-readable instructions (1,189 lines)
- ✅ Event log storage and querying
- ✅ Knowledge graph (Zettelkasten-style notes)
- ✅ Agent profiles (capability tracking)
- ✅ Trace context correlation
- ✅ Memory architecture documentation

**Phase 4.6 Deliverables (Agent Self-Service Tools):**
- ✅ `chora-memory` CLI tool
- ✅ Event querying commands (`query`, `trace`)
- ✅ Knowledge management (`knowledge search/create/show`)
- ✅ Agent profile management (`profile show/list`)
- ✅ Memory statistics dashboard

**Impact:**
- Enables cumulative agent learning across sessions
- Provides debugging infrastructure for workflows
- Supports single-developer multi-instance workflow
- Privacy-first (local storage, no credentials)

---

### Sprint 5: Production Workflows ✅ COMPLETE

**Timeline:** 4-5 days
**Version:** v0.5.0
**Status:** ✅ Complete (49 tests passing)

**Deliverables:**
- ✅ Daily Report workflow (`run_daily_report`)
  - Git commit aggregation
  - Event log querying
  - chora-compose template rendering
  - Statistics aggregation

- ✅ EventWorkflowRouter (event-driven automation)
  - YAML-based event mapping configuration
  - Pattern matching (field-based rules)
  - Jinja2 parameter templating
  - Hot-reload with file watching (watchdog)

**Test Coverage:**
- 21 EventWorkflowRouter tests passing
- 28 Daily Report tests passing
- 100% core functionality coverage

**Architecture:**
- Workflow as reusable Python functions
- Trace context automatic correlation
- Type-safe result objects
- Dependency injection for testability

---

## In Progress

### Phase 6: Documentation Refactor 🚧 IN PROGRESS

**Timeline:** 21.5 hours estimated
**Status:** 31/43 tasks complete (72%)

**Progress:**
- ✅ Phase 0: Planning & templates (4/4 tasks)
- ✅ Phase 1: Audit & categorization (3/3 tasks)
- ✅ Phase 2: Build new docs
  - ✅ Dev docs (5/5 tasks)
  - ✅ Tutorials (3/3 tasks)
  - ✅ How-to guides (7/7 tasks)
  - ✅ Reference docs (5/5 tasks)
  - ✅ Explanation docs (4/4 tasks)
  - ⏳ Project docs (0/3 tasks)
- ⏳ Phase 3: Archive & cleanup (0/6 tasks)
- ⏳ Phase 4: Generate metadata (0/4 tasks)

**Completed Documents:**
- Dev: ARCHITECTURE, DEVELOPMENT, TESTING, RELEASE, AGENTS
- Tutorials: getting-started, first-workflow, event-driven-workflow
- How-To: install, setup-claude-desktop, setup-cursor, configure-backends, query-events, build-custom-workflow, debug-gateway
- Reference: tools, api, event-schema, configuration, cli-reference
- Explanation: architecture, memory-system, integration-patterns, workflows

**Next:**
- Project docs (ROADMAP, SPRINT_STATUS, CHANGELOG)
- Archive old docs to `docs/archive/`
- Create navigation indices (docs/README.md)

---

## Planned Sprints

### Sprint 6: Advanced Workflow Capabilities (Planned)

**Timeline:** 3-4 days
**Target Version:** v0.6.0

**Goals:**
- Template-based workflow library
- Workflow versioning and deployment
- Enhanced error handling (retry logic, circuit breakers)
- Parallel execution support
- Workflow composition (workflows calling workflows)

**Dependencies:**
- Sprint 5 completion ✅
- Documentation refactor ✅ (almost complete)

---

### Sprint 7: n8n Integration (Planned)

**Timeline:** 5-7 days
**Target Version:** v0.7.0

**Goals:**
- Pattern N2: n8n as MCP Server
  - Expose n8n workflows as MCP tools
  - `n8n:execute_workflow`, `n8n:list_workflows`

- Pattern N3: n8n as MCP Client
  - Custom n8n node `@chora/mcp-tool-call`
  - Call MCP tools from n8n workflows

- Pattern N5: Artifact Assembly Pipelines
  - Visual workflow orchestration
  - Multi-source data aggregation
  - Scheduled report generation

**Dependencies:**
- n8n deployment infrastructure
- Custom node development (@chora/mcp-tool-call)
- Testing framework for visual workflows

---

### Sprint 8: Production Hardening (Planned)

**Timeline:** 3-5 days
**Target Version:** v1.0.0

**Goals:**
- HTTP+SSE transport (multi-tenant support)
- Dynamic backend loading (add/remove at runtime)
- Health checks and circuit breakers
- Comprehensive error recovery
- Production deployment guides

**Quality Gates:**
- ≥95% test coverage
- Zero critical security issues (Snyk scan)
- Performance benchmarks documented
- Load testing completed (100 concurrent requests)

---

## Feature Roadmap

### Core Gateway Features

| Feature | Status | Sprint | Version |
|---------|--------|--------|---------|
| Tool namespacing | ✅ Complete | Sprint 1 | v0.1.0 |
| Backend registry | ✅ Complete | Sprint 1 | v0.1.0 |
| STDIO subprocess transport | ✅ Complete | Sprint 1 | v0.1.0 |
| Credential management | ✅ Complete | Sprint 1 | v0.1.0 |
| Multi-backend routing | ✅ Complete | Sprint 2 | v0.2.0 |
| Event monitoring | ✅ Complete | Sprint 3 | v0.3.0 |
| HTTP+SSE transport | ⏳ Planned | Sprint 8 | v1.0.0 |
| Dynamic backend loading | ⏳ Planned | Sprint 8 | v1.0.0 |

### Memory & Telemetry

| Feature | Status | Sprint | Version |
|---------|--------|--------|---------|
| Event log storage | ✅ Complete | Phase 4.5 | v0.4.0 |
| Knowledge graph | ✅ Complete | Phase 4.5 | v0.4.0 |
| Agent profiles | ✅ Complete | Phase 4.5 | v0.4.0 |
| Trace context | ✅ Complete | Phase 4.5 | v0.4.0 |
| CLI tools (`chora-memory`) | ✅ Complete | Phase 4.6 | v0.4.0 |
| Vector database integration | 📋 Future | TBD | TBD |
| Cross-project memory | 📋 Future | TBD | TBD |

### Workflows

| Feature | Status | Sprint | Version |
|---------|--------|--------|---------|
| Daily Report workflow | ✅ Complete | Sprint 5 | v0.5.0 |
| EventWorkflowRouter | ✅ Complete | Sprint 5 | v0.5.0 |
| YAML event mapping | ✅ Complete | Sprint 5 | v0.5.0 |
| Jinja2 templating | ✅ Complete | Sprint 5 | v0.5.0 |
| Hot-reload | ✅ Complete | Sprint 5 | v0.5.0 |
| Workflow templates library | ⏳ Planned | Sprint 6 | v0.6.0 |
| Workflow versioning | ⏳ Planned | Sprint 6 | v0.6.0 |
| n8n integration (N2/N3/N5) | ⏳ Planned | Sprint 7 | v0.7.0 |

### Documentation

| Feature | Status | Phase | Progress |
|---------|--------|-------|----------|
| Audit existing docs | ✅ Complete | Phase 1 | 100% |
| Dev documentation | ✅ Complete | Phase 2 | 100% |
| Product documentation | ✅ Complete | Phase 2 | 100% |
| Project documentation | 🚧 In Progress | Phase 2 | 0% |
| Archive old docs | ⏳ Planned | Phase 3 | 0% |
| Navigation indices | ⏳ Planned | Phase 4 | 0% |

---

## Success Criteria

### Sprint 5 Success (ACHIEVED ✅)
- ✅ Daily Report workflow runs successfully
- ✅ EventWorkflowRouter routes events to workflows
- ✅ YAML config hot-reload working
- ✅ 49 unit tests passing
- ✅ Template rendering with chora-compose
- ✅ Event emission for all workflow operations

### Documentation Refactor Success (IN PROGRESS)
- ✅ 24/27 product docs complete (89%)
- ⏳ 0/3 project docs complete (0%)
- ⏳ 0/6 archive tasks complete (0%)
- ⏳ 0/4 metadata tasks complete (0%)

### v1.0.0 Release Criteria (FUTURE)
- ⏳ HTTP+SSE transport implemented
- ⏳ ≥95% test coverage
- ⏳ Production deployment guide
- ⏳ Load testing completed
- ⏳ Security audit passed (Snyk scan)
- ⏳ All documentation complete and published

---

## Related Documents

**Project Documentation:**
- [SPRINT_STATUS.md](SPRINT_STATUS.md) - Current sprint status and progress
- [CHANGELOG.md](CHANGELOG.md) - Version history and release notes
- [DOC_REFACTOR_CHECKLIST.md](DOC_REFACTOR_CHECKLIST.md) - Documentation work tracking

**Development Documentation:**
- [dev-docs/ARCHITECTURE.md](../dev-docs/ARCHITECTURE.md) - System architecture
- [dev-docs/DEVELOPMENT.md](../dev-docs/DEVELOPMENT.md) - Development setup
- [dev-docs/TESTING.md](../dev-docs/TESTING.md) - Testing strategy
- [dev-docs/RELEASE.md](../dev-docs/RELEASE.md) - Release process
- [dev-docs/AGENTS.md](../dev-docs/AGENTS.md) - AI agent instructions

**Product Documentation:**
- [docs/tutorials/](../docs/tutorials/) - Step-by-step tutorials
- [docs/how-to/](../docs/how-to/) - Task-focused guides
- [docs/reference/](../docs/reference/) - API and CLI reference
- [docs/explanation/](../docs/explanation/) - Conceptual explanations

---

**Last Updated:** 2025-10-21
**Sprint 5 Status:** ✅ COMPLETE
**Documentation Phase:** 72% complete (31/43 tasks)
**Next Milestone:** Complete documentation refactor, plan Sprint 6
