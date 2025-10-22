"""
Main entry point for running the MCP server via python -m weaviate_mcp
"""

import asyncio
import sys

from weaviate_mcp.app import mcp  # Import instance from central location

# Import all tool modules that register components with the FastMCP instance
from weaviate_mcp.tools import (
    collection_tools,  # noqa: F401
    data_tools,  # noqa: F401
    ingestion_tools,  # noqa: F401
    schema_tools,  # noqa: F401
)


def main():
    """Main entry point for the MCP server."""
    try:
        asyncio.run(mcp.run())
    except KeyboardInterrupt:
        # Print to stderr to avoid breaking MCP protocol (stdout is for JSON-RPC only)
        print("\nShutting down MCP server...", file=sys.stderr)


if __name__ == "__main__":
    main()
