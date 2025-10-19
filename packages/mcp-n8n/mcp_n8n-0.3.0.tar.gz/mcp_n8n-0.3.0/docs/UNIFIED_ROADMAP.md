# Unified Integration Roadmap: mcp-n8n + chora-composer

**Context:** Single developer, multi-instance Claude Code development
**Optimization:** Minimize context switching, maximize integration quality
**Timeline:** ~18-22 days of focused work (YOUR time, not calendar time)
**Includes:** 3-4 buffer days for debugging and iteration

---

## Premise

You're orchestrating both sides of this integration using different Claude Code instances:
- **mcp-n8n instance:** Gateway/orchestration work (Layer 3)
- **chora-composer instance:** Platform capability work (Layer 2)

**Key Constraint:** Context switching cost between instances, not coordination overhead

**Strategy:**
- Work in **sprints** with clear boundaries
- Complete one side fully before switching contexts
- Use specs (event schema) to prevent integration bugs
- Skip coordination bureaucracy (you're both teams)

---

## Table of Contents

1. [Sprint Overview](#sprint-overview)
2. [Sprint 1: Validation](#sprint-1-validation-2-3-days)
3. [Sprint 2: Chora Foundation](#sprint-2-chora-foundation-2-3-days)
4. [Sprint 3: Weekly Report Workflow](#sprint-3-weekly-report-workflow-4-5-days)
5. [Sprint 4: Chora Gateway Features](#sprint-4-chora-gateway-features-3-5-days)
6. [Sprint 5: Production Workflows](#sprint-5-production-workflows-4-5-days)
7. [Context Switching Protocol](#context-switching-protocol)
8. [Success Criteria](#success-criteria)

---

## Sprint Overview

```
Sprint 1 (mcp-n8n)        Sprint 2 (chora)         Sprint 3 (mcp-n8n)
    ↓                          ↓                         ↓
Validate integration    Implement v1.1.1      Build weekly report
Test current state      - Generator deps       - Credential check
Hello World workflow    - Event emission       - Event monitoring
Document needs          - Limits exposure      - Full workflow
                                                - Feedback doc
    ↓ CONTEXT SWITCH          ↓ CONTEXT SWITCH         ↓ CONTEXT SWITCH

Sprint 4 (chora)          Sprint 5 (mcp-n8n)
    ↓                          ↓
Implement v1.2.0        Production workflows
- Gateway context        - 3-5 templates
- Preview artifact       - Performance tuning
- Telemetry resource     - Documentation
                         - v0.3.0 release
```

**Total Estimated Time:** 18-22 days of focused work (includes 3-4 buffer days)

**Key Decision Points:**
- After Sprint 1: Proceed with v1.1.1 OR fix blockers
- After Sprint 3: Proceed with v1.2.0 OR simplify scope
- After Sprint 5: Production ready OR iterate

---

## Sprint 1: Validation (2-3 days)

**Context:** mcp-n8n instance
**Goal:** Validate that current mcp-n8n works with chora v1.1.0, document what's needed, define integration contracts

### Checklist

#### Day 1: Integration Smoke Tests

- [ ] **Deploy mcp-n8n locally**
  ```bash
  cd /Users/victorpiper/code/mcp-n8n
  git submodule update --init --recursive
  cd chora-composer
  git checkout v1.1.0  # Or current main
  cd ..
  pip install -e ".[dev]"
  ```

- [ ] **Test basic tool calls through gateway**
  - [ ] `chora:generate_content` - Does routing work?
  - [ ] `chora:assemble_artifact` - Does result come back correctly?
  - [ ] `coda:list_docs` - Does multi-backend routing work?
  - [ ] Document latency overhead (should be <10ms)

- [ ] **Identify integration issues**
  - [ ] Subprocess communication working?
  - [ ] Namespace routing correct?
  - [ ] Error messages surfaced properly?
  - [ ] Log any blockers

#### Day 2: Hello World Workflow

- [ ] **Set up n8n**
  ```bash
  npx n8n
  # Opens http://localhost:5678
  ```

- [ ] **Build simplest workflow**
  ```
  Manual Trigger
      ↓
  HTTP Request (fetch sample data from httpbin.org/json)
      ↓
  Function (format data for chora)
      ↓
  Execute Command: mcp-n8n call chora:assemble_artifact
      ↓
  Log output
  ```

- [ ] **Execute workflow**
  - [ ] Run manually in n8n UI
  - [ ] Verify artifact created
  - [ ] Measure end-to-end time (<30s target)
  - [ ] Export workflow JSON: `workflows/hello-world.json`

#### Day 3: Document Needs & Define Integration Contracts

- [ ] **Review event-schema.md**
  - [ ] Read `docs/process/specs/event-schema.md`
  - [ ] Does schema make sense for your use case?
  - [ ] Any fields missing?
  - [ ] Approve it (you're both teams!)

- [ ] **Define trace context propagation mechanism**
  - **Decision:** How will mcp-n8n pass trace_id to chora subprocess?
  - **Recommended:** Environment variable `CHORA_TRACE_ID`
  - **Document in:** `docs/process/specs/event-schema.md` (new section)
  - **Why now:** Prevents Sprint 3 debugging hell
  ```python
  # mcp-n8n will do:
  subprocess.run(
      ["chora-compose", "generate-content"],
      env={"CHORA_TRACE_ID": "abc123"}
  )

  # chora-compose will read:
  trace_id = os.getenv("CHORA_TRACE_ID", generate_trace_id())
  ```

- [ ] **Draft telemetry capabilities schema**
  - **File:** `docs/process/specs/telemetry-capabilities-schema.md` (NEW)
  - What should `capabilities://telemetry` return?
  - Schema for event types, sampling rate, export format
  - **Why now:** Prevents "I wish this had X" in Sprint 5

- [ ] **Write requirements for chora v1.1.1**
  - **File:** `docs/chora-v1.1.1-requirements.md`
  - What do you need from chora for Phase 1?
    - [ ] Generator dependency metadata format
    - [ ] Event emission format (matches event-schema.md)
    - [ ] Concurrency limits exposure
    - [ ] Trace context from environment variable
  - Example use cases (credential pre-validation, event monitoring)

- [ ] **Write submodule management guide**
  - **File:** `docs/SUBMODULE_MANAGEMENT.md`
  - How to update chora-composer submodule
  - How to test after updates
  - Compatibility matrix

### Sprint 1 Exit Criteria

- ✅ Integration tests pass with chora v1.1.0
- ✅ "Hello World" workflow works
- ✅ No blocking issues (or issues documented)
- ✅ Event schema approved
- ✅ Requirements for chora v1.1.1 documented
- ✅ Ready to switch to chora-composer instance

---

## Sprint 2: Chora Foundation (2-3 days)

**Context:** chora-composer instance
**Goal:** Implement v1.1.1 essentials (generator deps, events, limits) and validate integration

### Checklist

#### Day 1: Generator Dependencies & Limits

- [ ] **Read mcp-n8n requirements doc**
  - Review `docs/chora-v1.1.1-requirements.md` (from Sprint 1)
  - Understand what mcp-n8n needs

- [ ] **Add generator dependency metadata**
  - [ ] Update `GeneratorCapability` model in `src/chora_compose/mcp/types.py`
    ```python
    class GeneratorCapability(BaseModel):
        generator_type: str
        indicators: list[GeneratorIndicator]
        # NEW: Upstream dependencies
        upstream_dependencies: dict[str, Any] = Field(default_factory=dict)
    ```
  - [ ] Update all builtin generators with dependency metadata
    - `DemonstrationGenerator`: No external deps
    - `Jinja2Generator`: No external deps
    - `CodeGenerationGenerator`: `ANTHROPIC_API_KEY` required
    - `BDDScenarioGenerator`: No external deps
  - [ ] Update `capabilities://generators` resource provider
  - [ ] Tests: Validate dependency metadata present

- [ ] **Expose concurrency limits**
  - [ ] Add `limits` dict to `capabilities://server` response
    ```python
    {
      "limits": {
        "max_parallel_generations": 4,
        "max_concurrent_connections": 10,
        "max_artifact_size_bytes": 10_000_000
      }
    }
    ```
  - [ ] Source from config or defaults
  - [ ] Tests: Validate limits in capability response

#### Day 2: Event Emission with Trace Context

- [ ] **Implement event emission utility**
  - **File:** `src/chora_compose/telemetry/events.py`
  ```python
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
  ```

- [ ] **Implement trace context propagation**
  - [ ] Read trace_id from environment variable `CHORA_TRACE_ID`
  - [ ] Fall back to generated trace_id if not provided
  - [ ] Document in CLI help (`--trace-id` flag or env var)
  ```python
  import os
  import uuid

  def get_trace_id() -> str:
      """Get trace ID from environment or generate new one"""
      return os.getenv("CHORA_TRACE_ID", str(uuid.uuid4()))
  ```

- [ ] **Emit events from tools**
  - [ ] `generate_content`: Emit `chora.content_generated`
  - [ ] `assemble_artifact`: Emit `chora.artifact_assembled`
  - [ ] `validate_content`: Emit `chora.validation_completed`
  - [ ] Include trace_id from get_trace_id()

- [ ] **Tests**
  - [ ] Events written to file
  - [ ] Events match schema (validate against event-schema.md)
  - [ ] Trace context propagated correctly
  - [ ] Environment variable override works

#### Day 3: Integration Testing & Release

- [ ] **Integration checkpoint: Validate mcp-n8n can consume events**
  - **File:** `tests/integration/test_mcp_n8n_integration.py` (NEW)
  ```python
  import json
  from pathlib import Path

  def test_event_file_format():
      """Validate events.jsonl is parseable by mcp-n8n event watcher"""
      # Generate test event
      emit_event("chora.content_generated", trace_id="test123", status="success")

      # Mock mcp-n8n event parser
      event_file = Path("var/telemetry/events.jsonl")
      with event_file.open() as f:
          for line in f:
              event = json.loads(line)  # Should not throw

              # Validate required fields (from event-schema.md)
              assert "timestamp" in event
              assert "trace_id" in event
              assert "status" in event
              assert "schema_version" in event
              assert "event_type" in event

              # Validate field formats
              assert event["schema_version"] == "1.0"
              assert event["status"] in ["success", "failure", "pending", "cancelled"]
  ```

- [ ] **Why this matters:**
  - Catches integration issues BEFORE context switch
  - Validates event schema compliance
  - Prevents Sprint 3 debugging hell

- [ ] **Buffer time for edge cases**
  - File permissions on Mac vs. Linux
  - Append-only guarantees
  - Concurrent write handling
  - Event file rotation logic (if implemented)

- [ ] **Tag v1.1.1 ONLY after integration test passes**
  ```bash
  pytest tests/integration/test_mcp_n8n_integration.py
  # ✅ Pass

  git add .
  git commit -m "Add generator dependencies, event emission, limits exposure, trace context"
  git tag v1.1.1
  git push origin main --tags
  ```

### Sprint 2 Exit Criteria

- ✅ Generator dependency metadata in all generators
- ✅ Concurrency limits exposed via capabilities
- ✅ Events emitted to `var/telemetry/events.jsonl`
- ✅ Events match event-schema.md v1.0
- ✅ Trace context from `CHORA_TRACE_ID` environment variable working
- ✅ **Integration test passes** (mcp-n8n can parse events)
- ✅ Tests pass (>95% coverage maintained)
- ✅ v1.1.1 tagged and pushed
- ✅ Ready to switch back to mcp-n8n instance

### Sprint 2 Decision Point

**Proceed if:**
- ✅ All exit criteria met
- ✅ Integration test passes (critical!)
- ✅ No blocking bugs in event emission

**Adjust if:**
- ⚠️ Integration test fails → Debug before tagging v1.1.1
- ⚠️ Event emission has edge cases → Add Day 4 for fixes
- ⚠️ Trace context not working → Fix before switching contexts

**Abort if:**
- ❌ Fundamental issue with event file format → Redesign event-schema.md

---

## Sprint 3: Weekly Report Workflow (4-5 days)

**Context:** mcp-n8n instance
**Goal:** Build the "Weekly Engineering Report" workflow, validate integration
**Added Time:** +1 day for debugging workflow issues

### Checklist

#### Day 1: Credential Pre-Validation

- [ ] **Update chora-composer submodule to v1.1.1**
  ```bash
  cd chora-composer
  git fetch --tags
  git checkout v1.1.1
  cd ..
  git add chora-composer
  git commit -m "Update chora-composer to v1.1.1"
  ```

- [ ] **Implement credential checker**
  - **File:** `src/mcp_n8n/credential_validator.py`
  ```python
  async def validate_backend_credentials(backend: Backend) -> dict[str, bool]:
      """Check if required credentials are present"""
      capabilities = await backend.get_capabilities()
      generators = capabilities.get("generators", [])

      cred_status = {}
      for gen in generators:
          deps = gen.get("upstream_dependencies", {})
          for service, metadata in deps.items():
              if metadata.get("required"):
                  cred_name = metadata.get("credential")
                  cred_status[cred_name] = os.getenv(cred_name) is not None

      return cred_status
  ```

- [ ] **Add to gateway startup**
  - [ ] Validate credentials on backend start
  - [ ] Log warnings for missing credentials
  - [ ] Add credential status to `gateway_status` tool

- [ ] **Tests**
  - [ ] Missing credentials detected
  - [ ] Gateway status shows credential state
  - [ ] Tool calls fail fast with clear errors

#### Day 2: Event Monitoring with Trace Propagation

- [ ] **Implement event watcher**
  - **File:** `src/mcp_n8n/event_watcher.py`
  ```python
  async def watch_events(event_file: Path, handler: Callable):
      """Tail events file and handle new events"""
      with event_file.open("r") as f:
          f.seek(0, 2)  # Seek to end

          while True:
              line = f.readline()
              if not line:
                  await asyncio.sleep(0.1)
                  continue

              event = json.loads(line)
              await handler(event)
  ```

- [ ] **Implement trace context propagation to backend**
  - [ ] Generate trace_id for each incoming request
  - [ ] Pass `CHORA_TRACE_ID` environment variable when spawning subprocess
  ```python
  # In backend subprocess spawn:
  trace_id = generate_trace_id()
  subprocess.run(
      ["chora-compose", "generate-content"],
      env={
          **os.environ,
          "CHORA_TRACE_ID": trace_id
      }
  )
  ```
  - [ ] Verify backend events include correct trace_id

- [ ] **Implement event correlation**
  - [ ] Map trace_id to original request
  - [ ] Detect artifact completion events
  - [ ] Forward events to gateway telemetry

- [ ] **Tests**
  - [ ] Event file watching works
  - [ ] Trace_id propagation to backend works
  - [ ] Event correlation by trace_id
  - [ ] Gateway telemetry includes backend events

#### Day 3-4: Simple Report Workflow (De-Risk)

- [ ] **Build "Simple GitHub Report" workflow**
  ```
  Schedule (daily)
      ↓
  GitHub API: Fetch commits (last 24h)
      ↓
  chora:generate_content(template="daily-commits", context={commits})
      ↓
  chora:assemble_artifact(config="daily-report")
      ↓
  Log output (or Slack notification)
  ```

- [ ] **Create chora templates**
  - **File:** `chora-composer/configs/daily-commits.yaml`
  - **File:** `chora-composer/configs/daily-report.yaml`
  - Simple templates with minimal complexity

- [ ] **Test workflow**
  - [ ] Run manually 3 times
  - [ ] Verify report generated correctly
  - [ ] Measure latency (target <60s)
  - [ ] Export workflow: `workflows/simple-daily-report.json`

#### Day 5: Full Weekly Report Workflow

- [ ] **Build "Weekly Engineering Report" workflow**
  ```
  Schedule (Monday 9am)
      ↓
  Parallel:
    ├─ GitHub API: Fetch commits (last 7 days)
    ├─ Jira API: Fetch closed tickets (last 7 days)
    └─ Mock DataDog data (or real if available)
      ↓
  Aggregate data
      ↓
  chora:generate_content(template="report-intro", context={...})
      ↓
  chora:generate_content(template="github-summary", context={...})
      ↓
  chora:generate_content(template="jira-summary", context={...})
      ↓
  chora:assemble_artifact(config="weekly-eng-report")
      ↓
  coda:create_row (if Coda available, else skip)
      ↓
  Log output (or Slack notification)
  ```

- [ ] **Create chora templates**
  - [ ] `chora-composer/configs/weekly-report-intro.yaml`
  - [ ] `chora-composer/configs/weekly-report-github.yaml`
  - [ ] `chora-composer/configs/weekly-report-jira.yaml`
  - [ ] `chora-composer/configs/weekly-report.yaml` (main config)

- [ ] **Test workflow**
  - [ ] Run manually
  - [ ] Debug and fix issues
  - [ ] Run 3 times to validate consistency
  - [ ] Measure performance:
    - Total execution time
    - Per-step latency
    - Resource usage
  - [ ] Export workflow: `workflows/weekly-engineering-report.json`

#### Day 5 (Evening): Feedback Document

- [ ] **Write feedback for chora v1.2.0**
  - **File:** `docs/chora-v1.2.0-feedback.md`
  - What worked well?
  - What was painful?
  - What do you wish chora had?
    - Gateway context parameter (`?context=gateway`)?
    - Preview artifact tool?
    - Better telemetry discovery?
  - Specific feature requests with use cases

### Sprint 3 Exit Criteria

- ✅ Credential validation working
- ✅ Event monitoring functional
- ✅ Trace_id correlation working end-to-end
- ✅ "Simple GitHub Report" workflow works
- ✅ "Weekly Engineering Report" workflow complete
- ✅ Performance acceptable (<2 minutes end-to-end)
- ✅ Feedback document written
- ✅ mcp-n8n v0.2.0 tagged
- ✅ Ready to switch to chora-composer for v1.2.0

### Sprint 3 Decision Point

**Proceed if:**
- ✅ All exit criteria met
- ✅ Weekly report workflow runs successfully 3+ times
- ✅ Feedback document has clear v1.2.0 feature requests

**Adjust if:**
- ⚠️ Weekly report too complex → Use "Simple GitHub Report" as primary deliverable
- ⚠️ Performance issues → Add performance sprint before v1.2.0
- ⚠️ Event correlation flaky → Fix before switching contexts

**Abort if:**
- ❌ Fundamental orchestration problem → Revisit gateway architecture

---

## Sprint 4: Chora Gateway Features (3-5 days)

**Context:** chora-composer instance
**Goal:** Implement v1.2.0 gateway-aware features (context param, preview, telemetry)

### Checklist

#### Day 1: Gateway-Aware Capabilities

- [ ] **Read mcp-n8n feedback doc**
  - Review `docs/chora-v1.2.0-feedback.md` (from Sprint 3)
  - Prioritize requests

- [ ] **Implement `?context=gateway` parameter**
  - [ ] Update capability resource providers
    ```python
    async def get_capabilities(context: str = "direct"):
        if context == "gateway":
            # Return gateway-optimized view
            return filter_local_only_features(capabilities)
        else:
            # Return full capabilities
            return capabilities
    ```
  - [ ] Filter out local-only features in gateway view
    - Hide local file paths
    - Exclude debug/internal tools
    - Include concurrency hints
  - [ ] Tests: Validate gateway vs. direct views differ

#### Day 2: Preview Artifact Tool

- [ ] **Implement `preview_artifact` tool**
  - Similar to `test_config` pattern
  - Returns diff of what will change without writing files
  - **File:** `src/chora_compose/mcp/tools/preview_artifact.py`
  ```python
  async def preview_artifact(
      artifact_config_id: str,
      context: dict[str, Any]
  ) -> dict[str, Any]:
      """Show what will change without writing files"""
      # Load config
      # Generate sections
      # Compute diffs
      # Return preview result
      return {
          "sections": [
              {
                  "section_id": "intro",
                  "action": "add",  # or "modify", "delete"
                  "estimated_size_bytes": 1024,
                  "preview": "First 200 chars..."
              }
          ],
          "total_estimated_size_bytes": 5120
      }
  ```

- [ ] **Tests**
  - [ ] Preview returns accurate diff
  - [ ] Preview does not write files
  - [ ] Subsequent `assemble_artifact` matches preview

#### Day 3: Telemetry Capabilities Resource

- [ ] **Implement `capabilities://telemetry` resource**
  - **File:** `src/chora_compose/mcp/resources/telemetry.py`
  ```python
  async def get_telemetry_capabilities() -> dict[str, Any]:
      return {
          "event_types": [
              {
                  "name": "chora.content_generated",
                  "schema": {...},
                  "frequency": "per_operation"
              },
              {
                  "name": "chora.artifact_assembled",
                  "schema": {...},
                  "frequency": "per_operation"
              }
          ],
          "sampling_rate": 1.0,
          "export_format": "jsonl",
          "export_location": "var/telemetry/events.jsonl"
      }
  ```

- [ ] **Tests**
  - [ ] Resource returns event catalog
  - [ ] Schemas match event-schema.md

#### Day 4-5: Documentation & Release

- [ ] **Update documentation**
  - [ ] CHANGELOG.md: Document v1.2.0 changes
  - [ ] README.md: Mention gateway features
  - [ ] API reference: Document new tools/resources

- [ ] **Tag v1.2.0**
  ```bash
  git add .
  git commit -m "Add gateway-aware capabilities, preview_artifact, telemetry resource"
  git tag v1.2.0
  git push origin main --tags
  ```

### Sprint 4 Exit Criteria

- ✅ Gateway context parameter working
- ✅ `preview_artifact` tool implemented
- ✅ `capabilities://telemetry` resource available
- ✅ Tests pass (>95% coverage)
- ✅ Documentation updated
- ✅ v1.2.0 tagged and pushed
- ✅ Ready to switch back to mcp-n8n for production workflows

### Sprint 4 Decision Point

**Proceed if:**
- ✅ All exit criteria met
- ✅ Gateway-aware capabilities demonstrably different from direct
- ✅ `preview_artifact` accurately predicts assembly output

**Adjust if:**
- ⚠️ Gateway context not providing value → Make it optional feature
- ⚠️ Preview artifact diff inaccurate → Simplify to size estimation only

**Abort if:**
- ❌ Breaking changes needed in v1.2.0 → Bump to v2.0.0 instead

---

## Sprint 5: Production Workflows (4-5 days)

**Context:** mcp-n8n instance
**Goal:** Build 3-5 production workflow templates, optimize performance
**Added Time:** +1 day for performance tuning

### Checklist

#### Day 1: Update & Context-Aware Routing

- [ ] **Update chora-composer submodule to v1.2.0**
  ```bash
  cd chora-composer
  git fetch --tags
  git checkout v1.2.0
  cd ..
  git add chora-composer
  git commit -m "Update chora-composer to v1.2.0"
  ```

- [ ] **Implement context-aware discovery**
  - [ ] Update backend initialization to request gateway context
    ```python
    capabilities = await backend.get_capabilities(context="gateway")
    ```
  - [ ] Use concurrency limits for routing decisions
  - [ ] Filter local-only tools from gateway tool list

- [ ] **Tests**
  - [ ] Gateway receives optimized capabilities
  - [ ] Local-only features hidden
  - [ ] Routing respects concurrency limits

#### Day 2: Preview Workflow Pattern

- [ ] **Add preview to Weekly Report workflow**
  ```
  [Data Gathering] → [Generate Sections]
      ↓
  chora:preview_artifact(config="weekly-report")
      ↓
  Log preview (show diff)
      ↓
  Manual approval (or auto-approve for now)
      ↓
  chora:assemble_artifact(...)
  ```

- [ ] **Test preview accuracy**
  - [ ] Preview diff matches actual assembly
  - [ ] No unwanted artifacts created

#### Day 3-4: Build 3 Production Workflows

**Workflow 1: Event-Driven Documentation Updates**
```
GitHub Webhook (PR merged, /docs files changed)
    ↓
Extract changed files
    ↓
chora:preview_artifact(config="api-docs")
    ↓
Log preview (or post as GitHub comment)
    ↓
chora:assemble_artifact(config="api-docs")
    ↓
Create PR with updated docs
```

**Workflow 2: Daily Standup Notes**
```
Schedule (daily 8am)
    ↓
GitHub API: Yesterday's commits
    ↓
Jira API: Tickets updated yesterday
    ↓
chora:generate_content(template="standup-notes")
    ↓
chora:assemble_artifact(config="daily-standup")
    ↓
Post to Slack #standup
```

**Workflow 3: Customer Onboarding (Simplified)**
```
Manual Trigger (when new customer signs up)
    ↓
Input: customer name, email
    ↓
chora:generate_content(template="welcome-letter", context={...})
    ↓
chora:assemble_artifact(config="onboarding-guide")
    ↓
Log output (or email if SendGrid available)
```

- [ ] **Build each workflow**
- [ ] **Test with real/mock data**
- [ ] **Export workflow JSONs** to `workflows/`
- [ ] **Document setup** in `docs/workflows/`

#### Day 5: Performance & Release

- [ ] **Performance optimization**
  - [ ] Capability caching (reduce startup time)
  - [ ] Connection pooling (persistent subprocess connections?)
  - [ ] Benchmark: Gateway overhead <10ms p95

- [ ] **Documentation**
  - [ ] Update README.md with workflow examples
  - [ ] Production deployment guide
  - [ ] Troubleshooting guide

- [ ] **Tag mcp-n8n v0.3.0**
  ```bash
  git add .
  git commit -m "Add production workflows, preview patterns, performance optimizations"
  git tag v0.3.0
  git push origin main --tags
  ```

### Sprint 5 Exit Criteria

- ✅ Context-aware routing implemented
- ✅ Preview workflows validated
- ✅ 3+ production workflow templates
- ✅ Performance targets met (<10ms routing overhead)
- ✅ Documentation complete
- ✅ mcp-n8n v0.3.0 tagged
- ✅ **PRODUCTION READY**

### Sprint 5 Decision Point

**Proceed if:**
- ✅ All exit criteria met
- ✅ 3+ workflows run successfully in production environment
- ✅ Performance acceptable for expected load

**Adjust if:**
- ⚠️ Only 1-2 workflows working → Tag v0.3.0-rc, iterate on workflows
- ⚠️ Performance issues → Add Sprint 6 for optimization
- ⚠️ Documentation incomplete → Delay release, finish docs

**Celebrate if:**
- ✅ All criteria exceeded
- ✅ Ready for Phase 3 (advanced patterns)

---

## Context Switching Protocol

### Before Switching Contexts

1. **Commit all work**
   ```bash
   git add .
   git commit -m "Sprint X: [description]"
   git push origin main
   ```

2. **Tag if at major milestone**
   ```bash
   git tag vX.Y.Z
   git push origin --tags
   ```

3. **Write handoff note**
   - **File:** `SPRINT_HANDOFF.md` (in each repo)
   - What was completed
   - What's next for the other instance
   - Any blockers or questions

4. **Close all files in IDE**
   - Clear mental context
   - Prevents accidental edits in wrong repo

### When Resuming Context

1. **Pull latest changes**
   ```bash
   git pull origin main
   git fetch --tags
   ```

2. **Read handoff note**
   - Review `SPRINT_HANDOFF.md`
   - Understand what the other instance did

3. **Update submodules if needed** (for mcp-n8n)
   ```bash
   git submodule update --remote chora-composer
   ```

4. **Run smoke tests**
   - Verify nothing broke
   - Quick integration test

---

## Success Criteria

### Overall Success (End of Sprint 5)

- ✅ **Integration Works:** mcp-n8n gateway successfully routes to chora-composer
- ✅ **Real Workflows:** 3+ production-ready workflow templates
- ✅ **Event Monitoring:** Gateway can correlate backend events via trace_id
- ✅ **Preview Pattern:** Workflows can preview before creating artifacts
- ✅ **Performance:** Gateway overhead <10ms p95, workflows complete <2 min
- ✅ **Documentation:** Complete setup guides, workflow docs, troubleshooting
- ✅ **Releases:** chora v1.2.0 + mcp-n8n v0.3.0 tagged and working together

### Sprint-Level Success

**Sprint 1:**
- Integration validated, no blockers, event schema approved

**Sprint 2:**
- chora v1.1.1 released with generator deps, events, limits

**Sprint 3:**
- Weekly report workflow working, feedback doc written

**Sprint 4:**
- chora v1.2.0 released with gateway features

**Sprint 5:**
- mcp-n8n v0.3.0 released, production ready

---

## Quick Reference

### File Locations

**mcp-n8n:**
- Main roadmap: `docs/ROADMAP.md` (original, detailed)
- This roadmap: `docs/UNIFIED_ROADMAP.md` (simplified, single-dev)
- Event schema: `docs/process/specs/event-schema.md`
- Workflows: `workflows/*.json`
- Submodule: `chora-composer/` (git submodule)

**chora-composer:**
- Generator code: `src/chora_compose/generators/`
- MCP tools: `src/chora_compose/mcp/tools/`
- Capability resources: `src/chora_compose/mcp/resources/`
- Configs: `configs/*.yaml`
- Events: `var/telemetry/events.jsonl`

### Key Commands

**Update chora submodule in mcp-n8n:**
```bash
cd /Users/victorpiper/code/mcp-n8n
git submodule update --remote chora-composer
cd chora-composer
git checkout v1.1.1  # or v1.2.0
cd ..
git add chora-composer
git commit -m "Update chora-composer to v1.1.1"
```

**Run mcp-n8n gateway:**
```bash
cd /Users/victorpiper/code/mcp-n8n
source .venv/bin/activate
mcp-n8n
```

**Run n8n:**
```bash
npx n8n
# Opens http://localhost:5678
```

**Test chora tool directly:**
```bash
cd /Users/victorpiper/code/mcp-n8n/chora-composer
chora-compose generate-content --config daily-commits
```

---

## Appendix: Differences from Original Roadmap

| Aspect | Original (2-Team) | Unified (1-Dev) |
|--------|------------------|-----------------|
| **Timeline** | Calendar weeks (14 weeks) | Sprints (~15 days YOUR time) |
| **Coordination** | Weekly meetings, formal approvals | Context switching protocol |
| **Parallelism** | Teams work in parallel | Sequential sprints |
| **Releases** | Beta/RC ceremonies | Tag when ready |
| **Approvals** | "Team A reviews, Team B approves" | "You approve as you switch contexts" |
| **Feedback Loops** | Formal feedback documents | Handoff notes between sprints |
| **Risk** | Timeline coupling, coordination | Context switching cost |
| **Optimization** | Minimize dependencies | Minimize context switches |

**Key Insight:** Original roadmap optimized for team coordination. This optimizes for single-developer context switching.

---

## Document Metadata

**Version:** 1.0.0
**Status:** Active
**Last Updated:** 2025-10-17
**Next Review:** After Sprint 1 (validate approach)
**Owner:** You (both instances)

**Related Documents:**
- [docs/ROADMAP.md](ROADMAP.md) - Original detailed roadmap (reference)
- [docs/process/specs/event-schema.md](process/specs/event-schema.md) - Event schema specification
- [docs/process/CROSS_TEAM_COORDINATION.md](process/CROSS_TEAM_COORDINATION.md) - Original coordination doc (mostly irrelevant for single-dev)

**Change Log:**
- 2025-10-17: Initial version optimized for single-developer multi-instance workflow
