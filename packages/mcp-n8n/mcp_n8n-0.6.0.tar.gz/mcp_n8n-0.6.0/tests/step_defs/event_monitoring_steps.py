"""BDD step definitions for event monitoring feature.

This module implements the Gherkin scenarios from event_monitoring.feature
following the Red-Green-Refactor TDD cycle.
"""

import json
import os
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

# Import components to be implemented
# These will fail initially (RED phase)
from mcp_n8n.event_watcher import EventWatcher
from mcp_n8n.memory.event_log import EventLog
from mcp_n8n.tools.event_query import get_events
from pytest_bdd import given, parsers, scenarios, then, when

# Load scenarios from feature file
scenarios("../features/event_monitoring.feature")


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def event_log(tmp_path: Path) -> EventLog:
    """Create EventLog instance for testing."""
    events_dir = tmp_path / ".chora" / "memory" / "events"
    events_dir.mkdir(parents=True, exist_ok=True)
    return EventLog(base_dir=events_dir)


@pytest.fixture
def events_file(tmp_path: Path) -> Path:
    """Create temporary events.jsonl file."""
    events_dir = tmp_path / "var" / "telemetry"
    events_dir.mkdir(parents=True, exist_ok=True)
    events_file = events_dir / "events.jsonl"
    events_file.touch()
    return events_file


@pytest.fixture
def event_watcher(event_log: EventLog, events_file: Path) -> EventWatcher:
    """Create EventWatcher instance for testing."""
    return EventWatcher(
        event_log=event_log,
        events_file=str(events_file),
        n8n_webhook_url=None,  # Default: no webhook
    )


@pytest.fixture
def mock_webhook_server(tmp_path: Path):
    """Create mock webhook server that captures requests."""
    # This will be implemented with aiohttp in the GREEN phase
    pass


# ============================================================================
# Background Steps
# ============================================================================


@given("the mcp-n8n gateway is running", target_fixture="gateway_running")
def gateway_running():
    """Simulate gateway running state."""
    return {"status": "running", "trace_id": None}


@given("the chora-composer backend is configured", target_fixture="backend_config")
def backend_configured():
    """Simulate backend configuration."""
    return {"name": "chora-composer", "enabled": True}


@given(
    "an EventWatcher is monitoring var/telemetry/events.jsonl",
    target_fixture="watcher_started",
)
async def watcher_monitoring(event_watcher: EventWatcher):
    """Start EventWatcher monitoring."""
    await event_watcher.start()
    yield event_watcher
    await event_watcher.stop()


# ============================================================================
# Scenario: Event appears in gateway telemetry (AC1)
# ============================================================================


@given("chora-compose generates a test event", target_fixture="test_event")
def test_event_generated():
    """Generate a test event structure."""
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "trace_id": "",  # Will be set in when step
        "status": "success",
        "schema_version": "1.0",
        "event_type": "chora.content_generated",
        "content_config_id": "test-config",
        "generator_type": "jinja2",
        "duration_ms": 45,
        "content_size_bytes": 1234,
    }


@when(
    parsers.parse('the event is emitted with trace_id "{trace_id}"'),
    target_fixture="emitted_event",
)
def emit_event_with_trace(test_event: dict[str, Any], events_file: Path, trace_id: str):
    """Emit event to events.jsonl file."""
    test_event["trace_id"] = trace_id

    # Write to events.jsonl
    with events_file.open("a") as f:
        f.write(json.dumps(test_event) + "\n")

    time.sleep(0.01)  # Allow 10ms for event processing
    return test_event


@then("the event appears in .chora/memory/events/ within 100ms")
async def event_appears_in_memory(event_log: EventLog, emitted_event: dict[str, Any]):
    """Verify event appears in gateway event log."""
    # Query by trace_id
    trace_id = emitted_event["trace_id"]
    events = event_log.query(trace_id=trace_id)

    assert len(events) > 0, f"No events found with trace_id={trace_id}"
    assert events[0]["trace_id"] == trace_id


@then(parsers.parse('the event includes trace_id "{expected_trace_id}"'))
def event_has_trace_id(emitted_event: dict[str, Any], expected_trace_id: str):
    """Verify event has correct trace_id."""
    assert emitted_event["trace_id"] == expected_trace_id


@then("the event includes timestamp in ISO format")
def event_has_iso_timestamp(emitted_event: dict[str, Any]):
    """Verify event has ISO 8601 timestamp."""
    timestamp = emitted_event["timestamp"]
    # Should parse as ISO 8601
    datetime.fromisoformat(timestamp)


@then(parsers.parse('the event includes status "{expected_status}"'))
def event_has_status(emitted_event: dict[str, Any], expected_status: str):
    """Verify event has correct status."""
    assert emitted_event["status"] == expected_status


# ============================================================================
# Scenario: Trace ID propagates to backend (AC2)
# ============================================================================


@given(parsers.parse('I have a trace_id "{trace_id}"'), target_fixture="trace_context")
def have_trace_id(trace_id: str):
    """Set up trace context."""
    return {"trace_id": trace_id}


@when(
    parsers.parse('I call the tool "{tool_name}" with the trace_id'),
    target_fixture="tool_call_result",
)
async def call_tool_with_trace(trace_context: dict[str, Any], tool_name: str):
    """Call MCP tool with trace context."""
    # This will test trace ID propagation to subprocess
    # Implementation in GREEN phase
    trace_id = trace_context["trace_id"]

    # Set environment variable
    os.environ["CHORA_TRACE_ID"] = trace_id

    # Simulate tool call (will be real implementation in GREEN)
    return {
        "tool": tool_name,
        "trace_id": trace_id,
        "env_trace_id": os.getenv("CHORA_TRACE_ID"),
    }


@then(
    parsers.parse('the chora-compose subprocess receives CHORA_TRACE_ID "{trace_id}"')
)
def subprocess_receives_trace_id(tool_call_result: dict[str, Any], trace_id: str):
    """Verify subprocess received trace ID in environment."""
    assert tool_call_result["env_trace_id"] == trace_id


@then(parsers.parse('all emitted events include trace_id "{trace_id}"'))
async def all_events_have_trace_id(event_log: EventLog, trace_id: str):
    """Verify all events from this trace have the trace ID."""
    events = event_log.query(trace_id=trace_id)
    assert all(event["trace_id"] == trace_id for event in events)


# ============================================================================
# Scenario: Query events by trace ID (AC4)
# ============================================================================


@given(
    parsers.parse('events exist with trace_ids "{trace_ids}"'),
    target_fixture="existing_events",
)
async def events_with_trace_ids(event_log: EventLog, trace_ids: str):
    """Create events with specified trace IDs."""
    trace_id_list = [tid.strip() for tid in trace_ids.split(",")]
    events = []

    for trace_id in trace_id_list:
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": trace_id,
            "status": "success",
            "schema_version": "1.0",
            "event_type": "chora.test_event",
        }
        event_log.emit(**event)
        events.append(event)

    return events


@when(
    parsers.parse('I call get_events with trace_id "{trace_id}"'),
    target_fixture="query_result",
)
async def query_events_by_trace_id(trace_id: str):
    """Query events using get_events MCP tool."""
    # Call the MCP tool implementation
    result = await get_events(trace_id=trace_id)
    return result


@then(parsers.parse('I receive only events with trace_id "{trace_id}"'))
def only_matching_trace_ids(query_result: list[dict[str, Any]], trace_id: str):
    """Verify all returned events have the specified trace ID."""
    assert len(query_result) > 0, "No events returned"
    assert all(event["trace_id"] == trace_id for event in query_result)


@then("the events are ordered by timestamp ascending")
def events_ordered_by_timestamp(query_result: list[dict[str, Any]]):
    """Verify events are in chronological order."""
    if len(query_result) < 2:
        return  # No ordering to verify

    timestamps = [datetime.fromisoformat(event["timestamp"]) for event in query_result]

    for i in range(len(timestamps) - 1):
        assert (
            timestamps[i] <= timestamps[i + 1]
        ), f"Events not in order: {timestamps[i]} > {timestamps[i+1]}"


# ============================================================================
# Scenario: Filter events by type and status (AC5)
# ============================================================================


@given("events of different types exist:", target_fixture="different_events")
async def events_of_different_types(event_log: EventLog, datatable):
    """Create events with different types and statuses."""
    events = []

    for row in datatable:
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": row["trace_id"],
            "status": row["status"],
            "schema_version": "1.0",
            "event_type": row["event_type"],
        }
        event_log.emit(**event)
        events.append(event)
        time.sleep(0.001)  # Ensure different timestamps

    return events


@when(
    parsers.parse(
        'I call get_events with event_type "{event_type}" and status "{status}"'
    ),
    target_fixture="filtered_result",
)
async def query_with_filters(event_type: str, status: str):
    """Query events with type and status filters."""
    result = await get_events(event_type=event_type, status=status)
    return result


@then(parsers.parse("I receive {count:d} event"))
def receive_count_events(filtered_result: list[dict[str, Any]], count: int):
    """Verify correct number of events returned."""
    assert len(filtered_result) == count


@then(parsers.parse('the event has event_type "{expected_type}"'))
def event_has_type(filtered_result: list[dict[str, Any]], expected_type: str):
    """Verify event type matches."""
    assert len(filtered_result) > 0
    assert filtered_result[0]["event_type"] == expected_type


@then(parsers.parse('the event has status "{expected_status}"'))
def event_has_expected_status(
    filtered_result: list[dict[str, Any]], expected_status: str
):
    """Verify event status matches."""
    assert len(filtered_result) > 0
    assert filtered_result[0]["status"] == expected_status


# ============================================================================
# Scenario: n8n webhook receives events (AC3)
# ============================================================================


@given(parsers.parse('N8N_WEBHOOK_URL is set to "{webhook_url}"'))
def set_webhook_url(event_watcher: EventWatcher, webhook_url: str):
    """Configure webhook URL."""
    event_watcher.n8n_webhook_url = webhook_url


@given("a mock webhook server is listening", target_fixture="webhook_requests")
def mock_webhook_listening():
    """Set up mock webhook server."""
    # Will be implemented with aiohttp in GREEN phase
    return {"requests": []}


@when(
    parsers.parse('chora-compose emits an event with trace_id "{trace_id}"'),
    target_fixture="webhook_event",
)
def emit_event_for_webhook(events_file: Path, trace_id: str):
    """Emit event that should trigger webhook."""
    event = {
        "timestamp": datetime.now(UTC).isoformat(),
        "trace_id": trace_id,
        "status": "success",
        "schema_version": "1.0",
        "event_type": "chora.test_event",
    }

    with events_file.open("a") as f:
        f.write(json.dumps(event) + "\n")

    time.sleep(0.01)  # Allow processing time
    return event


@then("the webhook receives a POST request within 50ms")
def webhook_receives_post(webhook_requests: dict[str, Any]):
    """Verify webhook received POST request."""
    # Will verify timing in GREEN phase
    assert len(webhook_requests["requests"]) > 0


@then("the request body includes the event JSON")
def webhook_body_has_event(
    webhook_requests: dict[str, Any], webhook_event: dict[str, Any]
):
    """Verify webhook received correct event data."""
    request = webhook_requests["requests"][0]
    assert request["body"]["trace_id"] == webhook_event["trace_id"]


@then(parsers.parse('the request header Content-Type is "{content_type}"'))
def webhook_has_content_type(webhook_requests: dict[str, Any], content_type: str):
    """Verify webhook request has correct Content-Type."""
    request = webhook_requests["requests"][0]
    assert request["headers"]["Content-Type"] == content_type


# ============================================================================
# Scenario: Webhook failure doesn't block event storage (AC3)
# ============================================================================


@given("N8N_WEBHOOK_URL points to unavailable endpoint")
def webhook_unavailable(event_watcher: EventWatcher):
    """Set webhook to unavailable URL."""
    event_watcher.n8n_webhook_url = "http://localhost:9999/nonexistent"


@then("the event is still stored in .chora/memory/events/")
async def event_stored_despite_webhook_failure(
    event_log: EventLog, webhook_event: dict[str, Any]
):
    """Verify event was stored even though webhook failed."""
    events = event_log.query(trace_id=webhook_event["trace_id"])
    assert len(events) > 0


@then("a warning is logged about webhook failure")
def warning_logged_for_webhook_failure(caplog):
    """Verify warning was logged."""
    # Will check caplog in GREEN phase
    pass


# ============================================================================
# Scenario: Query events with time range filtering (AC6)
# ============================================================================


@given("events exist with different timestamps", target_fixture="timestamped_events")
async def events_with_timestamps(event_log: EventLog):
    """Create events with various timestamps."""
    now = datetime.now(UTC)
    events = []

    # Create events at different times
    timestamps = [
        now - timedelta(hours=48),  # 2 days ago
        now - timedelta(hours=12),  # 12 hours ago
        now - timedelta(hours=1),  # 1 hour ago
        now,  # Now
    ]

    for i, ts in enumerate(timestamps):
        event = {
            "timestamp": ts.isoformat(),
            "trace_id": f"time-test-{i:03d}",
            "status": "success",
            "schema_version": "1.0",
            "event_type": "chora.test_event",
        }
        event_log.emit(**event)
        events.append(event)

    return events


@when(parsers.parse('I call get_events with since "{time_range}"'))
async def query_with_time_range(time_range: str):
    """Query events with time range filter."""
    result = await get_events(since=time_range)
    return result


@then("I receive only events from the last 24 hours")
def only_recent_events(query_result: list[dict[str, Any]]):
    """Verify all events are within 24 hours."""
    cutoff = datetime.now(UTC) - timedelta(hours=24)

    for event in query_result:
        event_time = datetime.fromisoformat(event["timestamp"])
        assert event_time >= cutoff, f"Event {event['trace_id']} is older than 24 hours"


# ============================================================================
# Scenario: Query events with limit (AC6)
# ============================================================================


@given(parsers.parse("{count:d} events exist in the event log"))
async def many_events_exist(event_log: EventLog, count: int):
    """Create many events for pagination testing."""
    for i in range(count):
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": f"limit-test-{i:04d}",
            "status": "success",
            "schema_version": "1.0",
            "event_type": "chora.test_event",
        }
        event_log.emit(**event)
        time.sleep(0.0001)  # Ensure different timestamps


@when(parsers.parse("I call get_events with limit {limit:d}"))
async def query_with_limit(limit: int):
    """Query events with limit."""
    result = await get_events(limit=limit)
    return result


@then(parsers.parse("I receive exactly {count:d} events"))
def receive_exact_count(query_result: list[dict[str, Any]], count: int):
    """Verify exact number of events returned."""
    assert len(query_result) == count


@then(parsers.parse("the events are the most recent {count:d}"))
def events_are_most_recent(query_result: list[dict[str, Any]], count: int):
    """Verify events are the most recent ones."""
    # Events should be ordered by timestamp ascending, with most recent last
    assert len(query_result) == count
    # Additional verification would check these are indeed the most recent
