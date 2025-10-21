"""Unit tests for daily report workflow.

DEPRECATED: This test file contains tests for the legacy API (pre-TDD refactor).
The daily_report module has been refactored following TDD methodology.
New comprehensive tests are in tests/unit/test_daily_report_workflow.py (28 tests).

These tests are kept for reference but skipped to avoid API incompatibility issues.

Legacy API issues:
- run_daily_report() signature changed: now requires backend_registry + event_log
- aggregate_statistics() return structure changed
- get_recent_commits() parameter renamed: repository_path → repo_path
- DailyReportResult changed from dict to dataclass

Tests are organized by acceptance criteria (AC) from
docs/workflows/daily-report-acceptance-criteria.md

Following TDD RED-GREEN-REFACTOR cycle:
- RED: Tests fail because code doesn't exist yet
- GREEN: Implement minimal code to pass tests
- REFACTOR: Improve design while keeping tests green
"""

import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

# mypy: disable-error-code="import-not-found,no-untyped-def,misc"
# Import from refactored module (for reference only - tests are skipped)
from mcp_n8n.workflows.daily_report import (  # noqa: F401
    aggregate_statistics,
    get_recent_commits,
    run_daily_report,
)

# Skip all tests in this file - deprecated legacy API tests
pytestmark = pytest.mark.skip(
    reason="Legacy API tests - see tests/unit/test_daily_report_workflow.py"
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_git_repo(tmp_path: Path) -> Path:
    """Create a mock git repository for testing."""
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

    return repo_path


@pytest.fixture
def sample_commits() -> list[dict[str, Any]]:
    """Sample commit data for testing."""
    now = datetime.now(UTC)
    return [
        {
            "hash": "abc1234",
            "author": "Alice",
            "message": "feat: Add new feature",
            "timestamp": (now - timedelta(hours=2)).isoformat(),
            "files_changed": 5,
        },
        {
            "hash": "def5678",
            "author": "Bob",
            "message": "fix: Bug fix",
            "timestamp": (now - timedelta(hours=5)).isoformat(),
            "files_changed": 2,
        },
        {
            "hash": "ghi9012",
            "author": "Charlie",
            "message": "docs: Update README",
            "timestamp": (now - timedelta(hours=10)).isoformat(),
            "files_changed": 1,
        },
    ]


@pytest.fixture
def sample_events() -> list[dict[str, Any]]:
    """Sample event data for testing."""
    now = datetime.now(UTC)
    events = []

    # Create 127 events with 95% success rate (per AC-10)
    for i in range(127):
        events.append(
            {
                "timestamp": (now - timedelta(hours=23 - (i % 24))).isoformat(),
                "trace_id": f"trace-{i // 5}",
                "event_type": (
                    "gateway.tool_call"
                    if i % 3 == 0
                    else "chora.content_generated"
                    if i % 3 == 1
                    else "chora.artifact_assembled"
                ),
                "status": "success" if i < 121 else "failure",
                "schema_version": "1.0",
                "metadata": {
                    "backend": "chora-composer" if i % 2 == 0 else "coda-mcp",
                    "tool": "chora:generate_content"
                    if i % 2 == 0
                    else "coda:list_docs",
                },
            }
        )

    return events


# ============================================================================
# AC-8: Git Commit Retrieval
# ============================================================================


@pytest.mark.asyncio
async def test_get_recent_commits_returns_all_commits(mock_git_repo: Path):
    """AC-8: Given 5 commits in last 24 hours, when calling get_recent_commits(),
    then all 5 commits are returned."""
    # Create 5 commits
    for i in range(5):
        test_file = mock_git_repo / f"file_{i}.txt"
        test_file.write_text(f"content {i}")
        subprocess.run(["git", "add", str(test_file)], cwd=mock_git_repo, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"commit {i}"], cwd=mock_git_repo, check=True
        )

    # from mcp_n8n.workflows.daily_report import get_recent_commits
    commits = await get_recent_commits(repo_path=str(mock_git_repo))

    assert len(commits) == 5
    assert all(isinstance(c, dict) for c in commits)


@pytest.mark.asyncio
async def test_get_recent_commits_includes_required_fields(mock_git_repo: Path):
    """AC-8: Each commit includes hash, author, message, timestamp, files_changed."""
    # Create 1 commit
    test_file = mock_git_repo / "test.txt"
    test_file.write_text("content")
    subprocess.run(["git", "add", str(test_file)], cwd=mock_git_repo, check=True)
    subprocess.run(
        ["git", "commit", "-m", "test commit"], cwd=mock_git_repo, check=True
    )

    # from mcp_n8n.workflows.daily_report import get_recent_commits
    commits = await get_recent_commits(repo_path=str(mock_git_repo))

    assert len(commits) == 1
    commit = commits[0]
    assert "hash" in commit
    assert "author" in commit
    assert "message" in commit
    assert "timestamp" in commit
    assert "files_changed" in commit


@pytest.mark.asyncio
async def test_get_recent_commits_orders_by_timestamp(mock_git_repo: Path):
    """AC-8: Commits are ordered by timestamp (most recent first)."""
    # from mcp_n8n.workflows.daily_report import get_recent_commits
    commits = await get_recent_commits(repo_path=str(mock_git_repo))

    # Verify chronological order (newest first)
    timestamps = [datetime.fromisoformat(c["timestamp"]) for c in commits]
    assert timestamps == sorted(timestamps, reverse=True)


# ============================================================================
# AC-10: Statistics Aggregation
# ============================================================================


def test_aggregate_statistics_calculates_success_rate(sample_events):
    """AC-10: Success rate is calculated correctly (121/127 = 95.28%)."""
    # from mcp_n8n.workflows.daily_report import aggregate_statistics
    stats = aggregate_statistics(sample_events)

    assert "success_rate" in stats
    assert abs(stats["success_rate"] - 95.28) < 0.01  # Allow small floating point error


def test_aggregate_statistics_groups_by_type(sample_events):
    """AC-10: Events are grouped by type."""
    # from mcp_n8n.workflows.daily_report import aggregate_statistics
    stats = aggregate_statistics(sample_events)

    assert "by_type" in stats
    assert isinstance(stats["by_type"], dict)
    assert "gateway.tool_call" in stats["by_type"]
    assert "chora.content_generated" in stats["by_type"]


def test_aggregate_statistics_groups_by_status(sample_events):
    """AC-10: Events are grouped by status."""
    # from mcp_n8n.workflows.daily_report import aggregate_statistics
    stats = aggregate_statistics(sample_events)

    assert "by_status" in stats
    assert stats["by_status"]["success"] == 121
    assert stats["by_status"]["failure"] == 6


def test_aggregate_statistics_extracts_tool_usage(sample_events):
    """AC-10: Tool usage counts are extracted from metadata."""
    # from mcp_n8n.workflows.daily_report import aggregate_statistics
    stats = aggregate_statistics(sample_events)

    assert "tool_usage" in stats
    assert isinstance(stats["tool_usage"], dict)
    assert "chora:generate_content" in stats["tool_usage"]


# ============================================================================
# AC-1: Successful Report Generation
# ============================================================================


@pytest.mark.asyncio
async def test_run_daily_report_returns_success(mock_git_repo: Path, tmp_path: Path):
    """AC-1: Successful report generation returns status 'success'."""
    # Create some commits
    test_file = mock_git_repo / "test.txt"
    test_file.write_text("content")
    subprocess.run(["git", "add", str(test_file)], cwd=mock_git_repo, check=True)
    subprocess.run(["git", "commit", "-m", "test"], cwd=mock_git_repo, check=True)

    # No need to mock chora-compose - using manual string generation for now
    from mcp_n8n.workflows.daily_report import run_daily_report

    result = await run_daily_report(repository_path=str(mock_git_repo))

    assert result["status"] == "success"
    assert result["report_path"] is not None
    assert result["error"] is None


@pytest.mark.asyncio
async def test_run_daily_report_includes_summary(mock_git_repo: Path):
    """AC-1: Report includes summary section with key metrics."""
    # from mcp_n8n.workflows.daily_report import run_daily_report
    result = await run_daily_report(repository_path=str(mock_git_repo))

    assert "summary" in result
    summary = result["summary"]
    assert "commit_count" in summary
    assert "event_count" in summary
    assert "tool_calls" in summary
    assert "success_rate" in summary
    assert "backends_active" in summary


# ============================================================================
# AC-2: Report with No Recent Commits
# ============================================================================


@pytest.mark.asyncio
async def test_run_daily_report_handles_no_commits(mock_git_repo: Path):
    """AC-2: Report generation succeeds even with no commits."""
    # Empty repository (initialized but no commits)
    # from mcp_n8n.workflows.daily_report import run_daily_report
    result = await run_daily_report(repository_path=str(mock_git_repo))

    assert result["status"] == "success"
    assert result["summary"]["commit_count"] == 0


# ============================================================================
# AC-4: Git Repository Not Found
# ============================================================================


@pytest.mark.asyncio
async def test_run_daily_report_fails_when_repo_not_found():
    """AC-4: Workflow fails gracefully when repository doesn't exist."""
    # from mcp_n8n.workflows.daily_report import run_daily_report
    result = await run_daily_report(repository_path="/nonexistent/repo")

    assert result["status"] == "failure"
    assert result["error"] is not None
    assert "Repository path not found" in result["error"]
    assert result["report_path"] is None


# ============================================================================
# AC-6: Custom Date Range
# ============================================================================


@pytest.mark.asyncio
async def test_run_daily_report_respects_since_hours(mock_git_repo: Path):
    """AC-6: Report respects custom time range (since_hours)."""
    # from mcp_n8n.workflows.daily_report import run_daily_report
    result = await run_daily_report(repository_path=str(mock_git_repo), since_hours=48)

    assert result["status"] == "success"
    # Verify time range in report content (implementation-specific)


# ============================================================================
# AC-17: Execution Time Target
# ============================================================================


@pytest.mark.asyncio
async def test_run_daily_report_completes_under_60_seconds(mock_git_repo: Path):
    """AC-17: Workflow completes in less than 60 seconds."""
    import time

    # from mcp_n8n.workflows.daily_report import run_daily_report
    start = time.time()
    result = await run_daily_report(repository_path=str(mock_git_repo))
    duration = time.time() - start

    assert result["status"] == "success"
    assert duration < 60, f"Execution took {duration}s, expected <60s"


# ============================================================================
# AC-21: Empty Repository
# ============================================================================


@pytest.mark.asyncio
async def test_run_daily_report_handles_empty_repository(mock_git_repo: Path):
    """AC-21: Handle freshly initialized repository with no commits."""
    # from mcp_n8n.workflows.daily_report import run_daily_report
    result = await run_daily_report(repository_path=str(mock_git_repo))

    assert result["status"] == "success"
    assert result["summary"]["commit_count"] == 0


# ============================================================================
# AC-22: Invalid Date Format
# ============================================================================


@pytest.mark.asyncio
async def test_run_daily_report_rejects_invalid_date():
    """AC-22: Reject invalid date format with helpful error."""
    # from mcp_n8n.workflows.daily_report import run_daily_report

    with pytest.raises(ValueError) as exc_info:
        await run_daily_report(date="2025-13-45")

    assert "YYYY-MM-DD" in str(exc_info.value)


# ============================================================================
# Helper function tests
# ============================================================================


def test_aggregate_statistics_with_empty_list():
    """Edge case: Statistics for empty event list."""
    # from mcp_n8n.workflows.daily_report import aggregate_statistics
    stats = aggregate_statistics([])

    assert stats["total_events"] == 0
    assert stats["success_rate"] == 0.0
    assert stats["by_type"] == {}
    assert stats["by_status"] == {}
    assert stats["tool_usage"] == {}


@pytest.mark.asyncio
async def test_get_recent_commits_with_since_hours_filter(mock_git_repo: Path):
    """Custom time range filtering for commits."""
    # from mcp_n8n.workflows.daily_report import get_recent_commits

    # Create commits at different times (mock implementation needed)
    commits = await get_recent_commits(
        repository_path=str(mock_git_repo), since_hours=48
    )

    # Verify all commits are within 48 hours
    now = datetime.now(UTC)
    cutoff = now - timedelta(hours=48)
    for commit in commits:
        commit_time = datetime.fromisoformat(commit["timestamp"])
        assert commit_time >= cutoff


# ============================================================================
# RED Phase Summary
# ============================================================================

# At this point, all tests are SKIPPED because the implementation doesn't exist.
# This is expected in the RED phase of TDD.
#
# Next steps (GREEN phase):
# 1. Create src/mcp_n8n/workflows/__init__.py
# 2. Create src/mcp_n8n/workflows/daily_report.py
# 3. Implement minimal functions to make tests pass
# 4. Run tests: pytest tests/workflows/test_daily_report.py
# 5. Watch tests turn GREEN one by one
# 6. REFACTOR once all tests pass
