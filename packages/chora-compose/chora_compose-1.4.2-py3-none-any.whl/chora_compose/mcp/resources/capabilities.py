"""MCP capability discovery resources for chora-compose.

This module implements the capabilities:// resource family that enables
LLM agents to introspect and self-configure by discovering server features,
tools, resources, and generators dynamically.

Resources:
- capabilities://server - Server metadata, features, limits, runtime
- capabilities://tools - Tool inventory with schemas and examples
- capabilities://resources - Resource URI catalog
- capabilities://generators - Generator registry with selection metadata

Version: 1.3.0 (Gateway Essentials)
"""

import sys
from typing import Any, Literal

from chora_compose.models import UpstreamDependencies
from pydantic import BaseModel, Field

# =============================================================================
# Pydantic Models for Capability Structures
# =============================================================================


class ServerCapabilities(BaseModel):
    """Server-level capabilities and metadata."""

    name: str = Field(description="Server name")
    version: str = Field(description="Server version (semver)")
    mcp_version: str = Field(description="MCP protocol version")
    features: dict[str, bool] = Field(
        description="Feature flags indicating what capabilities are available"
    )
    limits: dict[str, int] = Field(
        description="Operational limits (max sizes, retention, etc.)"
    )
    concurrency_limits: dict[str, int] = Field(
        description="Concurrency and queue limits for parallel operations (v1.3.0+)"
    )
    runtime: dict[str, str] = Field(description="Runtime environment information")
    tool_count: int = Field(description="Number of MCP tools available")
    resource_count: int = Field(description="Number of resource URI patterns")
    generator_count: int = Field(description="Number of registered generators")


class ToolCapability(BaseModel):
    """Metadata for a single MCP tool."""

    name: str = Field(description="Tool name")
    category: Literal[
        "content", "artifact", "config", "storage", "query", "validation", "batch"
    ] = Field(description="Tool category")
    description: str = Field(description="What this tool does")
    version: str = Field(description="Tool version")
    input_schema: dict[str, Any] = Field(description="Pydantic input schema")
    output_schema: dict[str, Any] = Field(description="Pydantic output schema")
    examples: list[dict[str, Any]] = Field(description="Usage examples")
    common_errors: list[dict[str, str]] = Field(description="Common error codes")
    performance: dict[str, str] = Field(description="Performance expectations")


class ResourceCapability(BaseModel):
    """Metadata for a resource URI pattern."""

    patterns: list[str] = Field(description="URI patterns for this resource")
    mime_type: str = Field(description="MIME type of resource content")
    description: str = Field(description="What this resource provides")
    parameters: dict[str, dict[str, Any]] = Field(description="URI parameters")
    examples: list[str] = Field(description="Example URIs")


class GeneratorCapability(BaseModel):
    """Enhanced generator metadata with upstream dependencies.

    Version 1.3.0 adds upstream_dependencies to enable gateways to:
    - Pre-validate credentials before calling generation tools
    - Display required services to users
    - Make intelligent routing decisions
    - Provide better error messages when dependencies are missing
    """

    type: str = Field(description="Generator type identifier")
    name: str = Field(description="Generator class name")
    version: str = Field(description="Generator version")
    source: Literal["builtin", "plugin"] = Field(
        description="Whether builtin or from plugin"
    )
    plugin_path: str | None = Field(
        default=None, description="Path to plugin file if source=plugin"
    )
    status: Literal["stable", "experimental", "deprecated"] = Field(
        description="Generator stability status"
    )
    capabilities: list[str] = Field(description="Generator capabilities")
    indicators: dict[str, Any] = Field(
        description="Patterns that suggest using this generator"
    )
    requirements: dict[str, Any] = Field(
        description="Requirements for using this generator"
    )
    best_for: list[str] = Field(description="Ideal use cases")
    docs_uri: str | None = Field(default=None, description="Documentation URI")
    upstream_dependencies: UpstreamDependencies | None = Field(
        default=None,
        description=(
            "External services and credentials required by this generator (v1.3.0+)"
        ),
    )


# =============================================================================
# Server Capabilities Provider
# =============================================================================


async def get_server_capabilities() -> dict[str, Any]:
    """Return server-level capabilities and metadata.

    URI: capabilities://server

    Returns server version, supported features, limits, concurrency limits,
    and runtime info that agents can use to understand what this MCP server
    can do.

    Returns:
        dict with server metadata, features, limits, concurrency_limits, runtime info

    Example:
        {
            "name": "chora-compose",
            "version": "1.3.0",
            "features": {"config_lifecycle": True, ...},
            "limits": {"max_content_size_bytes": 10000000, ...},
            "concurrency_limits": {"max_concurrent_generations": 3, ...},
            ...
        }
    """
    try:
        import fastmcp

        fastmcp_version = fastmcp.__version__
    except (ImportError, AttributeError):
        fastmcp_version = "unknown"

    # Get generator count from registry
    from chora_compose.generators.registry import GeneratorRegistry

    registry = GeneratorRegistry()
    generator_count = len(registry.list_types())

    return {
        "name": "chora-compose",
        "version": "1.3.0",
        "mcp_version": "1.0",
        "features": {
            "content_generation": True,
            "artifact_assembly": True,
            "config_lifecycle": True,  # v1.1.0+
            "batch_operations": True,
            "ephemeral_storage": True,
            "resource_providers": True,
            "generator_plugins": True,
            "capability_discovery": True,  # v1.1.0+ (this feature)
            "validation_suggestions": False,  # Removed in v1.0.1
        },
        "limits": {
            "max_content_size_bytes": 10_000_000,
            "max_artifact_components": 100,
            "ephemeral_retention_days": 30,
            "max_batch_size": 50,
        },
        "concurrency_limits": {
            "max_concurrent_generations": 3,
            "max_concurrent_assemblies": 2,
            "queue_size": 10,
            "timeout_seconds": 300,
        },
        "runtime": {
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "fastmcp": fastmcp_version,
            "platform": sys.platform,
        },
        "tool_count": 17,
        "resource_count": 5,  # config, schema, content, generator, capabilities
        "generator_count": generator_count,
    }


# =============================================================================
# Generator Capabilities Provider (Enhanced Decision Tree)
# =============================================================================


async def get_generator_capabilities() -> dict[str, Any]:
    """Return generator registry with selection metadata.

    URI: capabilities://generators

    Enhanced replacement for generator://decision_tree that reflects the
    LIVE generator registry (including plugins) and provides structured
    indicators for generator selection.

    Returns:
        dict with generators dict, selection_strategy, and metadata

    Example:
        {
            "generators": {
                "jinja2": {...},
                "demonstration": {...},
                ...
            },
            "selection_strategy": {...},
            "metadata": {...}
        }
    """
    from chora_compose.generators.registry import GeneratorRegistry

    registry = GeneratorRegistry()
    generators = {}

    builtin_types = {
        "demonstration",
        "jinja2",
        "template_fill",
        "code_generation",
        "bdd_scenario_assembly",
    }

    for gen_type in registry.list_types():
        try:
            generator = registry.get(gen_type)

            # Detect source (builtin vs plugin)
            source = "builtin" if gen_type in builtin_types else "plugin"

            # Get version from generator if available
            version = getattr(generator, "__version__", "1.0.0")

            # Extract upstream dependencies if available (v1.3.0+)
            upstream_deps = getattr(generator, "upstream_dependencies", None)
            upstream_deps_dict = (
                upstream_deps.model_dump() if upstream_deps is not None else None
            )

            generators[gen_type] = {
                "type": gen_type,
                "name": generator.__class__.__name__,
                "version": version,
                "source": source,
                "plugin_path": None,  # TODO: Extract from registry if plugin
                "status": _get_generator_status(gen_type),
                "capabilities": _get_generator_capabilities(gen_type),
                "indicators": _get_generator_indicators(gen_type),
                "requirements": _get_generator_requirements(gen_type),
                "best_for": _get_generator_best_for(gen_type),
                "docs_uri": f"docs://generators/{gen_type}",
                # v1.3.0: Gateway integration
                "upstream_dependencies": upstream_deps_dict,
            }
        except Exception:
            # Skip generators that fail to load
            continue

    builtin_count = sum(1 for g in generators.values() if g["source"] == "builtin")
    plugin_count = sum(1 for g in generators.values() if g["source"] == "plugin")

    return {
        "generators": generators,
        "selection_strategy": {
            "type": "indicator_match",
            "explanation": (
                "Match config characteristics against generator indicators. "
                "Explicit type specification (generation.patterns[0].type) takes "
                "precedence, followed by template syntax detection, then structural "
                "patterns like elements array presence."
            ),
            "fallback": "jinja2",
        },
        "metadata": {
            "version": "1.3.0",
            "generator_count": len(generators),
            "builtin_count": builtin_count,
            "plugin_count": plugin_count,
        },
    }


def _get_generator_status(gen_type: str) -> str:
    """Get generator stability status."""
    # All builtin generators are stable
    STABLE = {
        "demonstration",
        "jinja2",
        "template_fill",
        "code_generation",
        "bdd_scenario_assembly",
    }
    return "stable" if gen_type in STABLE else "experimental"


def _get_generator_capabilities(gen_type: str) -> list[str]:
    """Get generator capabilities."""
    CAPABILITIES = {
        "jinja2": ["templates", "loops", "conditionals", "filters", "inheritance"],
        "demonstration": ["examples", "few_shot", "style_consistency"],
        "template_fill": ["variable_substitution", "simple_placeholders"],
        "code_generation": ["ai_powered", "multi_language", "cost_tracking"],
        "bdd_scenario_assembly": ["gherkin", "scenarios", "data_tables"],
    }
    return CAPABILITIES.get(gen_type, [])


def _get_generator_indicators(gen_type: str) -> dict[str, Any]:
    """Get indicators that suggest using this generator.

    Migrated from decision_tree logic but made more structured.
    """
    INDICATORS = {
        "jinja2": {
            "config_field": "generation.patterns[0].type",
            "config_values": ["jinja2"],
            "template_patterns": ["{{", "{%"],
            "confidence": "high",
        },
        "demonstration": {
            "config_fields": ["elements"],
            "required_subfields": ["example_output"],
            "confidence": "medium",
        },
        "template_fill": {
            "config_field": "generation.patterns[0].type",
            "config_values": ["template_fill"],
            "template_patterns": ["{{"],  # But NOT {%
            "excludes": ["{%"],
            "confidence": "high",
        },
        "code_generation": {
            "config_field": "generation.patterns[0].type",
            "config_values": ["code_generation"],
            "metadata_field": "output_format",
            "metadata_values": ["python", "javascript", "typescript"],
            "confidence": "high",
        },
        "bdd_scenario_assembly": {
            "config_field": "generation.patterns[0].type",
            "config_values": ["bdd_scenario_assembly"],
            "metadata_field": "output_format",
            "metadata_values": ["gherkin"],
            "confidence": "high",
        },
    }
    return INDICATORS.get(gen_type, {"confidence": "low"})


def _get_generator_requirements(gen_type: str) -> dict[str, Any]:
    """Get requirements for using this generator."""
    REQUIREMENTS = {
        "jinja2": {
            "fields": ["generation.patterns[0].template"],
            "dependencies": [],
            "env_vars": [],
        },
        "demonstration": {
            "fields": ["elements"],
            "subfields": ["elements[].example_output"],
            "dependencies": [],
            "env_vars": [],
        },
        "template_fill": {
            "fields": ["generation.patterns[0].template"],
            "dependencies": [],
            "env_vars": [],
        },
        "code_generation": {
            "fields": ["generation.patterns[0].specification"],
            "dependencies": ["anthropic"],
            "env_vars": ["ANTHROPIC_API_KEY"],
        },
        "bdd_scenario_assembly": {
            "fields": ["generation.patterns[0].template"],
            "dependencies": [],
            "env_vars": [],
        },
    }
    return REQUIREMENTS.get(
        gen_type, {"fields": [], "dependencies": [], "env_vars": []}
    )


def _get_generator_best_for(gen_type: str) -> list[str]:
    """Get ideal use cases for this generator."""
    BEST_FOR = {
        "jinja2": [
            "Complex templates with logic",
            "Variable substitution from config data",
            "Iterating over arrays (loops)",
            "Conditional content rendering",
            "Template inheritance and composition",
        ],
        "demonstration": [
            "Creative content generation",
            "Maintaining consistent style/format",
            "Few-shot learning patterns",
            "Generating similar content from examples",
        ],
        "template_fill": [
            "Simple text replacement",
            "No logic needed (no loops/conditionals)",
            "Quick templating without Jinja2 overhead",
            "Static content with variable placeholders",
        ],
        "code_generation": [
            "Generating source code files",
            "Creating test files",
            "Scaffolding project structures",
            "API client generation from schemas",
        ],
        "bdd_scenario_assembly": [
            "Generating Gherkin feature files",
            "Creating BDD test scenarios",
            "Behavior specification documents",
            "Acceptance criteria as executable tests",
        ],
    }
    return BEST_FOR.get(gen_type, [])


# =============================================================================
# Tool Capabilities Provider
# =============================================================================


async def get_tool_capabilities() -> dict[str, Any]:
    """Return comprehensive tool inventory with usage patterns.

    URI: capabilities://tools

    Provides structured metadata about all 17 MCP tools, organized by
    category for easy discovery by agents.

    Returns:
        dict with tools_by_category and metadata

    Example:
        {
            "tools_by_category": {
                "content": [...],
                "artifact": [...],
                ...
            },
            "metadata": {"total_count": 17, ...}
        }
    """
    # Import all tool types for schema extraction
    from ..types import (
        AssembleArtifactInput,
        AssembleArtifactResult,
        DraftConfigInput,
        DraftConfigResult,
        GenerateContentInput,
        GenerateContentResult,
    )

    # Build tool capabilities by category
    tools_by_category = {
        "content": [
            _build_tool_capability(
                name="generate_content",
                category="content",
                description="Generate content from configurations using templates or AI",
                input_model=GenerateContentInput,
                output_model=GenerateContentResult,
                examples=[
                    {
                        "input": {
                            "content_config_id": "readme",
                            "context": {},
                            "force": False,
                        },
                        "description": "Generate README from config",
                    }
                ],
                common_errors=[
                    {"code": "config_not_found", "message": "Content config not found"},
                    {"code": "generator_error", "message": "Generator failed"},
                ],
                performance={"typical_ms": "500-2000", "timeout_ms": "30000"},
            ),
            # TODO: Add regenerate_content, preview_generation
        ],
        "artifact": [
            _build_tool_capability(
                name="assemble_artifact",
                category="artifact",
                description="Assemble artifacts from multiple content pieces",
                input_model=AssembleArtifactInput,
                output_model=AssembleArtifactResult,
                examples=[
                    {
                        "input": {
                            "artifact_config_id": "documentation",
                            "context": {},
                            "force": False,
                        },
                        "description": "Assemble multi-section documentation",
                    }
                ],
                common_errors=[
                    {
                        "code": "artifact_not_found",
                        "message": "Artifact config not found",
                    },
                    {"code": "assembly_error", "message": "Assembly failed"},
                ],
                performance={"typical_ms": "1000-5000", "timeout_ms": "60000"},
            ),
        ],
        "config": [
            _build_tool_capability(
                name="draft_config",
                category="config",
                description="Create temporary configs in ephemeral storage",
                input_model=DraftConfigInput,
                output_model=DraftConfigResult,
                examples=[
                    {
                        "input": {
                            "config_type": "content",
                            "config_id": "test-readme",
                            "config_data": {"type": "content"},
                        },
                        "description": "Draft a new content config",
                    }
                ],
                common_errors=[
                    {"code": "validation_error", "message": "Config invalid"},
                ],
                performance={"typical_ms": "<100", "timeout_ms": "5000"},
            ),
            # TODO: Add test_config, save_config, modify_config
        ],
        # TODO: Add storage, query, validation, batch categories
    }

    # Count total tools
    total_count = sum(len(tools) for tools in tools_by_category.values())

    return {
        "tools_by_category": tools_by_category,
        "metadata": {
            "total_count": total_count,
            "version": "1.3.0",
        },
    }


def _build_tool_capability(
    name: str,
    category: str,
    description: str,
    input_model: type[BaseModel],
    output_model: type[BaseModel],
    examples: list[dict],
    common_errors: list[dict],
    performance: dict[str, str],
) -> dict[str, Any]:
    """Build structured tool capability from Pydantic models."""
    return {
        "name": name,
        "category": category,
        "description": description,
        "version": "1.3.0",
        "input_schema": input_model.model_json_schema(),
        "output_schema": output_model.model_json_schema(),
        "examples": examples,
        "common_errors": common_errors,
        "performance": performance,
    }


# =============================================================================
# Resource Capabilities Provider
# =============================================================================


async def get_resource_capabilities() -> dict[str, Any]:
    """Return catalog of all MCP resources with schemas.

    URI: capabilities://resources

    Provides structured metadata about resource URIs, MIME types,
    and parameters for agent discovery.

    Returns:
        dict with resources dict and metadata

    Example:
        {
            "resources": {
                "config": {...},
                "schema": {...},
                ...
            },
            "metadata": {"total_count": 5, ...}
        }
    """
    return {
        "resources": {
            "config": {
                "patterns": [
                    "config://artifact/{artifact_id}",
                    "config://content/{content_id}",
                ],
                "mime_type": "application/json",
                "description": "Access configuration files for artifacts and content",
                "parameters": {
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact config ID",
                    },
                    "content_id": {
                        "type": "string",
                        "description": "Content config ID",
                    },
                },
                "examples": [
                    "config://artifact/test-artifact",
                    "config://content/simple-readme",
                ],
            },
            "schema": {
                "patterns": ["schema://{schema_name}"],
                "mime_type": "application/json",
                "description": "JSON Schema definitions",
                "parameters": {
                    "schema_name": {
                        "type": "string",
                        "description": "Schema name (content, artifact)",
                    }
                },
                "examples": ["schema://content", "schema://artifact"],
            },
            "content": {
                "patterns": [
                    "content://{content_id}",
                    "content://{content_id}/{version_id}",
                ],
                "mime_type": "text/plain",
                "description": "Generated content from ephemeral storage",
                "parameters": {
                    "content_id": {"type": "string", "description": "Content ID"},
                    "version_id": {
                        "type": "string",
                        "description": "Optional version ID",
                    },
                },
                "examples": [
                    "content://simple-readme",
                    "content://simple-readme/v1729012345",
                ],
            },
            "generator": {
                "patterns": ["generator://{generator_type}"],
                "mime_type": "application/json",
                "description": "Generator metadata and capabilities",
                "parameters": {
                    "generator_type": {
                        "type": "string",
                        "description": "Generator type",
                    }
                },
                "examples": ["generator://jinja2", "generator://code_generation"],
            },
            "capabilities": {
                "patterns": ["capabilities://{capability_type}"],
                "mime_type": "application/json",
                "description": "Server capability discovery (this resource)",
                "parameters": {
                    "capability_type": {
                        "type": "string",
                        "description": "Capability type (server, tools, resources, generators)",
                        "enum": ["server", "tools", "resources", "generators"],
                    }
                },
                "examples": [
                    "capabilities://server",
                    "capabilities://generators",
                ],
            },
        },
        "metadata": {
            "total_count": 5,
            "version": "1.3.0",
        },
    }
