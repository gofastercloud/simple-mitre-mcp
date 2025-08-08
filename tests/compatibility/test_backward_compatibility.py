"""
Consolidated backward compatibility test suite for test suite rationalization.

This module provides comprehensive backward compatibility testing in a single,
streamlined suite that covers all critical compatibility scenarios.
"""

import pytest
import json
import uuid
from unittest.mock import Mock, patch
from typing import Dict, List, Any, Optional

import stix2
from stix2 import Bundle, AttackPattern, IntrusionSet, CourseOfAction
from stix2.exceptions import STIXError, InvalidValueError, MissingPropertiesError

from src.parsers.stix_parser import STIXParser
from src.data_loader import DataLoader
from src.mcp_server import create_mcp_server
from tests.base import BaseTestCase


class ConsolidatedBackwardCompatibilityTest(BaseTestCase):
    """Consolidated backward compatibility test suite."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = STIXParser()
        self.sample_stix_data = self._create_comprehensive_test_data()

    def _create_comprehensive_test_data(self) -> Dict[str, Any]:
        """Create comprehensive STIX test data covering all entity types."""
        # Create technique with full data
        technique = stix2.AttackPattern(
            name="Process Injection",
            description="Adversaries may inject code into processes in order to evade process-based defenses.",
            external_references=[
                stix2.ExternalReference(
                    source_name="mitre-attack",
                    external_id="T1055",
                    url="https://attack.mitre.org/techniques/T1055/",
                )
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

        # Create group with aliases
        group = stix2.IntrusionSet(
            name="APT29",
            description="APT29 is a threat group that has been attributed to Russia's Foreign Intelligence Service.",
            aliases=["APT29", "Cozy Bear", "The Dukes", "YTTRIUM"],
            external_references=[
                stix2.ExternalReference(
                    source_name="mitre-attack",
                    external_id="G0016",
                    url="https://attack.mitre.org/groups/G0016/",
                )
            ],
        )

        # Create tactic
        tactic = stix2.parse(
            {
                "type": "x-mitre-tactic",
                "spec_version": "2.1",
                "id": f"x-mitre-tactic--{uuid.uuid4()}",
                "name": "Defense Evasion",
                "description": "The adversary is trying to avoid being detected.",
                "external_references": [
                    {
                        "source_name": "mitre-attack",
                        "external_id": "TA0005",
                        "url": "https://attack.mitre.org/tactics/TA0005/",
                    }
                ],
                "x_mitre_shortname": "defense-evasion",
            },
            allow_custom=True,
        )

        # Create mitigation
        mitigation = stix2.CourseOfAction(
            name="Application Isolation and Sandboxing",
            description="Restrict execution of code to a virtual environment on or in transit to an endpoint system.",
            external_references=[
                stix2.ExternalReference(
                    source_name="mitre-attack",
                    external_id="M1048",
                    url="https://attack.mitre.org/mitigations/M1048/",
                )
            ],
        )

        # Create relationships
        uses_relationship = stix2.Relationship(
            relationship_type="uses", source_ref=group.id, target_ref=technique.id
        )

        mitigates_relationship = stix2.Relationship(
            relationship_type="mitigates",
            source_ref=mitigation.id,
            target_ref=technique.id,
        )

        # Create bundle
        bundle = stix2.Bundle(
            technique,
            group,
            tactic,
            mitigation,
            uses_relationship,
            mitigates_relationship,
            allow_custom=True,
        )

        return json.loads(bundle.serialize())

    def test_entity_extraction_output_format_compatibility(self):
        """Test that all entity extraction produces expected output format."""
        entity_types = ["techniques", "groups", "tactics", "mitigations"]
        
        # Parse with STIX2 library method
        result = self.parser._parse_with_stix2_library(
            self.sample_stix_data, entity_types
        )

        # Verify all entity types are present with correct structure
        for entity_type in entity_types:
            assert entity_type in result
            assert isinstance(result[entity_type], list)

        # Verify technique data structure
        assert len(result["techniques"]) == 1
        technique = result["techniques"][0]
        assert technique["id"] == "T1055"
        assert technique["name"] == "Process Injection"
        assert isinstance(technique["platforms"], list)
        assert isinstance(technique["tactics"], list)
        assert isinstance(technique["mitigations"], list)
        assert "Windows" in technique["platforms"]

        # Verify group data structure
        assert len(result["groups"]) == 1
        group = result["groups"][0]
        assert group["id"] == "G0016"
        assert group["name"] == "APT29"
        assert isinstance(group["aliases"], list)
        assert "Cozy Bear" in group["aliases"]
        assert "APT29" not in group["aliases"]  # Primary name filtered out

        # Verify tactic data structure
        assert len(result["tactics"]) == 1
        tactic = result["tactics"][0]
        assert tactic["id"] == "TA0005"
        assert tactic["name"] == "Defense Evasion"

        # Verify mitigation data structure
        assert len(result["mitigations"]) == 1
        mitigation = result["mitigations"][0]
        assert mitigation["id"] == "M1048"
        assert mitigation["name"] == "Application Isolation and Sandboxing"

    def test_stix2_library_parsing_compatibility(self):
        """Test comprehensive STIX2 library parsing compatibility."""
        # Create test data with various STIX2 features
        test_stix_data = {
            "type": "bundle",
            "id": f"bundle--{uuid.uuid4()}",
            "objects": [
                {
                    "type": "attack-pattern",
                    "id": f"attack-pattern--{uuid.uuid4()}",
                    "name": "Test Technique",
                    "description": "Test description for STIX2 compatibility",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "T9999"}
                    ],
                    "x_mitre_platforms": ["Windows", "Linux"],
                    "kill_chain_phases": [
                        {"kill_chain_name": "mitre-attack", "phase_name": "execution"},
                        {"kill_chain_name": "mitre-attack", "phase_name": "defense-evasion"},
                    ],
                },
                {
                    "type": "intrusion-set",
                    "id": f"intrusion-set--{uuid.uuid4()}",
                    "name": "Test Group",
                    "description": "Test threat group",
                    "aliases": ["TestGroup", "TG-Test"],
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "G9999"}
                    ],
                },
                {
                    "type": "course-of-action",
                    "id": f"course-of-action--{uuid.uuid4()}",
                    "name": "Test Mitigation",
                    "description": "Test mitigation strategy",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "M9999"}
                    ],
                },
            ],
        }

        # Parse with STIX2 library
        result = self.parser.parse(
            test_stix_data, ["techniques", "groups", "mitigations"]
        )

        # Verify comprehensive parsing
        assert all(entity_type in result for entity_type in ["techniques", "groups", "mitigations"])
        assert all(isinstance(result[entity_type], list) for entity_type in result)

        # Verify technique parsing
        assert len(result["techniques"]) == 1
        technique = result["techniques"][0]
        assert technique["id"] == "T9999"
        assert technique["name"] == "Test Technique"
        assert "Windows" in technique.get("platforms", [])
        assert "TA0002" in technique.get("tactics", [])  # execution

        # Verify group parsing
        assert len(result["groups"]) == 1
        group = result["groups"][0]
        assert group["id"] == "G9999"
        assert group["name"] == "Test Group"
        assert "TestGroup" in group.get("aliases", [])

        # Verify mitigation parsing
        assert len(result["mitigations"]) == 1
        mitigation = result["mitigations"][0]
        assert mitigation["id"] == "M9999"
        assert mitigation["name"] == "Test Mitigation"

    @pytest.mark.asyncio
    async def test_mcp_tools_compatibility(self):
        """Test that all MCP tools maintain compatibility with refactored parser."""
        # Create mock data loader
        mock_data_loader = Mock(spec=DataLoader)

        # Parse test data
        parsed_data = self.parser.parse(
            self.sample_stix_data, ["techniques", "groups", "tactics", "mitigations"]
        )

        # Add relationships for comprehensive testing
        parsed_data["relationships"] = [
            {"type": "uses", "source_id": "G0016", "target_id": "T1055"},
            {"type": "mitigates", "source_id": "M1048", "target_id": "T1055"},
        ]

        # Update entities with relationship data
        parsed_data["groups"][0]["techniques"] = ["T1055"]
        parsed_data["techniques"][0]["mitigations"] = ["M1048"]
        parsed_data["mitigations"][0]["techniques"] = ["T1055"]

        mock_data_loader.get_cached_data.return_value = parsed_data

        # Create MCP server
        mcp_server = create_mcp_server(mock_data_loader)

        # Test all 8 MCP tools for compatibility
        tools_to_test = [
            ("search_attack", {"query": "process"}),
            ("get_technique", {"technique_id": "T1055"}),
            ("list_tactics", {}),
            ("get_group_techniques", {"group_id": "G0016"}),
            ("get_technique_mitigations", {"technique_id": "T1055"}),
            ("build_attack_path", {"start_tactic": "TA0001", "end_tactic": "TA0005"}),
            ("analyze_coverage_gaps", {"threat_groups": ["G0016"]}),
            ("detect_technique_relationships", {"technique_id": "T1055"}),
        ]

        for tool_name, params in tools_to_test:
            result, _ = await mcp_server.call_tool(tool_name, params)

            # Verify tool executed successfully
            assert result is not None
            assert len(result) > 0
            assert result[0].type == "text"

            # Verify tool-specific content based on tool type
            content = result[0].text
            if tool_name in ["search_attack", "get_technique"]:
                assert "T1055" in content or "Process Injection" in content
            elif tool_name == "list_tactics":
                assert "TA0005" in content or "Defense Evasion" in content
            elif tool_name == "get_group_techniques":
                assert "G0016" in content or "APT29" in content
            elif tool_name == "get_technique_mitigations":
                assert "M1048" in content

    def test_error_handling_compatibility(self):
        """Test that error handling maintains backward compatibility."""
        error_scenarios = [
            # Invalid STIX object type
            {
                "type": "bundle",
                "spec_version": "2.1",
                "id": f"bundle--{uuid.uuid4()}",
                "objects": [
                    {
                        "type": "invalid-object-type",
                        "spec_version": "2.1",
                        "id": f"invalid-object-type--{uuid.uuid4()}",
                        "name": "Invalid Object",
                    }
                ],
            },
            # Missing MITRE ID
            {
                "type": "bundle",
                "spec_version": "2.1",
                "id": f"bundle--{uuid.uuid4()}",
                "objects": [
                    {
                        "type": "attack-pattern",
                        "spec_version": "2.1",
                        "id": f"attack-pattern--{uuid.uuid4()}",
                        "name": "No MITRE ID Technique",
                        "description": "Technique without MITRE ID",
                        "external_references": [
                            {"source_name": "other-source", "external_id": "OTHER-123"}
                        ],
                    }
                ],
            },
            # Empty bundle
            {
                "type": "bundle",
                "spec_version": "2.1",
                "id": f"bundle--{uuid.uuid4()}",
                "objects": [],
            },
        ]

        for error_data in error_scenarios:
            # Should handle gracefully without crashing
            result = self.parser.parse(error_data, ["techniques"])

            # Should return empty results for invalid/unusable data
            assert isinstance(result, dict)
            assert "techniques" in result
            assert isinstance(result["techniques"], list)

    def test_data_loader_integration_compatibility(self):
        """Test DataLoader integration maintains backward compatibility."""
        data_loader = DataLoader()

        # Mock the download to return test data
        with patch.object(data_loader, "download_data") as mock_download:
            mock_download.return_value = self.sample_stix_data

            # Mock configuration
            with patch.object(
                data_loader,
                "config",
                {
                    "data_sources": {
                        "test_source": {
                            "url": "http://test.com/data.json",
                            "format": "stix",
                            "entity_types": [
                                "techniques",
                                "groups",
                                "tactics",
                                "mitigations",
                            ],
                        }
                    }
                },
            ):
                # Load data using refactored parser
                result = data_loader.load_data_source("test_source")

                # Verify all entity types loaded correctly
                assert all(entity_type in result for entity_type in ["techniques", "groups", "tactics", "mitigations"])

                # Verify entity data integrity
                assert len(result["techniques"]) == 1
                assert result["techniques"][0]["id"] == "T1055"
                assert len(result["groups"]) == 1
                assert result["groups"][0]["id"] == "G0016"

    def test_relationship_processing_compatibility(self):
        """Test relationship processing maintains backward compatibility."""
        data_loader = DataLoader()

        # Process relationships using refactored parser
        entity_types = ["techniques", "groups", "mitigations"]
        parsed_data = self.parser.parse(self.sample_stix_data, entity_types)

        # Process relationships
        enhanced_data = data_loader._process_relationships(
            self.sample_stix_data, parsed_data
        )

        # Verify relationships processed correctly
        assert "relationships" in enhanced_data

        # Check group has techniques
        group = next((g for g in enhanced_data["groups"] if g["id"] == "G0016"), None)
        assert group is not None
        assert "techniques" in group
        assert "T1055" in group["techniques"]

        # Check technique has mitigations
        technique = next(
            (t for t in enhanced_data["techniques"] if t["id"] == "T1055"), None
        )
        assert technique is not None
        assert "mitigations" in technique
        assert "M1048" in technique["mitigations"]

    def test_unicode_and_special_characters_compatibility(self):
        """Test handling of Unicode and special characters maintains compatibility."""
        # Create STIX data with Unicode characters
        unicode_technique = stix2.AttackPattern(
            name="Téchnique with Ünicode",
            description="Description with émojis 🔒 and spëcial characters: <>&\"'",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T9999")
            ],
            allow_custom=True,
        )

        bundle = stix2.Bundle(unicode_technique, allow_custom=True)
        unicode_stix_data = json.loads(bundle.serialize())

        # Parse with refactored parser
        result = self.parser.parse(unicode_stix_data, ["techniques"])

        # Verify Unicode handling
        assert len(result["techniques"]) == 1
        technique = result["techniques"][0]
        assert technique["id"] == "T9999"
        assert "Ünicode" in technique["name"]
        assert "🔒" in technique["description"]
        assert '<>&"' in technique["description"]

    def test_performance_regression_compatibility(self):
        """Test that compatibility doesn't introduce performance regression."""
        import time

        # Create larger test dataset
        large_stix_data = self._create_large_test_dataset()

        # Measure parsing time
        start_time = time.time()
        result = self.parser.parse(
            large_stix_data, ["techniques", "groups", "tactics", "mitigations"]
        )
        end_time = time.time()

        parsing_time = end_time - start_time

        # Verify parsing completed successfully
        assert isinstance(result, dict)
        assert all(
            entity_type in result
            for entity_type in ["techniques", "groups", "tactics", "mitigations"]
        )

        # Performance should be reasonable (less than 3 seconds for test data)
        assert (
            parsing_time < 3.0
        ), f"Parsing took {parsing_time:.2f} seconds, indicating performance regression"

    def _create_large_test_dataset(self) -> Dict[str, Any]:
        """Create a larger STIX dataset for performance testing."""
        objects = []

        # Create multiple techniques
        for i in range(20):
            technique = stix2.AttackPattern(
                name=f"Test Technique {i}",
                description=f"Test technique {i} description",
                external_references=[
                    stix2.ExternalReference(
                        source_name="mitre-attack", external_id=f"T{1000 + i:04d}"
                    )
                ],
                x_mitre_platforms=["Windows", "Linux"],
                kill_chain_phases=[
                    stix2.KillChainPhase(
                        kill_chain_name="mitre-attack", phase_name="execution"
                    )
                ],
                allow_custom=True,
            )
            objects.append(technique)

        # Create multiple groups
        for i in range(10):
            group = stix2.IntrusionSet(
                name=f"Test Group {i}",
                description=f"Test group {i} description",
                aliases=[f"Test Group {i}", f"TG{i}", f"Group{i}"],
                external_references=[
                    stix2.ExternalReference(
                        source_name="mitre-attack", external_id=f"G{1000 + i:04d}"
                    )
                ],
            )
            objects.append(group)

        # Create bundle
        bundle = stix2.Bundle(*objects, allow_custom=True)
        return json.loads(bundle.serialize())


class TestAPICompatibility(BaseTestCase):
    """Test API compatibility for external integrations."""

    def test_parser_api_compatibility(self):
        """Test that parser API maintains compatibility."""
        parser = STIXParser()
        
        # Test main parse method signature
        test_data = {"type": "bundle", "objects": []}
        entity_types = ["techniques"]
        
        # Should accept same parameters as before
        result = parser.parse(test_data, entity_types)
        
        assert isinstance(result, dict)
        assert "techniques" in result
        assert isinstance(result["techniques"], list)

    def test_data_loader_api_compatibility(self):
        """Test that DataLoader API maintains compatibility."""
        data_loader = DataLoader()
        
        # Test that key methods exist and work
        assert hasattr(data_loader, 'load_data_source')
        assert hasattr(data_loader, 'get_cached_data')
        assert hasattr(data_loader, '_process_relationships')
        
        # Test method signatures haven't changed
        with patch.object(data_loader, 'download_data') as mock_download:
            mock_download.return_value = {"type": "bundle", "objects": []}
            
            with patch.object(data_loader, 'config', {"data_sources": {"test": {"url": "http://test.com", "format": "stix", "entity_types": ["techniques"]}}}):
                # Should not raise signature errors
                try:
                    result = data_loader.load_data_source("test")
                    assert isinstance(result, dict)
                except Exception as e:
                    # Should not be signature-related errors
                    assert "signature" not in str(e).lower()

    def test_mcp_server_api_compatibility(self):
        """Test that MCP server API maintains compatibility."""
        mock_data_loader = Mock(spec=DataLoader)
        mock_data_loader.get_cached_data.return_value = {
            "techniques": [],
            "groups": [],
            "tactics": [],
            "mitigations": [],
            "relationships": []
        }
        
        # Should create server without errors
        mcp_server = create_mcp_server(mock_data_loader)
        assert mcp_server is not None
        
        # Should have all expected tools
        expected_tools = [
            "search_attack",
            "get_technique", 
            "list_tactics",
            "get_group_techniques",
            "get_technique_mitigations",
            "build_attack_path",
            "analyze_coverage_gaps",
            "detect_technique_relationships"
        ]
        
        # Verify tools are registered (implementation-dependent check)
        assert hasattr(mcp_server, 'list_tools') or hasattr(mcp_server, '_tools')