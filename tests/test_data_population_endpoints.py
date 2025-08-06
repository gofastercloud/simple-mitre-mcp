"""
Unit tests for data population endpoints in HTTP proxy server.

These tests verify the functionality of the new API endpoints that provide
formatted data for smart form controls in the web interface.
"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from http_proxy import HTTPProxy  # noqa: E402


class TestDataPopulationEndpoints(AioHTTPTestCase):
    """Test cases for data population endpoints."""

    async def get_application(self):
        """Create test application with mocked MCP server."""
        # Create mock MCP server
        mock_mcp_server = MagicMock()
        mock_data_loader = MagicMock()

        # Set up mock data loader
        mock_mcp_server.data_loader = mock_data_loader

        # Create HTTP proxy with mock server
        self.proxy = HTTPProxy(mock_mcp_server)

        # Store proxy reference in app for test access
        self.proxy.app["proxy"] = self.proxy

        return self.proxy.app

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()

        # Sample test data
        self.sample_groups_data = [
            {
                "id": "G0001",
                "name": "Axiom",
                "aliases": ["Group 72", "APT1"],
                "description": "Axiom is a cyber espionage group...",
            },
            {
                "id": "G0002",
                "name": "Lazarus Group",
                "aliases": ["HIDDEN COBRA", "Guardians of Peace", "ZINC"],
                "description": "Lazarus Group is a North Korean state-sponsored...",
            },
            {
                "id": "G0003",
                "name": "APT28",
                "aliases": ["Fancy Bear", "Pawn Storm", "Sofacy"],
                "description": "APT28 is a threat group...",
            },
        ]

        self.sample_tactics_data = [
            {
                "id": "TA0001",
                "name": "Initial Access",
                "description": "The adversary is trying to get into your network...",
            },
            {
                "id": "TA0002",
                "name": "Execution",
                "description": "The adversary is trying to run malicious code...",
            },
            {
                "id": "TA0003",
                "name": "Persistence",
                "description": "The adversary is trying to maintain their foothold...",
            },
        ]

        self.sample_techniques_data = [
            {
                "id": "T1055",
                "name": "Process Injection",
                "description": "Adversaries may inject code into processes...",
            },
            {
                "id": "T1059",
                "name": "Command and Scripting Interpreter",
                "description": "Adversaries may abuse command and script interpreters...",
            },
            {
                "id": "T1070",
                "name": "Indicator Removal on Host",
                "description": "Adversaries may delete or alter generated artifacts...",
            },
        ]

    @unittest_run_loop
    async def test_get_groups_success(self):
        """Test successful groups endpoint response."""
        # Mock the data loader to return sample data
        mock_data = {
            "groups": self.sample_groups_data,
            "tactics": [],
            "techniques": [],
            "mitigations": [],
        }

        with patch.object(
            self.app["proxy"].mcp_server.data_loader,
            "get_cached_data",
            return_value=mock_data,
        ):
            resp = await self.client.request("GET", "/api/groups")

            self.assertEqual(resp.status, 200)

            data = await resp.json()
            self.assertIn("groups", data)

            groups = data["groups"]
            self.assertEqual(len(groups), 3)

            # Check first group formatting
            first_group = groups[0]  # Should be APT28 after sorting
            self.assertEqual(first_group["id"], "G0003")
            self.assertEqual(first_group["name"], "APT28")
            self.assertIn("Fancy Bear", first_group["display_name"])
            self.assertEqual(
                first_group["aliases"], ["Fancy Bear", "Pawn Storm", "Sofacy"]
            )

    @unittest_run_loop
    async def test_get_groups_no_data_loader(self):
        """Test groups endpoint when data loader is not available."""
        # Remove data loader from mock server
        self.app["proxy"].mcp_server.data_loader = None

        resp = await self.client.request("GET", "/api/groups")

        self.assertEqual(resp.status, 500)
        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("Data loader not available", data["error"])

    @unittest_run_loop
    async def test_get_groups_no_data_loaded(self):
        """Test groups endpoint when no data is loaded."""
        with patch.object(
            self.app["proxy"].mcp_server.data_loader,
            "get_cached_data",
            return_value=None,
        ):
            resp = await self.client.request("GET", "/api/groups")

            self.assertEqual(resp.status, 500)
            data = await resp.json()
            self.assertIn("error", data)
            self.assertIn("MITRE ATT&CK data not loaded", data["error"])

    @unittest_run_loop
    async def test_get_tactics_success(self):
        """Test successful tactics endpoint response."""
        # Mock the data loader to return sample data
        mock_data = {
            "groups": [],
            "tactics": self.sample_tactics_data,
            "techniques": [],
            "mitigations": [],
        }

        with patch.object(
            self.app["proxy"].mcp_server.data_loader,
            "get_cached_data",
            return_value=mock_data,
        ):
            resp = await self.client.request("GET", "/api/tactics")

            self.assertEqual(resp.status, 200)

            data = await resp.json()
            self.assertIn("tactics", data)

            tactics = data["tactics"]
            self.assertEqual(len(tactics), 3)

            # Check first tactic formatting (should be sorted by ID)
            first_tactic = tactics[0]
            self.assertEqual(first_tactic["id"], "TA0001")
            self.assertEqual(first_tactic["name"], "Initial Access")
            self.assertEqual(first_tactic["display_name"], "Initial Access (TA0001)")

    @unittest_run_loop
    async def test_get_tactics_no_data_loader(self):
        """Test tactics endpoint when data loader is not available."""
        # Remove data loader from mock server
        self.app["proxy"].mcp_server.data_loader = None

        resp = await self.client.request("GET", "/api/tactics")

        self.assertEqual(resp.status, 500)
        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("Data loader not available", data["error"])

    @unittest_run_loop
    async def test_get_techniques_success_id_match(self):
        """Test successful techniques endpoint response with ID match."""
        # Mock the data loader to return sample data
        mock_data = {
            "groups": [],
            "tactics": [],
            "techniques": self.sample_techniques_data,
            "mitigations": [],
        }

        with patch.object(
            self.app["proxy"].mcp_server.data_loader,
            "get_cached_data",
            return_value=mock_data,
        ):
            resp = await self.client.request("GET", "/api/techniques?q=T1055")

            self.assertEqual(resp.status, 200)

            data = await resp.json()
            self.assertIn("techniques", data)

            techniques = data["techniques"]
            self.assertEqual(len(techniques), 1)

            # Check technique formatting
            technique = techniques[0]
            self.assertEqual(technique["id"], "T1055")
            self.assertEqual(technique["name"], "Process Injection")
            self.assertEqual(technique["display_name"], "Process Injection (T1055)")
            self.assertEqual(technique["match_reason"], "ID")

    @unittest_run_loop
    async def test_get_techniques_success_name_match(self):
        """Test successful techniques endpoint response with name match."""
        # Mock the data loader to return sample data
        mock_data = {
            "groups": [],
            "tactics": [],
            "techniques": self.sample_techniques_data,
            "mitigations": [],
        }

        with patch.object(
            self.app["proxy"].mcp_server.data_loader,
            "get_cached_data",
            return_value=mock_data,
        ):
            resp = await self.client.request("GET", "/api/techniques?q=injection")

            self.assertEqual(resp.status, 200)

            data = await resp.json()
            self.assertIn("techniques", data)

            techniques = data["techniques"]
            self.assertEqual(len(techniques), 1)

            # Check technique formatting
            technique = techniques[0]
            self.assertEqual(technique["id"], "T1055")
            self.assertEqual(technique["name"], "Process Injection")
            self.assertEqual(technique["match_reason"], "Name")

    @unittest_run_loop
    async def test_get_techniques_missing_query_param(self):
        """Test techniques endpoint with missing query parameter."""
        resp = await self.client.request("GET", "/api/techniques")

        self.assertEqual(resp.status, 400)
        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("Query parameter 'q' is required", data["error"])

    @unittest_run_loop
    async def test_get_techniques_empty_query_param(self):
        """Test techniques endpoint with empty query parameter."""
        resp = await self.client.request("GET", "/api/techniques?q=")

        self.assertEqual(resp.status, 400)
        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("Query parameter 'q' is required", data["error"])

    @unittest_run_loop
    async def test_get_techniques_short_query(self):
        """Test techniques endpoint with query too short."""
        resp = await self.client.request("GET", "/api/techniques?q=T")

        self.assertEqual(resp.status, 400)
        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("Query must be at least 2 characters long", data["error"])

    @unittest_run_loop
    async def test_get_techniques_long_query(self):
        """Test techniques endpoint with query too long."""
        long_query = "a" * 101  # 101 characters
        resp = await self.client.request("GET", f"/api/techniques?q={long_query}")

        self.assertEqual(resp.status, 400)
        data = await resp.json()
        self.assertIn("error", data)
        self.assertIn("Query must be less than 100 characters", data["error"])

    @unittest_run_loop
    async def test_get_techniques_no_matches(self):
        """Test techniques endpoint with query that matches nothing."""
        # Mock the data loader to return sample data
        mock_data = {
            "groups": [],
            "tactics": [],
            "techniques": self.sample_techniques_data,
            "mitigations": [],
        }

        with patch.object(
            self.app["proxy"].mcp_server.data_loader,
            "get_cached_data",
            return_value=mock_data,
        ):
            resp = await self.client.request("GET", "/api/techniques?q=nonexistent")

            self.assertEqual(resp.status, 200)

            data = await resp.json()
            self.assertIn("techniques", data)

            techniques = data["techniques"]
            self.assertEqual(len(techniques), 0)

    def test_extract_groups_for_dropdown(self):
        """Test the _extract_groups_for_dropdown helper method."""
        # Create a mock proxy instance
        mock_mcp_server = MagicMock()
        proxy = HTTPProxy(mock_mcp_server)

        # Test with sample data
        result = proxy._extract_groups_for_dropdown(self.sample_groups_data)

        self.assertEqual(len(result), 3)

        # Check sorting (should be alphabetical by name)
        self.assertEqual(result[0]["name"], "APT28")
        self.assertEqual(result[1]["name"], "Axiom")
        self.assertEqual(result[2]["name"], "Lazarus Group")

        # Check formatting of group with aliases
        apt28_group = result[0]
        self.assertEqual(apt28_group["id"], "G0003")
        self.assertEqual(apt28_group["name"], "APT28")
        self.assertIn("Fancy Bear", apt28_group["display_name"])
        self.assertIn("Pawn Storm", apt28_group["display_name"])
        self.assertEqual(apt28_group["aliases"], ["Fancy Bear", "Pawn Storm", "Sofacy"])

    def test_extract_groups_for_dropdown_with_many_aliases(self):
        """Test _extract_groups_for_dropdown with group having many aliases."""
        # Create a mock proxy instance
        mock_mcp_server = MagicMock()
        proxy = HTTPProxy(mock_mcp_server)

        # Test data with many aliases
        test_data = [
            {
                "id": "G0001",
                "name": "Test Group",
                "aliases": ["Alias1", "Alias2", "Alias3", "Alias4", "Alias5"],
            }
        ]

        result = proxy._extract_groups_for_dropdown(test_data)

        self.assertEqual(len(result), 1)
        group = result[0]

        # Should show first 2 aliases plus count of remaining
        self.assertIn("Alias1", group["display_name"])
        self.assertIn("Alias2", group["display_name"])
        self.assertIn("+3 more", group["display_name"])

    def test_extract_tactics_for_dropdown(self):
        """Test the _extract_tactics_for_dropdown helper method."""
        # Create a mock proxy instance
        mock_mcp_server = MagicMock()
        proxy = HTTPProxy(mock_mcp_server)

        # Test with sample data
        result = proxy._extract_tactics_for_dropdown(self.sample_tactics_data)

        self.assertEqual(len(result), 3)

        # Check sorting (should be by ID)
        self.assertEqual(result[0]["id"], "TA0001")
        self.assertEqual(result[1]["id"], "TA0002")
        self.assertEqual(result[2]["id"], "TA0003")

        # Check formatting
        first_tactic = result[0]
        self.assertEqual(first_tactic["id"], "TA0001")
        self.assertEqual(first_tactic["name"], "Initial Access")
        self.assertEqual(first_tactic["display_name"], "Initial Access (TA0001)")

    def test_extract_techniques_for_autocomplete_id_match(self):
        """Test _extract_techniques_for_autocomplete with ID match."""
        # Create a mock proxy instance
        mock_mcp_server = MagicMock()
        proxy = HTTPProxy(mock_mcp_server)

        # Test with ID query
        result = proxy._extract_techniques_for_autocomplete(
            self.sample_techniques_data, "t1055"
        )

        self.assertEqual(len(result), 1)
        technique = result[0]
        self.assertEqual(technique["id"], "T1055")
        self.assertEqual(technique["match_reason"], "ID")

    def test_extract_techniques_for_autocomplete_name_match(self):
        """Test _extract_techniques_for_autocomplete with name match."""
        # Create a mock proxy instance
        mock_mcp_server = MagicMock()
        proxy = HTTPProxy(mock_mcp_server)

        # Test with name query
        result = proxy._extract_techniques_for_autocomplete(
            self.sample_techniques_data, "injection"
        )

        self.assertEqual(len(result), 1)
        technique = result[0]
        self.assertEqual(technique["id"], "T1055")
        self.assertEqual(technique["match_reason"], "Name")

    def test_extract_techniques_for_autocomplete_description_match(self):
        """Test _extract_techniques_for_autocomplete with description match."""
        # Create a mock proxy instance
        mock_mcp_server = MagicMock()
        proxy = HTTPProxy(mock_mcp_server)

        # Test with description query
        result = proxy._extract_techniques_for_autocomplete(
            self.sample_techniques_data, "processes"
        )

        self.assertEqual(len(result), 1)
        technique = result[0]
        self.assertEqual(technique["id"], "T1055")
        self.assertEqual(technique["match_reason"], "Description")

    def test_extract_techniques_for_autocomplete_sorting(self):
        """Test _extract_techniques_for_autocomplete sorting logic."""
        # Create a mock proxy instance
        mock_mcp_server = MagicMock()
        proxy = HTTPProxy(mock_mcp_server)

        # Create test data that will match in different ways
        test_data = [
            {
                "id": "T1059",
                "name": "Command and Scripting Interpreter",
                "description": "Adversaries may abuse command and script interpreters...",
            },
            {
                "id": "T1055",
                "name": "Process Injection",
                "description": "Adversaries may inject code into processes...",
            },
            {
                "id": "T1070",
                "name": "Indicator Removal on Host",
                "description": "Adversaries may delete or alter generated artifacts on a host system, including logs or captured files such as quarantined malware. Locations and format of logs are platform or product-specific however standard operating system logs are captured as Windows events or Linux/macOS files such as Bash History and /var/log/*.",
            },
        ]

        # Test with query that matches ID, name, and description
        result = proxy._extract_techniques_for_autocomplete(test_data, "t")

        # Should return all 3, with ID matches first
        self.assertEqual(len(result), 3)

        # Check that results are properly sorted
        # ID matches should come first, then name matches, then description matches
        id_matches = [t for t in result if t["match_reason"] == "ID"]

        # All should be ID matches in this case since "t" appears in all IDs
        self.assertEqual(len(id_matches), 3)

    def test_extract_techniques_for_autocomplete_limit_results(self):
        """Test that _extract_techniques_for_autocomplete limits results to 50."""
        # Create a mock proxy instance
        mock_mcp_server = MagicMock()
        proxy = HTTPProxy(mock_mcp_server)

        # Create 60 test techniques that all match
        test_data = []
        for i in range(60):
            test_data.append(
                {
                    "id": f"T{i:04d}",
                    "name": f"Test Technique {i}",
                    "description": "Test description",
                }
            )

        # Test with query that matches all
        result = proxy._extract_techniques_for_autocomplete(test_data, "test")

        # Should be limited to 50 results
        self.assertEqual(len(result), 50)

    def test_extract_methods_handle_missing_data(self):
        """Test that extract methods handle missing or malformed data gracefully."""
        # Create a mock proxy instance
        mock_mcp_server = MagicMock()
        proxy = HTTPProxy(mock_mcp_server)

        # Test with malformed data (missing required fields)
        malformed_groups = [
            {"id": "G0001"},  # Missing name
            {"name": "Test Group"},  # Missing id
            {"id": "G0002", "name": "Valid Group"},  # Valid
        ]

        result = proxy._extract_groups_for_dropdown(malformed_groups)

        # Should only return the valid group
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "G0002")

        # Test with empty data
        result = proxy._extract_groups_for_dropdown([])
        self.assertEqual(len(result), 0)

        # Test tactics with malformed data
        malformed_tactics = [
            {"id": "TA0001"},  # Missing name
            {"name": "Test Tactic"},  # Missing id
            {"id": "TA0002", "name": "Valid Tactic"},  # Valid
        ]

        result = proxy._extract_tactics_for_dropdown(malformed_tactics)

        # Should only return the valid tactic
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "TA0002")


if __name__ == "__main__":
    import unittest

    unittest.main()
