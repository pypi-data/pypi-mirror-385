"""FastMCP server instance - single source of truth.

This module creates the main FastMCP server instance in isolation to avoid
circular import issues between server.py and tools.py.

Import structure:
- instance.py: Creates mcp instance (no imports from mcp package)
- tools.py: Imports mcp from instance.py, decorates functions
- server.py: Imports mcp from instance.py, imports tools to register them
"""

from fastmcp import FastMCP

# Create MCP server instance - single source of truth
mcp = FastMCP(
    name="chora-compose",
    instructions=(
        "Configuration-driven content generation and artifact assembly. "
        "Generate content from templates, assemble artifacts from content pieces, "
        "and manage generators through a simple, declarative configuration format."
    ),
    version="1.1.0",
)
