# API Reference

This document provides comprehensive API documentation for the MITRE ATT&CK MCP Server.

## Overview

The MCP server provides three different API interfaces:
1. **MCP Protocol** - For AI assistant integration
2. **HTTP REST API** - For programmatic access  
3. **Web Interface API** - For browser-based interaction

## MCP Protocol API

The Model Context Protocol (MCP) API is designed for integration with AI assistants like Claude Desktop.

### Connection
```bash
# STDIO transport (recommended for AI assistants)
uv run src/main_stdio.py

# JSON-RPC over STDIO
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | uv run src/main_stdio.py
```

### Available Methods

#### `tools/list`
List all available MCP tools.

**Request:**
```json
{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
```

**Response:**
```json
{
  "jsonrpc": "2.0", 
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "search_attack",
        "description": "Search across all MITRE ATT&CK entities",
        "inputSchema": {
          "type": "object",
          "properties": {
            "query": {"type": "string", "description": "Search query"}
          },
          "required": ["query"]
        }
      }
      // ... other tools
    ]
  }
}
```

#### `tools/call`
Execute a specific MCP tool.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2, 
  "method": "tools/call",
  "params": {
    "name": "search_attack",
    "arguments": {"query": "process injection"}
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "# MITRE ATT&CK Search Results for 'process injection'\n\n## Techniques Found (3 results):\n\n### T1055 - Process Injection\n**Description:** Adversaries may inject code into processes..."
      }
    ]
  }
}
```

## HTTP REST API

The HTTP API provides RESTful endpoints for programmatic access.

### Base URL
```
http://localhost:8000
```

### Authentication
No authentication required for local deployments. For production, implement reverse proxy authentication.

### Content Type
All POST requests should use `Content-Type: application/json`.

### Common Response Format

**Success Response:**
```json
{
  "result": "...",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Error Response:**
```json
{
  "error": "Error message",
  "status": 400,
  "timestamp": "2024-01-01T00:00:00Z",
  "path": "/api/endpoint",
  "method": "POST"
}
```

### Endpoints

#### System Information

**GET /system_info**
Get comprehensive system information and statistics.

```bash
curl http://localhost:8000/system_info
```

**Response:**
```json
{
  "server_info": {
    "version": "1.0.0",
    "mcp_protocol_version": "1.0",
    "startup_time": "2024-01-01T00:00:00Z",
    "data_source": "MITRE ATT&CK Enterprise"
  },
  "data_statistics": {
    "techniques_count": 823,
    "tactics_count": 14, 
    "groups_count": 181,
    "mitigations_count": 268,
    "relationships_count": 15000,
    "data_loaded": true,
    "last_updated": "2024-01-01T00:00:00Z"
  },
  "capabilities": {
    "basic_tools": 5,
    "advanced_tools": 3,
    "total_tools": 8,
    "web_interface": true,
    "api_access": true
  }
}
```

#### Tools Management

**GET /tools**
List all available MCP tools with their schemas.

```bash
curl http://localhost:8000/tools
```

**POST /call_tool**
Execute a specific tool.

```bash
curl http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_attack",
    "parameters": {"query": "persistence"}
  }'
```

### Data Population APIs

These endpoints provide formatted data for web interface components.

#### **GET /api/groups**
Get formatted threat group data for dropdowns.

```bash
curl http://localhost:8000/api/groups
```

**Response:**
```json
{
  "groups": [
    {
      "id": "G0016",
      "name": "APT29",
      "display_name": "APT29 (Cozy Bear, The Dukes)",
      "aliases": ["Cozy Bear", "The Dukes"]
    }
  ]
}
```

#### **GET /api/tactics**
Get formatted tactic data for dropdowns.

```bash
curl http://localhost:8000/api/tactics
```

**Response:**
```json
{
  "tactics": [
    {
      "id": "TA0001",
      "name": "Initial Access", 
      "display_name": "Initial Access (TA0001)"
    }
  ]
}
```

#### **GET /api/techniques**
Search techniques for autocomplete functionality.

```bash
curl "http://localhost:8000/api/techniques?q=process"
```

**Response:**
```json
{
  "techniques": [
    {
      "id": "T1055",
      "name": "Process Injection",
      "display_name": "Process Injection (T1055)",
      "match_reason": "Name"
    }
  ]
}
```

## Tool-Specific API

Each MCP tool has specific parameters and return formats.

### search_attack
Search across all MITRE ATT&CK entities.

**Parameters:**
- `query` (string, required): Search term

**Example:**
```bash
curl http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "search_attack", "parameters": {"query": "lateral movement"}}'
```

### get_technique
Get detailed information about a specific technique.

**Parameters:**
- `technique_id` (string, required): MITRE technique ID (e.g., "T1055")

**Example:**
```bash
curl http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "get_technique", "parameters": {"technique_id": "T1055"}}'
```

### list_tactics
List all MITRE ATT&CK tactics.

**Parameters:** None

**Example:**
```bash
curl http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "list_tactics", "parameters": {}}'
```

### get_group_techniques
Get techniques used by a specific threat group.

**Parameters:**
- `group_id` (string, required): MITRE group ID (e.g., "G0016")

**Example:**
```bash
curl http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "get_group_techniques", "parameters": {"group_id": "G0016"}}'
```

### get_technique_mitigations
Get mitigations for a specific technique.

**Parameters:**
- `technique_id` (string, required): MITRE technique ID (e.g., "T1055")

**Example:**
```bash
curl http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "get_technique_mitigations", "parameters": {"technique_id": "T1055"}}'
```

### build_attack_path
Build complete attack paths across the MITRE kill chain.

**Parameters:**
- `start_tactic` (string): Starting tactic ID (default: "TA0001")
- `end_tactic` (string): Target tactic ID (default: "TA0040") 
- `group_id` (string, optional): Filter by threat group
- `platform` (string, optional): Filter by platform

**Example:**
```bash
curl http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "build_attack_path",
    "parameters": {
      "start_tactic": "TA0001",
      "end_tactic": "TA0040",
      "group_id": "G0016"
    }
  }'
```

### analyze_coverage_gaps
Analyze defensive coverage gaps against threat groups.

**Parameters:**
- `threat_groups` (array, required): List of group IDs
- `technique_list` (array, optional): Specific techniques to analyze
- `exclude_mitigations` (array, optional): Implemented mitigations to exclude

**Example:**
```bash
curl http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "analyze_coverage_gaps",
    "parameters": {
      "threat_groups": ["G0016", "G0032"]
    }
  }'
```

### detect_technique_relationships
Discover complex relationships between techniques.

**Parameters:**
- `technique_id` (string, required): Primary technique to analyze
- `relationship_types` (array, optional): Types to include
- `depth` (integer, optional): Traversal depth (1-3, default: 2)

**Example:**
```bash
curl http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "detect_technique_relationships", 
    "parameters": {
      "technique_id": "T1055",
      "depth": 2
    }
  }'
```

## Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (invalid endpoint)
- `500` - Internal Server Error
- `503` - Service Unavailable (MCP server not ready)

### Error Response Format
```json
{
  "error": "Detailed error message",
  "status": 400,
  "timestamp": "2024-01-01T00:00:00Z",
  "path": "/call_tool",
  "method": "POST",
  "request_id": "12345"  // Only for 5xx errors
}
```

### Common Error Scenarios

#### Invalid Tool Name
```json
{
  "error": "Unknown tool: invalid_tool. Available tools: search_attack, get_technique, ...",
  "status": 400
}
```

#### Missing Required Parameters
```json
{
  "error": "Missing required parameter: technique_id",
  "status": 400
}
```

#### Data Not Loaded
```json
{
  "error": "MITRE ATT&CK data not loaded",
  "status": 500
}
```

## Rate Limiting

Currently no rate limiting is implemented. For production deployments, consider implementing rate limiting at the reverse proxy level.

## WebSocket API

WebSocket support is planned for future releases to enable real-time updates and streaming responses.

## SDK and Client Libraries

### Python SDK Example
```python
import requests

class MitreAttackClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def search_attack(self, query):
        response = requests.post(f"{self.base_url}/call_tool", json={
            "tool_name": "search_attack",
            "parameters": {"query": query}
        })
        return response.text
    
    def get_technique(self, technique_id):
        response = requests.post(f"{self.base_url}/call_tool", json={
            "tool_name": "get_technique", 
            "parameters": {"technique_id": technique_id}
        })
        return response.text

# Usage
client = MitreAttackClient()
results = client.search_attack("process injection")
technique = client.get_technique("T1055")
```

### JavaScript SDK Example
```javascript
class MitreAttackClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async callTool(toolName, parameters) {
    const response = await fetch(`${this.baseUrl}/call_tool`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({tool_name: toolName, parameters})
    });
    return await response.text();
  }

  async searchAttack(query) {
    return this.callTool('search_attack', {query});
  }

  async getTechnique(techniqueId) {
    return this.callTool('get_technique', {technique_id: techniqueId});
  }
}

// Usage
const client = new MitreAttackClient();
const results = await client.searchAttack('persistence');
```

## Testing APIs

### Health Check
```bash
curl -f http://localhost:8000/system_info
```

### Tool Validation
```bash
# Test all tools are available
curl http://localhost:8000/tools | jq '.tools | length'

# Test basic tool execution  
curl http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "list_tactics", "parameters": {}}'
```

### Load Testing
```bash
# Using Apache Bench
ab -n 100 -c 10 http://localhost:8000/system_info

# Using curl for tool testing
for i in {1..10}; do
  curl -s http://localhost:8000/call_tool \
    -H "Content-Type: application/json" \
    -d '{"tool_name": "search_attack", "parameters": {"query": "test'$i'"}}' &
done
```

## API Versioning

Currently the API does not include explicit versioning. Future versions will include version headers:
- `API-Version: 1.0` - Current version
- `Accept-Version: 1.0` - Client version preference

## OpenAPI Specification

An OpenAPI (Swagger) specification is planned for future releases to provide interactive API documentation and client generation capabilities.