"""Main MCP gateway server implementation.

Implements Pattern P5 (Gateway & Aggregator) to provide a unified MCP
interface to multiple backend servers, with Chora Composer as the exclusive
artifact creation mechanism.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Literal

from fastmcp import FastMCP

from mcp_n8n import __version__
from mcp_n8n.backends import BackendRegistry
from mcp_n8n.config import load_config
from mcp_n8n.event_watcher import EventWatcher
from mcp_n8n.logging_config import setup_structured_logging
from mcp_n8n.memory import TraceContext, emit_event
from mcp_n8n.memory.event_log import EventLog
from mcp_n8n.tools.event_query import get_events as query_events
from mcp_n8n.tools.event_query import set_event_log

# Initialize gateway configuration
config = load_config()
setup_structured_logging(
    log_level=config.log_level,
    log_file="logs/mcp-n8n.log",
    debug=config.debug,
)
logger = logging.getLogger("mcp_n8n.gateway")

# Create FastMCP server
mcp = FastMCP(
    name="mcp-n8n",
    instructions=(
        "MCP Gateway & Aggregator providing unified access to multiple specialized "
        "MCP servers. Route artifact creation to Chora Composer (chora:* tools) "
        "and data operations to Coda MCP (coda:* tools). All tools are namespaced "
        "by backend."
    ),
    version=__version__,
)

# Initialize backend registry
registry = BackendRegistry()

# Initialize event monitoring components
event_log = EventLog(base_dir=Path(".chora/memory/events"))
event_watcher: EventWatcher | None = None


async def initialize_backends() -> None:
    """Initialize and start all configured backends."""
    global event_watcher

    logger.info("Initializing mcp-n8n gateway...")

    # Initialize EventLog for get_events tool
    set_event_log(event_log)

    # Start EventWatcher for chora-compose event monitoring
    try:
        event_watcher = EventWatcher(
            event_log=event_log,
            events_file="var/telemetry/events.jsonl",
            n8n_webhook_url=config.n8n_event_webhook_url,
        )
        await event_watcher.start()
        logger.info("EventWatcher started successfully")
    except Exception as e:
        logger.error(f"Failed to start EventWatcher: {e}")
        logger.warning("Event monitoring will be unavailable")
        event_watcher = None

    # Emit gateway started event
    with TraceContext() as trace_id:
        emit_event(
            "gateway.started",
            trace_id=trace_id,
            status="success",
            version=__version__,
            backend_count=len(config.get_all_backend_configs()),
            event_monitoring_enabled=event_watcher is not None,
        )

    # Register backends from configuration
    for backend_config in config.get_all_backend_configs():
        try:
            registry.register(backend_config)
            # Emit backend registered event
            emit_event(
                "gateway.backend_registered",
                status="success",
                backend_name=backend_config.name,
                namespace=backend_config.namespace,
                capabilities=backend_config.capabilities,
            )
        except ValueError as e:
            logger.error(f"Failed to register backend: {e}")
            emit_event(
                "gateway.backend_registered",
                status="failure",
                backend_name=backend_config.name,
                error=str(e),
            )

    # Start all backends
    await registry.start_all()

    # Emit backend started events
    status = registry.get_status()
    for backend_name, backend_status in status.items():
        event_status = "success" if backend_status["status"] == "running" else "failure"
        emit_event(
            "gateway.backend_started",
            status=event_status,
            backend_name=backend_name,
            namespace=backend_status["namespace"],
            tool_count=backend_status["tool_count"],
        )

    # Log backend status
    logger.info(f"Backend status: {status}")

    # Log aggregated capabilities
    tools = registry.get_all_tools()
    logger.info(f"Total tools available: {len(tools)}")
    for tool in tools:
        logger.info(f"  - {tool['name']} (backend: {tool.get('_backend', 'unknown')})")


async def shutdown_backends() -> None:
    """Shutdown all backends gracefully."""
    logger.info("Shutting down backends...")
    await registry.stop_all()

    # Stop EventWatcher
    if event_watcher:
        logger.info("Stopping EventWatcher...")
        await event_watcher.stop()
        logger.info("EventWatcher stopped")

    # Emit gateway stopped event
    emit_event("gateway.stopped", status="success")


# Register gateway tools
@mcp.tool()  # type: ignore[misc]
async def gateway_status() -> dict[str, Any]:
    """Get status of the gateway and all backends.

    Returns:
        Status information including backend health, tool counts, etc.
    """
    return {
        "gateway": {
            "name": "mcp-n8n",
            "version": __version__,
            "config": {
                "log_level": config.log_level,
                "debug": config.debug,
                "backend_timeout": config.backend_timeout,
            },
            "event_monitoring": {
                "enabled": event_watcher is not None,
                "webhook_configured": config.n8n_event_webhook_url is not None,
            },
        },
        "backends": registry.get_status(),
        "capabilities": {
            "tools": len(registry.get_all_tools()),
            "resources": len(registry.get_all_resources()),
            "prompts": len(registry.get_all_prompts()),
        },
    }


@mcp.tool()  # type: ignore[misc]
async def get_events(
    trace_id: str | None = None,
    event_type: str | None = None,
    status: Literal["success", "failure", "pending"] | None = None,
    since: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Query events from gateway telemetry.

    Allows querying events by trace_id, event_type, status, and time range.
    Useful for debugging multi-step workflows and correlating requests across
    gateway and backend boundaries.

    Args:
        trace_id: Filter by trace ID (returns all events for this trace)
        event_type: Filter by event type (e.g., "chora.content_generated")
        status: Filter by status (success/failure/pending)
        since: Filter by time range (e.g., "24h", "7d", ISO timestamp)
        limit: Maximum number of events to return (default 100, max 1000)

    Returns:
        List of events matching the query filters, ordered chronologically

    Examples:
        # Get all events for a trace
        events = await get_events(trace_id="abc123")

        # Get recent failures
        failures = await get_events(status="failure", since="1h")

        # Get all artifact assembly events from last day
        artifacts = await get_events(event_type="chora.artifact_assembled", since="24h")
    """
    # Validate limit
    if limit > 1000:
        limit = 1000

    # Call the event query function
    return await query_events(
        trace_id=trace_id,
        event_type=event_type,
        status=status,
        since=since,
        limit=limit,
    )


# TODO: Implement dynamic tool registration from backends
# For now, we'll document the expected tools:
#
# Chora Composer Tools (chora:*):
#   - chora:generate_content - Generate content from templates
#   - chora:assemble_artifact - Assemble artifacts from content pieces
#   - chora:list_generators - List available generators
#   - chora:validate_content - Validate content or configurations
#
# Coda MCP Tools (coda:*):
#   - coda:list_docs - List Coda documents
#   - coda:list_tables - List tables in a document
#   - coda:list_rows - List rows from a table
#   - coda:create_hello_doc_in_folder - Create a sample document


def main() -> None:
    """Main entry point for the gateway server."""
    print("=" * 60, file=sys.stderr)
    print(f"mcp-n8n Gateway v{__version__}", file=sys.stderr)
    print("Pattern P5: Gateway & Aggregator", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(file=sys.stderr)

    # Print configuration
    print("Configuration:", file=sys.stderr)
    print(f"  Log Level: {config.log_level}", file=sys.stderr)
    print(f"  Debug: {config.debug}", file=sys.stderr)
    print(f"  Backend Timeout: {config.backend_timeout}s", file=sys.stderr)
    print(file=sys.stderr)

    # Print backend status
    backends = config.get_all_backend_configs()
    print(f"Backends configured: {len(backends)}", file=sys.stderr)
    for backend in backends:
        status = "✓" if backend.enabled else "✗"
        caps = backend.capabilities
        print(
            f"  {status} {backend.name} ({backend.namespace}:*) - {caps}",
            file=sys.stderr,
        )
    print(file=sys.stderr)

    # Check for missing credentials
    warnings = []
    if not config.anthropic_api_key:
        warnings.append("ANTHROPIC_API_KEY not set - Chora Composer will be disabled")
    if not config.coda_api_key:
        warnings.append("CODA_API_KEY not set - Coda MCP will be disabled")

    if warnings:
        print("⚠️  Warnings:", file=sys.stderr)
        for warning in warnings:
            print(f"  - {warning}", file=sys.stderr)
        print(file=sys.stderr)

    print("Starting gateway on STDIO transport...", file=sys.stderr)
    print("-" * 60, file=sys.stderr)

    # Initialize backends before starting server
    asyncio.run(initialize_backends())

    try:
        # Run FastMCP server
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        # Cleanup
        asyncio.run(shutdown_backends())
        logger.info("Gateway shutdown complete")


if __name__ == "__main__":
    main()
