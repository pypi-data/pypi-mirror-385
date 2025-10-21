"""Tests for agent memory system."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from mcp_n8n.memory import (
    EventLog,
    KnowledgeGraph,
    TraceContext,
    emit_event,
    get_trace_id,
)


class TestTraceContext:
    """Tests for trace context management."""

    def test_get_trace_id_generates_uuid(self) -> None:
        """Test that get_trace_id generates valid UUID."""
        trace_id = get_trace_id()
        assert len(trace_id) == 36  # UUID format
        assert trace_id.count("-") == 4

    def test_trace_context_sets_environment(self) -> None:
        """Test that TraceContext sets environment variable."""
        with TraceContext("test-trace-123") as trace_id:
            assert trace_id == "test-trace-123"
            assert get_trace_id() == "test-trace-123"

    def test_trace_context_restores_previous(self) -> None:
        """Test that TraceContext restores previous trace ID."""
        with TraceContext("outer"):
            assert get_trace_id() == "outer"

            with TraceContext("inner"):
                assert get_trace_id() == "inner"

            assert get_trace_id() == "outer"


class TestEventEmission:
    """Tests for event emission."""

    def test_emit_event_creates_file(self, tmp_path: Path) -> None:
        """Test that emit_event creates event log file."""
        # Mock base directory
        import mcp_n8n.memory.trace as trace_module

        original_write = trace_module._write_event
        events_written = []

        def mock_write(
            event: dict[str, Any], base_dir: Path | str | None = None
        ) -> None:
            events_written.append(event)

        trace_module._write_event = mock_write

        try:
            event = emit_event(
                "test.event",
                trace_id="abc123",
                status="success",
                test_field="test_value",
            )

            assert event["event_type"] == "test.event"
            assert event["trace_id"] == "abc123"
            assert event["status"] == "success"
            assert event["metadata"]["test_field"] == "test_value"
            assert "timestamp" in event
            assert "schema_version" in event

            assert len(events_written) == 1
        finally:
            trace_module._write_event = original_write


class TestEventLog:
    """Tests for event log storage and querying."""

    def test_query_by_trace_id(self, tmp_path: Path) -> None:
        """Test querying events by trace ID."""
        log = EventLog(tmp_path)

        # Create test events
        trace_id = "test-trace-123"
        month_dir = tmp_path / datetime.now(UTC).strftime("%Y-%m")
        month_dir.mkdir(parents=True)
        trace_dir = month_dir / "traces"
        trace_dir.mkdir()

        trace_file = trace_dir / f"{trace_id}.jsonl"
        events = [
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": trace_id,
                "status": "success",
                "event_type": "test.event1",
            },
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": trace_id,
                "status": "success",
                "event_type": "test.event2",
            },
        ]

        with trace_file.open("w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        # Query by trace ID
        results = log.get_by_trace(trace_id)
        assert len(results) == 2
        assert results[0]["event_type"] == "test.event1"
        assert results[1]["event_type"] == "test.event2"

    def test_query_by_event_type(self, tmp_path: Path) -> None:
        """Test querying events by event type."""
        log = EventLog(tmp_path)

        # Create test events
        month_dir = tmp_path / datetime.now(UTC).strftime("%Y-%m")
        month_dir.mkdir(parents=True)

        events_file = month_dir / "events.jsonl"
        events = [
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": "trace1",
                "status": "success",
                "event_type": "test.success",
            },
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": "trace2",
                "status": "failure",
                "event_type": "test.failure",
            },
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": "trace3",
                "status": "success",
                "event_type": "test.success",
            },
        ]

        with events_file.open("w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        # Query by event type
        results = log.query(event_type="test.success")
        assert len(results) == 2

        # Query by status
        results = log.query(status="failure")
        assert len(results) == 1
        assert results[0]["event_type"] == "test.failure"

    def test_query_with_time_range(self, tmp_path: Path) -> None:
        """Test querying events with time range."""
        log = EventLog(tmp_path)

        # Create test events with different timestamps
        month_dir = tmp_path / datetime.now(UTC).strftime("%Y-%m")
        month_dir.mkdir(parents=True)

        events_file = month_dir / "events.jsonl"
        now = datetime.now(UTC)
        events = [
            {
                "timestamp": (now - timedelta(hours=2)).isoformat(),
                "trace_id": "trace1",
                "status": "success",
                "event_type": "test.old",
            },
            {
                "timestamp": now.isoformat(),
                "trace_id": "trace2",
                "status": "success",
                "event_type": "test.recent",
            },
        ]

        with events_file.open("w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        # Query recent events only
        results = log.query(since=now - timedelta(hours=1))
        assert len(results) == 1
        assert results[0]["event_type"] == "test.recent"

    def test_aggregate_count(self, tmp_path: Path) -> None:
        """Test aggregating event counts."""
        log = EventLog(tmp_path)

        # Create test events
        month_dir = tmp_path / datetime.now(UTC).strftime("%Y-%m")
        month_dir.mkdir(parents=True)

        events_file = month_dir / "events.jsonl"
        events = [
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": "t1",
                "status": "success",
                "event_type": "test.event1",
            },
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": "t2",
                "status": "success",
                "event_type": "test.event1",
            },
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "trace_id": "t3",
                "status": "failure",
                "event_type": "test.event2",
            },
        ]

        with events_file.open("w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        # Aggregate by event type
        results = log.aggregate(group_by="event_type", metric="count")
        assert results["test.event1"] == 2
        assert results["test.event2"] == 1


class TestKnowledgeGraph:
    """Tests for knowledge graph."""

    def test_create_note(self, tmp_path: Path) -> None:
        """Test creating knowledge note."""
        kg = KnowledgeGraph(tmp_path)

        note_id = kg.create_note(
            title="Test Note",
            content="This is a test note.",
            tags=["test", "example"],
            confidence="high",
        )

        assert note_id == "test-note"

        note_file = tmp_path / "notes" / "test-note.md"
        assert note_file.exists()

        # Read note
        with note_file.open() as f:
            content = f.read()
            assert "id: test-note" in content
            assert '["test", "example"]' in content
            assert "# Test Note" in content
            assert "This is a test note." in content

    def test_update_note(self, tmp_path: Path) -> None:
        """Test updating knowledge note."""
        kg = KnowledgeGraph(tmp_path)

        note_id = kg.create_note(
            title="Test Note", content="Original content.", tags=["test"]
        )

        kg.update_note(note_id, content_append="Updated content.", tags_add=["updated"])

        note = kg.get_note(note_id)
        assert "Original content." in note["content"]
        assert "Updated content." in note["content"]
        assert "test" in note["tags"]
        assert "updated" in note["tags"]

    def test_search_by_tags(self, tmp_path: Path) -> None:
        """Test searching notes by tags."""
        kg = KnowledgeGraph(tmp_path)

        kg.create_note("Note 1", "Content 1", tags=["backend", "timeout"])
        kg.create_note("Note 2", "Content 2", tags=["backend", "error"])
        kg.create_note("Note 3", "Content 3", tags=["frontend"])

        # Search for backend notes
        results = kg.search(tags=["backend"])
        assert len(results) == 2

        # Search for specific combination
        results = kg.search(tags=["backend", "timeout"])
        assert len(results) == 1

    def test_search_by_text(self, tmp_path: Path) -> None:
        """Test searching notes by text content."""
        kg = KnowledgeGraph(tmp_path)

        kg.create_note("Note 1", "Timeout error in backend")
        kg.create_note("Note 2", "Connection refused error")
        kg.create_note("Note 3", "Success message")

        # Search for "timeout"
        results = kg.search(text="timeout")
        assert len(results) == 1

        # Search for "error"
        results = kg.search(text="error")
        assert len(results) == 2

    def test_link_notes(self, tmp_path: Path) -> None:
        """Test linking notes together."""
        kg = KnowledgeGraph(tmp_path)

        note1_id = kg.create_note("Note 1", "First note")
        note2_id = kg.create_note("Note 2", "Second note", links=[note1_id])

        # Check links file
        links_file = tmp_path / "links.json"
        assert links_file.exists()

        with links_file.open() as f:
            links_data = json.load(f)
            # Find note2 entry
            note2_entry = next(n for n in links_data["notes"] if n["id"] == note2_id)
            assert note1_id in note2_entry["outgoing_links"]

            # Find note1 entry (should have incoming link)
            note1_entry = next(n for n in links_data["notes"] if n["id"] == note1_id)
            assert note2_id in note1_entry["incoming_links"]

    def test_get_related_notes(self, tmp_path: Path) -> None:
        """Test getting related notes."""
        kg = KnowledgeGraph(tmp_path)

        # Create chain: note1 -> note2 -> note3
        note1_id = kg.create_note("Note 1", "First note")
        note2_id = kg.create_note("Note 2", "Second note", links=[note1_id])
        note3_id = kg.create_note("Note 3", "Third note", links=[note2_id])

        # Get direct links (distance=1)
        related = kg.get_related(note3_id, max_distance=1)
        assert len(related) == 1
        assert related[0]["note_id"] == note2_id
        assert related[0]["distance"] == 1

        # Get extended links (distance=2)
        related = kg.get_related(note3_id, max_distance=2)
        assert len(related) == 2
        note_ids = {r["note_id"] for r in related}
        assert note2_id in note_ids
        assert note1_id in note_ids
