"""Tests for backend registry."""

import pytest
from mcp_n8n.backends.registry import BackendRegistry
from mcp_n8n.config import BackendConfig, BackendType


class TestBackendRegistry:
    """Tests for BackendRegistry."""

    def test_register_backend(self) -> None:
        """Test registering a backend."""
        registry = BackendRegistry()
        config = BackendConfig(
            name="test-backend",
            type=BackendType.STDIO_SUBPROCESS,
            command="test",
            namespace="test",
        )

        registry.register(config)

        backend = registry.get_backend_by_name("test-backend")
        assert backend is not None
        assert backend.name == "test-backend"
        assert backend.namespace == "test"

    def test_register_duplicate_name_fails(self) -> None:
        """Test that registering duplicate backend name raises error."""
        registry = BackendRegistry()
        config1 = BackendConfig(
            name="test-backend",
            namespace="test1",
        )
        config2 = BackendConfig(
            name="test-backend",  # Duplicate name
            namespace="test2",
        )

        registry.register(config1)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(config2)

    def test_register_duplicate_namespace_fails(self) -> None:
        """Test that registering duplicate namespace raises error."""
        registry = BackendRegistry()
        config1 = BackendConfig(
            name="backend1",
            namespace="test",  # Same namespace
        )
        config2 = BackendConfig(
            name="backend2",
            namespace="test",  # Same namespace
        )

        registry.register(config1)

        with pytest.raises(ValueError, match="already used"):
            registry.register(config2)

    def test_get_backend_by_namespace(self) -> None:
        """Test retrieving backend by namespace."""
        registry = BackendRegistry()
        config = BackendConfig(
            name="test-backend",
            namespace="test",
        )

        registry.register(config)

        backend = registry.get_backend_by_namespace("test")
        assert backend is not None
        assert backend.name == "test-backend"

    def test_route_tool_call(self) -> None:
        """Test routing a tool call to appropriate backend."""
        registry = BackendRegistry()
        config = BackendConfig(
            name="test-backend",
            namespace="test",
        )

        registry.register(config)

        result = registry.route_tool_call("test:my_tool")
        assert result is not None
        backend, tool_name = result
        assert backend.name == "test-backend"
        assert tool_name == "my_tool"

    def test_route_tool_call_no_namespace(self) -> None:
        """Test routing fails for tool without namespace."""
        registry = BackendRegistry()

        result = registry.route_tool_call("my_tool")
        assert result is None

    def test_route_tool_call_unknown_namespace(self) -> None:
        """Test routing fails for unknown namespace."""
        registry = BackendRegistry()

        result = registry.route_tool_call("unknown:my_tool")
        assert result is None

    def test_get_status(self) -> None:
        """Test getting status of all backends."""
        registry = BackendRegistry()
        config = BackendConfig(
            name="test-backend",
            namespace="test",
        )

        registry.register(config)

        status = registry.get_status()
        assert "test-backend" in status
        assert status["test-backend"]["namespace"] == "test"
        assert status["test-backend"]["status"] == "stopped"
