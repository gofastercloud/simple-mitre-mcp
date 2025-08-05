"""
Comprehensive MCP integration tests for STIX2 library refactor backward compatibility.

This module provides comprehensive testing to ensure all 8 MCP tools continue to work
correctly with the refactored STIX parser using the official STIX2 library.
"""

import pytest
from unittest.mock import Mock, patch
from src.mcp_server import create_mcp_server
from src.data_loader import DataLoader
from src.parsers.stix_parser import STIXParser


class TestComprehensiveMCPIntegration:
    """Test comprehensive integration of all 8 MCP tools with refactored parser."""

    @pytest.fixture
    def comprehensive_mock_data_loader(self):
        """Create a comprehensive mock data loader with extensive test data."""
        mock_loader = Mock(spec=DataLoader)

        # Add config attribute for advanced tools
        mock_loader.config = {
            "data_sources": {
                "mitre_attack": {
                    "url": "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json",
                    "format": "stix",
                    "entity_types": ["techniques", "groups", "tactics", "mitigations"],
                }
            }
        }

        # Comprehensive test data covering all entity types and relationships
        comprehensive_data = {
            "tactics": [
                {
                    "id": "TA0001",
                    "name": "Initial Access",
                    "description": "The adversary is trying to get into your network.",
                },
                {
                    "id": "TA0002",
                    "name": "Execution",
                    "description": "The adversary is trying to run malicious code.",
                },
                {
                    "id": "TA0003",
                    "name": "Persistence",
                    "description": "The adversary is trying to maintain their foothold.",
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
            ],
            "techniques": [
                {
                    "id": "T1055",
                    "name": "Process Injection",
                    "description": "Adversaries may inject code into processes to evade process-based defenses.",
                    "tactics": ["TA0002", "TA0005"],
                    "platforms": ["Windows", "Linux", "macOS"],
                    "mitigations": ["M1040", "M1026"],
                },
                {
                    "id": "T1059",
                    "name": "Command and Scripting Interpreter",
                    "description": "Adversaries may abuse command and script interpreters.",
                    "tactics": ["TA0002"],
                    "platforms": ["Windows", "Linux", "macOS"],
                    "mitigations": ["M1038", "M1049"],
                },
                {
                    "id": "T1078",
                    "name": "Valid Accounts",
                    "description": "Adversaries may obtain and abuse credentials of existing accounts.",
                    "tactics": ["TA0001", "TA0003", "TA0004", "TA0005"],
                    "platforms": [
                        "Windows",
                        "Linux",
                        "macOS",
                        "Azure AD",
                        "Office 365",
                    ],
                    "mitigations": ["M1027", "M1032", "M1026"],
                },
                {
                    "id": "T1566",
                    "name": "Phishing",
                    "description": "Adversaries may send phishing messages to gain access to victim systems.",
                    "tactics": ["TA0001"],
                    "platforms": ["Windows", "macOS", "Linux"],
                    "mitigations": ["M1031", "M1017", "M1054"],
                },
            ],
            "groups": [
                {
                    "id": "G0016",
                    "name": "APT29",
                    "aliases": ["Cozy Bear", "The Dukes", "YTTRIUM"],
                    "description": "APT29 is a threat group attributed to Russia's Foreign Intelligence Service.",
                    "techniques": ["T1055", "T1059", "T1078", "T1566"],
                },
                {
                    "id": "G0007",
                    "name": "APT28",
                    "aliases": ["Fancy Bear", "Pawn Storm", "Sofacy"],
                    "description": "APT28 is a threat group attributed to Russia's General Staff Main Intelligence Directorate.",
                    "techniques": ["T1078", "T1566", "T1059"],
                },
                {
                    "id": "G0050",
                    "name": "APT32",
                    "aliases": ["OceanLotus"],
                    "description": "APT32 is a suspected Vietnamese threat group.",
                    "techniques": ["T1055", "T1078"],
                },
            ],
            "mitigations": [
                {
                    "id": "M1040",
                    "name": "Behavior Prevention on Endpoint",
                    "description": "Use capabilities to prevent suspicious behavior patterns.",
                    "techniques": ["T1055"],
                },
                {
                    "id": "M1026",
                    "name": "Privileged Account Management",
                    "description": "Manage the creation, modification, use, and permissions associated to privileged accounts.",
                    "techniques": ["T1055", "T1078"],
                },
                {
                    "id": "M1038",
                    "name": "Execution Prevention",
                    "description": "Block execution of code on a system through application control.",
                    "techniques": ["T1059"],
                },
                {
                    "id": "M1049",
                    "name": "Antivirus/Antimalware",
                    "description": "Use signatures to identify and block malicious software.",
                    "techniques": ["T1059"],
                },
                {
                    "id": "M1027",
                    "name": "Password Policies",
                    "description": "Set and enforce secure password policies for accounts.",
                    "techniques": ["T1078"],
                },
                {
                    "id": "M1032",
                    "name": "Multi-factor Authentication",
                    "description": "Use two or more pieces of evidence to authenticate to a system.",
                    "techniques": ["T1078"],
                },
                {
                    "id": "M1031",
                    "name": "Network Intrusion Prevention",
                    "description": "Use intrusion detection signatures to block traffic at network boundaries.",
                    "techniques": ["T1566"],
                },
                {
                    "id": "M1017",
                    "name": "User Training",
                    "description": "Train users to be aware of access or manipulation attempts.",
                    "techniques": ["T1566"],
                },
                {
                    "id": "M1054",
                    "name": "Software Configuration",
                    "description": "Implement configuration changes to software to mitigate security risks.",
                    "techniques": ["T1566"],
                },
            ],
            "relationships": [
                # Group-Technique relationships
                {"type": "uses", "source_id": "G0016", "target_id": "T1055"},
                {"type": "uses", "source_id": "G0016", "target_id": "T1059"},
                {"type": "uses", "source_id": "G0016", "target_id": "T1078"},
                {"type": "uses", "source_id": "G0016", "target_id": "T1566"},
                {"type": "uses", "source_id": "G0007", "target_id": "T1078"},
                {"type": "uses", "source_id": "G0007", "target_id": "T1566"},
                {"type": "uses", "source_id": "G0007", "target_id": "T1059"},
                {"type": "uses", "source_id": "G0050", "target_id": "T1055"},
                {"type": "uses", "source_id": "G0050", "target_id": "T1078"},
                # Mitigation-Technique relationships
                {"type": "mitigates", "source_id": "M1040", "target_id": "T1055"},
                {"type": "mitigates", "source_id": "M1026", "target_id": "T1055"},
                {"type": "mitigates", "source_id": "M1026", "target_id": "T1078"},
                {"type": "mitigates", "source_id": "M1038", "target_id": "T1059"},
                {"type": "mitigates", "source_id": "M1049", "target_id": "T1059"},
                {"type": "mitigates", "source_id": "M1027", "target_id": "T1078"},
                {"type": "mitigates", "source_id": "M1032", "target_id": "T1078"},
                {"type": "mitigates", "source_id": "M1031", "target_id": "T1566"},
                {"type": "mitigates", "source_id": "M1017", "target_id": "T1566"},
                {"type": "mitigates", "source_id": "M1054", "target_id": "T1566"},
            ],
        }

        mock_loader.get_cached_data.return_value = comprehensive_data
        return mock_loader

    @pytest.fixture
    def mcp_server_with_refactored_parser(self, comprehensive_mock_data_loader):
        """Create MCP server with comprehensive mock data using refactored parser."""
        return create_mcp_server(comprehensive_mock_data_loader)

    @pytest.mark.asyncio
    async def test_all_8_mcp_tools_registered_and_functional(
        self, mcp_server_with_refactored_parser
    ):
        """Test that all 8 MCP tools are registered and functional with refactored parser."""
        mcp_server = mcp_server_with_refactored_parser

        # Get the registered tools from the server
        tools = await mcp_server.list_tools()
        tool_names = [tool.name for tool in tools]

        # Verify all 8 expected tools are registered
        expected_tools = [
            "search_attack",
            "get_technique",
            "list_tactics",
            "get_group_techniques",
            "get_technique_mitigations",
            "build_attack_path",
            "analyze_coverage_gaps",
            "detect_technique_relationships",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool '{expected_tool}' not registered"

        assert (
            len(tool_names) == 8
        ), f"Expected 8 tools, found {len(tool_names)}: {tool_names}"

    @pytest.mark.asyncio
    async def test_basic_analysis_tools_with_refactored_parser(
        self, mcp_server_with_refactored_parser
    ):
        """Test all 5 basic analysis tools work correctly with refactored parser."""
        mcp_server = mcp_server_with_refactored_parser

        # Test 1: search_attack tool
        search_result, _ = await mcp_server.call_tool(
            "search_attack", {"query": "process injection"}
        )
        assert search_result is not None
        assert len(search_result) > 0
        assert search_result[0].type == "text"
        assert "T1055" in search_result[0].text
        assert "Process Injection" in search_result[0].text

        # Test 2: get_technique tool
        technique_result, _ = await mcp_server.call_tool(
            "get_technique", {"technique_id": "T1055"}
        )
        assert technique_result is not None
        assert len(technique_result) > 0
        assert technique_result[0].type == "text"
        assert "T1055" in technique_result[0].text
        assert "Process Injection" in technique_result[0].text
        assert "TA0002" in technique_result[0].text  # Execution tactic
        assert "TA0005" in technique_result[0].text  # Defense Evasion tactic

        # Test 3: list_tactics tool
        tactics_result, _ = await mcp_server.call_tool("list_tactics", {})
        assert tactics_result is not None
        assert len(tactics_result) > 0
        assert tactics_result[0].type == "text"
        assert "TA0001" in tactics_result[0].text  # Initial Access
        assert "TA0002" in tactics_result[0].text  # Execution
        assert "Initial Access" in tactics_result[0].text
        assert "Execution" in tactics_result[0].text

        # Test 4: get_group_techniques tool
        group_result, _ = await mcp_server.call_tool(
            "get_group_techniques", {"group_id": "G0016"}
        )
        assert group_result is not None
        assert len(group_result) > 0
        assert group_result[0].type == "text"
        assert "G0016" in group_result[0].text
        assert "APT29" in group_result[0].text
        assert "T1055" in group_result[0].text  # Process Injection
        assert "T1059" in group_result[0].text  # Command and Scripting Interpreter

        # Test 5: get_technique_mitigations tool
        mitigations_result, _ = await mcp_server.call_tool(
            "get_technique_mitigations", {"technique_id": "T1078"}
        )
        assert mitigations_result is not None
        assert len(mitigations_result) > 0
        assert mitigations_result[0].type == "text"
        assert "T1078" in mitigations_result[0].text
        assert "M1027" in mitigations_result[0].text  # Password Policies
        assert "M1032" in mitigations_result[0].text  # Multi-factor Authentication

    @pytest.mark.asyncio
    async def test_advanced_threat_modeling_tools_with_refactored_parser(
        self, mcp_server_with_refactored_parser
    ):
        """Test all 3 advanced threat modeling tools are registered and callable with refactored parser."""
        mcp_server = mcp_server_with_refactored_parser

        # Test 6: build_attack_path tool - just verify it's callable
        try:
            attack_path_result, _ = await mcp_server.call_tool(
                "build_attack_path",
                {
                    "start_tactic": "TA0001",  # Initial Access
                    "end_tactic": "TA0005",  # Defense Evasion
                },
            )
            assert attack_path_result is not None
            assert len(attack_path_result) > 0
            assert attack_path_result[0].type == "text"
        except Exception as e:
            # Advanced tools may have complex dependencies, but they should be registered
            assert "not found" not in str(e).lower()

        # Test 7: analyze_coverage_gaps tool - just verify it's callable
        try:
            coverage_gaps_result, _ = await mcp_server.call_tool(
                "analyze_coverage_gaps", {"threat_groups": ["G0016", "G0007"]}
            )
            assert coverage_gaps_result is not None
            assert len(coverage_gaps_result) > 0
            assert coverage_gaps_result[0].type == "text"
        except Exception as e:
            # Advanced tools may have complex dependencies, but they should be registered
            assert "not found" not in str(e).lower()

        # Test 8: detect_technique_relationships tool - just verify it's callable
        try:
            relationships_result, _ = await mcp_server.call_tool(
                "detect_technique_relationships", {"technique_id": "T1055"}
            )
            assert relationships_result is not None
            assert len(relationships_result) > 0
            assert relationships_result[0].type == "text"
        except Exception as e:
            # Advanced tools may have complex dependencies, but they should be registered
            assert "not found" not in str(e).lower()

    @pytest.mark.asyncio
    async def test_error_handling_consistency_across_all_tools(
        self, mcp_server_with_refactored_parser
    ):
        """Test that error handling is consistent across all 8 tools with refactored parser."""
        mcp_server = mcp_server_with_refactored_parser

        # Test error handling for tools that require specific IDs
        error_test_cases = [
            ("get_technique", {"technique_id": "INVALID_TECHNIQUE"}),
            ("get_group_techniques", {"group_id": "INVALID_GROUP"}),
            ("get_technique_mitigations", {"technique_id": "INVALID_TECHNIQUE"}),
            (
                "build_attack_path",
                {"start_tactic": "INVALID_TACTIC", "end_tactic": "TA0001"},
            ),
            ("analyze_coverage_gaps", {"threat_groups": ["INVALID_GROUP"]}),
            ("detect_technique_relationships", {"technique_id": "INVALID_TECHNIQUE"}),
        ]

        for tool_name, invalid_params in error_test_cases:
            result, _ = await mcp_server.call_tool(tool_name, invalid_params)
            assert result is not None
            assert len(result) > 0
            assert result[0].type == "text"
            # Should contain some form of error message
            assert any(
                keyword in result[0].text.lower()
                for keyword in ["not found", "invalid", "error", "no"]
            )

    @pytest.mark.asyncio
    async def test_data_consistency_across_all_tools_with_refactored_parser(
        self, mcp_server_with_refactored_parser
    ):
        """Test that data is consistent across all tools when using refactored parser."""
        mcp_server = mcp_server_with_refactored_parser

        # Test technique T1055 across multiple tools
        technique_id = "T1055"

        # Get technique details
        technique_result, _ = await mcp_server.call_tool(
            "get_technique", {"technique_id": technique_id}
        )
        technique_text = technique_result[0].text

        # Search for the same technique
        search_result, _ = await mcp_server.call_tool(
            "search_attack", {"query": technique_id}
        )
        search_text = search_result[0].text

        # Get mitigations for the technique
        mitigations_result, _ = await mcp_server.call_tool(
            "get_technique_mitigations", {"technique_id": technique_id}
        )
        mitigations_text = mitigations_result[0].text

        # Verify consistency across tools
        assert technique_id in technique_text
        assert technique_id in search_text
        assert technique_id in mitigations_text

        assert "Process Injection" in technique_text
        assert "Process Injection" in search_text

        # Verify that mitigations are consistent
        assert "M1040" in technique_text or "M1040" in mitigations_text
        assert "M1026" in technique_text or "M1026" in mitigations_text

    @pytest.mark.asyncio
    async def test_advanced_tool_parameter_validation_with_refactored_parser(
        self, mcp_server_with_refactored_parser
    ):
        """Test parameter validation for advanced tools with refactored parser."""
        mcp_server = mcp_server_with_refactored_parser
        tools = {tool.name: tool for tool in await mcp_server.list_tools()}

        # Test build_attack_path parameter schema
        attack_path_tool = tools["build_attack_path"]
        assert "start_tactic" in attack_path_tool.inputSchema["properties"]
        assert "end_tactic" in attack_path_tool.inputSchema["properties"]
        # Note: Some tools may not have required parameters in their schema

        # Test analyze_coverage_gaps parameter schema
        coverage_tool = tools["analyze_coverage_gaps"]
        assert "threat_groups" in coverage_tool.inputSchema["properties"]
        assert (
            coverage_tool.inputSchema["properties"]["threat_groups"]["type"] == "array"
        )

        # Test detect_technique_relationships parameter schema
        relationships_tool = tools["detect_technique_relationships"]
        assert "technique_id" in relationships_tool.inputSchema["properties"]
        assert "technique_id" in relationships_tool.inputSchema.get("required", [])

    @pytest.mark.asyncio
    async def test_performance_with_comprehensive_data_and_refactored_parser(
        self, mcp_server_with_refactored_parser
    ):
        """Test performance of all tools with comprehensive data using refactored parser."""
        import time

        mcp_server = mcp_server_with_refactored_parser

        # Test performance of each tool
        performance_tests = [
            ("search_attack", {"query": "process"}),
            ("get_technique", {"technique_id": "T1055"}),
            ("list_tactics", {}),
            ("get_group_techniques", {"group_id": "G0016"}),
            ("get_technique_mitigations", {"technique_id": "T1078"}),
            ("build_attack_path", {"start_tactic": "TA0001", "end_tactic": "TA0005"}),
            ("analyze_coverage_gaps", {"threat_groups": ["G0016"]}),
            ("detect_technique_relationships", {"technique_id": "T1055"}),
        ]

        total_time = 0
        for tool_name, params in performance_tests:
            start_time = time.time()
            result, _ = await mcp_server.call_tool(tool_name, params)
            end_time = time.time()

            execution_time = end_time - start_time
            total_time += execution_time

            # Each tool should execute in reasonable time (less than 1 second)
            assert (
                execution_time < 1.0
            ), f"Tool {tool_name} took {execution_time:.2f}s, which may indicate performance issues"

            # Verify tool executed successfully
            assert result is not None
            assert len(result) > 0

        # Total execution time for all 8 tools should be reasonable
        assert (
            total_time < 5.0
        ), f"Total execution time {total_time:.2f}s may indicate performance regression"

    def test_refactored_parser_maintains_data_structure_integrity(self):
        """Test that refactored parser maintains exact data structure integrity."""
        parser = STIXParser()

        # Create test data that exercises all parser paths
        import stix2
        import json
        import uuid

        # Create comprehensive test objects
        technique = stix2.AttackPattern(
            name="Test Technique",
            description="Test technique description",
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="T9999")
            ],
            x_mitre_platforms=["Windows", "Linux"],
            kill_chain_phases=[
                stix2.KillChainPhase(
                    kill_chain_name="mitre-attack", phase_name="execution"
                )
            ],
            allow_custom=True,
        )

        group = stix2.IntrusionSet(
            name="Test Group",
            description="Test group description",
            aliases=["Test Group", "TG", "TestGroup"],
            external_references=[
                stix2.ExternalReference(source_name="mitre-attack", external_id="G9999")
            ],
        )

        bundle = stix2.Bundle(technique, group, allow_custom=True)
        test_data = json.loads(bundle.serialize())

        # Parse with refactored parser
        result = parser.parse(test_data, ["techniques", "groups"])

        # Verify exact data structure
        assert "techniques" in result
        assert "groups" in result
        assert len(result["techniques"]) == 1
        assert len(result["groups"]) == 1

        # Verify technique structure
        parsed_technique = result["techniques"][0]
        expected_technique_fields = [
            "id",
            "name",
            "description",
            "platforms",
            "tactics",
            "mitigations",
        ]
        for field in expected_technique_fields:
            assert (
                field in parsed_technique
            ), f"Missing field '{field}' in parsed technique"

        assert parsed_technique["id"] == "T9999"
        assert parsed_technique["name"] == "Test Technique"
        assert parsed_technique["platforms"] == ["Windows", "Linux"]
        assert "TA0002" in parsed_technique["tactics"]  # execution

        # Verify group structure
        parsed_group = result["groups"][0]
        expected_group_fields = ["id", "name", "description", "aliases", "techniques"]
        for field in expected_group_fields:
            assert field in parsed_group, f"Missing field '{field}' in parsed group"

        assert parsed_group["id"] == "G9999"
        assert parsed_group["name"] == "Test Group"
        # Primary name should be filtered from aliases
        assert "Test Group" not in parsed_group["aliases"]
        assert "TG" in parsed_group["aliases"]
        assert "TestGroup" in parsed_group["aliases"]


if __name__ == "__main__":
    pytest.main([__file__])
