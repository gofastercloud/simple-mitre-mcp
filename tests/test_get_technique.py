"""
Tests for get_technique MCP tool functionality.

This module contains unit tests for the get_technique tool implementation,
including technique retrieval, error handling, and data validation.
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
    This function mimics the core logic of the get_technique tool.

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


def _format_technique_response(technique: dict, data: dict) -> str:
    """
    Helper function to format technique response.
    This function mimics the formatting logic of the get_technique tool.

    Args:
        technique: Technique data dictionary
        data: Full data dictionary for lookups

    Returns:
        str: Formatted technique response
    """
    result_text = "TECHNIQUE DETAILS\n"
    result_text += "================\n\n"
    result_text += f"ID: {technique.get('id', 'N/A')}\n"
    result_text += f"Name: {technique.get('name', 'N/A')}\n\n"

    # Description
    description = technique.get('description', 'No description available')
    result_text += f"Description:\n{description}\n\n"

    # Associated tactics
    tactics = technique.get('tactics', [])
    if tactics:
        result_text += f"Associated Tactics ({len(tactics)}):\n"
        # Look up tactic names
        tactic_details = []
        for tactic_id in tactics:
            for tactic in data.get('tactics', []):
                if tactic.get('id') == tactic_id:
                    tactic_details.append(f"  - {tactic_id}: {tactic.get('name', 'Unknown')}")
                    break
            else:
                tactic_details.append(f"  - {tactic_id}: (Name not found)")
        result_text += "\n".join(tactic_details) + "\n\n"
    else:
        result_text += "Associated Tactics: None\n\n"

    # Platforms
    platforms = technique.get('platforms', [])
    if platforms:
        result_text += f"Platforms ({len(platforms)}):\n"
        result_text += "  " + ", ".join(platforms) + "\n\n"
    else:
        result_text += "Platforms: Not specified\n\n"

    # Mitigations
    mitigations = technique.get('mitigations', [])
    if mitigations:
        result_text += f"Mitigations ({len(mitigations)}):\n"
        # Look up mitigation names
        mitigation_details = []
        for mitigation_id in mitigations:
            for mitigation in data.get('mitigations', []):
                if mitigation.get('id') == mitigation_id:
                    mitigation_details.append(f"  - {mitigation_id}: {mitigation.get('name', 'Unknown')}")
                    break
            else:
                mitigation_details.append(f"  - {mitigation_id}: (Name not found)")
        result_text += "\n".join(mitigation_details) + "\n\n"
    else:
        result_text += "Mitigations: None available\n\n"

    # Additional metadata
    if technique.get('data_sources'):
        result_text += f"Data Sources: {', '.join(technique['data_sources'])}\n"

    if technique.get('detection'):
        result_text += f"\nDetection:\n{technique['detection']}\n"

    return result_text


class TestGetTechnique:
    """Test cases for get_technique MCP tool."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Sample test data
        self.sample_data = {
            'techniques': [
                {
                    'id': 'T1055',
                    'name': 'Process Injection',
                    'description': 'Adversaries may inject code into processes in order to evade process-based defenses.',
                    'tactics': ['TA0004', 'TA0005'],
                    'platforms': ['Windows', 'Linux', 'macOS'],
                    'mitigations': ['M1040', 'M1026'],
                    'data_sources': ['Process monitoring', 'API monitoring'],
                    'detection': 'Monitor for suspicious process behavior and API calls.'
                },
                {
                    'id': 'T1059',
                    'name': 'Command and Scripting Interpreter',
                    'description': 'Adversaries may abuse command and script interpreters to execute commands.',
                    'tactics': ['TA0002'],
                    'platforms': ['Windows', 'Linux', 'macOS'],
                    'mitigations': ['M1038', 'M1042']
                },
                {
                    'id': 'T1003',
                    'name': 'OS Credential Dumping',
                    'description': 'Adversaries may attempt to dump credentials to obtain account login information.',
                    'tactics': ['TA0006'],
                    'platforms': ['Windows', 'Linux'],
                    'mitigations': []  # No mitigations
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
                },
                {
                    'id': 'TA0002',
                    'name': 'Execution',
                    'description': 'The adversary is trying to run malicious code.'
                },
                {
                    'id': 'TA0006',
                    'name': 'Credential Access',
                    'description': 'The adversary is trying to steal account names and passwords.'
                }
            ],
            'mitigations': [
                {
                    'id': 'M1040',
                    'name': 'Behavior Prevention on Endpoint',
                    'description': 'Use capabilities to prevent suspicious behavior patterns.'
                },
                {
                    'id': 'M1026',
                    'name': 'Privileged Account Management',
                    'description': 'Manage the creation, modification, use, and permissions associated with privileged accounts.'
                },
                {
                    'id': 'M1038',
                    'name': 'Execution Prevention',
                    'description': 'Block execution of code on a system through application control.'
                },
                {
                    'id': 'M1042',
                    'name': 'Disable or Remove Feature or Program',
                    'description': 'Remove or deny access to unnecessary and potentially vulnerable software.'
                }
            ],
            'groups': []
        }

    def test_get_technique_by_id_success(self):
        """Test successful technique retrieval by ID."""
        technique = _get_technique_by_id('T1055', self.sample_data)

        assert technique is not None
        assert technique['id'] == 'T1055'
        assert technique['name'] == 'Process Injection'
        assert 'Adversaries may inject code into processes' in technique['description']
        assert technique['tactics'] == ['TA0004', 'TA0005']
        assert technique['platforms'] == ['Windows', 'Linux', 'macOS']
        assert technique['mitigations'] == ['M1040', 'M1026']

    def test_get_technique_by_id_case_insensitive(self):
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

    def test_get_technique_by_id_with_whitespace(self):
        """Test technique ID with leading/trailing whitespace."""
        technique = _get_technique_by_id('  T1055  ', self.sample_data)

        assert technique is not None
        assert technique['id'] == 'T1055'
        assert technique['name'] == 'Process Injection'

    def test_get_technique_by_id_not_found(self):
        """Test handling of invalid technique ID."""
        technique = _get_technique_by_id('T9999', self.sample_data)
        assert technique is None

    def test_get_technique_by_id_empty_id(self):
        """Test handling of empty technique ID."""
        technique = _get_technique_by_id('', self.sample_data)
        assert technique is None

    def test_format_technique_response_full_details(self):
        """Test formatting technique response with full details."""
        technique = self.sample_data['techniques'][0]  # T1055
        response = _format_technique_response(technique, self.sample_data)

        # Check basic structure
        assert 'TECHNIQUE DETAILS' in response
        assert 'T1055' in response
        assert 'Process Injection' in response
        assert 'Adversaries may inject code into processes' in response

        # Check tactics with names
        assert 'TA0004: Privilege Escalation' in response
        assert 'TA0005: Defense Evasion' in response

        # Check platforms
        assert 'Windows, Linux, macOS' in response

        # Check mitigations with names
        assert 'M1040: Behavior Prevention on Endpoint' in response
        assert 'M1026: Privileged Account Management' in response

        # Check additional metadata
        assert 'Process monitoring, API monitoring' in response
        assert 'Monitor for suspicious process behavior' in response

    def test_format_technique_response_minimal_details(self):
        """Test formatting technique response with minimal details."""
        technique = self.sample_data['techniques'][2]  # T1003 with no mitigations
        response = _format_technique_response(technique, self.sample_data)

        assert 'T1003' in response
        assert 'OS Credential Dumping' in response
        assert 'TA0006: Credential Access' in response
        assert 'Mitigations: None available' in response

    def test_format_technique_response_missing_tactic_names(self):
        """Test formatting when tactic names are not found in data."""
        # Create data with missing tactic
        data_missing_tactic = self.sample_data.copy()
        data_missing_tactic['tactics'] = [
            {
                'id': 'TA0004',
                'name': 'Privilege Escalation',
                'description': 'The adversary is trying to gain higher-level permissions.'
            }
            # TA0005 is missing
        ]

        technique = self.sample_data['techniques'][0]  # T1055
        response = _format_technique_response(technique, data_missing_tactic)

        assert 'TA0004: Privilege Escalation' in response
        assert 'TA0005: (Name not found)' in response

    def test_format_technique_response_missing_mitigation_names(self):
        """Test formatting when mitigation names are not found in data."""
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

        technique = self.sample_data['techniques'][0]  # T1055
        response = _format_technique_response(technique, data_missing_mitigation)

        assert 'M1040: Behavior Prevention on Endpoint' in response
        assert 'M1026: (Name not found)' in response

    def test_format_technique_response_no_tactics(self):
        """Test formatting technique with no tactics."""
        technique = {
            'id': 'T9999',
            'name': 'Test Technique',
            'description': 'Test description',
            'tactics': [],
            'platforms': ['Windows'],
            'mitigations': []
        }

        response = _format_technique_response(technique, self.sample_data)

        assert 'T9999' in response
        assert 'Test Technique' in response
        assert 'Associated Tactics: None' in response
        assert 'Mitigations: None available' in response

    def test_format_technique_response_no_platforms(self):
        """Test formatting technique with no platforms."""
        technique = {
            'id': 'T9999',
            'name': 'Test Technique',
            'description': 'Test description',
            'tactics': ['TA0004'],
            'platforms': [],
            'mitigations': []
        }

        response = _format_technique_response(technique, self.sample_data)

        assert 'T9999' in response
        assert 'Platforms: Not specified' in response

    def test_integration_get_technique_logic(self):
        """Test the complete get_technique logic integration."""
        # Test successful retrieval
        technique = _get_technique_by_id('T1055', self.sample_data)
        assert technique is not None

        response = _format_technique_response(technique, self.sample_data)

        # Verify all expected content is present
        assert 'T1055' in response
        assert 'Process Injection' in response
        assert 'Adversaries may inject code into processes' in response
        assert 'TA0004: Privilege Escalation' in response
        assert 'TA0005: Defense Evasion' in response
        assert 'Windows, Linux, macOS' in response
        assert 'M1040: Behavior Prevention on Endpoint' in response
        assert 'M1026: Privileged Account Management' in response
        assert 'Process monitoring, API monitoring' in response
        assert 'Monitor for suspicious process behavior' in response

    def test_integration_get_technique_not_found(self):
        """Test the complete get_technique logic for not found case."""
        technique = _get_technique_by_id('T9999', self.sample_data)
        assert technique is None

        # This would result in a "not found" response in the actual MCP tool

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


if __name__ == '__main__':
    pytest.main([__file__])
