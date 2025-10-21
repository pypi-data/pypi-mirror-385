"""Unit tests for EventWorkflowRouter.

Tests the event-to-workflow routing logic, pattern matching, parameter templating,
and config hot-reload functionality.
"""
# mypy: disable-error-code="no-untyped-def"

import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
import yaml
from mcp_n8n.workflows.event_router import EventWorkflowRouter

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_event_mappings() -> dict[str, Any]:
    """Sample event-to-workflow mappings for testing."""
    return {
        "mappings": [
            {
                "event_pattern": {
                    "type": "gateway.tool_call",
                    "status": "failure",
                },
                "workflow": {
                    "id": "error-alert-workflow",
                    "parameters": {
                        "error": "{{ event.data.error }}",
                        "tool": "{{ event.data.tool_name }}",
                    },
                },
            },
            {
                "event_pattern": {
                    "type": "gateway.tool_call",
                },
                "workflow": {
                    "id": "tool-call-logger",
                    "parameters": {},
                },
            },
            {
                "event_pattern": {
                    "type": "gateway.backend_status",
                    "backend": "chora-composer",
                },
                "workflow": {
                    "id": "chora-status-monitor",
                    "parameters": {
                        "backend": "{{ event.backend }}",
                        "status": "{{ event.data.status }}",
                    },
                },
            },
        ]
    }


@pytest.fixture
def config_file(tmp_path: Path, sample_event_mappings: dict[str, Any]) -> Path:
    """Create a temporary config file with sample mappings."""
    config_path = tmp_path / "event_mappings.yaml"
    config_path.write_text(yaml.dump(sample_event_mappings))
    return config_path


@pytest.fixture
def mock_backend_registry():
    """Mock BackendRegistry for testing."""
    registry = Mock()
    registry.get_backend_by_namespace = Mock(return_value=Mock())
    return registry


@pytest.fixture
def sample_event() -> dict[str, Any]:
    """Sample event for testing."""
    return {
        "type": "gateway.tool_call",
        "status": "failure",
        "backend": "chora-composer",
        "timestamp": "2025-10-20T10:00:00Z",
        "data": {
            "tool_name": "generate_content",
            "error": "Template not found",
            "trace_id": "abc123",
        },
    }


# ============================================================================
# Test: Initialization and Config Loading
# ============================================================================


def test_router_init_with_valid_config(config_file: Path, mock_backend_registry):
    """Test EventWorkflowRouter initialization with valid config."""
    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )

    assert router.config_path == str(config_file)
    assert router.backend_registry == mock_backend_registry
    assert router.mappings == []  # Not loaded until load_mappings() called


def test_router_init_with_missing_config(tmp_path: Path, mock_backend_registry):
    """Test EventWorkflowRouter initialization with missing config file."""
    missing_config = tmp_path / "nonexistent.yaml"

    with pytest.raises(FileNotFoundError) as exc_info:
        EventWorkflowRouter(
            config_path=str(missing_config),
            backend_registry=mock_backend_registry,
        )

    assert "event_mappings.yaml" in str(exc_info.value).lower() or "nonexistent" in str(
        exc_info.value
    )


@pytest.mark.asyncio
async def test_load_mappings_success(
    config_file: Path, mock_backend_registry, sample_event_mappings
):
    """Test loading mappings from YAML config."""
    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )

    mappings = await router.load_mappings()

    assert len(mappings) == 3
    assert mappings[0]["event_pattern"]["type"] == "gateway.tool_call"
    assert mappings[0]["event_pattern"]["status"] == "failure"
    assert mappings[0]["workflow"]["id"] == "error-alert-workflow"


@pytest.mark.asyncio
async def test_load_mappings_invalid_yaml(tmp_path: Path, mock_backend_registry):
    """Test loading mappings from invalid YAML."""
    invalid_config = tmp_path / "invalid.yaml"
    invalid_config.write_text("invalid: yaml: content: [unclosed")

    router = EventWorkflowRouter(
        config_path=str(invalid_config),
        backend_registry=mock_backend_registry,
    )

    with pytest.raises(yaml.YAMLError):
        await router.load_mappings()


@pytest.mark.asyncio
async def test_load_mappings_missing_required_fields(
    tmp_path: Path, mock_backend_registry
):
    """Test loading mappings with missing required fields."""
    invalid_mappings = {
        "mappings": [
            {
                "event_pattern": {"type": "gateway.tool_call"},
                # Missing "workflow" field
            }
        ]
    }

    config_path = tmp_path / "invalid_structure.yaml"
    config_path.write_text(yaml.dump(invalid_mappings))

    router = EventWorkflowRouter(
        config_path=str(config_path),
        backend_registry=mock_backend_registry,
    )

    with pytest.raises((KeyError, ValueError)):
        await router.load_mappings()


# ============================================================================
# Test: Event Matching Logic
# ============================================================================


@pytest.mark.asyncio
async def test_match_event_exact_match(
    config_file: Path, mock_backend_registry, sample_event
):
    """Test matching event with exact pattern match."""
    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()

    # Event matches first mapping (type + status)
    result = await router.match_event(sample_event)

    assert result is not None
    assert result["workflow_id"] == "error-alert-workflow"
    assert "parameters" in result


@pytest.mark.asyncio
async def test_match_event_partial_match(config_file: Path, mock_backend_registry):
    """Test matching event with partial pattern (subset of fields)."""
    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()

    # Event with only "type" field (should match second mapping)
    event = {
        "type": "gateway.tool_call",
        "status": "success",  # Different status, but pattern doesn't specify
        "data": {},
    }

    result = await router.match_event(event)

    assert result is not None
    # Should match second mapping (only requires "type")
    assert result["workflow_id"] == "tool-call-logger"


@pytest.mark.asyncio
async def test_match_event_no_match(config_file: Path, mock_backend_registry):
    """Test matching event when no patterns match."""
    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()

    # Event that doesn't match any patterns
    event = {
        "type": "coda.document_updated",
        "status": "success",
        "data": {},
    }

    result = await router.match_event(event)

    assert result is None


@pytest.mark.asyncio
async def test_match_event_first_match_wins(
    config_file: Path, mock_backend_registry, sample_event
):
    """Test that first matching pattern wins (short-circuit)."""
    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()

    # sample_event matches both mapping 1 (type+status) and mapping 2 (type only)
    # Should return mapping 1 (first match)
    result = await router.match_event(sample_event)

    assert result is not None
    assert result["workflow_id"] == "error-alert-workflow"  # First mapping


@pytest.mark.asyncio
async def test_match_event_with_missing_fields(
    config_file: Path, mock_backend_registry
):
    """Test matching event with missing fields in event data."""
    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()

    # Event missing fields required by pattern
    event = {
        "type": "gateway.backend_status",
        # Missing "backend" field required by third mapping
        "data": {},
    }

    result = await router.match_event(event)

    # Should not match third mapping (missing "backend")
    # Should not match first two mappings (different type)
    assert result is None


# ============================================================================
# Test: Parameter Templating
# ============================================================================


@pytest.mark.asyncio
async def test_template_parameters_simple(
    config_file: Path, mock_backend_registry, sample_event
):
    """Test parameter templating with simple variable substitution."""
    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()

    result = await router.match_event(sample_event)

    assert result is not None
    assert result["parameters"]["error"] == "Template not found"
    assert result["parameters"]["tool"] == "generate_content"


@pytest.mark.asyncio
async def test_template_parameters_missing_field(
    config_file: Path, mock_backend_registry
):
    """Test parameter templating when event is missing referenced field."""
    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()

    # Event missing data.error field
    event = {
        "type": "gateway.tool_call",
        "status": "failure",
        "data": {
            "tool_name": "generate_content",
            # Missing "error" field
        },
    }

    result = await router.match_event(event)

    assert result is not None
    # Should use empty string or None for missing field
    assert result["parameters"]["error"] in ("", None, "")
    assert result["parameters"]["tool"] == "generate_content"


@pytest.mark.asyncio
async def test_template_parameters_nested_access(
    config_file: Path, mock_backend_registry
):
    """Test parameter templating with nested field access."""
    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()

    event = {
        "type": "gateway.backend_status",
        "backend": "chora-composer",
        "data": {
            "status": "healthy",
            "nested": {
                "field": "value",
            },
        },
    }

    result = await router.match_event(event)

    assert result is not None
    assert result["workflow_id"] == "chora-status-monitor"
    assert result["parameters"]["backend"] == "chora-composer"
    assert result["parameters"]["status"] == "healthy"


# ============================================================================
# Test: Config Hot Reload
# ============================================================================


@pytest.mark.asyncio
async def test_hot_reload_valid_config(
    tmp_path: Path, mock_backend_registry, sample_event_mappings
):
    """Test hot reload with valid config modification."""
    config_path = tmp_path / "event_mappings.yaml"
    config_path.write_text(yaml.dump(sample_event_mappings))

    router = EventWorkflowRouter(
        config_path=str(config_path),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()
    assert len(router.mappings) == 3

    # Modify config to add a new mapping
    new_mappings = sample_event_mappings.copy()
    new_mappings["mappings"].append(
        {
            "event_pattern": {"type": "new.event"},
            "workflow": {"id": "new-workflow", "parameters": {}},
        }
    )
    config_path.write_text(yaml.dump(new_mappings))

    # Trigger reload
    await router.reload_config()

    assert len(router.mappings) == 4


@pytest.mark.asyncio
async def test_hot_reload_invalid_config_keeps_previous(
    tmp_path: Path, mock_backend_registry, sample_event_mappings
):
    """Test hot reload with invalid config keeps previous valid config."""
    config_path = tmp_path / "event_mappings.yaml"
    config_path.write_text(yaml.dump(sample_event_mappings))

    router = EventWorkflowRouter(
        config_path=str(config_path),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()
    original_mappings = router.mappings.copy()
    assert len(original_mappings) == 3

    # Modify config with invalid YAML
    config_path.write_text("invalid: yaml: [unclosed")

    # Trigger reload (should fail gracefully)
    with pytest.raises(yaml.YAMLError):
        await router.reload_config()

    # Should keep previous valid config
    assert router.mappings == original_mappings
    assert len(router.mappings) == 3


@pytest.mark.asyncio
async def test_start_watching_file(
    tmp_path: Path, mock_backend_registry, sample_event_mappings
):
    """Test file watching for config changes."""
    config_path = tmp_path / "event_mappings.yaml"
    config_path.write_text(yaml.dump(sample_event_mappings))

    router = EventWorkflowRouter(
        config_path=str(config_path),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()

    # Start watching in background
    watch_task = asyncio.create_task(router.start_watching())

    # Give watcher time to start
    await asyncio.sleep(0.1)

    # Modify config
    new_mappings = sample_event_mappings.copy()
    new_mappings["mappings"].append(
        {
            "event_pattern": {"type": "watched.event"},
            "workflow": {"id": "watched-workflow", "parameters": {}},
        }
    )
    config_path.write_text(yaml.dump(new_mappings))

    # Give watcher time to detect change
    await asyncio.sleep(1.5)

    # Should have reloaded
    assert len(router.mappings) == 4

    # Stop watching
    watch_task.cancel()
    try:
        await watch_task
    except asyncio.CancelledError:
        pass


# ============================================================================
# Test: Workflow Triggering
# ============================================================================


@pytest.mark.asyncio
async def test_trigger_workflow_via_backend(
    config_file: Path, mock_backend_registry, sample_event
):
    """Test triggering workflow via backend registry."""
    mock_n8n_backend = AsyncMock()
    mock_backend_registry.get_backend_by_namespace.return_value = mock_n8n_backend

    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()

    # Trigger workflow
    await router.trigger_workflow(
        workflow_id="error-alert-workflow",
        parameters={"error": "Test error", "tool": "test_tool"},
    )

    # Should have called backend
    mock_backend_registry.get_backend_by_namespace.assert_called_once()
    mock_n8n_backend.call_tool.assert_called_once()


@pytest.mark.asyncio
async def test_trigger_workflow_backend_unavailable(
    config_file: Path, mock_backend_registry
):
    """Test triggering workflow when backend is unavailable."""
    mock_backend_registry.get_backend_by_namespace.return_value = None

    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()

    # Should log warning and not raise exception
    await router.trigger_workflow(
        workflow_id="error-alert-workflow",
        parameters={"error": "Test error"},
    )

    # No exception raised, gracefully degraded


# ============================================================================
# Test: Edge Cases
# ============================================================================


@pytest.mark.asyncio
async def test_empty_mappings_config(tmp_path: Path, mock_backend_registry):
    """Test loading config with empty mappings list."""
    empty_config = tmp_path / "empty.yaml"
    empty_config.write_text(yaml.dump({"mappings": []}))

    router = EventWorkflowRouter(
        config_path=str(empty_config),
        backend_registry=mock_backend_registry,
    )

    mappings = await router.load_mappings()
    assert mappings == []


@pytest.mark.asyncio
async def test_match_event_empty_event(config_file: Path, mock_backend_registry):
    """Test matching empty event dict."""
    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()

    result = await router.match_event({})
    assert result is None


@pytest.mark.asyncio
async def test_concurrent_event_matching(
    config_file: Path, mock_backend_registry, sample_event
):
    """Test concurrent event matching (thread safety)."""
    router = EventWorkflowRouter(
        config_path=str(config_file),
        backend_registry=mock_backend_registry,
    )
    await router.load_mappings()

    # Match multiple events concurrently
    tasks = [router.match_event(sample_event) for _ in range(10)]
    results = await asyncio.gather(*tasks)

    # All should return same result
    assert all(r is not None for r in results)
    assert all(
        r["workflow_id"] == "error-alert-workflow" for r in results if r is not None
    )
