"""
Consolidated end-to-end integration tests.

This module consolidates all end-to-end integration tests into comprehensive workflows
that validate complete user journeys through the MCP server system.
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

# Configure logging for E2E tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.e2e
class TestEndToEndIntegration:
    """Consolidated end-to-end integration tests for complete user workflows."""

    def setup_method(self):
        """Set up test fixtures for each E2E test method."""
        self.data_loader = DataLoader()
        self.parser = STIXParser()

        # Comprehensive test data for E2E scenarios
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
                {
                    "id": "T1003",
                    "name": "OS Credential Dumping",
                    "description": "Adversaries may attempt to dump credentials.",
                    "tactics": ["TA0006"],
                    "platforms": ["Windows", "Linux", "macOS"],
                    "mitigations": ["M1027", "M1043"],
                    "data_sources": [
                        "Command: Command Execution",
                        "File: File Access",
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
                    "id": "TA0006",
                    "name": "Credential Access",
                    "description": "Adversaries are trying to steal account names and passwords.",
                },
            ],
            "groups": [
                {
                    "id": "G0016",
                    "name": "APT29",
                    "description": "APT29 is a sophisticated threat group.",
                    "aliases": ["APT29", "Cozy Bear", "The Dukes"],
                    "techniques": ["T1055", "T1059", "T1190", "T1003"],
                },
                {
                    "id": "G0032",
                    "name": "Lazarus Group",
                    "description": "Lazarus Group is a North Korean state-sponsored group.",
                    "aliases": ["Lazarus Group", "HIDDEN COBRA", "Zinc"],
                    "techniques": ["T1055", "T1190", "T1003"],
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
                {
                    "id": "M1027",
                    "name": "Password Policies",
                    "description": "Set and enforce secure password policies for accounts.",
                },
                {
                    "id": "M1043",
                    "name": "Credential Access Protection",
                    "description": "Use capabilities to prevent successful credential access.",
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
    async def test_threat_analysis_workflow(self, workflow_executor, e2e_test_data):
        """Test complete threat analysis workflow from search to mitigation."""
        logger.info("Starting threat analysis workflow E2E test...")

        with patch.object(
            self.data_loader, "get_cached_data", return_value=self.test_data
        ):
            mcp_server = create_mcp_server(self.data_loader)

            # Define comprehensive threat analysis workflow
            workflow_executor.add_step(
                "initial_search",
                mcp_server.call_tool,
                "search_attack",
                {"query": "process injection"}
            )

            workflow_executor.add_step(
                "technique_details",
                mcp_server.call_tool,
                "get_technique",
                {"technique_id": "T1055"}
            )

            workflow_executor.add_step(
                "technique_mitigations",
                mcp_server.call_tool,
                "get_technique_mitigations",
                {"technique_id": "T1055"}
            )

            workflow_executor.add_step(
                "group_analysis",
                mcp_server.call_tool,
                "get_group_techniques",
                {"group_id": "G0016"}
            )

            workflow_executor.add_step(
                "coverage_analysis",
                mcp_server.call_tool,
                "analyze_coverage_gaps",
                {"threat_groups": ["G0016", "G0032"]}
            )

            # Execute workflow
            results = await workflow_executor.execute_workflow()

            # Validate workflow completion
            workflow_executor.assert_workflow_success()

            # Validate workflow results
            assert len(results) == 5, "All workflow steps should complete"

            # Validate each step produces meaningful output
            for step_name, result in results.items():
                assert result["success"], f"Step {step_name} should succeed"
                assert result["execution_time"] > 0, f"Step {step_name} should have execution time"

                # Validate result content
                step_result = result["result"]
                assert isinstance(step_result, tuple), f"Step {step_name} should return tuple"
                assert len(step_result) == 2, f"Step {step_name} should return (content, metadata)"

                content, metadata = step_result
                assert len(content) > 0, f"Step {step_name} should return content"
                assert hasattr(content[0], "text"), f"Step {step_name} should return text content"
                assert len(content[0].text) > 0, f"Step {step_name} should return non-empty text"

            logger.info("Threat analysis workflow completed successfully")

    @pytest.mark.asyncio
    async def test_attack_path_construction_workflow(self, workflow_executor):
        """Test complete attack path construction workflow."""
        logger.info("Starting attack path construction workflow E2E test...")

        with patch.object(
            self.data_loader, "get_cached_data", return_value=self.test_data
        ):
            mcp_server = create_mcp_server(self.data_loader)

            # Define attack path construction workflow
            workflow_executor.add_step(
                "list_tactics",
                mcp_server.call_tool,
                "list_tactics",
                {}
            )

            workflow_executor.add_step(
                "build_attack_path",
                mcp_server.call_tool,
                "build_attack_path",
                {"start_tactic": "TA0001", "end_tactic": "TA0006"}
            )

            workflow_executor.add_step(
                "filtered_attack_path",
                mcp_server.call_tool,
                "build_attack_path",
                {"start_tactic": "TA0001", "end_tactic": "TA0006", "group_id": "G0016"}
            )

            workflow_executor.add_step(
                "relationship_analysis",
                mcp_server.call_tool,
                "detect_technique_relationships",
                {"technique_id": "T1055", "relationship_types": ["uses", "mitigates"], "depth": 2}
            )

            # Execute workflow
            results = await workflow_executor.execute_workflow()

            # Validate workflow completion
            workflow_executor.assert_workflow_success()

            # Validate attack path construction results
            attack_path_result = workflow_executor.get_step_result("build_attack_path")
            assert attack_path_result is not None, "Attack path should be constructed"

            content, metadata = attack_path_result
            text = content[0].text
            assert "ATTACK PATH CONSTRUCTION" in text, "Should include attack path header"
            assert "TA0001" in text, "Should include start tactic"
            assert "TA0006" in text, "Should include end tactic"

            # Validate filtered attack path
            filtered_result = workflow_executor.get_step_result("filtered_attack_path")
            content, metadata = filtered_result
            text = content[0].text
            assert "Group Filter: G0016" in text, "Should include group filter"

            logger.info("Attack path construction workflow completed successfully")

    @pytest.mark.asyncio
    async def test_comprehensive_threat_intelligence_workflow(self, workflow_executor, user_simulation):
        """Test comprehensive threat intelligence analysis workflow."""
        logger.info("Starting comprehensive threat intelligence workflow E2E test...")

        with patch.object(
            self.data_loader, "get_cached_data", return_value=self.test_data
        ):
            mcp_server = create_mcp_server(self.data_loader)

            # Simulate user performing comprehensive threat intelligence analysis
            search_result = user_simulation.simulate_search_workflow("APT29")
            assert search_result["results_found"], "Search should find results"

            technique_result = user_simulation.simulate_technique_analysis("T1055")
            assert technique_result["details_loaded"], "Technique details should load"

            attack_path_result = user_simulation.simulate_attack_path_creation("T1190", "T1003")
            assert attack_path_result["path_created"], "Attack path should be created"

            coverage_result = user_simulation.simulate_coverage_analysis("G0016")
            assert coverage_result["analysis_completed"], "Coverage analysis should complete"

            # Execute actual MCP tools to validate simulation
            workflow_executor.add_step(
                "search_apt29",
                mcp_server.call_tool,
                "search_attack",
                {"query": "APT29"}
            )

            workflow_executor.add_step(
                "analyze_t1055",
                mcp_server.call_tool,
                "get_technique",
                {"technique_id": "T1055"}
            )

            workflow_executor.add_step(
                "build_path",
                mcp_server.call_tool,
                "build_attack_path",
                {"start_tactic": "TA0001", "end_tactic": "TA0006"}
            )

            workflow_executor.add_step(
                "coverage_gaps",
                mcp_server.call_tool,
                "analyze_coverage_gaps",
                {"threat_groups": ["G0016"]}
            )

            # Execute workflow
            results = await workflow_executor.execute_workflow()
            workflow_executor.assert_workflow_success()

            # Validate comprehensive analysis results
            search_result = workflow_executor.get_step_result("search_apt29")
            content, metadata = search_result
            assert "G0016" in content[0].text, "Should find APT29 group"

            technique_result = workflow_executor.get_step_result("analyze_t1055")
            content, metadata = technique_result
            assert "Process Injection" in content[0].text, "Should include technique name"

            logger.info("Comprehensive threat intelligence workflow completed successfully")

    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, workflow_executor):
        """Test error handling across complete workflows."""
        logger.info("Starting error handling workflow E2E test...")

        with patch.object(
            self.data_loader, "get_cached_data", return_value=self.test_data
        ):
            mcp_server = create_mcp_server(self.data_loader)

            # Test workflow with invalid inputs
            workflow_executor.add_step(
                "invalid_search",
                mcp_server.call_tool,
                "search_attack",
                {"query": "nonexistent_technique_xyz"}
            )

            workflow_executor.add_step(
                "invalid_technique",
                mcp_server.call_tool,
                "get_technique",
                {"technique_id": "T9999"}
            )

            workflow_executor.add_step(
                "invalid_group",
                mcp_server.call_tool,
                "get_group_techniques",
                {"group_id": "G9999"}
            )

            workflow_executor.add_step(
                "invalid_attack_path",
                mcp_server.call_tool,
                "build_attack_path",
                {"start_tactic": "TA9999", "end_tactic": "TA9998"}
            )

            # Execute workflow (should handle errors gracefully)
            results = await workflow_executor.execute_workflow()

            # Validate error handling
            for step_name, result in results.items():
                assert result["success"], f"Step {step_name} should handle errors gracefully"

                # Validate error responses contain appropriate messages
                step_result = result["result"]
                content, metadata = step_result
                text = content[0].text

                if "invalid" in step_name:
                    assert any(
                        error_msg in text.lower()
                        for error_msg in ["not found", "invalid", "error", "no results"]
                    ), f"Step {step_name} should return appropriate error message"

            logger.info("Error handling workflow completed successfully")

    @pytest.mark.asyncio
    async def test_performance_workflow(self, workflow_executor, e2e_test_timeout):
        """Test performance characteristics of complete workflows."""
        logger.info("Starting performance workflow E2E test...")

        with patch.object(
            self.data_loader, "get_cached_data", return_value=self.test_data
        ):
            mcp_server = create_mcp_server(self.data_loader)

            # Define performance-focused workflow
            start_time = time.time()

            # Execute multiple tools in sequence to test performance
            tools_to_test = [
                ("search_attack", {"query": "injection"}),
                ("list_tactics", {}),
                ("get_technique", {"technique_id": "T1055"}),
                ("get_group_techniques", {"group_id": "G0016"}),
                ("get_technique_mitigations", {"technique_id": "T1055"}),
                ("build_attack_path", {"start_tactic": "TA0001", "end_tactic": "TA0005"}),
                ("analyze_coverage_gaps", {"threat_groups": ["G0016"]}),
                ("detect_technique_relationships", {"technique_id": "T1055"}),
            ]

            for i, (tool_name, params) in enumerate(tools_to_test):
                workflow_executor.add_step(
                    f"perf_test_{i}_{tool_name}",
                    mcp_server.call_tool,
                    tool_name,
                    params
                )

            # Execute workflow
            results = await workflow_executor.execute_workflow()
            total_time = time.time() - start_time

            # Validate performance requirements
            workflow_executor.assert_workflow_success()

            # Performance assertions
            assert total_time < 30.0, f"Complete workflow should complete in under 30 seconds, took {total_time:.2f}s"

            # Individual tool performance
            for step_name, result in results.items():
                execution_time = result["execution_time"]
                assert execution_time < 5.0, f"Individual tool {step_name} should complete in under 5 seconds, took {execution_time:.2f}s"

            # Calculate average execution time
            avg_time = sum(r["execution_time"] for r in results.values()) / len(results)
            assert avg_time < 2.0, f"Average tool execution time should be under 2 seconds, was {avg_time:.2f}s"

            logger.info(f"Performance workflow completed in {total_time:.2f}s (avg: {avg_time:.2f}s per tool)")

    @pytest.mark.asyncio
    async def test_data_consistency_workflow(self, workflow_executor, system_health_checker):
        """Test data consistency across complete workflows."""
        logger.info("Starting data consistency workflow E2E test...")

        with patch.object(
            self.data_loader, "get_cached_data", return_value=self.test_data
        ):
            mcp_server = create_mcp_server(self.data_loader)

            # Check system health before workflow
            health_status = system_health_checker.check_data_availability()
            assert health_status["data_loaded"], "Data should be available before workflow"

            # Execute workflow that accesses same data through different tools
            workflow_executor.add_step(
                "search_t1055",
                mcp_server.call_tool,
                "search_attack",
                {"query": "T1055"}
            )

            workflow_executor.add_step(
                "get_t1055",
                mcp_server.call_tool,
                "get_technique",
                {"technique_id": "T1055"}
            )

            workflow_executor.add_step(
                "mitigations_t1055",
                mcp_server.call_tool,
                "get_technique_mitigations",
                {"technique_id": "T1055"}
            )

            # Execute workflow
            results = await workflow_executor.execute_workflow()
            workflow_executor.assert_workflow_success()

            # Validate data consistency across tools
            search_result = workflow_executor.get_step_result("search_t1055")
            technique_result = workflow_executor.get_step_result("get_t1055")
            mitigation_result = workflow_executor.get_step_result("mitigations_t1055")

            # All results should reference T1055
            for result_name, result in [
                ("search", search_result),
                ("technique", technique_result),
                ("mitigation", mitigation_result)
            ]:
                content, metadata = result
                text = content[0].text
                assert "T1055" in text, f"{result_name} result should contain T1055"
                assert "Process Injection" in text, f"{result_name} result should contain technique name"

            logger.info("Data consistency workflow completed successfully")

    @pytest.mark.asyncio
    async def test_concurrent_workflow_execution(self, e2e_event_loop):
        """Test concurrent execution of multiple workflows."""
        logger.info("Starting concurrent workflow execution E2E test...")

        with patch.object(
            self.data_loader, "get_cached_data", return_value=self.test_data
        ):
            mcp_server = create_mcp_server(self.data_loader)

            # Define multiple concurrent workflows
            async def workflow_1():
                result = await mcp_server.call_tool("search_attack", {"query": "injection"})
                return ("workflow_1", result)

            async def workflow_2():
                result = await mcp_server.call_tool("get_technique", {"technique_id": "T1055"})
                return ("workflow_2", result)

            async def workflow_3():
                result = await mcp_server.call_tool("list_tactics", {})
                return ("workflow_3", result)

            # Execute workflows concurrently
            start_time = time.time()
            results = await asyncio.gather(workflow_1(), workflow_2(), workflow_3())
            concurrent_time = time.time() - start_time

            # Execute workflows sequentially for comparison
            start_time = time.time()
            seq_result_1 = await mcp_server.call_tool("search_attack", {"query": "injection"})
            seq_result_2 = await mcp_server.call_tool("get_technique", {"technique_id": "T1055"})
            seq_result_3 = await mcp_server.call_tool("list_tactics", {})
            sequential_time = time.time() - start_time

            # Validate concurrent execution
            assert len(results) == 3, "All concurrent workflows should complete"

            for workflow_name, result in results:
                assert isinstance(result, tuple), f"{workflow_name} should return tuple"
                assert len(result) == 2, f"{workflow_name} should return (content, metadata)"
                content, metadata = result
                assert len(content) > 0, f"{workflow_name} should return content"

            # Performance comparison (concurrent should not be significantly slower)
            performance_ratio = concurrent_time / sequential_time
            assert performance_ratio < 2.0, f"Concurrent execution should not be more than 2x slower than sequential (ratio: {performance_ratio:.2f})"

            logger.info(f"Concurrent workflows completed in {concurrent_time:.2f}s vs {sequential_time:.2f}s sequential")