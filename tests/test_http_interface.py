"""
Tests for MCP server HTTP interface analysis.

This module contains tests for understanding and analyzing the HTTP interface
of the FastMCP server implementation.
"""

import asyncio
import json
import logging
import pytest
from src.mcp_server import create_mcp_server
from src.data_loader import DataLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestMCPHTTPInterface:
    """Test cases for MCP server HTTP interface analysis."""

    @pytest.fixture
    def mcp_server_with_data(self):
        """Create MCP server with loaded data for testing."""
        try:
            # Initialize data loader
            data_loader = DataLoader()
            logger.info("Data loaded successfully")

            # Create MCP server
            app = create_mcp_server(data_loader)
            logger.info("MCP server created")

            return app
        except Exception:
            logger.error("Error creating server: {e}")
            pytest.skip("Could not load data: {e}")

    @pytest.mark.asyncio
    async def test_mcp_server_tool_listing(self, mcp_server_with_data):
        """Test that MCP server can list available tools."""
        app = mcp_server_with_data

        # Test list_tools
        tools = await app.list_tools()
        assert tools is not None
        assert len(tools) == 8

        tool_names = [tool.name for tool in tools]
        expected_tools = [
            'search_attack', 'get_technique', 'list_tactics',
            'get_group_techniques', 'get_technique_mitigations'
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

        logger.info("Available tools: {tool_names}")

    @pytest.mark.asyncio
    async def test_tool_execution(self, mcp_server_with_data):
        """Test basic tool execution."""
        app = mcp_server_with_data

        # Test a simple tool call
        result, _ = await app.call_tool('list_tactics', {})
        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        assert len(result[0].text) > 0

        logger.info("Tool result type: {type(result)}")
        logger.info("Tool result content length: {len(result[0].text)}")

    @pytest.mark.asyncio
    async def test_tool_schemas_for_web_interface(self, mcp_server_with_data):
        """Test and document tool schemas for web interface development."""
        app = mcp_server_with_data

        tools = await app.list_tools()

        # Verify each tool has proper schema
        for tool in tools:
            assert tool.name is not None
            assert tool.description is not None
            assert tool.inputSchema is not None
            assert isinstance(tool.inputSchema, dict)

            # Log schema for web interface development
            logger.info("\nTool: {tool.name}")
            logger.info("Description: {tool.description}")
            logger.info("Input Schema: {json.dumps(tool.inputSchema, indent=2)}")

        # Verify specific tool schemas
        tool_dict = {tool.name: tool for tool in tools}

        # search_attack should require query parameter
        search_tool = tool_dict['search_attack']
        assert 'query' in search_tool.inputSchema['properties']
        assert 'query' in search_tool.inputSchema.get('required', [])

        # list_tactics should have no required parameters
        tactics_tool = tool_dict['list_tactics']
        assert len(tactics_tool.inputSchema['properties']) == 0


if __name__ == '__main__':
    pytest.main([__file__])
