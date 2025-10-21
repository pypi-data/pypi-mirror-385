# Chora-Compose + mcp-n8n Roadmap Alignment Analysis

**Date:** 2025-10-18 (Updated)
**mcp-n8n Version:** v0.2.0
**chora-compose Version:** v1.3.0 ✅
**Status:** ✅ RESOLVED - All Features Delivered

---

## Executive Summary

**UPDATE (2025-10-18):** ✅ **ALL BLOCKERS REMOVED**

chora-compose v1.3.0 has been released with **100% of expected Sprint 1 features** from the UNIFIED_ROADMAP. All critical integration features are now available:

- ✅ Event emission to `var/telemetry/events.jsonl`
- ✅ Trace context propagation (`CHORA_TRACE_ID`)
- ✅ Generator dependency metadata (`upstream_dependencies`)
- ✅ Concurrency limits exposure

**Previous State (v1.2.1):** Critical integration features were missing, blocking mcp-n8n Phase 1.

**Current State (v1.3.0):** All features delivered with comprehensive testing (48 new tests) and documentation (2,500+ lines).

**Recommendation:** **INTEGRATE IMMEDIATELY** - Proceed to mcp-n8n Sprint 2 (Phase 0 validation workflow).

---

## Resolution Summary (v1.3.0)

### What Was Delivered

**Sprint 1 Complete (6 days, 2025-10-13 to 2025-10-18):**
1. ✅ Generator Dependencies (Day 1)
2. ✅ Event Emission & Trace Context (Day 2-3)
3. ✅ Concurrency Limits (Day 4)
4. ✅ Integration Tests + Documentation (Day 5-6)

**Test Coverage:** 48 new tests (42 unit + 6 integration) - ALL PASSING
**Documentation:** 2,500+ lines of API reference and how-to guides
**Backward Compatibility:** 100% - no breaking changes

See [CHORA_V1_3_0_REVIEW.md](CHORA_V1_3_0_REVIEW.md) for detailed analysis.

---

## Original Analysis (v1.2.1) - ARCHIVED

---

## Current State Comparison

### chora-compose v1.2.1 (Released 2025-10-17)

**Delivered:**
- ✅ 13 MCP tools (down from documented 17 in v1.2.0)
- ✅ 5 MCP resources (capabilities://)
- ✅ Agent documentation (AGENTS.md - 1,418 lines)
- ✅ 384/384 tests passing (100%)
- ✅ CLI entry point (`chora-compose`)
- ✅ Complete branding (HAWF → Chora Compose)

**NOT Delivered (per UNIFIED_ROADMAP Sprint 2 expectations):**
- ❌ Event emission to `var/telemetry/events.jsonl`
- ❌ Trace context propagation (`CHORA_TRACE_ID` environment variable)
- ❌ Generator dependency metadata (`upstream_dependencies` field)
- ❌ Concurrency limits exposure in capabilities
- ❌ Telemetry capabilities resource (`capabilities://telemetry`)

**Evidence:**
```bash
# Searched chora-compose v1.2.1 codebase:
grep -r "emit_event\|events\.jsonl" src/     # NO MATCHES
grep -r "TRACE_ID\|trace_context" src/       # NO MATCHES
grep -r "upstream_dependencies" src/          # NO MATCHES
```

### mcp-n8n v0.2.0 (Released 2025-10-17)

**Delivered:**
- ✅ Phase 0 validation (19/21 integration tests passing)
- ✅ Performance baseline (2500x faster than targets)
- ✅ Agent infrastructure (AGENTS.md, memory system, CLI tools)
- ✅ Gateway integration with chora-compose v1.1.0
- ✅ Environment configuration improvements

**Blocked Features (waiting on chora-compose):**
- ⏳ Event monitoring foundation (Phase 1 Week 5)
- ⏳ "Weekly Engineering Report" workflow (Phase 1 Week 6)
- ⏳ Event correlation by trace_id
- ⏳ Backend telemetry integration

---

## UNIFIED_ROADMAP vs Actual Progress

| Planned (UNIFIED_ROADMAP) | Expected Version | Actual | Status | Impact |
|----------------------------|------------------|---------|--------|---------|
| **Sprint 1: Gateway Validation** | mcp-n8n v0.1.0 | v0.2.0 | ✅ **EXCEEDED** | None |
| **Sprint 2: Chora Foundation** | chora v1.1.1 | v1.2.1 | ❌ **MISSING FEATURES** | **BLOCKING** |
| **Sprint 3: Weekly Report** | mcp-n8n v0.2.0 | - | ⏳ **BLOCKED** | High |
| **Sprint 4: Gateway Features** | chora v1.2.0 | - | ⏳ **PENDING** | Medium |

### Sprint 2 Expected Features (chora-compose v1.1.1)

Per `docs/UNIFIED_ROADMAP.md` Sprint 2 (Days 1-3):

**Day 1: Generator Dependencies & Limits**
```python
# Expected in GeneratorCapability model:
class GeneratorCapability(BaseModel):
    generator_type: str
    indicators: list[GeneratorIndicator]
    upstream_dependencies: dict[str, Any] = Field(default_factory=dict)  # MISSING

# Expected in capabilities://server response:
{
  "limits": {
    "max_parallel_generations": 4,
    "max_concurrent_connections": 10,
    "max_artifact_size_bytes": 10_000_000
  }
}
```

**Day 2: Event Emission with Trace Context**
```python
# Expected implementation:
def emit_event(event_type: str, trace_id: str, status: str, **metadata):
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": trace_id,
        "status": status,
        "schema_version": "1.0",
        "event_type": event_type,
        **metadata
    }

    event_file = Path("var/telemetry/events.jsonl")
    event_file.parent.mkdir(parents=True, exist_ok=True)

    with event_file.open("a") as f:
        f.write(json.dumps(event) + "\n")

# Expected trace context:
trace_id = os.getenv("CHORA_TRACE_ID", str(uuid.uuid4()))
```

**Day 3: Integration Testing**
- Events emitted from `generate_content` and `assemble_artifact`
- Integration test validates mcp-n8n can parse events
- Tag v1.1.1 after integration test passes

**Actual:** None of this was implemented in v1.2.0 or v1.2.1.

---

## Impact Analysis

### Phase 1 Blockers (mcp-n8n)

**Week 3: Credential Pre-Validation**
- **Status:** ⚠️ Partially blocked
- **Missing:** Generator dependency metadata to detect required credentials
- **Workaround:** Can implement using hardcoded knowledge of generators

**Week 5: Event Monitoring Foundation**
- **Status:** ❌ Fully blocked
- **Missing:** Event emission from chora-compose
- **Impact:** Cannot implement event watcher, cannot correlate requests

**Week 6: "Weekly Engineering Report" Workflow**
- **Status:** ❌ Fully blocked
- **Missing:** Event monitoring foundation
- **Impact:** Cannot validate Pattern N5 workflow, cannot demonstrate value

**Phase 1 Exit Criteria:**
- ❌ **Cannot meet** - Weekly Engineering Report workflow is critical deliverable
- ❌ **Cannot deliver feedback** to chora team for v1.2.0 design (already released)

### Coordination Overhead

**Without Event Emission:**
- mcp-n8n must implement gateway-level event wrapping (Option 3)
- Duplicates effort when chora-compose eventually adds events
- Diverges from UNIFIED_ROADMAP vision
- Events only at gateway level (missing backend internal events)

**With Event Emission:**
- Full event correlation across gateway → backend boundary
- Enables rich telemetry and debugging
- Aligns with original roadmap design
- Minimal implementation effort (2-3 hours based on mcp-n8n memory system)

---

## Recommended Path Forward

### Option 1: chora-compose v1.3.0 - Event & Telemetry Features (RECOMMENDED)

**Approach:** Coordinate on v1.3.0 release with event emission and trace context

**Features to Add:**

1. **Event Emission Utility** (`src/chora_compose/telemetry/events.py`)
   ```python
   def emit_event(event_type: str, trace_id: str, status: str, **metadata):
       """Emit event to var/telemetry/events.jsonl with event schema v1.0."""
       # ~30 lines of code
   ```

2. **Trace Context Propagation**
   ```python
   import os, uuid

   def get_trace_id() -> str:
       """Get trace ID from environment or generate new one."""
       return os.getenv("CHORA_TRACE_ID", str(uuid.uuid4()))
   ```

3. **Event Emission from Tools**
   - Emit `chora.content_generated` from `generate_content`
   - Emit `chora.artifact_assembled` from `assemble_artifact`
   - Emit `chora.validation_completed` from `validate_content`

4. **Generator Dependency Metadata**
   ```python
   # In GeneratorCapability model:
   upstream_dependencies: dict[str, Any] = Field(default_factory=dict)

   # Example for CodeGenerationGenerator:
   {
       "anthropic_api": {
           "required": True,
           "credential": "ANTHROPIC_API_KEY",
           "description": "Anthropic API for Claude Code Generation"
       }
   }
   ```

5. **Telemetry Capabilities Resource** (`capabilities://telemetry`)
   ```python
   async def get_telemetry_capabilities() -> dict[str, Any]:
       return {
           "event_types": [
               {"name": "chora.content_generated", "schema": {...}},
               {"name": "chora.artifact_assembled", "schema": {...}}
           ],
           "export_format": "jsonl",
           "export_location": "var/telemetry/events.jsonl"
       }
   ```

**Estimated Effort:** 4-6 hours

**Benefits:**
- ✅ Unblocks mcp-n8n Phase 1 completely
- ✅ Enables "Weekly Engineering Report" workflow
- ✅ Aligns with UNIFIED_ROADMAP vision
- ✅ Minimal scope (feature addition, not refactor)
- ✅ Provides value to all chora-compose users

**Timeline:**
- Week 1: Implement features in chora-compose
- Week 2: Integration testing with mcp-n8n
- Week 3: Release v1.3.0 + update mcp-n8n to v0.3.0

---

### Option 2: Gateway-Level Event Wrapping (mcp-n8n Only)

**Approach:** Add event emission in mcp-n8n's backend integration layer

**Implementation:**
```python
# In mcp-n8n: src/mcp_n8n/backends/chora_composer.py
class ChoraComposerBackend(StdioSubprocessBackend):
    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        trace_id = get_trace_id()
        emit_event("chora.tool_call.started", trace_id, "pending", tool=tool_name)

        result = await super().call_tool(tool_name, arguments)

        emit_event("chora.tool_call.completed", trace_id, "success", tool=tool_name)
        return result
```

**Estimated Effort:** 2-3 hours

**Benefits:**
- ✅ No dependency on chora-compose changes
- ✅ Can proceed with Phase 1 immediately
- ✅ Full control over event schema

**Drawbacks:**
- ❌ Events only at gateway level (not backend internal events)
- ❌ Diverges from UNIFIED_ROADMAP vision
- ❌ May duplicate effort when chora-compose adds events later
- ❌ Harder to debug chora-compose issues (no internal events)

---

### Option 3: Defer Phase 1, Skip to Phase 2

**Approach:** Accept roadmap divergence, work on other features

**mcp-n8n adjusts to:**
- Skip Sprint 3 (Weekly Engineering Report)
- Move to Phase 1 Week 3-4 (credential validation, gateway discovery)
- Defer event monitoring to Phase 2

**Benefits:**
- ✅ No coordination overhead
- ✅ Can proceed with available features
- ✅ chora-compose continues independent development

**Drawbacks:**
- ❌ Cannot build Strategic Focus workflow ("Weekly Engineering Report")
- ❌ Event correlation blocked indefinitely
- ❌ Roadmap divergence continues to grow
- ❌ Reduces value of UNIFIED_ROADMAP as coordination tool

---

## Proposal: Coordinate on v1.3.0

### For chora-compose Team

**Requested Features (v1.3.0):**
1. Event emission utility (~30 lines)
2. Trace context propagation (~10 lines)
3. Event emission from tools (~50 lines total)
4. Generator dependency metadata (~20 lines per generator)
5. Telemetry capabilities resource (~40 lines)

**Total Estimated Effort:** 4-6 hours

**Value Proposition:**
- Enables ecosystem integration (mcp-n8n gateway)
- Provides telemetry for all users
- Aligns with platform vision (observability)
- Minimal implementation cost
- Follows event schema v1.0 standard

### For mcp-n8n Team

**Waiting Period:** 1-2 weeks for chora-compose v1.3.0

**Work During Wait:**
- Complete Phase 0 Week 2 (submodule management docs)
- Implement Phase 1 Week 3-4 (credential validation, gateway discovery)
- Prepare event monitoring code (ready to activate when v1.3.0 releases)
- Begin n8n integration guide

**After v1.3.0 Release:**
- Update to chora-compose v1.3.0
- Complete Phase 1 Week 5-6 (event monitoring, weekly report)
- Release mcp-n8n v0.3.0 with full Phase 1 capabilities

---

## Next Steps

### Immediate (This Week)

**chora-compose:**
1. ☐ Review this alignment document
2. ☐ Decide on Option 1 (v1.3.0) vs other approach
3. ☐ If v1.3.0: Create issue for event emission features
4. ☐ Provide timeline estimate

**mcp-n8n:**
1. ☐ Share this document with chora-compose team
2. ☐ Wait for response (1-2 days)
3. ☐ If v1.3.0 confirmed: Proceed with Phase 1 Week 3-4
4. ☐ If blocked: Implement Option 2 (gateway-level wrapping)

### Coordination

**Communication:**
- GitHub issue in chora-compose repo: "Event emission for gateway integration"
- Reference this document and UNIFIED_ROADMAP.md
- Link to mcp-n8n event schema examples

**Success Criteria:**
- ✅ Event emission working in chora-compose v1.3.0
- ✅ Integration tests passing in both repos
- ✅ "Weekly Engineering Report" workflow validated
- ✅ Roadmap realignment documented

---

## Appendix: Event Schema v1.0

### Event: `chora.content_generated`

```json
{
  "timestamp": "2025-10-17T12:00:00Z",
  "trace_id": "abc123-def456",
  "status": "success",
  "schema_version": "1.0",
  "event_type": "chora.content_generated",
  "content_config_id": "welcome-message",
  "generator_type": "jinja2",
  "duration_ms": 45,
  "content_size_bytes": 1234
}
```

### Event: `chora.artifact_assembled`

```json
{
  "timestamp": "2025-10-17T12:00:05Z",
  "trace_id": "abc123-def456",
  "status": "success",
  "schema_version": "1.0",
  "event_type": "chora.artifact_assembled",
  "artifact_config_id": "weekly-report",
  "section_count": 4,
  "duration_ms": 123,
  "artifact_size_bytes": 5678,
  "output_path": "output/weekly-report-2025-10-17.md"
}
```

### Event: `chora.validation_completed`

```json
{
  "timestamp": "2025-10-17T12:00:03Z",
  "trace_id": "abc123-def456",
  "status": "failure",
  "schema_version": "1.0",
  "event_type": "chora.validation_completed",
  "config_type": "content",
  "config_id": "invalid-config",
  "errors": ["Missing required field: generator_type"]
}
```

---

**Status:** ⏳ Awaiting chora-compose team response
**Next Review:** After decision on v1.3.0 timeline
**Contact:** victor@example.com (mcp-n8n maintainer)
