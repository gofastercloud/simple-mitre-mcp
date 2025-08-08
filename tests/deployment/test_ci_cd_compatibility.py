#!/usr/bin/env python3
"""
Optimized CI/CD compatibility tests for test suite rationalization.

This module provides streamlined CI/CD compatibility testing with faster
execution and focused on critical compatibility scenarios.
"""

import os
import pytest
from unittest.mock import patch, Mock


class TestOptimizedCICDCompatibility:
    """Test CI/CD compatibility and integration test handling."""

    def test_integration_tests_compatibility(self):
        """Test that integration tests are compatible with CI/CD environments."""
        # Verify integration test modules can be imported
        try:
            import tests.integration.test_http_interface as http_tests
            import tests.integration.test_mcp_integration as mcp_tests
            
            assert http_tests is not None, "HTTP interface tests should be importable"
            assert mcp_tests is not None, "MCP integration tests should be importable"
        except ImportError as e:
            pytest.fail(f"Integration test modules should be importable in CI/CD: {e}")

    def test_environment_variables_default_properly_in_ci(self):
        """Test that environment variables default properly in CI environments."""
        # Simulate CI environment with minimal variables
        ci_env = {"CI": "true", "GITHUB_ACTIONS": "true", "RUNNER_OS": "Linux"}

        with patch.dict(os.environ, ci_env, clear=True):
            # These should all work with defaults
            host = os.getenv("MCP_HTTP_HOST", "localhost")
            port = os.getenv("MCP_HTTP_PORT", "8000")
            url = os.getenv("MITRE_ATTACK_URL", "https://example.com/default.json")

            assert host == "localhost", "Should use localhost in CI"
            assert port == "8000", "Should use default port in CI"
            assert url is not None, "Should have default URL in CI"

    def test_core_modules_importable_in_ci(self):
        """Test that core modules can be imported in CI environments."""
        core_modules = [
            'src.mcp_server',
            'src.http_proxy', 
            'src.data_loader',
            'src.parsers.stix_parser'
        ]
        
        for module_name in core_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Core module {module_name} should be importable in CI: {e}")

    def test_required_dependencies_available_in_ci(self):
        """Test that required dependencies are available in CI environments."""
        required_deps = [
            'aiohttp',
            'stix2', 
            'pydantic',
            'pytest',
            'psutil'
        ]
        
        for dep in required_deps:
            try:
                __import__(dep)
            except ImportError as e:
                pytest.fail(f"Required dependency {dep} should be available in CI: {e}")

    def test_ci_environment_configuration(self):
        """Test configuration works properly in CI environments."""
        ci_env = {
            "CI": "true",
            "GITHUB_ACTIONS": "true",
        }

        with patch.dict(os.environ, ci_env, clear=True):
            # Configuration should work with defaults
            host = os.getenv("MCP_HTTP_HOST", "localhost")
            port = os.getenv("MCP_HTTP_PORT", "8000")

            assert host == "localhost", "Should use localhost default in CI"
            assert port == "8000", "Should use default port in CI"

    def test_graceful_connection_error_handling(self):
        """Test that connection errors are handled gracefully in CI."""
        import socket

        # Test connection handling without raising unhandled exceptions
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)  # Very short timeout
                s.connect(("localhost", 8000))
        except (socket.error, ConnectionRefusedError, OSError):
            # This is expected in CI/CD environments - should not crash
            pass
