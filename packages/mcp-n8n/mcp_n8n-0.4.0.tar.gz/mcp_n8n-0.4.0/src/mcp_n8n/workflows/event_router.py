"""Event-to-workflow routing based on YAML configuration.

This module implements the EventWorkflowRouter which:
- Loads event-to-workflow mappings from YAML config
- Matches incoming events against patterns
- Templates workflow parameters using Jinja2
- Triggers workflows via backend registry
- Supports hot-reload of config file
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Template
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from mcp_n8n.backends.registry import BackendRegistry

logger = logging.getLogger(__name__)

# Type aliases to avoid mypy issues with watchdog
ObserverType = Any  # Observer from watchdog


class EventWorkflowRouter:
    """Routes events to workflows based on YAML configuration patterns.

    This router:
    1. Loads event-to-workflow mappings from a YAML config file
    2. Matches incoming events against patterns using field-based matching
    3. Templates workflow parameters using Jinja2 syntax ({{ event.* }})
    4. Triggers workflows via the backend registry
    5. Supports hot-reload when config file is modified

    Example config file (config/event_mappings.yaml):
    ```yaml
    mappings:
      - event_pattern:
          type: "gateway.tool_call"
          status: "failure"
        workflow:
          id: "error-alert-workflow"
          namespace: "n8n"
          parameters:
            error: "{{ event.data.error }}"
            tool: "{{ event.data.tool_name }}"
    ```

    Pattern Matching Rules:
    - All fields in event_pattern must be present in the event
    - Event can have extra fields not in pattern (still matches)
    - First matching pattern wins (order matters)
    - Parameters are templated using Jinja2 syntax
    """

    def __init__(
        self,
        config_path: str,
        backend_registry: BackendRegistry,
    ):
        """Initialize router with config file and backend registry.

        Args:
            config_path: Path to event_mappings.yaml file
            backend_registry: BackendRegistry for triggering workflows

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        self.config_path = str(config_path)  # Store as string, not Path
        if not Path(config_path).exists():
            raise FileNotFoundError(
                f"Config file not found: {config_path}\n"
                f"Expected: event_mappings.yaml\n"
                f"Please create the file with event-to-workflow mappings"
            )

        self.backend_registry = backend_registry
        self.mappings: list[dict[str, Any]] = []
        self._observer: ObserverType = None
        self._watching = False

    async def load_mappings(self) -> list[dict[str, Any]]:
        """Load event-to-workflow mappings from YAML config file.

        Returns:
            List of mapping dictionaries with 'event_pattern' and 'workflow' keys

        Raises:
            yaml.YAMLError: If config file contains invalid YAML
            ValueError: If config structure is invalid
        """
        logger.info(f"Loading event mappings from {self.config_path}")

        try:
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in config file: {e}")
            raise

        if not isinstance(config, dict) or "mappings" not in config:
            raise ValueError(
                "Invalid config structure. Expected:\n"
                "mappings:\n"
                "  - event_pattern: {...}\n"
                "    workflow: {...}"
            )

        mappings = config["mappings"]
        if not isinstance(mappings, list):
            raise ValueError("'mappings' must be a list")

        # Validate each mapping
        for i, mapping in enumerate(mappings):
            if not isinstance(mapping, dict):
                raise ValueError(f"Mapping {i} must be a dictionary")

            if "event_pattern" not in mapping:
                raise ValueError(f"Mapping {i} missing 'event_pattern'")

            if "workflow" not in mapping:
                raise ValueError(f"Mapping {i} missing 'workflow'")

            workflow = mapping["workflow"]
            if not isinstance(workflow, dict) or "id" not in workflow:
                raise ValueError(f"Mapping {i} workflow must have 'id' field")

        self.mappings = mappings
        logger.info(f"Loaded {len(self.mappings)} event-to-workflow mappings")
        return self.mappings

    def _matches_pattern(self, event: dict[str, Any], pattern: dict[str, Any]) -> bool:
        """Check if event matches pattern.

        Pattern matching rules:
        - All fields in pattern must be present in event with same value
        - Event can have extra fields (they are ignored)
        - Nested dict matching supported (e.g., pattern["data"]["status"])

        Args:
            event: Event dictionary to check
            pattern: Pattern dictionary to match against

        Returns:
            True if event matches pattern, False otherwise
        """
        for key, pattern_value in pattern.items():
            if key not in event:
                return False

            event_value = event[key]

            # Handle nested dictionaries
            if isinstance(pattern_value, dict):
                if not isinstance(event_value, dict):
                    return False
                if not self._matches_pattern(event_value, pattern_value):
                    return False
            else:
                # Direct value comparison
                if event_value != pattern_value:
                    return False

        return True

    async def match_event(self, event: dict[str, Any]) -> dict[str, Any] | None:
        """Match event against patterns and return workflow target with
        templated parameters.

        Args:
            event: Event dictionary to match

        Returns:
            Workflow dictionary with 'workflow_id', 'namespace', 'parameters'
            (templated) or None if no pattern matches
        """
        for mapping in self.mappings:
            pattern = mapping["event_pattern"]

            if self._matches_pattern(event, pattern):
                workflow = mapping["workflow"]
                logger.debug(
                    f"Event matched pattern: {pattern}\n" f"Workflow: {workflow['id']}"
                )

                # Template parameters before returning
                raw_params = workflow.get("parameters", {})
                templated_params = self._template_parameters(raw_params, event)

                # Return workflow details with templated parameters
                result = {
                    "workflow_id": workflow["id"],
                    "namespace": workflow.get("namespace"),
                    "parameters": templated_params,
                }
                return result

        logger.debug(f"No pattern matched event: {event.get('type', 'unknown')}")
        return None

    def _template_parameters(
        self,
        params: dict[str, Any],
        event: dict[str, Any],
    ) -> dict[str, Any]:
        """Render Jinja2 templates in workflow parameters.

        Templates use {{ event.* }} syntax to access event fields.
        Example: "{{ event.data.error }}" -> event["data"]["error"]

        Args:
            params: Parameter dictionary with template strings
            event: Event dictionary for template context

        Returns:
            Dictionary with templates rendered
        """
        result: dict[str, Any] = {}

        for key, value in params.items():
            if isinstance(value, str):
                # Render Jinja2 template
                try:
                    template = Template(value)
                    rendered = template.render(event=event)
                    result[key] = rendered
                except Exception as e:
                    logger.warning(
                        f"Failed to render template '{value}': {e}\n"
                        f"Using empty string"
                    )
                    result[key] = ""
            elif isinstance(value, dict):
                # Recursively template nested dicts
                result[key] = self._template_parameters(value, event)
            elif isinstance(value, list):
                # Template each list item
                result[key] = [
                    self._template_parameters({"item": item}, event)["item"]
                    if isinstance(item, dict | str)
                    else item
                    for item in value
                ]
            else:
                # Non-template value (int, bool, etc.)
                result[key] = value

        return result

    async def trigger_workflow(
        self,
        workflow_id: str,
        parameters: dict[str, Any],
        namespace: str | None = None,
    ) -> dict[str, Any] | None:
        """Trigger workflow via backend registry.

        Args:
            workflow_id: Workflow identifier
            parameters: Workflow parameters (already templated)
            namespace: Backend namespace (e.g., "n8n", "chora"), or None for default

        Returns:
            Workflow execution result, or None if backend unavailable
        """
        # Get backend by namespace (or default if None)
        backend = self.backend_registry.get_backend_by_namespace(
            namespace if namespace else ""
        )

        if not backend:
            logger.warning(
                f"Backend not found: {namespace or 'default'}\n"
                f"Workflow {workflow_id} will not be triggered"
            )
            return None

        logger.info(
            f"Triggering workflow: {workflow_id}\n"
            f"Backend: {namespace or 'default'}\n"
            f"Parameters: {parameters}"
        )

        try:
            # Call workflow via backend
            result = await backend.call_tool(workflow_id, parameters)
            logger.info(f"Workflow {workflow_id} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            raise RuntimeError(f"Workflow execution failed: {e}") from e

    async def reload_config(self) -> bool:
        """Reload config file.

        If new config is invalid, restores previous config and re-raises the exception.

        Returns:
            True if reload succeeded

        Raises:
            Exception: If config reload fails (previous config is restored
                before raising)
        """
        logger.info("Reloading event mappings config")

        # Keep backup of current mappings
        previous_mappings = self.mappings.copy()

        try:
            await self.load_mappings()
            logger.info("Config reloaded successfully")
            return True
        except Exception as e:
            logger.error(
                f"Failed to reload config: {e}\n"
                f"Restoring previous config ({len(previous_mappings)} mappings)"
            )
            self.mappings = previous_mappings
            raise  # Re-raise the exception after restoring previous config

    async def start_watching(self) -> None:
        """Start watching config file for changes.

        When config file is modified, automatically reloads mappings.
        Uses watchdog library for file system monitoring.
        """
        if self._watching:
            logger.warning("Already watching config file")
            return

        # Get the current event loop to use from the handler thread
        loop = asyncio.get_event_loop()

        class ConfigFileHandler(FileSystemEventHandler):  # type: ignore[misc]
            """Handler for config file modification events."""

            def __init__(self, router: "EventWorkflowRouter", event_loop: Any) -> None:
                self.router = router
                self.event_loop = event_loop

            def on_modified(self, event: Any) -> None:
                if event.src_path == self.router.config_path:
                    logger.info(f"Config file modified: {event.src_path}")
                    # Schedule reload in the main event loop from watchdog thread
                    # Note: reload_config() will raise on error but restore
                    # previous config first
                    asyncio.run_coroutine_threadsafe(
                        self.router.reload_config(), self.event_loop
                    )
                    # Don't wait for result - fire and forget
                    # Errors will be logged by reload_config()

        # Create observer and start watching
        self._observer = Observer()
        event_handler = ConfigFileHandler(self, loop)
        self._observer.schedule(
            event_handler,
            path=str(Path(self.config_path).parent),
            recursive=False,
        )
        self._observer.start()
        self._watching = True

        logger.info(f"Started watching config file: {self.config_path}")

    async def stop_watching(self) -> None:
        """Stop watching config file."""
        if not self._watching or not self._observer:
            return

        self._observer.stop()
        self._observer.join()
        self._watching = False
        logger.info("Stopped watching config file")

    async def route_event(self, event: dict[str, Any]) -> dict[str, Any] | None:
        """Match event, template parameters, and trigger workflow.

        This is the main entry point for routing events.

        Args:
            event: Event dictionary to route

        Returns:
            Workflow execution result or None if no pattern matched
        """
        # Match event to workflow
        match = await self.match_event(event)
        if not match:
            return None

        # Template parameters
        templated_params = self._template_parameters(match["parameters"], event)

        # Trigger workflow
        result = await self.trigger_workflow(
            workflow_id=match["workflow_id"],
            parameters=templated_params,
            namespace=match["namespace"],
        )

        return result
