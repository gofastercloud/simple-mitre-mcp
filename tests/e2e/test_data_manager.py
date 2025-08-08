"""
E2E Test Data Management.

This module provides efficient test data management for E2E scenarios,
including data caching, scenario generation, and performance optimization.
"""

import json
import time
import hashlib
from typing import Dict, Any, List, Optional
from pathlib import Path


class E2ETestDataManager:
    """Manages test data for E2E scenarios with caching and optimization."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize test data manager."""
        self.cache_dir = cache_dir or Path(__file__).parent / ".test_data_cache"
        self.cache_dir.mkdir(exist_ok=True)
        self._data_cache = {}
        self._scenario_cache = {}

    def get_comprehensive_test_data(self) -> Dict[str, Any]:
        """Get comprehensive test data for E2E scenarios."""
        cache_key = "comprehensive_data"
        
        if cache_key in self._data_cache:
            return self._data_cache[cache_key]

        data = {
            "techniques": [
                {
                    "id": "T1566",
                    "name": "Phishing",
                    "description": "Adversaries may send phishing messages to gain access to victim systems.",
                    "tactics": ["TA0001"],
                    "platforms": ["Windows", "macOS", "Linux"],
                    "mitigations": ["M1031", "M1017"],
                    "data_sources": ["Application Log: Application Log Content", "Network Traffic: Network Traffic Content"],
                    "detection": "Monitor for suspicious email attachments and links.",
                    "kill_chain_phases": ["initial-access"],
                },
                {
                    "id": "T1055",
                    "name": "Process Injection",
                    "description": "Adversaries may inject code into processes to evade process-based defenses.",
                    "tactics": ["TA0004", "TA0005"],
                    "platforms": ["Windows", "macOS", "Linux"],
                    "mitigations": ["M1040", "M1026"],
                    "data_sources": ["Process: Process Creation", "Process: OS API Execution"],
                    "detection": "Monitor for process injection techniques and API calls.",
                    "kill_chain_phases": ["privilege-escalation", "defense-evasion"],
                },
                {
                    "id": "T1003",
                    "name": "OS Credential Dumping",
                    "description": "Adversaries may attempt to dump credentials to obtain account login information.",
                    "tactics": ["TA0006"],
                    "platforms": ["Windows", "Linux", "macOS"],
                    "mitigations": ["M1027", "M1043"],
                    "data_sources": ["Command: Command Execution", "File: File Access"],
                    "detection": "Monitor for credential dumping tools and techniques.",
                    "kill_chain_phases": ["credential-access"],
                },
                {
                    "id": "T1070",
                    "name": "Indicator Removal on Host",
                    "description": "Adversaries may delete or alter generated artifacts on a host system.",
                    "tactics": ["TA0005"],
                    "platforms": ["Windows", "Linux", "macOS"],
                    "mitigations": ["M1029", "M1022"],
                    "data_sources": ["File: File Deletion", "File: File Modification"],
                    "detection": "Monitor for file deletion and modification activities.",
                    "kill_chain_phases": ["defense-evasion"],
                },
                {
                    "id": "T1190",
                    "name": "Exploit Public-Facing Application",
                    "description": "Adversaries may attempt to take advantage of a weakness in an Internet-facing computer or program.",
                    "tactics": ["TA0001"],
                    "platforms": ["Windows", "Linux", "macOS"],
                    "mitigations": ["M1048", "M1030"],
                    "data_sources": ["Application Log: Application Log Content", "Network Traffic: Network Traffic Content"],
                    "detection": "Monitor for exploitation attempts against public-facing applications.",
                    "kill_chain_phases": ["initial-access"],
                },
                {
                    "id": "T1059",
                    "name": "Command and Scripting Interpreter",
                    "description": "Adversaries may abuse command and script interpreters to execute commands.",
                    "tactics": ["TA0002"],
                    "platforms": ["Windows", "Linux", "macOS"],
                    "mitigations": ["M1038", "M1042"],
                    "data_sources": ["Command: Command Execution", "Process: Process Creation"],
                    "detection": "Monitor for command and script interpreter usage.",
                    "kill_chain_phases": ["execution"],
                },
            ],
            "tactics": [
                {"id": "TA0001", "name": "Initial Access", "description": "The adversary is trying to get into your network.", "order": 1},
                {"id": "TA0002", "name": "Execution", "description": "The adversary is trying to run malicious code.", "order": 2},
                {"id": "TA0004", "name": "Privilege Escalation", "description": "The adversary is trying to gain higher-level permissions.", "order": 4},
                {"id": "TA0005", "name": "Defense Evasion", "description": "The adversary is trying to avoid being detected.", "order": 5},
                {"id": "TA0006", "name": "Credential Access", "description": "The adversary is trying to steal account names and passwords.", "order": 6},
                {"id": "TA0040", "name": "Impact", "description": "The adversary is trying to manipulate, interrupt, or destroy your systems and data.", "order": 14},
            ],
            "groups": [
                {
                    "id": "G0016",
                    "name": "APT29",
                    "description": "APT29 is threat group that has been attributed to Russia's Foreign Intelligence Service.",
                    "aliases": ["APT29", "Cozy Bear", "The Dukes"],
                    "techniques": ["T1566", "T1055", "T1003", "T1070", "T1190", "T1059"],
                    "country": "Russia",
                    "sophistication": "high",
                },
                {
                    "id": "G0007",
                    "name": "APT28",
                    "description": "APT28 is a threat group that has been attributed to Russia's General Staff Main Intelligence Directorate.",
                    "aliases": ["APT28", "Fancy Bear", "Pawn Storm"],
                    "techniques": ["T1566", "T1055", "T1003", "T1190", "T1059"],
                    "country": "Russia",
                    "sophistication": "high",
                },
                {
                    "id": "G0032",
                    "name": "Lazarus Group",
                    "description": "Lazarus Group is a North Korean state-sponsored cyber threat group.",
                    "aliases": ["Lazarus Group", "HIDDEN COBRA", "Zinc"],
                    "techniques": ["T1055", "T1190", "T1003", "T1070"],
                    "country": "North Korea",
                    "sophistication": "high",
                },
            ],
            "mitigations": [
                {"id": "M1031", "name": "Network Intrusion Prevention", "description": "Use intrusion detection signatures to block traffic at network boundaries.", "effectiveness": "high"},
                {"id": "M1017", "name": "User Training", "description": "Train users to identify social engineering techniques and spear phishing emails.", "effectiveness": "medium"},
                {"id": "M1040", "name": "Behavior Prevention on Endpoint", "description": "Use capabilities to prevent suspicious behavior patterns from occurring on endpoint systems.", "effectiveness": "high"},
                {"id": "M1026", "name": "Privileged Account Management", "description": "Manage the creation, modification, use, and permissions associated to privileged accounts.", "effectiveness": "high"},
                {"id": "M1027", "name": "Password Policies", "description": "Set and enforce secure password policies for accounts.", "effectiveness": "medium"},
                {"id": "M1043", "name": "Credential Access Protection", "description": "Use capabilities to prevent successful credential access by adversaries.", "effectiveness": "high"},
                {"id": "M1029", "name": "Remote Data Storage", "description": "Use remote security log and sensitive file storage where access can be controlled better.", "effectiveness": "medium"},
                {"id": "M1022", "name": "Restrict File and Directory Permissions", "description": "Restrict access by setting directory and file permissions.", "effectiveness": "medium"},
                {"id": "M1048", "name": "Application Isolation and Sandboxing", "description": "Restrict execution of code to a virtual environment on or in transit to an endpoint system.", "effectiveness": "high"},
                {"id": "M1030", "name": "Network Segmentation", "description": "Architect sections of the network to isolate critical systems and functions.", "effectiveness": "high"},
                {"id": "M1038", "name": "Execution Prevention", "description": "Block execution of code on a system through application control.", "effectiveness": "high"},
                {"id": "M1042", "name": "Disable or Remove Feature or Program", "description": "Remove or deny access to unnecessary and potentially vulnerable software.", "effectiveness": "medium"},
            ],
            "relationships": [
                {"relationship_type": "uses", "source_ref": "intrusion-set--g0016-stix-id", "target_ref": "attack-pattern--t1566-stix-id", "confidence": "high"},
                {"relationship_type": "uses", "source_ref": "intrusion-set--g0007-stix-id", "target_ref": "attack-pattern--t1566-stix-id", "confidence": "high"},
                {"relationship_type": "uses", "source_ref": "intrusion-set--g0032-stix-id", "target_ref": "attack-pattern--t1055-stix-id", "confidence": "high"},
                {"relationship_type": "mitigates", "source_ref": "course-of-action--m1031-stix-id", "target_ref": "attack-pattern--t1566-stix-id", "confidence": "high"},
                {"relationship_type": "mitigates", "source_ref": "course-of-action--m1040-stix-id", "target_ref": "attack-pattern--t1055-stix-id", "confidence": "high"},
                {"relationship_type": "mitigates", "source_ref": "course-of-action--m1027-stix-id", "target_ref": "attack-pattern--t1003-stix-id", "confidence": "medium"},
            ],
        }

        self._data_cache[cache_key] = data
        return data

    def get_workflow_scenarios(self) -> List[Dict[str, Any]]:
        """Get predefined workflow scenarios for testing."""
        cache_key = "workflow_scenarios"
        
        if cache_key in self._scenario_cache:
            return self._scenario_cache[cache_key]

        scenarios = [
            {
                "name": "security_analyst_investigation",
                "description": "Complete security analyst investigation workflow",
                "steps": [
                    {"tool": "search_attack", "params": {"query": "phishing"}, "expected_time": 1.0},
                    {"tool": "get_technique", "params": {"technique_id": "T1566"}, "expected_time": 1.5},
                    {"tool": "get_technique_mitigations", "params": {"technique_id": "T1566"}, "expected_time": 1.5},
                    {"tool": "get_group_techniques", "params": {"group_id": "G0016"}, "expected_time": 2.0},
                    {"tool": "analyze_coverage_gaps", "params": {"threat_groups": ["G0016"]}, "expected_time": 3.0},
                ],
                "expected_total_time": 10.0,
                "success_criteria": ["phishing", "T1566", "M1031", "APT29", "coverage"],
            },
            {
                "name": "threat_hunter_workflow",
                "description": "Threat hunter investigation and analysis workflow",
                "steps": [
                    {"tool": "search_attack", "params": {"query": "process injection"}, "expected_time": 1.0},
                    {"tool": "get_technique", "params": {"technique_id": "T1055"}, "expected_time": 1.5},
                    {"tool": "detect_technique_relationships", "params": {"technique_id": "T1055", "depth": 2}, "expected_time": 2.5},
                    {"tool": "build_attack_path", "params": {"start_tactic": "TA0001", "end_tactic": "TA0005"}, "expected_time": 3.0},
                ],
                "expected_total_time": 8.0,
                "success_criteria": ["injection", "T1055", "relationship", "attack path"],
            },
            {
                "name": "incident_response_workflow",
                "description": "Incident response and containment workflow",
                "steps": [
                    {"tool": "get_group_techniques", "params": {"group_id": "G0016"}, "expected_time": 2.0},
                    {"tool": "build_attack_path", "params": {"start_tactic": "TA0001", "end_tactic": "TA0040", "group_id": "G0016"}, "expected_time": 3.0},
                    {"tool": "analyze_coverage_gaps", "params": {"threat_groups": ["G0016", "G0007"]}, "expected_time": 3.5},
                    {"tool": "get_technique_mitigations", "params": {"technique_id": "T1055"}, "expected_time": 1.5},
                ],
                "expected_total_time": 10.0,
                "success_criteria": ["APT29", "attack path", "coverage gap", "mitigation"],
            },
            {
                "name": "red_team_planning",
                "description": "Red team attack planning and emulation workflow",
                "steps": [
                    {"tool": "get_group_techniques", "params": {"group_id": "G0007"}, "expected_time": 2.0},
                    {"tool": "build_attack_path", "params": {"start_tactic": "TA0001", "end_tactic": "TA0006", "group_id": "G0007"}, "expected_time": 3.0},
                    {"tool": "list_tactics", "params": {}, "expected_time": 1.0},
                    {"tool": "detect_technique_relationships", "params": {"technique_id": "T1566", "depth": 1}, "expected_time": 2.0},
                ],
                "expected_total_time": 8.0,
                "success_criteria": ["APT28", "attack path", "tactics", "relationship"],
            },
            {
                "name": "compliance_assessment",
                "description": "Security compliance and coverage assessment workflow",
                "steps": [
                    {"tool": "analyze_coverage_gaps", "params": {"threat_groups": ["G0016", "G0007", "G0032"]}, "expected_time": 4.0},
                    {"tool": "list_tactics", "params": {}, "expected_time": 1.0},
                    {"tool": "get_technique_mitigations", "params": {"technique_id": "T1566"}, "expected_time": 1.5},
                    {"tool": "get_technique_mitigations", "params": {"technique_id": "T1055"}, "expected_time": 1.5},
                ],
                "expected_total_time": 8.0,
                "success_criteria": ["coverage gap", "tactics", "mitigation", "assessment"],
            },
        ]

        self._scenario_cache[cache_key] = scenarios
        return scenarios

    def get_performance_test_data(self) -> Dict[str, Any]:
        """Get test data optimized for performance testing."""
        return {
            "quick_scenarios": [
                {"tool": "search_attack", "params": {"query": "T1055"}, "max_time": 1.0},
                {"tool": "get_technique", "params": {"technique_id": "T1055"}, "max_time": 1.5},
                {"tool": "list_tactics", "params": {}, "max_time": 1.0},
                {"tool": "get_group_techniques", "params": {"group_id": "G0016"}, "max_time": 2.0},
            ],
            "medium_scenarios": [
                {"tool": "get_technique_mitigations", "params": {"technique_id": "T1055"}, "max_time": 2.0},
                {"tool": "build_attack_path", "params": {"start_tactic": "TA0001", "end_tactic": "TA0005"}, "max_time": 3.0},
            ],
            "complex_scenarios": [
                {"tool": "analyze_coverage_gaps", "params": {"threat_groups": ["G0016", "G0007"]}, "max_time": 4.0},
                {"tool": "detect_technique_relationships", "params": {"technique_id": "T1055", "depth": 2}, "max_time": 3.0},
            ],
        }

    def get_error_test_scenarios(self) -> List[Dict[str, Any]]:
        """Get test scenarios for error handling validation."""
        return [
            {
                "name": "invalid_technique_id",
                "tool": "get_technique",
                "params": {"technique_id": "T9999"},
                "expected_error_indicators": ["not found", "invalid", "does not exist"],
            },
            {
                "name": "invalid_group_id",
                "tool": "get_group_techniques",
                "params": {"group_id": "G9999"},
                "expected_error_indicators": ["not found", "invalid", "does not exist"],
            },
            {
                "name": "invalid_tactic_id",
                "tool": "build_attack_path",
                "params": {"start_tactic": "TA9999", "end_tactic": "TA9998"},
                "expected_error_indicators": ["not found", "invalid", "unable to build"],
            },
            {
                "name": "empty_search_query",
                "tool": "search_attack",
                "params": {"query": ""},
                "expected_error_indicators": ["empty", "invalid", "no query"],
            },
            {
                "name": "nonexistent_search_term",
                "tool": "search_attack",
                "params": {"query": "nonexistent_technique_xyz_123"},
                "expected_error_indicators": ["no results", "not found", "no matches"],
            },
        ]

    def generate_stress_test_data(self, num_scenarios: int = 100) -> List[Dict[str, Any]]:
        """Generate stress test scenarios for load testing."""
        import random
        
        techniques = ["T1055", "T1566", "T1003", "T1070", "T1190", "T1059"]
        groups = ["G0016", "G0007", "G0032"]
        tactics = ["TA0001", "TA0002", "TA0004", "TA0005", "TA0006", "TA0040"]
        search_terms = ["injection", "phishing", "credential", "evasion", "access", "execution"]

        scenarios = []
        for i in range(num_scenarios):
            scenario_type = random.choice(["search", "technique", "group", "attack_path", "coverage"])
            
            if scenario_type == "search":
                scenario = {
                    "id": f"stress_{i}",
                    "tool": "search_attack",
                    "params": {"query": random.choice(search_terms)},
                }
            elif scenario_type == "technique":
                scenario = {
                    "id": f"stress_{i}",
                    "tool": "get_technique",
                    "params": {"technique_id": random.choice(techniques)},
                }
            elif scenario_type == "group":
                scenario = {
                    "id": f"stress_{i}",
                    "tool": "get_group_techniques",
                    "params": {"group_id": random.choice(groups)},
                }
            elif scenario_type == "attack_path":
                start_tactic = random.choice(tactics)
                end_tactic = random.choice([t for t in tactics if t != start_tactic])
                scenario = {
                    "id": f"stress_{i}",
                    "tool": "build_attack_path",
                    "params": {"start_tactic": start_tactic, "end_tactic": end_tactic},
                }
            else:  # coverage
                selected_groups = random.sample(groups, random.randint(1, len(groups)))
                scenario = {
                    "id": f"stress_{i}",
                    "tool": "analyze_coverage_gaps",
                    "params": {"threat_groups": selected_groups},
                }
            
            scenarios.append(scenario)
        
        return scenarios

    def cache_scenario_results(self, scenario_name: str, results: Dict[str, Any]):
        """Cache scenario results for analysis."""
        cache_file = self.cache_dir / f"{scenario_name}_results.json"
        
        # Add timestamp and performance metrics
        cached_data = {
            "timestamp": time.time(),
            "scenario_name": scenario_name,
            "results": results,
            "performance_summary": self._calculate_performance_summary(results),
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cached_data, f, indent=2)

    def load_cached_results(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """Load cached scenario results."""
        cache_file = self.cache_dir / f"{scenario_name}_results.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def _calculate_performance_summary(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate performance summary from results."""
        if not results:
            return {}
        
        execution_times = []
        for result in results.values():
            if isinstance(result, dict) and "execution_time" in result:
                execution_times.append(result["execution_time"])
        
        if not execution_times:
            return {}
        
        return {
            "total_time": sum(execution_times),
            "average_time": sum(execution_times) / len(execution_times),
            "min_time": min(execution_times),
            "max_time": max(execution_times),
            "num_operations": len(execution_times),
        }

    def validate_scenario_results(self, scenario: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, bool]:
        """Validate scenario results against success criteria."""
        validation_results = {}
        
        if "success_criteria" not in scenario:
            return {"no_criteria": True}
        
        for criterion in scenario["success_criteria"]:
            found = False
            for result in results.values():
                if isinstance(result, dict) and "result" in result:
                    step_result = result["result"]
                    if isinstance(step_result, tuple) and len(step_result) == 2:
                        content, metadata = step_result
                        if hasattr(content[0], "text"):
                            text = content[0].text.lower()
                            if criterion.lower() in text:
                                found = True
                                break
            
            validation_results[criterion] = found
        
        return validation_results

    def cleanup_cache(self, max_age_hours: int = 24):
        """Clean up old cached data."""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                file_age = current_time - cache_file.stat().st_mtime
                if file_age > max_age_seconds:
                    cache_file.unlink()
            except (OSError, IOError):
                pass  # Ignore errors during cleanup