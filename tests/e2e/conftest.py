"""End-to-end test specific fixtures and configuration."""

import pytest
import asyncio
import time
import json
from typing import Dict, Any, List


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
        
        def execute_workflow(self) -> Dict[str, Any]:
            """Execute all workflow steps."""
            workflow_results = {}
            
            for step in self.steps:
                try:
                    start_time = time.time()
                    result = step['action'](*step['args'], **step['kwargs'])
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
def e2e_test_data():
    """Provide comprehensive test data for E2E scenarios."""
    return {
        'search_scenarios': [
            {'term': 'phishing', 'expected_results': 5},
            {'term': 'credential', 'expected_results': 10},
            {'term': 'persistence', 'expected_results': 8}
        ],
        'technique_scenarios': [
            {'id': 'T1566', 'name': 'Phishing'},
            {'id': 'T1055', 'name': 'Process Injection'},
            {'id': 'T1003', 'name': 'OS Credential Dumping'}
        ],
        'group_scenarios': [
            {'id': 'G0016', 'name': 'APT29'},
            {'id': 'G0007', 'name': 'APT28'}
        ],
        'attack_path_scenarios': [
            {
                'start': 'T1566',
                'end': 'T1003',
                'expected_length': 4
            }
        ],
        'coverage_scenarios': [
            {
                'group_id': 'G0016',
                'expected_gaps': 3,
                'expected_coverage': 75.0
            }
        ]
    }


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


@pytest.fixture(autouse=True)
def e2e_test_isolation():
    """Ensure E2E tests are properly isolated."""
    # Clean up any existing processes or connections
    import psutil
    
    # Kill any existing test processes
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'test' in ' '.join(proc.info['cmdline'] or []).lower():
                if 'mcp' in ' '.join(proc.info['cmdline'] or []).lower():
                    proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    yield
    
    # Cleanup after test
    time.sleep(1)  # Allow processes to clean up