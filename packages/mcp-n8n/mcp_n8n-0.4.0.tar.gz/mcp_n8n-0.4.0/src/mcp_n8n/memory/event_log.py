"""Event log storage and querying for agent memory.

Provides append-only event storage with efficient querying by trace ID,
event type, status, and time range.
"""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal


class EventLog:
    """Event log storage and query interface."""

    def __init__(self, base_dir: Path | None = None) -> None:
        """Initialize event log.

        Args:
            base_dir: Base directory for event storage
                (defaults to .chora/memory/events)
        """
        self.base_dir = base_dir or Path(".chora/memory/events")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_by_trace(self, trace_id: str) -> list[dict[str, Any]]:
        """Get all events for a specific trace ID.

        Args:
            trace_id: Trace ID to query

        Returns:
            List of events (chronologically ordered)
        """
        events: list[dict[str, Any]] = []

        # Search all monthly partitions for trace files
        for month_dir in sorted(self.base_dir.iterdir()):
            if not month_dir.is_dir():
                continue

            trace_file = month_dir / "traces" / f"{trace_id}.jsonl"
            if trace_file.exists():
                with trace_file.open(encoding="utf-8") as f:
                    for line in f:
                        events.append(json.loads(line))

        return events

    def query(
        self,
        event_type: str | None = None,
        status: Literal["success", "failure", "pending"] | None = None,
        source: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query events with filters.

        Args:
            event_type: Filter by event type
            status: Filter by status
            source: Filter by source
            since: Start of time range (inclusive)
            until: End of time range (inclusive)
            limit: Maximum number of results

        Returns:
            List of matching events
        """
        events: list[dict[str, Any]] = []

        # Determine which monthly partitions to search
        if since:
            start_month = since.strftime("%Y-%m")
        else:
            start_month = None

        if until:
            end_month = until.strftime("%Y-%m")
        else:
            end_month = None

        # Search monthly partitions
        for month_dir in sorted(self.base_dir.iterdir()):
            if not month_dir.is_dir():
                continue

            month_name = month_dir.name
            if start_month and month_name < start_month:
                continue
            if end_month and month_name > end_month:
                continue

            events_file = month_dir / "events.jsonl"
            if not events_file.exists():
                continue

            with events_file.open(encoding="utf-8") as f:
                for line in f:
                    event = json.loads(line)

                    # Apply filters
                    if event_type and event["event_type"] != event_type:
                        continue
                    if status and event["status"] != status:
                        continue
                    if source and event["source"] != source:
                        continue

                    # Time range filter
                    event_time = datetime.fromisoformat(
                        event["timestamp"].replace("Z", "+00:00")
                    )
                    if since and event_time < since:
                        continue
                    if until and event_time > until:
                        continue

                    events.append(event)

                    # Check limit
                    if limit and len(events) >= limit:
                        return events

        return events

    def aggregate(
        self,
        group_by: Literal["event_type", "status", "source"],
        metric: Literal["count", "avg_duration"],
        since: datetime | None = None,
    ) -> dict[str, Any]:
        """Aggregate event statistics.

        Args:
            group_by: Field to group by
            metric: Metric to calculate
            since: Start of time range

        Returns:
            Dictionary mapping group values to metric values
        """
        results: dict[str, Any] = {}

        events = self.query(since=since)

        for event in events:
            key = event.get(group_by, "unknown")

            if metric == "count":
                results[key] = results.get(key, 0) + 1
            elif metric == "avg_duration":
                duration = event.get("metadata", {}).get("duration_ms", 0)
                if key not in results:
                    results[key] = {"total": 0, "count": 0}
                results[key]["total"] += duration
                results[key]["count"] += 1

        # Calculate averages
        if metric == "avg_duration":
            results = {
                key: val["total"] / val["count"] if val["count"] > 0 else 0
                for key, val in results.items()
            }

        return results


def query_events(
    event_type: str | None = None,
    status: Literal["success", "failure", "pending"] | None = None,
    since_hours: int | None = None,
    since_days: int | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Convenience function for querying events.

    Args:
        event_type: Filter by event type
        status: Filter by status
        since_hours: Query events from last N hours
        since_days: Query events from last N days
        limit: Maximum number of results

    Returns:
        List of matching events
    """
    log = EventLog()

    # Calculate since timestamp
    since = None
    if since_hours:
        since = datetime.now(UTC) - timedelta(hours=since_hours)
    elif since_days:
        since = datetime.now(UTC) - timedelta(days=since_days)

    return log.query(event_type=event_type, status=status, since=since, limit=limit)
