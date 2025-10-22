---
title: Behavior Driven Development (BDD) Workflow
category: process
version: 0.5.0
created: 2025-10-15
---

# Using This Template

> Replace placeholders like `{{INTEGRATION}}`, `{{integration}}`, and any example tool names with values that match your MCP server integration.

# Behavior Driven Development (BDD) Workflow

## Philosophy

**Behavior Driven Development** uses natural language scenarios to specify expected behavior. BDD bridges the gap between:
- Product requirements (what we want)
- Technical implementation (how we build it)
- Test validation (proof it works)

## Core Principle

> "Scenarios written in Gherkin are executable specifications."

BDD scenarios:
- **Readable by non-developers**: Product owners can review
- **Executable as tests**: Automated via pytest-bdd
- **Living documentation**: Always up-to-date because they must pass

## Gherkin Syntax

### Structure

```gherkin
Feature: High-level capability
  {Description of the feature and its value}

  Background:
    Given {common preconditions for all scenarios}

  Scenario: Specific behavior
    Given {precondition}
    And {another precondition}
    When {action}
    Then {expected outcome}
    And {another expected outcome}

  Scenario Outline: Parameterized scenario
    When I do <action>
    Then I see <result>

    Examples:
      | action  | result  |
      | create  | success |
      | update  | success |
```

### Keywords

- **Feature**: Top-level grouping (one per file)
- **Background**: Setup steps run before each scenario
- **Scenario**: Single test case
- **Scenario Outline**: Template for multiple test cases
- **Given**: Preconditions (arrange)
- **When**: Actions (act)
- **Then**: Assertions (assert)
- **And/But**: Additional steps of same type

## BDD Process

### Step 1: Write Feature File

**Location**: `tests/features/{feature_name}.feature`

**From Documentation**: Convert acceptance criteria from API docs to Gherkin. Start with the How-to section of the Diátaxis change request and refine each step into a concrete scenario.

**Example** (from a permissions tool specification):

**API Doc Acceptance Criteria**:
```markdown
1. Given a valid document ID
   When I call `grant_{{integration}}_permission` with email and access level
   Then the user is granted access

2. Given an invalid document ID
   When I call `grant_{{integration}}_permission`
   Then the tool returns a 404 error
```

**Gherkin Feature**:
```gherkin
# tests/features/permissions.feature
Feature: {{INTEGRATION}} Permission Management

  As an AI agent
  I want to manage document permissions
  So that I can help users share {{INTEGRATION}} documents

  Background:
    Given the MCP server is running
    And I have a valid {{INTEGRATION}} API token

  Scenario: Grant write permission to user by email
    Given a {{INTEGRATION}} document "doc-abc123"
    When I call tool "grant_{{integration}}_permission" with:
      | doc_id   | doc-abc123           |
      | access   | write                |
      | principal| {"type": "email", "email": "alice@example.com"} |
    Then the tool returns success
    And the response includes "id" field
    And the response includes "access" = "write"
    And the permission is created in {{INTEGRATION}}

  Scenario: Handle document not found error
    When I call tool "grant_{{integration}}_permission" with:
      | doc_id   | doc-invalid          |
      | access   | write                |
      | principal| {"type": "email", "email": "alice@example.com"} |
    Then the tool returns error
    And the error message contains "not found"
    And the error HTTP code is 404

  Scenario Outline: Support all access levels
    Given a {{INTEGRATION}} document "doc-abc123"
    When I grant "<access_level>" permission to "bob@example.com"
    Then the permission is granted
    And the user has "<access_level>" access

    Examples:
      | access_level |
      | readonly     |
      | comment      |
      | write        |
```

### Step 2: Implement Step Definitions

**Location**: `tests/step_defs/{domain}_steps.py`

**Purpose**: Map Gherkin steps to Python code

**Example**:

```python
# tests/step_defs/tool_steps.py
import pytest
from pytest_bdd import given, when, then, parsers
from {{integration}}_mcp import server

# --- GIVEN steps (arrange) ---

@given("the MCP server is running", target_fixture="mcp_server")
def mcp_server():
    """Fixture that returns configured server instance."""
    return server

@given(parsers.parse('a {{INTEGRATION}} document "{doc_id}"'), target_fixture="doc_id")
def {{integration}}_document(doc_id):
    """Store document ID for use in When steps."""
    return doc_id

# --- WHEN steps (act) ---

@when(parsers.parse('I call tool "{tool_name}" with:'))
async def call_tool_with_params(tool_name, datatable, mcp_server):
    """
    Call MCP tool with parameters from Gherkin table.

    Stores result in pytest context for Then assertions.
    """
    # Convert Gherkin table to dict
    params = {row['key']: _parse_value(row['value']) for row in datatable}

    # Call the tool
    tool_fn = getattr(mcp_server, tool_name)
    result = await tool_fn(**params)

    # Store for assertions
    pytest.last_result = result

@when(parsers.parse('I grant "{access}" permission to "{email}"'))
async def grant_permission(access, email, doc_id, mcp_server):
    """Shorthand for grant_{{integration}}_permission."""
    result = await mcp_server.grant_{{integration}}_permission(
        doc_id=doc_id,
        access=access,
        principal={"type": "email", "email": email}
    )
    pytest.last_result = result

# --- THEN steps (assert) ---

@then("the tool returns success")
def tool_returns_success():
    """Assert the tool call succeeded."""
    assert pytest.last_result.get("success") is True

@then("the tool returns error")
def tool_returns_error():
    """Assert the tool call failed."""
    assert pytest.last_result.get("success") is False

@then(parsers.parse('the response includes "{field}" field'))
def response_includes_field(field):
    """Assert response contains field."""
    assert field in pytest.last_result

@then(parsers.parse('the response includes "{field}" = "{value}"'))
def response_field_equals(field, value):
    """Assert response field has specific value."""
    actual = pytest.last_result.get(field)
    expected = _parse_value(value)
    assert actual == expected

@then(parsers.parse('the error message contains "{text}"'))
def error_contains_text(text):
    """Assert error message includes substring."""
    error_msg = pytest.last_result.get("error", "")
    assert text in error_msg

# --- Helper functions ---

def _parse_value(value_str):
    """Parse string to appropriate type (JSON, bool, int, float, str)."""
    import json

    # Try JSON first (handles dicts, lists, null)
    try:
        return json.loads(value_str)
    except json.JSONDecodeError:
        pass

    # Try bool
    if value_str.lower() in ("true", "false"):
        return value_str.lower() == "true"

    # Try int
    try:
        return int(value_str)
    except ValueError:
        pass

    # Try float
    try:
        return float(value_str)
    except ValueError:
        pass

    # Default to string
    return value_str
```

### Step 3: Run BDD Tests (RED)

**Command**:
```bash
pytest tests/features/ --gherkin-terminal-reporter -v
```

**Expected**: Tests FAIL (tool not implemented yet)

**Output**:
```
tests/features/permissions.feature::Grant write permission to user
  FAILED - NotImplementedError: grant_{{integration}}_permission not found
```

### Step 4: Implement Tool (TDD)

See [TDD Workflow](tdd-workflow.md) for implementation cycle.

**Goal**: Make BDD scenarios pass through red-green-refactor

### Step 5: Run BDD Tests (GREEN)

**Command**:
```bash
pytest tests/features/ --gherkin-terminal-reporter -v
```

**Expected**: All scenarios PASS

**Output**:
```
tests/features/permissions.feature::Grant write permission to user
  Feature: {{INTEGRATION}} Permission Management
    Scenario: Grant write permission to user by email
      Given a {{INTEGRATION}} document "doc-abc123" PASSED
      When I call tool "grant_{{integration}}_permission" with: PASSED
      Then the tool returns success PASSED
      And the response includes "id" field PASSED
      And the response includes "access" = "write" PASSED
      And the permission is created in {{INTEGRATION}} PASSED

================ 3 passed in 2.34s ================
```

## BDD Test Organization

### Feature Files Structure

```
tests/
└── features/
    ├── tool_contracts.feature      # All 31 canonical tools
    ├── document_lifecycle.feature  # Create → Update → Delete
    ├── table_operations.feature    # Tables and columns
    ├── row_crud.feature            # Row CRUD operations
    ├── row_upsert.feature          # Upsert and incremental sync
    ├── page_content.feature        # Page operations
    ├── automations.feature         # Buttons and triggers
    ├── permissions.feature         # Sharing and access control
    └── error_handling.feature      # Error scenarios (404, 403, 429)
```

### Step Definitions Structure

```
tests/
└── step_defs/
    ├── __init__.py
    ├── tool_steps.py        # Generic tool call steps
    ├── assertion_steps.py   # Response validation steps
    ├── data_steps.py        # Test data setup/teardown
    ├── error_steps.py       # Error handling steps
    └── conftest.py          # pytest-bdd configuration
```

## BDD Scenarios by Type

### Contract Test (Tool Signature)

**Purpose**: Verify tool accepts correct parameters and returns expected shape

```gherkin
Feature: Tool Contracts

  Scenario: list_{{integration}}_docs accepts all filter parameters
    When I call tool "list_{{integration}}_docs" with:
      | is_owner     | true          |
      | is_published | false         |
      | query        | "roadmap"     |
      | limit        | 50            |
    Then the tool returns success
    And the response includes "docs" field (not "items")
    And the response includes "next_page_token" field
```

### Integration Test (Multi-Step Workflow)

**Purpose**: Verify tools work together in realistic workflows

```gherkin
Feature: Document Lifecycle

  Scenario: Create document, add table, insert rows, then delete
    # Step 1: Create document
    When I create a document named "Project Tracker"
    Then I receive a document ID

    # Step 2: Create table in document
    When I create a table named "Tasks" with columns:
      | name   | type   |
      | Task   | text   |
      | Status | select |
    Then I receive a table ID

    # Step 3: Insert rows
    When I insert a row with Task="Setup" and Status="Done"
    Then the row is created

    # Step 4: Cleanup
    When I delete the document
    Then the document is removed
```

### Error Scenario Test

**Purpose**: Verify error handling for common failure modes

```gherkin
Feature: Error Handling

  Scenario Outline: Handle HTTP error codes gracefully
    When I call "<tool>" with invalid <param_type>
    Then the tool returns error
    And the error HTTP code is <code>
    And the error message is helpful

    Examples:
      | tool                | param_type | code |
      | get_{{integration}}_doc        | doc_id     | 404  |
      | grant_{{integration}}_permission | doc_id   | 403  |
      | list_{{integration}}_rows      | table_id   | 404  |
```

### Performance Test

**Purpose**: Verify tools meet performance SLAs

```gherkin
Feature: Performance

  Scenario: list_{{integration}}_tables completes quickly
    Given a document with 50 tables
    When I call "list_{{integration}}_tables" with limit=100
    Then the response is received within 2 seconds
    And all tables are returned
```

## pytest-bdd Configuration

### pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = [
    "-v",
    "--tb=short",
    "--gherkin-terminal-reporter",
    "--gherkin-terminal-reporter-expanded"
]
bdd_features_base_dir = "tests/features/"
```

### conftest.py

```python
# tests/step_defs/conftest.py
import pytest
from pytest_bdd import given, when, then

# Make step definitions discoverable
pytest_plugins = [
    "tests.step_defs.tool_steps",
    "tests.step_defs.assertion_steps",
    "tests.step_defs.data_steps",
    "tests.step_defs.error_steps"
]

# Shared fixtures
@pytest.fixture(scope="session")
def mcp_server():
    """MCP server instance for all BDD tests."""
    from {{integration}}_mcp import server
    return server

@pytest.fixture(scope="function")
def test_context():
    """Context dict to share data between steps."""
    return {}
```

## BDD Best Practices

### ✅ DO: Write Declarative Scenarios

**Good** (What, not how):
```gherkin
When I create a document named "Roadmap"
Then the document is created
```

**Bad** (Imperative, too detailed):
```gherkin
When I call the {{INTEGRATION}} API POST /docs endpoint
And I set the body to {"name": "Roadmap"}
And I send the request
Then the HTTP status is 200
```

### ✅ DO: Use Background for Common Setup

**Good**:
```gherkin
Background:
  Given the MCP server is running
  And I have a valid API token

Scenario: Create document
  When I create a document...

Scenario: Update document
  When I update a document...
```

**Bad** (repeating same Given in every scenario):
```gherkin
Scenario: Create document
  Given the MCP server is running
  And I have a valid API token
  When I create a document...
```

### ✅ DO: One Scenario per Behavior

**Good** (focused):
```gherkin
Scenario: Create table with initial rows
  When I create a table with 3 initial rows
  Then the table has 3 rows

Scenario: Create table without initial rows
  When I create a table without initial rows
  Then the table has 0 rows
```

**Bad** (testing multiple behaviors):
```gherkin
Scenario: Table creation
  When I create a table with 3 rows
  Then the table has 3 rows
  When I create another table without rows
  Then the second table has 0 rows
```

### ✅ DO: Use Scenario Outline for Variations

**Good** (parameterized):
```gherkin
Scenario Outline: Support all access levels
  When I grant "<access>" permission
  Then the user has "<access>" access

  Examples:
    | access   |
    | readonly |
    | comment  |
    | write    |
```

**Bad** (copy-paste scenarios):
```gherkin
Scenario: Grant readonly permission...
Scenario: Grant comment permission...
Scenario: Grant write permission...
```

## BDD Anti-Patterns

### ❌ Tightly Coupled to Implementation

**Problem**:
```gherkin
When I call the `{{integration}}_request()` function with method "POST"
```

**Solution**: Focus on behavior, not implementation:
```gherkin
When I create a new document
```

### ❌ Testing the Test

**Problem**:
```gherkin
When I mock the {{INTEGRATION}} API to return 404
Then the tool raises an exception
```

**Solution**: Test real behavior:
```gherkin
When I call get_{{integration}}_doc with invalid document ID
Then the tool returns a 404 error
```

### ❌ Overly Generic Steps

**Problem**:
```gherkin
Given I have data
When I do the thing
Then I see a result
```

**Solution**: Be specific:
```gherkin
Given a {{INTEGRATION}} document "doc-abc123"
When I create a table named "Tasks"
Then the table is created with ID "table-xyz"
```

## BDD Metrics

**Track in CI**:
- Scenario pass rate: 100% (block merge if failing)
- Scenario count: Track growth over time
- Step reuse: % of steps from shared library (target: ≥70%)

**Review in Retrospectives**:
- Are scenarios readable by product team? (qualitative)
- Did scenarios catch bugs before production? (count incidents)
- How often do scenarios change vs. implementation? (should be stable)

## Related Documentation

- [Development Lifecycle](development-lifecycle.md) - Overall workflow
- [DDD Workflow](ddd-workflow.md) - Documentation-first principles
- [TDD Workflow](tdd-workflow.md) - Red-green-refactor implementation
- Testing philosophy reference for your integration
- [pytest-bdd Documentation](https://pytest-bdd.readthedocs.io/) - External reference

---

**Version**: 0.5.0
**Last Updated**: 2025-10-15
**Maintainer**: MCP Server {{INTEGRATION}} Team
