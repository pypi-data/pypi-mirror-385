"""Base backend interface for MCP server integrations."""

import asyncio
import json
import logging
import subprocess
import uuid
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
        self._response_queue: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._read_task: asyncio.Task[None] | None = None

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
            # Prepare environment (inherit current env + add config env)
            import os

            env = {**os.environ, **self.config.env}

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

            # Start stdout reader (for JSON-RPC responses)
            self._read_task = asyncio.create_task(self._read_responses())

            # Initialize backend (send initialize request, discover capabilities)
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

        if self._read_task:
            self._read_task.cancel()

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
            Tool result (parsed from MCP content structure)

        Raises:
            BackendError: If backend not running or call fails
        """
        if self.status != BackendStatus.RUNNING or not self._process:
            raise BackendError(self.name, "Backend not running")

        self.logger.info(f"Calling tool {tool_name} with args: {arguments}")

        # self._tools contains the RAW tool definitions from the backend server
        # with their original names (e.g., "list_generators"). These are what
        # the backend server expects in tools/call requests. The namespace prefix
        # (e.g., "chora:list_generators") is added by get_tools() for routing,
        # but NOT used when talking to the backend.

        # Verify tool exists in our discovered tools
        tool_names = [t.get("name") for t in self._tools]
        if tool_name not in tool_names:
            raise BackendError(
                self.name, f"Unknown tool '{tool_name}'. Available: {tool_names}"
            )

        try:
            # Send tools/call JSON-RPC request with the tool name as-is
            # (backend servers expect their original tool names, not our
            # namespaced versions)
            result = await self._send_jsonrpc(
                method="tools/call", params={"name": tool_name, "arguments": arguments}
            )

            # MCP protocol: tools/call returns structure:
            # {"content": [{"type": "text", "text": "...JSON string..."}]}
            # We need to parse the inner JSON string
            if "content" in result and isinstance(result["content"], list):
                content_items = result["content"]
                if content_items and len(content_items) > 0:
                    first_item = content_items[0]
                    if (
                        isinstance(first_item, dict)
                        and first_item.get("type") == "text"
                    ):
                        text_content = first_item.get("text", "{}")
                        try:
                            # Parse the JSON string inside the text field
                            parsed = json.loads(text_content)
                            self.logger.debug(
                                f"Tool {tool_name} returned (parsed): {parsed}"
                            )
                            return parsed  # type: ignore[no-any-return]
                        except json.JSONDecodeError:
                            self.logger.warning(
                                f"Could not parse tool response as JSON: "
                                f"{text_content[:200]}..."
                            )
                            # Return as plain text if not JSON
                            return {"text": text_content}

            # Fallback: return result as-is if not standard MCP structure
            self.logger.debug(f"Tool {tool_name} returned (non-standard): {result}")
            return result

        except BackendError:
            raise
        except Exception as e:
            raise BackendError(self.name, f"Tool call {tool_name} failed: {e}") from e

    async def _initialize(self) -> None:
        """Send initialize request to backend and discover capabilities."""
        try:
            # Send initialize request
            init_result = await self._send_jsonrpc(
                method="initialize",
                params={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "mcp-n8n-gateway", "version": "0.3.0"},
                },
            )

            self.logger.info(f"Backend {self.name} initialized: {init_result}")

            # Discover tools
            try:
                tools_result = await self._send_jsonrpc(method="tools/list")
                self._tools = tools_result.get("tools", [])
                self.logger.info(
                    f"Discovered {len(self._tools)} tools from {self.name}"
                )
            except Exception as e:
                self.logger.warning(f"Could not discover tools: {e}")
                self._tools = []

            # Discover resources
            try:
                resources_result = await self._send_jsonrpc(method="resources/list")
                self._resources = resources_result.get("resources", [])
                self.logger.info(
                    f"Discovered {len(self._resources)} resources from {self.name}"
                )
            except Exception as e:
                self.logger.warning(f"Could not discover resources: {e}")
                self._resources = []

            # Discover prompts
            try:
                prompts_result = await self._send_jsonrpc(method="prompts/list")
                self._prompts = prompts_result.get("prompts", [])
                self.logger.info(
                    f"Discovered {len(self._prompts)} prompts from {self.name}"
                )
            except Exception as e:
                self.logger.warning(f"Could not discover prompts: {e}")
                self._prompts = []

        except Exception as e:
            raise BackendError(self.name, f"Initialization failed: {e}") from e

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
                    self.logger.debug(f"[{self.name} stderr] {decoded}")
        except asyncio.CancelledError:
            pass

    async def _send_jsonrpc(
        self, method: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Send a JSON-RPC request and wait for response.

        Args:
            method: JSON-RPC method name
            params: Method parameters (optional)

        Returns:
            JSON-RPC result

        Raises:
            BackendError: If request fails or backend not running
        """
        if not self._process or not self._process.stdin or not self._process.stdout:
            raise BackendError(self.name, "Backend not running or STDIO not available")

        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Build JSON-RPC request
        request: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
        }
        if params is not None:
            request["params"] = params

        # Create future for response
        response_future: asyncio.Future[dict[str, Any]] = asyncio.Future()
        self._response_queue[request_id] = response_future

        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            self.logger.debug(f"Sending JSON-RPC request: {request_json.strip()}")
            await asyncio.to_thread(
                self._process.stdin.write, request_json.encode("utf-8")
            )
            await asyncio.to_thread(self._process.stdin.flush)

            # Wait for response (with timeout)
            response = await asyncio.wait_for(
                response_future, timeout=self.config.timeout
            )

            # Check for JSON-RPC error
            if "error" in response:
                error = response["error"]
                error_msg = error.get("message", "Unknown error")
                error_code = error.get("code", "N/A")
                error_data = error.get("data", "")

                # Log detailed error information
                self.logger.error(
                    f"JSON-RPC error from {self.name}:\n"
                    f"  Message: {error_msg}\n"
                    f"  Code: {error_code}\n"
                    f"  Data: {error_data}\n"
                    f"  Full error: {json.dumps(error, indent=2)}"
                )

                # Include error data in exception message
                error_detail = f"{error_msg}"
                if error_data:
                    error_detail += f" - {error_data}"

                raise BackendError(self.name, f"JSON-RPC error: {error_detail}")

            return response.get("result", {})  # type: ignore[no-any-return]

        except TimeoutError:
            del self._response_queue[request_id]
            raise BackendError(
                self.name, f"Request timeout after {self.config.timeout}s"
            )
        except Exception as e:
            del self._response_queue[request_id]
            raise BackendError(self.name, f"JSON-RPC request failed: {e}") from e

    async def _read_responses(self) -> None:
        """Read JSON-RPC responses from backend stdout."""
        if not self._process or not self._process.stdout:
            return

        try:
            while True:
                # Read line from stdout
                line = await asyncio.to_thread(self._process.stdout.readline)
                if not line:
                    break

                decoded = line.decode("utf-8").strip()
                if not decoded:
                    continue

                self.logger.debug(f"Received JSON-RPC response: {decoded}")

                try:
                    response = json.loads(decoded)

                    # Handle response
                    if "id" in response and response["id"] in self._response_queue:
                        future = self._response_queue[response["id"]]
                        if not future.done():
                            future.set_result(response)
                    else:
                        # Notification (no response needed)
                        self.logger.debug(f"Received notification: {response}")

                except json.JSONDecodeError as e:
                    self.logger.error(
                        f"Failed to decode JSON-RPC response: {decoded} - {e}"
                    )

        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(f"Error reading responses: {e}")
