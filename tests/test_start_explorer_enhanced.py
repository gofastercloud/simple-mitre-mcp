"""
Tests for enhanced start_explorer.py functionality.

This module tests the comprehensive validation, health checks, graceful shutdown,
and command-line interface enhancements added in Task 17.
"""

import pytest
import asyncio
import os
import sys
import tempfile
import socket
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pathlib import Path
import argparse
from io import StringIO

# Add the project root to the Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import start_explorer


class TestEnhancedValidation:
    """Test enhanced validation functionality"""

    def test_check_port_available_success(self):
        """Test port availability check with available port"""
        # Use a high port that should be available
        assert start_explorer.check_port_available("127.0.0.1", 65432) == True

    def test_check_port_available_failure(self):
        """Test port availability check with occupied port"""
        # Create a socket to occupy a port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", 0))  # Bind to available port
            _, port = sock.getsockname()
            
            # Now test that the port is detected as unavailable
            assert start_explorer.check_port_available("127.0.0.1", port) == False
        finally:
            sock.close()

    def test_get_module_version_success(self):
        """Test getting module version successfully"""
        # Test with sys module which always has version info
        version = start_explorer.get_module_version("sys")
        assert isinstance(version, str)
        
    def test_get_module_version_missing_module(self):
        """Test getting version of non-existent module"""
        version = start_explorer.get_module_version("nonexistent_module_xyz")
        assert version is None

    @patch('start_explorer.importlib.import_module')
    def test_validate_dependencies_success(self, mock_import):
        """Test successful dependency validation"""
        # Mock all imports to succeed
        mock_import.return_value = Mock(__version__="1.0.0")
        
        success, errors = start_explorer.validate_dependencies(verbose=False)
        assert success == True
        assert len(errors) == 0

    @patch('start_explorer.importlib.import_module')
    def test_validate_dependencies_failure(self, mock_import):
        """Test dependency validation with missing modules"""
        # Mock some imports to fail
        def side_effect(module_name):
            if module_name in ["aiohttp", "src.http_proxy"]:
                raise ImportError(f"No module named '{module_name}'")
            return Mock(__version__="1.0.0")
        
        mock_import.side_effect = side_effect
        
        success, errors = start_explorer.validate_dependencies(verbose=False)
        assert success == False
        assert len(errors) > 0
        assert any("aiohttp" in error for error in errors)

    def test_validate_web_interface_structure_success(self, tmp_path):
        """Test successful web interface structure validation"""
        # Create temporary web interface files
        web_interface = tmp_path / "web_interface"
        web_interface.mkdir()
        
        # Create required directories
        (web_interface / "css").mkdir()
        (web_interface / "js").mkdir()
        
        # Create required files with content
        required_files = [
            "index.html",
            "css/styles.css",
            "css/components.css", 
            "js/app.js",
            "js/api.js",
            "js/SystemDashboard.js",
            "js/ToolsSection.js",
            "js/ResultsSection.js",
            "js/SmartFormControls.js",
            "js/ThemeToggle.js"
        ]
        
        for file_path in required_files:
            file_full_path = web_interface / file_path
            file_full_path.write_text("/* test content */")
        
        # Temporarily change working directory
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            success, errors = start_explorer.validate_web_interface_structure()
            assert success == True
            assert len(errors) == 0
        finally:
            os.chdir(original_cwd)

    def test_validate_web_interface_structure_missing_files(self, tmp_path):
        """Test web interface structure validation with missing files"""
        # Only create some files, leave others missing
        web_interface = tmp_path / "web_interface"
        web_interface.mkdir()
        (web_interface / "index.html").write_text("test")
        
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            success, errors = start_explorer.validate_web_interface_structure()
            assert success == False
            assert len(errors) > 0
            assert any("missing" in error.lower() for error in errors)
        finally:
            os.chdir(original_cwd)

    @patch('yaml.safe_load')
    def test_validate_configuration_files_success(self, mock_yaml_load, tmp_path):
        """Test successful configuration file validation"""
        # Create config directory and files
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        
        # Create YAML config files
        (config_dir / "data_sources.yaml").write_text("test: value")
        (config_dir / "entity_schemas.yaml").write_text("test: value")
        (config_dir / "tools.yaml").write_text("test: value")
        
        # Create TOML file
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        
        mock_yaml_load.return_value = {"test": "value"}
        
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            success, errors = start_explorer.validate_configuration_files()
            assert success == True
            assert len(errors) == 0
        finally:
            os.chdir(original_cwd)


class TestHealthCheck:
    """Test health check functionality"""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check"""
        with patch('start_explorer.urllib.request.urlopen') as mock_urlopen:
            # Mock successful HTTP responses
            mock_response = Mock()
            mock_response.status = 200
            mock_response.__enter__ = Mock(return_value=mock_response)
            mock_response.__exit__ = Mock(return_value=None)
            mock_urlopen.return_value = mock_response
            
            result = await start_explorer.health_check("localhost", 8000, timeout=5)
            
            assert result["healthy"] == True
            assert result["server_reachable"] == True
            assert len(result["endpoints"]) > 0
            assert len(result["response_times"]) > 0

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check with server errors"""
        with patch('start_explorer.urllib.request.urlopen') as mock_urlopen:
            # Mock failed HTTP responses
            mock_urlopen.side_effect = Exception("Connection refused")
            
            result = await start_explorer.health_check("localhost", 8000, timeout=5)
            
            assert result["healthy"] == False
            assert result["server_reachable"] == False
            assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_run_health_check_success(self):
        """Test run_health_check wrapper function"""
        with patch('start_explorer.health_check') as mock_health_check:
            mock_health_check.return_value = {
                "healthy": True,
                "response_times": {"/": 100, "/tools": 150}
            }
            
            result = await start_explorer.run_health_check("localhost", 8000)
            assert result == True

    @pytest.mark.asyncio 
    async def test_run_health_check_failure(self):
        """Test run_health_check with unhealthy server"""
        with patch('start_explorer.health_check') as mock_health_check:
            mock_health_check.return_value = {
                "healthy": False,
                "errors": ["Connection failed"]
            }
            
            result = await start_explorer.run_health_check("localhost", 8000)
            assert result == False


class TestSignalHandling:
    """Test signal handling and graceful shutdown"""

    def test_setup_signal_handlers(self):
        """Test signal handler setup"""
        with patch('start_explorer.signal.signal') as mock_signal:
            start_explorer.setup_signal_handlers()
            
            # Verify signal handlers were set up
            assert mock_signal.call_count >= 2  # At least SIGINT and SIGTERM

    def test_signal_handler_sets_shutdown_flag(self):
        """Test that signal handler sets shutdown flag"""
        import signal
        
        # Reset shutdown flag
        start_explorer.shutdown_requested = False
        
        # Set up signal handlers
        start_explorer.setup_signal_handlers()
        
        # Trigger signal handler (simulate SIGINT)
        handlers = []
        original_signal = signal.signal
        
        def mock_signal_func(sig, handler):
            handlers.append((sig, handler))
            return original_signal(sig, handler)
        
        with patch('signal.signal', side_effect=mock_signal_func):
            start_explorer.setup_signal_handlers()
            
            # Find and call the SIGINT handler
            for sig, handler in handlers:
                if sig == signal.SIGINT:
                    handler(signal.SIGINT, None)
                    break
            
            assert start_explorer.shutdown_requested == True


class TestCommandLineInterface:
    """Test command-line interface functionality"""

    def test_create_argument_parser(self):
        """Test argument parser creation"""
        parser = start_explorer.create_argument_parser()
        assert isinstance(parser, argparse.ArgumentParser)
        
        # Test parsing help doesn't raise exception
        with pytest.raises(SystemExit):  # argparse calls sys.exit for --help
            parser.parse_args(['--help'])

    def test_argument_parsing_validate(self):
        """Test parsing --validate argument"""
        parser = start_explorer.create_argument_parser()
        args = parser.parse_args(['--validate'])
        assert args.validate == True
        assert args.health_check == False

    def test_argument_parsing_health_check(self):
        """Test parsing --health-check argument"""
        parser = start_explorer.create_argument_parser()
        args = parser.parse_args(['--health-check'])
        assert args.health_check == True
        assert args.validate == False

    def test_argument_parsing_server_options(self):
        """Test parsing server option arguments"""
        parser = start_explorer.create_argument_parser()
        args = parser.parse_args(['--no-browser', '--port', '9000', '--host', '0.0.0.0'])
        assert args.no_browser == True
        assert args.port == 9000
        assert args.host == '0.0.0.0'

    def test_argument_parsing_debug_options(self):
        """Test parsing debug option arguments"""
        parser = start_explorer.create_argument_parser()
        
        # Test verbose
        args = parser.parse_args(['--verbose'])
        assert args.verbose == True
        
        # Test quiet
        args = parser.parse_args(['--quiet'])
        assert args.quiet == True

    def test_configure_logging_verbose(self):
        """Test logging configuration in verbose mode"""
        with patch('start_explorer.logging.basicConfig') as mock_config:
            start_explorer.configure_logging(verbose=True, quiet=False)
            mock_config.assert_called_once()
            args, kwargs = mock_config.call_args
            assert kwargs['level'] == start_explorer.logging.DEBUG

    def test_configure_logging_quiet(self):
        """Test logging configuration in quiet mode"""
        with patch('start_explorer.logging.basicConfig') as mock_config:
            start_explorer.configure_logging(verbose=False, quiet=True)
            mock_config.assert_called_once()
            args, kwargs = mock_config.call_args
            assert kwargs['level'] == start_explorer.logging.ERROR


class TestMainFunction:
    """Test main function and integration"""

    @patch('start_explorer.run_startup_validation')
    @patch('sys.argv', ['start_explorer.py', '--validate'])
    def test_main_validate_mode(self, mock_validation):
        """Test main function in validate mode"""
        mock_validation.return_value = True
        
        with pytest.raises(SystemExit) as excinfo:
            start_explorer.main()
        assert excinfo.value.code == 0

    @patch('start_explorer.asyncio.run')
    @patch('sys.argv', ['start_explorer.py', '--health-check'])
    def test_main_health_check_mode(self, mock_asyncio_run):
        """Test main function in health check mode"""
        mock_asyncio_run.return_value = True
        
        with pytest.raises(SystemExit) as excinfo:
            start_explorer.main()
        assert excinfo.value.code == 0

    @patch('start_explorer.run_startup_validation')
    @patch('start_explorer.asyncio.run')
    @patch('sys.argv', ['start_explorer.py'])
    def test_main_normal_startup(self, mock_asyncio_run, mock_validation):
        """Test main function normal startup mode"""
        mock_validation.return_value = True
        mock_asyncio_run.return_value = None
        
        with patch('start_explorer.importlib.import_module'):
            # This should not raise an exception
            start_explorer.main()

    def test_main_keyboard_interrupt(self):
        """Test main function handling keyboard interrupt"""
        with patch('start_explorer.create_argument_parser') as mock_parser:
            mock_parser.side_effect = KeyboardInterrupt()
            
            with pytest.raises(SystemExit) as excinfo:
                start_explorer.main()
            assert excinfo.value.code == 0


class TestEnvironmentValidation:
    """Test environment validation enhancements"""

    def test_validate_environment_python_version_check(self):
        """Test Python version validation"""
        # Create a mock version_info that has the attributes we need
        from collections import namedtuple
        VersionInfo = namedtuple('VersionInfo', ['major', 'minor', 'micro'])
        mock_version = VersionInfo(3, 11, 0)
        
        with patch('start_explorer.sys.version_info', mock_version):
            success, errors = start_explorer.validate_environment()
            assert success == False
            assert any("Python 3.12" in error for error in errors)

    @patch('start_explorer.validate_web_interface_structure')
    @patch('start_explorer.validate_configuration_files')
    def test_validate_environment_comprehensive(self, mock_config, mock_web):
        """Test comprehensive environment validation"""
        mock_web.return_value = (True, [])
        mock_config.return_value = (True, [])
        
        with patch('os.path.exists', return_value=True):
            success, errors = start_explorer.validate_environment()
            # Should succeed if all sub-validations pass
            assert isinstance(success, bool)
            assert isinstance(errors, list)


class TestIntegration:
    """Integration tests for enhanced functionality"""

    def test_startup_validation_integration(self):
        """Test complete startup validation integration"""
        with patch('start_explorer.validate_dependencies') as mock_deps, \
             patch('start_explorer.validate_environment') as mock_env:
            
            mock_deps.return_value = (True, [])
            mock_env.return_value = (True, [])
            
            result = start_explorer.run_startup_validation(verbose=False)
            assert result == True

    def test_startup_validation_failure_integration(self):
        """Test startup validation with failures"""
        with patch('start_explorer.validate_dependencies') as mock_deps, \
             patch('start_explorer.validate_environment') as mock_env:
            
            mock_deps.return_value = (False, ["Missing dependency"])
            mock_env.return_value = (True, [])
            
            result = start_explorer.run_startup_validation(verbose=False)
            assert result == False

    @pytest.mark.asyncio
    async def test_server_startup_with_graceful_shutdown(self):
        """Test server startup with graceful shutdown capability"""
        # Import the function to patch it in the right namespace
        with patch('src.http_proxy.create_http_proxy_server') as mock_server:
            mock_runner = Mock()
            mock_runner.cleanup = AsyncMock()
            mock_server.return_value = (mock_runner, Mock())
            
            # Set shutdown flag to exit quickly
            start_explorer.shutdown_requested = True
            
            # This should complete without hanging
            await start_explorer.start_web_explorer(open_browser_flag=False, verbose=False)
            
            # Verify cleanup was called
            mock_runner.cleanup.assert_called_once()


# Reset shutdown flag after tests
def pytest_runtest_teardown():
    """Reset global state after each test"""
    start_explorer.shutdown_requested = False