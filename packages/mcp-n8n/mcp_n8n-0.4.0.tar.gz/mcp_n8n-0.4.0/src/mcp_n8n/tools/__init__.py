"""MCP tools for mcp-n8n gateway.

This package contains MCP tool implementations that extend the gateway's
capabilities beyond simple backend routing.
"""

from mcp_n8n.tools.event_query import get_events

__all__ = ["get_events"]
