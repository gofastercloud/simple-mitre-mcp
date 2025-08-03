"""
Tests for list_tactics tool functionality.

This module contains unit tests for the list_tactics MCP tool,
including tactics listing, formatting, and edge cases.
"""

import pytest
from unittest.mock import Mock
from src.data_loader import DataLoader


def _get_all_tactics(data: dict) -> list:
    """
    Helper function to retrieve all tactics from data.
    This function mimics the core logic of the list_tactics tool.

    Args:
        data: Dictionary containing all entity types and their data

    Returns:
        list: List of all tactics sorted by ID
    """
    tactics = data.get('tactics', [])
    # Sort tactics by ID for consistent ordering
    return sorted(tactics, key=lambda x: x.get('id', ''))


def _format_tactics_response(tactics: list) -> str:
    """
    Helper function to format tactics listing response.
    This function mimics the formatting logic of the list_tactics tool.

    Args:
        tactics: List of tactic dictionaries

    Returns:
        str: Formatted tactics listing response
    """
    if not tactics:
        return "No tactics found in the loaded data."

    # Build formatted response
    result_text = "MITRE ATT&CK TACTICS\n"
    result_text += "===================\n\n"
    result_text += f"Total tactics: {len(tactics)}\n\n"

    for tactic in tactics:
        tactic_id = tactic.get('id', 'N/A')
        tactic_name = tactic.get('name', 'N/A')
        tactic_description = tactic.get('description', 'No description available')

        result_text += f"ID: {tactic_id}\n"
        result_text += f"Name: {tactic_name}\n"
        result_text += f"Description: {tactic_description}\n"
        result_text += f"{'-' * 50}\n\n"

    return result_text


class TestListTactics:
    """Test cases for list_tactics tool functionality."""

    def setup_method(self):
        """Set up test data for each test method."""
        self.sample_tactics_data = {
            'tactics': [
                {
                    'id': 'TA0001',
                    'name': 'Initial Access',
                    'description': 'The adversary is trying to get into your network. Initial Access consists of techniques that use various entry vectors to gain their initial foothold within a network.'
                },
                {
                    'id': 'TA0002',
                    'name': 'Execution',
                    'description': 'The adversary is trying to run malicious code. Execution consists of techniques that result in adversary-controlled code running on a local or remote system.'
                },
                {
                    'id': 'TA0003',
                    'name': 'Persistence',
                    'description': 'The adversary is trying to maintain their foothold. Persistence consists of techniques that adversaries use to keep access to systems across restarts.'
                }
            ],
            'techniques': [],
            'groups': [],
            'mitigations': []
        }

        self.empty_data = {
            'tactics': [],
            'techniques': [],
            'groups': [],
            'mitigations': []
        }

    def test_get_all_tactics_success(self):
        """Test successful tactics retrieval."""
        tactics = _get_all_tactics(self.sample_tactics_data)

        assert len(tactics) == 3
        assert tactics[0]['id'] == 'TA0001'
        assert tactics[0]['name'] == 'Initial Access'
        assert tactics[1]['id'] == 'TA0002'
        assert tactics[1]['name'] == 'Execution'
        assert tactics[2]['id'] == 'TA0003'
        assert tactics[2]['name'] == 'Persistence'

    def test_get_all_tactics_empty_data(self):
        """Test tactics retrieval with no tactics in data."""
        tactics = _get_all_tactics(self.empty_data)

        assert len(tactics) == 0
        assert tactics == []

    def test_get_all_tactics_missing_tactics_key(self):
        """Test tactics retrieval when tactics key is missing."""
        data_no_tactics_key = {
            'techniques': [],
            'groups': [],
            'mitigations': []
        }

        tactics = _get_all_tactics(data_no_tactics_key)
        assert len(tactics) == 0
        assert tactics == []

    def test_get_all_tactics_sorting(self):
        """Test that tactics are sorted by ID."""
        # Create data with tactics in non-alphabetical order
        unsorted_data = {
            'tactics': [
                {
                    'id': 'TA0003',
                    'name': 'Persistence',
                    'description': 'Persistence description'
                },
                {
                    'id': 'TA0001',
                    'name': 'Initial Access',
                    'description': 'Initial Access description'
                },
                {
                    'id': 'TA0002',
                    'name': 'Execution',
                    'description': 'Execution description'
                }
            ],
            'techniques': [],
            'groups': [],
            'mitigations': []
        }

        tactics = _get_all_tactics(unsorted_data)

        # Verify sorting - should be TA0001, TA0002, TA0003
        assert len(tactics) == 3
        assert tactics[0]['id'] == 'TA0001'
        assert tactics[1]['id'] == 'TA0002'
        assert tactics[2]['id'] == 'TA0003'

    def test_get_all_tactics_missing_fields(self):
        """Test tactics retrieval with missing optional fields."""
        incomplete_data = {
            'tactics': [
                {
                    'id': 'TA0001',
                    'name': 'Initial Access'
                    # Missing description
                },
                {
                    'id': 'TA0002',
                    # Missing name
                    'description': 'Some description'
                },
                {
                    # Missing id
                    'name': 'Some Tactic',
                    'description': 'Some description'
                }
            ],
            'techniques': [],
            'groups': [],
            'mitigations': []
        }

        tactics = _get_all_tactics(incomplete_data)

        # Should handle missing fields gracefully
        assert len(tactics) == 3

        # Check that tactics are still returned even with missing fields
        # The sorting should handle missing IDs by treating them as empty strings
        for tactic in tactics:
            assert isinstance(tactic, dict)

    def test_format_tactics_response_success(self):
        """Test successful tactics response formatting."""
        tactics = self.sample_tactics_data['tactics']
        response = _format_tactics_response(tactics)

        # Check header format
        assert "MITRE ATT&CK TACTICS" in response
        assert "===================" in response

        # Check total count
        assert "Total tactics: 3" in response

        # Check individual tactic format
        assert "ID: TA0001" in response
        assert "Name: Initial Access" in response
        assert "Description: The adversary is trying to get into your network" in response

        assert "ID: TA0002" in response
        assert "Name: Execution" in response

        assert "ID: TA0003" in response
        assert "Name: Persistence" in response

        # Check separators
        assert "---" in response  # Should have separators between tactics

    def test_format_tactics_response_empty_list(self):
        """Test formatting with empty tactics list."""
        response = _format_tactics_response([])

        assert response == "No tactics found in the loaded data."

    def test_format_tactics_response_missing_fields(self):
        """Test formatting with missing optional fields."""
        incomplete_tactics = [
            {
                'id': 'TA0001',
                'name': 'Initial Access'
                # Missing description
            },
            {
                'id': 'TA0002',
                # Missing name
                'description': 'Some description'
            },
            {
                # Missing id
                'name': 'Some Tactic',
                'description': 'Some description'
            }
        ]

        response = _format_tactics_response(incomplete_tactics)

        # Should handle missing fields gracefully
        assert "Total tactics: 3" in response
        assert "N/A" in response  # Should show N/A for missing fields
        assert "No description available" in response  # Should show default for missing description

    def test_integration_list_tactics_logic(self):
        """Test the complete list_tactics logic integration."""
        # Test successful retrieval and formatting
        tactics = _get_all_tactics(self.sample_tactics_data)
        assert len(tactics) == 3

        response = _format_tactics_response(tactics)

        # Verify all expected content is present
        assert "MITRE ATT&CK TACTICS" in response
        assert "Total tactics: 3" in response
        assert "TA0001" in response
        assert "Initial Access" in response
        assert "TA0002" in response
        assert "Execution" in response
        assert "TA0003" in response
        assert "Persistence" in response

    def test_integration_list_tactics_empty_data(self):
        """Test the complete list_tactics logic for empty data case."""
        tactics = _get_all_tactics(self.empty_data)
        assert len(tactics) == 0

        response = _format_tactics_response(tactics)
        assert response == "No tactics found in the loaded data."

    def test_edge_cases_empty_data_structure(self):
        """Test edge cases with empty data structures."""
        empty_data = {}

        tactics = _get_all_tactics(empty_data)
        assert len(tactics) == 0
        assert tactics == []

    def test_edge_cases_malformed_data(self):
        """Test edge cases with malformed data structures."""
        malformed_data = {
            'tactics': [
                {
                    # Missing all fields
                }
            ]
        }

        tactics = _get_all_tactics(malformed_data)
        assert len(tactics) == 1

        response = _format_tactics_response(tactics)
        assert "N/A" in response  # Should handle missing fields gracefully


if __name__ == '__main__':
    pytest.main([__file__])
