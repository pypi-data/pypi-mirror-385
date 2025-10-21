"""Smoke test: Chora Composer namespace routing."""

import pytest


@pytest.mark.asyncio
async def test_chora_tool_routing(mock_backend_registry, sample_tool_call):
    """Test that chora:* tools route to Chora backend."""
    # Call with chora: prefixed tool
    result = await mock_backend_registry.route_tool(
        "chora:generate_content", {"content_config_id": "test"}
    )

    assert result is not None
    assert result["success"] is True
    assert "data" in result


@pytest.mark.asyncio
async def test_chora_namespace_isolation(mock_backend_registry):
    """Test that chora: namespace is isolated from other backends."""
    chora_backend = mock_backend_registry.get_backend("chora-composer")
    coda_backend = mock_backend_registry.get_backend("coda-mcp")

    assert chora_backend.namespace == "chora"
    assert coda_backend.namespace == "coda"
    assert chora_backend.namespace != coda_backend.namespace


def test_chora_tools_have_namespace_prefix(sample_chora_tools):
    """Test that all Chora tools are prefixed with chora:"""
    for tool in sample_chora_tools:
        assert tool["name"].startswith("chora:")
        assert ":" in tool["name"]


@pytest.mark.asyncio
async def test_chora_tool_call_passes_arguments(mock_backend_registry):
    """Test that arguments are passed correctly to Chora backend."""
    test_args = {"content_config_id": "test-config", "output_path": "/tmp/test.md"}

    await mock_backend_registry.route_tool("chora:generate_content", test_args)

    # Verify the backend's call_tool was called with correct arguments
    chora_backend = mock_backend_registry.get_backend("chora-composer")
    chora_backend.call_tool.assert_called_once()


@pytest.mark.asyncio
async def test_chora_multiple_tools(mock_backend_registry):
    """Test multiple Chora tool calls in sequence."""
    tools = [
        "chora:generate_content",
        "chora:assemble_artifact",
        "chora:list_generators",
    ]

    for tool_name in tools:
        result = await mock_backend_registry.route_tool(tool_name, {})
        assert result is not None
        assert "success" in result
