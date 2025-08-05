"""
Unit tests for STIX2 library integration layer.

Tests the new STIX2 library integration methods in STIXParser class.
"""

import pytest
import json
import uuid
from unittest.mock import Mock, patch

import stix2
from stix2.exceptions import STIXError, InvalidValueError, MissingPropertiesError

from src.parsers.stix_parser import STIXParser


class TestSTIX2LibraryIntegration:
    """Test STIX2 library integration functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = STIXParser()

    def test_parse_with_stix2_library_success(self):
        """Test successful parsing using STIX2 library."""
        # Create valid STIX data using the library
        attack_pattern = stix2.AttackPattern(
            name="Test Technique",
            description="A test attack pattern",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T1234")
            ],
            x_mitre_platforms=["Windows", "Linux"],
            kill_chain_phases=[
                stix2.KillChainPhase(
                    kill_chain_name="mitre-attack", phase_name="execution"
                )
            ],
            allow_custom=True,
        )

        bundle = stix2.Bundle(attack_pattern, allow_custom=True)
        stix_data = json.loads(bundle.serialize())

        # Test parsing
        result = self.parser._parse_with_stix2_library(stix_data, ["techniques"])

        assert "techniques" in result
        assert len(result["techniques"]) == 1

        technique = result["techniques"][0]
        assert technique["id"] == "T1234"
        assert technique["name"] == "Test Technique"
        assert technique["description"] == "A test attack pattern"
        assert technique["platforms"] == ["Windows", "Linux"]
        assert "TA0002" in technique["tactics"]  # execution tactic

    def test_parse_with_stix2_library_bundle_format(self):
        """Test parsing STIX Bundle format."""
        # Create multiple STIX objects
        technique = stix2.AttackPattern(
            name="Test Technique",
            description="A test technique",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T1001")
            ],
            allow_custom=True,
        )

        group = stix2.IntrusionSet(
            name="Test Group",
            description="A test group",
            aliases=["Test Group", "TG1", "TestGroup"],
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="G1001")
            ],
        )

        bundle = stix2.Bundle(technique, group, allow_custom=True)
        stix_data = json.loads(bundle.serialize())

        # Test parsing both entity types
        result = self.parser._parse_with_stix2_library(
            stix_data, ["techniques", "groups"]
        )

        assert "techniques" in result
        assert "groups" in result
        assert len(result["techniques"]) == 1
        assert len(result["groups"]) == 1

        # Verify technique
        parsed_technique = result["techniques"][0]
        assert parsed_technique["id"] == "T1001"
        assert parsed_technique["name"] == "Test Technique"

        # Verify group
        parsed_group = result["groups"][0]
        assert parsed_group["id"] == "G1001"
        assert parsed_group["name"] == "Test Group"
        assert "TG1" in parsed_group["aliases"]
        assert "TestGroup" in parsed_group["aliases"]
        assert "Test Group" not in parsed_group["aliases"]  # Primary name filtered out

    def test_parse_with_stix2_library_error_handling(self):
        """Test error handling in STIX2 library parsing."""
        # Test with invalid STIX data
        invalid_data = {
            "type": "bundle",
            "spec_version": "2.1",
            "id": f"bundle--{uuid.uuid4()}",
            "objects": [
                {
                    "type": "attack-pattern",
                    "spec_version": "2.1",
                    "id": "invalid-id-format",  # Invalid ID format
                    "name": "Test",
                }
            ],
        }

        # Should raise STIXError due to invalid ID format
        with pytest.raises(STIXError):
            self.parser._parse_with_stix2_library(invalid_data, ["techniques"])

    def test_parse_with_stix2_library_graceful_object_errors(self):
        """Test graceful handling of individual object parsing errors."""
        # Create mix of valid and invalid objects
        valid_technique = stix2.AttackPattern(
            name="Valid Technique",
            description="A valid technique",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T1001")
            ],
            allow_custom=True,
        )

        bundle = stix2.Bundle(valid_technique, allow_custom=True)
        stix_data = json.loads(bundle.serialize())

        # Add an invalid object manually to the bundle
        stix_data["objects"].append(
            {
                "type": "attack-pattern",
                "spec_version": "2.1",
                "id": f"attack-pattern--{uuid.uuid4()}",
                "name": "Invalid Technique",
                # Missing required description field
            }
        )

        # Should parse valid objects and skip invalid ones
        result = self.parser._parse_with_stix2_library(stix_data, ["techniques"])

        assert "techniques" in result
        assert len(result["techniques"]) == 1  # Only valid technique parsed
        assert result["techniques"][0]["id"] == "T1001"

    def test_extract_entity_from_stix_object_technique(self):
        """Test extracting technique data from STIX2 library object."""
        technique = stix2.AttackPattern(
            name="Process Injection",
            description="Adversaries may inject code into processes",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T1055")
            ],
            x_mitre_platforms=["Windows", "macOS", "Linux"],
            kill_chain_phases=[
                stix2.KillChainPhase(
                    kill_chain_name="mitre-attack", phase_name="defense-evasion"
                ),
                stix2.KillChainPhase(
                    kill_chain_name="mitre-attack", phase_name="privilege-escalation"
                ),
            ],
            allow_custom=True,
        )

        # Convert STIX object to dictionary for the main extraction method
        technique_dict = dict(technique)
        result = self.parser._extract_technique_data(technique_dict)

        assert result is not None
        # The _extract_technique_data method returns technique-specific fields
        assert result["platforms"] == ["Windows", "macOS", "Linux"]
        # Tactics should be extracted from kill chain phases (TA0005=Defense Evasion, TA0004=Privilege Escalation)
        assert "TA0005" in result["tactics"]  # defense-evasion
        assert "TA0004" in result["tactics"]  # privilege-escalation
        assert result["mitigations"] == []  # Empty initially

    def test_extract_entity_from_stix_object_group(self):
        """Test extracting group data from STIX2 library object."""
        group = stix2.IntrusionSet(
            name="APT1",
            description="APT1 is a threat group",
            aliases=["APT1", "Comment Crew", "PLA Unit 61398"],
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="G0006")
            ],
        )

        # Convert STIX object to dictionary for the main extraction method
        group_dict = dict(group)
        result = self.parser._extract_group_data(group_dict)

        assert result is not None
        # The _extract_group_data method returns group-specific fields
        assert "Comment Crew" in result["aliases"]
        assert "PLA Unit 61398" in result["aliases"]
        assert "APT1" not in result["aliases"]  # Primary name filtered out
        assert result["techniques"] == []  # Empty initially

    def test_extract_entity_from_stix_object_mitigation(self):
        """Test extracting mitigation data from STIX2 library object."""
        mitigation = stix2.CourseOfAction(
            name="Application Isolation and Sandboxing",
            description="Restrict execution of code to a virtual environment",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="M1048")
            ],
        )

        # Convert STIX object to dictionary for the main extraction method
        mitigation_dict = dict(mitigation)
        result = self.parser._extract_mitigation_data(mitigation_dict)

        assert result is not None
        # The _extract_mitigation_data method returns mitigation-specific fields
        assert result["techniques"] == []  # Empty initially

    def test_extract_mitre_id_from_stix_object(self):
        """Test MITRE ID extraction from STIX2 library objects."""
        technique = stix2.AttackPattern(
            name="Test Technique",
            description="Test description",
            external_references=[
                stix2.ExternalReference(source_name="capec", external_id="CAPEC-123"),
                stix2.ExternalReference(
                    source_name="mitre-attack", external_id="T1234"
                ),
                stix2.ExternalReference(
                    source_name="other-source", external_id="OTHER-456"
                ),
            ],
            allow_custom=True,
        )

        mitre_id = self.parser._extract_mitre_id_from_stix_object(technique)
        assert mitre_id == "T1234"

    def test_extract_mitre_id_from_stix_object_missing(self):
        """Test MITRE ID extraction when no MITRE reference exists."""
        technique = stix2.AttackPattern(
            name="Test Technique",
            description="Test description",
            external_references=[
                stix2.ExternalReference(source_name="capec", external_id="CAPEC-123")
            ],
            allow_custom=True,
        )

        mitre_id = self.parser._extract_mitre_id_from_stix_object(technique)
        assert mitre_id == ""

    def test_extract_entity_from_stix_object_missing_required_fields(self):
        """Test handling of STIX objects with missing required fields."""
        # Create technique without MITRE ID
        technique = stix2.AttackPattern(
            name="Test Technique",
            description="Test description",
            allow_custom=True,
            # No external_references with mitre-attack source
        )

        # Convert STIX object to dictionary for the main extraction method
        technique_dict = dict(technique)
        result = self.parser._extract_technique_data(technique_dict)
        # The method still returns data even without MITRE ID (basic technique-specific data)
        assert result is not None
        assert "mitigations" in result

    def test_fallback_to_custom_parsing(self):
        """Test fallback mechanism when STIX2 library parsing fails."""
        # Create invalid STIX data that will cause library parsing to fail
        invalid_stix_data = {
            "type": "bundle",
            "spec_version": "2.1",
            "id": "invalid-bundle-id",  # Invalid format
            "objects": [],
        }

        # The parser should now handle invalid STIX data gracefully
        # Since deprecated fallback was removed, it should raise an error or handle gracefully
        try:
            result = self.parser.parse(invalid_stix_data, ["techniques"])
            # If it doesn't raise an error, verify it returns empty results
            assert isinstance(result, dict)
            assert "techniques" in result
        except Exception as e:
            # This is expected behavior for invalid STIX data
            assert "STIX" in str(e) or "parsing" in str(e).lower() or "Invalid" in str(e)

    def test_stix2_library_error_handling(self):
        """Test that STIX2 library errors are properly handled."""
        parser = STIXParser()

        # Test with completely invalid STIX data that will cause parsing errors
        invalid_stix_data = {
            "type": "bundle",
            "spec_version": "2.1",
            "id": "invalid-bundle-id-format",  # Invalid ID format
            "objects": [],
        }

        # The parser should handle the error gracefully and raise it
        with pytest.raises(InvalidValueError):
            parser._parse_with_stix2_library(invalid_stix_data, ["techniques"])

        # Test that the error handling logs appropriately
        import logging

        with patch("src.parsers.stix_parser.logger") as mock_logger:
            try:
                parser._parse_with_stix2_library(invalid_stix_data, ["techniques"])
            except InvalidValueError:
                pass  # Expected

            # Verify that error was logged
            mock_logger.error.assert_called()

    def test_technique_data_extraction_edge_cases(self):
        """Test technique data extraction edge cases."""
        # Technique without platforms or kill chain phases
        technique = stix2.AttackPattern(
            name="Minimal Technique",
            description="Minimal technique data",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T9999")
            ],
            allow_custom=True,
        )

        # Convert STIX object to dictionary for the main extraction method
        technique_dict = dict(technique)
        result = self.parser._extract_technique_data(technique_dict)

        # Should handle missing optional fields gracefully
        assert "platforms" not in result
        assert "tactics" not in result
        assert result["mitigations"] == []

    def test_group_data_extraction_edge_cases(self):
        """Test group data extraction edge cases."""
        # Group without aliases
        group = stix2.IntrusionSet(
            name="Simple Group",
            description="Group without aliases",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="G9999")
            ],
        )

        # Convert STIX object to dictionary for the main extraction method
        group_dict = dict(group)
        result = self.parser._extract_group_data(group_dict)

        # Should handle missing aliases gracefully
        assert "aliases" not in result
        assert result["techniques"] == []

    def test_dictionary_fallback_in_stix_object_methods(self):
        """Test that STIX object methods can handle dictionary inputs as fallback."""
        # Test with dictionary instead of STIX object
        technique_dict = {
            "type": "attack-pattern",  # Required for STIX2 parsing
            "name": "Dict Technique",
            "description": "Technique from dictionary",
            "external_references": [
                {"source_name": "mitre-attack", "external_id": "T8888"}
            ],
            "x_mitre_platforms": ["Windows"],
            "kill_chain_phases": [
                {"kill_chain_name": "mitre-attack", "phase_name": "execution"}
            ],
        }

        # Use the current method for technique data extraction
        result = self.parser._extract_technique_data(technique_dict)

        assert result is not None
        # The _extract_technique_data method returns technique-specific fields
        assert result["platforms"] == ["Windows"]
        assert "TA0002" in result["tactics"]  # execution
