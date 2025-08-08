"""End-to-end test specific fixtures and configuration."""

import pytest
import asyncio
import time
import json
import logging
from typing import Dict, Any, List
from .test_data_manager import E2ETestDataManager

# Configure logging for E2E tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def e2e_event_loop():
    """Event loop for end-to-end async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def full_system_setup():
    """Set up complete system for end-to-end testing."""
    import subprocess
    import tempfile
    import os
    
    # Create temporary directory for E2E test data
    test_data_dir = tempfile.mkdtemp(prefix='e2e_test_')
    
    # Set up environment for full system
    e2e_env = os.environ.copy()
    e2e_env.update({
        'MCP_SERVER_HOST': 'localhost',
        'MCP_SERVER_PORT': '3002',  # Different port to avoid conflicts
        'MCP_HTTP_HOST': 'localhost',
        'MCP_HTTP_PORT': '8002',    # Different port to avoid conflicts
        'TEST_DATA_DIR': test_data_dir,
        'LOG_LEVEL': 'DEBUG'
    })
    
    yield {
        'env': e2e_env,
        'data_dir': test_data_dir,
        'server_url': 'http://localhost:3002',
        'http_url': 'http://localhost:8002'
    }
    
    # Cleanup
    import shutil
    shutil.rmtree(test_data_dir, ignore_errors=True)


@pytest.fixture
def workflow_executor():
    """Execute complete user workflows for E2E testing."""
    class WorkflowExecutor:
        def __init__(self):
            self.steps = []
            self.results = {}
        
        def add_step(self, name: str, action: callable, *args, **kwargs):
            """Add a step to the workflow."""
            self.steps.append({
                'name': name,
                'action': action,
                'args': args,
                'kwargs': kwargs
            })
        
        async def execute_workflow(self) -> Dict[str, Any]:
            """Execute all workflow steps (async version)."""
            workflow_results = {}
            
            for step in self.steps:
                try:
                    start_time = time.time()
                    result = step['action'](*step['args'], **step['kwargs'])
                    
                    # Handle async results
                    if asyncio.iscoroutine(result):
                        result = await result
                    
                    end_time = time.time()
                    
                    workflow_results[step['name']] = {
                        'success': True,
                        'result': result,
                        'execution_time': end_time - start_time
                    }
                except Exception as e:
                    workflow_results[step['name']] = {
                        'success': False,
                        'error': str(e),
                        'execution_time': 0
                    }
            
            self.results = workflow_results
            return workflow_results
        
        def assert_workflow_success(self):
            """Assert that all workflow steps succeeded."""
            failed_steps = [
                name for name, result in self.results.items() 
                if not result.get('success', False)
            ]
            
            if failed_steps:
                error_details = []
                for step in failed_steps:
                    error = self.results[step].get('error', 'Unknown error')
                    error_details.append(f"{step}: {error}")
                
                pytest.fail(f"Workflow steps failed: {', '.join(error_details)}")
        
        def get_step_result(self, step_name: str):
            """Get result from a specific step."""
            return self.results.get(step_name, {}).get('result')
    
    return WorkflowExecutor()


@pytest.fixture
def user_simulation():
    """Simulate user interactions for E2E testing."""
    class UserSimulation:
        def __init__(self):
            self.session_data = {}
        
        def simulate_search_workflow(self, search_term: str) -> Dict[str, Any]:
            """Simulate a user searching for attack techniques."""
            # This would typically make HTTP requests to the actual system
            return {
                'search_term': search_term,
                'results_found': True,
                'result_count': 5,
                'execution_time': 0.5
            }
        
        def simulate_technique_analysis(self, technique_id: str) -> Dict[str, Any]:
            """Simulate user analyzing a specific technique."""
            return {
                'technique_id': technique_id,
                'details_loaded': True,
                'mitigations_found': True,
                'execution_time': 0.3
            }
        
        def simulate_attack_path_creation(self, start_technique: str, 
                                        end_technique: str) -> Dict[str, Any]:
            """Simulate user creating an attack path."""
            return {
                'start_technique': start_technique,
                'end_technique': end_technique,
                'path_created': True,
                'path_length': 4,
                'execution_time': 2.1
            }
        
        def simulate_coverage_analysis(self, group_id: str) -> Dict[str, Any]:
            """Simulate user performing coverage gap analysis."""
            return {
                'group_id': group_id,
                'analysis_completed': True,
                'gaps_identified': 3,
                'coverage_percentage': 75.5,
                'execution_time': 1.8
            }
    
    return UserSimulation()


@pytest.fixture
def system_health_checker():
    """Check system health during E2E tests."""
    class SystemHealthChecker:
        def __init__(self):
            self.health_checks = []
        
        def check_server_health(self, server_url: str) -> Dict[str, Any]:
            """Check if MCP server is healthy."""
            import requests
            try:
                # This would check actual health endpoint
                response = requests.get(f"{server_url}/health", timeout=5)
                return {
                    'healthy': response.status_code == 200,
                    'response_time': response.elapsed.total_seconds(),
                    'status_code': response.status_code
                }
            except Exception as e:
                return {
                    'healthy': False,
                    'error': str(e)
                }
        
        def check_http_proxy_health(self, proxy_url: str) -> Dict[str, Any]:
            """Check if HTTP proxy is healthy."""
            import requests
            try:
                response = requests.get(f"{proxy_url}/tools", timeout=5)
                return {
                    'healthy': response.status_code == 200,
                    'tools_available': len(response.json()) > 0,
                    'response_time': response.elapsed.total_seconds()
                }
            except Exception as e:
                return {
                    'healthy': False,
                    'error': str(e)
                }
        
        def check_data_availability(self) -> Dict[str, Any]:
            """Check if required data is available."""
            # This would check if MITRE ATT&CK data is loaded
            return {
                'data_loaded': True,
                'technique_count': 100,
                'group_count': 50,
                'tactic_count': 14
            }
        
        def run_all_health_checks(self, system_config: Dict[str, str]) -> Dict[str, Any]:
            """Run all health checks."""
            results = {}
            
            if 'server_url' in system_config:
                results['server'] = self.check_server_health(system_config['server_url'])
            
            if 'http_url' in system_config:
                results['http_proxy'] = self.check_http_proxy_health(system_config['http_url'])
            
            results['data'] = self.check_data_availability()
            
            # Overall health
            all_healthy = all(
                check.get('healthy', False) 
                for check in results.values()
            )
            results['overall_healthy'] = all_healthy
            
            return results
    
    return SystemHealthChecker()


@pytest.fixture
def e2e_test_data_manager():
    """Provide E2E test data manager with caching and optimization."""
    return E2ETestDataManager()


@pytest.fixture
def e2e_test_data(e2e_test_data_manager):
    """Provide comprehensive test data for E2E scenarios."""
    return e2e_test_data_manager.get_comprehensive_test_data()


@pytest.fixture
def workflow_scenarios(e2e_test_data_manager):
    """Provide predefined workflow scenarios for testing."""
    return e2e_test_data_manager.get_workflow_scenarios()


@pytest.fixture
def performance_test_data(e2e_test_data_manager):
    """Provide performance-optimized test data."""
    return e2e_test_data_manager.get_performance_test_data()


@pytest.fixture
def error_test_scenarios(e2e_test_data_manager):
    """Provide error handling test scenarios."""
    return e2e_test_data_manager.get_error_test_scenarios()


@pytest.fixture
def e2e_test_timeout():
    """Extended timeout for end-to-end tests."""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("End-to-end test exceeded maximum execution time")
    
    # Set 600 second (10 minute) timeout for E2E tests
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(600)
    
    yield
    
    # Clear the alarm
    signal.alarm(0)


@pytest.fixture
def e2e_test_manager():
    """Comprehensive E2E test management and optimization."""
    class E2ETestManager:
        def __init__(self):
            self.test_start_time = None
            self.test_data_cache = {}
            self.performance_metrics = {}
            self.cleanup_tasks = []
        
        def start_test(self, test_name: str):
            """Start test timing and setup."""
            self.test_start_time = time.time()
            logger.info(f"Starting E2E test: {test_name}")
        
        def end_test(self, test_name: str):
            """End test and record metrics."""
            if self.test_start_time:
                duration = time.time() - self.test_start_time
                self.performance_metrics[test_name] = duration
                logger.info(f"E2E test {test_name} completed in {duration:.2f}s")
        
        def cache_test_data(self, key: str, data: Any):
            """Cache test data for reuse across test steps."""
            self.test_data_cache[key] = data
        
        def get_cached_data(self, key: str) -> Any:
            """Retrieve cached test data."""
            return self.test_data_cache.get(key)
        
        def add_cleanup_task(self, task: callable):
            """Add cleanup task to be executed after test."""
            self.cleanup_tasks.append(task)
        
        def cleanup(self):
            """Execute all cleanup tasks."""
            for task in self.cleanup_tasks:
                try:
                    task()
                except Exception as e:
                    logger.warning(f"Cleanup task failed: {e}")
            self.cleanup_tasks.clear()
        
        def get_performance_summary(self) -> Dict[str, float]:
            """Get performance metrics summary."""
            return self.performance_metrics.copy()
    
    manager = E2ETestManager()
    yield manager
    manager.cleanup()


@pytest.fixture
def optimized_test_data():
    """Optimized test data for E2E scenarios with efficient loading."""
    # Pre-computed test data to avoid repeated generation
    return {
        'comprehensive_data': {
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
                },
            ],
            "tactics": [
                {"id": "TA0001", "name": "Initial Access", "description": "The adversary is trying to get into your network."},
                {"id": "TA0002", "name": "Execution", "description": "The adversary is trying to run malicious code."},
                {"id": "TA0004", "name": "Privilege Escalation", "description": "The adversary is trying to gain higher-level permissions."},
                {"id": "TA0005", "name": "Defense Evasion", "description": "The adversary is trying to avoid being detected."},
                {"id": "TA0006", "name": "Credential Access", "description": "The adversary is trying to steal account names and passwords."},
                {"id": "TA0040", "name": "Impact", "description": "The adversary is trying to manipulate, interrupt, or destroy your systems and data."},
            ],
            "groups": [
                {
                    "id": "G0016",
                    "name": "APT29",
                    "description": "APT29 is threat group that has been attributed to Russia's Foreign Intelligence Service.",
                    "aliases": ["APT29", "Cozy Bear", "The Dukes"],
                    "techniques": ["T1566", "T1055", "T1003", "T1070", "T1190"],
                },
                {
                    "id": "G0007",
                    "name": "APT28",
                    "description": "APT28 is a threat group that has been attributed to Russia's General Staff Main Intelligence Directorate.",
                    "aliases": ["APT28", "Fancy Bear", "Pawn Storm"],
                    "techniques": ["T1566", "T1055", "T1003", "T1190"],
                },
                {
                    "id": "G0032",
                    "name": "Lazarus Group",
                    "description": "Lazarus Group is a North Korean state-sponsored cyber threat group.",
                    "aliases": ["Lazarus Group", "HIDDEN COBRA", "Zinc"],
                    "techniques": ["T1055", "T1190", "T1003"],
                },
            ],
            "mitigations": [
                {"id": "M1031", "name": "Network Intrusion Prevention", "description": "Use intrusion detection signatures to block traffic at network boundaries."},
                {"id": "M1017", "name": "User Training", "description": "Train users to identify social engineering techniques and spear phishing emails."},
                {"id": "M1040", "name": "Behavior Prevention on Endpoint", "description": "Use capabilities to prevent suspicious behavior patterns from occurring on endpoint systems."},
                {"id": "M1026", "name": "Privileged Account Management", "description": "Manage the creation, modification, use, and permissions associated to privileged accounts."},
                {"id": "M1027", "name": "Password Policies", "description": "Set and enforce secure password policies for accounts."},
                {"id": "M1043", "name": "Credential Access Protection", "description": "Use capabilities to prevent successful credential access by adversaries."},
                {"id": "M1029", "name": "Remote Data Storage", "description": "Use remote security log and sensitive file storage where access can be controlled better."},
                {"id": "M1022", "name": "Restrict File and Directory Permissions", "description": "Restrict access by setting directory and file permissions."},
                {"id": "M1048", "name": "Application Isolation and Sandboxing", "description": "Restrict execution of code to a virtual environment on or in transit to an endpoint system."},
                {"id": "M1030", "name": "Network Segmentation", "description": "Architect sections of the network to isolate critical systems and functions."},
            ],
            "relationships": [
                {"relationship_type": "uses", "source_ref": "intrusion-set--g0016-stix-id", "target_ref": "attack-pattern--t1566-stix-id"},
                {"relationship_type": "uses", "source_ref": "intrusion-set--g0007-stix-id", "target_ref": "attack-pattern--t1566-stix-id"},
                {"relationship_type": "uses", "source_ref": "intrusion-set--g0032-stix-id", "target_ref": "attack-pattern--t1055-stix-id"},
                {"relationship_type": "mitigates", "source_ref": "course-of-action--m1031-stix-id", "target_ref": "attack-pattern--t1566-stix-id"},
                {"relationship_type": "mitigates", "source_ref": "course-of-action--m1040-stix-id", "target_ref": "attack-pattern--t1055-stix-id"},
            ],
        },
        'performance_scenarios': [
            {'name': 'quick_search', 'query': 'phishing', 'expected_time': 1.0},
            {'name': 'technique_analysis', 'technique_id': 'T1055', 'expected_time': 2.0},
            {'name': 'group_analysis', 'group_id': 'G0016', 'expected_time': 2.5},
            {'name': 'attack_path', 'start': 'TA0001', 'end': 'TA0040', 'expected_time': 3.0},
            {'name': 'coverage_analysis', 'groups': ['G0016', 'G0007'], 'expected_time': 4.0},
        ],
        'workflow_scenarios': [
            {
                'name': 'threat_analysis',
                'steps': [
                    {'tool': 'search_attack', 'params': {'query': 'injection'}},
                    {'tool': 'get_technique', 'params': {'technique_id': 'T1055'}},
                    {'tool': 'get_technique_mitigations', 'params': {'technique_id': 'T1055'}},
                ],
                'expected_duration': 5.0
            },
            {
                'name': 'incident_response',
                'steps': [
                    {'tool': 'get_group_techniques', 'params': {'group_id': 'G0016'}},
                    {'tool': 'build_attack_path', 'params': {'start_tactic': 'TA0001', 'end_tactic': 'TA0006'}},
                    {'tool': 'analyze_coverage_gaps', 'params': {'threat_groups': ['G0016']}},
                ],
                'expected_duration': 8.0
            },
        ]
    }


@pytest.fixture(autouse=True)
def e2e_test_isolation():
    """Ensure E2E tests are properly isolated with efficient cleanup."""
    # Pre-test setup
    import gc
    
    # Force garbage collection before test
    gc.collect()
    
    yield
    
    # Post-test cleanup (more efficient)
    gc.collect()  # Clean up test objects
    time.sleep(0.1)  # Minimal cleanup delay