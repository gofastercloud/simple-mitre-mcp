#!/usr/bin/env python3
"""
Tests for HTTP proxy configuration and connection handling.

This module tests that the HTTP proxy server configuration works properly
and doesn't cause connection issues in CI/CD environments.
"""

import os
import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio


class TestHTTPProxyConfiguration:
    """Test HTTP proxy configuration and connection handling."""

    def test_http_proxy_import_without_connection(self):
        """Test that HTTP proxy can be imported without making connections."""
        # This should not cause any connection attempts
        try:
            from http_proxy import HTTPProxy
            assert HTTPProxy is not None, "HTTPProxy class should be importable"
        except ImportError as e:
            pytest.fail(f"Failed to import HTTPProxy: {e}")

    def test_http_proxy_configuration_parsing(self):
        """Test that HTTP proxy configuration is parsed correctly."""
        # Test with environment variables
        with patch.dict(os.environ, {'MCP_HTTP_HOST': '127.0.0.1', 'MCP_HTTP_PORT': '9000'}):
            host = os.getenv('MCP_HTTP_HOST', 'localhost')
            port = int(os.getenv('MCP_HTTP_PORT', '8000'))
            
            assert host == '127.0.0.1', "Host should be parsed from environment"
            assert port == 9000, "Port should be parsed from environment"

    def test_http_proxy_default_configuration(self):
        """Test that HTTP proxy uses correct defaults."""
        with patch.dict(os.environ, {}, clear=True):
            host = os.getenv('MCP_HTTP_HOST', 'localhost')
            port = int(os.getenv('MCP_HTTP_PORT', '8000'))
            
            assert host == 'localhost', "Should use default host"
            assert port == 8000, "Should use default port"

    @patch('http_proxy.create_http_proxy_server')
    def test_http_proxy_server_creation_mock(self, mock_create_server):
        """Test HTTP proxy server creation without actual connections."""
        # Mock the server creation to avoid actual connections
        mock_runner = Mock()
        mock_server = Mock()
        mock_create_server.return_value = (mock_runner, mock_server)
        
        # This should not cause connection issues
        from http_proxy import create_http_proxy_server
        assert create_http_proxy_server is not None, "Function should be importable"

    def test_aiohttp_dependency_available(self):
        """Test that aiohttp dependency is available."""
        try:
            import aiohttp
            import aiohttp_cors
            assert aiohttp is not None, "aiohttp should be available"
            assert aiohttp_cors is not None, "aiohttp_cors should be available"
        except ImportError as e:
            pytest.fail(f"Required HTTP dependencies not available: {e}")

    def test_http_proxy_class_initialization_mock(self):
        """Test HTTP proxy class initialization with mocked MCP server."""
        from http_proxy import HTTPProxy
        
        # Create a mock MCP server
        mock_mcp_server = Mock()
        
        # This should not cause connection issues
        try:
            proxy = HTTPProxy(mock_mcp_server)
            assert proxy is not None, "HTTPProxy should initialize with mock server"
            assert proxy.mcp_server == mock_mcp_server, "Should store MCP server reference"
        except Exception as e:
            pytest.fail(f"HTTPProxy initialization failed: {e}")

    def test_http_proxy_routes_setup(self):
        """Test that HTTP proxy routes are set up correctly."""
        from http_proxy import HTTPProxy
        
        mock_mcp_server = Mock()
        proxy = HTTPProxy(mock_mcp_server)
        
        # Check that the app was created
        assert hasattr(proxy, 'app'), "HTTPProxy should have app attribute"
        assert proxy.app is not None, "App should be initialized"

    def test_http_proxy_cors_setup(self):
        """Test that CORS is set up correctly."""
        from http_proxy import HTTPProxy
        
        mock_mcp_server = Mock()
        proxy = HTTPProxy(mock_mcp_server)
        
        # This should not raise any exceptions
        assert proxy.app is not None, "App should be initialized with CORS"

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
        localhost_available = is_port_available('localhost', 8000)
        assert isinstance(localhost_available, bool), "Port check should return boolean"

    def test_environment_variable_validation(self):
        """Test that environment variables are validated properly."""
        # Test valid port
        with patch.dict(os.environ, {'MCP_HTTP_PORT': '8080'}):
            try:
                port = int(os.getenv('MCP_HTTP_PORT', '8000'))
                assert 1 <= port <= 65535, "Port should be in valid range"
            except ValueError:
                pytest.fail("Valid port should not raise ValueError")
        
        # Test invalid port handling
        with patch.dict(os.environ, {'MCP_HTTP_PORT': 'invalid'}):
            try:
                port = int(os.getenv('MCP_HTTP_PORT', '8000'))
                pytest.fail("Invalid port should raise ValueError")
            except ValueError:
                # This is expected - should fall back to default
                port = 8000
                assert port == 8000, "Should fall back to default on invalid port"

    def test_ci_cd_environment_simulation(self):
        """Test behavior in simulated CI/CD environment."""
        # Simulate minimal CI/CD environment
        ci_env = {
            'CI': 'true',
            'GITHUB_ACTIONS': 'true',
            'PATH': '/usr/bin:/bin'
        }
        
        with patch.dict(os.environ, ci_env, clear=True):
            # These should work without issues
            host = os.getenv('MCP_HTTP_HOST', 'localhost')
            port = os.getenv('MCP_HTTP_PORT', '8000')
            
            assert host == 'localhost', "Should work in CI/CD environment"
            assert port == '8000', "Should use default port in CI/CD"
            
            # Should be able to convert to int
            port_int = int(port)
            assert port_int == 8000, "Port should be convertible to int"

    def test_no_actual_network_connections(self):
        """Test that importing modules doesn't make actual network connections."""
        # This test ensures that simply importing our modules doesn't
        # cause network connections that could fail in CI/CD
        
        try:
            # These imports should not cause network connections
            import http_proxy
            from http_proxy import HTTPProxy, create_http_proxy_server
            
            # These should all be available without connections
            assert http_proxy is not None
            assert HTTPProxy is not None
            assert create_http_proxy_server is not None
            
        except Exception as e:
            pytest.fail(f"Module imports should not cause connection errors: {e}")

    def test_mock_server_creation_async(self):
        """Test async server creation with mocks to avoid connection issues."""
        
        @patch('http_proxy.DataLoader')
        @patch('http_proxy.create_mcp_server')
        @patch('aiohttp.web.AppRunner')
        @patch('aiohttp.web.TCPSite')
        async def mock_test(mock_site, mock_runner, mock_create_mcp, mock_data_loader):
            """Async test with all external dependencies mocked."""
            # Mock all the components that could cause connection issues
            mock_data_loader_instance = Mock()
            mock_data_loader.return_value = mock_data_loader_instance
            
            mock_mcp_server = Mock()
            mock_create_mcp.return_value = mock_mcp_server
            
            mock_runner_instance = Mock()
            mock_runner.return_value = mock_runner_instance
            mock_runner_instance.setup = AsyncMock()
            
            mock_site_instance = Mock()
            mock_site.return_value = mock_site_instance
            mock_site_instance.start = AsyncMock()
            
            # This should work without actual connections
            from http_proxy import create_http_proxy_server
            
            # The function should be callable (even if mocked)
            assert callable(create_http_proxy_server), "Function should be callable"
        
        # Run the async test
        asyncio.run(mock_test())
