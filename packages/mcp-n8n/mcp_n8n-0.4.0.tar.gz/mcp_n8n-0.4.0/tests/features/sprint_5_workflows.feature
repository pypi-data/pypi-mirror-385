Feature: Sprint 5 Production Workflows
  As a workflow developer
  I want event-driven workflow orchestration with template-based reporting
  So that I can build automated workflows that react to events and generate formatted reports

  Background:
    Given the mcp-n8n gateway is running
    And chora-compose v1.4.2 or higher is available
    And the chora-configs directory exists with templates

  # ================================================================
  # chora-compose Integration
  # ================================================================

  # AC-1: Template Discovery and Rendering
  Scenario: chora-compose discovers and renders template from chora-configs
    Given a template file "chora-configs/templates/daily-report.md.j2" exists
    And a content config "chora-configs/content/daily-report.json" exists
    And the content config references template "daily-report.md.j2"
    When I call chora:generate_content with content_config_id "daily-report"
    And I provide context data with commits and events
    Then the template is rendered successfully
    And the output is valid Markdown
    And the output includes the commits data
    And the output includes the events data
    And the generation completes in less than 5 seconds

  # AC-2: Template Rendering with Empty Data
  Scenario: chora-compose handles empty context gracefully
    Given a template file exists with conditional blocks
    And a content config exists
    When I call chora:generate_content with empty commits list
    And I call chora:generate_content with empty events list
    Then the template renders successfully
    And the output shows "No commits" message
    And the output shows "No events" message
    And no errors are raised

  # AC-3: Template Config Discovery
  Scenario: chora-compose loads configs from mcp-n8n chora-configs directory
    Given the mcp-n8n project root is "/path/to/mcp-n8n"
    And chora-compose is configured with cwd "/path/to/mcp-n8n"
    And configs exist in "/path/to/mcp-n8n/chora-configs/"
    When chora-compose backend starts
    Then it discovers content configs in chora-configs/content/
    And it discovers templates in chora-configs/templates/
    And generate_content tool can reference config IDs
    And no FileNotFoundError is raised

  # ================================================================
  # EventWorkflowRouter
  # ================================================================

  # AC-4: Router Loads Event Mappings from YAML
  Scenario: EventWorkflowRouter loads mappings configuration
    Given a config file "config/event_mappings.yaml" exists
    And the config file contains 3 event-to-workflow mappings
    When EventWorkflowRouter initializes with the config path
    Then 3 mappings are loaded successfully
    And each mapping has event_pattern and workflow fields
    And the router is ready to match events
    And initialization completes in less than 100ms

  # AC-5: Router Matches Event to Workflow (Exact Match)
  Scenario: Router identifies target workflow for matching event
    Given EventWorkflowRouter is initialized with mappings
    And a mapping exists for event_pattern type "gateway.tool_call" status "failure"
    And the mapping targets workflow "error-alert-workflow"
    When an event occurs with type "gateway.tool_call" and status "failure"
    And the router calls match_event with the event
    Then the router returns workflow_id "error-alert-workflow"
    And the match completes in less than 10ms

  # AC-6: Router Matches Event (Partial Pattern)
  Scenario: Router matches event with partial pattern (subset of fields)
    Given a mapping with pattern type "gateway.tool_call" (no status specified)
    And the mapping targets workflow "tool-call-logger"
    When an event occurs with type "gateway.tool_call" and status "success"
    Then the router matches the event to "tool-call-logger"
    And the match succeeds because all pattern fields are present in event

  # AC-7: Router No Match Found
  Scenario: Router returns None when no patterns match
    Given EventWorkflowRouter has mappings for "gateway.tool_call" events only
    When an event occurs with type "coda.document_updated"
    Then the router returns None
    And no workflow is triggered
    And no errors are raised

  # AC-8: Router Templates Workflow Parameters
  Scenario: Router templates parameters from event data
    Given a mapping with parameters tool "{{ event.data.tool_name }}"
    And parameters error "{{ event.data.error }}"
    When an event occurs with data.tool_name "generate_content"
    And data.error "Template not found"
    Then the router renders parameters with tool "generate_content"
    And parameters with error "Template not found"
    And the templated parameters are passed to workflow trigger

  # AC-9: Router Config Hot Reload
  Scenario: Router reloads config when YAML file changes
    Given EventWorkflowRouter is running with 2 mappings
    And a file watcher monitors "config/event_mappings.yaml"
    When I modify the YAML file to add a 3rd mapping
    And I save the file
    Then the router detects the file change within 1 second
    And the router reloads the config
    And the router now has 3 mappings loaded
    And no restart is required

  # AC-10: Router Config Hot Reload - Invalid YAML
  Scenario: Router keeps previous config when new config is invalid
    Given EventWorkflowRouter is running with 2 valid mappings
    When I modify the YAML file with invalid syntax
    And I save the file
    Then the router detects the file change
    And the router attempts to reload
    And the reload fails with validation error
    And the router keeps the previous 2 valid mappings
    And a warning is logged about invalid config
    And events continue to match against old config

  # ================================================================
  # Daily Report Workflow
  # ================================================================

  # AC-11: Daily Report End-to-End
  Scenario: Daily report workflow executes successfully
    Given the git repository has 5 commits in the last 24 hours
    And the event log has 50 gateway events in the last 24 hours
    And chora-configs/templates/daily-report.md.j2 exists
    And chora-configs/content/daily-report.json exists
    When I run run_daily_report workflow
    Then the workflow calls get_recent_commits
    And the workflow calls get_recent_events
    And the workflow calls aggregate_statistics
    And the workflow calls chora:generate_content
    And the workflow returns a DailyReportResult
    And the result.content is valid Markdown
    And the result.commit_count equals 5
    And the result.event_count equals 50
    And the workflow completes in less than 10 seconds

  # AC-12: Daily Report Commit Parsing
  Scenario: Workflow parses git commits correctly
    Given the git repository has commits with various formats
    And commits include merge commits, standard commits, and signed commits
    When the workflow calls get_recent_commits
    Then all commits are parsed successfully
    And each commit has hash, author, message, timestamp fields
    And commits are ordered by timestamp descending (most recent first)
    And no parsing errors occur

  # AC-13: Daily Report Event Aggregation
  Scenario: Workflow aggregates event statistics
    Given the event log has 100 events
    And 70 events have type "gateway.tool_call"
    And 30 events have type "gateway.backend_status"
    And 90 events have status "success"
    And 10 events have status "failure"
    When the workflow calls aggregate_statistics
    Then stats.total_events equals 100
    And stats.tool_calls equals 70
    And stats.success_count equals 90
    And stats.errors equals 10
    And stats.success_rate equals 90
    And stats.error_rate equals 10

  # AC-14: Daily Report with Custom Time Range
  Scenario: Daily report for custom hours
    Given the git repository has commits from last 7 days
    And I want a report for last 48 hours only
    When I run run_daily_report with since_hours 48
    Then only commits from last 48 hours are included
    And only events from last 48 hours are included
    And the report header shows "Last 48 hours"

  # ================================================================
  # Event-to-Workflow Integration
  # ================================================================

  # AC-15: Event Triggers Workflow via Router
  Scenario: Gateway event automatically triggers workflow
    Given EventWorkflowRouter is running
    And a mapping exists for type "gateway.tool_call" status "failure" → "error-alert"
    When the gateway emits an event with type "gateway.tool_call" status "failure"
    And the EventWatcher detects the event
    And the router processes the event
    Then the router matches "error-alert" workflow
    And the router triggers the workflow
    And the workflow receives event parameters
    And the end-to-end latency is less than 100ms

  # AC-16: Workflow Calls chora-compose for Formatting
  Scenario: Error alert workflow generates formatted report
    Given an error-alert workflow is triggered by router
    And the workflow receives event data with error details
    When the workflow calls chora:generate_content
    And passes content_config_id "error-alert"
    And passes context with error, stack_trace, timestamp
    Then chora-compose renders error-alert.md.j2 template
    And the output includes formatted error message
    And the output includes stack trace (if present)
    And the output includes timestamp
    And the formatted alert is returned to workflow

  # AC-17: Complete Event-Driven Pipeline
  Scenario: End-to-end event → router → workflow → report
    Given the complete system is running (gateway, router, chora-compose)
    And mappings configured for tool_call failures
    When a tool call fails in the gateway
    Then gateway emits event to EventLog
    And EventWatcher forwards to EventWorkflowRouter
    And router matches event to error-alert workflow
    And workflow gathers error context
    And workflow calls chora:generate_content
    And formatted error report is generated
    And report is saved or sent to notification channel
    And the complete pipeline executes in less than 200ms

  # ================================================================
  # Workflow Documentation Generation
  # ================================================================

  # AC-18: Generate Workflow Documentation
  Scenario: Auto-generate docs from workflow JSON definitions
    Given a workflow definition file "workflows/daily-report.json" exists
    And the workflow has name, nodes, connections metadata
    And a template "workflow-docs.md.j2" exists
    When I call chora:generate_content with content_config_id "workflow-docs"
    And I provide context with workflow definition
    Then formatted documentation is generated
    And docs include workflow name and description
    And docs include node configuration
    And docs include data flow diagram (ASCII or Markdown)
    And the docs are valid Markdown

  # AC-19: Self-Documenting Workflow System
  Scenario: CI/CD regenerates workflow docs on changes
    Given workflow definitions exist in workflows/ directory
    And templates exist for workflow documentation
    When a workflow JSON file is modified
    And the CI/CD pipeline detects the change
    Then the pipeline calls chora:generate_content
    And updated documentation is generated
    And docs are committed to docs/workflows/
    And documentation stays in sync with workflow definitions

  # ================================================================
  # Error Handling & Edge Cases
  # ================================================================

  # AC-20: Router Handles Missing Config File
  Scenario: Router fails gracefully when config file missing
    Given the config file "config/event_mappings.yaml" does NOT exist
    When EventWorkflowRouter initializes
    Then initialization raises FileNotFoundError
    And the error message indicates missing config file
    And the error message suggests creating the file

  # AC-21: Template Rendering Fails Gracefully
  Scenario: Workflow handles template rendering errors
    Given a daily report workflow is running
    When chora:generate_content fails (template not found)
    Then the workflow catches the error
    And the workflow returns status "failure"
    And the error message includes template ID
    And the error message includes troubleshooting steps
    And no unhandled exceptions occur

  # AC-22: Event Data Missing Required Fields
  Scenario: Router handles malformed events
    Given EventWorkflowRouter is running
    When an event occurs with missing "type" field
    Then the router logs a warning
    And the router skips the malformed event
    And the router continues processing next events
    And no exceptions are raised

  # AC-23: Workflow Parameter Templating Fails
  Scenario: Router handles template rendering errors in parameters
    Given a mapping with parameters referencing "{{ event.data.missing_field }}"
    When an event occurs without the missing_field
    Then the router logs a warning
    And the router uses empty string or None for missing field
    And the workflow still triggers (with partial parameters)
    And no exceptions are raised
