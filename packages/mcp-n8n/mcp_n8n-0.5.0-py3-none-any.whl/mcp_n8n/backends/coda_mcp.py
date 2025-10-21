"""Coda MCP backend integration.

Integrates the Coda MCP server for data operations on Coda documents,
tables, and rows.
"""

import logging
from typing import Any

from mcp_n8n.backends.base import StdioSubprocessBackend
from mcp_n8n.config import BackendConfig


class CodaMcpBackend(StdioSubprocessBackend):
    """Backend for Coda MCP server.

    Provides data operation capabilities:
    - list_docs: List Coda documents
    - list_tables: List tables in a document
    - list_rows: List rows from a table
    - create_hello_doc_in_folder: Create a sample document (for testing)
    """

    EXPECTED_TOOLS = [
        "list_docs",
        "list_tables",
        "list_rows",
        "create_hello_doc_in_folder",
    ]

    def __init__(self, config: BackendConfig) -> None:
        """Initialize Coda MCP backend.

        Args:
            config: Backend configuration
        """
        super().__init__(config)
        self.logger = logging.getLogger("mcp_n8n.backends.coda_mcp")

    async def _initialize(self) -> None:
        """Initialize connection to Coda MCP and discover tools.

        Overrides base implementation to set expected Coda MCP tools.
        In a full implementation, this would make JSON-RPC calls to discover
        actual capabilities.
        """
        # TODO: Implement actual JSON-RPC tool discovery
        # For now, mock the expected tools based on Coda MCP's interface

        self._tools = [
            {
                "name": "list_docs",
                "description": (
                    "List Coda documents accessible with the configured API key. "
                    "Supports optional query filtering and result limiting."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Optional search query to filter documents",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of documents to return",
                            "default": 100,
                        },
                    },
                },
            },
            {
                "name": "list_tables",
                "description": (
                    "List all tables in a Coda document. Returns both regular tables "
                    "and views."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "ID of the Coda document",
                        }
                    },
                    "required": ["doc_id"],
                },
            },
            {
                "name": "list_rows",
                "description": (
                    "List rows from a table in a Coda document. Supports pagination, "
                    "filtering, and query parameters."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "doc_id": {
                            "type": "string",
                            "description": "ID of the Coda document",
                        },
                        "table": {
                            "type": "string",
                            "description": "Table ID or name",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of rows to return",
                        },
                        "query": {
                            "type": "string",
                            "description": "Optional query to filter rows",
                        },
                    },
                    "required": ["doc_id", "table"],
                },
            },
            {
                "name": "create_hello_doc_in_folder",
                "description": (
                    "Create a sample 'Hello World' document in a specified folder. "
                    "Useful for testing write operations and permissions."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "folder_id": {
                            "type": "string",
                            "description": "ID of the Coda folder",
                        },
                        "workspace_id": {
                            "type": "string",
                            "description": "Optional workspace ID",
                        },
                    },
                    "required": ["folder_id"],
                },
            },
        ]

        self._resources = []  # Could expose doc/table resources in future
        self._prompts = []

        self.logger.info(f"Initialized Coda MCP backend with {len(self._tools)} tools")

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Forward tool call to Coda MCP.

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

        # Log data operations
        if tool_name in ["list_docs", "list_tables", "list_rows"]:
            self.logger.info(f"Routing Coda data operation: {tool_name}")

        # Call parent implementation (which will eventually do JSON-RPC)
        return await super().call_tool(tool_name, arguments)
