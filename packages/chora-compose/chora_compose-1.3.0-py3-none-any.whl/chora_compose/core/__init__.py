"""Core module for chora-compose."""

from pathlib import Path

from chora_compose.core.config_loader import ConfigLoader

__all__ = ["ConfigLoader", "get_config_loader"]

_config_loader_instance: ConfigLoader | None = None


def get_config_loader(config_root: Path | str | None = None) -> ConfigLoader:
    """Get or create config loader singleton.

    This provides a shared config loader instance across all MCP tools to ensure
    consistent configuration access and avoid multiple loader instances.

    Args:
        config_root: Root directory for configurations. Defaults to "configs"
                    in the current working directory.

    Returns:
        Shared ConfigLoader instance

    Example:
        >>> loader = get_config_loader()
        >>> config = loader.load_content_config("simple-readme")
    """
    global _config_loader_instance

    if _config_loader_instance is None:
        if config_root is None:
            config_root = Path("configs")
        _config_loader_instance = ConfigLoader(config_root=config_root)

    return _config_loader_instance
