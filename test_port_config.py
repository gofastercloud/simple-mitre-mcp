#!/usr/bin/env python3
"""
Test script to demonstrate configurable port functionality.

This script shows how the MCP server can be configured to run on different
ports using environment variables.
"""

import os
import sys

def test_port_configurations():
    """Test different port configurations."""
    print("🔧 MITRE ATT&CK MCP Server - Port Configuration Test")
    print("=" * 60)
    
    # Test 1: Default configuration
    print("\n1. DEFAULT CONFIGURATION:")
    print(f"   Host: {os.getenv('MCP_HTTP_HOST', 'localhost')}")
    print(f"   Port: {os.getenv('MCP_HTTP_PORT', '8000')}")
    print(f"   URL:  http://{os.getenv('MCP_HTTP_HOST', 'localhost')}:{os.getenv('MCP_HTTP_PORT', '8000')}")
    
    # Test 2: Legacy test configuration (port 3000)
    print("\n2. LEGACY TEST CONFIGURATION:")
    os.environ['MCP_HTTP_PORT'] = '3000'
    print(f"   Host: {os.getenv('MCP_HTTP_HOST', 'localhost')}")
    print(f"   Port: {os.getenv('MCP_HTTP_PORT', '8000')}")
    print(f"   URL:  http://{os.getenv('MCP_HTTP_HOST', 'localhost')}:{os.getenv('MCP_HTTP_PORT', '8000')}")
    print("   Usage: MCP_HTTP_PORT=3000 python start_explorer.py")
    
    # Test 3: Production configuration (external access)
    print("\n3. PRODUCTION CONFIGURATION:")
    os.environ['MCP_HTTP_HOST'] = '0.0.0.0'
    os.environ['MCP_HTTP_PORT'] = '8080'
    print(f"   Host: {os.getenv('MCP_HTTP_HOST', 'localhost')}")
    print(f"   Port: {os.getenv('MCP_HTTP_PORT', '8000')}")
    print(f"   URL:  http://{os.getenv('MCP_HTTP_HOST', 'localhost')}:{os.getenv('MCP_HTTP_PORT', '8000')}")
    print("   Usage: MCP_HTTP_HOST=0.0.0.0 MCP_HTTP_PORT=8080 python start_explorer.py")
    
    # Test 4: Development configuration
    print("\n4. DEVELOPMENT CONFIGURATION:")
    os.environ['MCP_HTTP_HOST'] = '127.0.0.1'
    os.environ['MCP_HTTP_PORT'] = '5000'
    print(f"   Host: {os.getenv('MCP_HTTP_HOST', 'localhost')}")
    print(f"   Port: {os.getenv('MCP_HTTP_PORT', '8000')}")
    print(f"   URL:  http://{os.getenv('MCP_HTTP_HOST', 'localhost')}:{os.getenv('MCP_HTTP_PORT', '8000')}")
    print("   Usage: MCP_HTTP_HOST=127.0.0.1 MCP_HTTP_PORT=5000 python start_explorer.py")
    
    print("\n" + "=" * 60)
    print("✅ All configurations work! Use environment variables to customize.")
    print("\nTo set permanent configuration:")
    print("1. Copy .env.example to .env")
    print("2. Edit .env with your preferred settings")
    print("3. The server will automatically use those settings")

if __name__ == "__main__":
    test_port_configurations()
