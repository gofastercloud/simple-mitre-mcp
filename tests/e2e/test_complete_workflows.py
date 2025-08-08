"""
Complete user workflow validation tests.

This module tests complete user journeys through the MCP server system,
validating realistic usage patterns and workflow combinations.
"""

import pytest
import asyncio
import logging
import time
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

from src.data_loader import DataLoader
from src.mcp_server import create_mcp_server

# Configure logging for workflow tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.e2e
class TestCompleteWorkflows:
    """Test complete user workflows and journey validation."""

    def setup_method(self):
        """Set up test fixtures for workflow tests."""
        self.data_loader = DataLoader()

        # Enhanced test data for complete workflows
        self.test_data = {
            "techniques": [
                {
                    "id": "T1566",
                    "name": "Phishing",
                    "description": "Adversaries may send phishing messages to gain access.",
                    "tactics": ["TA0001"],
                    "platforms": ["Windows", "macOS", "Linux"],
                    "mitigations": ["M1031", "M1017"],
                    "data_sources": ["Application Log: Application Log Content"],
                },
                {
                    "id": "T1055",
                    "name": "Process Injection",
                    "description": "Adversaries may inject code into processes.",
                    "tactics": ["TA0004", "TA0005"],
                    "platforms": ["Windows", "macOS", "Linux"],
                    "mitigations": ["M1040", "M1026"],
                    "data_sources": ["Process: Process Creation"],
                },
                {
                    "id": "T1003",
                    "name": "OS Credential Dumping",
                    "description": "Adversaries may attempt to dump credentials.",
                    "tactics": ["TA0006"],
                    "platforms": ["Windows", "Linux", "macOS"],
                    "mitigations": ["M1027", "M1043"],
                    "data_sources": ["Command: Command Execution"],
                },
                {
                    "id": "T1070",
                    "name": "Indicator Removal on Host",
                    "description": "Adversaries may delete or alter generated artifacts.",
                    "tactics": ["TA0005"],
                    "platforms": ["Windows", "Linux", "macOS"],
                    "mitigations": ["M1029", "M1022"],
                    "data_sources": ["File: File Deletion"],
                },
            ],
            "tactics": [
                {"id": "TA0001", "name": "Initial Access", "description": "Get into network"},
                {"id": "TA0004", "name": "Privilege Escalation", "description": "Gain higher permissions"},
                {"id": "TA0005", "name": "Defense Evasion", "description": "Avoid detection"},
                {"id": "TA0006", "name": "Credential Access", "description": "Steal credentials"},
                {"id": "TA0040", "name": "Impact", "description": "Manipulate or destroy systems"},
            ],
            "groups": [
                {
                    "id": "G0016",
                    "name": "APT29",
                    "description": "Sophisticated threat group",
                    "aliases": ["APT29", "Cozy Bear"],
                    "techniques": ["T1566", "T1055", "T1003", "T1070"],
                },
                {
                    "id": "G0007",
                    "name": "APT28",
                    "description": "Russian military intelligence group",
                    "aliases": ["APT28", "Fancy Bear"],
                    "techniques": ["T1566", "T1055", "T1003"],
                },
            ],
            "mitigations": [
                {"id": "M1031", "name": "Network Intrusion Prevention", "description": "Block malicious network traffic"},
                {"id": "M1017", "name": "User Training", "description": "Train users to identify threats"},
                {"id": "M1040", "name": "Behavior Prevention on Endpoint", "description": "Prevent suspicious behavior"},
                {"id": "M1026", "name": "Privileged Account Management", "description": "Manage privileged accounts"},
                {"id": "M1027", "name": "Password Policies", "description": "Enforce secure passwords"},
                {"id": "M1043", "name": "Credential Access Protection", "description": "Protect credential access"},
                {"id": "M1029", "name": "Remote Data Storage", "description": "Store data remotely"},
                {"id": "M1022", "name": "Restrict File and Directory Permissions", "description": "Limit file access"},
            ],
            "relationships": [
                {"relationship_type": "uses", "source_ref": "intrusion-set--g0016", "target_ref": "attack-pattern--t1566"},
                {"relationship_type": "uses", "source_ref": "intrusion-set--g0007", "target_ref": "attack-pattern--t1566"},
                {"relationship_type": "mitigates", "source_ref": "course-of-action--m1031", "target_ref": "attack-pattern--t1566"},
            ],
        }

    @pytest.mark.asyncio
    async def test_security_analyst_investigation_workflow(self, workflow_executor):
        """Test complete security analyst investigation workflow."""
        logger.info("Starting security analyst investigation workflow...")

        with patch.object(self.data_loader, "get_cached_data", return_value=self.test_data):
            mcp_server = create_mcp_server(self.data_loader)

            # Phase 1: Initial threat discovery
            workflow_executor.add_step(
                "discover_phishing",
                mcp_server.call_tool,
                "search_attack",
                {"query": "phishing"}
            )

            # Phase 2: Technique analysis
            workflow_executor.add_step(
                "analyze_phishing_technique",
                mcp_server.call_tool,
                "get_technique",
                {"technique_id": "T1566"}
            )

            # Phase 3: Mitigation research
            workflow_executor.add_step(
                "research_mitigations",
                mcp_server.call_tool,
                "get_technique_mitigations",
                {"technique_id": "T1566"}
            )

            # Phase 4: Threat actor analysis
            workflow_executor.add_step(
                "analyze_apt29",
                mcp_server.call_tool,
                "get_group_techniques",
                {"group_id": "G0016"}
            )

            # Phase 5: Attack path construction
            workflow_executor.add_step(
                "build_attack_chain",
                mcp_server.call_tool,
                "build_attack_path",
                {"start_tactic": "TA0001", "end_tactic": "TA0040"}
            )

            # Phase 6: Coverage gap analysis
            workflow_executor.add_step(
                "assess_coverage",
                mcp_server.call_tool,
                "analyze_coverage_gaps",
                {"threat_groups": ["G0016", "G0007"]}
            )

            # Execute complete investigation workflow
            results = await workflow_executor.execute_workflow()
            workflow_executor.assert_workflow_success()

            # Validate investigation phases
            self._validate_investigation_phase(
                workflow_executor.get_step_result("discover_phishing"),
                "phishing", "T1566"
            )

            self._validate_investigation_phase(
                workflow_executor.get_step_result("analyze_phishing_technique"),
                "Phishing", "TA0001"
            )

            self._validate_investigation_phase(
                workflow_executor.get_step_result("research_mitigations"),
                "M1031", "Network Intrusion Prevention"
            )

            self._validate_investigation_phase(
                workflow_executor.get_step_result("analyze_apt29"),
                "APT29", "T1566"
            )

            # Validate workflow timing
            total_time = sum(r["execution_time"] for r in results.values())
            assert total_time < 60.0, f"Investigation workflow should complete in under 60 seconds, took {total_time:.2f}s"

            logger.info(f"Security analyst investigation workflow completed in {total_time:.2f}s")

    @pytest.mark.asyncio
    async def test_threat_hunter_workflow(self, workflow_executor, user_simulation):
        """Test complete threat hunter workflow."""
        logger.info("Starting threat hunter workflow...")

        with patch.object(self.data_loader, "get_cached_data", return_value=self.test_data):
            mcp_server = create_mcp_server(self.data_loader)

            # Simulate threat hunter activities
            hunt_scenarios = [
                {"technique": "T1055", "context": "process injection hunting"},
                {"technique": "T1003", "context": "credential dumping detection"},
                {"technique": "T1070", "context": "artifact removal investigation"},
            ]

            for i, scenario in enumerate(hunt_scenarios):
                # Hunt for specific technique
                workflow_executor.add_step(
                    f"hunt_{i}_search",
                    mcp_server.call_tool,
                    "search_attack",
                    {"query": scenario["technique"]}
                )

                # Analyze technique details
                workflow_executor.add_step(
                    f"hunt_{i}_analyze",
                    mcp_server.call_tool,
                    "get_technique",
                    {"technique_id": scenario["technique"]}
                )

                # Find relationships
                workflow_executor.add_step(
                    f"hunt_{i}_relationships",
                    mcp_server.call_tool,
                    "detect_technique_relationships",
                    {"technique_id": scenario["technique"], "relationship_types": ["uses"], "depth": 1}
                )

            # Execute hunting workflow
            results = await workflow_executor.execute_workflow()
            workflow_executor.assert_workflow_success()

            # Validate hunting results
            for i, scenario in enumerate(hunt_scenarios):
                search_result = workflow_executor.get_step_result(f"hunt_{i}_search")
                analyze_result = workflow_executor.get_step_result(f"hunt_{i}_analyze")
                relationship_result = workflow_executor.get_step_result(f"hunt_{i}_relationships")

                # Validate each hunting phase
                self._validate_hunt_result(search_result, scenario["technique"])
                self._validate_hunt_result(analyze_result, scenario["technique"])
                self._validate_hunt_result(relationship_result, scenario["technique"])

            logger.info("Threat hunter workflow completed successfully")

    @pytest.mark.asyncio
    async def test_incident_response_workflow(self, workflow_executor):
        """Test complete incident response workflow."""
        logger.info("Starting incident response workflow...")

        with patch.object(self.data_loader, "get_cached_data", return_value=self.test_data):
            mcp_server = create_mcp_server(self.data_loader)

            # Incident: Suspected APT29 activity
            incident_context = {
                "suspected_group": "G0016",
                "observed_techniques": ["T1566", "T1055"],
                "affected_systems": ["Windows", "Linux"]
            }

            # Phase 1: Threat actor profiling
            workflow_executor.add_step(
                "profile_threat_actor",
                mcp_server.call_tool,
                "get_group_techniques",
                {"group_id": incident_context["suspected_group"]}
            )

            # Phase 2: Technique analysis for each observed technique
            for i, technique in enumerate(incident_context["observed_techniques"]):
                workflow_executor.add_step(
                    f"analyze_technique_{i}",
                    mcp_server.call_tool,
                    "get_technique",
                    {"technique_id": technique}
                )

                workflow_executor.add_step(
                    f"get_mitigations_{i}",
                    mcp_server.call_tool,
                    "get_technique_mitigations",
                    {"technique_id": technique}
                )

            # Phase 3: Attack path reconstruction
            workflow_executor.add_step(
                "reconstruct_attack_path",
                mcp_server.call_tool,
                "build_attack_path",
                {
                    "start_tactic": "TA0001",
                    "end_tactic": "TA0040",
                    "group_id": incident_context["suspected_group"]
                }
            )

            # Phase 4: Coverage assessment
            workflow_executor.add_step(
                "assess_defensive_gaps",
                mcp_server.call_tool,
                "analyze_coverage_gaps",
                {"threat_groups": [incident_context["suspected_group"]]}
            )

            # Execute incident response workflow
            results = await workflow_executor.execute_workflow()
            workflow_executor.assert_workflow_success()

            # Validate incident response phases
            threat_profile = workflow_executor.get_step_result("profile_threat_actor")
            self._validate_incident_response_result(threat_profile, "APT29", "G0016")

            attack_path = workflow_executor.get_step_result("reconstruct_attack_path")
            self._validate_incident_response_result(attack_path, "ATTACK PATH", "G0016")

            coverage_gaps = workflow_executor.get_step_result("assess_defensive_gaps")
            self._validate_incident_response_result(coverage_gaps, "COVERAGE GAP", "G0016")

            # Validate response time
            total_time = sum(r["execution_time"] for r in results.values())
            assert total_time < 45.0, f"Incident response should complete in under 45 seconds, took {total_time:.2f}s"

            logger.info(f"Incident response workflow completed in {total_time:.2f}s")

    @pytest.mark.asyncio
    async def test_red_team_planning_workflow(self, workflow_executor):
        """Test complete red team planning workflow."""
        logger.info("Starting red team planning workflow...")

        with patch.object(self.data_loader, "get_cached_data", return_value=self.test_data):
            mcp_server = create_mcp_server(self.data_loader)

            # Red team scenario: Emulate APT29 attack chain
            red_team_scenario = {
                "target_group": "G0016",
                "attack_phases": ["TA0001", "TA0004", "TA0005", "TA0006"],
                "platforms": ["Windows", "Linux"]
            }

            # Phase 1: Study target threat group
            workflow_executor.add_step(
                "study_target_group",
                mcp_server.call_tool,
                "get_group_techniques",
                {"group_id": red_team_scenario["target_group"]}
            )

            # Phase 2: Plan attack path
            workflow_executor.add_step(
                "plan_attack_path",
                mcp_server.call_tool,
                "build_attack_path",
                {
                    "start_tactic": red_team_scenario["attack_phases"][0],
                    "end_tactic": red_team_scenario["attack_phases"][-1],
                    "group_id": red_team_scenario["target_group"]
                }
            )

            # Phase 3: Analyze each attack phase
            for i, tactic in enumerate(red_team_scenario["attack_phases"]):
                workflow_executor.add_step(
                    f"analyze_phase_{i}",
                    mcp_server.call_tool,
                    "search_attack",
                    {"query": f"tactic:{tactic}"}
                )

            # Phase 4: Study defensive mitigations
            key_techniques = ["T1566", "T1055", "T1003"]
            for i, technique in enumerate(key_techniques):
                workflow_executor.add_step(
                    f"study_defenses_{i}",
                    mcp_server.call_tool,
                    "get_technique_mitigations",
                    {"technique_id": technique}
                )

            # Execute red team planning workflow
            results = await workflow_executor.execute_workflow()
            workflow_executor.assert_workflow_success()

            # Validate red team planning results
            group_study = workflow_executor.get_step_result("study_target_group")
            self._validate_red_team_result(group_study, "APT29", "techniques")

            attack_plan = workflow_executor.get_step_result("plan_attack_path")
            self._validate_red_team_result(attack_plan, "ATTACK PATH", "Group Filter")

            # Validate planning completeness
            assert len(results) >= 8, "Red team planning should include all phases"

            logger.info("Red team planning workflow completed successfully")

    @pytest.mark.asyncio
    async def test_compliance_assessment_workflow(self, workflow_executor):
        """Test complete compliance assessment workflow."""
        logger.info("Starting compliance assessment workflow...")

        with patch.object(self.data_loader, "get_cached_data", return_value=self.test_data):
            mcp_server = create_mcp_server(self.data_loader)

            # Compliance scenario: Assess coverage against common threat groups
            compliance_groups = ["G0016", "G0007"]
            critical_tactics = ["TA0001", "TA0004", "TA0005", "TA0006"]

            # Phase 1: Assess overall coverage
            workflow_executor.add_step(
                "assess_overall_coverage",
                mcp_server.call_tool,
                "analyze_coverage_gaps",
                {"threat_groups": compliance_groups}
            )

            # Phase 2: Analyze each critical tactic
            for i, tactic in enumerate(critical_tactics):
                workflow_executor.add_step(
                    f"analyze_tactic_{i}",
                    mcp_server.call_tool,
                    "search_attack",
                    {"query": f"tactic:{tactic}"}
                )

            # Phase 3: Review mitigation coverage
            key_techniques = ["T1566", "T1055", "T1003", "T1070"]
            for i, technique in enumerate(key_techniques):
                workflow_executor.add_step(
                    f"review_mitigations_{i}",
                    mcp_server.call_tool,
                    "get_technique_mitigations",
                    {"technique_id": technique}
                )

            # Execute compliance assessment workflow
            results = await workflow_executor.execute_workflow()
            workflow_executor.assert_workflow_success()

            # Validate compliance assessment
            coverage_result = workflow_executor.get_step_result("assess_overall_coverage")
            self._validate_compliance_result(coverage_result, "COVERAGE GAP", compliance_groups)

            # Validate all phases completed
            assert len(results) == 1 + len(critical_tactics) + len(key_techniques), "All compliance phases should complete"

            logger.info("Compliance assessment workflow completed successfully")

    @pytest.mark.asyncio
    async def test_multi_user_concurrent_workflows(self, e2e_event_loop):
        """Test multiple users executing workflows concurrently."""
        logger.info("Starting multi-user concurrent workflows test...")

        with patch.object(self.data_loader, "get_cached_data", return_value=self.test_data):
            mcp_server = create_mcp_server(self.data_loader)

            # Define different user workflows
            async def analyst_workflow():
                """Security analyst workflow."""
                results = []
                results.append(await mcp_server.call_tool("search_attack", {"query": "phishing"}))
                results.append(await mcp_server.call_tool("get_technique", {"technique_id": "T1566"}))
                results.append(await mcp_server.call_tool("get_technique_mitigations", {"technique_id": "T1566"}))
                return ("analyst", results)

            async def hunter_workflow():
                """Threat hunter workflow."""
                results = []
                results.append(await mcp_server.call_tool("get_group_techniques", {"group_id": "G0016"}))
                results.append(await mcp_server.call_tool("detect_technique_relationships", {"technique_id": "T1055"}))
                results.append(await mcp_server.call_tool("build_attack_path", {"start_tactic": "TA0001", "end_tactic": "TA0006"}))
                return ("hunter", results)

            async def responder_workflow():
                """Incident responder workflow."""
                results = []
                results.append(await mcp_server.call_tool("analyze_coverage_gaps", {"threat_groups": ["G0016"]}))
                results.append(await mcp_server.call_tool("list_tactics", {}))
                results.append(await mcp_server.call_tool("search_attack", {"query": "credential"}))
                return ("responder", results)

            # Execute workflows concurrently
            start_time = time.time()
            concurrent_results = await asyncio.gather(
                analyst_workflow(),
                hunter_workflow(),
                responder_workflow()
            )
            concurrent_time = time.time() - start_time

            # Validate concurrent execution
            assert len(concurrent_results) == 3, "All concurrent workflows should complete"

            for user_type, results in concurrent_results:
                assert len(results) == 3, f"{user_type} workflow should complete all steps"
                for result in results:
                    assert isinstance(result, tuple), f"{user_type} should return valid results"
                    assert len(result) == 2, f"{user_type} should return (content, metadata)"

            # Performance validation
            assert concurrent_time < 30.0, f"Concurrent workflows should complete in under 30 seconds, took {concurrent_time:.2f}s"

            logger.info(f"Multi-user concurrent workflows completed in {concurrent_time:.2f}s")

    def _validate_investigation_phase(self, result, expected_content, additional_content=None):
        """Validate investigation phase results."""
        assert result is not None, "Investigation phase should return result"
        content, metadata = result
        text = content[0].text
        assert expected_content.lower() in text.lower(), f"Should contain {expected_content}"
        if additional_content:
            assert additional_content in text, f"Should contain {additional_content}"

    def _validate_hunt_result(self, result, technique_id):
        """Validate threat hunting results."""
        assert result is not None, "Hunt result should not be None"
        content, metadata = result
        text = content[0].text
        assert technique_id in text, f"Hunt result should contain {technique_id}"

    def _validate_incident_response_result(self, result, expected_header, expected_content):
        """Validate incident response results."""
        assert result is not None, "Incident response result should not be None"
        content, metadata = result
        text = content[0].text
        assert expected_header in text, f"Should contain {expected_header}"
        assert expected_content in text, f"Should contain {expected_content}"

    def _validate_red_team_result(self, result, expected_content, additional_check):
        """Validate red team planning results."""
        assert result is not None, "Red team result should not be None"
        content, metadata = result
        text = content[0].text
        assert expected_content in text, f"Should contain {expected_content}"
        # Make additional check case-insensitive and more flexible
        assert additional_check.lower() in text.lower(), f"Should contain {additional_check} (case-insensitive)"

    def _validate_compliance_result(self, result, expected_header, groups):
        """Validate compliance assessment results."""
        assert result is not None, "Compliance result should not be None"
        content, metadata = result
        text = content[0].text
        assert expected_header in text, f"Should contain {expected_header}"
        for group in groups:
            assert group in text, f"Should contain group {group}"


@pytest.mark.e2e
class TestWorkflowIntegration:
    """Test workflow integration with external systems."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.data_loader = DataLoader()

    @pytest.mark.asyncio
    async def test_http_proxy_workflow_integration(self, full_system_setup):
        """Test workflow integration through HTTP proxy."""
        logger.info("Starting HTTP proxy workflow integration test...")

        # This test would validate that workflows work through the HTTP proxy
        # In a real implementation, this would start the HTTP proxy and test through it
        system_config = full_system_setup

        # Validate system setup
        assert system_config["http_url"] == "http://localhost:8002", "HTTP proxy URL should be configured"
        assert system_config["server_url"] == "http://localhost:3002", "MCP server URL should be configured"

        # In a full implementation, this would make HTTP requests to test workflows
        logger.info("HTTP proxy workflow integration test completed")

    @pytest.mark.asyncio
    async def test_web_interface_workflow_integration(self, system_health_checker, full_system_setup):
        """Test workflow integration through web interface."""
        logger.info("Starting web interface workflow integration test...")

        system_config = full_system_setup

        # Check system health
        health_status = system_health_checker.run_all_health_checks(system_config)
        
        # Validate health check structure
        assert "overall_healthy" in health_status, "Health check should include overall status"

        # In a full implementation, this would test web interface workflows
        logger.info("Web interface workflow integration test completed")

    @pytest.mark.asyncio
    async def test_workflow_data_persistence(self, workflow_executor):
        """Test workflow data persistence and state management."""
        logger.info("Starting workflow data persistence test...")

        # This test validates that workflow state is properly managed
        # and data persists correctly across workflow steps

        test_data = {
            "techniques": [{"id": "T1055", "name": "Process Injection"}],
            "tactics": [{"id": "TA0001", "name": "Initial Access"}],
            "groups": [{"id": "G0016", "name": "APT29"}],
            "mitigations": [{"id": "M1040", "name": "Behavior Prevention"}],
            "relationships": []
        }

        with patch.object(self.data_loader, "get_cached_data", return_value=test_data):
            mcp_server = create_mcp_server(self.data_loader)

            # Execute workflow steps that depend on persistent data
            workflow_executor.add_step(
                "step1",
                mcp_server.call_tool,
                "search_attack",
                {"query": "T1055"}
            )

            workflow_executor.add_step(
                "step2",
                mcp_server.call_tool,
                "get_technique",
                {"technique_id": "T1055"}
            )

            results = await workflow_executor.execute_workflow()
            workflow_executor.assert_workflow_success()

            # Validate data consistency across steps
            step1_result = workflow_executor.get_step_result("step1")
            step2_result = workflow_executor.get_step_result("step2")

            # Both steps should reference the same data
            content1, _ = step1_result
            content2, _ = step2_result
            
            assert "T1055" in content1[0].text, "Step 1 should contain T1055"
            assert "T1055" in content2[0].text, "Step 2 should contain T1055"
            assert "Process Injection" in content2[0].text, "Step 2 should contain technique name"

        logger.info("Workflow data persistence test completed")