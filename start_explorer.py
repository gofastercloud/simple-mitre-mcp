#!/usr/bin/env python3
"""
Web Explorer Launcher for MITRE ATT&CK MCP Server

This script provides a convenient way to start the web interface for the MITRE ATT&CK MCP server.
It automatically starts the HTTP proxy server and opens the web browser to the interface.
"""

import asyncio
import logging
import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from http_proxy import create_http_proxy_server

logger = logging.getLogger(__name__)


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
        print("   - Ensure dependencies are installed: uv sync")
        sys.exit(1)


def main():
    """Main entry point."""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    # Check if dependencies are available
    try:
        import aiohttp
        import aiohttp_cors
    except ImportError as e:
        print("❌ Missing dependencies. Please install them:")
        print("   uv sync")
        print(f"   Error: {e}")
        sys.exit(1)

    # Check if web_explorer.html exists
    web_explorer_path = Path(__file__).parent / "web_explorer.html"
    if not web_explorer_path.exists():
        print("❌ web_explorer.html not found in current directory")
        print("   Please ensure the file exists for the web interface to work")
        sys.exit(1)

    # Start the web explorer
    try:
        asyncio.run(start_web_explorer())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
