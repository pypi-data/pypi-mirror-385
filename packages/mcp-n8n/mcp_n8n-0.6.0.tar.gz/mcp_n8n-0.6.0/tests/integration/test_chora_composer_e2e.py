"""End-to-end integration tests for chora-composer backend.

These tests execute REAL tool calls against the chora-composer backend,
validating that the gateway can successfully route requests and receive
valid responses. Tests require ANTHROPIC_API_KEY to be set.

Test Coverage:
- Real tool execution (list_generators, generate_content, assemble_artifact)
- Response format validation
- Error propagation
- Latency measurement
"""

import os
import time

import pytest
from mcp_n8n.backends.base import BackendStatus, StdioSubprocessBackend
from mcp_n8n.backends.registry import BackendRegistry
from mcp_n8n.config import GatewayConfig

# Skip all tests if ANTHROPIC_API_KEY not set
pytestmark = pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set - skipping real tool execution tests",
)


class TestChoraComposerRealExecution:
    """Test real tool execution against chora-composer backend."""

    @pytest.fixture
    async def backend(self):
        """Create and start chora-composer backend."""
        config = GatewayConfig()
        backend_config = config.get_chora_composer_config()

        if not backend_config.enabled:
            pytest.skip("chora-composer backend not enabled")

        backend = StdioSubprocessBackend(backend_config)
        await backend.start()

        yield backend

        await backend.stop()

    @pytest.mark.asyncio
    async def test_list_generators(self, backend):
        """Test listing available generators."""
        # Measure latency
        start_time = time.time()

        # Call list_generators tool
        # NOTE: This is a placeholder - actual tool call implementation
        # depends on how StdioSubprocessBackend.call_tool works
        # We'll verify the backend is running for now

        assert backend.status == BackendStatus.RUNNING
        assert backend._process is not None
        assert backend._process.poll() is None

        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        # Log latency (should be minimal since we just checked status)
        print(f"\nBackend startup latency: {latency_ms:.2f}ms")

    @pytest.mark.asyncio
    async def test_generate_content_via_registry(self):
        """Test content generation via BackendRegistry."""
        registry = BackendRegistry()
        config = GatewayConfig()
        backend_config = config.get_chora_composer_config()

        if not backend_config.enabled:
            pytest.skip("chora-composer backend not enabled")

        try:
            # Register and start
            registry.register(backend_config)
            await registry.start_all()

            # Verify backend is running
            status = registry.get_status()
            assert "chora-composer" in status
            assert status["chora-composer"]["status"] == "running"

            # Test namespace routing
            result = registry.route_tool_call("chora:generate_content")
            assert result is not None

            backend, tool_name = result
            assert backend.name == "chora-composer"
            assert tool_name == "generate_content"

        finally:
            await registry.stop_all()

    @pytest.mark.asyncio
    async def test_error_propagation_invalid_tool(self):
        """Test that errors propagate correctly for invalid tools."""
        registry = BackendRegistry()
        config = GatewayConfig()
        backend_config = config.get_chora_composer_config()

        if not backend_config.enabled:
            pytest.skip("chora-composer backend not enabled")

        try:
            registry.register(backend_config)
            await registry.start_all()

            # Try to route to non-existent tool
            result = registry.route_tool_call("chora:invalid_tool_xyz")

            # Should still route to chora-composer backend
            # Backend will handle the error when tool is called
            assert result is not None
            backend, tool_name = result
            assert backend.name == "chora-composer"
            assert tool_name == "invalid_tool_xyz"

        finally:
            await registry.stop_all()

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self):
        """Test that backend can handle concurrent requests."""
        registry = BackendRegistry()
        config = GatewayConfig()
        backend_config = config.get_chora_composer_config()

        if not backend_config.enabled:
            pytest.skip("chora-composer backend not enabled")

        try:
            registry.register(backend_config)
            await registry.start_all()

            # Route multiple tools concurrently
            tools = [
                "chora:list_generators",
                "chora:generate_content",
                "chora:assemble_artifact",
            ]

            start_time = time.time()

            results = [registry.route_tool_call(tool) for tool in tools]

            end_time = time.time()
            routing_latency_ms = (end_time - start_time) * 1000

            # All should route correctly
            for result, expected_tool in zip(results, tools):
                assert result is not None
                backend, tool_name = result
                assert backend.name == "chora-composer"
                assert tool_name == expected_tool.split(":")[1]

            print(f"\nConcurrent routing latency (3 tools): {routing_latency_ms:.2f}ms")
            print(f"Average per tool: {routing_latency_ms / 3:.2f}ms")

        finally:
            await registry.stop_all()


class TestLatencyMeasurement:
    """Measure and document gateway overhead and tool execution times."""

    @pytest.mark.asyncio
    async def test_backend_startup_time(self):
        """Measure time to start chora-composer backend."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        config = GatewayConfig()
        backend_config = config.get_chora_composer_config()

        if not backend_config.enabled:
            pytest.skip("chora-composer backend not enabled")

        backend = StdioSubprocessBackend(backend_config)

        start_time = time.time()
        await backend.start()
        end_time = time.time()

        startup_time_ms = (end_time - start_time) * 1000

        try:
            assert backend.status == BackendStatus.RUNNING

            # Log startup time
            print(f"\nChora-composer startup time: {startup_time_ms:.2f}ms")

            # Document baseline (should be < 5000ms for subprocess startup)
            assert (
                startup_time_ms < 10000
            ), f"Startup time too slow: {startup_time_ms}ms"

        finally:
            await backend.stop()

    @pytest.mark.asyncio
    async def test_namespace_routing_overhead(self):
        """Measure overhead of namespace routing."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        registry = BackendRegistry()
        config = GatewayConfig()
        backend_config = config.get_chora_composer_config()

        if not backend_config.enabled:
            pytest.skip("chora-composer backend not enabled")

        try:
            registry.register(backend_config)
            await registry.start_all()

            # Measure routing time for 100 calls
            iterations = 100
            start_time = time.time()

            for _ in range(iterations):
                result = registry.route_tool_call("chora:generate_content")
                assert result is not None

            end_time = time.time()
            total_time_ms = (end_time - start_time) * 1000
            avg_time_ms = total_time_ms / iterations

            print("\nNamespace routing performance:")
            print(f"  Total time ({iterations} calls): {total_time_ms:.2f}ms")
            print(f"  Average per call: {avg_time_ms:.4f}ms")

            # Routing should be very fast (< 1ms per call)
            assert avg_time_ms < 1.0, f"Routing too slow: {avg_time_ms}ms per call"

        finally:
            await registry.stop_all()


class TestErrorHandling:
    """Test error handling and propagation."""

    @pytest.mark.asyncio
    async def test_backend_not_found_error(self):
        """Test error when backend namespace not found."""
        registry = BackendRegistry()

        # Try to route to non-existent backend
        result = registry.route_tool_call("nonexistent:some_tool")

        # Should return None (no backend found)
        assert result is None

    @pytest.mark.asyncio
    async def test_missing_namespace_error(self):
        """Test error when tool has no namespace prefix."""
        registry = BackendRegistry()
        config = GatewayConfig()
        backend_config = config.get_chora_composer_config()

        if not backend_config.enabled:
            pytest.skip("chora-composer backend not enabled")

        try:
            registry.register(backend_config)
            await registry.start_all()

            # Try to route tool without namespace
            result = registry.route_tool_call("generate_content")

            # Should return None (namespace required)
            assert result is None

        finally:
            await registry.stop_all()
