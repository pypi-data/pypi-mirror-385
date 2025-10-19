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

        Overrides base implementation to set expected Chora Composer tools.
        In a full implementation, this would make JSON-RPC calls to discover
        actual capabilities.
        """
        # TODO: Implement actual JSON-RPC tool discovery
        # For now, mock the expected tools based on Chora Composer's interface

        self._tools = [
            {
                "name": "generate_content",
                "description": (
                    "Generate content from a configuration-driven template. "
                    "Supports multiple generator types including jinja2, markdown, "
                    "and AI-powered code generation."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content_config_id": {
                            "type": "string",
                            "description": "ID of the content configuration to use",
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Override output path for generated content",
                        },
                    },
                    "required": ["content_config_id"],
                },
            },
            {
                "name": "assemble_artifact",
                "description": (
                    "Assemble a final artifact by combining multiple content pieces "
                    "according to a composition strategy. This is the PRIMARY tool "
                    "for all artifact creation in the gateway."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "artifact_config_id": {
                            "type": "string",
                            "description": "ID of the artifact configuration",
                        },
                        "output_path": {
                            "type": "string",
                            "description": (
                                "Override output path for assembled artifact"
                            ),
                        },
                        "force": {
                            "type": "boolean",
                            "description": "Force reassembly even if artifact exists",
                            "default": False,
                        },
                    },
                    "required": ["artifact_config_id"],
                },
            },
            {
                "name": "list_generators",
                "description": (
                    "List all available content generators. Useful for discovering "
                    "what types of content can be generated."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filter_by_type": {
                            "type": "string",
                            "description": "Optional filter by generator type",
                        }
                    },
                },
            },
            {
                "name": "validate_content",
                "description": (
                    "Validate a content configuration or artifact configuration "
                    "against its schema. Useful for checking configs before generation."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "config_id": {
                            "type": "string",
                            "description": "ID of configuration to validate",
                        },
                        "config_type": {
                            "type": "string",
                            "enum": ["content", "artifact"],
                            "description": "Type of configuration",
                        },
                    },
                    "required": ["config_id", "config_type"],
                },
            },
        ]

        self._resources = []  # Chora Composer doesn't expose resources
        self._prompts = []  # Chora Composer doesn't use prompts

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
