"""MCP utility functions.

This module provides helper functions used across MCP tools.

Day 1: Basic utilities
Days 4-5: Additional utilities as needed
"""

import time
from typing import Any, Callable


def measure_duration(func: Callable) -> tuple[Any, int]:
    """Measure function execution duration.

    Args:
        func: Function to measure (should be a callable with no args)

    Returns:
        Tuple of (function result, duration in milliseconds)
    """
    start_time = time.time()
    result = func()
    duration_ms = int((time.time() - start_time) * 1000)
    return result, duration_ms


async def measure_duration_async(func: Callable) -> tuple[Any, int]:
    """Measure async function execution duration.

    Args:
        func: Async function to measure (should be a callable with no args)

    Returns:
        Tuple of (function result, duration in milliseconds)
    """
    start_time = time.time()
    result = await func()
    duration_ms = int((time.time() - start_time) * 1000)
    return result, duration_ms


def sanitize_config_id(config_id: str) -> str:
    """Sanitize configuration ID to prevent path traversal.

    Args:
        config_id: Configuration ID from user input

    Returns:
        Sanitized configuration ID

    Raises:
        ValueError: If config ID contains invalid characters
    """
    # Remove any path separators
    if "/" in config_id or "\\" in config_id:
        raise ValueError(
            f"Invalid config ID: '{config_id}' - cannot contain path separators"
        )

    # Remove any parent directory references
    if ".." in config_id:
        msg = f"Invalid config ID: '{config_id}' - "
        msg += "cannot contain parent directory references"
        raise ValueError(msg)

    return config_id


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 KB", "2.3 MB")
    """
    size_float = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size_float < 1024.0:
            return f"{size_float:.1f} {unit}"
        size_float /= 1024.0
    return f"{size_float:.1f} TB"
