"""Base backend interface for MCP server integrations."""

import asyncio
import logging
import subprocess
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from mcp_n8n.config import BackendConfig


class BackendStatus(str, Enum):
    """Status of a backend server."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    FAILED = "failed"


class BackendError(Exception):
    """Base exception for backend errors."""

    def __init__(self, backend_name: str, message: str) -> None:
        self.backend_name = backend_name
        super().__init__(f"Backend '{backend_name}': {message}")


class Backend(ABC):
    """Abstract base class for MCP backend servers.

    Provides the interface for managing backend server lifecycle and
    forwarding tool calls. Implementations handle specific integration
    methods (subprocess, external, HTTP).
    """

    def __init__(self, config: BackendConfig) -> None:
        """Initialize backend with configuration.

        Args:
            config: Backend configuration including command, args, env, etc.
        """
        self.config = config
        self.status = BackendStatus.STOPPED
        self.logger = logging.getLogger(f"mcp_n8n.backends.{config.name}")
        self._tools: list[dict[str, Any]] = []
        self._resources: list[dict[str, Any]] = []
        self._prompts: list[dict[str, Any]] = []

    @property
    def name(self) -> str:
        """Get backend name."""
        return self.config.name

    @property
    def namespace(self) -> str:
        """Get tool namespace prefix."""
        return self.config.namespace

    @abstractmethod
    async def start(self) -> None:
        """Start the backend server.

        Should set status to STARTING, then RUNNING on success or FAILED on error.
        Should populate _tools, _resources, _prompts from backend's capabilities.
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the backend server.

        Should gracefully shutdown and set status to STOPPED.
        """
        pass

    @abstractmethod
    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Forward a tool call to the backend.

        Args:
            tool_name: Name of tool WITHOUT namespace prefix
            arguments: Tool arguments

        Returns:
            Tool result from backend

        Raises:
            BackendError: If call fails
        """
        pass

    def get_tools(self) -> list[dict[str, Any]]:
        """Get list of tools provided by this backend.

        Returns namespaced tool definitions.
        """
        return [self._namespace_tool(tool) for tool in self._tools]

    def get_resources(self) -> list[dict[str, Any]]:
        """Get list of resources provided by this backend."""
        return self._resources

    def get_prompts(self) -> list[dict[str, Any]]:
        """Get list of prompts provided by this backend."""
        return self._prompts

    def _namespace_tool(self, tool: dict[str, Any]) -> dict[str, Any]:
        """Add namespace prefix to tool name.

        Args:
            tool: Tool definition from backend

        Returns:
            Tool definition with namespaced name
        """
        namespaced = tool.copy()
        original_name = tool.get("name", "unknown")
        namespaced["name"] = f"{self.namespace}:{original_name}"
        namespaced["_original_name"] = original_name
        namespaced["_backend"] = self.name
        return namespaced

    def _remove_namespace(self, tool_name: str) -> str:
        """Remove namespace prefix from tool name.

        Args:
            tool_name: Namespaced tool name (e.g., "chora:assemble_artifact")

        Returns:
            Original tool name (e.g., "assemble_artifact")
        """
        if ":" in tool_name:
            _, name = tool_name.split(":", 1)
            return name
        return tool_name


class StdioSubprocessBackend(Backend):
    """Backend that spawns MCP server as subprocess and communicates via STDIO.

    This is the primary integration method for Pattern P1 (Local STDIO Companion)
    backends like Chora Composer and Coda MCP.
    """

    def __init__(self, config: BackendConfig) -> None:
        super().__init__(config)
        self._process: subprocess.Popen[bytes] | None = None
        self._reader_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Start backend as subprocess."""
        if self.status == BackendStatus.RUNNING:
            self.logger.warning(f"Backend {self.name} already running")
            return

        if not self.config.command:
            raise BackendError(self.name, "No command specified for subprocess backend")

        self.status = BackendStatus.STARTING
        self.logger.info(
            f"Starting backend {self.name} with command: {self.config.command}"
        )

        try:
            # Prepare environment
            env = {**self.config.env}

            # Spawn subprocess
            self._process = subprocess.Popen(
                [self.config.command] + self.config.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )

            # Start stderr reader (for logging backend errors)
            self._reader_task = asyncio.create_task(self._read_stderr())

            # Initialize backend (send initialize request)
            await self._initialize()

            self.status = BackendStatus.RUNNING
            self.logger.info(f"Backend {self.name} started successfully")

        except Exception as e:
            self.status = BackendStatus.FAILED
            self.logger.error(f"Failed to start backend {self.name}: {e}")
            raise BackendError(self.name, f"Failed to start: {e}") from e

    async def stop(self) -> None:
        """Stop backend subprocess."""
        if self._process:
            self.logger.info(f"Stopping backend {self.name}")
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.logger.warning(f"Backend {self.name} did not terminate, killing")
                self._process.kill()

        if self._reader_task:
            self._reader_task.cancel()

        self.status = BackendStatus.STOPPED
        self.logger.info(f"Backend {self.name} stopped")

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Forward tool call to backend via STDIO JSON-RPC.

        Args:
            tool_name: Tool name WITHOUT namespace
            arguments: Tool arguments

        Returns:
            Tool result

        Raises:
            BackendError: If backend not running or call fails
        """
        if self.status != BackendStatus.RUNNING or not self._process:
            raise BackendError(self.name, "Backend not running")

        # For now, return mock response
        # TODO: Implement actual JSON-RPC communication
        self.logger.info(f"Calling tool {tool_name} with args: {arguments}")
        return {
            "success": True,
            "message": f"Mock response from {self.name} for tool {tool_name}",
        }

    async def _initialize(self) -> None:
        """Send initialize request to backend and discover capabilities."""
        # TODO: Implement JSON-RPC initialize request
        # For now, set empty tool list
        self._tools = []
        self._resources = []
        self._prompts = []
        self.logger.info(f"Backend {self.name} initialized (mock)")

    async def _read_stderr(self) -> None:
        """Read stderr from backend process for logging."""
        if not self._process or not self._process.stderr:
            return

        try:
            while True:
                line = await asyncio.to_thread(self._process.stderr.readline)
                if not line:
                    break
                decoded = line.decode("utf-8").strip()
                if decoded:
                    self.logger.info(f"[{self.name} stderr] {decoded}")
        except asyncio.CancelledError:
            pass
