"""
Tests for the build_attack_path MCP tool.

This module tests the build_attack_path tool functionality including
attack path construction, kill chain sequencing, and filtering capabilities.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from mcp.types import TextContent
from src.mcp_server import create_mcp_server
from src.data_loader import DataLoader


class TestBuildAttackPath:
    """Test build_attack_path tool functionality."""
    
    @pytest.fixture
    def mock_data_loader(self):
        """Create a mock data loader with sample MITRE ATT&CK data."""
        mock_loader = Mock(spec=DataLoader)
        
        # Sample test data with tactics, techniques, and groups
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
                },
                {
                    'id': 'TA0040',
                    'name': 'Impact',
                    'description': 'The adversary is trying to manipulate, interrupt, or destroy your systems and data.'
                }
            ],
            'techniques': [
                {
                    'id': 'T1566',
                    'name': 'Phishing',
                    'description': 'Adversaries may send phishing messages.',
                    'tactics': ['TA0001'],
                    'platforms': ['Windows', 'macOS', 'Linux'],
                    'mitigations': ['M1031']
                },
                {
                    'id': 'T1059',
                    'name': 'Command and Scripting Interpreter',
                    'description': 'Adversaries may abuse command interpreters.',
                    'tactics': ['TA0002'],
                    'platforms': ['Windows', 'Linux', 'macOS'],
                    'mitigations': ['M1038']
                },
                {
                    'id': 'T1486',
                    'name': 'Data Encrypted for Impact',
                    'description': 'Adversaries may encrypt data on target systems.',
                    'tactics': ['TA0040'],
                    'platforms': ['Windows', 'Linux'],
                    'mitigations': ['M1040']
                }
            ],
            'groups': [
                {
                    'id': 'G0016',
                    'name': 'APT29',
                    'description': 'APT29 is a threat group.',
                    'aliases': ['Cozy Bear'],
                    'techniques': ['T1566', 'T1059']
                }
            ],
            'mitigations': [
                {
                    'id': 'M1031',
                    'name': 'Network Intrusion Prevention',
                    'description': 'Use intrusion detection signatures.',
                    'techniques': ['T1566']
                }
            ]
        }
        
        mock_loader.get_cached_data.return_value = sample_data
        return mock_loader
    
    @pytest.fixture
    def mcp_server(self, mock_data_loader):
        """Create MCP server with mock data loader."""
        return create_mcp_server(mock_data_loader)
    
    @pytest.mark.asyncio
    async def test_build_attack_path_basic(self, mcp_server):
        """Test basic attack path construction from Initial Access to Impact."""
        # Execute the tool with default parameters
        result, _ = await mcp_server.call_tool('build_attack_path', {})
        
        # Verify result structure
        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        
        # Verify content contains expected elements
        content = result[0].text
        assert "ATTACK PATH ANALYSIS" in content
        assert "TA0001" in content  # Initial Access
        assert "TA0040" in content  # Impact
        assert "Step 1:" in content
        assert "Initial Access" in content
        assert "Impact" in content
    
    @pytest.mark.asyncio
    async def test_build_attack_path_custom_range(self, mcp_server):
        """Test attack path with custom start and end tactics."""
        # Execute with custom range
        result, _ = await mcp_server.call_tool('build_attack_path', {
            'start_tactic': 'TA0001',
            'end_tactic': 'TA0002'
        })
        
        assert result is not None
        assert len(result) > 0
        
        content = result[0].text
        assert "TA0001 → TA0002" in content
        assert "Initial Access" in content
        assert "Execution" in content
        # Should not contain Impact since we're stopping at Execution
        assert "Step 1:" in content
        assert "Step 2:" in content
    
    @pytest.mark.asyncio
    async def test_build_attack_path_group_filter(self, mcp_server):
        """Test attack path filtered by threat group."""
        # Execute with group filter
        result, _ = await mcp_server.call_tool('build_attack_path', {'group_id': 'G0016'})
        
        assert result is not None
        assert len(result) > 0
        
        content = result[0].text
        assert "Group Filter: G0016" in content
        assert "APT29" in content
        # Should only show techniques used by APT29
        assert "T1566" in content or "T1059" in content
    
    @pytest.mark.asyncio
    async def test_build_attack_path_platform_filter(self, mcp_server):
        """Test attack path filtered by platform."""
        # Execute with platform filter
        result, _ = await mcp_server.call_tool('build_attack_path', {'platform': 'Windows'})
        
        assert result is not None
        assert len(result) > 0
        
        content = result[0].text
        assert "Platform Filter: Windows" in content
        # Should show techniques available on Windows
        assert "Platforms: " in content
    
    @pytest.mark.asyncio
    async def test_build_attack_path_invalid_start_tactic(self, mcp_server):
        """Test error handling for invalid start tactic."""
        # Execute with invalid start tactic
        result, _ = await mcp_server.call_tool('build_attack_path', {'start_tactic': 'TA9999'})
        
        assert result is not None
        assert len(result) > 0
        
        content = result[0].text
        assert "Invalid start tactic" in content
        assert "TA9999" in content
    
    @pytest.mark.asyncio
    async def test_build_attack_path_invalid_end_tactic(self, mcp_server):
        """Test error handling for invalid end tactic."""
        # Execute with invalid end tactic
        result, _ = await mcp_server.call_tool('build_attack_path', {'end_tactic': 'TA9999'})
        
        assert result is not None
        assert len(result) > 0
        
        content = result[0].text
        assert "Invalid end tactic" in content
        assert "TA9999" in content
    
    @pytest.mark.asyncio
    async def test_build_attack_path_reverse_order(self, mcp_server):
        """Test error handling when start tactic comes after end tactic."""
        # Execute with reversed order (Impact before Initial Access)
        result, _ = await mcp_server.call_tool('build_attack_path', {
            'start_tactic': 'TA0040',
            'end_tactic': 'TA0001'
        })
        
        assert result is not None
        assert len(result) > 0
        
        content = result[0].text
        assert "comes after" in content
        assert "kill chain" in content
    
    @pytest.mark.asyncio
    async def test_build_attack_path_invalid_group(self, mcp_server):
        """Test error handling for invalid group ID."""
        # Execute with invalid group
        result, _ = await mcp_server.call_tool('build_attack_path', {'group_id': 'G9999'})
        
        assert result is not None
        assert len(result) > 0
        
        content = result[0].text
        assert "Group 'G9999' not found" in content
    
    @pytest.mark.asyncio
    async def test_build_attack_path_no_data_loader(self):
        """Test error handling when data loader is not available."""
        # Create server without data loader
        server = create_mcp_server(None)
        
        result, _ = await server.call_tool('build_attack_path', {})
        
        assert result is not None
        assert len(result) > 0
        
        content = result[0].text
        assert "Data loader not available" in content
    
    @pytest.mark.asyncio
    async def test_build_attack_path_no_cached_data(self, mcp_server):
        """Test error handling when cached data is not available."""
        # Mock data loader to return None for cached data
        mcp_server.data_loader.get_cached_data.return_value = None
        
        result, _ = await mcp_server.call_tool('build_attack_path', {})
        
        assert result is not None
        assert len(result) > 0
        
        content = result[0].text
        assert "MITRE ATT&CK data not loaded" in content
    
    @pytest.mark.asyncio
    async def test_build_attack_path_summary_section(self, mcp_server):
        """Test that attack path includes summary section with statistics."""
        result, _ = await mcp_server.call_tool('build_attack_path', {})
        
        assert result is not None
        assert len(result) > 0
        
        content = result[0].text
        assert "ATTACK PATH SUMMARY" in content
        assert "Total Tactics:" in content
        assert "Total Available Techniques:" in content
        assert "kill chain methodology" in content
        
        content = result[0].text
        assert "ATTACK PATH SUMMARY" in content
        assert "Total Tactics:" in content
        assert "Total Available Techniques:" in content
        assert "kill chain methodology" in content
    
    @pytest.mark.asyncio
    async def test_build_attack_path_technique_limiting(self, mcp_server):
        """Test that techniques are limited to top 5 per tactic for readability."""
        # Create mock data with many techniques for one tactic
        mock_loader = Mock(spec=DataLoader)
        
        # Create 7 techniques for Initial Access to test limiting
        techniques = []
        for i in range(7):
            techniques.append({
                'id': f'T{1000 + i}',
                'name': f'Test Technique {i + 1}',
                'description': f'Test technique {i + 1} description.',
                'tactics': ['TA0001'],
                'platforms': ['Windows'],
                'mitigations': []
            })
        
        sample_data = {
            'tactics': [
                {
                    'id': 'TA0001',
                    'name': 'Initial Access',
                    'description': 'The adversary is trying to get into your network.'
                }
            ],
            'techniques': techniques,
            'groups': [],
            'mitigations': []
        }
        
        mock_loader.get_cached_data.return_value = sample_data
        server = create_mcp_server(mock_loader)
        
        result, _ = await server.call_tool('build_attack_path', {
            'start_tactic': 'TA0001',
            'end_tactic': 'TA0001'
        })
        
        content = result[0].text
        # Should show "... and 2 more techniques" since we limit to 5
        assert "and 2 more techniques" in content
        # Should show techniques 1-5
        assert "1. T1000:" in content
        assert "5. T1004:" in content
