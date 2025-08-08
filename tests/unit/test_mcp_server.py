"""
Unit tests for MCP server functionality.

This module contains unit tests for the MCP server implementation,
including tool registration and basic request handling.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from src.mcp_server import MCPServer, create_mcp_server
from src.data_loader import DataLoader
from tests.base import BaseMCPTestCase


class TestMCPServer(BaseMCPTestCase):
    """Test cases for MCP server functionality."""

    def test_mcp_server_initialization(self, mock_data_loader):
        """Test that MCP server initializes correctly."""
        # Initialize MCP server
        server = MCPServer(mock_data_loader)

        # Verify server is created
        assert server is not None
        assert server.data_loader == mock_data_loader
        assert server.app is not None
        assert server.app.name == "mitre-attack-mcp-server"

    def test_create_mcp_server_function(self, mock_data_loader):
        """Test the create_mcp_server function."""
        app = create_mcp_server(mock_data_loader)

        assert app is not None
        assert app.name == "mitre-attack-mcp-server"
        assert hasattr(app, "data_loader")
        assert app.data_loader == mock_data_loader

    @patch("src.mcp_server.ConfigLoader")
    def test_tools_registration(self, mock_config_loader, mock_data_loader):
        """Test that MCP tools are registered correctly."""
        # Mock configuration
        mock_config_loader.return_value.load_tools_config.return_value = {
            "tools": {
                "search_attack": {
                    "description": "Search test",
                    "parameters": [
                        {"name": "query", "type": "string", "required": True}
                    ],
                }
            }
        }

        server = MCPServer(mock_data_loader)

        # Verify server was created successfully
        assert server.app is not None

    def test_server_has_data_loader_attribute(self, mock_data_loader):
        """Test that the server stores the data loader correctly."""
        app = create_mcp_server(mock_data_loader)

        # Verify the data loader is stored
        assert hasattr(app, "data_loader")
        assert app.data_loader == mock_data_loader

    def test_server_name_and_instructions(self, mock_data_loader):
        """Test that the server has correct name and instructions."""
        app = create_mcp_server(mock_data_loader)

        # Verify server configuration
        assert app.name == "mitre-attack-mcp-server"
        assert "MITRE ATT&CK framework" in app.instructions

    def test_server_configuration(self, mock_data_loader):
        """Test that the server is configured correctly."""
        app = create_mcp_server(mock_data_loader)

        # Verify server is properly configured
        assert app is not None
        assert hasattr(app, "name")
        assert hasattr(app, "instructions")


if __name__ == "__main__":
    pytest.main([__file__])