---
title: Documentation Driven Development
type: explanation
status: current
audience: intermediate
last_updated: 2025-10-21
category: process
related:
  - ../process/DOCUMENTATION_STANDARD.md
  - ../../dev-docs/DEVELOPMENT_LIFECYCLE.md
  - ../../dev-docs/TESTING.md
source: "dev-docs/DDD_WORKFLOW.md, project experience"
---

# Documentation Driven Development (DDD)

## What is Documentation Driven Development?

**Documentation Driven Development (DDD)** is a development approach where documentation is written **before code**, not after. Documentation serves as the executable specification, design tool, and communication medium that drives implementation.

### Core Principle

> "If you can't document it clearly, you can't build it correctly."

In traditional development, documentation lags behind code and often becomes stale. In DDD, documentation **is** the specification, so it can never be out of sync.

### The DDD Promise

When done correctly, DDD eliminates common documentation problems:
- ❌ **API Drift** - Docs lag behind code changes
- ❌ **Stale Examples** - Code examples don't match reality
- ❌ **Late-Stage Design Issues** - Costly to fix after implementation
- ❌ **Incomplete Coverage** - Missing edge cases and error scenarios

✅ **With DDD:**
- Documentation and code are always synchronized (docs came first)
- API design flaws are caught before expensive implementation
- Test cases are derived directly from documentation examples
- Implementation is guaranteed to match specification

---

## Why Documentation First?

### 1. Documentation as Design Tool

Writing documentation forces clarity about:
- **Interfaces** - What parameters? What returns?
- **Behavior** - What happens in edge cases?
- **Errors** - What can go wrong? How is it communicated?
- **Naming** - Are names clear and consistent?

**Example:** Trying to document a tool signature reveals design issues:

```markdown
<!-- BEFORE DDD (vague) -->
## do_something
Does something with the thing.

<!-- AFTER DDD (clear) -->
## create_workflow_from_template
Creates a new workflow from an existing template.

**Parameters:**
- template_id (string, required) - ID of template to clone
- workflow_name (string, required) - Name for new workflow
- customizations (object, optional) - Field overrides

**Returns:**
- workflow_id (string) - ID of created workflow
- created_at (ISO 8601 string) - Creation timestamp

**Errors:**
- 404 - Template not found
- 403 - No access to template
- 400 - Invalid workflow_name (contains special chars)
```

The second version required thinking through the design. Writing it revealed:
- Need to handle missing templates
- Need to validate workflow names
- Need to return creation timestamp for tracking

### 2. Documentation as Communication

Stakeholders can review documentation before expensive development:
- **Product owners** - Verify features match requirements
- **Developers** - Understand what to build
- **QA** - Know what to test
- **Users** - See what's coming

**Review cycle:**
1. Write API documentation
2. Stakeholders review and provide feedback
3. Iterate on documentation (cheap)
4. Approve documentation
5. Implement (expensive, but now clearly specified)

### 3. Documentation as Executable Specification

Documentation examples become test cases:

```markdown
## Example: Create Workflow

\`\`\`python
result = create_workflow_from_template(
    template_id="daily-report-template",
    workflow_name="Engineering Weekly Report"
)
assert result["workflow_id"].startswith("wf_")
assert "created_at" in result
\`\`\`
```

This example is:
- ✅ **Extracted to tests** - Becomes `test_create_workflow_from_template()`
- ✅ **Executed in CI** - Fails if implementation doesn't match
- ✅ **Always up-to-date** - Tests break if docs don't match reality

---

## DDD + Diátaxis: The Meta-Framework

mcp-n8n uses two complementary systems that work together:

### DDD Answers "WHEN"

**When do you write documentation?**
- **DDD:** Write documentation **BEFORE** code
- Documentation is the specification, not an afterthought

### Diátaxis Answers "HOW"

**How do you organize documentation?**
- **Diátaxis:** Organize by user intent (tutorial/how-to/reference/explanation)
- Each document type serves a different purpose

### The Integration

Together, DDD and Diátaxis tell you:
1. **WHAT** to write → Diátaxis framework (4 types)
2. **WHEN** to write it → DDD (before code)
3. **HOW** to structure it → DOCUMENTATION_STANDARD.md
4. **WHY** it matters → This document!

**The Complete Flow:**

```
Change Request
    ↓
1. DDD Phase: Write Diátaxis Docs FIRST
    ├─ Explanation → Why this change? (context, business value)
    ├─ Reference → API specification (parameters, returns, errors)
    ├─ How-To → Usage patterns (solve specific problems)
    └─ Tutorial → Learning path (optional, for major features)
    ↓
2. BDD Phase: Extract Scenarios from Docs
    └─ Reference acceptance criteria → Gherkin scenarios
    ↓
3. TDD Phase: Implement from Tests
    └─ BDD scenarios → Failing tests → Implementation
    ↓
Result: Code that matches docs (because docs came first!)
```

---

## The DDD Workflow

### Phase 1: Understand the Need

**Input:** User story, feature request, or bug report

**Output:** Clear understanding of "why" and "who"

**Questions to answer:**
- Why is this needed? (business value, user pain point)
- Who will use it? (AI agents, developers, both)
- What problem does it solve?

**Example:**
```markdown
**User Story:** As an AI agent, I want to create workflows from templates
so that I can quickly scaffold common automation patterns.

**User Need:** Currently must manually configure each workflow.
Using templates would save time and ensure consistency.

**Users:** Claude, ChatGPT, custom MCP clients
```

### Phase 2: Define Acceptance Criteria

**Format:** Given-When-Then (feeds into BDD)

```markdown
**Acceptance Criteria:**

1. **Given** a valid template ID
   **When** I call `create_workflow_from_template`
   **Then** a new workflow is created with template defaults

2. **Given** an invalid template ID
   **When** I call `create_workflow_from_template`
   **Then** the tool returns a 404 error with clear message

3. **Given** a workflow name with special characters
   **When** I call `create_workflow_from_template`
   **Then** the tool returns a 400 error explaining valid names
```

These acceptance criteria become BDD scenarios directly.

### Phase 3: Design the API

**Output:** Complete API reference documentation

**Location:** `docs/reference/` (following DOCUMENTATION_STANDARD.md)

**Must include:**
- Tool signature (parameters and types)
- Return value structure
- Error scenarios
- **Executable examples** (marked with `test_extraction: true`)

**Example:**
```markdown
---
title: Workflow Tools
type: reference
test_extraction: true
---

## create_workflow_from_template

**Parameters:**
- `template_id` (string, required) - Template to clone
- `workflow_name` (string, required) - Name for new workflow
- `customizations` (object, optional) - Field overrides

**Returns:**
```json
{
  "workflow_id": "wf_abc123",
  "created_at": "2025-10-21T10:30:00Z",
  "template_id": "daily-report-template"
}
```

**Examples:**
\`\`\`python
# Create workflow from template
result = create_workflow_from_template(
    template_id="daily-report-template",
    workflow_name="Engineering Weekly Report"
)
assert result["workflow_id"].startswith("wf_")
\`\`\`

**Errors:**
- 404: Template not found
- 403: No access to template
- 400: Invalid workflow_name
```

### Phase 4: Write Supporting Documentation

**How-To Guide** (docs/how-to/):
```markdown
---
title: Create Custom Workflows
type: how-to
---

# Create Custom Workflows

## Problem

You need to create a workflow with specific configuration.

## Solutions

### Solution 1: Use a Template

[Shows how to use create_workflow_from_template]

### Solution 2: Manual Configuration

[Shows alternative approach]
```

**Tutorial** (docs/tutorials/) - Optional for major features:
```markdown
---
title: Build Your First Workflow
type: tutorial
---

# Build Your First Workflow

In this tutorial, you'll create an automated daily report workflow
using templates and customization.

[Step-by-step learning path]
```

### Phase 5: Review Documentation

**Before any coding:**
1. Stakeholders review documentation
2. Check for clarity, completeness, consistency
3. Iterate on documentation (cheap to change)
4. Approve documentation as specification

### Phase 6: Extract BDD Scenarios

From acceptance criteria in reference docs:

```gherkin
Feature: Workflow Template Creation

  Scenario: Create workflow from valid template
    Given a template "daily-report-template" exists
    When I create workflow from template with name "Weekly Report"
    Then a new workflow is created
    And the workflow ID starts with "wf_"
    And the created_at timestamp is recent
```

### Phase 7: Implement via TDD

BDD scenarios drive TDD implementation:

1. **RED** - Write failing test from BDD scenario
2. **GREEN** - Implement minimal code to pass
3. **REFACTOR** - Improve design (tests stay green)
4. **REPEAT** - Next scenario

**Result:** Code that passes all documentation-derived tests.

---

## Real Example: Sprint 5 Workflows

### The Change Request

[docs/archive/sprints/change-requests/sprint-5-workflows/intent.md](../archive/sprints/change-requests/sprint-5-workflows/intent.md)

**Followed DDD:**
1. **Intent document** (Explanation) - Why workflows? Business value?
2. **API reference** - Defined tool signatures before implementation
3. **BDD scenarios** - 23 Gherkin scenarios from acceptance criteria
4. **Implementation** - TDD driven by BDD scenarios

### The Results

- ✅ **49 unit tests passing** - All derived from documentation
- ✅ **Zero API drift** - Implementation matches docs exactly
- ✅ **Clear specification** - Reviewers approved docs before coding
- ✅ **Living documentation** - Tests extracted from docs, so docs must be accurate

### The Documentation Created

Following Diátaxis (per DOCUMENTATION_STANDARD.md):

**Explanation:**
- [workflows.md](workflows.md) - Understanding workflow concepts

**Reference:**
- [tools.md](../reference/tools.md) - Tool signatures (run_daily_report, etc.)
- [cli-reference.md](../reference/cli-reference.md) - CLI usage

**How-To:**
- [build-custom-workflow.md](../how-to/build-custom-workflow.md) - Creating workflows

**Tutorial:**
- [event-driven-workflow.md](../tutorials/event-driven-workflow.md) - Learning path

**All written BEFORE implementation.**

---

## Benefits of DDD in Practice

### From mcp-n8n Experience

**Sprint 5 (Workflows):**
- **Documentation first:** 2 days of API design and review
- **Implementation:** 3 days (clear spec made this fast)
- **Result:** 49 tests passing, zero bugs, perfect doc-code match

**Sprint 3 (Event Monitoring):**
- **Traditional approach (no DDD):** 5 days, 3 bugs found later
- **After adopting DDD:** Clear specification prevented bugs

### Measured Benefits

1. **Zero API Drift**
   - Docs written first → Can't lag behind
   - Tests extracted from docs → Docs must be accurate
   - CI fails if examples don't work

2. **Better Design**
   - Writing docs reveals design flaws early
   - Cheaper to fix docs than code
   - Stakeholder review before expensive dev

3. **Faster Implementation**
   - Clear specification → Less uncertainty
   - Pre-approved design → No mid-flight changes
   - Tests from docs → Know when you're done

4. **Living Documentation**
   - Examples are tested → Always work
   - Tests break if docs drift → Forces updates
   - Documentation is trustworthy

---

## Common Questions

### "Isn't documentation overhead?"

**No** - Documentation is investment that pays off:
- **Writing docs:** 2-3 hours
- **Fixing design issues found in docs:** Saved 1-2 days of rework
- **Stakeholder alignment:** Prevented wrong feature being built
- **Test creation:** Tests derive from docs automatically

**Net result:** Faster delivery, fewer bugs, better product.

### "What if requirements change?"

**Update docs first, then code:**
1. Modify reference documentation
2. Update BDD scenarios
3. Tests fail (expected)
4. Update code to match new docs
5. Tests pass

Documentation remains source of truth.

### "Do all docs need to be written before code?"

**No** - Focus on Reference docs:
- **Must write first:** Reference (API specification)
- **Should write first:** How-To (common patterns)
- **Can write after:** Tutorial (if minor feature)
- **Can evolve:** Explanation (understanding deepens)

**Minimum DDD:** Write Reference docs first with executable examples.

---

## Related Documentation

### Process Documentation

- **[DOCUMENTATION_STANDARD.md](../process/DOCUMENTATION_STANDARD.md)** - How to structure documentation (templates, formats, Diátaxis)
- **[DEVELOPMENT_LIFECYCLE.md](../../dev-docs/DEVELOPMENT_LIFECYCLE.md)** - Complete DDD→BDD→TDD→CI/CD flow
- **[TESTING.md](../../dev-docs/TESTING.md)** - BDD and TDD implementation details

### Examples in Practice

- **Sprint 5 Intent:** [docs/archive/sprints/change-requests/sprint-5-workflows/intent.md](../archive/sprints/change-requests/sprint-5-workflows/intent.md)
- **Sprint 3 DDD Summary:** [docs/archive/sprints/change-requests/sprint-3-event-monitoring/ddd-success-summary.md](../archive/sprints/change-requests/sprint-3-event-monitoring/ddd-success-summary.md)

### Product Documentation

- **[Architecture](architecture.md)** - How DDD influenced system design
- **[Memory System](memory-system.md)** - Example of DDD-designed feature
- **[Workflows](workflows.md)** - Sprint 5 DDD success story

---

## Summary

**Documentation Driven Development** means writing documentation BEFORE code. Combined with **Diátaxis** (organizing by user intent), it creates a powerful development approach:

1. **DDD** tells you **WHEN** → Write docs first
2. **Diátaxis** tells you **HOW** → Organize by intent (tutorial/how-to/reference/explanation)
3. **DOCUMENTATION_STANDARD** tells you **WHAT** → Templates and formats
4. **BDD/TDD** tells you **HOW TO IMPLEMENT** → Tests from docs

**The result:**
- Code that matches documentation (because docs came first)
- Better design (flaws caught in docs, not code)
- Faster implementation (clear specification)
- Living documentation (tests keep it accurate)

**Next steps:**
- Read [DOCUMENTATION_STANDARD.md](../process/DOCUMENTATION_STANDARD.md) for templates
- Review [DEVELOPMENT_LIFECYCLE.md](../../dev-docs/DEVELOPMENT_LIFECYCLE.md) for complete flow
- See [TESTING.md](../../dev-docs/TESTING.md) for BDD/TDD details
