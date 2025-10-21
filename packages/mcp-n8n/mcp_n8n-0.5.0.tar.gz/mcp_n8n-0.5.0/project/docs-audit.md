---
title: Documentation Audit for Refactor
type: project
status: draft
created: 2025-10-21
purpose: Categorize existing docs into KEEP/EXTRACT/ARCHIVE/DELETE
---

# Documentation Audit

**Purpose:** Categorize all existing documentation into four actions:
- **KEEP:** Documents that remain useful in current form
- **EXTRACT:** Documents with valuable content to incorporate into new structure
- **ARCHIVE:** Documents to move to `docs/archive/` for historical reference
- **DELETE:** Obsolete documents to remove entirely

**Source Locations:** Root directory + `docs/` subdirectories

---

## Summary

- **Total Documents:** 54
- **KEEP:** 6 (11%)
- **EXTRACT:** 23 (43%)
- **ARCHIVE:** 24 (44%)
- **DELETE:** 1 (2%)

---

## KEEP (6 documents)

Documents that remain useful as-is or with minimal updates.

| File | Type | Status | Rationale |
|------|------|--------|-----------|
| `README.md` | Root | ✅ Keep | Main project entry point, basic install info |
| `CONTRIBUTING.md` | Root | ✅ Keep | PR process and code style still relevant |
| `TROUBLESHOOTING.md` | docs/ | ✅ Keep | User-facing debugging (to become dev-docs/TROUBLESHOOTING.md) |
| `GETTING_STARTED.md` | Root | ✅ Keep | Useful quick start reference |
| `QUICK_REFERENCE.md` | Root | ✅ Keep | Useful command/endpoint reference |
| `LICENSE` | Root | ✅ Keep | Required legal document |

---

## EXTRACT (23 documents)

Documents with valuable content to extract and incorporate into new documentation structure.

### Core Technical Docs → Dev Docs

| File | Type | New Location | Extraction Purpose |
|------|------|-------------|-------------------|
| `ARCHITECTURE.md` | docs/ | dev-docs/ARCHITECTURE.md | Add component diagrams and backend integration details |
| `DEVELOPMENT.md` | docs/ | dev-docs/DEVELOPMENT.md | Add justfile commands reference |
| `testing/INTEGRATION_TESTING.md` | docs/ | dev-docs/TESTING.md | BDD/TDD workflow and test organization |
| `RELEASE_CHECKLIST.md` | docs/ | dev-docs/RELEASE.md | Release process and checklist |
| `ROLLBACK_PROCEDURE.md` | docs/ | dev-docs/RELEASE.md | Merge rollback procedures |

### Roadmap/Strategy → Project Docs

| File | Type | New Location | Extraction Purpose |
|------|------|-------------|-------------------|
| `UNIFIED_ROADMAP.md` | docs/ | project/ROADMAP.md | Use as base, mark Sprint 5 complete |
| `ROADMAP.md` | docs/ | project/ROADMAP.md | Consolidate roadmapping strategy |
| `PERFORMANCE_BASELINE.md` | docs/ | project/ROADMAP.md | Performance milestone tracking |

### Specifications → Reference Docs

| File | Type | New Location | Extraction Purpose |
|------|------|-------------|-------------------|
| `process/specs/event-schema.md` | docs/ | docs/reference/event-schema.md | Event log schema v1.0 field definitions |
| `process/specs/telemetry-capabilities-schema.md` | docs/ | docs/reference/api.md | JSON-RPC API specification |
| `process/specs/README.md` | docs/ | docs/reference/api.md | Request/response format details |

### Workflows → How-To + Reference

| File | Type | New Location | Extraction Purpose |
|------|------|-------------|-------------------|
| `tutorials/event-monitoring-tutorial.md` | docs/ | docs/tutorials/event-driven-workflow.md | Event → Router → Workflow pipeline examples |
| `workflows/daily-report-acceptance-criteria.md` | docs/ | docs/tutorials/first-workflow.md | Daily report workflow step-by-step |
| `workflows/daily-report-api-reference.md` | docs/ | docs/reference/tools.md | Tool parameters and return values |

### Memory System → Explanation Docs

| File | Type | New Location | Extraction Purpose |
|------|------|-------------|-------------------|
| `PHASE_4.5_SUMMARY.md` | docs/ | docs/explanation/memory-system.md | Event log and trace correlation explanation |
| `PHASE_4.6_SUMMARY.md` | docs/ | docs/explanation/memory-system.md | Knowledge graph and profile learning |

### Integration Patterns → Explanation Docs

| File | Type | New Location | Extraction Purpose |
|------|------|-------------|-------------------|
| `ecosystem/architecture.md` | docs/ | docs/explanation/integration-patterns.md | Pattern P5, N2, N3, N5 explanations |
| `ecosystem/chora-compose-architecture.md` | docs/ | docs/explanation/integration-patterns.md | Backend integration patterns |
| `ecosystem/integration-analysis.md` | docs/ | docs/explanation/integration-patterns.md | Pattern usage guidance |
| `ecosystem/n8n-integration.md` | docs/ | docs/explanation/integration-patterns.md | n8n as MCP integration |
| `ecosystem/n8n-solution-neutral-intent.md` | docs/ | docs/explanation/integration-patterns.md | Multi-pattern implementation |

### Process → Dev Docs

| File | Type | New Location | Extraction Purpose |
|------|------|-------------|-------------------|
| `process/bdd-workflow.md` | docs/ | dev-docs/TESTING.md | BDD workflow explanation |
| `process/ddd-workflow.md` | docs/ | dev-docs/TESTING.md | DDD workflow explanation |
| `process/tdd-workflow.md` | docs/ | dev-docs/TESTING.md | TDD workflow explanation |
| `process/development-lifecycle.md` | docs/ | dev-docs/DEVELOPMENT.md | Development workflow |

---

## ARCHIVE (24 documents)

Documents to move to `docs/archive/` for historical reference.

### Sprint-specific Documentation

| File | Type | Archive Location |
|------|------|------------------|
| `change-requests/sprint-3-daily-report/completion-summary.md` | docs/ | docs/archive/sprints/ |
| `change-requests/sprint-3-daily-report/intent.md` | docs/ | docs/archive/sprints/ |
| `change-requests/sprint-3-event-monitoring/bdd-red-phase.md` | docs/ | docs/archive/sprints/ |
| `change-requests/sprint-3-event-monitoring/ddd-success-summary.md` | docs/ | docs/archive/sprints/ |
| `change-requests/sprint-3-event-monitoring/e2e-test-plan.md` | docs/ | docs/archive/sprints/ |
| `change-requests/sprint-3-event-monitoring/gateway-integration-complete.md` | docs/ | docs/archive/sprints/ |
| `change-requests/sprint-3-event-monitoring/implementation-progress.md` | docs/ | docs/archive/sprints/ |
| `change-requests/sprint-3-event-monitoring/intent.md` | docs/ | docs/archive/sprints/ |
| `change-requests/sprint-3-event-monitoring/sprint-3-completion-summary.md` | docs/ | docs/archive/sprints/ |
| `change-requests/sprint-5-workflows/bdd-red-phase.md` | docs/ | docs/archive/sprints/ |
| `change-requests/sprint-5-workflows/intent.md` | docs/ | docs/archive/sprints/ |
| `SPRINT_1_VALIDATION.md` | docs/ | docs/archive/sprints/ |

### Chora Alignment Documentation

| File | Type | Archive Location |
|------|------|------------------|
| `CHORA_BASE_ADOPTION_STATUS.md` | docs/ | docs/archive/chora-alignment/ |
| `CHORA_ROADMAP_ALIGNMENT.md` | docs/ | docs/archive/chora-alignment/ |
| `CHORA_V1_3_0_REVIEW.md` | docs/ | docs/archive/chora-alignment/ |

### Integration Strategy Documentation

| File | Type | Archive Location |
|------|------|------------------|
| `INTEGRATION_STRATEGY_UPDATE.md` | docs/ | docs/archive/integration-strategies/ |
| `N8N_INTEGRATION_GUIDE.md` | docs/ | docs/archive/integration-strategies/ |

### Ecosystem Documentation (Remaining)

| File | Type | Archive Location |
|------|------|------------------|
| `ecosystem/ecosystem-intent.md` | docs/ | docs/archive/ecosystem/ |

### Process Documentation (Remaining)

| File | Type | Archive Location |
|------|------|------------------|
| `process/CROSS_TEAM_COORDINATION.md` | docs/ | docs/archive/process/ |
| `process/DOCUMENTATION_STANDARD.md` | docs/ | docs/archive/process/ |
| `process/documentation-best-practices-for-mcp-n8n.md` | docs/ | docs/archive/process/ |
| `process/IMPLEMENTATION-SUMMARY.md` | docs/ | docs/archive/process/ |
| `process/README.md` | docs/ | docs/archive/process/ |
| `process/ROADMAP_GATEWAY_INTEGRATION.md` | docs/ | docs/archive/process/ |

### Other

| File | Type | Archive Location |
|------|------|------------------|
| `research/` | docs/ | docs/archive/research/ |

---

## DELETE (1 document)

Documents to remove entirely as obsolete.

| File | Type | Rationale |
|------|------|-----------|
| `.DS_Store` | system | macOS system files, should be gitignored |

---

## Mapping Table

| Category | Count | Action | Next Steps |
|-----------|--------|--------|------------|
| KEEP | 6 | Minor updates | Update links to new structure |
| EXTRACT | 23 | Extract → New Docs | Process in Phase 2 tasks |
| ARCHIVE | 24 | Move to archive/ | Execute in Phase 3 |
| DELETE | 1 | Remove entirely | Execute in Phase 3 |

---

## Next Steps

1. **Phase 1.2:** Verify all 54 documents categorized (count matches)
2. **Phase 1.3:** Expand mapping table with specific extraction tasks
3. **Phase 2:** Create new docs from EXTRACT category sources
4. **Phase 3:** Move ARCHIVE category to `docs/archive/`, delete DELETE category

---

**Document Count Verification:**
- KEEP: 6 ✅
- EXTRACT: 23 ✅
- ARCHIVE: 24 ✅
- DELETE: 1 ✅
- **TOTAL: 54** ✅

---

**Created:** 2025-10-21
**Source:** DOC_REFACTOR_PLAN.md guidelines
**Verification:** Manual count and categorization by file type/purpose
