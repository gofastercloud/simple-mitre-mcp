#!/usr/bin/env python3
"""
HTTP Proxy for MCP Server

This module provides a simple HTTP server that acts as a proxy to the MCP server,
allowing web browsers to interact with the MCP server through standard HTTP requests.
"""

import json
import logging
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time
from src.mcp_server import create_mcp_server
from src.data_loader import DataLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler that proxies requests to the MCP server."""

    def __init__(self, *args, mcp_app=None, **kwargs):
        self.mcp_app = mcp_app
        super().__init__(*args, **kwargs)

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests and proxy them to the MCP server."""
        try:
            # Parse the request
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)

            # Parse JSON request
            try:
                request_data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                self.send_error_response(400, "Invalid JSON: {e}")
                return

            # Extract method and params
            method = request_data.get('method')
            params = request_data.get('params', {})
            request_id = request_data.get('id', 1)

            logger.info("Received request: {method} with params: {params}")

            # Handle different MCP methods
            if method == 'tools/list':
                response = self.handle_tools_list(request_id)
            elif method == 'tools/call':
                tool_name = params.get('name')
                tool_args = params.get('arguments', {})
                response = asyncio.run(self.handle_tool_call(request_id, tool_name, tool_args))
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }

            # Send response
            self.send_json_response(response)

        except Exception:
            logger.error("Error handling request: {e}")
            self.send_error_response(500, "Internal server error: {e}")

    def handle_tools_list(self, request_id):
        """Handle tools/list request."""
        tools = [
            {
                "name": "search_attack",
                "description": "Search across all ATT&CK entities (tactics, techniques, groups, mitigations)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search term"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_technique",
                "description": "Get detailed information about a specific technique",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "technique_id": {"type": "string", "description": "MITRE technique ID (e.g., T1055)"}
                    },
                    "required": ["technique_id"]
                }
            },
            {
                "name": "list_tactics",
                "description": "Get all MITRE ATT&CK tactics",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_group_techniques",
                "description": "Get all techniques used by a specific threat group",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "group_id": {"type": "string", "description": "MITRE group ID (e.g., G0016)"}
                    },
                    "required": ["group_id"]
                }
            },
            {
                "name": "get_technique_mitigations",
                "description": "Get mitigations for a specific technique",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "technique_id": {"type": "string", "description": "MITRE technique ID (e.g., T1055)"}
                    },
                    "required": ["technique_id"]
                }
            },
            {
                "name": "build_attack_path",
                "description": "Build complete attack paths from initial access to objectives, showing technique sequences across tactics",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_tactic": {"type": "string", "description": "Starting tactic ID (default: TA0001 - Initial Access)"},
                        "end_tactic": {"type": "string", "description": "Target tactic ID (default: TA0040 - Impact)"},
                        "group_id": {"type": "string", "description": "Filter paths to techniques used by specific group (e.g., G0016)"},
                        "platform": {"type": "string", "description": "Filter to specific platform (Windows, Linux, macOS)"}
                    },
                    "required": []
                }
            },
            {
                "name": "analyze_coverage_gaps",
                "description": "Analyze defensive coverage gaps against threat groups or technique sets",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "threat_groups": {"type": "array", "items": {"type": "string"}, "description": "List of group IDs to analyze (e.g., ['G0016', 'G0032'])"},
                        "technique_list": {"type": "array", "items": {"type": "string"}, "description": "Specific techniques to analyze coverage for (e.g., ['T1055', 'T1059'])"},
                        "exclude_mitigations": {"type": "array", "items": {"type": "string"}, "description": "Mitigations already implemented to exclude from analysis (e.g., ['M1040', 'M1038'])"}
                    },
                    "required": []
                }
            },
            {
                "name": "detect_technique_relationships",
                "description": "Discover complex relationships between techniques, including detection, attribution, and subtechnique hierarchies",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "technique_id": {"type": "string", "description": "Primary technique to analyze relationships for (e.g., T1055)"},
                        "relationship_types": {"type": "array", "items": {"type": "string"}, "description": "Types to include: ['detects', 'subtechnique-of', 'attributed-to', 'uses', 'mitigates'] (default: all)"},
                        "depth": {"type": "integer", "description": "Relationship traversal depth (default: 2, max: 3)"}
                    },
                    "required": ["technique_id"]
                }
            }
        ]

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }

    async def handle_tool_call(self, request_id, tool_name, tool_args):
        """Handle tools/call request by calling the actual MCP tool."""
        try:
            if not self.mcp_app or not self.mcp_app.data_loader:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": "MCP server not available"
                    }
                }

            # Import the tool functions directly
            from src.mcp_server import _search_entities

            # Get the data from the data loader
            data = self.mcp_app.data_loader.get_cached_data('mitre_attack')
            if not data:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": "MITRE ATT&CK data not loaded"
                    }
                }

            # Call the appropriate tool function
            if tool_name == 'search_attack':
                query = tool_args.get('query', '')
                search_results = _search_entities(query.lower(), data)

                if not search_results:
                    result_text = "No results found for query: '{query}'"
                else:
                    result_text = "Search results for '{query}' ({len(search_results)} matches):\n\n"
                    for result in search_results:

                        result_text += "[{entity_type}] {entity_id}: {entity_name}\n"
                        result_text += "  Match: {match_reason}\n"

                        if 'description' in result and result['description']:
                            result_text += "  Description: {desc_preview}\n"

                        result_text += "\n"

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": result_text}]
                    }
                }

            elif tool_name == 'list_tactics':
                tactics = data.get('tactics', [])
                if not tactics:
                    result_text = "No tactics found in the loaded data."
                else:
                    sorted_tactics = sorted(tactics, key=lambda x: x.get('id', ''))
                    result_text = "MITRE ATT&CK TACTICS\n"
                    result_text += "===================\n\n"
                    result_text += "Total tactics: {len(sorted_tactics)}\n\n"

                    for tactic in sorted_tactics:
                        tactic_id = tactic.get('id', 'N/A')
                        tactic_name = tactic.get('name', 'N/A')
                        tactic_description = tactic.get('description', 'No description available')

                        result_text += "ID: {tactic_id}\n"
                        result_text += "Name: {tactic_name}\n"
                        result_text += "Description: {tactic_description}\n"
                        result_text += "{'-' * 50}\n\n"

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": result_text}]
                    }
                }

            elif tool_name == 'get_technique':
                technique_id = tool_args.get('technique_id', '').upper().strip()

                # Find the technique
                technique = None
                for tech in data.get('techniques', []):
                    if tech.get('id', '').upper() == technique_id:
                        technique = tech
                        break

                if not technique:
                    result_text = "Technique '{technique_id}' not found. Please verify the technique ID is correct."
                else:
                    result_text = "TECHNIQUE DETAILS\n"
                    result_text += "================\n\n"
                    result_text += "ID: {technique.get('id', 'N/A')}\n"
                    result_text += "Name: {technique.get('name', 'N/A')}\n\n"

                    description = technique.get('description', 'No description available')
                    result_text += "Description:\n{description}\n\n"

                    # Associated tactics
                    tactics = technique.get('tactics', [])
                    if tactics:
                        result_text += "Associated Tactics ({len(tactics)}):\n"
                        tactic_details = []
                        for tactic_id in tactics:
                            for tactic in data.get('tactics', []):
                                if tactic.get('id') == tactic_id:
                                    tactic_details.append("  - {tactic_id}: {tactic.get('name', 'Unknown')}")
                                    break
                            else:
                                tactic_details.append("  - {tactic_id}: (Name not found)")
                        result_text += "\n".join(tactic_details) + "\n\n"
                    else:
                        result_text += "Associated Tactics: None\n\n"

                    # Platforms
                    platforms = technique.get('platforms', [])
                    if platforms:
                        result_text += "Platforms ({len(platforms)}):\n"
                        result_text += "  " + ", ".join(platforms) + "\n\n"
                    else:
                        result_text += "Platforms: Not specified\n\n"

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": result_text}]
                    }
                }

            elif tool_name == 'get_group_techniques':
                group_id = tool_args.get('group_id', '').upper().strip()

                # Find the group
                group = None
                for grp in data.get('groups', []):
                    if grp.get('id', '').upper() == group_id:
                        group = grp
                        break

                if not group:
                    result_text = "Group '{group_id}' not found. Please verify the group ID is correct."
                else:
                    group_techniques = group.get('techniques', [])
                    if not group_techniques:
                        result_text = "No techniques found for group '{group_id}' ({group.get('name', 'Unknown')})."
                    else:
                        result_text = "GROUP TECHNIQUES\n"
                        result_text += "================\n\n"
                        result_text += "Group ID: {group.get('id', 'N/A')}\n"
                        result_text += "Group Name: {group.get('name', 'N/A')}\n"

                        aliases = group.get('aliases', [])
                        if aliases:
                            result_text += "Aliases: {', '.join(aliases)}\n"

                        result_text += "\nTechniques Used ({len(group_techniques)}):\n"
                        result_text += "{'-' * 40}\n\n"

                        for i, technique_id in enumerate(group_techniques, 1):
                            # Find technique details
                            technique_info = None
                            for tech in data.get('techniques', []):
                                if tech.get('id') == technique_id:
                                    technique_info = tech
                                    break

                            if technique_info:
                                result_text += "{i}. {technique_id}: {technique_info.get('name', 'Unknown')}\n"
                                desc = technique_info.get('description', 'No description available')
                                if len(desc) > 150:
                                    desc = desc[:150] + "..."
                                result_text += "   Description: {desc}\n\n"
                            else:
                                result_text += "{i}. {technique_id}: (Name not found)\n\n"

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": result_text}]
                    }
                }

            elif tool_name == 'get_technique_mitigations':
                technique_id = tool_args.get('technique_id', '').upper().strip()

                # Find the technique
                technique = None
                for tech in data.get('techniques', []):
                    if tech.get('id', '').upper() == technique_id:
                        technique = tech
                        break

                if not technique:
                    result_text = "Technique '{technique_id}' not found. Please verify the technique ID is correct."
                else:
                    technique_mitigations = technique.get('mitigations', [])
                    if not technique_mitigations:
                        result_text = "No mitigations found for technique '{technique_id}' ({technique.get('name', 'Unknown')})."
                    else:
                        result_text = "TECHNIQUE MITIGATIONS\n"
                        result_text += "====================\n\n"
                        result_text += "Technique ID: {technique.get('id', 'N/A')}\n"
                        result_text += "Technique Name: {technique.get('name', 'N/A')}\n\n"

                        result_text += "Mitigations ({len(technique_mitigations)}):\n"
                        result_text += "{'-' * 40}\n\n"

                        for i, mitigation_id in enumerate(technique_mitigations, 1):
                            # Find mitigation details
                            mitigation_info = None
                            for mitigation in data.get('mitigations', []):
                                if mitigation.get('id') == mitigation_id:
                                    mitigation_info = mitigation
                                    break

                            if mitigation_info:
                                result_text += "{i}. {mitigation_id}: {mitigation_info.get('name', 'Unknown')}\n"
                                desc = mitigation_info.get('description', 'No description available')
                                if len(desc) > 300:
                                    desc = desc[:300] + "..."
                                result_text += "   Description: {desc}\n\n"
                            else:
                                result_text += "{i}. {mitigation_id}: (Name not found)\n\n"

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": result_text}]
                    }
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }

        except Exception:
            logger.error("Error calling tool {tool_name}: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution error: {str(e)}"
                }
            }

    def send_json_response(self, data):
        """Send a JSON response with CORS headers."""
        response_json = json.dumps(data, indent=2)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')
        self.end_headers()

        self.wfile.write(response_json.encode('utf-8'))

    def send_error_response(self, status_code, message):
        """Send an error response with CORS headers."""
        error_response = {
            "jsonrpc": "2.0",
            "id": "error",
            "error": {
                "code": status_code,
                "message": message
            }
        }

        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info("{self.address_string()} - {format % args}")


def create_handler_class(mcp_app):
    """Create a handler class with the MCP app injected."""
    class Handler(MCPHTTPHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, mcp_app=mcp_app, **kwargs)
    return Handler


def main():
    """Start the HTTP proxy server."""
    logger.info("Starting HTTP Proxy for MCP Server...")

    try:
        # Initialize data loader and load MITRE ATT&CK data
        logger.info("Loading MITRE ATT&CK data...")
        data_loader = DataLoader()        logger.info("MITRE ATT&CK data loaded successfully")

        # Create MCP server app (but don't run it)
        mcp_app = create_mcp_server(data_loader)
        logger.info("MCP server app created")

        # Create HTTP server
        handler_class = create_handler_class(mcp_app)
        server = HTTPServer(('127.0.0.1', 8000), handler_class)

        logger.info("HTTP Proxy server starting on http://127.0.0.1:8000")
        logger.info("You can now use the web explorer to interact with the MCP server")

        server.serve_forever()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception:
        logger.error("Failed to start HTTP proxy server: {e}")
        raise


if __name__ == '__main__':
    main()
