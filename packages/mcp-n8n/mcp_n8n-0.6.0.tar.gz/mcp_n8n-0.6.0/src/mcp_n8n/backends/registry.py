"""Backend registry for managing multiple MCP servers."""

import logging
from typing import Any

from mcp_n8n.backends.base import (
    Backend,
    BackendError,
    BackendStatus,
    StdioSubprocessBackend,
)
from mcp_n8n.config import BackendConfig, BackendType


class BackendRegistry:
    """Registry for managing multiple backend MCP servers.

    Handles backend lifecycle (start/stop), tool routing, and capability
    aggregation following the P5 Gateway & Aggregator pattern.
    """

    def __init__(self) -> None:
        """Initialize empty backend registry."""
        self._backends: dict[str, Backend] = {}
        self._namespace_map: dict[str, Backend] = {}
        self.logger = logging.getLogger("mcp_n8n.backends.registry")

    def register(self, config: BackendConfig) -> None:
        """Register a backend server.

        Args:
            config: Backend configuration

        Raises:
            ValueError: If backend or namespace already registered
        """
        if config.name in self._backends:
            raise ValueError(f"Backend '{config.name}' already registered")

        if config.namespace in self._namespace_map:
            raise ValueError(
                f"Namespace '{config.namespace}' already used by backend "
                f"'{self._namespace_map[config.namespace].name}'"
            )

        # Create backend based on type
        backend = self._create_backend(config)

        self._backends[config.name] = backend
        self._namespace_map[config.namespace] = backend
        self.logger.info(
            f"Registered backend '{config.name}' with namespace '{config.namespace}'"
        )

    def _create_backend(self, config: BackendConfig) -> Backend:
        """Create backend instance based on configuration.

        Args:
            config: Backend configuration

        Returns:
            Backend instance

        Raises:
            ValueError: If backend type not supported
        """
        if config.type == BackendType.STDIO_SUBPROCESS:
            return StdioSubprocessBackend(config)
        else:
            raise ValueError(f"Unsupported backend type: {config.type}")

    async def start_all(self) -> None:
        """Start all registered backends."""
        self.logger.info(f"Starting {len(self._backends)} backends...")

        for name, backend in self._backends.items():
            try:
                await backend.start()
            except BackendError as e:
                self.logger.error(f"Failed to start backend '{name}': {e}")
                # Continue starting other backends

        running_count = sum(
            1 for b in self._backends.values() if b.status == BackendStatus.RUNNING
        )
        self.logger.info(
            f"Started {running_count}/{len(self._backends)} backends successfully"
        )

    async def stop_all(self) -> None:
        """Stop all registered backends."""
        self.logger.info("Stopping all backends...")

        for backend in self._backends.values():
            try:
                await backend.stop()
            except Exception as e:
                self.logger.error(f"Error stopping backend '{backend.name}': {e}")

        self.logger.info("All backends stopped")

    def get_backend_by_name(self, name: str) -> Backend | None:
        """Get backend by name.

        Args:
            name: Backend name

        Returns:
            Backend instance or None if not found
        """
        return self._backends.get(name)

    def get_backend_by_namespace(self, namespace: str) -> Backend | None:
        """Get backend by namespace prefix.

        Args:
            namespace: Namespace prefix (e.g., 'chora', 'coda')

        Returns:
            Backend instance or None if not found
        """
        return self._namespace_map.get(namespace)

    def route_tool_call(self, tool_name: str) -> tuple[Backend, str] | None:
        """Route a tool call to the appropriate backend.

        Args:
            tool_name: Namespaced tool name (e.g., 'chora:assemble_artifact')

        Returns:
            Tuple of (backend, original_tool_name) or None if not found
        """
        if ":" not in tool_name:
            self.logger.warning(f"Tool '{tool_name}' has no namespace prefix")
            return None

        namespace, original_name = tool_name.split(":", 1)
        backend = self.get_backend_by_namespace(namespace)

        if not backend:
            self.logger.warning(f"No backend found for namespace '{namespace}'")
            return None

        return backend, original_name

    def get_all_tools(self) -> list[dict[str, Any]]:
        """Aggregate tools from all backends.

        Returns:
            List of all tools with namespace prefixes
        """
        all_tools = []
        for backend in self._backends.values():
            if backend.status == BackendStatus.RUNNING:
                all_tools.extend(backend.get_tools())
        return all_tools

    def get_all_resources(self) -> list[dict[str, Any]]:
        """Aggregate resources from all backends.

        Returns:
            List of all resources
        """
        all_resources = []
        for backend in self._backends.values():
            if backend.status == BackendStatus.RUNNING:
                all_resources.extend(backend.get_resources())
        return all_resources

    def get_all_prompts(self) -> list[dict[str, Any]]:
        """Aggregate prompts from all backends.

        Returns:
            List of all prompts
        """
        all_prompts = []
        for backend in self._backends.values():
            if backend.status == BackendStatus.RUNNING:
                all_prompts.extend(backend.get_prompts())
        return all_prompts

    def get_status(self) -> dict[str, Any]:
        """Get status of all backends.

        Returns:
            Dictionary mapping backend names to their status
        """
        return {
            name: {
                "status": backend.status.value,
                "namespace": backend.namespace,
                "tool_count": len(backend.get_tools()),
            }
            for name, backend in self._backends.items()
        }
