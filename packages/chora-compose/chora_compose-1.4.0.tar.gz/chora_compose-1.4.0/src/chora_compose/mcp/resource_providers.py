"""MCP Resource Providers for chora-compose.

This module implements MCP resource providers that expose read-only access
to configuration data, schemas, and content through URI-based access patterns.

Resource URI Patterns:
- config://artifact/{artifact_id} - Artifact configuration
- config://content/{content_id} - Content configuration
- schema://{schema_name} - JSON schema definitions

All resources are read-only and return JSON or text data.
"""

from pathlib import Path
from typing import Any

# =============================================================================
# config:// Resource Provider Functions
# =============================================================================


async def get_artifact_config(artifact_id: str) -> str:
    """Get artifact configuration as JSON.

    URI Pattern: config://artifact/{artifact_id}

    Returns the complete artifact configuration JSON for the specified
    artifact ID. This allows Claude to inspect artifact definitions,
    understand dependencies, and view composition strategies.

    Args:
        artifact_id: Artifact configuration ID (e.g., "test-artifact")

    Returns:
        JSON string containing the artifact configuration

    Example Usage:
        Read artifact config in Claude Desktop:
        >>> Read config://artifact/test-artifact

    Errors:
        404: Artifact configuration not found
        500: Error reading configuration file
    """
    from chora_compose.core.config_loader import ConfigLoader

    try:
        config_loader = ConfigLoader()
        artifact_config = config_loader.load_artifact_config(artifact_id)

        # Convert to JSON string
        import json

        return json.dumps(artifact_config.model_dump(), indent=2)

    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Artifact configuration '{artifact_id}' not found"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Error loading artifact configuration '{artifact_id}': {str(e)}"
        ) from e


async def get_content_config(content_id: str) -> str:
    """Get content configuration as JSON.

    URI Pattern: config://content/{content_id}

    Returns the complete content configuration JSON for the specified
    content ID. This allows Claude to inspect content definitions,
    understand generation patterns, and view metadata.

    Args:
        content_id: Content configuration ID (e.g., "simple-readme")

    Returns:
        JSON string containing the content configuration

    Example Usage:
        Read content config in Claude Desktop:
        >>> Read config://content/simple-readme

    Errors:
        404: Content configuration not found
        500: Error reading configuration file
    """
    from chora_compose.core.config_loader import ConfigLoader

    try:
        config_loader = ConfigLoader()
        content_config = config_loader.load_content_config(content_id)

        # Convert to JSON string
        import json

        return json.dumps(content_config.model_dump(), indent=2)

    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Content configuration '{content_id}' not found"
        ) from e
    except Exception as e:
        raise RuntimeError(
            f"Error loading content configuration '{content_id}': {str(e)}"
        ) from e


# =============================================================================
# schema:// Resource Provider Function
# =============================================================================


async def get_schema(schema_name: str) -> str:
    """Get JSON schema definition.

    URI Pattern: schema://{schema_name}

    Returns the JSON schema definition for the specified schema name.
    Supports content, artifact, and other schema types defined in the
    schemas directory.

    Args:
        schema_name: Schema name (e.g., "content", "artifact", "generator")

    Returns:
        JSON string containing the schema definition

    Example Usage:
        Read schema in Claude Desktop:
        >>> Read schema://content
        >>> Read schema://artifact

    Errors:
        404: Schema not found
        500: Error reading schema file
    """
    try:
        # Schema files are in schemas/ directory
        schema_file = Path(f"schemas/{schema_name}-schema.json")

        if not schema_file.exists():
            raise FileNotFoundError(f"Schema '{schema_name}' not found")

        # Read schema file
        schema_content = schema_file.read_text(encoding="utf-8")

        return schema_content

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Schema '{schema_name}' not found") from e
    except Exception as e:
        raise RuntimeError(f"Error loading schema '{schema_name}': {str(e)}") from e


# =============================================================================
# content:// Resource Provider Function
# =============================================================================


async def get_content(
    content_id: str, version_id: str | None = None, _storage: Any = None
) -> str:
    """Get generated content from ephemeral storage.

    URI Patterns:
    - content://{content_id} - Get latest version
    - content://{content_id}/{version_id} - Get specific version

    Returns the generated content text for the specified content ID and
    optional version. If no version is specified, returns the latest version.

    Args:
        content_id: Content configuration ID (e.g., "simple-readme")
        version_id: Optional version ID to fetch specific version
        _storage: EphemeralStorageManager instance (injected for testing)

    Returns:
        Plain text content from ephemeral storage

    Example Usage:
        Read latest content in Claude Desktop:
        >>> Read content://simple-readme

        Read specific version:
        >>> Read content://simple-readme/v1234567890

    Errors:
        404: Content not found in ephemeral storage
        500: Error reading content from storage
    """
    from chora_compose.storage.ephemeral import EphemeralStorageManager

    try:
        storage = _storage or EphemeralStorageManager()

        if version_id:
            # Fetch specific version
            stored_version = storage.retrieve_version(content_id, version_id)
            if not stored_version:
                raise FileNotFoundError(
                    f"Content '{content_id}' version '{version_id}' not found in storage"
                )
            return stored_version.content
        else:
            # Fetch latest version
            stored_version = storage.retrieve(content_id)
            if not stored_version:
                raise FileNotFoundError(
                    f"Content '{content_id}' not found in storage (no versions available)"
                )
            return stored_version.content

    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Error loading content '{content_id}': {str(e)}") from e


# =============================================================================
# generator:// Resource Provider Function
# =============================================================================


async def get_generator_info(generator_type: str, _registry: Any = None) -> str:
    """Get generator metadata and capabilities.

    URI Pattern: generator://{generator_type}

    Returns metadata about a specific generator including its capabilities,
    required context keys, supported patterns, and configuration options.

    Args:
        generator_type: Generator type (e.g., "jinja2", "code_generation")
        _registry: GeneratorRegistry instance (injected for testing)

    Returns:
        JSON string containing generator metadata and capabilities

    Example Usage:
        Read generator info in Claude Desktop:
        >>> Read generator://jinja2
        >>> Read generator://code_generation

    Errors:
        404: Generator not found in registry
        500: Error loading generator metadata
    """
    from chora_compose.generators.registry import GeneratorRegistry

    try:
        registry = _registry or GeneratorRegistry()

        # Get generator from registry
        generator = registry.get_generator(generator_type)

        if not generator:
            raise FileNotFoundError(
                f"Generator '{generator_type}' not found in registry"
            )

        # Extract metadata
        import json

        metadata = {
            "type": generator_type,
            "name": generator.__class__.__name__,
            "description": generator.__doc__
            or f"{generator.__class__.__name__} generator",
            "capabilities": {
                "supports_context": hasattr(generator, "generate_with_context"),
                "supports_templates": hasattr(generator, "template"),
                "supports_async": hasattr(generator, "generate_async"),
            },
            "module": generator.__class__.__module__,
            "class": generator.__class__.__name__,
        }

        # Try to extract required context keys if available
        if hasattr(generator, "required_context_keys"):
            metadata["required_context_keys"] = generator.required_context_keys
        elif hasattr(generator, "REQUIRED_CONTEXT_KEYS"):
            metadata["required_context_keys"] = generator.REQUIRED_CONTEXT_KEYS

        return json.dumps(metadata, indent=2)

    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(
            f"Error loading generator '{generator_type}': {str(e)}"
        ) from e


# =============================================================================
# Resource Listing Helpers
# =============================================================================


async def list_artifact_configs() -> list[dict[str, Any]]:
    """List all available artifact configurations.

    Returns:
        List of artifact metadata dictionaries with id, title, type
    """
    configs_dir = Path("configs/artifacts")
    artifacts = []

    for config_path in configs_dir.glob("**/*.json"):
        try:
            from chora_compose.core.config_loader import ConfigLoader

            artifact_id = config_path.stem
            config_loader = ConfigLoader()
            artifact_config = config_loader.load_artifact_config(artifact_id)

            artifacts.append(
                {
                    "id": artifact_id,
                    "title": artifact_config.metadata.get("title", artifact_id),
                    "type": artifact_config.metadata.get("type", "unknown"),
                    "uri": f"config://artifact/{artifact_id}",
                }
            )
        except Exception:
            continue

    return artifacts


async def list_content_configs() -> list[dict[str, Any]]:
    """List all available content configurations.

    Returns:
        List of content metadata dictionaries with id, description, type
    """
    configs_dir = Path("configs/content")
    contents = []

    for config_path in configs_dir.glob("**/*.json"):
        try:
            from chora_compose.core.config_loader import ConfigLoader

            content_id = config_path.stem
            config_loader = ConfigLoader()
            content_config = config_loader.load_content_config(content_id)

            contents.append(
                {
                    "id": content_id,
                    "description": content_config.metadata.get(
                        "description", content_id
                    ),
                    "uri": f"config://content/{content_id}",
                }
            )
        except Exception:
            continue

    return contents


async def list_schemas() -> list[dict[str, str]]:
    """List all available schemas.

    Returns:
        List of schema metadata dictionaries with name, description, uri
    """
    schemas_dir = Path("schemas")
    schemas = []

    for schema_path in schemas_dir.glob("*-schema.json"):
        schema_name = schema_path.stem.replace("-schema", "")
        schemas.append(
            {
                "name": schema_name,
                "uri": f"schema://{schema_name}",
                "description": f"{schema_name.capitalize()} schema definition",
            }
        )

    return schemas


# =============================================================================
# Resource Registration
# =============================================================================


def register_resource_providers() -> None:
    """Register resource providers with the MCP server.

    This function is called by resources/__init__.py to register all
    basic resource providers (config://, schema://, content://, generator://).
    """
    try:
        from .server import mcp

        # Register config:// resources
        mcp.resource("config://artifact/{artifact_id}")(get_artifact_config)
        mcp.resource("config://content/{content_id}")(get_content_config)

        # Register schema:// resource
        mcp.resource("schema://{schema_name}")(get_schema)

        # Register content:// resources
        mcp.resource("content://{content_id}")(get_content)
        mcp.resource("content://{content_id}/{version_id}")(get_content)

        # Register generator:// resource
        mcp.resource("generator://{generator_type}")(get_generator_info)

    except ImportError:
        # FastMCP not available (testing environment)
        pass
