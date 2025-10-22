"""CLI commands for chora-memory."""

import json
from datetime import UTC, datetime, timedelta

import click

from mcp_n8n.memory import EventLog, KnowledgeGraph
from mcp_n8n.memory.profiles import AgentProfileManager


@click.command()
@click.option(
    "--type", "-t", "event_type", help="Filter by event type (e.g., gateway.started)"
)
@click.option(
    "--status",
    "-s",
    type=click.Choice(["success", "failure", "pending"]),
    help="Filter by status",
)
@click.option(
    "--since",
    help='Time range (e.g., "24h", "7d", "2025-01-17")',
)
@click.option("--limit", "-n", type=int, help="Maximum number of results")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def query(
    event_type: str | None,
    status: str | None,
    since: str | None,
    limit: int | None,
    output_json: bool,
) -> None:
    """Query events from the event log.

    Examples:

        # Get recent failures
        chora-memory query --type gateway.backend_failed --status failure --since 24h

        # Get all events from last 7 days
        chora-memory query --since 7d --limit 100

        # Get events as JSON for processing
        chora-memory query --type gateway.started --json
    """
    log = EventLog()

    # Parse since parameter
    since_dt = None
    if since:
        since_dt = _parse_since(since)

    # Query events
    events = log.query(
        event_type=event_type, status=status, since=since_dt, limit=limit
    )

    if output_json:
        click.echo(json.dumps(events, indent=2))
    else:
        if not events:
            click.echo("No events found.")
            return

        click.echo(f"Found {len(events)} events:\n")
        for event in events:
            _print_event(event)


@click.command()
@click.argument("trace_id")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def trace(trace_id: str, output_json: bool) -> None:
    """Show timeline for a specific trace ID.

    Examples:

        # Show workflow timeline
        chora-memory trace abc123

        # Get trace as JSON
        chora-memory trace abc123 --json
    """
    log = EventLog()
    events = log.get_by_trace(trace_id)

    if not events:
        click.echo(f"No events found for trace_id: {trace_id}", err=True)
        return

    if output_json:
        click.echo(json.dumps(events, indent=2))
    else:
        click.echo(f"Trace Timeline: {trace_id}\n")
        click.echo(f"Total events: {len(events)}\n")

        # Calculate total duration
        if len(events) >= 2:
            start_time = datetime.fromisoformat(
                events[0]["timestamp"].replace("Z", "+00:00")
            )
            end_time = datetime.fromisoformat(
                events[-1]["timestamp"].replace("Z", "+00:00")
            )
            duration = (end_time - start_time).total_seconds() * 1000
            click.echo(f"Duration: {duration:.0f}ms\n")

        # Print timeline
        for i, event in enumerate(events, 1):
            _print_event(event, index=i)


@click.group()
def knowledge() -> None:
    """Manage knowledge graph notes."""
    pass


@knowledge.command("search")
@click.option("--tag", "-t", multiple=True, help="Filter by tags (multiple allowed)")
@click.option("--text", help="Search in content (case-insensitive)")
@click.option(
    "--confidence",
    type=click.Choice(["low", "medium", "high"]),
    help="Filter by confidence",
)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def knowledge_search(
    tag: tuple[str, ...], text: str | None, confidence: str | None, output_json: bool
) -> None:
    """Search knowledge notes.

    Examples:

        # Find notes about backend troubleshooting
        chora-memory knowledge search --tag backend --tag troubleshooting

        # Search for timeout issues
        chora-memory knowledge search --text timeout

        # Find high-confidence notes
        chora-memory knowledge search --confidence high
    """
    kg = KnowledgeGraph()

    # Convert tuple to list
    tags = list(tag) if tag else None

    # Search notes
    note_ids = kg.search(tags=tags, text=text, confidence=confidence)  # type: ignore

    if not note_ids:
        click.echo("No notes found.")
        return

    if output_json:
        notes = [kg.get_note(note_id) for note_id in note_ids]
        click.echo(json.dumps(notes, indent=2))
    else:
        click.echo(f"Found {len(note_ids)} notes:\n")
        for note_id in note_ids:
            note = kg.get_note(note_id)
            click.echo(f"ID: {note['id']}")
            click.echo(f"Tags: {', '.join(note.get('tags', []))}")
            click.echo(f"Confidence: {note.get('confidence', 'unknown')}")
            click.echo(f"Created: {note.get('created', 'unknown')}")
            click.echo()


@knowledge.command("create")
@click.argument("title")
@click.option("--content", "-c", help="Note content (markdown)")
@click.option("--tag", "-t", multiple=True, help="Tags (multiple allowed)")
@click.option(
    "--confidence",
    type=click.Choice(["low", "medium", "high"]),
    default="medium",
    help="Confidence level",
)
@click.option("--link", "-l", multiple=True, help="Link to other notes")
def knowledge_create(
    title: str,
    content: str | None,
    tag: tuple[str, ...],
    confidence: str,
    link: tuple[str, ...],
) -> None:
    """Create new knowledge note.

    Examples:

        # Create note from command line
        chora-memory knowledge create "Backend Timeout Fix" \\
            --content "Increase timeout to 60s" \\
            --tag troubleshooting --tag backend \\
            --confidence high

        # Create note and link to existing notes
        chora-memory knowledge create "Error Handling Pattern" \\
            --link backend-timeout-fix \\
            --link trace-context-pattern
    """
    kg = KnowledgeGraph()

    # Read content from stdin if not provided
    if content is None:
        click.echo("Enter note content (Ctrl+D when done):")
        content = click.get_text_stream("stdin").read()

    # Create note
    note_id = kg.create_note(
        title=title,
        content=content,
        tags=list(tag) if tag else None,
        links=list(link) if link else None,
        confidence=confidence,  # type: ignore
    )

    click.echo(f"Created note: {note_id}")


@knowledge.command("show")
@click.argument("note_id")
def knowledge_show(note_id: str) -> None:
    """Show knowledge note details.

    Examples:

        chora-memory knowledge show backend-timeout-fix
    """
    kg = KnowledgeGraph()

    try:
        note = kg.get_note(note_id)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        return

    # Print note
    click.echo(f"ID: {note['id']}")
    click.echo(f"Tags: {', '.join(note.get('tags', []))}")
    click.echo(f"Confidence: {note.get('confidence', 'unknown')}")
    click.echo(f"Created: {note.get('created', 'unknown')}")
    click.echo(f"Updated: {note.get('updated', 'unknown')}")
    click.echo(f"Links: {', '.join(note.get('linked_to', []))}")
    click.echo("\nContent:")
    click.echo("=" * 60)
    click.echo(note["content"])


@click.command()
@click.option("--since", help='Time range (e.g., "24h", "7d")', default="7d")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def stats(since: str, output_json: bool) -> None:
    """Show memory system statistics.

    Examples:

        # Stats for last 7 days
        chora-memory stats

        # Stats for last 24 hours
        chora-memory stats --since 24h

        # Get stats as JSON
        chora-memory stats --json
    """
    log = EventLog()
    kg = KnowledgeGraph()

    # Parse since
    since_dt = _parse_since(since)

    # Get event statistics
    event_counts = log.aggregate(group_by="event_type", metric="count", since=since_dt)
    status_counts = log.aggregate(group_by="status", metric="count", since=since_dt)

    # Get knowledge statistics
    all_notes = kg.search()
    note_count = len(all_notes)

    if output_json:
        stats_data = {
            "time_range": since,
            "events": {
                "by_type": event_counts,
                "by_status": status_counts,
                "total": sum(event_counts.values()),
            },
            "knowledge": {"total_notes": note_count},
        }
        click.echo(json.dumps(stats_data, indent=2))
    else:
        click.echo(f"Memory Statistics (last {since}):\n")

        click.echo("Events by Type:")
        for event_type, count in sorted(
            event_counts.items(), key=lambda x: x[1], reverse=True
        ):
            click.echo(f"  {event_type}: {count}")

        click.echo("\nEvents by Status:")
        for status, count in status_counts.items():
            click.echo(f"  {status}: {count}")

        click.echo(f"\nKnowledge Notes: {note_count}")


@click.group()
def profile() -> None:
    """Manage agent profiles."""
    pass


@profile.command("show")
@click.argument("agent_name")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def profile_show(agent_name: str, output_json: bool) -> None:
    """Show agent profile.

    Examples:

        chora-memory profile show claude-code
    """
    manager = AgentProfileManager()

    try:
        agent_profile = manager.get_profile(agent_name)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        return

    if output_json:
        click.echo(json.dumps(agent_profile.to_dict(), indent=2))
    else:
        click.echo(f"Agent: {agent_profile.agent_name}")
        click.echo(f"Version: {agent_profile.agent_version}")
        click.echo(f"Last Active: {agent_profile.last_active}")
        click.echo(f"Session Count: {agent_profile.session_count}")
        click.echo("\nCapabilities:")
        for cap, details in agent_profile.capabilities.items():
            click.echo(f"  {cap}:")
            click.echo(f"    Skill Level: {details.get('skill_level', 'unknown')}")
            success = details.get("successful_operations", 0)
            failed = details.get("failed_operations", 0)
            click.echo(f"    Success Rate: {success}/{success + failed}")


@profile.command("list")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def profile_list(output_json: bool) -> None:
    """List all agent profiles.

    Examples:

        chora-memory profile list
    """
    manager = AgentProfileManager()
    profiles = manager.list_profiles()

    if output_json:
        click.echo(json.dumps(profiles, indent=2))
    else:
        if not profiles:
            click.echo("No agent profiles found.")
            return

        click.echo(f"Found {len(profiles)} agent profiles:\n")
        for profile_name in profiles:
            agent_profile = manager.get_profile(profile_name)
            click.echo(f"  {profile_name} (sessions: {agent_profile.session_count})")


# Helper functions


def _parse_since(since: str) -> datetime:
    """Parse since parameter to datetime.

    Supports:
    - Relative: "24h", "7d"
    - Absolute: "2025-01-17"
    """
    now = datetime.now(UTC)

    if since.endswith("h"):
        hours = int(since[:-1])
        return now - timedelta(hours=hours)
    elif since.endswith("d"):
        days = int(since[:-1])
        return now - timedelta(days=days)
    else:
        # Try parsing as ISO date
        try:
            return datetime.fromisoformat(since).replace(tzinfo=UTC)
        except ValueError:
            raise click.BadParameter(
                f"Invalid since format: {since}. Use '24h', '7d', or '2025-01-17'"
            )


def _print_event(event: dict, index: int | None = None) -> None:
    """Print event in human-readable format."""
    prefix = f"{index}. " if index else ""
    timestamp = event["timestamp"]
    event_type = event["event_type"]
    status = event["status"]

    # Status emoji
    status_emoji = {"success": "✓", "failure": "✗", "pending": "⋯"}.get(status, "?")

    click.echo(f"{prefix}[{timestamp}] {status_emoji} {event_type} ({status})")

    # Print metadata if present
    metadata = event.get("metadata", {})
    if metadata:
        for key, value in metadata.items():
            click.echo(f"  {key}: {value}")

    click.echo()
