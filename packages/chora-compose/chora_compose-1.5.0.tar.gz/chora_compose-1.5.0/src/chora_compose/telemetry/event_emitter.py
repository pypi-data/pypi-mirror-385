"""Event emission infrastructure for gateway integration.

This module provides:
- EventEmitter class for writing events to JSON Lines files
- Trace context propagation from environment variables
- Thread-safe file writing for concurrent event emission
- Helper function for emitting events from generators
"""

import json
import os
import threading
from pathlib import Path
from typing import Any

from chora_compose.telemetry.event_schemas import TelemetryEvent


class EventEmitter:
    """Thread-safe event emitter that writes to JSON Lines files.

    Events are written to var/telemetry/events.jsonl with one event per line.
    The emitter handles:
    - Automatic directory creation
    - Thread-safe file appending
    - Trace context propagation from CHORA_TRACE_ID env var
    - Event validation before emission

    Examples:
        ```python
        from chora_compose.telemetry import EventEmitter, ContentGeneratedEvent

        emitter = EventEmitter()

        event = ContentGeneratedEvent(
            content_config_id="readme-intro",
            generator_type="jinja2",
            status="success",
            duration_ms=234
        )

        emitter.emit(event)
        ```
    """

    def __init__(self, events_file: str | Path = "var/telemetry/events.jsonl") -> None:
        """Initialize the event emitter.

        Args:
            events_file: Path to the events file (default: var/telemetry/events.jsonl)
        """
        self.events_file = Path(events_file)
        self._lock = threading.Lock()
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        """Create the events directory if it doesn't exist."""
        self.events_file.parent.mkdir(parents=True, exist_ok=True)

    def _get_trace_id(self) -> str | None:
        """Get trace ID from environment variable.

        Gateways set CHORA_TRACE_ID to enable request/response correlation.

        Returns:
            Trace ID if set, None otherwise
        """
        return os.environ.get("CHORA_TRACE_ID")

    def emit(self, event: TelemetryEvent) -> None:
        """Emit an event to the events file.

        This method is thread-safe and can be called concurrently from
        multiple generators.

        Args:
            event: Event to emit (must be a TelemetryEvent subclass)
        """
        # Set trace_id from environment if not already set
        if event.trace_id is None:
            event.trace_id = self._get_trace_id()

        # Serialize event to JSON
        event_json = event.model_dump_json()

        # Write to file with lock for thread safety
        with self._lock:
            with open(self.events_file, "a", encoding="utf-8") as f:
                f.write(event_json + "\n")

    def read_events(self, trace_id: str | None = None) -> list[dict[str, Any]]:
        """Read events from the events file.

        This is primarily for testing. Production gateways should use
        streaming parsers to avoid loading the entire file into memory.

        Args:
            trace_id: Optional trace ID to filter events

        Returns:
            List of event dictionaries
        """
        if not self.events_file.exists():
            return []

        events = []
        with open(self.events_file, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                event = json.loads(line)
                if trace_id is None or event.get("trace_id") == trace_id:
                    events.append(event)

        return events

    def clear(self) -> None:
        """Clear all events from the events file.

        This is primarily for testing. Production systems should not
        clear events - use log rotation or archival instead.
        """
        if self.events_file.exists():
            self.events_file.unlink()


# Global emitter instance
_global_emitter: EventEmitter | None = None


def get_emitter() -> EventEmitter:
    """Get the global EventEmitter instance.

    Returns:
        Global EventEmitter instance
    """
    global _global_emitter
    if _global_emitter is None:
        _global_emitter = EventEmitter()
    return _global_emitter


def emit_event(event: TelemetryEvent) -> None:
    """Emit an event using the global emitter.

    This is a convenience function for generators to emit events
    without managing their own EventEmitter instance.

    Args:
        event: Event to emit

    Examples:
        ```python
        from chora_compose.telemetry import emit_event, ContentGeneratedEvent

        emit_event(ContentGeneratedEvent(
            content_config_id="readme-intro",
            generator_type="jinja2",
            status="success",
            duration_ms=234
        ))
        ```
    """
    get_emitter().emit(event)
