#!/usr/bin/env python3
"""
Web Explorer Launcher for MITRE ATT&CK MCP Server

This script provides a convenient way to start the web interface for the MITRE ATT&CK MCP server.
It automatically starts the HTTP proxy server and opens the web browser to the interface.

Enhanced with comprehensive dependency validation, health checks, graceful shutdown,
and command-line options for debugging and validation.
"""

import argparse
import asyncio
import importlib
import json
import logging
import os
import signal
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import urllib.request
import urllib.error

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

logger = logging.getLogger(__name__)
shutdown_requested = False


def check_port_available(host: str, port: int) -> bool:
    """Check if a port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def get_module_version(module_name: str) -> Optional[str]:
    """Get the version of a module if available."""
    try:
        module = importlib.import_module(module_name)
        return getattr(module, '__version__', 'Unknown')
    except (ImportError, AttributeError):
        return None


def validate_dependencies(verbose: bool = False) -> Tuple[bool, List[str]]:
    """
    Validate that all required dependencies are available for the web explorer.

    Args:
        verbose: Show detailed version information

    Returns:
        Tuple[bool, List[str]]: (success, list of error messages)
    """
    required_modules = [
        ("aiohttp", "aiohttp>=3.12.15", True),
        ("aiohttp_cors", "aiohttp-cors>=0.8.1", True),
        ("stix2", "stix2>=3.0.0", True),
        ("mcp", "mcp>=0.5.0", True),
        ("yaml", "PyYAML", True),
        ("asyncio", "Built-in Python module", False),
        ("logging", "Built-in Python module", False),
        ("threading", "Built-in Python module", False),
        ("webbrowser", "Built-in Python module", False),
        ("pathlib", "Built-in Python module", False),
    ]

    missing_modules = []
    print("🔍 Validating web explorer dependencies...")

    for module_name, package_info, check_version in required_modules:
        try:
            importlib.import_module(module_name)
            version = get_module_version(module_name) if check_version else None
            
            if verbose and version:
                print(f"  ✅ {module_name} v{version} - OK")
            else:
                print(f"  ✅ {module_name} - OK")
        except ImportError as e:
            error_msg = f"  ❌ {module_name} - MISSING ({package_info})"
            print(error_msg)
            missing_modules.append(f"{module_name}: {str(e)}")

    # Test project-specific imports
    project_modules = [
        ("src.http_proxy", "HTTP proxy server module"),
        ("src.mcp_server", "MCP server implementation"),
        ("src.data_loader", "Data loader module"),
        ("src.config_loader", "Configuration loader module"),
        ("src.parsers.stix_parser", "STIX parser module"),
    ]

    print("\n🔍 Validating project modules...")
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


def validate_web_interface_structure() -> Tuple[bool, List[str]]:
    """
    Validate the complete web interface file structure.
    
    Returns:
        Tuple[bool, List[str]]: (success, list of error messages)
    """
    issues = []
    print("🔍 Validating web interface structure...")
    
    # Required web interface files
    web_files = [
        "web_interface/index.html",
        "web_interface/css/styles.css", 
        "web_interface/css/components.css",
        "web_interface/js/app.js",
        "web_interface/js/api.js",
        "web_interface/js/SystemDashboard.js",
        "web_interface/js/ToolsSection.js",
        "web_interface/js/ResultsSection.js",
        "web_interface/js/SmartFormControls.js",
        "web_interface/js/ThemeToggle.js"
    ]
    
    for file_path in web_files:
        path = Path(file_path)
        if not path.exists():
            issues.append(f"Web interface file missing: {file_path}")
            print(f"  ❌ {file_path} - MISSING")
        elif path.stat().st_size == 0:
            issues.append(f"Web interface file is empty: {file_path}")
            print(f"  ❌ {file_path} - EMPTY")
        else:
            print(f"  ✅ {file_path} - OK")
    
    return len(issues) == 0, issues


def validate_configuration_files() -> Tuple[bool, List[str]]:
    """
    Validate configuration files exist and have valid format.
    
    Returns:
        Tuple[bool, List[str]]: (success, list of error messages)
    """
    issues = []
    print("\n🔍 Validating configuration files...")
    
    config_files = [
        ("config/data_sources.yaml", "YAML"),
        ("config/entity_schemas.yaml", "YAML"),
        ("config/tools.yaml", "YAML"),
        ("pyproject.toml", "TOML"),
    ]
    
    for file_path, file_type in config_files:
        path = Path(file_path)
        if not path.exists():
            issues.append(f"Configuration file missing: {file_path}")
            print(f"  ❌ {file_path} - MISSING")
        else:
            # Basic format validation
            try:
                if file_type == "YAML":
                    import yaml
                    with open(path, 'r') as f:
                        yaml.safe_load(f)
                elif file_type == "TOML":
                    import tomllib
                    with open(path, 'rb') as f:
                        tomllib.load(f)
                print(f"  ✅ {file_path} - OK")
            except Exception as e:
                issues.append(f"Invalid {file_type} format in {file_path}: {e}")
                print(f"  ❌ {file_path} - INVALID FORMAT")
    
    return len(issues) == 0, issues


def validate_environment(verbose: bool = False) -> Tuple[bool, List[str]]:
    """
    Validate the environment setup for the web explorer.

    Args:
        verbose: Show detailed information

    Returns:
        Tuple[bool, List[str]]: (success, list of error messages)
    """
    issues = []

    print("🔍 Validating environment setup...")

    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 12):
        issues.append(f"Python 3.12+ required, found {python_version.major}.{python_version.minor}")
        print(f"  ❌ Python {python_version.major}.{python_version.minor} - TOO OLD")
    else:
        print(f"  ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} - OK")

    # Check project structure
    required_directories = [
        "src/",
        "web_interface/",
        "config/",
        "tests/",
    ]

    for dir_path in required_directories:
        path = Path(dir_path)
        if not path.exists() or not path.is_dir():
            issues.append(f"Required directory missing: {dir_path}")
            print(f"  ❌ {dir_path} - MISSING")
        else:
            print(f"  ✅ {dir_path} - OK")

    # Validate web interface structure
    web_ok, web_issues = validate_web_interface_structure()
    issues.extend(web_issues)

    # Validate configuration files
    config_ok, config_issues = validate_configuration_files() 
    issues.extend(config_issues)

    # Check environment variables
    host = os.getenv("MCP_HTTP_HOST", "localhost")
    port = os.getenv("MCP_HTTP_PORT", "8000")

    print(f"\n🔍 Validating server configuration...")
    
    # Validate port
    try:
        port_int = int(port)
        if port_int < 1 or port_int > 65535:
            issues.append(f"Invalid port number: {port} (must be 1-65535)")
            print(f"  ❌ Port {port} - INVALID RANGE")
        elif not check_port_available(host, port_int):
            print(f"  ⚠️  Port {port} - IN USE (will attempt to bind anyway)")
        else:
            print(f"  ✅ Port {port} - AVAILABLE")
    except ValueError:
        issues.append(f"Invalid port number: {port} (must be numeric)")
        print(f"  ❌ Port {port} - INVALID FORMAT")

    # Validate host
    if host in ['localhost', '127.0.0.1', '0.0.0.0']:
        print(f"  ✅ Host {host} - OK")
    else:
        print(f"  ⚠️  Host {host} - CUSTOM (ensure it's accessible)")

    if verbose:
        print(f"\n📊 Environment Details:")
        print(f"  • Working Directory: {os.getcwd()}")
        print(f"  • Python Executable: {sys.executable}")
        print(f"  • Platform: {sys.platform}")
        print(f"  • Process ID: {os.getpid()}")

    if issues:
        return False, issues

    print("✅ Environment validation completed successfully")
    return True, []


async def health_check(host: str, port: int, timeout: int = 10) -> Dict[str, Any]:
    """
    Perform health check on the running web explorer server.
    
    Args:
        host: Server host
        port: Server port  
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with health check results
    """
    health_status = {
        "healthy": False,
        "server_reachable": False,
        "endpoints": {},
        "response_times": {},
        "errors": []
    }
    
    base_url = f"http://{host}:{port}"
    
    # Test endpoints to check
    test_endpoints = [
        "/",
        "/tools", 
        "/system_info",
        "/api/groups",
        "/api/tactics"
    ]
    
    print(f"🏥 Running health check on {base_url}...")
    
    try:
        for endpoint in test_endpoints:
            url = base_url + endpoint
            start_time = time.time()
            
            try:
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'WebExplorerHealthCheck/1.0')
                
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    response_time = time.time() - start_time
                    health_status["endpoints"][endpoint] = {
                        "status": response.status,
                        "healthy": response.status == 200
                    }
                    health_status["response_times"][endpoint] = round(response_time * 1000, 2)
                    
                    if response.status == 200:
                        print(f"  ✅ {endpoint} - OK ({response_time*1000:.1f}ms)")
                    else:
                        print(f"  ⚠️  {endpoint} - HTTP {response.status}")
                        
            except urllib.error.URLError as e:
                health_status["endpoints"][endpoint] = {
                    "status": "error",
                    "error": str(e),
                    "healthy": False
                }
                health_status["errors"].append(f"{endpoint}: {str(e)}")
                print(f"  ❌ {endpoint} - ERROR: {str(e)}")
    
    except Exception as e:
        health_status["errors"].append(f"Health check failed: {str(e)}")
        print(f"  ❌ Health check failed: {str(e)}")
        return health_status
        
    # Determine overall health
    healthy_endpoints = sum(1 for ep in health_status["endpoints"].values() if ep.get("healthy", False))
    total_endpoints = len(test_endpoints)
    
    health_status["healthy"] = healthy_endpoints >= (total_endpoints * 0.8)  # 80% success rate
    health_status["server_reachable"] = healthy_endpoints > 0
    
    if health_status["healthy"]:
        print(f"✅ Health check passed ({healthy_endpoints}/{total_endpoints} endpoints healthy)")
    else:
        print(f"⚠️  Health check partial ({healthy_endpoints}/{total_endpoints} endpoints healthy)")
        
    return health_status


def print_troubleshooting_guide(
    dependency_errors: List[str] = None, environment_errors: List[str] = None
):
    """Print comprehensive troubleshooting guide."""
    print("\n" + "=" * 70)
    print("🔧 TROUBLESHOOTING GUIDE")
    print("=" * 70)

    if dependency_errors:
        print("\n📦 DEPENDENCY ISSUES:")
        for error in dependency_errors:
            print(f"   • {error}")

        print("\n🛠️  SOLUTIONS:")
        print("   1. Install/update dependencies:")
        print("      uv sync")
        print("   2. If UV is not available:")
        print("      pip install uv")
        print("      uv sync")
        print("   3. Check Python version (requires >=3.12):")
        print("      python --version")
        print("   4. Reinstall all dependencies:")
        print("      uv sync --reinstall")
        print("   5. Clear UV cache if issues persist:")
        print("      uv cache clean")
        print("      uv sync")

    if environment_errors:
        print("\n🌍 ENVIRONMENT ISSUES:")
        for error in environment_errors:
            print(f"   • {error}")

        print("\n🛠️  SOLUTIONS:")
        print("   1. Ensure you're in the project root directory")
        print("   2. Check file permissions (chmod +r for config files)")
        print("   3. Verify project structure is intact")
        print("   4. Try different port if current port is in use:")
        print("      MCP_HTTP_PORT=8001 uv run start_explorer.py")
        print("   5. For file structure issues, re-clone the repository")

    print("\n🏥 HEALTH CHECKS:")
    print("   • Run validation only:")
    print("     uv run start_explorer.py --validate")
    print("   • Run health check on running server:")  
    print("     uv run start_explorer.py --health-check")
    print("   • Run with verbose output:")
    print("     uv run start_explorer.py --verbose --validate")

    print("\n📞 ADDITIONAL HELP:")
    print("   • Project documentation: README.md")
    print("   • Deployment guide: deployment/TROUBLESHOOTING.md") 
    print("   • Check UV installation: uv --version")
    print("   • Run tests to verify setup: uv run python -m pytest tests/ -x")
    print("   • Enable debug logging: LOG_LEVEL=DEBUG uv run start_explorer.py")
    print("   • Check system requirements and compatibility")
    
    print("\n🚨 COMMON FIXES:")
    print("   • Import errors: uv sync --reinstall")
    print("   • Port conflicts: MCP_HTTP_PORT=8080 uv run start_explorer.py")
    print("   • Permission errors: Check file/directory permissions")
    print("   • Network issues: Check firewall and proxy settings")
    print("=" * 70)


def setup_signal_handlers():
    """Setup graceful shutdown signal handlers."""
    global shutdown_requested
    
    def signal_handler(signum, frame):
        global shutdown_requested
        signal_name = signal.Signals(signum).name
        print(f"\n🛑 Received {signal_name}, initiating graceful shutdown...")
        shutdown_requested = True
    
    # Handle common shutdown signals
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, signal_handler)
    
    # Handle SIGHUP for reload (Unix only)
    if hasattr(signal, 'SIGHUP'):
        def reload_handler(signum, frame):
            print("\n🔄 Received SIGHUP, consider restarting to reload configuration...")
        signal.signal(signal.SIGHUP, reload_handler)


def run_startup_validation(verbose: bool = False) -> bool:
    """
    Run comprehensive startup validation.

    Args:
        verbose: Show detailed validation information

    Returns:
        bool: True if all validations pass, False otherwise
    """
    print("🚀 Starting Web Explorer Validation...")
    print("=" * 60)

    # Validate Python environment first
    python_version = sys.version_info
    print(f"🐍 Python {python_version.major}.{python_version.minor}.{python_version.micro} on {sys.platform}")
    
    if verbose:
        print(f"   Executable: {sys.executable}")
        print(f"   Working Directory: {os.getcwd()}")

    # Validate dependencies
    deps_ok, dep_errors = validate_dependencies(verbose)

    # Validate environment
    env_ok, env_errors = validate_environment(verbose)

    if deps_ok and env_ok:
        print("\n✅ All validations passed! Web Explorer is ready to start.")
        print("🌐 You can start the web interface with:")
        print("   uv run start_explorer.py")
        return True
    else:
        print("\n❌ Validation failed. Please resolve the issues below:")
        print_troubleshooting_guide(
            dep_errors if not deps_ok else None, env_errors if not env_ok else None
        )
        return False


async def run_health_check(host: str, port: int) -> bool:
    """
    Run health check against a running server.
    
    Args:
        host: Server host
        port: Server port
        
    Returns:
        bool: True if health check passes
    """
    try:
        health_result = await health_check(host, port)
        
        if health_result["healthy"]:
            print("\n✅ Server health check passed!")
            
            # Show response times
            if health_result["response_times"]:
                print("\n📊 Performance Metrics:")
                for endpoint, time_ms in health_result["response_times"].items():
                    status = "🟢" if time_ms < 1000 else "🟡" if time_ms < 3000 else "🔴"
                    print(f"   {status} {endpoint}: {time_ms}ms")
            
            return True
        else:
            print("\n⚠️  Server health check failed!")
            if health_result["errors"]:
                print("Errors found:")
                for error in health_result["errors"]:
                    print(f"   • {error}")
            return False
            
    except Exception as e:
        print(f"\n❌ Health check failed with error: {e}")
        return False


def open_browser(url, delay=2):
    """Open browser after a delay to ensure server is ready."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
        logger.info(f"Opened browser to {url}")
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")


async def start_web_explorer(open_browser_flag: bool = True, verbose: bool = False):
    """
    Start the web explorer with HTTP proxy server.
    
    Args:
        open_browser_flag: Whether to open browser automatically
        verbose: Show verbose output
    """
    global shutdown_requested
    
    # Import here after validation
    from src.http_proxy import create_http_proxy_server

    # Get configuration from environment variables
    host = os.getenv("MCP_HTTP_HOST", "localhost")
    port = int(os.getenv("MCP_HTTP_PORT", "8000"))

    # Setup graceful shutdown
    setup_signal_handlers()
    
    runner = None
    mcp_server = None

    try:
        print("🚀 Starting MITRE ATT&CK MCP Web Explorer...")
        print(f"📊 Loading MITRE ATT&CK data and starting server on http://{host}:{port}")
        print("⏳ This may take 10-15 seconds for initial data loading...")
        
        if verbose:
            print(f"   Host: {host}")
            print(f"   Port: {port}")
            print(f"   Process ID: {os.getpid()}")

        # Create and start the HTTP proxy server
        start_time = time.time()
        runner, mcp_server = await create_http_proxy_server(host, port)
        startup_time = time.time() - start_time
        
        if verbose:
            print(f"   Startup time: {startup_time:.2f} seconds")

        # Start browser in a separate thread if requested
        url = f"http://{host}:{port}"
        if open_browser_flag:
            browser_thread = threading.Thread(target=open_browser, args=(url, 3))
            browser_thread.daemon = True
            browser_thread.start()
            print("🌐 Web interface will open in your browser")

        print(f"✅ Web Explorer ready at: {url}")
        print("🛠️  Available tools: 8 (5 basic + 3 advanced threat modeling)")
        print("📋 Press Ctrl+C to stop the server")
        
        if verbose:
            print(f"🔍 Debug mode enabled - verbose logging active")

        # Keep the server running with graceful shutdown handling
        shutdown_initiated = False
        try:
            while not shutdown_requested:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            if not shutdown_initiated:
                print("\n🛑 Received interrupt signal, shutting down...")
                shutdown_initiated = True
        
        # Graceful shutdown sequence
        if not shutdown_initiated:
            print("\n🛑 Shutting down Web Explorer...")
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use.")
            print(f"🔧 Try a different port:")
            print(f"   MCP_HTTP_PORT=8001 uv run start_explorer.py")
            print(f"   MCP_HTTP_PORT=9000 uv run start_explorer.py")
        else:
            print(f"❌ Network error: {e}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Failed to start Web Explorer: {e}")
        print(f"❌ Unexpected error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   - Run validation: uv run start_explorer.py --validate")
        print("   - Check logs for detailed error information")
        print("   - Ensure all dependencies are installed: uv sync")
        sys.exit(1)
        
    finally:
        # Cleanup resources
        if runner:
            print("🧹 Cleaning up server resources...")
            try:
                await runner.cleanup()
                print("✅ Web Explorer stopped cleanly")
            except Exception as cleanup_error:
                logger.error(f"Error during cleanup: {cleanup_error}")
                print(f"⚠️  Cleanup warning: {cleanup_error}")


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="MITRE ATT&CK MCP Web Explorer - Interactive threat intelligence analysis interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  MCP_HTTP_HOST=localhost    Server host (default: localhost)
  MCP_HTTP_PORT=8000        Server port (default: 8000)
  LOG_LEVEL=INFO            Logging level (DEBUG, INFO, WARNING, ERROR)

Examples:
  uv run start_explorer.py
  uv run start_explorer.py --validate --verbose
  uv run start_explorer.py --no-browser --port 9000
  MCP_HTTP_PORT=8080 uv run start_explorer.py --verbose
  LOG_LEVEL=DEBUG uv run start_explorer.py --validate

For more help, see: deployment/TROUBLESHOOTING.md
        """)

    # Main actions
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        '--validate', '-v', action='store_true',
        help='Run validation checks only (don\'t start server)')
    action_group.add_argument(
        '--health-check', action='store_true',
        help='Run health check against running server')

    # Server options
    parser.add_argument(
        '--no-browser', action='store_true',
        help='Don\'t automatically open web browser')
    parser.add_argument(
        '--port', type=int, metavar='PORT',
        help='Override server port (can also use MCP_HTTP_PORT env var)')
    parser.add_argument(
        '--host', metavar='HOST',
        help='Override server host (can also use MCP_HTTP_HOST env var)')

    # Debug options
    parser.add_argument(
        '--verbose', action='store_true',
        help='Show detailed output and debug information')
    parser.add_argument(
        '--quiet', '-q', action='store_true',
        help='Minimize output (only show errors)')

    # Utility options  
    parser.add_argument(
        '--version', action='version', version='MITRE ATT&CK MCP Web Explorer 1.0.0')

    return parser


def configure_logging(verbose: bool = False, quiet: bool = False):
    """Configure logging based on command line options."""
    if quiet:
        log_level = logging.ERROR
    elif verbose:
        log_level = logging.DEBUG
    else:
        # Check environment variable
        env_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        log_level = getattr(logging, env_level, logging.INFO)

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if verbose else '%(levelname)s: %(message)s'
    )

    # Reduce noise from some libraries in non-verbose mode
    if not verbose:
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)


def main():
    """Main entry point with comprehensive command-line interface."""
    try:
        # Parse command line arguments
        parser = create_argument_parser()
        args = parser.parse_args()

        # Configure logging
        configure_logging(args.verbose, args.quiet)

        # Override environment variables with command line arguments
        if args.host:
            os.environ['MCP_HTTP_HOST'] = args.host
        if args.port:
            os.environ['MCP_HTTP_PORT'] = str(args.port)

        host = os.getenv("MCP_HTTP_HOST", "localhost")
        port = int(os.getenv("MCP_HTTP_PORT", "8000"))

        # Handle different actions
        if args.validate:
            if not args.quiet:
                print("🔍 Running comprehensive validation...")
            success = run_startup_validation(args.verbose)
            sys.exit(0 if success else 1)

        elif args.health_check:
            if not args.quiet:
                print(f"🏥 Running health check on {host}:{port}...")
            try:
                success = asyncio.run(run_health_check(host, port))
                sys.exit(0 if success else 1)
            except Exception as e:
                print(f"❌ Health check failed: {e}")
                sys.exit(1)

        else:
            # Normal startup sequence
            if not args.quiet:
                print("🚀 MITRE ATT&CK MCP Web Explorer")
                print("=" * 50)

            # Run comprehensive startup validation unless quiet
            if not run_startup_validation(args.verbose):
                sys.exit(1)

            # Import http_proxy after validation
            try:
                from src.http_proxy import create_http_proxy_server  # noqa: F401
            except ImportError as e:
                print(f"❌ Failed to import src.http_proxy: {e}")
                print("   This indicates a project structure issue.")
                print_troubleshooting_guide(dependency_errors=[f"http_proxy: {str(e)}"])
                sys.exit(1)

            # Start the web explorer
            try:
                asyncio.run(start_web_explorer(
                    open_browser_flag=not args.no_browser,
                    verbose=args.verbose
                ))
            except KeyboardInterrupt:
                if not args.quiet:
                    print("\n👋 Goodbye!")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print(f"\n❌ Unexpected error occurred: {e}")
                print("\n🔧 Try running validation to diagnose issues:")
                print("   uv run start_explorer.py --validate --verbose")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
        sys.exit(0)
    except SystemExit:
        raise
    except Exception as e:
        print(f"❌ Critical error: {e}")
        print("🔧 Try running with --verbose for more information")
        sys.exit(1)


if __name__ == "__main__":
    main()
