# E2E Test Suite: Smoke Test

**Version:** v1.0.0
**Duration:** 5-10 minutes
**Purpose:** Quick validation that mcp-n8n gateway is functioning correctly
**Prerequisites:** Gateway running in Claude Desktop, ANTHROPIC_API_KEY set
**Last Updated:** October 21, 2025

---

## ⚠️ IMPORTANT: Server Disambiguation

**You may have TWO MCP servers running:**

1. **mcp-n8n gateway** - The server we are testing
   - Name: "mcp-n8n"
   - Has gateway-specific tools: `gateway_status`, `get_events`
   - Routes to backends with namespaces: `chora:*`, `coda:*`
   - This is the AGGREGATOR/GATEWAY pattern

2. **chora-compose (direct)** - The backend server (may also be configured)
   - Name: "chora-compose"
   - Has direct tools: `list_generators`, `generate_content` (NO namespace prefix)
   - This is a BACKEND server

**How to tell which server you're using:**

✅ **Using mcp-n8n gateway (CORRECT for these tests):**

- Tool `gateway_status` is available
- Tool `get_events` is available
- Chora tools are namespaced: `chora:list_generators`
- Backend name in status is "chora-composer" (with hyphen)

❌ **Using chora-compose directly (WRONG for these tests):**

- No `gateway_status` tool
- No `get_events` tool
- Tools are NOT namespaced: `list_generators` (no `chora:` prefix)
- This is NOT the gateway

**Before starting tests, verify you're using the gateway:**

Ask Claude Desktop:
```
Do you have a tool called "gateway_status"?
If yes, what server provides it?
```

Expected answer: "Yes, from mcp-n8n server"

---

## Overview

This suite validates **basic gateway functionality** - ensuring the mcp-n8n gateway starts successfully, connects to backends, and responds to simple queries.

### What You'll Test

**Tools (2):**
- `gateway_status` - Gateway health and backend connectivity
- `get_events` - Event log query functionality

**Success Indicators:**
- Gateway responds to tool calls
- Backends are discovered and connected
- Event monitoring is active
- Tool namespacing works correctly

---

## Test 0: Server Verification (REQUIRED FIRST)

### Step 0.1: Verify You're Using mcp-n8n Gateway

**Prompt:**
```
List all available MCP servers and their tools.
Do you have a tool called "gateway_status"?
If yes, which server provides it?
```

**Success Criteria:**
- [ ] `gateway_status` tool exists
- [ ] Provided by server named "mcp-n8n" (NOT "chora-compose")
- [ ] Tool `get_events` also exists
- [ ] Chora tools are namespaced: `chora:list_generators` (NOT just `list_generators`)

**Expected Answer:**
```
Yes, I have a tool called "gateway_status" from the mcp-n8n server.
I also have chora:list_generators (namespaced with chora:) from the same server.
```

**If you see this instead - STOP:**
```
I have list_generators from chora-compose server.
I don't have gateway_status.
```
→ This means you're connected to chora-compose directly, NOT the gateway.
→ Check your Claude Desktop configuration and ensure mcp-n8n is enabled.

### Step 0.2: Confirm Tool Namespacing

**Prompt:**
```
Show me the exact names of all tools that involve "list_generators".
Are they namespaced with "chora:" prefix?
```

**Success Criteria:**
- [ ] Tool is named `chora:list_generators` (WITH namespace prefix)
- [ ] NOT named just `list_generators` (without prefix)
- [ ] This confirms you're using the gateway routing

**Why this matters:**
- Gateway adds namespace prefixes to backend tools
- Direct chora-compose has no prefix
- If you see `list_generators` without `chora:`, you're testing the wrong server!

---

## Test 1: Gateway Health Check

### Step 1.1: Check Gateway Status

**Prompt:**
```
Use gateway_status to check if the mcp-n8n gateway is running and healthy.
What backends are connected?
```

**Success Criteria:**
- [ ] gateway.name = "mcp-n8n"
- [ ] gateway.version shows current version (e.g., "0.4.0")
- [ ] backends object contains at least one backend
- [ ] Response time < 100ms

**Expected Output:**
```json
{
  "gateway": {
    "name": "mcp-n8n",
    "version": "0.4.0",
    "config": {
      "log_level": "INFO",
      "debug": false,
      "backend_timeout": 30
    },
    "event_monitoring": {
      "enabled": true,
      "webhook_configured": false
    }
  },
  "backends": {
    "chora-composer": {
      "status": "running",
      "namespace": "chora",
      "tool_count": 17
    }
  },
  "capabilities": {
    "tools": 19,
    "resources": 0,
    "prompts": 0
  }
}
```

---

## Test 2: Backend Discovery

### Step 2.1: Verify Backend Registration

**Prompt:**
```
From the gateway_status output, list all registered backends.
What namespaces are available?
```

**Success Criteria:**
- [ ] At least "chora-composer" backend registered
- [ ] Backend status = "running"
- [ ] Namespace "chora" is available
- [ ] tool_count > 0 for each backend

**Expected Backends:**
- **chora-composer**: Artifact generation (namespace: `chora`)
- **coda-mcp** (optional): Data operations (namespace: `coda`)

---

## Test 3: Tool Namespacing

### Step 3.1: List Available Tools

**Prompt:**
```
What tools are available through the gateway?
Show me the complete list with their namespaces.
```

**Success Criteria:**
- [ ] Tools are namespaced (e.g., `chora:generate_content`)
- [ ] Gateway tools available (`gateway_status`, `get_events`)
- [ ] No duplicate tool names across namespaces

**Expected Tools (minimum):**
- `gateway_status` - Gateway-level tool
- `get_events` - Gateway-level tool
- `chora:list_generators` - Chora Composer tool
- `chora:generate_content` - Chora Composer tool
- Additional chora:* tools...

---

## Test 4: Event Monitoring

### Step 4.1: Query Recent Events

**Prompt:**
```
Use get_events to show the last 10 events from the gateway.
What types of events are being captured?
```

**Success Criteria:**
- [ ] Returns list of events
- [ ] Events have required fields: type, timestamp, trace_id
- [ ] At least one "gateway.started" event
- [ ] Events are ordered chronologically
- [ ] Response time < 200ms

**Expected Event Structure:**
```json
[
  {
    "type": "gateway.started",
    "timestamp": "2025-10-21T14:30:00.123Z",
    "trace_id": "abc123...",
    "status": "success",
    "data": {
      "version": "0.4.0",
      "backend_count": 1
    }
  }
]
```

### Step 4.2: Filter Events by Type

**Prompt:**
```
Use get_events with event_type="gateway.started" to find gateway startup events.
How many times has the gateway been restarted?
```

**Success Criteria:**
- [ ] Filtering works correctly
- [ ] Only returns events matching the type
- [ ] At least 1 event returned

---

## Test 5: Error Handling

### Step 5.1: Invalid Query Parameters

**Prompt:**
```
Try to use get_events with limit=5000 (above the max of 1000).
What happens?
```

**Success Criteria:**
- [ ] Limit is clamped to 1000
- [ ] No error thrown
- [ ] Returns valid results

### Step 5.2: Query Non-existent Event Type

**Prompt:**
```
Use get_events with event_type="nonexistent.event.type".
What is the response?
```

**Success Criteria:**
- [ ] Returns empty list []
- [ ] No error thrown
- [ ] Response time < 100ms

---

## Test 6: Performance Baseline

### Step 6.1: Response Time Check

**Prompt:**
```
Call gateway_status three times in a row.
What is the average response time?
```

**Success Criteria:**
- [ ] All calls complete successfully
- [ ] Average response time < 100ms
- [ ] Consistent performance across calls

---

**Test Suite:** Smoke Test
**Duration:** 5-10 minutes
**Tools Tested:** 2 of 19+
**Status:** ✅ Foundation validated

---

## Next Steps

After completing this smoke test:

1. ✅ **If all tests pass:** Proceed to [E2E_BACKEND_ROUTING.md](E2E_BACKEND_ROUTING.md)
2. ⚠️ **If any test fails:** Check gateway logs and backend connectivity
3. 📝 **Document:** Note any unexpected behavior for investigation

## Troubleshooting

**Gateway not responding:**
- Verify mcp-n8n is configured in Claude Desktop's `claude_desktop_config.json`
- Check logs at `logs/mcp-n8n.log`
- Ensure ANTHROPIC_API_KEY is set

**No backends registered:**
- Check chora-compose is installed and accessible
- Verify backend configuration in gateway config
- Check subprocess logs for backend startup errors

**Event monitoring disabled:**
- Verify `.chora/memory/events/` directory exists
- Check file permissions
- Review EventWatcher initialization logs
