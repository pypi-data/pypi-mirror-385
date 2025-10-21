"""Event schema definitions for telemetry.

All events follow a common structure with event-specific metadata fields.
Events are serialized to JSON Lines format for efficient streaming and parsing.
"""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class TelemetryEvent(BaseModel):
    """Base telemetry event schema.

    All events include:
    - ISO 8601 timestamp
    - Trace ID for correlation across systems
    - Event type identifier
    - Status (success/error)
    - Event-specific metadata

    Examples:
        ```python
        event = ContentGeneratedEvent(
            trace_id="abc123",
            status="success",
            content_config_id="readme-intro",
            generator_type="jinja2",
            duration_ms=234
        )
        ```
    """

    timestamp: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="ISO 8601 timestamp of event occurrence",
    )
    trace_id: str | None = Field(
        default=None,
        description=(
            "Trace ID for correlating events across systems "
            "(set by gateway via CHORA_TRACE_ID env var)"
        ),
    )
    event_type: str = Field(description="Event type identifier")
    status: Literal["success", "error"] = Field(description="Event outcome status")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "examples": [
                {
                    "timestamp": "2025-10-17T12:00:00.123Z",
                    "trace_id": "abc123",
                    "event_type": "chora.content_generated",
                    "status": "success",
                }
            ]
        }


class ContentGeneratedEvent(TelemetryEvent):
    """Event emitted after content generation completes.

    This event signals that a content config has been processed and
    ephemeral content has been generated and stored.
    """

    event_type: Literal["chora.content_generated"] = "chora.content_generated"
    content_config_id: str = Field(
        description="ID of the content config that was generated"
    )
    generator_type: str = Field(
        description=(
            "Type of generator used (jinja2, demonstration, code_generation, etc.)"
        )
    )
    duration_ms: int = Field(description="Generation duration in milliseconds", ge=0)
    error_message: str | None = Field(
        default=None, description="Error message if status is error"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "examples": [
                {
                    "timestamp": "2025-10-17T12:00:00.123Z",
                    "trace_id": "abc123",
                    "event_type": "chora.content_generated",
                    "status": "success",
                    "content_config_id": "weekly-report-intro",
                    "generator_type": "jinja2",
                    "duration_ms": 234,
                }
            ]
        }


class ArtifactAssembledEvent(TelemetryEvent):
    """Event emitted after artifact assembly completes.

    This event signals that an artifact config has been processed,
    all content pieces have been generated, and the final artifact
    has been assembled and written to the filesystem.
    """

    event_type: Literal["chora.artifact_assembled"] = "chora.artifact_assembled"
    artifact_config_id: str = Field(
        description="ID of the artifact config that was assembled"
    )
    section_count: int = Field(description="Number of content sections assembled", ge=0)
    duration_ms: int = Field(description="Assembly duration in milliseconds", ge=0)
    output_path: str | None = Field(
        default=None, description="Path where artifact was written"
    )
    error_message: str | None = Field(
        default=None, description="Error message if status is error"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "examples": [
                {
                    "timestamp": "2025-10-17T12:00:05.456Z",
                    "trace_id": "abc123",
                    "event_type": "chora.artifact_assembled",
                    "status": "success",
                    "artifact_config_id": "weekly-report",
                    "section_count": 4,
                    "duration_ms": 1234,
                    "output_path": "output/report.md",
                }
            ]
        }


class ValidationCompletedEvent(TelemetryEvent):
    """Event emitted after content validation completes.

    This event signals that validation rules have been run against
    generated content and the results are available.

    Note: This is a stub implementation for v1.1.1. Full validation
    event emission will be implemented in a future version.
    """

    event_type: Literal["chora.validation_completed"] = "chora.validation_completed"
    content_config_id: str = Field(
        description="ID of the content config that was validated"
    )
    validation_passed: bool = Field(description="Whether all validation rules passed")
    rule_count: int = Field(description="Number of validation rules executed", ge=0)
    duration_ms: int = Field(description="Validation duration in milliseconds", ge=0)
    error_message: str | None = Field(
        default=None, description="Error message if status is error"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "examples": [
                {
                    "timestamp": "2025-10-17T12:00:10.789Z",
                    "trace_id": "abc123",
                    "event_type": "chora.validation_completed",
                    "status": "success",
                    "content_config_id": "weekly-report-intro",
                    "validation_passed": True,
                    "rule_count": 3,
                    "duration_ms": 456,
                }
            ]
        }
