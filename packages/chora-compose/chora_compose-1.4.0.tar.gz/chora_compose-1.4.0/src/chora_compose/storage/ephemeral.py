"""Ephemeral storage manager for versioned content."""

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


class StoredVersion:
    """Represents a stored version of ephemeral content."""

    def __init__(
        self,
        content_id: str,
        timestamp: str,
        format: str,
        file_path: Path,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize a stored version.

        Args:
            content_id: Unique identifier for the content
            timestamp: ISO 8601 timestamp of when content was saved
            format: File format extension (md, json, txt, etc.)
            file_path: Path to the stored content file
            metadata: Additional metadata about this version
        """
        self.content_id = content_id
        self.timestamp = timestamp
        self.format = format
        self.file_path = file_path
        self.metadata = metadata or {}

    @property
    def version_id(self) -> str:
        """Get version identifier (timestamp string)."""
        return self.timestamp

    @property
    def timestamp_dt(self) -> datetime:
        """Get timestamp as datetime object."""
        return datetime.fromisoformat(self.timestamp)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "content_id": self.content_id,
            "timestamp": self.timestamp,
            "format": self.format,
            "file_path": str(self.file_path),
            "metadata": self.metadata,
        }


class CleanupResult:
    """Result of a cleanup operation."""

    def __init__(
        self, files_removed: int, versions_removed: int, space_freed: int
    ) -> None:
        """Initialize cleanup result.

        Args:
            files_removed: Number of files deleted
            versions_removed: Number of versions removed
            space_freed: Bytes freed
        """
        self.files_removed = files_removed
        self.versions_removed = versions_removed
        self.space_freed = space_freed


class EphemeralStorageManager:
    """Manages ephemeral storage with versioning and retention policies.

    Stores generated content with timestamps, supports multiple retrieval
    strategies, handles concurrent access, and implements cleanup policies.
    """

    def __init__(
        self,
        base_path: Path | str | None = None,
        retention_days: int = 30,
        auto_cleanup: bool = False,
    ) -> None:
        """Initialize ephemeral storage manager.

        Args:
            base_path: Root directory for ephemeral storage
            retention_days: Days to retain old versions (0 = keep forever)
            auto_cleanup: Automatically cleanup on save operations
        """
        resolved_base_path = (
            Path(base_path) if base_path is not None else Path("ephemeral")
        )
        self.base_path = resolved_base_path
        self.retention_days = retention_days
        self.auto_cleanup = auto_cleanup
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        content_id: str,
        content: str,
        format: str = "txt",
        metadata: dict[str, Any] | None = None,
    ) -> StoredVersion:
        """Save content with automatic versioning.

        Uses atomic writes (write to temp, then rename) to prevent corruption.
        Optionally runs cleanup if auto_cleanup is enabled.

        Args:
            content_id: Unique identifier for the content
            content: Content to save
            format: File extension (md, json, txt, etc.)
            metadata: Optional metadata to store alongside content

        Returns:
            StoredVersion object with saved version information

        Raises:
            OSError: If file operations fail
        """
        # Create content directory
        content_dir = self.base_path / content_id
        content_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamp with microseconds for uniqueness
        timestamp = datetime.now(timezone.utc).isoformat()

        # Create safe filename from timestamp (keep microseconds for uniqueness)
        # Replace colons with dashes, keep microseconds
        safe_timestamp = timestamp.replace(":", "-").replace(".", "-")
        content_file = content_dir / f"{safe_timestamp}.{format}"
        metadata_file = content_dir / f"{safe_timestamp}.meta.json"

        # Atomic write using temp file
        with tempfile.NamedTemporaryFile(
            mode="w", dir=content_dir, delete=False, suffix=f".tmp.{format}"
        ) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        # Rename to final location (atomic on POSIX)
        tmp_path.rename(content_file)

        # Save metadata
        version_metadata = metadata or {}
        version_metadata.update(
            {
                "content_id": content_id,
                "timestamp": timestamp,
                "format": format,
                "size": len(content),
            }
        )

        with open(metadata_file, "w") as f:
            json.dump(version_metadata, f, indent=2)

        # Auto cleanup if enabled
        if self.auto_cleanup and self.retention_days > 0:
            self.cleanup(content_id)

        return StoredVersion(
            content_id=content_id,
            timestamp=timestamp,
            format=format,
            file_path=content_file,
            metadata=version_metadata,
        )

    def retrieve(
        self, content_id: str, strategy: str = "latest"
    ) -> str | list[str] | None:
        """Retrieve content using specified strategy.

        Supported strategies:
        - 'latest': Most recent version
        - 'all': All versions chronologically
        - 'version:X.Y.Z': Specific semantic version (from metadata)
        - 'timestamp:YYYY-MM-DD': Specific timestamp

        Args:
            content_id: Content identifier
            strategy: Retrieval strategy

        Returns:
            Content string for single version, list of strings for 'all',
            or None if not found

        Raises:
            ValueError: If strategy is invalid
            FileNotFoundError: If content_id doesn't exist
        """
        content_dir = self.base_path / content_id
        if not content_dir.exists():
            raise FileNotFoundError(f"Content not found: {content_id}")

        versions = self.list_versions(content_id)
        if not versions:
            return None

        if strategy == "latest":
            # Return most recent
            latest = versions[-1]
            with open(latest.file_path) as f:
                return f.read()

        elif strategy == "all":
            # Return all versions
            contents = []
            for version in versions:
                with open(version.file_path) as f:
                    contents.append(f.read())
            return contents

        elif strategy.startswith("version:"):
            # Find by semantic version in metadata
            version_num = strategy.split(":", 1)[1]
            for version in versions:
                if version.metadata.get("version") == version_num:
                    with open(version.file_path) as f:
                        return f.read()
            return None

        elif strategy.startswith("timestamp:"):
            # Find by timestamp prefix
            timestamp_prefix = strategy.split(":", 1)[1]
            for version in versions:
                if version.timestamp.startswith(timestamp_prefix):
                    with open(version.file_path) as f:
                        return f.read()
            return None

        else:
            raise ValueError(f"Invalid retrieval strategy: {strategy}")

    def list_versions(self, content_id: str) -> list[StoredVersion]:
        """List all versions for a content ID.

        Args:
            content_id: Content identifier

        Returns:
            List of StoredVersion objects, sorted chronologically

        Raises:
            FileNotFoundError: If content_id doesn't exist
        """
        content_dir = self.base_path / content_id
        if not content_dir.exists():
            raise FileNotFoundError(f"Content not found: {content_id}")

        versions = []

        # Find all content files (not .meta.json files)
        for file_path in sorted(content_dir.iterdir()):
            if file_path.suffix == ".json" and ".meta" in file_path.name:
                continue

            # Extract timestamp and format from filename
            filename = file_path.stem  # Without extension
            format_ext = file_path.suffix[1:]  # Remove leading dot

            # Try to load metadata
            meta_path = content_dir / f"{filename}.meta.json"
            metadata = {}
            if meta_path.exists():
                with open(meta_path) as f:
                    metadata = json.load(f)

            # Convert filename timestamp back to ISO format
            timestamp = filename.replace("-", ":")
            timestamp = metadata.get("timestamp", timestamp)

            versions.append(
                StoredVersion(
                    content_id=content_id,
                    timestamp=timestamp,
                    format=format_ext,
                    file_path=file_path,
                    metadata=metadata,
                )
            )

        return versions

    def cleanup(self, content_id: str | None = None) -> CleanupResult:
        """Remove old versions based on retention policy.

        Args:
            content_id: Specific content to clean, or None for all content

        Returns:
            CleanupResult with statistics

        Raises:
            ValueError: If retention_days is 0 (keep forever)
        """
        if self.retention_days == 0:
            raise ValueError("Cleanup disabled (retention_days=0)")

        files_removed = 0
        versions_removed = 0
        space_freed = 0

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        # Make cutoff timezone-aware for comparison
        if cutoff_date.tzinfo is None:
            cutoff_date = cutoff_date.replace(tzinfo=timezone.utc)

        # Determine which content IDs to process
        if content_id:
            content_dirs = [self.base_path / content_id]
        else:
            content_dirs = [d for d in self.base_path.iterdir() if d.is_dir()]

        for content_dir in content_dirs:
            if not content_dir.exists():
                continue

            versions = self.list_versions(content_dir.name)

            for version in versions:
                # Parse timestamp
                try:
                    version_date = datetime.fromisoformat(version.timestamp)
                    # Ensure timezone-aware for comparison
                    if version_date.tzinfo is None:
                        version_date = version_date.replace(tzinfo=timezone.utc)
                except ValueError:
                    continue

                # Remove if older than cutoff
                if version_date < cutoff_date:
                    # Get file size before deletion
                    size = version.file_path.stat().st_size
                    space_freed += size

                    # Remove content file
                    version.file_path.unlink()
                    files_removed += 1

                    # Remove metadata file if exists
                    meta_path = version.file_path.parent / (
                        version.file_path.stem + ".meta.json"
                    )
                    if meta_path.exists():
                        space_freed += meta_path.stat().st_size
                        meta_path.unlink()
                        files_removed += 1

                    versions_removed += 1

        return CleanupResult(files_removed, versions_removed, space_freed)

    def delete_content(self, content_id: str) -> None:
        """Permanently delete all versions of a content ID.

        Args:
            content_id: Content identifier to delete

        Raises:
            FileNotFoundError: If content_id doesn't exist
        """
        content_dir = self.base_path / content_id
        if not content_dir.exists():
            raise FileNotFoundError(f"Content not found: {content_id}")

        # Remove all files in the directory
        for file_path in content_dir.iterdir():
            file_path.unlink()

        # Remove the directory
        content_dir.rmdir()

    def list_content_ids(self) -> list[str]:
        """List all content IDs in storage.

        Returns:
            List of content IDs (directory names) in storage

        Example:
            >>> storage.list_content_ids()
            ['simple-readme', 'release-announcement', 'test-content']
        """
        if not self.base_path.exists():
            return []

        return [d.name for d in self.base_path.iterdir() if d.is_dir()]

    def delete_version(self, content_id: str, version_id: str | None = None) -> bool:
        """Delete specific version or all versions of content.

        Args:
            content_id: Content identifier
            version_id: Specific version timestamp to delete, or None to delete all

        Returns:
            True if content was deleted, False if not found

        Example:
            >>> # Delete specific version
            >>> storage.delete_version("test", "2025-10-15T12:00:00")
            True
            >>> # Delete all versions
            >>> storage.delete_version("test")
            True
        """
        content_dir = self.base_path / content_id

        if not content_dir.exists():
            return False

        if version_id is None:
            # Delete all versions (entire content directory)
            import shutil

            shutil.rmtree(content_dir)
            return True
        else:
            # Delete specific version by timestamp
            # Convert ISO timestamp to filename format
            safe_timestamp = version_id.replace(":", "-").replace(".", "-")

            # Find files matching this timestamp
            deleted = False
            for file_path in content_dir.iterdir():
                if file_path.stem.startswith(safe_timestamp):
                    file_path.unlink()
                    deleted = True

            return deleted

    def get_version_metadata(self, content_id: str, version_id: str) -> dict[str, Any]:
        """Get metadata for specific version including size.

        Args:
            content_id: Content identifier
            version_id: Version timestamp

        Returns:
            Dictionary with version_id, size_bytes, created, and other metadata

        Raises:
            FileNotFoundError: If version not found

        Example:
            >>> meta = storage.get_version_metadata("test", "2025-10-15T12:00:00")
            >>> print(meta['size_bytes'])
            1024
        """
        content_dir = self.base_path / content_id

        if not content_dir.exists():
            raise FileNotFoundError(f"Content not found: {content_id}")

        # Convert ISO timestamp to filename format
        safe_timestamp = version_id.replace(":", "-").replace(".", "-")

        # Find content file matching this timestamp
        content_file = None
        for file_path in content_dir.iterdir():
            if file_path.stem.startswith(
                safe_timestamp
            ) and not file_path.name.endswith(".meta.json"):
                content_file = file_path
                break

        if content_file is None:
            raise FileNotFoundError(f"Version not found: {content_id}/{version_id}")

        # Calculate size
        size_bytes = content_file.stat().st_size

        # Load metadata if exists
        meta_path = content_dir / f"{content_file.stem}.meta.json"
        metadata = {}
        if meta_path.exists():
            with open(meta_path) as f:
                metadata = json.load(f)

        return {
            "version_id": version_id,
            "size_bytes": size_bytes,
            "created": metadata.get("timestamp", version_id),
            **metadata,
        }
