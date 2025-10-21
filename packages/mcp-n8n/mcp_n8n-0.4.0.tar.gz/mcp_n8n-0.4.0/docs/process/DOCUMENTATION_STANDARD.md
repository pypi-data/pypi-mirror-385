---
title: mcp-n8n Documentation Standard
type: process
status: current
audience: all
last_updated: 2025-10-20
version: 1.0.0
---

# mcp-n8n Documentation Standard

**Purpose:** Define documentation structure, formats, and processes for mcp-n8n project
**Scope:** All markdown files in `docs/`
**Framework:** Diátaxis (documentation system)
**Last Updated:** 2025-10-20
**Status:** Active

---

## Table of Contents

1. [Overview](#overview)
2. [Diátaxis Framework](#diátaxis-framework)
3. [Directory Structure](#directory-structure)
4. [Frontmatter Schema](#frontmatter-schema)
5. [Document Templates](#document-templates)
6. [Writing Standards](#writing-standards)
7. [Process Integration](#process-integration)
8. [Automation & Validation](#automation--validation)
9. [Migration Guide](#migration-guide)

---

## Overview

### Philosophy

mcp-n8n follows **Documentation Driven Design (DDD)**:
- Documentation is written BEFORE code
- Documentation serves as executable specification
- Tests are extracted FROM documentation examples
- Documentation and code stay synchronized

### Core Principles

1. **User Intent**: Organize by what users want to DO, not by technical topics
2. **Executable Examples**: All code examples must be testable
3. **Cross-References**: Related docs must link to each other
4. **Maintenance**: Clear ownership, update schedules, staleness warnings
5. **Accessibility**: Clear audience targeting (beginners vs. advanced)

---

## Diátaxis Framework

mcp-n8n organizes documentation by **user intent**, following the [Diátaxis framework](https://diataxis.fr/):

### The Four Document Types

| Type | Purpose | User Intent | Structure |
|------|---------|-------------|-----------|
| **Tutorial** | Learning-oriented | "Teach me" | Step-by-step lessons with expected output |
| **How-To Guide** | Task-oriented | "Show me how to solve X" | Problem → Solution variations |
| **Reference** | Information-oriented | "What parameters does this take?" | Specifications, API docs, schemas |
| **Explanation** | Understanding-oriented | "Why does this work this way?" | Concepts, context, design decisions |

### When to Use Each Type

**Tutorial:**
- ✅ First-time user onboarding
- ✅ Learning a new feature end-to-end
- ✅ Building confidence through success
- ❌ NOT for solving specific problems (use How-To)

**How-To Guide:**
- ✅ Solving a specific problem
- ✅ Achieving a particular goal
- ✅ Multiple approaches to same problem
- ❌ NOT for teaching concepts (use Tutorial)

**Reference:**
- ✅ API documentation
- ✅ Configuration options
- ✅ Schema specifications
- ❌ NOT for explaining why (use Explanation)

**Explanation:**
- ✅ Architecture decisions
- ✅ Design patterns
- ✅ System context and history
- ❌ NOT for step-by-step instructions (use Tutorial)

---

## Directory Structure

### Standard Layout

```
docs/
├── tutorials/                # Learning-oriented (hands-on)
│   ├── 01-getting-started.md
│   ├── 02-first-validation-workflow.md
│   └── 03-multi-step-content-generation.md
│
├── how-to/                   # Task-oriented (problem-solving)
│   ├── integration/
│   │   ├── n8n-integration-guide.md
│   │   ├── debug-event-correlation.md
│   │   └── pre-validate-dependencies.md
│   ├── workflows/
│   │   ├── handle-validation-errors.md
│   │   └── configure-timeout-handling.md
│   └── troubleshooting.md
│
├── reference/                # Information-oriented (specifications)
│   ├── api/
│   │   ├── event-schema.md
│   │   ├── telemetry-capabilities-schema.md
│   │   └── backend-api.md
│   ├── architecture.md
│   ├── performance-baseline.md
│   └── workflows/
│       └── daily-report.md
│
├── explanation/              # Understanding-oriented (concepts)
│   ├── ecosystem/
│   │   ├── architecture.md
│   │   ├── integration-analysis.md
│   │   └── chora-compose-architecture.md
│   ├── process/
│   │   ├── bdd-workflow.md
│   │   ├── ddd-workflow.md
│   │   ├── tdd-workflow.md
│   │   └── development-lifecycle.md
│   └── design-decisions/
│       └── gateway-pattern-p5.md
│
├── project/                  # Project status & planning
│   ├── SPRINT_STATUS.md
│   ├── UNIFIED_ROADMAP.md
│   ├── sprints/
│   │   └── sprint-1-validation.md
│   ├── releases/
│   │   ├── RELEASE_CHECKLIST.md
│   │   └── ROLLBACK_PROCEDURE.md
│   └── integration-planning/
│       ├── INTEGRATION_STRATEGY_UPDATE.md
│       └── CHORA_ROADMAP_ALIGNMENT.md
│
├── change-requests/          # Sprint-specific change documentation
│   ├── sprint-3-event-monitoring/
│   └── sprint-5-workflows/
│
└── archived/                 # Deprecated/historical docs
    └── ROADMAP_V1.md
```

### Migration Strategy

**Soft Migration (Recommended):**
1. Create new Diátaxis structure
2. Symlink old paths to new locations
3. Update new docs to use new structure
4. Gradually migrate old docs
5. Deprecate warnings in old locations

**Backward Compatibility:**
```bash
# Old location still works via symlink
docs/TROUBLESHOOTING.md → docs/how-to/troubleshooting.md
docs/ecosystem/architecture.md → docs/explanation/ecosystem/architecture.md
```

---

## Frontmatter Schema

### Required Fields (All Documents)

```yaml
---
title: "Document Title"                  # Human-readable title
type: tutorial | how-to | reference | explanation | process | project | change-request
status: current | draft | deprecated      # Lifecycle status
last_updated: YYYY-MM-DD                  # ISO 8601 date
---
```

### Optional Fields

```yaml
---
# Audience & Context
audience: beginners | intermediate | advanced | maintainers
sprint: 2-5                               # Sprint number (for sprint-specific docs)

# Navigation & Discovery
category: integration | workflows | architecture | testing
tags: [n8n, chora-compose, validation]   # Searchable tags
related:                                  # Cross-references
  - ../how-to/handle-validation-errors.md
  - ../../reference/api/event-schema.md

# For Tutorials & How-To Guides
estimated_time: "30 minutes"              # How long to complete
prerequisites:                            # What to know/have first
  - tutorials/01-getting-started.md
  - Basic Python knowledge

# For Reference Docs
version: 1.0.0                            # API/schema version
test_extraction: true                     # Has executable examples for testing

# Metadata
created: YYYY-MM-DD                       # Original creation date
author: "Team Name"                       # Original author
maintainer: "Current Owner"               # Who maintains this doc
---
```

### Frontmatter Examples

**Tutorial:**
```yaml
---
title: "Build Your First n8n Validation Workflow"
type: tutorial
status: current
audience: beginners
last_updated: 2025-10-20
estimated_time: "30 minutes"
prerequisites:
  - tutorials/01-getting-started.md
  - n8n installed
related:
  - ../how-to/workflows/handle-validation-errors.md
  - ../reference/workflows/validation-workflow.md
---
```

**How-To Guide:**
```yaml
---
title: "How to Handle Validation Errors in n8n"
type: how-to
status: current
audience: intermediate
last_updated: 2025-10-20
category: workflows
tags: [error-handling, validation, n8n]
related:
  - ../tutorials/02-first-validation-workflow.md
  - ../../reference/api/event-schema.md
---
```

**Reference:**
```yaml
---
title: "Event Schema v1.0 Specification"
type: reference
status: current
audience: all
last_updated: 2025-10-20
version: 1.0.0
test_extraction: true
category: api
related:
  - telemetry-capabilities-schema.md
  - ../../how-to/integration/debug-event-correlation.md
---
```

**Explanation:**
```yaml
---
title: "Gateway Pattern P5: Architecture Deep Dive"
type: explanation
status: current
audience: advanced
last_updated: 2025-10-20
category: architecture
related:
  - ecosystem/architecture.md
  - ../../reference/architecture.md
---
```

---

## Document Templates

### Tutorial Template

```markdown
---
title: "{Tutorial Name}"
type: tutorial
status: current
audience: beginners | intermediate
last_updated: YYYY-MM-DD
estimated_time: "XX minutes"
prerequisites: []
related: []
---

# Tutorial: {Name}

## What You'll Build

Brief description of the end result (1-2 sentences).

## What You'll Learn

- Skill 1
- Skill 2
- Skill 3

## Prerequisites

- [ ] Prerequisite 1
- [ ] Prerequisite 2
- [ ] Tool installed

## Time Required

Approximately XX minutes

---

## Step 1: {Action}

**What we're doing:** Brief explanation

**Code:**
```bash
# Copy-pasteable command
command --with-flags
```

**Expected output:**
```
✓ Success message
```

**Explanation:** Why this step matters, what it does

---

## Step 2: {Action}

...continue with numbered steps...

---

## What You've Learned

- Summary of skills acquired
- What you can do now

## Next Steps

Where to go from here:
- [ ] Tutorial 2: Advanced topic
- [ ] How-to Guide: Solve specific problem
- [ ] Build your own variation

## Troubleshooting

**Problem:** Common error
**Solution:** How to fix

---

## Related Documentation

- [How-To: Related Task](../how-to/...)
- [Reference: API Used](../reference/...)
```

### How-To Guide Template

```markdown
---
title: "How to {Task}"
type: how-to
status: current
audience: intermediate
last_updated: YYYY-MM-DD
category: {workflows | integration | testing}
tags: []
related: []
---

# How to {Task}

## Problem

Brief description of the problem this guide solves (2-3 sentences).

## Solution Overview

High-level approach (bullet points).

## Prerequisites

- [ ] Prerequisite 1
- [ ] Prerequisite 2

---

## Approach 1: {Method Name} (Recommended)

**When to use:** Situation where this approach works best

**Steps:**

1. Do this
   ```bash
   command
   ```

2. Then this
   ```python
   code_example()
   ```

3. Finally this

**Pros:**
- ✅ Advantage 1
- ✅ Advantage 2

**Cons:**
- ❌ Limitation 1

---

## Approach 2: {Alternative Method}

**When to use:** Different situation

**Steps:** ...

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Error X | Reason | Fix Y |

---

## Related Documentation

- [Tutorial: Learn the Basics](../tutorials/...)
- [Reference: API Documentation](../reference/...)
```

### Reference Template

```markdown
---
title: "{API/Schema Name}"
type: reference
status: current
audience: all
last_updated: YYYY-MM-DD
version: X.Y.Z
test_extraction: true
category: api
related: []
---

# {API/Schema Name}

## Overview

Brief description (1-2 sentences).

**Status:** ✅ Stable | ⚠️ Beta | 🚧 Experimental
**Version:** X.Y.Z
**Last Updated:** YYYY-MM-DD

---

## Specification

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `param1` | string | Yes | – | Description |
| `param2` | number | No | `0` | Description |

### Response Schema

```json
{
  "field1": "value",
  "field2": 123
}
```

### Field Definitions

**`field1`** (string)
- Description
- Valid values: `option1`, `option2`
- Example: `"example-value"`

---

## Examples

### Example 1: {Common Use Case}

```python
# Executable example
result = api_call(
    param1="value",
    param2=123
)
# Expected result
assert result["field1"] == "value"
```

### Example 2: {Edge Case}

```python
# Error handling
result = api_call(invalid_param="bad")
# Returns: {"error": "Invalid parameter"}
```

---

## Test Cases

**Note:** These examples are extracted for automated testing (test_extraction: true)

```python
# tests/integration/test_from_docs.py
def test_example_1():
    """Test from Reference docs: Example 1"""
    result = api_call(param1="value", param2=123)
    assert result["field1"] == "value"
```

---

## Error Scenarios

| Error | HTTP Code | Cause | Resolution |
|-------|-----------|-------|------------|
| Not Found | 404 | Invalid ID | Verify ID exists |
| Forbidden | 403 | No access | Request permissions |

---

## Related Documentation

- [How-To: Use This API](../how-to/...)
- [Explanation: Why This Design](../../explanation/...)
```

### Explanation Template

```markdown
---
title: "{Concept/Decision Title}"
type: explanation
status: current
audience: intermediate | advanced
last_updated: YYYY-MM-DD
category: {architecture | design-patterns | process}
related: []
---

# {Concept Name}

## Overview

What is this concept/decision? (2-3 sentences)

## Context

**Problem:** What problem does this solve?

**Constraints:** What limitations did we work within?

**Alternatives Considered:** What else did we evaluate?

---

## The Solution

### High-Level Approach

Description with diagrams if applicable.

```
┌─────────────┐
│   Component │
│      A      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Component │
│      B      │
└─────────────┘
```

### Key Decisions

1. **Decision:** What we chose
   - **Rationale:** Why we chose it
   - **Trade-offs:** What we gave up

2. **Decision:** ...

---

## How It Works

Technical deep-dive (as needed for understanding).

---

## Benefits

- ✅ Benefit 1
- ✅ Benefit 2

## Limitations

- ❌ Limitation 1
- ⚠️ Trade-off 1

---

## Related Patterns

- Pattern X: Similar approach in different context
- Pattern Y: Complementary pattern

---

## Related Documentation

- [Reference: Architecture](../reference/architecture.md)
- [How-To: Implement This](../how-to/...)
```

---

## Writing Standards

### General Principles

1. **Clarity First**
   - Use simple language
   - Define technical terms on first use
   - One idea per paragraph

2. **Active Voice**
   - ✅ "Run the command"
   - ❌ "The command should be run"

3. **Present Tense**
   - ✅ "The system validates input"
   - ❌ "The system will validate input"

4. **Consistency**
   - Use same terminology throughout
   - Follow naming conventions
   - Maintain consistent structure

### Code Blocks

**All code blocks MUST specify language:**

```markdown
✅ GOOD:
\`\`\`python
def example():
    return "testable"
\`\`\`

❌ BAD:
\`\`\`
def example():
    return "not testable"
\`\`\`
```

**Executable examples MUST be complete:**

```python
# ✅ GOOD: Complete, runnable
from mcp_n8n.gateway import Gateway

async def main():
    gateway = Gateway()
    result = await gateway.call_tool("chora:validate_content", {...})
    assert result["success"] is True

# ❌ BAD: Missing imports, incomplete
result = gateway.call_tool(...)
assert result["success"]
```

### Examples Requirements

**Reference docs MUST include:**
- Happy path example (most common use)
- Error handling example
- Edge case example (if applicable)
- Complete, copy-pasteable code

**Tutorials MUST include:**
- Expected output for each step
- Explanation of what each step does
- Troubleshooting for common issues

**How-To guides MUST include:**
- Multiple approaches (when applicable)
- When to use each approach
- Pros/cons of each approach

### Cross-References

**Use relative paths:**
```markdown
✅ GOOD: [How-To Guide](../how-to/solve-problem.md)
❌ BAD: [How-To Guide](/docs/how-to/solve-problem.md)
```

**Link to specific sections:**
```markdown
[Event Schema v1.0](../reference/api/event-schema.md#field-definitions)
```

**Required links:**
- Related tutorials (in how-to guides)
- Related how-to guides (in tutorials)
- API reference (in tutorials and how-to guides)
- Explanation context (in reference docs)

### Frontmatter Rules

1. **All docs MUST have frontmatter** (no exceptions)
2. **Required fields cannot be omitted**
3. **Dates use ISO 8601** (YYYY-MM-DD)
4. **Status must be accurate** (update when deprecated)
5. **Related docs must be bidirectional** (if A links to B, B links to A)

---

## Process Integration

### BDD Workflow

Reference: [BDD Workflow](bdd-workflow.md)

**Integration Points:**
1. **Feature Files** → Reference docs
   - Gherkin scenarios derived from API reference acceptance criteria
   - Reference docs updated BEFORE feature files

2. **Step Definitions** → How-To guides
   - Common step patterns extracted to how-to guides
   - Reusable step libraries documented

3. **Examples** → Tutorials
   - BDD scenarios become tutorial steps
   - Tutorial "What You'll Build" matches BDD feature description

### DDD Workflow

Reference: [DDD Workflow](ddd-workflow.md)

**Integration Points:**
1. **Change Requests** → All doc types
   - Explanation section → explanation docs
   - How-to section → how-to guides
   - Reference section → reference docs
   - Tutorial (optional) → tutorials

2. **API Design** → Reference docs
   - API reference written BEFORE implementation
   - Reference docs include acceptance criteria
   - Examples are executable

3. **Documentation Review** → Quality gate
   - Docs reviewed and approved before coding
   - Documentation-first enforced in PR template

### TDD Workflow

Reference: [TDD Workflow](tdd-workflow.md)

**Integration Points:**
1. **Test Extraction** → Automated
   - Code examples marked with `test_extraction: true`
   - Tests extracted to `tests/integration/test_from_docs.py`
   - CI fails if examples don't work

2. **Red-Green-Refactor** → Documentation updates
   - Red: Write failing test from reference doc example
   - Green: Implement to make test pass
   - Refactor: Update docs if API changes

---

## Automation & Validation

### Scripts

**Location:** `scripts/`

#### 1. Generate Documentation Map

**File:** `scripts/generate_docs_map.py`

**Purpose:** Auto-generate DOCUMENTATION_MAP.md from frontmatter

**Usage:**
```bash
python scripts/generate_docs_map.py
# Outputs: docs/DOCUMENTATION_MAP.md
```

#### 2. Validate Documentation

**File:** `scripts/validate_docs.py`

**Purpose:** Check documentation quality

**Checks:**
- [ ] All docs have frontmatter
- [ ] Required fields present
- [ ] Frontmatter schema valid
- [ ] No broken internal links
- [ ] Staleness warnings (>90 days)
- [ ] Related links are bidirectional

**Usage:**
```bash
python scripts/validate_docs.py
# Exit code 0 = pass, 1 = fail
```

#### 3. Extract Tests from Documentation

**File:** `scripts/extract_tests.py`

**Purpose:** Extract code examples for testing

**Process:**
1. Find docs with `test_extraction: true`
2. Parse code blocks with language tags
3. Generate test file: `tests/integration/test_from_docs.py`
4. Run tests in CI

**Usage:**
```bash
python scripts/extract_tests.py
pytest tests/integration/test_from_docs.py
```

### CI Integration

**File:** `.github/workflows/docs.yml`

**Triggers:**
- Pull requests (any docs/ changes)
- Nightly (staleness checks)

**Checks:**
1. ✅ Frontmatter schema valid
2. ✅ No broken internal links
3. ✅ Documentation examples work (extracted tests pass)
4. ✅ Related links bidirectional
5. ⚠️ Staleness warnings (>90 days since update)

**Enforcement:**
- ❌ Block merge if validation fails
- ⚠️ Warning if staleness detected (doesn't block)

---

## Migration Guide

### For Existing Documents

**Step 1: Add Missing Frontmatter Fields**

```bash
# Find docs without type field
grep -L "^type:" docs/**/*.md

# Add minimal frontmatter
---
type: {determine based on content}
status: current
last_updated: YYYY-MM-DD
---
```

**Step 2: Categorize by Diátaxis Type**

Ask: "What is the user's intent when reading this?"
- Learning → tutorial
- Solving a problem → how-to
- Looking up specification → reference
- Understanding why → explanation
- Project status → project

**Step 3: Move to New Location** (optional, via symlink)

```bash
# Example: Move TROUBLESHOOTING.md
mv docs/TROUBLESHOOTING.md docs/how-to/troubleshooting.md
ln -s how-to/troubleshooting.md docs/TROUBLESHOOTING.md
```

**Step 4: Update Cross-References**

Update `related:` field in frontmatter:
```yaml
related:
  - ../tutorials/getting-started.md
  - ../../reference/api/event-schema.md
```

### For New Documents

**Step 1: Choose Document Type**

Use decision tree:
1. Is this teaching someone? → Tutorial
2. Is this solving a specific problem? → How-To
3. Is this a specification? → Reference
4. Is this explaining a concept? → Explanation
5. Is this project status? → Project

**Step 2: Use Template**

Copy appropriate template from this document.

**Step 3: Fill Frontmatter**

All required fields + relevant optional fields.

**Step 4: Follow Writing Standards**

- Code blocks with language tags
- Executable examples (if reference/tutorial)
- Cross-references to related docs

**Step 5: Review Checklist**

- [ ] Frontmatter complete and valid
- [ ] Code examples testable
- [ ] Cross-references bidirectional
- [ ] Follows template structure
- [ ] Passes `scripts/validate_docs.py`

---

## Maintenance

### Update Schedule

| Document Type | Update Frequency | Owner |
|---------------|-----------------|-------|
| DOCUMENTATION_STANDARD.md | Quarterly | Core team |
| Tutorials | As features change | Feature owners |
| How-To guides | As needed | Maintainers |
| Reference | With every API change | API owners |
| Explanation | Major changes only | Architects |
| Project | Daily (SPRINT_STATUS) | Project lead |

### Staleness Policy

**Definition:** Document not updated in >90 days

**Action:**
1. CI generates warning (doesn't block)
2. Assigned to original author for review
3. Options:
   - Update content → reset timer
   - Mark as `status: deprecated` → move to archived/
   - Confirm still accurate → add "reviewed: YYYY-MM-DD" to frontmatter

### Deprecation Process

**Step 1: Mark as Deprecated**
```yaml
status: deprecated
deprecated_date: YYYY-MM-DD
replacement: path/to/new-doc.md
```

**Step 2: Add Deprecation Notice**
```markdown
> ⚠️ **DEPRECATED:** This document is deprecated as of YYYY-MM-DD.
> Use [{New Doc}](path/to/new-doc.md) instead.
```

**Step 3: Move to Archived** (after 90 days)
```bash
mv docs/old-doc.md docs/archived/old-doc.md
```

---

## Quality Checklist

### Before Creating a New Doc

- [ ] Determine Diátaxis type (tutorial/how-to/reference/explanation)
- [ ] Use appropriate template
- [ ] Fill all required frontmatter fields
- [ ] Add cross-references to related docs

### Before Committing Doc Changes

- [ ] Run `scripts/validate_docs.py`
- [ ] Verify code examples are testable
- [ ] Check internal links work
- [ ] Update `last_updated` field
- [ ] Run extracted tests (if applicable)

### During PR Review

- [ ] Frontmatter schema valid
- [ ] Code examples follow standards
- [ ] Cross-references bidirectional
- [ ] Writing is clear and concise
- [ ] Examples are complete and copy-pasteable

---

## Related Documentation

- [BDD Workflow](bdd-workflow.md) - Feature → Test → Implementation
- [DDD Workflow](ddd-workflow.md) - Documentation → Design → Code
- [TDD Workflow](tdd-workflow.md) - Test → Code → Refactor
- [Development Lifecycle](development-lifecycle.md) - Overall process
- [Documentation Best Practices](documentation-best-practices-for-mcp-n8n.md) - Writing tips

---

## Appendix: Quick Reference

### Document Type Decision Tree

```
What's the user's goal?
│
├─ Learn a new skill/feature?
│  └─ Tutorial (step-by-step with expected output)
│
├─ Solve a specific problem?
│  └─ How-To Guide (problem → solution variations)
│
├─ Look up API/specification?
│  └─ Reference (spec with executable examples)
│
├─ Understand why/how system works?
│  └─ Explanation (concepts, architecture, decisions)
│
└─ Check project status?
   └─ Project (roadmaps, sprint status, releases)
```

### Frontmatter Quick Reference

```yaml
# REQUIRED (all docs)
---
title: "Document Title"
type: tutorial | how-to | reference | explanation | process | project
status: current | draft | deprecated
last_updated: YYYY-MM-DD
---

# OPTIONAL (add as needed)
audience: beginners | intermediate | advanced | maintainers
sprint: 2-5
category: integration | workflows | architecture | testing
tags: [tag1, tag2]
related: [../path/to/doc1.md, ../path/to/doc2.md]

# For tutorials/how-to
estimated_time: "30 minutes"
prerequisites: [tutorial1.md, "Tool installed"]

# For reference docs
version: 1.0.0
test_extraction: true
```

---

**Version:** 1.0.0
**Last Updated:** 2025-10-20
**Maintained By:** mcp-n8n core team
**Status:** Active

**Changes from previous versions:**
- v1.0.0 (2025-10-20): Initial release
