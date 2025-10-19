"""Trace context management for event correlation.

Implements CHORA_TRACE_ID propagation following the Chora ecosystem event schema.
"""

import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def get_trace_id() -> str:
    """Get trace ID from environment or generate new one.

    Returns:
        Trace ID (UUID string)
    """
    return os.getenv("CHORA_TRACE_ID", str(uuid.uuid4()))


def set_trace_id(trace_id: str) -> None:
    """Set trace ID in environment for subprocess propagation.

    Args:
        trace_id: Trace ID to set
    """
    os.environ["CHORA_TRACE_ID"] = trace_id


class TraceContext:
    """Context manager for trace ID scope."""

    def __init__(self, trace_id: str | None = None) -> None:
        """Initialize trace context.

        Args:
            trace_id: Explicit trace ID, or None to generate new one
        """
        self.trace_id = trace_id or str(uuid.uuid4())
        self.previous_trace_id: str | None = None

    def __enter__(self) -> str:
        """Enter trace context (set environment variable).

        Returns:
            Trace ID
        """
        self.previous_trace_id = os.getenv("CHORA_TRACE_ID")
        set_trace_id(self.trace_id)
        return self.trace_id

    def __exit__(self, *args: Any) -> None:
        """Exit trace context (restore previous trace ID)."""
        if self.previous_trace_id:
            set_trace_id(self.previous_trace_id)
        elif "CHORA_TRACE_ID" in os.environ:
            del os.environ["CHORA_TRACE_ID"]


def emit_event(
    event_type: str,
    trace_id: str | None = None,
    status: str = "success",
    source: str = "mcp-n8n",
    **metadata: Any,
) -> dict[str, Any]:
    """Emit event to memory system.

    Args:
        event_type: Event type (e.g., "gateway.tool_call")
        trace_id: Trace ID (defaults to current trace or new UUID)
        status: Event status ("success", "failure", "pending")
        source: Event source identifier
        **metadata: Additional event-specific metadata

    Returns:
        Event dictionary
    """
    event = {
        "timestamp": datetime.now(UTC).isoformat(),
        "trace_id": trace_id or get_trace_id(),
        "status": status,
        "schema_version": "1.0",
        "event_type": event_type,
        "source": source,
        "metadata": metadata,
    }

    # Write to event log
    _write_event(event)

    return event


def _write_event(event: dict[str, Any]) -> None:
    """Write event to JSONL log file.

    Args:
        event: Event dictionary
    """
    # Determine log directory (monthly partitions)
    timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
    month_dir = Path(".chora/memory/events") / timestamp.strftime("%Y-%m")
    month_dir.mkdir(parents=True, exist_ok=True)

    # Write to daily events file
    events_file = month_dir / "events.jsonl"
    with events_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    # Also write to trace-specific file
    trace_dir = month_dir / "traces"
    trace_dir.mkdir(exist_ok=True)
    trace_file = trace_dir / f"{event['trace_id']}.jsonl"
    with trace_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
