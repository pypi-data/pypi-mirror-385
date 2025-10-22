---
title: Test Driven Development (TDD) Workflow
category: process
version: 0.5.0
created: 2025-10-15
---

# Using This Template

> Update placeholders such as `{{INTEGRATION}}`, `{{integration}}`, and tool names to match your MCP server before sharing with other teams.

# Test Driven Development (TDD) Workflow

## Philosophy

**Test Driven Development** means writing tests before implementation code. TDD is a design discipline that:
- **Forces clarity**: Can't write test without understanding requirements
- **Drives design**: Tests reveal interfaces before implementation details
- **Enables refactoring**: Green tests allow confident improvements
- **Provides documentation**: Tests show how to use the code

## Core Principle

> "Write the test you wish you had, then make it pass."

## The Red-Green-Refactor Cycle

```
   ┌──────────────┐
   │    START     │
   └──────┬───────┘
          ↓
   ┌──────────────┐
   │  1. RED      │ ← Write failing test
   │  (Test fails)│    Define expected behavior
   └──────┬───────┘
          ↓
   ┌──────────────┐
   │  2. GREEN    │ ← Write minimal code
   │  (Test passes│    Make test pass (simplest way)
   └──────┬───────┘
          ↓
   ┌──────────────┐
   │  3. REFACTOR │ ← Improve design
   │  (Tests still│    Clean up while keeping tests green
   │   pass)      │
   └──────┬───────┘
          │
          └──→ Repeat for next behavior
```

## TDD Process (Detailed)

### Step 1: RED - Write Failing Test

**Activity**: Write a test that defines the desired behavior

**Input**: Acceptance criteria from [DDD documentation](ddd-workflow.md) derived from the Diátaxis change request (Explanation + How-to + Reference)

**Example** (implementing `create_{{integration}}_table`):

**From API Docs** (acceptance criteria):
```markdown
Given a valid document ID
When I call create_{{integration}}_table with name and column definitions
Then a new table is created with the specified schema
```

**Contract Test** (RED):
```python
# tests/contracts/test_table_tools.py
import pytest
from {{integration}}_mcp import server

pytestmark = pytest.mark.asyncio

async def test_create_{{integration}}_table_signature():
    """
    Contract: create_{{integration}}_table accepts doc_id, name, columns.
    Returns success with table id and name.
    """
    result = await server.create_{{integration}}_table(
        doc_id="doc-test123",
        name="Tasks",
        columns=[
            {"name": "Task", "type": "text"},
            {"name": "Status", "type": "select"}
        ]
    )

    # Assert response shape
    assert result["success"] is True
    assert "id" in result
    assert result["name"] == "Tasks"
    assert "columns" in result
```

**Run test**:
```bash
pytest tests/contracts/test_table_tools.py::test_create_{{integration}}_table_signature -v
```

**Expected Output** (RED):
```
FAILED - AttributeError: module '{{integration}}_mcp.server' has no attribute 'create_{{integration}}_table'
```

✅ **Test fails** - This is GOOD! We've defined the desired behavior.

### Step 2: GREEN - Make Test Pass

**Activity**: Write the simplest code to make the test pass

**Implementation**:

```python
# src/{{integration}}_mcp/tools/tables.py
from typing import List, Dict, Any
from {{integration}}_mcp.{{integration}}_client import {{integration}}_request
from {{integration}}_mcp.logging import get_logger

log = get_logger("{{integration}}_mcp.tools.tables")

async def create_{{integration}}_table(
    doc_id: str,
    name: str,
    columns: List[Dict[str, Any]]
) -> dict:
    """
    Create a new table in a {{INTEGRATION}} document.

    Args:
        doc_id: ID of the document
        name: Name of the table
        columns: Column definitions: [{"name": str, "type": str}]

    Returns:
        Dictionary with success, id, name, columns
    """
    try:
        log.info(f"Creating table '{name}' in doc {doc_id}")

        # Call {{INTEGRATION}} API
        result = await {{integration}}_request(
            "POST",
            "docs", doc_id, "tables",
            json={
                "name": name,
                "columns": columns
            }
        )

        log.info(f"Table created: {result.get('id')}")

        # Return normalized response
        return {
            "success": True,
            "id": result["id"],
            "name": result["name"],
            "columns": result.get("columns", [])
        }

    except Exception as e:
        log.error(f"Failed to create table: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}"
        }
```

**Register in server**:
```python
# src/{{integration}}_mcp/server.py
from {{integration}}_mcp.tools import tables

@mcp.tool()
async def create_{{integration}}_table(
    doc_id: str,
    name: str,
    columns: list[dict]
) -> dict:
    """Create a new table in a {{INTEGRATION}} document."""
    return await tables.create_{{integration}}_table(doc_id, name, columns)
```

**Run test again**:
```bash
pytest tests/contracts/test_table_tools.py::test_create_{{integration}}_table_signature -v
```

**Expected Output** (GREEN):
```
PASSED tests/contracts/test_table_tools.py::test_create_{{integration}}_table_signature
```

✅ **Test passes** - Implementation satisfies contract!

### Step 3: REFACTOR - Improve Design

**Activity**: Clean up code while keeping tests green

**Improvements**:
1. Extract validation logic
2. Add type hints
3. Improve error messages
4. Add logging

**Refactored**:
```python
# src/{{integration}}_mcp/tools/tables.py
from typing import List, Dict, Any, Optional
from {{integration}}_mcp.{{integration}}_client import {{integration}}_request
from {{integration}}_mcp.logging import get_logger
from {{integration}}_mcp.validation import validate_doc_id, validate_column_schema

log = get_logger("{{integration}}_mcp.tools.tables")

async def create_{{integration}}_table(
    doc_id: str,
    name: str,
    columns: List[Dict[str, Any]],
    initial_rows: Optional[List[Dict[str, Any]]] = None
) -> dict:
    """
    Create a new table in a {{INTEGRATION}} document.

    Args:
        doc_id: ID of the document
        name: Name of the table
        columns: Column definitions: [{"name": str, "type": str, "formula": str?}]
        initial_rows: Optional initial row data

    Returns:
        Dictionary with success, id, name, browserLink, columns

    Raises:
        ValueError: If doc_id or column schema is invalid
    """
    # Validation
    validate_doc_id(doc_id)
    if not name or not name.strip():
        raise ValueError("Table name cannot be empty")
    validate_column_schema(columns)

    try:
        log.info(f"Creating table '{name}' in doc {doc_id} with {len(columns)} columns")

        # Build request payload
        payload = {"name": name.strip(), "columns": columns}
        if initial_rows:
            payload["initialRows"] = initial_rows

        # Call {{INTEGRATION}} API
        result = await {{integration}}_request(
            "POST",
            "docs", doc_id, "tables",
            json=payload
        )

        log.info(f"Table created: {result.get('id')} - {result.get('name')}")

        # Return normalized response
        return {
            "success": True,
            "id": result["id"],
            "name": result["name"],
            "browserLink": result.get("browserLink"),
            "columns": result.get("columns", [])
        }

    except ValueError as e:
        log.error(f"Validation error: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        log.error(f"Failed to create table: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}"
        }
```

**Run tests again** (ensure refactoring didn't break anything):
```bash
pytest tests/contracts/test_table_tools.py -v
```

**Expected**: All tests STILL PASS ✅

### Step 4: Repeat for Next Behavior

**Next test** (error handling):
```python
async def test_create_{{integration}}_table_handles_invalid_doc_id():
    """Error handling: Invalid document ID returns 404."""
    result = await server.create_{{integration}}_table(
        doc_id="invalid-!!!",
        name="Tasks",
        columns=[{"name": "Task", "type": "text"}]
    )

    assert result["success"] is False
    assert "error" in result
    assert "invalid" in result["error"].lower()
```

**Run** → RED → Implement validation → GREEN → Refactor → Repeat

## TDD Test Levels

### Unit Tests (Isolated, Fast)

**Purpose**: Test individual functions in isolation

**Characteristics**:
- Mock all external dependencies ({{INTEGRATION}} API, database)
- Fast (<10ms per test)
- Focus on edge cases and error handling

**Example**:
```python
# tests/unit/test_validation.py
import pytest
from {{integration}}_mcp.validation import validate_column_schema

def test_validate_column_schema_accepts_valid_columns():
    """Valid column schema passes validation."""
    columns = [
        {"name": "Task", "type": "text"},
        {"name": "Status", "type": "select"}
    ]

    # Should not raise
    validate_column_schema(columns)

def test_validate_column_schema_rejects_empty_list():
    """Empty column list raises ValueError."""
    with pytest.raises(ValueError, match="at least one column"):
        validate_column_schema([])

def test_validate_column_schema_rejects_invalid_type():
    """Invalid column type raises ValueError."""
    columns = [{"name": "Task", "type": "invalid_type"}]

    with pytest.raises(ValueError, match="Invalid column type"):
        validate_column_schema(columns)

def test_validate_column_schema_rejects_missing_name():
    """Column without name raises ValueError."""
    columns = [{"type": "text"}]

    with pytest.raises(ValueError, match="Column name required"):
        validate_column_schema(columns)
```

### Integration Tests (Real Dependencies)

**Purpose**: Test tool interactions with real {{INTEGRATION}} API

**Characteristics**:
- Use test {{INTEGRATION}} document (not production)
- Slower (100-1000ms per test)
- Test happy path and common errors

**Example**:
```python
# tests/integration/test_create_table.py
import pytest
import os
from {{integration}}_mcp import server

pytestmark = pytest.mark.asyncio

@pytest.fixture
def test_doc_id():
    """Test document ID from environment."""
    return os.getenv("CODA_TEST_DOC_ID")

async def test_create_{{integration}}_table_creates_real_table(test_doc_id):
    """Integration: Create actual table in {{INTEGRATION}} test document."""
    # Arrange
    table_name = f"Test Table {uuid.uuid4()}"  # Unique name
    columns = [
        {"name": "Task", "type": "text"},
        {"name": "Status", "type": "select"}
    ]

    # Act: Create table
    result = await server.create_{{integration}}_table(
        doc_id=test_doc_id,
        name=table_name,
        columns=columns
    )

    # Assert: Table created
    assert result["success"] is True
    assert "id" in result
    table_id = result["id"]

    # Verify: Check table exists in {{INTEGRATION}}
    tables = await server.list_{{integration}}_tables(test_doc_id)
    assert any(t["id"] == table_id for t in tables["tables"])

    # Cleanup: Delete test table (optional, or manual cleanup)
    # Note: {{INTEGRATION}} API doesn't support table deletion, so use manual cleanup
```

### Contract Tests (API Shape Validation)

**Purpose**: Ensure tool signatures and response shapes comply with standards

**Characteristics**:
- Fast (mocked or test doc)
- Validate parameter passing
- Validate response structure

**Example**:
```python
# tests/contracts/test_table_tools.py
async def test_create_{{integration}}_table_response_shape():
    """Contract: Response includes required fields."""
    result = await server.create_{{integration}}_table(
        doc_id="doc-test",
        name="Tasks",
        columns=[{"name": "Task", "type": "text"}]
    )

    # Validate response shape
    assert "success" in result
    assert isinstance(result["success"], bool)

    if result["success"]:
        assert "id" in result
        assert "name" in result
        assert "columns" in result
        assert isinstance(result["columns"], list)
    else:
        assert "error" in result
        assert isinstance(result["error"], str)
```

## TDD for Different Scenarios

### New Tool (from scratch)

**Process**:
1. **RED**: Write contract test (signature + response shape)
2. **GREEN**: Implement basic tool (no error handling)
3. **RED**: Write error handling tests (404, 403, validation)
4. **GREEN**: Add error handling
5. **REFACTOR**: Extract common patterns, improve logging
6. **RED**: Write integration test (real API call)
7. **GREEN**: Ensure integration works
8. **REFACTOR**: Final cleanup

**Time**: 4-8 hours

### Bug Fix (regression test)

**Process**:
1. **RED**: Write regression test reproducing the bug
2. **GREEN**: Fix the bug (minimal change)
3. **REFACTOR**: Improve fix if needed
4. **Document**: Add comment explaining the bug

**Time**: 1-4 hours

**Example**:
```python
# tests/regression/test_issue_42.py
async def test_issue_42_formula_injection_vulnerability():
    """
    Regression test for #42: Formula injection via row data.

    Bug: User could inject {{INTEGRATION}} formulas by providing "=SUM(...)"
    Fix: Escape dangerous characters before sending to API
    """
    # RED: This test fails before fix
    malicious_input = "=SUM(A1:A10)"

    result = await server.create_{{integration}}_row(
        doc_id="doc-test",
        table_id="table-test",
        row_data={"Task": malicious_input}
    )

    # GREEN: After fix, input is escaped
    assert result["success"] is True
    assert result["values"]["Task"] == "\\=SUM(A1:A10)"  # Escaped
    # Not: "=SUM(A1:A10)" which would execute as formula
```

### Refactoring (no behavior change)

**Process**:
1. **Ensure GREEN**: All tests pass before refactoring
2. **REFACTOR**: Improve code (extract functions, rename, etc.)
3. **Ensure STILL GREEN**: Tests still pass after refactoring

**Time**: 1-2 hours

**Example**:
```python
# Before refactoring: All tests GREEN ✅

# Refactor: Extract duplicate error handling
def _handle_api_error(error: Exception) -> dict:
    """Centralized error response formatting."""
    log.error(f"API error: {error}", exc_info=True)
    return {
        "success": False,
        "error": f"{type(error).__name__}: {str(error)}"
    }

# After refactoring: All tests STILL GREEN ✅
```

## TDD Best Practices

### ✅ DO: Write the Simplest Test First

**Good** (simple):
```python
def test_create_table_returns_success():
    result = await server.create_{{integration}}_table(...)
    assert result["success"] is True
```

**Bad** (too complex):
```python
def test_create_table_complete_workflow():
    # Creates table, adds rows, updates columns, deletes rows...
    # Too much in one test!
```

### ✅ DO: One Assert Per Test (Usually)

**Good** (focused):
```python
def test_create_table_returns_id():
    result = await server.create_{{integration}}_table(...)
    assert "id" in result

def test_create_table_returns_name():
    result = await server.create_{{integration}}_table(...)
    assert result["name"] == "Tasks"
```

**Acceptable** (related assertions):
```python
def test_create_table_response_shape():
    result = await server.create_{{integration}}_table(...)
    assert result["success"] is True
    assert "id" in result
    assert "name" in result
    # All assertions validate same concept: response shape
```

### ✅ DO: Test Behavior, Not Implementation

**Good** (behavior):
```python
def test_create_table_validates_empty_name():
    result = await server.create_{{integration}}_table(
        doc_id="doc-123",
        name="",  # Empty name
        columns=[...]
    )
    assert result["success"] is False
    assert "empty" in result["error"].lower()
```

**Bad** (implementation):
```python
def test_create_table_calls_validate_function():
    # Testing that specific internal function is called
    # This is testing HOW, not WHAT
    with mock.patch("{{integration}}_mcp.validation.validate_name") as mock_validate:
        await server.create_{{integration}}_table(...)
        mock_validate.assert_called_once()
```

### ✅ DO: Use Descriptive Test Names

**Good**:
```python
def test_create_{{integration}}_table_with_initial_rows_creates_rows():
    ...

def test_create_{{integration}}_table_with_invalid_doc_id_returns_404():
    ...
```

**Bad**:
```python
def test_create_table():
    ...

def test_error():
    ...
```

## TDD Anti-Patterns

### ❌ Writing Tests After Code

**Problem**: Tests become validation of implementation, not specification of behavior

**Solution**: Always write test FIRST (even if just the signature)

### ❌ Testing Everything Through Mocks

**Problem**: Tests pass but real code doesn't work

**Solution**: Mix unit tests (mocked) with integration tests (real API)

### ❌ Green Bar Fallacy

**Problem**: All tests pass, but there's a bug

**Solution**: Ensure test FAILS before making it pass (verify test works)

### ❌ Fragile Tests

**Problem**: Tests break when implementation changes (but behavior doesn't)

**Solution**: Test public interfaces, not private details

### ❌ Slow Test Suite

**Problem**: Tests take too long, developers skip them

**Solution**: Keep unit tests fast (<1s total), use CI for slow integration tests

## TDD Metrics

**Track**:
- Test coverage: ≥85% overall (≥90% unit, ≥80% integration)
- Test execution time: <5 minutes for full suite
- Test-first commits: % of commits with test + implementation (target: ≥80%)

**Review**:
- Did TDD catch bugs before production? (count regressions)
- How often do tests need updating vs. implementation? (should be lower)
- Are tests readable as documentation? (qualitative)

## Related Documentation

- [Development Lifecycle](development-lifecycle.md) - Overall workflow
- [DDD Workflow](ddd-workflow.md) - Documentation-first principles
- [BDD Workflow](bdd-workflow.md) - Gherkin scenarios
- Testing philosophy - Strategy for balancing test coverage and speed
- Tool standards - API contract specifications

---

**Version**: 0.5.0
**Last Updated**: 2025-10-15
**Maintainer**: MCP Server {{INTEGRATION}} Team
