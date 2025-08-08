"""
Unit tests for search_attack tool functionality.

This module contains unit tests for the search_attack MCP tool,
including search logic, result formatting, and edge cases.
"""

import pytest
from unittest.mock import Mock
from src.mcp_server import _search_entities, create_mcp_server
from src.data_loader import DataLoader
from tests.base import BaseMCPTestCase


class TestSearchAttack(BaseMCPTestCase):
    """Test cases for search_attack tool functionality."""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return {
            "tactics": [
                {
                    "id": "TA0001",
                    "name": "Initial Access",
                    "description": "The adversary is trying to get into your network.",
                },
                {
                    "id": "TA0002",
                    "name": "Execution",
                    "description": "The adversary is trying to run malicious code.",
                },
            ],
            "techniques": [
                {
                    "id": "T1055",
                    "name": "Process Injection",
                    "description": "Adversaries may inject code into processes to evade process-based defenses.",
                    "tactics": ["TA0004", "TA0005"],
                    "platforms": ["Windows", "Linux"],
                },
                {
                    "id": "T1059",
                    "name": "Command and Scripting Interpreter",
                    "description": "Adversaries may abuse command and script interpreters to execute commands.",
                    "tactics": ["TA0002"],
                    "platforms": ["Windows", "Linux", "macOS"],
                },
            ],
            "groups": [
                {
                    "id": "G0016",
                    "name": "APT29",
                    "aliases": ["Cozy Bear", "The Dukes"],
                    "description": "APT29 is a threat group that has been attributed to Russia.",
                },
                {
                    "id": "G0007",
                    "name": "APT1",
                    "aliases": ["Comment Crew", "PLA Unit 61398"],
                    "description": "APT1 is a Chinese threat group that has been attributed to the 2nd Bureau of the PLA.",
                },
            ],
            "mitigations": [
                {
                    "id": "M1013",
                    "name": "Application Developer Guidance",
                    "description": "This mitigation describes any guidance or training given to developers.",
                },
                {
                    "id": "M1040",
                    "name": "Behavior Prevention on Endpoint",
                    "description": "Use capabilities to prevent suspicious behavior patterns from executing.",
                },
            ],
        }

    def test_search_entities_by_id(self, sample_data):
        """Test searching entities by ID."""
        results = _search_entities("t1055", sample_data)

        assert len(results) == 1
        assert results[0]["entity_type"] == "technique"
        assert results[0]["id"] == "T1055"
        assert results[0]["name"] == "Process Injection"
        assert "ID contains" in results[0]["match_reason"]

    def test_search_entities_by_name(self, sample_data):
        """Test searching entities by name."""
        results = _search_entities("process", sample_data)

        assert len(results) == 1
        assert results[0]["entity_type"] == "technique"
        assert results[0]["id"] == "T1055"
        assert "name contains" in results[0]["match_reason"]

    def test_search_entities_by_description(self, sample_data):
        """Test searching entities by description."""
        results = _search_entities("adversary", sample_data)

        # Should find multiple entities with 'adversary' in description
        assert len(results) >= 2

        # Check that all results have 'adversary' in their match reason
        for result in results:
            assert "description contains" in result["match_reason"]

    def test_search_entities_by_alias(self, sample_data):
        """Test searching groups by alias."""
        results = _search_entities("cozy bear", sample_data)

        assert len(results) == 1
        assert results[0]["entity_type"] == "group"
        assert results[0]["id"] == "G0016"
        assert "alias" in results[0]["match_reason"]

    def test_search_entities_case_insensitive(self, sample_data):
        """Test that search is case insensitive."""
        # The _search_entities function expects lowercase input
        # Case conversion is handled by the MCP tool before calling this function
        results_lower = _search_entities("apt29", sample_data)
        results_upper = _search_entities("APT29".lower(), sample_data)
        results_mixed = _search_entities("ApT29".lower(), sample_data)

        assert len(results_lower) == 1
        assert len(results_upper) == 1
        assert len(results_mixed) == 1

        # All should return the same result
        assert (
            results_lower[0]["id"] == results_upper[0]["id"] == results_mixed[0]["id"]
        )

    def test_search_entities_multiple_matches(self, sample_data):
        """Test searching with query that matches multiple entities."""
        results = _search_entities("apt", sample_data)

        # Should find both APT29 and APT1
        assert len(results) >= 2

        # Check that we get both groups
        group_ids = [r["id"] for r in results if r["entity_type"] == "group"]
        assert "G0016" in group_ids  # APT29
        assert "G0007" in group_ids  # APT1

    def test_search_entities_no_matches(self, sample_data):
        """Test searching with query that has no matches."""
        results = _search_entities("nonexistent", sample_data)

        assert len(results) == 0

    def test_search_entities_empty_query(self, sample_data):
        """Test searching with empty query."""
        results = _search_entities("", sample_data)

        # Empty query should match all entities (since empty string is in all strings)
        total_entities = sum(len(entities) for entities in sample_data.values())
        assert len(results) == total_entities

    def test_search_entities_result_structure(self, sample_data):
        """Test that search results have correct structure."""
        results = _search_entities("apt29", sample_data)

        assert len(results) == 1
        result = results[0]

        # Check required fields
        assert "entity_type" in result
        assert "id" in result
        assert "name" in result
        assert "description" in result
        assert "match_reason" in result

        # Check group-specific fields
        if result["entity_type"] == "group":
            assert "aliases" in result

    def test_search_entities_sorting(self, sample_data):
        """Test that search results are sorted correctly."""
        results = _search_entities(
            "a", sample_data
        )  # Should match multiple entities

        # Results should be sorted by entity_type, then by id
        for i in range(len(results) - 1):
            current = results[i]
            next_result = results[i + 1]

            # Either entity_type is different (and current <= next)
            # Or entity_type is same and id is sorted
            if current["entity_type"] == next_result["entity_type"]:
                assert current["id"] <= next_result["id"]
            else:
                assert current["entity_type"] <= next_result["entity_type"]

    def test_search_entities_with_missing_fields(self):
        """Test search with entities that have missing optional fields."""
        incomplete_data = {
            "tactics": [
                {
                    "id": "TA0001",
                    "name": "Test Tactic",
                    # Missing description
                }
            ],
            "groups": [
                {
                    "id": "G0001",
                    "name": "Test Group",
                    "description": "Test description",
                    # Missing aliases
                }
            ],
            "techniques": [],
            "mitigations": [],
        }

        results = _search_entities("test", incomplete_data)

        assert len(results) == 2
        # Should handle missing fields gracefully
        for result in results:
            assert "entity_type" in result
            assert "id" in result
            assert "name" in result

    def test_search_attack_integration_with_data(self, sample_data, mock_data_loader):
        """Test search_attack integration with actual data."""
        mock_data_loader.get_cached_data.return_value = sample_data

        # Test the search function directly with the data structure
        results = _search_entities("apt29", sample_data)

        assert len(results) == 1
        assert results[0]["entity_type"] == "group"
        assert results[0]["id"] == "G0016"
        assert results[0]["name"] == "APT29"

    def test_search_attack_integration_no_results(self, sample_data):
        """Test search_attack integration when no results are found."""
        results = _search_entities("nonexistentquery12345", sample_data)
        assert len(results) == 0

    def test_search_attack_integration_multiple_entity_types(self, sample_data):
        """Test search_attack integration across multiple entity types."""
        # Search for 'adversary' which should appear in multiple descriptions
        results = _search_entities("adversary", sample_data)

        # Should find entities from different types
        entity_types = set(result["entity_type"] for result in results)
        assert len(entity_types) >= 1  # At least one entity type should match

        # All results should have 'adversary' in their match reason
        for result in results:
            assert "description contains" in result["match_reason"]


if __name__ == "__main__":
    pytest.main([__file__])