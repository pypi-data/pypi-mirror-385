"""MCP Resources module for chora-compose.

This module provides MCP resource providers including capability discovery
resources that enable agents to introspect server features dynamically.

Resources:
- capabilities://server - Server metadata and feature flags
- capabilities://tools - Tool inventory with schemas
- capabilities://resources - Resource URI catalog
- capabilities://generators - Generator registry

Version: 1.1.0
"""

from chora_compose.mcp.resources.capabilities import (
    GeneratorCapability,
    ResourceCapability,
    ServerCapabilities,
    ToolCapability,
    get_generator_capabilities,
    get_resource_capabilities,
    get_server_capabilities,
    get_tool_capabilities,
)

__all__ = [
    # Pydantic models
    "ServerCapabilities",
    "ToolCapability",
    "ResourceCapability",
    "GeneratorCapability",
    # Async resource providers
    "get_server_capabilities",
    "get_tool_capabilities",
    "get_resource_capabilities",
    "get_generator_capabilities",
]
