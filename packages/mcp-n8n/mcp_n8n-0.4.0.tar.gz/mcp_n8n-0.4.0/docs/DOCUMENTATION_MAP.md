# mcp-n8n Documentation Map

**Generated:** 2025-10-19
**Purpose:** Complete index of all documentation in the mcp-n8n project
**Scope:** All markdown files in [docs/](.)

---

## Quick Navigation

- [Getting Started](#getting-started)
- [Project Status & Planning](#project-status--planning)
- [Architecture & Development](#architecture--development)
- [Integration & Ecosystem](#integration--ecosystem)
- [Workflows & Patterns](#workflows--patterns)
- [Process & Quality](#process--quality)
- [Testing & Validation](#testing--validation)
- [Specifications](#specifications)
- [Change Requests](#change-requests)

---

## Getting Started

### Core Documentation
| Document | Purpose | Audience | Status |
|----------|---------|----------|--------|
| [README.md](../README.md) | Project overview, quick start | New users, contributors | ✅ Current |
| [CONTRIBUTING.md](../CONTRIBUTING.md) | Contribution guidelines, development setup | Contributors | ✅ Current |
| [GETTING_STARTED.md](../GETTING_STARTED.md) | Detailed setup, first workflow | New users | ⚠️ Needs update |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Deep technical guide for developers | Core developers | ✅ Current |

---

## Project Status & Planning

### Roadmaps & Strategy
| Document | Purpose | Key Info | Last Updated |
|----------|---------|----------|--------------|
| [ROADMAP.md](ROADMAP.md) | **Main implementation roadmap** (4 phases) | Phase 0-3 plans, dependency model, weekly report workflow | 2025-10-17 |
| [UNIFIED_ROADMAP.md](UNIFIED_ROADMAP.md) | **Coordinated roadmap** (mcp-n8n + chora-compose) | Sprint-based timeline, integration milestones | 2025-10-19 |
| [SPRINT_STATUS.md](SPRINT_STATUS.md) | **Current sprint status** | Active sprint, completed work, blockers | 2025-10-19 ✅ |
| [SPRINT_1_VALIDATION.md](SPRINT_1_VALIDATION.md) | Sprint 1 completion report | Phase 0 validation results | 2025-10-17 |

### Integration Planning
| Document | Purpose | Key Info | Status |
|----------|---------|----------|--------|
| [INTEGRATION_STRATEGY_UPDATE.md](INTEGRATION_STRATEGY_UPDATE.md) | **Simplified chora-compose integration** | Hybrid method (submodule + package) | 2025-10-19 |
| [CHORA_ROADMAP_ALIGNMENT.md](CHORA_ROADMAP_ALIGNMENT.md) | Alignment analysis with chora-compose releases | Feature gaps, dependencies | 2025-10-18 ✅ RESOLVED |
| [CHORA_V1_3_0_REVIEW.md](CHORA_V1_3_0_REVIEW.md) | chora-compose v1.3.0 release review | Feature completeness, integration readiness | 2025-10-18 |

### Template Adoption
| Document | Purpose | Key Info | Status |
|----------|---------|----------|--------|
| [CHORA_BASE_ADOPTION_STATUS.md](CHORA_BASE_ADOPTION_STATUS.md) | **chora-base template adoption tracking** | v1.0.0 → v1.5.0 gap analysis, recommended actions | 2025-10-19 |

---

## Architecture & Development

### Core Architecture
| Document | Purpose | Key Info | Audience |
|----------|---------|----------|----------|
| [ARCHITECTURE.md](../ARCHITECTURE.md) | **System architecture** | Pattern P5 implementation, backend registry | All developers |
| [DEVELOPMENT.md](DEVELOPMENT.md) | **Development deep dive** | Code organization, testing, debugging | Core developers |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Problem solving guide | Common issues, diagnostics, solutions | All users |

### Performance & Validation
| Document | Purpose | Key Info | Status |
|----------|---------|----------|--------|
| [PERFORMANCE_BASELINE.md](PERFORMANCE_BASELINE.md) | Performance benchmarks | Routing overhead, startup time | 2025-10-17 |
| [PHASE_4.5_SUMMARY.md](PHASE_4.5_SUMMARY.md) | Memory system implementation | A-MEM integration, knowledge graph | 2025-10-17 |
| [PHASE_4.6_SUMMARY.md](PHASE_4.6_SUMMARY.md) | CLI tools & agent infrastructure | chora-memory CLI, AGENTS.md | 2025-10-17 |

---

## Integration & Ecosystem

### n8n Integration
| Document | Purpose | Key Info | Audience |
|----------|---------|----------|----------|
| [N8N_INTEGRATION_GUIDE.md](N8N_INTEGRATION_GUIDE.md) | **n8n integration patterns** | 3 patterns, workflow examples | n8n users |

### Ecosystem Analysis
| Document | Purpose | Key Info | Status |
|----------|---------|----------|--------|
| [ecosystem/architecture.md](ecosystem/architecture.md) | Overall ecosystem architecture | 3-layer model, component relationships | ✅ Current |
| [ecosystem/chora-compose-architecture.md](ecosystem/chora-compose-architecture.md) | chora-compose deep dive | Components, capabilities, MCP integration | ✅ Current |
| [ecosystem/chora-compose-solution-neutral-intent.md](ecosystem/chora-compose-solution-neutral-intent.md) | Design intent & patterns | Atomic capabilities, composability | ✅ Current |
| [ecosystem/ecosystem-intent.md](ecosystem/ecosystem-intent.md) | Platform vision | Layer separation, coordination patterns | ✅ Current |
| [ecosystem/integration-analysis.md](ecosystem/integration-analysis.md) | Integration patterns analysis | mcp-n8n ↔ chora-compose integration | ✅ Current |
| [ecosystem/n8n-integration.md](ecosystem/n8n-integration.md) | n8n technical integration | MCP server/client patterns (N2, N3, N5) | ✅ Current |
| [ecosystem/n8n-solution-neutral-intent.md](ecosystem/n8n-solution-neutral-intent.md) | n8n design intent | Workflow orchestration patterns | ✅ Current |

---

## Workflows & Patterns

### Workflow Specifications
| Document | Purpose | Key Info | Status |
|----------|---------|----------|--------|
| [workflows/daily-report-spec.md](workflows/daily-report-spec.md) | **Daily Report workflow spec** | Sprint 5 validation workflow | 2025-10-19 |
| [workflows/chora-compose-storage-question.md](workflows/chora-compose-storage-question.md) | **Question for chora-compose team** | Ephemeral artifact storage patterns | 2025-10-19 |

---

## Process & Quality

### Development Process
| Document | Purpose | Key Info | Audience |
|----------|---------|----------|----------|
| [process/README.md](process/README.md) | Process documentation index | BDD, DDD, TDD workflows | All developers |
| [process/bdd-workflow.md](process/bdd-workflow.md) | **BDD workflow** | Feature → Scenario → Implementation | Developers |
| [process/ddd-workflow.md](process/ddd-workflow.md) | **DDD workflow** | Documentation-first development | Developers |
| [process/tdd-workflow.md](process/tdd-workflow.md) | **TDD workflow** | Test → Code → Refactor | Developers |
| [process/development-lifecycle.md](process/development-lifecycle.md) | Complete development lifecycle | Phase progression, quality gates | All developers |

### Documentation Best Practices
| Document | Purpose | Key Info | Audience |
|----------|---------|----------|----------|
| [process/documentation-best-practices-for-mcp-n8n.md](process/documentation-best-practices-for-mcp-n8n.md) | **Documentation standards** | Patterns, templates, frontmatter schema | All contributors |

### Cross-Team Coordination
| Document | Purpose | Key Info | Audience |
|----------|---------|----------|----------|
| [process/CROSS_TEAM_COORDINATION.md](process/CROSS_TEAM_COORDINATION.md) | Coordination guidelines | Sync patterns, decision-making | Team leads |
| [process/IMPLEMENTATION-SUMMARY.md](process/IMPLEMENTATION-SUMMARY.md) | Implementation tracking | Phase completion summaries | All developers |
| [process/ROADMAP_GATEWAY_INTEGRATION.md](process/ROADMAP_GATEWAY_INTEGRATION.md) | Gateway integration roadmap | Backend integration patterns | Developers |

---

## Testing & Validation

### Testing Documentation
| Document | Purpose | Key Info | Status |
|----------|---------|----------|--------|
| [testing/INTEGRATION_TESTING.md](testing/INTEGRATION_TESTING.md) | Integration testing guide | E2E tests, backend validation | ✅ Current |

### Tutorials
| Document | Purpose | Key Info | Audience |
|----------|---------|----------|----------|
| [tutorials/event-monitoring-tutorial.md](tutorials/event-monitoring-tutorial.md) | **Event monitoring tutorial** | Step-by-step implementation guide | Developers |

---

## Specifications

### API & Schema Specs
| Document | Purpose | Key Info | Status |
|----------|---------|----------|--------|
| [process/specs/README.md](process/specs/README.md) | Specifications index | Event schema, telemetry capabilities | ✅ Current |
| [process/specs/event-schema.md](process/specs/event-schema.md) | **Event schema v1.0** | JSONL format, event types | ✅ Current |
| [process/specs/telemetry-capabilities-schema.md](process/specs/telemetry-capabilities-schema.md) | **Telemetry capabilities schema** | capabilities://telemetry resource | ✅ Current |

---

## Change Requests

### Sprint 3: Event Monitoring
| Document | Purpose | Key Info | Status |
|----------|---------|----------|--------|
| [change-requests/sprint-3-event-monitoring/intent.md](change-requests/sprint-3-event-monitoring/intent.md) | Sprint 3 intent | Event monitoring foundation | ✅ Complete |
| [change-requests/sprint-3-event-monitoring/bdd-red-phase.md](change-requests/sprint-3-event-monitoring/bdd-red-phase.md) | BDD red phase plan | Feature file, step definitions | ✅ Complete |
| [change-requests/sprint-3-event-monitoring/ddd-success-summary.md](change-requests/sprint-3-event-monitoring/ddd-success-summary.md) | DDD completion summary | Documentation deliverables | ✅ Complete |
| [change-requests/sprint-3-event-monitoring/gateway-integration-complete.md](change-requests/sprint-3-event-monitoring/gateway-integration-complete.md) | Gateway integration completion | Integration test results | ✅ Complete |
| [change-requests/sprint-3-event-monitoring/implementation-progress.md](change-requests/sprint-3-event-monitoring/implementation-progress.md) | Implementation tracking | Phase-by-phase progress | ✅ Complete |
| [change-requests/sprint-3-event-monitoring/sprint-3-completion-summary.md](change-requests/sprint-3-event-monitoring/sprint-3-completion-summary.md) | **Sprint 3 final summary** | 25/25 tests passing, deliverables | ✅ Complete |
| [change-requests/sprint-3-event-monitoring/e2e-test-plan.md](change-requests/sprint-3-event-monitoring/e2e-test-plan.md) | E2E test plan | End-to-end testing strategy | ✅ Complete |

---

## Release & Operations

### Release Management
| Document | Purpose | Key Info | Audience |
|----------|---------|----------|----------|
| [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) | **Release process** | Pre-release, release, post-release steps | Maintainers |
| [ROLLBACK_PROCEDURE.md](ROLLBACK_PROCEDURE.md) | Rollback procedures | Emergency rollback, version downgrade | Maintainers |

---

## Document Statistics

### Total Documents
- **Total files:** 45 markdown documents
- **Categories:** 9 main categories
- **Status:**
  - ✅ Current: 37 documents
  - ⚠️ Needs update: 1 document (GETTING_STARTED.md)
  - 📋 Planned: 7 documents (future sprints)

### By Category
| Category | Count | Status |
|----------|-------|--------|
| Project Status & Planning | 8 | ✅ Current |
| Architecture & Development | 6 | ✅ Current |
| Integration & Ecosystem | 8 | ✅ Current |
| Process & Quality | 8 | ✅ Current |
| Testing & Validation | 2 | ✅ Current |
| Specifications | 3 | ✅ Current |
| Change Requests | 7 | ✅ Complete |
| Workflows | 2 | 📋 Active |
| Release & Operations | 2 | ✅ Current |

---

## Documentation Maintenance

### Update Frequency
| Document Type | Update Frequency | Last Review |
|---------------|-----------------|-------------|
| **SPRINT_STATUS.md** | Daily during sprints | 2025-10-19 |
| **Roadmaps** | Weekly/per sprint | 2025-10-19 |
| **Integration docs** | Per chora-compose release | 2025-10-19 |
| **Process docs** | Monthly or as needed | 2025-10-19 |
| **Specifications** | Per schema version | 2025-10-17 |
| **Architecture** | Quarterly or major changes | 2025-10-17 |

### Review Schedule
- **Weekly:** SPRINT_STATUS.md, active change requests
- **Monthly:** ROADMAP.md, UNIFIED_ROADMAP.md, integration docs
- **Quarterly:** ARCHITECTURE.md, process docs, CHORA_BASE_ADOPTION_STATUS.md
- **As-needed:** Troubleshooting, tutorials, specs

---

## How to Use This Map

### For New Contributors
1. Start with [README.md](../README.md) and [CONTRIBUTING.md](../CONTRIBUTING.md)
2. Read [DEVELOPMENT.md](DEVELOPMENT.md) for technical deep dive
3. Check [SPRINT_STATUS.md](SPRINT_STATUS.md) for current work
4. Follow [process/bdd-workflow.md](process/bdd-workflow.md) for feature development

### For Planning Work
1. Review [UNIFIED_ROADMAP.md](UNIFIED_ROADMAP.md) for overall timeline
2. Check [SPRINT_STATUS.md](SPRINT_STATUS.md) for current sprint
3. Review [CHORA_ROADMAP_ALIGNMENT.md](CHORA_ROADMAP_ALIGNMENT.md) for dependencies
4. Check [change-requests/](change-requests/) for completed work

### For Integration Work
1. Read [INTEGRATION_STRATEGY_UPDATE.md](INTEGRATION_STRATEGY_UPDATE.md) first
2. Check [ecosystem/](ecosystem/) for architecture context
3. Review [N8N_INTEGRATION_GUIDE.md](N8N_INTEGRATION_GUIDE.md) for patterns
4. Reference [process/specs/](process/specs/) for schemas

### For Troubleshooting
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) first
2. Review [PERFORMANCE_BASELINE.md](PERFORMANCE_BASELINE.md) for metrics
3. Check [testing/INTEGRATION_TESTING.md](testing/INTEGRATION_TESTING.md)
4. Search [change-requests/](change-requests/) for related issues

---

## Related External Documentation

### chora-compose
- **Repository:** https://github.com/liminalcommons/chora-compose
- **Relevant docs:**
  - chora-compose/docs/ROADMAP.md
  - chora-compose/docs/API_REFERENCE.md
  - chora-compose/docs/MCP_INTEGRATION.md

### chora-base Template
- **Repository:** https://github.com/liminalcommons/chora-base
- **Relevant docs:**
  - chora-base/docs/upgrades/PHILOSOPHY.md
  - chora-base/CHANGELOG.md
  - chora-base/docs/BENEFITS.md

### MCP Specification
- **URL:** https://modelcontextprotocol.io
- **GitHub:** https://github.com/anthropics/mcp

### n8n
- **Documentation:** https://docs.n8n.io/
- **Custom Nodes:** https://docs.n8n.io/integrations/creating-nodes/

---

## Document Maintenance

**Last Full Audit:** 2025-10-19
**Next Audit:** 2025-11-19 (monthly)
**Maintained by:** mcp-n8n core team
**Issues:** Report documentation issues in GitHub Issues with label `documentation`

---

## Quick Reference

### Most Important Documents (Top 10)
1. [SPRINT_STATUS.md](SPRINT_STATUS.md) - Current work status
2. [UNIFIED_ROADMAP.md](UNIFIED_ROADMAP.md) - Complete project roadmap
3. [INTEGRATION_STRATEGY_UPDATE.md](INTEGRATION_STRATEGY_UPDATE.md) - Integration approach
4. [DEVELOPMENT.md](DEVELOPMENT.md) - Technical deep dive
5. [process/bdd-workflow.md](process/bdd-workflow.md) - Development workflow
6. [CHORA_BASE_ADOPTION_STATUS.md](CHORA_BASE_ADOPTION_STATUS.md) - Template alignment
7. [N8N_INTEGRATION_GUIDE.md](N8N_INTEGRATION_GUIDE.md) - n8n patterns
8. [process/specs/event-schema.md](process/specs/event-schema.md) - Event schema
9. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problem solving
10. [ARCHITECTURE.md](../ARCHITECTURE.md) - System design

### By Use Case
**Starting a new feature:**
→ [process/bdd-workflow.md](process/bdd-workflow.md) + [SPRINT_STATUS.md](SPRINT_STATUS.md)

**Integrating with chora-compose:**
→ [INTEGRATION_STRATEGY_UPDATE.md](INTEGRATION_STRATEGY_UPDATE.md) + [ecosystem/integration-analysis.md](ecosystem/integration-analysis.md)

**Building an n8n workflow:**
→ [N8N_INTEGRATION_GUIDE.md](N8N_INTEGRATION_GUIDE.md) + [workflows/daily-report-spec.md](workflows/daily-report-spec.md)

**Updating template version:**
→ [CHORA_BASE_ADOPTION_STATUS.md](CHORA_BASE_ADOPTION_STATUS.md)

**Troubleshooting an issue:**
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md) + [testing/INTEGRATION_TESTING.md](testing/INTEGRATION_TESTING.md)

---

**Generated:** 2025-10-19
**Version:** 1.0.0
**Format:** Markdown with frontmatter
**Purpose:** Complete documentation index for mcp-n8n project
