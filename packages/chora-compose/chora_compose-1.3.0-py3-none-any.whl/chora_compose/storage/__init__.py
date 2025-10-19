"""Storage module for chora-compose."""

from pathlib import Path

from chora_compose.storage.ephemeral import EphemeralStorageManager
from chora_compose.storage.ephemeral_config import EphemeralConfigManager

__all__ = [
    "EphemeralStorageManager",
    "EphemeralConfigManager",
    "get_ephemeral_storage",
    "get_ephemeral_config_manager",
]

_storage_instance: EphemeralStorageManager | None = None
_config_manager_instance: EphemeralConfigManager | None = None


def get_ephemeral_storage(
    base_path: Path | str | None = None,
) -> EphemeralStorageManager:
    """Get or create ephemeral storage manager singleton.

    This provides a shared storage instance across all MCP tools to ensure
    consistent storage state and avoid multiple manager instances.

    Args:
        base_path: Root directory for ephemeral storage. Defaults to "ephemeral"
                  in the current working directory.

    Returns:
        Shared EphemeralStorageManager instance

    Example:
        >>> storage = get_ephemeral_storage()
        >>> storage.save("test", "content")
    """
    global _storage_instance

    if _storage_instance is None:
        if base_path is None:
            base_path = Path("ephemeral")
        _storage_instance = EphemeralStorageManager(base_path=base_path)

    return _storage_instance


def get_ephemeral_config_manager(
    base_path: Path | str | None = None,
) -> EphemeralConfigManager:
    """Get or create ephemeral config manager singleton.

    This provides a shared config manager instance across all MCP tools
    for managing draft configurations.

    Args:
        base_path: Root directory for ephemeral storage. Defaults to "ephemeral"
                  in the current working directory. Drafts stored in {base_path}/drafts/

    Returns:
        Shared EphemeralConfigManager instance

    Example:
        >>> config_mgr = get_ephemeral_config_manager()
        >>> draft = config_mgr.create_draft("content", {...})
    """
    global _config_manager_instance

    if _config_manager_instance is None:
        if base_path is None:
            base_path = Path("ephemeral")
        _config_manager_instance = EphemeralConfigManager(base_path=base_path)

    return _config_manager_instance
