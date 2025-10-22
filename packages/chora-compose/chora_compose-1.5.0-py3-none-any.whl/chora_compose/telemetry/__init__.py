"""Telemetry and event emission for chora-compose.

This package provides event emission infrastructure for gateway integration,
enabling request/response correlation through trace context propagation.
"""

from chora_compose.telemetry.event_emitter import EventEmitter, emit_event
from chora_compose.telemetry.event_schemas import (
    ArtifactAssembledEvent,
    ContentGeneratedEvent,
    TelemetryEvent,
    ValidationCompletedEvent,
)

__all__ = [
    "EventEmitter",
    "emit_event",
    "TelemetryEvent",
    "ContentGeneratedEvent",
    "ArtifactAssembledEvent",
    "ValidationCompletedEvent",
]
