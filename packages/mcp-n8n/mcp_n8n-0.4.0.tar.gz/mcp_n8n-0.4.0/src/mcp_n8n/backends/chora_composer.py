"""Chora Composer backend integration.

Integrates the Chora Composer MCP server as the EXCLUSIVE artifact creation
mechanism in the gateway. All artifact generation and assembly operations
route through this backend.
"""

import logging
from typing import Any

from mcp_n8n.backends.base import StdioSubprocessBackend
from mcp_n8n.config import BackendConfig


class ChoraComposerBackend(StdioSubprocessBackend):
    """Backend for Chora Composer MCP server.

    Provides exclusive access to artifact creation capabilities:
    - generate_content: Generate content from templates
    - assemble_artifact: Assemble artifacts from content pieces
    - list_generators: List available content generators
    - validate_content: Validate content or configurations
    """

    EXPECTED_TOOLS = [
        "generate_content",
        "assemble_artifact",
        "list_generators",
        "validate_content",
    ]

    def __init__(self, config: BackendConfig) -> None:
        """Initialize Chora Composer backend.

        Args:
            config: Backend configuration
        """
        super().__init__(config)
        self.logger = logging.getLogger("mcp_n8n.backends.chora_composer")

    async def _initialize(self) -> None:
        """Initialize connection to Chora Composer and discover tools.

        Uses base class JSON-RPC implementation to discover actual tools
        from chora-compose.
        """
        # Call parent implementation which does real JSON-RPC tool discovery
        await super()._initialize()

        self.logger.info(
            f"Initialized Chora Composer backend with {len(self._tools)} tools"
        )

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Forward tool call to Chora Composer.

        Args:
            tool_name: Tool name (without namespace)
            arguments: Tool arguments

        Returns:
            Tool execution result

        Raises:
            BackendError: If tool call fails
        """
        # Validate tool exists
        if tool_name not in self.EXPECTED_TOOLS:
            from mcp_n8n.backends.base import BackendError

            raise BackendError(
                self.name,
                f"Unknown tool '{tool_name}'. Expected one of: {self.EXPECTED_TOOLS}",
            )

        # Log artifact-specific operations
        if tool_name == "assemble_artifact":
            artifact_id = arguments.get("artifact_config_id", "unknown")
            self.logger.info(f"Routing artifact assembly request: {artifact_id}")

        # Call parent implementation (which will eventually do JSON-RPC)
        return await super().call_tool(tool_name, arguments)
