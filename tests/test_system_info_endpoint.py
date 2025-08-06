"""
Unit tests for the system information endpoint functionality.

This module tests the /system_info endpoint and related data statistics methods
in the HTTP proxy server.
"""

import asyncio
import json
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

import sys
from pathlib import Path

from http_proxy import HTTPProxy, create_http_proxy_server

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestSystemInfoEndpoint(AioHTTPTestCase):
    """Test cases for the system information endpoint."""

    async def get_application(self):
        """Create test application with mocked MCP server."""
        # Create mock MCP server
        mock_mcp_server = Mock()
        mock_data_loader = Mock()

        # Mock data loader with sample data
        sample_data = {
            "techniques": [{"id": "T1001", "name": "Test Technique 1"}] * 100,
            "tactics": [{"id": "TA0001", "name": "Test Tactic 1"}] * 14,
            "groups": [{"id": "G0001", "name": "Test Group 1"}] * 50,
            "mitigations": [{"id": "M0001", "name": "Test Mitigation 1"}] * 75,
            "relationships": [
                {"type": "uses", "source_id": "G0001", "target_id": "T1001"}
            ]
            * 200,
        }

        mock_data_loader.get_cached_data.return_value = sample_data
        mock_mcp_server.data_loader = mock_data_loader

        # Create HTTP proxy with mocked server
        proxy = HTTPProxy(mock_mcp_server)
        return proxy.app

    @unittest_run_loop
    async def test_system_info_endpoint_success(self):
        """Test successful system info endpoint response."""
        resp = await self.client.request("GET", "/system_info")

        self.assertEqual(resp.status, 200)

        data = await resp.json()

        # Verify response structure
        self.assertIn("server_info", data)
        self.assertIn("data_statistics", data)
        self.assertIn("capabilities", data)

        # Verify server info
        server_info = data["server_info"]
        self.assertIn("version", server_info)
        self.assertIn("mcp_protocol_version", server_info)
        self.assertIn("startup_time", server_info)
        self.assertIn("data_source", server_info)

        # Verify data statistics
        stats = data["data_statistics"]
        self.assertEqual(stats["techniques_count"], 100)
        self.assertEqual(stats["tactics_count"], 14)
        self.assertEqual(stats["groups_count"], 50)
        self.assertEqual(stats["mitigations_count"], 75)
        self.assertEqual(stats["relationships_count"], 200)
        self.assertTrue(stats["data_loaded"])

        # Verify capabilities
        capabilities = data["capabilities"]
        self.assertEqual(capabilities["basic_tools"], 5)
        self.assertEqual(capabilities["advanced_tools"], 3)
        self.assertEqual(capabilities["total_tools"], 8)
        self.assertTrue(capabilities["web_interface"])
        self.assertTrue(capabilities["api_access"])

    @unittest_run_loop
    async def test_system_info_no_data_loaded(self):
        """Test system info endpoint when no data is loaded."""
        # Create proxy with no data
        mock_mcp_server = Mock()
        mock_data_loader = Mock()
        mock_data_loader.get_cached_data.return_value = None
        mock_mcp_server.data_loader = mock_data_loader

        proxy = HTTPProxy(mock_mcp_server)

        # Make request using the proxy's app directly
        request = Mock()
        response = await proxy.handle_system_info(request)

        # Parse response
        response_text = response.text
        data = json.loads(response_text)

        # Verify data statistics show no data
        stats = data["data_statistics"]
        self.assertEqual(stats["techniques_count"], 0)
        self.assertEqual(stats["tactics_count"], 0)
        self.assertEqual(stats["groups_count"], 0)
        self.assertEqual(stats["mitigations_count"], 0)
        self.assertEqual(stats["relationships_count"], 0)
        self.assertFalse(stats["data_loaded"])

    @unittest_run_loop
    async def test_system_info_no_data_loader(self):
        """Test system info endpoint when data loader is not available."""
        # Create proxy with no data loader
        mock_mcp_server = Mock()
        mock_mcp_server.data_loader = None

        proxy = HTTPProxy(mock_mcp_server)

        # Make request using the proxy's app directly
        request = Mock()
        response = await proxy.handle_system_info(request)

        # Parse response
        response_text = response.text
        data = json.loads(response_text)

        # Verify data statistics show no data
        stats = data["data_statistics"]
        self.assertEqual(stats["techniques_count"], 0)
        self.assertEqual(stats["tactics_count"], 0)
        self.assertEqual(stats["groups_count"], 0)
        self.assertEqual(stats["mitigations_count"], 0)
        self.assertEqual(stats["relationships_count"], 0)
        self.assertFalse(stats["data_loaded"])


class TestDataStatisticsMethods:
    """Test cases for data statistics helper methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_mcp_server = Mock()
        self.mock_data_loader = Mock()
        self.mock_mcp_server.data_loader = self.mock_data_loader
        self.proxy = HTTPProxy(self.mock_mcp_server)

    @pytest.mark.asyncio
    async def test_get_data_statistics_with_data(self):
        """Test _get_data_statistics with loaded data."""
        # Mock data
        sample_data = {
            "techniques": [
                {"id": f"T{i:04d}"} for i in range(1, 501)
            ],  # 500 techniques
            "tactics": [{"id": f"TA{i:04d}"} for i in range(1, 15)],  # 14 tactics
            "groups": [{"id": f"G{i:04d}"} for i in range(1, 101)],  # 100 groups
            "mitigations": [
                {"id": f"M{i:04d}"} for i in range(1, 201)
            ],  # 200 mitigations
            "relationships": [
                {"type": "uses"} for _ in range(1000)
            ],  # 1000 relationships
        }

        self.mock_data_loader.get_cached_data.return_value = sample_data

        stats = await self.proxy._get_data_statistics()

        assert stats["techniques_count"] == 500
        assert stats["tactics_count"] == 14
        assert stats["groups_count"] == 100
        assert stats["mitigations_count"] == 200
        assert stats["relationships_count"] == 1000
        assert stats["data_loaded"] is True
        assert "last_updated" in stats

    @pytest.mark.asyncio
    async def test_get_data_statistics_no_data(self):
        """Test _get_data_statistics with no data loaded."""
        self.mock_data_loader.get_cached_data.return_value = None

        stats = await self.proxy._get_data_statistics()

        assert stats["techniques_count"] == 0
        assert stats["tactics_count"] == 0
        assert stats["groups_count"] == 0
        assert stats["mitigations_count"] == 0
        assert stats["relationships_count"] == 0
        assert stats["data_loaded"] is False
        assert stats["last_updated"] is None

    @pytest.mark.asyncio
    async def test_get_data_statistics_error_handling(self):
        """Test _get_data_statistics error handling."""
        # Mock data loader to raise exception
        self.mock_data_loader.get_cached_data.side_effect = Exception("Test error")

        stats = await self.proxy._get_data_statistics()

        assert stats["techniques_count"] == 0
        assert stats["tactics_count"] == 0
        assert stats["groups_count"] == 0
        assert stats["mitigations_count"] == 0
        assert stats["relationships_count"] == 0
        assert stats["data_loaded"] is False
        assert stats["last_updated"] is None
        assert "error" in stats

    @pytest.mark.asyncio
    async def test_count_relationships_from_main_data(self):
        """Test _count_relationships when relationships are in main data."""
        sample_data = {"relationships": [{"type": "uses"} for _ in range(150)]}

        self.mock_data_loader.get_cached_data.return_value = sample_data

        count = await self.proxy._count_relationships()

        assert count == 150

    @pytest.mark.asyncio
    async def test_count_relationships_from_separate_cache(self):
        """Test _count_relationships when relationships are in separate cache."""
        # Mock main data without relationships
        self.mock_data_loader.get_cached_data.side_effect = [
            {"techniques": []},  # Main data call
            [{"type": "uses"} for _ in range(75)],  # Relationships cache call
        ]

        count = await self.proxy._count_relationships()

        assert count == 75

    @pytest.mark.asyncio
    async def test_count_relationships_no_data(self):
        """Test _count_relationships with no data."""
        self.mock_data_loader.get_cached_data.return_value = None

        count = await self.proxy._count_relationships()

        assert count == 0

    @pytest.mark.asyncio
    async def test_count_relationships_no_data_loader(self):
        """Test _count_relationships with no data loader."""
        self.proxy.mcp_server.data_loader = None

        count = await self.proxy._count_relationships()

        assert count == 0

    @pytest.mark.asyncio
    async def test_count_relationships_error_handling(self):
        """Test _count_relationships error handling."""
        self.mock_data_loader.get_cached_data.side_effect = Exception("Test error")

        count = await self.proxy._count_relationships()

        assert count == 0


class TestSystemInfoIntegration:
    """Integration tests for system info functionality."""

    @pytest.mark.asyncio
    async def test_system_info_endpoint_cors(self):
        """Test that system info endpoint has proper CORS setup."""
        # This would be tested in a full integration test
        # For now, we verify the route is properly registered
        mock_mcp_server = Mock()
        proxy = HTTPProxy(mock_mcp_server)

        # Check that the route exists
        routes = [route.resource.canonical for route in proxy.app.router.routes()]
        assert "/system_info" in routes

    def test_startup_time_initialization(self):
        """Test that startup time is properly initialized."""
        mock_mcp_server = Mock()
        proxy = HTTPProxy(mock_mcp_server)

        assert hasattr(proxy, "startup_time")
        assert isinstance(proxy.startup_time, datetime)

    @pytest.mark.asyncio
    async def test_system_info_response_format(self):
        """Test that system info response has the correct format."""
        mock_mcp_server = Mock()
        mock_data_loader = Mock()
        mock_data_loader.get_cached_data.return_value = {
            "techniques": [],
            "tactics": [],
            "groups": [],
            "mitigations": [],
            "relationships": [],
        }
        mock_mcp_server.data_loader = mock_data_loader

        proxy = HTTPProxy(mock_mcp_server)
        request = Mock()

        response = await proxy.handle_system_info(request)
        data = json.loads(response.text)

        # Verify all required fields are present
        required_fields = {
            "server_info": [
                "version",
                "mcp_protocol_version",
                "startup_time",
                "data_source",
            ],
            "data_statistics": [
                "techniques_count",
                "tactics_count",
                "groups_count",
                "mitigations_count",
                "relationships_count",
                "data_loaded",
            ],
            "capabilities": [
                "basic_tools",
                "advanced_tools",
                "total_tools",
                "web_interface",
                "api_access",
            ],
        }

        for section, fields in required_fields.items():
            assert section in data
            for field in fields:
                assert field in data[section]


if __name__ == "__main__":
    pytest.main([__file__])
