---
title: mcp-n8n Changelog
status: active
last_updated: 2025-10-21
---

# Changelog

All notable changes to mcp-n8n will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

No unreleased changes yet.

## [0.5.0] - 2025-10-21

### Added
- Documentation refactor following Diátaxis framework
  - Complete product documentation (tutorials, how-tos, reference, explanation)
  - Improved dev documentation (ARCHITECTURE, DEVELOPMENT, TESTING, RELEASE, AGENTS)
  - Navigation indices and archive structure
- Project documentation (ROADMAP.md, SPRINT_STATUS.md, CHANGELOG.md)
- New how-to guides: troubleshoot.md, rollback-backend.md

### Changed
- Reorganized documentation into clear categories (dev-docs/, docs/, project/)
- Updated ROADMAP.md with Sprint 5 completion status
- Updated SPRINT_STATUS.md with current progress (100% documentation complete)
- Moved specifications to docs/reference/specs/
- Updated release scripts to use project/CHANGELOG.md location

### Removed
- Obsolete and duplicate documentation files (11 files deleted)
- Archived sprint-specific docs (7 files moved to docs/archive/)
- Empty directories (docs/testing/, docs/architecture/)

---

## [0.4.0] - 2025-01-17

### Added

**Sprint 5: Production Workflows**
- Daily Report workflow (`run_daily_report`)
  - Git commit aggregation from repositories
  - Event log querying with flexible time ranges
  - Statistics aggregation (tool usage, success rates, performance)
  - chora-compose template rendering integration
  - Type-safe `DailyReportResult` return object
- EventWorkflowRouter for event-driven automation
  - YAML-based event-to-workflow mapping configuration
  - Pattern matching engine (field-based rules)
  - Jinja2 parameter templating for workflow inputs
  - Hot-reload support with watchdog file monitoring
  - Trace correlation for all triggered workflows
- Test coverage: 49 unit tests (21 router + 28 workflow)
- API documentation: `docs/workflows/daily-report-api-reference.md`
- BDD scenarios: 23 Gherkin scenarios in feature files

**Phase 4.5: LLM-Intelligent Developer Experience**
- AGENTS.md machine-readable instructions (1,189 lines)
  - Project overview (Pattern P5 Gateway & Aggregator)
  - Dev environment tips and prerequisites
  - Testing instructions (test tiers, coverage, hooks)
  - PR instructions (branch naming, commit format, quality gates)
  - Common tasks for agents (5 detailed workflows)
  - Complete agent memory system documentation
- Memory infrastructure (`src/mcp_n8n/memory/`)
  - Event log with monthly JSONL partitions
  - Trace-based indexing for O(1) workflow lookups
  - Query API (by trace_id, event_type, status, time range)
  - Aggregation support (count, avg_duration)
- Knowledge graph (`src/mcp_n8n/memory/knowledge_graph.py`)
  - Zettelkasten-inspired markdown notes with YAML frontmatter
  - Bidirectional linking between notes
  - Tag-based organization and search
  - Confidence tracking (low/medium/high)
  - Content search (case-insensitive full-text)
- Agent profiles (`src/mcp_n8n/memory/profiles.py`)
  - Per-agent capability tracking
  - Skill level progression (novice → intermediate → expert)
  - Success/failure rate tracking
  - Learned pattern references
  - Session count and activity timestamps
- TraceContext context manager
  - Automatic `CHORA_TRACE_ID` generation (UUID v4)
  - Environment variable propagation to subprocesses
  - OpenTelemetry-compatible format
- Memory architecture documentation (`.chora/memory/README.md`, 454 lines)

**Phase 4.6: Agent Self-Service Tools**
- `chora-memory` CLI tool (Click framework)
  - `query` - Query events with filters (type, status, time, limit)
  - `trace` - Show workflow timeline for trace ID
  - `knowledge` subcommands (search/create/show)
  - `stats` - Memory system statistics dashboard
  - `profile` subcommands (show/list)
- JSON output mode for scripting (`--json` flag)
- Human-readable formatting for terminal use
- Comprehensive help documentation (`--help`)
- Time range parsing (`24h`, `7d`, ISO dates)

### Changed
- Updated pyproject.toml with click dependency (≥8.0.0)
- Added mypy configuration for click module
- Registered `chora-memory` entry point in scripts
- Enhanced .gitignore with memory directory exclusions

### Documentation
- Phase 4.5 summary document (`docs/PHASE_4.5_SUMMARY.md`)
- Phase 4.6 summary document (`docs/PHASE_4.6_SUMMARY.md`)
- Sprint 5 intent document with API reference
- Sprint 5 acceptance criteria (23 BDD scenarios)
- Memory system usage guide (query patterns, knowledge management)

---

## [0.3.0] - 2025-10-19

### Added

**Sprint 3: Event Monitoring**
- EventWatcher class (`src/mcp_n8n/event_watcher.py`)
  - Async file tailing with asyncio
  - Monitors `var/telemetry/events.jsonl` from chora-compose
  - Forwards events to EventLog for persistence
  - Optional webhook forwarding to n8n
  - Graceful shutdown support
- `get_events` MCP tool (`src/mcp_n8n/tools/event_query.py`)
  - Flexible event querying (type, status, source, time range, limit)
  - Trace-based filtering
  - Returns JSON arrays of matching events
  - Integrates with EventLog backend
- Test coverage: 25 tests (14 unit + 11 integration)
- Production-ready implementation with comprehensive error handling

**Sprint 3 Integration:**
- Gateway lifecycle integration
  - EventWatcher started automatically with gateway
  - Graceful shutdown on SIGINT/SIGTERM
  - Event emission for gateway lifecycle events
- PyPI-only dependency management
  - Migrated from git submodules to PyPI packages
  - Simplified installation (`pip install mcp-n8n`)
  - chora-compose v1.3.0 dependency

### Changed
- Updated integration strategy (PyPI-only, removed submodules)
- Improved Python requirement to >=3.12 (match chora-compose)
- Enhanced CI workflow with coverage requirements

### Documentation
- Sprint 3 completion summary
- Roadmap alignment analysis with chora-compose v1.3.0
- Integration strategy documentation

### Fixed
- CI workflow issues (submodule checkout, smoke tests)
- Import errors in integration tests
- Coverage reporting configuration

---

## [0.2.0] - 2025-10-17

### Added

**Sprint 1-2: Gateway Foundation**
- Pattern P5 Gateway & Aggregator architecture
- Backend registry (`src/mcp_n8n/backends/registry.py`)
  - Namespace-based routing (`chora:*`, `coda:*`)
  - Multi-backend aggregation
  - Backend lifecycle management (start/stop)
  - Tool discovery and registration
- Backend implementations
  - Chora Composer backend (STDIO subprocess)
  - Coda MCP backend (STDIO subprocess)
  - Abstract base class (`Backend`)
  - `StdioSubprocessBackend` for subprocess-based backends
- Gateway tools
  - `gateway_status` - Health monitoring
  - Backend status reporting
- Configuration management (`src/mcp_n8n/config.py`)
  - Pydantic-based configuration
  - Environment variable loading
  - BackendConfig model
  - GatewayConfig model
- Integration smoke tests (19/21 passing)

### Performance
- Gateway routing overhead: 0.0006ms (1600x faster than 1ms target)
- Backend startup: 1.97ms (2500x faster than 5000ms target)
- Concurrent routing: 0.02ms for 3 tools

### Documentation
- AGENTS.md initial version
- Integration validation documentation
- Sprint 1 completion summary
- chora-base adoption guides
- Compatibility matrix

---

## [0.1.0] - 2025-10-14

### Added
- Initial project structure
- FastMCP integration
- Basic MCP server setup
- Development environment configuration
  - Pre-commit hooks (ruff, mypy, formatting)
  - Test infrastructure (pytest, pytest-asyncio)
  - justfile for common tasks
- Basic .gitignore patterns
- pyproject.toml with dependencies

### Documentation
- README.md with project overview
- CONTRIBUTING.md with development guidelines
- Initial architecture documentation

---

## Version History

| Version | Release Date | Sprint | Key Features |
|---------|--------------|--------|--------------|
| 0.1.0 | 2025-10-14 | Sprint 0 | Initial setup, FastMCP integration |
| 0.2.0 | 2025-10-17 | Sprint 1-2 | Gateway architecture, backend routing |
| 0.3.0 | 2025-10-19 | Sprint 3 | Event monitoring, PyPI packaging |
| 0.4.0 | 2025-01-17 | Sprint 4-5 | Agent memory, production workflows |
| Unreleased | - | Phase 6 | Documentation refactor |

---

## Sprint Mapping

Each version corresponds to completed sprints:

- **v0.1.0:** Initial project setup
- **v0.2.0:** Sprint 1 (Validation) + Sprint 2 (Chora Foundation)
- **v0.3.0:** Sprint 3 (Event Monitoring)
- **v0.4.0:** Phase 4.5 (Memory Infrastructure) + Phase 4.6 (CLI Tools) + Sprint 5 (Production Workflows)
- **Unreleased:** Phase 6 (Documentation Refactor)

---

## Deprecated Features

None yet. All features introduced remain supported.

---

## Security

**No known security vulnerabilities.** All releases pass:
- Snyk security scans (zero critical/high issues)
- Dependency audits (no vulnerable packages)
- Code quality checks (ruff, mypy)

**Security Policy:**
- No credentials or PII stored in event logs
- API keys injected via environment variables only
- Subprocess isolation for backends
- Local-first memory storage (no network transmission)

---

## Migration Guides

### Upgrading from v0.3.0 to v0.4.0

**New Features:**
- Agent memory system (optional, opt-in)
- `chora-memory` CLI tool (requires click dependency)
- Production workflows (daily report, event router)

**Breaking Changes:**
None. v0.4.0 is fully backward compatible with v0.3.0.

**Action Required:**
None. All new features are additive.

**Recommended:**
- Install click for CLI tools: `pip install "mcp-n8n[cli]"`
- Review AGENTS.md for memory system usage
- Explore workflow templates in `src/mcp_n8n/workflows/`

### Upgrading from v0.2.0 to v0.3.0

**New Features:**
- Event monitoring (EventWatcher + get_events tool)
- PyPI packaging (no more submodules)

**Breaking Changes:**
None. v0.3.0 is fully backward compatible with v0.2.0.

**Action Required:**
1. Upgrade chora-compose to v1.3.0: `pip install --upgrade chora-compose`
2. Remove old submodule directory: `rm -rf chora-composer/`
3. Reinstall mcp-n8n: `pip install -e ".[dev]"`

**Configuration Changes:**
None required.

---

## Planned Releases

### v0.6.0 (Sprint 6: Advanced Workflows)
**Target:** 2025-11
- Workflow templates library
- Workflow versioning and deployment
- Enhanced error handling (retry, circuit breakers)
- Parallel execution support

### v0.7.0 (Sprint 7: n8n Integration)
**Target:** 2025-12
- Pattern N2 (n8n as MCP Server)
- Pattern N3 (n8n as MCP Client)
- Pattern N5 (Artifact Assembly Pipelines)
- Visual workflow orchestration

### v1.0.0 (Sprint 8: Production Hardening)
**Target:** 2026-01
- HTTP+SSE transport (multi-tenant support)
- Dynamic backend loading
- Health checks and circuit breakers
- Production deployment guides
- ≥95% test coverage
- Full security audit

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines and [dev-docs/DEVELOPMENT.md](../dev-docs/DEVELOPMENT.md) for setup instructions.

**Development Workflow:**
1. Create feature branch from `main`
2. Implement changes following TDD (tests first)
3. Run pre-commit hooks: `just lint test`
4. Submit PR with clear description
5. Wait for CI checks to pass
6. Merge after review

---

## Links

- **Repository:** https://github.com/anthropics/mcp-n8n
- **Documentation:** [docs/](../docs/)
- **Issue Tracker:** https://github.com/anthropics/mcp-n8n/issues
- **Releases:** https://github.com/anthropics/mcp-n8n/releases

---

**Last Updated:** 2025-10-21
**Current Version:** v0.4.0
**Next Release:** v0.6.0 (Sprint 6: Advanced Workflows)
