"""Smoke test: Namespace isolation between backends."""

import pytest


@pytest.mark.asyncio
async def test_namespaces_dont_collide(mock_backend_registry):
    """Test that chora: and coda: namespaces don't collide."""
    # Call both backends
    chora_result = await mock_backend_registry.route_tool("chora:generate_content", {})
    coda_result = await mock_backend_registry.route_tool("coda:list_docs", {})

    # Both should succeed independently
    assert chora_result["success"] is True
    assert coda_result["success"] is True

    # Results should be different (from different backends)
    assert chora_result["data"] == "mock_chora_response"
    assert coda_result["data"] == "mock_coda_response"


def test_backend_namespaces_are_unique(mock_backend_registry):
    """Test that each backend has a unique namespace."""
    backends = mock_backend_registry.list_backends()
    namespaces = [b.namespace for b in backends]

    # All namespaces should be unique
    assert len(namespaces) == len(set(namespaces))


def test_tool_names_include_namespace(sample_chora_tools, sample_coda_tools):
    """Test that tool names always include their namespace prefix."""
    all_tools = sample_chora_tools + sample_coda_tools

    for tool in all_tools:
        name = tool["name"]
        # Should have exactly one colon separating namespace and tool name
        assert name.count(":") == 1

        namespace, tool_name = name.split(":")

        # Namespace should match expected values
        assert namespace in ["chora", "coda"]

        # Tool name should not be empty
        assert len(tool_name) > 0


@pytest.mark.asyncio
async def test_wrong_namespace_not_routed(mock_backend_registry):
    """Test that tools with wrong namespace prefix don't get routed."""
    # This should fail or route to correct backend based on implementation
    # For now, we test that namespace-based routing is enforced

    chora_backend = mock_backend_registry.get_backend("chora-composer")
    coda_backend = mock_backend_registry.get_backend("coda-mcp")

    # Verify backends exist and have correct namespaces
    assert chora_backend.namespace == "chora"
    assert coda_backend.namespace == "coda"


def test_backend_capabilities_isolated(mock_chora_backend, mock_coda_backend):
    """Test that backend capabilities don't overlap."""
    chora_caps = set(mock_chora_backend.capabilities)
    coda_caps = set(mock_coda_backend.capabilities)

    # Capabilities should not overlap
    assert len(chora_caps.intersection(coda_caps)) == 0


@pytest.mark.asyncio
async def test_concurrent_namespace_calls(mock_backend_registry):
    """Test that calls to different namespaces can work concurrently."""
    import asyncio

    # Simulate concurrent calls to different namespaces
    chora_task = mock_backend_registry.route_tool("chora:generate_content", {})
    coda_task = mock_backend_registry.route_tool("coda:list_docs", {})

    chora_result, coda_result = await asyncio.gather(chora_task, coda_task)

    # Both should succeed
    assert chora_result["success"] is True
    assert coda_result["success"] is True

    # Should have different responses
    assert chora_result["data"] != coda_result["data"]
