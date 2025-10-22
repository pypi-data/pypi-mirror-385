# Production Workflows for Sprint 5

**Change Request ID:** sprint-5-workflows
**Type:** Feature (New Capability)
**Status:** Ready for DDD
**Sprint:** Sprint 5 (Production Workflows)
**Estimated Effort:** 6.5-7.5 days
**Priority:** High (production readiness)

---

## Business Context

### Problem Statement

Sprint 5 delivers **production-ready workflow infrastructure** to demonstrate the value of the mcp-n8n gateway with real-world automation. We need:
- Event-driven workflow orchestration (events trigger n8n workflows automatically)
- Template-based report generation (using chora-compose correctly as template engine)
- Dynamic configuration (hot-reloadable mappings without restart)
- Self-documenting workflows (virtuous cycle of generated documentation)

**Current Situation:**
- ✅ Sprint 3 complete: EventLog + EventWatcher + get_events MCP tool
- ✅ chora-compose v1.4.2 integrated via PyPI (NOT submodules)
- ✅ Architecture clarified: chora-compose is template engine, NOT storage system
- ✅ n8n ready for integration (Pattern N3: n8n as MCP client)
- ❌ No event-to-workflow routing infrastructure
- ❌ No chora-compose template configs in mcp-n8n repo
- ❌ No production workflow examples

**Critical Architectural Understanding** (from [docs/architecture/n8n-chora-compose-integration.md](../../architecture/n8n-chora-compose-integration.md)):
- chora-compose is a **template engine** (like Jinja2/Flask), NOT a storage system
- Templates and configs belong in **YOUR project** (mcp-n8n), not chora-compose
- Current version (v1.4.2) uses **Jinja2Generator** only (NO LLM integration)
- Ephemeral storage is for **generated content output**, not user data storage
- Use `generate_content` for single templates (NOT `assemble_artifact`)

### Success Metrics

**Sprint 5 Must Demonstrate:**
1. ✅ 1+ working workflow (Daily Report) with real git + event data
2. ✅ EventWorkflowRouter matches events → workflows from YAML config
3. ✅ chora-compose renders templates from `chora-configs/` directory
4. ✅ Config hot-reload (modify YAML, router reloads without restart)
5. ✅ End-to-end: Event → Router → n8n → chora:generate_content → Output
6. ✅ 20+ tests (unit + integration) with ≥85% coverage

**Long-term Value:**
- Foundation for all production workflows (Sprint 6+)
- Proven event-driven architecture
- Self-service workflow authoring (YAML configs, no code)
- Correct chora-compose integration pattern (reusable across ecosystem)

### Why This Approach?

**Separation of Concerns:**
- **Storage:** Git (workflow definitions, event mappings, templates)
- **Orchestration:** n8n (workflow execution, data gathering)
- **Formatting:** chora-compose (template rendering, report generation)
- **Routing:** EventWorkflowRouter (event → workflow mapping)

**Configuration-Driven:**
- Event mappings in `config/event_mappings.yaml` (hot-reloadable)
- Workflow definitions in `workflows/*.json` (version-controlled)
- chora-compose configs in `chora-configs/` (project-owned)
- No hardcoded routing logic, all declarative

**Follows Best Practices:**
- DDD/BDD/TDD development process
- chora-base template standards
- MCP integration patterns (Pattern N3: n8n as MCP client)
- Strategic Design framework (refactor when it serves both present and future)

---

## User Stories

### Story 1: Daily Report Author
```
As a developer wanting daily status updates,
I want an automated daily report generated from git commits and gateway events,
So that I can see yesterday's work summarized in Markdown format
Without manually gathering data or formatting reports.
```

**Acceptance Criteria:**
- Daily report workflow runs on schedule (or manual trigger)
- Gathers last 24h of git commits from repository
- Gathers last 24h of gateway events from EventLog
- Calls `chora:generate_content` with data as context
- chora-compose renders Jinja2 template (`daily-report.md.j2`)
- Generated report includes:
  - Commit count and list (author, message, timestamp)
  - Event statistics (total, by type, by status)
  - Performance metrics (if available)
- Output saved to `docs/reports/daily-YYYY-MM-DD.md` or sent to Slack

### Story 2: Event-Driven Workflow Author
```
As an n8n workflow author,
I want certain events to automatically trigger workflows,
So that I can react to failures, completions, or thresholds
Without polling or manual intervention.
```

**Acceptance Criteria:**
- `config/event_mappings.yaml` defines event patterns → workflow mappings
- EventWorkflowRouter loads mappings on startup
- Router subscribes to EventLog or EventWatcher
- When event matches pattern, router identifies target workflow
- Router triggers workflow via n8n backend (or executes directly)
- Event parameters templated into workflow parameters (`{{ event.data.tool_name }}`)
- Example: `gateway.tool_call` with `status: failure` → trigger `error-alert` workflow

### Story 3: Workflow Documenter
```
As a workflow maintainer,
I want workflow documentation auto-generated from workflow JSON definitions,
So that documentation stays in sync with actual workflow configuration
Without manual updates or documentation drift.
```

**Acceptance Criteria:**
- Workflow definitions stored in `workflows/*.json` (n8n export format)
- chora-compose template `workflow-docs.md.j2` renders workflow documentation
- Documentation includes: name, trigger, nodes, parameters, data flow
- CI/CD can regenerate docs when workflows change
- Demonstrates correct chora-compose usage (formatting, not storage)
- Self-documenting system (virtuous cycle)

### Story 4: Hot-Config Administrator
```
As an mcp-n8n administrator,
I want to modify event-to-workflow mappings without restarting the gateway,
So that I can quickly adjust routing rules in production
Without service interruption or deployment.
```

**Acceptance Criteria:**
- EventWorkflowRouter watches `config/event_mappings.yaml` for changes
- File modification detected within 1 second (filesystem watcher)
- New mappings loaded and validated
- Invalid config detected and rejected (keeps previous valid config)
- Logged: "Reloaded event mappings (3 patterns loaded)"
- No restart required, no dropped events during reload

---

## Architecture Overview

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────┐
│ Sprint 5: Production Workflows Architecture            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Layer 1: Data Storage (Git + Filesystem)               │
│   ├─ workflows/ (n8n workflow JSON definitions)        │
│   ├─ config/ (event-to-workflow mappings YAML)         │
│   └─ chora-configs/ (templates + content configs)      │
│          ↓                                              │
│ Layer 2: Event Source (EventLog)                       │
│   ├─ Emits events (gateway.tool_call, etc.)            │
│   └─ Monthly partitioned append-only files             │
│          ↓                                              │
│ Layer 3: Event Router (Python code)                    │
│   ├─ Loads mappings from config/event_mappings.yaml    │
│   ├─ Matches events against patterns                   │
│   └─ Triggers n8n workflows                            │
│          ↓                                              │
│ Layer 4: Workflow Execution (n8n)                      │
│   ├─ Loads workflow definitions from workflows/        │
│   ├─ Gathers data (git, APIs, EventLog)                │
│   ├─ Calls chora:generate_content for formatting       │
│   └─ Outputs reports/notifications                     │
│          ↓                                              │
│ Layer 5: Documentation Generation (chora-compose)      │
│   ├─ Templates render data → Markdown/HTML             │
│   ├─ NO LLM calls (pure Jinja2 rendering)              │
│   ├─ Ephemeral storage for generated docs (30 days)    │
│   └─ Returns formatted content to n8n                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Component Details

#### EventWorkflowRouter

**Responsibilities:**
- Load event-to-workflow mappings from `config/event_mappings.yaml`
- Watch config file for changes (hot reload)
- Match incoming events against patterns
- Template workflow parameters from event data
- Trigger target workflows (via n8n backend or direct execution)

**Key Methods:**
```python
class EventWorkflowRouter:
    def __init__(self, config_path: str, backend_registry: BackendRegistry)
    async def load_mappings(self) -> List[EventMapping]
    async def match_event(self, event: Event) -> Optional[WorkflowTarget]
    async def trigger_workflow(self, workflow_id: str, parameters: Dict) -> None
    async def start_watching(self) -> None  # File watcher for hot reload
```

**Config Schema:**
```yaml
# config/event_mappings.yaml
mappings:
  - event_pattern:
      type: "gateway.tool_call"
      backend: "chora-composer"
      status: "success"
    workflow:
      id: "chora-success-notification"
      parameters:
        tool: "{{ event.data.tool_name }}"
        duration: "{{ event.data.duration_ms }}"

  - event_pattern:
      type: "gateway.tool_call"
      status: "failure"
    workflow:
      id: "error-alert-workflow"
      parameters:
        error: "{{ event.data.error }}"
        context: "{{ event.data.context }}"
```

#### Daily Report Workflow

**File:** `src/mcp_n8n/workflows/daily_report.py`

**Functions:**
```python
async def get_recent_commits(repo_path: str, since_hours: int = 24) -> List[CommitData]
async def get_recent_events(event_log: EventLog, since_hours: int = 24) -> List[Event]
def aggregate_statistics(events: List[Event]) -> Dict[str, Any]
async def run_daily_report(
    backend_registry: BackendRegistry,
    event_log: EventLog,
    repo_path: str = ".",
    since_hours: int = 24,
    date: Optional[str] = None
) -> DailyReportResult
```

**Data Flow:**
1. Gather git commits (via subprocess git log)
2. Gather gateway events (via EventLog query)
3. Aggregate statistics (counts by type, status, etc.)
4. Prepare context dict for template
5. Call `chora:generate_content` with context
6. Return generated Markdown report

#### chora-compose Integration

**Directory Structure:**
```
chora-configs/
├── content/
│   ├── daily-report.json         # Content config
│   ├── error-alert.json
│   └── workflow-docs.json
├── templates/
│   ├── daily-report.md.j2        # Jinja2 templates
│   ├── error-alert.md.j2
│   └── workflow-docs.md.j2
└── README.md                     # Template authoring guide
```

**Content Config Example:**
```json
{
  "type": "content",
  "id": "daily-report",
  "schemaRef": {
    "id": "content-schema",
    "version": "3.1"
  },
  "metadata": {
    "description": "Daily engineering report",
    "version": "1.0.0",
    "output_format": "markdown"
  },
  "generation": {
    "patterns": [
      {
        "id": "daily-report-generation",
        "type": "jinja2",
        "template": "daily-report.md.j2",
        "generation_config": {
          "context": {
            "date": {"source": "runtime"},
            "generated_at": {"source": "runtime"},
            "commits": {"source": "runtime"},
            "stats": {"source": "runtime"}
          }
        }
      }
    ]
  }
}
```

**Template Example:**
```jinja2
{# chora-configs/templates/daily-report.md.j2 #}
# Daily Report - {{ date }}

**Generated:** {{ generated_at }}

## Summary

- Total commits: {{ commits | length }}
- Total events: {{ stats.total_events }}
- Success rate: {{ stats.success_rate }}%

## Recent Commits

{% for commit in commits[:10] %}
- **{{ commit.hash[:7] }}**: {{ commit.message }}
  - Author: {{ commit.author }}
  - Time: {{ commit.timestamp }}
{% else %}
*No commits in this period*
{% endfor %}

## Gateway Events

- Total events: {{ stats.total_events }}
- Tool calls: {{ stats.tool_calls }}
- Errors: {{ stats.errors }}
- Average duration: {{ stats.avg_duration_ms }}ms

---
*Generated by chora-compose via mcp-n8n*
```

---

## API Reference

### EventWorkflowRouter

#### `__init__(config_path: str, backend_registry: BackendRegistry)`

Initialize router with config file path and backend registry.

**Parameters:**
- `config_path` (str): Path to `event_mappings.yaml` file
- `backend_registry` (BackendRegistry): Gateway backend registry for workflow execution

**Raises:**
- `FileNotFoundError`: If config file doesn't exist
- `yaml.YAMLError`: If config file is invalid YAML

---

#### `async load_mappings() -> List[EventMapping]`

Load event-to-workflow mappings from YAML config file.

**Returns:**
- `List[EventMapping]`: Validated mapping objects

**Side Effects:**
- Updates internal `self.mappings` state
- Logs number of mappings loaded

**Raises:**
- `ValidationError`: If mapping schema is invalid

---

#### `async match_event(event: Event) -> Optional[WorkflowTarget]`

Match event against configured patterns and return target workflow.

**Parameters:**
- `event` (Event): Event to match against patterns

**Returns:**
- `WorkflowTarget`: Target workflow ID and parameters, or `None` if no match

**Algorithm:**
1. Iterate through mappings in order
2. Check if event matches pattern (all fields must match)
3. If match, template parameters using event data
4. Return first match (short-circuit evaluation)

---

#### `async trigger_workflow(workflow_id: str, parameters: Dict) -> None`

Trigger target workflow with parameters.

**Parameters:**
- `workflow_id` (str): Workflow identifier (e.g., "daily-report-generator")
- `parameters` (Dict): Workflow parameters (templated from event)

**Implementation:**
- If n8n backend available: call `n8n:execute_workflow`
- Else: execute workflow function directly (fallback)

---

### Daily Report Workflow

#### `async run_daily_report(...) -> DailyReportResult`

Execute daily report workflow end-to-end.

**Parameters:**
- `backend_registry` (BackendRegistry): Gateway backend registry
- `event_log` (EventLog): Event log instance for querying events
- `repo_path` (str): Path to git repository (default: ".")
- `since_hours` (int): Hours to look back for commits/events (default: 24)
- `date` (Optional[str]): Report date (default: today)

**Returns:**
- `DailyReportResult`: Result object with:
  - `content` (str): Generated Markdown report
  - `metadata` (Dict): Stats and metrics
  - `commit_count` (int): Number of commits processed
  - `event_count` (int): Number of events processed

**Workflow Steps:**
1. Call `get_recent_commits(repo_path, since_hours)` → List[CommitData]
2. Call `get_recent_events(event_log, since_hours)` → List[Event]
3. Call `aggregate_statistics(events)` → Dict[str, Any]
4. Prepare context dict with all data
5. Get chora-compose backend from registry
6. Call `backend.call_tool("generate_content", {...})` with context
7. Return generated report content

**Example Usage:**
```python
from mcp_n8n.workflows.daily_report import run_daily_report

result = await run_daily_report(
    backend_registry=registry,
    event_log=gateway.event_log,
    repo_path="/path/to/mcp-n8n",
    since_hours=24
)

print(result.content)  # Markdown report
print(f"Processed {result.commit_count} commits, {result.event_count} events")
```

---

## File Structure

```
mcp-n8n/
├── chora-configs/              # chora-compose configs (NEW)
│   ├── content/
│   │   ├── daily-report.json
│   │   ├── error-alert.json
│   │   └── workflow-docs.json
│   ├── templates/
│   │   ├── daily-report.md.j2
│   │   ├── error-alert.md.j2
│   │   └── workflow-docs.md.j2
│   └── README.md               # Template authoring guide
│
├── config/                     # Event routing configs (NEW)
│   └── event_mappings.yaml     # Event → workflow mappings
│
├── workflows/                  # n8n workflow definitions (NEW)
│   ├── daily-report.json
│   ├── error-alerts.json
│   └── README.md               # Workflow usage guide
│
├── src/mcp_n8n/workflows/     # Workflow infrastructure (NEW)
│   ├── __init__.py
│   ├── event_router.py        # EventWorkflowRouter class
│   └── daily_report.py        # Daily report workflow logic
│
├── tests/
│   ├── features/
│   │   └── sprint_5_workflows.feature  # BDD scenarios (NEW)
│   ├── step_defs/
│   │   └── test_workflow_steps.py     # BDD step definitions (NEW)
│   ├── unit/
│   │   ├── test_event_router.py       # Router unit tests (NEW)
│   │   └── test_daily_report_workflow.py  # Workflow unit tests (NEW)
│   └── integration/
│       ├── test_chora_template_rendering.py  # Integration tests (NEW)
│       └── test_event_router_integration.py
│
└── docs/
    ├── architecture/
    │   └── n8n-chora-compose-integration.md  # Architecture reference (EXISTING)
    ├── change-requests/
    │   └── sprint-5-workflows/
    │       ├── intent.md           # This file
    │       ├── bdd-red-phase.md    # BDD RED documentation (TBD)
    │       └── completion-summary.md  # Sprint completion (TBD)
    └── workflows/
        └── README.md               # Workflow authoring guide (NEW)
```

---

## Dependencies

**Existing (No New Dependencies):**
- `pyyaml` - Already in dependencies (config loading)
- `watchdog` - Already in dev dependencies (file watching)
- `jinja2` - Transitive dependency via chora-compose
- `pytest-bdd` - Already in dev dependencies (BDD testing)

**chora-compose Requirements:**
- Version: v1.4.2 or higher (via PyPI)
- Configuration: `cwd` parameter pointing to mcp-n8n project root
- Discovery: chora-compose loads `configs/` from current working directory

**n8n Integration:**
- n8n backend (optional, can execute workflows via Python directly)
- n8n instance running locally or remotely
- Workflow JSON definitions in `workflows/` directory

---

## Testing Strategy

### Unit Tests (15+ tests)

**EventWorkflowRouter:**
- `test_load_mappings_from_yaml` - Load valid YAML config
- `test_load_mappings_invalid_yaml` - Handle invalid YAML
- `test_match_event_exact_match` - Exact pattern match
- `test_match_event_partial_match` - Partial pattern match (subset of fields)
- `test_match_event_no_match` - No pattern matches event
- `test_match_event_first_match_wins` - Short-circuit on first match
- `test_parameter_templating` - Template `{{ event.data.* }}` parameters
- `test_hot_reload_valid_config` - Reload config when file changes
- `test_hot_reload_invalid_config` - Keep previous config if new one invalid

**Daily Report Workflow:**
- `test_get_recent_commits_success` - Parse git log output
- `test_get_recent_commits_empty` - Handle no commits
- `test_get_recent_events_success` - Query EventLog
- `test_aggregate_statistics` - Compute stats from events
- `test_run_daily_report_end_to_end` - Full workflow with mocked backend

### Integration Tests (5+ tests)

**chora-compose Integration:**
- `test_template_discovery_from_chora_configs` - chora-compose finds templates
- `test_generate_content_with_real_backend` - Call actual chora-compose backend
- `test_template_includes_commits_and_events` - Verify template rendering

**EventWorkflowRouter Integration:**
- `test_router_triggers_workflow_on_event` - End-to-end event → workflow
- `test_event_to_daily_report_pipeline` - Full pipeline with all components

### BDD Scenarios (5+ scenarios)

See `tests/features/sprint_5_workflows.feature`:
1. chora-compose renders daily report template
2. EventWorkflowRouter loads config from YAML
3. EventWorkflowRouter matches events to workflows
4. Daily report workflow end-to-end
5. Config hot-reload without restart

---

## Success Criteria

### Phase 1: DDD (Complete)
- ✅ Intent document created (this file)
- ✅ Architecture documented with diagrams
- ✅ API reference written with signatures
- ✅ File structure defined

### Phase 2: BDD
- [ ] 5+ Gherkin scenarios written
- [ ] Step definitions implemented
- [ ] All scenarios initially FAIL (RED phase)

### Phase 3: TDD
- [ ] 15+ unit tests written and PASSING
- [ ] 5+ integration tests written and PASSING
- [ ] All BDD scenarios PASSING
- [ ] Test coverage ≥85%

### Phase 4: Implementation
- [ ] EventWorkflowRouter implemented
- [ ] Daily report workflow implemented
- [ ] chora-compose integration working
- [ ] Config hot-reload working
- [ ] All quality gates passing (lint, typecheck, pre-commit)

### Phase 5: Documentation
- [ ] README.md updated
- [ ] SPRINT_STATUS.md updated
- [ ] Workflow usage guides created
- [ ] Completion summary written

### Phase 6: Release
- [ ] Version bumped (v0.3.0 → v0.4.0)
- [ ] CHANGELOG.md updated
- [ ] Git commit with proper message
- [ ] Tagged and pushed to GitHub

---

## Timeline

**Estimated:** 6.5-7.5 days

| Phase | Duration |
|-------|----------|
| DDD (Documentation) | 0.5 days |
| BDD (Scenarios) | 0.5 days |
| TDD RED (Failing tests) | 0.5 days |
| TDD GREEN (Implementation) | 4-5 days |
| TDD REFACTOR | 0.25 days |
| Documentation | 0.5 days |
| Release Prep | 0.25 days |

---

## Risks & Mitigations

**Risk 1:** chora-compose config discovery issues
- **Mitigation:** Test early, validate `cwd` parameter in Claude Desktop config
- **Fallback:** Symlink `chora-configs → configs` if needed

**Risk 2:** EventWorkflowRouter complexity
- **Mitigation:** Start with simple pattern matching, iterate
- **Fallback:** Hardcode initial mappings, make configurable later

**Risk 3:** n8n workflow JSON complexity
- **Mitigation:** Use Execute Command pattern (simpler)
- **Fallback:** Python orchestration instead of n8n

**Risk 4:** Timeline extends beyond 7.5 days
- **Mitigation:** Daily checkpoint reviews, adjust scope
- **Fallback:** Ship P0 features only (daily report + basic router)

---

## References

- [UNIFIED_ROADMAP.md](../../UNIFIED_ROADMAP.md) - Sprint 5 original plan
- [SPRINT_STATUS.md](../../SPRINT_STATUS.md) - Current progress tracking
- [n8n-chora-compose-integration.md](../../architecture/n8n-chora-compose-integration.md) - Architecture reference
- [development-lifecycle.md](../../process/development-lifecycle.md) - DDD/BDD/TDD process
- [Sprint 3 Intent](../sprint-3-event-monitoring/intent.md) - Similar structure reference

---

**Next Steps:**
1. Review this intent document
2. Proceed to Phase 2: BDD (write Gherkin scenarios)
3. Create `tests/features/sprint_5_workflows.feature`
4. Implement step definitions
5. Confirm RED phase (all scenarios fail)
