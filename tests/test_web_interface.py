"""
Tests for web interface HTTP communication.

This module contains tests for verifying the web interface can properly
communicate with the MCP server via HTTP requests.
"""

import asyncio
import json
import aiohttp
import logging
import pytest
import threading
import time
import os
from unittest.mock import Mock, patch
from src.mcp_server import create_mcp_server
from src.data_loader import DataLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration with environment variable support
MCP_HTTP_HOST = os.getenv("MCP_HTTP_HOST", "localhost")
MCP_HTTP_PORT = int(os.getenv("MCP_HTTP_PORT", "8000"))
MCP_HTTP_URL = f"http://{MCP_HTTP_HOST}:{MCP_HTTP_PORT}"


class TestWebInterface:
    """Test cases for web interface HTTP communication."""

    @pytest.fixture
    def mock_data_loader(self):
        """Create a mock data loader with sample data for testing."""
        mock_loader = Mock(spec=DataLoader)

        # Sample test data
        sample_data = {
            "tactics": [
                {
                    "id": "TA0001",
                    "name": "Initial Access",
                    "description": "The adversary is trying to get into your network.",
                }
            ],
            "techniques": [
                {
                    "id": "T1055",
                    "name": "Process Injection",
                    "description": "Adversaries may inject code into processes.",
                    "tactics": ["TA0002"],
                    "platforms": ["Windows", "Linux"],
                    "mitigations": ["M1040"],
                }
            ],
            "groups": [
                {
                    "id": "G0016",
                    "name": "APT29",
                    "aliases": ["Cozy Bear"],
                    "description": "APT29 is a threat group.",
                    "techniques": ["T1055"],
                }
            ],
            "mitigations": [
                {
                    "id": "M1040",
                    "name": "Behavior Prevention on Endpoint",
                    "description": "Use capabilities to prevent suspicious behavior patterns.",
                }
            ],
        }

        mock_loader.get_cached_data.return_value = sample_data
        return mock_loader

    @pytest.mark.asyncio
    async def test_json_rpc_tools_list_format(self, mock_data_loader):
        """Test that JSON-RPC tools/list request format is correct."""
        app = create_mcp_server(mock_data_loader)

        # Test the internal method that would handle tools/list
        tools = await app.list_tools()

        assert tools is not None
        assert len(tools) == 8

        # Verify tool structure matches what web interface expects
        for tool in tools:
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "inputSchema")
            assert isinstance(tool.inputSchema, dict)

    @pytest.mark.asyncio
    async def test_json_rpc_tool_call_format(self, mock_data_loader):
        """Test that JSON-RPC tools/call request format is correct."""
        app = create_mcp_server(mock_data_loader)

        # Test list_tactics tool call
        result, _ = await app.call_tool("list_tactics", {})

        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        assert isinstance(result[0].text, str)
        assert len(result[0].text) > 0

    @pytest.mark.asyncio
    async def test_search_tool_with_parameters(self, mock_data_loader):
        """Test search tool with parameters as web interface would use."""
        app = create_mcp_server(mock_data_loader)

        # Test search_attack tool call with query parameter
        result, _ = await app.call_tool("search_attack", {"query": "process"})

        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        assert "process" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_technique_detail_tool(self, mock_data_loader):
        """Test technique detail tool as web interface would use."""
        app = create_mcp_server(mock_data_loader)

        # Test get_technique tool call
        result, _ = await app.call_tool("get_technique", {"technique_id": "T1055"})

        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        assert "T1055" in result[0].text
        assert "Process Injection" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling_for_web_interface(self, mock_data_loader):
        """Test error handling as web interface would encounter."""
        app = create_mcp_server(mock_data_loader)

        # Test with invalid technique ID
        result, _ = await app.call_tool("get_technique", {"technique_id": "INVALID"})

        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        assert "not found" in result[0].text.lower()

    def test_web_interface_tool_parameters(self, mock_data_loader):
        """Test that tool parameters match web interface expectations."""
        app = create_mcp_server(mock_data_loader)

        # Get tools synchronously for parameter validation
        import asyncio

        tools = asyncio.run(app.list_tools())
        tool_dict = {tool.name: tool for tool in tools}

        # Verify search_attack parameters
        search_tool = tool_dict["search_attack"]
        assert "query" in search_tool.inputSchema["properties"]
        assert search_tool.inputSchema["properties"]["query"]["type"] == "string"
        assert "query" in search_tool.inputSchema.get("required", [])

        # Verify get_technique parameters
        technique_tool = tool_dict["get_technique"]
        assert "technique_id" in technique_tool.inputSchema["properties"]
        assert (
            technique_tool.inputSchema["properties"]["technique_id"]["type"] == "string"
        )
        assert "technique_id" in technique_tool.inputSchema.get("required", [])

        # Verify list_tactics has no required parameters
        tactics_tool = tool_dict["list_tactics"]
        assert len(tactics_tool.inputSchema["properties"]) == 0
        assert tactics_tool.inputSchema.get("required", []) == []


class TestWebInterfaceIntegration:
    """Integration tests for web interface with actual HTTP requests."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_http_request_format(self):
        """Test actual HTTP request format (requires running server)."""
        # This test would require a running server
        # Skip if server is not available
        pytest.skip("Integration test requires running MCP server")

        async with aiohttp.ClientSession() as session:
            # Test tools/list request
            payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}

            try:
                async with session.post(MCP_HTTP_URL, json=payload) as response:
                    assert response.status == 200
                    result = await response.json()
                    assert "result" in result
                    assert "tools" in result["result"]
            except aiohttp.ClientError:
                pytest.skip(f"MCP server not running on {MCP_HTTP_URL}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tool_call_http_format(self):
        """Test actual tool call HTTP format (requires running server)."""
        pytest.skip("Integration test requires running MCP server")

        async with aiohttp.ClientSession() as session:
            # Test tools/call request
            payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "list_tactics", "arguments": {}},
            }

            try:
                async with session.post(MCP_HTTP_URL, json=payload) as response:
                    assert response.status == 200
                    result = await response.json()
                    assert "result" in result
                    assert "content" in result["result"]
            except aiohttp.ClientError:
                pytest.skip(f"MCP server not running on {MCP_HTTP_URL}")


if __name__ == "__main__":
    pytest.main([__file__])
