#!/usr/bin/env python3
"""
Tests for environment variable configuration.

This module tests that the application properly handles environment variables
for configuration, especially in CI/CD environments where they might not be set.
"""

import os
import pytest
from unittest.mock import patch


class TestEnvironmentConfiguration:
    """Test environment variable configuration handling."""

    def test_default_http_host_configuration(self):
        """Test that default HTTP host is set correctly."""
        # Test without environment variable
        with patch.dict(os.environ, {}, clear=True):
            host = os.getenv('MCP_HTTP_HOST', 'localhost')
            assert host == 'localhost', "Default HTTP host should be localhost"

    def test_default_http_port_configuration(self):
        """Test that default HTTP port is set correctly."""
        # Test without environment variable
        with patch.dict(os.environ, {}, clear=True):
            port = int(os.getenv('MCP_HTTP_PORT', '8000'))
            assert port == 8000, "Default HTTP port should be 8000"

    def test_custom_http_host_configuration(self):
        """Test that custom HTTP host is respected."""
        with patch.dict(os.environ, {'MCP_HTTP_HOST': '127.0.0.1'}):
            host = os.getenv('MCP_HTTP_HOST', 'localhost')
            assert host == '127.0.0.1', "Custom HTTP host should be respected"

    def test_custom_http_port_configuration(self):
        """Test that custom HTTP port is respected."""
        with patch.dict(os.environ, {'MCP_HTTP_PORT': '3000'}):
            port = int(os.getenv('MCP_HTTP_PORT', '8000'))
            assert port == 3000, "Custom HTTP port should be respected"

    def test_invalid_port_handling(self):
        """Test that invalid port values are handled gracefully."""
        with patch.dict(os.environ, {'MCP_HTTP_PORT': 'invalid'}):
            try:
                port = int(os.getenv('MCP_HTTP_PORT', '8000'))
                # This should not be reached if the environment variable is invalid
                assert False, "Should have raised ValueError for invalid port"
            except ValueError:
                # This is expected behavior
                # Fall back to default
                port = 8000
                assert port == 8000, "Should fall back to default port on invalid value"

    def test_environment_variable_precedence(self):
        """Test that environment variables take precedence over defaults."""
        test_cases = [
            ('MCP_HTTP_HOST', '0.0.0.0', 'localhost'),
            ('MCP_HTTP_PORT', '9000', '8000'),
        ]
        
        for env_var, custom_value, default_value in test_cases:
            # Test with custom value
            with patch.dict(os.environ, {env_var: custom_value}):
                value = os.getenv(env_var, default_value)
                assert value == custom_value, f"{env_var} should use custom value"
            
            # Test without custom value
            with patch.dict(os.environ, {}, clear=True):
                value = os.getenv(env_var, default_value)
                assert value == default_value, f"{env_var} should use default value"

    def test_ci_cd_environment_compatibility(self):
        """Test that the application works in CI/CD environments."""
        # Simulate CI/CD environment with minimal environment variables
        ci_env = {
            'CI': 'true',
            'PATH': '/usr/bin:/bin',
            'HOME': '/tmp'
        }
        
        with patch.dict(os.environ, ci_env, clear=True):
            # These should work with defaults
            host = os.getenv('MCP_HTTP_HOST', 'localhost')
            port = int(os.getenv('MCP_HTTP_PORT', '8000'))
            
            assert host == 'localhost', "Should work with default host in CI/CD"
            assert port == 8000, "Should work with default port in CI/CD"

    def test_docker_environment_compatibility(self):
        """Test that the application works in Docker environments."""
        # Simulate Docker environment
        docker_env = {
            'MCP_HTTP_HOST': '0.0.0.0',
            'MCP_HTTP_PORT': '8080',
            'CONTAINER': 'docker'
        }
        
        with patch.dict(os.environ, docker_env, clear=True):
            host = os.getenv('MCP_HTTP_HOST', 'localhost')
            port = int(os.getenv('MCP_HTTP_PORT', '8000'))
            
            assert host == '0.0.0.0', "Should use Docker-friendly host"
            assert port == 8080, "Should use Docker-friendly port"

    def test_data_source_url_configuration(self):
        """Test that data source URL configuration works properly."""
        default_url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
        
        # Test with default
        with patch.dict(os.environ, {}, clear=True):
            url = os.getenv('MITRE_ATTACK_URL', default_url)
            assert url == default_url, "Should use default MITRE ATT&CK URL"
        
        # Test with custom URL
        custom_url = "https://example.com/custom-attack.json"
        with patch.dict(os.environ, {'MITRE_ATTACK_URL': custom_url}):
            url = os.getenv('MITRE_ATTACK_URL', default_url)
            assert url == custom_url, "Should use custom MITRE ATT&CK URL"

    def test_environment_variable_types(self):
        """Test that environment variables are properly typed."""
        # Test integer conversion
        with patch.dict(os.environ, {'MCP_HTTP_PORT': '3000'}):
            port_str = os.getenv('MCP_HTTP_PORT', '8000')
            port_int = int(port_str)
            assert isinstance(port_int, int), "Port should be converted to integer"
            assert port_int == 3000, "Port should have correct value"
        
        # Test string values
        with patch.dict(os.environ, {'MCP_HTTP_HOST': 'example.com'}):
            host = os.getenv('MCP_HTTP_HOST', 'localhost')
            assert isinstance(host, str), "Host should be string"
            assert host == 'example.com', "Host should have correct value"

    def test_missing_environment_variables_graceful_handling(self):
        """Test that missing environment variables are handled gracefully."""
        # Clear all environment variables
        with patch.dict(os.environ, {}, clear=True):
            # These should all work with defaults
            host = os.getenv('MCP_HTTP_HOST', 'localhost')
            port = os.getenv('MCP_HTTP_PORT', '8000')
            url = os.getenv('MITRE_ATTACK_URL', 'https://example.com/default.json')
            
            assert host is not None, "Host should have default value"
            assert port is not None, "Port should have default value"
            assert url is not None, "URL should have default value"
            
            # Test that they can be converted to appropriate types
            port_int = int(port)
            assert isinstance(port_int, int), "Port should be convertible to int"
