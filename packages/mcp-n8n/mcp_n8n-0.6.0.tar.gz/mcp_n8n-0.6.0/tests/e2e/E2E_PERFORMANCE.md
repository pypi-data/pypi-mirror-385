# E2E Test Suite: Performance Validation

**Version:** v1.0.0
**Duration:** 15-20 minutes
**Purpose:** Validate performance characteristics and identify bottlenecks
**Prerequisites:** Complete [E2E_ERROR_HANDLING.md](E2E_ERROR_HANDLING.md) first
**Last Updated:** October 21, 2025

---

## Overview

This suite validates **performance characteristics** - ensuring the gateway meets performance targets for latency, throughput, and resource usage.

### What You'll Test

**Performance Metrics:**
- Gateway overhead (< 1ms target)
- Tool call latency
- Event query performance
- Concurrent request handling
- Memory usage patterns
- Config reload speed

**Benchmarks:**
- Baseline: Direct MCP server call
- With Gateway: Additional overhead
- Target: < 0.001ms overhead (Phase 0 validation: 2500x faster than 2.5ms target)

---

## Test 1: Gateway Overhead

### Step 1.1: Measure Routing Latency

**Prompt:**
```
Call gateway_status 10 times and record the response times.
Calculate:
1. Minimum latency
2. Maximum latency
3. Average latency
4. Standard deviation
```

**Success Criteria:**
- [ ] Average latency < 100ms
- [ ] No extreme outliers (> 500ms)
- [ ] Consistent performance across calls
- [ ] Minimal variation (std dev < 20ms)

**Expected Results:**
```
Min: 15ms
Max: 85ms
Avg: 45ms
StdDev: 18ms
```

### Step 1.2: Compare Direct vs Gateway

**Prompt:**
```
If possible, measure:
1. Direct call to chora-composer (without gateway)
2. Same call through mcp-n8n gateway

What is the gateway overhead?
```

**Success Criteria:**
- [ ] Overhead < 10ms for simple calls
- [ ] Overhead proportional to call complexity
- [ ] No exponential degradation

---

## Test 2: Tool Call Performance

### Step 2.1: Lightweight Tool Calls

**Prompt:**
```
Measure latency for chora:list_generators (metadata query, no AI):
- Call 5 times
- Record each duration
- Calculate average
```

**Success Criteria:**
- [ ] Average < 2000ms
- [ ] Consistent timing
- [ ] No degradation over repeated calls

### Step 2.2: Heavy Tool Calls

**Prompt:**
```
Measure latency for chora:generate_content (AI generation):
- Call 3 times with same template
- Record each duration
- Note variation
```

**Success Criteria:**
- [ ] Average 3-7 seconds (AI generation time)
- [ ] Gateway overhead < 5% of total time
- [ ] Acceptable variation (AI is non-deterministic)

---

## Test 3: Event Query Performance

### Step 3.1: Small Result Sets

**Prompt:**
```
Query events with limit=10:
get_events(limit=10)

Measure response time.
```

**Success Criteria:**
- [ ] Response time < 200ms
- [ ] Linear scaling with limit
- [ ] No full table scans

### Step 3.2: Large Result Sets

**Prompt:**
```
Query events with limit=1000 (maximum):
get_events(limit=1000)

Measure response time.
```

**Success Criteria:**
- [ ] Response time < 2000ms
- [ ] Memory usage reasonable (< 100MB)
- [ ] No pagination issues

### Step 3.3: Filtered Queries

**Prompt:**
```
Compare query times:
1. get_events(limit=100) - No filters
2. get_events(event_type="gateway.tool_call", limit=100)
3. get_events(trace_id="specific_id")

Which is fastest? Does filtering help or hurt?
```

**Success Criteria:**
- [ ] Filtered queries should be faster
- [ ] trace_id lookup very fast (indexed)
- [ ] event_type filter reduces scan size

---

## Test 4: Concurrent Requests

### Step 4.1: Parallel Tool Calls

**Prompt:**
```
If Claude Desktop supports it, make multiple calls simultaneously:
- 3x gateway_status in parallel
- 2x chora:list_generators in parallel

Do they complete faster than sequential?
```

**Success Criteria:**
- [ ] Concurrent execution supported
- [ ] Total time < sequential sum
- [ ] No deadlocks or race conditions
- [ ] All calls complete successfully

### Step 4.2: Backend Concurrency

**Prompt:**
```
Make concurrent calls to the same backend:
- 5x chora:list_generators simultaneously

Does the backend handle concurrency?
```

**Success Criteria:**
- [ ] Backend processes requests
- [ ] May queue or execute in parallel
- [ ] No errors from concurrency
- [ ] Reasonable throughput

---

## Test 5: Memory Usage

### Step 5.1: Baseline Memory

**Prompt:**
```
Check gateway process memory usage at startup:
ps aux | grep mcp-n8n

Record RSS (Resident Set Size).
```

**Success Criteria:**
- [ ] Baseline < 200MB
- [ ] Reasonable for Python process
- [ ] Stable over time

### Step 5.2: Memory Under Load

**Prompt:**
```
After running all E2E tests (generating events, tool calls, etc.):
Check memory usage again.

Has it grown significantly?
```

**Success Criteria:**
- [ ] Growth < 100MB from baseline
- [ ] No memory leaks
- [ ] Garbage collection working
- [ ] Returns to baseline when idle

### Step 5.3: Event Log Memory

**Prompt:**
```
Query large event sets (limit=1000) multiple times.
Does memory spike and recover?
```

**Success Criteria:**
- [ ] Temporary spike during query
- [ ] Memory released after query
- [ ] No accumulation over repeated queries

---

## Test 6: Config Reload Performance

### Step 6.1: Reload Speed

**Prompt:**
```
Modify config/event_mappings.yaml and measure reload time.
Check logs for duration.
```

**Success Criteria:**
- [ ] Reload completes < 100ms
- [ ] No service interruption
- [ ] Thread-safe operation

### Step 6.2: Large Config Files

**Prompt:**
```
Test with config file containing:
- 10 mappings
- 50 mappings
- 100 mappings

How does reload time scale?
```

**Success Criteria:**
- [ ] Linear or better scaling
- [ ] 100 mappings < 500ms reload
- [ ] No exponential degradation

---

## Test 7: Throughput Testing

### Step 7.1: Sustained Request Rate

**Prompt:**
```
Make tool calls repeatedly for 1 minute:
- gateway_status every 5 seconds (12 calls)
- chora:list_generators every 30 seconds (2 calls)

Does performance degrade over time?
```

**Success Criteria:**
- [ ] Consistent performance throughout
- [ ] No degradation from first to last call
- [ ] All requests complete successfully

### Step 7.2: Burst Handling

**Prompt:**
```
Make 10 rapid tool calls in quick succession.
Do they all complete? Any failures?
```

**Success Criteria:**
- [ ] All requests processed
- [ ] May queue but no drops
- [ ] Recovery to normal after burst

---

## Test 8: Bottleneck Identification

### Step 8.1: Profile Call Chain

**Prompt:**
```
For a single chora:generate_content call, identify time spent in:
1. Gateway routing
2. JSON-RPC communication
3. Backend processing
4. Response serialization

Where is most time spent?
```

**Success Criteria:**
- [ ] Backend processing is dominant (expected)
- [ ] Gateway overhead < 10% of total
- [ ] Networking overhead < 5%

### Step 8.2: Optimization Opportunities

**Prompt:**
```
Based on performance testing, what are the slowest operations?
1. Event queries?
2. Config reloads?
3. Tool routing?
4. Backend communication?
```

**Success Criteria:**
- [ ] Bottlenecks identified
- [ ] Recommendations for optimization
- [ ] Performance baseline documented

---

**Test Suite:** Performance Validation
**Duration:** 15-20 minutes
**Metrics Collected:** Latency, throughput, memory, concurrency
**Status:** ✅ Performance characteristics validated

---

## Performance Summary

After completing all tests, compile a performance profile:

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Gateway overhead | < 1ms | ? ms | ?  |
| gateway_status latency | < 100ms | ? ms | ? |
| Event query (10 events) | < 200ms | ? ms | ? |
| Event query (1000 events) | < 2s | ? ms | ? |
| Config reload | < 100ms | ? ms | ? |
| Memory baseline | < 200MB | ? MB | ? |
| Memory under load | < 300MB | ? MB | ? |

## Next Steps

1. ✅ **All tests complete:** E2E test suite finished!
2. 📊 **Document results:** Create performance report
3. 🔧 **Optimize:** Address identified bottlenecks
4. 📈 **Monitor:** Track metrics in production

## Troubleshooting

**High latency:**
- Check backend health and response times
- Review network latency (if remote backends)
- Profile Python code for slow operations
- Consider caching frequently accessed data

**Memory growth:**
- Check for unclosed file handles
- Review event log retention settings
- Monitor for circular references
- Use memory profiler (memory_profiler)

**Poor concurrency:**
- Review asyncio implementation
- Check for blocking operations
- Consider connection pooling
- Monitor backend capacity
