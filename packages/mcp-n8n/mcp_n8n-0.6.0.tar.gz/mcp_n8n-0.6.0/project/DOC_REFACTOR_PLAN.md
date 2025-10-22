---
title: Documentation Refactor Plan for v0.4.0
type: project
status: complete
created: 2025-10-20
completed: 2025-10-21
owner: Victor Piper
estimated_total_time: 21.5 hours
completion_tracking: project/DOC_REFACTOR_CHECKLIST.md
---

# Documentation Refactor Plan for mcp-n8n v0.4.0

## Executive Summary

**Problem:** 54 documents with accumulated cruft, unclear dev/product separation, potential repo incoherence.

**Solution:** Build NEW documentation from ground truth (code, tests, BDD features) rather than reorganizing existing cruft:
- **dev-docs/** - For contributors (technical, code-focused)
- **docs/** - For end users (Diátaxis framework: tutorials, how-to, reference, explanation)
- **project/** - For team (status, planning, releases)

**Approach:**
1. Understand what mcp-n8n IS (from code/tests)
2. Define docs it NEEDS (not wants)
3. Build from scratch citing ground truth
4. Archive cruft

---

## What mcp-n8n IS (Ground Truth Analysis)

### Core Identity

From `src/mcp_n8n/` and `tests/`:

- **Pattern P5 Gateway & Aggregator** - Meta-MCP server that routes to multiple backends
- **Version 0.4.0** - Production release
- **Three Main Systems:**
  1. **Gateway** (`gateway.py`, `backends/`) - Routes `chora:*`, `coda:*` namespaced tools
  2. **Memory** (`memory/`) - Event log (JSONL), knowledge graph, trace correlation
  3. **Workflows** (`workflows/`) - Daily report, event routing, template-based reporting

### Key Components

**Gateway Layer:**
- `gateway.py` - FastMCP server, main entry point
- `backends/registry.py` - Backend lifecycle management, routing by namespace
- `backends/chora_composer.py` - Chora Composer backend integration
- `backends/coda_mcp.py` - Coda MCP backend integration
- `credential_validator.py` - Pre-flight credential validation

**Memory Layer:**
- `memory/event_log.py` - JSONL event persistence
- `memory/knowledge_graph.py` - Cross-session learning
- `memory/trace.py` - Distributed trace correlation
- `memory/profiles.py` - Agent profiles (Phase 4.6)

**Workflow Layer:**
- `workflows/daily_report.py` - Daily engineering report generation
- `workflows/event_router.py` - Event→workflow routing with YAML config
- `workflows/__main__.py` - Workflow CLI entry point

### Test Coverage (Ground Truth Behavior)

**BDD Features (3 files):**
1. `tests/features/event_monitoring.feature` - Event watching, correlation (Sprint 3)
2. `tests/features/daily_report.feature` - Daily report workflow (Sprint 3)
3. `tests/features/sprint_5_workflows.feature` - 23 scenarios covering:
   - Template rendering (AC 1-3)
   - EventWorkflowRouter (AC 4-10)
   - Daily report end-to-end (AC 11-14)
   - Event-driven pipelines (AC 15-17)
   - Workflow doc generation (AC 18-19)
   - Error handling (AC 20-23)

**Test Stats:**
- 25/25 Sprint 3 tests passing
- Integration tests for gateway, backends, workflows
- Smoke tests for routing, namespace isolation, startup

### Modality Patterns Implemented

- ✅ **Pattern P5** - Gateway & Aggregator (core architecture)
- ⏳ **Pattern N2** - n8n as MCP Server (planned)
- ⏳ **Pattern N3** - n8n as MCP Client (in progress via workflow integration)
- ⏳ **Pattern N5** - n8n workflows calling mcp-n8n (validation workflows)

---

## Documentation Structure (What We NEED)

### Total: 22 Core Documents (down from 54)

**Breakdown:**
- **Dev Docs:** 7 (for contributors)
- **Product Docs:** 15 (for end users, Diátaxis framework)
  - Tutorials: 3
  - How-To Guides: 7
  - Reference: 5
  - Explanation: 4
- **Project Docs:** 3 (for team)

---

## Dev Docs (For Contributors)

**Location:** `dev-docs/`
**Audience:** Developers who contribute to mcp-n8n
**Style:** Technical, code-focused, references source directly

### Documents (7 total)

1. **`dev-docs/ARCHITECTURE.md`**
   - Pattern P5 implementation details
   - Component interaction diagrams
   - Backend integration model
   - Source: Current ARCHITECTURE.md + code analysis

2. **`dev-docs/DEVELOPMENT.md`**
   - Setup, testing, debugging
   - Justfile commands reference
   - Development workflow
   - Source: Current DEVELOPMENT.md + justfile

3. **`dev-docs/TESTING.md`** (NEW)
   - BDD/TDD workflow
   - Test organization (smoke, unit, integration, BDD)
   - Running tests by category
   - Source: `tests/` structure + process docs

4. **`dev-docs/CONTRIBUTING.md`**
   - PR process, code style
   - Source: Current CONTRIBUTING.md (minimal updates)

5. **`dev-docs/RELEASE.md`** (NEW)
   - Release process, checklist
   - Rollback procedures
   - Source: RELEASE_CHECKLIST.md + ROLLBACK_PROCEDURE.md (merge)

6. **`dev-docs/TROUBLESHOOTING.md`**
   - Common issues, diagnostics
   - Debugging techniques
   - Source: Current TROUBLESHOOTING.md (improve)

7. **`dev-docs/AGENTS.md`**
   - Machine-readable project instructions
   - Source: Current AGENTS.md (update links)

---

## Product Docs (For End Users) - DIÁTAXIS FRAMEWORK

**Location:** `docs/`
**Audience:** Users who install and use mcp-n8n
**Framework:** Diátaxis (organize by user intent)

### Tutorials (Learning-oriented, hands-on)

**Location:** `docs/tutorials/`

1. **`getting-started.md`**
   - 5-minute quickstart: Install → Configure → First tool call
   - Expected output at each step
   - Source: README.md install + `tests/smoke/` as tutorial steps

2. **`first-workflow.md`**
   - 30-minute tutorial: Build daily report workflow end-to-end
   - Step-by-step with code examples
   - Source: `workflows/daily_report.py` + `tests/features/daily_report.feature`

3. **`event-driven-workflow.md`**
   - 30-minute tutorial: Event → Router → Workflow pipeline
   - Source: `tests/features/sprint_5_workflows.feature` (AC 15-17)

### How-To Guides (Task-oriented, problem-solving)

**Location:** `docs/how-to/`

4. **`install.md`**
   - Production vs development installation
   - Environment setup
   - Source: README.md installation section

5. **`configure-backends.md`**
   - Add/configure backends
   - Backend interface implementation
   - Source: `backends/base.py` + `config.py`

6. **`setup-claude-desktop.md`**
   - Claude Desktop configuration (stable + dev modes)
   - Source: `.config/claude-desktop.example.json`

7. **`setup-cursor.md`**
   - Cursor MCP configuration
   - Source: `.config/cursor-mcp.example.json`

8. **`query-events.md`**
   - Query event log, filter by type/status
   - `chora-memory` CLI usage
   - Source: `memory/event_log.py` + `cli/` modules

9. **`build-custom-workflow.md`**
   - Create event-driven workflow
   - YAML mapping configuration
   - Source: `workflows/event_router.py` + examples

10. **`debug-gateway.md`**
    - Diagnose routing issues
    - Debug logging, diagnostics
    - Source: TROUBLESHOOTING.md (user-focused subset)

### Reference (Information-oriented, specifications)

**Location:** `docs/reference/`

11. **`tools.md`**
    - All tools: `chora:*`, `coda:*`, `gateway_status`
    - Parameters, return values, examples
    - Source: `gateway.py` tool definitions + BDD examples

12. **`api.md`**
    - JSON-RPC API specification
    - Request/response format
    - Source: `process/specs/` + MCP protocol docs

13. **`event-schema.md`**
    - Event log schema v1.0
    - Field definitions, examples
    - Source: `process/specs/event-schema.md` + `memory/event_log.py`

14. **`configuration.md`**
    - All environment variables
    - Defaults, validation
    - Source: `config.py` docstrings + `.env.example`

15. **`cli-reference.md`**
    - `chora-memory` CLI commands
    - Usage examples
    - Source: `cli/` modules + PHASE_4.6_SUMMARY.md

### Explanation (Understanding-oriented, concepts)

**Location:** `docs/explanation/`

16. **`architecture.md`**
    - Why Pattern P5? Design decisions
    - Gateway architecture explained
    - Source: ARCHITECTURE.md (simplified for users)

17. **`memory-system.md`**
    - How memory works: event log, knowledge graph, traces
    - Cross-session learning
    - Source: PHASE_4.5_SUMMARY.md + PHASE_4.6_SUMMARY.md (merge)

18. **`integration-patterns.md`**
    - Pattern P5, N2, N3, N5 explained
    - When to use each pattern
    - Source: `ecosystem/*.md` (extract useful parts only)

19. **`workflows.md`**
    - Workflow architecture
    - Event-driven model
    - Source: `workflows/` modules analysis

---

## Project Management Docs

**Location:** `project/`
**Audience:** Internal team

### Documents (3 total)

20. **`project/ROADMAP.md`**
    - Sprint-based timeline
    - Milestones, dependencies
    - Source: UNIFIED_ROADMAP.md (use as base, update Sprint 5 complete)

21. **`project/SPRINT_STATUS.md`**
    - Current sprint status
    - Active tasks, blockers
    - Source: Current SPRINT_STATUS.md (update)

22. **`project/CHANGELOG.md`** (NEW)
    - Version history
    - Breaking changes, features, fixes
    - Source: Git history + sprint completion summaries

---

## Execution Phases

### Phase 0: Document This Plan (1.5 hours) ✅ IN PROGRESS

**Purpose:** Create persistent artifacts for LLM agent execution across sessions

**Tasks:**
- [x] Task 0.1: Create `project/DOC_REFACTOR_PLAN.md` (this file)
- [ ] Task 0.2: Create `project/DOC_REFACTOR_CHECKLIST.md`
- [ ] Task 0.3: Create `project/doc-templates/`
- [ ] Task 0.4: Create `project/DOC_SOURCE_MAP.md`

### Phase 1: Audit & Categorize (2 hours)

**Tasks:**
- [ ] Task 1.1: Create `docs-audit.md` with KEEP/EXTRACT/ARCHIVE/DELETE categories
- [ ] Task 1.2: Categorize all 54 docs
- [ ] Task 1.3: Create mapping table (old path → new path → ground truth)

### Phase 2: Build New Docs (15 hours)

**Dev Docs (4 hours):**
- [ ] Task 2.1: Improve `dev-docs/ARCHITECTURE.md`
- [ ] Task 2.2: Improve `dev-docs/DEVELOPMENT.md`
- [ ] Task 2.3: NEW `dev-docs/TESTING.md`
- [ ] Task 2.4: NEW `dev-docs/RELEASE.md`
- [ ] Task 2.5: Update `dev-docs/AGENTS.md`

**Product Docs - Tutorials (3 hours):**
- [ ] Task 2.6: NEW `docs/tutorials/getting-started.md`
- [ ] Task 2.7: NEW `docs/tutorials/first-workflow.md`
- [ ] Task 2.8: NEW `docs/tutorials/event-driven-workflow.md`

**Product Docs - How-To (4 hours):**
- [ ] Task 2.9: NEW `docs/how-to/install.md`
- [ ] Task 2.10: NEW `docs/how-to/configure-backends.md`
- [ ] Task 2.11: NEW `docs/how-to/setup-claude-desktop.md`
- [ ] Task 2.12: NEW `docs/how-to/setup-cursor.md`
- [ ] Task 2.13: NEW `docs/how-to/query-events.md`
- [ ] Task 2.14: NEW `docs/how-to/build-custom-workflow.md`
- [ ] Task 2.15: NEW `docs/how-to/debug-gateway.md`

**Product Docs - Reference (3 hours):**
- [ ] Task 2.16: NEW `docs/reference/tools.md`
- [ ] Task 2.17: NEW `docs/reference/api.md`
- [ ] Task 2.18: NEW `docs/reference/event-schema.md`
- [ ] Task 2.19: NEW `docs/reference/configuration.md`
- [ ] Task 2.20: NEW `docs/reference/cli-reference.md`

**Product Docs - Explanation (2-3 hours):**
- [ ] Task 2.21: NEW `docs/explanation/architecture.md`
- [ ] Task 2.22: NEW `docs/explanation/memory-system.md`
- [ ] Task 2.23: NEW `docs/explanation/integration-patterns.md`
- [ ] Task 2.24: NEW `docs/explanation/workflows.md`

**Project Docs (1 hour):**
- [ ] Task 2.25: Update `project/ROADMAP.md`
- [ ] Task 2.26: Update `project/SPRINT_STATUS.md`
- [ ] Task 2.27: NEW `project/CHANGELOG.md`

### Phase 3: Archive & Cleanup (2 hours)

**Tasks:**
- [ ] Task 3.1: Create `docs/archive/` structure
- [ ] Task 3.2: Move sprint docs to `docs/archive/sprints/`
- [ ] Task 3.3: Move chora-alignment docs to `docs/archive/chora-alignment/`
- [ ] Task 3.4: Move integration-strategies to `docs/archive/integration-strategies/`
- [ ] Task 3.5: Move `ecosystem/` to `docs/archive/ecosystem/` (after extraction)
- [ ] Task 3.6: Update all internal links

### Phase 4: Generate Metadata (1 hour)

**Tasks:**
- [ ] Task 4.1: Create `docs/README.md` (Diátaxis navigation index)
- [ ] Task 4.2: Update root `README.md` (link to dev-docs/ and docs/)
- [ ] Task 4.3: Create `.github/DOCUMENTATION_STANDARD.md`
- [ ] Task 4.4: Mark `DOC_REFACTOR_PLAN.md` as complete

---

## Resumption Protocol for LLM Agents

### On New Session Start

**Step 1: Check if refactor is in progress**
```bash
ls project/DOC_REFACTOR_CHECKLIST.md
# If exists, refactor is in progress
```

**Step 2: Read execution state**
```bash
cat project/DOC_REFACTOR_CHECKLIST.md | grep "^- \[ \]" | head -1
# First unchecked task = next task to execute
```

**Step 3: Read full context**
```bash
cat project/DOC_REFACTOR_PLAN.md
# This file - full plan with rationale
```

**Step 4: Read ground truth sources for current task**
```bash
cat project/DOC_SOURCE_MAP.md | grep "Task X.Y"
# Get source files for current task
```

**Step 5: Execute task**
- Follow execution steps from this plan
- Use template from `project/doc-templates/`
- Extract content from ground truth sources
- Create document with frontmatter

**Step 6: Update state**
```bash
# Check box in checklist
sed -i 's/- \[ \] Task X.Y/- [x] Task X.Y/' project/DOC_REFACTOR_CHECKLIST.md

# Commit with standard message
git add project/DOC_REFACTOR_CHECKLIST.md [new-doc.md]
git commit -m "docs: Complete Task X.Y - [description]"
```

**Step 7: Repeat**
- Continue until all tasks checked
- Or until session ends (next session resumes from Step 1)

---

## Example Task Execution

### Task 2.6: Create getting-started.md

**File:** `docs/tutorials/getting-started.md`

**Ground Truth Sources:**
- `README.md` lines 52-150 (installation section)
- `tests/smoke/test_gateway_startup.py` (gateway startup verification)
- `tests/smoke/test_chora_routing.py` (first tool call example)

**Template:** `project/doc-templates/tutorial-template.md`

**Execution Steps:**

1. Read ground truth sources
2. Extract key steps from smoke tests (convert to tutorial format)
3. Copy tutorial template
4. Fill in template:
   - **Title:** "Getting Started with mcp-n8n"
   - **What You'll Build:** Working gateway with first tool call
   - **Time:** 5 minutes
   - **Prerequisites:** Python 3.12+, pip
   - **Step 1:** Install mcp-n8n (from README)
   - **Step 2:** Set environment variables (from README)
   - **Step 3:** Start gateway (from test_gateway_startup.py)
   - **Step 4:** Test tool call (from test_chora_routing.py)
   - **Step 5:** Verify success (expected output)
5. Add frontmatter:
   ```yaml
   ---
   title: Getting Started with mcp-n8n
   type: tutorial
   audience: beginners
   estimated_time: "5 minutes"
   test_extraction: true
   source: README.md, tests/smoke/
   ---
   ```
6. Check box for Task 2.6 in `DOC_REFACTOR_CHECKLIST.md`
7. Commit: `git commit -m "docs: Create getting-started tutorial (Task 2.6)"`

---

## Final Directory Structure

```
/
├── README.md (root - main entry point)
│
├── dev-docs/ (for contributors)
│   ├── ARCHITECTURE.md
│   ├── DEVELOPMENT.md
│   ├── TESTING.md (NEW)
│   ├── CONTRIBUTING.md
│   ├── RELEASE.md (NEW)
│   ├── TROUBLESHOOTING.md
│   └── AGENTS.md
│
├── docs/ (for users - DIÁTAXIS)
│   ├── README.md (navigation index)
│   │
│   ├── tutorials/ (learning-oriented)
│   │   ├── getting-started.md (NEW)
│   │   ├── first-workflow.md (NEW)
│   │   └── event-driven-workflow.md (NEW)
│   │
│   ├── how-to/ (task-oriented)
│   │   ├── install.md (NEW)
│   │   ├── configure-backends.md (NEW)
│   │   ├── setup-claude-desktop.md (NEW)
│   │   ├── setup-cursor.md (NEW)
│   │   ├── query-events.md (NEW)
│   │   ├── build-custom-workflow.md (NEW)
│   │   └── debug-gateway.md (NEW)
│   │
│   ├── reference/ (information-oriented)
│   │   ├── tools.md (NEW)
│   │   ├── api.md (NEW)
│   │   ├── event-schema.md (NEW)
│   │   ├── configuration.md (NEW)
│   │   └── cli-reference.md (NEW)
│   │
│   ├── explanation/ (understanding-oriented)
│   │   ├── architecture.md (NEW)
│   │   ├── memory-system.md (NEW)
│   │   ├── integration-patterns.md (NEW)
│   │   └── workflows.md (NEW)
│   │
│   └── archive/ (historical)
│       ├── sprints/
│       ├── chora-alignment/
│       ├── integration-strategies/
│       ├── ecosystem/
│       └── workflow-drafts/
│
├── project/ (for team)
│   ├── ROADMAP.md
│   ├── SPRINT_STATUS.md
│   ├── CHANGELOG.md (NEW)
│   ├── DOC_REFACTOR_PLAN.md (this file)
│   ├── DOC_REFACTOR_CHECKLIST.md (NEW)
│   ├── DOC_SOURCE_MAP.md (NEW)
│   └── doc-templates/ (NEW)
│       ├── tutorial-template.md
│       ├── how-to-template.md
│       ├── reference-template.md
│       └── explanation-template.md
│
└── .github/
    └── DOCUMENTATION_STANDARD.md (NEW)
```

---

## Success Criteria

✅ All boxes in `DOC_REFACTOR_CHECKLIST.md` checked
✅ 22 new docs created with ground truth sources cited
✅ 32 docs archived
✅ Diátaxis structure implemented for `docs/`
✅ `dev-docs/` vs `docs/` vs `project/` separation clear
✅ Documentation examples extracted to tests
✅ All commits follow pattern: `docs: [Task X.Y] - description`

---

## Benefits of This Approach

✅ **Session Persistence:** Any LLM agent can resume from checklist
✅ **Progress Tracking:** Clear completion percentage
✅ **Context Preservation:** Full plan + source map + templates
✅ **Resumable:** Clear resumption protocol
✅ **Testable:** Each task has clear inputs/outputs
✅ **Committable:** Granular commits for review
✅ **Reviewable:** Can review progress at checkpoints

---

## Completion Summary

**Status:** ✅ **COMPLETE**
**Created:** 2025-10-20
**Completed:** 2025-10-21
**Duration:** 2 days
**Final Progress:** 43/43 tasks (100%)

### Final Statistics

**Documents Created:** 22
- 5 dev-docs (ARCHITECTURE.md, DEVELOPMENT.md, TESTING.md, RELEASE.md, AGENTS.md updates)
- 3 tutorials (getting-started, first-workflow, event-driven-workflow)
- 7 how-to guides (install, configure-backends, setup-claude-desktop, setup-cursor, query-events, build-custom-workflow, debug-gateway)
- 5 reference docs (tools, api, event-schema, configuration, cli-reference)
- 4 explanation docs (architecture, memory-system, integration-patterns, workflows)
- 3 project docs (ROADMAP.md, SPRINT_STATUS.md, CHANGELOG.md)

**Documents Archived:** 22
- 11 sprint docs → docs/archive/sprints/
- 3 chora alignment docs → docs/archive/chora-alignment/
- 2 integration strategies → docs/archive/integration-strategies/
- 6 ecosystem docs → docs/archive/ecosystem/

**Navigation Created:**
- docs/README.md (Diátaxis navigation index)
- docs/archive/README.md (Archive navigation guide)
- .github/DOCUMENTATION_STANDARD.md (Contributor guide)
- README.md (Root documentation links)

### Success Metrics Achieved

✅ **Ground Truth Compliance:** All 22 new docs cite code/tests/BDD features as sources
✅ **Diátaxis Structure:** Tutorials, How-To, Reference, Explanation clearly separated
✅ **Test Extraction:** 15+ documentation examples extracted to tests
✅ **Navigation:** Multiple entry points (by type, by task, by role)
✅ **Archive Preservation:** 22 historical docs preserved with navigation
✅ **Link Integrity:** All internal links updated and verified
✅ **Session Persistence:** Checklist enables resumption at any point
✅ **Granular Commits:** 11 commits documenting progress across 7 batches

### Documentation Coverage

**v0.5.0 Feature Coverage:**
- ✅ Gateway & Aggregator (Pattern P5) - Explained in docs/explanation/architecture.md
- ✅ Event-driven workflows - Tutorial in docs/tutorials/event-driven-workflow.md
- ✅ Template rendering - How-to in docs/how-to/build-custom-workflow.md
- ✅ Event log querying - How-to in docs/how-to/query-events.md
- ✅ CLI tools (chora-memory) - Reference in docs/reference/cli-reference.md
- ✅ Memory system - Explanation in docs/explanation/memory-system.md

---

**Final Status:** Documentation Refactor Complete (43/43 tasks, 100%)
**Next Phase:** Maintain docs alongside code changes per DOCUMENTATION_STANDARD.md
