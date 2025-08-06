"""
Unit tests for the JavaScript API communication layer.

This module tests the API endpoints that the JavaScript API layer communicates with,
ensuring proper error handling, response formats, and functionality.
"""

import json
import pytest
from unittest.mock import Mock, patch, AsyncMock
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from http_proxy import HTTPProxy, create_http_proxy_server
from src.mcp_server import create_mcp_server
from src.data_loader import DataLoader


class TestAPIEndpoints(AioHTTPTestCase):
    """Test the HTTP endpoints that the JavaScript API layer uses."""

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

    @unittest_run_loop
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

    @unittest_run_loop
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

    @unittest_run_loop
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

    @unittest_run_loop
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

    @unittest_run_loop
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

    @unittest_run_loop
    async def test_techniques_endpoint_missing_query(self):
        """Test the /api/techniques endpoint without query parameter."""
        resp = await self.client.request("GET", "/api/techniques")
        self.assertEqual(resp.status, 400)

        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("required", data["error"].lower())

    @unittest_run_loop
    async def test_techniques_endpoint_short_query(self):
        """Test the /api/techniques endpoint with too short query."""
        resp = await self.client.request("GET", "/api/techniques?q=a")
        self.assertEqual(resp.status, 400)

        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("2 characters", data["error"])

    @unittest_run_loop
    async def test_techniques_endpoint_long_query(self):
        """Test the /api/techniques endpoint with too long query."""
        long_query = "a" * 101  # 101 characters
        resp = await self.client.request("GET", f"/api/techniques?q={long_query}")
        self.assertEqual(resp.status, 400)

        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("100 characters", data["error"])

    @unittest_run_loop
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

    @unittest_run_loop
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

    @unittest_run_loop
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

    @unittest_run_loop
    async def test_call_tool_endpoint_empty_body(self):
        """Test /call_tool endpoint with empty request body."""
        resp = await self.client.request(
            "POST", "/call_tool", data="", headers={"Content-Type": "application/json"}
        )

        self.assertEqual(resp.status, 400)
        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("empty", data["error"].lower())


class TestAPIErrorHandling:
    """Test error handling scenarios for the API endpoints."""

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

    def test_timeout_calculation(self):
        """Test timeout and backoff calculations."""
        base_delay = 1000  # 1 second
        backoff_multiplier = 2

        # Test exponential backoff
        assert self._calculate_delay(0, base_delay, backoff_multiplier) == 1000
        assert self._calculate_delay(1, base_delay, backoff_multiplier) == 2000
        assert self._calculate_delay(2, base_delay, backoff_multiplier) == 4000

    def _calculate_delay(self, retry_count, base_delay, backoff_multiplier):
        """Simulate JavaScript delay calculation."""
        return base_delay * (backoff_multiplier**retry_count)


class TestAPIValidation:
    """Test API parameter validation logic."""

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

    def test_tool_parameter_validation(self):
        """Test tool parameter validation."""
        # Valid parameters
        assert self._validate_tool_params("search_attack", {"query": "test"}) == True
        assert (
            self._validate_tool_params("get_technique", {"technique_id": "T1055"})
            == True
        )

        # Invalid parameters
        assert (
            self._validate_tool_params("", {"query": "test"}) == False
        )  # Empty tool name
        assert (
            self._validate_tool_params("search_attack", None) == False
        )  # Null parameters
        assert (
            self._validate_tool_params("search_attack", "invalid") == False
        )  # Non-object parameters

    def _validate_tool_params(self, tool_name, parameters):
        """Simulate JavaScript tool parameter validation."""
        if not tool_name or not isinstance(tool_name, str):
            return False
        if not isinstance(parameters, dict) or parameters is None:
            return False
        return True


@pytest.fixture
def mock_api_responses():
    """Fixture providing mock API responses for testing."""
    return {
        "system_info": {
            "server_info": {
                "version": "1.0.0",
                "mcp_protocol_version": "1.0",
                "startup_time": "2024-01-01T00:00:00",
                "data_source": "MITRE ATT&CK Enterprise",
            },
            "data_statistics": {
                "techniques_count": 100,
                "tactics_count": 14,
                "groups_count": 50,
                "mitigations_count": 40,
                "relationships_count": 500,
                "last_updated": "2024-01-01T00:00:00",
                "data_loaded": True,
            },
            "capabilities": {
                "basic_tools": 5,
                "advanced_tools": 3,
                "total_tools": 8,
                "web_interface": True,
                "api_access": True,
            },
        },
        "tools": [
            {
                "name": "search_attack",
                "description": "Search across all MITRE ATT&CK entities",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"],
                },
            }
        ],
        "groups": [
            {
                "id": "G0016",
                "name": "APT29",
                "display_name": "APT29 (Cozy Bear, The Dukes)",
                "aliases": ["Cozy Bear", "The Dukes"],
            }
        ],
        "tactics": [
            {
                "id": "TA0001",
                "name": "Initial Access",
                "display_name": "Initial Access (TA0001)",
            }
        ],
        "techniques": [
            {
                "id": "T1055",
                "name": "Process Injection",
                "display_name": "Process Injection (T1055)",
                "match_reason": "Name",
            }
        ],
    }


def test_mock_responses_structure(mock_api_responses):
    """Test that mock responses have the expected structure."""
    # Test system_info structure
    system_info = mock_api_responses["system_info"]
    assert "server_info" in system_info
    assert "data_statistics" in system_info
    assert "capabilities" in system_info

    # Test tools structure
    tools = mock_api_responses["tools"]
    assert len(tools) > 0
    assert "name" in tools[0]
    assert "inputSchema" in tools[0]

    # Test groups structure
    groups = mock_api_responses["groups"]
    assert len(groups) > 0
    assert "id" in groups[0]
    assert "display_name" in groups[0]

    # Test tactics structure
    tactics = mock_api_responses["tactics"]
    assert len(tactics) > 0
    assert "id" in tactics[0]
    assert "display_name" in tactics[0]

    # Test techniques structure
    techniques = mock_api_responses["techniques"]
    assert len(techniques) > 0
    assert "id" in techniques[0]
    assert "match_reason" in techniques[0]


if __name__ == "__main__":
    pytest.main([__file__])
