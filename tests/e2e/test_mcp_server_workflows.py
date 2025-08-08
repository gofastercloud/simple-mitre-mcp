"""
MCP Server workflow integration tests.

This module consolidates MCP server workflow tests that were previously
scattered across different test files, focusing on complete user journeys
and tool integration scenarios.
"""

import pytest
import asyncio
import logging
import time
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

from src.data_loader import DataLoader
from src.mcp_server import create_mcp_server
from src.parsers.stix_parser import STIXParser

# Configure logging for MCP workflow tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.e2e
class TestMCPServerWorkflows:
    """Consolidated MCP server workflow tests."""

    def setup_method(self):
        """Set up test fixtures for MCP workflow tests."""
        self.data_loader = DataLoader()
        self.parser = STIXParser()

        # Comprehensive test data for MCP workflows
        self.test_data = {
            "techniques": [
                {
                    "id": "T1055",
                    "name": "Process Injection",
                    "description": "Adversaries may inject code into processes to evade defenses.",
                    "tactics": ["TA0004", "TA0005"],
                    "platforms": ["Windows", "macOS", "Linux"],
                    "mitigations": ["M1040", "M1026"],
                    "data_sources": [
                        "Process: Process Creation",
                        "Process: OS API Execution",
                    ],
                    "detection": "Monitor for process injection techniques.",
                },
                {
                    "id": "T1059",
                    "name": "Command and Scripting Interpreter",
                    "description": "Adversaries may abuse command interpreters to execute commands.",
                    "tactics": ["TA0002"],
                    "platforms": ["Windows", "Linux", "macOS"],
                    "mitigations": ["M1038", "M1042"],
                    "data_sources": [
                        "Command: Command Execution",
                        "Process: Process Creation",
                    ],
                },
                {
                    "id": "T1190",
                    "name": "Exploit Public-Facing Application",
                    "description": "Adversaries may exploit public-facing applications.",
                    "tactics": ["TA0001"],
                    "platforms": ["Windows", "Linux", "macOS"],
                    "mitigations": ["M1048", "M1030"],
                    "data_sources": [
                        "Application Log: Application Log Content",
                        "Network Traffic: Network Traffic Content",
                    ],
                },
            ],
            "tactics": [
                {
                    "id": "TA0001",
                    "name": "Initial Access",
                    "description": "Adversaries are trying to get into your network.",
                },
                {
                    "id": "TA0002",
                    "name": "Execution",
                    "description": "Adversaries are trying to run malicious code.",
                },
                {
                    "id": "TA0004",
                    "name": "Privilege Escalation",
                    "description": "Adversaries are trying to gain higher-level permissions.",
                },
                {
                    "id": "TA0005",
                    "name": "Defense Evasion",
                    "description": "Adversaries are trying to avoid being detected.",
                },
                {
                    "id": "TA0040",
                    "name": "Impact",
                    "description": "Adversaries are trying to manipulate, interrupt, or destroy your systems.",
                },
            ],
            "groups": [
                {
                    "id": "G0016",
                    "name": "APT29",
                    "description": "APT29 is a sophisticated threat group.",
                    "aliases": ["APT29", "Cozy Bear", "The Dukes"],
                    "techniques": ["T1055", "T1059", "T1190"],
                },
                {
                    "id": "G0032",
                    "name": "Lazarus Group",
                    "description": "Lazarus Group is a North Korean state-sponsored group.",
                    "aliases": ["Lazarus Group", "HIDDEN COBRA", "Zinc"],
                    "techniques": ["T1055", "T1190"],
                },
            ],
            "mitigations": [
                {
                    "id": "M1040",
                    "name": "Behavior Prevention on Endpoint",
                    "description": "Use capabilities to prevent suspicious behavior patterns.",
                },
                {
                    "id": "M1026",
                    "name": "Privileged Account Management",
                    "description": "Manage the creation, modification, use, and permissions associated with privileged accounts.",
                },
                {
                    "id": "M1038",
                    "name": "Execution Prevention",
                    "description": "Block execution of code on a system through application control.",
                },
                {
                    "id": "M1042",
                    "name": "Disable or Remove Feature or Program",
                    "description": "Remove or deny access to unnecessary features or programs.",
                },
                {
                    "id": "M1048",
                    "name": "Application Isolation and Sandboxing",
                    "description": "Restrict execution of code to virtual environments.",
                },
                {
                    "id": "M1030",
                    "name": "Network Segmentation",
                    "description": "Architect network security to separate networks and functions.",
                },
            ],
            "relationships": [
                {
                    "relationship_type": "uses",
                    "source_ref": "intrusion-set--g0016-stix-id",
                    "target_ref": "attack-pattern--t1055-stix-id",
                },
                {
                    "relationship_type": "uses",
                    "source_ref": "intrusion-set--g0032-stix-id",
                    "target_ref": "attack-pattern--t1055-stix-id",
                },
                {
                    "relationship_type": "mitigates",
                    "source_ref": "course-of-action--m1040-stix-id",
                    "target_ref": "attack-pattern--t1055-stix-id",
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_complete_threat_analysis_workflow(self, workflow_executor, e2e_test_manager):
        """Test complete threat analysis workflow (consolidated from task 14)."""
        e2e_test_manager.start_test("complete_threat_analysis_workflow")
        logger.info("Starting complete threat analysis workflow...")

        with patch.object(
            self.data_loader, "get_cached_data", return_value=self.test_data
        ):
            mcp_server = create_mcp_server(self.data_loader)

            # Define comprehensive threat analysis workflow
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
                ("detect_technique_relationships", {"technique_id": "T1055", "depth": 1}),
            ]

            # Execute workflow using workflow executor
            for step_num, (tool_name, params) in enumerate(workflow_steps, 1):
                workflow_executor.add_step(
                    f"step_{step_num}_{tool_name}",
                    mcp_server.call_tool,
                    tool_name,
                    params
                )

            # Execute complete workflow
            results = await workflow_executor.execute_workflow()
            workflow_executor.assert_workflow_success()

            # Validate workflow results
            assert len(results) == len(workflow_steps), "All workflow steps should complete"

            workflow_results = []
            for step_name, result in results.items():
                assert result["success"], f"Step {step_name} should succeed"
                
                # Validate result structure
                step_result = result["result"]
                assert isinstance(step_result, tuple), f"Step {step_name} should return tuple"
                assert len(step_result) == 2, f"Step {step_name} should return (content, metadata)"

                tool_result, metadata = step_result
                assert isinstance(tool_result, list), f"Step {step_name} should return list"
                assert len(tool_result) > 0, f"Step {step_name} should return non-empty result"

                content = tool_result[0]
                assert hasattr(content, "text"), f"Step {step_name} should return text content"
                assert len(content.text) > 0, f"Step {step_name} should return non-empty text"

                workflow_results.append({
                    "step": step_name,
                    "result_length": len(content.text),
                    "execution_time": result["execution_time"],
                    "success": True,
                })

            # Performance validation
            total_output = sum(r["result_length"] for r in workflow_results)
            total_time = sum(r["execution_time"] for r in workflow_results)

            assert total_time < 30.0, f"Complete workflow should finish in under 30 seconds, took {total_time:.2f}s"
            assert total_output > 1000, f"Workflow should generate substantial output, got {total_output} characters"

            # Log workflow summary
            logger.info(f"Complete workflow generated {total_output} characters across {len(workflow_steps)} steps in {total_time:.2f}s")
            for result in workflow_results:
                logger.info(f"  {result['step']}: {result['result_length']} chars in {result['execution_time']:.2f}s")

        e2e_test_manager.end_test("complete_threat_analysis_workflow")

    @pytest.mark.asyncio
    async def test_all_mcp_tools_integration_workflow(self, workflow_executor):
        """Test integration workflow covering all 8 MCP tools."""
        logger.info("Starting all MCP tools integration workflow...")

        with patch.object(
            self.data_loader, "get_cached_data", return_value=self.test_data
        ):
            mcp_server = create_mcp_server(self.data_loader)

            # Test all 8 MCP tools in a logical workflow
            all_tools_workflow = [
                # Basic analysis tools
                ("search_attack", {"query": "injection"}),
                ("get_technique", {"technique_id": "T1055"}),
                ("list_tactics", {}),
                ("get_group_techniques", {"group_id": "G0016"}),
                ("get_technique_mitigations", {"technique_id": "T1055"}),
                
                # Advanced analysis tools
                ("build_attack_path", {"start_tactic": "TA0001", "end_tactic": "TA0005"}),
                ("analyze_coverage_gaps", {"threat_groups": ["G0016", "G0032"]}),
                ("detect_technique_relationships", {"technique_id": "T1055", "relationship_types": ["uses", "mitigates"], "depth": 2}),
            ]

            # Execute all tools workflow
            for i, (tool_name, params) in enumerate(all_tools_workflow):
                workflow_executor.add_step(
                    f"tool_{i}_{tool_name}",
                    mcp_server.call_tool,
                    tool_name,
                    params
                )

            results = await workflow_executor.execute_workflow()
            workflow_executor.assert_workflow_success()

            # Validate all tools executed successfully
            assert len(results) == 8, "All 8 MCP tools should execute"

            # Validate specific tool outputs
            search_result = workflow_executor.get_step_result("tool_0_search_attack")
            content, metadata = search_result
            assert "T1055" in content[0].text or "injection" in content[0].text.lower(), "Search should find relevant results"

            technique_result = workflow_executor.get_step_result("tool_1_get_technique")
            content, metadata = technique_result
            assert "Process Injection" in content[0].text, "Technique details should include name"

            tactics_result = workflow_executor.get_step_result("tool_2_list_tactics")
            content, metadata = tactics_result
            assert "TA0001" in content[0].text, "Tactics list should include Initial Access"

            group_result = workflow_executor.get_step_result("tool_3_get_group_techniques")
            content, metadata = group_result
            assert "APT29" in content[0].text, "Group analysis should include group name"

            mitigations_result = workflow_executor.get_step_result("tool_4_get_technique_mitigations")
            content, metadata = mitigations_result
            assert "M1040" in content[0].text or "M1026" in content[0].text, "Mitigations should be listed"

            attack_path_result = workflow_executor.get_step_result("tool_5_build_attack_path")
            content, metadata = attack_path_result
            assert "ATTACK PATH" in content[0].text, "Attack path should be constructed"

            coverage_result = workflow_executor.get_step_result("tool_6_analyze_coverage_gaps")
            content, metadata = coverage_result
            assert "COVERAGE GAP" in content[0].text, "Coverage analysis should be performed"

            relationships_result = workflow_executor.get_step_result("tool_7_detect_technique_relationships")
            content, metadata = relationships_result
            assert "RELATIONSHIP" in content[0].text, "Relationship analysis should be performed"

            logger.info("All MCP tools integration workflow completed successfully")

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, workflow_executor):
        """Test error handling across MCP tools workflow."""
        logger.info("Starting error handling workflow...")

        with patch.object(
            self.data_loader, "get_cached_data", return_value=self.test_data
        ):
            mcp_server = create_mcp_server(self.data_loader)

            # Test workflow with various error conditions
            error_scenarios = [
                ("search_attack", {"query": "nonexistent_technique_xyz"}),
                ("get_technique", {"technique_id": "T9999"}),
                ("get_group_techniques", {"group_id": "G9999"}),
                ("get_technique_mitigations", {"technique_id": "T9999"}),
                ("build_attack_path", {"start_tactic": "TA9999", "end_tactic": "TA9998"}),
                ("analyze_coverage_gaps", {"threat_groups": ["G9999"]}),
                ("detect_technique_relationships", {"technique_id": "T9999"}),
            ]

            # Execute error scenarios
            for i, (tool_name, params) in enumerate(error_scenarios):
                workflow_executor.add_step(
                    f"error_{i}_{tool_name}",
                    mcp_server.call_tool,
                    tool_name,
                    params
                )

            results = await workflow_executor.execute_workflow()
            workflow_executor.assert_workflow_success()

            # Validate error handling
            for step_name, result in results.items():
                assert result["success"], f"Error scenario {step_name} should handle errors gracefully"

                # Validate error responses contain appropriate messages
                step_result = result["result"]
                content, metadata = step_result
                text = content[0].text.lower()

                # Should contain error indicators
                error_indicators = ["not found", "invalid", "error", "no results", "unable to"]
                assert any(
                    indicator in text for indicator in error_indicators
                ), f"Step {step_name} should return appropriate error message"

            logger.info("Error handling workflow completed successfully")

    @pytest.mark.asyncio
    async def test_performance_optimization_workflow(self, workflow_executor, e2e_test_timeout):
        """Test performance characteristics of MCP tools workflow."""
        logger.info("Starting performance optimization workflow...")

        with patch.object(
            self.data_loader, "get_cached_data", return_value=self.test_data
        ):
            mcp_server = create_mcp_server(self.data_loader)

            # Performance-focused workflow
            performance_tests = [
                ("search_attack", {"query": "T1055"}),
                ("get_technique", {"technique_id": "T1055"}),
                ("list_tactics", {}),
                ("get_group_techniques", {"group_id": "G0016"}),
                ("get_technique_mitigations", {"technique_id": "T1055"}),
            ]

            start_time = time.time()

            # Execute performance tests
            for i, (tool_name, params) in enumerate(performance_tests):
                workflow_executor.add_step(
                    f"perf_{i}_{tool_name}",
                    mcp_server.call_tool,
                    tool_name,
                    params
                )

            results = await workflow_executor.execute_workflow()
            total_time = time.time() - start_time

            workflow_executor.assert_workflow_success()

            # Performance assertions
            assert total_time < 15.0, f"Performance workflow should complete in under 15 seconds, took {total_time:.2f}s"

            # Individual tool performance
            for step_name, result in results.items():
                execution_time = result["execution_time"]
                assert execution_time < 3.0, f"Individual tool {step_name} should complete in under 3 seconds, took {execution_time:.2f}s"

            # Calculate performance metrics
            avg_time = sum(r["execution_time"] for r in results.values()) / len(results)
            assert avg_time < 1.5, f"Average tool execution time should be under 1.5 seconds, was {avg_time:.2f}s"

            logger.info(f"Performance workflow completed in {total_time:.2f}s (avg: {avg_time:.2f}s per tool)")

    @pytest.mark.asyncio
    async def test_concurrent_mcp_tools_workflow(self, e2e_event_loop):
        """Test concurrent execution of MCP tools."""
        logger.info("Starting concurrent MCP tools workflow...")

        with patch.object(
            self.data_loader, "get_cached_data", return_value=self.test_data
        ):
            mcp_server = create_mcp_server(self.data_loader)

            # Define concurrent tool executions
            async def concurrent_search():
                return await mcp_server.call_tool("search_attack", {"query": "injection"})

            async def concurrent_technique():
                return await mcp_server.call_tool("get_technique", {"technique_id": "T1055"})

            async def concurrent_tactics():
                return await mcp_server.call_tool("list_tactics", {})

            async def concurrent_group():
                return await mcp_server.call_tool("get_group_techniques", {"group_id": "G0016"})

            # Execute tools concurrently
            start_time = time.time()
            concurrent_results = await asyncio.gather(
                concurrent_search(),
                concurrent_technique(),
                concurrent_tactics(),
                concurrent_group()
            )
            concurrent_time = time.time() - start_time

            # Execute tools sequentially for comparison
            start_time = time.time()
            seq_results = []
            seq_results.append(await mcp_server.call_tool("search_attack", {"query": "injection"}))
            seq_results.append(await mcp_server.call_tool("get_technique", {"technique_id": "T1055"}))
            seq_results.append(await mcp_server.call_tool("list_tactics", {}))
            seq_results.append(await mcp_server.call_tool("get_group_techniques", {"group_id": "G0016"}))
            sequential_time = time.time() - start_time

            # Validate concurrent execution
            assert len(concurrent_results) == 4, "All concurrent tools should complete"

            for result in concurrent_results:
                assert isinstance(result, tuple), "Each result should be a tuple"
                assert len(result) == 2, "Each result should have (content, metadata)"
                content, metadata = result
                assert len(content) > 0, "Each result should have content"

            # Performance comparison (allow for some overhead in concurrent execution)
            performance_ratio = concurrent_time / sequential_time
            assert performance_ratio < 3.0, f"Concurrent execution should not be more than 3x slower (ratio: {performance_ratio:.2f})"

            logger.info(f"Concurrent tools completed in {concurrent_time:.2f}s vs {sequential_time:.2f}s sequential")

    @pytest.mark.asyncio
    async def test_data_consistency_workflow(self, workflow_executor):
        """Test data consistency across MCP tools workflow."""
        logger.info("Starting data consistency workflow...")

        with patch.object(
            self.data_loader, "get_cached_data", return_value=self.test_data
        ):
            mcp_server = create_mcp_server(self.data_loader)

            # Test data consistency across different tools accessing same data
            consistency_tests = [
                ("search_t1055", "search_attack", {"query": "T1055"}),
                ("get_t1055", "get_technique", {"technique_id": "T1055"}),
                ("mitigations_t1055", "get_technique_mitigations", {"technique_id": "T1055"}),
                ("group_with_t1055", "get_group_techniques", {"group_id": "G0016"}),
            ]

            # Execute consistency tests
            for step_name, tool_name, params in consistency_tests:
                workflow_executor.add_step(
                    step_name,
                    mcp_server.call_tool,
                    tool_name,
                    params
                )

            results = await workflow_executor.execute_workflow()
            workflow_executor.assert_workflow_success()

            # Validate data consistency
            search_result = workflow_executor.get_step_result("search_t1055")
            technique_result = workflow_executor.get_step_result("get_t1055")
            mitigation_result = workflow_executor.get_step_result("mitigations_t1055")
            group_result = workflow_executor.get_step_result("group_with_t1055")

            # All results should reference T1055 and Process Injection
            for result_name, result in [
                ("search", search_result),
                ("technique", technique_result),
                ("mitigation", mitigation_result),
                ("group", group_result)
            ]:
                content, metadata = result
                text = content[0].text
                assert "T1055" in text, f"{result_name} result should contain T1055"
                
                # Process Injection should appear in most results
                if result_name in ["search", "technique", "mitigation"]:
                    assert "Process Injection" in text, f"{result_name} result should contain technique name"

            logger.info("Data consistency workflow completed successfully")