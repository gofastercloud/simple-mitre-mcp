"""
Consolidated HTTP interface and web interface integration tests.

This module consolidates all HTTP interface tests including:
- HTTP proxy server functionality
- Web interface communication
- JSON-RPC protocol handling
- API endpoint testing
- Error handling and validation
"""

import pytest
import asyncio
import json
import aiohttp
import os
import time
from unittest.mock import Mock, patch, AsyncMock
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase

from src.http_proxy import HTTPProxy, create_http_proxy_server
from src.mcp_server import create_mcp_server
from src.data_loader import DataLoader


# Configuration with environment variable support
MCP_HTTP_HOST = os.getenv("MCP_HTTP_HOST", "localhost")
MCP_HTTP_PORT = int(os.getenv("MCP_HTTP_PORT", "8000"))
MCP_HTTP_URL = f"http://{MCP_HTTP_HOST}:{MCP_HTTP_PORT}"


class TestHTTPInterfaceIntegration:
    """Test HTTP interface integration with MCP server."""

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

    @pytest.fixture
    def mcp_server_with_data(self, mock_data_loader):
        """Create MCP server with loaded data for testing."""
        return create_mcp_server(mock_data_loader)

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
            "search_attack",
            "get_technique",
            "list_tactics",
            "get_group_techniques",
            "get_technique_mitigations",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_tool_execution(self, mcp_server_with_data):
        """Test basic tool execution."""
        app = mcp_server_with_data

        # Test a simple tool call
        result, _ = await app.call_tool("list_tactics", {})
        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        assert len(result[0].text) > 0

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

        # Verify specific tool schemas
        tool_dict = {tool.name: tool for tool in tools}

        # search_attack should require query parameter
        search_tool = tool_dict["search_attack"]
        assert "query" in search_tool.inputSchema["properties"]
        assert "query" in search_tool.inputSchema.get("required", [])

        # list_tactics should have no required parameters
        tactics_tool = tool_dict["list_tactics"]
        assert len(tactics_tool.inputSchema["properties"]) == 0

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


class TestHTTPProxyIntegration(AioHTTPTestCase):
    """Test HTTP proxy integration with aiohttp."""

    async def get_application(self):
        """Create test application with mocked MCP server."""
        # Create mock MCP server
        mock_mcp_server = Mock()
        mock_mcp_server.call_tool = AsyncMock()

        # Create mock data loader with sample data
        mock_data_loader = Mock()
        mock_data_loader.get_cached_data = Mock()

        # Sample test data
        sample_data = {
            "techniques": [
                {
                    "id": "T1055",
                    "name": "Process Injection",
                    "description": "Test technique",
                },
                {
                    "id": "T1059",
                    "name": "Command and Scripting Interpreter",
                    "description": "Test technique 2",
                },
            ],
            "tactics": [
                {"id": "TA0001", "name": "Initial Access"},
                {"id": "TA0002", "name": "Execution"},
            ],
            "groups": [
                {"id": "G0016", "name": "APT29", "aliases": ["Cozy Bear", "The Dukes"]},
                {"id": "G0007", "name": "APT1", "aliases": ["Comment Crew"]},
            ],
            "mitigations": [
                {"id": "M1013", "name": "Application Developer Guidance"},
                {"id": "M1026", "name": "Privileged Account Management"},
            ],
            "relationships": [],
        }

        mock_data_loader.get_cached_data.return_value = sample_data
        mock_mcp_server.data_loader = mock_data_loader

        # Create HTTP proxy with mocked server
        proxy = HTTPProxy(mock_mcp_server)
        return proxy.app

    async def test_system_info_endpoint(self):
        """Test the /system_info endpoint."""
        resp = await self.client.request("GET", "/system_info")
        self.assertEqual(resp.status, 200)

        data = await resp.json()

        # Check response structure
        self.assertIn("server_info", data)
        self.assertIn("data_statistics", data)
        self.assertIn("capabilities", data)

        # Check server info
        server_info = data["server_info"]
        self.assertIn("version", server_info)
        self.assertIn("mcp_protocol_version", server_info)
        self.assertIn("startup_time", server_info)
        self.assertIn("data_source", server_info)

        # Check capabilities
        capabilities = data["capabilities"]
        self.assertEqual(capabilities["basic_tools"], 5)
        self.assertEqual(capabilities["advanced_tools"], 3)
        self.assertEqual(capabilities["total_tools"], 8)
        self.assertTrue(capabilities["web_interface"])
        self.assertTrue(capabilities["api_access"])

    async def test_tools_list_endpoint(self):
        """Test the /tools endpoint."""
        resp = await self.client.request("GET", "/tools")
        self.assertEqual(resp.status, 200)

        data = await resp.json()
        self.assertIn("tools", data)

        tools = data["tools"]
        self.assertEqual(len(tools), 8)  # Should have all 8 MCP tools

        # Check that each tool has required fields
        for tool in tools:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)

            # Check input schema structure
            schema = tool["inputSchema"]
            self.assertIn("type", schema)
            self.assertEqual(schema["type"], "object")
            self.assertIn("properties", schema)
            self.assertIn("required", schema)

    async def test_groups_endpoint(self):
        """Test the /api/groups endpoint."""
        resp = await self.client.request("GET", "/api/groups")
        self.assertEqual(resp.status, 200)

        data = await resp.json()
        self.assertIn("groups", data)

        groups = data["groups"]
        self.assertGreater(len(groups), 0)

        # Check group structure
        for group in groups:
            self.assertIn("id", group)
            self.assertIn("name", group)
            self.assertIn("display_name", group)
            self.assertIn("aliases", group)

            # Check that display_name includes aliases
            if group["aliases"]:
                self.assertIn("(", group["display_name"])

    async def test_tactics_endpoint(self):
        """Test the /api/tactics endpoint."""
        resp = await self.client.request("GET", "/api/tactics")
        self.assertEqual(resp.status, 200)

        data = await resp.json()
        self.assertIn("tactics", data)

        tactics = data["tactics"]
        self.assertGreater(len(tactics), 0)

        # Check tactic structure
        for tactic in tactics:
            self.assertIn("id", tactic)
            self.assertIn("name", tactic)
            self.assertIn("display_name", tactic)

            # Check that display_name includes ID
            self.assertIn(tactic["id"], tactic["display_name"])

    async def test_techniques_endpoint_with_query(self):
        """Test the /api/techniques endpoint with query parameter."""
        resp = await self.client.request("GET", "/api/techniques?q=process")
        self.assertEqual(resp.status, 200)

        data = await resp.json()
        self.assertIn("techniques", data)

        techniques = data["techniques"]

        # Check technique structure
        for technique in techniques:
            self.assertIn("id", technique)
            self.assertIn("name", technique)
            self.assertIn("display_name", technique)
            self.assertIn("match_reason", technique)

            # Check that the technique matches the query
            query = "process"
            self.assertTrue(
                query.lower() in technique["id"].lower()
                or query.lower() in technique["name"].lower()
                or query.lower() in technique.get("description", "").lower()
            )

    async def test_techniques_endpoint_missing_query(self):
        """Test the /api/techniques endpoint without query parameter."""
        resp = await self.client.request("GET", "/api/techniques")
        self.assertEqual(resp.status, 400)

        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("required", data["error"].lower())

    async def test_techniques_endpoint_short_query(self):
        """Test the /api/techniques endpoint with too short query."""
        resp = await self.client.request("GET", "/api/techniques?q=a")
        self.assertEqual(resp.status, 400)

        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("2 characters", data["error"])

    async def test_call_tool_endpoint_success(self):
        """Test successful tool execution via /call_tool endpoint."""
        # Mock successful tool execution
        mock_result = [Mock()]
        mock_result[0].text = "Test tool execution result"

        # The mcp_server is already mocked in get_application
        # We need to access it through the app's routes
        for route in self.app.router.routes():
            if hasattr(route, "_handler") and hasattr(route._handler, "__self__"):
                proxy = route._handler.__self__
                if hasattr(proxy, "mcp_server"):
                    proxy.mcp_server.call_tool.return_value = (mock_result, None)
                    break

        # Test tool call
        payload = {"tool_name": "search_attack", "parameters": {"query": "test"}}

        resp = await self.client.request(
            "POST",
            "/call_tool",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(resp.status, 200)
        result = await resp.text()
        self.assertIn("Test tool execution result", result)

    async def test_call_tool_endpoint_missing_tool_name(self):
        """Test /call_tool endpoint with missing tool name."""
        payload = {"parameters": {"query": "test"}}

        resp = await self.client.request(
            "POST",
            "/call_tool",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(resp.status, 400)
        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("tool name", data["error"].lower())

    async def test_call_tool_endpoint_invalid_json(self):
        """Test /call_tool endpoint with invalid JSON."""
        resp = await self.client.request(
            "POST",
            "/call_tool",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(resp.status, 400)
        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("json", data["error"].lower())


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


class TestHTTPErrorHandling:
    """Test HTTP interface error handling scenarios."""

    def test_api_error_creation(self):
        """Test APIError creation and properties."""
        # This would be tested in JavaScript, but we can test the concept
        error_message = "Test error"
        status_code = 404

        # Simulate what the JavaScript APIError would contain
        error_data = {
            "message": error_message,
            "status": status_code,
            "name": "APIError",
        }

        assert error_data["message"] == error_message
        assert error_data["status"] == status_code
        assert error_data["name"] == "APIError"

    def test_retry_logic_conditions(self):
        """Test conditions for retry logic."""
        # Test retry conditions (simulating JavaScript logic)
        max_retries = 3

        # Should retry on network errors (5xx)
        assert self._should_retry_status(500, 1, max_retries) == True
        assert self._should_retry_status(502, 2, max_retries) == True

        # Should not retry on client errors (4xx), except 408 and 429
        assert self._should_retry_status(400, 1, max_retries) == False
        assert self._should_retry_status(404, 1, max_retries) == False
        assert self._should_retry_status(408, 1, max_retries) == True  # Timeout
        assert self._should_retry_status(429, 1, max_retries) == True  # Rate limit

        # Should not retry if max retries exceeded
        assert self._should_retry_status(500, 3, max_retries) == False

    def _should_retry_status(self, status, retry_count, max_retries):
        """Simulate JavaScript retry logic."""
        if retry_count >= max_retries:
            return False

        if 400 <= status < 500:
            return status == 408 or status == 429

        return status >= 500

    def test_query_validation(self):
        """Test query parameter validation."""
        # Valid queries
        assert self._validate_query("test") == True
        assert self._validate_query("process injection") == True
        assert self._validate_query("T1055") == True

        # Invalid queries
        assert self._validate_query("") == False
        assert self._validate_query("a") == False  # Too short
        assert self._validate_query("a" * 101) == False  # Too long
        assert self._validate_query(None) == False

    def _validate_query(self, query):
        """Simulate JavaScript query validation."""
        if not query or not isinstance(query, str):
            return False
        if len(query) < 2 or len(query) > 100:
            return False
        return True


if __name__ == "__main__":
    pytest.main([__file__])