# ruff: noqa: E501
# Day 2 complete implementation: Comprehensive Pydantic models for MCP tool I/O

"""Pydantic models for MCP tool I/O.

This module defines all input and output types for MCP tools using
Pydantic models. These models provide:
- Runtime type validation
- JSON serialization/deserialization
- Self-documenting schemas
- Schema generation for OpenAPI/JSON Schema
- Field-level validation and constraints

All models match the specifications in docs/mcp/tool-reference.md exactly.
"""

import json
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

# =============================================================================
# generate_content Types
# =============================================================================


class GenerateContentInput(BaseModel):
    """Input parameters for the generate_content MCP tool.

    Generates content from a content configuration using the specified generator.
    Content is stored in ephemeral storage and returned for immediate use.

    Example:
        ```python
        # Object form (preferred)
        input = GenerateContentInput(
            content_config_id="welcome-message",
            context={"user": {"name": "Alice"}},
            force=False
        )

        # String form (auto-parsed for Claude Desktop chat compatibility)
        input = GenerateContentInput(
            content_config_id="welcome-message",
            context='{"user": {"name": "Alice"}}',
            force=False
        )
        ```

    Attributes:
        content_config_id: ID of the content configuration file (without .json extension).
            Must be a valid filename without path separators or parent directory references.
        context: Context variables for template substitution. Accepts either a JSON object
            or a string containing JSON (which will be auto-parsed). Merged with config
            context, with tool-provided values taking precedence.
        force: If False (default), skip generation if content already exists. If True,
            always regenerate and replace existing content.
    """

    content_config_id: str = Field(
        ...,
        description="Content configuration ID (matches filename in configs/content/)",
        min_length=1,
        max_length=255,
        examples=["welcome-message", "user-profile", "api-docs"],
    )

    context: dict[str, Any] | str = Field(
        default_factory=lambda: {},
        description=(
            "Context variables for template substitution (merged with config context). "
            "Accepts JSON object or string containing JSON (auto-parsed)."
        ),
        examples=[
            {"user": {"name": "Alice", "role": "admin"}},
            {"timestamp": "2025-10-14T12:00:00Z", "version": "1.0.0"},
            '{"user": {"name": "Alice"}}',  # String form - auto-parsed
        ],
    )

    force: bool = Field(
        default=False,
        description="Force regeneration even if content already exists in ephemeral storage",
    )

    @field_validator("context", mode="before")
    @classmethod
    def normalize_context(cls, v: Any) -> dict[str, Any]:
        """Normalize context to dict, parsing JSON strings if needed.

        This validator handles the Claude Desktop quirk where JSON pasted in chat
        is serialized as a string. It auto-detects and parses stringified JSON,
        while passing through dict objects unchanged.

        Args:
            v: Context value (dict, str, or None)

        Returns:
            Normalized dict context

        Raises:
            ValueError: If string is provided but is not valid JSON
        """
        if v is None or v == "":
            return {}
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if not isinstance(parsed, dict):
                    raise ValueError(
                        f"context string must parse to JSON object, got {type(parsed).__name__}"
                    )
                return parsed
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"context string is not valid JSON: {e}. "
                    f"Received: {v[:100]}{'...' if len(v) > 100 else ''}"
                ) from e
        raise ValueError(f"context must be dict or JSON string, got {type(v).__name__}")


class GenerateContentResult(BaseModel):
    """Result from the generate_content MCP tool.

    Contains the generated content, metadata about the generation process,
    and performance metrics.

    Example:
        ```python
        result = GenerateContentResult(
            success=True,
            content_id="welcome-message",
            content="# Welcome Alice!\\n...",
            generator="template_fill",
            status="generated",
            duration_ms=142,
            metadata={
                "context_variables": ["user"],
                "ephemeral_stored": True
            }
        )
        ```

    Attributes:
        success: Always True for successful operations.
        content_id: ID of the generated content (matches input content_config_id).
        content: The generated content as a string.
        generator: Name of the generator used (e.g., "jinja2", "template_fill").
        status: Generation status - "generated" (newly created), "skipped" (already exists),
            or "regenerated" (forced regeneration).
        duration_ms: Total execution time in milliseconds.
        metadata: Additional information about generation (context variables,
            storage location, sizes, cache hits, etc.).
    """

    success: bool = Field(
        ...,
        description="Operation success indicator (always True for successful operations)",
    )

    content_id: str = Field(
        ...,
        description="ID of the generated content (matches content_config_id)",
        examples=["welcome-message", "user-profile"],
    )

    content: str = Field(
        ...,
        description="The generated content text",
        examples=["# Welcome Alice!\n\nGenerated at: 2025-10-14"],
    )

    generator: str = Field(
        ...,
        description="Name of generator used for content generation",
        examples=[
            "jinja2",
            "template_fill",
            "code_generation",
            "bdd_scenario_assembly",
        ],
    )

    status: Literal["generated", "skipped", "regenerated"] = Field(
        ...,
        description="Generation status: generated (new), skipped (exists), regenerated (forced)",
    )

    duration_ms: int = Field(
        ...,
        description="Execution time in milliseconds",
        ge=0,
        examples=[142, 1250, 5600],
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional generation metadata (context vars, storage info, performance)",
        examples=[
            {
                "context_variables": ["user", "timestamp"],
                "ephemeral_stored": True,
                "ephemeral_path": "ephemeral://content/welcome-message",
                "template_size": 256,
                "output_size": 512,
                "cache_hit": False,
            }
        ],
    )


# =============================================================================
# assemble_artifact Types
# =============================================================================


class AssembleArtifactInput(BaseModel):
    """Input parameters for the assemble_artifact MCP tool.

    Assembles a final artifact by combining multiple content pieces according
    to an artifact configuration's composition strategy.

    Example:
        ```python
        input = AssembleArtifactInput(
            artifact_config_id="user-documentation",
            output_path="/tmp/docs.md",  # Optional override
            force=False
        )
        ```

    Attributes:
        artifact_config_id: ID of the artifact configuration file (without .json extension).
            Must be a valid filename without path separators.
        output_path: Override the output path specified in artifact config. Can be
            absolute or relative path. Directory must exist or be creatable.
        force: If False (default), skip assembly if output file exists. If True,
            always reassemble and overwrite existing file.
    """

    artifact_config_id: str = Field(
        ...,
        description="Artifact configuration ID (matches filename in configs/artifact/)",
        min_length=1,
        max_length=255,
        examples=["user-documentation", "api-docs", "release-notes"],
    )

    output_path: str | None = Field(
        default=None,
        description="Override output path from config (absolute or relative path)",
        examples=[
            "/Users/user/project/output/documentation.md",
            "output/docs.md",
            "/tmp/api-docs.md",
        ],
    )

    force: bool = Field(
        default=False,
        description="Force reassembly even if artifact already exists at output path",
    )


class ComponentInfo(BaseModel):
    """Information about a single content component in an assembled artifact.

    Attributes:
        id: Content ID of the component.
        size: Size of the component in bytes.
    """

    id: str = Field(..., description="Content ID of the component")
    size: int = Field(..., description="Size of component in bytes", ge=0)


class AssembleArtifactResult(BaseModel):
    """Result from the assemble_artifact MCP tool.

    Contains information about the assembled artifact, including output location,
    composition details, and performance metrics.

    Example:
        ```python
        result = AssembleArtifactResult(
            success=True,
            artifact_id="user-documentation",
            output_path="/Users/user/project/output/docs.md",
            content_count=5,
            size_bytes=12480,
            status="assembled",
            duration_ms=890,
            metadata={
                "composition_strategy": "sequential",
                "components": [
                    {"id": "intro", "size": 1024},
                    {"id": "usage", "size": 4096}
                ]
            }
        )
        ```

    Attributes:
        success: Always True for successful operations.
        artifact_id: ID of the assembled artifact (matches input artifact_config_id).
        output_path: Absolute path where artifact was written to filesystem.
        content_count: Number of content pieces assembled into artifact.
        size_bytes: Total size of assembled artifact in bytes.
        status: Assembly status - "assembled" (newly created), "skipped" (already exists),
            or "reassembled" (forced reassembly).
        duration_ms: Total execution time in milliseconds.
        metadata: Additional information about assembly (composition strategy, components,
            timings, separators, etc.).
    """

    success: bool = Field(
        ...,
        description="Operation success indicator (always True for successful operations)",
    )

    artifact_id: str = Field(
        ...,
        description="ID of the assembled artifact (matches artifact_config_id)",
        examples=["user-documentation", "api-docs"],
    )

    output_path: str = Field(
        ...,
        description="Absolute path where artifact was written",
        examples=["/Users/user/project/output/documentation.md", "/tmp/docs.md"],
    )

    content_count: int = Field(
        ...,
        description="Number of content pieces assembled into artifact",
        ge=0,
        examples=[5, 12, 3],
    )

    size_bytes: int = Field(
        ...,
        description="Total size of assembled artifact in bytes",
        ge=0,
        examples=[12480, 8192, 1024],
    )

    status: Literal["assembled", "skipped", "reassembled"] = Field(
        ...,
        description="Assembly status: assembled (new), skipped (exists), reassembled (forced)",
    )

    duration_ms: int = Field(
        ...,
        description="Total execution time in milliseconds",
        ge=0,
        examples=[890, 1234, 456],
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional assembly metadata (strategy, components, timings, separators)",
        examples=[
            {
                "composition_strategy": "sequential",
                "components": [
                    {"id": "intro", "size": 1024},
                    {"id": "usage", "size": 4096},
                ],
                "separator": "\n\n---\n\n",
                "total_generation_time_ms": 456,
                "total_assembly_time_ms": 434,
            }
        ],
    )


# =============================================================================
# list_generators Types
# =============================================================================


class ListGeneratorsInput(BaseModel):
    """Input parameters for the list_generators MCP tool.

    Queries the generator registry to list available built-in and plugin generators.

    Example:
        ```python
        # List all generators
        input = ListGeneratorsInput()

        # List only built-in generators
        input = ListGeneratorsInput(generator_type="builtin")

        # List generators but exclude plugins
        input = ListGeneratorsInput(include_plugins=False)
        ```

    Attributes:
        generator_type: Filter by type - "builtin" for built-in generators,
            "plugin" for plugin generators, or None for all generators.
        include_plugins: Whether to include plugin generators in results.
            Has no effect if generator_type="builtin".
    """

    generator_type: Literal["builtin", "plugin"] | None = Field(
        default=None,
        description='Filter by type: "builtin", "plugin", or null for all',
        examples=["builtin", "plugin", None],
    )

    include_plugins: bool = Field(
        default=True,
        description="Whether to include plugin generators in results",
    )


class GeneratorInfo(BaseModel):
    """Metadata about a single generator.

    Contains information about generator name, type, version, description,
    and capabilities.

    Example:
        ```python
        info = GeneratorInfo(
            name="jinja2",
            type="builtin",
            version="0.2.0",
            description="Jinja2 template engine with full template language support",
            capabilities=["templates", "conditionals", "loops", "filters"]
        )
        ```

    Attributes:
        name: Generator identifier used in content configs.
        type: Generator type - "builtin" (shipped with chora-compose) or
            "plugin" (discovered from plugin directories).
        version: Generator version string (semantic versioning).
        description: Human-readable description of generator purpose.
        capabilities: List of capability tags (e.g., "templates", "ai", "loops").
    """

    name: str = Field(
        ...,
        description="Generator identifier (used in content configs)",
        examples=["jinja2", "template_fill", "code_generation"],
    )

    type: Literal["builtin", "plugin"] = Field(
        ...,
        description='Generator type: "builtin" (shipped) or "plugin" (discovered)',
    )

    version: str = Field(
        ...,
        description="Generator version (semantic versioning)",
        examples=["0.2.0", "0.8.0", "1.0.0"],
    )

    description: str = Field(
        ...,
        description="Human-readable generator description",
        examples=[
            "Jinja2 template engine with full template language support",
            "Simple variable substitution with {{variable}} syntax",
            "AI-powered code generation using Claude API",
        ],
    )

    capabilities: list[str] = Field(
        default_factory=list,
        description="List of generator capabilities/features",
        examples=[
            ["templates", "conditionals", "loops", "filters"],
            ["templates", "variables"],
            ["ai", "code", "contextual"],
        ],
    )


class ListGeneratorsResult(BaseModel):
    """Result from the list_generators MCP tool.

    Contains list of generators with their metadata, total count, and
    filter status.

    Example:
        ```python
        result = ListGeneratorsResult(
            success=True,
            generators=[
                GeneratorInfo(name="jinja2", type="builtin", ...),
                GeneratorInfo(name="template_fill", type="builtin", ...),
            ],
            total_count=2,
            filtered=True
        )
        ```

    Attributes:
        success: Always True for successful operations.
        generators: List of generator metadata objects.
        total_count: Total number of generators in results.
        filtered: Whether results were filtered by generator_type parameter.
    """

    success: bool = Field(
        ...,
        description="Operation success indicator (always True for successful operations)",
    )

    generators: list[GeneratorInfo] = Field(
        ...,
        description="List of generator metadata objects",
    )

    total_count: int = Field(
        ...,
        description="Total number of generators in results",
        ge=0,
        examples=[4, 2, 10],
    )

    filtered: bool = Field(
        ...,
        description="Whether results were filtered (generator_type specified)",
    )


# =============================================================================
# validate_content Types
# =============================================================================


class ValidationRuleConfig(BaseModel):
    """Configuration for a single validation rule.

    Example:
        ```python
        rule = ValidationRuleConfig(
            type="length",
            severity="warning",
            config={"min": 100, "max": 10000}
        )
        ```

    Attributes:
        type: Rule type (e.g., "schema", "length", "required_fields").
        severity: Issue severity for rule violations - "error", "warning", or "info".
        config: Rule-specific configuration parameters.
    """

    type: str = Field(
        ...,
        description="Rule type (schema, length, required_fields, format, links, spelling)",
        examples=["schema", "length", "required_fields", "format"],
    )

    severity: Literal["error", "warning", "info"] = Field(
        ...,
        description='Issue severity: "error" (invalid), "warning" (suboptimal), "info" (informational)',
    )

    config: dict[str, Any] = Field(
        default_factory=dict,
        description="Rule-specific configuration parameters",
        examples=[
            {"min": 100, "max": 10000},
            {"fields": ["title", "content"]},
            {"format": "markdown"},
        ],
    )


class ValidationInput(BaseModel):
    """Input parameters for the validate_content MCP tool.

    Validates content configurations or generated content against rules and schemas.

    Example:
        ```python
        # Validate with default rules
        input = ValidationInput(content_or_config_id="user-profile")

        # Validate with custom rules
        input = ValidationInput(
            content_or_config_id="api-docs",
            validation_rules=[
                {
                    "type": "length",
                    "severity": "error",
                    "config": {"min": 1000}
                }
            ]
        )
        ```

    Attributes:
        content_or_config_id: ID of content or configuration to validate.
            System automatically determines whether it's a config or generated content.
        validation_rules: Custom validation rules to apply. If None, uses default rules.
            Each rule specifies type, severity, and type-specific config.
    """

    content_or_config_id: str = Field(
        ...,
        description="Content or configuration ID to validate",
        min_length=1,
        max_length=255,
        examples=["user-profile", "api-docs", "welcome-message"],
    )

    validation_rules: list[dict[str, Any]] | None = Field(
        default=None,
        description="Custom validation rules (null = use defaults)",
        examples=[
            [
                {"type": "length", "severity": "warning", "config": {"min": 100}},
                {
                    "type": "required_fields",
                    "severity": "error",
                    "config": {"fields": ["title", "content"]},
                },
            ]
        ],
    )


class ValidationIssue(BaseModel):
    """A single validation issue found during content/config validation.

    Example:
        ```python
        issue = ValidationIssue(
            severity="error",
            code="missing_required_field",
            message="Required field 'metadata.description' is missing",
            location="metadata.description",
            details={
                "field": "metadata.description",
                "required_by": "schema"
            }
        )
        ```

    Attributes:
        severity: Issue severity - "error" (critical, content invalid),
            "warning" (suboptimal, content usable), or "info" (informational).
        code: Machine-readable issue code for programmatic handling.
        message: Human-readable issue description.
        location: Location of issue (JSON path, line number, or section).
        details: Additional context about the issue.
    """

    severity: Literal["error", "warning", "info"] = Field(
        ...,
        description='Issue severity: "error" (invalid), "warning" (suboptimal), "info" (informational)',
    )

    code: str = Field(
        ...,
        description="Machine-readable issue code",
        examples=[
            "missing_required_field",
            "content_too_short",
            "invalid_generator",
            "schema_validation_failed",
        ],
    )

    message: str = Field(
        ...,
        description="Human-readable issue description",
        examples=[
            "Required field 'metadata.description' is missing",
            "Content length (45 chars) below recommended minimum (100 chars)",
            "Generator 'nonexistent' not found in registry",
        ],
    )

    location: str | None = Field(
        default=None,
        description="Location of issue (JSON path, line number, or section)",
        examples=["metadata.description", "generation.patterns[0].type", "content"],
    )

    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context about the issue",
        examples=[
            {"field": "metadata.description", "required_by": "schema"},
            {"actual_length": 45, "min_recommended": 100},
            {"specified_generator": "nonexistent", "available_generators": ["jinja2"]},
        ],
    )


class ValidationResult(BaseModel):
    """Result from the validate_content MCP tool.

    Contains validation status, list of issues found, and counts by severity.

    Example:
        ```python
        result = ValidationResult(
            success=True,
            valid=False,
            issues=[
                ValidationIssue(severity="error", code="missing_required_field", ...),
                ValidationIssue(severity="warning", code="content_too_short", ...),
            ],
            error_count=1,
            warning_count=1,
            info_count=0
        )
        ```

    Attributes:
        success: Always True for successful validation operations.
        valid: Whether content passed validation (no error-severity issues).
        issues: List of validation issues found (errors, warnings, info).
        error_count: Count of error-severity issues (validation failed if > 0).
        warning_count: Count of warning-severity issues.
        info_count: Count of info-severity issues.
    """

    success: bool = Field(
        ...,
        description="Operation success indicator (always True for successful operations)",
    )

    valid: bool = Field(
        ...,
        description="Whether content passed validation (error_count == 0)",
    )

    issues: list[ValidationIssue] = Field(
        default_factory=list,
        description="List of validation issues found (errors, warnings, info)",
    )

    error_count: int = Field(
        ...,
        description="Count of error-severity issues",
        ge=0,
        examples=[0, 1, 5],
    )

    warning_count: int = Field(
        ...,
        description="Count of warning-severity issues",
        ge=0,
        examples=[0, 2, 10],
    )

    info_count: int = Field(
        ...,
        description="Count of info-severity issues",
        ge=0,
        examples=[0, 1, 3],
    )


# =============================================================================
# Error Response Types
# =============================================================================


class ErrorDetails(BaseModel):
    """Additional details about an error.

    Provides context, suggestions, and debugging information for errors.

    Example:
        ```python
        details = ErrorDetails(
            content_config_id="missing-config",
            searched_paths=["/configs/content/missing-config.json"],
            suggestion="Check configuration file exists"
        )
        ```

    Attributes:
        Additional fields provided as a flexible dictionary to accommodate
        different error types and contexts.
    """

    class Config:
        """Pydantic config to allow arbitrary fields."""

        extra = "allow"


class MCPError(BaseModel):
    """Error structure for MCP tool failures.

    All MCP tools return errors in this consistent format.
    Note: This is a data class (BaseModel), not an Exception. Use for
    serialization and error responses, not for raising.

    Example:
        ```python
        error = MCPError(
            code="config_not_found",
            message="Content config 'missing-config' not found",
            details={
                "content_config_id": "missing-config",
                "searched_paths": ["/configs/content/missing-config.json"]
            }
        )
        ```

    Attributes:
        code: Machine-readable error code for programmatic handling.
        message: Human-readable error description.
        details: Additional error context, suggestions, and debugging information.
    """

    code: str = Field(
        ...,
        description="Machine-readable error code",
        examples=[
            "config_not_found",
            "generation_failed",
            "invalid_context",
            "write_failed",
        ],
    )

    message: str = Field(
        ...,
        description="Human-readable error description",
        examples=[
            "Content config 'missing-config' not found",
            "Template generation failed: undefined variable 'username'",
            "Cannot write artifact: Permission denied",
        ],
    )

    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional error context, suggestions, and debugging information",
        examples=[
            {
                "content_config_id": "missing-config",
                "searched_paths": ["/configs/content/missing-config.json"],
            },
            {
                "generator": "jinja2",
                "missing_variable": "username",
                "available_variables": ["user", "timestamp"],
            },
        ],
    )


class ErrorResponse(BaseModel):
    """Top-level error response structure for MCP tool failures.

    All MCP tool errors are wrapped in this structure.

    Example:
        ```python
        response = ErrorResponse(
            success=False,
            error=MCPError(
                code="config_not_found",
                message="Content config 'missing-config' not found",
                details={"content_config_id": "missing-config"}
            )
        )
        ```

    Attributes:
        success: Always False for error responses.
        error: Structured error information (code, message, details).
    """

    success: Literal[False] = Field(
        ...,
        description="Operation success indicator (always False for errors)",
    )

    error: MCPError = Field(
        ...,
        description="Structured error information",
    )


# =============================================================================
# regenerate_content Types
# =============================================================================


class PreviousVersionInfo(BaseModel):
    """Previous version metadata for change tracking.

    Contains information about the previous version of content
    that was replaced by regeneration.

    Attributes:
        timestamp: ISO 8601 timestamp of previous generation
        content_hash: SHA-256 hash of previous content
    """

    timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp of previous generation",
        examples=["2025-10-14T10:30:00Z"],
    )
    content_hash: str = Field(
        ...,
        description="SHA-256 hash of previous content for verification",
        examples=["abc123def456"],
    )


class ContentChanges(BaseModel):
    """Detailed change information between versions.

    Provides diff statistics and a human-readable summary
    of changes between the previous and current version.

    Attributes:
        lines_added: Number of lines added
        lines_removed: Number of lines removed
        lines_changed: Number of lines modified
        summary: Human-readable description of changes
    """

    lines_added: int = Field(
        ...,
        ge=0,
        description="Number of lines added in regeneration",
    )
    lines_removed: int = Field(
        ...,
        ge=0,
        description="Number of lines removed in regeneration",
    )
    lines_changed: int = Field(
        ...,
        ge=0,
        description="Number of lines modified in regeneration",
    )
    summary: str = Field(
        ...,
        description="Human-readable summary of changes",
        examples=["Updated version from 1.0 to 2.0, added new features section"],
    )


class RegenerateContentInput(BaseModel):
    """Input parameters for the regenerate_content MCP tool.

    Forces regeneration of existing content with change tracking.
    Unlike generate_content, this always regenerates even if content exists,
    and optionally compares with the previous version to show what changed.

    Example:
        ```python
        # Basic regeneration with change tracking
        input = RegenerateContentInput(
            content_config_id="user-guide",
            reason="Updated template with new sections"
        )

        # With updated context and comparison
        input = RegenerateContentInput(
            content_config_id="api-docs",
            context={"version": "2.0.0", "new_features": [...]},
            reason="API v2.0 release",
            compare=True
        )

        # Skip comparison for faster regeneration
        input = RegenerateContentInput(
            content_config_id="release-notes",
            compare=False
        )
        ```

    Attributes:
        content_config_id: ID of the content configuration to regenerate
        context: Context variables for template substitution (dict or JSON string)
        reason: Human-readable reason for regeneration (for audit trail)
        compare: Whether to compare with previous version and calculate diff
    """

    content_config_id: str = Field(
        ...,
        description="Content configuration ID to regenerate",
        examples=["user-guide", "api-docs", "release-notes"],
    )
    context: dict[str, Any] | str = Field(
        default_factory=lambda: {},
        description="Context variables for template substitution (dict or JSON string)",
    )
    reason: str | None = Field(
        default=None,
        description="Human-readable reason for regeneration (for audit trail)",
        examples=["Updated template", "Context change", "Bug fix"],
    )
    compare: bool = Field(
        default=True,
        description="Whether to compare with previous version and calculate diff",
    )

    @field_validator("context", mode="before")
    @classmethod
    def normalize_context(cls, v: Any) -> dict[str, Any]:
        """Auto-parse JSON strings for Claude Desktop compatibility.

        Claude Desktop serializes dict parameters as JSON strings in chat mode.
        This validator automatically detects and parses JSON strings back to dicts.

        Args:
            v: Context value (dict or JSON string)

        Returns:
            Normalized dict
        """
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                return {}
        return dict(v) if v else {}


class RegenerateContentResult(BaseModel):
    """Result from the regenerate_content MCP tool.

    Contains the regenerated content along with change tracking information
    if comparison was enabled.

    Example:
        ```python
        {
            "success": True,
            "content_id": "user-guide",
            "status": "regenerated",
            "content": "# User Guide\\n\\nVersion 2.0\\n...",
            "previous_version": {
                "timestamp": "2025-10-13T15:00:00Z",
                "content_hash": "abc123def456"
            },
            "changes": {
                "lines_added": 12,
                "lines_removed": 3,
                "lines_changed": 5,
                "summary": "Updated version, added new features section"
            },
            "reason": "Updated template",
            "metadata": {
                "generator_type": "jinja2",
                "context_variables": ["version", "features"],
                "template_hash": "def456ghi789"
            },
            "duration_ms": 245
        }
        ```

    Attributes:
        success: Whether regeneration succeeded
        content_id: Content configuration ID that was regenerated
        status: Always "regenerated" for successful regeneration
        content: The newly regenerated content text
        previous_version: Previous version metadata (if exists)
        changes: Detailed change information (if compare=true and previous exists)
        reason: Echoed reason for regeneration
        metadata: Generation metadata
        duration_ms: Time taken to regenerate in milliseconds
    """

    success: bool = Field(...)
    content_id: str = Field(...)
    status: Literal["regenerated"] = Field(...)
    content: str = Field(..., description="Regenerated content text")
    previous_version: PreviousVersionInfo | None = Field(
        default=None,
        description="Previous version metadata (if exists)",
    )
    changes: ContentChanges | None = Field(
        default=None,
        description="Detailed changes (if compare=true and previous version exists)",
    )
    reason: str | None = Field(
        default=None,
        description="Echoed reason for regeneration",
    )
    metadata: dict[str, Any] = Field(
        ...,
        description=(
            "Generation metadata "
            "(generator_type, context_variables, template_hash, etc.)"
        ),
    )
    duration_ms: int = Field(..., ge=0)


# =============================================================================
# delete_content Types
# =============================================================================


class ContentReferences(BaseModel):
    """Artifact references to content."""

    artifact_ids: list[str] = Field(
        ..., description="Artifact IDs that reference this content"
    )
    count: int = Field(..., ge=0, description="Number of references")


class DeleteContentInput(BaseModel):
    """Input parameters for delete_content tool."""

    content_id: str = Field(
        ..., description="Content ID to delete from ephemeral storage"
    )
    preserve_metadata: bool = Field(
        default=False,
        description=("Keep metadata file but delete content (for audit trail)"),
    )
    force: bool = Field(
        default=False,
        description="Delete even if referenced by artifacts (use with caution)",
    )


class DeleteContentResult(BaseModel):
    """Result from delete_content tool."""

    success: bool = Field(...)
    content_id: str = Field(...)
    status: Literal["deleted"] = Field(...)
    versions_deleted: int = Field(
        ..., ge=0, description="Number of content versions deleted"
    )
    bytes_freed: int = Field(..., ge=0, description="Approximate bytes freed")
    metadata_preserved: bool = Field(...)
    warnings: list[str] | None = Field(
        default=None, description="Warnings about potential issues"
    )
    references: ContentReferences | None = Field(
        default=None,
        description=("Present if content was referenced by artifacts (force=true)"),
    )
    duration_ms: int = Field(..., ge=0)


# =============================================================================
# preview_generation Types
# =============================================================================


class PreviewMetadata(BaseModel):
    """Detailed generation metadata for preview."""

    generator_type: str = Field(..., description="Generator used")
    context_variables: list[str] = Field(..., description="Context variables provided")
    template_hash: str = Field(..., description="Template file hash")
    variable_usage: dict[str, int] = Field(
        ..., description="How many times each variable was used"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Warnings (unused vars, missing vars with defaults)",
    )


class PreviewGenerationInput(BaseModel):
    """Input parameters for preview_generation tool."""

    content_config_id: str = Field(
        ..., description="Content configuration ID to preview"
    )
    context: dict[str, Any] | str = Field(
        default_factory=lambda: {},
        description="Context variables for template substitution",
    )
    show_metadata: bool = Field(
        default=False,
        description="Include detailed generation metadata (for debugging)",
    )

    @field_validator("context", mode="before")
    @classmethod
    def normalize_context(cls, v: Any) -> dict[str, Any]:
        """Auto-parse JSON strings for Claude Desktop compatibility."""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, dict) else {}
            except json.JSONDecodeError:
                return {}
        return dict(v) if v else {}


class PreviewGenerationResult(BaseModel):
    """Result from preview_generation tool."""

    success: bool = Field(...)
    content_id: str = Field(...)
    status: Literal["preview"] = Field(
        ..., description="Always 'preview' to indicate dry-run"
    )
    content: str = Field(..., description="Generated content (NOT saved to storage)")
    metadata: PreviewMetadata | None = Field(
        default=None,
        description="Detailed metadata (if show_metadata=true)",
    )
    duration_ms: int = Field(..., ge=0)


# =============================================================================
# batch_generate Types
# =============================================================================


class ContentGenerationResult(BaseModel):
    """Individual result for one content generation in batch."""

    content_id: str = Field(..., description="Content ID that was generated")
    success: bool = Field(...)
    status: Literal["generated", "skipped", "failed"] = Field(...)
    content: str | None = Field(
        default=None, description="Generated content (if successful)"
    )
    error: dict[str, str] | None = Field(
        default=None, description="Error code and message (if failed)"
    )
    duration_ms: int = Field(..., ge=0)


class GenerationError(BaseModel):
    """Error information for failed generation."""

    content_id: str = Field(..., description="Content ID that failed")
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class BatchGenerateInput(BaseModel):
    """Input parameters for batch_generate tool."""

    content_ids: list[str] = Field(
        ...,
        min_length=1,
        description="Array of content configuration IDs to generate",
    )
    shared_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Context applied to all content generations",
    )
    individual_contexts: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Per-ID context overrides (merged with shared_context)",
    )
    force: bool = Field(
        default=False, description="Force regeneration of existing content"
    )
    continue_on_error: bool = Field(
        default=True, description="Continue if one generation fails"
    )
    max_parallel: int = Field(
        default=4,
        ge=1,
        le=10,
        description="Maximum concurrent generations",
    )


class BatchGenerateResult(BaseModel):
    """Result from batch_generate tool."""

    success: bool = Field(...)
    status: Literal["batch_complete", "batch_partial", "batch_failed"] = Field(...)
    total: int = Field(..., ge=0, description="Total content items")
    generated: int = Field(..., ge=0, description="Successfully generated")
    skipped: int = Field(..., ge=0, description="Skipped (already exists)")
    failed: int = Field(..., ge=0, description="Failed to generate")
    results: list[ContentGenerationResult] = Field(
        ...,
        description="Individual results (same order as input)",
    )
    errors: list[GenerationError] = Field(default_factory=list)
    duration_ms: int = Field(..., ge=0)
    parallel_efficiency: float = Field(
        ..., ge=0.0, description="Speedup factor vs sequential"
    )


# =============================================================================
# trace_dependencies Types
# =============================================================================


class DependencyMetadata(BaseModel):
    """Metadata for a content dependency."""

    generator_type: str = Field(..., description="Generator used")
    last_generated: str = Field(..., description="ISO 8601 timestamp")
    versions_available: int = Field(
        ..., ge=0, description="Number of versions in storage"
    )


class DependencyInfo(BaseModel):
    """Information about a single content dependency."""

    content_id: str = Field(..., description="Content configuration ID")
    path: str = Field(..., description="Path to content config file")
    required: bool = Field(..., description="Whether this content is required")
    order: int = Field(..., ge=1, description="Assembly order (1-based)")
    status: Literal["ready", "missing", "unknown"] = Field(...)
    retrieval_strategy: str = Field(
        ...,
        description=("How to retrieve content (latest, specific_version)"),
    )
    metadata: DependencyMetadata | None = Field(default=None)


class TraceDependenciesInput(BaseModel):
    """Input parameters for trace_dependencies tool."""

    artifact_config_id: str = Field(
        ..., description="Artifact configuration ID to analyze"
    )
    check_status: bool = Field(
        default=True,
        description=(
            "Check if each content piece exists (slower but more informative)"
        ),
    )
    show_metadata: bool = Field(
        default=False,
        description="Include detailed metadata for each content",
    )


class TraceDependenciesResult(BaseModel):
    """Result from trace_dependencies tool."""

    success: bool = Field(...)
    artifact_id: str = Field(...)
    status: Literal["ready", "incomplete", "missing_config", "unknown"] = Field(...)
    total_dependencies: int = Field(..., ge=0)
    ready: int = Field(..., ge=0, description="Dependencies that exist")
    missing: int = Field(..., ge=0, description="Dependencies that don't exist")
    dependencies: list[DependencyInfo] = Field(...)
    assembly_order: list[str] = Field(..., description="Content IDs in assembly order")
    missing_content_ids: list[str] | None = Field(
        default=None,
        description="List of missing content IDs (can pass to batch_generate)",
    )
    duration_ms: int = Field(..., ge=0)


# =============================================================================
# Day 3 Tools: list_artifacts, list_content
# =============================================================================


class ArtifactSummary(BaseModel):
    """Summary information for a single artifact."""

    id: str = Field(..., description="Artifact configuration ID")
    title: str = Field(..., description="Artifact title from metadata")
    type: str = Field(
        ..., description="Artifact type (documentation, test, code, report, etc.)"
    )
    stage: str = Field(
        ..., description="Evolution stage (draft, active, deprecated, etc.)"
    )
    purpose: str = Field(..., description="Artifact purpose from metadata")
    dependencies: int = Field(..., ge=0, description="Number of content dependencies")
    assembled: bool = Field(..., description="Whether artifact has been assembled")
    last_assembled: str | None = Field(
        default=None, description="ISO 8601 timestamp of last assembly (if assembled)"
    )
    output_file: str | None = Field(
        default=None, description="Path to assembled output file (if assembled)"
    )
    composition_strategy: str = Field(
        ..., description="Composition strategy (concat, template, etc.)"
    )


class ListArtifactsInput(BaseModel):
    """Input parameters for list_artifacts tool."""

    filter: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Optional filters: type (string), stage (string), assembled (boolean)"
        ),
    )
    sort: Literal["id", "title", "assembled", "modified"] = Field(
        default="id", description="Sort order for results"
    )
    limit: int = Field(
        default=100, ge=1, le=500, description="Maximum number of results to return"
    )


class ListArtifactsResult(BaseModel):
    """Result from list_artifacts tool."""

    success: bool = Field(...)
    total: int = Field(..., ge=0, description="Total artifacts matching filter")
    returned: int = Field(..., ge=0, description="Number of artifacts in results")
    artifacts: list[ArtifactSummary] = Field(
        ..., description="List of artifact summaries"
    )
    duration_ms: int = Field(..., ge=0)


class ContentSummary(BaseModel):
    """Summary information for a single content configuration."""

    id: str = Field(..., description="Content configuration ID")
    title: str = Field(..., description="Content title/description")
    generator_type: str = Field(..., description="Generator type used")
    purpose: str = Field(..., description="Content purpose from metadata")
    stage: str = Field(
        ..., description="Evolution stage (draft, active, deprecated, etc.)"
    )
    generated: bool = Field(..., description="Whether content has been generated")
    last_generated: str | None = Field(
        default=None, description="ISO 8601 timestamp of last generation (if generated)"
    )
    versions_available: int | None = Field(
        default=None,
        ge=0,
        description="Number of versions in ephemeral storage (if generated)",
    )
    output_format: str = Field(
        ..., description="Output format (markdown, text, code, etc.)"
    )


class ListContentInput(BaseModel):
    """Input parameters for list_content tool."""

    filter: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Optional filters: "
            "generator_type (string), generated (boolean), stage (string)"
        ),
    )
    sort: Literal["id", "title", "generator", "modified"] = Field(
        default="id", description="Sort order for results"
    )
    limit: int = Field(
        default=100, ge=1, le=500, description="Maximum number of results to return"
    )


class ListContentResult(BaseModel):
    """Result from list_content tool."""

    success: bool = Field(...)
    total: int = Field(..., ge=0, description="Total content configs matching filter")
    returned: int = Field(..., ge=0, description="Number of content configs in results")
    content: list[ContentSummary] = Field(..., description="List of content summaries")
    duration_ms: int = Field(..., ge=0)


class ContentConfigSummary(BaseModel):
    """Basic summary information for a content configuration file (list_content_configs)."""

    id: str = Field(..., description="Content configuration ID")
    file_path: str = Field(..., description="Relative path to config file")
    generator_type: str = Field(..., description="Generator type")
    description: str = Field(..., description="Content description from metadata")
    title: str = Field(..., description="Content title from metadata")


class ListContentConfigsResult(BaseModel):
    """Result from list_content_configs tool."""

    success: bool = Field(...)
    total: int = Field(..., ge=0, description="Total content configs found")
    configs: list[ContentConfigSummary] = Field(
        ..., description="List of content config summaries"
    )
    duration_ms: int = Field(..., ge=0)


class ArtifactConfigSummary(BaseModel):
    """Basic summary information for an artifact configuration file (list_artifact_configs)."""

    id: str = Field(..., description="Artifact configuration ID")
    file_path: str = Field(..., description="Relative path to config file")
    description: str = Field(..., description="Artifact description from metadata")
    title: str = Field(..., description="Artifact title from metadata")
    component_count: int = Field(..., ge=0, description="Number of components/children")


class ListArtifactConfigsResult(BaseModel):
    """Result from list_artifact_configs tool."""

    success: bool = Field(...)
    total: int = Field(..., ge=0, description="Total artifact configs found")
    configs: list[ArtifactConfigSummary] = Field(
        ..., description="List of artifact config summaries"
    )
    duration_ms: int = Field(..., ge=0)


# =============================================================================
# Day 4 Tools: cleanup_ephemeral + Resource Providers
# =============================================================================


class ContentCleanupDetail(BaseModel):
    """Per-content cleanup statistics."""

    content_id: str = Field(..., description="Content ID that was cleaned")
    versions_before: int = Field(
        ..., ge=0, description="Number of versions before cleanup"
    )
    versions_deleted: int = Field(..., ge=0, description="Number of versions deleted")
    versions_after: int = Field(..., ge=0, description="Number of versions remaining")
    bytes_freed: int = Field(..., ge=0, description="Bytes freed by deletion")
    oldest_kept: str | None = Field(
        default=None, description="ISO 8601 timestamp of oldest kept version"
    )
    latest_kept: str | None = Field(
        default=None, description="ISO 8601 timestamp of latest kept version"
    )


class RetentionPolicy(BaseModel):
    """Retention policy for cleanup operations."""

    keep_versions: int = Field(
        default=3, ge=0, description="Minimum number of versions to keep per content"
    )
    keep_days: int = Field(
        default=7, ge=0, description="Keep versions newer than this many days"
    )
    keep_latest: bool = Field(
        default=True, description="Always preserve the latest version (safety feature)"
    )


class CleanupFilter(BaseModel):
    """Filter for targeted cleanup operations."""

    content_ids: list[str] = Field(
        default_factory=list,
        description="Only clean specific content IDs (empty = all content)",
    )
    older_than_days: int | None = Field(
        default=None,
        ge=0,
        description="Only consider content with versions older than X days",
    )


class CleanupEphemeralInput(BaseModel):
    """Input parameters for cleanup_ephemeral tool."""

    retention: RetentionPolicy = Field(
        default_factory=RetentionPolicy, description="Retention policy settings"
    )
    filter: CleanupFilter = Field(
        default_factory=CleanupFilter, description="Filter for targeted cleanup"
    )
    dry_run: bool = Field(
        default=False,
        description="Preview mode - don't actually delete (always use dry_run first!)",
    )


class CleanupEphemeralResult(BaseModel):
    """Result from cleanup_ephemeral tool."""

    success: bool = Field(...)
    status: Literal["cleaned", "dry_run"] = Field(
        ..., description="'cleaned' if deleted, 'dry_run' if preview only"
    )
    total_content_checked: int = Field(
        ..., ge=0, description="Number of content items checked"
    )
    total_versions_deleted: int = Field(
        ..., ge=0, description="Total versions deleted across all content"
    )
    bytes_freed: int = Field(..., ge=0, description="Total bytes freed")
    content_cleaned: list[ContentCleanupDetail] = Field(
        ..., description="Per-content cleanup details"
    )
    duration_ms: int = Field(..., ge=0)


class SchemaListItem(BaseModel):
    """Schema catalog item for schema:// provider."""

    name: str = Field(..., description="Schema name (content, artifact, etc.)")
    uri: str = Field(..., description="URI to fetch this schema")
    description: str = Field(..., description="Human-readable description")
    version: str = Field(..., description="Schema version")


# =============================================================================
# Config Lifecycle Management Types (v1.1.0)
# =============================================================================


class DraftConfigInput(BaseModel):
    """Input for draft_config tool."""

    config_type: Literal["content", "artifact"] = Field(
        ..., description="Type of configuration"
    )
    config_data: dict[str, Any] = Field(..., description="Configuration JSON")
    description: str | None = Field(
        default=None, description="Optional description for this draft"
    )


class DraftConfigResult(BaseModel):
    """Result from draft_config tool."""

    success: bool = True
    draft_id: str = Field(..., description="Generated draft identifier")
    config_type: str = Field(..., description="Content or artifact")
    validation_status: Literal["valid", "invalid"] = Field(
        ..., description="Schema validation result"
    )
    preview_path: str = Field(..., description="Location in ephemeral storage")
    created_at: str = Field(..., description="ISO 8601 timestamp")
    duration_ms: int = Field(..., ge=0)


class TestConfigInput(BaseModel):
    """Input for test_config tool."""

    draft_id: str = Field(..., description="Draft config identifier")
    context: dict[str, Any] | str = Field(
        default_factory=lambda: {},
        description="Context for generation (auto-parses JSON strings)",
    )
    dry_run: bool = Field(default=True, description="Don't store output")

    @field_validator("context", mode="before")
    @classmethod
    def normalize_context(cls, v: Any) -> dict[str, Any]:
        """Normalize context to dict, parsing JSON strings."""
        if v is None or v == "":
            return {}
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if not isinstance(parsed, dict):
                    raise ValueError(
                        f"JSON must be object, got {type(parsed).__name__}"
                    )
                return parsed
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in context parameter: {e}")
        if isinstance(v, dict):
            return v
        raise ValueError(f"context must be dict or JSON string, got {type(v)}")


class TestConfigResult(BaseModel):
    """Result from test_config tool."""

    success: bool = True
    draft_id: str = Field(..., description="Draft tested")
    preview_content: str = Field(
        ..., description="Generated output (truncated if large)"
    )
    content_length: int = Field(..., ge=0, description="Full content length")
    generator_used: str = Field(..., description="Generator that processed config")
    validation_issues: list[str] = Field(
        default_factory=list, description="Any problems found"
    )
    estimated_cost: dict[str, Any] | None = Field(
        default=None, description="Token usage for AI generators"
    )
    duration_ms: int = Field(..., ge=0)


class SaveConfigInput(BaseModel):
    """Input for save_config tool."""

    draft_id: str = Field(..., description="Draft to persist")
    config_id: str = Field(
        ...,
        description="Permanent config ID (kebab-case, no slashes)",
        min_length=1,
        max_length=255,
    )
    overwrite: bool = Field(default=False, description="Allow overwriting existing")


class SaveConfigResult(BaseModel):
    """Result from save_config tool."""

    success: bool = True
    config_path: str = Field(..., description="Filesystem location")
    config_id: str = Field(..., description="Permanent ID")
    config_type: str = Field(..., description="Content or artifact")
    backup_path: str | None = Field(
        default=None, description="Previous version if overwritten"
    )
    duration_ms: int = Field(..., ge=0)


class ModifyConfigInput(BaseModel):
    """Input for modify_config tool."""

    config_id: str = Field(..., description="Draft ID or permanent config ID")
    updates: dict[str, Any] = Field(..., description="JSON patch to apply")
    create_backup: bool = Field(default=True, description="Backup before modifying")


class ModifyConfigResult(BaseModel):
    """Result from modify_config tool."""

    success: bool = True
    config_id: str = Field(..., description="Modified config ID")
    config_type: str = Field(..., description="Content or artifact")
    validation_status: Literal["valid", "invalid"] = Field(
        ..., description="Schema check after modification"
    )
    backup_path: str | None = Field(
        default=None, description="Previous version location"
    )
    draft_id: str | None = Field(
        default=None, description="New draft ID if config was persisted"
    )
    duration_ms: int = Field(..., ge=0)


# =============================================================================
# Type Exports
# =============================================================================

__all__ = [
    # generate_content
    "GenerateContentInput",
    "GenerateContentResult",
    # assemble_artifact
    "AssembleArtifactInput",
    "AssembleArtifactResult",
    "ComponentInfo",
    # list_generators
    "ListGeneratorsInput",
    "ListGeneratorsResult",
    "GeneratorInfo",
    # validate_content
    "ValidationInput",
    "ValidationResult",
    "ValidationIssue",
    "ValidationRuleConfig",
    # regenerate_content
    "RegenerateContentInput",
    "RegenerateContentResult",
    "PreviousVersionInfo",
    "ContentChanges",
    # delete_content
    "DeleteContentInput",
    "DeleteContentResult",
    "ContentReferences",
    # preview_generation
    "PreviewGenerationInput",
    "PreviewGenerationResult",
    "PreviewMetadata",
    # batch_generate
    "BatchGenerateInput",
    "BatchGenerateResult",
    "ContentGenerationResult",
    "GenerationError",
    # trace_dependencies
    "TraceDependenciesInput",
    "TraceDependenciesResult",
    "DependencyInfo",
    "DependencyMetadata",
    # list_artifacts
    "ListArtifactsInput",
    "ListArtifactsResult",
    "ArtifactSummary",
    # list_content
    "ListContentInput",
    "ListContentResult",
    "ContentSummary",
    # cleanup_ephemeral
    "CleanupEphemeralInput",
    "CleanupEphemeralResult",
    "ContentCleanupDetail",
    "RetentionPolicy",
    "CleanupFilter",
    # config lifecycle management (v1.1.0)
    "DraftConfigInput",
    "DraftConfigResult",
    "TestConfigInput",
    "TestConfigResult",
    "SaveConfigInput",
    "SaveConfigResult",
    "ModifyConfigInput",
    "ModifyConfigResult",
    # resource providers
    "SchemaListItem",
    # errors
    "MCPError",
    "ErrorDetails",
    "ErrorResponse",
]
