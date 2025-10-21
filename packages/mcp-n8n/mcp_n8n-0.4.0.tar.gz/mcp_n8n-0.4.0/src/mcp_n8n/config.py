"""Configuration management for mcp-n8n gateway.

Handles environment variables, backend configuration, and runtime settings
following the Pydantic Settings pattern.
"""

from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BackendType(str, Enum):
    """Type of backend server integration."""

    STDIO_SUBPROCESS = "stdio_subprocess"  # Spawn as subprocess, communicate via STDIO
    STDIO_EXTERNAL = "stdio_external"  # Connect to external STDIO server
    HTTP_SSE = "http_sse"  # Connect via HTTP+SSE


class BackendConfig(BaseSettings):  # type: ignore[misc]
    """Configuration for a single backend MCP server."""

    name: str = Field(description="Backend identifier (e.g., 'chora-composer')")
    type: BackendType = Field(
        default=BackendType.STDIO_SUBPROCESS,
        description="Integration method for this backend",
    )
    command: str | None = Field(
        default=None, description="Command to execute (for subprocess backends)"
    )
    args: list[str] = Field(
        default_factory=list, description="Arguments to pass to command"
    )
    enabled: bool = Field(default=True, description="Whether backend is active")
    namespace: str = Field(description="Tool namespace prefix (e.g., 'chora', 'coda')")
    capabilities: list[str] = Field(
        default_factory=list,
        description="Capability categories (e.g., ['artifacts', 'data'])",
    )
    env: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables to pass to backend",
    )
    timeout: int = Field(
        default=30, description="Timeout in seconds for backend operations"
    )

    model_config = SettingsConfigDict(use_enum_values=True)


class GatewayConfig(BaseSettings):  # type: ignore[misc]
    """Main configuration for mcp-n8n gateway."""

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # Backend credentials
    # Note: These can be set as MCP_N8N_ANTHROPIC_API_KEY or ANTHROPIC_API_KEY
    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key for Chora Composer",
        validation_alias="ANTHROPIC_API_KEY",  # Allow unprefixed env var
    )
    coda_api_key: str | None = Field(
        default=None,
        description="Coda API key for Coda MCP",
        validation_alias="CODA_API_KEY",  # Allow unprefixed env var
    )
    coda_folder_id: str | None = Field(
        default=None,
        description="Default Coda folder ID for write operations",
        validation_alias="CODA_FOLDER_ID",  # Allow unprefixed env var
    )

    # Event monitoring
    n8n_event_webhook_url: str | None = Field(
        default=None,
        description="n8n webhook URL for real-time event forwarding (optional)",
        validation_alias="N8N_EVENT_WEBHOOK_URL",  # Allow unprefixed env var
    )

    # Gateway behavior
    backend_timeout: int = Field(
        default=30, description="Default timeout for backend operations"
    )
    max_retries: int = Field(
        default=3, description="Maximum retries for failed backend calls"
    )

    # Paths
    config_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "configs",
        description="Directory for backend configuration files",
    )

    model_config = SettingsConfigDict(
        env_prefix="MCP_N8N_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_chora_composer_config(self) -> BackendConfig:
        """Get configuration for Chora Composer backend.

        Requires chora-compose to be installed via pip:
            pip install chora-compose>=1.3.0
        """
        import sys

        # Verify chora_compose is installed
        try:
            import chora_compose  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "chora-compose not found. Install with:\n"
                "  pip install chora-compose>=1.3.0\n"
                "Or install all dependencies with:\n"
                "  pip install -e .[dev]"
            )

        return BackendConfig(
            name="chora-composer",
            type=BackendType.STDIO_SUBPROCESS,
            command=sys.executable,
            args=["-m", "chora_compose.mcp.server"],
            enabled=self.anthropic_api_key is not None,
            namespace="chora",
            capabilities=["artifacts", "content_generation"],
            env={"ANTHROPIC_API_KEY": self.anthropic_api_key or ""},
            timeout=self.backend_timeout,
        )

    def get_coda_mcp_config(self) -> BackendConfig:
        """Get configuration for Coda MCP backend."""
        env_vars = {"CODA_API_KEY": self.coda_api_key or ""}
        if self.coda_folder_id:
            env_vars["CODA_FOLDER_ID"] = self.coda_folder_id

        return BackendConfig(
            name="coda-mcp",
            type=BackendType.STDIO_SUBPROCESS,
            command="coda-mcp",
            args=[],
            enabled=self.coda_api_key is not None,
            namespace="coda",
            capabilities=["data_operations", "documents"],
            env=env_vars,
            timeout=self.backend_timeout,
        )

    def get_all_backend_configs(self) -> list[BackendConfig]:
        """Get configurations for all enabled backends."""
        backends = [
            self.get_chora_composer_config(),
            self.get_coda_mcp_config(),
        ]
        return [b for b in backends if b.enabled]


def load_config() -> GatewayConfig:
    """Load gateway configuration from environment."""
    return GatewayConfig()
