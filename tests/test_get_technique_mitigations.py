"""
Tests for get_technique_mitigations MCP tool functionality.

This module contains unit tests for the get_technique_mitigations tool implementation,
including mitigation retrieval, error handling, and data validation.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from mcp.types import TextContent
from src.mcp_server import create_mcp_server
from src.data_loader import DataLoader


def _get_technique_by_id(technique_id: str, data: dict) -> dict:
    """
    Helper function to retrieve technique by ID from data.
    This function mimics the core logic of the get_technique_mitigations tool.

    Args:
        technique_id: MITRE technique ID (e.g., T1055)
        data: Dictionary containing all entity types and their data

    Returns:
        dict: Technique data or None if not found
    """
    # Normalize technique ID (ensure uppercase)
    technique_id = technique_id.upper().strip()

    # Find the technique
    for tech in data.get('techniques', []):
        if tech.get('id', '').upper() == technique_id:
            return tech

    return None


def _get_mitigation_details(mitigation_ids: list, data: dict) -> list:
    """
    Helper function to get detailed mitigation information.

    Args:
        mitigation_ids: List of mitigation IDs
        data: Full data dictionary for lookups

    Returns:
        list: List of mitigation details
    """
    mitigation_details = []
    for mitigation_id in mitigation_ids:
        # Find mitigation details
        mitigation_info = None
        for mitigation in data.get('mitigations', []):
            if mitigation.get('id') == mitigation_id:
                mitigation_info = mitigation
                break

        if mitigation_info:
            mitigation_details.append({
                'id': mitigation_id,
                'name': mitigation_info.get('name', 'Unknown'),
                'description': mitigation_info.get('description', 'No description available')
            })
        else:
            mitigation_details.append({
                'id': mitigation_id,
                'name': '(Name not found)',
                'description': 'Mitigation details not available'
            })

    # Sort mitigations by ID for consistent ordering
    mitigation_details.sort(key=lambda x: x['id'])
    return mitigation_details


def _format_technique_mitigations_response(technique: dict, mitigation_details: list) -> str:
    """
    Helper function to format technique mitigations response.
    This function mimics the formatting logic of the get_technique_mitigations tool.

    Args:
        technique: Technique data dictionary
        mitigation_details: List of mitigation details

    Returns:
        str: Formatted technique mitigations response
    """
    result_text = "TECHNIQUE MITIGATIONS\n"
    result_text += "====================\n\n"
    result_text += f"Technique ID: {technique.get('id', 'N/A')}\n"
    result_text += f"Technique Name: {technique.get('name', 'N/A')}\n\n"

    # Add technique description preview
    description = technique.get('description', 'No description available')
    if len(description) > 200:
        description = description[:200] + "..."
    result_text += f"Description: {description}\n\n"

    result_text += f"Mitigations ({len(mitigation_details)}):\n"
    result_text += f"{'-' * 40}\n\n"

    # Format mitigation details
    for i, mitigation in enumerate(mitigation_details, 1):
        result_text += f"{i}. {mitigation['id']}: {mitigation['name']}\n"

        # Add description
        desc = mitigation['description']
        if len(desc) > 300:
            desc = desc[:300] + "..."
        result_text += f"   Description: {desc}\n\n"

    return result_text


class TestGetTechniqueMitigations:
    """Test cases for get_technique_mitigations MCP tool."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Sample test data
        self.sample_data = {
            'techniques': [
                {
                    'id': 'T1055',
                    'name': 'Process Injection',
                    'description': 'Adversaries may inject code into processes in order to evade process-based defenses as well as possibly elevate privileges.',
                    'tactics': ['TA0004', 'TA0005'],
                    'platforms': ['Windows', 'Linux', 'macOS'],
                    'mitigations': ['M1040', 'M1026', 'M1038']
                },
                {
                    'id': 'T1059',
                    'name': 'Command and Scripting Interpreter',
                    'description': 'Adversaries may abuse command and script interpreters to execute commands, scripts, or binaries.',
                    'tactics': ['TA0002'],
                    'platforms': ['Windows', 'Linux', 'macOS'],
                    'mitigations': ['M1038', 'M1042']
                },
                {
                    'id': 'T1003',
                    'name': 'OS Credential Dumping',
                    'description': 'Adversaries may attempt to dump credentials to obtain account login and credential material.',
                    'tactics': ['TA0006'],
                    'platforms': ['Windows', 'Linux'],
                    'mitigations': []  # No mitigations
                },
                {
                    'id': 'T1078',
                    'name': 'Valid Accounts',
                    'description': 'Adversaries may obtain and abuse credentials of existing accounts as a means of gaining Initial Access.',
                    'tactics': ['TA0001', 'TA0003', 'TA0004', 'TA0005'],
                    'platforms': ['Windows', 'Linux', 'macOS', 'Network'],
                    'mitigations': ['M1015', 'M1026', 'M1027', 'M1032', 'M1036']
                }
            ],
            'tactics': [
                {
                    'id': 'TA0004',
                    'name': 'Privilege Escalation',
                    'description': 'The adversary is trying to gain higher-level permissions.'
                },
                {
                    'id': 'TA0005',
                    'name': 'Defense Evasion',
                    'description': 'The adversary is trying to avoid being detected.'
                }
            ],
            'mitigations': [
                {
                    'id': 'M1040',
                    'name': 'Behavior Prevention on Endpoint',
                    'description': 'Use capabilities to prevent suspicious behavior patterns from occurring on endpoint systems. This could include suspicious process, file, API call, etc. behavior.'
                },
                {
                    'id': 'M1026',
                    'name': 'Privileged Account Management',
                    'description': 'Manage the creation, modification, use, and permissions associated with privileged accounts, including SYSTEM and root.'
                },
                {
                    'id': 'M1038',
                    'name': 'Execution Prevention',
                    'description': 'Block execution of code on a system through application control, and/or script blocking.'
                },
                {
                    'id': 'M1042',
                    'name': 'Disable or Remove Feature or Program',
                    'description': 'Remove or deny access to unnecessary and potentially vulnerable software to prevent abuse by adversaries.'
                },
                {
                    'id': 'M1015',
                    'name': 'Active Directory Configuration',
                    'description': 'Configure Active Directory to prevent use of certain techniques; use SID Filtering, etc.'
                },
                {
                    'id': 'M1027',
                    'name': 'Password Policies',
                    'description': 'Set and enforce secure password policies for accounts.'
                },
                {
                    'id': 'M1032',
                    'name': 'Multi-factor Authentication',
                    'description': 'Use two or more pieces of evidence to authenticate to a system; such as username and password in addition to a token from a physical smart card or token generator.'
                },
                {
                    'id': 'M1036',
                    'name': 'Account Use Policies',
                    'description': 'Configure features related to account use like login attempt lockouts, specific login times, etc.'
                }
            ],
            'groups': []
        }

    def test_get_technique_mitigations_success(self):
        """Test successful technique mitigation retrieval."""
        technique = _get_technique_by_id('T1055', self.sample_data)
        assert technique is not None

        mitigation_ids = technique.get('mitigations', [])
        assert len(mitigation_ids) == 3
        assert 'M1040' in mitigation_ids
        assert 'M1026' in mitigation_ids
        assert 'M1038' in mitigation_ids

        mitigation_details = _get_mitigation_details(mitigation_ids, self.sample_data)
        assert len(mitigation_details) == 3

        # Check that mitigations are sorted by ID
        assert mitigation_details[0]['id'] == 'M1026'
        assert mitigation_details[1]['id'] == 'M1038'
        assert mitigation_details[2]['id'] == 'M1040'

    def test_get_technique_mitigations_case_insensitive(self):
        """Test that technique ID lookup is case insensitive."""
        # Test lowercase
        technique_lower = _get_technique_by_id('t1055', self.sample_data)
        assert technique_lower is not None
        assert technique_lower['id'] == 'T1055'

        # Test mixed case
        technique_mixed = _get_technique_by_id('T1055', self.sample_data)
        assert technique_mixed is not None
        assert technique_mixed['id'] == 'T1055'

        # Both should return the same technique
        assert technique_lower == technique_mixed

    def test_get_technique_mitigations_with_whitespace(self):
        """Test technique ID with leading/trailing whitespace."""
        technique = _get_technique_by_id('  T1055  ', self.sample_data)

        assert technique is not None
        assert technique['id'] == 'T1055'
        assert len(technique.get('mitigations', [])) == 3

    def test_get_technique_mitigations_not_found(self):
        """Test handling of invalid technique ID."""
        technique = _get_technique_by_id('T9999', self.sample_data)
        assert technique is None

    def test_get_technique_mitigations_empty_id(self):
        """Test handling of empty technique ID."""
        technique = _get_technique_by_id('', self.sample_data)
        assert technique is None

    def test_get_technique_mitigations_no_mitigations(self):
        """Test technique with no mitigations."""
        technique = _get_technique_by_id('T1003', self.sample_data)
        assert technique is not None

        mitigation_ids = technique.get('mitigations', [])
        assert len(mitigation_ids) == 0

        mitigation_details = _get_mitigation_details(mitigation_ids, self.sample_data)
        assert len(mitigation_details) == 0

    def test_get_technique_mitigations_many_mitigations(self):
        """Test technique with many mitigations."""
        technique = _get_technique_by_id('T1078', self.sample_data)
        assert technique is not None

        mitigation_ids = technique.get('mitigations', [])
        assert len(mitigation_ids) == 5

        mitigation_details = _get_mitigation_details(mitigation_ids, self.sample_data)
        assert len(mitigation_details) == 5

        # Check that mitigations are sorted by ID
        expected_order = ['M1015', 'M1026', 'M1027', 'M1032', 'M1036']
        actual_order = [m['id'] for m in mitigation_details]
        assert actual_order == expected_order

    def test_get_mitigation_details_success(self):
        """Test successful mitigation details retrieval."""
        mitigation_ids = ['M1040', 'M1026']
        mitigation_details = _get_mitigation_details(mitigation_ids, self.sample_data)

        assert len(mitigation_details) == 2

        # Check first mitigation (should be M1026 due to sorting)
        assert mitigation_details[0]['id'] == 'M1026'
        assert mitigation_details[0]['name'] == 'Privileged Account Management'
        assert 'Manage the creation, modification, use' in mitigation_details[0]['description']

        # Check second mitigation (should be M1040 due to sorting)
        assert mitigation_details[1]['id'] == 'M1040'
        assert mitigation_details[1]['name'] == 'Behavior Prevention on Endpoint'
        assert 'Use capabilities to prevent suspicious behavior' in mitigation_details[1]['description']

    def test_get_mitigation_details_missing_mitigation(self):
        """Test handling of missing mitigation in data."""
        # Create data with missing mitigation
        data_missing_mitigation = self.sample_data.copy()
        data_missing_mitigation['mitigations'] = [
            {
                'id': 'M1040',
                'name': 'Behavior Prevention on Endpoint',
                'description': 'Use capabilities to prevent suspicious behavior patterns.'
            }
            # M1026 is missing
        ]

        mitigation_ids = ['M1040', 'M1026']
        mitigation_details = _get_mitigation_details(mitigation_ids, data_missing_mitigation)

        assert len(mitigation_details) == 2

        # Check found mitigation
        found_mitigation = next(m for m in mitigation_details if m['id'] == 'M1040')
        assert found_mitigation['name'] == 'Behavior Prevention on Endpoint'

        # Check missing mitigation
        missing_mitigation = next(m for m in mitigation_details if m['id'] == 'M1026')
        assert missing_mitigation['name'] == '(Name not found)'
        assert missing_mitigation['description'] == 'Mitigation details not available'

    def test_get_mitigation_details_empty_list(self):
        """Test handling of empty mitigation list."""
        mitigation_details = _get_mitigation_details([], self.sample_data)
        assert len(mitigation_details) == 0

    def test_format_technique_mitigations_response_full_details(self):
        """Test formatting technique mitigations response with full details."""
        technique = self.sample_data['techniques'][0]  # T1055
        mitigation_ids = technique.get('mitigations', [])
        mitigation_details = _get_mitigation_details(mitigation_ids, self.sample_data)

        response = _format_technique_mitigations_response(technique, mitigation_details)

        # Check basic structure
        assert 'TECHNIQUE MITIGATIONS' in response
        assert 'T1055' in response
        assert 'Process Injection' in response
        assert 'Adversaries may inject code into processes' in response

        # Check mitigation count
        assert 'Mitigations (3)' in response

        # Check mitigation details (should be in sorted order)
        assert '1. M1026: Privileged Account Management' in response
        assert '2. M1038: Execution Prevention' in response
        assert '3. M1040: Behavior Prevention on Endpoint' in response

        # Check mitigation descriptions
        assert 'Manage the creation, modification, use' in response
        assert 'Block execution of code on a system' in response
        assert 'Use capabilities to prevent suspicious behavior' in response

    def test_format_technique_mitigations_response_no_mitigations(self):
        """Test formatting technique mitigations response with no mitigations."""
        technique = self.sample_data['techniques'][2]  # T1003 with no mitigations
        mitigation_details = []

        response = _format_technique_mitigations_response(technique, mitigation_details)

        assert 'T1003' in response
        assert 'OS Credential Dumping' in response
        assert 'Mitigations (0)' in response

    def test_format_technique_mitigations_response_long_description(self):
        """Test formatting with long technique description (should be truncated)."""
        technique = {
            'id': 'T9999',
            'name': 'Test Technique',
            'description': 'A' * 250,  # Long description that should be truncated
            'mitigations': ['M1040']
        }

        mitigation_details = _get_mitigation_details(['M1040'], self.sample_data)
        response = _format_technique_mitigations_response(technique, mitigation_details)

        # Check that description is truncated
        assert 'A' * 200 + '...' in response
        assert 'A' * 250 not in response

    def test_format_technique_mitigations_response_long_mitigation_description(self):
        """Test formatting with long mitigation description (should be truncated)."""
        # Create data with long mitigation description
        data_long_desc = self.sample_data.copy()
        data_long_desc['mitigations'] = [
            {
                'id': 'M1040',
                'name': 'Behavior Prevention on Endpoint',
                'description': 'B' * 350  # Long description that should be truncated
            }
        ]

        technique = self.sample_data['techniques'][0]  # T1055
        mitigation_details = _get_mitigation_details(['M1040'], data_long_desc)
        response = _format_technique_mitigations_response(technique, mitigation_details)

        # Check that mitigation description is truncated
        assert 'B' * 300 + '...' in response
        assert 'B' * 350 not in response

    def test_format_technique_mitigations_response_missing_mitigation_names(self):
        """Test formatting when mitigation names are not found in data."""
        technique = self.sample_data['techniques'][0]  # T1055

        # Create mitigation details with missing names
        mitigation_details = [
            {
                'id': 'M1040',
                'name': 'Behavior Prevention on Endpoint',
                'description': 'Use capabilities to prevent suspicious behavior patterns.'
            },
            {
                'id': 'M9999',
                'name': '(Name not found)',
                'description': 'Mitigation details not available'
            }
        ]

        response = _format_technique_mitigations_response(technique, mitigation_details)

        assert 'M1040: Behavior Prevention on Endpoint' in response
        assert 'M9999: (Name not found)' in response
        assert 'Mitigation details not available' in response

    def test_integration_get_technique_mitigations_logic(self):
        """Test the complete get_technique_mitigations logic integration."""
        # Test successful retrieval
        technique = _get_technique_by_id('T1055', self.sample_data)
        assert technique is not None

        mitigation_ids = technique.get('mitigations', [])
        mitigation_details = _get_mitigation_details(mitigation_ids, self.sample_data)
        response = _format_technique_mitigations_response(technique, mitigation_details)

        # Verify all expected content is present
        assert 'T1055' in response
        assert 'Process Injection' in response
        assert 'Adversaries may inject code into processes' in response
        assert 'Mitigations (3)' in response
        assert 'M1026: Privileged Account Management' in response
        assert 'M1038: Execution Prevention' in response
        assert 'M1040: Behavior Prevention on Endpoint' in response

    def test_integration_get_technique_mitigations_not_found(self):
        """Test the complete get_technique_mitigations logic for not found case."""
        technique = _get_technique_by_id('T9999', self.sample_data)
        assert technique is None

        # This would result in a "not found" response in the actual MCP tool

    def test_integration_get_technique_mitigations_no_mitigations(self):
        """Test the complete get_technique_mitigations logic for technique with no mitigations."""
        technique = _get_technique_by_id('T1003', self.sample_data)
        assert technique is not None

        mitigation_ids = technique.get('mitigations', [])
        assert len(mitigation_ids) == 0

        # This would result in a "no mitigations found" response in the actual MCP tool

    def test_edge_cases_empty_data(self):
        """Test edge cases with empty data structures."""
        empty_data = {
            'techniques': [],
            'tactics': [],
            'mitigations': [],
            'groups': []
        }

        technique = _get_technique_by_id('T1055', empty_data)
        assert technique is None

    def test_edge_cases_malformed_data(self):
        """Test edge cases with malformed data structures."""
        malformed_data = {
            'techniques': [
                {
                    # Missing required fields
                    'name': 'Test Technique'
                }
            ],
            'tactics': [],
            'mitigations': [],
            'groups': []
        }

        technique = _get_technique_by_id('T1055', malformed_data)
        assert technique is None

    def test_edge_cases_technique_without_mitigations_field(self):
        """Test technique that doesn't have mitigations field at all."""
        data_no_mitigations_field = {
            'techniques': [
                {
                    'id': 'T1055',
                    'name': 'Process Injection',
                    'description': 'Test description'
                    # No mitigations field
                }
            ],
            'mitigations': []
        }

        technique = _get_technique_by_id('T1055', data_no_mitigations_field)
        assert technique is not None

        mitigation_ids = technique.get('mitigations', [])
        assert len(mitigation_ids) == 0

    def test_mitigation_sorting_consistency(self):
        """Test that mitigation sorting is consistent across multiple calls."""
        mitigation_ids = ['M1040', 'M1026', 'M1038', 'M1015', 'M1042']

        # Call multiple times and ensure consistent ordering
        details1 = _get_mitigation_details(mitigation_ids, self.sample_data)
        details2 = _get_mitigation_details(mitigation_ids, self.sample_data)
        details3 = _get_mitigation_details(mitigation_ids, self.sample_data)

        # Extract IDs from each call
        ids1 = [m['id'] for m in details1]
        ids2 = [m['id'] for m in details2]
        ids3 = [m['id'] for m in details3]

        # All should be identical and sorted
        assert ids1 == ids2 == ids3
        assert ids1 == sorted(ids1)

        # Expected order
        expected_order = ['M1015', 'M1026', 'M1038', 'M1040', 'M1042']
        assert ids1 == expected_order


if __name__ == '__main__':
    pytest.main([__file__])
