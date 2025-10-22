# E2E Test Suite: Error Handling & Resilience

**Version:** v1.0.0
**Duration:** 10-15 minutes
**Purpose:** Validate error handling, recovery, and graceful degradation
**Prerequisites:** Complete [E2E_WORKFLOW_ORCHESTRATION.md](E2E_WORKFLOW_ORCHESTRATION.md) first
**Last Updated:** October 21, 2025

---

## Overview

This suite validates **error handling and resilience** - ensuring the gateway handles failures gracefully and provides useful error messages.

### What You'll Test

**Error Scenarios:**
- Backend unavailability
- Tool call timeouts
- Invalid parameters
- Malformed events
- Config validation errors
- Partial system failures

**Key Goals:**
- Graceful degradation
- Clear error messages
- System stability
- Recovery mechanisms

---

## Test 1: Backend Failures

### Step 1.1: Backend Unavailable

**Prompt:**
```
If the chora-composer backend is stopped or crashes:
1. Check gateway_status - what is the backend status?
2. Try to call chora:list_generators
3. Does the gateway remain responsive?
```

**Success Criteria:**
- [ ] Backend status = "stopped" or "error"
- [ ] Tool call fails with clear error
- [ ] Gateway continues operating
- [ ] Other backends unaffected
- [ ] Error message suggests checking backend logs

**Expected Error:**
```json
{
  "error": {
    "code": "backend_unavailable",
    "message": "Backend 'chora-composer' is not running",
    "backend": "chora-composer",
    "suggestion": "Check backend logs or restart the backend"
  }
}
```

### Step 1.2: Backend Timeout

**Prompt:**
```
If a backend call takes longer than the timeout (default 30s):
What error do you receive?
```

**Success Criteria:**
- [ ] Timeout enforced
- [ ] error.code = "timeout"
- [ ] Includes duration attempted
- [ ] Gateway remains responsive
- [ ] Trace ID for debugging

---

## Test 2: Invalid Parameters

### Step 2.1: Missing Required Parameter

**Prompt:**
```
Call chora:generate_content without the required 'config_id' parameter.
What validation error do you get?
```

**Success Criteria:**
- [ ] Parameter validation at gateway level
- [ ] Clear error about missing parameter
- [ ] No backend call attempted
- [ ] Fast failure (< 100ms)

**Expected Error:**
```json
{
  "error": {
    "code": "missing_parameter",
    "message": "Required parameter 'config_id' not provided",
    "parameter": "config_id"
  }
}
```

### Step 2.2: Invalid Parameter Type

**Prompt:**
```
Call a tool with wrong parameter type (e.g., string instead of number).
How is the type error communicated?
```

**Success Criteria:**
- [ ] Type validation occurs
- [ ] Error specifies expected vs actual type
- [ ] Parameter name identified
- [ ] No cryptic backend errors

---

## Test 3: Malformed Requests

### Step 3.1: Invalid Tool Name

**Prompt:**
```
Try to call a non-existent tool like "invalid:nonexistent_tool".
What error do you receive?
```

**Success Criteria:**
- [ ] error.code = "tool_not_found"
- [ ] Lists available namespaces/tools
- [ ] Suggestion for similar tools (if applicable)
- [ ] Response time < 100ms

**Expected Error:**
```json
{
  "error": {
    "code": "tool_not_found",
    "message": "Tool 'invalid:nonexistent_tool' not found",
    "available_namespaces": ["chora", "coda", "gateway"],
    "suggestion": "Use gateway_status to list available tools"
  }
}
```

### Step 3.2: Invalid Namespace

**Prompt:**
```
Call a tool without a namespace (e.g., "list_generators" instead of "chora:list_generators").
What guidance is provided?
```

**Success Criteria:**
- [ ] Error indicates namespace required
- [ ] Lists available namespaces
- [ ] Suggests correct tool name

---

## Test 4: Event System Errors

### Step 4.1: Invalid Event Query

**Prompt:**
```
Use get_events with an invalid 'since' parameter like since="invalid".
How is the error handled?
```

**Success Criteria:**
- [ ] Parameter validation error
- [ ] Explains valid formats ("1h", "24h", ISO timestamp)
- [ ] No crash or undefined behavior

### Step 4.2: Event Log Corruption

**Prompt:**
```
What happens if the event log files are corrupted or unreadable?
Does get_events still work for recent events?
```

**Success Criteria:**
- [ ] Corrupted files skipped
- [ ] Error logged but not propagated
- [ ] Valid events still returned
- [ ] Graceful degradation

---

## Test 5: Configuration Errors

### Step 5.1: Invalid YAML Syntax

**Prompt:**
```
Edit config/event_mappings.yaml and introduce a YAML syntax error.
What happens when the hot-reload tries to process it?
```

**Success Criteria:**
- [ ] Error logged with line number
- [ ] Previous config preserved
- [ ] Gateway continues with old config
- [ ] No service disruption

**Expected Log:**
```
ERROR: Failed to reload config: Invalid YAML syntax at line 15
INFO: Previous configuration retained
```

### Step 5.2: Invalid Mapping Structure

**Prompt:**
```
Create a mapping with missing required fields (e.g., no workflow.id).
Does validation catch this?
```

**Success Criteria:**
- [ ] Schema validation occurs
- [ ] Error identifies missing fields
- [ ] Config reload rejected
- [ ] Previous config active

---

## Test 6: Resource Exhaustion

### Step 6.1: Concurrent Request Handling

**Prompt:**
```
If many tool calls are made simultaneously:
1. Are they all processed?
2. Is there rate limiting or queuing?
3. Does the gateway remain responsive?
```

**Success Criteria:**
- [ ] All requests processed (may queue)
- [ ] No dropped requests
- [ ] Reasonable performance degradation
- [ ] Gateway remains stable

### Step 6.2: Large Event Queries

**Prompt:**
```
Query events with limit=1000 (maximum).
Does the large result set cause issues?
```

**Success Criteria:**
- [ ] Large queries complete successfully
- [ ] Memory usage reasonable
- [ ] Response time acceptable (< 2s)
- [ ] No crashes or timeouts

---

## Test 7: Partial System Failures

### Step 7.1: Event Monitoring Disabled

**Prompt:**
```
If EventWatcher fails to start (e.g., .chora/memory/ not writable):
1. Does the gateway still function?
2. Are tool calls still processed?
3. What functionality is lost?
```

**Success Criteria:**
- [ ] Gateway starts despite EventWatcher failure
- [ ] Warning logged
- [ ] Tool routing still works
- [ ] get_events returns empty or partial results
- [ ] event_monitoring_enabled = false in status

### Step 7.2: One Backend Down

**Prompt:**
```
With multiple backends configured:
1. Stop one backend (e.g., coda-mcp)
2. Verify other backends still work (e.g., chora-composer)
3. Check gateway_status shows partial availability
```

**Success Criteria:**
- [ ] Working backends continue operating
- [ ] Failed backend clearly indicated
- [ ] No cascading failures
- [ ] Clear status differentiation

---

## Test 8: Recovery Mechanisms

### Step 8.1: Backend Auto-Restart

**Prompt:**
```
Does the gateway attempt to restart failed backends automatically?
Or is manual intervention required?
```

**Success Criteria:**
- [ ] Behavior documented
- [ ] If auto-restart: retry logic with backoff
- [ ] If manual: clear instructions for restart
- [ ] Status reflects current state

### Step 8.2: Event Log Recovery

**Prompt:**
```
If event logging fails temporarily (disk full, permissions):
Are events queued in memory for later write?
Or are they lost?
```

**Success Criteria:**
- [ ] Failure handling documented
- [ ] Events either queued or logged to fallback
- [ ] System doesn't crash
- [ ] Recovery when conditions improve

---

**Test Suite:** Error Handling & Resilience
**Duration:** 10-15 minutes
**Scenarios Tested:** 8 failure modes
**Status:** ✅ Resilience validated

---

## Next Steps

After completing this resilience test:

1. ✅ **All tests pass:** Proceed to [E2E_PERFORMANCE.md](E2E_PERFORMANCE.md) (optional)
2. ⚠️ **Unexpected crashes:** Review error handling implementation
3. ⚠️ **Poor error messages:** Improve error context and suggestions
4. 📝 **Document:** Note failure modes and recovery behaviors

## Troubleshooting

**Gateway crashes on errors:**
- Check exception handling in gateway code
- Review logs for stack traces
- Ensure all errors are caught and logged

**Unclear error messages:**
- Add more context to error responses
- Include trace IDs for debugging
- Provide actionable suggestions

**No recovery from failures:**
- Implement retry logic with exponential backoff
- Add health checks for backends
- Consider circuit breaker pattern
