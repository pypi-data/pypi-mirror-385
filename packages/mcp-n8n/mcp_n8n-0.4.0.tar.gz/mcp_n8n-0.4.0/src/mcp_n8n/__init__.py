"""mcp-n8n: MCP Gateway & Aggregator.

A Pattern P5 (Gateway & Aggregator) MCP server that provides a unified
interface to multiple specialized MCP servers, with Chora Composer as the
exclusive artifact creation mechanism.

Architecture:
    - Gateway routes requests to appropriate backend servers
    - Tool namespacing prevents conflicts (chora:*, coda:*, etc.)
    - Backend servers managed as subprocesses or internal clients
    - DRSO-aligned telemetry and change signals

Backends:
    - Chora Composer: Exclusive artifact generation and assembly
    - Coda MCP: Data operations (list, read, write to Coda docs)
    - Future: n8n workflows, additional integrations
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
