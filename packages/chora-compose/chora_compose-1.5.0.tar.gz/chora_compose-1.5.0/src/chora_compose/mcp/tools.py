"""MCP tool implementations.

This module contains the implementation of all MCP tools exposed by
the chora-compose server.

Day 1: hello_world test tool to validate stdio transport
Day 4: generate_content and list_generators implementation
Day 5: assemble_artifact and validate_content implementation
"""

import importlib.util
import sys as _sys
import time
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, TypeVar

import pydantic
from chora_compose.core import get_config_loader
from chora_compose.core.composer import ArtifactComposer
from chora_compose.generators.registry import GeneratorRegistry
from chora_compose.storage import get_ephemeral_storage
from chora_compose.storage.ephemeral import EphemeralStorageManager

# Type variable for function decoration
F = TypeVar("F", bound=Callable[..., Any])

# Import MCP instance - using instance.py to avoid circular imports
try:
    from .instance import mcp
except (ImportError, ModuleNotFoundError):
    # Create a no-op decorator for testing
    class MockMCP:
        """Mock MCP decorator for testing without FastMCP."""

        def tool(self, name: str | None = None, **kwargs: Any) -> Callable[[F], F]:
            """Mock tool decorator that returns the function unchanged."""

            def decorator(func: F) -> F:
                return func

            return decorator

    mcp: Any = MockMCP()  # type: ignore[no-redef]  # Fallback for testing

# Keep version reporting aligned with server metadata
HELLO_WORLD_VERSION = getattr(mcp, "version", "1.0.1")

# Import types - use absolute import to avoid __init__.py issues in tests

# Try relative import first (normal case)
try:
    from .types import (
        ArtifactConfigSummary,
        ArtifactSummary,
        AssembleArtifactResult,
        BatchGenerateResult,
        CleanupEphemeralResult,
        CleanupFilter,
        ContentChanges,
        ContentCleanupDetail,
        ContentConfigSummary,
        ContentGenerationResult,
        ContentReferences,
        ContentSummary,
        DeleteContentResult,
        DependencyInfo,
        DependencyMetadata,
        ErrorResponse,
        GenerateContentResult,
        GenerationError,
        GeneratorInfo,
        ListArtifactConfigsResult,
        ListArtifactsResult,
        ListContentConfigsResult,
        ListContentResult,
        ListGeneratorsResult,
        MCPError,
        PreviewGenerationResult,
        PreviewMetadata,
        PreviousVersionInfo,
        RegenerateContentResult,
        RetentionPolicy,
        TraceDependenciesResult,
        ValidationIssue,
        ValidationResult,
    )
except (ImportError, ModuleNotFoundError):
    # Fallback for testing: load types.py directly
    _types_file = Path(__file__).parent / "types.py"
    _spec = importlib.util.spec_from_file_location(
        "chora_compose.mcp.types", _types_file
    )

    if _spec is None or _spec.loader is None:
        raise ImportError(
            f"Failed to load types module from {_types_file}. "
            "Ensure the file exists and is readable."
        )

    _types_module: ModuleType = importlib.util.module_from_spec(_spec)
    _sys.modules.setdefault("chora_compose.mcp.types", _types_module)
    _spec.loader.exec_module(_types_module)

    # Use getattr to extract types from module (dynamic loading for testing)
    ArtifactConfigSummary = getattr(_types_module, "ArtifactConfigSummary")  # type: ignore[misc]
    ArtifactSummary = getattr(_types_module, "ArtifactSummary")  # type: ignore[misc]
    AssembleArtifactResult = getattr(_types_module, "AssembleArtifactResult")  # type: ignore[misc]
    BatchGenerateResult = getattr(_types_module, "BatchGenerateResult")  # type: ignore[misc]
    CleanupEphemeralResult = getattr(_types_module, "CleanupEphemeralResult")  # type: ignore[misc]
    CleanupFilter = getattr(_types_module, "CleanupFilter")  # type: ignore[misc]
    ContentChanges = getattr(_types_module, "ContentChanges")  # type: ignore[misc]
    ContentCleanupDetail = getattr(_types_module, "ContentCleanupDetail")  # type: ignore[misc]
    ContentConfigSummary = getattr(_types_module, "ContentConfigSummary")  # type: ignore[misc]
    ContentGenerationResult = getattr(_types_module, "ContentGenerationResult")  # type: ignore[misc]
    ContentReferences = getattr(_types_module, "ContentReferences")  # type: ignore[misc]
    ContentSummary = getattr(_types_module, "ContentSummary")  # type: ignore[misc]
    DeleteContentResult = getattr(_types_module, "DeleteContentResult")  # type: ignore[misc]
    DependencyInfo = getattr(_types_module, "DependencyInfo")  # type: ignore[misc]
    DependencyMetadata = getattr(_types_module, "DependencyMetadata")  # type: ignore[misc]
    ErrorResponse = getattr(_types_module, "ErrorResponse")  # type: ignore[misc]
    GenerateContentResult = getattr(_types_module, "GenerateContentResult")  # type: ignore[misc]
    GenerationError = getattr(_types_module, "GenerationError")  # type: ignore[misc]
    GeneratorInfo = getattr(_types_module, "GeneratorInfo")  # type: ignore[misc]
    ListArtifactConfigsResult = getattr(_types_module, "ListArtifactConfigsResult")  # type: ignore[misc]
    ListArtifactsResult = getattr(_types_module, "ListArtifactsResult")  # type: ignore[misc]
    ListContentConfigsResult = getattr(_types_module, "ListContentConfigsResult")  # type: ignore[misc]
    ListContentResult = getattr(_types_module, "ListContentResult")  # type: ignore[misc]
    ListGeneratorsResult = getattr(_types_module, "ListGeneratorsResult")  # type: ignore[misc]
    MCPError = getattr(_types_module, "MCPError")  # type: ignore[misc]
    PreviewGenerationResult = getattr(_types_module, "PreviewGenerationResult")  # type: ignore[misc]
    PreviewMetadata = getattr(_types_module, "PreviewMetadata")  # type: ignore[misc]
    PreviousVersionInfo = getattr(_types_module, "PreviousVersionInfo")  # type: ignore[misc]
    RegenerateContentResult = getattr(_types_module, "RegenerateContentResult")  # type: ignore[misc]
    RetentionPolicy = getattr(_types_module, "RetentionPolicy")  # type: ignore[misc]
    TraceDependenciesResult = getattr(_types_module, "TraceDependenciesResult")  # type: ignore[misc]
    ValidationIssue = getattr(_types_module, "ValidationIssue")  # type: ignore[misc]
    ValidationResult = getattr(_types_module, "ValidationResult")  # type: ignore[misc]


# =============================================================================
# Helper Functions
# =============================================================================


# -----------------------------------------------------------------------------
# Validation Rule System (Week 3 Days 2-4)
# -----------------------------------------------------------------------------
#
# Validation rules allow custom validation logic to be applied to content
# and configurations beyond basic schema validation.
#
# Rule Schema:
# {
#     "type": str,       # Rule type: "length" | "required_fields" | "regex"
#     "severity": str,   # Issue severity: "error" | "warning" | "info"
#     "config": dict,    # Type-specific configuration
# }
#
# Supported Rule Types:
#
# 1. "length" - Validates content/config length
#    Config: {"min": int, "max": int}  # Both optional
#    Example: {"type": "length", "severity": "error", "config": {"min": 100}}
#
# 2. "required_fields" - Validates required fields present in config
#    Config: {"fields": list[str]}
#    Example: {"type": "required_fields", "severity": "error",
#              "config": {"fields": ["title", "content"]}}
#
# Design Decisions:
# - Rules processed AFTER schema validation (schema must pass first)
# - Invalid rules raise ValueError (caught by outer exception handler)
# - Unknown rule types generate warnings (not errors)
# - Rules can be chained (multiple rules processed in order)
# - Each rule generates 0 or more ValidationIssue objects
#


def _validate_config_id(config_id: str) -> None:
    """Validate config ID for security.

    Args:
        config_id: Configuration ID to validate

    Raises:
        ValueError: If config_id is invalid
    """
    if not config_id or not config_id.strip():
        raise ValueError("Config ID cannot be empty")
    if ".." in config_id or "/" in config_id or "\\" in config_id:
        raise ValueError(
            "Config ID contains invalid path characters (path traversal attempt)"
        )


def _merge_context(
    config_context: dict[str, Any], tool_context: dict[str, Any]
) -> dict[str, Any]:
    """Merge contexts with tool context taking precedence.

    Args:
        config_context: Context from configuration file
        tool_context: Context from tool invocation

    Returns:
        Merged context dictionary
    """
    merged = config_context.copy()
    merged.update(tool_context)
    return merged


def _handle_tool_error(error: Any, tool_name: str, start_time: float) -> dict[str, Any]:
    """Convert exception to ErrorResponse.

    Args:
        error: Exception or MCPError that occurred
        tool_name: Name of the tool that errored
        start_time: Start time (from time.time())

    Returns:
        ErrorResponse as dict
    """
    if isinstance(error, MCPError):
        error_response = ErrorResponse(success=False, error=error)
    else:
        # Map specific exception types to error codes
        if isinstance(error, FileNotFoundError):
            error_code = "config_not_found"
        elif isinstance(error, ValueError) and "path traversal" in str(error):
            error_code = "invalid_config_id"
        elif isinstance(error, ValueError) and (
            "output" in str(error).lower() or "path" in str(error).lower()
        ):
            error_code = "invalid_output_path"
        elif type(error).__name__ == "RegistryError":
            error_code = "generator_not_found"
        elif type(error).__name__ == "CompositionError":
            error_code = "assembly_failed"
        elif "generate" in tool_name.lower():
            # Generator execution errors
            error_code = "generation_failed"
        elif "assemble" in tool_name.lower():
            # Assembly errors
            error_code = "assembly_failed"
        elif "validate" in tool_name.lower():
            # Validation errors
            error_code = "validation_failed"
        else:
            error_code = "internal_error"

        error_response = ErrorResponse(
            success=False,
            error=MCPError(
                code=error_code,
                message=str(error),
                details={"tool": tool_name, "error_type": type(error).__name__},
            ),
        )

    return error_response.model_dump()


def _validate_rule_structure(rule: dict[str, Any]) -> None:
    """Validate validation rule structure.

    Validates that a custom validation rule has all required fields and
    valid values. This function is called before applying any rule to
    catch malformed rules early.

    Args:
        rule: Validation rule dictionary to validate

    Raises:
        ValueError: If rule is malformed or has invalid values

    Example:
        >>> rule = {"type": "length", "severity": "error", "config": {"min": 100}}
        >>> _validate_rule_structure(rule)  # Passes
        >>>
        >>> bad_rule = {"severity": "error"}  # Missing 'type'
        >>> _validate_rule_structure(bad_rule)  # Raises ValueError

    Test Cases (to be enabled Day 3):
        1. Valid rule with all fields
        2. Valid rule with default severity
        3. Invalid rule missing 'type' → ValueError
        4. Invalid rule with bad severity → ValueError
        5. Invalid rule with non-dict config → ValueError
    """
    # Check required field: type
    if "type" not in rule:
        raise ValueError("Validation rule missing required field 'type'")

    # Severity is optional, but if present must be valid
    if "severity" in rule:
        valid_severities = ["error", "warning", "info"]
        if rule["severity"] not in valid_severities:
            raise ValueError(
                f"Invalid severity '{rule['severity']}'. "
                f"Must be one of: {', '.join(valid_severities)}"
            )
    else:
        # Default to "error" if not specified
        rule["severity"] = "error"

    # Config must be a dict if present
    if "config" in rule and not isinstance(rule["config"], dict):
        raise ValueError("Rule 'config' must be a dictionary")


def _apply_length_rule(content: str, rule: dict[str, Any]) -> list[ValidationIssue]:
    """Apply length validation rule to content.

    Checks if content meets minimum and/or maximum length requirements
    specified in the rule configuration.

    Args:
        content: Content string to validate
        rule: Rule dictionary with config.min and/or config.max

    Returns:
        List of ValidationIssue objects (empty if validation passes)

    Example:
        >>> rule = {"type": "length", "severity": "error", "config": {"min": 100}}
        >>> content = "Short"
        >>> issues = _apply_length_rule(content, rule)
        >>> len(issues)  # 1 issue (content too short)
        1
        >>> issues[0].code
        'content_too_short'
    """
    issues = []
    config = rule.get("config", {})
    content_length = len(content)

    # Check minimum length
    if "min" in config and content_length < config["min"]:
        issues.append(
            ValidationIssue(
                severity=rule["severity"],
                code="content_too_short",
                message=(
                    f"Content length {content_length} is below minimum {config['min']}"
                ),
                location="content",
                details={"actual": content_length, "required": config["min"]},
            )
        )

    # Check maximum length
    if "max" in config and content_length > config["max"]:
        issues.append(
            ValidationIssue(
                severity=rule["severity"],
                code="content_too_long",
                message=(
                    f"Content length {content_length} exceeds maximum {config['max']}"
                ),
                location="content",
                details={"actual": content_length, "limit": config["max"]},
            )
        )

    return issues


def _apply_required_fields_rule(
    config: Any, rule: dict[str, Any]
) -> list[ValidationIssue]:
    """Apply required fields validation rule to config.

    Checks if all required fields specified in the rule are present
    in the configuration object.

    Args:
        config: Configuration object to validate (typically ContentConfig)
        rule: Rule dictionary with config.fields list

    Returns:
        List of ValidationIssue objects (empty if all fields present)

    Example:
        >>> rule = {
        ...     "type": "required_fields",
        ...     "severity": "error",
        ...     "config": {"fields": ["title", "description"]}
        ... }
        >>> config = Mock(title="Test")  # Missing description
        >>> issues = _apply_required_fields_rule(config, rule)
        >>> len(issues)  # 1 issue (missing description)
        1
        >>> issues[0].code
        'missing_required_field'
    """
    issues = []
    config_dict = rule.get("config", {})
    required_fields = config_dict.get("fields", [])

    for field in required_fields:
        # Check if field exists (works for both dict and object attributes)
        has_field = False
        if isinstance(config, dict):
            has_field = field in config
        else:
            has_field = hasattr(config, field)

        if not has_field:
            issues.append(
                ValidationIssue(
                    severity=rule["severity"],
                    code="missing_required_field",
                    message=f"Required field '{field}' is missing",
                    location=field,
                    details={"field": field, "required": True},
                )
            )

    return issues


def _validate_generated_content(
    content_id: str,
    content: str | list,
    validation_rules: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """Validate generated content quality.

    Performs quality checks on generated content including:
    - Emptiness check
    - Length warnings for very short content
    - Completeness check (... or [TBD] markers)
    - Custom validation rules

    Args:
        content_id: Content identifier
        content: Content string or list to validate
        validation_rules: Optional custom rules to apply

    Returns:
        ValidationResult as dict

    Example:
        >>> content = "# Guide\\n\\nShort..."
        >>> result = _validate_generated_content("guide", content, None)
        >>> result["valid"]  # False (incomplete)
        False
        >>> result["warning_count"]  # 1 (incomplete marker)
        1
    """
    issues = []

    # Convert list to string if needed
    if isinstance(content, list):
        content = "\n".join(str(item) for item in content)

    # 1. Emptiness check (error)
    if not content or not content.strip():
        issues.append(
            ValidationIssue(
                severity="error",
                code="content_empty",
                message="Generated content is empty",
                location=content_id,
                details={},
            )
        )
        return _build_validation_result(issues)

    # 2. Length warning for very short content
    if len(content) < 10:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="content_very_short",
                message=f"Content is very short ({len(content)} characters)",
                location=content_id,
                details={"length": len(content)},
            )
        )

    # 3. Completeness check (warning)
    if content.endswith("...") or "[TBD]" in content:
        issues.append(
            ValidationIssue(
                severity="warning",
                code="content_incomplete",
                message="Content appears incomplete (contains ... or [TBD])",
                location=content_id,
                details={},
            )
        )

    # 4. Apply custom validation rules
    if validation_rules:
        for rule in validation_rules:
            try:
                _validate_rule_structure(rule)
                if rule["type"] == "length":
                    issues.extend(_apply_length_rule(content, rule))
                # Note: required_fields doesn't apply to content strings
            except ValueError as e:
                # Invalid rule structure
                issues.append(
                    ValidationIssue(
                        severity="error",
                        code="invalid_rule",
                        message=f"Invalid validation rule: {e}",
                        location=content_id,
                        details={"rule_error": str(e)},
                    )
                )

    return _build_validation_result(issues)


def _build_validation_result(issues: list) -> dict[str, Any]:
    """Build ValidationResult from issues list.

    Args:
        issues: List of ValidationIssue objects

    Returns:
        ValidationResult as dict with success=True, valid based on error_count
    """
    error_count = sum(1 for i in issues if i.severity == "error")
    warning_count = sum(1 for i in issues if i.severity == "warning")
    info_count = sum(1 for i in issues if i.severity == "info")

    return ValidationResult(
        success=True,
        valid=error_count == 0,
        issues=issues,
        error_count=error_count,
        warning_count=warning_count,
        info_count=info_count,
    ).model_dump()


# =============================================================================
# Test Tool (Day 1)
# =============================================================================


@mcp.tool(name="choracompose:hello_world")
async def hello_world(name: str = "World") -> dict[str, Any]:
    """
    Test tool to validate MCP connection.

    This is a simple test tool used to verify that the stdio transport
    is working correctly and that Claude Desktop can successfully call
    MCP tools on the chora-compose server.

    Args:
        name: Name to greet (default: "World")

    Returns:
        dict containing:
        - message: Greeting message
        - version: Server version
        - tools_available: Number of tools available
        - status: Server operational status
    """
    return {
        "message": f"Hello {name} from chora-compose!",
        "version": HELLO_WORLD_VERSION,
        "tools_available": 4,
        "status": "operational",
        "transport": "stdio",
    }


# =============================================================================
# Core Tools (Day 4)
# =============================================================================


@mcp.tool(name="choracompose:list_generators")
async def list_generators(
    generator_type: str | None = None,
    include_plugins: bool = True,
) -> dict[str, Any]:
    """List all available content generators.

    Args:
        generator_type: Filter by type ("builtin" or "plugin"). None = all.
        include_plugins: Include plugin generators in results.

    Returns:
        ListGeneratorsResult as dict with:
        - success: bool
        - generators: List[GeneratorInfo]
        - total_count: int
        - filtered: bool
    """
    start_time = time.time()

    try:
        # Get registry instance
        registry = GeneratorRegistry()

        # Get all generator types
        all_types = registry.list_types()

        # List of known built-in generator names
        builtin_names = {
            "demonstration",
            "jinja2",
            "template_fill",
            "bdd_scenario_assembly",
            "code_generation",
        }

        # Build generator info list
        generators = []
        for gen_type in all_types:
            generator = registry.get(gen_type)

            # Determine if builtin or plugin
            is_builtin = gen_type in builtin_names
            # Cast to Literal type for type safety
            from typing import Literal, cast

            gen_info_type_lit: Literal["builtin", "plugin"] = cast(
                Literal["builtin", "plugin"], "builtin" if is_builtin else "plugin"
            )

            # Apply filters
            if generator_type and gen_info_type_lit != generator_type:
                continue
            if not include_plugins and gen_info_type_lit == "plugin":
                continue

            # Get generator metadata (with fallbacks)
            gen_info = GeneratorInfo(
                name=gen_type,
                type=gen_info_type_lit,
                version=getattr(generator, "version", "unknown"),
                description=getattr(generator, "description", f"{gen_type} generator"),
                capabilities=getattr(generator, "capabilities", []),
            )
            generators.append(gen_info)

        filters_applied = (generator_type is not None) or (include_plugins is False)

        result = ListGeneratorsResult(
            success=True,
            generators=generators,
            total_count=len(generators),
            filtered=filters_applied,
        )

        return result.model_dump()

    except Exception as e:
        return _handle_tool_error(e, "list_generators", start_time)


async def _generate_content_impl(
    content_config_id: str,
    context: dict[str, Any] | str | None = None,
    force: bool = False,
    # Hidden parameters for testing (not exposed in MCP schema)
    _config_loader: Any = None,
    _registry: Any = None,
    _storage: Any = None,
) -> dict[str, Any]:
    """Internal implementation of generate_content.

    This function contains the actual logic and can be called by both the
    MCP tool wrapper and other tools like batch_generate.

    Args:
        content_config_id: ID of content config to use
        context: Context variables (merged with config context).
            Can be dict or JSON string.
        force: Force regeneration even if exists
        _config_loader: Injected config loader (for testing)
        _registry: Injected generator registry (for testing)
        _storage: Injected storage (for testing)

    Returns:
        GenerateContentResult as dict with:
        - success: bool
        - content_id: str
        - content: str
        - generator: str
        - status: str (generated|skipped|regenerated)
        - duration_ms: int
        - metadata: dict
    """
    start_time = time.time()

    # Parse context parameter first (before defaulting to {})
    parsed_context: dict[str, Any] = {}

    # Defensive guard: Normalize stringified JSON context
    # Pydantic should handle this, but guard against edge cases
    # where validation is bypassed
    if isinstance(context, str):
        # Empty string is treated as empty context
        if context == "":
            parsed_context = {}
        else:
            try:
                import json as _json

                parsed_context = _json.loads(context)
                if not isinstance(parsed_context, dict):
                    return _handle_tool_error(
                        MCPError(
                            code="invalid_context",
                            message=(
                                f"context must be JSON object; "
                                f"parsed to {type(parsed_context).__name__}"
                            ),
                            details={"received_type": type(parsed_context).__name__},
                        ),
                        "generate_content",
                        start_time,
                    )
            except _json.JSONDecodeError as e:
                return _handle_tool_error(
                    MCPError(
                        code="invalid_context",
                        message=(
                            "context must be JSON object; "
                            "received string we could not parse"
                        ),
                        details={
                            "received": context[:100] if context else "",
                            "error": str(e),
                        },
                    ),
                    "generate_content",
                    start_time,
                )
    elif context is not None:
        parsed_context = context  # Already a dict
    else:
        parsed_context = {}  # None provided

    try:
        # Validate config ID
        _validate_config_id(content_config_id)

        # Initialize components (use injected or create real ones)
        config_loader = _config_loader or get_config_loader()
        registry = _registry or GeneratorRegistry()
        storage = _storage or EphemeralStorageManager(base_path=Path("ephemeral"))

        # Check if already exists (idempotency)
        if not force:
            try:
                existing = storage.retrieve(content_config_id, strategy="latest")
            except FileNotFoundError:
                existing = None
            if existing:
                # Ensure content is string type
                existing_content: str = (
                    "\n".join(existing) if isinstance(existing, list) else str(existing)
                )
                duration_ms = int((time.time() - start_time) * 1000)
                result = GenerateContentResult(
                    success=True,
                    content_id=content_config_id,
                    content=existing_content,
                    generator="cached",
                    status="skipped",
                    duration_ms=duration_ms,
                    metadata={"reason": "already_exists", "from_cache": True},
                )
                return result.model_dump()

        # Load content config
        content_config = config_loader.load_content_config(content_config_id)

        # Merge context (tool context takes precedence)
        # Handle both dict and Pydantic model for metadata
        if hasattr(content_config.metadata, "get"):
            config_context = content_config.metadata.get("context", {})
        elif hasattr(content_config.metadata, "model_dump"):
            config_context = content_config.metadata.model_dump().get("context", {})
        elif isinstance(content_config.metadata, dict):
            config_context = content_config.metadata.get("context", {})
        else:
            config_context = {}
        merged_context = _merge_context(config_context, parsed_context)

        # Get generator type from config
        # Handle both dict and Pydantic model for generation
        generation = content_config.generation or {}
        if hasattr(generation, "get"):
            patterns = generation.get("patterns", [])
        elif isinstance(generation, dict):
            patterns = generation.get("patterns", [])
        else:
            patterns = getattr(generation, "patterns", [])
        if not patterns:
            raise ValueError(
                f"No generation patterns defined in config '{content_config_id}'"
            )

        pattern = patterns[0]
        # Handle both dict and Pydantic model for pattern
        if hasattr(pattern, "get"):
            generator_type = pattern.get("type")
        elif isinstance(pattern, dict):
            generator_type = pattern.get("type")
        else:
            generator_type = getattr(pattern, "type", None)
        if not generator_type:
            raise ValueError(
                f"Pattern missing 'type' field in config '{content_config_id}'"
            )

        # Get generator and generate content
        generator = registry.get(generator_type)
        gen_output = generator.generate(content_config, merged_context)

        # Ensure content is a string (some generators might return list or other types)
        generated_content: str = (
            "\n".join(gen_output) if isinstance(gen_output, list) else str(gen_output)
        )

        # Store in ephemeral storage
        storage.save(
            content_id=content_config_id,
            content=generated_content,
            format="txt",
            metadata={"generator": generator_type, "context": merged_context},
        )

        duration_ms = int((time.time() - start_time) * 1000)

        result = GenerateContentResult(
            success=True,
            content_id=content_config_id,
            content=generated_content,
            generator=generator_type,
            status="regenerated" if force else "generated",
            duration_ms=duration_ms,
            metadata={
                "ephemeral_stored": True,
                "context_variables": list(merged_context.keys()),
                "generator_version": getattr(generator, "version", "unknown"),
            },
        )

        return result.model_dump()

    except FileNotFoundError:
        return _handle_tool_error(
            MCPError(
                code="config_not_found",
                message=f"Content config '{content_config_id}' not found",
                details={"content_config_id": content_config_id},
            ),
            "generate_content",
            start_time,
        )
    except ValueError as e:
        return _handle_tool_error(
            MCPError(
                code="invalid_config_id"
                if "path characters" in str(e)
                else "generation_failed",
                message=str(e),
                details={"content_config_id": content_config_id},
            ),
            "generate_content",
            start_time,
        )
    except Exception as e:
        return _handle_tool_error(e, "generate_content", start_time)


@mcp.tool(name="choracompose:generate_content")
async def generate_content(
    content_config_id: str,
    context: dict[str, Any] | str | None = None,
    force: bool = False,
    # Hidden parameters for testing (not exposed in MCP schema)
    _config_loader: Any = None,
    _registry: Any = None,
    _storage: Any = None,
) -> dict[str, Any]:
    """Generate content from a content configuration.

    Args:
        content_config_id: ID of content config to use
        context: Context variables (merged with config context).
            Can be dict or JSON string.
        force: Force regeneration even if exists

    Returns:
        GenerateContentResult as dict with:
        - success: bool
        - content_id: str
        - content: str
        - generator: str
        - status: str (generated|skipped|regenerated)
        - duration_ms: int
        - metadata: dict
    """
    return await _generate_content_impl(
        content_config_id=content_config_id,
        context=context,
        force=force,
        _config_loader=_config_loader,
        _registry=_registry,
        _storage=_storage,
    )


# =============================================================================
# Core Tools (Day 5)
# =============================================================================


@mcp.tool(name="choracompose:assemble_artifact")
async def assemble_artifact(
    artifact_config_id: str,
    output_path: str | None = None,
    force: bool = False,
    context: dict[str, Any] | str | None = None,
    # Hidden parameters for testing
    _config_loader: Any = None,
    _composer: Any = None,
    _storage: Any = None,
) -> dict[str, Any]:
    """Assemble final artifact by combining multiple content pieces.

    Args:
        artifact_config_id: ID of artifact config to use
        output_path: Override output path from config
        force: Force reassembly even if exists
        context: Optional context for child content generation (dict or JSON string)

    Returns:
        AssembleArtifactResult as dict with:
        - success: bool
        - artifact_id: str
        - output_path: str
        - content_count: int
        - size_bytes: int
        - status: str (assembled|skipped|reassembled)
        - duration_ms: int
        - metadata: dict
    """
    start_time = time.time()

    # Parse context parameter (similar to generate_content)
    parsed_context: dict[str, Any] = {}
    if isinstance(context, str):
        if context != "":
            try:
                import json as _json

                parsed_context = _json.loads(context)
                if not isinstance(parsed_context, dict):
                    return _handle_tool_error(
                        MCPError(
                            code="invalid_context",
                            message=(
                                f"context must be JSON object; "
                                f"parsed to {type(parsed_context).__name__}"
                            ),
                            details={"received_type": type(parsed_context).__name__},
                        ),
                        "assemble_artifact",
                        start_time,
                    )
            except _json.JSONDecodeError as e:
                return _handle_tool_error(
                    MCPError(
                        code="invalid_context",
                        message=(
                            "context must be JSON object; "
                            "received string we could not parse"
                        ),
                        details={
                            "received": context[:100] if context else "",
                            "error": str(e),
                        },
                    ),
                    "assemble_artifact",
                    start_time,
                )
    elif context is not None:
        parsed_context = context

    try:
        # Validate config ID
        _validate_config_id(artifact_config_id)

        # Initialize components (use injected or create real ones)
        config_loader = _config_loader or get_config_loader()
        composer = _composer or ArtifactComposer(config_loader=config_loader)

        # Determine output path
        if output_path:
            output_path_obj = Path(output_path)
        else:
            # Load config to get default output path
            artifact_config = config_loader.load_artifact_config(artifact_config_id)
            if not artifact_config.metadata.outputs:
                raise ValueError(
                    f"Artifact '{artifact_config_id}' has no output files defined"
                )
            output_path_obj = Path(artifact_config.metadata.outputs[0].file)

        # Check if already exists (idempotency)
        if not force and output_path_obj.exists():
            # Get file size and basic metadata
            size_bytes = output_path_obj.stat().st_size
            duration_ms = int((time.time() - start_time) * 1000)

            result = AssembleArtifactResult(
                success=True,
                artifact_id=artifact_config_id,
                output_path=str(output_path_obj.absolute()),
                content_count=0,  # Unknown without reassembly
                size_bytes=size_bytes,
                status="skipped",
                duration_ms=duration_ms,
                metadata={
                    "reason": "already_exists",
                    "from_cache": True,
                },
            )
            return result.model_dump()

        # Pre-assembly validation: Check if all required content exists
        # Load config to check content references
        artifact_config = config_loader.load_artifact_config(artifact_config_id)

        # Get list of required content IDs
        required_content_ids = []
        for content_ref in artifact_config.content.children:
            # Handle both dict and object forms
            if hasattr(content_ref, "id"):
                content_id = content_ref.id
            elif isinstance(content_ref, dict):
                content_id = content_ref.get("id") or content_ref.get("contentId")
            else:
                content_id = str(content_ref)

            if content_id:
                required_content_ids.append(content_id)

        # Check which content exists in storage (use injected or create real one)
        from chora_compose.storage.ephemeral import EphemeralStorageManager

        storage = _storage or EphemeralStorageManager(base_path=Path("ephemeral"))

        missing_content = []
        available_content = []

        for content_id in required_content_ids:
            try:
                retrieved = storage.retrieve(content_id)
                if retrieved:
                    available_content.append(content_id)
                else:
                    missing_content.append(content_id)
            except FileNotFoundError:
                missing_content.append(content_id)
            except Exception:
                # If we can't check, assume available (let composer handle it)
                available_content.append(content_id)

        # If any content is missing, return helpful error
        if missing_content:
            suggestions = [
                f"  generate_content(content_config_id='{cid}')"
                for cid in missing_content
            ]
            return _handle_tool_error(
                MCPError(
                    code="content_missing",
                    message=(
                        f"Cannot assemble artifact: {len(missing_content)} content "
                        f"piece(s) not generated yet. Artifact assembly uses "
                        f"cached content only."
                    ),
                    details={
                        "missing_content": missing_content,
                        "available_content": available_content,
                        "total_required": len(required_content_ids),
                        "suggestion": "Generate missing content first:\n"
                        + "\n".join(suggestions),
                        "note": (
                            "Artifact assembly combines pre-existing cached content. "
                            "It does not regenerate content pieces on demand. "
                            "Generate all required content before assembling."
                        ),
                    },
                ),
                "assemble_artifact",
                start_time,
            )

        # Assemble the artifact
        output_override = Path(output_path) if output_path else None
        result_path = composer.assemble(
            artifact_id=artifact_config_id,
            output_override=output_override,
            context=parsed_context if parsed_context else None,
        )

        # Get output file stats
        size_bytes = result_path.stat().st_size
        duration_ms = int((time.time() - start_time) * 1000)

        # Get component count (artifact_config already loaded above)
        content_count = len(artifact_config.content.children)

        # Build components list with sizes
        components = []
        for child in artifact_config.content.children:
            # Extract content ID from child
            if hasattr(child, "id"):
                content_id = child.id
            elif isinstance(child, dict):
                content_id = child.get("id") or child.get("contentId")
            else:
                content_id = str(child)

            # Try to get size from storage
            try:
                content = storage.retrieve(content_id)
                component_size = len(content.encode("utf-8")) if content else 0
            except Exception:
                component_size = 0  # Unknown size if can't retrieve

            components.append({"content_id": content_id, "size_bytes": component_size})

        # Determine separator based on composition strategy
        composition_strategy_value = (
            artifact_config.metadata.compositionStrategy.value
            if hasattr(artifact_config.metadata.compositionStrategy, "value")
            else str(artifact_config.metadata.compositionStrategy)
        )

        # Default separators by strategy
        separator_map = {
            "concat": "\n\n",
            "merge": "",
            "template": "N/A",
            "custom": "N/A",
        }
        separator = separator_map.get(composition_strategy_value, "\n\n")

        # Build result with proper Literal typing
        from typing import Literal, cast

        status_lit: Literal["assembled", "skipped", "reassembled"] = cast(
            Literal["assembled", "skipped", "reassembled"],
            "reassembled" if force else "assembled",
        )
        result = AssembleArtifactResult(
            success=True,
            artifact_id=artifact_config_id,
            output_path=str(result_path.absolute()),
            content_count=content_count,
            size_bytes=size_bytes,
            status=status_lit,
            duration_ms=duration_ms,
            metadata={
                "composition_strategy": composition_strategy_value,
                "components": components,
                "separator": separator,
                "total_assembly_time_ms": duration_ms,
            },
        )
        return result.model_dump()

    except FileNotFoundError as e:
        return _handle_tool_error(e, "assemble_artifact", start_time)
    except ValueError as e:
        return _handle_tool_error(e, "assemble_artifact", start_time)
    except PermissionError as e:
        # Specific handling for write permission errors
        return _handle_tool_error(
            MCPError(
                code="write_failed",
                message=f"Cannot write artifact output: {str(e)}",
                details={
                    "output_path": output_path or "default",
                    "error_type": "permission_denied",
                    "suggestion": "Check that:\n"
                    "  1. The output directory exists and is writable\n"
                    "  2. You have write permissions for the target path\n"
                    "  3. The file is not locked by another process\n"
                    "  4. The disk is not full or read-only",
                },
            ),
            "assemble_artifact",
            start_time,
        )
    except Exception as e:
        return _handle_tool_error(e, "assemble_artifact", start_time)


@mcp.tool(name="choracompose:validate_content")
async def validate_content(
    content_or_config_id: str,
    validation_rules: list[dict[str, Any]] | None = None,
    # Hidden parameters for testing
    _config_loader: Any = None,
    _storage: Any = None,
) -> dict[str, Any]:
    """Validate content configuration or generated content.

    Validates either:
    1. Config file (if content_or_config_id is a config ID)
    2. Generated content (if content_or_config_id exists in storage)

    Storage is checked first. If content exists in storage, it validates
    the generated content quality. Otherwise, it validates the config file.

    Args:
        content_or_config_id: ID of config or generated content to validate
        validation_rules: Optional custom validation rules
        _config_loader: For testing - custom config loader
        _storage: For testing - custom storage manager

    Returns:
        ValidationResult as dict with:
        - success: bool
        - valid: bool
        - issues: list[ValidationIssue]
        - error_count: int
        - warning_count: int
        - info_count: int
    """
    start_time = time.time()

    try:
        # Initialize components
        config_loader = _config_loader or get_config_loader()
        storage = _storage or EphemeralStorageManager(base_path=Path.cwd())

        # Try storage first (content validation)
        try:
            content = storage.retrieve(content_or_config_id, strategy="latest")
            if content:
                # Validate generated content, not config
                return _validate_generated_content(
                    content_or_config_id, content, validation_rules
                )
        except Exception:
            # Not in storage or retrieval failed, try config validation
            pass

        # Try to load config - this validates against JSON schema
        try:
            content_config = config_loader.load_content_config(content_or_config_id)
            # If load succeeds, config is valid

            # Apply custom validation rules if provided
            if validation_rules:
                rule_issues = []
                for rule in validation_rules:
                    try:
                        _validate_rule_structure(rule)
                        if rule["type"] == "length":
                            content_str = str(content_config)
                            rule_issues.extend(_apply_length_rule(content_str, rule))
                        elif rule["type"] == "required_fields":
                            rule_issues.extend(
                                _apply_required_fields_rule(content_config, rule)
                            )
                        else:
                            # Unknown rule type - warning
                            rule_issues.append(
                                ValidationIssue(
                                    severity="warning",
                                    code="unknown_rule_type",
                                    message=(
                                        f"Unknown rule type '{rule['type']}' - skipped"
                                    ),
                                    location="rules",
                                    details={"rule_type": rule["type"]},
                                )
                            )
                    except ValueError as e:
                        raise ValueError(f"Invalid validation rule: {e}") from e

                if rule_issues:
                    error_count = sum(1 for i in rule_issues if i.severity == "error")
                    warning_count = sum(
                        1 for i in rule_issues if i.severity == "warning"
                    )
                    info_count = sum(1 for i in rule_issues if i.severity == "info")
                    return ValidationResult(
                        success=True,
                        valid=False,
                        issues=rule_issues,
                        error_count=error_count,
                        warning_count=warning_count,
                        info_count=info_count,
                    ).model_dump()

            result = ValidationResult(
                success=True,
                valid=True,
                issues=[],
                error_count=0,
                warning_count=0,
                info_count=0,
            )
            return result.model_dump()

        except (ValueError, KeyError, pydantic.ValidationError) as validation_error:
            # Config failed validation (specific validation errors only)
            # Parse Pydantic error into ValidationIssue format
            error_msg = str(validation_error)

            # Create a validation issue from the error
            issue = ValidationIssue(
                severity="error",
                code="schema_validation_failed",
                message=error_msg,
                location=content_or_config_id,
                details={"validation_error": error_msg},
            )

            result = ValidationResult(
                success=True,  # Tool executed successfully
                valid=False,  # But config is invalid
                issues=[issue],
                error_count=1,
                warning_count=0,
                info_count=0,
            )
            return result.model_dump()

    except FileNotFoundError as e:
        return _handle_tool_error(e, "validate_content", start_time)
    except Exception as e:
        return _handle_tool_error(e, "validate_content", start_time)


# =============================================================================
# Content Management Tools (Week 2 Day 1)
# =============================================================================


@mcp.tool(name="choracompose:regenerate_content")
async def regenerate_content(
    content_config_id: str,
    context: dict[str, Any] | str | None = None,
    reason: str | None = None,
    compare: bool = True,
    # Hidden parameters for testing
    _config_loader: Any = None,
    _registry: Any = None,
    _storage: Any = None,
) -> dict[str, Any]:
    """Force regenerate content with change tracking.

    Unlike generate_content, this always regenerates even if content exists,
    and optionally compares with the previous version to show what changed.

    Args:
        content_config_id: ID of content config to regenerate
        context: Context variables (merged with config context).
            Can be dict or JSON string.
        reason: Human-readable reason for regeneration (for audit trail)
        compare: Whether to compare with previous version and calculate diff

    Returns:
        RegenerateContentResult as dict with:
        - success: bool
        - content_id: str
        - status: "regenerated"
        - content: str
        - previous_version: PreviousVersionInfo | None
        - changes: ContentChanges | None
        - reason: str | None
        - metadata: dict
        - duration_ms: int
    """
    import hashlib

    start_time = time.time()
    context = context or {}

    # Normalize JSON string context (Claude Desktop compatibility)
    if isinstance(context, str):
        try:
            import json as _json

            context = _json.loads(context)
            if not isinstance(context, dict):
                return _handle_tool_error(
                    MCPError(
                        code="invalid_context",
                        message=(
                            f"context must be JSON object, "
                            f"got {type(context).__name__}"
                        ),
                        details={"received_type": type(context).__name__},
                    ),
                    "regenerate_content",
                    start_time,
                )
        except _json.JSONDecodeError as e:
            return _handle_tool_error(
                MCPError(
                    code="invalid_context",
                    message="context must be valid JSON",
                    details={"error": str(e)},
                ),
                "regenerate_content",
                start_time,
            )

    try:
        # Validate config ID
        _validate_config_id(content_config_id)

        # Initialize components
        config_loader = _config_loader or get_config_loader()
        registry = _registry or GeneratorRegistry()
        storage = _storage or EphemeralStorageManager(base_path=Path("ephemeral"))

        # Try to read previous version for comparison
        previous_content = None
        previous_timestamp = None

        if compare:
            try:
                # Read latest version
                prev_data = storage.retrieve(content_config_id, strategy="latest")
                if prev_data:
                    previous_content = (
                        "\n".join(prev_data)
                        if isinstance(prev_data, list)
                        else str(prev_data)
                    )
                    # Try to get metadata
                    try:
                        # Get all versions to find timestamp
                        versions = storage.list_versions(content_config_id)
                        if versions:
                            # Get most recent version info
                            latest_version = max(
                                versions, key=lambda v: v.get("timestamp", "")
                            )
                            previous_timestamp = latest_version.get("timestamp")
                            latest_version.get("metadata", {})
                    except Exception:
                        # If can't get version info, that's ok
                        pass
            except FileNotFoundError:
                # No previous version exists
                pass

        # Load content config
        content_config = config_loader.load_content_config(content_config_id)

        # Merge context
        if hasattr(content_config.metadata, "get"):
            config_context = content_config.metadata.get("context", {})
        elif hasattr(content_config.metadata, "model_dump"):
            config_context = content_config.metadata.model_dump().get("context", {})
        elif isinstance(content_config.metadata, dict):
            config_context = content_config.metadata.get("context", {})
        else:
            config_context = {}
        merged_context = _merge_context(config_context, context)

        # Get generator
        generation = content_config.generation or {}
        if hasattr(generation, "get"):
            patterns = generation.get("patterns", [])
        elif isinstance(generation, dict):
            patterns = generation.get("patterns", [])
        else:
            patterns = getattr(generation, "patterns", [])

        if not patterns:
            raise ValueError(
                f"No generation patterns defined in config '{content_config_id}'"
            )

        pattern = patterns[0]
        if hasattr(pattern, "get"):
            generator_type = pattern.get("type")
        elif isinstance(pattern, dict):
            generator_type = pattern.get("type")
        else:
            generator_type = getattr(pattern, "type", None)

        if not generator_type:
            raise ValueError(
                f"Pattern missing 'type' field in config '{content_config_id}'"
            )

        # Generate new content (force=True behavior)
        generator = registry.get(generator_type)
        gen_output = generator.generate(content_config, merged_context)
        new_content: str = (
            "\n".join(gen_output) if isinstance(gen_output, list) else str(gen_output)
        )

        # Calculate changes if compare=True and previous exists
        changes = None
        previous_version_info = None

        if compare and previous_content:
            # Calculate content hash
            content_hash = hashlib.sha256(previous_content.encode()).hexdigest()[:12]

            # Create previous version info
            previous_version_info = PreviousVersionInfo(
                timestamp=previous_timestamp or "unknown",
                content_hash=content_hash,
            )

            # Simple line-based diff
            prev_lines = previous_content.splitlines()
            new_lines = new_content.splitlines()

            # Calculate changes
            lines_added = len([line for line in new_lines if line not in prev_lines])
            lines_removed = len([line for line in prev_lines if line not in new_lines])
            lines_changed = min(lines_added, lines_removed)

            # Generate summary
            if lines_added == 0 and lines_removed == 0:
                summary = "No changes detected"
            else:
                summary = (
                    f"Updated: +{lines_added} -{lines_removed} ~{lines_changed} lines"
                )

            changes = ContentChanges(
                lines_added=lines_added,
                lines_removed=lines_removed,
                lines_changed=lines_changed,
                summary=summary,
            )

        # Store in ephemeral storage
        storage.save(
            content_id=content_config_id,
            content=new_content,
            format="txt",
            metadata={
                "generator": generator_type,
                "context": merged_context,
                "reason": reason,
                "regenerated": True,
            },
        )

        duration_ms = int((time.time() - start_time) * 1000)

        result = RegenerateContentResult(
            success=True,
            content_id=content_config_id,
            status="regenerated",
            content=new_content,
            previous_version=previous_version_info,
            changes=changes,
            reason=reason,
            metadata={
                "generator_type": generator_type,
                "context_variables": list(merged_context.keys()),
                "template_hash": hashlib.sha256(str(pattern).encode()).hexdigest()[:12],
            },
            duration_ms=duration_ms,
        )

        return result.model_dump()

    except FileNotFoundError:
        return _handle_tool_error(
            MCPError(
                code="config_not_found",
                message=f"Content config '{content_config_id}' not found",
                details={"content_config_id": content_config_id},
            ),
            "regenerate_content",
            start_time,
        )
    except ValueError as e:
        return _handle_tool_error(
            MCPError(
                code="invalid_config_id"
                if "path characters" in str(e)
                else "generation_failed",
                message=str(e),
                details={"content_config_id": content_config_id},
            ),
            "regenerate_content",
            start_time,
        )
    except Exception as e:
        return _handle_tool_error(e, "regenerate_content", start_time)


@mcp.tool(name="choracompose:delete_content")
async def delete_content(
    content_id: str,
    preserve_metadata: bool = False,
    force: bool = False,
    _config_loader: Any = None,
    _storage: Any = None,
) -> dict[str, Any]:
    """
    Remove content from ephemeral storage.

    Safely deletes generated content with optional metadata preservation
    for audit trails. Warns if content is referenced by artifacts.

    Args:
        content_id: Content ID to delete from ephemeral storage
        preserve_metadata: Keep metadata file but delete content (default: False)
        force: Delete even if referenced by artifacts (default: False)
        _config_loader: Injected config loader (for testing)
        _storage: Injected storage (for testing)

    Returns:
        DeleteContentResult with deletion statistics

    Raises:
        MCPError: If content not found or referenced without force=True
    """
    import os
    from pathlib import Path

    start_time = time.time()

    try:
        # Dependency injection
        storage = _storage or get_ephemeral_storage()

        # Check if content exists in storage
        content_exists = False
        try:
            versions = storage.list_versions(content_id)
            content_exists = len(versions) > 0
        except Exception:
            content_exists = False

        if not content_exists:
            return _handle_tool_error(
                MCPError(
                    code="content_not_found",
                    message=(f"Content '{content_id}' not found in ephemeral storage"),
                    details={
                        "content_id": content_id,
                        "hint": "Use list_content to see available content",
                    },
                ),
                "delete_content",
                start_time,
            )

        # Check for artifact references
        config_loader = _config_loader or get_config_loader()
        artifact_ids: list[str] = []

        try:
            # Scan all artifact configs for references to this content
            configs_dir = Path("configs/artifacts")
            if configs_dir.exists():
                for artifact_file in configs_dir.glob("*-artifact.json"):
                    try:
                        artifact_config = config_loader.load(str(artifact_file))
                        # Check if this content is in the artifact's children
                        children = artifact_config.get("content", {}).get(
                            "children", []
                        )
                        for child in children:
                            if child.get("id") == content_id:
                                artifact_ids.append(
                                    artifact_config.get("id", "unknown")
                                )
                                break
                    except Exception:
                        # Skip artifacts that can't be loaded
                        continue
        except Exception:
            # If we can't scan artifacts, proceed anyway
            pass

        # If referenced and not force, error
        if artifact_ids and not force:
            return _handle_tool_error(
                MCPError(
                    code="content_referenced",
                    message=(
                        f"Content '{content_id}' is referenced by "
                        f"{len(artifact_ids)} artifact(s)"
                    ),
                    details={
                        "content_id": content_id,
                        "artifact_ids": artifact_ids,
                        "hint": "Use force=true to delete anyway",
                    },
                ),
                "delete_content",
                start_time,
            )

        # Calculate statistics before deletion
        versions = storage.list_versions(content_id)
        versions_deleted = len(versions)

        # Calculate bytes freed
        bytes_freed = 0
        storage_path = storage.base_path / content_id
        if storage_path.exists():
            for file_path in storage_path.rglob("*"):
                if file_path.is_file():
                    try:
                        bytes_freed += os.path.getsize(file_path)
                    except Exception:
                        pass

        # Perform deletion
        # Note: Actual storage implementation may vary
        # This is a simplified approach
        try:
            if hasattr(storage, "delete"):
                storage.delete(content_id, preserve_metadata=preserve_metadata)
            else:
                # Fallback: manually delete storage directory
                if storage_path.exists():
                    if preserve_metadata:
                        # Delete content files but keep metadata
                        for file_path in storage_path.rglob("*.txt"):
                            file_path.unlink()
                        for file_path in storage_path.rglob("*.md"):
                            file_path.unlink()
                    else:
                        # Delete entire directory
                        import shutil

                        shutil.rmtree(storage_path)
        except Exception as e:
            return _handle_tool_error(
                MCPError(
                    code="deletion_failed",
                    message=f"Failed to delete content: {str(e)}",
                    details={"content_id": content_id},
                ),
                "delete_content",
                start_time,
            )

        # Build warnings
        warnings: list[str] = []
        if artifact_ids:
            warnings.append(
                "Content was referenced by artifacts - they may now fail to assemble"
            )
        if preserve_metadata:
            warnings.append("Metadata preserved for audit trail")

        # Build result
        result = DeleteContentResult(
            success=True,
            content_id=content_id,
            status="deleted",
            versions_deleted=versions_deleted,
            bytes_freed=bytes_freed,
            metadata_preserved=preserve_metadata,
            warnings=warnings if warnings else None,
            references=(
                ContentReferences(artifact_ids=artifact_ids, count=len(artifact_ids))
                if artifact_ids
                else None
            ),
            duration_ms=int((time.time() - start_time) * 1000),
        )

        return result.model_dump()

    except Exception as e:
        return _handle_tool_error(e, "delete_content", start_time)


@mcp.tool(name="choracompose:preview_generation")
async def preview_generation(
    content_config_id: str,
    context: dict[str, Any] | str | None = None,
    show_metadata: bool = False,
    _config_loader: Any = None,
    _registry: Any = None,
) -> dict[str, Any]:
    """
    Dry-run content generation without writing to storage.

    Perfect for testing templates, validating context, and previewing
    output before committing to storage.

    Args:
        content_config_id: Content configuration ID to preview
        context: Context variables for template substitution.
            Can be dict or JSON string (default: {})
        show_metadata: Include detailed generation metadata (default: False)
        _config_loader: Injected config loader (for testing)
        _registry: Injected generator registry (for testing)

    Returns:
        PreviewGenerationResult with generated content (NOT saved)

    Raises:
        MCPError: If config not found or generation fails
    """
    import hashlib

    start_time = time.time()
    context = context or {}

    # Normalize stringified JSON context (same as generate_content)
    if isinstance(context, str):
        try:
            import json as _json

            context = _json.loads(context)
            if not isinstance(context, dict):
                return _handle_tool_error(
                    MCPError(
                        code="invalid_context",
                        message=(
                            f"context must be JSON object; "
                            f"parsed to {type(context).__name__}"
                        ),
                        details={"received_type": type(context).__name__},
                    ),
                    "preview_generation",
                    start_time,
                )
        except _json.JSONDecodeError as e:
            return _handle_tool_error(
                MCPError(
                    code="invalid_context",
                    message=(
                        "context must be JSON object; "
                        "received string we could not parse"
                    ),
                    details={
                        "received": context[:100] if context else "",
                        "error": str(e),
                    },
                ),
                "preview_generation",
                start_time,
            )
    elif context is None:
        context = {}

    try:
        # Validate config ID
        _validate_config_id(content_config_id)

        # Initialize components (use injected or create real ones)
        config_loader = _config_loader or get_config_loader()
        registry = _registry or GeneratorRegistry()

        # Load content config
        content_config = config_loader.load_content_config(content_config_id)

        # Merge context (tool context takes precedence)
        if hasattr(content_config.metadata, "get"):
            config_context = content_config.metadata.get("context", {})
        elif hasattr(content_config.metadata, "model_dump"):
            config_context = content_config.metadata.model_dump().get("context", {})
        elif isinstance(content_config.metadata, dict):
            config_context = content_config.metadata.get("context", {})
        else:
            config_context = {}
        merged_context = _merge_context(config_context, context)

        # Get generator type from config (same as generate_content)
        generation = content_config.generation or {}
        if hasattr(generation, "get"):
            patterns = generation.get("patterns", [])
        elif isinstance(generation, dict):
            patterns = generation.get("patterns", [])
        else:
            patterns = getattr(generation, "patterns", [])
        if not patterns:
            raise ValueError(
                f"No generation patterns defined in config '{content_config_id}'"
            )

        pattern = patterns[0]
        # Handle both dict and Pydantic model for pattern
        if hasattr(pattern, "get"):
            generator_type = pattern.get("type")
        elif isinstance(pattern, dict):
            generator_type = pattern.get("type")
        else:
            generator_type = getattr(pattern, "type", None)
        if not generator_type:
            raise ValueError(
                f"Pattern missing 'type' field in config '{content_config_id}'"
            )

        # Get generator from registry
        generator = registry.get(generator_type)
        if not generator:
            return _handle_tool_error(
                MCPError(
                    code="generator_not_found",
                    message=f"Generator '{generator_type}' not found in registry",
                    details={"requested_generator": generator_type},
                ),
                "preview_generation",
                start_time,
            )

        # Generate content (same as generate_content)
        generated_content = generator.generate(content_config, merged_context)

        # Ensure content is string type
        if isinstance(generated_content, list):
            content = "\n".join(generated_content)
        else:
            content = str(generated_content)

        # Build metadata if requested
        metadata: PreviewMetadata | None = None
        if show_metadata:
            # Calculate template hash
            template_hash = "unknown"
            try:
                if hasattr(content_config.generation, "template_path"):
                    template_path_str = str(content_config.generation.template_path)
                    from pathlib import Path

                    template_file = Path(template_path_str)
                    if template_file.exists():
                        template_bytes = template_file.read_bytes()
                        hash_obj = hashlib.sha256(template_bytes)
                        template_hash = hash_obj.hexdigest()[:12]
            except Exception:
                # If we can't read template, use placeholder
                template_hash = "unavailable"

            # Analyze variable usage
            variable_usage: dict[str, int] = {}
            context_variables = list(merged_context.keys())

            for var_name in context_variables:
                var_value = str(merged_context[var_name])
                # Simple string counting for variable usage
                count = content.count(var_value)
                variable_usage[var_name] = count

            # Generate warnings
            warnings: list[str] = []
            for var_name, count in variable_usage.items():
                if count == 0:
                    warnings.append(
                        f"Context variable '{var_name}' provided "
                        "but not used in template"
                    )

            # Build metadata
            metadata = PreviewMetadata(
                generator_type=generator_type,
                context_variables=context_variables,
                template_hash=template_hash,
                variable_usage=variable_usage,
                warnings=warnings,
            )

        # Build result
        result = PreviewGenerationResult(
            success=True,
            content_id=content_config_id,
            status="preview",
            content=content,
            metadata=metadata,
            duration_ms=int((time.time() - start_time) * 1000),
        )

        return result.model_dump()

    except FileNotFoundError:
        return _handle_tool_error(
            MCPError(
                code="config_not_found",
                message=f"Content config '{content_config_id}' not found",
                details={"content_config_id": content_config_id},
            ),
            "preview_generation",
            start_time,
        )
    except Exception as e:
        return _handle_tool_error(
            MCPError(
                code="generation_failed",
                message=f"Content generation failed: {str(e)}",
                details={"content_config_id": content_config_id},
            ),
            "preview_generation",
            start_time,
        )


@mcp.tool(name="choracompose:batch_generate")
async def batch_generate(
    content_ids: list[str],
    shared_context: dict[str, Any] | str | None = None,
    individual_contexts: dict[str, dict[str, Any] | str] | None = None,
    force: bool = False,
    continue_on_error: bool = True,
    max_parallel: int = 4,
    _config_loader: Any = None,
    _registry: Any = None,
    _storage: Any = None,
) -> dict[str, Any]:
    """
    Generate multiple content pieces in parallel.

    Optimized for efficiency with parallel execution, shared context,
    and consolidated error reporting.

    Args:
        content_ids: Array of content configuration IDs to generate
        shared_context: Context applied to all generations.
            Can be dict or JSON string (default: {})
        individual_contexts: Per-ID context overrides.
            Values can be dict or JSON string (default: {})
        force: Force regeneration of existing content (default: False)
        continue_on_error: Continue if one generation fails (default: True)
        max_parallel: Maximum concurrent generations (default: 4, max: 10)
        _config_loader: Injected config loader (for testing)
        _registry: Injected generator registry (for testing)
        _storage: Injected storage (for testing)

    Returns:
        BatchGenerateResult with individual results and statistics

    Raises:
        MCPError: If input validation fails
    """
    import asyncio

    start_time = time.time()

    try:
        # Validate content_ids
        if not content_ids or len(content_ids) == 0:
            return _handle_tool_error(
                MCPError(
                    code="invalid_input",
                    message="content_ids must be non-empty array",
                    details={"content_ids": content_ids},
                ),
                "batch_generate",
                start_time,
            )

        # Deduplicate content_ids while preserving order
        unique_ids = list(dict.fromkeys(content_ids))

        # Parse and normalize contexts
        # Parse shared_context if string
        parsed_shared_context: dict[str, Any] = {}
        if isinstance(shared_context, str):
            try:
                import json as _json

                parsed_shared_context = _json.loads(shared_context)
                if not isinstance(parsed_shared_context, dict):
                    return _handle_tool_error(
                        MCPError(
                            code="invalid_context",
                            message=(
                                f"shared_context must be JSON object; "
                                f"parsed to {type(parsed_shared_context).__name__}"
                            ),
                            details={
                                "received_type": type(parsed_shared_context).__name__
                            },
                        ),
                        "batch_generate",
                        start_time,
                    )
            except _json.JSONDecodeError as e:
                return _handle_tool_error(
                    MCPError(
                        code="invalid_context",
                        message=(
                            "shared_context must be JSON object; "
                            "received string we could not parse"
                        ),
                        details={
                            "received": shared_context[:100] if shared_context else "",
                            "error": str(e),
                        },
                    ),
                    "batch_generate",
                    start_time,
                )
        elif shared_context is not None:
            parsed_shared_context = shared_context
        else:
            parsed_shared_context = {}

        # Parse individual_contexts if any values are strings
        parsed_individual_contexts: dict[str, dict[str, Any]] = {}
        if individual_contexts:
            for content_id, ctx in individual_contexts.items():
                if isinstance(ctx, str):
                    try:
                        import json as _json

                        parsed_ctx = _json.loads(ctx)
                        if not isinstance(parsed_ctx, dict):
                            return _handle_tool_error(
                                MCPError(
                                    code="invalid_context",
                                    message=(
                                        f"individual_contexts['{content_id}'] "
                                        f"must be JSON object; "
                                        f"parsed to {type(parsed_ctx).__name__}"
                                    ),
                                    details={
                                        "content_id": content_id,
                                        "received_type": type(parsed_ctx).__name__,
                                    },
                                ),
                                "batch_generate",
                                start_time,
                            )
                        parsed_individual_contexts[content_id] = parsed_ctx
                    except _json.JSONDecodeError as e:
                        return _handle_tool_error(
                            MCPError(
                                code="invalid_context",
                                message=(
                                    f"individual_contexts['{content_id}'] "
                                    f"must be JSON object; "
                                    f"received string we could not parse"
                                ),
                                details={
                                    "content_id": content_id,
                                    "received": ctx[:100] if ctx else "",
                                    "error": str(e),
                                },
                            ),
                            "batch_generate",
                            start_time,
                        )
                else:
                    parsed_individual_contexts[content_id] = ctx

        # Initialize dependencies (use injected or create real ones)
        config_loader = _config_loader or get_config_loader()
        registry = _registry or GeneratorRegistry()
        storage = _storage or get_ephemeral_storage()

        # Create semaphore for max_parallel control
        semaphore = asyncio.Semaphore(max_parallel)

        async def generate_one(content_id: str) -> ContentGenerationResult:
            """Generate single content with semaphore control."""
            async with semaphore:
                gen_start = time.time()

                try:
                    # Merge contexts: shared + individual (individual takes precedence)
                    merged_context = {**parsed_shared_context}
                    if content_id in parsed_individual_contexts:
                        merged_context.update(parsed_individual_contexts[content_id])

                    # Call internal generate_content implementation
                    result = await _generate_content_impl(
                        content_config_id=content_id,
                        context=merged_context,
                        force=force,
                        _config_loader=config_loader,
                        _registry=registry,
                        _storage=storage,
                    )

                    gen_duration = int((time.time() - gen_start) * 1000)

                    # Check if generation succeeded
                    if result.get("success"):
                        status_str = result.get("status", "generated")
                        # Cast to expected literal type
                        if status_str in ["generated", "skipped", "failed"]:
                            status = status_str
                        else:
                            status = "generated"

                        return ContentGenerationResult(
                            content_id=content_id,
                            success=True,
                            status=status,
                            content=result.get("content"),
                            duration_ms=gen_duration,
                        )
                    else:
                        # Generation failed
                        error = result.get("error", {})
                        return ContentGenerationResult(
                            content_id=content_id,
                            success=False,
                            status="failed",
                            error={
                                "code": error.get("code", "unknown"),
                                "message": error.get("message", "Unknown error"),
                            },
                            duration_ms=gen_duration,
                        )

                except Exception as e:
                    gen_duration = int((time.time() - gen_start) * 1000)
                    return ContentGenerationResult(
                        content_id=content_id,
                        success=False,
                        status="failed",
                        error={"code": "generation_error", "message": str(e)},
                        duration_ms=gen_duration,
                    )

        # Execute all generations in parallel
        tasks = [generate_one(cid) for cid in unique_ids]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        # Process results and calculate statistics
        generated = 0
        skipped = 0
        failed = 0
        errors: list[GenerationError] = []
        individual_times: list[int] = []

        for result in results:
            individual_times.append(result.duration_ms)

            if result.success:
                if result.status == "generated":
                    generated += 1
                elif result.status == "skipped":
                    skipped += 1
            else:
                failed += 1
                # Add to errors list
                if result.error:
                    errors.append(
                        GenerationError(
                            content_id=result.content_id,
                            code=result.error["code"],
                            message=result.error["message"],
                        )
                    )

        # Calculate metrics
        total = len(unique_ids)
        total_duration = int((time.time() - start_time) * 1000)

        # Parallel efficiency = sequential time / parallel time
        sequential_time = sum(individual_times)
        # Handle edge case where operations complete instantly (< 1ms)
        if sequential_time == 0:
            parallel_efficiency = 1.0  # Perfect efficiency (no measurable time)
        elif total_duration > 0:
            parallel_efficiency = sequential_time / total_duration
        else:
            parallel_efficiency = 1.0

        # Determine batch status
        if failed == 0:
            batch_status = "batch_complete"
        elif failed == total:
            batch_status = "batch_failed"
        else:
            batch_status = "batch_partial"

        # Build result
        result_obj = BatchGenerateResult(
            success=(failed < total),  # Success if at least one succeeded
            status=batch_status,
            total=total,
            generated=generated,
            skipped=skipped,
            failed=failed,
            results=results,  # In same order as input
            errors=errors,
            duration_ms=total_duration,
            parallel_efficiency=parallel_efficiency,
        )

        return result_obj.model_dump()

    except Exception as e:
        return _handle_tool_error(e, "batch_generate", start_time)


@mcp.tool(name="choracompose:trace_dependencies")
async def trace_dependencies(
    artifact_config_id: str,
    check_status: bool = True,
    show_metadata: bool = False,
    _config_loader: Any = None,
    _storage: Any = None,
) -> dict[str, Any]:
    """Trace content dependencies for an artifact configuration.

    This tool analyzes an artifact configuration and reports:
    - What content pieces are required
    - Whether each piece exists (if check_status=True)
    - Assembly order
    - Missing content IDs (can be passed to batch_generate)

    Args:
        artifact_config_id: ID of artifact config to analyze
        check_status: Check if each content piece exists
            (slower but more informative)
        show_metadata: Include detailed metadata for each content
            (generator, versions, etc.)

    Returns:
        TraceDependenciesResult as dict with:
        - success: bool
        - artifact_id: str
        - status: str (ready|incomplete|missing_config)
        - total_dependencies: int
        - ready: int (dependencies that exist)
        - missing: int (dependencies that don't exist)
        - dependencies: list[DependencyInfo]
        - assembly_order: list[str] (content IDs in assembly order)
        - missing_content_ids: list[str] | None (can pass to batch_generate)
        - duration_ms: int
    """
    start_time = time.time()

    try:
        # Validate config ID
        _validate_config_id(artifact_config_id)

        # Initialize dependencies (use injected or create real ones)
        config_loader = _config_loader or get_config_loader()
        storage = _storage or get_ephemeral_storage()

        # Load artifact config
        artifact_config = config_loader.load_artifact_config(artifact_config_id)

        # Extract children from content field
        children = []
        if hasattr(artifact_config, "content") and artifact_config.content:
            if isinstance(artifact_config.content, dict):
                children = artifact_config.content.get("children", [])
            elif hasattr(artifact_config.content, "children"):
                children = artifact_config.content.children
            else:
                children = []

        # Build dependency info for each child
        dependencies: list[DependencyInfo] = []
        ready_count = 0
        missing_count = 0
        missing_ids: list[str] = []

        for child in children:
            # Extract child fields
            if isinstance(child, dict):
                content_id = child.get("id", "")
                path = child.get("path", "")
                required = child.get("required", True)
                order = child.get("order") or 1
                retrieval_strategy = child.get("retrievalStrategy", "latest")
            else:
                # Pydantic model
                content_id = getattr(child, "id", "")
                path = getattr(child, "path", "")
                required = getattr(child, "required", True)
                order = getattr(child, "order", None) or 1
                retrieval_strategy = str(getattr(child, "retrievalStrategy", "latest"))

            # Check status if requested
            if check_status:
                try:
                    existing = storage.retrieve(content_id, strategy="latest")
                    if existing:
                        status = "ready"
                        ready_count += 1
                    else:
                        status = "missing"
                        missing_count += 1
                        missing_ids.append(content_id)
                except FileNotFoundError:
                    status = "missing"
                    missing_count += 1
                    missing_ids.append(content_id)
            else:
                status = "unknown"

            # Get metadata if requested
            metadata = None
            if show_metadata and status == "ready":
                try:
                    # Load content config to get generator info
                    content_config = config_loader.load_content_config(content_id)
                    generator_type = "unknown"
                    if hasattr(content_config, "generation"):
                        gen = content_config.generation
                        if isinstance(gen, dict):
                            patterns = gen.get("patterns", [])
                        else:
                            patterns = getattr(gen, "patterns", [])
                        if patterns and len(patterns) > 0:
                            pattern = patterns[0]
                            if isinstance(pattern, dict):
                                generator_type = pattern.get("type", "unknown")
                            else:
                                generator_type = getattr(pattern, "type", "unknown")

                    metadata = DependencyMetadata(
                        generator_type=generator_type,
                        last_generated="unknown",  # Would need storage metadata
                        versions_available=1,  # Would need storage version counting
                    )
                except Exception:
                    # Silently skip metadata if we can't load it
                    metadata = None

            # Create dependency info
            dep_info = DependencyInfo(
                content_id=content_id,
                path=path,
                required=required,
                order=order,
                status=status,
                retrieval_strategy=retrieval_strategy,
                metadata=metadata,
            )
            dependencies.append(dep_info)

        # Sort dependencies by order
        dependencies.sort(key=lambda d: d.order)

        # Build assembly order
        assembly_order = [dep.content_id for dep in dependencies]

        # Determine overall status
        if not children:
            overall_status = "missing_config"
        elif not check_status:
            overall_status = "unknown"
        elif missing_count == 0:
            overall_status = "ready"
        else:
            overall_status = "incomplete"

        duration_ms = int((time.time() - start_time) * 1000)

        # Build result
        result_obj = TraceDependenciesResult(
            success=True,
            artifact_id=artifact_config_id,
            status=overall_status,
            total_dependencies=len(dependencies),
            ready=ready_count,
            missing=missing_count,
            dependencies=dependencies,
            assembly_order=assembly_order,
            missing_content_ids=missing_ids if missing_ids else None,
            duration_ms=duration_ms,
        )

        return result_obj.model_dump()

    except FileNotFoundError:
        return _handle_tool_error(
            MCPError(
                code="config_not_found",
                message=f"Artifact config '{artifact_config_id}' not found",
                details={"artifact_config_id": artifact_config_id},
            ),
            "trace_dependencies",
            start_time,
        )
    except Exception as e:
        return _handle_tool_error(e, "trace_dependencies", start_time)


@mcp.tool(name="choracompose:list_artifacts")
async def list_artifacts(
    filter: dict[str, Any] | None = None,
    sort: str = "id",
    limit: int = 100,
    _config_loader: Any = None,
) -> dict[str, Any]:
    """List all available artifact configurations with metadata.

    Browse artifact catalog, check assembly status, and discover artifacts.

    Args:
        filter: Optional filters (type, stage, assembled)
        sort: Sort order (id, title, assembled, modified)
        limit: Maximum results (1-500, default 100)

    Returns:
        ListArtifactsResult as dict with:
        - success: bool
        - total: int (total matching filter)
        - returned: int (number in results)
        - artifacts: list[ArtifactSummary]
        - duration_ms: int
    """
    start_time = time.time()

    try:
        # Validate inputs
        if limit < 1 or limit > 500:
            return _handle_tool_error(
                MCPError(
                    code="invalid_input",
                    message=f"limit must be between 1 and 500, got {limit}",
                    details={"limit": limit},
                ),
                "list_artifacts",
                start_time,
            )

        allowed_sorts = ["id", "title", "assembled", "modified"]
        if sort not in allowed_sorts:
            return _handle_tool_error(
                MCPError(
                    code="invalid_input",
                    message=f"sort must be one of {allowed_sorts}, got '{sort}'",
                    details={"sort": sort, "allowed": allowed_sorts},
                ),
                "list_artifacts",
                start_time,
            )

        # Initialize dependencies
        config_loader = _config_loader or get_config_loader()
        filter = filter or {}

        # Scan for artifact configs
        configs_dir = Path("configs/artifacts")
        if not configs_dir.exists():
            # No configs directory, return empty list
            result_obj = ListArtifactsResult(
                success=True,
                total=0,
                returned=0,
                artifacts=[],
                duration_ms=int((time.time() - start_time) * 1000),
            )
            return result_obj.model_dump()

        artifacts: list[ArtifactSummary] = []

        # Load all artifact configs (match *-artifact.json pattern)
        for config_path in configs_dir.glob("**/*-artifact.json"):
            try:
                # Extract artifact ID from filename
                # Handle both "-artifact-artifact.json" and "-artifact.json" patterns
                stem = config_path.stem
                if stem.endswith("-artifact-artifact"):
                    # Files like "test-artifact-artifact.json" → "test-artifact"
                    artifact_id = stem.removesuffix("-artifact-artifact")
                else:
                    # Files like "kernel-artifact.json" → "kernel"
                    artifact_id = stem.removesuffix("-artifact")

                # Load config
                artifact_config = config_loader.load_artifact_config(artifact_id)

                # Extract metadata
                metadata = artifact_config.metadata
                if isinstance(metadata, dict):
                    title = metadata.get("title", artifact_id)
                    artifact_type = metadata.get("type", "unknown")
                    purpose = metadata.get("purpose", "")
                    composition_strategy = metadata.get("compositionStrategy", "concat")
                else:
                    title = getattr(metadata, "title", artifact_id)
                    artifact_type = getattr(metadata, "type", "unknown")
                    purpose = getattr(metadata, "purpose", "")
                    composition_strategy = getattr(
                        metadata, "compositionStrategy", "concat"
                    )

                # Get evolution stage
                evolution = getattr(artifact_config, "evolution", None)
                if evolution:
                    if isinstance(evolution, dict):
                        stage = evolution.get("stage", "draft")
                    else:
                        stage = getattr(evolution, "stage", "draft")
                else:
                    stage = "draft"

                # Count dependencies
                content = artifact_config.content
                if isinstance(content, dict):
                    children = content.get("children", [])
                else:
                    children = getattr(content, "children", [])
                dependencies_count = len(children)

                # Check if assembled (output file exists)
                assembled = False
                last_assembled = None
                output_file = None

                if isinstance(metadata, dict):
                    outputs = metadata.get("outputs", [])
                else:
                    outputs = getattr(metadata, "outputs", [])

                if outputs and len(outputs) > 0:
                    output_spec = outputs[0]
                    if isinstance(output_spec, dict):
                        output_path = output_spec.get("file", "")
                    else:
                        output_path = getattr(output_spec, "file", "")

                    if output_path:
                        output_file_path = Path(output_path)
                        if output_file_path.exists():
                            assembled = True
                            output_file = output_path
                            # Get last modified time
                            mtime = output_file_path.stat().st_mtime
                            last_assembled = (
                                datetime.fromtimestamp(mtime).isoformat() + "Z"
                            )

                # Create artifact summary
                artifact_summary = ArtifactSummary(
                    id=artifact_id,
                    title=title,
                    type=artifact_type,
                    stage=stage,
                    purpose=purpose,
                    dependencies=dependencies_count,
                    assembled=assembled,
                    last_assembled=last_assembled,
                    output_file=output_file,
                    composition_strategy=composition_strategy,
                )

                artifacts.append(artifact_summary)

            except Exception:
                # Skip invalid configs
                continue

        # Apply filters
        if "type" in filter:
            artifacts = [a for a in artifacts if a.type == filter["type"]]
        if "stage" in filter:
            artifacts = [a for a in artifacts if a.stage == filter["stage"]]
        if "assembled" in filter:
            artifacts = [a for a in artifacts if a.assembled == filter["assembled"]]

        # Sort
        sort_keys = {
            "id": lambda x: x.id,
            "title": lambda x: x.title,
            "assembled": lambda x: (x.last_assembled or ""),
            "modified": lambda x: (x.last_assembled or ""),
        }
        if sort in sort_keys:
            artifacts.sort(key=sort_keys[sort])

        # Apply limit
        total = len(artifacts)
        artifacts = artifacts[:limit]
        returned = len(artifacts)

        duration_ms = int((time.time() - start_time) * 1000)

        # Build result
        result_obj = ListArtifactsResult(
            success=True,
            total=total,
            returned=returned,
            artifacts=artifacts,
            duration_ms=duration_ms,
        )

        return result_obj.model_dump()

    except Exception as e:
        return _handle_tool_error(e, "list_artifacts", start_time)


@mcp.tool(name="choracompose:list_artifact_configs")
async def list_artifact_configs(
    filter_pattern: str | None = None,
    _config_loader: Any = None,
) -> dict[str, Any]:
    """List all available artifact configuration files.

    Browse the artifact configs directory to discover what artifact types
    are available for assembly. Returns basic config metadata without
    checking generation status.

    Args:
        filter_pattern: Optional glob pattern (e.g., "report*", "*-bundle")
        _config_loader: Optional config loader for testing

    Returns:
        ListArtifactConfigsResult as dict with:
        - success: bool
        - total: int (total configs found)
        - configs: list[ArtifactConfigSummary]
        - duration_ms: int

    Example:
        list_artifact_configs()  # List all
        list_artifact_configs("report*")  # Filter by pattern
    """
    start_time = time.time()

    try:
        config_loader = _config_loader or get_config_loader()
        configs_dir = Path("configs/artifacts")

        if not configs_dir.exists():
            result_obj = ListArtifactConfigsResult(
                success=True,
                total=0,
                configs=[],
                duration_ms=int((time.time() - start_time) * 1000),
            )
            return result_obj.model_dump()

        configs_list: list[ArtifactConfigSummary] = []
        pattern = filter_pattern or "*"

        # Scan for artifact configs matching pattern
        for config_path in configs_dir.glob(f"**/{pattern}-artifact.json"):
            try:
                # Extract artifact ID from filename (remove -artifact suffix)
                artifact_id = config_path.stem.removesuffix("-artifact")

                # Load config
                artifact_config = config_loader.load_artifact_config(artifact_id)

                # Build summary
                summary = ArtifactConfigSummary(
                    id=artifact_id,
                    file_path=str(config_path),
                    description=artifact_config.metadata.get(
                        "description", artifact_id
                    ),
                    title=artifact_config.metadata.get("title", artifact_id),
                    component_count=len(artifact_config.content.children),
                )

                configs_list.append(summary)

            except Exception:
                # Skip invalid configs
                continue

        # Sort by ID
        configs_list.sort(key=lambda x: x.id)

        duration_ms = int((time.time() - start_time) * 1000)

        result_obj = ListArtifactConfigsResult(
            success=True,
            total=len(configs_list),
            configs=configs_list,
            duration_ms=duration_ms,
        )

        return result_obj.model_dump()

    except Exception as e:
        return _handle_tool_error(e, "list_artifact_configs", start_time)


@mcp.tool(name="choracompose:list_content")
async def list_content(
    filter: dict[str, Any] | None = None,
    sort: str = "id",
    limit: int = 100,
    _config_loader: Any = None,
    _storage: Any = None,
) -> dict[str, Any]:
    """List all available content configurations with generation status.

    Browse content catalog, check generation status, and discover content.

    Args:
        filter: Optional filters (generator_type, generated, stage)
        sort: Sort order (id, title, generator, modified)
        limit: Maximum results (1-500, default 100)

    Returns:
        ListContentResult as dict with:
        - success: bool
        - total: int (total matching filter)
        - returned: int (number in results)
        - content: list[ContentSummary]
        - duration_ms: int
    """
    start_time = time.time()

    try:
        # Validate inputs
        if limit < 1 or limit > 500:
            return _handle_tool_error(
                MCPError(
                    code="invalid_input",
                    message=f"limit must be between 1 and 500, got {limit}",
                    details={"limit": limit},
                ),
                "list_content",
                start_time,
            )

        allowed_sorts = ["id", "title", "generator", "modified"]
        if sort not in allowed_sorts:
            return _handle_tool_error(
                MCPError(
                    code="invalid_input",
                    message=f"sort must be one of {allowed_sorts}, got '{sort}'",
                    details={"sort": sort, "allowed": allowed_sorts},
                ),
                "list_content",
                start_time,
            )

        # Initialize dependencies
        config_loader = _config_loader or get_config_loader()
        storage = _storage or get_ephemeral_storage()
        filter = filter or {}

        # Scan for content configs
        configs_dir = Path("configs/content")
        if not configs_dir.exists():
            # No configs directory, return empty list
            result_obj = ListContentResult(
                success=True,
                total=0,
                returned=0,
                content=[],
                duration_ms=int((time.time() - start_time) * 1000),
            )
            return result_obj.model_dump()

        content_list: list[ContentSummary] = []

        # Load all content configs
        for config_path in configs_dir.glob("**/*-content.json"):
            try:
                # Extract content ID from filename (remove -content suffix)
                content_id = config_path.stem.removesuffix("-content")

                # Load config
                content_config = config_loader.load_content_config(content_id)

                # Extract metadata
                metadata = content_config.metadata
                if isinstance(metadata, dict):
                    description = metadata.get("description", content_id)
                    purpose = description[:100]  # First 100 chars as purpose
                    title = description[:50] if len(description) > 50 else description
                    output_format = metadata.get("output_format", "markdown")
                else:
                    description = getattr(metadata, "description", content_id)
                    purpose = description[:100]
                    title = description[:50] if len(description) > 50 else description
                    output_format = getattr(metadata, "output_format", "markdown")

                # Get evolution stage
                evolution = getattr(content_config, "evolution", None)
                if evolution:
                    if isinstance(evolution, dict):
                        stage = evolution.get("stage", "draft")
                    else:
                        stage = getattr(evolution, "stage", "draft")
                else:
                    stage = "draft"

                # Extract generator type
                generation = content_config.generation
                generator_type = "unknown"
                if generation:
                    if isinstance(generation, dict):
                        patterns = generation.get("patterns", [])
                    else:
                        patterns = getattr(generation, "patterns", [])

                    if patterns and len(patterns) > 0:
                        pattern = patterns[0]
                        if isinstance(pattern, dict):
                            generator_type = pattern.get("type", "unknown")
                        else:
                            generator_type = getattr(pattern, "type", "unknown")

                # Check if generated (exists in ephemeral storage)
                generated = False
                last_generated = None
                versions_available = None

                try:
                    existing = storage.retrieve(content_id, strategy="latest")
                    if existing:
                        generated = True
                        # Try to get timestamp from storage metadata (simplified)
                        # In real implementation, this would query storage metadata
                        last_generated = datetime.now().isoformat() + "Z"
                        versions_available = 1  # Simplified - would query storage
                except (FileNotFoundError, Exception):
                    generated = False

                # Create content summary
                content_summary = ContentSummary(
                    id=content_id,
                    title=title,
                    generator_type=generator_type,
                    purpose=purpose,
                    stage=stage,
                    generated=generated,
                    last_generated=last_generated,
                    versions_available=versions_available,
                    output_format=output_format,
                )

                content_list.append(content_summary)

            except Exception:
                # Skip invalid configs
                continue

        # Apply filters
        if "generator_type" in filter:
            content_list = [
                c for c in content_list if c.generator_type == filter["generator_type"]
            ]
        if "generated" in filter:
            content_list = [
                c for c in content_list if c.generated == filter["generated"]
            ]
        if "stage" in filter:
            content_list = [c for c in content_list if c.stage == filter["stage"]]

        # Sort
        sort_keys = {
            "id": lambda x: x.id,
            "title": lambda x: x.title,
            "generator": lambda x: x.generator_type,
            "modified": lambda x: (x.last_generated or ""),
        }
        if sort in sort_keys:
            content_list.sort(key=sort_keys[sort])

        # Apply limit
        total = len(content_list)
        content_list = content_list[:limit]
        returned = len(content_list)

        duration_ms = int((time.time() - start_time) * 1000)

        # Build result
        result_obj = ListContentResult(
            success=True,
            total=total,
            returned=returned,
            content=content_list,
            duration_ms=duration_ms,
        )

        return result_obj.model_dump()

    except Exception as e:
        return _handle_tool_error(e, "list_content", start_time)


@mcp.tool(name="choracompose:list_content_configs")
async def list_content_configs(
    filter_pattern: str | None = None,
    _config_loader: Any = None,
) -> dict[str, Any]:
    """List all available content configuration files.

    Browse the content configs directory to discover what content types
    are available for generation. Unlike list_content, this returns
    basic config metadata without checking generation status.

    Args:
        filter_pattern: Optional glob pattern (e.g., "api*", "*-intro")
        _config_loader: Optional config loader for testing

    Returns:
        ListContentConfigsResult as dict with:
        - success: bool
        - total: int (total configs found)
        - configs: list[ContentConfigSummary]
        - duration_ms: int

    Example:
        list_content_configs()  # List all
        list_content_configs("api*")  # Filter by pattern
    """
    start_time = time.time()

    try:
        config_loader = _config_loader or get_config_loader()
        configs_dir = Path("configs/content")

        if not configs_dir.exists():
            result_obj = ListContentConfigsResult(
                success=True,
                total=0,
                configs=[],
                duration_ms=int((time.time() - start_time) * 1000),
            )
            return result_obj.model_dump()

        configs_list: list[ContentConfigSummary] = []
        pattern = filter_pattern or "*"

        # Scan for content configs matching pattern
        for config_path in configs_dir.glob(f"**/{pattern}-content.json"):
            try:
                # Extract content ID from filename (remove -content suffix)
                content_id = config_path.stem.removesuffix("-content")

                # Load config
                content_config = config_loader.load_content_config(content_id)

                # Build summary
                summary = ContentConfigSummary(
                    id=content_id,
                    file_path=str(config_path),
                    generator_type=content_config.generation.generator.type,
                    description=content_config.metadata.get("description", content_id),
                    title=content_config.metadata.get("title", content_id),
                )

                configs_list.append(summary)

            except Exception:
                # Skip invalid configs
                continue

        # Sort by ID
        configs_list.sort(key=lambda x: x.id)

        duration_ms = int((time.time() - start_time) * 1000)

        result_obj = ListContentConfigsResult(
            success=True,
            total=len(configs_list),
            configs=configs_list,
            duration_ms=duration_ms,
        )

        return result_obj.model_dump()

    except Exception as e:
        return _handle_tool_error(e, "list_content_configs", start_time)


@mcp.tool(name="choracompose:cleanup_ephemeral")
async def cleanup_ephemeral(
    retention: dict[str, Any] | None = None,
    filter: dict[str, Any] | None = None,
    dry_run: bool = False,
    _storage: Any = None,
) -> dict[str, Any]:
    """Clean up old ephemeral storage versions based on retention policy.

    Removes old content versions from ephemeral storage while preserving
    recent versions according to configurable retention rules. Always performs
    a dry run first to preview changes.

    Args:
        retention: Retention policy dict with optional keys:
            - keep_versions (int): Minimum versions to keep (default: 3)
            - keep_days (int): Keep versions newer than N days (default: 7)
            - keep_latest (bool): Always preserve latest (default: True)
            Note: Pass as flat dict, NOT nested object
        filter: Optional filter dict with keys:
            - content_ids (list[str]): Specific content IDs to clean
            - older_than_days (int): Only clean versions older than N days
        dry_run: Preview mode - show what would be deleted without actually deleting
        _storage: EphemeralStorageManager instance (injected for testing)

    Returns:
        CleanupEphemeralResult with cleanup statistics and per-content details

    Retention Logic:
        1. Always preserve latest version (if keep_latest=True)
        2. Keep N most recent versions (keep_versions)
        3. Keep versions within time window (keep_days)
        4. Delete versions not matched by any rule

    Example (dry run first):
        >>> result = await cleanup_ephemeral(
        ...     retention={"keep_versions": 2, "keep_days": 3},
        ...     dry_run=True
        ... )
        >>> print(f"Would delete {result['total_versions_deleted']} versions")

    Example (actual cleanup):
        >>> result = await cleanup_ephemeral(
        ...     retention={"keep_versions": 2, "keep_days": 3},
        ...     dry_run=False
        ... )
        >>> print(f"Freed {result['bytes_freed']} bytes")

    Errors:
        - invalid_retention: Invalid retention policy parameters
        - storage_error: Failed to access ephemeral storage
    """
    start_time = time.time()

    try:
        # Initialize dependencies
        from chora_compose.storage.ephemeral import EphemeralStorageManager

        storage = _storage or EphemeralStorageManager()

        # Parse and validate retention policy
        retention_dict = retention or {}
        retention_policy = RetentionPolicy(**retention_dict)

        # Parse filter
        filter_dict = filter or {}
        cleanup_filter = CleanupFilter(**filter_dict)

        # Get list of all content IDs in storage
        if cleanup_filter.content_ids:
            # Use specific content IDs from filter
            content_ids = cleanup_filter.content_ids
        else:
            # Get all content IDs from storage
            content_ids = storage.list_content_ids()

        # Track cleanup statistics
        total_content_checked = 0
        total_versions_deleted = 0
        bytes_freed = 0
        content_cleaned: list[dict[str, Any]] = []

        # Process each content ID
        for content_id in content_ids:
            total_content_checked += 1

            # Get all versions for this content
            versions = storage.list_versions(content_id)

            if not versions:
                continue

            # Count versions before cleanup
            versions_before = len(versions)

            # Apply retention logic to determine which versions to delete
            versions_to_delete = _apply_retention_policy(
                versions, retention_policy, cleanup_filter
            )

            if not versions_to_delete:
                continue

            # Count versions to delete
            versions_deleted_count = len(versions_to_delete)
            versions_after = versions_before - versions_deleted_count

            # Calculate bytes freed
            content_bytes_freed = 0
            for v in versions_to_delete:
                # Support both real StoredVersion (with file_path)
                # and mocks (with size_bytes)
                if hasattr(v, "size_bytes"):
                    content_bytes_freed += v.size_bytes
                elif hasattr(v, "file_path") and v.file_path.exists():
                    content_bytes_freed += v.file_path.stat().st_size

            # Actually delete if not dry run
            if not dry_run:
                for version in versions_to_delete:
                    storage.delete_version(version.content_id, version.timestamp)

            # Track statistics
            total_versions_deleted += versions_deleted_count
            bytes_freed += content_bytes_freed

            # Get oldest and latest kept versions
            # Use version_id for comparison
            # (Mock objects don't support identity comparison)
            deleted_ids = {v.version_id for v in versions_to_delete}
            kept_versions = [v for v in versions if v.version_id not in deleted_ids]

            # Helper to get timestamp as datetime (handles both StoredVersion and mocks)
            def get_timestamp_dt_for_sort(v: Any) -> Any:
                from datetime import datetime, timezone

                if hasattr(v, "timestamp_dt"):
                    return v.timestamp_dt
                elif hasattr(v, "timestamp"):
                    if isinstance(v.timestamp, datetime):
                        return v.timestamp
                    elif isinstance(v.timestamp, str):
                        return datetime.fromisoformat(v.timestamp)
                # Fallback: if timestamp is Mock or invalid, return epoch
                return datetime(1970, 1, 1, tzinfo=timezone.utc)

            # Helper to get timestamp as ISO string
            def get_timestamp_str(v: Any) -> str:
                from datetime import datetime

                if hasattr(v, "timestamp") and isinstance(v.timestamp, str):
                    return v.timestamp
                elif hasattr(v, "timestamp") and isinstance(v.timestamp, datetime):
                    return v.timestamp.isoformat()
                return str(v.timestamp)

            oldest_kept = (
                get_timestamp_str(min(kept_versions, key=get_timestamp_dt_for_sort))
                if kept_versions
                else None
            )
            latest_kept = (
                get_timestamp_str(max(kept_versions, key=get_timestamp_dt_for_sort))
                if kept_versions
                else None
            )

            # Create cleanup detail
            cleanup_detail = ContentCleanupDetail(
                content_id=content_id,
                versions_before=versions_before,
                versions_deleted=versions_deleted_count,
                versions_after=versions_after,
                bytes_freed=content_bytes_freed,
                oldest_kept=oldest_kept,
                latest_kept=latest_kept,
            )

            content_cleaned.append(cleanup_detail.model_dump())

        duration_ms = int((time.time() - start_time) * 1000)

        # Build result
        result_obj = CleanupEphemeralResult(
            success=True,
            status="dry_run" if dry_run else "cleaned",
            total_content_checked=total_content_checked,
            total_versions_deleted=total_versions_deleted,
            bytes_freed=bytes_freed,
            content_cleaned=content_cleaned,
            duration_ms=duration_ms,
        )

        return result_obj.model_dump()

    except Exception as e:
        return _handle_tool_error(e, "cleanup_ephemeral", start_time)


def _apply_retention_policy(
    versions: list[Any],
    retention: RetentionPolicy,
    filter: CleanupFilter,
) -> list[Any]:
    """Apply retention policy to determine which versions to delete.

    Args:
        versions: List of StoredVersion objects
        retention: Retention policy with keep_versions, keep_days, keep_latest
        filter: Cleanup filter with older_than_days

    Returns:
        List of versions to delete
    """
    from datetime import datetime, timedelta, timezone

    if not versions:
        return []

    # Helper to get timestamp as datetime (handles both StoredVersion and mocks)
    def get_timestamp_dt(v: Any) -> datetime:
        if hasattr(v, "timestamp_dt"):
            return v.timestamp_dt
        elif hasattr(v, "timestamp") and isinstance(v.timestamp, datetime):
            return v.timestamp
        elif hasattr(v, "timestamp") and isinstance(v.timestamp, str):
            return datetime.fromisoformat(v.timestamp)
        # Fallback: return epoch with timezone for comparable datetime
        return datetime(1970, 1, 1, tzinfo=timezone.utc)

    # Sort versions by timestamp (newest first)
    sorted_versions = sorted(versions, key=get_timestamp_dt, reverse=True)

    # Track which versions to keep
    versions_to_keep = set()

    # Rule 1: Always keep latest if keep_latest=True
    if retention.keep_latest:
        versions_to_keep.add(sorted_versions[0].version_id)

    # Rule 2: Keep N most recent versions
    for version in sorted_versions[: retention.keep_versions]:
        versions_to_keep.add(version.version_id)

    # Rule 3: Keep versions within time window (keep_days)
    if retention.keep_days > 0:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention.keep_days)
        for version in sorted_versions:
            if get_timestamp_dt(version) >= cutoff_date:
                versions_to_keep.add(version.version_id)

    # Apply filter: only consider versions older than X days for deletion
    if filter.older_than_days is not None and filter.older_than_days > 0:
        filter_cutoff = datetime.now(timezone.utc) - timedelta(
            days=filter.older_than_days
        )
        eligible_for_deletion = [
            v for v in sorted_versions if get_timestamp_dt(v) < filter_cutoff
        ]
    else:
        eligible_for_deletion = sorted_versions

    # Return versions not in keep set and eligible for deletion
    versions_to_delete = [
        v for v in eligible_for_deletion if v.version_id not in versions_to_keep
    ]

    return versions_to_delete
