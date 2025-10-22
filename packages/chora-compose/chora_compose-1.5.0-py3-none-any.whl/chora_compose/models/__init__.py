"""Chora Compose data models package.

This package contains Pydantic models for various aspects of the system,
including upstream dependencies, telemetry events, and other structured data.
"""

from chora_compose.models.upstream_dependencies import UpstreamDependencies

__all__ = ["UpstreamDependencies"]
