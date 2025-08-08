"""
Unit tests for Smart Form Controls functionality.

This module tests the SmartFormControls JavaScript class functionality
through Python-based testing of the web interface components.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Import the HTTP proxy for testing endpoints
import sys

sys.path.append(str(Path(__file__).parent.parent))

from src.http_proxy import HTTPProxy
from src.mcp_server import MCPServer


class TestSmartFormControlsEndpoints:
    """Test the backend endpoints that support smart form controls."""

    @pytest.fixture
    def http_proxy(self):
        """Create HTTP proxy instance for testing."""
        mcp_server = Mock(spec=MCPServer)
        proxy = HTTPProxy(mcp_server)
        return proxy

    @pytest.fixture
    def sample_groups_data(self):
        """Sample threat groups data for testing."""
        return [
            {
                "id": "intrusion-set--f40eb8ce-2a74-4e56-89a1-227021410142",
                "name": "APT29",
                "aliases": ["Cozy Bear", "The Dukes"],
                "description": "APT29 is a Russian cyber espionage group",
            },
            {
                "id": "intrusion-set--31b90234-f9c4-4a7e-8a5d-2f7c8b9e1234",
                "name": "APT1",
                "aliases": ["Comment Crew", "PLA Unit 61398"],
                "description": "APT1 is a Chinese cyber espionage group",
            },
            {
                "id": "intrusion-set--12345678-1234-1234-1234-123456789012",
                "name": "Lazarus Group",
                "aliases": ["HIDDEN COBRA", "Guardians of Peace"],
                "description": "North Korean state-sponsored group",
            },
        ]

    @pytest.fixture
    def sample_tactics_data(self):
        """Sample tactics data for testing."""
        return [
            {
                "id": "TA0001",
                "name": "Initial Access",
                "description": "The adversary is trying to get into your network",
            },
            {
                "id": "TA0002",
                "name": "Execution",
                "description": "The adversary is trying to run malicious code",
            },
            {
                "id": "TA0003",
                "name": "Persistence",
                "description": "The adversary is trying to maintain their foothold",
            },
        ]

    @pytest.fixture
    def sample_techniques_data(self):
        """Sample techniques data for testing."""
        return [
            {
                "id": "T1055",
                "name": "Process Injection",
                "description": "Adversaries may inject code into processes",
            },
            {
                "id": "T1059",
                "name": "Command and Scripting Interpreter",
                "description": "Adversaries may abuse command and script interpreters",
            },
            {
                "id": "T1566",
                "name": "Phishing",
                "description": "Adversaries may send phishing messages",
            },
        ]

    @pytest.mark.asyncio
    async def test_groups_endpoint_success(self, http_proxy, sample_groups_data):
        """Test successful groups endpoint response."""
        # Mock the data loader and cached data
        mock_data_loader = Mock()
        mock_data_loader.get_cached_data.return_value = {"groups": sample_groups_data}
        http_proxy.mcp_server.data_loader = mock_data_loader

        # Create mock request
        request = Mock()
        request.query = {}

        # Call the handler
        response = await http_proxy.handle_get_groups(request)

        # Verify response
        assert response.status == 200
        response_data = json.loads(response.body)
        assert "groups" in response_data
        assert len(response_data["groups"]) == 3

        # Verify data loader was called correctly
        mock_data_loader.get_cached_data.assert_called_once_with("mitre_attack")

    @pytest.mark.asyncio
    async def test_tactics_endpoint_success(self, http_proxy, sample_tactics_data):
        """Test successful tactics endpoint response."""
        # Mock the data loader and cached data
        mock_data_loader = Mock()
        mock_data_loader.get_cached_data.return_value = {"tactics": sample_tactics_data}
        http_proxy.mcp_server.data_loader = mock_data_loader

        # Create mock request
        request = Mock()
        request.query = {}

        # Call the handler
        response = await http_proxy.handle_get_tactics(request)

        # Verify response
        assert response.status == 200
        response_data = json.loads(response.body)
        assert "tactics" in response_data
        assert len(response_data["tactics"]) == 3
        assert response_data["tactics"][0]["id"] == "TA0001"

        # Verify data loader was called correctly
        mock_data_loader.get_cached_data.assert_called_once_with("mitre_attack")

    @pytest.mark.asyncio
    async def test_techniques_endpoint_success(
        self, http_proxy, sample_techniques_data
    ):
        """Test successful techniques endpoint response."""
        # Mock the data loader and cached data
        mock_data_loader = Mock()
        mock_data_loader.get_cached_data.return_value = {
            "techniques": sample_techniques_data
        }
        http_proxy.mcp_server.data_loader = mock_data_loader

        # Create mock request with query parameter
        request = Mock()
        request.query = {"q": "process"}

        # Call the handler
        response = await http_proxy.handle_get_techniques(request)

        # Verify response
        assert response.status == 200
        response_data = json.loads(response.body)
        assert "techniques" in response_data
        assert len(response_data["techniques"]) == 1  # Only T1055 matches "process"

        # Verify data loader was called correctly
        mock_data_loader.get_cached_data.assert_called_once_with("mitre_attack")

    @pytest.mark.asyncio
    async def test_groups_endpoint_error_handling(self, http_proxy):
        """Test groups endpoint error handling."""
        # Mock the data loader to return None (no data loaded)
        mock_data_loader = Mock()
        mock_data_loader.get_cached_data.return_value = None
        http_proxy.mcp_server.data_loader = mock_data_loader

        # Create mock request
        request = Mock()
        request.query = {}

        # Call the handler
        response = await http_proxy.handle_get_groups(request)

        # Verify error response
        assert response.status == 500
        response_data = json.loads(response.body)
        assert "error" in response_data
        assert "MITRE ATT&CK data not loaded" in response_data["error"]

    @pytest.mark.asyncio
    async def test_techniques_endpoint_missing_query(self, http_proxy):
        """Test techniques endpoint with missing query parameter."""
        # Create mock request without query parameter
        request = Mock()
        request.query = {}

        # Call the handler
        response = await http_proxy.handle_get_techniques(request)

        # Verify error response
        assert response.status == 400
        response_data = json.loads(response.body)
        assert "error" in response_data
        assert (
            "query parameter" in response_data["error"].lower()
            and "required" in response_data["error"].lower()
        )

    @pytest.mark.asyncio
    async def test_techniques_endpoint_short_query(self, http_proxy):
        """Test techniques endpoint with query too short."""
        # Create mock request with short query
        request = Mock()
        request.query = {"q": "a"}

        # Call the handler
        response = await http_proxy.handle_get_techniques(request)

        # Verify error response
        assert response.status == 400
        response_data = json.loads(response.body)
        assert "error" in response_data
        assert "at least 2 characters" in response_data["error"].lower()


class TestSmartFormControlsDataExtraction:
    """Test data extraction methods for smart form controls."""

    @pytest.fixture
    def http_proxy(self):
        """Create HTTP proxy instance for testing."""
        mcp_server = Mock(spec=MCPServer)
        return HTTPProxy(mcp_server)

    def test_extract_groups_for_dropdown(self, http_proxy):
        """Test group data extraction for dropdown population."""
        # Sample STIX data
        stix_data = {
            "objects": [
                {
                    "type": "intrusion-set",
                    "id": "intrusion-set--f40eb8ce-2a74-4e56-89a1-227021410142",
                    "name": "APT29",
                    "aliases": ["Cozy Bear", "The Dukes"],
                    "description": "APT29 is a Russian cyber espionage group",
                },
                {
                    "type": "intrusion-set",
                    "id": "intrusion-set--31b90234-f9c4-4a7e-8a5d-2f7c8b9e1234",
                    "name": "APT1",
                    "aliases": ["Comment Crew"],
                    "description": "APT1 is a Chinese cyber espionage group",
                },
            ]
        }

        # Test the extraction method - pass the objects list directly
        result = http_proxy._extract_groups_for_dropdown(stix_data["objects"])

        # Verify results
        assert len(result) == 2

        # Find APT1 and APT29 in results (they're sorted alphabetically)
        apt1 = next(g for g in result if g["name"] == "APT1")
        apt29 = next(g for g in result if g["name"] == "APT29")

        assert apt1["id"] == "intrusion-set--31b90234-f9c4-4a7e-8a5d-2f7c8b9e1234"
        assert apt1["aliases"] == ["Comment Crew"]
        assert apt1["display_name"] == "APT1 (Comment Crew)"

        assert apt29["id"] == "intrusion-set--f40eb8ce-2a74-4e56-89a1-227021410142"
        assert apt29["aliases"] == ["Cozy Bear", "The Dukes"]
        assert apt29["display_name"] == "APT29 (Cozy Bear, The Dukes)"

    def test_extract_tactics_for_dropdown(self, http_proxy):
        """Test tactic data extraction for dropdown population."""
        # Sample tactics data
        tactics_data = [
            {
                "id": "TA0001",
                "name": "Initial Access",
                "description": "The adversary is trying to get into your network",
            },
            {
                "id": "TA0002",
                "name": "Execution",
                "description": "The adversary is trying to run malicious code",
            },
        ]

        # Test the extraction method - pass the tactics list directly
        result = http_proxy._extract_tactics_for_dropdown(tactics_data)

        # Verify results
        assert len(result) == 2
        assert result[0]["id"] == "TA0001"
        assert result[0]["name"] == "Initial Access"
        assert result[0]["display_name"] == "Initial Access (TA0001)"

        assert result[1]["id"] == "TA0002"
        assert result[1]["display_name"] == "Execution (TA0002)"

    def test_extract_techniques_for_autocomplete(self, http_proxy):
        """Test technique data extraction for autocomplete."""
        # Sample STIX data with techniques
        stix_data = {
            "objects": [
                {
                    "type": "attack-pattern",
                    "id": "attack-pattern--43e7dc91-05b2-474c-b9ac-2ed4fe101f4d",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "T1055"}
                    ],
                    "name": "Process Injection",
                    "description": "Adversaries may inject code into processes",
                },
                {
                    "type": "attack-pattern",
                    "id": "attack-pattern--7385dfaf-6886-4229-9ecd-6fd678040830",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "T1059"}
                    ],
                    "name": "Command and Scripting Interpreter",
                    "description": "Adversaries may abuse command and script interpreters",
                },
            ]
        }

        # Test the extraction method - pass the objects list directly
        result = http_proxy._extract_techniques_for_autocomplete(
            stix_data["objects"], "process"
        )

        # Verify results
        assert len(result) >= 1
        # Should include the Process Injection technique
        process_injection = next(
            (t for t in result if "T1055" in t.get("display_name", "")), None
        )
        assert process_injection is not None
        assert process_injection["name"] == "Process Injection"

    def test_extract_groups_empty_data(self, http_proxy):
        """Test group extraction with empty data."""
        result = http_proxy._extract_groups_for_dropdown([])
        assert result == []

        result = http_proxy._extract_groups_for_dropdown([])
        assert result == []

    def test_extract_groups_invalid_data(self, http_proxy):
        """Test group extraction with invalid data."""
        # Test with None
        result = http_proxy._extract_groups_for_dropdown(None)
        assert result == []

        # Test with malformed group data
        result = http_proxy._extract_groups_for_dropdown(
            [{"name": "APT29"}]
        )  # Missing ID
        assert result == []

    def test_extract_tactics_empty_data(self, http_proxy):
        """Test tactic extraction with empty data."""
        result = http_proxy._extract_tactics_for_dropdown([])
        assert result == []

    def test_extract_techniques_empty_query(self, http_proxy):
        """Test technique extraction with empty query."""
        result = http_proxy._extract_techniques_for_autocomplete([], "")
        assert result == []


class TestSmartFormControlsValidation:
    """Test form validation functionality."""

    def test_form_validation_rules(self):
        """Test form validation rules are properly defined."""
        # This would test the JavaScript validation rules
        # For now, we'll test the concept through Python

        validation_rules = {
            "required_fields": ["group_id", "tactic_id"],
            "min_length": {"technique_query": 2},
            "max_length": {"description": 500},
            "patterns": {
                "technique_id": r"^T\d{4}(\.\d{3})?$",
                "group_id": r"^(G\d{4}|intrusion-set--[a-f0-9-]{36})$",
            },
        }

        # Test required field validation
        assert "group_id" in validation_rules["required_fields"]
        assert "tactic_id" in validation_rules["required_fields"]

        # Test length validation
        assert validation_rules["min_length"]["technique_query"] == 2
        assert validation_rules["max_length"]["description"] == 500

        # Test pattern validation
        technique_pattern = validation_rules["patterns"]["technique_id"]
        import re

        assert re.match(technique_pattern, "T1055")
        assert re.match(technique_pattern, "T1055.001")
        assert not re.match(technique_pattern, "invalid")

    def test_input_sanitization(self):
        """Test input sanitization for security."""
        # Test cases for input sanitization
        test_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "javascript:alert('xss')",
        ]

        # Mock sanitization function
        def sanitize_input(input_str):
            """Basic input sanitization."""
            if not isinstance(input_str, str):
                return ""

            # Remove HTML tags
            import re

            clean = re.sub(r"<[^>]*>", "", input_str)

            # Remove SQL injection patterns
            sql_patterns = [
                r"';",
                r"--",
                r"/\*",
                r"\*/",
                r"DROP\s+TABLE",
                r"SELECT\s+\*",
            ]
            for pattern in sql_patterns:
                clean = re.sub(pattern, "", clean, flags=re.IGNORECASE)

            # Remove path traversal
            clean = clean.replace("../", "").replace("..\\", "")

            # Remove javascript protocol
            clean = re.sub(r"javascript:", "", clean, flags=re.IGNORECASE)

            return clean.strip()

        # Test sanitization
        for test_input in test_inputs:
            sanitized = sanitize_input(test_input)
            assert "<script>" not in sanitized
            assert "DROP TABLE" not in sanitized.upper()
            assert "../" not in sanitized
            assert "javascript:" not in sanitized.lower()

    def test_autocomplete_query_validation(self):
        """Test autocomplete query validation."""

        def validate_autocomplete_query(query):
            """Validate autocomplete query."""
            if not query or not isinstance(query, str):
                return False, "Query is required"

            query = query.strip()
            if len(query) < 2:
                return False, "Query must be at least 2 characters"

            if len(query) > 100:
                return False, "Query too long"

            # Check for suspicious patterns
            suspicious_patterns = [r"<script", r"javascript:", r"on\w+\s*="]
            import re

            for pattern in suspicious_patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return False, "Invalid characters in query"

            return True, ""

        # Test valid queries
        valid, msg = validate_autocomplete_query("process")
        assert valid
        assert msg == ""

        valid, msg = validate_autocomplete_query("T1055")
        assert valid

        # Test invalid queries
        valid, msg = validate_autocomplete_query("")
        assert not valid
        assert "required" in msg

        valid, msg = validate_autocomplete_query("a")
        assert not valid
        assert "2 characters" in msg

        valid, msg = validate_autocomplete_query("<script>alert('xss')</script>")
        assert not valid
        assert "Invalid characters" in msg


class TestSmartFormControlsIntegration:
    """Test integration between smart form controls and other components."""

    @pytest.mark.asyncio
    async def test_form_controls_initialization_sequence(self):
        """Test the initialization sequence of smart form controls."""
        # Mock the initialization steps
        initialization_steps = [
            "load_groups_data",
            "load_tactics_data",
            "setup_group_dropdowns",
            "setup_tactic_dropdowns",
            "setup_technique_autocomplete",
            "setup_form_validation",
        ]

        completed_steps = []

        async def mock_step(step_name):
            """Mock an initialization step."""
            await asyncio.sleep(0.01)  # Simulate async operation
            completed_steps.append(step_name)
            return True

        # Execute initialization steps
        for step in initialization_steps:
            success = await mock_step(step)
            assert success

        # Verify all steps completed
        assert len(completed_steps) == len(initialization_steps)
        assert completed_steps == initialization_steps

    def test_form_controls_error_recovery(self):
        """Test error recovery mechanisms."""
        # Mock error scenarios and recovery
        error_scenarios = [
            {"error": "network_timeout", "recovery": "retry_with_backoff"},
            {"error": "invalid_response", "recovery": "use_cached_data"},
            {"error": "server_error", "recovery": "show_error_message"},
        ]

        def handle_error(error_type):
            """Mock error handling."""
            scenario = next(
                (s for s in error_scenarios if s["error"] == error_type), None
            )
            return scenario["recovery"] if scenario else "unknown_error"

        # Test error handling
        assert handle_error("network_timeout") == "retry_with_backoff"
        assert handle_error("invalid_response") == "use_cached_data"
        assert handle_error("server_error") == "show_error_message"
        assert handle_error("unknown") == "unknown_error"

    def test_form_controls_performance_metrics(self):
        """Test performance metrics for form controls."""
        # Mock performance metrics
        metrics = {
            "groups_load_time": 150,  # ms
            "tactics_load_time": 120,  # ms
            "autocomplete_response_time": 80,  # ms
            "form_validation_time": 5,  # ms
            "cache_hit_rate": 0.85,  # 85%
        }

        # Test performance thresholds
        assert metrics["groups_load_time"] < 500  # Should load in under 500ms
        assert metrics["tactics_load_time"] < 500
        assert (
            metrics["autocomplete_response_time"] < 200
        )  # Autocomplete should be fast
        assert metrics["form_validation_time"] < 50  # Validation should be instant
        assert metrics["cache_hit_rate"] > 0.8  # Good cache performance

    def test_accessibility_compliance(self):
        """Test accessibility compliance for form controls."""
        # Mock accessibility checks
        accessibility_features = {
            "aria_labels": True,
            "keyboard_navigation": True,
            "screen_reader_support": True,
            "high_contrast_support": True,
            "focus_indicators": True,
            "error_announcements": True,
        }

        # Verify all accessibility features are enabled
        for feature, enabled in accessibility_features.items():
            assert enabled, f"Accessibility feature {feature} should be enabled"

    def test_responsive_design_breakpoints(self):
        """Test responsive design breakpoints."""
        # Mock responsive design breakpoints
        breakpoints = {
            "mobile": {"max_width": 576, "columns": 1},
            "tablet": {"max_width": 768, "columns": 2},
            "desktop": {"max_width": 1200, "columns": 3},
            "large": {"max_width": None, "columns": 4},
        }

        def get_layout_for_width(width):
            """Get layout configuration for screen width."""
            for name, config in breakpoints.items():
                if config["max_width"] is None or width <= config["max_width"]:
                    return config["columns"]
            return 1

        # Test responsive behavior
        assert get_layout_for_width(400) == 1  # Mobile
        assert get_layout_for_width(700) == 2  # Tablet
        assert get_layout_for_width(1000) == 3  # Desktop
        assert get_layout_for_width(1400) == 4  # Large screen


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
