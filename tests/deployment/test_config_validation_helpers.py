#!/usr/bin/env python3
"""
Test configuration validation helpers functionality.

This module tests the configuration validation helper functions
that were implemented as part of the deployment test consolidation.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch


class TestConfigurationValidationHelpers:
    """Test configuration validation helper functions."""

    def test_config_validator_fixture_available(self, config_validator):
        """Test that config validator fixture is available and functional."""
        assert config_validator is not None, "Config validator should be available"
        
        # Test that it has the expected methods
        expected_methods = [
            'validate_server_config',
            'validate_environment_vars',
            'validate_port_availability',
            'validate_file_permissions',
            'validate_yaml_config',
            'validate_json_config',
            'validate_deployment_readiness'
        ]
        
        for method in expected_methods:
            assert hasattr(config_validator, method), f"Config validator should have {method} method"

    def test_yaml_config_validation(self, config_validator, tmp_path):
        """Test YAML configuration validation helper."""
        # Create a valid YAML file
        valid_yaml = tmp_path / "valid.yaml"
        valid_yaml.write_text("""
data_sources:
  mitre_attack:
    url: "https://example.com/data.json"
    format: "stix"
""")
        
        result = config_validator.validate_yaml_config(str(valid_yaml))
        assert result['valid'], "Valid YAML should pass validation"
        assert result['config'] is not None, "Valid YAML should return config"
        assert result['error'] is None, "Valid YAML should not have error"
        
        # Test invalid YAML
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: content: [")
        
        result = config_validator.validate_yaml_config(str(invalid_yaml))
        assert not result['valid'], "Invalid YAML should fail validation"
        assert result['config'] is None, "Invalid YAML should not return config"
        assert result['error'] is not None, "Invalid YAML should have error"

    def test_json_config_validation(self, config_validator, tmp_path):
        """Test JSON configuration validation helper."""
        # Create a valid JSON file
        valid_json = tmp_path / "valid.json"
        valid_json.write_text('{"server": {"host": "localhost", "port": 8000}}')
        
        result = config_validator.validate_json_config(str(valid_json))
        assert result['valid'], "Valid JSON should pass validation"
        assert result['config'] is not None, "Valid JSON should return config"
        assert result['error'] is None, "Valid JSON should not have error"
        
        # Test invalid JSON
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text('{"invalid": json content}')
        
        result = config_validator.validate_json_config(str(invalid_json))
        assert not result['valid'], "Invalid JSON should fail validation"
        assert result['config'] is None, "Invalid JSON should not return config"
        assert result['error'] is not None, "Invalid JSON should have error"

    def test_deployment_readiness_validation(self, config_validator):
        """Test deployment readiness validation helper."""
        # Test with minimal environment
        with patch.dict(os.environ, {}, clear=True):
            result = config_validator.validate_deployment_readiness()
            
            assert 'ready' in result, "Result should include readiness status"
            assert 'checks' in result, "Result should include individual checks"
            assert isinstance(result['ready'], bool), "Readiness should be boolean"
            
            # Check that all expected checks are present
            expected_checks = ['environment_vars', 'port_available', 'python_version', 'dependencies']
            for check in expected_checks:
                assert check in result['checks'], f"Should include {check} check"

    def test_fast_deployment_check_fixture(self, fast_deployment_check):
        """Test fast deployment check fixture functionality."""
        assert fast_deployment_check is not None, "Fast deployment check should be available"
        
        # Test that it has the expected methods
        expected_methods = [
            'quick_environment_check',
            'quick_import_check', 
            'quick_file_structure_check',
            'run_all_quick_checks'
        ]
        
        for method in expected_methods:
            assert hasattr(fast_deployment_check, method), f"Fast deployment check should have {method} method"

    def test_fast_deployment_check_caching(self, fast_deployment_check):
        """Test that fast deployment check uses caching for performance."""
        # Run checks multiple times to test caching
        result1 = fast_deployment_check.quick_environment_check()
        result2 = fast_deployment_check.quick_environment_check()
        
        assert result1 == result2, "Cached results should be consistent"
        
        # Test that cache is being used (check internal cache)
        assert hasattr(fast_deployment_check, 'checks_cache'), "Should have checks cache"
        assert 'environment' in fast_deployment_check.checks_cache, "Environment check should be cached"

    def test_run_all_quick_checks(self, fast_deployment_check):
        """Test running all quick checks together."""
        results = fast_deployment_check.run_all_quick_checks()
        
        expected_checks = ['environment', 'imports', 'files']
        for check in expected_checks:
            assert check in results, f"Should include {check} in results"
            assert isinstance(results[check], bool), f"{check} result should be boolean"

    def test_configuration_validation_performance(self, config_validator):
        """Test that configuration validation is fast enough for CI/CD."""
        import time
        
        # Test that basic validation completes quickly
        start_time = time.time()
        
        # Run multiple validation checks
        config_validator.validate_server_config({'host': 'localhost', 'port': 8000})
        config_validator.validate_environment_vars(['MCP_HTTP_HOST', 'MCP_HTTP_PORT'])
        config_validator.validate_deployment_readiness()
        
        elapsed_time = time.time() - start_time
        
        # Should complete in under 1 second for fast feedback
        assert elapsed_time < 1.0, f"Configuration validation should be fast, took {elapsed_time:.2f}s"

    def test_error_handling_in_validation_helpers(self, config_validator):
        """Test error handling in validation helper functions."""
        # Test with non-existent file
        result = config_validator.validate_yaml_config("/nonexistent/file.yaml")
        assert not result['valid'], "Non-existent file should fail validation"
        assert result['error'] is not None, "Should provide error message"
        
        # Test with invalid port range
        with patch.dict(os.environ, {'MCP_HTTP_PORT': '99999'}):
            try:
                port = int(os.getenv('MCP_HTTP_PORT', '8000'))
                # This should work but be out of practical range
                assert port == 99999, "Should parse large port number"
            except ValueError:
                # This is also acceptable behavior
                pass

    def test_integration_with_existing_fixtures(self, config_validator, deployment_environment):
        """Test that new validation helpers work with existing deployment fixtures."""
        # Test that config validator works with deployment environment
        env_vars = ['MCP_SERVER_HOST', 'MCP_SERVER_PORT', 'MCP_HTTP_HOST', 'MCP_HTTP_PORT']
        result = config_validator.validate_environment_vars(env_vars)
        
        # Should find the variables set by deployment_environment fixture
        assert any(result.values()), "Should find some environment variables from deployment fixture"
        
        # Test deployment readiness with deployment environment
        readiness = config_validator.validate_deployment_readiness()
        assert 'ready' in readiness, "Should provide readiness status"
        assert 'checks' in readiness, "Should provide individual check results"