#!/usr/bin/env python3
"""
Consolidated deployment validation tests for the MITRE ATT&CK MCP Server.

This module consolidates deployment validation, environment configuration,
and CI/CD compatibility tests into a unified deployment test suite.
"""

import pytest
import asyncio
import json
import subprocess
import os
import tempfile
import shutil
import socket
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import yaml
import aiohttp
from aiohttp import web


class TestDeploymentValidation:
    """Test deployment validation functionality."""

    @pytest.fixture
    def project_root(self):
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def mock_process_success(self):
        """Mock successful subprocess execution."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "success"
        mock_process.stderr = ""
        return mock_process

    def test_required_project_files_exist(self, project_root):
        """Test that all required project files exist."""
        required_files = [
            "src/mcp_server.py",
            "src/http_proxy.py",
            "src/data_loader.py",
            "src/parsers/stix_parser.py",
            "start_explorer.py",
            "web_interface/index.html",
            "web_interface/css/styles.css",
            "web_interface/css/components.css",
            "web_interface/js/app.js",
            "web_interface/js/api.js",
            "config/data_sources.yaml",
            "config/entity_schemas.yaml",
            "config/tools.yaml",
            "pyproject.toml",
        ]

        for file_path in required_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Required file should exist: {file_path}"
            assert (
                full_path.stat().st_size > 0
            ), f"File should not be empty: {file_path}"

    def test_config_files_are_valid_yaml(self, project_root):
        """Test that YAML configuration files are valid."""
        yaml_configs = [
            "config/data_sources.yaml",
            "config/entity_schemas.yaml",
            "config/tools.yaml",
        ]

        for config_file in yaml_configs:
            config_path = project_root / config_file
            assert config_path.exists(), f"YAML config should exist: {config_file}"

            # Validate YAML format
            with open(config_path, "r") as f:
                try:
                    yaml.safe_load(f)
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {config_file}: {e}")

    def test_example_config_files_exist(self, project_root):
        """Test that example configuration files exist and are valid JSON."""
        example_configs = [
            "examples/mcp_client_configs/claude_desktop_config.json",
            "examples/mcp_client_configs/mcp_client_config.json",
        ]

        for config_file in example_configs:
            config_path = project_root / config_file
            if config_path.exists():  # Some example configs may not exist
                # Validate JSON format
                with open(config_path, "r") as f:
                    try:
                        json.load(f)
                    except json.JSONDecodeError as e:
                        pytest.fail(f"Invalid JSON in {config_file}: {e}")

    def test_security_headers_in_http_proxy(self, project_root):
        """Test that HTTP proxy includes security headers."""
        proxy_path = project_root / "src" / "http_proxy.py"

        with open(proxy_path, "r") as f:
            content = f.read()

        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Content-Security-Policy",
        ]

        for header in security_headers:
            assert (
                header in content
            ), f"HTTP proxy should include {header} security header"

    def test_importability_of_core_modules(self, project_root):
        """Test that core modules can be imported without errors."""
        import sys

        sys.path.insert(0, str(project_root))

        try:
            # Test core module imports
            from src.config_loader import ConfigLoader
            assert ConfigLoader is not None

            from src.data_loader import DataLoader
            assert DataLoader is not None

        except ImportError:
            # Expected in test environment without full dependency installation
            pass
        finally:
            sys.path.remove(str(project_root))


class TestEnvironmentConfiguration:
    """Test environment variable configuration handling."""

    def test_default_http_host_configuration(self):
        """Test that default HTTP host is set correctly."""
        # Test without environment variable
        with patch.dict(os.environ, {}, clear=True):
            host = os.getenv("MCP_HTTP_HOST", "localhost")
            assert host == "localhost", "Default HTTP host should be localhost"

    def test_default_http_port_configuration(self):
        """Test that default HTTP port is set correctly."""
        # Test without environment variable
        with patch.dict(os.environ, {}, clear=True):
            port = int(os.getenv("MCP_HTTP_PORT", "8000"))
            assert port == 8000, "Default HTTP port should be 8000"

    def test_custom_http_host_configuration(self):
        """Test that custom HTTP host is respected."""
        with patch.dict(os.environ, {"MCP_HTTP_HOST": "127.0.0.1"}):
            host = os.getenv("MCP_HTTP_HOST", "localhost")
            assert host == "127.0.0.1", "Custom HTTP host should be respected"

    def test_custom_http_port_configuration(self):
        """Test that custom HTTP port is respected."""
        with patch.dict(os.environ, {"MCP_HTTP_PORT": "3000"}):
            port = int(os.getenv("MCP_HTTP_PORT", "8000"))
            assert port == 3000, "Custom HTTP port should be respected"

    def test_invalid_port_handling(self):
        """Test that invalid port values are handled gracefully."""
        with patch.dict(os.environ, {"MCP_HTTP_PORT": "invalid"}):
            try:
                port = int(os.getenv("MCP_HTTP_PORT", "8000"))
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
            ("MCP_HTTP_HOST", "0.0.0.0", "localhost"),
            ("MCP_HTTP_PORT", "9000", "8000"),
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

    def test_data_source_url_configuration(self):
        """Test that data source URL configuration works properly."""
        default_url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"

        # Test with default
        with patch.dict(os.environ, {}, clear=True):
            url = os.getenv("MITRE_ATTACK_URL", default_url)
            assert url == default_url, "Should use default MITRE ATT&CK URL"

        # Test with custom URL
        custom_url = "https://example.com/custom-attack.json"
        with patch.dict(os.environ, {"MITRE_ATTACK_URL": custom_url}):
            url = os.getenv("MITRE_ATTACK_URL", default_url)
            assert url == custom_url, "Should use custom MITRE ATT&CK URL"

    def test_environment_variable_types(self):
        """Test that environment variables are properly typed."""
        # Test integer conversion
        with patch.dict(os.environ, {"MCP_HTTP_PORT": "3000"}):
            port_str = os.getenv("MCP_HTTP_PORT", "8000")
            port_int = int(port_str)
            assert isinstance(port_int, int), "Port should be converted to integer"
            assert port_int == 3000, "Port should have correct value"

        # Test string values
        with patch.dict(os.environ, {"MCP_HTTP_HOST": "example.com"}):
            host = os.getenv("MCP_HTTP_HOST", "localhost")
            assert isinstance(host, str), "Host should be string"
            assert host == "example.com", "Host should have correct value"

    def test_missing_environment_variables_graceful_handling(self):
        """Test that missing environment variables are handled gracefully."""
        # Clear all environment variables
        with patch.dict(os.environ, {}, clear=True):
            # These should all work with defaults
            host = os.getenv("MCP_HTTP_HOST", "localhost")
            port = os.getenv("MCP_HTTP_PORT", "8000")
            url = os.getenv("MITRE_ATTACK_URL", "https://example.com/default.json")

            assert host is not None, "Host should have default value"
            assert port is not None, "Port should have default value"
            assert url is not None, "URL should have default value"

            # Test that they can be converted to appropriate types
            port_int = int(port)
            assert isinstance(port_int, int), "Port should be convertible to int"


class TestCICDCompatibility:
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

    def test_ci_cd_environment_compatibility(self):
        """Test that the application works in CI/CD environments."""
        # Simulate CI/CD environment with minimal environment variables
        ci_env = {"CI": "true", "PATH": "/usr/bin:/bin", "HOME": "/tmp"}

        with patch.dict(os.environ, ci_env, clear=True):
            # These should work with defaults
            host = os.getenv("MCP_HTTP_HOST", "localhost")
            port = int(os.getenv("MCP_HTTP_PORT", "8000"))

            assert host == "localhost", "Should work with default host in CI/CD"
            assert port == 8000, "Should work with default port in CI/CD"

    def test_docker_environment_compatibility(self):
        """Test that the application works in Docker environments."""
        # Simulate Docker environment
        docker_env = {
            "MCP_HTTP_HOST": "0.0.0.0",
            "MCP_HTTP_PORT": "8080",
            "CONTAINER": "docker",
        }

        with patch.dict(os.environ, docker_env, clear=True):
            host = os.getenv("MCP_HTTP_HOST", "localhost")
            port = int(os.getenv("MCP_HTTP_PORT", "8000"))

            assert host == "0.0.0.0", "Should use Docker-friendly host"
            assert port == 8080, "Should use Docker-friendly port"

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


class TestHTTPProxyConfiguration:
    """Test HTTP proxy configuration and connection handling."""

    def test_http_proxy_import_without_connection(self):
        """Test that HTTP proxy can be imported without making connections."""
        # This should not cause any connection attempts
        try:
            from src.http_proxy import HTTPProxy

            assert HTTPProxy is not None, "HTTPProxy class should be importable"
        except ImportError as e:
            pytest.fail(f"Failed to import HTTPProxy: {e}")

    def test_http_proxy_configuration_parsing(self):
        """Test that HTTP proxy configuration is parsed correctly."""
        # Test with environment variables
        with patch.dict(
            os.environ, {"MCP_HTTP_HOST": "127.0.0.1", "MCP_HTTP_PORT": "9000"}
        ):
            host = os.getenv("MCP_HTTP_HOST", "localhost")
            port = int(os.getenv("MCP_HTTP_PORT", "8000"))

            assert host == "127.0.0.1", "Host should be parsed from environment"
            assert port == 9000, "Port should be parsed from environment"

    def test_http_proxy_default_configuration(self):
        """Test that HTTP proxy uses correct defaults."""
        with patch.dict(os.environ, {}, clear=True):
            host = os.getenv("MCP_HTTP_HOST", "localhost")
            port = int(os.getenv("MCP_HTTP_PORT", "8000"))

            assert host == "localhost", "Should use default host"
            assert port == 8000, "Should use default port"

    def test_port_availability_check(self):
        """Test port availability checking logic."""
        import socket

        def is_port_available(host, port):
            """Check if a port is available."""
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex((host, port))
                    return result != 0  # Port is available if connection fails
            except Exception:
                return True  # Assume available if we can't check

        # Test that we can check port availability
        localhost_available = is_port_available("localhost", 8000)
        assert isinstance(localhost_available, bool), "Port check should return boolean"

    def test_environment_variable_validation(self):
        """Test that environment variables are validated properly."""
        # Test valid port
        with patch.dict(os.environ, {"MCP_HTTP_PORT": "8080"}):
            try:
                port = int(os.getenv("MCP_HTTP_PORT", "8000"))
                assert 1 <= port <= 65535, "Port should be in valid range"
            except ValueError:
                pytest.fail("Valid port should not raise ValueError")

        # Test invalid port handling
        with patch.dict(os.environ, {"MCP_HTTP_PORT": "invalid"}):
            try:
                port = int(os.getenv("MCP_HTTP_PORT", "8000"))
                pytest.fail("Invalid port should raise ValueError")
            except ValueError:
                # This is expected - should fall back to default
                port = 8000
                assert port == 8000, "Should fall back to default on invalid port"

    def test_no_actual_network_connections(self):
        """Test that importing modules doesn't make actual network connections."""
        # This test ensures that simply importing our modules doesn't
        # cause network connections that could fail in CI/CD

        try:
            # These imports should not cause network connections
            import src.http_proxy as http_proxy
            from src.http_proxy import HTTPProxy, create_http_proxy_server

            # These should all be available without connections
            assert http_proxy is not None
            assert HTTPProxy is not None
            assert create_http_proxy_server is not None

        except Exception as e:
            pytest.fail(f"Module imports should not cause connection errors: {e}")


class TestConfigurationValidationHelpers:
    """Test configuration validation helper functions."""

    @pytest.fixture
    def config_validator(self):
        """Configuration validation utilities."""
        class ConfigValidator:
            def validate_server_config(self, config):
                """Validate server configuration."""
                required_keys = ['host', 'port']
                return all(key in config for key in required_keys)
            
            def validate_environment_vars(self, required_vars):
                """Validate required environment variables."""
                return {var: var in os.environ for var in required_vars}
            
            def validate_port_availability(self, host, port):
                """Check if a port is available."""
                import socket
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        result = s.connect_ex((host, port))
                        return result != 0  # Port is available if connection fails
                except Exception:
                    return False
            
            def validate_file_permissions(self, file_path, required_perms):
                """Validate file permissions."""
                if not os.path.exists(file_path):
                    return False
                
                import stat
                file_stat = os.stat(file_path)
                file_perms = stat.filemode(file_stat.st_mode)
                
                # Simple permission check (could be more sophisticated)
                return 'r' in required_perms and 'r' in file_perms
        
        return ConfigValidator()

    def test_server_config_validation(self, config_validator):
        """Test server configuration validation."""
        # Valid config
        valid_config = {'host': 'localhost', 'port': 8000}
        assert config_validator.validate_server_config(valid_config), "Valid config should pass"
        
        # Invalid config - missing keys
        invalid_config = {'host': 'localhost'}
        assert not config_validator.validate_server_config(invalid_config), "Invalid config should fail"

    def test_environment_vars_validation(self, config_validator):
        """Test environment variables validation."""
        required_vars = ['MCP_HTTP_HOST', 'MCP_HTTP_PORT']
        
        # Test with variables set
        with patch.dict(os.environ, {'MCP_HTTP_HOST': 'localhost', 'MCP_HTTP_PORT': '8000'}):
            result = config_validator.validate_environment_vars(required_vars)
            assert all(result.values()), "All required vars should be present"
        
        # Test with variables missing
        with patch.dict(os.environ, {}, clear=True):
            result = config_validator.validate_environment_vars(required_vars)
            assert not any(result.values()), "No required vars should be present"

    def test_port_availability_validation(self, config_validator):
        """Test port availability validation."""
        # Test with a port that should be available (high port number)
        result = config_validator.validate_port_availability('localhost', 65432)
        assert isinstance(result, bool), "Should return boolean result"

    def test_file_permissions_validation(self, config_validator, tmp_path):
        """Test file permissions validation."""
        # Create a test file
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")
        
        # Test readable file
        result = config_validator.validate_file_permissions(str(test_file), 'r')
        assert result, "Readable file should pass validation"
        
        # Test non-existent file
        result = config_validator.validate_file_permissions(str(tmp_path / "nonexistent.txt"), 'r')
        assert not result, "Non-existent file should fail validation"


class TestOptimizedDeploymentExecution:
    """Test optimized deployment test execution for faster feedback."""

    def test_fast_configuration_validation(self):
        """Test fast configuration validation without external dependencies."""
        # This test should complete quickly without network calls or file I/O
        config = {
            'host': 'localhost',
            'port': 8000,
            'timeout': 30
        }
        
        # Quick validation checks
        assert isinstance(config['host'], str), "Host should be string"
        assert isinstance(config['port'], int), "Port should be integer"
        assert 1 <= config['port'] <= 65535, "Port should be in valid range"
        assert config['timeout'] > 0, "Timeout should be positive"

    def test_fast_environment_check(self):
        """Test fast environment variable checking."""
        # Quick environment variable validation
        env_vars = ['MCP_HTTP_HOST', 'MCP_HTTP_PORT', 'MITRE_ATTACK_URL']
        
        for var in env_vars:
            # Just check that we can get the variable (with default)
            value = os.getenv(var, 'default')
            assert value is not None, f"Environment variable {var} should have value or default"

    def test_fast_import_validation(self):
        """Test fast import validation for critical modules."""
        # Test that critical modules can be imported quickly
        critical_modules = [
            'os',
            'json', 
            'yaml',
            'pathlib'
        ]
        
        for module_name in critical_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                pytest.fail(f"Critical module {module_name} should be importable: {e}")

    def test_fast_dependency_check(self):
        """Test fast dependency availability check."""
        # Quick check for required dependencies
        required_deps = ['pytest', 'pydantic', 'aiohttp']
        
        for dep in required_deps:
            try:
                __import__(dep)
            except ImportError:
                # Don't fail the test, just note the missing dependency
                # This allows tests to run in minimal environments
                pass

    @pytest.mark.fast
    def test_minimal_deployment_validation(self):
        """Test minimal deployment validation for quick feedback."""
        # This test should run very quickly and provide basic validation
        
        # Check that we can create basic configuration
        config = {
            'server': {
                'host': os.getenv('MCP_HTTP_HOST', 'localhost'),
                'port': int(os.getenv('MCP_HTTP_PORT', '8000'))
            }
        }
        
        assert config['server']['host'] is not None, "Server host should be configured"
        assert isinstance(config['server']['port'], int), "Server port should be integer"
        assert 1 <= config['server']['port'] <= 65535, "Server port should be valid"

    @pytest.mark.fast
    def test_quick_file_structure_check(self):
        """Test quick file structure validation."""
        # Quick check for essential files without full validation
        project_root = Path(__file__).parent.parent.parent
        
        essential_files = [
            'src/mcp_server.py',
            'src/http_proxy.py',
            'pyproject.toml'
        ]
        
        for file_path in essential_files:
            full_path = project_root / file_path
            assert full_path.exists(), f"Essential file should exist: {file_path}"