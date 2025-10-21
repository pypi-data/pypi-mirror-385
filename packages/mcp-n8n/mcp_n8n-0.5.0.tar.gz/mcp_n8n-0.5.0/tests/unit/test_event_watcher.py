"""Unit tests for EventWatcher.

Tests the event monitoring functionality in isolation from the full gateway.
Following TDD RED-GREEN-REFACTOR cycle.
"""
# mypy: disable-error-code="no-untyped-def"

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from mcp_n8n.event_watcher import EventWatcher
from mcp_n8n.memory.event_log import EventLog
from mcp_n8n.memory.trace import emit_event
from mcp_n8n.tools.event_query import get_events

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
    """Create temporary events.jsonl file for chora-compose events."""
    events_dir = tmp_path / "var" / "telemetry"
    events_dir.mkdir(parents=True, exist_ok=True)
    events_file = events_dir / "events.jsonl"
    events_file.touch()
    return events_file


@pytest.fixture
def event_watcher(event_log: EventLog, events_file: Path) -> EventWatcher:
    """Create EventWatcher instance without webhook."""
    return EventWatcher(
        event_log=event_log,
        events_file=str(events_file),
        n8n_webhook_url=None,
    )


@pytest.fixture
def event_watcher_with_webhook(event_log: EventLog, events_file: Path) -> EventWatcher:
    """Create EventWatcher instance with webhook configured."""
    return EventWatcher(
        event_log=event_log,
        events_file=str(events_file),
        n8n_webhook_url="http://localhost:5678/webhook-test",
    )


@pytest.fixture
def sample_event() -> dict[str, Any]:
    """Create sample event for testing."""
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "trace_id": "test-trace-001",
        "status": "success",
        "schema_version": "1.0",
        "event_type": "chora.content_generated",
        "content_config_id": "test-config",
        "generator_type": "jinja2",
        "duration_ms": 45,
        "content_size_bytes": 1234,
    }


# ============================================================================
# EventWatcher Initialization Tests
# ============================================================================


def test_event_watcher_init(event_watcher: EventWatcher, events_file: Path):
    """Test EventWatcher initialization."""
    assert event_watcher.events_file == Path(events_file)
    assert event_watcher.n8n_webhook_url is None
    assert not event_watcher._running


def test_event_watcher_init_with_webhook(
    event_watcher_with_webhook: EventWatcher,
):
    """Test EventWatcher initialization with webhook."""
    assert (
        event_watcher_with_webhook.n8n_webhook_url
        == "http://localhost:5678/webhook-test"
    )


# ============================================================================
# Event File Watching Tests
# ============================================================================


@pytest.mark.asyncio
async def test_event_watcher_starts_and_stops(event_watcher: EventWatcher):
    """Test that EventWatcher can start and stop gracefully."""
    # Start watcher
    await event_watcher.start()
    assert event_watcher._running

    # Stop watcher
    await event_watcher.stop()
    assert not event_watcher._running


@pytest.mark.asyncio
async def test_event_watcher_detects_new_events(
    event_watcher: EventWatcher,
    events_file: Path,
    sample_event: dict[str, Any],
):
    """Test that EventWatcher detects events written to file."""
    # Start watching
    watch_task = asyncio.create_task(event_watcher.start())

    # Wait for watcher to start
    await asyncio.sleep(0.1)

    # Write event to file
    with events_file.open("a") as f:
        f.write(json.dumps(sample_event) + "\n")

    # Wait for event processing
    await asyncio.sleep(0.2)

    # Stop watcher
    await event_watcher.stop()
    await watch_task

    # Verify event was stored in event log
    events = event_watcher.event_log.get_by_trace(sample_event["trace_id"])
    assert len(events) > 0
    assert events[0]["trace_id"] == sample_event["trace_id"]


@pytest.mark.asyncio
async def test_event_watcher_handles_multiple_events(
    event_watcher: EventWatcher,
    events_file: Path,
):
    """Test that EventWatcher handles multiple events correctly."""
    # Start watching
    watch_task = asyncio.create_task(event_watcher.start())
    await asyncio.sleep(0.1)

    # Write multiple events
    events_to_write = []
    for i in range(5):
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": f"test-trace-{i:03d}",
            "status": "success",
            "schema_version": "1.0",
            "event_type": "chora.test_event",
        }
        events_to_write.append(event)

        with events_file.open("a") as f:
            f.write(json.dumps(event) + "\n")

        await asyncio.sleep(0.05)

    # Wait for processing
    await asyncio.sleep(0.2)

    # Stop watcher
    await event_watcher.stop()
    await watch_task

    # Verify all events stored
    for event in events_to_write:
        stored_events = event_watcher.event_log.get_by_trace(event["trace_id"])
        assert len(stored_events) > 0, f"Event {event['trace_id']} not found"


# ============================================================================
# Webhook Forwarding Tests
# ============================================================================


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post")
async def test_webhook_forwarding(
    mock_post: AsyncMock,
    event_watcher_with_webhook: EventWatcher,
    events_file: Path,
    sample_event: dict[str, Any],
):
    """Test that events are forwarded to webhook."""
    # Mock successful webhook response
    mock_response = Mock()
    mock_response.status = 200
    mock_post.return_value.__aenter__.return_value = mock_response

    # Start watching
    watch_task = asyncio.create_task(event_watcher_with_webhook.start())
    await asyncio.sleep(0.1)

    # Write event
    with events_file.open("a") as f:
        f.write(json.dumps(sample_event) + "\n")

    # Wait for processing and webhook call
    await asyncio.sleep(0.3)

    # Stop watcher
    await event_watcher_with_webhook.stop()
    await watch_task

    # Verify webhook was called
    assert mock_post.called
    call_args = mock_post.call_args
    assert call_args[0][0] == "http://localhost:5678/webhook-test"
    assert call_args[1]["json"]["trace_id"] == sample_event["trace_id"]


@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post")
async def test_webhook_failure_doesnt_block_storage(
    mock_post: AsyncMock,
    event_watcher_with_webhook: EventWatcher,
    events_file: Path,
    sample_event: dict[str, Any],
):
    """Test that webhook failures don't prevent event storage."""
    # Mock failed webhook response
    mock_post.side_effect = Exception("Webhook unavailable")

    # Start watching
    watch_task = asyncio.create_task(event_watcher_with_webhook.start())
    await asyncio.sleep(0.1)

    # Write event
    with events_file.open("a") as f:
        f.write(json.dumps(sample_event) + "\n")

    # Wait for processing
    await asyncio.sleep(0.3)

    # Stop watcher
    await event_watcher_with_webhook.stop()
    await watch_task

    # Verify event was still stored despite webhook failure
    events = event_watcher_with_webhook.event_log.get_by_trace(sample_event["trace_id"])
    assert len(events) > 0


# ============================================================================
# get_events Tool Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_events_by_trace_id(event_log: EventLog):
    """Test querying events by trace ID."""
    # Initialize EventLog for get_events tool
    from mcp_n8n.tools.event_query import set_event_log

    set_event_log(event_log)

    # Create test events
    for i in range(3):
        emit_event(
            event_type="chora.test",
            trace_id=f"trace-{i}",
            status="success",
            base_dir=event_log.base_dir,
        )

    # Query by specific trace ID
    result = await get_events(trace_id="trace-1")

    assert len(result) > 0
    assert all(event["trace_id"] == "trace-1" for event in result)


@pytest.mark.asyncio
async def test_get_events_by_event_type(event_log: EventLog):
    """Test filtering events by event type."""
    # Initialize EventLog for get_events tool
    from mcp_n8n.tools.event_query import set_event_log

    set_event_log(event_log)

    # Create events with different types
    emit_event(
        event_type="chora.content_generated",
        trace_id="test-001",
        status="success",
        base_dir=event_log.base_dir,
    )
    emit_event(
        event_type="chora.artifact_assembled",
        trace_id="test-002",
        status="success",
        base_dir=event_log.base_dir,
    )

    # Query by event type
    result = await get_events(event_type="chora.content_generated")

    assert len(result) > 0
    assert all(event["event_type"] == "chora.content_generated" for event in result)


@pytest.mark.asyncio
async def test_get_events_by_status(event_log: EventLog):
    """Test filtering events by status."""
    # Initialize EventLog for get_events tool
    from mcp_n8n.tools.event_query import set_event_log

    set_event_log(event_log)

    # Create events with different statuses
    emit_event(
        event_type="chora.test",
        trace_id="test-001",
        status="success",
        base_dir=event_log.base_dir,
    )
    emit_event(
        event_type="chora.test",
        trace_id="test-002",
        status="failure",
        base_dir=event_log.base_dir,
    )

    # Query by status
    result = await get_events(status="failure")

    assert len(result) > 0
    assert all(event["status"] == "failure" for event in result)


@pytest.mark.asyncio
async def test_get_events_with_limit(event_log: EventLog):
    """Test limiting number of returned events."""
    # Initialize EventLog for get_events tool
    from mcp_n8n.tools.event_query import set_event_log

    set_event_log(event_log)

    # Create many events
    for i in range(150):
        emit_event(
            event_type="chora.test",
            trace_id=f"test-{i:04d}",
            status="success",
            base_dir=event_log.base_dir,
        )

    # Query with limit
    result = await get_events(limit=50)

    assert len(result) == 50


@pytest.mark.asyncio
async def test_get_events_with_time_range(event_log: EventLog):
    """Test filtering events by time range."""
    # Initialize EventLog for get_events tool
    from mcp_n8n.tools.event_query import set_event_log

    set_event_log(event_log)

    # Create an event
    emit_event(
        event_type="chora.test",
        trace_id="test-recent",
        status="success",
        base_dir=event_log.base_dir,
    )

    result = await get_events(since="24h")

    # All events should be recent (this is a simple test)
    assert isinstance(result, list)
    assert len(result) >= 1


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.asyncio
async def test_event_watcher_handles_malformed_json(
    event_watcher: EventWatcher,
    events_file: Path,
):
    """Test that EventWatcher handles malformed JSON gracefully."""
    # Start watching
    watch_task = asyncio.create_task(event_watcher.start())
    await asyncio.sleep(0.1)

    # Write malformed JSON
    with events_file.open("a") as f:
        f.write("{ invalid json }\n")

    # Write valid event after
    valid_event = {
        "timestamp": datetime.now(UTC).isoformat(),
        "trace_id": "valid-event",
        "status": "success",
        "schema_version": "1.0",
        "event_type": "chora.test",
    }
    with events_file.open("a") as f:
        f.write(json.dumps(valid_event) + "\n")

    # Wait for processing
    await asyncio.sleep(0.2)

    # Stop watcher
    await event_watcher.stop()
    await watch_task

    # Verify valid event was still processed
    events = event_watcher.event_log.get_by_trace("valid-event")
    assert len(events) > 0


@pytest.mark.asyncio
async def test_event_watcher_handles_missing_file(
    event_log: EventLog,
    tmp_path: Path,
):
    """Test that EventWatcher handles missing events file gracefully."""
    nonexistent_file = tmp_path / "nonexistent" / "events.jsonl"

    watcher = EventWatcher(
        event_log=event_log,
        events_file=str(nonexistent_file),
        n8n_webhook_url=None,
    )

    # Should not crash when starting with missing file
    # Will create parent directories and file
    await watcher.start()
    await asyncio.sleep(0.1)
    await watcher.stop()

    assert nonexistent_file.exists()
