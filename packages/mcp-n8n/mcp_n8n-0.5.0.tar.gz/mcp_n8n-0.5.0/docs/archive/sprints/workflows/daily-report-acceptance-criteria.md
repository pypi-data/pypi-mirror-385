# Daily Report Workflow - Acceptance Criteria

**Version:** 1.0.0
**Status:** DRAFT
**Sprint:** Sprint 5 - Production Workflows
**Related:** [daily-report-api-reference.md](./daily-report-api-reference.md)

---

## Overview

This document defines the acceptance criteria for the Daily Report workflow using the **Given-When-Then** format from Behavior Driven Development (BDD).

These criteria will be translated into Gherkin scenarios in Phase 2 (BDD) and validated through automated tests in Phase 3 (TDD).

---

## Core Workflow Acceptance Criteria

### AC-1: Successful Report Generation

**Given** the gateway has access to a git repository
**And** the gateway has access to the event log
**And** chora-compose is installed and available
**When** I run the daily report workflow for today
**Then** a report is generated successfully
**And** the report includes a summary section with key metrics
**And** the report includes recent commits (if any)
**And** the report includes gateway event statistics
**And** the report is stored in ephemeral storage with 7-day retention
**And** the workflow returns status "success"
**And** the workflow execution completes in less than 60 seconds

---

### AC-2: Report with No Recent Commits

**Given** the git repository has no commits in the last 24 hours
**And** the gateway has event data available
**When** I run the daily report workflow
**Then** a report is generated successfully
**And** the report includes a "No commits" section
**And** the report still includes event statistics
**And** the summary shows commit_count = 0
**And** the workflow returns status "success"

---

### AC-3: Report with No Recent Events

**Given** the git repository has commits in the last 24 hours
**And** the event log has no events in the last 24 hours
**When** I run the daily report workflow
**Then** a report is generated successfully
**And** the report includes commit information
**And** the report includes a "No events" section
**And** the summary shows event_count = 0
**And** the workflow returns status "success"

---

### AC-4: Git Repository Not Found

**Given** the specified repository path does not exist
**When** I run the daily report workflow with that path
**Then** the workflow returns status "failure"
**And** the error message indicates "Git repository not found at {path}"
**And** no report is generated
**And** the report_path is None

---

### AC-5: Chora-Compose Not Available

**Given** chora-compose is not installed or not in PATH
**And** the git repository and event log are accessible
**When** I run the daily report workflow
**Then** the workflow returns status "failure"
**And** the error message indicates "chora-compose not available"
**And** the error message suggests installation instructions
**And** no report is generated

---

### AC-6: Custom Date Range

**Given** the git repository has commits from the last 7 days
**And** I want a report covering the last 48 hours
**When** I run the daily report workflow with since_hours=48
**Then** a report is generated successfully
**And** the report only includes commits from the last 48 hours
**And** the report only includes events from the last 48 hours
**And** the report header shows "Coverage: Last 48 hours"

---

### AC-7: HTML Output Format

**Given** I want the report in HTML format instead of Markdown
**When** I run the daily report workflow with output_format="html"
**Then** a report is generated in HTML format
**And** the file extension is .html
**And** the content includes proper HTML structure (html, head, body tags)
**And** the report_path points to the HTML file

---

## Data Gathering Acceptance Criteria

### AC-8: Git Commit Retrieval

**Given** the git repository has 5 commits in the last 24 hours
**When** the workflow calls get_recent_commits()
**Then** all 5 commits are returned
**And** each commit includes: hash, author, message, timestamp, files_changed
**And** commits are ordered by timestamp (most recent first)

---

### AC-9: Event Log Querying

**Given** the event log has 127 events in the last 24 hours
**When** the workflow queries events using get_events(since="24h")
**Then** all 127 events are returned
**And** each event includes: event_type, status, timestamp, metadata
**And** events are filtered to the correct time range

---

### AC-10: Statistics Aggregation

**Given** a list of 127 events
**And** 121 events have status="success"
**And** 6 events have status="failure"
**When** the workflow calls aggregate_statistics(events)
**Then** the success_rate is calculated as 95.28%
**And** events are grouped by type, status, and backend
**And** tool usage counts are extracted from metadata

---

## Chora-Compose Integration Acceptance Criteria

### AC-11: Ephemeral Storage Configuration

**Given** the workflow is configured to use ephemeral storage
**When** the report artifact is assembled
**Then** chora:assemble_artifact is called with storage_type="ephemeral"
**And** the retention policy is set to 7 days
**And** the report is stored in the ephemeral storage directory
**And** the report will be automatically deleted after 7 days

---

### AC-12: Template Rendering

**Given** the daily-report.jinja2 template exists in chora-compose
**When** the workflow calls chora:generate_content with the template
**Then** the template is rendered with the correct context data
**And** the context includes: date, commits, stats, generated_at
**And** the rendered content includes all sections (summary, commits, events)

---

### AC-13: Fallback to Local Storage (Optional)

**Given** chora-compose ephemeral storage is not available
**And** the workflow is configured with fallback_to_local=True
**When** the workflow runs
**Then** the report is written to a local file in /tmp/mcp-n8n-reports/
**And** the workflow returns status "success" with a warning
**And** the warning message indicates "Using local storage fallback"
**And** the report_path points to the local file

**Note:** This is an optional enhancement for resilience.

---

## CLI Interface Acceptance Criteria

### AC-14: Command-Line Execution

**Given** the workflow is invoked via CLI
**When** I run `python -m mcp_n8n.workflows.daily_report`
**Then** the workflow executes successfully
**And** the report path is printed to stdout
**And** the summary statistics are printed to stdout
**And** the exit code is 0

---

### AC-15: CLI Error Handling

**Given** the workflow fails due to missing git repository
**When** I run the CLI command
**Then** an error message is printed to stderr
**And** the exit code is 1
**And** no report path is printed

---

### AC-16: CLI Help Text

**Given** I want to know how to use the CLI
**When** I run `python -m mcp_n8n.workflows.daily_report --help`
**Then** usage information is printed
**And** all parameters are documented with descriptions
**And** examples are provided
**And** the exit code is 0

---

## Performance Acceptance Criteria

### AC-17: Execution Time Target

**Given** a typical repository with ~50 commits in 24 hours
**And** an event log with ~500 events in 24 hours
**When** the workflow executes
**Then** the total execution time is less than 60 seconds
**And** git commit retrieval takes less than 5 seconds
**And** event querying takes less than 2 seconds

---

### AC-18: Large Dataset Handling

**Given** a repository with 500 commits in 24 hours
**And** an event log with 5000 events in 24 hours
**When** the workflow executes
**Then** the workflow completes without timeout
**And** the total execution time is less than 120 seconds
**And** the report is generated successfully

---

## Security Acceptance Criteria

### AC-19: Sensitive Data Filtering

**Given** a commit message contains an API key pattern (e.g., "ANTHROPIC_API_KEY=sk-...")
**When** the workflow generates the report
**Then** the API key is redacted in the commit message
**And** the redacted version shows "ANTHROPIC_API_KEY=[REDACTED]"

**Note:** This is an enhancement - implement if time allows.

---

### AC-20: Path Sanitization

**Given** a repository path contains ".." (parent directory traversal)
**When** the workflow validates the path
**Then** a ValueError is raised
**And** the error message indicates "Invalid repository path"
**And** no report is generated

---

## Edge Cases Acceptance Criteria

### AC-21: Empty Repository

**Given** the git repository is freshly initialized with no commits
**When** the workflow runs
**Then** a report is generated successfully
**And** the commits section shows "No commits in this period"
**And** the summary shows commit_count = 0

---

### AC-22: Invalid Date Format

**Given** I provide an invalid date string (e.g., "2025-13-45")
**When** the workflow runs with that date
**Then** a ValueError is raised
**And** the error message shows the expected format "YYYY-MM-DD"
**And** an example of a valid date is provided

---

### AC-23: Future Date

**Given** I provide a date in the future (e.g., "2026-01-01")
**When** the workflow runs with that date
**Then** a report is generated successfully
**And** the report shows "No commits" and "No events" (none exist yet)
**And** a warning is logged: "Report date is in the future"

---

## Success Metrics

The Daily Report workflow is considered **production-ready** when:

- ✅ All 23 acceptance criteria pass
- ✅ Unit test coverage ≥90%
- ✅ Integration test coverage ≥80%
- ✅ BDD scenarios pass (all Given-When-Then scenarios automated)
- ✅ Performance targets met (AC-17, AC-18)
- ✅ Security considerations validated (AC-19, AC-20)
- ✅ CLI interface fully functional (AC-14, AC-15, AC-16)
- ✅ Chora-compose integration tested (AC-11, AC-12)

---

## Priority Matrix

### Must Have (P0)

- AC-1: Successful Report Generation
- AC-4: Git Repository Not Found
- AC-5: Chora-Compose Not Available
- AC-8: Git Commit Retrieval
- AC-9: Event Log Querying
- AC-10: Statistics Aggregation
- AC-11: Ephemeral Storage Configuration
- AC-12: Template Rendering
- AC-14: Command-Line Execution
- AC-17: Execution Time Target

### Should Have (P1)

- AC-2: Report with No Recent Commits
- AC-3: Report with No Recent Events
- AC-6: Custom Date Range
- AC-7: HTML Output Format
- AC-15: CLI Error Handling
- AC-16: CLI Help Text
- AC-21: Empty Repository
- AC-22: Invalid Date Format

### Could Have (P2)

- AC-13: Fallback to Local Storage
- AC-18: Large Dataset Handling
- AC-19: Sensitive Data Filtering
- AC-20: Path Sanitization
- AC-23: Future Date

---

## Next Steps

1. ✅ **DDD Complete:** API reference and acceptance criteria defined
2. ⏭️ **BDD Phase:** Translate these criteria into Gherkin scenarios
3. ⏭️ **TDD Phase:** Implement tests and code to satisfy all criteria

---

**Document Status:** DRAFT
**Review Status:** Pending self-review
**Owner:** Victor Piper
**Last Updated:** 2025-10-19
