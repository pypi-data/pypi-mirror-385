"""Daily Engineering Report workflow implementation.

This module implements the Daily Report workflow following the API specification
in docs/workflows/daily-report-api-reference.md and acceptance criteria in
docs/workflows/daily-report-acceptance-criteria.md.

The workflow aggregates:
- Recent Git commits from the repository
- Gateway telemetry events from the last N hours
- Tool usage statistics and performance metrics

Reports are stored using chora-compose ephemeral storage with 7-day retention.
"""

import logging
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, TypedDict

logger = logging.getLogger(__name__)


# ============================================================================
# Type Definitions
# ============================================================================


class CommitInfo(TypedDict):
    """Information about a single git commit."""

    hash: str
    author: str
    message: str
    timestamp: str  # ISO 8601 format
    files_changed: int


@dataclass
class DailyReportResult:
    """Result of running the daily report workflow."""

    content: str
    commit_count: int
    event_count: int
    statistics: dict[str, Any]
    metadata: dict[str, Any]


# ============================================================================
# Core Functions
# ============================================================================


async def get_recent_commits(
    repo_path: str = ".",
    since_hours: int = 24,
    branch: str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve commits from git repository in the specified time range.

    Args:
        repo_path: Path to git repository (default: current directory)
        since_hours: Hours to look back (default: 24)
        branch: Branch name (None = current branch)

    Returns:
        List of CommitInfo dicts with commit details

    Raises:
        RuntimeError: If git is not installed
        FileNotFoundError: If repository path doesn't exist
        ValueError: If path is not a git repository
    """
    repository_path = Path(repo_path).resolve()

    # Validate repository exists
    if not repository_path.exists():
        raise FileNotFoundError(f"Git repository not found: {repo_path}")

    # Calculate time cutoff
    since_time = datetime.now(UTC) - timedelta(hours=since_hours)
    since_arg = since_time.strftime("%Y-%m-%d %H:%M:%S")

    # Build git log command
    # Format: hash|author|timestamp|message (using --format with | separator)
    git_cmd = [
        "git",
        "log",
        f"--since={since_arg}",
        "--format=%H|%an|%aI|%s",  # hash|author|ISO timestamp|subject
        "--numstat",  # Show file statistics
    ]

    if branch:
        git_cmd.append(branch)

    try:
        result = subprocess.run(
            git_cmd,
            cwd=repository_path,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Git is not installed or not in PATH\n"
            "Install git: https://git-scm.com/downloads"
        )
    except subprocess.CalledProcessError as e:
        # Handle empty repository (no commits yet) - return empty list
        if "does not have any commits yet" in e.stderr.lower():
            logger.info(f"Repository {repository_path} has no commits yet")
            return []
        # Re-raise the error as-is (tests expect subprocess.CalledProcessError)
        raise

    # Parse output
    commits = []
    lines = result.stdout.strip().split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Parse commit line (hash|author|timestamp|message)
        if "|" in line:
            parts = line.split("|", 3)
            if len(parts) == 4:
                commit_hash, author, timestamp, message = parts

                # Count files changed (numstat lines follow until next commit or blank)
                files_changed = 0
                i += 1
                while i < len(lines) and lines[i].strip() and "|" not in lines[i]:
                    # numstat format: additions deletions filename
                    files_changed += 1
                    i += 1

                commits.append(
                    {
                        "hash": commit_hash,  # Full hash (40 chars)
                        "author": author,
                        "message": message,
                        "timestamp": timestamp,
                        "files_changed": files_changed,
                    }
                )
                continue

        i += 1

    logger.info(
        f"Retrieved {len(commits)} commits from {repository_path} "
        f"(since {since_hours}h ago)"
    )

    return commits


async def get_recent_events(
    event_log: Any, since_hours: int = 24
) -> list[dict[str, Any]]:
    """Retrieve recent events from the event log.

    Args:
        event_log: EventLog instance to query
        since_hours: Hours to look back (default: 24)

    Returns:
        List of event dictionaries

    Raises:
        RuntimeError: If event log query fails
    """
    try:
        # Query events from the last N hours
        events: list[dict[str, Any]] = event_log.query(since_hours=since_hours)
        logger.info(f"Retrieved {len(events)} events from last {since_hours} hours")
        return events
    except Exception as e:
        logger.error(f"Failed to query event log: {e}")
        raise RuntimeError(f"Event log query failed: {e}") from e


def aggregate_statistics(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate statistics from event list.

    Args:
        events: List of events from event log

    Returns:
        Dictionary with aggregated metrics
    """
    if not events:
        return {
            "total_events": 0,
            "tool_calls": 0,
            "backend_status_events": 0,
            "success_count": 0,
            "error_count": 0,
            "success_rate": 0.0,
            "by_backend": {},
            "avg_duration_ms": 0.0,
            "min_duration_ms": 0,
            "max_duration_ms": 0,
        }

    # Initialize counters
    by_backend: dict[str, int] = {}
    tool_calls = 0
    backend_status_events = 0
    success_count = 0
    error_count = 0
    durations: list[float] = []

    for event in events:
        # Count by event type
        event_type = event.get("type", "unknown")
        if event_type == "gateway.tool_call":
            tool_calls += 1
        elif event_type == "gateway.backend_status":
            backend_status_events += 1

        # Count by status
        status = event.get("status", "unknown")
        if status == "success":
            success_count += 1
        elif status == "failure":
            error_count += 1

        # Count by backend
        backend = event.get("backend", "unknown")
        by_backend[backend] = by_backend.get(backend, 0) + 1

        # Collect duration if available
        data = event.get("data", {})
        if "duration_ms" in data:
            durations.append(data["duration_ms"])

    # Calculate success rate
    total_events = len(events)
    success_rate = (success_count / total_events * 100) if total_events > 0 else 0.0

    # Calculate duration statistics
    avg_duration_ms = sum(durations) / len(durations) if durations else 0.0
    min_duration_ms = min(durations) if durations else 0
    max_duration_ms = max(durations) if durations else 0

    logger.info(
        f"Aggregated {total_events} events: "
        f"{success_count} success, "
        f"{error_count} failure "
        f"({success_rate:.2f}% success rate)"
    )

    return {
        "total_events": total_events,
        "tool_calls": tool_calls,
        "backend_status_events": backend_status_events,
        "success_count": success_count,
        "error_count": error_count,
        "success_rate": round(success_rate, 2),
        "by_backend": by_backend,
        "avg_duration_ms": avg_duration_ms,
        "min_duration_ms": min_duration_ms,
        "max_duration_ms": max_duration_ms,
    }


async def run_daily_report(
    backend_registry: Any,
    event_log: Any,
    repo_path: str = ".",
    since_hours: int = 24,
    date: str | None = None,
) -> DailyReportResult:
    """Generate a daily engineering report.

    This workflow:
    1. Gets recent commits from git repository
    2. Gets recent events from event log
    3. Aggregates statistics from events
    4. Generates report content via chora-compose
    5. Returns DailyReportResult with report content and metadata

    Args:
        backend_registry: BackendRegistry for accessing chora-compose backend
        event_log: EventLog instance for querying events
        repo_path: Path to git repository (default: current directory)
        since_hours: Hours to look back (default: 24)
        date: ISO date string YYYY-MM-DD (default: today)

    Returns:
        DailyReportResult with content, counts, statistics, and metadata

    Raises:
        RuntimeError: If chora-compose backend not available or report generation fails
    """
    # Use current date if not provided
    report_date = date or datetime.now(UTC).date().isoformat()
    generated_at = datetime.now(UTC).isoformat()

    logger.info(
        f"Starting daily report generation for {report_date} "
        f"(repo: {repo_path}, since: {since_hours}h)"
    )

    # Step 1: Get chora-compose backend
    chora_backend = backend_registry.get_backend_by_namespace("chora")
    if not chora_backend:
        raise RuntimeError(
            "chora-compose backend not available\n"
            "Daily report requires chora-compose for template rendering"
        )

    # Step 2: Gather git commits
    commits = await get_recent_commits(repo_path=repo_path, since_hours=since_hours)
    logger.info(f"Gathered {len(commits)} commits")

    # Step 3: Gather events from event log
    events = await get_recent_events(event_log=event_log, since_hours=since_hours)
    logger.info(f"Gathered {len(events)} events")

    # Step 4: Aggregate statistics
    stats = aggregate_statistics(events)

    # Step 5: Generate report content via chora-compose
    context = {
        "date": report_date,
        "generated_at": generated_at,
        "since_hours": since_hours,
        "commits": commits,
        "events": events,
        "stats": stats,
    }

    result = await chora_backend.call_tool(
        "generate_content",
        {
            "content_config_id": "daily-report",
            "context": context,
            "force": True,
        },
    )

    # Extract content from result
    content = result.get("content", "")

    # Return DailyReportResult
    return DailyReportResult(
        content=content,
        commit_count=len(commits),
        event_count=len(events),
        statistics=stats,
        metadata={
            "date": report_date,
            "generated_at": generated_at,
            "since_hours": since_hours,
        },
    )
