Feature: Event Monitoring for Workflow Validation
  As a workflow developer
  I want to monitor chora-compose events in real-time
  So that I can build event-driven n8n workflows

  Background:
    Given the mcp-n8n gateway is running
    And the chora-composer backend is configured
    And an EventWatcher is monitoring var/telemetry/events.jsonl

  Scenario: Event appears in gateway telemetry (AC1)
    Given chora-compose generates a test event
    When the event is emitted with trace_id "test-001"
    Then the event appears in .chora/memory/events/ within 100ms
    And the event includes trace_id "test-001"
    And the event includes timestamp in ISO format
    And the event includes status "success"

  Scenario: Trace ID propagates to backend (AC2)
    Given I have a trace_id "workflow-123"
    When I call the tool "chora:generate_content" with the trace_id
    Then the chora-compose subprocess receives CHORA_TRACE_ID "workflow-123"
    And all emitted events include trace_id "workflow-123"

  Scenario: Query events by trace ID (AC4)
    Given events exist with trace_ids "test-001", "test-002", "test-003"
    When I call get_events with trace_id "test-002"
    Then I receive only events with trace_id "test-002"
    And the events are ordered by timestamp ascending

  Scenario: Filter events by type and status (AC5)
    Given events of different types exist:
      | event_type               | status  | trace_id   |
      | chora.content_generated  | success | trace-001  |
      | chora.artifact_assembled | success | trace-002  |
      | chora.content_generated  | failure | trace-003  |
      | chora.artifact_assembled | failure | trace-004  |
    When I call get_events with event_type "chora.content_generated" and status "success"
    Then I receive 1 event
    And the event has event_type "chora.content_generated"
    And the event has status "success"

  Scenario: n8n webhook receives events (AC3)
    Given N8N_WEBHOOK_URL is set to "http://localhost:5678/webhook-test"
    And a mock webhook server is listening
    When chora-compose emits an event with trace_id "webhook-test-001"
    Then the webhook receives a POST request within 50ms
    And the request body includes the event JSON
    And the request header Content-Type is "application/json"

  Scenario: Webhook failure doesn't block event storage (AC3)
    Given N8N_WEBHOOK_URL points to unavailable endpoint
    When chora-compose emits an event with trace_id "failure-test-001"
    Then the event is still stored in .chora/memory/events/
    And a warning is logged about webhook failure
    And the event includes trace_id "failure-test-001"

  Scenario: Query events with time range filtering (AC6)
    Given events exist with different timestamps
    When I call get_events with since "24h"
    Then I receive only events from the last 24 hours
    And the events are ordered by timestamp ascending

  Scenario: Query events with limit (AC6)
    Given 150 events exist in the event log
    When I call get_events with limit 50
    Then I receive exactly 50 events
    And the events are the most recent 50
