"""MCP tool for querying gateway events.

This module provides the get_events MCP tool that allows querying events
from the gateway's telemetry system (.chora/memory/events/).
"""

import re
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from mcp_n8n.memory.event_log import EventLog

# Singleton EventLog instance for the gateway
# Will be initialized by gateway on startup
_event_log: EventLog | None = None


def set_event_log(event_log: EventLog) -> None:
    """Set the global EventLog instance for the gateway.

    Args:
        event_log: EventLog instance to use for queries
    """
    global _event_log
    _event_log = event_log


def _parse_time_range(since: str) -> datetime:
    """Parse time range string to datetime.

    Args:
        since: Time range string (e.g., "24h", "7d", ISO timestamp)

    Returns:
        Datetime cutoff for filtering

    Raises:
        ValueError: If time range format is invalid
    """
    # Try ISO timestamp first
    try:
        return datetime.fromisoformat(since)
    except ValueError:
        pass

    # Try relative time ranges (e.g., "24h", "7d")
    match = re.match(r"^(\d+)([hdwmy])$", since.lower())
    if not match:
        raise ValueError(
            f"Invalid time range format: {since}. "
            f"Expected: '24h', '7d', or ISO timestamp"
        )

    value = int(match.group(1))
    unit = match.group(2)

    now = datetime.now(UTC)

    if unit == "h":
        return now - timedelta(hours=value)
    elif unit == "d":
        return now - timedelta(days=value)
    elif unit == "w":
        return now - timedelta(weeks=value)
    elif unit == "m":
        return now - timedelta(days=value * 30)  # Approximate
    elif unit == "y":
        return now - timedelta(days=value * 365)  # Approximate

    raise ValueError(f"Unknown time unit: {unit}")


async def get_events(
    trace_id: str | None = None,
    event_type: str | None = None,
    status: Literal["success", "failure", "pending"] | None = None,
    since: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Query events from gateway telemetry.

    Args:
        trace_id: Filter by trace ID
        event_type: Filter by event type (e.g., "chora.content_generated")
        status: Filter by status (success/failure/pending)
        since: Filter by time range (e.g., "24h", "7d", ISO timestamp)
        limit: Maximum number of events to return (default 100)

    Returns:
        List of events matching the query filters, ordered by timestamp ascending

    Raises:
        RuntimeError: If EventLog is not initialized
        ValueError: If time range format is invalid
    """
    if _event_log is None:
        raise RuntimeError("EventLog not initialized. Call set_event_log() first.")

    # Parse time range if provided
    since_dt = None
    if since:
        since_dt = _parse_time_range(since)

    # Query events using EventLog
    if trace_id:
        # Use get_by_trace for trace-specific queries
        events = _event_log.get_by_trace(trace_id)
    else:
        # Use general query for other filters
        events = _event_log.query(
            event_type=event_type,
            status=status,
            since=since_dt,
        )

    # Apply additional filtering if needed (e.g., event_type when trace_id is set)
    if trace_id and event_type:
        events = [e for e in events if e.get("event_type") == event_type]
    if trace_id and status:
        events = [e for e in events if e.get("status") == status]
    if trace_id and since_dt:
        events = [
            e for e in events if datetime.fromisoformat(e["timestamp"]) >= since_dt
        ]

    # Apply limit
    if limit and len(events) > limit:
        # Return the most recent events (last N)
        events = events[-limit:]

    return events
