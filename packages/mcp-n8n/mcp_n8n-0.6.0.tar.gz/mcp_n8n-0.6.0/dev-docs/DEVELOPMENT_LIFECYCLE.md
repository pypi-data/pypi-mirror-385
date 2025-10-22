---
title: Development Lifecycle
category: process
version: 0.5.0
created: 2025-10-15
---

# Using This Template

> Swap placeholders like `{{INTEGRATION}}` / `{{integration}}` and adjust examples to match your MCP server domain before distribution.

# Development Lifecycle

## Overview

The MCP Server {{INTEGRATION}} project follows an integrated development lifecycle that combines **Documentation Driven Design (DDD)**, **Behavior Driven Development (BDD)**, and **Test Driven Development (TDD)** methodologies, supported by **DevOps best practices** for continuous quality and delivery.

## Core Principles

1. **Documentation First**: API contracts and behavior specifications are written before implementation
2. **Test as Specification**: Tests define expected behavior and serve as living documentation
3. **Red-Green-Refactor**: Implement iteratively with failing tests driving design
4. **Continuous Integration**: Automated quality gates prevent regressions
5. **Semantic Versioning**: Clear version communication for API changes

## Change Request Intake

Require a Diátaxis document for every change request so intent is clear before implementation:
- **Explanation** records business context and success metrics (feeds DDD Step 1).
- **How-to Guide** lists workflows that turn into BDD scenarios.
- **Reference** proposes API/tool contract updates refined during DDD Step 3.
- **Tutorial** (optional) sketches the end-to-end experience for onboarding or release notes.

Store drafts in `docs/change-requests/{issue-id}/` or attach them to the ticket. Mark requests as “Ready for DDD” only after Explanation and Reference sections are reviewed. For low-risk fixes, a lightweight version (Explanation + Reference) is acceptable if it still explains the observable behavior change.

## Development Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DOCUMENTATION DRIVEN DESIGN (DDD)                        │
├─────────────────────────────────────────────────────────────┤
│ → Write API reference docs (parameters, returns, examples)  │
│ → Define acceptance criteria in plain English               │
│ → Review with stakeholders                                  │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. BEHAVIOR DRIVEN DEVELOPMENT (BDD)                        │
├─────────────────────────────────────────────────────────────┤
│ → Write Gherkin scenarios from acceptance criteria          │
│ → Implement step definitions                                │
│ → Run scenarios (RED - should fail)                         │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. TEST DRIVEN DEVELOPMENT (TDD)                            │
├─────────────────────────────────────────────────────────────┤
│ RED:   Write failing unit/integration tests                 │
│ GREEN: Implement minimal code to pass                       │
│ REFACTOR: Improve design while keeping tests green          │
│ → Repeat until all BDD scenarios pass                       │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. CONTINUOUS INTEGRATION (CI)                              │
├─────────────────────────────────────────────────────────────┤
│ → Commit to feature branch                                  │
│ → CI runs: lint → unit → contracts → BDD → integration     │
│ → All quality gates must pass                               │
│ → Code review (1+ approvals)                                │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. MERGE & RELEASE                                          │
├─────────────────────────────────────────────────────────────┤
│ → Merge to develop (integration branch)                     │
│ → Automated regression tests                                │
│ → Tag release when ready (semantic versioning)              │
│ → Publish to PyPI + GitHub Release                          │
└─────────────────────────────────────────────────────────────┘
```

## Workflow by Artifact Type

### New Tool Implementation

**Scenario**: Adding a new MCP tool (e.g., `create_{{integration}}_table`)

1. **DDD Phase** (2-4 hours)
   - Review your tool naming standards (for example `tool-standards.md`) for consistent naming
   - Create API reference in `docs/reference/api/tools/{category}.md`
   - Document: signature, parameters (with types/defaults), returns (with JSON example), usage examples
   - Define acceptance criteria: "Given X, When Y, Then Z"
   - Get technical review from team

2. **BDD Phase** (1-2 hours)
   - Create Gherkin scenario in `tests/features/tool_contracts.feature`:
     ```gherkin
     Scenario: create_{{integration}}_table creates table with schema
       Given a valid {{INTEGRATION}} document "doc-abc123"
       When I call tool "create_{{integration}}_table" with:
         | doc_id | doc-abc123 |
         | name   | Tasks      |
         | columns| [{"name": "Task", "type": "text"}] |
       Then the tool returns success
       And the response includes "id" field
       And the response includes "name" = "Tasks"
     ```
   - Implement step definitions in `tests/step_defs/tool_steps.py`
   - Run pytest-bdd → RED (scenario fails, tool doesn't exist)

3. **TDD Phase** (4-8 hours)
   - **RED**: Write contract test in `tests/contracts/test_table_tools.py`:
     ```python
     async def test_create_{{integration}}_table_signature():
         # Verify tool accepts correct parameters
         result = await server.create_{{integration}}_table(
             doc_id="doc-123",
             name="Tasks",
             columns=[{"name": "Task", "type": "text"}]
         )
         assert result["success"] == True
     ```
   - Run test → FAILS (tool not implemented)

   - **GREEN**: Implement in `src/{{integration}}_mcp/tools/tables.py`:
     ```python
     async def create_{{integration}}_table(doc_id: str, name: str, columns: List[Dict]) -> dict:
         result = await {{integration}}_request("POST", "docs", doc_id, "tables", json={
             "name": name,
             "columns": columns
         })
         return {
             "success": True,
             "id": result["id"],
             "name": result["name"]
         }
     ```
   - Register in `src/{{integration}}_mcp/server.py` with `@mcp.tool()`
   - Run test → PASSES

   - **REFACTOR**: Add error handling, logging, type hints
   - Run all tests → STILL PASSES

4. **CI Phase** (automatic, 5-10 min)
   - Commit with message: "feat: add create_{{integration}}_table tool\n\nImplements table creation per tool-standards.md.\nCloses #XX"
   - Push to feature branch `feature/create-{{integration}}-table`
   - CI runs all quality gates (see [CI/CD section](#cicd-pipeline))
   - Request PR review

5. **Review & Merge** (1-2 hours)
   - Code review: implementation quality, test coverage
   - Docs review: API reference completeness
   - Approval → Merge to `develop`
   - CI runs E2E regression tests
   - Ready for next release

**Total Time**: 1-2 days (including reviews)

### Bug Fix

**Scenario**: Fixing a bug (e.g., formula injection vulnerability)

1. **DDD Phase** (30 min - 1 hour)
   - Document the bug in GitHub issue with reproduction steps
   - Define expected behavior in issue description
   - Update docs if behavior was incorrectly documented

2. **TDD Phase** (2-4 hours)
   - **RED**: Write regression test in `tests/regression/test_issue_{num}.py`:
     ```python
     def test_issue_42_formula_injection_vulnerability():
         """
         Regression: Formula injection via task names.
         Bug: User could inject formulas like "=SUM(A1:A10)"
         Fix: Sanitize input to escape dangerous characters
         """
         malicious_input = "=SUM(A1:A10)"
         result = await server.create_{{integration}}_row(
             doc_id="doc-123",
             table_id="tbl-456",
             row_data={"Task": malicious_input}
         )
         # Should store as literal text, not formula
         assert result["values"]["Task"] == "\\=SUM(A1:A10)"
     ```
   - Run test → FAILS (bug reproduced)

   - **GREEN**: Implement fix in `src/{{integration}}_mcp/tools/rows.py`:
     ```python
     def sanitize_formula_input(value: str) -> str:
         """Escape formula injection characters."""
         if value.startswith("="):
             return "\\" + value
         return value
     ```
   - Apply sanitization before API call
   - Run test → PASSES

   - **REFACTOR**: Extract to utility module, add more test cases

3. **BDD Phase** (optional, 1 hour)
   - Add error scenario to `tests/features/error_handling.feature`:
     ```gherkin
     Scenario: Prevent formula injection in row data
       When I create a row with Task = "=SUM(A1:A10)"
       Then the row is created with escaped value "\\=SUM(A1:A10)"
       And the formula is not executed
     ```

4. **CI & Merge** (same as above)
   - Commit: "fix: sanitize formula injection in row data\n\nFixes #42"
   - PR → Review → Merge
   - Backport to release branch if critical

**Total Time**: Half day to 1 day

### Feature Enhancement

**Scenario**: Adding new functionality to existing tool (e.g., `content_format` parameter for pages)

1. **DDD Phase** (1-2 hours)
   - Update API reference in `docs/reference/api/tools/pages.md`
   - Add new parameter documentation:
     ```markdown
     | Name | Type | Required | Default | Description |
     |------|------|----------|---------|-------------|
     | content_format | string | No | `markdown` | Format: `markdown`, `html`, `canvas_json` |
     ```
   - Add examples showing all formats
   - Update migration guide if this is a new capability

2. **BDD Phase** (1-2 hours)
   - Extend scenario in `tests/features/page_operations.feature`:
     ```gherkin
     Scenario Outline: get_{{integration}}_page supports multiple formats
       When I call "get_{{integration}}_page" with content_format = "<format>"
       Then the response includes content in "<format>" format

       Examples:
         | format      |
         | markdown    |
         | html        |
         | canvas_json |
     ```

3. **TDD Phase** (2-4 hours)
   - RED: Add parameter to signature, write failing tests
   - GREEN: Implement parameter passing to {{INTEGRATION}} API
   - REFACTOR: Validate format values, add error handling

4. **CI & Merge** (same as above)

**Total Time**: 1-2 days

## Quality Gates

### PR Checklist (enforced via GitHub template)

Every PR must satisfy:

- [ ] **Documentation First (DDD)**
  - [ ] API reference updated (if tool/API change)
  - [ ] Acceptance criteria defined in issue/PR description
  - [ ] Migration guide updated (if breaking change)
  - [ ] CHANGELOG.md entry added

- [ ] **Behavior Specifications (BDD)**
  - [ ] Gherkin scenarios written for new behavior
  - [ ] All BDD scenarios pass (pytest-bdd)
  - [ ] Contract tests pass for affected tools

- [ ] **Test Coverage (TDD)**
  - [ ] Unit tests added/updated (≥90% coverage)
  - [ ] Integration tests added (if API interaction)
  - [ ] Regression test added (if bug fix)
  - [ ] All tests pass locally

- [ ] **Code Quality**
  - [ ] Lint passes (ruff check)
  - [ ] Type hints complete (mypy)
  - [ ] Security scan passes (bandit, pip-audit)
  - [ ] No code smells (complexity, duplication)

- [ ] **Review**
  - [ ] Code reviewed by 1+ engineers
  - [ ] Documentation reviewed by technical writer (for API changes)
  - [ ] All review comments addressed

### CI/CD Pipeline

**Triggered on**: Push to feature branch, PR to develop/main

**Stages** (must all pass):

1. **Lint** (30 sec)
   - ruff check → No errors
   - black --check → Formatted
   - mypy → Type safe

2. **Unit Tests** (1-2 min)
   - pytest tests/unit/ --cov
   - Coverage ≥90% for new code
   - All tests pass

3. **Contract Tests** (1-2 min)
   - pytest tests/contracts/
   - All 31 canonical tools validate
   - All 19 aliases forward correctly
   - Response shapes comply with standards

4. **BDD Scenarios** (2-3 min)
   - pytest tests/features/ --gherkin-terminal-reporter
   - All scenarios pass
   - Step coverage 100%

5. **Integration Tests** (3-5 min)
   - pytest tests/integration/
   - Real {{INTEGRATION}} API calls (test document)
   - Error scenarios (401/403/404/429) handled
   - Coverage ≥80%

6. **Security Scan** (1-2 min)
   - bandit -r src/ → No critical findings
   - pip-audit → No high-severity vulnerabilities

7. **Coverage Report** (30 sec)
   - Aggregate coverage ≥85%
   - Upload to Codecov
   - Block merge if coverage drops

**Total Pipeline Time**: 8-12 minutes

**Merge Conditions**:
- All stages GREEN
- 1+ code review approval
- No unresolved review comments
- Branch up to date with target

## Branching Strategy

### Branch Types

- **`main`**: Production releases only
  - Protected: no direct commits
  - Tagged with semantic versions (v0.5.0)
  - Published to PyPI

- **`develop`**: Integration branch
  - Protected: requires PR + CI
  - Staging ground for next release
  - Regular E2E regression tests

- **`feature/*`**: New features
  - Example: `feature/create-{{integration}}-table`
  - PR to `develop`
  - Delete after merge

- **`fix/*`**: Bug fixes
  - Example: `fix/formula-injection-42`
  - PR to `develop`
  - Delete after merge

- **`hotfix/*`**: Critical production fixes
  - Example: `hotfix/security-cve-123`
  - PR to BOTH `main` AND `develop`
  - Emergency releases (v0.5.1)

### Release Process

1. **Prepare Release** (in `develop`)
   - Update `pyproject.toml` version (semantic versioning)
   - Update `CHANGELOG.md` with all changes since last release
   - Update migration guide if breaking changes
   - Finalize release notes in `docs/release/v{X.Y.Z}-release-notes.md`

2. **Create Release PR** (`develop` → `main`)
   - Title: "Release v{X.Y.Z}"
   - Description: Link to release notes, migration guide
   - Trigger E2E smoke tests
   - Get release manager approval

3. **Merge & Tag**
   - Merge to `main`
   - Tag commit: `git tag v{X.Y.Z}`
   - Push tag: `git push origin v{X.Y.Z}`

4. **Automated Release** (triggered by tag push)
   - `.github/workflows/release.yml` runs
   - Build package (wheel + sdist)
   - Publish to PyPI
   - Create GitHub Release with notes
   - Upload release artifacts

5. **Post-Release**
   - Announce in GitHub Discussions
   - Update documentation site
   - Monitor for issues
   - Merge `main` back to `develop`

## Semantic Versioning Rules

**Version Format**: `MAJOR.MINOR.PATCH` (e.g., `0.5.0`)

- **MAJOR**: Breaking changes (incompatible API changes)
  - Example: Removing a tool, changing response shape
  - Migration guide REQUIRED
  - Deprecation warnings in previous MINOR release

- **MINOR**: New features (backward compatible)
  - Example: Adding new tool, new parameter (with default)
  - Update API reference docs
  - Release notes highlighting new capabilities

- **PATCH**: Bug fixes (backward compatible)
  - Example: Fixing validation, error handling
  - CHANGELOG entry
  - Quick turnaround (no feature freeze)

**Pre-release versions**: `{MAJOR}.{MINOR}.{PATCH}-{pre}.{N}`
- Examples: `0.5.0-alpha.1`, `0.5.0-beta.2`, `0.5.0-rc.1`
- Used for testing before official release

## Metrics & KPIs

### Development Velocity
- **Cycle Time**: Issue open → PR merged (target: <5 days)
- **Lead Time**: Commit → Production (target: <2 weeks)
- **PR Throughput**: PRs merged per week (track trend)

### Quality Metrics
- **Test Coverage**: Overall ≥85% (unit ≥90%, integration ≥80%)
- **Bug Escape Rate**: Bugs found in production (target: <2 per release)
- **Mean Time to Recover** (MTTR): Critical bug fix deployment (target: <4 hours)
- **Security Findings**: Critical vulnerabilities (target: 0)

### Process Adoption
- **Documentation First**: % of PRs with docs updated before code (target: 100%)
- **BDD Coverage**: % of tools with BDD scenarios (target: 100%)
- **TDD Practice**: % of commits with test + implementation (target: ≥80%)
- **CI Success Rate**: % of CI runs passing (target: ≥95%)

## Related Documentation

- [DDD Workflow](ddd-workflow.md) - Documentation-first principles
- [BDD Workflow](bdd-workflow.md) - Gherkin and pytest-bdd guide
- [TDD Workflow](tdd-workflow.md) - Red-Green-Refactor cycles
- Contributing guide - Step-by-step contributor onboarding
- Tool standards - API contract specifications
- Testing philosophy - Testing strategy

---

**Version**: 0.5.0
**Last Updated**: 2025-10-15
**Maintainer**: MCP Server {{INTEGRATION}} Team
