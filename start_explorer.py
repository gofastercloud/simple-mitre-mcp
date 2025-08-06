#!/usr/bin/env python3
"""
Web Explorer Launcher for MITRE ATT&CK MCP Server

This script provides a convenient way to start the web interface for the MITRE ATT&CK MCP server.
It automatically starts the HTTP proxy server and opens the web browser to the interface.

Enhanced with comprehensive dependency validation and error handling.
"""

import asyncio
import importlib
import logging
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import List, Tuple

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

logger = logging.getLogger(__name__)


def validate_dependencies() -> Tuple[bool, List[str]]:
    """
    Validate that all required dependencies are available for the web explorer.

    Returns:
        Tuple[bool, List[str]]: (success, list of error messages)
    """
    required_modules = [
        ("aiohttp", "aiohttp>=3.12.15"),
        ("aiohttp_cors", "aiohttp-cors>=0.8.1"),
        ("asyncio", "Built-in Python module"),
        ("logging", "Built-in Python module"),
        ("threading", "Built-in Python module"),
        ("webbrowser", "Built-in Python module"),
        ("pathlib", "Built-in Python module"),
    ]

    missing_modules = []

    print("🔍 Validating web explorer dependencies...")

    for module_name, package_info in required_modules:
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {module_name} - OK")
        except ImportError as e:
            error_msg = f"  ❌ {module_name} - MISSING ({package_info})"
            print(error_msg)
            missing_modules.append(f"{module_name}: {str(e)}")

    # Test project-specific imports
    project_modules = [
        ("http_proxy", "HTTP proxy server module"),
        ("src.mcp_server", "MCP server implementation"),
    ]

    for module_name, description in project_modules:
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {module_name} - OK")
        except ImportError as e:
            error_msg = f"  ❌ {module_name} - MISSING ({description})"
            print(error_msg)
            missing_modules.append(f"{module_name}: {str(e)}")

    if missing_modules:
        return False, missing_modules

    print("✅ All dependencies validated successfully")
    return True, []


def validate_environment() -> Tuple[bool, List[str]]:
    """
    Validate the environment setup for the web explorer.

    Returns:
        Tuple[bool, List[str]]: (success, list of error messages)
    """
    issues = []

    print("🔍 Validating environment setup...")

    # Check if web_explorer.html exists
    web_explorer_path = Path(__file__).parent / "web_explorer.html"
    if not web_explorer_path.exists():
        issues.append("web_explorer.html not found in current directory")
        print("  ❌ web_explorer.html - MISSING")
    else:
        print("  ✅ web_explorer.html - OK")

    # Check if required source files exist
    required_files = [
        "http_proxy.py",
        "src/mcp_server.py",
        "src/data_loader.py",
        "config/data_sources.yaml",
    ]

    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append(f"Required file missing: {file_path}")
            print(f"  ❌ {file_path} - MISSING")
        else:
            print(f"  ✅ {file_path} - OK")

    # Check environment variables
    host = os.getenv("MCP_HTTP_HOST", "localhost")
    port = os.getenv("MCP_HTTP_PORT", "8000")

    try:
        port_int = int(port)
        if port_int < 1024 or port_int > 65535:
            issues.append(f"Invalid port number: {port} (must be between 1024-65535)")
            print(f"  ❌ Port {port} - INVALID RANGE")
        else:
            print(f"  ✅ Port {port} - OK")
    except ValueError:
        issues.append(f"Invalid port number: {port} (must be numeric)")
        print(f"  ❌ Port {port} - INVALID FORMAT")

    print(f"  ✅ Host {host} - OK")

    if issues:
        return False, issues

    print("✅ Environment validation completed successfully")
    return True, []


def print_troubleshooting_guide(
    dependency_errors: List[str] = None, environment_errors: List[str] = None
):
    """Print comprehensive troubleshooting guide."""
    print("\n" + "=" * 60)
    print("🔧 TROUBLESHOOTING GUIDE")
    print("=" * 60)

    if dependency_errors:
        print("\n📦 DEPENDENCY ISSUES:")
        for error in dependency_errors:
            print(f"   • {error}")

        print("\n🛠️  SOLUTIONS:")
        print("   1. Install/update dependencies:")
        print("      uv sync")
        print("   2. If UV is not installed:")
        print("      pip install uv")
        print("   3. Check Python version (requires >=3.12):")
        print("      python --version")
        print("   4. Reinstall dependencies:")
        print("      uv sync --force")

    if environment_errors:
        print("\n🌍 ENVIRONMENT ISSUES:")
        for error in environment_errors:
            print(f"   • {error}")

        print("\n🛠️  SOLUTIONS:")
        print("   1. Ensure you're in the project root directory")
        print("   2. Check file permissions")
        print("   3. Verify project structure is intact")
        print("   4. Try different port if port is in use:")
        print("      MCP_HTTP_PORT=8001 uv run start_explorer.py")

    print("\n📞 ADDITIONAL HELP:")
    print("   • Check project README.md for setup instructions")
    print("   • Verify UV installation: uv --version")
    print("   • Run tests to verify setup: uv run pytest tests/ -x")
    print("   • Check logs for detailed error information")
    print("=" * 60)


def run_startup_validation() -> bool:
    """
    Run comprehensive startup validation.

    Returns:
        bool: True if all validations pass, False otherwise
    """
    print("🚀 Starting Web Explorer Validation...")
    print("=" * 50)

    # Validate dependencies
    deps_ok, dep_errors = validate_dependencies()

    # Validate environment
    env_ok, env_errors = validate_environment()

    if deps_ok and env_ok:
        print("\n✅ All validations passed! Web Explorer is ready to start.")
        return True
    else:
        print("\n❌ Validation failed. Please resolve the issues below:")
        print_troubleshooting_guide(
            dep_errors if not deps_ok else None, env_errors if not env_ok else None
        )
        return False


def open_browser(url, delay=2):
    """Open browser after a delay to ensure server is ready."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
        logger.info(f"Opened browser to {url}")
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")


async def start_web_explorer():
    """Start the web explorer with HTTP proxy server."""
    # Import here after validation
    from http_proxy import create_http_proxy_server

    # Get configuration from environment variables
    host = os.getenv("MCP_HTTP_HOST", "localhost")
    port = int(os.getenv("MCP_HTTP_PORT", "8000"))

    try:
        print("🚀 Starting MITRE ATT&CK MCP Web Explorer...")
        print(
            f"📊 Loading MITRE ATT&CK data and starting server on http://{host}:{port}"
        )
        print("⏳ This may take 10-15 seconds for initial data loading...")

        # Create and start the HTTP proxy server
        runner, mcp_server = await create_http_proxy_server(host, port)

        # Start browser in a separate thread
        url = f"http://{host}:{port}"
        browser_thread = threading.Thread(target=open_browser, args=(url, 3))
        browser_thread.daemon = True
        browser_thread.start()

        print(f"✅ Web Explorer ready at: {url}")
        print("🌐 Web interface opened in your browser")
        print("🛠️  Available tools: 8 (5 basic + 3 advanced threat modeling)")
        print("📋 Press Ctrl+C to stop the server")

        # Keep the server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Web Explorer...")
        finally:
            await runner.cleanup()
            print("✅ Web Explorer stopped")

    except Exception as e:
        logger.error(f"Failed to start Web Explorer: {e}")
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print(f"   - Check if port {port} is available")
        print("   - Try a different port: MCP_HTTP_PORT=8001 uv run start_explorer.py")
        print("   - Run validation: uv run start_explorer.py --validate")
        print("   - Ensure dependencies are installed: uv sync")
        sys.exit(1)


def main():
    """Main entry point with comprehensive validation."""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--validate", "-v", "--check"]:
            print("🔍 Running standalone validation...")
            success = run_startup_validation()
            sys.exit(0 if success else 1)
        elif sys.argv[1] in ["--help", "-h"]:
            print("MITRE ATT&CK MCP Web Explorer")
            print("Usage:")
            print("  uv run start_explorer.py           # Start web explorer")
            print("  uv run start_explorer.py --validate # Run validation only")
            print("  uv run start_explorer.py --help     # Show this help")
            print("\nEnvironment Variables:")
            print("  MCP_HTTP_HOST=localhost  # Server host (default: localhost)")
            print("  MCP_HTTP_PORT=8000       # Server port (default: 8000)")
            sys.exit(0)

    # Run comprehensive startup validation
    if not run_startup_validation():
        sys.exit(1)

    # Import http_proxy after validation
    try:
        from http_proxy import create_http_proxy_server  # noqa: F401
    except ImportError as e:
        print(f"❌ Failed to import http_proxy: {e}")
        print("   This indicates a project structure issue.")
        print_troubleshooting_guide(dependency_errors=[f"http_proxy: {str(e)}"])
        sys.exit(1)

    # Start the web explorer
    try:
        asyncio.run(start_web_explorer())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error occurred: {e}")
        print("\n🔧 Try running validation to diagnose issues:")
        print("   uv run start_explorer.py --validate")
        sys.exit(1)


if __name__ == "__main__":
    main()
