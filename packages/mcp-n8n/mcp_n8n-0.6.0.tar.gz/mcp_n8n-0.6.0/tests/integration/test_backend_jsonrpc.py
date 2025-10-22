"""Integration tests for backend JSON-RPC communication.

Tests real JSON-RPC communication with chora-compose MCP server.
"""
# mypy: disable-error-code="no-untyped-def"

import logging

import pytest
from mcp_n8n.backends.base import BackendStatus
from mcp_n8n.backends.chora_composer import ChoraComposerBackend
from mcp_n8n.config import BackendConfig, BackendType

# Enable debug logging for these tests
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
async def chora_backend():
    """Create and start a real chora-compose backend."""
    config = BackendConfig(
        name="chora-composer-test",
        type=BackendType.STDIO_SUBPROCESS,
        command="python3.12",
        args=["-m", "chora_compose.mcp.server"],
        namespace="chora",
        capabilities=["artifacts"],
        timeout=10,
        env={},
    )

    backend = ChoraComposerBackend(config)

    try:
        await backend.start()
        yield backend
    finally:
        await backend.stop()


@pytest.mark.asyncio
async def test_backend_starts_and_initializes(chora_backend):
    """Test that backend starts and initializes successfully."""
    assert chora_backend.status == BackendStatus.RUNNING


@pytest.mark.asyncio
async def test_backend_discovers_tools(chora_backend):
    """Test that backend discovers tools during initialization."""
    tools = chora_backend.get_tools()

    assert len(tools) > 0, "Backend should discover at least one tool"

    # Check for expected chora tools
    tool_names = [tool["name"] for tool in tools]
    assert "chora:generate_content" in tool_names
    assert "chora:assemble_artifact" in tool_names

    print(f"Discovered tools: {tool_names}")


@pytest.mark.asyncio
async def test_backend_call_list_generators(chora_backend):
    """Test calling list_generators tool via JSON-RPC."""
    try:
        result = await chora_backend.call_tool("list_generators", {})

        assert result is not None
        assert isinstance(result, dict)

        print(f"list_generators result: {result}")

    except Exception as e:
        pytest.fail(f"Tool call failed: {e}")


@pytest.mark.asyncio
async def test_backend_call_nonexistent_tool(chora_backend):
    """Test that calling a non-existent tool fails gracefully."""
    from mcp_n8n.backends.base import BackendError

    with pytest.raises(BackendError):
        await chora_backend.call_tool("nonexistent_tool", {})


@pytest.mark.asyncio
async def test_multiple_sequential_tool_calls(chora_backend):
    """Test making multiple tool calls in sequence."""
    # Call list_generators multiple times
    for i in range(3):
        result = await chora_backend.call_tool("list_generators", {})
        assert result is not None
        print(f"Call {i+1}: {result}")
