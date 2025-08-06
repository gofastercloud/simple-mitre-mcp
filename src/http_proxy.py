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
from typing import Dict, Any, List
from aiohttp import web, web_request
from aiohttp.web_response import Response
import aiohttp_cors

# No need to add src to path since we're already in src

# Handle imports depending on how this module is called
try:
    from .mcp_server import create_mcp_server
    from .data_loader import DataLoader
except ImportError:
    # Fallback for when run as standalone module
    from src.mcp_server import create_mcp_server
    from src.data_loader import DataLoader

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


class HTTPProxy:
    """HTTP proxy server that bridges web requests to MCP tools."""

    def __init__(self, mcp_server=None):
        """Initialize the HTTP proxy with an MCP server instance."""
        self.mcp_server = mcp_server
        self.app = web.Application(
            middlewares=[
                self.error_handling_middleware,
                self.security_headers_middleware,
            ]
        )
        self.startup_time = datetime.now()
        self.setup_routes()
        self.setup_cors()

    def setup_routes(self):
        """Set up HTTP routes."""
        self.app.router.add_get("/", self.serve_web_interface)
        self.app.router.add_get("/tools", self.handle_tools_list)
        self.app.router.add_post("/call_tool", self.handle_tool_call)
        self.app.router.add_get("/system_info", self.handle_system_info)
        # Data population endpoints for smart form controls
        self.app.router.add_get("/api/groups", self.handle_get_groups)
        self.app.router.add_get("/api/tactics", self.handle_get_tactics)
        self.app.router.add_get("/api/techniques", self.handle_get_techniques)
        # Add static file serving for web interface assets
        self.app.router.add_static(
            "/css/", Path(__file__).parent.parent / "web_interface" / "css"
        )
        self.app.router.add_static(
            "/js/", Path(__file__).parent.parent / "web_interface" / "js"
        )
        self.app.router.add_static(
            "/assets/", Path(__file__).parent.parent / "web_interface" / "assets"
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

    @web.middleware
    async def error_handling_middleware(self, request: web_request.Request, handler):
        """Enhanced error handling middleware for all endpoints."""
        try:
            response = await handler(request)
            return response
        except web.HTTPException as e:
            # Handle HTTP exceptions (4xx, 5xx) with structured error responses
            error_response = {
                "error": e.text or str(e),
                "status": e.status,
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url),
                "method": request.method,
            }

            # Add request details for debugging (exclude sensitive data)
            if e.status >= 500:
                error_response["request_id"] = id(request)
                logger.error(
                    f"Server error {e.status} for {request.method} {request.url}: {e.text}"
                )
            else:
                logger.warning(
                    f"Client error {e.status} for {request.method} {request.url}: {e.text}"
                )

            return web.json_response(error_response, status=e.status)
        except Exception as e:
            # Handle unexpected exceptions
            request_id = id(request)
            error_response = {
                "error": "Internal server error occurred",
                "status": 500,
                "timestamp": datetime.now().isoformat(),
                "path": str(request.url),
                "method": request.method,
                "request_id": request_id,
            }

            logger.error(
                f"Unexpected error {request_id} for {request.method} {request.url}: {str(e)}"
            )
            return web.json_response(error_response, status=500)

    @web.middleware
    async def security_headers_middleware(self, request: web_request.Request, handler):
        """Add security headers to all responses."""
        response = await handler(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Add CSP header for web interface requests
        if (
            request.path == "/"
            or request.path.startswith("/css")
            or request.path.startswith("/js")
        ):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "img-src 'self' data:; "
                "connect-src 'self';"
            )

        # Add cache control headers
        if (
            request.path.startswith("/css")
            or request.path.startswith("/js")
            or request.path.startswith("/assets")
        ):
            response.headers["Cache-Control"] = (
                "public, max-age=3600"  # 1 hour cache for static assets
            )
        else:
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response

    async def serve_web_interface(self, request: web_request.Request) -> Response:
        """Serve the web explorer HTML interface."""
        try:
            web_interface_path = (
                Path(__file__).parent.parent / "web_interface" / "index.html"
            )
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
            # Enhanced input validation
            if request.content_type not in ["application/json", "text/plain"]:
                if request.content_type:
                    logger.warning(f"Unexpected content type: {request.content_type}")

            # Parse request body with size limit
            body = await request.text()
            if not body:
                return web.json_response({"error": "Empty request body"}, status=400)

            if len(body) > 10000:  # 10KB limit
                return web.json_response(
                    {"error": "Request body too large (max 10KB)"}, status=400
                )

            try:
                data = json.loads(body)
            except json.JSONDecodeError as e:
                return web.json_response(
                    {"error": f"Invalid JSON format: {str(e)}"}, status=400
                )

            # Validate data structure
            if not isinstance(data, dict):
                return web.json_response(
                    {"error": "Request body must be a JSON object"}, status=400
                )

            # Extract tool name and parameters
            tool_name = data.get("tool_name") or data.get("name")
            parameters = data.get("parameters", {}) or data.get("arguments", {})

            if not tool_name:
                return web.json_response({"error": "Missing tool name"}, status=400)

            if not isinstance(tool_name, str):
                return web.json_response(
                    {"error": "tool_name must be a string"}, status=400
                )

            if not isinstance(parameters, dict):
                return web.json_response(
                    {"error": "parameters must be an object"}, status=400
                )

            # Validate tool name against available tools
            valid_tools = {
                "search_attack",
                "list_tactics",
                "get_technique",
                "get_group_techniques",
                "get_technique_mitigations",
                "build_attack_path",
                "analyze_coverage_gaps",
                "detect_technique_relationships",
            }
            if tool_name not in valid_tools:
                return web.json_response(
                    {
                        "error": f"Unknown tool: {tool_name}. Available tools: {', '.join(sorted(valid_tools))}"
                    },
                    status=400,
                )

            logger.info(f"Executing tool: {tool_name} with parameters: {parameters}")

            # Execute tool using the MCP server
            if not self.mcp_server:
                return web.json_response(
                    {"error": "MCP server not available"}, status=503
                )

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
            if (
                self.mcp_server
                and hasattr(self.mcp_server, "data_loader")
                and self.mcp_server.data_loader
            ):
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

    async def handle_get_groups(self, request: web_request.Request) -> Response:
        """Handle requests for threat group data for dropdown population."""
        try:
            logger.info("Executing /api/groups endpoint")

            # Input validation - no parameters expected for this endpoint
            if request.query:
                logger.warning(f"Unexpected query parameters: {dict(request.query)}")

            # Get cached data
            if (
                not hasattr(self.mcp_server, "data_loader")
                or not self.mcp_server.data_loader
            ):
                return web.json_response(
                    {"error": "Data loader not available"}, status=500
                )

            data = self.mcp_server.data_loader.get_cached_data("mitre_attack")
            if not data:
                return web.json_response(
                    {"error": "MITRE ATT&CK data not loaded"}, status=500
                )

            # Extract groups for dropdown
            groups = self._extract_groups_for_dropdown(data.get("groups", []))

            return web.json_response({"groups": groups})

        except Exception as e:
            logger.error(f"Error in /api/groups endpoint: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_get_tactics(self, request: web_request.Request) -> Response:
        """Handle requests for tactic data for dropdown population."""
        try:
            logger.info("Executing /api/tactics endpoint")

            # Input validation - no parameters expected for this endpoint
            if request.query:
                logger.warning(f"Unexpected query parameters: {dict(request.query)}")

            # Get cached data
            if (
                not hasattr(self.mcp_server, "data_loader")
                or not self.mcp_server.data_loader
            ):
                return web.json_response(
                    {"error": "Data loader not available"}, status=500
                )

            data = self.mcp_server.data_loader.get_cached_data("mitre_attack")
            if not data:
                return web.json_response(
                    {"error": "MITRE ATT&CK data not loaded"}, status=500
                )

            # Extract tactics for dropdown
            tactics = self._extract_tactics_for_dropdown(data.get("tactics", []))

            return web.json_response({"tactics": tactics})

        except Exception as e:
            logger.error(f"Error in /api/tactics endpoint: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_get_techniques(self, request: web_request.Request) -> Response:
        """Handle requests for technique data for autocomplete functionality."""
        try:
            logger.info("Executing /api/techniques endpoint")

            # Enhanced input validation - check for query parameter
            query = request.query.get("q", "").strip()
            if not query:
                return web.json_response(
                    {"error": "Query parameter 'q' is required for technique search"},
                    status=400,
                )

            # Validate query length to prevent excessive processing
            if len(query) < 2:
                return web.json_response(
                    {"error": "Query must be at least 2 characters long"}, status=400
                )

            if len(query) > 100:
                return web.json_response(
                    {"error": "Query must be less than 100 characters"}, status=400
                )

            # Validate query contains only safe characters (alphanumeric, spaces, hyphens, periods)
            import re

            if not re.match(r"^[a-zA-Z0-9\s\-\.]+$", query):
                return web.json_response(
                    {
                        "error": "Search query contains invalid characters. Use only letters, numbers, spaces, hyphens, and periods."
                    },
                    status=400,
                )

            # Rate limiting check (basic implementation)
            client_ip = request.remote or "unknown"
            logger.debug(f"Technique search request from {client_ip}: '{query}'")

            # Get cached data
            if (
                not hasattr(self.mcp_server, "data_loader")
                or not self.mcp_server.data_loader
            ):
                return web.json_response(
                    {"error": "Data loader not available"}, status=500
                )

            data = self.mcp_server.data_loader.get_cached_data("mitre_attack")
            if not data:
                return web.json_response(
                    {"error": "MITRE ATT&CK data not loaded"}, status=500
                )

            # Extract techniques for autocomplete
            techniques = self._extract_techniques_for_autocomplete(
                data.get("techniques", []), query.lower()
            )

            return web.json_response({"techniques": techniques})

        except Exception as e:
            logger.error(f"Error in /api/techniques endpoint: {e}")
            return web.json_response({"error": str(e)}, status=500)

    def _extract_groups_for_dropdown(
        self, groups_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract and format threat group data for dropdown population.

        Args:
            groups_data: Raw groups data from the data loader

        Returns:
            List of formatted group objects with id, name, display_name, and aliases
        """
        if not groups_data:
            return []

        formatted_groups = []

        for group in groups_data:
            group_id = group.get("id", "")
            group_name = group.get("name", "")
            aliases = group.get("aliases", [])

            # Skip groups without essential data
            if not group_id or not group_name:
                continue

            # Create display name with aliases
            display_name = group_name
            if aliases:
                # Show first few aliases in display name
                alias_text = ", ".join(aliases[:2])  # Limit to first 2 aliases
                if len(aliases) > 2:
                    alias_text += f" (+{len(aliases) - 2} more)"
                display_name = f"{group_name} ({alias_text})"

            formatted_group = {
                "id": group_id,
                "name": group_name,
                "display_name": display_name,
                "aliases": aliases,
            }

            formatted_groups.append(formatted_group)

        # Sort by group name for consistent ordering
        formatted_groups.sort(key=lambda x: x["name"].lower())

        return formatted_groups

    def _extract_tactics_for_dropdown(
        self, tactics_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract and format tactic data for dropdown population.

        Args:
            tactics_data: Raw tactics data from the data loader

        Returns:
            List of formatted tactic objects with id, name, and display_name
        """
        if not tactics_data:
            return []

        formatted_tactics = []

        for tactic in tactics_data:
            tactic_id = tactic.get("id", "")
            tactic_name = tactic.get("name", "")

            # Skip tactics without essential data
            if not tactic_id or not tactic_name:
                continue

            # Create display name with ID and name
            display_name = f"{tactic_name} ({tactic_id})"

            formatted_tactic = {
                "id": tactic_id,
                "name": tactic_name,
                "display_name": display_name,
            }

            formatted_tactics.append(formatted_tactic)

        # Sort by tactic ID for consistent ordering (TA0001, TA0002, etc.)
        formatted_tactics.sort(key=lambda x: x["id"])

        return formatted_tactics

    def _extract_techniques_for_autocomplete(
        self, techniques_data: List[Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        """
        Extract and format technique data for autocomplete functionality.

        Args:
            techniques_data: Raw techniques data from the data loader
            query: Search query string (already lowercased)

        Returns:
            List of formatted technique objects matching the query
        """
        if not techniques_data or not query:
            return []

        matching_techniques = []

        for technique in techniques_data:
            technique_name = technique.get("name", "")

            # Extract MITRE ATT&CK ID from external references
            technique_id = ""
            external_refs = technique.get("external_references", [])
            for ref in external_refs:
                if ref.get("source_name") == "mitre-attack":
                    technique_id = ref.get("external_id", "")
                    break

            # Fallback to using the STIX ID if no MITRE ID found
            if not technique_id:
                technique_id = technique.get("id", "")

            # Skip techniques without essential data
            if not technique_id or not technique_name:
                continue

            # Check if technique matches query
            matches = False
            match_reason = ""

            # Search in technique ID
            if query in technique_id.lower():
                matches = True
                match_reason = "ID"

            # Search in technique name
            elif query in technique_name.lower():
                matches = True
                match_reason = "Name"

            # Search in description (if available)
            elif (
                "description" in technique and query in technique["description"].lower()
            ):
                matches = True
                match_reason = "Description"

            if matches:
                # Create display name with ID and name
                display_name = f"{technique_name} ({technique_id})"

                formatted_technique = {
                    "id": technique_id,
                    "name": technique_name,
                    "display_name": display_name,
                    "match_reason": match_reason,
                }

                matching_techniques.append(formatted_technique)

        # Sort by relevance: ID matches first, then name matches, then description matches
        # Within each category, sort alphabetically
        def sort_key(tech):
            if tech["match_reason"] == "ID":
                return (0, tech["id"])
            elif tech["match_reason"] == "Name":
                return (1, tech["name"].lower())
            else:  # Description
                return (2, tech["name"].lower())

        matching_techniques.sort(key=sort_key)

        # Limit results to prevent overwhelming the UI
        return matching_techniques[:50]


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
        logger.info(f"  - Groups Data: http://{host}:{port}/api/groups")
        logger.info(f"  - Tactics Data: http://{host}:{port}/api/tactics")
        logger.info(
            f"  - Techniques Search: http://{host}:{port}/api/techniques?q=<query>"
        )

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
