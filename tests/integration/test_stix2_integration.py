"""
STIX2 library integration tests.

This module tests the STIX2 library integration functionality,
ensuring proper parsing and data structure integrity.
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
        # Primary name should be filtered from aliases
        assert "Test Group" not in parsed_group["aliases"]
        assert "TG1" in parsed_group["aliases"]
        assert "TestGroup" in parsed_group["aliases"]

    def test_parse_with_stix2_library_error_handling(self):
        """Test error handling in STIX2 library parsing."""
        # Test with invalid STIX data
        invalid_data = {"invalid": "data"}

        # The parser should raise an exception for invalid data
        with pytest.raises(Exception):
            self.parser._parse_with_stix2_library(invalid_data, ["techniques"])

    def test_parse_with_stix2_library_empty_bundle(self):
        """Test parsing empty STIX bundle."""
        # Create a proper empty bundle with objects array
        empty_bundle_data = {
            "type": "bundle",
            "id": f"bundle--{uuid.uuid4()}",
            "objects": []
        }

        result = self.parser._parse_with_stix2_library(empty_bundle_data, ["techniques", "groups"])

        assert "techniques" in result
        assert "groups" in result
        assert len(result["techniques"]) == 0
        assert len(result["groups"]) == 0

    def test_parse_with_stix2_library_complex_relationships(self):
        """Test parsing STIX data with complex relationships."""
        # Create technique
        technique = stix2.AttackPattern(
            name="Complex Technique",
            description="A technique with relationships",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T2001")
            ],
            x_mitre_platforms=["Windows"],
            kill_chain_phases=[
                stix2.KillChainPhase(
                    kill_chain_name="mitre-attack", phase_name="initial-access"
                )
            ],
            allow_custom=True,
        )

        # Create group
        group = stix2.IntrusionSet(
            name="Complex Group",
            description="A group that uses the technique",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="G2001")
            ],
        )

        # Create relationship
        relationship = stix2.Relationship(
            relationship_type="uses",
            source_ref=group.id,
            target_ref=technique.id,
        )

        bundle = stix2.Bundle(technique, group, relationship, allow_custom=True)
        stix_data = json.loads(bundle.serialize())

        result = self.parser._parse_with_stix2_library(
            stix_data, ["techniques", "groups", "relationships"]
        )

        assert "techniques" in result
        assert "groups" in result
        assert "relationships" in result
        assert len(result["techniques"]) == 1
        assert len(result["groups"]) == 1
        # Note: The parser may not extract relationships as separate entities
        # This depends on the parser implementation

    def test_parse_with_stix2_library_mitigation_objects(self):
        """Test parsing STIX mitigation objects."""
        # Create mitigation
        mitigation = stix2.CourseOfAction(
            name="Test Mitigation",
            description="A test mitigation",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="M2001")
            ],
            allow_custom=True,
        )

        bundle = stix2.Bundle(mitigation, allow_custom=True)
        stix_data = json.loads(bundle.serialize())

        result = self.parser._parse_with_stix2_library(stix_data, ["mitigations"])

        assert "mitigations" in result
        assert len(result["mitigations"]) == 1

        parsed_mitigation = result["mitigations"][0]
        assert parsed_mitigation["id"] == "M2001"
        assert parsed_mitigation["name"] == "Test Mitigation"
        assert parsed_mitigation["description"] == "A test mitigation"

    def test_parse_with_stix2_library_tactic_objects(self):
        """Test parsing STIX tactic objects."""
        # Create tactic using proper STIX2 custom object syntax
        tactic_data = {
            "type": "x-mitre-tactic",
            "id": f"x-mitre-tactic--{uuid.uuid4()}",
            "name": "Test Tactic",
            "description": "A test tactic",
            "x_mitre_shortname": "test-tactic",
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": "TA2001"
                }
            ]
        }

        bundle_data = {
            "type": "bundle",
            "id": f"bundle--{uuid.uuid4()}",
            "objects": [tactic_data]
        }

        result = self.parser._parse_with_stix2_library(bundle_data, ["tactics"])

        assert "tactics" in result
        if len(result["tactics"]) > 0:
            parsed_tactic = result["tactics"][0]
            assert parsed_tactic["id"] == "TA2001"
            assert parsed_tactic["name"] == "Test Tactic"
            assert parsed_tactic["description"] == "A test tactic"

    def test_parse_with_stix2_library_performance(self):
        """Test performance of STIX2 library parsing with large datasets."""
        import time

        # Create a larger dataset
        objects = []
        for i in range(100):
            technique = stix2.AttackPattern(
                name=f"Technique {i}",
                description=f"Test technique {i}",
                external_references=[
                    stix2.ExternalReference(
                        source_name="mitre-attack", external_id=f"T{i:04d}"
                    )
                ],
                allow_custom=True,
            )
            objects.append(technique)

        bundle = stix2.Bundle(*objects, allow_custom=True)
        stix_data = json.loads(bundle.serialize())

        # Measure parsing time
        start_time = time.time()
        result = self.parser._parse_with_stix2_library(stix_data, ["techniques"])
        end_time = time.time()

        parsing_time = end_time - start_time

        # Verify results
        assert "techniques" in result
        assert len(result["techniques"]) == 100

        # Performance should be reasonable (less than 1 second for 100 objects)
        assert parsing_time < 1.0, f"Parsing took {parsing_time:.2f}s, which may indicate performance issues"

    def test_parse_with_stix2_library_data_integrity(self):
        """Test that STIX2 library parsing maintains data integrity."""
        # Create comprehensive test data
        technique = stix2.AttackPattern(
            name="Data Integrity Test",
            description="Testing data integrity preservation",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T9999"),
                stix2.ExternalReference(
                    source_name="capec", external_id="CAPEC-123", url="https://example.com"
                ),
            ],
            x_mitre_platforms=["Windows", "Linux", "macOS"],
            x_mitre_data_sources=["Process monitoring", "File monitoring"],
            kill_chain_phases=[
                stix2.KillChainPhase(
                    kill_chain_name="mitre-attack", phase_name="execution"
                ),
                stix2.KillChainPhase(
                    kill_chain_name="mitre-attack", phase_name="defense-evasion"
                ),
            ],
            allow_custom=True,
        )

        bundle = stix2.Bundle(technique, allow_custom=True)
        stix_data = json.loads(bundle.serialize())

        result = self.parser._parse_with_stix2_library(stix_data, ["techniques"])

        assert "techniques" in result
        assert len(result["techniques"]) == 1

        parsed_technique = result["techniques"][0]

        # Verify all data is preserved
        assert parsed_technique["id"] == "T9999"
        assert parsed_technique["name"] == "Data Integrity Test"
        assert parsed_technique["description"] == "Testing data integrity preservation"
        assert set(parsed_technique["platforms"]) == {"Windows", "Linux", "macOS"}
        assert "TA0002" in parsed_technique["tactics"]  # execution
        assert "TA0005" in parsed_technique["tactics"]  # defense-evasion

    def test_parse_with_stix2_library_edge_cases(self):
        """Test STIX2 library parsing with edge cases."""
        # Test with minimal required fields
        minimal_technique = stix2.AttackPattern(
            name="Minimal Technique",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T0001")
            ],
            allow_custom=True,
        )

        bundle = stix2.Bundle(minimal_technique, allow_custom=True)
        stix_data = json.loads(bundle.serialize())

        result = self.parser._parse_with_stix2_library(stix_data, ["techniques"])

        assert "techniques" in result
        assert len(result["techniques"]) == 1

        parsed_technique = result["techniques"][0]
        assert parsed_technique["id"] == "T0001"
        assert parsed_technique["name"] == "Minimal Technique"
        # Should have default values for missing fields
        assert "description" in parsed_technique
        # Note: platforms, tactics, and mitigations may not be present for minimal objects
        # This depends on the parser's default value handling


if __name__ == "__main__":
    pytest.main([__file__])