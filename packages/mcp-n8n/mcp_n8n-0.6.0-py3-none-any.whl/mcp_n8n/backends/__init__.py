"""Backend MCP server integrations.

This package provides abstractions for connecting to and managing
backend MCP servers, following the P5 Gateway & Aggregator pattern.
"""

from .base import Backend, BackendError, BackendStatus
from .registry import BackendRegistry

__all__ = ["Backend", "BackendError", "BackendStatus", "BackendRegistry"]
