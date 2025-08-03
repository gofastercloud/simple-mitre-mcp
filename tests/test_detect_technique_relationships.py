"""
Tests for the detect_technique_relationships MCP tool.

This module tests the detect_technique_relationships tool functionality including
relationship discovery, hierarchy traversal, and attribution analysis.
"""

import pytest
from unittest.mock import Mock
from mcp.types import TextContent
from src.mcp_server import create_mcp_server
from src.data_loader import DataLoader


class TestDetectTechniqueRelationships:
    """Test detect_technique_relationships tool functionality."""

    @pytest.fixture
    def mock_data_loader(self):
        """Create a mock data loader with sample MITRE ATT&CK data and relationships."""
        mock_loader = Mock(spec=DataLoader)

        # Sample test data
        sample_data = {
            'techniques': [
                {
                    'id': 'T1055',
                    'name': 'Process Injection',
                    'description': 'Adversaries may inject code into processes.',
                    'tactics': ['TA0004'],
                    'platforms': ['Windows', 'Linux'],
                    'mitigations': ['M1040']
                },
                {
                    'id': 'T1055.001',
                    'name': 'Dynamic-link Library Injection',
                    'description': 'Adversaries may inject DLLs into processes.',
                    'tactics': ['TA0004'],
                    'platforms': ['Windows'],
                    'mitigations': ['M1040']
                },
                {
                    'id': 'T1059',
                    'name': 'Command and Scripting Interpreter',
                    'description': 'Adversaries may abuse command interpreters.',
                    'tactics': ['TA0002'],
                    'platforms': ['Windows', 'Linux', 'macOS'],
                    'mitigations': ['M1038']
                }
            ],
            'groups': [
                {
                    'id': 'G0016',
                    'name': 'APT29',
                    'description': 'APT29 is a threat group.',
                    'aliases': ['Cozy Bear', 'The Dukes'],
                    'techniques': ['T1055', 'T1059']
                },
                {
                    'id': 'G0032',
                    'name': 'Lazarus Group',
                    'description': 'Lazarus Group is a threat group.',
                    'aliases': ['HIDDEN COBRA'],
                    'techniques': ['T1055']
                }
            ],
            'mitigations': [
                {
                    'id': 'M1040',
                    'name': 'Behavior Prevention on Endpoint',
                    'description': 'Use capabilities to prevent suspicious behavior.',
                    'techniques': ['T1055', 'T1055.001']
                },
                {
                    'id': 'M1038',
                    'name': 'Execution Prevention',
                    'description': 'Block execution of code.',
                    'techniques': ['T1059']
                }
            ],
            'tactics': [
                {
                    'id': 'TA0002',
                    'name': 'Execution',
                    'description': 'The adversary is trying to run malicious code.'
                },
                {
                    'id': 'TA0004',
                    'name': 'Privilege Escalation',
                    'description': 'The adversary is trying to gain higher-level permissions.'
                }
            ]
        }

        # Sample STIX relationships
        sample_relationships = [
            {
                'type': 'relationship',
                'relationship_type': 'uses',
                'source_ref': 'intrusion-set--899ce53f-13a0-479b-a0e4-67d46e241542',  # APT29
                'target_ref': 'attack-pattern--43e7dc91-05b2-474c-b9ac-2ed4fe101f4d'   # T1055
            },
            {
                'type': 'relationship',
                'relationship_type': 'uses',
                'source_ref': 'intrusion-set--68391641-859f-4a9a-9a1e-3e5cf71ec376',  # Lazarus
                'target_ref': 'attack-pattern--43e7dc91-05b2-474c-b9ac-2ed4fe101f4d'   # T1055
            },
            {
                'type': 'relationship',
                'relationship_type': 'subtechnique-of',
                'source_ref': 'attack-pattern--f4599aa0-4f85-4a32-80ea-fc39dc965945',  # T1055.001
                'target_ref': 'attack-pattern--43e7dc91-05b2-474c-b9ac-2ed4fe101f4d'   # T1055
            },
            {
                'type': 'relationship',
                'relationship_type': 'mitigates',
                'source_ref': 'course-of-action--90c218c3-fbf8-4830-98a7-e8cfb7eaa485',  # M1040
                'target_ref': 'attack-pattern--43e7dc91-05b2-474c-b9ac-2ed4fe101f4d'   # T1055
            },
            {
                'type': 'relationship',
                'relationship_type': 'detects',
                'source_ref': 'x-mitre-data-component--685f917a-e95e-4ba0-ade1-c7d354dae6e0',  # Sample detector
                'target_ref': 'attack-pattern--43e7dc91-05b2-474c-b9ac-2ed4fe101f4d'   # T1055
            }
        ]

        mock_loader.get_cached_data.side_effect = lambda key: {
            'mitre_attack': sample_data,
            'mitre_attack_relationships': sample_relationships
        }.get(key)

        # Mock the download_data method to return sample raw data
        mock_raw_data = {
            'objects': [
                {
                    'id': 'attack-pattern--43e7dc91-05b2-474c-b9ac-2ed4fe101f4d',
                    'type': 'attack-pattern',
                    'name': 'Process Injection',
                    'external_references': [
                        {'source_name': 'mitre-attack', 'external_id': 'T1055'}
                    ]
                },
                {
                    'id': 'attack-pattern--f4599aa0-4f85-4a32-80ea-fc39dc965945',
                    'type': 'attack-pattern',
                    'name': 'Dynamic-link Library Injection',
                    'external_references': [
                        {'source_name': 'mitre-attack', 'external_id': 'T1055.001'}
                    ]
                },
                {
                    'id': 'attack-pattern--7385dfaf-6886-4229-9ecd-6fd678040830',
                    'type': 'attack-pattern',
                    'name': 'Command and Scripting Interpreter',
                    'external_references': [
                        {'source_name': 'mitre-attack', 'external_id': 'T1059'}
                    ]
                },
                {
                    'id': 'intrusion-set--899ce53f-13a0-479b-a0e4-67d46e241542',
                    'type': 'intrusion-set',
                    'name': 'APT29',
                    'external_references': [
                        {'source_name': 'mitre-attack', 'external_id': 'G0016'}
                    ]
                },
                {
                    'id': 'intrusion-set--68391641-859f-4a9a-9a1e-3e5cf71ec376',
                    'type': 'intrusion-set',
                    'name': 'Lazarus Group',
                    'external_references': [
                        {'source_name': 'mitre-attack', 'external_id': 'G0032'}
                    ]
                },
                {
                    'id': 'course-of-action--90c218c3-fbf8-4830-98a7-e8cfb7eaa485',
                    'type': 'course-of-action',
                    'name': 'Behavior Prevention on Endpoint',
                    'external_references': [
                        {'source_name': 'mitre-attack', 'external_id': 'M1040'}
                    ]
                },
                {
                    'id': 'x-mitre-data-component--685f917a-e95e-4ba0-ade1-c7d354dae6e0',
                    'type': 'x-mitre-data-component',
                    'name': 'Process Creation',
                    'external_references': [
                        {'source_name': 'mitre-attack', 'external_id': 'DS0009.001'}
                    ]
                }
            ]
        }

        mock_loader.download_data.return_value = mock_raw_data
        mock_loader.config = {
            'data_sources': {
                'mitre_attack': {
                    'url': 'https://example.com/test.json'
                }
            }
        }

        return mock_loader

    @pytest.fixture
    def mcp_server(self, mock_data_loader):
        """Create MCP server with mock data loader."""
        return create_mcp_server(mock_data_loader)

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_basic(self, mcp_server):
        """Test basic relationship detection for a technique."""
        # Execute with default parameters
        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 'T1055'
        })

        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"

        content = result[0].text
        assert "TECHNIQUE RELATIONSHIP ANALYSIS" in content
        assert "T1055 - Process Injection" in content
        assert "RELATIONSHIP SUMMARY" in content

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_specific_types(self, mcp_server):
        """Test relationship detection with specific relationship types."""
        # Execute with specific relationship types
        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 'T1055',
            'relationship_types': ['uses', 'subtechnique-o']
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "TECHNIQUE RELATIONSHIP ANALYSIS" in content
        assert "Relationship Types: uses, subtechnique-o" in content
        assert "USES RELATIONSHIPS" in content
        assert "SUBTECHNIQUE OF RELATIONSHIPS" in content

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_custom_depth(self, mcp_server):
        """Test relationship detection with custom depth."""
        # Execute with custom depth
        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 'T1055',
            'depth': 3
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "Analysis Depth: 3" in content

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_depth_limits(self, mcp_server):
        """Test that depth is properly limited."""
        # Execute with excessive depth
        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 'T1055',
            'depth': 10
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "Analysis Depth: 3" in content  # Should be capped at 3

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_subtechnique_hierarchy(self, mcp_server):
        """Test subtechnique hierarchy analysis."""
        # Execute focusing on subtechnique relationships
        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 'T1055',
            'relationship_types': ['subtechnique-o']
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "TECHNIQUE HIERARCHY" in content
        assert "Subtechniques" in content
        assert "T1055.001" in content

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_attribution(self, mcp_server):
        """Test attribution analysis."""
        # Execute focusing on uses relationships for attribution
        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 'T1055',
            'relationship_types': ['uses']
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "ATTRIBUTION ANALYSIS" in content
        assert "Threat Groups Using This Technique" in content
        assert "G0016" in content  # APT29
        assert "G0032" in content  # Lazarus Group

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_detection(self, mcp_server):
        """Test detection relationship analysis."""
        # Execute focusing on detection relationships
        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 'T1055',
            'relationship_types': ['detects']
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "DETECTION ANALYSIS" in content
        assert "Entities That Can Detect This Technique" in content

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_invalid_technique(self, mcp_server):
        """Test error handling for invalid technique ID."""
        # Execute with invalid technique
        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 'T9999'
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "Technique 'T9999' not found" in content

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_invalid_relationship_types(self, mcp_server):
        """Test error handling for invalid relationship types."""
        # Execute with invalid relationship types
        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 'T1055',
            'relationship_types': ['invalid_type', 'another_invalid']
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "No valid relationship types specified" in content

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_no_data_loader(self):
        """Test error handling when data loader is not available."""
        # Create server without data loader
        server = create_mcp_server(None)

        result, _ = await server.call_tool('detect_technique_relationships', {
            'technique_id': 'T1055'
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "Data loader not available" in content

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_no_cached_data(self, mcp_server):
        """Test error handling when cached data is not available."""
        # Mock data loader to return None for both cached data calls
        def mock_get_cached_data(key):
            return None

        mcp_server.data_loader.get_cached_data.side_effect = mock_get_cached_data

        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 'T1055'
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "MITRE ATT&CK data not loaded" in content

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_case_insensitive(self, mcp_server):
        """Test that technique ID is case insensitive."""
        # Execute with lowercase technique ID
        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 't1055'
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "T1055 - Process Injection" in content  # Should be normalized to uppercase

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_no_relationships(self, mcp_server):
        """Test handling of techniques with no relationships."""
        # Execute with technique that has no relationships in our mock data
        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 'T1059',  # This technique has no relationships in our mock
            'relationship_types': ['detects']  # Specific type that won't match
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "TECHNIQUE RELATIONSHIP ANALYSIS" in content
        assert "Total Relationships Found: 0" in content
        assert "No relationships found" in content

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_mixed_types(self, mcp_server):
        """Test with a mix of valid and invalid relationship types."""
        # Execute with mixed relationship types
        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 'T1055',
            'relationship_types': ['uses', 'invalid_type', 'mitigates', 'another_invalid']
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "TECHNIQUE RELATIONSHIP ANALYSIS" in content
        assert "Relationship Types: uses, mitigates" in content  # Should filter out invalid types

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_all_types(self, mcp_server):
        """Test with all valid relationship types."""
        # Execute with all relationship types
        result, _ = await mcp_server.call_tool('detect_technique_relationships', {
            'technique_id': 'T1055',
            'relationship_types': ['detects', 'subtechnique-of', 'attributed-to', 'uses', 'mitigates', 'revoked-by']
        })

        assert result is not None
        assert len(result) > 0

        content = result[0].text
        assert "TECHNIQUE RELATIONSHIP ANALYSIS" in content
        assert "detects, subtechnique-of, attributed-to, uses, mitigates, revoked-by" in content
