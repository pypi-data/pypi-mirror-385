"""Context resolver for resolving input sources to actual data."""

import json
import subprocess
from pathlib import Path
from typing import Any

from chora_compose.core.config_loader import ConfigLoader
from chora_compose.core.models import (
    ArtifactConfig,
    ContentConfig,
    InputSource,
    SourceType,
)
from chora_compose.storage.ephemeral import EphemeralStorageManager


class ContextResolutionError(Exception):
    """Raised when a source cannot be resolved."""

    pass


class ContextResolver:
    """Resolves input sources from configs to actual data.

    Supports multiple source types:
    - external_file: Load from filesystem
    - content_config: Load and reference content config
    - artifact_config: Load artifact config data
    - ephemeral_output: Retrieve from ephemeral storage
    - git_reference: Load from git commit/branch
    - inline_data: Pass through embedded data
    - requirement_id: Plugin-based (extensible)
    """

    def __init__(
        self,
        config_loader: ConfigLoader,
        storage_manager: EphemeralStorageManager | None = None,
        base_path: Path | None = None,
    ) -> None:
        """Initialize context resolver.

        Args:
            config_loader: ConfigLoader instance for loading configs
            storage_manager: Optional ephemeral storage manager
            base_path: Base path for resolving relative file paths
        """
        self.config_loader = config_loader
        self.storage_manager = storage_manager
        self.base_path = base_path or Path.cwd()
        self._cache: dict[str, Any] = {}

    def resolve(self, sources: list[InputSource] | None) -> dict[str, Any]:
        """Resolve all input sources to a context dict.

        Args:
            sources: List of input sources to resolve

        Returns:
            Dictionary mapping source names to resolved data

        Raises:
            ContextResolutionError: If a required source cannot be resolved
        """
        if not sources:
            return {}

        context = {}

        for source in sources:
            try:
                data = self.resolve_source(source)
                context[source.id] = data
            except Exception as e:
                if source.required:
                    raise ContextResolutionError(
                        f"Failed to resolve required source '{source.id}': {e}"
                    ) from e
                # Optional source failed, continue
                context[source.id] = None

        return context

    def resolve_source(self, source: InputSource) -> Any:
        """Resolve a single input source.

        Args:
            source: Input source specification

        Returns:
            Resolved data (string, dict, list, etc.)

        Raises:
            ContextResolutionError: If source cannot be resolved
            ValueError: If source type is not supported
        """
        # Check cache first
        cache_key = f"{source.source_type}:{source.source_locator}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Resolve based on source type
        data: Any
        if source.source_type == SourceType.EXTERNAL_FILE:
            data = self._resolve_external_file(source.source_locator)
        elif source.source_type == SourceType.CONTENT_CONFIG:
            data = self._resolve_content_config(source.source_locator)
        elif source.source_type == SourceType.ARTIFACT_CONFIG:
            data = self._resolve_artifact_config(source.source_locator)
        elif source.source_type == SourceType.EPHEMERAL_OUTPUT:
            data = self._resolve_ephemeral_output(source.source_locator)
        elif source.source_type == SourceType.GIT_REFERENCE:
            data = self._resolve_git_reference(source.source_locator)
        elif source.source_type == SourceType.INLINE_DATA:
            data = self._resolve_inline_data(source.source_locator)
        elif source.source_type == SourceType.REQUIREMENT_ID:
            data = self._resolve_requirement_id(source.source_locator)
        else:
            raise ValueError(f"Unsupported source type: {source.source_type}")

        # Cache the result
        self._cache[cache_key] = data
        return data

    def _resolve_external_file(self, locator: str) -> str:
        """Resolve external file source.

        Args:
            locator: File path (relative or absolute)

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(locator)

        # Make absolute if relative
        if not file_path.is_absolute():
            file_path = self.base_path / file_path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path) as f:
            return f.read()

    def _resolve_content_config(self, locator: str) -> ContentConfig:
        """Resolve content config source.

        Args:
            locator: Content config ID or path

        Returns:
            Loaded ContentConfig object

        Raises:
            FileNotFoundError: If config not found
        """
        # Try as ID first
        try:
            return self.config_loader.load_content_config(locator)
        except FileNotFoundError:
            # Try as path
            path = Path(locator)
            if not path.is_absolute():
                path = self.base_path / path
            config = self.config_loader.load_config(path)
            if not isinstance(config, ContentConfig):
                raise ValueError(f"Expected ContentConfig, got {type(config).__name__}")
            return config

    def _resolve_artifact_config(self, locator: str) -> dict[str, Any]:
        """Resolve artifact config source.

        Args:
            locator: Artifact config ID or path

        Returns:
            Artifact config as dictionary

        Raises:
            FileNotFoundError: If config not found
        """
        # Try as ID first
        try:
            artifact = self.config_loader.load_artifact_config(locator)
            return artifact.model_dump()
        except FileNotFoundError:
            # Try as path
            path = Path(locator)
            if not path.is_absolute():
                path = self.base_path / path
            config = self.config_loader.load_config(path)
            if not isinstance(config, ArtifactConfig):
                raise ValueError(
                    f"Expected ArtifactConfig, got {type(config).__name__}"
                )
            result: dict[str, Any] = config.model_dump()
            return result

    def _resolve_ephemeral_output(self, locator: str) -> str | list[str]:
        """Resolve ephemeral output source.

        Args:
            locator: Format: "content_id:strategy" or just "content_id"

        Returns:
            Retrieved content (str for single version, list[str] for 'all' strategy)

        Raises:
            ValueError: If storage_manager not provided
            FileNotFoundError: If content not found
        """
        if not self.storage_manager:
            raise ValueError("Storage manager required for ephemeral_output sources")

        # Parse locator: "content_id:strategy" or "content_id"
        parts = locator.split(":", 1)
        content_id = parts[0]
        strategy = parts[1] if len(parts) > 1 else "latest"

        content = self.storage_manager.retrieve(content_id, strategy)

        if content is None:
            raise FileNotFoundError(f"Ephemeral content not found: {content_id}")

        # If strategy is 'all', return list; otherwise return string
        return content

    def _resolve_git_reference(self, locator: str) -> str:
        """Resolve git reference source.

        Args:
            locator: Format: "commit:path" or "branch:path"
                    e.g., "HEAD:README.md" or "main:src/config.py"

        Returns:
            File contents from git

        Raises:
            subprocess.CalledProcessError: If git command fails
        """
        # Parse locator: "ref:path"
        if ":" not in locator:
            raise ValueError(
                f"Invalid git reference format: {locator}. Expected 'ref:path'"
            )

        ref, path = locator.split(":", 1)

        # Use git show to retrieve file
        try:
            result = subprocess.run(
                ["git", "show", f"{ref}:{path}"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.base_path,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise ContextResolutionError(f"Git command failed: {e.stderr}") from e

    def _resolve_inline_data(self, locator: str) -> Any:
        """Resolve inline data source.

        Args:
            locator: Data embedded directly (string or JSON)

        Returns:
            The locator itself (as data)
        """
        # Try to parse as JSON first
        try:
            return json.loads(locator)
        except json.JSONDecodeError:
            # Not JSON, return as string
            return locator

    def _resolve_requirement_id(self, locator: str) -> dict[str, Any]:
        """Resolve requirement ID source.

        This is a plugin-based resolver that can be extended in the future
        to integrate with requirement management systems.

        Args:
            locator: Requirement ID

        Returns:
            Requirement data (currently a placeholder)

        Note:
            This is a stub implementation. To use this source type,
            implement a custom resolver or plugin.
        """
        # Placeholder implementation
        # In a real system, this would query a requirements management system
        return {
            "id": locator,
            "type": "requirement",
            "note": "Requirement resolver not yet implemented",
        }

    def clear_cache(self) -> None:
        """Clear the resolution cache."""
        self._cache.clear()
