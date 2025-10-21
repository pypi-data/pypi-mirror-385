# Sprint 3 End-to-End Test Plan

**Date:** 2025-10-19
**Sprint:** Sprint 3 Event Monitoring
**Purpose:** Validate complete integration before Sprint 4
**Timeline:** 1.5-2 hours
**Required:** 80%+ tests passing to proceed to Sprint 4

---

## Overview

This document provides a comprehensive end-to-end testing strategy to validate that Sprint 3 event monitoring works in real-world scenarios before building Sprint 4 features on top of it.

### Scope

- Full event monitoring pipeline validation
- chora-compose subprocess integration testing
- n8n webhook integration (optional feature)
- Performance and reliability validation
- Error handling and graceful degradation

### Test Environment

- **OS:** macOS (or Linux)
- **Python:** 3.12+
- **Gateway:** mcp-n8n v0.3.0-dev (Sprint 3 complete)
- **Backend:** chora-compose v1.3.0+
- **Optional:** n8n for webhook testing

---

## Prerequisites Checklist

**Before starting tests:**

- [ ] Sprint 3 committed (commit `850493639cd`)
- [ ] All 34 unit/integration tests passing
  ```bash
  python3.12 -m pytest tests/unit/test_event_watcher.py \
    tests/integration/test_event_monitoring_tutorial.py \
    tests/integration/test_gateway_event_integration.py -v
  # Expected: 34 passed
  ```
- [ ] No uncommitted changes in working directory
- [ ] chora-compose v1.3.0+ installed and accessible
  ```bash
  python3.12 -c "import chora_compose; print(chora_compose.__version__)"
  # Expected: >= 1.3.0
  ```
- [ ] n8n installed (optional, for webhook tests)
  ```bash
  npx n8n --version
  # Or: which n8n
  ```
- [ ] Event storage directory created
  ```bash
  mkdir -p var/telemetry .chora/memory/events
  ```

---

## Test Suite 1: Manual Smoke Tests (30 minutes)

**Goal:** Verify basic functionality works in real environment

### 1.1 Gateway Startup Test

**Objective:** Validate gateway starts cleanly with EventWatcher

**Steps:**
```bash
# Start gateway
python3.12 -m mcp_n8n.gateway
```

**Expected Output:**
```
=============================================================
mcp-n8n Gateway v0.3.0
Pattern P5: Gateway & Aggregator
=============================================================

Configuration:
  Log Level: INFO
  Debug: False
  Backend Timeout: 30s

[INFO] Initializing mcp-n8n gateway...
[INFO] Starting EventWatcher on var/telemetry/events.jsonl
[INFO] EventWatcher started successfully
[INFO] Backend status: {...}
[INFO] Total tools available: X

Starting gateway on STDIO transport...
-------------------------------------------------------------
```

**Success Criteria:**
- ✅ Gateway starts without errors
- ✅ "EventWatcher started successfully" message appears
- ✅ No warnings or error messages
- ✅ Gateway responds to Ctrl+C (SIGINT) and shuts down cleanly

**Failure Actions:**
- Check that `var/telemetry/` directory exists
- Check logs for specific error messages
- Verify Python dependencies installed
- Check file permissions on `.chora/memory/events/`

---

### 1.2 Event Detection Test

**Objective:** Verify EventWatcher detects events written to file

**Setup:**
- Keep gateway running from test 1.1
- Open second terminal for event generation

**Steps:**
```bash
# In second terminal, generate test event
echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","trace_id":"manual-test-001","status":"success","schema_version":"1.0","event_type":"test.manual","metadata":{"test":"smoke"}}' >> var/telemetry/events.jsonl
```

**Expected Gateway Logs:**
```
[INFO] Event detected: test.manual (trace: manual-test-001)
[INFO] Event stored in telemetry
```

**Verification:**
```bash
# Check event was stored
cat .chora/memory/events/$(date +%Y-%m)/events.jsonl | grep "manual-test-001"

# Check trace-specific file created
ls -la .chora/memory/events/$(date +%Y-%m)/traces/manual-test-001.jsonl
```

**Success Criteria:**
- ✅ Event detected within 100ms of write
- ✅ Event stored in `.chora/memory/events/[YYYY-MM]/events.jsonl`
- ✅ Trace-specific file created at `.chora/memory/events/[YYYY-MM]/traces/manual-test-001.jsonl`
- ✅ Both files contain the event JSON

**Performance Benchmark:**
- Detection latency: _____ ms (target: <100ms)

---

### 1.3 get_events Tool Test

**Objective:** Validate get_events MCP tool returns results

**Note:** This requires an MCP client (Claude Desktop, Cursor, or MCP inspector)

**If using MCP inspector:**
```bash
# Install MCP inspector if not available
npx @modelcontextprotocol/inspector python3.12 -m mcp_n8n.gateway
```

**Steps:**
1. Connect MCP client to gateway
2. Call tool: `get_events(trace_id="manual-test-001")`

**Expected Result:**
```json
[
  {
    "timestamp": "2025-10-19T...",
    "trace_id": "manual-test-001",
    "status": "success",
    "schema_version": "1.0",
    "event_type": "test.manual",
    "source": "mcp-n8n",
    "metadata": {
      "test": "smoke"
    }
  }
]
```

**Success Criteria:**
- ✅ Tool responds without error
- ✅ Returns array with 1 event
- ✅ Event data matches what was written
- ✅ Query completes in <10ms

**Performance Benchmark:**
- Query latency: _____ ms (target: <10ms)

---

## Test Suite 2: n8n Webhook Integration (30 minutes)

**Goal:** Validate optional webhook forwarding works

### 2.1 n8n Setup

**Objective:** Create test workflow to receive events

**Steps:**
```bash
# Start n8n (in new terminal)
npx n8n
# Opens http://localhost:5678
```

**Create Workflow:**
1. Open n8n UI (http://localhost:5678)
2. Create new workflow named "Chora Events Test"
3. Add **Webhook** trigger node:
   - Method: POST
   - Path: `chora-events-test`
   - Respond: Immediately
4. Add **Function** node connected to webhook:
   ```javascript
   // Display received event
   return {
     received_at: new Date().toISOString(),
     event_type: $json.event_type,
     trace_id: $json.trace_id,
     status: $json.status,
     full_event: $json
   };
   ```
5. **Activate** workflow
6. **Copy webhook URL** (e.g., `http://localhost:5678/webhook/chora-events-test`)

**Success Criteria:**
- ✅ n8n running on port 5678
- ✅ Workflow created and activated
- ✅ Webhook URL accessible

---

### 2.2 Gateway with Webhook Configuration

**Objective:** Start gateway with webhook URL configured

**Steps:**
```bash
# Stop gateway from test 1.1 (Ctrl+C)

# Set webhook URL environment variable
export N8N_EVENT_WEBHOOK_URL=http://localhost:5678/webhook/chora-events-test

# Restart gateway
python3.12 -m mcp_n8n.gateway
```

**Expected Output:**
```
[INFO] EventWatcher started successfully
[INFO] Webhook URL configured: http://localhost:5678/webhook/chora-events-test
```

**Success Criteria:**
- ✅ Gateway starts successfully
- ✅ Log message confirms webhook configured
- ✅ No connection errors

---

### 2.3 Webhook Delivery Test

**Objective:** Verify events delivered to n8n successfully

**Steps:**
```bash
# In second terminal, generate test event
echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","trace_id":"webhook-test-001","status":"success","schema_version":"1.0","event_type":"test.webhook","metadata":{"webhook":"enabled"}}' >> var/telemetry/events.jsonl
```

**Expected Gateway Logs:**
```
[INFO] Event detected: test.webhook (trace: webhook-test-001)
[INFO] Event stored in telemetry
[INFO] Event forwarded to webhook: webhook-test-001
```

**Verification in n8n:**
1. Check "Executions" tab in n8n
2. Should see new execution for "Chora Events Test" workflow
3. Click execution to view data
4. Verify received event matches what was sent

**Success Criteria:**
- ✅ Gateway logs show "Event forwarded to webhook"
- ✅ n8n workflow executed successfully
- ✅ n8n received complete event data
- ✅ Event also stored locally (dual consumption)
- ✅ Delivery latency <50ms

**Performance Benchmark:**
- Webhook delivery latency: _____ ms (target: <50ms best-effort)

---

### 2.4 Webhook Failure Graceful Degradation

**Objective:** Verify gateway continues working if webhook fails

**Steps:**
```bash
# Stop n8n (Ctrl+C in n8n terminal)

# Gateway should still be running

# Generate event with n8n down
echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","trace_id":"webhook-fail-001","status":"success","schema_version":"1.0","event_type":"test.webhook_fail"}' >> var/telemetry/events.jsonl
```

**Expected Gateway Logs:**
```
[INFO] Event detected: test.webhook_fail (trace: webhook-fail-001)
[INFO] Event stored in telemetry
[WARNING] Webhook delivery failed: Connection refused
```

**Verification:**
```bash
# Verify event still stored locally
cat .chora/memory/events/$(date +%Y-%m)/events.jsonl | grep "webhook-fail-001"
```

**Success Criteria:**
- ✅ Warning logged (not error)
- ✅ Event stored despite webhook failure
- ✅ Gateway continues running (doesn't crash)
- ✅ Subsequent events still processed

---

## Test Suite 3: chora-compose Integration (45 minutes)

**Goal:** Validate end-to-end with real chora-compose subprocess

**Note:** This requires chora-compose v1.3.0+ which supports event emission

### 3.1 Verify chora-compose Event Emission

**Objective:** Confirm chora-compose emits events to expected file

**Steps:**
```bash
# Ensure var/telemetry directory exists
mkdir -p var/telemetry

# Clear existing events for clean test
> var/telemetry/events.jsonl

# Run chora-compose directly (adjust to your setup)
# Example using chora-compose API:
python3.12 <<EOF
from chora_compose import __version__
print(f"chora-compose version: {__version__}")

# If you have test content configs, generate content
# This will emit events to var/telemetry/events.jsonl
# from chora_compose.generator import generate_content
# generate_content('test-content-config')
EOF

# Check that events file has content
cat var/telemetry/events.jsonl | tail -5
```

**Expected Output:**
```json
{"timestamp":"2025-10-19T...","trace_id":"...","event_type":"chora.content_generated",...}
```

**Success Criteria:**
- ✅ chora-compose version >= 1.3.0
- ✅ Events written to `var/telemetry/events.jsonl`
- ✅ Events have proper schema (timestamp, trace_id, event_type, etc.)

**If chora-compose doesn't emit events:**
- Check version is >= 1.3.0
- Verify event emission is enabled in chora-compose config
- Skip this test suite (not blocking for Sprint 3 validation)

---

### 3.2 Gateway Detects chora-compose Events

**Objective:** Verify EventWatcher detects events from chora-compose

**Steps:**
```bash
# Ensure gateway is running with EventWatcher

# Clear events file
> var/telemetry/events.jsonl

# Run chora-compose operation that emits events
# (Adjust based on your chora-compose setup)
# Example:
# python3.12 -c "from chora_compose.generator import generate_content; generate_content('test-config')"

# Watch gateway logs for event detection
```

**Expected Gateway Logs:**
```
[INFO] Event detected: chora.content_generated (trace: ...)
[INFO] Event stored in telemetry
```

**Verification:**
```bash
# Check events stored in gateway telemetry
ls -la .chora/memory/events/$(date +%Y-%m)/events.jsonl
cat .chora/memory/events/$(date +%Y-%m)/events.jsonl | tail -5
```

**Success Criteria:**
- ✅ Gateway detects chora-compose events
- ✅ Events stored in gateway telemetry
- ✅ Event type is `chora.*` (from chora-compose)
- ✅ trace_id populated

---

### 3.3 Trace ID Propagation (Deferred to JSON-RPC)

**Current Status:** ⏸️ DEFERRED - Requires JSON-RPC implementation

**Note:** Trace ID propagation per-request (not per-subprocess) requires JSON-RPC communication between gateway and backend. This is documented as future work.

**Current Capability:**
- Trace ID can be set via environment variable for subprocess
- This works for single-operation subprocesses
- Per-request propagation is TODO

**Test Workaround:**
```bash
# Manual test with environment variable
export CHORA_TRACE_ID="manual-trace-$(date +%s)"

# Run chora-compose with this trace_id
# It should use the environment variable

# Verify events have the trace_id
cat var/telemetry/events.jsonl | grep "$CHORA_TRACE_ID"
```

**Success Criteria (Manual):**
- ✅ Environment variable propagates to subprocess
- ✅ chora-compose reads and uses CHORA_TRACE_ID
- ✅ Events contain the specified trace_id

**Future Work:**
- Implement JSON-RPC for per-request trace propagation
- See [backends/base.py:TODO](../../../src/mcp_n8n/backends/base.py) comments

---

### 3.4 Multi-Step Workflow Simulation

**Objective:** Simulate multi-step workflow with event correlation

**Note:** This is a simulated test using manual events until gateway<->backend integration is complete

**Steps:**
```bash
# Simulate multi-step workflow with shared trace_id
WORKFLOW_TRACE_ID="workflow-$(date +%s)"

# Step 1: Content generation event
echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","trace_id":"'$WORKFLOW_TRACE_ID'","status":"success","schema_version":"1.0","event_type":"chora.content_generated","metadata":{"content_config_id":"intro"}}' >> var/telemetry/events.jsonl

sleep 1

# Step 2: Artifact assembly event
echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","trace_id":"'$WORKFLOW_TRACE_ID'","status":"success","schema_version":"1.0","event_type":"chora.artifact_assembled","metadata":{"artifact_id":"daily-report"}}' >> var/telemetry/events.jsonl
```

**Verification:**
```bash
# Query all events for this workflow (via MCP client or direct query)
python3.12 <<EOF
import asyncio
from mcp_n8n.memory.event_log import EventLog
from mcp_n8n.tools.event_query import get_events, set_event_log

async def test():
    event_log = EventLog()
    set_event_log(event_log)
    events = await get_events(trace_id="$WORKFLOW_TRACE_ID")
    print(f"Found {len(events)} events for workflow:")
    for e in events:
        print(f"  - {e['event_type']} @ {e['timestamp']}")

asyncio.run(test())
EOF
```

**Expected Output:**
```
Found 2 events for workflow:
  - chora.content_generated @ 2025-10-19T...
  - chora.artifact_assembled @ 2025-10-19T...
```

**Success Criteria:**
- ✅ Both events visible in event log
- ✅ Same trace_id for both
- ✅ Events chronologically ordered
- ✅ Query returns complete workflow timeline

---

## Test Suite 4: Performance & Reliability (15 minutes)

**Goal:** Validate performance targets and error handling

### 4.1 Event Latency Test

**Objective:** Measure event detection latency

**Steps:**
```bash
# Generate 10 events rapidly
for i in {1..10}; do
  echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","trace_id":"perf-test-'$i'","status":"success","schema_version":"1.0","event_type":"test.performance"}' >> var/telemetry/events.jsonl
  sleep 0.1
done

# Watch gateway logs for timestamps
```

**Measurement:**
- Note timestamp when event written
- Note timestamp in gateway log when detected
- Calculate delta for each event

**Success Criteria:**
- ✅ All 10 events detected
- ✅ Detection latency < 100ms for each
- ✅ No events missed or delayed significantly

**Performance Benchmark:**
- Average latency: _____ ms (target: <100ms)
- Max latency: _____ ms (target: <200ms)
- Min latency: _____ ms

---

### 4.2 Malformed JSON Handling

**Objective:** Verify graceful handling of malformed input

**Steps:**
```bash
# Write malformed JSON
echo "{ invalid json }" >> var/telemetry/events.jsonl

# Write valid event after
echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","trace_id":"after-error","status":"success","schema_version":"1.0","event_type":"test.error_recovery"}' >> var/telemetry/events.jsonl
```

**Expected Gateway Logs:**
```
[WARNING] Malformed JSON in events file: Expecting property name enclosed in double quotes: line 1 column 3 (char 2)
[INFO] Event detected: test.error_recovery (trace: after-error)
[INFO] Event stored in telemetry
```

**Verification:**
```bash
# Check valid event was still processed
cat .chora/memory/events/$(date +%Y-%m)/events.jsonl | grep "after-error"
```

**Success Criteria:**
- ✅ Malformed JSON logged as WARNING (not ERROR)
- ✅ Subsequent valid events processed normally
- ✅ EventWatcher continues running (doesn't crash)
- ✅ No data corruption in event storage

---

### 4.3 Batch Processing Test

**Objective:** Verify reliable handling of event bursts

**Steps:**
```bash
# Generate 100 events rapidly
for i in {1..100}; do
  echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","trace_id":"batch-'$(printf "%03d" $i)'","status":"success","schema_version":"1.0","event_type":"test.batch"}' >> var/telemetry/events.jsonl
done

# Wait for processing
sleep 3

# Query all batch events
python3.12 <<EOF
import asyncio
from mcp_n8n.memory.event_log import EventLog
from mcp_n8n.tools.event_query import get_events, set_event_log

async def test():
    event_log = EventLog()
    set_event_log(event_log)
    events = await get_events(event_type="test.batch", limit=100)
    print(f"Found {len(events)} batch events")

asyncio.run(test())
EOF
```

**Expected Output:**
```
Found 100 batch events
```

**Success Criteria:**
- ✅ All 100 events detected and stored
- ✅ No events lost or duplicated
- ✅ Query returns exactly 100 events
- ✅ No performance degradation observed

**Performance Benchmark:**
- Total processing time: _____ seconds (100 events)
- Throughput: _____ events/second

---

## Results Documentation

### Test Execution Summary

| Test Suite | Tests | Passed | Failed | Skipped | Pass Rate |
|------------|-------|--------|--------|---------|-----------|
| Suite 1: Smoke Tests | 3 | ___ | ___ | ___ | ___% |
| Suite 2: n8n Integration | 4 | ___ | ___ | ___ | ___% |
| Suite 3: chora-compose | 4 | ___ | ___ | ___ | ___% |
| Suite 4: Performance | 3 | ___ | ___ | ___ | ___% |
| **Total** | **14** | **___** | **___** | **___** | **___%** |

**Overall Quality Gate:** ___% (target: ≥80% to proceed to Sprint 4)

---

### Performance Metrics Summary

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Event detection latency | <100ms | ___ ms | ⬜ |
| Webhook delivery latency | <50ms | ___ ms | ⬜ |
| Query latency (get_events) | <10ms | ___ ms | ⬜ |
| Batch throughput | N/A | ___ events/sec | ⬜ |

---

### Issues Found

**Issue 1:** ___________________________________________

- **Severity:** Critical / High / Medium / Low
- **Test:** [Suite X.Y Test Name]
- **Reproduction:**
- **Expected:**
- **Actual:**
- **Action:**

**Issue 2:** ___________________________________________

[Add more as needed]

---

## Decision Matrix

Based on test results, choose next steps:

### Scenario A: ≥95% Tests Passing (Excellent)

**Decision:** ✅ **Proceed to Sprint 4 immediately**

- Event monitoring foundation is solid
- All critical paths validated
- Performance meets targets
- Ready for Sprint 4 features

**Actions:**
- Document test results
- Mark Sprint 3 as COMPLETE
- Begin Sprint 4 planning

---

### Scenario B: 80-94% Tests Passing (Good)

**Decision:** ⚠️ **Fix minor issues, then proceed to Sprint 4**

- Core functionality works
- Some edge cases or optional features need work
- Non-critical bugs can be fixed

**Actions:**
1. Document all failing tests
2. Triage issues (critical vs nice-to-have)
3. Fix critical issues (estimated: ___ hours)
4. Rerun affected tests
5. Proceed to Sprint 4 when critical issues resolved

---

### Scenario C: <80% Tests Passing (Needs Work)

**Decision:** ❌ **Address issues before Sprint 4**

- Foundational problems exist
- Sprint 4 would build on unstable base
- Need to investigate and fix

**Actions:**
1. Document all failing tests with details
2. Root cause analysis for failures
3. Prioritize fixes
4. Implement fixes (estimated: ___ hours)
5. Rerun full test suite
6. Only proceed to Sprint 4 after ≥80% pass rate

---

## Appendix A: Quick Test Commands

**Run all unit/integration tests:**
```bash
python3.12 -m pytest tests/unit/test_event_watcher.py \
  tests/integration/test_event_monitoring_tutorial.py \
  tests/integration/test_gateway_event_integration.py -v
```

**Start gateway:**
```bash
python3.12 -m mcp_n8n.gateway
```

**Generate test event:**
```bash
echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","trace_id":"test-'$(date +%s)'","status":"success","schema_version":"1.0","event_type":"test.manual"}' >> var/telemetry/events.jsonl
```

**Query events:**
```bash
python3.12 <<EOF
import asyncio
from mcp_n8n.memory.event_log import EventLog
from mcp_n8n.tools.event_query import get_events, set_event_log

async def query():
    set_event_log(EventLog())
    events = await get_events(limit=10)
    for e in events:
        print(f"{e['trace_id']}: {e['event_type']}")

asyncio.run(query())
EOF
```

**Clear event files:**
```bash
> var/telemetry/events.jsonl
rm -rf .chora/memory/events/*
```

---

## Appendix B: Common Issues & Solutions

### Issue: Gateway won't start

**Symptoms:** Gateway exits immediately or errors on startup

**Solutions:**
1. Check Python version: `python3.12 --version` (need 3.12+)
2. Check dependencies: `pip install -e ".[dev]"`
3. Check file permissions: `ls -la .chora/memory/events/`
4. Check for port conflicts
5. Review error message in logs

### Issue: Events not detected

**Symptoms:** Events written but gateway doesn't log detection

**Solutions:**
1. Verify EventWatcher started: Check for "EventWatcher started successfully" in logs
2. Check file path: Ensure writing to `var/telemetry/events.jsonl`
3. Check polling: EventWatcher polls every 50ms
4. Check JSON format: Malformed JSON is skipped with warning
5. Check file permissions: EventWatcher needs read access

### Issue: get_events returns no results

**Symptoms:** Query returns empty array

**Solutions:**
1. Verify EventLog base_dir: Default is `.chora/memory/events`
2. Check monthly partition exists: `.chora/memory/events/2025-10/`
3. Verify events file has content: `cat .chora/memory/events/2025-10/events.jsonl`
4. Check query parameters: Ensure trace_id/type match what was emitted
5. Check set_event_log was called: Tool needs EventLog instance

### Issue: Webhook not receiving events

**Symptoms:** n8n workflow doesn't execute

**Solutions:**
1. Verify n8n running: `curl http://localhost:5678` should respond
2. Check workflow activated: Look for green "Active" badge in n8n
3. Verify webhook URL: Check N8N_EVENT_WEBHOOK_URL env var
4. Check URL format: Should be `http://localhost:5678/webhook/[path]`
5. Review gateway logs: Look for "Event forwarded to webhook" or errors

---

**Document Status:** READY FOR EXECUTION
**Last Updated:** 2025-10-19
**Next Steps:** Run test suites and document results
**Quality Gate:** ≥80% pass rate required for Sprint 4
