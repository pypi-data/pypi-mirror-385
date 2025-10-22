"""MCP tools for configuration lifecycle management (v1.1.0).

This module implements conversational workflow authoring by enabling agents
to create, test, and manage configurations through MCP tools.

New tools:
- draft_config: Create temporary configs in ephemeral storage
- test_config: Preview generation without side effects
- save_config: Persist drafts to filesystem
- modify_config: Update existing configs incrementally
"""

import time
from pathlib import Path
from typing import Any

from chora_compose.core.models import ContentConfig
from chora_compose.generators.registry import GeneratorRegistry
from chora_compose.storage import get_ephemeral_config_manager

from .instance import mcp
from .types import (
    DraftConfigResult,
    ErrorResponse,
    MCPError,
    ModifyConfigResult,
    SaveConfigResult,
    TestConfigResult,
)


@mcp.tool(name="choracompose:draft_config")
async def draft_config(  # type: ignore[no-any-return]
    config_type: str,
    config_data: dict[str, Any],
    description: str | None = None,
) -> dict[str, Any]:
    """Create a draft configuration in ephemeral storage for testing.

    Draft configs are temporary and auto-cleanup after 30 days.
    Use save_config() to persist to filesystem when ready.

    Args:
        config_type: "content" or "artifact"
        config_data: Configuration JSON
        description: Optional description for this draft

    Returns:
        DraftConfigResult with draft_id and validation status
    """
    start_time = time.time()

    try:
        # Get ephemeral config manager
        config_mgr = get_ephemeral_config_manager()

        # Create draft (validates schema)
        draft = config_mgr.create_draft(config_type, config_data, description)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Return result
        result = DraftConfigResult(
            success=True,
            draft_id=draft.draft_id,
            config_type=draft.config_type,
            validation_status="valid",
            preview_path=str(
                config_mgr._get_draft_path(draft.draft_id, draft.config_type)
            ),
            created_at=draft.created_at,
            duration_ms=duration_ms,
        )

        return result.model_dump()

    except ValueError as e:
        # Schema validation failed
        duration_ms = int((time.time() - start_time) * 1000)
        return ErrorResponse(
            success=False,
            error=MCPError(
                code="validation_error",
                message=str(e),
                details={"config_type": config_type, "duration_ms": duration_ms},
            ),
        ).model_dump()

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ErrorResponse(
            success=False,
            error=MCPError(
                code="draft_creation_failed",
                message=f"Failed to create draft: {e}",
                details={"config_type": config_type, "duration_ms": duration_ms},
            ),
        ).model_dump()


@mcp.tool(name="choracompose:test_config")
async def test_config(  # type: ignore[no-any-return]
    draft_id: str,
    context: dict[str, Any] | str | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Test a draft config by running generation without persisting output.

    Useful for validating config before committing to filesystem.

    Args:
        draft_id: Draft config to test
        context: Optional context for generation (auto-parses JSON strings)
        dry_run: Don't store output (default True)

    Returns:
        TestConfigResult with preview content and validation issues
    """
    start_time = time.time()

    try:
        # Normalize context
        if context is None or context == "":
            context = {}
        elif isinstance(context, str):
            import json

            context = json.loads(context)

        # Get managers
        config_mgr = get_ephemeral_config_manager()

        # Load draft
        draft = config_mgr.get_draft(draft_id)

        # Only support content configs for now
        if draft.config_type != "content":
            raise ValueError(
                f"test_config only supports content configs, got {draft.config_type}"
            )

        # Get generator
        config_data = draft.config_data
        generator_type = config_data["generation"]["patterns"][0]["type"]
        registry = GeneratorRegistry()
        generator = registry.get(generator_type)

        if generator is None:
            raise ValueError(f"Generator not found: {generator_type}")

        # Parse config dict to ContentConfig model
        content_config = ContentConfig(**config_data)

        # Ensure context is dict (should already be normalized)
        context_dict = context if isinstance(context, dict) else {}

        # Generate content (synchronous, not async)
        generated_content = generator.generate(content_config, context_dict)

        # Truncate preview if large (max 10000 chars)
        preview_content = generated_content[:10000]
        if len(generated_content) > 10000:
            truncation_msg = (
                f"\n\n... (truncated, total {len(generated_content)} chars)"
            )
            preview_content += truncation_msg

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Return result
        result = TestConfigResult(
            success=True,
            draft_id=draft_id,
            preview_content=preview_content,
            content_length=len(generated_content),
            generator_used=generator_type,
            validation_issues=[],
            estimated_cost=None,  # TODO: Add token counting for AI generators
            duration_ms=duration_ms,
        )

        return result.model_dump()

    except FileNotFoundError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ErrorResponse(
            success=False,
            error=MCPError(
                code="draft_not_found",
                message=str(e),
                details={"draft_id": draft_id, "duration_ms": duration_ms},
            ),
        ).model_dump()

    except ValueError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ErrorResponse(
            success=False,
            error=MCPError(
                code="test_failed",
                message=str(e),
                details={"draft_id": draft_id, "duration_ms": duration_ms},
            ),
        ).model_dump()

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ErrorResponse(
            success=False,
            error=MCPError(
                code="test_execution_failed",
                message=f"Test execution failed: {e}",
                details={"draft_id": draft_id, "duration_ms": duration_ms},
            ),
        ).model_dump()


@mcp.tool(name="choracompose:save_config")
async def save_config(  # type: ignore[no-any-return]
    draft_id: str,
    config_id: str,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Save draft config to filesystem with proper directory structure.

    Creates: configs/{type}/{config_id}/{config_id}-{type}.json

    Args:
        draft_id: Draft to persist
        config_id: Permanent ID (e.g., "meeting-themes")
        overwrite: Allow overwriting existing config

    Returns:
        SaveConfigResult with filesystem path
    """
    start_time = time.time()

    try:
        # Get config manager
        config_mgr = get_ephemeral_config_manager()

        # Load draft to check type
        draft = config_mgr.get_draft(draft_id)

        # Check if config already exists
        config_path = (
            Path("configs")
            / draft.config_type
            / config_id
            / f"{config_id}-{draft.config_type}.json"
        )

        backup_path = None
        if config_path.exists() and not overwrite:
            error_msg = (
                f"Config already exists at {config_path}. "
                "Use overwrite=True to replace."
            )
            raise ValueError(error_msg)
        elif config_path.exists() and overwrite:
            # Create backup
            backup_path = config_path.with_suffix(".json.backup")
            import shutil

            shutil.copy(config_path, backup_path)

        # Persist draft
        saved_path = config_mgr.persist_draft(draft_id, config_id)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Return result
        result = SaveConfigResult(
            success=True,
            config_path=str(saved_path),
            config_id=config_id,
            config_type=draft.config_type,
            backup_path=str(backup_path) if backup_path else None,
            duration_ms=duration_ms,
        )

        return result.model_dump()

    except FileNotFoundError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ErrorResponse(
            success=False,
            error=MCPError(
                code="draft_not_found",
                message=str(e),
                details={"draft_id": draft_id, "duration_ms": duration_ms},
            ),
        ).model_dump()

    except ValueError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ErrorResponse(
            success=False,
            error=MCPError(
                code="save_failed",
                message=str(e),
                details={
                    "draft_id": draft_id,
                    "config_id": config_id,
                    "duration_ms": duration_ms,
                },
            ),
        ).model_dump()

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ErrorResponse(
            success=False,
            error=MCPError(
                code="save_execution_failed",
                message=f"Save execution failed: {e}",
                details={
                    "draft_id": draft_id,
                    "config_id": config_id,
                    "duration_ms": duration_ms,
                },
            ),
        ).model_dump()


@mcp.tool(name="choracompose:modify_config")
async def modify_config(  # type: ignore[no-any-return]
    config_id: str,
    updates: dict[str, Any],
    create_backup: bool = True,
) -> dict[str, Any]:
    """Apply incremental updates to a config.

    Works on both draft configs (ephemeral) and persisted configs (filesystem).
    Uses merge strategy: updates override existing fields.

    Args:
        config_id: Draft ID (draft-*) or permanent config ID
        updates: Dictionary of updates to apply
        create_backup: Backup before modifying (default True)

    Returns:
        ModifyConfigResult with validation status
    """
    start_time = time.time()

    try:
        config_mgr = get_ephemeral_config_manager()

        # Detect if this is a draft or persisted config
        is_draft = config_id.startswith("draft-")

        if is_draft:
            # Modify draft in ephemeral storage
            updated_draft = config_mgr.update_draft(config_id, updates)

            duration_ms = int((time.time() - start_time) * 1000)

            result = ModifyConfigResult(
                success=True,
                config_id=config_id,
                config_type=updated_draft.config_type,
                validation_status="valid",
                backup_path=None,  # Drafts don't need backups (versioned in ephemeral)
                draft_id=None,  # Already a draft
                duration_ms=duration_ms,
            )

            return result.model_dump()

        else:
            # Modify persisted config
            # For now, load as draft, modify, and optionally save back
            # TODO: Implement direct filesystem modification with backup
            raise NotImplementedError(
                "Modifying persisted configs not yet implemented. "
                f"Create a draft from {config_id} first using draft_config."
            )

    except FileNotFoundError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ErrorResponse(
            success=False,
            error=MCPError(
                code="config_not_found",
                message=str(e),
                details={"config_id": config_id, "duration_ms": duration_ms},
            ),
        ).model_dump()

    except ValueError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ErrorResponse(
            success=False,
            error=MCPError(
                code="modification_failed",
                message=str(e),
                details={"config_id": config_id, "duration_ms": duration_ms},
            ),
        ).model_dump()

    except NotImplementedError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ErrorResponse(
            success=False,
            error=MCPError(
                code="not_implemented",
                message=str(e),
                details={"config_id": config_id, "duration_ms": duration_ms},
            ),
        ).model_dump()

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return ErrorResponse(
            success=False,
            error=MCPError(
                code="modification_execution_failed",
                message=f"Modification execution failed: {e}",
                details={"config_id": config_id, "duration_ms": duration_ms},
            ),
        ).model_dump()
