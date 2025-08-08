"""Base test classes and shared utilities for the test suite."""

import logging
import pytest
import tempfile
import os
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch


class BaseTestCase:
    """Base test class with common setup and utilities."""
    
    @pytest.fixture(autouse=True)
    def setup_logging(self):
        """Configure test logging to suppress noise during tests."""
        logging.getLogger().setLevel(logging.CRITICAL)
        # Suppress specific loggers that are noisy during tests
        logging.getLogger('urllib3').setLevel(logging.CRITICAL)
        logging.getLogger('requests').setLevel(logging.CRITICAL)
        logging.getLogger('httpx').setLevel(logging.CRITICAL)
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up clean test environment variables."""
        # Store original environment
        self.original_env = os.environ.copy()
        
        # Set test-specific environment variables
        os.environ['MCP_SERVER_HOST'] = 'localhost'
        os.environ['MCP_SERVER_PORT'] = '3001'  # Different from default to avoid conflicts
        os.environ['MCP_HTTP_HOST'] = 'localhost'
        os.environ['MCP_HTTP_PORT'] = '8001'  # Different from default to avoid conflicts
        
        yield
        
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def assert_valid_response(self, response: Dict[str, Any], expected_keys: List[str]):
        """Common response validation for MCP tool responses.
        
        Args:
            response: The response dictionary to validate
            expected_keys: List of keys that must be present in the response
        """
        assert isinstance(response, dict), f"Response must be a dictionary, got {type(response)}"
        
        for key in expected_keys:
            assert key in response, f"Response missing required key: {key}"
        
        # Check for common error indicators
        if 'error' in response:
            pytest.fail(f"Response contains error: {response['error']}")
    
    def assert_valid_technique(self, technique: Dict[str, Any]):
        """Validate that a technique object has required fields.
        
        Args:
            technique: Technique dictionary to validate
        """
        required_fields = ['id', 'name', 'description']
        for field in required_fields:
            assert field in technique, f"Technique missing required field: {field}"
        
        # For STIX objects, check if external_references contains MITRE ID
        if 'external_references' in technique:
            mitre_refs = [ref for ref in technique['external_references'] 
                         if ref.get('source_name') == 'mitre-attack']
            if mitre_refs and 'external_id' in mitre_refs[0]:
                mitre_id = mitre_refs[0]['external_id']
                assert mitre_id.startswith('T'), f"Invalid technique ID format: {mitre_id}"
        # For simplified objects, check ID directly
        elif technique['id'].startswith('T'):
            assert technique['id'].startswith('T'), f"Invalid technique ID format: {technique['id']}"
    
    def assert_valid_group(self, group: Dict[str, Any]):
        """Validate that a group object has required fields.
        
        Args:
            group: Group dictionary to validate
        """
        required_fields = ['id', 'name', 'description']
        for field in required_fields:
            assert field in group, f"Group missing required field: {field}"
        
        # For STIX objects, check if external_references contains MITRE ID
        if 'external_references' in group:
            mitre_refs = [ref for ref in group['external_references'] 
                         if ref.get('source_name') == 'mitre-attack']
            if mitre_refs and 'external_id' in mitre_refs[0]:
                mitre_id = mitre_refs[0]['external_id']
                assert mitre_id.startswith('G'), f"Invalid group ID format: {mitre_id}"
        # For simplified objects, check ID directly
        elif group['id'].startswith('G'):
            assert group['id'].startswith('G'), f"Invalid group ID format: {group['id']}"
    
    def assert_valid_tactic(self, tactic: Dict[str, Any]):
        """Validate that a tactic object has required fields.
        
        Args:
            tactic: Tactic dictionary to validate
        """
        required_fields = ['id', 'name', 'description']
        for field in required_fields:
            assert field in tactic, f"Tactic missing required field: {field}"
        
        # For STIX objects, check if external_references contains MITRE ID
        if 'external_references' in tactic:
            mitre_refs = [ref for ref in tactic['external_references'] 
                         if ref.get('source_name') == 'mitre-attack']
            if mitre_refs and 'external_id' in mitre_refs[0]:
                mitre_id = mitre_refs[0]['external_id']
                assert mitre_id.startswith('TA'), f"Invalid tactic ID format: {mitre_id}"
        # For simplified objects, check ID directly
        elif tactic['id'].startswith('TA'):
            assert tactic['id'].startswith('TA'), f"Invalid tactic ID format: {tactic['id']}"
    
    def create_temp_file(self, content: str, suffix: str = '.json') -> str:
        """Create a temporary file with given content.
        
        Args:
            content: Content to write to the file
            suffix: File suffix/extension
            
        Returns:
            Path to the created temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up a temporary file.
        
        Args:
            file_path: Path to the file to delete
        """
        try:
            os.unlink(file_path)
        except FileNotFoundError:
            pass  # File already deleted


class BaseMCPTestCase(BaseTestCase):
    """Base class for MCP tool tests with common MCP-specific utilities."""
    
    @pytest.fixture
    def mock_data_loader(self):
        """Shared mock data loader for MCP tests."""
        mock_loader = Mock()
        mock_loader.get_techniques.return_value = []
        mock_loader.get_groups.return_value = []
        mock_loader.get_tactics.return_value = []
        mock_loader.get_mitigations.return_value = []
        mock_loader.search_entities.return_value = []
        return mock_loader
    
    @pytest.fixture
    def mock_mcp_server(self):
        """Mock MCP server for testing tool interactions."""
        with patch('src.mcp_server.app') as mock_app:
            yield mock_app
    
    def create_mock_technique(self, technique_id: str = "T1055", **overrides) -> Dict[str, Any]:
        """Create a mock technique object for testing.
        
        Args:
            technique_id: The technique ID
            **overrides: Additional fields to override
            
        Returns:
            Mock technique dictionary
        """
        technique = {
            'id': technique_id,
            'name': f'Test Technique {technique_id}',
            'description': f'Description for {technique_id}',
            'tactics': ['initial-access', 'execution'],
            'platforms': ['Windows', 'Linux'],
            'data_sources': ['Process monitoring', 'File monitoring'],
            'mitigations': [],
            'detection': 'Monitor for suspicious process activity'
        }
        technique.update(overrides)
        return technique
    
    def create_mock_group(self, group_id: str = "G0016", **overrides) -> Dict[str, Any]:
        """Create a mock group object for testing.
        
        Args:
            group_id: The group ID
            **overrides: Additional fields to override
            
        Returns:
            Mock group dictionary
        """
        group = {
            'id': group_id,
            'name': f'Test Group {group_id}',
            'description': f'Description for {group_id}',
            'aliases': [f'Alias for {group_id}'],
            'techniques': [],
            'software': [],
            'references': []
        }
        group.update(overrides)
        return group
    
    def create_mock_tactic(self, tactic_id: str = "TA0001", **overrides) -> Dict[str, Any]:
        """Create a mock tactic object for testing.
        
        Args:
            tactic_id: The tactic ID
            **overrides: Additional fields to override
            
        Returns:
            Mock tactic dictionary
        """
        tactic = {
            'id': tactic_id,
            'name': f'Test Tactic {tactic_id}',
            'description': f'Description for {tactic_id}',
            'short_name': tactic_id.lower().replace('ta', 'tactic-'),
            'techniques': []
        }
        tactic.update(overrides)
        return tactic
    
    def assert_mcp_tool_response(self, response: Dict[str, Any], tool_name: str):
        """Validate MCP tool response format.
        
        Args:
            response: The tool response to validate
            tool_name: Name of the tool that generated the response
        """
        # Basic response structure validation
        assert isinstance(response, dict), f"{tool_name} response must be a dictionary"
        
        # Check for error conditions
        if 'error' in response:
            raise AssertionError(f"{tool_name} returned error: {response['error']}")
        
        # Validate response has content
        assert len(response) > 0, f"{tool_name} returned empty response"


class BaseIntegrationTestCase(BaseTestCase):
    """Base class for integration tests with setup for component interactions."""
    
    @pytest.fixture(autouse=True)
    def setup_integration_environment(self):
        """Set up environment for integration testing."""
        # Additional setup for integration tests
        self.test_data_dir = tempfile.mkdtemp()
        yield
        # Cleanup
        import shutil
        shutil.rmtree(self.test_data_dir, ignore_errors=True)
    
    def wait_for_server_ready(self, host: str, port: int, timeout: int = 10):
        """Wait for a server to be ready for connections.
        
        Args:
            host: Server host
            port: Server port
            timeout: Maximum time to wait in seconds
        """
        import socket
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                sock.close()
                if result == 0:
                    return True
            except Exception:
                pass
            time.sleep(0.1)
        
        return False


class BasePerformanceTestCase(BaseTestCase):
    """Base class for performance tests with timing and benchmarking utilities."""
    
    def measure_execution_time(self, func, *args, **kwargs):
        """Measure execution time of a function.
        
        Args:
            func: Function to measure
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Tuple of (result, execution_time_seconds)
        """
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        return result, end_time - start_time
    
    def assert_performance_threshold(self, execution_time: float, threshold: float, operation: str):
        """Assert that execution time is within performance threshold.
        
        Args:
            execution_time: Actual execution time in seconds
            threshold: Maximum allowed time in seconds
            operation: Description of the operation being measured
        """
        assert execution_time <= threshold, (
            f"{operation} took {execution_time:.3f}s, "
            f"which exceeds threshold of {threshold:.3f}s"
        )
    
    @pytest.fixture
    def performance_monitor(self):
        """Fixture for monitoring performance during tests."""
        import psutil
        import time
        
        process = psutil.Process()
        start_memory = process.memory_info().rss
        start_time = time.time()
        
        yield
        
        end_time = time.time()
        end_memory = process.memory_info().rss
        
        # Log performance metrics
        execution_time = end_time - start_time
        memory_delta = end_memory - start_memory
        
        print(f"Test execution time: {execution_time:.3f}s")
        print(f"Memory delta: {memory_delta / 1024 / 1024:.2f}MB")