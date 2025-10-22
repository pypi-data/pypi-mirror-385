"""Integration tests for gateway subprocess communication.

Tests that the gateway can properly communicate with backend MCP servers
via STDIO subprocess, using a mock server to validate the architecture.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest
from mcp_n8n.backends.base import BackendStatus, StdioSubprocessBackend
from mcp_n8n.backends.registry import BackendRegistry
from mcp_n8n.config import BackendConfig, BackendType

# Path to mock MCP server
MOCK_SERVER = Path(__file__).parent / "mock_mcp_server.py"


class TestSubprocessCommunication:
    """Test subprocess communication with mock MCP server."""

    def test_mock_server_runs_standalone(self) -> None:
        """Test that mock server can run and respond to basic request."""
        # Start mock server
        proc = subprocess.Popen(
            [sys.executable, str(MOCK_SERVER)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            # Send initialize request
            request = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
            proc.stdin.write(json.dumps(request) + "\n")  # type: ignore
            proc.stdin.flush()  # type: ignore

            # Read response (with timeout)
            response_line = proc.stdout.readline()  # type: ignore
            assert response_line, "No response from mock server"

            response = json.loads(response_line)

            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response
            assert response["result"]["serverInfo"]["name"] == "mock-mcp-server"

        finally:
            proc.terminate()
            proc.wait(timeout=1)

    @pytest.mark.asyncio
    async def test_backend_can_start_mock_server(self) -> None:
        """Test that StdioSubprocessBackend can start mock server."""
        config = BackendConfig(
            name="mock-backend",
            type=BackendType.STDIO_SUBPROCESS,
            command=sys.executable,
            args=[str(MOCK_SERVER)],
            enabled=True,
            namespace="mock",
            capabilities=["testing"],
            timeout=5,
        )

        backend = StdioSubprocessBackend(config)

        try:
            # Start backend
            await backend.start()

            # Check status
            assert backend.status == BackendStatus.RUNNING
            assert backend._process is not None
            assert backend._process.poll() is None  # Still running

        finally:
            # Stop backend
            await backend.stop()
            assert backend.status == BackendStatus.STOPPED

    @pytest.mark.asyncio
    async def test_backend_registry_with_mock(self) -> None:
        """Test that BackendRegistry can manage mock backend."""
        registry = BackendRegistry()

        config = BackendConfig(
            name="mock-backend",
            type=BackendType.STDIO_SUBPROCESS,
            command=sys.executable,
            args=[str(MOCK_SERVER)],
            enabled=True,
            namespace="mock",
            capabilities=["testing"],
            timeout=5,
        )

        try:
            # Register backend
            registry.register(config)

            # Start all backends
            await registry.start_all()

            # Check status
            status = registry.get_status()
            assert "mock-backend" in status
            assert status["mock-backend"]["status"] == "running"
            assert status["mock-backend"]["namespace"] == "mock"

            # Get backend by namespace
            backend = registry.get_backend_by_namespace("mock")
            assert backend is not None
            assert backend.name == "mock-backend"

        finally:
            # Stop all backends
            await registry.stop_all()

    @pytest.mark.asyncio
    async def test_subprocess_error_handling(self) -> None:
        """Test error handling when subprocess fails to start."""
        config = BackendConfig(
            name="bad-backend",
            type=BackendType.STDIO_SUBPROCESS,
            command="nonexistent_command_12345",  # Command doesn't exist
            args=[],
            enabled=True,
            namespace="bad",
            capabilities=[],
            timeout=5,
        )

        backend = StdioSubprocessBackend(config)

        # Starting should raise BackendError
        from mcp_n8n.backends.base import BackendError

        with pytest.raises(BackendError):
            await backend.start()

        # Check status is failed (not running, not stopped)
        assert backend.status == BackendStatus.FAILED
        assert backend._process is None

    @pytest.mark.skip(reason="Startup timeout not yet implemented")
    @pytest.mark.asyncio
    async def test_subprocess_timeout_handling(self) -> None:
        """Test timeout handling for slow subprocess startup."""
        config = BackendConfig(
            name="slow-backend",
            type=BackendType.STDIO_SUBPROCESS,
            command=sys.executable,
            args=["-c", "import time; time.sleep(10); print('Ready')"],  # Slow startup
            enabled=True,
            namespace="slow",
            capabilities=[],
            timeout=1,  # Very short timeout
        )

        backend = StdioSubprocessBackend(config)

        try:
            # Start should timeout
            await backend.start()

            # Status should be failed or stopped (depending on implementation)
            assert backend.status in [BackendStatus.FAILED, BackendStatus.STOPPED]

        finally:
            await backend.stop()

    @pytest.mark.asyncio
    async def test_multiple_backends_concurrent(self) -> None:
        """Test multiple backends can run concurrently."""
        registry = BackendRegistry()

        # Create two mock backends
        config1 = BackendConfig(
            name="mock-1",
            type=BackendType.STDIO_SUBPROCESS,
            command=sys.executable,
            args=[str(MOCK_SERVER)],
            enabled=True,
            namespace="mock1",
            capabilities=["testing"],
            timeout=5,
        )

        config2 = BackendConfig(
            name="mock-2",
            type=BackendType.STDIO_SUBPROCESS,
            command=sys.executable,
            args=[str(MOCK_SERVER)],
            enabled=True,
            namespace="mock2",
            capabilities=["testing"],
            timeout=5,
        )

        try:
            # Register both
            registry.register(config1)
            registry.register(config2)

            # Start all
            await registry.start_all()

            # Check both running
            status = registry.get_status()
            assert status["mock-1"]["status"] == "running"
            assert status["mock-2"]["status"] == "running"

            # Verify namespace isolation
            backend1 = registry.get_backend_by_namespace("mock1")
            backend2 = registry.get_backend_by_namespace("mock2")
            assert backend1 is not None
            assert backend2 is not None
            assert backend1.name != backend2.name

        finally:
            await registry.stop_all()


class TestNamespaceRouting:
    """Test namespace-based tool routing."""

    @pytest.mark.asyncio
    async def test_route_tool_call_success(self) -> None:
        """Test routing tool call to correct backend."""
        registry = BackendRegistry()

        config = BackendConfig(
            name="mock-backend",
            type=BackendType.STDIO_SUBPROCESS,
            command=sys.executable,
            args=[str(MOCK_SERVER)],
            enabled=True,
            namespace="mock",
            capabilities=["testing"],
            timeout=5,
        )

        try:
            registry.register(config)
            await registry.start_all()

            # Route namespaced tool call
            result = registry.route_tool_call("mock:generate_content")
            assert result is not None

            backend, tool_name = result
            assert backend.name == "mock-backend"
            assert tool_name == "generate_content"  # Namespace stripped

        finally:
            await registry.stop_all()

    @pytest.mark.asyncio
    async def test_route_tool_call_unknown_namespace(self) -> None:
        """Test routing with unknown namespace."""
        registry = BackendRegistry()

        # No backends registered

        # Route should return None for unknown namespace
        result = registry.route_tool_call("unknown:some_tool")
        assert result is None

    @pytest.mark.asyncio
    async def test_route_tool_call_no_namespace(self) -> None:
        """Test routing with missing namespace prefix."""
        registry = BackendRegistry()

        # Route should return None for tool without namespace
        result = registry.route_tool_call("generate_content")
        assert result is None


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.skip(reason="Crash detection not yet implemented")
    @pytest.mark.asyncio
    async def test_backend_crash_recovery(self) -> None:
        """Test detection when backend process crashes."""
        config = BackendConfig(
            name="crash-backend",
            type=BackendType.STDIO_SUBPROCESS,
            command=sys.executable,
            args=["-c", "import sys; sys.exit(1)"],  # Exits immediately
            enabled=True,
            namespace="crash",
            capabilities=[],
            timeout=5,
        )

        backend = StdioSubprocessBackend(config)

        try:
            await backend.start()

            # Wait for process to exit
            await asyncio.sleep(0.5)

            # Status should reflect crash
            assert backend.status in [BackendStatus.FAILED, BackendStatus.STOPPED]

        finally:
            await backend.stop()

    @pytest.mark.asyncio
    async def test_graceful_shutdown(self) -> None:
        """Test graceful shutdown of running backends."""
        registry = BackendRegistry()

        config = BackendConfig(
            name="mock-backend",
            type=BackendType.STDIO_SUBPROCESS,
            command=sys.executable,
            args=[str(MOCK_SERVER)],
            enabled=True,
            namespace="mock",
            capabilities=["testing"],
            timeout=5,
        )

        # Start backend
        registry.register(config)
        await registry.start_all()

        # Verify running
        status = registry.get_status()
        assert status["mock-backend"]["status"] == "running"

        # Stop all
        await registry.stop_all()

        # Verify stopped
        backend = registry.get_backend_by_name("mock-backend")
        assert backend is not None
        assert backend.status == BackendStatus.STOPPED
        assert backend._process is None or backend._process.poll() is not None


class TestChoraComposerIntegration:
    """Test integration with real chora-composer backend.

    These tests require chora-composer to be installed and ANTHROPIC_API_KEY set.
    Tests are conditional - skip if prerequisites not met.
    """

    @pytest.mark.asyncio
    async def test_gateway_can_start_chora_composer(self) -> None:
        """Test that gateway can start actual chora-composer backend."""
        import os

        # Skip if ANTHROPIC_API_KEY not set
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip(
                "ANTHROPIC_API_KEY not set - skipping chora-composer integration test"
            )

        from mcp_n8n.config import GatewayConfig

        config = GatewayConfig()
        backend_config = config.get_chora_composer_config()

        # Check if enabled
        if not backend_config.enabled:
            pytest.skip("chora-composer backend not enabled")

        backend = StdioSubprocessBackend(backend_config)

        try:
            # Start backend
            await backend.start()

            # Check status
            assert backend.status == BackendStatus.RUNNING
            assert backend._process is not None
            assert backend._process.poll() is None  # Still running

        finally:
            # Stop backend
            await backend.stop()
            assert backend.status == BackendStatus.STOPPED

    @pytest.mark.asyncio
    async def test_chora_composer_tool_routing(self) -> None:
        """Test namespace routing to chora-composer."""
        import os

        # Skip if ANTHROPIC_API_KEY not set
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip(
                "ANTHROPIC_API_KEY not set - skipping chora-composer integration test"
            )

        from mcp_n8n.config import GatewayConfig

        registry = BackendRegistry()
        config = GatewayConfig()
        backend_config = config.get_chora_composer_config()

        if not backend_config.enabled:
            pytest.skip("chora-composer backend not enabled")

        try:
            # Register and start
            registry.register(backend_config)
            await registry.start_all()

            # Test namespace routing
            result = registry.route_tool_call("chora:generate_content")
            assert result is not None

            backend, tool_name = result
            assert backend.name == "chora-composer"
            assert tool_name == "generate_content"  # Namespace stripped

        finally:
            await registry.stop_all()
