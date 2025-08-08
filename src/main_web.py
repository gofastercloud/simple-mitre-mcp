#!/usr/bin/env python3
"""
MITRE ATT&CK MCP Server

A Model Context Protocol server that provides structured access to the MITRE ATT&CK framework
for Large Language Models. This server enables security analysts and researchers to query
and explore the MITRE ATT&CK knowledge base through natural language interactions.
"""

import logging
from .mcp_server import MCPServer
from .data_loader import DataLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the MCP server."""
    logger.info("Starting MITRE ATT&CK MCP Server...")

    try:
        # Initialize data loader and load MITRE ATT&CK data
        logger.info("Loading MITRE ATT&CK data...")
        data_loader = DataLoader()
        data_loader.load_data_source("mitre_attack")
        logger.info("MITRE ATT&CK data loaded successfully")

        # Create MCP server with loaded data
        mcp_server = MCPServer(data_loader)

        logger.info("MCP server starting with streamable-http transport")
        mcp_server.run(transport="streamable-http")

    except Exception:
        logger.error("Failed to start MCP server: {e}")
        raise


if __name__ == "__main__":
    main()
