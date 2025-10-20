"""MCP error handling.

This module provides error handling utilities for MCP tools, converting
Python exceptions into structured MCP error responses.

Day 1: Basic error handling structure
Days 4-5: Full error handling implementation
"""

from typing import Any


class MCPError(Exception):
    """Base MCP error with structured data.

    All MCP-specific errors should inherit from this class to ensure
    consistent error handling and reporting.
    """

    def __init__(
        self, code: str, message: str, details: dict[str, Any] | None = None
    ) -> None:
        """Initialize MCP error.

        Args:
            code: Error code (e.g., "config_not_found", "validation_failed")
            message: Human-readable error message
            details: Optional additional error details
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for JSON serialization.

        Returns:
            Dictionary with error structure suitable for MCP responses
        """
        return {
            "success": False,
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            },
        }


def handle_mcp_error(e: Exception) -> dict[str, Any]:
    """Convert Python exceptions to MCP error responses.

    This function provides a consistent way to handle errors in MCP tools,
    converting common Python exceptions into structured MCP error responses.

    Args:
        e: Exception to handle

    Returns:
        Dictionary with structured error information

    Error Codes:
        - config_not_found: Configuration file not found (FileNotFoundError)
        - validation_failed: Input validation failed (ValueError)
        - permission_denied: Permission error (PermissionError)
        - internal_error: Unexpected error (all others)
    """
    if isinstance(e, MCPError):
        return e.to_dict()
    elif isinstance(e, FileNotFoundError):
        return {
            "success": False,
            "error": {
                "code": "config_not_found",
                "message": str(e),
                "details": {"type": "FileNotFoundError", "path": str(e)},
            },
        }
    elif isinstance(e, ValueError):
        return {
            "success": False,
            "error": {
                "code": "validation_failed",
                "message": str(e),
                "details": {"type": "ValueError"},
            },
        }
    elif isinstance(e, PermissionError):
        return {
            "success": False,
            "error": {
                "code": "permission_denied",
                "message": str(e),
                "details": {"type": "PermissionError"},
            },
        }
    elif isinstance(e, NotImplementedError):
        return {
            "success": False,
            "error": {
                "code": "not_implemented",
                "message": str(e),
                "details": {"type": "NotImplementedError"},
            },
        }
    else:
        return {
            "success": False,
            "error": {
                "code": "internal_error",
                "message": str(e),
                "details": {"type": type(e).__name__},
            },
        }
