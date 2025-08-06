#!/usr/bin/env python3
"""
MITRE ATT&CK MCP Server (STDIO Transport)

A Model Context Protocol server that provides structured access to the MITRE ATT&CK framework
for Large Language Models using STDIO transport for direct MCP client integration.

This version uses STDIO transport, which is required for MCP client integration with AI assistants
like Claude Desktop, ChatGPT, and other MCP-compatible clients.
"""

import logging
from .mcp_server import MCPServer
from .data_loader import DataLoader

# Configure logging for stdio transport (reduced verbosity)
logging.basicConfig(
    level=logging.WARNING,  # Reduced to WARNING to avoid interference with STDIO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp_server.log"),  # Log to file instead of stderr
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the MCP server with STDIO transport."""
    try:
        # Initialize data loader and load MITRE ATT&CK data
        data_loader = DataLoader()
        data_loader.load_data_source("mitre_attack")

        # Create MCP server with loaded data
        mcp_server = MCPServer(data_loader)

        # Run with STDIO transport for MCP client integration
        mcp_server.run(transport="stdio")

    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        raise


if __name__ == "__main__":
    main()
