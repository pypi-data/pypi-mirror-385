"""Integration tests for chora-compose detection and configuration.

Tests that the gateway correctly detects chora-compose installation
via PyPI package and configures itself accordingly.
"""

import inspect
import sys
from pathlib import Path

import pytest
from mcp_n8n.config import GatewayConfig


def test_chora_compose_available():
    """Verify chora-compose is available as PyPI package."""
    import chora_compose

    assert hasattr(chora_compose, "__version__") or hasattr(chora_compose, "__file__")
    print(f"✓ chora-compose available as package: {chora_compose.__file__}")


def test_gateway_config_detects_chora_compose():
    """Verify gateway config can detect chora-compose installation."""
    config = GatewayConfig()
    chora_config = config.get_chora_composer_config()

    # Should have a valid command (Python executable)
    assert chora_config.command is not None
    assert chora_config.command != ""
    print(f"✓ Detected Python command: {chora_config.command}")

    # Should use current Python or system Python
    assert Path(chora_config.command).exists() or chora_config.command in [
        "python",
        "python3",
        "python3.11",
        "python3.12",
    ]

    # Should have correct module args
    assert chora_config.args == ["-m", "chora_compose.mcp.server"]

    # Should have namespace
    assert chora_config.namespace == "chora"


def test_config_uses_package_installation():
    """Verify config uses PyPI package installation."""
    config = GatewayConfig()
    chora_config = config.get_chora_composer_config()

    # Package installation should NOT set PYTHONPATH
    assert (
        "PYTHONPATH" not in chora_config.env
    ), "Package install shouldn't set PYTHONPATH"
    print("✓ Using package installation (no PYTHONPATH)")


def test_config_no_hardcoded_paths():
    """Verify config doesn't contain hardcoded machine-specific paths."""
    config = GatewayConfig()

    # Get source code of the config method
    source = inspect.getsource(config.get_chora_composer_config)

    # Should not contain hardcoded user paths
    assert (
        "/Users/victorpiper/" not in source
    ), "Config contains hardcoded user-specific path"
    assert (
        "Library/Caches/pypoetry" not in source
    ), "Config contains hardcoded Poetry venv path"

    print("✓ No hardcoded paths found in config")


def test_config_command_is_current_python():
    """Verify config uses sys.executable (current Python)."""
    config = GatewayConfig()
    chora_config = config.get_chora_composer_config()

    # The command should be the current Python executable or a system Python
    assert chora_config.command == sys.executable or Path(
        chora_config.command
    ).name.startswith("python")

    print(f"✓ Using Python: {chora_config.command}")
    print(f"  (Current Python: {sys.executable})")


def test_config_error_message_helpful():
    """Verify error message is helpful when chora-compose not found."""
    config = GatewayConfig()
    source = inspect.getsource(config.get_chora_composer_config)

    assert "chora-compose not found" in source
    assert "pip install chora-compose" in source
    assert "pip install -e .[dev]" in source

    print("✓ Helpful error message present in config")


@pytest.mark.asyncio
async def test_backend_starts_with_detected_config():
    """Verify backend can start with detected configuration."""
    from mcp_n8n.backends.registry import BackendRegistry
    from mcp_n8n.config import GatewayConfig

    config = GatewayConfig()
    chora_config = config.get_chora_composer_config()

    # Only test if API key is available
    if chora_config.enabled:
        registry = BackendRegistry()
        registry.register(chora_config)

        try:
            await registry.start_all()

            # Backend should start successfully
            from mcp_n8n.backends.base import BackendStatus

            backend = registry.get_backend_by_name("chora-composer")
            assert backend is not None
            assert backend.status == BackendStatus.RUNNING

            print("✓ Backend started successfully with detected config")
        finally:
            # Clean up
            await registry.stop_all()
    else:
        pytest.skip("ANTHROPIC_API_KEY not set, skipping backend startup test")


def test_no_submodules_present():
    """Verify no git submodules are present (using PyPI packages only)."""
    project_root = Path(__file__).parent.parent.parent
    vendors_path = project_root / "vendors"

    # Vendors directory should not exist or be empty
    if vendors_path.exists():
        submodules = list(vendors_path.iterdir())
        assert len(submodules) == 0, f"Found unexpected submodules: {submodules}"
        print("✓ Vendors directory exists but is empty")
    else:
        print("✓ No vendors directory (PyPI packages only)")
