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
    """Run the MCP server with configurable transport.

    Transport options:
    - stdio: For Claude Desktop integration (default if no env vars set)
    - sse: HTTP/SSE transport for n8n and other HTTP clients (Docker deployment)

    Configuration via environment variables:
    - MCP_TRANSPORT: Transport type (stdio or sse)
    - MCP_SERVER_HOST: Host to bind to (default: 127.0.0.1 for stdio, 0.0.0.0 for sse)
    - MCP_SERVER_PORT: Port for HTTP transport (default: 8000)
    """
    import os
    import sys

    # Determine transport from environment (default: stdio for backward compatibility)
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    host = os.getenv("MCP_SERVER_HOST")
    port = int(os.getenv("MCP_SERVER_PORT", "8000"))

    # Auto-detect host if not specified
    if host is None:
        host = "0.0.0.0" if transport == "sse" else "127.0.0.1"

    print("Starting chora-compose MCP server...", file=sys.stderr)
    print("Server: chora-compose v1.1.0", file=sys.stderr)
    print(f"Transport: {transport}", file=sys.stderr)
    if transport == "sse":
        print(f"Listening on: http://{host}:{port}/sse", file=sys.stderr)
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
        if transport == "stdio":
            print(
                "   Set in claude_desktop_config.json 'env' or system environment.",
                file=sys.stderr,
            )
        else:
            print(
                "   Set in docker-compose.yml or .env file.",
                file=sys.stderr,
            )
    else:
        print(
            "✓ ANTHROPIC_API_KEY detected - code_generation available", file=sys.stderr
        )

    print("-" * 60, file=sys.stderr)

    # Run server with configured transport
    if transport == "sse":
        print(f"Server ready at http://{host}:{port}/sse", file=sys.stderr)
        print("Waiting for connections...", file=sys.stderr)
        mcp.run(transport="sse", host=host, port=port)
    else:
        # Default: stdio transport (for Claude Desktop)
        mcp.run(transport="stdio")


# Entry point for stdio transport
if __name__ == "__main__":
    main()
