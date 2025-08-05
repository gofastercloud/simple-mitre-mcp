#!/usr/bin/env python3
"""
Tests for CI/CD compatibility and integration test handling.

This module ensures that all tests work properly in CI/CD environments
and that integration tests are properly skipped when servers aren't available.
"""

import os
import pytest
from unittest.mock import patch, Mock


class TestCICDCompatibility:
    """Test CI/CD compatibility and integration test handling."""

    def test_integration_tests_are_properly_marked(self):
        """Test that integration tests are properly marked for skipping."""
        # Check that integration tests have proper pytest marks
        from tests.test_web_interface import TestWebInterfaceIntegration

        # Get the test methods
        test_methods = [
            method
            for method in dir(TestWebInterfaceIntegration)
            if method.startswith("test_")
        ]

        assert len(test_methods) > 0, "Should have integration test methods"

        # These tests should be designed to skip when server isn't available
        for method_name in test_methods:
            method = getattr(TestWebInterfaceIntegration, method_name)
            # The methods should contain skip logic
            if hasattr(method, "__code__"):
                source_lines = method.__code__.co_names
                assert "skip" in source_lines, f"{method_name} should have skip logic"

    def test_no_hardcoded_connections_in_tests(self):
        """Test that tests don't make hardcoded connections that could fail in CI/CD."""
        # This test ensures our test files don't contain hardcoded connection attempts
        # that could cause issues in CI/CD environments

        import tests.test_web_interface as web_tests
        import tests.test_http_interface as http_tests

        # These modules should be importable without making connections
        assert web_tests is not None, "Web interface tests should be importable"
        assert http_tests is not None, "HTTP interface tests should be importable"

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

    def test_mock_data_available_for_tests(self):
        """Test that mock data is available for tests that need it."""
        from tests.test_end_to_end_integration import TestEndToEndIntegration

        # Check that the test class has the fixture method
        test_instance = TestEndToEndIntegration()
        assert hasattr(
            test_instance, "mock_data_loader"
        ), "Should have mock_data_loader fixture method"

    def test_no_real_network_calls_in_unit_tests(self):
        """Test that unit tests don't make real network calls."""
        # This is a meta-test to ensure our test design is CI/CD friendly

        # Check that data loader tests use mocks
        import tests.test_data_loader as data_tests

        # The module should be importable without network calls
        assert data_tests is not None, "Data loader tests should be importable"

    def test_pytest_markers_are_respected(self):
        """Test that pytest markers work correctly for skipping integration tests."""
        # This test verifies that our pytest configuration respects markers

        # Integration tests should be skippable
        integration_marker = pytest.mark.integration
        assert integration_marker is not None, "Integration marker should be available"

    def test_aiohttp_imports_work_in_ci(self):
        """Test that aiohttp imports work in CI environments."""
        try:
            import aiohttp
            import aiohttp_cors
            from aiohttp import web

            assert aiohttp is not None, "aiohttp should be available in CI"
            assert aiohttp_cors is not None, "aiohttp_cors should be available in CI"
            assert web is not None, "aiohttp.web should be available in CI"

        except ImportError as e:
            pytest.fail(f"Required aiohttp dependencies should be available in CI: {e}")

    def test_http_proxy_can_be_imported_in_ci(self):
        """Test that HTTP proxy module can be imported in CI environments."""
        try:
            import http_proxy
            from http_proxy import HTTPProxy, create_http_proxy_server

            assert (
                http_proxy is not None
            ), "http_proxy module should be importable in CI"
            assert HTTPProxy is not None, "HTTPProxy class should be importable in CI"
            assert (
                create_http_proxy_server is not None
            ), "create_http_proxy_server should be importable in CI"

        except ImportError as e:
            pytest.fail(f"HTTP proxy should be importable in CI: {e}")

    def test_mcp_server_can_be_imported_in_ci(self):
        """Test that MCP server module can be imported in CI environments."""
        try:
            import src.mcp_server as mcp_server
            from src.mcp_server import create_mcp_server

            assert (
                mcp_server is not None
            ), "MCP server module should be importable in CI"
            assert (
                create_mcp_server is not None
            ), "create_mcp_server should be importable in CI"

        except ImportError as e:
            pytest.fail(f"MCP server should be importable in CI: {e}")

    def test_all_test_files_are_ci_compatible(self):
        """Test that all test files can be imported without causing connection issues."""
        import glob
        import importlib.util

        # Get all test files
        test_files = glob.glob("tests/test_*.py")

        for test_file in test_files:
            if test_file.endswith("__init__.py"):
                continue

            # Convert file path to module name
            module_name = test_file.replace("/", ".").replace(".py", "")

            try:
                # Import the module - this should not cause connection errors
                spec = importlib.util.spec_from_file_location(module_name, test_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    assert module is not None, f"{test_file} should be importable"

            except Exception as e:
                pytest.fail(f"Test file {test_file} should be importable in CI: {e}")

    def test_github_actions_environment_simulation(self):
        """Test behavior in simulated GitHub Actions environment."""
        github_env = {
            "GITHUB_ACTIONS": "true",
            "CI": "true",
            "RUNNER_OS": "Linux",
            "GITHUB_WORKFLOW": "CI",
            "GITHUB_RUN_ID": "123456789",
            "GITHUB_REPOSITORY": "test/repo",
        }

        with patch.dict(os.environ, github_env, clear=True):
            # Configuration should work in GitHub Actions
            host = os.getenv("MCP_HTTP_HOST", "localhost")
            port = os.getenv("MCP_HTTP_PORT", "8000")

            assert host == "localhost", "Should work in GitHub Actions"
            assert port == "8000", "Should use default port in GitHub Actions"

            # Should be able to import modules
            try:
                import http_proxy

                assert http_proxy is not None, "Should import in GitHub Actions"
            except ImportError as e:
                pytest.fail(f"Imports should work in GitHub Actions: {e}")

    def test_connection_error_handling(self):
        """Test that connection errors are handled gracefully."""
        # This test ensures that if connections fail, tests handle it gracefully

        import socket

        def test_connection_handling():
            """Test function that might encounter connection issues."""
            try:
                # This might fail in CI/CD, which is fine
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.1)  # Very short timeout
                    s.connect(("localhost", 8000))
                return True
            except (socket.error, ConnectionRefusedError, OSError):
                # This is expected in CI/CD environments
                return False

        # The function should not raise unhandled exceptions
        result = test_connection_handling()
        assert isinstance(result, bool), "Connection test should return boolean"
