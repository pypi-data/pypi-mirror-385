"""Event monitoring for chora-compose telemetry.

This module provides EventWatcher to monitor chora-compose events and forward
them to both gateway telemetry (.chora/memory/events/) and optionally to n8n
webhooks for event-driven workflows.
"""
# mypy: disable-error-code="import-not-found,type-arg"

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import aiohttp

from mcp_n8n.memory.event_log import EventLog

logger = logging.getLogger(__name__)


class EventWatcher:
    """Monitor chora-compose events and forward to telemetry + n8n.

    Implements dual-consumption pattern (Option 4 from intent.md):
    - Stores all events in gateway telemetry (.chora/memory/events/)
    - Forwards events to n8n webhook (optional, fire-and-forget)
    """

    def __init__(
        self,
        event_log: EventLog,
        events_file: str | Path = "var/telemetry/events.jsonl",
        n8n_webhook_url: str | None = None,
    ):
        """Initialize event watcher.

        Args:
            event_log: Existing EventLog instance for storing events
            events_file: Path to chora-compose events file
            n8n_webhook_url: Optional n8n webhook URL for forwarding
        """
        self.event_log = event_log
        self.events_file = Path(events_file)
        self.n8n_webhook_url = n8n_webhook_url
        self._running = False
        self._watch_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start watching events continuously.

        Tails the events file and processes new events as they appear.
        """
        if self._running:
            logger.warning("EventWatcher already running")
            return

        self._running = True
        logger.info(f"Starting EventWatcher on {self.events_file}")

        # Ensure events file exists
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.events_file.exists():
            self.events_file.touch()

        # Start watching in background
        self._watch_task = asyncio.create_task(self._watch_events())

    async def stop(self) -> None:
        """Stop watching events gracefully."""
        if not self._running:
            return

        logger.info("Stopping EventWatcher")
        self._running = False

        # Cancel watch task
        if self._watch_task:
            self._watch_task.cancel()
            try:
                await self._watch_task
            except asyncio.CancelledError:
                pass

    async def _watch_events(self) -> None:
        """Watch events file for new events (tail -f behavior)."""
        # Get current file size to skip existing events
        current_size = (
            self.events_file.stat().st_size if self.events_file.exists() else 0
        )

        while self._running:
            try:
                # Check if file grew
                if not self.events_file.exists():
                    await asyncio.sleep(0.1)
                    continue

                file_size = self.events_file.stat().st_size

                if file_size > current_size:
                    # Read new content
                    with self.events_file.open("r") as f:
                        f.seek(current_size)
                        new_content = f.read()
                        current_size = file_size

                    # Process each new line
                    for line in new_content.strip().split("\n"):
                        if not line:
                            continue

                        try:
                            event = json.loads(line)
                            await self._process_event(event)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Malformed JSON in events file: {e}")
                            continue

                # Sleep to avoid busy waiting
                await asyncio.sleep(0.05)  # 50ms poll interval

            except asyncio.CancelledError:
                logger.debug("Event watching cancelled")
                break
            except Exception as e:
                logger.error(f"Error watching events: {e}")
                await asyncio.sleep(1)  # Back off on error

    async def _process_event(self, event: dict[str, Any]) -> None:
        """Process a single event: store + forward to webhook.

        Args:
            event: Event dictionary from chora-compose
        """
        try:
            # Store in gateway telemetry (always)
            # Use the emit_event function from trace module
            from mcp_n8n.memory.trace import emit_event

            # Re-emit the event to gateway telemetry
            # The event already has all required fields from chora-compose
            emit_event(
                event_type=event.get("event_type", "unknown"),
                trace_id=event.get("trace_id"),
                status=event.get("status", "success"),
                source="chora-compose",
                base_dir=self.event_log.base_dir,  # Use EventLog's base_dir
                **{
                    k: v
                    for k, v in event.items()
                    if k
                    not in [
                        "event_type",
                        "trace_id",
                        "status",
                        "schema_version",
                        "timestamp",
                        "source",
                    ]
                },
            )

            # Forward to webhook (optional, fire-and-forget)
            if self.n8n_webhook_url:
                asyncio.create_task(self._forward_to_webhook(event))

        except Exception as e:
            logger.error(f"Error processing event: {e}")

    async def _forward_to_webhook(self, event: dict[str, Any]) -> None:
        """Forward event to n8n webhook (fire-and-forget).

        Args:
            event: Event to forward
        """
        if not self.n8n_webhook_url:
            return

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.n8n_webhook_url,
                    json=event,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    if response.status != 200:
                        logger.warning(
                            f"Webhook returned status {response.status}: "
                            f"{await response.text()}"
                        )
                    else:
                        logger.debug(
                            f"Event forwarded to webhook: {event.get('trace_id')}"
                        )

        except TimeoutError:
            logger.warning(f"Webhook timeout for event {event.get('trace_id')}")
        except Exception as e:
            logger.warning(f"Webhook delivery failed: {e}")
