"""Integration tests extracted from event monitoring tutorial.

These tests validate that the examples in the tutorial actually work,
following the Documentation-Driven Development (DDD) pattern from chora-compose.

If the tutorial changes, these tests must be updated to match.
If these tests fail, the tutorial examples are broken.
"""

import asyncio
import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pytest
from mcp_n8n.event_watcher import EventWatcher
from mcp_n8n.memory.event_log import EventLog
from mcp_n8n.memory.trace import emit_event
from mcp_n8n.tools.event_query import get_events, set_event_log

# ============================================================================
# Part 2: Basic Event Monitoring (Without Webhooks)
# ============================================================================


@pytest.mark.asyncio
async def test_tutorial_part2_step1_create_event_watcher(tmp_path: Path):
    """Validate tutorial Part 2, Step 1: Create EventWatcher.

    From tutorial:
    > Create a Python script to test the EventWatcher
    """
    # Initialize EventLog
    event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")

    # Create EventWatcher (no webhook)
    watcher = EventWatcher(
        event_log=event_log,
        events_file=str(tmp_path / "var" / "telemetry" / "events.jsonl"),
        n8n_webhook_url=None,  # No webhook for now
    )

    # Start watching
    await watcher.start()
    assert watcher._running is True

    # Keep running briefly
    await asyncio.sleep(0.1)

    # Stop gracefully
    await watcher.stop()
    assert watcher._running is False


@pytest.mark.asyncio
async def test_tutorial_part2_step2_generate_test_events(tmp_path: Path):
    """Validate tutorial Part 2, Step 2: Generate Test Events.

    From tutorial:
    > While the EventWatcher is running, generate some test events
    """
    # Setup
    events_file = tmp_path / "var" / "telemetry" / "events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)
    events_file.touch()

    event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    watcher = EventWatcher(
        event_log=event_log,
        events_file=str(events_file),
        n8n_webhook_url=None,
    )

    # Start watching
    await watcher.start()
    await asyncio.sleep(0.1)

    # Generate a test event (from tutorial example)
    test_event = {
        "timestamp": "2025-10-19T10:00:00Z",
        "trace_id": "test-001",
        "status": "success",
        "schema_version": "1.0",
        "event_type": "chora.content_generated",
        "metadata": {"generator": "test"},
    }

    with events_file.open("a") as f:
        f.write(json.dumps(test_event) + "\n")

    # Wait for processing
    await asyncio.sleep(0.2)

    # Stop watcher
    await watcher.stop()

    # Validate: EventWatcher should have detected and stored the event
    events = event_log.get_by_trace("test-001")
    assert len(events) > 0
    assert events[0]["trace_id"] == "test-001"
    assert events[0]["event_type"] == "chora.content_generated"


@pytest.mark.asyncio
async def test_tutorial_part2_step3_query_events(tmp_path: Path):
    """Validate tutorial Part 2, Step 3: Query Events.

    From tutorial:
    > After the EventWatcher has processed events, query them
    """
    # Setup: Create EventLog and emit test event
    event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")

    # Emit event directly (simulating EventWatcher processing)
    emit_event(
        event_type="chora.content_generated",
        trace_id="test-001",
        status="success",
        base_dir=event_log.base_dir,
        generator="test",
    )

    # Query all events for trace_id (from tutorial example)
    events = event_log.get_by_trace("test-001")

    # Validate (from tutorial expected output)
    assert len(events) == 1
    assert events[0]["event_type"] == "chora.content_generated"
    assert events[0]["trace_id"] == "test-001"


def test_tutorial_part2_step4_verify_event_storage(tmp_path: Path):
    """Validate tutorial Part 2, Step 4: Verify Event Storage.

    From tutorial:
    > Check that events are stored in the correct location
    """
    # Setup
    event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")

    # Emit event
    emit_event(
        event_type="chora.test",
        trace_id="test-001",
        status="success",
        base_dir=event_log.base_dir,
    )

    # Verify directory structure (from tutorial)
    events_dir = tmp_path / ".chora" / "memory" / "events"
    assert events_dir.exists()

    # Check monthly partition
    current_month = datetime.now(UTC).strftime("%Y-%m")
    month_dir = events_dir / current_month
    assert month_dir.exists()

    # Check events.jsonl file
    events_file = month_dir / "events.jsonl"
    assert events_file.exists()

    # Check trace-specific file
    trace_file = month_dir / "traces" / "test-001.jsonl"
    assert trace_file.exists()


# ============================================================================
# Part 3: Event Monitoring with n8n Webhooks
# ============================================================================


@pytest.mark.asyncio
async def test_tutorial_part3_step4_webhook_failure_graceful_degradation(
    tmp_path: Path,
):
    """Validate tutorial Part 3, Step 4: Handle Webhook Failures Gracefully.

    From tutorial:
    > Stop n8n and generate another event
    > Expected result: Event is STILL stored (graceful degradation!)
    """
    # Setup with invalid webhook URL
    events_file = tmp_path / "var" / "telemetry" / "events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)
    events_file.touch()

    event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    watcher = EventWatcher(
        event_log=event_log,
        events_file=str(events_file),
        n8n_webhook_url="http://localhost:9999/invalid",  # Webhook will fail
    )

    # Start watching
    await watcher.start()
    await asyncio.sleep(0.1)

    # Generate event (from tutorial example)
    test_event = {
        "timestamp": "2025-10-19T10:10:00Z",
        "trace_id": "test-failure-001",
        "status": "success",
        "schema_version": "1.0",
        "event_type": "chora.content_generated",
    }

    with events_file.open("a") as f:
        f.write(json.dumps(test_event) + "\n")

    # Wait for processing
    await asyncio.sleep(0.3)

    # Stop watcher
    await watcher.stop()

    # Validate: Event should STILL be stored despite webhook failure
    events = event_log.get_by_trace("test-failure-001")
    assert len(events) > 0, "Event should be stored even when webhook fails"


# ============================================================================
# Part 4: Querying Events with get_events Tool
# ============================================================================


@pytest.mark.asyncio
async def test_tutorial_part4_step1_query_by_trace_id(tmp_path: Path):
    """Validate tutorial Part 4, Step 1: Query by Trace ID.

    From tutorial:
    > Query all events for a specific trace
    """
    # Setup
    event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    set_event_log(event_log)

    # Emit test event
    emit_event(
        event_type="chora.content_generated",
        trace_id="test-001",
        status="success",
        base_dir=event_log.base_dir,
    )

    # Query (from tutorial example)
    events = await get_events(trace_id="test-001")

    # Validate (from tutorial expected output)
    assert len(events) == 1
    assert events[0]["event_type"] == "chora.content_generated"
    assert events[0]["status"] == "success"


@pytest.mark.asyncio
async def test_tutorial_part4_step2_query_by_event_type(tmp_path: Path):
    """Validate tutorial Part 4, Step 2: Query by Event Type.

    From tutorial:
    > Get all artifact assembly events
    """
    # Setup
    event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    set_event_log(event_log)

    # Emit different event types
    emit_event(
        event_type="chora.artifact_assembled",
        trace_id="test-001",
        status="success",
        base_dir=event_log.base_dir,
    )
    emit_event(
        event_type="chora.content_generated",
        trace_id="test-002",
        status="success",
        base_dir=event_log.base_dir,
    )

    # Query by event type (from tutorial example)
    events = await get_events(event_type="chora.artifact_assembled")

    # Validate
    assert len(events) > 0
    assert all(e["event_type"] == "chora.artifact_assembled" for e in events)


@pytest.mark.asyncio
async def test_tutorial_part4_step3_query_recent_events(tmp_path: Path):
    """Validate tutorial Part 4, Step 3: Query Recent Events.

    From tutorial:
    > Get all events from last 24 hours
    > Get all failures from last hour
    """
    # Setup
    event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    set_event_log(event_log)

    # Emit test events
    emit_event(
        event_type="chora.test",
        trace_id="test-success",
        status="success",
        base_dir=event_log.base_dir,
    )
    emit_event(
        event_type="chora.test",
        trace_id="test-failure",
        status="failure",
        base_dir=event_log.base_dir,
    )

    # Query from tutorial examples
    all_recent = await get_events(since="24h")
    assert len(all_recent) >= 2

    failures = await get_events(status="failure", since="1h")
    assert len(failures) >= 1
    assert all(e["status"] == "failure" for e in failures)


@pytest.mark.asyncio
async def test_tutorial_part4_step4_limit_results(tmp_path: Path):
    """Validate tutorial Part 4, Step 4: Limit Results.

    From tutorial:
    > Get last 10 events
    """
    # Setup
    event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    set_event_log(event_log)

    # Emit many events
    for i in range(50):
        emit_event(
            event_type="chora.test",
            trace_id=f"test-{i:03d}",
            status="success",
            base_dir=event_log.base_dir,
        )

    # Query with limit (from tutorial example)
    events = await get_events(limit=10)

    # Validate
    assert len(events) == 10


# ============================================================================
# Part 5: Trace ID Propagation (Gateway Integration)
# ============================================================================


@pytest.mark.asyncio
async def test_tutorial_part5_trace_id_propagation(tmp_path: Path):
    """Validate tutorial Part 5: Trace ID Propagation.

    From tutorial:
    > Example: Debugging a Multi-Step Workflow
    """
    # Setup
    event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    set_event_log(event_log)

    # Simulate gateway generating trace_id (from tutorial example)
    trace_id = str(uuid.uuid4())
    os.environ["CHORA_TRACE_ID"] = trace_id

    # Simulate backend operations (from tutorial example)
    # Step 1: Generate content
    emit_event(
        event_type="chora.content_generated",
        trace_id=trace_id,
        status="success",
        base_dir=event_log.base_dir,
        content_config_id="intro-section",
        duration_ms=234,
    )

    # Step 2: Assemble artifact
    emit_event(
        event_type="chora.artifact_assembled",
        trace_id=trace_id,
        status="success",
        base_dir=event_log.base_dir,
        artifact_config_id="daily-report",
        output_path="output/daily-report.md",
        section_count=4,
    )

    # Query the full workflow (from tutorial example)
    events = await get_events(trace_id=trace_id)

    # Validate (from tutorial expected output)
    assert len(events) == 2
    assert events[0]["event_type"] == "chora.content_generated"
    assert events[1]["event_type"] == "chora.artifact_assembled"
    assert all(e["trace_id"] == trace_id for e in events)
    assert all(e["status"] == "success" for e in events)

    # Cleanup
    del os.environ["CHORA_TRACE_ID"]


# ============================================================================
# Tutorial Completion Test
# ============================================================================


@pytest.mark.asyncio
async def test_tutorial_complete_end_to_end(tmp_path: Path):
    """End-to-end test validating the complete tutorial flow.

    This test combines all parts of the tutorial to ensure
    the entire workflow works together.
    """
    # Setup
    events_file = tmp_path / "var" / "telemetry" / "events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)
    events_file.touch()

    event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    set_event_log(event_log)

    # Part 1: Create and start EventWatcher
    watcher = EventWatcher(
        event_log=event_log,
        events_file=str(events_file),
        n8n_webhook_url=None,
    )
    await watcher.start()
    await asyncio.sleep(0.1)

    # Part 2: Generate trace ID
    trace_id = str(uuid.uuid4())
    os.environ["CHORA_TRACE_ID"] = trace_id

    # Part 3: Write events to file (simulating chora-compose)
    events_to_write = [
        {
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": trace_id,
            "status": "success",
            "schema_version": "1.0",
            "event_type": "chora.content_generated",
            "metadata": {"content_config_id": "intro"},
        },
        {
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": trace_id,
            "status": "success",
            "schema_version": "1.0",
            "event_type": "chora.artifact_assembled",
            "metadata": {"artifact_id": "daily-report"},
        },
    ]

    for event in events_to_write:
        with events_file.open("a") as f:
            f.write(json.dumps(event) + "\n")
        await asyncio.sleep(0.1)

    # Wait for processing
    await asyncio.sleep(0.3)

    # Stop watcher
    await watcher.stop()

    # Part 4: Query events by trace_id
    events = await get_events(trace_id=trace_id)

    # Part 5: Validate complete workflow
    assert len(events) == 2
    assert events[0]["event_type"] == "chora.content_generated"
    assert events[1]["event_type"] == "chora.artifact_assembled"
    assert all(e["trace_id"] == trace_id for e in events)
    assert all(e["status"] == "success" for e in events)

    # Cleanup
    del os.environ["CHORA_TRACE_ID"]

    # Tutorial Success!
    print("✅ Tutorial completed successfully!")
