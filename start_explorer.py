#!/usr/bin/env python3
"""
Startup script for the MITRE ATT&CK MCP Explorer.

This script starts the HTTP proxy server and opens the web explorer in your default browser.
"""

import os
import sys
import time
import webbrowser
import subprocess
import threading
import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_uv_available():
    """Check if uv is available in the system."""
    return shutil.which('uv') is not None


def start_http_proxy():
    """Start the HTTP proxy server using uv run."""
    try:
        logger.info("Starting HTTP proxy server with uv...")

        # Use uv run if available, otherwise fall back to python
        if check_uv_available():
            cmd = ['uv', 'run', 'http_proxy.py']
            logger.info("Using uv run to start HTTP proxy server")
        else:
            cmd = [sys.executable, 'http_proxy.py']
            logger.info("uv not found, using python directly")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        # Stream output
        for line in iter(process.stdout.readline, ''):
            if line:
                print("[HTTP Proxy] {line.strip()}")

        return process
    except Exception:
        logger.error("Failed to start HTTP proxy server: {e}")
        return None


def open_web_explorer():
    """Open the web explorer in the default browser."""
    try:
        # Get the absolute path to the HTML file
        html_file = Path(__file__).parent / 'web_explorer.html'
        file_url = "file://{html_file.absolute()}"

        logger.info("Opening web explorer: {file_url}")
        webbrowser.open(file_url)

    except Exception:
        logger.error("Failed to open web explorer: {e}")


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        if check_uv_available():
            # Check if dependencies are synced
            result = subprocess.run(['uv', 'sync', '--check'],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning("Dependencies may not be synced. Running uv sync...")
                subprocess.run(['uv', 'sync'], check=True)
                logger.info("Dependencies synced successfully")
        else:
            logger.warning("uv not found. Make sure dependencies are installed manually.")

    except subprocess.CalledProcessError as e:
        logger.error("Failed to sync dependencies: {e}")
        return False
    except Exception:
        logger.error("Error checking dependencies: {e}")
        return False

    return True


def main():
    """Main function to start everything."""
    print("🛡️  MITRE ATT&CK MCP Explorer Startup")
    print("=" * 50)

    # Check if web_explorer.html exists
    html_file = Path('web_explorer.html')
    if not html_file.exists():
        logger.error("web_explorer.html not found in current directory")
        sys.exit(1)

    # Check if http_proxy.py exists
    proxy_file = Path('http_proxy.py')
    if not proxy_file.exists():
        logger.error("http_proxy.py not found in current directory")
        sys.exit(1)

    # Check dependencies
    if not check_dependencies():
        logger.error("Dependency check failed")
        sys.exit(1)

    try:
        # Start HTTP proxy server in background thread
        def run_server():
            start_http_proxy()

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Wait a bit for server to start
        logger.info("Waiting for HTTP proxy server to start...")
        time.sleep(8)

        # Open web explorer
        open_web_explorer()

        print("\n✅ Setup complete!")
        print("📋 Instructions:")
        print("   1. The HTTP proxy server is running on http://127.0.0.1:8000")
        print("   2. The web explorer should have opened in your browser")
        print("   3. If not, manually open: web_explorer.html")
        print("   4. The web explorer connects to the HTTP proxy, which provides access to MCP tools")
        print("   5. Press Ctrl+C to stop the server")

        print("\n🔧 Available Tools:")
        print("   • search_attack - Search across all ATT&CK entities")
        print("   • list_tactics - Get all MITRE ATT&CK tactics")
        print("   • get_technique - Get detailed technique information")
        print("   • get_group_techniques - Get techniques used by a group")
        print("   • get_technique_mitigations - Get mitigations for a technique")

        if not check_uv_available():
            print("\n💡 Tip: Install uv for better dependency management:")
            print("   https://docs.astral.sh/uv/getting-started/installation/")

        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")

    except Exception:
        logger.error("Error during startup: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
