"""Shared fixtures and mocks for smoke tests."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_chora_backend():
    """Mock Chora Composer backend for testing."""
    backend = MagicMock()
    backend.name = "chora-composer"
    backend.namespace = "chora"
    backend.enabled = True
    backend.capabilities = ["artifact_generation", "content_generation"]

    # Mock tool responses
    backend.call_tool = AsyncMock(
        return_value={"success": True, "data": "mock_chora_response"}
    )

    return backend


@pytest.fixture
def mock_coda_backend():
    """Mock Coda MCP backend for testing."""
    backend = MagicMock()
    backend.name = "coda-mcp"
    backend.namespace = "coda"
    backend.enabled = True
    backend.capabilities = ["data_operations"]

    # Mock tool responses
    backend.call_tool = AsyncMock(
        return_value={"success": True, "data": "mock_coda_response"}
    )

    return backend


@pytest.fixture
def mock_backend_registry(mock_chora_backend, mock_coda_backend):
    """Mock backend registry with both backends."""
    registry = MagicMock()
    registry.backends = {
        "chora-composer": mock_chora_backend,
        "coda-mcp": mock_coda_backend,
    }

    registry.get_backend = lambda name: registry.backends.get(name)
    registry.list_backends = lambda: list(registry.backends.values())
    registry.route_tool = AsyncMock(
        side_effect=lambda tool_name, args: mock_chora_backend.call_tool(
            tool_name, args
        )
        if tool_name.startswith("chora:")
        else mock_coda_backend.call_tool(tool_name, args)
    )

    return registry


@pytest.fixture
def sample_tool_call() -> dict[str, Any]:
    """Sample tool call structure."""
    return {
        "name": "chora:generate_content",
        "arguments": {
            "content_config_id": "test-config",
            "output_path": "/tmp/test.md",
        },
    }


@pytest.fixture
def sample_chora_tools() -> list[dict[str, Any]]:
    """Sample Chora Composer tools."""
    return [
        {
            "name": "chora:generate_content",
            "description": "Generate content from templates",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content_config_id": {"type": "string"},
                    "output_path": {"type": "string"},
                },
                "required": ["content_config_id"],
            },
        },
        {
            "name": "chora:assemble_artifact",
            "description": "Assemble artifacts from content pieces",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "artifact_config_id": {"type": "string"},
                    "output_path": {"type": "string"},
                },
                "required": ["artifact_config_id"],
            },
        },
    ]


@pytest.fixture
def sample_coda_tools() -> list[dict[str, Any]]:
    """Sample Coda MCP tools."""
    return [
        {
            "name": "coda:list_docs",
            "description": "List Coda documents",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "coda:list_tables",
            "description": "List tables in a document",
            "inputSchema": {
                "type": "object",
                "properties": {"doc_id": {"type": "string"}},
                "required": ["doc_id"],
            },
        },
    ]
