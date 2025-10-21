"""Tests for configuration management."""

import pytest
from mcp_n8n.config import BackendConfig, BackendType, GatewayConfig


class TestBackendConfig:
    """Tests for BackendConfig model."""

    def test_backend_config_creation(self) -> None:
        """Test creating a valid backend configuration."""
        config = BackendConfig(
            name="test-backend",
            type=BackendType.STDIO_SUBPROCESS,
            command="test-command",
            namespace="test",
        )

        assert config.name == "test-backend"
        assert config.type == BackendType.STDIO_SUBPROCESS
        assert config.command == "test-command"
        assert config.namespace == "test"
        assert config.enabled is True
        assert config.timeout == 30

    def test_backend_config_with_env(self) -> None:
        """Test backend configuration with environment variables."""
        config = BackendConfig(
            name="test-backend",
            namespace="test",
            env={"API_KEY": "secret", "DEBUG": "true"},
        )

        assert config.env["API_KEY"] == "secret"
        assert config.env["DEBUG"] == "true"


class TestGatewayConfig:
    """Tests for GatewayConfig model."""

    def test_gateway_config_defaults(self) -> None:
        """Test gateway configuration with defaults."""
        config = GatewayConfig()

        assert config.log_level == "INFO"
        assert config.debug is False
        assert config.backend_timeout == 30
        assert config.max_retries == 3

    def test_chora_composer_config_enabled(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test Chora Composer backend enabled when API key present."""
        monkeypatch.setenv("MCP_N8N_ANTHROPIC_API_KEY", "test-key")
        config = GatewayConfig()

        chora_config = config.get_chora_composer_config()
        assert chora_config.enabled is True
        assert chora_config.name == "chora-composer"
        assert chora_config.namespace == "chora"
        assert chora_config.env["ANTHROPIC_API_KEY"] == "test-key"

    def test_chora_composer_config_disabled(self) -> None:
        """Test Chora Composer backend disabled when no API key."""
        config = GatewayConfig()

        chora_config = config.get_chora_composer_config()
        assert chora_config.enabled is False

    def test_coda_mcp_config_enabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test Coda MCP backend enabled when API key present."""
        monkeypatch.setenv("MCP_N8N_CODA_API_KEY", "test-coda-key")
        monkeypatch.setenv("MCP_N8N_CODA_FOLDER_ID", "test-folder")
        config = GatewayConfig()

        coda_config = config.get_coda_mcp_config()
        assert coda_config.enabled is True
        assert coda_config.name == "coda-mcp"
        assert coda_config.namespace == "coda"
        assert coda_config.env["CODA_API_KEY"] == "test-coda-key"
        assert coda_config.env["CODA_FOLDER_ID"] == "test-folder"

    def test_get_all_backend_configs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test getting all enabled backend configurations."""
        monkeypatch.setenv("MCP_N8N_ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("MCP_N8N_CODA_API_KEY", "test-coda-key")
        config = GatewayConfig()

        backends = config.get_all_backend_configs()
        assert len(backends) == 2

        namespaces = {b.namespace for b in backends}
        assert "chora" in namespaces
        assert "coda" in namespaces
