"""
Task 14: Integration testing with all MCP tools.

This module provides comprehensive integration tests for all 8 MCP tools
with the refactored STIX2 library-based parser.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

from src.data_loader import DataLoader
from src.mcp_server import create_mcp_server
from src.parsers.stix_parser import STIXParser

# Configure logging for integration tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestTask14Integration:
    """Integration tests for all MCP tools with refactored parser."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.data_loader = DataLoader()
        self.parser = STIXParser()
        
        # Create test data that mimics real MITRE ATT&CK structure
        self.test_data = {
            "techniques": [
                {
                    "id": "T1055",
                    "name": "Process Injection",
                    "description": "Adversaries may inject code into processes to evade defenses.",
                    "tactics": ["TA0004", "TA0005"],
                    "platforms": ["Windows", "macOS", "Linux"],
                    "mitigations": ["M1040", "M1026"],
                    "data_sources": ["Process: Process Creation", "Process: OS API Execution"],
                    "detection": "Monitor for process injection techniques."
                },
                {
                    "id": "T1059",
                    "name": "Command and Scripting Interpreter",
                    "description": "Adversaries may abuse command interpreters to execute commands.",
                    "tactics": ["TA0002"],
                    "platforms": ["Windows", "Linux", "macOS"],
                    "mitigations": ["M1038", "M1042"],
                    "data_sources": ["Command: Command Execution", "Process: Process Creation"]
                },
                {
                    "id": "T1190",
                    "name": "Exploit Public-Facing Application",
                    "description": "Adversaries may exploit public-facing applications.",
                    "tactics": ["TA0001"],
                    "platforms": ["Windows", "Linux", "macOS"],
                    "mitigations": ["M1048", "M1030"],
                    "data_sources": ["Application Log: Application Log Content", "Network Traffic: Network Traffic Content"]
                }
            ],
            "tactics": [
                {
                    "id": "TA0001",
                    "name": "Initial Access",
                    "description": "Adversaries are trying to get into your network."
                },
                {
                    "id": "TA0002",
                    "name": "Execution",
                    "description": "Adversaries are trying to run malicious code."
                },
                {
                    "id": "TA0004",
                    "name": "Privilege Escalation",
                    "description": "Adversaries are trying to gain higher-level permissions."
                },
                {
                    "id": "TA0005",
                    "name": "Defense Evasion",
                    "description": "Adversaries are trying to avoid being detected."
                },
                {
                    "id": "TA0040",
                    "name": "Impact",
                    "description": "Adversaries are trying to manipulate, interrupt, or destroy your systems."
                }
            ],
            "groups": [
                {
                    "id": "G0016",
                    "name": "APT29",
                    "description": "APT29 is a sophisticated threat group.",
                    "aliases": ["APT29", "Cozy Bear", "The Dukes"],
                    "techniques": ["T1055", "T1059", "T1190"]
                },
                {
                    "id": "G0032",
                    "name": "Lazarus Group",
                    "description": "Lazarus Group is a North Korean state-sponsored group.",
                    "aliases": ["Lazarus Group", "HIDDEN COBRA", "Zinc"],
                    "techniques": ["T1055", "T1190"]
                }
            ],
            "mitigations": [
                {
                    "id": "M1040",
                    "name": "Behavior Prevention on Endpoint",
                    "description": "Use capabilities to prevent suspicious behavior patterns."
                },
                {
                    "id": "M1026",
                    "name": "Privileged Account Management",
                    "description": "Manage the creation, modification, use, and permissions associated with privileged accounts."
                },
                {
                    "id": "M1038",
                    "name": "Execution Prevention",
                    "description": "Block execution of code on a system through application control."
                },
                {
                    "id": "M1042",
                    "name": "Disable or Remove Feature or Program",
                    "description": "Remove or deny access to unnecessary features or programs."
                },
                {
                    "id": "M1048",
                    "name": "Application Isolation and Sandboxing",
                    "description": "Restrict execution of code to virtual environments."
                },
                {
                    "id": "M1030",
                    "name": "Network Segmentation",
                    "description": "Architect network security to separate networks and functions."
                }
            ],
            "relationships": [
                {
                    "relationship_type": "uses",
                    "source_ref": "intrusion-set--g0016-stix-id",
                    "target_ref": "attack-pattern--t1055-stix-id"
                },
                {
                    "relationship_type": "uses",
                    "source_ref": "intrusion-set--g0032-stix-id", 
                    "target_ref": "attack-pattern--t1055-stix-id"
                },
                {
                    "relationship_type": "mitigates",
                    "source_ref": "course-of-action--m1040-stix-id",
                    "target_ref": "attack-pattern--t1055-stix-id"
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_search_attack_tool(self):
        """Test the search_attack MCP tool with various queries."""
        logger.info("Testing search_attack tool...")
        
        # Mock the data loader
        with patch.object(self.data_loader, 'get_cached_data', return_value=self.test_data):
            # Create MCP server
            mcp_server = create_mcp_server(self.data_loader)
            
            # Test various search queries
            test_queries = [
                "injection",
                "T1055",
                "APT29",
                "Initial Access",
                "process",
                "nonexistent_term"
            ]
            
            for query in test_queries:
                logger.info(f"Testing search query: '{query}'")
                
                # Call the search_attack tool 
                result = await mcp_server.call_tool("search_attack", {"query": query})
                
                # MCP server returns tuple of (result_list, metadata_dict)
                assert isinstance(result, tuple), f"Expected tuple result for query '{query}'"
                assert len(result) == 2, f"Expected tuple with 2 elements for query '{query}'"
                
                search_results, metadata = result
                assert isinstance(search_results, list), f"Expected list result for query '{query}'"
                assert len(search_results) > 0, f"Expected non-empty results for query '{query}'"
                
                # Verify content structure
                content = search_results[0]
                assert hasattr(content, 'text'), f"Expected text content for query '{query}'"
                assert isinstance(content.text, str), f"Expected string text for query '{query}'"
                
                # Log results for verification
                logger.info(f"Query '{query}' returned {len(content.text)} characters")
                
                # Special verification for specific queries
                if query == "T1055":
                    assert "T1055" in content.text, "T1055 should be found in technique search"
                    assert "Process Injection" in content.text, "Technique name should be included"
                elif query == "APT29":
                    assert "G0016" in content.text, "Group ID should be found in group search"
                elif query == "nonexistent_term":
                    assert "No results found" in content.text, "Should return no results message"

    @pytest.mark.asyncio
    async def test_get_technique_tool(self):
        """Test the get_technique MCP tool with various technique IDs."""
        logger.info("Testing get_technique tool...")
        
        with patch.object(self.data_loader, 'get_cached_data', return_value=self.test_data):
            mcp_server = create_mcp_server(self.data_loader)
            
            # Test valid technique IDs
            valid_technique_ids = ["T1055", "T1059", "T1190"]
            
            for technique_id in valid_technique_ids:
                logger.info(f"Testing technique: {technique_id}")
                
                result = await mcp_server.call_tool("get_technique", {"technique_id": technique_id})
                
                # MCP server returns tuple of (result_list, metadata_dict)
                assert isinstance(result, tuple), f"Expected tuple result for technique {technique_id}"
                assert len(result) == 2, f"Expected tuple with 2 elements for technique {technique_id}"
                
                technique_info, metadata = result
                assert isinstance(technique_info, list), f"Expected list result for technique {technique_id}"
                assert len(technique_info) > 0, f"Expected non-empty results for technique {technique_id}"
                
                content = technique_info[0]
                assert hasattr(content, 'text'), f"Expected text content for technique {technique_id}"
                
                # Verify technique details are included
                text = content.text
                assert technique_id in text, f"Technique ID should be in response for {technique_id}"
                assert "TECHNIQUE DETAILS" in text, f"Should include technique details header for {technique_id}"
                assert "Description:" in text, f"Should include description for {technique_id}"
                assert "Associated Tactics" in text, f"Should include tactics for {technique_id}"
                assert "Platforms" in text, f"Should include platforms for {technique_id}"
                assert "Mitigations" in text, f"Should include mitigations for {technique_id}"
                
                logger.info(f"Technique {technique_id} details verified successfully")
            
            # Test invalid technique ID
            result = await mcp_server.call_tool("get_technique", {"technique_id": "T9999"})
            
            # MCP server returns tuple of (result_list, metadata_dict)
            assert isinstance(result, tuple), f"Expected tuple result for invalid technique"
            assert len(result) == 2, f"Expected tuple with 2 elements for invalid technique"
            
            error_info, metadata = result
            assert "not found" in error_info[0].text, "Should indicate technique not found"

    @pytest.mark.asyncio
    async def test_list_tactics_tool(self):
        """Test the list_tactics MCP tool."""
        logger.info("Testing list_tactics tool...")
        
        with patch.object(self.data_loader, 'get_cached_data', return_value=self.test_data):
            mcp_server = create_mcp_server(self.data_loader)
            
            result = await mcp_server.call_tool("list_tactics", {})
            
            # MCP server returns tuple of (result_list, metadata_dict)
            assert isinstance(result, tuple), f"Expected tuple result for list_tactics"
            assert len(result) == 2, f"Expected tuple with 2 elements for list_tactics"
            
            tactics_list, metadata = result
            assert isinstance(tactics_list, list), "Expected list result from list_tactics"
            assert len(tactics_list) > 0, "Expected non-empty tactics list"
            
            content = tactics_list[0]
            assert hasattr(content, 'text'), "Expected text content from list_tactics"
            
            text = content.text
            assert "MITRE ATT&CK TACTICS" in text, "Should include tactics header"
            assert "Total tactics:" in text, "Should include tactics count"
            
            # Verify all test tactics are included
            for tactic_id in ["TA0001", "TA0002", "TA0004", "TA0005", "TA0040"]:
                assert tactic_id in text, f"Tactic {tactic_id} should be listed"
            
            logger.info("list_tactics tool verified successfully")

    @pytest.mark.asyncio
    async def test_get_group_techniques_tool(self):
        """Test the get_group_techniques MCP tool."""
        logger.info("Testing get_group_techniques tool...")
        
        with patch.object(self.data_loader, 'get_cached_data', return_value=self.test_data):
            mcp_server = create_mcp_server(self.data_loader)
            
            # Test valid group IDs
            valid_group_ids = ["G0016", "G0032"]
            
            for group_id in valid_group_ids:
                logger.info(f"Testing group: {group_id}")
                
                result = await mcp_server.call_tool("get_group_techniques", {"group_id": group_id})
                
                # MCP server returns tuple of (result_list, metadata_dict)
                assert isinstance(result, tuple), f"Expected tuple result for group {group_id}"
                assert len(result) == 2, f"Expected tuple with 2 elements for group {group_id}"
                
                group_info, metadata = result
                assert isinstance(group_info, list), f"Expected list result for group {group_id}"
                assert len(group_info) > 0, f"Expected non-empty results for group {group_id}"
                
                content = group_info[0]
                text = content.text
                
                assert "GROUP TECHNIQUES" in text, f"Should include group techniques header for {group_id}"
                assert group_id in text, f"Group ID should be in response for {group_id}"
                assert "Techniques Used" in text, f"Should include techniques section for {group_id}"
                
                # Verify some techniques are listed
                if group_id == "G0016":
                    assert "T1055" in text, "APT29 should use T1055"
                    assert "T1059" in text, "APT29 should use T1059"
                    assert "T1190" in text, "APT29 should use T1190"
                elif group_id == "G0032":
                    assert "T1055" in text, "Lazarus Group should use T1055"
                    assert "T1190" in text, "Lazarus Group should use T1190"
                
                logger.info(f"Group {group_id} techniques verified successfully")
            
            # Test invalid group ID
            result = await mcp_server.call_tool("get_group_techniques", {"group_id": "G9999"})
            
            # MCP server returns tuple of (result_list, metadata_dict)
            assert isinstance(result, tuple), f"Expected tuple result for invalid group"
            assert len(result) == 2, f"Expected tuple with 2 elements for invalid group"
            
            error_info, metadata = result
            assert "not found" in error_info[0].text, "Should indicate group not found"

    @pytest.mark.asyncio
    async def test_get_technique_mitigations_tool(self):
        """Test the get_technique_mitigations MCP tool."""
        logger.info("Testing get_technique_mitigations tool...")
        
        with patch.object(self.data_loader, 'get_cached_data', return_value=self.test_data):
            mcp_server = create_mcp_server(self.data_loader)
            
            # Test techniques with mitigations
            test_techniques = ["T1055", "T1059", "T1190"]
            
            for technique_id in test_techniques:
                logger.info(f"Testing mitigations for technique: {technique_id}")
                
                result = await mcp_server.call_tool("get_technique_mitigations", {"technique_id": technique_id})
                
                # MCP server returns tuple of (result_list, metadata_dict)
                assert isinstance(result, tuple), f"Expected tuple result for technique {technique_id}"
                assert len(result) == 2, f"Expected tuple with 2 elements for technique {technique_id}"
                
                mitigation_info, metadata = result
                assert isinstance(mitigation_info, list), f"Expected list result for technique {technique_id}"
                assert len(mitigation_info) > 0, f"Expected non-empty results for technique {technique_id}"
                
                content = mitigation_info[0]
                text = content.text
                
                assert "TECHNIQUE MITIGATIONS" in text, f"Should include mitigations header for {technique_id}"
                assert technique_id in text, f"Technique ID should be in response for {technique_id}"
                assert "Mitigations" in text, f"Should include mitigations section for {technique_id}"
                
                # Verify specific mitigations based on test data
                if technique_id == "T1055":
                    assert "M1040" in text, "T1055 should have M1040 mitigation"
                    assert "M1026" in text, "T1055 should have M1026 mitigation"
                elif technique_id == "T1059":
                    assert "M1038" in text, "T1059 should have M1038 mitigation"
                    assert "M1042" in text, "T1059 should have M1042 mitigation"
                
                logger.info(f"Technique {technique_id} mitigations verified successfully")

    @pytest.mark.asyncio
    async def test_build_attack_path_tool(self):
        """Test the build_attack_path MCP tool."""
        logger.info("Testing build_attack_path tool...")
        
        with patch.object(self.data_loader, 'get_cached_data', return_value=self.test_data):
            mcp_server = create_mcp_server(self.data_loader)
            
            # Test basic attack path
            result = await mcp_server.call_tool("build_attack_path", {
                "start_tactic": "TA0001",
                "end_tactic": "TA0005"
            })
            
            # MCP server returns tuple of (result_list, metadata_dict)
            assert isinstance(result, tuple), f"Expected tuple result for build_attack_path"
            assert len(result) == 2, f"Expected tuple with 2 elements for build_attack_path"
            
            path_info, metadata = result
            assert isinstance(path_info, list), "Expected list result from build_attack_path"
            assert len(path_info) > 0, "Expected non-empty path results"
            
            content = path_info[0]
            text = content.text
            
            assert "ATTACK PATH CONSTRUCTION" in text, "Should include attack path header"
            assert "Path Configuration:" in text, "Should include path configuration"
            assert "TA0001" in text, "Should include start tactic"
            assert "TA0005" in text, "Should include end tactic"
            assert "ATTACK PATH SUMMARY" in text, "Should include path summary"
            
            logger.info("Basic attack path verified successfully")
            
            # Test attack path with group filter
            result = await mcp_server.call_tool("build_attack_path", {
                "start_tactic": "TA0001",
                "end_tactic": "TA0004",
                "group_id": "G0016"
            })
            
            # MCP server returns tuple of (result_list, metadata_dict)
            assert isinstance(result, tuple), f"Expected tuple result for filtered build_attack_path"
            assert len(result) == 2, f"Expected tuple with 2 elements for filtered build_attack_path"
            
            filtered_path_info, metadata = result
            content = filtered_path_info[0]
            text = content.text
            
            assert "Group Filter: G0016" in text, "Should include group filter information"
            logger.info("Filtered attack path verified successfully")

    @pytest.mark.asyncio
    async def test_analyze_coverage_gaps_tool(self):
        """Test the analyze_coverage_gaps MCP tool."""
        logger.info("Testing analyze_coverage_gaps tool...")
        
        with patch.object(self.data_loader, 'get_cached_data', return_value=self.test_data):
            mcp_server = create_mcp_server(self.data_loader)
            
            # Test coverage analysis with threat groups
            result = await mcp_server.call_tool("analyze_coverage_gaps", {
                "threat_groups": ["G0016", "G0032"]
            })
            
            # MCP server returns tuple of (result_list, metadata_dict)
            assert isinstance(result, tuple), f"Expected tuple result for analyze_coverage_gaps"
            assert len(result) == 2, f"Expected tuple with 2 elements for analyze_coverage_gaps"
            
            coverage_info, metadata = result
            assert isinstance(coverage_info, list), "Expected list result from analyze_coverage_gaps"
            assert len(coverage_info) > 0, "Expected non-empty coverage results"
            
            content = coverage_info[0]
            text = content.text
            
            assert "COVERAGE GAP ANALYSIS" in text, "Should include coverage analysis header"
            assert "Threat Groups Analyzed:" in text, "Should include analyzed groups"
            assert "COVERAGE STATISTICS" in text, "Should include coverage statistics"
            assert "G0016" in text, "Should include G0016 in analysis"
            assert "G0032" in text, "Should include G0032 in analysis"
            
            logger.info("Coverage gap analysis with threat groups verified successfully")
            
            # Test coverage analysis with specific techniques
            result = await mcp_server.call_tool("analyze_coverage_gaps", {
                "technique_list": ["T1055", "T1059"]
            })
            
            # MCP server returns tuple of (result_list, metadata_dict)
            assert isinstance(result, tuple), f"Expected tuple result for technique coverage analysis"
            assert len(result) == 2, f"Expected tuple with 2 elements for technique coverage analysis"
            
            technique_coverage_info, metadata = result
            content = technique_coverage_info[0]
            text = content.text
            
            assert "Specific Techniques:" in text, "Should include specific techniques"
            assert "T1055" in text, "Should include T1055 in analysis"
            assert "T1059" in text, "Should include T1059 in analysis"
            
            logger.info("Coverage gap analysis with techniques verified successfully")

    @pytest.mark.asyncio
    async def test_detect_technique_relationships_tool(self):
        """Test the detect_technique_relationships MCP tool."""
        logger.info("Testing detect_technique_relationships tool...")
        
        # Create enhanced test data with STIX IDs for relationships
        enhanced_data = self.test_data.copy()
        
        # Mock the download_data method to return raw STIX data
        mock_raw_data = {
            "objects": [
                {
                    "id": "attack-pattern--t1055-stix-id",
                    "type": "attack-pattern",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "T1055"}
                    ],
                    "name": "Process Injection"
                },
                {
                    "id": "intrusion-set--g0016-stix-id",
                    "type": "intrusion-set",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "G0016"}
                    ],
                    "name": "APT29"
                },
                {
                    "id": "course-of-action--m1040-stix-id",
                    "type": "course-of-action",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "M1040"}
                    ],
                    "name": "Behavior Prevention on Endpoint"
                }
            ]
        }
        
        with patch.object(self.data_loader, 'get_cached_data', return_value=enhanced_data), \
             patch.object(self.data_loader, 'download_data', return_value=mock_raw_data):
            
            mcp_server = create_mcp_server(self.data_loader)
            
            # Test relationship detection for T1055
            result = await mcp_server.call_tool("detect_technique_relationships", {
                "technique_id": "T1055",
                "relationship_types": ["uses", "mitigates"],
                "depth": 2
            })
            
            # MCP server returns tuple of (result_list, metadata_dict)
            assert isinstance(result, tuple), f"Expected tuple result for detect_technique_relationships"
            assert len(result) == 2, f"Expected tuple with 2 elements for detect_technique_relationships"
            
            relationship_info, metadata = result
            assert isinstance(relationship_info, list), "Expected list result from detect_technique_relationships"
            assert len(relationship_info) > 0, "Expected non-empty relationship results"
            
            content = relationship_info[0]
            text = content.text
            
            assert "TECHNIQUE RELATIONSHIP ANALYSIS" in text, "Should include relationship analysis header"
            assert "Primary Technique: T1055" in text, "Should include primary technique"
            assert "Analysis Depth:" in text, "Should include analysis depth"
            assert "Relationship Types:" in text, "Should include relationship types"
            
            logger.info("Technique relationship analysis verified successfully")

    @pytest.mark.asyncio
    async def test_all_tools_error_handling(self):
        """Test error handling for all MCP tools."""
        logger.info("Testing error handling for all MCP tools...")
        
        # Test with no data loader
        mcp_server = create_mcp_server(None)
        
        tools_to_test = [
            ("search_attack", {"query": "test"}),
            ("get_technique", {"technique_id": "T1055"}),
            ("list_tactics", {}),
            ("get_group_techniques", {"group_id": "G0016"}),
            ("get_technique_mitigations", {"technique_id": "T1055"}),
            ("build_attack_path", {"start_tactic": "TA0001", "end_tactic": "TA0005"}),
            ("analyze_coverage_gaps", {"threat_groups": ["G0016"]}),
            ("detect_technique_relationships", {"technique_id": "T1055"})
        ]
        
        for tool_name, params in tools_to_test:
            logger.info(f"Testing error handling for {tool_name}")
            
            result = await mcp_server.call_tool(tool_name, params)
            
            # MCP server returns tuple of (result_list, metadata_dict)
            assert isinstance(result, tuple), f"Expected tuple result for {tool_name}"
            assert len(result) == 2, f"Expected tuple with 2 elements for {tool_name}"
            
            tool_result, metadata = result
            assert isinstance(tool_result, list), f"Should return list for {tool_name}"
            assert len(tool_result) > 0, f"Should return non-empty result for {tool_name}"
            
            content = tool_result[0]
            text = content.text
            
            assert "Error: Data loader not available" in text, f"Should indicate data loader error for {tool_name}"
            
            logger.info(f"Error handling for {tool_name} verified successfully")

    @pytest.mark.asyncio
    async def test_tools_with_empty_data(self):
        """Test all tools with empty data scenarios."""
        logger.info("Testing all tools with empty data...")
        
        empty_data = {
            "techniques": [],
            "tactics": [],
            "groups": [],
            "mitigations": [],
            "relationships": []
        }
        
        with patch.object(self.data_loader, 'get_cached_data', return_value=empty_data):
            mcp_server = create_mcp_server(self.data_loader)
            
            # Test search_attack with empty data
            result = await mcp_server.call_tool("search_attack", {"query": "test"})
            
            # MCP server returns tuple of (result_list, metadata_dict)
            assert isinstance(result, tuple), f"Expected tuple result for search with empty data"
            assert len(result) == 2, f"Expected tuple with 2 elements for search with empty data"
            
            search_result, metadata = result
            assert "No results found" in search_result[0].text, "Should indicate no results"
            
            # Test list_tactics with empty data
            result = await mcp_server.call_tool("list_tactics", {})
            
            # MCP server returns tuple of (result_list, metadata_dict)
            assert isinstance(result, tuple), f"Expected tuple result for tactics with empty data"
            assert len(result) == 2, f"Expected tuple with 2 elements for tactics with empty data"
            
            tactics_result, metadata = result
            assert "No tactics found" in tactics_result[0].text, "Should indicate no tactics"
            
            logger.info("Empty data handling verified successfully")

    @pytest.mark.asyncio
    async def test_mcp_server_integration_end_to_end(self):
        """Test complete end-to-end integration of MCP server with all tools."""
        logger.info("Testing complete end-to-end MCP server integration...")
        
        with patch.object(self.data_loader, 'get_cached_data', return_value=self.test_data):
            mcp_server = create_mcp_server(self.data_loader)
            
            # Simulate a complete threat analysis workflow
            workflow_steps = [
                # Step 1: Search for techniques related to process injection
                ("search_attack", {"query": "process injection"}),
                
                # Step 2: Get detailed info about T1055
                ("get_technique", {"technique_id": "T1055"}),
                
                # Step 3: Find which groups use T1055
                ("get_group_techniques", {"group_id": "G0016"}),
                
                # Step 4: Get mitigations for T1055
                ("get_technique_mitigations", {"technique_id": "T1055"}),
                
                # Step 5: Build attack path from Initial Access to Defense Evasion
                ("build_attack_path", {"start_tactic": "TA0001", "end_tactic": "TA0005"}),
                
                # Step 6: Analyze coverage gaps for APT29
                ("analyze_coverage_gaps", {"threat_groups": ["G0016"]}),
                
                # Step 7: Analyze relationships for T1055
                ("detect_technique_relationships", {"technique_id": "T1055", "depth": 1})
            ]
            
            workflow_results = []
            
            for step_num, (tool_name, params) in enumerate(workflow_steps, 1):
                logger.info(f"Executing workflow step {step_num}: {tool_name}")
                
                result = await mcp_server.call_tool(tool_name, params)
                
                # MCP server returns tuple of (result_list, metadata_dict)
                assert isinstance(result, tuple), f"Expected tuple result for workflow step {step_num} ({tool_name})"
                assert len(result) == 2, f"Expected tuple with 2 elements for workflow step {step_num} ({tool_name})"
                
                tool_result, metadata = result
                assert isinstance(tool_result, list), f"Step {step_num} should return list"
                assert len(tool_result) > 0, f"Step {step_num} should return non-empty result"
                
                content = tool_result[0]
                assert hasattr(content, 'text'), f"Step {step_num} should return text content"
                assert len(content.text) > 0, f"Step {step_num} should return non-empty text"
                
                workflow_results.append({
                    "step": step_num,
                    "tool": tool_name,
                    "params": params,
                    "result_length": len(content.text),
                    "success": True
                })
                
                logger.info(f"Step {step_num} completed successfully - {len(content.text)} characters returned")
            
            # Verify workflow completion
            assert len(workflow_results) == len(workflow_steps), "All workflow steps should complete"
            
            successful_steps = [r for r in workflow_results if r["success"]]
            assert len(successful_steps) == len(workflow_steps), "All workflow steps should succeed"
            
            total_output = sum(r["result_length"] for r in workflow_results)
            logger.info(f"Complete workflow generated {total_output} characters of output across {len(workflow_steps)} steps")
            
            # Log workflow summary
            logger.info("End-to-end workflow summary:")
            for result in workflow_results:
                logger.info(f"  Step {result['step']}: {result['tool']} - {result['result_length']} chars")
            
            logger.info("Complete end-to-end integration test verified successfully")

    @pytest.mark.asyncio
    async def test_all_integration_tests_suite(self):
        """Run all integration tests in sequence."""
        logger.info("Starting comprehensive Task 14 integration test suite...")
        
        # Run all individual tool tests
        await self.test_search_attack_tool()
        await self.test_get_technique_tool()
        await self.test_list_tactics_tool()
        await self.test_get_group_techniques_tool()
        await self.test_get_technique_mitigations_tool()
        await self.test_build_attack_path_tool()
        await self.test_analyze_coverage_gaps_tool()
        await self.test_detect_technique_relationships_tool()
        
        # Run error handling tests
        await self.test_all_tools_error_handling()
        await self.test_tools_with_empty_data()
        
        # Run end-to-end integration test
        await self.test_mcp_server_integration_end_to_end()
        
        logger.info("Task 14 integration test suite completed successfully!")


# Additional HTTP proxy integration tests
class TestHTTPProxyIntegration:
    """Test HTTP proxy functionality with refactored backend."""
    
    def setup_method(self):
        """Set up HTTP proxy test fixtures."""
        self.data_loader = DataLoader()
        self.test_data = {
            "techniques": [
                {
                    "id": "T1055",
                    "name": "Process Injection",
                    "description": "Test technique for HTTP proxy testing.",
                    "tactics": ["TA0004"],
                    "platforms": ["Windows"],
                    "mitigations": ["M1040"]
                }
            ],
            "tactics": [
                {
                    "id": "TA0004",
                    "name": "Privilege Escalation",
                    "description": "Test tactic for HTTP proxy testing."
                }
            ],
            "groups": [],
            "mitigations": [
                {
                    "id": "M1040",  
                    "name": "Behavior Prevention on Endpoint",
                    "description": "Test mitigation for HTTP proxy testing."
                }
            ],
            "relationships": []
        }

    def test_http_proxy_creation(self):
        """Test HTTP proxy can be created with refactored MCP server."""
        logger.info("Testing HTTP proxy creation...")
        
        with patch.object(self.data_loader, 'get_cached_data', return_value=self.test_data):
            # Create MCP server with refactored parser
            mcp_server = create_mcp_server(self.data_loader)
            
            # Import and create HTTP proxy
            try:
                from http_proxy import HTTPProxy
                proxy = HTTPProxy(mcp_server)
                
                # Verify proxy has required attributes
                assert hasattr(proxy, 'app'), "HTTP proxy should have app attribute"
                assert hasattr(proxy, 'mcp_server'), "HTTP proxy should have mcp_server attribute"
                
                # Verify routes are configured
                if hasattr(proxy.app, 'router'):
                    routes = [route.resource.canonical for route in proxy.app.router.routes()]
                    expected_routes = ['/', '/tools', '/call_tool']
                    
                    for route in expected_routes:
                        assert route in routes, f"HTTP proxy should have {route} route"
                
                logger.info("HTTP proxy creation verified successfully")
                
            except ImportError:
                logger.warning("HTTP proxy module not available - skipping HTTP proxy tests")
                pytest.skip("HTTP proxy module not available")

    def test_web_interface_compatibility(self):
        """Test that web interface works with refactored backend."""
        logger.info("Testing web interface compatibility...")
        
        with patch.object(self.data_loader, 'get_cached_data', return_value=self.test_data):
            # Create MCP server
            mcp_server = create_mcp_server(self.data_loader)
            
            # Verify MCP server has required interface for web integration
            assert hasattr(mcp_server, 'call_tool'), "MCP server should have call_tool method"
            assert callable(mcp_server.call_tool), "call_tool should be callable"
            
            # Test that server can be called with standard web interface patterns
            # This simulates what the web interface would do
            import asyncio
            
            async def test_web_calls():
                # Test basic tool call pattern used by web interface
                result = await mcp_server.call_tool("search_attack", {"query": "test"})
                
                # MCP server returns tuple of (result_list, metadata_dict)
                assert isinstance(result, tuple), f"Expected tuple result for web interface test"
                assert len(result) == 2, f"Expected tuple with 2 elements for web interface test"
                
                result_data, metadata = result
                assert isinstance(result_data, list), "Should return list of content"
                
                return True
            
            # Run the async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success = loop.run_until_complete(test_web_calls())
                assert success, "Web interface compatibility test should succeed"
            finally:
                loop.close()
            
            logger.info("Web interface compatibility verified successfully")


if __name__ == "__main__":
    # Run the tests directly if executed as script
    pytest.main([__file__, "-v", "--tb=short"])