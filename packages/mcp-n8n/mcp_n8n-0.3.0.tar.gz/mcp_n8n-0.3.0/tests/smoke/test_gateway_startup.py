"""Smoke test: Gateway startup and initialization."""

import pytest


def test_gateway_module_imports():
    """Test that gateway module can be imported."""
    try:
        from mcp_n8n import gateway

        assert gateway is not None
    except ImportError as e:
        pytest.fail(f"Failed to import gateway module: {e}")


def test_config_module_imports():
    """Test that config module can be imported."""
    try:
        from mcp_n8n import config

        assert config is not None
    except ImportError as e:
        pytest.fail(f"Failed to import config module: {e}")


def test_backends_module_imports():
    """Test that backends modules can be imported."""
    try:
        from mcp_n8n.backends import base, registry

        assert registry is not None
        assert base is not None
    except ImportError as e:
        pytest.fail(f"Failed to import backends modules: {e}")


def test_gateway_config_creation():
    """Test that GatewayConfig can be instantiated."""
    from mcp_n8n.config import GatewayConfig

    config = GatewayConfig()

    assert config is not None
    assert hasattr(config, "log_level")
    assert hasattr(config, "get_all_backend_configs")


def test_backend_config_creation():
    """Test that BackendConfig can be instantiated."""
    from mcp_n8n.config import BackendConfig, BackendType

    backend = BackendConfig(
        name="test-backend",
        type=BackendType.STDIO_SUBPROCESS,
        namespace="test",
        command="echo",
        enabled=True,
    )

    assert backend.name == "test-backend"
    assert backend.namespace == "test"
    assert backend.enabled is True


@pytest.mark.asyncio
async def test_backend_registry_initialization(mock_backend_registry):
    """Test that backend registry can be initialized."""
    assert mock_backend_registry is not None
    assert len(mock_backend_registry.backends) == 2
    assert "chora-composer" in mock_backend_registry.backends
    assert "coda-mcp" in mock_backend_registry.backends


def test_gateway_has_main_function():
    """Test that gateway module has a main() function."""
    from mcp_n8n import gateway

    assert hasattr(gateway, "main")
    assert callable(gateway.main)
