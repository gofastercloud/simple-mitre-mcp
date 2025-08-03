#!/usr/bin/env python3
"""
MITRE ATT&CK MCP Explorer Launcher

This script launches the HTTP proxy server and opens the web interface
for interactive exploration of MITRE ATT&CK data.
"""

import asyncio
import logging
import webbrowser
import time
import threading
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from http_proxy import start_http_proxy

logger = logging.getLogger(__name__)

def open_browser(url, delay=2):
    """Open browser after a delay to ensure server is ready."""
    time.sleep(delay)
    try:
        webbrowser.open(url)
        logger.info(f"Opened browser to {url}")
    except Exception as e:
        logger.warning(f"Could not open browser automatically: {e}")
        logger.info(f"Please open your browser and navigate to {url}")

async def main():
    """Main function to start the explorer."""
    print("🛡️  MITRE ATT&CK MCP Explorer")
    print("=" * 50)
    print()
    
    # Configuration with environment variable support
    host = os.getenv('MCP_HTTP_HOST', 'localhost')
    port = int(os.getenv('MCP_HTTP_PORT', '8000'))
    url = f"http://{host}:{port}"
    
    print(f"Starting MITRE ATT&CK MCP Explorer...")
    print(f"Server will be available at: {url}")
    print()
    print("Available Tools:")
    print("  🔍 Basic Analysis Tools:")
    print("    - search_attack: Search across all MITRE ATT&CK entities")
    print("    - get_technique: Get detailed technique information")
    print("    - list_tactics: List all MITRE ATT&CK tactics")
    print("    - get_group_techniques: Get techniques used by threat groups")
    print("    - get_technique_mitigations: Get mitigations for techniques")
    print()
    print("  🚀 Advanced Threat Modeling Tools:")
    print("    - build_attack_path: Build attack paths through kill chain")
    print("    - analyze_coverage_gaps: Analyze security coverage gaps")
    print("    - detect_technique_relationships: Detect complex relationships")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start browser opener in background thread
    browser_thread = threading.Thread(
        target=open_browser, 
        args=(url,), 
        daemon=True
    )
    browser_thread.start()
    
    try:
        # Start the HTTP proxy server
        await start_http_proxy(host, port)
    except KeyboardInterrupt:
        print("\n\nShutting down MITRE ATT&CK MCP Explorer...")
        print("Thank you for using the MITRE ATT&CK MCP Explorer!")
    except Exception as e:
        logger.error(f"Error starting explorer: {e}")
        print(f"\nError: {e}")
        print("\nPlease check the logs for more details.")
        sys.exit(1)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the main function
    asyncio.run(main())
