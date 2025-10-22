"""Ephemeral config manager for draft configurations."""

import json
import secrets
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chora_compose.core import get_config_loader


class DraftConfig:
    """Represents a draft configuration."""

    def __init__(
        self,
        draft_id: str,
        config_type: str,
        config_data: dict[str, Any],
        created_at: str,
        updated_at: str,
        description: str | None = None,
    ) -> None:
        """Initialize a draft config.

        Args:
            draft_id: Unique identifier for the draft
            config_type: "content" or "artifact"
            config_data: Configuration JSON
            created_at: ISO 8601 timestamp of creation
            updated_at: ISO 8601 timestamp of last update
            description: Optional description
        """
        self.draft_id = draft_id
        self.config_type = config_type
        self.config_data = config_data
        self.created_at = created_at
        self.updated_at = updated_at
        self.description = description

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "draft_id": self.draft_id,
            "config_type": self.config_type,
            "config_data": self.config_data,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "description": self.description,
        }


class EphemeralConfigManager:
    """Manages draft configs in ephemeral storage before persistence.

    Draft configs are temporary configurations stored in ephemeral/drafts/
    that can be tested and iterated on before being persisted to the
    configs/ directory.

    Storage structure:
        ephemeral/
          drafts/
            content/
              draft-20251016-abc123.json
            artifact/
              draft-20251016-xyz789.json
    """

    def __init__(self, base_path: Path | str | None = None) -> None:
        """Initialize ephemeral config manager.

        Args:
            base_path: Root directory for ephemeral storage.
                      Defaults to "ephemeral/drafts" in current directory.
        """
        resolved_base_path = (
            Path(base_path) if base_path is not None else Path("ephemeral")
        )
        self.base_path = resolved_base_path / "drafts"
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for content and artifact drafts
        (self.base_path / "content").mkdir(exist_ok=True)
        (self.base_path / "artifact").mkdir(exist_ok=True)

    def _generate_draft_id(self) -> str:
        """Generate unique draft ID.

        Format: draft-{timestamp}-{random}
        Example: draft-20251016T153045-a1b2c3
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        random_suffix = secrets.token_hex(3)  # 6 character hex
        return f"draft-{timestamp}-{random_suffix}"

    def _get_draft_path(self, draft_id: str, config_type: str) -> Path:
        """Get filesystem path for a draft config.

        Args:
            draft_id: Draft identifier
            config_type: "content" or "artifact"

        Returns:
            Path to draft config file
        """
        return self.base_path / config_type / f"{draft_id}.json"

    def _validate_config_type(self, config_type: str) -> None:
        """Validate config type.

        Args:
            config_type: Config type to validate

        Raises:
            ValueError: If config_type is not "content" or "artifact"
        """
        if config_type not in ["content", "artifact"]:
            raise ValueError(
                f"Invalid config_type: {config_type}. Must be 'content' or 'artifact'"
            )

    def create_draft(
        self,
        config_type: str,
        config_data: dict[str, Any],
        description: str | None = None,
    ) -> DraftConfig:
        """Create a new draft config.

        Validates against JSON Schema before storing.

        Args:
            config_type: "content" or "artifact"
            config_data: Configuration JSON
            description: Optional description for the draft

        Returns:
            DraftConfig object with draft_id and metadata

        Raises:
            ValueError: If config_type is invalid or validation fails
        """
        self._validate_config_type(config_type)

        # Validate against schema
        loader = get_config_loader()
        try:
            if config_type == "content":
                # Validate but don't use the result - we store raw dict
                loader._validate_with_schema(config_data, "content", "3.1")
            else:
                loader._validate_with_schema(config_data, "artifact", "3.1")
        except Exception as e:
            raise ValueError(f"Schema validation failed: {e}")

        # Generate draft ID and timestamps
        draft_id = self._generate_draft_id()
        now = datetime.now(timezone.utc).isoformat()

        # Create draft config object
        draft = DraftConfig(
            draft_id=draft_id,
            config_type=config_type,
            config_data=config_data,
            created_at=now,
            updated_at=now,
            description=description,
        )

        # Write to filesystem (atomic)
        draft_path = self._get_draft_path(draft_id, config_type)
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=draft_path.parent,
            delete=False,
            suffix=".tmp.json",
        ) as tmp:
            json.dump(draft.to_dict(), tmp, indent=2)
            tmp_path = Path(tmp.name)

        # Atomic rename
        tmp_path.rename(draft_path)

        return draft

    def get_draft(self, draft_id: str) -> DraftConfig:
        """Retrieve a draft config.

        Args:
            draft_id: Draft identifier

        Returns:
            DraftConfig object

        Raises:
            FileNotFoundError: If draft doesn't exist
        """
        # Try both content and artifact directories
        for config_type in ["content", "artifact"]:
            draft_path = self._get_draft_path(draft_id, config_type)
            if draft_path.exists():
                with open(draft_path) as f:
                    data = json.load(f)
                return DraftConfig(**data)

        raise FileNotFoundError(f"Draft not found: {draft_id}")

    def update_draft(self, draft_id: str, updates: dict[str, Any]) -> DraftConfig:
        """Update a draft config with incremental changes.

        Uses merge strategy: updates override existing fields.

        Args:
            draft_id: Draft identifier
            updates: Dictionary of updates to apply

        Returns:
            Updated DraftConfig object

        Raises:
            FileNotFoundError: If draft doesn't exist
            ValueError: If validation fails after update
        """
        # Load existing draft
        draft = self.get_draft(draft_id)

        # Merge updates (simple shallow merge for now)
        # More sophisticated merge could be added later
        updated_config = {**draft.config_data, **updates}

        # Validate updated config
        loader = get_config_loader()
        try:
            if draft.config_type == "content":
                loader._validate_with_schema(updated_config, "content", "3.1")
            else:
                loader._validate_with_schema(updated_config, "artifact", "3.1")
        except Exception as e:
            raise ValueError(f"Schema validation failed after update: {e}")

        # Update draft
        draft.config_data = updated_config
        draft.updated_at = datetime.now(timezone.utc).isoformat()

        # Write back to filesystem (atomic)
        draft_path = self._get_draft_path(draft_id, draft.config_type)
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=draft_path.parent,
            delete=False,
            suffix=".tmp.json",
        ) as tmp:
            json.dump(draft.to_dict(), tmp, indent=2)
            tmp_path = Path(tmp.name)

        tmp_path.rename(draft_path)

        return draft

    def delete_draft(self, draft_id: str) -> bool:
        """Delete a draft config.

        Args:
            draft_id: Draft identifier

        Returns:
            True if deleted, False if not found
        """
        # Try both content and artifact directories
        for config_type in ["content", "artifact"]:
            draft_path = self._get_draft_path(draft_id, config_type)
            if draft_path.exists():
                draft_path.unlink()
                return True

        return False

    def list_drafts(self, config_type: str | None = None) -> list[DraftConfig]:
        """List all draft configs.

        Args:
            config_type: Optional filter by "content" or "artifact"

        Returns:
            List of DraftConfig objects, sorted by created_at
        """
        drafts = []

        # Determine which directories to scan
        if config_type:
            self._validate_config_type(config_type)
            dirs = [config_type]
        else:
            dirs = ["content", "artifact"]

        # Scan directories
        for dir_name in dirs:
            draft_dir = self.base_path / dir_name
            for draft_file in draft_dir.glob("draft-*.json"):
                try:
                    with open(draft_file) as f:
                        data = json.load(f)
                    drafts.append(DraftConfig(**data))
                except (json.JSONDecodeError, KeyError, TypeError):
                    # Skip malformed drafts
                    continue

        # Sort by created_at
        drafts.sort(key=lambda d: d.created_at)
        return drafts

    def persist_draft(self, draft_id: str, config_id: str) -> Path:
        """Persist a draft config to the filesystem.

        Creates proper directory structure:
          configs/{type}/{config_id}/{config_id}-{type}.json

        Args:
            draft_id: Draft identifier
            config_id: Permanent config ID (e.g., "meeting-themes")

        Returns:
            Path to persisted config file

        Raises:
            FileNotFoundError: If draft doesn't exist
            ValueError: If config_id is invalid
        """
        # Validate config_id (kebab-case, no slashes, no dots)
        if not config_id or "/" in config_id or "\\" in config_id or ".." in config_id:
            raise ValueError(
                f"Invalid config_id: {config_id}. "
                "Must be kebab-case, no path separators or parent refs."
            )

        # Load draft
        draft = self.get_draft(draft_id)

        # Determine output path
        config_root = Path("configs") / draft.config_type / config_id
        config_root.mkdir(parents=True, exist_ok=True)

        config_filename = f"{config_id}-{draft.config_type}.json"
        config_path = config_root / config_filename

        # Write config (atomic)
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=config_root,
            delete=False,
            suffix=".tmp.json",
        ) as tmp:
            json.dump(draft.config_data, tmp, indent=2)
            tmp_path = Path(tmp.name)

        tmp_path.rename(config_path)

        return config_path
