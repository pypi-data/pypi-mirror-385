---
title: Documentation Archive
type: project
status: current
last_updated: 2025-10-21
---

# Documentation Archive

This directory contains **historical documentation** that has been superseded by the Diátaxis-organized documentation in the parent `docs/` directory. These files are preserved for reference but are no longer actively maintained.

---

## What's Archived

### Sprints (`sprints/`)
Sprint-specific documentation from development phases:
- Sprint validation summaries
- Change request documentation
- Sprint completion reports
- Implementation progress tracking

**Superseded by:**
- [project/ROADMAP.md](../../project/ROADMAP.md) - Current roadmap with all sprint summaries
- [project/SPRINT_STATUS.md](../../project/SPRINT_STATUS.md) - Current sprint status
- [project/CHANGELOG.md](../../project/CHANGELOG.md) - Version history

### Chora Alignment (`chora-alignment/`)
Historical documentation of chora-compose integration alignment:
- Roadmap alignment analyses
- Version review documentation
- Adoption status tracking

**Superseded by:**
- [docs/explanation/integration-patterns.md](../explanation/integration-patterns.md) - Pattern P5, N2, N3, N5
- [project/ROADMAP.md](../../project/ROADMAP.md) - Sprint 2 completion summary

### Integration Strategies (`integration-strategies/`)
Historical integration planning documents:
- Integration strategy updates
- n8n integration guides (draft)

**Superseded by:**
- [docs/explanation/integration-patterns.md](../explanation/integration-patterns.md) - Comprehensive patterns
- [docs/tutorials/event-driven-workflow.md](../tutorials/event-driven-workflow.md) - Event routing tutorial

### Ecosystem (`ecosystem/`)
Original ecosystem architecture documentation:
- Ecosystem intent documents
- n8n solution-neutral intent
- Integration analysis

**Superseded by:**
- [docs/explanation/architecture.md](../explanation/architecture.md) - Gateway architecture
- [docs/explanation/integration-patterns.md](../explanation/integration-patterns.md) - Pattern explanations

### Workflow Drafts (`workflow-drafts/`)
Early workflow API documentation and acceptance criteria (pre-refactor).

**Superseded by:**
- [docs/tutorials/first-workflow.md](../tutorials/first-workflow.md) - Daily report tutorial
- [docs/tutorials/event-driven-workflow.md](../tutorials/event-driven-workflow.md) - Event routing
- [docs/how-to/build-custom-workflow.md](../how-to/build-custom-workflow.md) - Workflow patterns
- [docs/explanation/workflows.md](../explanation/workflows.md) - Workflow concepts

---

## Why Archive?

These documents were created during the project's evolution and represent important historical context. However, they:
- Use outdated organizational structure (flat file hierarchy vs. Diátaxis categories)
- Mix different document types (tutorials, reference, planning in one file)
- Contain superseded information (replaced by more comprehensive docs)

They are **preserved for reference** but not actively updated. All current documentation is in:
- [`docs/`](../) - Product documentation (Tutorials, How-To, Reference, Explanation)
- [`dev-docs/`](../../dev-docs/) - Development documentation (Architecture, Testing, Release)
- [`project/`](../../project/) - Project documentation (Roadmap, Sprint Status, Changelog)

---

## How to Use This Archive

**If you're looking for:**
- **Tutorial** on using mcp-n8n → See [`docs/tutorials/`](../tutorials/)
- **How to solve a problem** → See [`docs/how-to/`](../how-to/)
- **API reference** → See [`docs/reference/`](../reference/)
- **Understanding concepts** → See [`docs/explanation/`](../explanation/)
- **Development setup** → See [`dev-docs/`](../../dev-docs/)
- **Current roadmap** → See [`project/ROADMAP.md`](../../project/ROADMAP.md)

**Only refer to this archive if:**
- You need historical context on a specific sprint
- You're researching evolution of a design decision
- You want to see original planning documents

---

## Archive Policy

**Retention:** Indefinite (git history provides permanence)

**Updates:** No active updates. If information is needed, it should be incorporated into current docs.

**Deprecation:** Documents here are already deprecated. Use [`docs/`](../) for current information.

---

**Last Updated:** 2025-10-21
**Maintained By:** Documentation refactor (completed 2025-10-21)
