Feature: Daily Engineering Report Generation
  As an engineering manager
  I want automated daily reports aggregating commits and events
  So that I can track team progress and system health

  Background:
    Given the mcp-n8n gateway is running
    And chora-compose is installed and available

  # AC-1: Successful Report Generation
  Scenario: Generate daily report with commits and events
    Given the git repository has 5 commits in the last 24 hours
    And the event log has 127 events in the last 24 hours
    When I run the daily report workflow for today
    Then a report is generated successfully
    And the workflow returns status "success"
    And the report includes a summary section with key metrics
    And the report includes 5 recent commits
    And the report includes gateway event statistics
    And the report is stored in ephemeral storage with 7-day retention
    And the workflow execution completes in less than 60 seconds

  # AC-2: Report with No Recent Commits
  Scenario: Generate report when no commits exist
    Given the git repository has no commits in the last 24 hours
    And the event log has 50 events in the last 24 hours
    When I run the daily report workflow for today
    Then a report is generated successfully
    And the workflow returns status "success"
    And the report includes a "No commits" message
    And the report includes gateway event statistics
    And the summary shows commit_count equals 0
    And the summary shows event_count equals 50

  # AC-3: Report with No Recent Events
  Scenario: Generate report when no events exist
    Given the git repository has 3 commits in the last 24 hours
    And the event log has no events in the last 24 hours
    When I run the daily report workflow for today
    Then a report is generated successfully
    And the workflow returns status "success"
    And the report includes 3 recent commits
    And the report includes a "No events" message
    And the summary shows event_count equals 0
    And the summary shows commit_count equals 3

  # AC-4: Git Repository Not Found
  Scenario: Fail gracefully when git repository does not exist
    Given a repository path "/nonexistent/repo" that does not exist
    When I run the daily report workflow with repository_path "/nonexistent/repo"
    Then the workflow returns status "failure"
    And the error message contains "Git repository not found at /nonexistent/repo"
    And no report is generated
    And the report_path is None

  # AC-5: Chora-Compose Not Available
  Scenario: Fail gracefully when chora-compose is not installed
    Given chora-compose is not available in PATH
    And the git repository has commits in the last 24 hours
    When I run the daily report workflow for today
    Then the workflow returns status "failure"
    And the error message contains "chora-compose not available"
    And the error message includes installation instructions
    And no report is generated

  # AC-6: Custom Date Range
  Scenario: Generate report for custom time range
    Given the git repository has commits from the last 7 days
    And I want a report covering the last 48 hours
    When I run the daily report workflow with since_hours 48
    Then a report is generated successfully
    And the workflow returns status "success"
    And the report only includes commits from the last 48 hours
    And the report only includes events from the last 48 hours
    And the report header shows "Coverage: Last 48 hours"

  # AC-7: HTML Output Format
  Scenario: Generate report in HTML format
    Given the git repository has commits in the last 24 hours
    And I want the report in HTML format
    When I run the daily report workflow with output_format "html"
    Then a report is generated in HTML format
    And the file extension is ".html"
    And the content includes proper HTML structure
    And the report_path points to an HTML file

  # AC-8: Git Commit Retrieval
  Scenario: Retrieve git commits from repository
    Given the git repository has 5 commits in the last 24 hours
    When the workflow calls get_recent_commits()
    Then all 5 commits are returned
    And each commit includes hash, author, message, timestamp, files_changed
    And commits are ordered by timestamp descending

  # AC-9: Event Log Querying
  Scenario: Query events from event log
    Given the event log has 127 events in the last 24 hours
    When the workflow calls get_events with since "24h"
    Then all 127 events are returned
    And each event includes event_type, status, timestamp, metadata
    And events are filtered to the correct time range

  # AC-10: Statistics Aggregation
  Scenario: Aggregate statistics from events
    Given a list of 127 events
    And 121 events have status "success"
    And 6 events have status "failure"
    When the workflow calls aggregate_statistics with the events
    Then the success_rate is 95.28 percent
    And events are grouped by type, status, and backend
    And tool usage counts are extracted from metadata

  # AC-11: Ephemeral Storage Configuration
  Scenario: Store report in ephemeral storage
    Given the workflow is configured to use ephemeral storage
    When the report artifact is assembled
    Then chora:assemble_artifact is called with storage_type "ephemeral"
    And the retention policy is set to 7 days
    And the report is stored in the ephemeral storage directory
    And the report will auto-delete after 7 days

  # AC-12: Template Rendering
  Scenario: Render daily report template
    Given the daily-report.jinja2 template exists in chora-compose
    And the template context includes date, commits, stats, generated_at
    When the workflow calls chora:generate_content with the template
    Then the template is rendered with the correct context data
    And the rendered content includes summary, commits, and events sections

  # AC-14: Command-Line Execution
  Scenario: Run workflow from command line
    Given the workflow is invoked via CLI
    When I run "python -m mcp_n8n.workflows.daily_report"
    Then the workflow executes successfully
    And the report path is printed to stdout
    And the summary statistics are printed to stdout
    And the exit code is 0

  # AC-15: CLI Error Handling
  Scenario: Handle CLI errors gracefully
    Given the git repository does not exist at the specified path
    When I run the daily report CLI command
    Then an error message is printed to stderr
    And the exit code is 1
    And no report path is printed to stdout

  # AC-16: CLI Help Text
  Scenario: Display CLI help information
    Given I want to know how to use the daily report CLI
    When I run "python -m mcp_n8n.workflows.daily_report --help"
    Then usage information is printed to stdout
    And all parameters are documented with descriptions
    And examples are provided
    And the exit code is 0

  # AC-17: Execution Time Target
  Scenario: Meet performance targets for typical workload
    Given a repository with 50 commits in the last 24 hours
    And an event log with 500 events in the last 24 hours
    When the workflow executes
    Then the total execution time is less than 60 seconds
    And git commit retrieval takes less than 5 seconds
    And event querying takes less than 2 seconds

  # AC-21: Empty Repository
  Scenario: Handle empty repository gracefully
    Given the git repository is freshly initialized with no commits
    When I run the daily report workflow for today
    Then a report is generated successfully
    And the workflow returns status "success"
    And the commits section shows "No commits in this period"
    And the summary shows commit_count equals 0

  # AC-22: Invalid Date Format
  Scenario: Reject invalid date format
    Given I provide an invalid date string "2025-13-45"
    When I run the daily report workflow with that date
    Then a ValueError is raised
    And the error message shows the expected format "YYYY-MM-DD"
    And an example of a valid date is provided

  # AC-23: Future Date
  Scenario: Handle future date gracefully
    Given I provide a date in the future "2026-01-01"
    When I run the daily report workflow with that date
    Then a report is generated successfully
    And the workflow returns status "success"
    And the report shows "No commits" and "No events"
    And a warning is logged "Report date is in the future"

  # Additional Scenario: Integration with n8n
  Scenario: Export workflow for n8n integration
    Given the Python workflow is implemented and tested
    When I export the workflow as n8n JSON
    Then the n8n workflow includes 7 nodes
    And the workflow can be imported into n8n
    And the workflow executes successfully in n8n environment
