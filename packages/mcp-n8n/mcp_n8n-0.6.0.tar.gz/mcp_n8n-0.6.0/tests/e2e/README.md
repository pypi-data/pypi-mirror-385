# mcp-n8n E2E Test Suite

**Version:** v1.0.0
**Last Updated:** October 21, 2025
**Target Environment:** Claude Desktop

---

## Overview

This directory contains end-to-end (E2E) test suites designed to validate mcp-n8n gateway functionality through **interactive testing in Claude Desktop**. These tests are human-executed with clear pass/fail criteria.

### Design Philosophy

- **Human-in-the-loop:** Tests are prompts given to Claude Desktop, not automated scripts
- **Self-contained:** Each suite is independent and self-documenting
- **Progressive:** Start with smoke tests, build to advanced scenarios
- **Clear criteria:** Explicit success/failure indicators for each test
- **Real environment:** Tests run against actual gateway + backends

---

## Test Suite Catalog

### 1. **E2E_SMOKE_TEST.md** ⚡ (Foundation)
**Duration:** 5-10 minutes
**Purpose:** Quick validation that gateway is functioning
**Tools:** `gateway_status`, `get_events`

**When to run:**
- First-time gateway setup
- After configuration changes
- Before other test suites
- Quick health check

**Validates:**
- Gateway startup and initialization
- Backend connectivity
- Basic tool routing
- Event monitoring active

**Start here:** [E2E_SMOKE_TEST.md](E2E_SMOKE_TEST.md)

---

### 2. **E2E_BACKEND_ROUTING.md** 🔀 (Core)
**Duration:** 10-15 minutes
**Purpose:** Validate namespace-based routing to backends
**Tools:** `chora:*`, `coda:*`, gateway tools

**Validates:**
- Namespace-based routing (chora:, coda:)
- Tool name resolution
- Parameter passing across boundaries
- Error propagation
- Backend isolation

**Prerequisites:** Smoke test passing
**Continue:** [E2E_BACKEND_ROUTING.md](E2E_BACKEND_ROUTING.md)

---

### 3. **E2E_EVENT_MONITORING.md** 📊 (Telemetry)
**Duration:** 15-20 minutes
**Purpose:** Validate event capture and query capabilities
**Tools:** `get_events` with extensive filtering

**Validates:**
- Event capture (gateway, tool calls, backend events)
- Trace context propagation
- Query filtering (type, status, time, trace_id)
- Event correlation
- Webhook forwarding (optional)

**Prerequisites:** Backend routing working
**Continue:** [E2E_EVENT_MONITORING.md](E2E_EVENT_MONITORING.md)

---

### 4. **E2E_WORKFLOW_ORCHESTRATION.md** ⚙️ (Sprint 5)
**Duration:** 20-25 minutes
**Purpose:** Validate event-driven workflow features
**Components:** EventWorkflowRouter, Daily Report, Hot-reload

**Validates:**
- Event pattern matching
- Jinja2 parameter templating
- Daily Report workflow (git + telemetry)
- Config hot-reload
- Template rendering via chora-compose

**Prerequisites:** Event monitoring working
**Continue:** [E2E_WORKFLOW_ORCHESTRATION.md](E2E_WORKFLOW_ORCHESTRATION.md)

---

### 5. **E2E_ERROR_HANDLING.md** 🛡️ (Resilience)
**Duration:** 10-15 minutes
**Purpose:** Validate error handling and graceful degradation

**Validates:**
- Backend unavailability handling
- Invalid parameter validation
- Malformed request handling
- Config validation
- Partial system failures
- Recovery mechanisms

**Prerequisites:** Workflow orchestration tested
**Continue:** [E2E_ERROR_HANDLING.md](E2E_ERROR_HANDLING.md)

---

### 6. **E2E_PERFORMANCE.md** 🚀 (Optional)
**Duration:** 15-20 minutes
**Purpose:** Validate performance characteristics

**Validates:**
- Gateway overhead (< 1ms target)
- Tool call latency
- Event query performance
- Concurrent request handling
- Memory usage patterns
- Config reload speed

**Prerequisites:** All core tests passing
**Continue:** [E2E_PERFORMANCE.md](E2E_PERFORMANCE.md)

---

## Prerequisites

### Required

1. **mcp-n8n Gateway Installed**
   ```bash
   pip install mcp-n8n
   ```

2. **Claude Desktop Configured**
   - mcp-n8n added to `claude_desktop_config.json`
   - Gateway appears in tools list

3. **Environment Variables**
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   export CODA_API_KEY=your_key_here  # Optional, for Coda tests
   ```

4. **chora-compose Backend**
   - Installed and accessible
   - Configured in gateway

5. **Git Repository**
   - For Daily Report workflow tests
   - Initialized with commits

### Optional

- **n8n Webhook:** For event forwarding tests
- **Coda MCP:** For multi-backend routing tests

---

## How to Run Tests

### Step 1: Start Gateway

Ensure mcp-n8n gateway is running through Claude Desktop:

1. Open Claude Desktop
2. Verify mcp-n8n appears in tools list
3. Check connection is active

### Step 2: Run Smoke Test

Open [E2E_SMOKE_TEST.md](E2E_SMOKE_TEST.md) and follow the prompts:

```
Use gateway_status to check if the mcp-n8n gateway is running and healthy.
What backends are connected?
```

Give this prompt to Claude Desktop and verify the success criteria.

### Step 3: Progress Through Suites

Complete each suite in order:

1. ✅ Smoke Test (foundation)
2. ✅ Backend Routing (core)
3. ✅ Event Monitoring (telemetry)
4. ✅ Workflow Orchestration (Sprint 5)
5. ✅ Error Handling (resilience)
6. ⭐ Performance (optional)

### Step 4: Document Results

For each suite, check off success criteria and note:
- Which tests passed ✅
- Which tests failed ❌
- Any unexpected behavior ⚠️
- Performance observations 📊

---

## Success Criteria Format

Each test includes clear success criteria like:

```markdown
**Success Criteria:**
- [ ] Response time < 100ms
- [ ] Backend status = "running"
- [ ] No errors in output
- [ ] Trace ID included
```

Check each box as you verify the criterion.

---

## Test Execution Time

| Suite | Duration | Cumulative |
|-------|----------|------------|
| Smoke Test | 5-10 min | 5-10 min |
| Backend Routing | 10-15 min | 15-25 min |
| Event Monitoring | 15-20 min | 30-45 min |
| Workflow Orchestration | 20-25 min | 50-70 min |
| Error Handling | 10-15 min | 60-85 min |
| Performance (optional) | 15-20 min | 75-105 min |

**Total: 60-85 minutes** (or 75-105 min with performance suite)

---

## Troubleshooting

### Gateway Not Responding

1. Check Claude Desktop configuration
2. Verify mcp-n8n in tools list
3. Review logs: `logs/mcp-n8n.log`
4. Restart Claude Desktop

### Backend Not Found

1. Check `gateway_status` output
2. Verify chora-compose is installed
3. Check backend configuration
4. Review subprocess logs

### Event Monitoring Disabled

1. Check `.chora/memory/events/` exists
2. Verify file permissions
3. Review EventWatcher logs
4. Check gateway_status for event_monitoring_enabled

### Tests Failing

1. Run smoke test first
2. Check prerequisites are met
3. Review error messages
4. Check logs for details
5. Verify environment variables set

---

## Test Fixtures

The `fixtures/` directory contains:

- **sample_events.json:** Example event structures
- **test_event_mappings.yaml:** Sample workflow mappings
- **expected_outputs/:** Expected responses for comparison

These fixtures help validate test results.

---

## Continuous Improvement

This test suite should evolve with the gateway:

### Adding New Tests

1. Create new markdown file in `tests/e2e/`
2. Follow existing format (prompts + success criteria)
3. Add to this README catalog
4. Link from prerequisite suites

### Updating Existing Tests

1. Verify prompts work with current version
2. Update expected outputs if API changes
3. Adjust success criteria for performance targets
4. Document breaking changes

### Version Compatibility

- **v1.0.0:** mcp-n8n v0.4.0+
- Tests validated with Sprint 5 release
- Backward compatibility not guaranteed

---

## Related Documentation

- [Testing Guide](../../docs/TESTING.md) - Automated test information
- [Development Guide](../../docs/DEVELOPMENT.md) - Local development setup
- [Architecture](../../docs/ecosystem/architecture.md) - System design
- [Workflow API Reference](../../docs/workflows/daily-report-api-reference.md) - API docs

---

## Contributing

To contribute new E2E tests:

1. Follow the existing format
2. Include clear prompts and success criteria
3. Test in Claude Desktop before submitting
4. Document prerequisites
5. Add to this README

---

## Feedback

Found issues with tests? Improvements to suggest?

- Open GitHub issue with `e2e-test` label
- Include test suite name and step number
- Describe expected vs actual behavior
- Suggest improved wording or criteria

---

**Happy Testing! 🧪**

For questions or issues, see the [main project README](../../README.md) or open a GitHub issue.
