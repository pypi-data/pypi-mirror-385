---
title: "{API/Tool/Config Name} Reference"
type: reference
audience: all
version: X.Y.Z
test_extraction: true | false
category: {api | tools | configuration | schema}
source: "{source files}"
last_updated: YYYY-MM-DD
---

# {API/Tool/Config Name} Reference

## Overview

Brief description of what this reference covers (1-2 sentences).

**Status:** ✅ Stable | ⚠️ Beta | 🚧 Experimental
**Version:** X.Y.Z
**Last Updated:** YYYY-MM-DD

---

## Specification

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `param1` | string | Yes | – | Parameter description |
| `param2` | number | No | `0` | Parameter description |
| `param3` | boolean | No | `false` | Parameter description |

### Response Schema

```json
{
  "field1": "value_type",
  "field2": 123,
  "field3": {
    "nested": "object"
  }
}
```

### Field Definitions

**`field1`** (string)
- Description of field
- Valid values: `option1`, `option2`, `option3`
- Example: `"example-value"`

**`field2`** (number)
- Description of field
- Range: 0-100
- Example: `42`

**`field3`** (object)
- Description of nested object
- Fields: ...

---

## Examples

### Example 1: {Common Use Case}

Description of what this example demonstrates.

```python
# Executable example with full context
result = api_call(
    param1="value",
    param2=123
)

# Expected result
assert result["field1"] == "value"
```

**Output:**
```json
{
  "field1": "value",
  "field2": 123
}
```

### Example 2: {Edge Case or Variant}

Description of this variant.

```python
# Different usage pattern
result = api_call(
    param1="different",
    param3=True
)
```

**Output:**
```json
{
  "field1": "different",
  "field3": {"nested": "value"}
}
```

### Example 3: {Error Handling}

How to handle errors.

```python
try:
    result = api_call(invalid_param="bad")
except APIError as e:
    print(f"Error: {e}")
```

**Expected Error:**
```json
{
  "error": "Invalid parameter: invalid_param",
  "code": 400
}
```

---

## Test Cases

**Note:** These examples are extracted for automated testing

```python
# tests/integration/test_from_docs.py
def test_example_1():
    """Test from Reference docs: Example 1"""
    result = api_call(param1="value", param2=123)
    assert result["field1"] == "value"
    assert result["field2"] == 123

def test_example_2():
    """Test from Reference docs: Example 2"""
    result = api_call(param1="different", param3=True)
    assert "nested" in result["field3"]
```

---

## Error Scenarios

| Error | HTTP Code | Cause | Resolution |
|-------|-----------|-------|------------|
| Not Found | 404 | Invalid ID | Verify ID exists |
| Forbidden | 403 | No access | Request permissions |
| Bad Request | 400 | Invalid params | Check parameter types |
| Server Error | 500 | Internal error | Retry or contact support |

---

## Performance Notes

- **Typical Latency:** XX-YY ms
- **Rate Limits:** N requests per second
- **Max Payload:** X KB

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| X.Y.Z | YYYY-MM-DD | Current version - description |
| X.Y.0 | YYYY-MM-DD | Previous version - description |

---

## Related Documentation

- [How-To: Use This API](../how-to/...)
- [Tutorial: Get Started](../tutorials/...)
- [Explanation: Why This Design](../explanation/...)

---

**Source:** {List ground truth files}
**Test Extraction:** {Yes/No}
**Last Updated:** YYYY-MM-DD
