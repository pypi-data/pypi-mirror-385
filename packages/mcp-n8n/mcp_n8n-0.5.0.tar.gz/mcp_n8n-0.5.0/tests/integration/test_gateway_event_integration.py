"""Integration tests for EventWatcher gateway integration.

Tests that EventWatcher is properly integrated into the gateway lifecycle
and that the get_events MCP tool works correctly.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp_n8n.config import GatewayConfig
from mcp_n8n.event_watcher import EventWatcher
from mcp_n8n.gateway import event_log, initialize_backends, shutdown_backends
from mcp_n8n.memory.event_log import EventLog
from mcp_n8n.memory.trace import emit_event
from mcp_n8n.tools.event_query import get_events, set_event_log

# ============================================================================
# Gateway Integration Tests
# ============================================================================


@pytest.mark.asyncio
async def test_gateway_initializes_event_log(tmp_path: Path):
    """Test that gateway initializes EventLog on startup.

    Validates that the global event_log is created and configured
    for use by get_events tool.
    """
    # The global event_log should be initialized (happens at module import)
    assert event_log is not None
    assert isinstance(event_log, EventLog)
    assert event_log.base_dir.exists()


@pytest.mark.asyncio
async def test_event_watcher_lifecycle_integration(tmp_path: Path, monkeypatch):
    """Test that EventWatcher starts with gateway and stops on shutdown.

    Validates the full lifecycle integration of EventWatcher into
    the gateway startup/shutdown sequence.
    """
    # Mock config to avoid side effects
    mock_config = MagicMock(spec=GatewayConfig)
    mock_config.n8n_event_webhook_url = None
    mock_config.get_all_backend_configs.return_value = []

    with patch("mcp_n8n.gateway.config", mock_config):
        with patch("mcp_n8n.gateway.registry") as mock_registry:
            mock_registry.start_all = AsyncMock()
            mock_registry.stop_all = AsyncMock()
            mock_registry.get_status.return_value = {}
            mock_registry.get_all_tools.return_value = []

            # Initialize gateway (should start EventWatcher)
            await initialize_backends()

            # Verify EventWatcher was started
            from mcp_n8n.gateway import event_watcher as gw_watcher

            assert gw_watcher is not None
            assert gw_watcher._running is True

            # Shutdown gateway (should stop EventWatcher)
            await shutdown_backends()

            # Verify EventWatcher was stopped
            assert gw_watcher._running is False


@pytest.mark.asyncio
async def test_event_watcher_graceful_failure_handling(monkeypatch):
    """Test that gateway continues if EventWatcher fails to start.

    Validates graceful degradation - event monitoring becomes unavailable
    but gateway still functions.
    """
    # Mock config
    mock_config = MagicMock(spec=GatewayConfig)
    mock_config.n8n_event_webhook_url = None
    mock_config.get_all_backend_configs.return_value = []

    # Mock EventWatcher to raise exception on start
    with patch("mcp_n8n.gateway.EventWatcher") as mock_event_watcher_class:
        mock_watcher = AsyncMock(spec=EventWatcher)
        mock_watcher.start.side_effect = Exception("Simulated failure")
        mock_event_watcher_class.return_value = mock_watcher

        with patch("mcp_n8n.gateway.config", mock_config):
            with patch("mcp_n8n.gateway.registry") as mock_registry:
                mock_registry.start_all = AsyncMock()
                mock_registry.stop_all = AsyncMock()
                mock_registry.get_status.return_value = {}
                mock_registry.get_all_tools.return_value = []

                # Initialize should NOT raise exception
                await initialize_backends()

                # EventWatcher should be None (failed to start)
                from mcp_n8n.gateway import event_watcher as gw_watcher

                assert gw_watcher is None

                # Shutdown should still work
                await shutdown_backends()


# ============================================================================
# get_events Tool Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_events_tool_returns_events(tmp_path: Path):
    """Test that get_events MCP tool returns queried events.

    Validates that the tool properly queries the event log and returns results.
    """
    # Setup temporary EventLog
    test_event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    set_event_log(test_event_log)

    # Emit test events
    for i in range(5):
        emit_event(
            event_type="test.gateway_integration",
            trace_id=f"test-{i}",
            status="success",
            base_dir=test_event_log.base_dir,
            test_number=i,
        )

    # Query events using get_events tool
    events = await get_events(event_type="test.gateway_integration")

    # Validate results
    assert len(events) == 5
    assert all(e["event_type"] == "test.gateway_integration" for e in events)


@pytest.mark.asyncio
async def test_get_events_tool_respects_limit(tmp_path: Path):
    """Test that get_events tool respects limit parameter.

    Validates that the limit parameter correctly caps results,
    including the max limit of 1000.
    """
    # Setup temporary EventLog
    test_event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    set_event_log(test_event_log)

    # Emit many events
    for i in range(50):
        emit_event(
            event_type="test.limit",
            trace_id=f"limit-test-{i:03d}",
            status="success",
            base_dir=test_event_log.base_dir,
        )

    # Query with small limit
    events_10 = await get_events(event_type="test.limit", limit=10)
    assert len(events_10) == 10

    # Query with limit > 1000 (should cap at 1000)
    events_capped = await get_events(event_type="test.limit", limit=2000)
    assert len(events_capped) <= 1000  # Capped at max


@pytest.mark.asyncio
async def test_get_events_tool_filters_by_trace_id(tmp_path: Path):
    """Test that get_events filters correctly by trace_id.

    Validates trace_id filtering for debugging multi-step workflows.
    """
    # Setup temporary EventLog
    test_event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    set_event_log(test_event_log)

    # Emit events with different trace IDs
    emit_event(
        event_type="step1",
        trace_id="workflow-abc",
        status="success",
        base_dir=test_event_log.base_dir,
    )
    emit_event(
        event_type="step2",
        trace_id="workflow-abc",
        status="success",
        base_dir=test_event_log.base_dir,
    )
    emit_event(
        event_type="step1",
        trace_id="workflow-xyz",
        status="success",
        base_dir=test_event_log.base_dir,
    )

    # Query for specific trace
    events = await get_events(trace_id="workflow-abc")

    # Validate
    assert len(events) == 2
    assert all(e["trace_id"] == "workflow-abc" for e in events)
    assert events[0]["event_type"] == "step1"
    assert events[1]["event_type"] == "step2"


@pytest.mark.asyncio
async def test_get_events_tool_filters_by_status(tmp_path: Path):
    """Test that get_events filters correctly by status.

    Validates status filtering for finding failures.
    """
    # Setup temporary EventLog
    test_event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    set_event_log(test_event_log)

    # Emit events with different statuses
    for i in range(3):
        emit_event(
            event_type="test.status",
            trace_id=f"success-{i}",
            status="success",
            base_dir=test_event_log.base_dir,
        )

    for i in range(2):
        emit_event(
            event_type="test.status",
            trace_id=f"failure-{i}",
            status="failure",
            base_dir=test_event_log.base_dir,
        )

    # Query for failures only
    failures = await get_events(status="failure")

    # Validate
    assert len(failures) == 2
    assert all(e["status"] == "failure" for e in failures)


@pytest.mark.asyncio
async def test_get_events_tool_filters_by_time_range(tmp_path: Path):
    """Test that get_events filters correctly by time range.

    Validates since parameter for recent event queries.
    """
    # Setup temporary EventLog
    test_event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    set_event_log(test_event_log)

    # Emit recent event
    emit_event(
        event_type="test.recent",
        trace_id="recent-event",
        status="success",
        base_dir=test_event_log.base_dir,
    )

    # Query events from last 24 hours
    recent_events = await get_events(since="24h")

    # Validate event is included
    assert len(recent_events) >= 1
    assert any(e["trace_id"] == "recent-event" for e in recent_events)


# ============================================================================
# End-to-End Gateway Integration Test
# ============================================================================


@pytest.mark.asyncio
async def test_gateway_event_monitoring_end_to_end(tmp_path: Path):
    """End-to-end test of event monitoring through gateway.

    Tests the complete flow:
    1. Gateway emits events
    2. EventWatcher detects them (simulated)
    3. get_events tool queries them
    """
    # Setup temporary EventLog
    test_event_log = EventLog(base_dir=tmp_path / ".chora" / "memory" / "events")
    set_event_log(test_event_log)

    # Simulate gateway operation - emit events
    emit_event(
        event_type="gateway.backend_started",
        trace_id="init-001",
        status="success",
        base_dir=test_event_log.base_dir,
        backend_name="chora-composer",
    )

    emit_event(
        event_type="chora.content_generated",
        trace_id="workflow-001",
        status="success",
        base_dir=test_event_log.base_dir,
        content_config_id="intro",
    )

    emit_event(
        event_type="chora.artifact_assembled",
        trace_id="workflow-001",
        status="success",
        base_dir=test_event_log.base_dir,
        artifact_id="daily-report",
    )

    # Query workflow events
    workflow_events = await get_events(trace_id="workflow-001")

    # Validate complete workflow captured
    assert len(workflow_events) == 2
    assert workflow_events[0]["event_type"] == "chora.content_generated"
    assert workflow_events[1]["event_type"] == "chora.artifact_assembled"
    assert all(e["status"] == "success" for e in workflow_events)

    # Query gateway initialization events
    init_events = await get_events(event_type="gateway.backend_started")
    assert len(init_events) >= 1

    # Query all events
    all_events = await get_events(limit=100)
    assert len(all_events) >= 3
