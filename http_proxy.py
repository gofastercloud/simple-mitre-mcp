#!/usr/bin/env python3
"""
HTTP Proxy Server for MITRE ATT&CK MCP Server

This module provides an HTTP proxy that bridges web browser requests to the MCP server,
enabling web-based access to all MCP tools through a standard HTTP API.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from aiohttp import web, web_request
from aiohttp.web_response import Response
import aiohttp_cors

from mcp_server import create_mcp_server
from data_loader import DataLoader

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


class HTTPProxy:
    """HTTP proxy server that bridges web requests to MCP tools."""

    def __init__(self, mcp_server):
        """Initialize the HTTP proxy with an MCP server instance."""
        self.mcp_server = mcp_server
        self.app = web.Application()
        self.startup_time = datetime.now()
        self.setup_routes()
        self.setup_cors()

    def setup_routes(self):
        """Set up HTTP routes."""
        self.app.router.add_get("/", self.serve_web_interface)
        self.app.router.add_get("/tools", self.handle_tools_list)
        self.app.router.add_post("/call_tool", self.handle_tool_call)
        self.app.router.add_get("/system_info", self.handle_system_info)
        # Add static file serving for web interface assets
        self.app.router.add_static(
            "/css/", Path(__file__).parent / "web_interface" / "css"
        )
        self.app.router.add_static(
            "/js/", Path(__file__).parent / "web_interface" / "js"
        )
        self.app.router.add_static(
            "/assets/", Path(__file__).parent / "web_interface" / "assets"
        )

    def setup_cors(self):
        """Set up CORS to allow browser requests."""
        cors = aiohttp_cors.setup(
            self.app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*",
                )
            },
        )

        # Add CORS to all routes
        for route in list(self.app.router.routes()):
            cors.add(route)

    async def serve_web_interface(self, request: web_request.Request) -> Response:
        """Serve the web explorer HTML interface."""
        try:
            web_interface_path = Path(__file__).parent / "web_interface" / "index.html"
            if web_interface_path.exists():
                with open(web_interface_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                return web.Response(text=html_content, content_type="text/html")
            else:
                return web.Response(
                    text="Web interface not found. Please ensure web_interface/index.html exists.",
                    status=404,
                )
        except Exception as e:
            logger.error(f"Error serving web interface: {e}")
            return web.Response(
                text=f"Error loading web interface: {str(e)}", status=500
            )

    async def handle_tools_list(self, request: web_request.Request) -> Response:
        """Handle requests for the list of available tools."""
        try:
            tools = [
                {
                    "name": "search_attack",
                    "description": "Search across all MITRE ATT&CK entities (tactics, techniques, groups, mitigations)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"],
                    },
                },
                {
                    "name": "list_tactics",
                    "description": "List all MITRE ATT&CK tactics",
                    "inputSchema": {"type": "object", "properties": {}, "required": []},
                },
                {
                    "name": "get_technique",
                    "description": "Get detailed information about a specific technique",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "technique_id": {
                                "type": "string",
                                "description": "MITRE technique ID (e.g., T1055)",
                            }
                        },
                        "required": ["technique_id"],
                    },
                },
                {
                    "name": "get_group_techniques",
                    "description": "Get techniques used by a specific threat group",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "group_id": {
                                "type": "string",
                                "description": "MITRE group ID (e.g., G0016)",
                            }
                        },
                        "required": ["group_id"],
                    },
                },
                {
                    "name": "get_technique_mitigations",
                    "description": "Get mitigations for a specific technique",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "technique_id": {
                                "type": "string",
                                "description": "MITRE technique ID (e.g., T1055)",
                            }
                        },
                        "required": ["technique_id"],
                    },
                },
                {
                    "name": "build_attack_path",
                    "description": "Construct multi-stage attack paths through the MITRE ATT&CK kill chain",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "start_tactic": {
                                "type": "string",
                                "description": "Starting tactic ID (e.g., TA0001)",
                            },
                            "end_tactic": {
                                "type": "string",
                                "description": "Target tactic ID (e.g., TA0040)",
                            },
                            "group_id": {
                                "type": "string",
                                "description": "Optional: Filter by specific threat group",
                            },
                            "platform": {
                                "type": "string",
                                "description": "Optional: Filter by platform (Windows, Linux, macOS)",
                            },
                        },
                        "required": ["start_tactic", "end_tactic"],
                    },
                },
                {
                    "name": "analyze_coverage_gaps",
                    "description": "Analyze defensive coverage gaps against threat groups",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "threat_groups": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Array of threat group IDs",
                            },
                            "technique_list": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional: Array of specific techniques to analyze",
                            },
                            "exclude_mitigations": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional: Array of implemented mitigation IDs to exclude",
                            },
                        },
                        "required": ["threat_groups"],
                    },
                },
                {
                    "name": "detect_technique_relationships",
                    "description": "Discover complex STIX relationships and attribution chains",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "technique_id": {
                                "type": "string",
                                "description": "Primary technique to analyze",
                            },
                            "relationship_types": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional: Array of relationship types to include",
                            },
                            "depth": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 3,
                                "description": "Optional: Relationship traversal depth (default: 2, max: 3)",
                            },
                        },
                        "required": ["technique_id"],
                    },
                },
            ]

            return web.json_response({"tools": tools})

        except Exception as e:
            logger.error(f"Error handling tools list: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_tool_call(self, request: web_request.Request) -> Response:
        """Handle tool execution requests."""
        try:
            # Parse request body
            body = await request.text()
            if not body:
                return web.json_response({"error": "Empty request body"}, status=400)

            try:
                data = json.loads(body)
            except json.JSONDecodeError as e:
                return web.json_response(
                    {"error": f"Invalid JSON: {str(e)}"}, status=400
                )

            # Extract tool name and parameters
            tool_name = data.get("tool_name") or data.get("name")
            parameters = data.get("parameters", {}) or data.get("arguments", {})

            if not tool_name:
                return web.json_response({"error": "Missing tool name"}, status=400)

            logger.info(f"Executing tool: {tool_name} with parameters: {parameters}")

            # Execute tool using the MCP server
            try:
                result, _ = await self.mcp_server.call_tool(tool_name, parameters)

                # Extract text content
                if result and len(result) > 0:
                    response_text = result[0].text
                else:
                    response_text = "No results returned"

                return web.Response(
                    text=response_text, content_type="text/plain", charset="utf-8"
                )

            except Exception as tool_error:
                logger.error(f"Tool execution error: {tool_error}")
                return web.json_response(
                    {"error": f"Tool execution failed: {str(tool_error)}"}, status=500
                )

        except Exception as e:
            logger.error(f"Error handling tool call: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_system_info(self, request: web_request.Request) -> Response:
        """Handle requests for comprehensive system information."""
        try:
            logger.info("Executing system_info endpoint")

            # Get data statistics from MCP server
            data_stats = await self._get_data_statistics()

            # Get server version from package metadata or default
            server_version = "1.0.0"  # Could be extracted from pyproject.toml in future

            system_info = {
                "server_info": {
                    "version": server_version,
                    "mcp_protocol_version": "1.0",
                    "startup_time": self.startup_time.isoformat(),
                    "data_source": "MITRE ATT&CK Enterprise",
                },
                "data_statistics": data_stats,
                "capabilities": {
                    "basic_tools": 5,
                    "advanced_tools": 3,
                    "total_tools": 8,
                    "web_interface": True,
                    "api_access": True,
                },
            }

            return web.json_response(system_info)

        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _get_data_statistics(self) -> Dict[str, Any]:
        """Extract comprehensive statistics from loaded data."""
        stats = {}

        try:
            # Get cached data from the data loader
            if hasattr(self.mcp_server, "data_loader") and self.mcp_server.data_loader:
                data = self.mcp_server.data_loader.get_cached_data("mitre_attack")

                if data:
                    # Count entities by type
                    stats["techniques_count"] = len(data.get("techniques", []))
                    stats["tactics_count"] = len(data.get("tactics", []))
                    stats["groups_count"] = len(data.get("groups", []))
                    stats["mitigations_count"] = len(data.get("mitigations", []))

                    # Count relationships
                    stats["relationships_count"] = await self._count_relationships()

                    # Get data freshness information
                    stats["last_updated"] = self.startup_time.isoformat()
                    stats["data_loaded"] = True
                else:
                    # No data loaded
                    stats = {
                        "techniques_count": 0,
                        "tactics_count": 0,
                        "groups_count": 0,
                        "mitigations_count": 0,
                        "relationships_count": 0,
                        "last_updated": None,
                        "data_loaded": False,
                    }
            else:
                # Data loader not available
                stats = {
                    "techniques_count": 0,
                    "tactics_count": 0,
                    "groups_count": 0,
                    "mitigations_count": 0,
                    "relationships_count": 0,
                    "last_updated": None,
                    "data_loaded": False,
                }

        except Exception as e:
            logger.warning(f"Could not get data statistics: {e}")
            # Return default stats on error
            stats = {
                "techniques_count": 0,
                "tactics_count": 0,
                "groups_count": 0,
                "mitigations_count": 0,
                "relationships_count": 0,
                "last_updated": None,
                "data_loaded": False,
                "error": str(e),
            }

        return stats

    async def _count_relationships(self) -> int:
        """Count the total number of relationships in the loaded data."""
        try:
            if hasattr(self.mcp_server, "data_loader") and self.mcp_server.data_loader:
                # Try to get relationships from cached data
                data = self.mcp_server.data_loader.get_cached_data("mitre_attack")
                if data and "relationships" in data:
                    return len(data["relationships"])

                # Try to get relationships from the separate relationships cache
                relationships_data = self.mcp_server.data_loader.get_cached_data(
                    "mitre_attack_relationships"
                )
                if relationships_data:
                    return len(relationships_data)

            return 0

        except Exception as e:
            logger.warning(f"Could not count relationships: {e}")
            return 0


async def create_http_proxy_server(host: str = "localhost", port: int = 8000):
    """Create and configure the HTTP proxy server."""
    try:
        # Create data loader and load MITRE ATT&CK data
        logger.info("Loading MITRE ATT&CK data...")
        data_loader = DataLoader()

        # Load the MITRE ATT&CK data source
        mitre_data = data_loader.load_data_source("mitre_attack")
        logger.info(
            f"Loaded {sum(len(entities) for entities in mitre_data.values())} entities"
        )

        # Create MCP server instance (synchronous)
        logger.info("Creating MCP server instance...")
        mcp_server = create_mcp_server(data_loader)

        # Create HTTP proxy
        proxy = HTTPProxy(mcp_server)

        # Create and start the web server
        runner = web.AppRunner(proxy.app)
        await runner.setup()

        site = web.TCPSite(runner, host, port)
        await site.start()

        logger.info(f"Starting HTTP proxy server on http://{host}:{port}")
        logger.info("Available endpoints:")
        logger.info(f"  - Web Interface: http://{host}:{port}/")
        logger.info(f"  - Tools List: http://{host}:{port}/tools")
        logger.info(f"  - Tool Execution: POST http://{host}:{port}/call_tool")
        logger.info(f"  - System Information: http://{host}:{port}/system_info")

        return runner, mcp_server

    except Exception as e:
        logger.error(f"Failed to create HTTP proxy server: {e}")
        raise


async def main():
    """Main entry point for the HTTP proxy server."""
    # Get configuration from environment variables
    host = os.getenv("MCP_HTTP_HOST", "localhost")
    port = int(os.getenv("MCP_HTTP_PORT", "8000"))

    try:
        # Create and start the server
        runner, mcp_server = await create_http_proxy_server(host, port)

        # Keep the server running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down HTTP proxy server...")
        finally:
            await runner.cleanup()

    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
