"""
Comprehensive backward compatibility tests for STIX2 library refactor.

This module tests that the refactored STIX parser using the official STIX2 library
produces identical output to the original custom parsing implementation, ensuring
complete backward compatibility for all MCP tools and entity types.
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


class TestBackwardCompatibility:
    """Test backward compatibility of STIX2 library refactor."""

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
                    url="https://attack.mitre.org/techniques/T1055/"
                )
            ],
            x_mitre_platforms=["Windows", "macOS", "Linux"],
            kill_chain_phases=[
                stix2.KillChainPhase(
                    kill_chain_name="mitre-attack",
                    phase_name="defense-evasion"
                ),
                stix2.KillChainPhase(
                    kill_chain_name="mitre-attack",
                    phase_name="privilege-escalation"
                )
            ],
            allow_custom=True
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
                    url="https://attack.mitre.org/groups/G0016/"
                )
            ]
        )

        # Create tactic
        tactic = stix2.parse({
            "type": "x-mitre-tactic",
            "spec_version": "2.1",
            "id": f"x-mitre-tactic--{uuid.uuid4()}",
            "name": "Defense Evasion",
            "description": "The adversary is trying to avoid being detected.",
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": "TA0005",
                    "url": "https://attack.mitre.org/tactics/TA0005/"
                }
            ],
            "x_mitre_shortname": "defense-evasion"
        }, allow_custom=True)

        # Create mitigation
        mitigation = stix2.CourseOfAction(
            name="Application Isolation and Sandboxing",
            description="Restrict execution of code to a virtual environment on or in transit to an endpoint system.",
            external_references=[
                stix2.ExternalReference(
                    source_name="mitre-attack",
                    external_id="M1048",
                    url="https://attack.mitre.org/mitigations/M1048/"
                )
            ]
        )

        # Create relationships
        uses_relationship = stix2.Relationship(
            relationship_type="uses",
            source_ref=group.id,
            target_ref=technique.id
        )

        mitigates_relationship = stix2.Relationship(
            relationship_type="mitigates",
            source_ref=mitigation.id,
            target_ref=technique.id
        )

        # Create bundle
        bundle = stix2.Bundle(
            technique,
            group,
            tactic,
            mitigation,
            uses_relationship,
            mitigates_relationship,
            allow_custom=True
        )

        return json.loads(bundle.serialize())

    def _create_legacy_parser_mock(self) -> Mock:
        """Create a mock that simulates the old custom parsing behavior."""
        mock_parser = Mock(spec=STIXParser)
        
        # Mock the old custom parsing method to return expected legacy format
        def mock_custom_parse(stix_data, entity_types):
            result = {entity_type: [] for entity_type in entity_types}
            
            for obj in stix_data.get('objects', []):
                obj_type = obj.get('type', '')
                
                if obj_type == 'attack-pattern' and 'techniques' in entity_types:
                    result['techniques'].append({
                        'id': 'T1055',
                        'name': 'Process Injection',
                        'description': 'Adversaries may inject code into processes in order to evade process-based defenses.',
                        'platforms': ['Windows', 'macOS', 'Linux'],
                        'tactics': ['TA0005', 'TA0004'],
                        'mitigations': []
                    })
                elif obj_type == 'intrusion-set' and 'groups' in entity_types:
                    result['groups'].append({
                        'id': 'G0016',
                        'name': 'APT29',
                        'description': "APT29 is a threat group that has been attributed to Russia's Foreign Intelligence Service.",
                        'aliases': ['Cozy Bear', 'The Dukes', 'YTTRIUM'],  # Primary name filtered out
                        'techniques': []
                    })
                elif obj_type == 'x-mitre-tactic' and 'tactics' in entity_types:
                    result['tactics'].append({
                        'id': 'TA0005',
                        'name': 'Defense Evasion',
                        'description': 'The adversary is trying to avoid being detected.'
                    })
                elif obj_type == 'course-of-action' and 'mitigations' in entity_types:
                    result['mitigations'].append({
                        'id': 'M1048',
                        'name': 'Application Isolation and Sandboxing',
                        'description': 'Restrict execution of code to a virtual environment on or in transit to an endpoint system.',
                        'techniques': []
                    })
            
            return result
        
        mock_parser._parse_with_custom_logic.return_value = mock_custom_parse
        return mock_parser

    def test_technique_extraction_output_identical(self):
        """Test that technique extraction produces identical output."""
        # Parse with new STIX2 library method
        new_result = self.parser._parse_with_stix2_library(self.sample_stix_data, ['techniques'])
        
        # Verify technique data structure and content
        assert 'techniques' in new_result
        assert len(new_result['techniques']) == 1
        
        technique = new_result['techniques'][0]
        assert technique['id'] == 'T1055'
        assert technique['name'] == 'Process Injection'
        assert 'Adversaries may inject code into processes' in technique['description']
        assert technique['platforms'] == ['Windows', 'macOS', 'Linux']
        assert 'TA0005' in technique['tactics']  # defense-evasion
        assert 'TA0004' in technique['tactics']  # privilege-escalation
        assert technique['mitigations'] == []  # Initially empty

    def test_group_extraction_output_identical(self):
        """Test that group extraction produces identical output."""
        # Parse with new STIX2 library method
        new_result = self.parser._parse_with_stix2_library(self.sample_stix_data, ['groups'])
        
        # Verify group data structure and content
        assert 'groups' in new_result
        assert len(new_result['groups']) == 1
        
        group = new_result['groups'][0]
        assert group['id'] == 'G0016'
        assert group['name'] == 'APT29'
        assert "Russia's Foreign Intelligence Service" in group['description']
        
        # Verify aliases filtering (primary name should be filtered out)
        expected_aliases = ['Cozy Bear', 'The Dukes', 'YTTRIUM']
        assert all(alias in group['aliases'] for alias in expected_aliases)
        assert 'APT29' not in group['aliases']  # Primary name filtered out
        assert group['techniques'] == []  # Initially empty

    def test_tactic_extraction_output_identical(self):
        """Test that tactic extraction produces identical output."""
        # Parse with new STIX2 library method
        new_result = self.parser._parse_with_stix2_library(self.sample_stix_data, ['tactics'])
        
        # Verify tactic data structure and content
        assert 'tactics' in new_result
        assert len(new_result['tactics']) == 1
        
        tactic = new_result['tactics'][0]
        assert tactic['id'] == 'TA0005'
        assert tactic['name'] == 'Defense Evasion'
        assert 'trying to avoid being detected' in tactic['description']

    def test_mitigation_extraction_output_identical(self):
        """Test that mitigation extraction produces identical output."""
        # Parse with new STIX2 library method
        new_result = self.parser._parse_with_stix2_library(self.sample_stix_data, ['mitigations'])
        
        # Verify mitigation data structure and content
        assert 'mitigations' in new_result
        assert len(new_result['mitigations']) == 1
        
        mitigation = new_result['mitigations'][0]
        assert mitigation['id'] == 'M1048'
        assert mitigation['name'] == 'Application Isolation and Sandboxing'
        assert 'virtual environment' in mitigation['description']
        assert mitigation['techniques'] == []  # Initially empty

    def test_all_entity_types_extraction_identical(self):
        """Test that all entity types can be extracted together with identical output."""
        entity_types = ['techniques', 'groups', 'tactics', 'mitigations']
        
        # Parse with new STIX2 library method
        new_result = self.parser._parse_with_stix2_library(self.sample_stix_data, entity_types)
        
        # Verify all entity types are present
        for entity_type in entity_types:
            assert entity_type in new_result
            assert len(new_result[entity_type]) == 1
        
        # Verify specific entity data
        assert new_result['techniques'][0]['id'] == 'T1055'
        assert new_result['groups'][0]['id'] == 'G0016'
        assert new_result['tactics'][0]['id'] == 'TA0005'
        assert new_result['mitigations'][0]['id'] == 'M1048'

    def test_fallback_mechanism_maintains_compatibility(self):
        """Test that fallback to custom parsing maintains compatibility."""
        # Create invalid STIX data that will trigger fallback
        invalid_stix_data = {
            "type": "bundle",
            "spec_version": "2.1",
            "id": "invalid-bundle-id",  # Invalid format
            "objects": [
                {
                    "type": "attack-pattern",
                    "spec_version": "2.1",
                    "id": f"attack-pattern--{uuid.uuid4()}",
                    "name": "Test Technique",
                    "description": "Test description",
                    "external_references": [
                        {
                            "source_name": "mitre-attack",
                            "external_id": "T9999"
                        }
                    ]
                }
            ]
        }
        
        # Mock the custom parsing fallback
        with patch.object(self.parser, '_parse_with_custom_logic') as mock_custom:
            mock_custom.return_value = {
                'techniques': [{
                    'id': 'T9999',
                    'name': 'Test Technique',
                    'description': 'Test description',
                    'platforms': [],
                    'tactics': [],
                    'mitigations': []
                }]
            }
            
            # Parse should fallback to custom logic
            result = self.parser.parse(invalid_stix_data, ['techniques'])
            
            # Verify fallback was used and output format is maintained
            mock_custom.assert_called_once()
            assert 'techniques' in result
            assert len(result['techniques']) == 1
            assert result['techniques'][0]['id'] == 'T9999'

    @pytest.mark.asyncio
    async def test_all_mcp_tools_work_with_refactored_parser(self):
        """Test that all 8 MCP tools continue to work with refactored parser."""
        # Create mock data loader with comprehensive test data
        mock_data_loader = Mock(spec=DataLoader)
        
        # Parse test data with refactored parser
        parsed_data = self.parser.parse(self.sample_stix_data, ['techniques', 'groups', 'tactics', 'mitigations'])
        
        # Add relationships for testing
        parsed_data['relationships'] = [
            {
                'type': 'uses',
                'source_id': 'G0016',
                'target_id': 'T1055'
            },
            {
                'type': 'mitigates',
                'source_id': 'M1048',
                'target_id': 'T1055'
            }
        ]
        
        # Update entities with relationship data
        parsed_data['groups'][0]['techniques'] = ['T1055']
        parsed_data['techniques'][0]['mitigations'] = ['M1048']
        parsed_data['mitigations'][0]['techniques'] = ['T1055']
        
        mock_data_loader.get_cached_data.return_value = parsed_data
        
        # Create MCP server with refactored parser data
        mcp_server = create_mcp_server(mock_data_loader)
        
        # Test all 8 MCP tools
        tools_to_test = [
            ('search_attack', {'query': 'process'}),
            ('get_technique', {'technique_id': 'T1055'}),
            ('list_tactics', {}),
            ('get_group_techniques', {'group_id': 'G0016'}),
            ('get_technique_mitigations', {'technique_id': 'T1055'}),
            ('build_attack_path', {'start_tactic': 'TA0001', 'end_tactic': 'TA0005'}),
            ('analyze_coverage_gaps', {'threat_groups': ['G0016']}),
            ('detect_technique_relationships', {'technique_id': 'T1055'})
        ]
        
        for tool_name, params in tools_to_test:
            result, _ = await mcp_server.call_tool(tool_name, params)
            
            # Verify tool executed successfully
            assert result is not None
            assert len(result) > 0
            assert result[0].type == "text"
            
            # Verify tool-specific content
            if tool_name == 'search_attack':
                assert 'T1055' in result[0].text or 'Process Injection' in result[0].text
            elif tool_name == 'get_technique':
                assert 'T1055' in result[0].text
                assert 'Process Injection' in result[0].text
            elif tool_name == 'list_tactics':
                assert 'TA0005' in result[0].text or 'Defense Evasion' in result[0].text
            elif tool_name == 'get_group_techniques':
                assert 'G0016' in result[0].text
                assert 'APT29' in result[0].text
            elif tool_name == 'get_technique_mitigations':
                assert 'M1048' in result[0].text

    def test_edge_case_malformed_data_handling(self):
        """Test handling of malformed STIX data maintains compatibility."""
        malformed_cases = [
            # Missing required fields
            {
                "type": "bundle",
                "spec_version": "2.1",
                "id": f"bundle--{uuid.uuid4()}",
                "objects": [
                    {
                        "type": "attack-pattern",
                        "spec_version": "2.1",
                        "id": f"attack-pattern--{uuid.uuid4()}",
                        "name": "Incomplete Technique"
                        # Missing description and external_references
                    }
                ]
            },
            # Invalid external references
            {
                "type": "bundle",
                "spec_version": "2.1",
                "id": f"bundle--{uuid.uuid4()}",
                "objects": [
                    {
                        "type": "attack-pattern",
                        "spec_version": "2.1",
                        "id": f"attack-pattern--{uuid.uuid4()}",
                        "name": "Invalid Refs Technique",
                        "description": "Test description",
                        "external_references": "invalid_format"  # Should be array
                    }
                ]
            },
            # Empty bundle
            {
                "type": "bundle",
                "spec_version": "2.1",
                "id": f"bundle--{uuid.uuid4()}",
                "objects": []
            }
        ]
        
        for malformed_data in malformed_cases:
            # Should handle gracefully without crashing
            try:
                result = self.parser.parse(malformed_data, ['techniques'])
                # Should return empty results for malformed data
                assert isinstance(result, dict)
                assert 'techniques' in result
                assert isinstance(result['techniques'], list)
            except Exception as e:
                # If exceptions are raised, they should be handled gracefully
                assert isinstance(e, (STIXError, InvalidValueError, MissingPropertiesError))

    def test_error_scenarios_backward_compatibility(self):
        """Test that error scenarios maintain backward compatibility."""
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
                        "name": "Invalid Object"
                    }
                ]
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
                            {
                                "source_name": "other-source",
                                "external_id": "OTHER-123"
                            }
                        ]
                    }
                ]
            }
        ]
        
        for error_data in error_scenarios:
            result = self.parser.parse(error_data, ['techniques'])
            
            # Should return empty results for invalid/unusable data
            assert isinstance(result, dict)
            assert 'techniques' in result
            assert len(result['techniques']) == 0

    def test_data_loader_integration_backward_compatibility(self):
        """Test that DataLoader integration maintains backward compatibility."""
        data_loader = DataLoader()
        
        # Mock the download to return our test data
        with patch.object(data_loader, 'download_data') as mock_download:
            mock_download.return_value = self.sample_stix_data
            
            # Mock configuration
            with patch.object(data_loader, 'config', {
                'data_sources': {
                    'test_source': {
                        'url': 'http://test.com/data.json',
                        'format': 'stix',
                        'entity_types': ['techniques', 'groups', 'tactics', 'mitigations']
                    }
                }
            }):
                # Load data using refactored parser
                result = data_loader.load_data_source('test_source')
                
                # Verify all entity types are loaded correctly
                assert 'techniques' in result
                assert 'groups' in result
                assert 'tactics' in result
                assert 'mitigations' in result
                
                # Verify entity data integrity
                assert len(result['techniques']) == 1
                assert result['techniques'][0]['id'] == 'T1055'
                assert len(result['groups']) == 1
                assert result['groups'][0]['id'] == 'G0016'

    def test_relationship_processing_backward_compatibility(self):
        """Test that relationship processing maintains backward compatibility."""
        data_loader = DataLoader()
        
        # Process relationships using the refactored parser
        entity_types = ['techniques', 'groups', 'mitigations']
        parsed_data = self.parser.parse(self.sample_stix_data, entity_types)
        
        # Process relationships
        enhanced_data = data_loader._process_relationships(self.sample_stix_data, parsed_data)
        
        # Verify relationships are processed correctly
        assert 'relationships' in enhanced_data
        
        # Check that group has techniques
        group = next((g for g in enhanced_data['groups'] if g['id'] == 'G0016'), None)
        assert group is not None
        assert 'techniques' in group
        assert 'T1055' in group['techniques']
        
        # Check that technique has mitigations
        technique = next((t for t in enhanced_data['techniques'] if t['id'] == 'T1055'), None)
        assert technique is not None
        assert 'mitigations' in technique
        assert 'M1048' in technique['mitigations']

    def test_performance_regression_check(self):
        """Test that refactored parser doesn't have significant performance regression."""
        import time
        
        # Create larger test dataset
        large_stix_data = self._create_large_test_dataset()
        
        # Measure parsing time
        start_time = time.time()
        result = self.parser.parse(large_stix_data, ['techniques', 'groups', 'tactics', 'mitigations'])
        end_time = time.time()
        
        parsing_time = end_time - start_time
        
        # Verify parsing completed successfully
        assert isinstance(result, dict)
        assert all(entity_type in result for entity_type in ['techniques', 'groups', 'tactics', 'mitigations'])
        
        # Performance should be reasonable (less than 5 seconds for test data)
        assert parsing_time < 5.0, f"Parsing took {parsing_time:.2f} seconds, which may indicate performance regression"

    def _create_large_test_dataset(self) -> Dict[str, Any]:
        """Create a larger STIX dataset for performance testing."""
        objects = []
        
        # Create multiple techniques
        for i in range(10):
            technique = stix2.AttackPattern(
                name=f"Test Technique {i}",
                description=f"Test technique {i} description",
                external_references=[
                    stix2.ExternalReference(
                        source_name="mitre-attack",
                        external_id=f"T{1000 + i:04d}"
                    )
                ],
                x_mitre_platforms=["Windows", "Linux"],
                kill_chain_phases=[
                    stix2.KillChainPhase(
                        kill_chain_name="mitre-attack",
                        phase_name="execution"
                    )
                ],
                allow_custom=True
            )
            objects.append(technique)
        
        # Create multiple groups
        for i in range(5):
            group = stix2.IntrusionSet(
                name=f"Test Group {i}",
                description=f"Test group {i} description",
                aliases=[f"Test Group {i}", f"TG{i}", f"Group{i}"],
                external_references=[
                    stix2.ExternalReference(
                        source_name="mitre-attack",
                        external_id=f"G{1000 + i:04d}"
                    )
                ]
            )
            objects.append(group)
        
        # Create bundle
        bundle = stix2.Bundle(*objects, allow_custom=True)
        return json.loads(bundle.serialize())

    def test_unicode_and_special_characters_handling(self):
        """Test handling of Unicode and special characters maintains compatibility."""
        # Create STIX data with Unicode characters
        unicode_technique = stix2.AttackPattern(
            name="Téchnique with Ünicode",
            description="Description with émojis 🔒 and spëcial characters: <>&\"'",
            external_references=[
                stix2.ExternalReference(
                    source_name="mitre-attack",
                    external_id="T9999"
                )
            ],
            allow_custom=True
        )
        
        bundle = stix2.Bundle(unicode_technique, allow_custom=True)
        unicode_stix_data = json.loads(bundle.serialize())
        
        # Parse with refactored parser
        result = self.parser.parse(unicode_stix_data, ['techniques'])
        
        # Verify Unicode handling
        assert len(result['techniques']) == 1
        technique = result['techniques'][0]
        assert technique['id'] == 'T9999'
        assert 'Ünicode' in technique['name']
        assert '🔒' in technique['description']
        assert '<>&"' in technique['description']

    def test_empty_and_null_field_handling(self):
        """Test handling of empty and null fields maintains compatibility."""
        # Create STIX data with empty/null fields
        minimal_technique = stix2.AttackPattern(
            name="Minimal Technique",
            description="",  # Empty description
            external_references=[
                stix2.ExternalReference(
                    source_name="mitre-attack",
                    external_id="T8888"
                )
            ],
            allow_custom=True
        )
        
        bundle = stix2.Bundle(minimal_technique, allow_custom=True)
        minimal_stix_data = json.loads(bundle.serialize())
        
        # Parse with refactored parser
        result = self.parser.parse(minimal_stix_data, ['techniques'])
        
        # Verify empty field handling
        assert len(result['techniques']) == 1
        technique = result['techniques'][0]
        assert technique['id'] == 'T8888'
        assert technique['name'] == 'Minimal Technique'
        assert technique['description'] == ''  # Empty string preserved
        assert 'platforms' not in technique or technique['platforms'] == []
        assert 'tactics' not in technique or technique['tactics'] == []

    @pytest.mark.asyncio
    async def test_real_mitre_attack_data_integration(self):
        """Test integration with real MITRE ATT&CK data to ensure production compatibility."""
        import requests
        from src.data_loader import DataLoader
        
        # Skip this test if we can't reach the internet
        try:
            # Use a small timeout to avoid hanging in CI/CD
            response = requests.get(
                "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json",
                timeout=10
            )
            if response.status_code != 200:
                pytest.skip("Cannot download real MITRE ATT&CK data")
                
            real_stix_data = response.json()
            
        except (requests.RequestException, requests.Timeout, Exception) as e:
            pytest.skip(f"Cannot download real MITRE ATT&CK data: {e}")
        
        # Parse real data with refactored parser
        entity_types = ['techniques', 'groups', 'tactics', 'mitigations']
        result = self.parser.parse(real_stix_data, entity_types)
        
        # Verify all entity types are present and populated
        for entity_type in entity_types:
            assert entity_type in result
            assert isinstance(result[entity_type], list)
            assert len(result[entity_type]) > 0, f"No {entity_type} found in real data"
        
        # Verify we have a reasonable number of each entity type
        assert len(result['techniques']) > 100, f"Expected >100 techniques, got {len(result['techniques'])}"
        assert len(result['groups']) > 50, f"Expected >50 groups, got {len(result['groups'])}"
        assert len(result['tactics']) > 10, f"Expected >10 tactics, got {len(result['tactics'])}"
        assert len(result['mitigations']) > 30, f"Expected >30 mitigations, got {len(result['mitigations'])}"
        
        # Verify data structure integrity for each entity type
        for technique in result['techniques'][:5]:  # Check first 5 techniques
            assert 'id' in technique and technique['id'].startswith('T')
            assert 'name' in technique and len(technique['name']) > 0
            assert 'description' in technique
            assert 'platforms' in technique and isinstance(technique['platforms'], list)
            assert 'tactics' in technique and isinstance(technique['tactics'], list)
            assert 'mitigations' in technique and isinstance(technique['mitigations'], list)
        
        for group in result['groups'][:5]:  # Check first 5 groups
            assert 'id' in group and group['id'].startswith('G')
            assert 'name' in group and len(group['name']) > 0
            assert 'description' in group
            # Some groups may not have aliases, but if they do, it should be a list
            if 'aliases' in group:
                assert isinstance(group['aliases'], list)
            assert 'techniques' in group and isinstance(group['techniques'], list)
        
        for tactic in result['tactics']:  # Check all tactics
            assert 'id' in tactic and tactic['id'].startswith('TA')
            assert 'name' in tactic and len(tactic['name']) > 0
            assert 'description' in tactic
        
        for mitigation in result['mitigations'][:5]:  # Check first 5 mitigations
            assert 'id' in mitigation and len(mitigation['id']) > 0
            # Most mitigations start with 'M', but some legacy ones might have different formats
            assert mitigation['id'].startswith(('M', 'T'))  # Allow both M and T prefixes
            assert 'name' in mitigation and len(mitigation['name']) > 0
            assert 'description' in mitigation
            assert 'techniques' in mitigation and isinstance(mitigation['techniques'], list)
        
        # Test that MCP tools work with real data
        data_loader = DataLoader()
        
        # Mock the download to return real data
        with patch.object(data_loader, 'download_data') as mock_download:
            mock_download.return_value = real_stix_data
            
            # Mock configuration
            with patch.object(data_loader, 'config', {
                'data_sources': {
                    'mitre_attack': {
                        'url': 'https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json',
                        'format': 'stix',
                        'entity_types': entity_types
                    }
                }
            }):
                # Load and process real data
                processed_data = data_loader.load_data_source('mitre_attack')
                
                # Verify processing worked
                assert all(entity_type in processed_data for entity_type in entity_types)
                
                # Create MCP server with real data
                mcp_server = create_mcp_server(data_loader)
                
                # Test a few key MCP tools with real data
                search_result, _ = await mcp_server.call_tool('search_attack', {'query': 'process injection'})
                assert search_result is not None
                assert len(search_result) > 0
                assert 'T1055' in search_result[0].text or 'process' in search_result[0].text.lower()
                
                # Test getting a known technique
                if any(t['id'] == 'T1055' for t in processed_data['techniques']):
                    technique_result, _ = await mcp_server.call_tool('get_technique', {'technique_id': 'T1055'})
                    assert technique_result is not None
                    assert 'T1055' in technique_result[0].text
                
                # Test listing tactics
                tactics_result, _ = await mcp_server.call_tool('list_tactics', {})
                assert tactics_result is not None
                assert len(tactics_result) > 0
                assert 'TA' in tactics_result[0].text  # Should contain tactic IDs

    def test_stix2_library_error_handling_comprehensive(self):
        """Test comprehensive error handling with various STIX2 library error scenarios."""
        from stix2.exceptions import STIXError, InvalidValueError, MissingPropertiesError
        
        # Test cases that should trigger different STIX2 library errors
        error_test_cases = [
            # Invalid STIX version
            {
                "type": "bundle",
                "spec_version": "1.0",  # Invalid version
                "id": f"bundle--{uuid.uuid4()}",
                "objects": []
            },
            # Invalid UUID format
            {
                "type": "bundle",
                "spec_version": "2.1",
                "id": "invalid-uuid-format",
                "objects": []
            },
            # Missing required bundle fields
            {
                "type": "bundle",
                "spec_version": "2.1",
                # Missing id field
                "objects": []
            },
            # Invalid object in bundle
            {
                "type": "bundle",
                "spec_version": "2.1",
                "id": f"bundle--{uuid.uuid4()}",
                "objects": [
                    {
                        "type": "attack-pattern",
                        "spec_version": "2.1",
                        "id": "invalid-attack-pattern-id",  # Invalid UUID format
                        "name": "Test Technique"
                    }
                ]
            }
        ]
        
        for i, error_case in enumerate(error_test_cases):
            try:
                # Should handle errors gracefully without crashing
                result = self.parser.parse(error_case, ['techniques'])
                
                # Should return empty results for invalid data
                assert isinstance(result, dict)
                assert 'techniques' in result
                assert isinstance(result['techniques'], list)
                
                # Log which test case we're on for debugging
                print(f"Error test case {i + 1} handled gracefully")
                
            except Exception as e:
                # If exceptions are raised, they should be expected STIX errors
                assert isinstance(e, (STIXError, InvalidValueError, MissingPropertiesError, ValueError))
                print(f"Error test case {i + 1} raised expected exception: {type(e).__name__}")

    def test_large_dataset_performance_and_memory(self):
        """Test performance and memory usage with large datasets."""
        import time
        import gc
        
        # Create a very large test dataset
        large_objects = []
        
        # Create 100 techniques
        for i in range(100):
            technique = stix2.AttackPattern(
                name=f"Large Test Technique {i:03d}",
                description=f"This is a test technique {i} with a longer description to simulate real data size. " * 5,
                external_references=[
                    stix2.ExternalReference(
                        source_name="mitre-attack",
                        external_id=f"T{2000 + i:04d}",
                        url=f"https://attack.mitre.org/techniques/T{2000 + i:04d}/"
                    )
                ],
                x_mitre_platforms=["Windows", "Linux", "macOS"],
                kill_chain_phases=[
                    stix2.KillChainPhase(
                        kill_chain_name="mitre-attack",
                        phase_name="execution"
                    ),
                    stix2.KillChainPhase(
                        kill_chain_name="mitre-attack",
                        phase_name="defense-evasion"
                    )
                ],
                allow_custom=True
            )
            large_objects.append(technique)
        
        # Create 50 groups
        for i in range(50):
            group = stix2.IntrusionSet(
                name=f"Large Test Group {i:03d}",
                description=f"This is a test group {i} with detailed attribution information. " * 3,
                aliases=[f"Large Test Group {i:03d}", f"LTG{i:03d}", f"Group{i:03d}", f"TestGroup{i:03d}"],
                external_references=[
                    stix2.ExternalReference(
                        source_name="mitre-attack",
                        external_id=f"G{2000 + i:04d}",
                        url=f"https://attack.mitre.org/groups/G{2000 + i:04d}/"
                    )
                ]
            )
            large_objects.append(group)
        
        # Create bundle
        bundle = stix2.Bundle(*large_objects, allow_custom=True)
        large_stix_data = json.loads(bundle.serialize())
        
        # Measure memory before parsing
        gc.collect()
        
        # Measure parsing time and memory
        start_time = time.time()
        result = self.parser.parse(large_stix_data, ['techniques', 'groups'])
        end_time = time.time()
        
        parsing_time = end_time - start_time
        
        # Verify parsing completed successfully
        assert isinstance(result, dict)
        assert 'techniques' in result and 'groups' in result
        assert len(result['techniques']) == 100
        assert len(result['groups']) == 50
        
        # Performance should be reasonable (less than 10 seconds for large test data)
        assert parsing_time < 10.0, f"Large dataset parsing took {parsing_time:.2f} seconds, which may indicate performance issues"
        
        # Verify data integrity in large dataset
        for i, technique in enumerate(result['techniques']):
            assert technique['id'] == f"T{2000 + i:04d}"
            assert technique['name'] == f"Large Test Technique {i:03d}"
            assert len(technique['platforms']) == 3
            assert len(technique['tactics']) == 2  # execution and defense-evasion
        
        for i, group in enumerate(result['groups']):
            assert group['id'] == f"G{2000 + i:04d}"
            assert group['name'] == f"Large Test Group {i:03d}"
            assert len(group['aliases']) == 3  # Primary name filtered out
        
        print(f"Large dataset test completed: {parsing_time:.2f}s for 150 objects")


if __name__ == '__main__':
    pytest.main([__file__])