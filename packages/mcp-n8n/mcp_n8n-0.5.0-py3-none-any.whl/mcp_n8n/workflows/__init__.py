"""Production workflow implementations for mcp-n8n.

This package contains workflow templates that demonstrate common integration patterns
using the mcp-n8n gateway with chora-compose and other backends.

Available workflows:
- daily_report: Generate daily engineering reports from git commits and gateway events
"""

from mcp_n8n.workflows.daily_report import (
    aggregate_statistics,
    get_recent_commits,
    run_daily_report,
)

__all__ = [
    "run_daily_report",
    "get_recent_commits",
    "aggregate_statistics",
]
