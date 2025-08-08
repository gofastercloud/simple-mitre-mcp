"""Deployment test specific fixtures and configuration."""

import pytest
import os
import tempfile
import subprocess
import json
from typing import Dict, Any


@pytest.fixture
def deployment_environment():
    """Set up deployment test environment."""
    # Create temporary deployment directory
    deploy_dir = tempfile.mkdtemp(prefix='deploy_test_')
    
    # Store original environment
    original_env = os.environ.copy()
    
    # Set deployment-specific environment variables
    deployment_env = {
        'DEPLOYMENT_ENV': 'test',
        'MCP_SERVER_HOST': '0.0.0.0',
        'MCP_SERVER_PORT': '3000',
        'MCP_HTTP_HOST': '0.0.0.0',
        'MCP_HTTP_PORT': '8000',
        'LOG_LEVEL': 'INFO',
        'PYTHONPATH': os.getcwd()
    }
    
    for key, value in deployment_env.items():
        os.environ[key] = value
    
    yield {
        'deploy_dir': deploy_dir,
        'env': deployment_env
    }
    
    # Cleanup
    os.environ.clear()
    os.environ.update(original_env)
    
    import shutil
    shutil.rmtree(deploy_dir, ignore_errors=True)


@pytest.fixture
def docker_environment():
    """Docker environment for deployment testing."""
    def check_docker_available():
        """Check if Docker is available."""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    if not check_docker_available():
        pytest.skip("Docker not available for deployment testing")
    
    return {
        'available': True,
        'check_command': ['docker', 'ps'],
        'build_command': ['docker', 'build', '-t', 'test-mcp-server', '.'],
        'run_command': ['docker', 'run', '-d', '--name', 'test-mcp-server', 
                       '-p', '3000:3000', '-p', '8000:8000', 'test-mcp-server']
    }


@pytest.fixture
def config_validator():
    """Configuration validation utilities."""
    class ConfigValidator:
        def validate_server_config(self, config: Dict[str, Any]) -> bool:
            """Validate server configuration."""
            required_keys = ['host', 'port']
            return all(key in config for key in required_keys)
        
        def validate_environment_vars(self, required_vars: list) -> Dict[str, bool]:
            """Validate required environment variables."""
            return {var: var in os.environ for var in required_vars}
        
        def validate_port_availability(self, host: str, port: int) -> bool:
            """Check if a port is available."""
            import socket
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((host, port))
                    return result != 0  # Port is available if connection fails
            except Exception:
                return False
        
        def validate_file_permissions(self, file_path: str, required_perms: str) -> bool:
            """Validate file permissions."""
            if not os.path.exists(file_path):
                return False
            
            import stat
            file_stat = os.stat(file_path)
            file_perms = stat.filemode(file_stat.st_mode)
            
            # Simple permission check (could be more sophisticated)
            return 'r' in required_perms and 'r' in file_perms
    
    return ConfigValidator()


@pytest.fixture
def process_manager():
    """Process management utilities for deployment testing."""
    class ProcessManager:
        def __init__(self):
            self.processes = []
        
        def start_process(self, command: list, env: Dict[str, str] = None) -> subprocess.Popen:
            """Start a process and track it."""
            process = subprocess.Popen(
                command,
                env=env or os.environ.copy(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(process)
            return process
        
        def wait_for_process_ready(self, process: subprocess.Popen, 
                                 ready_indicator: str = "Server started", 
                                 timeout: int = 30) -> bool:
            """Wait for process to be ready."""
            import time
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if process.poll() is not None:
                    # Process has terminated
                    return False
                
                # Check if ready indicator appears in output
                # This is a simplified check - real implementation might be more complex
                time.sleep(0.5)
            
            return process.poll() is None  # Process is still running
        
        def cleanup(self):
            """Clean up all tracked processes."""
            for process in self.processes:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception:
                    pass
            self.processes.clear()
    
    manager = ProcessManager()
    yield manager
    manager.cleanup()


@pytest.fixture
def network_tester():
    """Network testing utilities."""
    class NetworkTester:
        def test_http_endpoint(self, url: str, expected_status: int = 200, 
                             timeout: int = 10) -> Dict[str, Any]:
            """Test HTTP endpoint availability."""
            import requests
            try:
                response = requests.get(url, timeout=timeout)
                return {
                    'available': True,
                    'status_code': response.status_code,
                    'success': response.status_code == expected_status,
                    'response_time': response.elapsed.total_seconds()
                }
            except requests.RequestException as e:
                return {
                    'available': False,
                    'error': str(e),
                    'success': False
                }
        
        def test_port_connectivity(self, host: str, port: int, timeout: int = 5) -> bool:
            """Test if a port is reachable."""
            import socket
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(timeout)
                    result = s.connect_ex((host, port))
                    return result == 0
            except Exception:
                return False
        
        def test_dns_resolution(self, hostname: str) -> bool:
            """Test DNS resolution."""
            import socket
            try:
                socket.gethostbyname(hostname)
                return True
            except socket.gaierror:
                return False
    
    return NetworkTester()


@pytest.fixture
def deployment_test_timeout():
    """Extended timeout for deployment tests."""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Deployment test exceeded maximum execution time")
    
    # Set 180 second (3 minute) timeout for deployment tests
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(180)
    
    yield
    
    # Clear the alarm
    signal.alarm(0)