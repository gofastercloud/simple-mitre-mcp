"""
Unit tests for technique extraction refactoring.

Tests comparing old vs new technique extraction output to ensure
backward compatibility when refactoring to use STIX2 library objects.
"""

import pytest
import json
import uuid
from unittest.mock import Mock, patch

import stix2
from stix2.exceptions import STIXError, InvalidValueError

from src.parsers.stix_parser import STIXParser


class TestTechniqueExtractionRefactor:
    """Test technique extraction refactoring for STIX2 library usage."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = STIXParser()

    def test_technique_extraction_output_compatibility(self):
        """Test that new STIX2 library extraction produces identical output to legacy method."""
        # Create test data as both STIX2 object and raw dictionary
        technique_dict = {
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": f"attack-pattern--{uuid.uuid4()}",
            "name": "Process Injection",
            "description": "Adversaries may inject code into processes in order to evade process-based defenses.",
            "external_references": [
                {"source_name": "mitre-attack", "external_id": "T1055"}
            ],
            "x_mitre_platforms": ["Windows", "macOS", "Linux"],
            "kill_chain_phases": [
                {"kill_chain_name": "mitre-attack", "phase_name": "defense-evasion"},
                {
                    "kill_chain_name": "mitre-attack",
                    "phase_name": "privilege-escalation",
                },
            ],
        }

        # Create STIX2 library object from the same data
        technique_stix = stix2.AttackPattern(
            name="Process Injection",
            description="Adversaries may inject code into processes in order to evade process-based defenses.",
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

        # Extract using both methods
        legacy_result = self.parser._extract_technique_data(technique_dict)
        stix2_result = self.parser._extract_technique_data_from_stix_object(
            technique_stix
        )

        # Compare results - they should be identical
        assert legacy_result == stix2_result

        # Verify specific fields
        assert legacy_result["platforms"] == ["Windows", "macOS", "Linux"]
        assert stix2_result["platforms"] == ["Windows", "macOS", "Linux"]

        assert "TA0005" in legacy_result["tactics"]  # defense-evasion
        assert "TA0004" in legacy_result["tactics"]  # privilege-escalation
        assert legacy_result["tactics"] == stix2_result["tactics"]

        assert legacy_result["mitigations"] == []
        assert stix2_result["mitigations"] == []

    def test_technique_extraction_minimal_data(self):
        """Test technique extraction with minimal required data."""
        # Minimal technique data
        technique_dict = {
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": f"attack-pattern--{uuid.uuid4()}",
            "name": "Minimal Technique",
            "description": "A minimal technique with no optional fields.",
            "external_references": [
                {"source_name": "mitre-attack", "external_id": "T9999"}
            ],
        }

        # Create STIX2 library object
        technique_stix = stix2.AttackPattern(
            name="Minimal Technique",
            description="A minimal technique with no optional fields.",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T9999")
            ],
            allow_custom=True,
        )

        # Extract using both methods
        legacy_result = self.parser._extract_technique_data(technique_dict)
        stix2_result = self.parser._extract_technique_data_from_stix_object(
            technique_stix
        )

        # Compare results
        assert legacy_result == stix2_result

        # Verify that optional fields are handled consistently
        assert "platforms" not in legacy_result or legacy_result.get("platforms") == []
        assert "platforms" not in stix2_result or stix2_result.get("platforms") == []

        assert "tactics" not in legacy_result or legacy_result.get("tactics") == []
        assert "tactics" not in stix2_result or stix2_result.get("tactics") == []

        assert legacy_result["mitigations"] == []
        assert stix2_result["mitigations"] == []

    def test_technique_extraction_single_platform(self):
        """Test technique extraction with single platform."""
        technique_dict = {
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": f"attack-pattern--{uuid.uuid4()}",
            "name": "Windows Technique",
            "description": "A Windows-specific technique.",
            "external_references": [
                {"source_name": "mitre-attack", "external_id": "T1001"}
            ],
            "x_mitre_platforms": ["Windows"],
        }

        technique_stix = stix2.AttackPattern(
            name="Windows Technique",
            description="A Windows-specific technique.",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T1001")
            ],
            x_mitre_platforms=["Windows"],
            allow_custom=True,
        )

        legacy_result = self.parser._extract_technique_data(technique_dict)
        stix2_result = self.parser._extract_technique_data_from_stix_object(
            technique_stix
        )

        assert legacy_result == stix2_result
        assert legacy_result["platforms"] == ["Windows"]
        assert stix2_result["platforms"] == ["Windows"]

    def test_technique_extraction_single_tactic(self):
        """Test technique extraction with single tactic."""
        technique_dict = {
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": f"attack-pattern--{uuid.uuid4()}",
            "name": "Execution Technique",
            "description": "An execution-only technique.",
            "external_references": [
                {"source_name": "mitre-attack", "external_id": "T1002"}
            ],
            "kill_chain_phases": [
                {"kill_chain_name": "mitre-attack", "phase_name": "execution"}
            ],
        }

        technique_stix = stix2.AttackPattern(
            name="Execution Technique",
            description="An execution-only technique.",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T1002")
            ],
            kill_chain_phases=[
                stix2.KillChainPhase(
                    kill_chain_name="mitre-attack", phase_name="execution"
                )
            ],
            allow_custom=True,
        )

        legacy_result = self.parser._extract_technique_data(technique_dict)
        stix2_result = self.parser._extract_technique_data_from_stix_object(
            technique_stix
        )

        assert legacy_result == stix2_result
        assert legacy_result["tactics"] == ["TA0002"]  # execution
        assert stix2_result["tactics"] == ["TA0002"]

    def test_technique_extraction_unknown_tactic_phase(self):
        """Test technique extraction with unknown kill chain phase."""
        technique_dict = {
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": f"attack-pattern--{uuid.uuid4()}",
            "name": "Unknown Phase Technique",
            "description": "A technique with unknown phase.",
            "external_references": [
                {"source_name": "mitre-attack", "external_id": "T1003"}
            ],
            "kill_chain_phases": [
                {"kill_chain_name": "mitre-attack", "phase_name": "unknown-phase"}
            ],
        }

        technique_stix = stix2.AttackPattern(
            name="Unknown Phase Technique",
            description="A technique with unknown phase.",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T1003")
            ],
            kill_chain_phases=[
                stix2.KillChainPhase(
                    kill_chain_name="mitre-attack", phase_name="unknown-phase"
                )
            ],
            allow_custom=True,
        )

        legacy_result = self.parser._extract_technique_data(technique_dict)
        stix2_result = self.parser._extract_technique_data_from_stix_object(
            technique_stix
        )

        assert legacy_result == stix2_result
        # Unknown phases should not be included in tactics
        assert "tactics" not in legacy_result or legacy_result.get("tactics") == []
        assert "tactics" not in stix2_result or stix2_result.get("tactics") == []

    def test_technique_extraction_non_mitre_kill_chain(self):
        """Test technique extraction with non-MITRE kill chain."""
        technique_dict = {
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": f"attack-pattern--{uuid.uuid4()}",
            "name": "Non-MITRE Technique",
            "description": "A technique with non-MITRE kill chain.",
            "external_references": [
                {"source_name": "mitre-attack", "external_id": "T1004"}
            ],
            "kill_chain_phases": [
                {"kill_chain_name": "other-framework", "phase_name": "some-phase"}
            ],
        }

        technique_stix = stix2.AttackPattern(
            name="Non-MITRE Technique",
            description="A technique with non-MITRE kill chain.",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T1004")
            ],
            kill_chain_phases=[
                stix2.KillChainPhase(
                    kill_chain_name="other-framework", phase_name="some-phase"
                )
            ],
            allow_custom=True,
        )

        legacy_result = self.parser._extract_technique_data(technique_dict)
        stix2_result = self.parser._extract_technique_data_from_stix_object(
            technique_stix
        )

        assert legacy_result == stix2_result
        # Non-MITRE kill chains should not be included in tactics
        assert "tactics" not in legacy_result or legacy_result.get("tactics") == []
        assert "tactics" not in stix2_result or stix2_result.get("tactics") == []

    def test_refactored_technique_extraction_uses_stix2_objects(self):
        """Test that refactored technique extraction method uses STIX2 library objects."""
        # Create a technique dictionary
        technique_dict = {
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": f"attack-pattern--{uuid.uuid4()}",
            "name": "Test Technique",
            "description": "A test technique.",
            "external_references": [
                {"source_name": "mitre-attack", "external_id": "T1005"}
            ],
            "x_mitre_platforms": ["Windows", "Linux"],
            "kill_chain_phases": [
                {"kill_chain_name": "mitre-attack", "phase_name": "collection"}
            ],
        }

        # Mock stix2.parse to verify it's being called
        with patch("src.parsers.stix_parser.stix2.parse") as mock_parse:
            # Create a mock STIX2 AttackPattern object
            mock_attack_pattern = Mock()
            mock_attack_pattern.x_mitre_platforms = ["Windows", "Linux"]
            mock_attack_pattern.kill_chain_phases = [
                Mock(kill_chain_name="mitre-attack", phase_name="collection")
            ]
            mock_parse.return_value = mock_attack_pattern

            # Mock the STIX2 extraction method to return expected data
            with patch.object(
                self.parser, "_extract_technique_data_from_stix_object"
            ) as mock_stix2_extract:
                mock_stix2_extract.return_value = {
                    "platforms": ["Windows", "Linux"],
                    "tactics": ["TA0009"],
                    "mitigations": [],
                }

                # Call the refactored method
                result = self.parser._extract_technique_data(technique_dict)

                # Verify that stix2.parse was called with the technique dictionary
                mock_parse.assert_called_once_with(technique_dict, allow_custom=True)

                # Verify that the STIX2 extraction method was called with the parsed object
                mock_stix2_extract.assert_called_once_with(mock_attack_pattern)

                # Verify the result
                assert result["platforms"] == ["Windows", "Linux"]
                assert result["tactics"] == ["TA0009"]  # collection
                assert result["mitigations"] == []

    def test_refactored_technique_extraction_fallback_on_stix2_error(self):
        """Test that refactored method falls back to legacy parsing on STIX2 errors."""
        technique_dict = {
            "type": "attack-pattern",
            "spec_version": "2.1",
            "id": f"attack-pattern--{uuid.uuid4()}",
            "name": "Test Technique",
            "description": "A test technique.",
            "external_references": [
                {"source_name": "mitre-attack", "external_id": "T1006"}
            ],
            "x_mitre_platforms": ["Windows"],
            "kill_chain_phases": [
                {"kill_chain_name": "mitre-attack", "phase_name": "execution"}
            ],
        }

        # Mock stix2.parse to raise an error
        with patch("src.parsers.stix_parser.stix2.parse") as mock_parse:
            mock_parse.side_effect = STIXError("Invalid STIX data")

            # Mock the legacy extraction method
            with patch.object(
                self.parser, "_extract_technique_data_legacy"
            ) as mock_legacy:
                mock_legacy.return_value = {
                    "platforms": ["Windows"],
                    "tactics": ["TA0002"],
                    "mitigations": [],
                }

                # Call the refactored method
                result = self.parser._extract_technique_data(technique_dict)

                # Verify that stix2.parse was called and failed
                mock_parse.assert_called_once_with(technique_dict, allow_custom=True)

                # Verify that the legacy method was called as fallback
                mock_legacy.assert_called_once_with(technique_dict)

                # Verify the result from fallback
                assert result["platforms"] == ["Windows"]
                assert result["tactics"] == ["TA0002"]
                assert result["mitigations"] == []

    def test_all_tactic_phase_mappings(self):
        """Test that all MITRE ATT&CK tactic phase mappings work correctly."""
        phase_mappings = {
            "initial-access": "TA0001",
            "execution": "TA0002",
            "persistence": "TA0003",
            "privilege-escalation": "TA0004",
            "defense-evasion": "TA0005",
            "credential-access": "TA0006",
            "discovery": "TA0007",
            "lateral-movement": "TA0008",
            "collection": "TA0009",
            "command-and-control": "TA0011",
            "exfiltration": "TA0010",
            "impact": "TA0040",
        }

        for phase_name, expected_tactic_id in phase_mappings.items():
            technique_dict = {
                "type": "attack-pattern",
                "spec_version": "2.1",
                "id": f"attack-pattern--{uuid.uuid4()}",
                "name": f"Test {phase_name.title()} Technique",
                "description": f"A technique for {phase_name}.",
                "external_references": [
                    {
                        "source_name": "mitre-attack",
                        "external_id": f"T{1000 + list(phase_mappings.keys()).index(phase_name)}",
                    }
                ],
                "kill_chain_phases": [
                    {"kill_chain_name": "mitre-attack", "phase_name": phase_name}
                ],
            }

            technique_stix = stix2.AttackPattern(
                name=f"Test {phase_name.title()} Technique",
                description=f"A technique for {phase_name}.",
                external_references=[
                    stix2.ExternalReference(
                        source_name="mitre-attack",
                        external_id=f"T{1000 + list(phase_mappings.keys()).index(phase_name)}",
                    )
                ],
                kill_chain_phases=[
                    stix2.KillChainPhase(
                        kill_chain_name="mitre-attack", phase_name=phase_name
                    )
                ],
                allow_custom=True,
            )

            legacy_result = self.parser._extract_technique_data(technique_dict)
            stix2_result = self.parser._extract_technique_data_from_stix_object(
                technique_stix
            )

            # Both methods should produce identical results
            assert legacy_result == stix2_result
            assert expected_tactic_id in legacy_result["tactics"]
            assert expected_tactic_id in stix2_result["tactics"]
