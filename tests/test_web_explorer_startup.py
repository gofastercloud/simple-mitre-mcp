"""
Test suite for web explorer startup and dependency validation.

This test suite validates the enhanced dependency resolution and validation
functionality implemented in task 1 of the web-explorer-improvements spec.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after path setup
from start_explorer import (  # noqa: E402
    validate_dependencies,
    validate_environment,
    run_startup_validation,
    print_troubleshooting_guide,
)


class TestDependencyValidation:
    """Test dependency validation functionality."""

    def test_validate_dependencies_success(self):
        """Test that validate_dependencies returns True when all deps are available."""
        success, errors = validate_dependencies()
        assert success is True
        assert len(errors) == 0

    def test_validate_dependencies_with_missing_module(self):
        """Test that validate_dependencies detects missing modules."""
        # Mock importlib.import_module to simulate missing module
        with patch("start_explorer.importlib.import_module") as mock_import:
            mock_import.side_effect = [
                None,  # aiohttp - OK
                None,  # aiohttp_cors - OK
                None,  # asyncio - OK
                None,  # logging - OK
                None,  # threading - OK
                None,  # webbrowser - OK
                None,  # pathlib - OK
                ImportError("No module named 'http_proxy'"),  # http_proxy - FAIL
                None,  # src.mcp_server - OK
            ]

            success, errors = validate_dependencies()
            assert success is False
            assert len(errors) > 0
            assert any("http_proxy" in error for error in errors)

    def test_validate_dependencies_output_format(self, capsys):
        """Test that validate_dependencies produces expected output format."""
        validate_dependencies()
        captured = capsys.readouterr()

        # Check for expected output patterns
        assert "🔍 Validating web explorer dependencies..." in captured.out
        assert "✅" in captured.out  # Should have success indicators
        assert "All dependencies validated successfully" in captured.out


class TestEnvironmentValidation:
    """Test environment validation functionality."""

    def test_validate_environment_success(self):
        """Test that validate_environment returns True when environment is valid."""
        success, errors = validate_environment()
        assert success is True
        assert len(errors) == 0

    def test_validate_environment_missing_web_explorer_html(self):
        """Test detection of missing web_explorer.html."""
        # Temporarily rename the file
        web_explorer_path = Path("web_explorer.html")
        backup_path = Path("web_explorer.html.backup")

        if web_explorer_path.exists():
            web_explorer_path.rename(backup_path)

        try:
            success, errors = validate_environment()
            assert success is False
            assert any("web_explorer.html" in error for error in errors)
        finally:
            # Restore the file
            if backup_path.exists():
                backup_path.rename(web_explorer_path)

    def test_validate_environment_invalid_port(self):
        """Test detection of invalid port configuration."""
        with patch.dict(os.environ, {"MCP_HTTP_PORT": "99999"}):
            success, errors = validate_environment()
            assert success is False
            assert any("port" in error.lower() for error in errors)

    def test_validate_environment_non_numeric_port(self):
        """Test detection of non-numeric port configuration."""
        with patch.dict(os.environ, {"MCP_HTTP_PORT": "invalid"}):
            success, errors = validate_environment()
            assert success is False
            assert any(
                "port" in error.lower() and "numeric" in error.lower()
                for error in errors
            )

    def test_validate_environment_output_format(self, capsys):
        """Test that validate_environment produces expected output format."""
        validate_environment()
        captured = capsys.readouterr()

        # Check for expected output patterns
        assert "🔍 Validating environment setup..." in captured.out
        assert "✅" in captured.out  # Should have success indicators


class TestStartupValidation:
    """Test comprehensive startup validation."""

    def test_run_startup_validation_success(self):
        """Test that run_startup_validation returns True when all validations pass."""
        success = run_startup_validation()
        assert success is True

    def test_run_startup_validation_output_format(self, capsys):
        """Test that run_startup_validation produces expected output format."""
        run_startup_validation()
        captured = capsys.readouterr()

        # Check for expected output patterns
        assert "🚀 Starting Web Explorer Validation..." in captured.out
        assert "=" in captured.out  # Should have separator lines
        assert "All validations passed" in captured.out


class TestTroubleshootingGuide:
    """Test troubleshooting guide functionality."""

    def test_print_troubleshooting_guide_dependency_errors(self, capsys):
        """Test troubleshooting guide with dependency errors."""
        dep_errors = ["aiohttp: No module named 'aiohttp'"]
        print_troubleshooting_guide(dependency_errors=dep_errors)
        captured = capsys.readouterr()

        assert "TROUBLESHOOTING GUIDE" in captured.out
        assert "DEPENDENCY ISSUES" in captured.out
        assert "uv sync" in captured.out
        assert "aiohttp" in captured.out

    def test_print_troubleshooting_guide_environment_errors(self, capsys):
        """Test troubleshooting guide with environment errors."""
        env_errors = ["web_explorer.html not found"]
        print_troubleshooting_guide(environment_errors=env_errors)
        captured = capsys.readouterr()

        assert "TROUBLESHOOTING GUIDE" in captured.out
        assert "ENVIRONMENT ISSUES" in captured.out
        assert "web_explorer.html" in captured.out

    def test_print_troubleshooting_guide_both_errors(self, capsys):
        """Test troubleshooting guide with both types of errors."""
        dep_errors = ["aiohttp: missing"]
        env_errors = ["file not found"]
        print_troubleshooting_guide(
            dependency_errors=dep_errors, environment_errors=env_errors
        )
        captured = capsys.readouterr()

        assert "DEPENDENCY ISSUES" in captured.out
        assert "ENVIRONMENT ISSUES" in captured.out
        assert "ADDITIONAL HELP" in captured.out


class TestCommandLineInterface:
    """Test command line interface functionality."""

    def test_help_command(self, capsys):
        """Test --help command line option."""
        with patch("sys.argv", ["start_explorer.py", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                from start_explorer import main

                main()

            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "MITRE ATT&CK MCP Web Explorer" in captured.out
            assert "Usage:" in captured.out

    def test_validate_command(self, capsys):
        """Test --validate command line option."""
        with patch("sys.argv", ["start_explorer.py", "--validate"]):
            with pytest.raises(SystemExit) as exc_info:
                from start_explorer import main

                main()

            # Should exit with 0 if validation passes
            assert exc_info.value.code == 0
            captured = capsys.readouterr()
            assert "Running standalone validation..." in captured.out


class TestStandaloneValidationScript:
    """Test the standalone validation script."""

    def test_standalone_script_imports(self):
        """Test that the standalone validation script can be imported."""
        import validate_web_explorer

        assert hasattr(validate_web_explorer, "main")

    def test_standalone_script_execution(self, capsys):
        """Test that the standalone validation script executes correctly."""
        from validate_web_explorer import main

        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should exit with 0 if validation passes
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Standalone Validation" in captured.out
        assert "SUCCESS" in captured.out


class TestIntegration:
    """Integration tests for the complete validation system."""

    def test_uv_sync_dependencies_available(self):
        """Test that uv sync has installed all required dependencies."""
        import importlib

        required_modules = [
            "aiohttp",
            "aiohttp_cors",
            "asyncio",
            "logging",
            "threading",
            "webbrowser",
            "pathlib",
        ]

        for module_name in required_modules:
            try:
                importlib.import_module(module_name)
            except ImportError:
                pytest.fail(
                    f"Required module {module_name} is not available after uv sync"
                )

    def test_project_structure_intact(self):
        """Test that all required project files exist."""
        required_files = [
            "web_explorer.html",
            "http_proxy.py",
            "src/mcp_server.py",
            "src/data_loader.py",
            "config/data_sources.yaml",
            "start_explorer.py",
            "validate_web_explorer.py",
        ]

        for file_path in required_files:
            assert Path(file_path).exists(), f"Required file {file_path} is missing"

    def test_enhanced_error_handling(self):
        """Test that enhanced error handling provides clear guidance."""
        # This test verifies that the error handling improvements are in place
        success, errors = validate_dependencies()

        # If there are no errors, that's good
        if success:
            assert len(errors) == 0
        else:
            # If there are errors, they should be informative
            for error in errors:
                assert ":" in error  # Should have module name and error description
                assert len(error.strip()) > 0  # Should not be empty

    def test_startup_validation_comprehensive(self):
        """Test that startup validation covers all required checks."""
        # Run the full validation and capture output
        import io
        from contextlib import redirect_stdout

        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            success = run_startup_validation()

        output = output_buffer.getvalue()

        # Verify comprehensive checks are performed
        assert "dependencies" in output.lower()
        assert "environment" in output.lower()
        assert "aiohttp" in output
        assert "web_explorer.html" in output
        assert "port" in output.lower()

        # Should indicate success or provide clear failure reasons
        if success:
            assert "All validations passed" in output
        else:
            assert "failed" in output.lower()
