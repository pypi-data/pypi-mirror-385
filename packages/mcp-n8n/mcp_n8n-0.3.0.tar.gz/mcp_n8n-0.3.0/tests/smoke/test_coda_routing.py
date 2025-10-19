"""Smoke test: Coda MCP namespace routing."""

import pytest


@pytest.mark.asyncio
async def test_coda_tool_routing(mock_backend_registry):
    """Test that coda:* tools route to Coda backend."""
    result = await mock_backend_registry.route_tool("coda:list_docs", {})

    assert result is not None
    assert result["success"] is True
    assert "data" in result


@pytest.mark.asyncio
async def test_coda_namespace_isolation(mock_backend_registry):
    """Test that coda: namespace is isolated from Chora."""
    coda_backend = mock_backend_registry.get_backend("coda-mcp")

    assert coda_backend.namespace == "coda"
    assert coda_backend.namespace != "chora"


def test_coda_tools_have_namespace_prefix(sample_coda_tools):
    """Test that all Coda tools are prefixed with coda:"""
    for tool in sample_coda_tools:
        assert tool["name"].startswith("coda:")
        assert ":" in tool["name"]


@pytest.mark.asyncio
async def test_coda_tool_with_arguments(mock_backend_registry):
    """Test Coda tool calls with arguments."""
    test_args = {"doc_id": "test-doc-123"}

    result = await mock_backend_registry.route_tool("coda:list_tables", test_args)

    assert result is not None
    assert result["success"] is True


@pytest.mark.asyncio
async def test_coda_multiple_tools(mock_backend_registry):
    """Test multiple Coda tool calls in sequence."""
    tools = [
        ("coda:list_docs", {}),
        ("coda:list_tables", {"doc_id": "test"}),
        ("coda:list_rows", {"doc_id": "test", "table_id": "table1"}),
    ]

    for tool_name, args in tools:
        result = await mock_backend_registry.route_tool(tool_name, args)
        assert result is not None
        assert "success" in result
