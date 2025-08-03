#!/usr/bin/env python3
"""
HTTP Proxy for MITRE ATT&CK MCP Server

This module provides an HTTP interface to the MCP server, allowing web-based
interaction with all 8 MITRE ATT&CK analysis tools.
"""

import asyncio
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import DataLoader
from mcp_server import create_mcp_server

logger = logging.getLogger(__name__)

class MCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP server proxy."""
    
    def __init__(self, *args, mcp_server=None, **kwargs):
        self.mcp_server = mcp_server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            # Serve the web explorer
            self.serve_web_explorer()
        elif parsed_path.path == '/tools':
            # Return available tools
            self.serve_tools_list()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/call_tool':
            # Handle tool calls
            self.handle_tool_call()
        else:
            self.send_error(404, "Not Found")
    
    def serve_web_explorer(self):
        """Serve the web explorer HTML."""
        try:
            with open('web_explorer.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "Web explorer not found")
        except Exception as e:
            logger.error(f"Error serving web explorer: {e}")
            self.send_error(500, "Internal Server Error")
    
    def serve_tools_list(self):
        """Serve the list of available tools."""
        try:
            tools = [
                {
                    "name": "search_attack",
                    "description": "Search across all MITRE ATT&CK entities",
                    "category": "basic"
                },
                {
                    "name": "get_technique",
                    "description": "Get detailed information about a specific technique",
                    "category": "basic"
                },
                {
                    "name": "list_tactics",
                    "description": "List all MITRE ATT&CK tactics",
                    "category": "basic"
                },
                {
                    "name": "get_group_techniques",
                    "description": "Get techniques used by a threat group",
                    "category": "basic"
                },
                {
                    "name": "get_technique_mitigations",
                    "description": "Get mitigations for a specific technique",
                    "category": "basic"
                },
                {
                    "name": "build_attack_path",
                    "description": "Build attack paths through the kill chain",
                    "category": "advanced"
                },
                {
                    "name": "analyze_coverage_gaps",
                    "description": "Analyze security coverage gaps",
                    "category": "advanced"
                },
                {
                    "name": "detect_technique_relationships",
                    "description": "Detect complex technique relationships",
                    "category": "advanced"
                }
            ]
            
            response = json.dumps(tools, indent=2)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error serving tools list: {e}")
            self.send_error(500, "Internal Server Error")
    
    def handle_tool_call(self):
        """Handle tool execution requests."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON request
            request_data = json.loads(post_data.decode('utf-8'))
            tool_name = request_data.get('tool')
            parameters = request_data.get('parameters', {})
            
            if not tool_name:
                self.send_error(400, "Missing tool name")
                return
            
            # Execute tool asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result, _ = loop.run_until_complete(
                    self.mcp_server.call_tool(tool_name, parameters)
                )
                
                # Extract text content
                if result and len(result) > 0:
                    response_text = result[0].text
                else:
                    response_text = "No results returned"
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Content-Length', str(len(response_text.encode('utf-8'))))
                self.end_headers()
                self.wfile.write(response_text.encode('utf-8'))
                
            finally:
                loop.close()
                
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
        except Exception as e:
            logger.error(f"Error handling tool call: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def log_message(self, format, *args):
        """Override to use proper logging."""
        logger.info(f"{self.address_string()} - {format % args}")

def create_http_handler(mcp_server):
    """Create HTTP handler with MCP server instance."""
    def handler(*args, **kwargs):
        return MCPHTTPHandler(*args, mcp_server=mcp_server, **kwargs)
    return handler

async def start_http_proxy(host=None, port=None):
    """Start the HTTP proxy server."""
    # Use environment variables with defaults
    host = host or os.getenv('MCP_HTTP_HOST', 'localhost')
    port = port or int(os.getenv('MCP_HTTP_PORT', '8000'))
    """Start the HTTP proxy server."""
    try:
        # Initialize data loader and MCP server
        logger.info("Initializing MITRE ATT&CK data loader...")
        data_loader = DataLoader()
        data_loader.load_data_source('mitre_attack')
        
        logger.info("Creating MCP server...")
        mcp_server = create_mcp_server(data_loader)
        
        # Create HTTP server
        handler_class = create_http_handler(mcp_server)
        httpd = HTTPServer((host, port), handler_class)
        
        logger.info(f"Starting HTTP proxy server on http://{host}:{port}")
        logger.info("Available endpoints:")
        logger.info(f"  - Web Interface: http://{host}:{port}/")
        logger.info(f"  - Tools List: http://{host}:{port}/tools")
        logger.info(f"  - Tool Execution: POST http://{host}:{port}/call_tool")
        
        # Start server
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Shutting down HTTP proxy server...")
        httpd.shutdown()
    except Exception as e:
        logger.error(f"Error starting HTTP proxy: {e}")
        raise

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start the HTTP proxy
    asyncio.run(start_http_proxy())
