# E2E Test Suite: Backend Routing

**Version:** v1.0.0
**Duration:** 10-15 minutes
**Purpose:** Validate namespace-based routing to multiple backends
**Prerequisites:** Complete [E2E_SMOKE_TEST.md](E2E_SMOKE_TEST.md) first
**Last Updated:** October 21, 2025

---

## Overview

This suite validates **backend routing** - ensuring the gateway correctly routes tool calls to the appropriate backend based on namespace prefixes.

### What You'll Test

**Backends (2):**
- **chora-composer** - Artifact generation (namespace: `chora`)
- **coda-mcp** - Data operations (namespace: `coda`, optional)

**Tools Tested:**
- `chora:list_generators` - List available content generators
- `chora:generate_content` - Generate content from templates
- `coda:list_docs` - List Coda documents (if configured)

**Key Concepts:**
- Namespace isolation
- Tool name resolution
- Parameter passing across boundaries
- Error propagation

---

## Test 1: Chora Composer Routing

### Step 1.1: List Available Generators

**Prompt:**
```
Use the chora:list_generators tool to see what content generators are available.
List the first 5 generators.
```

**Success Criteria:**
- [ ] Tool call routes to chora-composer backend
- [ ] Returns list of generators
- [ ] Each generator has: id, name, description
- [ ] Response time < 2000ms
- [ ] No routing errors

**Expected Output (sample):**
```json
{
  "generators": [
    {
      "id": "simple-readme",
      "name": "Simple README",
      "description": "Basic README.md template"
    },
    {
      "id": "api-docs",
      "name": "API Documentation",
      "description": "Generate API reference docs"
    }
  ],
  "count": 17
}
```

###

 Step 1.2: Generate Content with Template

**Prompt:**
```
Use chora:generate_content to generate a simple README using the "simple-readme" generator.
Show me the generated content.
```

**Success Criteria:**
- [ ] Tool call succeeds
- [ ] Returns generated markdown content
- [ ] Content is non-empty
- [ ] Response time < 5000ms (AI generation)
- [ ] Trace ID is included in response

**Expected Output Structure:**
```json
{
  "content": "# Project Name\n\n## Overview\n...",
  "metadata": {
    "generator_id": "simple-readme",
    "generated_at": "2025-10-21T14:35:00Z",
    "trace_id": "xyz789..."
  }
}
```

---

## Test 2: Namespace Isolation

### Step 2.1: Verify Tool Name Resolution

**Prompt:**
```
What happens if I try to call "list_generators" without the "chora:" prefix?
Is there a tool by that name?
```

**Success Criteria:**
- [ ] Tool not found (no namespace)
- [ ] Gateway does NOT auto-resolve namespace
- [ ] Error message suggests using namespaced version
- [ ] No partial matches accepted

**Expected Behavior:**
- Tool call fails with "Tool not found" error
- Suggestion: "Did you mean chora:list_generators?"

### Step 2.2: Cross-Namespace Collision Prevention

**Prompt:**
```
Are there any tools with the same name in different namespaces?
For example, is there both chora:status and coda:status?
```

**Success Criteria:**
- [ ] Each tool is uniquely identified by namespace:name
- [ ] No collisions between backends
- [ ] Gateway maintains strict namespace separation

---

## Test 3: Parameter Passing

### Step 3.1: Simple Parameters

**Prompt:**
```
Use chora:generate_content with these parameters:
- config_id: "simple-readme"
- context: {"project_name": "Test Project"}

Verify the project name appears in the output.
```

**Success Criteria:**
- [ ] Parameters passed correctly to backend
- [ ] Context data used in generation
- [ ] "Test Project" appears in output
- [ ] No parameter mangling

### Step 3.2: Complex Parameters

**Prompt:**
```
Use chora:generate_content with nested context:
{
  "project_name": "Complex Test",
  "metadata": {
    "author": "Test User",
    "version": "1.0.0"
  }
}

Are all nested fields preserved?
```

**Success Criteria:**
- [ ] Nested objects preserved
- [ ] All fields accessible to backend
- [ ] No data loss in transit
- [ ] JSON structure maintained

---

## Test 4: Error Propagation

### Step 4.1: Backend Error Handling

**Prompt:**
```
Try to use chora:generate_content with an invalid config_id like "nonexistent-template".
What error do you get?
```

**Success Criteria:**
- [ ] Error propagated from backend
- [ ] Error message is informative
- [ ] error.code indicates type (e.g., "template_not_found")
- [ ] Trace ID included for debugging
- [ ] No gateway-level error wrapping confusion

**Expected Error Structure:**
```json
{
  "error": {
    "code": "template_not_found",
    "message": "Template 'nonexistent-template' not found",
    "trace_id": "abc123..."
  }
}
```

### Step 4.2: Parameter Validation

**Prompt:**
```
Call chora:generate_content without required parameters (omit config_id).
What validation error do you receive?
```

**Success Criteria:**
- [ ] Parameter validation occurs
- [ ] Clear error about missing parameter
- [ ] No backend call attempted
- [ ] Fast failure (< 100ms)

---

## Test 5: Coda MCP Routing (Optional)

**Note:** These tests only run if Coda MCP backend is configured with CODA_API_KEY.

### Step 5.1: List Coda Documents

**Prompt:**
```
Use coda:list_docs to list your Coda documents.
How many documents do you have access to?
```

**Success Criteria:**
- [ ] Routes to coda-mcp backend
- [ ] Returns list of documents
- [ ] Each doc has: id, name, href
- [ ] No cross-contamination with chora namespace

**Expected Output:**
```json
{
  "documents": [
    {
      "id": "doc_abc123",
      "name": "My Document",
      "href": "https://coda.io/d/doc_abc123"
    }
  ]
}
```

### Step 5.2: Dual-Backend Operation

**Prompt:**
```
In sequence:
1. Call chora:list_generators
2. Call coda:list_docs
3. Call gateway_status

Verify all three backends/tools work correctly.
```

**Success Criteria:**
- [ ] All three calls succeed
- [ ] No interference between backends
- [ ] Each maintains independent state
- [ ] Gateway tracks all calls in events

---

## Test 6: Concurrent Routing

### Step 6.1: Parallel Tool Calls

**Prompt:**
```
If possible, make these calls concurrently:
- chora:list_generators
- gateway_status

Do both complete successfully?
```

**Success Criteria:**
- [ ] Both calls succeed
- [ ] No resource contention
- [ ] Total time < sequential time
- [ ] Each has unique trace_id

---

## Test 7: Backend Failure Scenarios

### Step 7.1: Backend Timeout

**Prompt:**
```
What happens if a backend takes too long to respond?
(Note: May require artificially slow operation or check documentation)
```

**Success Criteria:**
- [ ] Timeout is enforced (default 30s)
- [ ] Clear timeout error message
- [ ] Gateway remains responsive
- [ ] Other backends unaffected

### Step 7.2: Backend Unavailable

**Prompt:**
```
Check gateway_status. If a backend is stopped or unavailable, what is its status?
Can the gateway still function with remaining backends?
```

**Success Criteria:**
- [ ] Backend status = "stopped" or "error"
- [ ] Gateway reports backend unavailability
- [ ] Other backends continue working
- [ ] Tool calls to unavailable backend fail gracefully

---

**Test Suite:** Backend Routing
**Duration:** 10-15 minutes
**Tools Tested:** 3-5 (chora + optional coda)
**Status:** ✅ Core routing validated

---

## Next Steps

After completing this routing test:

1. ✅ **All tests pass:** Proceed to [E2E_EVENT_MONITORING.md](E2E_EVENT_MONITORING.md)
2. ⚠️ **Routing failures:** Check backend logs and namespace configuration
3. 📝 **Document:** Note routing latencies and any unexpected behavior

## Troubleshooting

**Tool not found errors:**
- Verify backend is running (`gateway_status`)
- Check namespace prefix is correct
- Ensure backend registered with gateway

**Parameter errors:**
- Check JSON structure is valid
- Verify required parameters are provided
- Review backend-specific parameter requirements

**Slow responses:**
- AI generation can take 3-5 seconds
- Check ANTHROPIC_API_KEY is valid
- Monitor backend process logs
