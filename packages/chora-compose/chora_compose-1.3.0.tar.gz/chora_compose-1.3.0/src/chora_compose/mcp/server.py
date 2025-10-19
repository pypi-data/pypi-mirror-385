"""FastMCP server instance for chora-compose.

This module creates the main FastMCP server instance that will be used
by all tools, resources, and prompts.

The server uses stdio transport for communication with Claude Desktop.
"""

from fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP(
    name="chora-compose",
    instructions=(
        "Configuration-driven content generation and artifact assembly. "
        "Generate content from templates, assemble artifacts from content pieces, "
        "and manage generators through a simple, declarative configuration format."
    ),
    version="1.1.0",
)

# Import tools and resources to register them with the server
# This must happen after mcp is created but before main() runs
from . import config_tools, resource_providers, resources, tools  # noqa: F401, E402


def main() -> None:
    """Run the MCP server on stdio transport."""
    import os
    import sys

    print("Starting chora-compose MCP server...", file=sys.stderr)
    print("Server: chora-compose v1.1.0", file=sys.stderr)
    print("Transport: stdio", file=sys.stderr)
    print("Tools: 17 (13 content + 4 config lifecycle)", file=sys.stderr)
    config_tools_list = "draft_config, test_config, save_config, modify_config"
    print(f"  Config tools: {config_tools_list}", file=sys.stderr)
    print("-" * 60, file=sys.stderr)

    # Check ANTHROPIC_API_KEY for code_generation generator
    if not os.getenv("ANTHROPIC_API_KEY"):
        print(
            "⚠️  Warning: ANTHROPIC_API_KEY not found in environment.",
            file=sys.stderr,
        )
        print(
            "   code_generation generator will not be registered.",
            file=sys.stderr,
        )
        print(
            "   Set in claude_desktop_config.json 'env' or system environment.",
            file=sys.stderr,
        )
    else:
        print(
            "✓ ANTHROPIC_API_KEY detected - code_generation available", file=sys.stderr
        )

    print("-" * 60, file=sys.stderr)

    # Run server with stdio transport (for Claude Desktop)
    mcp.run(transport="stdio")


# Entry point for stdio transport
if __name__ == "__main__":
    main()
