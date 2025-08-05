"""
Tests for get_group_techniques tool functionality.

This module contains unit tests for the get_group_techniques MCP tool,
including group validation, technique retrieval, and edge cases.
"""

import pytest
from unittest.mock import Mock
from src.data_loader import DataLoader


def _find_group_by_id(group_id: str, data: dict) -> dict:
    """
    Helper function to find a group by ID.
    This function mimics the core logic of the get_group_techniques tool.

    Args:
        group_id: MITRE group ID (normalized to uppercase)
        data: Dictionary containing all entity types and their data

    Returns:
        dict: Group dictionary if found, None otherwise
    """
    group_id = group_id.upper().strip()

    for group in data.get("groups", []):
        if group.get("id", "").upper() == group_id:
            return group

    return None


def _get_technique_details(technique_ids: list, data: dict) -> list:
    """
    Helper function to get technique details for a list of technique IDs.
    This function mimics the technique lookup logic of the get_group_techniques tool.

    Args:
        technique_ids: List of technique IDs
        data: Dictionary containing all entity types and their data

    Returns:
        list: List of technique detail dictionaries
    """
    technique_details = []

    for technique_id in technique_ids:
        # Find technique details
        technique_info = None
        for tech in data.get("techniques", []):
            if tech.get("id") == technique_id:
                technique_info = tech
                break

        if technique_info:
            technique_details.append(
                {
                    "id": technique_id,
                    "name": technique_info.get("name", "Unknown"),
                    "description": technique_info.get(
                        "description", "No description available"
                    ),
                    "tactics": technique_info.get("tactics", []),
                    "platforms": technique_info.get("platforms", []),
                }
            )
        else:
            technique_details.append(
                {
                    "id": technique_id,
                    "name": "(Name not found)",
                    "description": "Technique details not available",
                    "tactics": [],
                    "platforms": [],
                }
            )

    # Sort techniques by ID for consistent ordering
    technique_details.sort(key=lambda x: x["id"])

    return technique_details


def _format_group_techniques_response(
    group: dict, technique_details: list, data: dict
) -> str:
    """
    Helper function to format group techniques response.
    This function mimics the formatting logic of the get_group_techniques tool.

    Args:
        group: Group dictionary
        technique_details: List of technique detail dictionaries
        data: Dictionary containing all entity types for tactic name lookup

    Returns:
        str: Formatted group techniques response
    """
    if not technique_details:
        return f"No techniques found for group '{group.get('id', 'Unknown')}' ({group.get('name', 'Unknown')})."

    # Build detailed response
    result_text = "GROUP TECHNIQUES\n"
    result_text += "================\n\n"
    result_text += f"Group ID: {group.get('id', 'N/A')}\n"
    result_text += f"Group Name: {group.get('name', 'N/A')}\n"

    # Add aliases if available
    aliases = group.get("aliases", [])
    if aliases:
        result_text += f"Aliases: {', '.join(aliases)}\n"

    result_text += (
        f"\nDescription:\n{group.get('description', 'No description available')}\n\n"
    )

    result_text += f"Techniques Used ({len(technique_details)}):\n"
    result_text += f"{'-' * 40}\n\n"

    # Format technique details
    for i, tech in enumerate(technique_details, 1):
        result_text += f"{i}. {tech['id']}: {tech['name']}\n"

        # Add description preview
        desc = tech["description"]
        if len(desc) > 150:
            desc = desc[:150] + "..."
        result_text += f"   Description: {desc}\n"

        # Add tactics if available
        if tech["tactics"]:
            tactic_names = []
            for tactic_id in tech["tactics"]:
                # Look up tactic name
                for tactic in data.get("tactics", []):
                    if tactic.get("id") == tactic_id:
                        tactic_names.append(
                            f"{tactic_id} ({tactic.get('name', 'Unknown')})"
                        )
                        break
                else:
                    tactic_names.append(f"{tactic_id} (Name not found)")
            result_text += f"   Tactics: {', '.join(tactic_names)}\n"

        # Add platforms if available
        if tech["platforms"]:
            result_text += f"   Platforms: {', '.join(tech['platforms'])}\n"

        result_text += "\n"

    return result_text


class TestGetGroupTechniques:
    """Test cases for get_group_techniques tool functionality."""

    def setup_method(self):
        """Set up test data for each test method."""
        self.sample_data = {
            "groups": [
                {
                    "id": "G0016",
                    "name": "APT29",
                    "aliases": ["Cozy Bear", "The Dukes"],
                    "description": "APT29 is a threat group that has been attributed to Russia.",
                    "techniques": ["T1055", "T1059", "T1071"],
                },
                {
                    "id": "G0007",
                    "name": "APT1",
                    "aliases": ["Comment Crew", "PLA Unit 61398"],
                    "description": "APT1 is a Chinese threat group.",
                    "techniques": ["T1059", "T1105"],
                },
                {
                    "id": "G0001",
                    "name": "Axiom",
                    "aliases": ["Group 72"],
                    "description": "Axiom is a cyber espionage group.",
                    "techniques": [],  # Group with no techniques
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
                {
                    "id": "T1071",
                    "name": "Application Layer Protocol",
                    "description": "Adversaries may communicate using application layer protocols.",
                    "tactics": ["TA0011"],
                    "platforms": ["Windows", "Linux", "macOS"],
                },
                {
                    "id": "T1105",
                    "name": "Ingress Tool Transfer",
                    "description": "Adversaries may transfer tools or other files from an external system.",
                    "tactics": ["TA0011"],
                    "platforms": ["Windows", "Linux", "macOS"],
                },
            ],
            "tactics": [
                {
                    "id": "TA0002",
                    "name": "Execution",
                    "description": "The adversary is trying to run malicious code.",
                },
                {
                    "id": "TA0004",
                    "name": "Privilege Escalation",
                    "description": "The adversary is trying to gain higher-level permissions.",
                },
                {
                    "id": "TA0005",
                    "name": "Defense Evasion",
                    "description": "The adversary is trying to avoid being detected.",
                },
                {
                    "id": "TA0011",
                    "name": "Command and Control",
                    "description": "The adversary is trying to communicate with compromised systems.",
                },
            ],
            "mitigations": [],
        }

    def test_find_group_by_id_valid_group(self):
        """Test finding a valid group by ID."""
        group = _find_group_by_id("G0016", self.sample_data)

        assert group is not None
        assert group["id"] == "G0016"
        assert group["name"] == "APT29"
        assert "Cozy Bear" in group["aliases"]
        assert len(group["techniques"]) == 3

    def test_find_group_by_id_case_insensitive(self):
        """Test that group ID lookup is case insensitive."""
        group_lower = _find_group_by_id("g0016", self.sample_data)
        group_upper = _find_group_by_id("G0016", self.sample_data)
        group_mixed = _find_group_by_id("g0016", self.sample_data)

        assert group_lower is not None
        assert group_upper is not None
        assert group_mixed is not None

        # All should return the same group
        assert group_lower["id"] == group_upper["id"] == group_mixed["id"]
        assert group_lower["name"] == "APT29"

    def test_find_group_by_id_invalid_group(self):
        """Test finding an invalid group ID."""
        group = _find_group_by_id("G9999", self.sample_data)

        assert group is None

    def test_find_group_by_id_whitespace_handling(self):
        """Test that group ID whitespace is handled correctly."""
        group = _find_group_by_id("  G0016  ", self.sample_data)

        assert group is not None
        assert group["id"] == "G0016"
        assert group["name"] == "APT29"

    def test_get_technique_details_valid_techniques(self):
        """Test getting technique details for valid technique IDs."""
        technique_ids = ["T1055", "T1059"]
        details = _get_technique_details(technique_ids, self.sample_data)

        assert len(details) == 2

        # Check first technique (should be sorted)
        assert details[0]["id"] == "T1055"
        assert details[0]["name"] == "Process Injection"
        assert "TA0004" in details[0]["tactics"]
        assert "Windows" in details[0]["platforms"]

        # Check second technique
        assert details[1]["id"] == "T1059"
        assert details[1]["name"] == "Command and Scripting Interpreter"
        assert "TA0002" in details[1]["tactics"]

    def test_get_technique_details_missing_techniques(self):
        """Test getting technique details for missing technique IDs."""
        technique_ids = ["T1055", "T9999"]  # T9999 doesn't exist
        details = _get_technique_details(technique_ids, self.sample_data)

        assert len(details) == 2

        # Check valid technique
        assert details[0]["id"] == "T1055"
        assert details[0]["name"] == "Process Injection"

        # Check missing technique
        assert details[1]["id"] == "T9999"
        assert details[1]["name"] == "(Name not found)"
        assert details[1]["description"] == "Technique details not available"
        assert details[1]["tactics"] == []
        assert details[1]["platforms"] == []

    def test_get_technique_details_sorting(self):
        """Test that technique details are sorted by ID."""
        technique_ids = ["T1071", "T1055", "T1059"]  # Unsorted input
        details = _get_technique_details(technique_ids, self.sample_data)

        assert len(details) == 3

        # Should be sorted: T1055, T1059, T1071
        assert details[0]["id"] == "T1055"
        assert details[1]["id"] == "T1059"
        assert details[2]["id"] == "T1071"

    def test_get_technique_details_empty_list(self):
        """Test getting technique details for empty technique list."""
        details = _get_technique_details([], self.sample_data)

        assert len(details) == 0
        assert details == []

    def test_format_group_techniques_response_success(self):
        """Test successful group techniques response formatting."""
        group = self.sample_data["groups"][0]  # APT29
        technique_details = _get_technique_details(
            group["techniques"], self.sample_data
        )
        response = _format_group_techniques_response(
            group, technique_details, self.sample_data
        )

        # Check header format
        assert "GROUP TECHNIQUES" in response
        assert "================" in response

        # Check group information
        assert "Group ID: G0016" in response
        assert "Group Name: APT29" in response
        assert "Aliases: Cozy Bear, The Dukes" in response
        assert "APT29 is a threat group that has been attributed to Russia" in response

        # Check techniques count
        assert "Techniques Used (3)" in response

        # Check individual techniques
        assert "T1055: Process Injection" in response
        assert "T1059: Command and Scripting Interpreter" in response
        assert "T1071: Application Layer Protocol" in response

        # Check tactics with names
        assert "TA0004 (Privilege Escalation)" in response
        assert "TA0002 (Execution)" in response
        assert "TA0011 (Command and Control)" in response

        # Check platforms
        assert "Windows" in response
        assert "Linux" in response

    def test_format_group_techniques_response_no_techniques(self):
        """Test formatting response for group with no techniques."""
        group = self.sample_data["groups"][2]  # Axiom with no techniques
        technique_details = _get_technique_details(
            group["techniques"], self.sample_data
        )
        response = _format_group_techniques_response(
            group, technique_details, self.sample_data
        )

        assert "No techniques found for group 'G0001' (Axiom)" in response

    def test_format_group_techniques_response_missing_technique_details(self):
        """Test formatting response with missing technique details."""
        group = {
            "id": "G0016",
            "name": "APT29",
            "aliases": ["Cozy Bear"],
            "description": "APT29 is a threat group.",
            "techniques": ["T1055", "T9999"],  # T9999 doesn't exist
        }

        technique_details = _get_technique_details(
            group["techniques"], self.sample_data
        )
        response = _format_group_techniques_response(
            group, technique_details, self.sample_data
        )

        # Should handle missing technique gracefully
        assert "T1055: Process Injection" in response
        assert "T9999: (Name not found)" in response
        assert "Technique details not available" in response

    def test_format_group_techniques_response_missing_tactic_names(self):
        """Test formatting response when tactic names are missing."""
        # Create data with technique that references non-existent tactic
        modified_data = self.sample_data.copy()
        modified_data["techniques"] = [
            {
                "id": "T1055",
                "name": "Process Injection",
                "description": "Test description",
                "tactics": ["TA9999"],  # Non-existent tactic
                "platforms": ["Windows"],
            }
        ]

        group = {
            "id": "G0016",
            "name": "APT29",
            "aliases": [],
            "description": "Test group",
            "techniques": ["T1055"],
        }

        technique_details = _get_technique_details(group["techniques"], modified_data)
        response = _format_group_techniques_response(
            group, technique_details, modified_data
        )

        # Should handle missing tactic name gracefully
        assert "TA9999 (Name not found)" in response

    def test_integration_get_group_techniques_logic(self):
        """Test the complete get_group_techniques logic integration."""
        # Test successful retrieval and formatting
        group = _find_group_by_id("G0016", self.sample_data)
        assert group is not None

        technique_details = _get_technique_details(
            group["techniques"], self.sample_data
        )
        assert len(technique_details) == 3

        response = _format_group_techniques_response(
            group, technique_details, self.sample_data
        )

        # Verify all expected content is present
        assert "GROUP TECHNIQUES" in response
        assert "G0016" in response
        assert "APT29" in response
        assert "T1055" in response
        assert "Process Injection" in response
        assert "TA0004 (Privilege Escalation)" in response

    def test_integration_get_group_techniques_no_techniques(self):
        """Test the complete logic for group with no techniques."""
        group = _find_group_by_id("G0001", self.sample_data)
        assert group is not None

        technique_details = _get_technique_details(
            group["techniques"], self.sample_data
        )
        assert len(technique_details) == 0

        response = _format_group_techniques_response(
            group, technique_details, self.sample_data
        )
        assert "No techniques found for group 'G0001' (Axiom)" in response

    def test_edge_cases_empty_data(self):
        """Test edge cases with empty data structures."""
        empty_data = {"groups": [], "techniques": [], "tactics": [], "mitigations": []}

        group = _find_group_by_id("G0016", empty_data)
        assert group is None

    def test_edge_cases_malformed_group_data(self):
        """Test edge cases with malformed group data."""
        malformed_data = {
            "groups": [
                {
                    # Missing id field
                    "name": "Test Group",
                    "techniques": ["T1055"],
                }
            ],
            "techniques": [],
            "tactics": [],
            "mitigations": [],
        }

        group = _find_group_by_id("G0016", malformed_data)
        assert group is None  # Should not find group without proper ID


if __name__ == "__main__":
    pytest.main([__file__])
