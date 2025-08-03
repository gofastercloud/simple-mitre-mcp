"""
End-to-end integration tests for the MCP server with all tools.

This module tests the complete integration of all 5 MCP tools to ensure
they work together properly and provide the expected functionality.
"""

import pytest
from unittest.mock import Mock, patch
from src.mcp_server import create_mcp_server
from src.data_loader import DataLoader


class TestEndToEndIntegration:
    """Test complete integration of all MCP tools."""

    @pytest.fixture
    def mock_data_loader(self):
        """Create a mock data loader with sample MITRE ATT&CK data."""
        mock_loader = Mock(spec=DataLoader)

        # Sample test data
        sample_data = {
            'tactics': [
                {
                    'id': 'TA0001',
                    'name': 'Initial Access',
                    'description': 'The adversary is trying to get into your network.'
                },
                {
                    'id': 'TA0002',
                    'name': 'Execution',
                    'description': 'The adversary is trying to run malicious code.'
                }
            ],
            'techniques': [
                {
                    'id': 'T1055',
                    'name': 'Process Injection',
                    'description': 'Adversaries may inject code into processes.',
                    'tactics': ['TA0002'],
                    'platforms': ['Windows', 'Linux'],
                    'mitigations': ['M1040']
                },
                {
                    'id': 'T1059',
                    'name': 'Command and Scripting Interpreter',
                    'description': 'Adversaries may abuse command interpreters.',
                    'tactics': ['TA0002'],
                    'platforms': ['Windows', 'Linux', 'macOS'],
                    'mitigations': ['M1038', 'M1049']
                }
            ],
            'groups': [
                {
                    'id': 'G0016',
                    'name': 'APT29',
                    'aliases': ['Cozy Bear', 'The Dukes'],
                    'description': 'APT29 is a threat group.',
                    'techniques': ['T1055', 'T1059']
                }
            ],
            'mitigations': [
                {
                    'id': 'M1040',
                    'name': 'Behavior Prevention on Endpoint',
                    'description': 'Use capabilities to prevent suspicious behavior patterns.'
                },
                {
                    'id': 'M1038',
                    'name': 'Execution Prevention',
                    'description': 'Block execution of code on a system.'
                },
                {
                    'id': 'M1049',
                    'name': 'Antivirus/Antimalware',
                    'description': 'Use signatures to identify malicious software.'
                }
            ]
        }

        mock_loader.get_cached_data.return_value = sample_data
        return mock_loader

    @pytest.fixture
    def mcp_server(self, mock_data_loader):
        """Create MCP server with mock data."""
        return create_mcp_server(mock_data_loader)

    @pytest.mark.asyncio
    async def test_all_tools_registered(self, mcp_server):
        """Test that all 5 required tools are registered."""
        # Get the registered tools from the server
        tools = await mcp_server.list_tools()
        tool_names = [tool.name for tool in tools]

        expected_tools = [
            'search_attack',
            'get_technique',
            'list_tactics',
            'get_group_techniques',
            'get_technique_mitigations',
            'build_attack_path',
            'analyze_coverage_gaps',
            'detect_technique_relationships'
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool '{expected_tool}' not registered"

        assert len(tool_names) == 8, f"Expected 8 tools, found {len(tool_names)}: {tool_names}"

    @pytest.mark.asyncio
    async def test_search_attack_tool_execution(self, mcp_server):
        """Test search_attack tool execution."""
        # Execute the tool
        result, _ = await mcp_server.call_tool('search_attack', {'query': 'process'})

        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        assert "process" in result[0].text.lower()
        assert "T1055" in result[0].text  # Should find Process Injection technique

    @pytest.mark.asyncio
    async def test_get_technique_tool_execution(self, mcp_server):
        """Test get_technique tool execution."""
        # Execute the tool
        result, _ = await mcp_server.call_tool('get_technique', {'technique_id': 'T1055'})

        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        assert "T1055" in result[0].text
        assert "Process Injection" in result[0].text
        assert "TA0002" in result[0].text  # Should show associated tactic
        assert "M1040" in result[0].text  # Should show mitigation

    @pytest.mark.asyncio
    async def test_list_tactics_tool_execution(self, mcp_server):
        """Test list_tactics tool execution."""
        # Execute the tool
        result, _ = await mcp_server.call_tool('list_tactics', {})

        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        assert "TA0001" in result[0].text
        assert "Initial Access" in result[0].text
        assert "TA0002" in result[0].text
        assert "Execution" in result[0].text

    @pytest.mark.asyncio
    async def test_get_group_techniques_tool_execution(self, mcp_server):
        """Test get_group_techniques tool execution."""
        # Execute the tool
        result, _ = await mcp_server.call_tool('get_group_techniques', {'group_id': 'G0016'})

        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        assert "G0016" in result[0].text
        assert "APT29" in result[0].text
        assert "T1055" in result[0].text  # Should show technique used by group
        assert "T1059" in result[0].text  # Should show technique used by group

    @pytest.mark.asyncio
    async def test_get_technique_mitigations_tool_execution(self, mcp_server):
        """Test get_technique_mitigations tool execution."""
        # Execute the tool
        result, _ = await mcp_server.call_tool('get_technique_mitigations', {'technique_id': 'T1059'})

        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        assert "T1059" in result[0].text
        assert "M1038" in result[0].text  # Should show mitigation
        assert "M1049" in result[0].text  # Should show mitigation
        assert "Execution Prevention" in result[0].text

    @pytest.mark.asyncio
    async def test_tool_parameter_validation(self, mcp_server):
        """Test that tools properly validate their parameters."""
        tools = {tool.name: tool for tool in await mcp_server.list_tools()}

        # Test search_attack requires query parameter
        search_tool = tools['search_attack']
        assert len(search_tool.inputSchema['properties']) == 1
        assert 'query' in search_tool.inputSchema['properties']
        assert search_tool.inputSchema.get('required', []) == ['query']

        # Test get_technique requires technique_id parameter
        technique_tool = tools['get_technique']
        assert len(technique_tool.inputSchema['properties']) == 1
        assert 'technique_id' in technique_tool.inputSchema['properties']
        assert technique_tool.inputSchema.get('required', []) == ['technique_id']

        # Test list_tactics has no required parameters
        tactics_tool = tools['list_tactics']
        assert len(tactics_tool.inputSchema['properties']) == 0
        assert tactics_tool.inputSchema.get('required', []) == []

        # Test get_group_techniques requires group_id parameter
        group_tool = tools['get_group_techniques']
        assert len(group_tool.inputSchema['properties']) == 1
        assert 'group_id' in group_tool.inputSchema['properties']
        assert group_tool.inputSchema.get('required', []) == ['group_id']

        # Test get_technique_mitigations requires technique_id parameter
        mitigations_tool = tools['get_technique_mitigations']
        assert len(mitigations_tool.inputSchema['properties']) == 1
        assert 'technique_id' in mitigations_tool.inputSchema['properties']
        assert mitigations_tool.inputSchema.get('required', []) == ['technique_id']

    @pytest.mark.asyncio
    async def test_tool_descriptions_and_metadata(self, mcp_server):
        """Test that all tools have proper descriptions and metadata."""
        tools = {tool.name: tool for tool in await mcp_server.list_tools()}

        # Check search_attack metadata
        search_tool = tools['search_attack']
        assert search_tool.description is not None
        assert len(search_tool.description) > 0
        assert "search" in search_tool.description.lower()

        # Check get_technique metadata
        technique_tool = tools['get_technique']
        assert technique_tool.description is not None
        assert "technique" in technique_tool.description.lower()

        # Check list_tactics metadata
        tactics_tool = tools['list_tactics']
        assert tactics_tool.description is not None
        assert "tactics" in tactics_tool.description.lower()

        # Check get_group_techniques metadata
        group_tool = tools['get_group_techniques']
        assert group_tool.description is not None
        assert "group" in group_tool.description.lower()

        # Check get_technique_mitigations metadata
        mitigations_tool = tools['get_technique_mitigations']
        assert mitigations_tool.description is not None
        assert "mitigation" in mitigations_tool.description.lower()

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, mcp_server):
        """Test error handling across all tools."""
        # Test get_technique with invalid ID
        result, _ = await mcp_server.call_tool('get_technique', {'technique_id': 'INVALID'})
        assert result is not None
        assert "not found" in result[0].text.lower()

        # Test get_group_techniques with invalid ID
        result, _ = await mcp_server.call_tool('get_group_techniques', {'group_id': 'INVALID'})
        assert result is not None
        assert "not found" in result[0].text.lower()

        # Test get_technique_mitigations with invalid ID
        result, _ = await mcp_server.call_tool('get_technique_mitigations', {'technique_id': 'INVALID'})
        assert result is not None
        assert "not found" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_data_consistency_across_tools(self, mcp_server):
        """Test that data is consistent across different tools."""
        # Get technique details
        technique_result, _ = await mcp_server.call_tool('get_technique', {'technique_id': 'T1055'})

        # Search for the same technique
        search_result, _ = await mcp_server.call_tool('search_attack', {'query': 'T1055'})

        # Both should contain the technique ID and name
        technique_text = technique_result[0].text
        search_text = search_result[0].text

        assert "T1055" in technique_text
        assert "T1055" in search_text
        assert "Process Injection" in technique_text
        assert "Process Injection" in search_text

    @pytest.mark.asyncio
    async def test_server_configuration_integration(self, mcp_server):
        """Test that server is properly configured with all components."""
        # Check server has data loader
        assert hasattr(mcp_server, 'data_loader')
        assert mcp_server.data_loader is not None

        # Check server name and instructions
        assert mcp_server.name == "mitre-attack-mcp-server"
        assert mcp_server.instructions is not None
        assert len(mcp_server.instructions) > 0
        assert "MITRE ATT&CK" in mcp_server.instructions
