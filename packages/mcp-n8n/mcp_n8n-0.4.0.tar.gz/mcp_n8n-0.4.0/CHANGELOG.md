# Changelog

All notable changes to mcp-n8n will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

No unreleased changes yet.

## [0.4.0] - 2025-10-21

### Added - Sprint 5: Production Workflows

**Event-Driven Workflow Orchestration:**
- EventWorkflowRouter ([src/mcp_n8n/workflows/event_router.py](src/mcp_n8n/workflows/event_router.py))
  - Event-to-workflow routing from YAML configuration
  - Pattern matching with field-based rules (nested dict support)
  - Jinja2 parameter templating ({{event.data.*}} syntax)
  - Hot-reload with file watching (watchdog library)
  - Thread-safe config reload
  - 21 unit tests passing

**Daily Report Workflow:**
- Complete workflow implementation ([src/mcp_n8n/workflows/daily_report.py](src/mcp_n8n/workflows/daily_report.py))
  - Git commit retrieval and parsing
  - Event log querying integration
  - Statistics aggregation (tool_calls, success_rate, durations)
  - chora-compose template rendering integration
  - 28 unit tests passing

**Configuration & Templates:**
- Event mapping YAML configuration ([config/event_mappings.yaml](config/event_mappings.yaml))
- chora-compose template storage ([chora-configs/templates/](chora-configs/templates/))
- Content configuration ([chora-configs/content/](chora-configs/content/))
- Hot-reloadable workflow routing

**Documentation:**
- Sprint 5 intent document with API reference
- Architecture clarification for chora-compose integration
- 23 BDD scenarios documented (Gherkin)
- Workflow integration patterns

**Test Coverage:**
- 49 Sprint 5 unit tests passing (100% core functionality)
- All mypy type checks passing
- Integration with existing 52 integration tests
- Total: 101 passing tests

**Dependencies:**
- Added `watchdog==6.0.0` for file system monitoring

### Changed - Migration to PyPI-only Dependencies
- Removed all git submodules (chora-compose, chora-platform, mcp-server-coda)
- Simplified to use only PyPI package: `chora-compose>=1.3.0`
- Updated configuration to require PyPI installation only
- Removed submodule checkout from CI/CD workflows
- Updated documentation to reflect PyPI-only approach

### Deprecated
- Legacy daily_report tests ([tests/workflows/test_daily_report.py](tests/workflows/test_daily_report.py))
  - Incompatible with refactored TDD API
  - 19 tests skipped (replaced by 28 new comprehensive tests)

## [0.3.0] - 2025-10-19

### Changed - Simplified chora-compose Integration

**Configuration:**
- Rewrote `get_chora_composer_config()` with hybrid detection ([src/mcp_n8n/config.py](src/mcp_n8n/config.py:102-153))
  - Automatically detects package installation vs git submodule
  - No more hardcoded Poetry venv paths
  - Portable across machines and environments
  - Clear error messages with installation instructions

**Dependencies:**
- Added `chora-compose>=1.3.0` as package dependency ([pyproject.toml](pyproject.toml:18))
- Added mypy override for chora_compose module ([pyproject.toml](pyproject.toml:79-81))

**Git Submodules:**
- Added `vendors/chora-compose/` submodule pinned to v1.3.0
- Enables development with specific chora-compose versions
- Supports simultaneous development of both projects

**Documentation:**
- Updated [README.md](README.md) with dual installation methods (production vs development)
- Added Dependencies section explaining hybrid detection
- Updated [CONTRIBUTING.md](CONTRIBUTING.md) with submodule management guide
- Added common submodule commands and workflows

### Benefits

- **Production:** Simple `pip install mcp-n8n` with automatic chora-compose installation
- **Development:** Git submodules for reproducible builds and integration testing
- **Portability:** No machine-specific paths, works on any system
- **Flexibility:** Supports both package and submodule workflows seamlessly

## [0.2.0] - 2025-10-17

### Added - Phase 0: Foundation Validation

**Integration Validation:**
- End-to-end integration tests with real chora-composer backend (8 new tests)
- Performance baseline documentation ([docs/PERFORMANCE_BASELINE.md](docs/PERFORMANCE_BASELINE.md))
- Environment configuration improvements (validation_alias for unprefixed env vars)
- Integration test framework (mock + real backends, 21 tests total)
- Sprint validation documentation ([docs/SPRINT_1_VALIDATION.md](docs/SPRINT_1_VALIDATION.md))

**Performance Achievements:**
- Gateway routing overhead: 0.0006ms per call (1600x faster than target)
- Backend startup time: 1.97ms (2500x faster than target)
- Concurrent routing: 0.02ms for 3 tools
- All performance targets exceeded by 5-2500x

**Test Results:**
- 19 passed, 2 skipped (timeout/crash detection - future features)
- 8 e2e tests with real chora-composer execution
- 11 mock backend tests
- 2 chora-composer conditional tests

### Added - Phase 4.5: LLM-Intelligent Developer Experience

**Machine-Readable Instructions:**
- AGENTS.md (1,189 lines) - comprehensive agent workflow documentation
- P5 Gateway & Aggregator architecture for AI agents
- Tool namespacing patterns documentation
- Common tasks with detailed examples

**Memory Infrastructure (.chora/memory/):**
- Event log with trace correlation ([src/mcp_n8n/memory/event_log.py](src/mcp_n8n/memory/event_log.py))
  - Append-only JSONL storage with monthly partitions
  - Query by trace_id, event_type, status, time range
  - Aggregate statistics (count, avg_duration)
- Trace context ([src/mcp_n8n/memory/trace.py](src/mcp_n8n/memory/trace.py))
  - CHORA_TRACE_ID environment variable propagation
  - TraceContext context manager for scoped trace IDs
  - OpenTelemetry-compatible UUID format
- Knowledge graph ([src/mcp_n8n/memory/knowledge_graph.py](src/mcp_n8n/memory/knowledge_graph.py))
  - Zettelkasten-inspired markdown notes with YAML frontmatter
  - Bidirectional linking between notes
  - Tag-based organization and search
  - Confidence tracking (low/medium/high)
- Memory system architecture documentation (.chora/memory/README.md - 454 lines)

**Gateway Integration:**
- Event emission for lifecycle events (gateway.started, gateway.backend_registered, gateway.backend_started, gateway.stopped)
- TraceContext integration for workflow correlation
- Foundation for future tool call tracing

### Added - Phase 4.6: Agent Self-Service Tools

**chora-memory CLI Tool:**
- `chora-memory query` - Query events by type, status, time range
- `chora-memory trace` - Show workflow timeline by trace_id
- `chora-memory knowledge` - Search, create, show knowledge notes
- `chora-memory stats` - Display memory system statistics
- `chora-memory profile` - Manage agent profiles

**Agent Profile System:**
- AgentProfile tracking capabilities, preferences, sessions
- AgentProfileManager for CRUD operations
- Skill level progression (novice → intermediate → expert)
- Success/failure tracking per capability
- Learned pattern references

**Features:**
- Bash-accessible commands for agents
- Human-readable and JSON output modes
- Time range parsing ("24h", "7d", "2025-01-17")
- Comprehensive help documentation

### Added - Development Tooling

- Production-ready development environment with pinned dependencies
- Smoke test suite for quick validation (<30 seconds)
- Environment validation scripts (`check-env.sh`, `venv-create.sh`, `venv-clean.sh`)
- Configuration samples for Claude Desktop and Cursor (stable + dev modes)
- Coverage threshold enforcement (85%)
- GitHub Actions workflow for smoke tests
- `.python-version` for consistent Python version (3.11.9)
- `.editorconfig` for cross-editor consistency
- Dual configuration support (stable vs dev backends)
- Configuration toggle documentation

### Changed
- Pinned all dev dependencies to specific versions for reproducibility
- Enhanced `justfile` with environment management commands
- Improved documentation structure with configuration guides
- Updated README.md with Phase 0 and agent infrastructure features
- Environment configuration now accepts both prefixed (MCP_N8N_*) and unprefixed env vars

### Fixed
- API key loading from environment variables (added validation_alias support)
- Test configuration to support both prefixed and unprefixed environment variables

## [0.1.0] - 2025-10-17

### Added
- Initial implementation of Pattern P5 (Gateway & Aggregator)
- Chora Composer integration as exclusive artifact creator
- Coda MCP integration for data operations
- Tool namespacing system (chora:*, coda:*)
- FastMCP-based server with STDIO transport
- Backend registry for managing multiple MCP servers
- Configuration-driven backend management
- Graceful startup/shutdown with lifecycle management
- Pre-commit hooks (ruff, mypy, black, formatting checks)
- Task automation with `justfile` (15+ commands)
- Development scripts (setup, integration-test, handoff)
- GitHub Actions CI/CD (test, lint workflows)
- Comprehensive documentation (README, ARCHITECTURE, GETTING_STARTED)
- Context-switch automation for single-developer multi-instance workflow

### Backend Integrations
- **chora-composer**: Artifact generation and assembly tools
  - `chora:generate_content` - Generate content from templates
  - `chora:assemble_artifact` - Assemble multi-part artifacts
  - `chora:list_generators` - Discover available generators
  - `chora:validate_content` - Validate configurations
- **coda-mcp**: Data operations on Coda documents
  - `coda:list_docs` - List Coda documents
  - `coda:list_tables` - List tables in a document
  - `coda:list_rows` - List rows from a table
  - `coda:create_hello_doc_in_folder` - Create sample documents

### Documentation
- Project README with quick start guide
- Architecture documentation (P5 pattern implementation)
- Getting started guide with examples
- Quick reference card for common tasks
- Integration summary and roadmap
- Context-switching protocols for multi-instance development

### Testing
- Unit tests for configuration and routing
- Type checking with mypy (strict mode)
- Linting with ruff and black
- Test coverage reporting

### Development Experience
- Pre-commit hooks prevent bad commits
- Justfile provides consistent task interface
- Scripts automate common workflows
- Documentation covers setup through deployment

---

## Release History

- **v0.1.0** (2025-10-17): Initial release with P5 Gateway & Aggregator pattern
- **Unreleased**: Production-ready development environment and tooling maturity

---

## Upgrade Guide

### From Pre-Release to 0.1.0

This is the initial release, so no upgrade needed.

### From 0.1.0 to Unreleased

1. **Update dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Install pre-commit hooks** (if not already done):
   ```bash
   pre-commit install
   ```

3. **Create virtual environment** (recommended):
   ```bash
   ./scripts/venv-create.sh
   source .venv/bin/activate
   ```

4. **Run environment check:**
   ```bash
   just check-env
   ```

5. **Run smoke tests:**
   ```bash
   just smoke
   ```

6. **Review new configuration options:**
   - See `.config/README.md` for dual config setup (stable vs dev)
   - Update your Claude Desktop or Cursor config if using dev mode

---

## Notes

- This project follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format
- Version numbers follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- All notable changes should be documented here before release
- See [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) for release process (Phase 3)
