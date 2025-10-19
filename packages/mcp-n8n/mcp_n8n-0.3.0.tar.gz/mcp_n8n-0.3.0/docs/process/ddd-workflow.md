---
title: Documentation Driven Design (DDD) Workflow
category: process
version: 0.5.0
created: 2025-10-15
---

# Using This Template

> Replace placeholders like `{{INTEGRATION}}`, `{{integration}}`, and example tool names before sharing with your MCP server teams.

# Documentation Driven Design (DDD) Workflow

## Philosophy

**Documentation Driven Design** means writing the "contract" before the "code". API documentation serves as:
- **Specification**: Defines what the system should do
- **Design Tool**: Forces clarity about interfaces before implementation
- **Communication**: Stakeholders review docs before expensive development
- **Living Reference**: Docs stay synchronized because they're written first

## Core Principle

> "If you can't document it clearly, you can't build it correctly."

Writing documentation first reveals:
- Unclear requirements
- Missing edge cases
- API design flaws
- Naming inconsistencies

## DDD Process

### Change Request Intake (Diátaxis)

Kick off every change with a Diátaxis-formatted request so intent is captured before design:

- **Explanation** — context, problem statement, success metrics, stakeholders. This feeds Step 1 (Understand the Need).
- **How-to Guide** — user or agent workflow steps that convert into Given/When/Then scenarios during Step 2.
- **Reference** — proposed API/tool contract updates that become the source for Step 3 (Design the API).
- **Tutorial** *(optional but encouraged)* — outlines the end-to-end journey for onboarding or release notes once the change lands.

**Submission Checklist**
- Store drafts under `docs/change-requests/{issue-id}/` (or link the document in the ticket) before work begins.
- Reviewers confirm Explanation and Reference sections are complete before labeling a request “Ready for DDD”.
- Minor fixes may submit a condensed version (Explanation + Reference) but must still describe the behavior change clearly enough to drive BDD/TDD.

### Step 1: Understand the Need

**Input**: User story, feature request, or bug report

**Activity**: Define the "why" and "who"
- Why is this needed? (business value, user pain point)
- Who will use it? (AI agents, developers, both)
- What problem does it solve?

**Example**:
```markdown
**User Story**: As an AI agent, I want to create {{INTEGRATION}} tables programmatically
so that I can help users scaffold new project templates.

**User Need**: Currently must manually create tables via {{INTEGRATION}} UI.
Automating table creation enables templating workflows.

**Users**: Claude, ChatGPT, custom MCP clients
```

### Step 2: Define Acceptance Criteria

**Activity**: Write testable requirements in plain English

**Format**: Given-When-Then
```markdown
**Acceptance Criteria**:

1. **Given** a valid {{INTEGRATION}} document ID
   **When** I call `create_{{integration}}_table` with name and column definitions
   **Then** a new table is created with the specified schema

2. **Given** an invalid document ID
   **When** I call `create_{{integration}}_table`
   **Then** the tool returns a 404 error with clear message

3. **Given** insufficient permissions
   **When** I call `create_{{integration}}_table`
   **Then** the tool returns a 403 error explaining access requirements
```

### Step 3: Design the API

**Activity**: Write the tool signature and response shape

**Location**: `docs/reference/api/tools/{category}.md`

**Template**:
```markdown
## create_{{integration}}_table

**Canonical Name:** `create_{{integration}}_table`
**Category:** Tables
**Status:** ✅ Implemented (or ❌ Not yet implemented)

Create a new table in a {{INTEGRATION}} document with specified schema.

### Signature

```python
async def create_{{integration}}_table(
    doc_id: str,
    name: str,
    columns: List[Dict[str, str]],
    initial_rows: Optional[List[Dict[str, Any]]] = None
) -> dict:
```

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `doc_id` | string | Yes | – | ID of the document |
| `name` | string | Yes | – | Name of the table |
| `columns` | array[object] | Yes | – | Column definitions: `[{name, type, formula?}]` |
| `initial_rows` | array[object] | No | `None` | Optional initial row data |

**Column Definition Schema**:
```json
{
  "name": "Task",           // Column name
  "type": "text",           // text, number, select, date, person, checkbox
  "formula": "=Row1+Row2"   // Optional formula
}
```

### Returns

**Success**:
```json
{
  "success": true,
  "id": "table-abc123",
  "name": "Tasks",
  "browserLink": "https://{{integration}}.io/d/doc-abc123#table-abc123",
  "columns": [
    {"id": "col-1", "name": "Task", "type": "text"}
  ]
}
```

**Error**:
```json
{
  "success": false,
  "error": "Document not found: doc-invalid"
}
```

### Examples

**Create simple table**:
```python
result = await client.call_tool("create_{{integration}}_table", {
    "doc_id": "doc-abc123",
    "name": "Tasks",
    "columns": [
        {"name": "Task", "type": "text"},
        {"name": "Status", "type": "select"},
        {"name": "Due Date", "type": "date"}
    ]
})
```

**Create with initial data**:
```python
result = await client.call_tool("create_{{integration}}_table", {
    "doc_id": "doc-abc123",
    "name": "Team",
    "columns": [
        {"name": "Name", "type": "text"},
        {"name": "Role", "type": "select"}
    ],
    "initial_rows": [
        {"Name": "Alice", "Role": "Engineer"},
        {"Name": "Bob", "Role": "Designer"}
    ]
})
```

### Use Cases

1. **Project Template Creation**: Scaffold new docs with standard tables
2. **Data Migration**: Create tables to import external data
3. **Dynamic Schema**: Generate tables based on user requirements

### Error Scenarios

| Error | HTTP | Cause | Resolution |
|-------|------|-------|------------|
| Document not found | 404 | Invalid doc_id | Verify document exists, check access |
| Permission denied | 403 | No edit access | Request edit permissions from owner |
| Invalid column type | 400 | Unsupported type | Use valid types: text, number, select, date |
| Table name exists | 409 | Duplicate name | Choose unique table name |

### Performance

- **Typical Latency**: 500-1000ms (creates table in {{INTEGRATION}})
- **Rate Limit**: Subject to {{INTEGRATION}} API limits (10 req/sec)

### Related Tools

- [list_{{integration}}_tables](tables.md#list_{{integration}}_tables) - List existing tables
- [get_{{integration}}_table](tables.md#get_{{integration}}_table) - Get table schema
- [list_{{integration}}_columns](tables.md#list_{{integration}}_columns) - List columns
```

### Step 4: Document Examples & Edge Cases

**Activity**: Provide realistic usage examples and document edge cases

**Examples to Include**:
- **Happy path**: Most common use case
- **With optional parameters**: Show all parameters
- **Error handling**: How to handle common errors
- **Complex scenario**: Multi-step workflow

**Edge Cases to Document**:
- Empty inputs (empty list, empty string)
- Maximum values (max length, max items)
- Invalid inputs (wrong type, malformed data)
- Permission scenarios (read-only, no access)

### Step 5: Review & Validate

**Activity**: Get feedback BEFORE writing code

**Reviewers**:
- Product owner (validates business value)
- Engineers (validates technical feasibility)
- Technical writer (validates clarity)

**Review Checklist**:
- [ ] Signature matches tool-standards.md conventions
- [ ] All parameters documented with types and defaults
- [ ] Response shape includes `success: bool`
- [ ] Examples are realistic and copy-pastable
- [ ] Error scenarios comprehensively documented
- [ ] Related tools cross-referenced

**Approval**: Get explicit sign-off before proceeding to implementation

## DDD Anti-Patterns

### ❌ Writing Code First

**Problem**: Code written → Documentation as afterthought → Docs don't match reality

**Solution**: ALWAYS write docs first. If you start coding without docs, STOP.

### ❌ Vague Descriptions

**Problem**: "This tool manages tables" (not specific)

**Solution**: "Create a new table in a {{INTEGRATION}} document with specified column schema"

### ❌ Missing Edge Cases

**Problem**: Only documents happy path

**Solution**: Document error scenarios table with HTTP codes, causes, resolutions

### ❌ Inconsistent Naming

**Problem**: Mix of `create_table`, `make_{{integration}}_table`, `new_table`

**Solution**: Follow your agreed tool naming standards, for example `{verb}_{{integration}}_{noun}`

### ❌ No Examples

**Problem**: Just signature with parameter table

**Solution**: Provide 2-4 realistic examples showing different use cases

## DDD for Different Artifact Types

### New Tool

**Process**:
1. Create API reference section (15-30 min)
2. Document signature, parameters, returns (30-60 min)
3. Write 3-5 examples (30 min)
4. Document error scenarios (15 min)
5. Review with team (15-30 min)

**Total Time**: 2-3 hours

### API Change (Breaking)

**Process**:
1. Update API reference with NEW and OLD signatures (15 min)
2. Add migration section showing before/after (30 min)
3. Update any versioned migration guide (for example `migrate-to-v{X.Y}.md`) (30 min)
4. Document deprecation timeline (15 min)
5. Add to CHANGELOG.md as BREAKING CHANGE (10 min)

**Total Time**: 1.5-2 hours

### API Change (Non-Breaking)

**Process**:
1. Update API reference with new parameter/field (10 min)
2. Add example showing new capability (15 min)
3. Mark as "Added in v{X.Y}" (5 min)
4. Add to CHANGELOG.md (5 min)

**Total Time**: 30-45 min

### Bug Fix

**Process**:
1. Check if docs incorrectly documented behavior (10 min)
2. If YES: Update docs to reflect CORRECT behavior
3. If NO: Docs already correct, no doc change needed
4. Add note in CHANGELOG.md (5 min)

**Total Time**: 15-30 min

## DDD Templates

### Tool Implementation Template

Location: `templates/tool-implementation.md`

```markdown
# {Tool Name} Implementation Plan

## Overview
- **Tool**: `{canonical_name}`
- **Category**: {Documents/Tables/Rows/Pages/Automations/Permissions}
- **Purpose**: {One sentence description}

## Acceptance Criteria

**Given-When-Then**:
1. Given {precondition}
   When {action}
   Then {expected outcome}

2. Given {error condition}
   When {action}
   Then {error response}

## API Design

### Signature
```python
async def {tool_name}({params}) -> dict:
```

### Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|

### Response
```json
{
  "success": true,
  ...
}
```

## Examples

### Example 1: {Use case}
```python
result = await client.call_tool("{tool_name}", {...})
```

### Example 2: {Error case}
```python
result = await client.call_tool("{tool_name}", {...})
# Returns: {"success": false, "error": "..."}
```

## Implementation Checklist

- [ ] API reference documentation complete
- [ ] Acceptance criteria reviewed
- [ ] Examples validated
- [ ] Error scenarios documented
- [ ] Technical review approved
- [ ] Ready for BDD/TDD implementation
```

### Feature Specification Template

Location: `templates/feature-spec.md`

```markdown
# Feature: {Feature Name}

## User Story
As a {user type}
I want to {capability}
So that {benefit}

## Acceptance Criteria

**Scenario 1: {Happy path}**
- Given {precondition}
- When {action}
- Then {outcome}

**Scenario 2: {Edge case}**
- Given {precondition}
- When {action}
- Then {outcome}

## API Changes

### New Tools
- `{tool_name}`: {description}

### Modified Tools
- `{tool_name}`: Added parameter `{param_name}`

### Deprecated Tools
- `{old_tool_name}`: Use `{new_tool_name}` instead

## Migration Impact

**Breaking Changes**: Yes/No

If yes:
- Deprecation timeline: v{X.Y} deprecated, v{X+1.0} removed
- Migration guide: Ensure versioned `migrate-to-v{X.Y}.md` files stay current

## Documentation Deliverables

- [ ] API reference updated
- [ ] Examples added
- [ ] Migration guide (if breaking)
- [ ] CHANGELOG.md entry
- [ ] Release notes section

## Implementation Estimate

- Documentation: {hours}
- BDD scenarios: {hours}
- Implementation (TDD): {hours}
- Testing & review: {hours}
- **Total**: {days}
```

## DDD Metrics

**Track in PRs**:
- Documentation updated BEFORE code? (target: 100%)
- Docs reviewed and approved? (target: 100%)
- Examples tested and working? (target: 100%)

**Review in Retrospectives**:
- Did documentation-first catch design issues? (qualitative)
- How often did docs change during implementation? (lower is better)
- Did docs match final implementation? (target: 100%)

## Related Documentation

- [Development Lifecycle](development-lifecycle.md) - Overall workflow
- [BDD Workflow](bdd-workflow.md) - From docs to scenarios
- [TDD Workflow](tdd-workflow.md) - From scenarios to code
- Tool standards guide for this integration
- Contributing guide for this repository

---

**Version**: 0.5.0
**Last Updated**: 2025-10-15
**Maintainer**: MCP Server {{INTEGRATION}} Team
