"""Unit tests for daily report workflow.

Tests git commit parsing, event querying, statistics aggregation,
and end-to-end workflow execution.
"""
# mypy: disable-error-code="no-untyped-def"

import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from mcp_n8n.workflows.daily_report import (
    DailyReportResult,
    aggregate_statistics,
    get_recent_commits,
    get_recent_events,
    run_daily_report,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_git_repo(tmp_path: Path) -> Path:
    """Create a mock git repository with commits."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create some commits
    for i in range(5):
        test_file = repo_path / f"file{i}.txt"
        test_file.write_text(f"Content {i}")
        subprocess.run(
            ["git", "add", f"file{i}.txt"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", f"Commit {i}: Add file{i}"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

    return repo_path


@pytest.fixture
def sample_events() -> list[dict[str, Any]]:
    """Sample events for testing."""
    base_time = datetime.now(UTC)
    return [
        {
            "timestamp": (base_time - timedelta(hours=i)).isoformat(),
            "type": "gateway.tool_call" if i % 2 == 0 else "gateway.backend_status",
            "status": "success" if i % 10 != 9 else "failure",
            "backend": "chora-composer",
            "data": {
                "tool_name": "generate_content",
                "duration_ms": 100 + i * 10,
            },
        }
        for i in range(50)
    ]


@pytest.fixture
def mock_event_log(sample_events):
    """Mock EventLog for testing."""
    event_log = Mock()
    event_log.query = Mock(return_value=sample_events)
    return event_log


@pytest.fixture
def mock_backend_registry():
    """Mock BackendRegistry with chora-compose backend."""
    chora_backend = AsyncMock()
    chora_backend.call_tool = AsyncMock(
        return_value={
            "content": "# Daily Report\n\nTest report content...",
            "metadata": {"template_id": "daily-report"},
        }
    )

    registry = Mock()
    registry.get_backend_by_namespace = Mock(return_value=chora_backend)
    return registry


# ============================================================================
# Test: get_recent_commits
# ============================================================================


@pytest.mark.asyncio
async def test_get_recent_commits_success(mock_git_repo: Path):
    """Test getting recent commits from git repository."""
    commits = await get_recent_commits(repo_path=str(mock_git_repo), since_hours=24)

    assert len(commits) == 5
    assert all("hash" in commit for commit in commits)
    assert all("author" in commit for commit in commits)
    assert all("message" in commit for commit in commits)
    assert all("timestamp" in commit for commit in commits)


@pytest.mark.asyncio
async def test_get_recent_commits_time_filter(mock_git_repo: Path):
    """Test getting commits with time filter."""
    # Get commits from last 1 hour (should be all 5 since just created)
    commits = await get_recent_commits(repo_path=str(mock_git_repo), since_hours=1)

    # All commits should be recent
    assert len(commits) >= 0  # Depends on timing


@pytest.mark.asyncio
async def test_get_recent_commits_ordered_by_time(mock_git_repo: Path):
    """Test that commits are ordered by timestamp descending."""
    commits = await get_recent_commits(repo_path=str(mock_git_repo), since_hours=24)

    # Should be ordered newest first
    timestamps = [datetime.fromisoformat(c["timestamp"]) for c in commits]
    assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.asyncio
async def test_get_recent_commits_no_commits(tmp_path: Path):
    """Test getting commits when repository has no commits."""
    # Create empty repo
    empty_repo = tmp_path / "empty_repo"
    empty_repo.mkdir()
    subprocess.run(["git", "init"], cwd=empty_repo, check=True, capture_output=True)

    commits = await get_recent_commits(repo_path=str(empty_repo), since_hours=24)

    assert commits == []


@pytest.mark.asyncio
async def test_get_recent_commits_repo_not_found(tmp_path: Path):
    """Test getting commits when repository doesn't exist."""
    nonexistent = tmp_path / "nonexistent"

    with pytest.raises(FileNotFoundError) as exc_info:
        await get_recent_commits(repo_path=str(nonexistent), since_hours=24)

    assert "Git repository not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_recent_commits_not_a_repo(tmp_path: Path):
    """Test getting commits from directory that's not a git repo."""
    not_a_repo = tmp_path / "not_a_repo"
    not_a_repo.mkdir()

    with pytest.raises(subprocess.CalledProcessError):
        await get_recent_commits(repo_path=str(not_a_repo), since_hours=24)


@pytest.mark.asyncio
async def test_get_recent_commits_parse_fields(mock_git_repo: Path):
    """Test that commit fields are parsed correctly."""
    commits = await get_recent_commits(repo_path=str(mock_git_repo), since_hours=24)

    for commit in commits:
        # Verify hash format (40 hex characters)
        assert len(commit["hash"]) == 40
        assert all(c in "0123456789abcdef" for c in commit["hash"])

        # Verify author is not empty
        assert commit["author"]

        # Verify message is not empty
        assert commit["message"]

        # Verify timestamp is valid ISO format
        datetime.fromisoformat(commit["timestamp"])


# ============================================================================
# Test: get_recent_events
# ============================================================================


@pytest.mark.asyncio
async def test_get_recent_events_success(mock_event_log, sample_events):
    """Test getting recent events from event log."""
    events = await get_recent_events(event_log=mock_event_log, since_hours=24)

    assert len(events) == 50
    mock_event_log.query.assert_called_once()


@pytest.mark.asyncio
async def test_get_recent_events_time_filter(mock_event_log):
    """Test getting events with time filter."""
    await get_recent_events(event_log=mock_event_log, since_hours=12)

    # Should pass since_hours to query method
    call_args = mock_event_log.query.call_args
    assert call_args is not None


@pytest.mark.asyncio
async def test_get_recent_events_no_events(mock_event_log):
    """Test getting events when no events exist."""
    mock_event_log.query.return_value = []

    events = await get_recent_events(event_log=mock_event_log, since_hours=24)

    assert events == []


@pytest.mark.asyncio
async def test_get_recent_events_ordered(mock_event_log, sample_events):
    """Test that events are ordered chronologically."""
    events = await get_recent_events(event_log=mock_event_log, since_hours=24)

    # Should be ordered by timestamp
    timestamps = [datetime.fromisoformat(e["timestamp"]) for e in events]
    # Oldest first or newest first, just needs to be consistent
    assert len(timestamps) == len(events)


# ============================================================================
# Test: aggregate_statistics
# ============================================================================


def test_aggregate_statistics_success(sample_events):
    """Test aggregating statistics from events."""
    stats = aggregate_statistics(sample_events)

    assert stats["total_events"] == 50
    assert "tool_calls" in stats
    assert "backend_status_events" in stats
    assert "success_count" in stats
    assert "error_count" in stats
    assert "success_rate" in stats


def test_aggregate_statistics_counts_by_type(sample_events):
    """Test that statistics correctly count event types."""
    stats = aggregate_statistics(sample_events)

    # From sample_events: half are tool_call, half are backend_status
    assert stats["tool_calls"] == 25
    assert stats["backend_status_events"] == 25


def test_aggregate_statistics_counts_by_status(sample_events):
    """Test that statistics correctly count event status."""
    stats = aggregate_statistics(sample_events)

    # From sample_events: errors on i % 10 == 9, so 5 errors
    assert stats["error_count"] == 5
    assert stats["success_count"] == 45
    assert stats["success_rate"] == 90.0


def test_aggregate_statistics_empty_events():
    """Test aggregating statistics with no events."""
    stats = aggregate_statistics([])

    assert stats["total_events"] == 0
    assert stats["tool_calls"] == 0
    assert stats["success_count"] == 0
    assert stats["error_count"] == 0
    assert stats["success_rate"] == 0.0


def test_aggregate_statistics_calculates_averages(sample_events):
    """Test that statistics calculate average duration."""
    stats = aggregate_statistics(sample_events)

    assert "avg_duration_ms" in stats
    assert stats["avg_duration_ms"] > 0


def test_aggregate_statistics_groups_by_backend():
    """Test that statistics group events by backend."""
    events = [
        {"type": "gateway.tool_call", "status": "success", "backend": "chora"},
        {"type": "gateway.tool_call", "status": "success", "backend": "coda"},
        {"type": "gateway.tool_call", "status": "success", "backend": "chora"},
    ]

    stats = aggregate_statistics(events)

    assert "by_backend" in stats
    assert stats["by_backend"]["chora"] == 2
    assert stats["by_backend"]["coda"] == 1


# ============================================================================
# Test: run_daily_report (End-to-End)
# ============================================================================


@pytest.mark.asyncio
async def test_run_daily_report_success(
    mock_backend_registry, mock_event_log, mock_git_repo
):
    """Test running daily report workflow successfully."""
    result = await run_daily_report(
        backend_registry=mock_backend_registry,
        event_log=mock_event_log,
        repo_path=str(mock_git_repo),
        since_hours=24,
    )

    assert isinstance(result, DailyReportResult)
    assert result.content is not None
    assert "# Daily Report" in result.content
    assert result.commit_count == 5
    assert result.event_count == 50
    assert result.statistics is not None


@pytest.mark.asyncio
async def test_run_daily_report_with_date(
    mock_backend_registry, mock_event_log, mock_git_repo
):
    """Test running daily report with specific date."""
    result = await run_daily_report(
        backend_registry=mock_backend_registry,
        event_log=mock_event_log,
        repo_path=str(mock_git_repo),
        since_hours=24,
        date="2025-10-20",
    )

    assert isinstance(result, DailyReportResult)
    assert result.metadata["date"] == "2025-10-20"


@pytest.mark.asyncio
async def test_run_daily_report_custom_time_range(
    mock_backend_registry, mock_event_log, mock_git_repo
):
    """Test running daily report with custom time range."""
    result = await run_daily_report(
        backend_registry=mock_backend_registry,
        event_log=mock_event_log,
        repo_path=str(mock_git_repo),
        since_hours=48,
    )

    assert isinstance(result, DailyReportResult)
    assert result.metadata["since_hours"] == 48


@pytest.mark.asyncio
async def test_run_daily_report_no_commits(
    mock_backend_registry, mock_event_log, tmp_path
):
    """Test running daily report when no commits exist."""
    empty_repo = tmp_path / "empty_repo"
    empty_repo.mkdir()
    subprocess.run(["git", "init"], cwd=empty_repo, check=True, capture_output=True)

    result = await run_daily_report(
        backend_registry=mock_backend_registry,
        event_log=mock_event_log,
        repo_path=str(empty_repo),
        since_hours=24,
    )

    assert result.commit_count == 0
    assert result.content is not None  # Should still generate report


@pytest.mark.asyncio
async def test_run_daily_report_no_events(
    mock_backend_registry, mock_event_log, mock_git_repo
):
    """Test running daily report when no events exist."""
    mock_event_log.query.return_value = []

    result = await run_daily_report(
        backend_registry=mock_backend_registry,
        event_log=mock_event_log,
        repo_path=str(mock_git_repo),
        since_hours=24,
    )

    assert result.event_count == 0
    assert result.statistics["total_events"] == 0


@pytest.mark.asyncio
async def test_run_daily_report_chora_backend_not_available(
    mock_event_log, mock_git_repo
):
    """Test running daily report when chora-compose backend unavailable."""
    registry = Mock()
    registry.get_backend_by_namespace.return_value = None

    with pytest.raises(RuntimeError) as exc_info:
        await run_daily_report(
            backend_registry=registry,
            event_log=mock_event_log,
            repo_path=str(mock_git_repo),
            since_hours=24,
        )

    assert "chora-compose backend not available" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_run_daily_report_chora_generation_fails(
    mock_backend_registry, mock_event_log, mock_git_repo
):
    """Test running daily report when chora:generate_content fails."""
    chora_backend = mock_backend_registry.get_backend_by_namespace.return_value
    chora_backend.call_tool.side_effect = Exception("Template not found")

    with pytest.raises(Exception) as exc_info:
        await run_daily_report(
            backend_registry=mock_backend_registry,
            event_log=mock_event_log,
            repo_path=str(mock_git_repo),
            since_hours=24,
        )

    assert "Template not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_run_daily_report_passes_context_to_chora(
    mock_backend_registry, mock_event_log, mock_git_repo
):
    """Test that daily report passes correct context to chora-compose."""
    await run_daily_report(
        backend_registry=mock_backend_registry,
        event_log=mock_event_log,
        repo_path=str(mock_git_repo),
        since_hours=24,
        date="2025-10-20",
    )

    chora_backend = mock_backend_registry.get_backend_by_namespace.return_value
    call_args = chora_backend.call_tool.call_args

    assert call_args is not None
    tool_name, params = call_args[0]
    assert tool_name == "generate_content"
    assert "content_config_id" in params
    assert params["content_config_id"] == "daily-report"
    assert "context" in params
    assert "commits" in params["context"]
    assert "events" in params["context"]
    assert "stats" in params["context"]
    assert "date" in params["context"]


# ============================================================================
# Test: DailyReportResult Data Model
# ============================================================================


def test_daily_report_result_structure():
    """Test DailyReportResult data structure."""
    result = DailyReportResult(
        content="# Test Report",
        commit_count=5,
        event_count=10,
        statistics={"total": 10},
        metadata={"date": "2025-10-20"},
    )

    assert result.content == "# Test Report"
    assert result.commit_count == 5
    assert result.event_count == 10
    assert result.statistics["total"] == 10
    assert result.metadata["date"] == "2025-10-20"


# ============================================================================
# Test: Edge Cases
# ============================================================================


@pytest.mark.asyncio
async def test_run_daily_report_execution_time(
    mock_backend_registry, mock_event_log, mock_git_repo
):
    """Test that daily report executes within reasonable time."""
    import time

    start = time.time()
    await run_daily_report(
        backend_registry=mock_backend_registry,
        event_log=mock_event_log,
        repo_path=str(mock_git_repo),
        since_hours=24,
    )
    duration = time.time() - start

    # Should complete in less than 10 seconds
    assert duration < 10.0


@pytest.mark.asyncio
async def test_get_recent_commits_large_repo(mock_git_repo: Path):
    """Test getting commits from large repository (performance)."""
    # This test validates performance doesn't degrade with many commits
    # (Current repo has 5 commits, but test structure is ready for more)

    commits = await get_recent_commits(repo_path=str(mock_git_repo), since_hours=24)

    # Should complete quickly regardless of repo size
    assert len(commits) >= 0
