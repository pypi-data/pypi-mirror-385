"""Upstream dependencies model for generators.

This module defines the UpstreamDependencies model that captures what external
services and credentials a generator requires. This enables gateways to:
- Pre-validate credentials before calling tools
- Show users what's needed to use a generator
- Make intelligent routing decisions
- Provide better error messages
"""

from typing import Literal

from pydantic import BaseModel, Field


class UpstreamDependencies(BaseModel):
    """External dependencies required by a generator.

    This model captures what external services, credentials, and infrastructure
    a generator needs to function. It enables intelligent pre-flight checks and
    better user experience when generators have external dependencies.

    Examples:
        No dependencies (local generators):
        ```python
        UpstreamDependencies(
            services=[],
            credentials_required=[],
            concurrency_safe=True
        )
        ```

        Anthropic API dependency:
        ```python
        UpstreamDependencies(
            services=["anthropic"],
            credentials_required=["ANTHROPIC_API_KEY"],
            expected_latency_ms={"p50": 1500, "p95": 5000},
            stability="stable",
            concurrency_safe=True
        )
        ```

        Multiple services with optional fallback:
        ```python
        UpstreamDependencies(
            services=["openai"],
            credentials_required=["OPENAI_API_KEY"],
            optional_services=["anthropic"],  # Fallback if OpenAI unavailable
            expected_latency_ms={"p50": 2000, "p95": 8000},
            stability="stable",
            concurrency_safe=True
        )
        ```
    """

    services: list[str] = Field(
        default_factory=list,
        description=(
            "External services required (e.g., 'anthropic', 'openai', 'github')"
        ),
        examples=[["anthropic"], ["openai", "github"], []],
    )

    credentials_required: list[str] = Field(
        default_factory=list,
        description=(
            "Environment variables that must be set (e.g., 'ANTHROPIC_API_KEY')"
        ),
        examples=[
            ["ANTHROPIC_API_KEY"],
            ["OPENAI_API_KEY", "GITHUB_TOKEN"],
            [],
        ],
    )

    optional_services: list[str] = Field(
        default_factory=list,
        description="Optional services that enhance functionality but aren't required",
        examples=[["anthropic"], [], ["redis"]],
    )

    expected_latency_ms: dict[str, int] = Field(
        default_factory=dict,
        description="Expected latency percentiles in milliseconds",
        examples=[{"p50": 1000, "p95": 3000}, {"p50": 500, "p95": 2000}, {}],
    )

    stability: Literal["stable", "beta", "experimental"] = Field(
        default="stable",
        description="Stability level of the external service integration",
    )

    concurrency_safe: bool = Field(
        default=True,
        description="Whether this generator can be safely called concurrently",
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "examples": [
                {
                    "services": [],
                    "credentials_required": [],
                    "optional_services": [],
                    "expected_latency_ms": {},
                    "stability": "stable",
                    "concurrency_safe": True,
                },
                {
                    "services": ["anthropic"],
                    "credentials_required": ["ANTHROPIC_API_KEY"],
                    "optional_services": [],
                    "expected_latency_ms": {"p50": 1500, "p95": 5000},
                    "stability": "stable",
                    "concurrency_safe": True,
                },
            ]
        }
