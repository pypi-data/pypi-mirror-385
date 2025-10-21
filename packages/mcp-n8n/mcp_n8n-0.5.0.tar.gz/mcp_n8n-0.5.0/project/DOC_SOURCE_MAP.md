---
title: Documentation Source Map
type: project
status: current
created: 2025-10-21
purpose: Map new docs to ground truth sources for verification
---

# Documentation Source Map

**Purpose:** Map each new document to its ground truth sources (code, tests, existing docs)

**Usage:** When creating a new doc, consult this map to find authoritative sources

---

## Summary

This map connects the 22 new documents in Phase 2 to their ground truth sources from:
- Source code (`src/mcp_n8n/`)
- Tests (`tests/`)
- Existing documentation (`docs/`, root files)
- Configuration files (`.config/`, `pyproject.toml`, etc.)

---

## Dev Docs → Ground Truth (7 documents)

| Task | New Document | Ground Truth Sources | Type of Change |
|------|--------------|---------------------|----------------|
| 2.1 | `dev-docs/ARCHITECTURE.md` | `ARCHITECTURE.md` + `src/mcp_n8n/gateway.py` + `src/mcp_n8n/backends/registry.py` | Improve: Add component diagrams |
| 2.2 | `dev-docs/DEVELOPMENT.md` | `DEVELOPMENT.md` + `justfile` + `scripts/*.sh` | Improve: Add justfile reference |
| 2.3 | `dev-docs/TESTING.md` | `tests/` structure + `process/bdd-workflow.md` + `process/tdd-workflow.md` | NEW: Test pyramid + workflows |
| 2.4 | `dev-docs/RELEASE.md` | `RELEASE_CHECKLIST.md` + `ROLLBACK_PROCEDURE.md` | NEW: Merge both documents |
| 2.5 | `dev-docs/AGENTS.md` | `AGENTS.md` (current) | Update: Links to new structure |
| – | `dev-docs/CONTRIBUTING.md` | `CONTRIBUTING.md` (current) | Keep as-is |
| – | `dev-docs/TROUBLESHOOTING.md` | `TROUBLESHOOTING.md` (current) | Keep as-is |

---

## Product Docs: Tutorials → Ground Truth (3 documents)

| Task | New Document | Ground Truth Sources | Test Extraction | Time |
|------|--------------|---------------------|----------------|------|
| 2.6 | `docs/tutorials/getting-started.md` | `README.md` (lines 52-150) + `tests/smoke/test_gateway_startup.py` + `tests/smoke/test_chora_routing.py` | Yes | 5 min |
| 2.7 | `docs/tutorials/first-workflow.md` | `src/mcp_n8n/workflows/daily_report.py` + `tests/features/daily_report.feature` (AC 11-14) | Yes | 30 min |
| 2.8 | `docs/tutorials/event-driven-workflow.md` | `tests/features/sprint_5_workflows.feature` (AC 15-17) + `src/mcp_n8n/workflows/event_router.py` | Yes | 30 min |

---

## Product Docs: How-To Guides → Ground Truth (7 documents)

| Task | New Document | Ground Truth Sources | Notes |
|------|--------------|---------------------|-------|
| 2.9 | `docs/how-to/install.md` | `README.md` (install section) + `pyproject.toml` | Production vs dev install |
| 2.10 | `docs/how-to/configure-backends.md` | `src/mcp_n8n/config.py` + `src/mcp_n8n/backends/base.py` + `.env.example` | Adding custom backends |
| 2.11 | `docs/how-to/setup-claude-desktop.md` | `.config/claude-desktop.example.json` + `.config/README.md` | Stable + dev modes |
| 2.12 | `docs/how-to/setup-cursor.md` | `.config/cursor-mcp.example.json` + `.config/README.md` | Cursor-specific config |
| 2.13 | `docs/how-to/query-events.md` | `src/mcp_n8n/memory/event_log.py` + `src/mcp_n8n/cli/` + `PHASE_4.6_SUMMARY.md` | Event query patterns |
| 2.14 | `docs/how-to/build-custom-workflow.md` | `src/mcp_n8n/workflows/event_router.py` + `tests/features/sprint_5_workflows.feature` (AC 4-10) | YAML mapping config |
| 2.15 | `docs/how-to/debug-gateway.md` | `TROUBLESHOOTING.md` + `src/mcp_n8n/logging_config.py` + `justfile` | Debug patterns |

---

## Product Docs: Reference → Ground Truth (5 documents)

| Task | New Document | Ground Truth Sources | Test Extraction |
|------|--------------|---------------------|----------------|
| 2.16 | `docs/reference/tools.md` | `src/mcp_n8n/gateway.py` (tool defs) + `tests/features/*.feature` | Yes (all examples) |
| 2.17 | `docs/reference/api.md` | `process/specs/` + MCP protocol | No |
| 2.18 | `docs/reference/event-schema.md` | `process/specs/event-schema.md` + `src/mcp_n8n/memory/event_log.py` | Yes |
| 2.19 | `docs/reference/configuration.md` | `src/mcp_n8n/config.py` + `.env.example` | No |
| 2.20 | `docs/reference/cli-reference.md` | `src/mcp_n8n/cli/` + `PHASE_4.6_SUMMARY.md` | No |

---

## Product Docs: Explanation → Ground Truth (4 documents)

| Task | New Document | Ground Truth Sources | Notes |
|------|--------------|---------------------|-------|
| 2.21 | `docs/explanation/architecture.md` | `ARCHITECTURE.md` (simplified) + `src/mcp_n8n/gateway.py` | Pattern P5 for users |
| 2.22 | `docs/explanation/memory-system.md` | `PHASE_4.5_SUMMARY.md` + `PHASE_4.6_SUMMARY.md` + `src/mcp_n8n/memory/` | Merge summaries |
| 2.23 | `docs/explanation/integration-patterns.md` | `ecosystem/n8n-solution-neutral-intent.md` + `ecosystem/integration-analysis.md` | Extract P5/N2/N3/N5 only |
| 2.24 | `docs/explanation/workflows.md` | `src/mcp_n8n/workflows/` + `tests/features/sprint_5_workflows.feature` | Event-driven model |

---

## Project Docs → Ground Truth (3 documents)

| Task | New Document | Ground Truth Sources | Changes |
|------|--------------|---------------------|---------|
| 2.25 | `project/ROADMAP.md` | `UNIFIED_ROADMAP.md` (base) + `ROADMAP.md` (reference) | Mark Sprint 5 complete |
| 2.26 | `project/SPRINT_STATUS.md` | `SPRINT_STATUS.md` (current) | Update to current sprint |
| 2.27 | `project/CHANGELOG.md` | Git log + sprint summaries | NEW: Version history |

---

## Ground Truth Quick Reference

### Source Code Modules

**Gateway & Backends:**
- `src/mcp_n8n/gateway.py` - Main entry, tool definitions
- `src/mcp_n8n/backends/registry.py` - Backend lifecycle, routing
- `src/mcp_n8n/backends/base.py` - Backend interface
- `src/mcp_n8n/backends/chora_composer.py` - Chora integration
- `src/mcp_n8n/backends/coda_mcp.py` - Coda integration
- `src/mcp_n8n/config.py` - Configuration classes
- `src/mcp_n8n/credential_validator.py` - Credential validation

**Memory System:**
- `src/mcp_n8n/memory/event_log.py` - JSONL event persistence
- `src/mcp_n8n/memory/knowledge_graph.py` - Cross-session learning
- `src/mcp_n8n/memory/trace.py` - Trace correlation
- `src/mcp_n8n/memory/profiles.py` - Agent profiles

**Workflows:**
- `src/mcp_n8n/workflows/daily_report.py` - Daily report workflow
- `src/mcp_n8n/workflows/event_router.py` - Event→workflow routing
- `src/mcp_n8n/workflows/__main__.py` - CLI entry

**Tools & CLI:**
- `src/mcp_n8n/tools/event_query.py` - Event query tool
- `src/mcp_n8n/cli/` - chora-memory CLI commands

### Test Files

**BDD Features:**
- `tests/features/event_monitoring.feature` - Event watching (Sprint 3)
- `tests/features/daily_report.feature` - Daily report (Sprint 3)
- `tests/features/sprint_5_workflows.feature` - Workflows (Sprint 5)

**Integration Tests:**
- `tests/integration/test_chora_composer_e2e.py`
- `tests/integration/test_gateway_subprocess.py`
- `tests/integration/test_backend_jsonrpc.py`

**Smoke Tests:**
- `tests/smoke/test_gateway_startup.py`
- `tests/smoke/test_chora_routing.py`
- `tests/smoke/test_coda_routing.py`

### Configuration Files

- `pyproject.toml` - Project metadata
- `.env.example` - Environment variables
- `.config/claude-desktop.example.json`
- `.config/cursor-mcp.example.json`
- `justfile` - Task automation

### Existing Documentation (Extract From)

**To Dev Docs:**
- `ARCHITECTURE.md` → dev-docs/ARCHITECTURE.md
- `DEVELOPMENT.md` → dev-docs/DEVELOPMENT.md
- `RELEASE_CHECKLIST.md` + `ROLLBACK_PROCEDURE.md` → dev-docs/RELEASE.md

**To Project Docs:**
- `UNIFIED_ROADMAP.md` → project/ROADMAP.md
- `SPRINT_STATUS.md` → project/SPRINT_STATUS.md

**To Explanation:**
- `PHASE_4.5_SUMMARY.md` + `PHASE_4.6_SUMMARY.md` → docs/explanation/memory-system.md
- `ecosystem/*.md` → docs/explanation/integration-patterns.md

**To Reference:**
- `process/specs/event-schema.md` → docs/reference/event-schema.md
- `process/specs/*` → docs/reference/api.md

---

## Extraction Guidelines by Doc Type

### Tutorials
- Extract from smoke tests for step-by-step
- Extract from BDD features for expected behavior
- Format: Each step has expected output, copy-pasteable code
- Completion time: 5-30 minutes

### How-To Guides
- Extract from config files for setup
- Extract from code modules for implementation
- Format: Problem statement, 2-3 approaches, troubleshooting
- Include: Pros/cons of each approach

### Reference
- Extract from code docstrings for parameters
- Extract from BDD features for examples
- Format: Complete parameter table, 3-5 examples, test cases
- Test extraction: Mark all examples

### Explanation
- Extract from existing architecture docs (simplify)
- Extract from summaries for context
- Format: Context, design decisions, diagrams, comparisons
- Focus: Why, not how

---

## Verification Checklist

For each new doc, verify:
- [ ] All sources cited in frontmatter
- [ ] Examples extracted from actual code/tests
- [ ] Links to related docs included
- [ ] Test extraction marked if applicable
- [ ] Ground truth sources match this map
- [ ] Template structure followed

---

**Created:** 2025-10-21
**Last Updated:** 2025-10-21
**Next Use:** Phase 2 - Building new documentation
