# 🛡️ MITRE ATT&CK MCP Web Explorer

A comprehensive web-based interactive tool for testing and exploring your MITRE ATT&CK MCP server functionality through an HTTP proxy interface. The web explorer provides access to all 8 MCP tools including advanced threat modeling capabilities.

## Features

- **Interactive Tool Testing**: Click buttons to execute all 8 MCP tools with real-time results
- **Basic Analysis Tools**: Simple forms for fundamental MITRE ATT&CK queries
- **Advanced Threat Modeling**: Complex forms for sophisticated security analysis
- **Natural Language Interface**: Test how an LLM would interact with your MCP server
- **Real-time Connection Status**: Visual indicator showing server connectivity
- **Formatted Output**: Clean, readable display of tool results with structured formatting
- **Error Handling**: Clear error messages and troubleshooting guidance
- **HTTP Proxy Architecture**: Seamless bridge between web browser and MCP protocol
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Available Tools

### 🔍 Basic Analysis Tools (5 Core Tools)

#### Search and Discovery
- **Search ATT&CK Framework**: Global search across all entities (tactics, techniques, groups, mitigations)

#### Information Retrieval
- **List All Tactics**: Get all MITRE ATT&CK tactics with descriptions and IDs
- **Get Technique Details**: Detailed information about specific techniques including platforms, tactics, and mitigations
- **Get Group Techniques**: Techniques used by specific threat groups with TTP analysis
- **Get Technique Mitigations**: Mitigations for specific techniques with implementation guidance

### 🧠 Advanced Threat Modeling Tools (3 Sophisticated Tools)

#### Attack Path Analysis
- **🎯 Build Attack Path**: Construct multi-stage attack paths through the MITRE ATT&CK kill chain
  - Start and end tactic specification
  - Threat group filtering
  - Platform-specific analysis
  - Technique progression mapping

#### Defensive Analysis
- **📊 Analyze Coverage Gaps**: Analyze defensive coverage gaps against specific threat groups
  - Multiple threat group analysis
  - Coverage percentage calculations
  - Mitigation exclusion support
  - Prioritized gap recommendations

#### Relationship Discovery
- **🔗 Detect Technique Relationships**: Explore complex STIX relationships and attribution chains
  - Multi-depth relationship traversal
  - Attribution chain analysis
  - Subtechnique hierarchy exploration
  - Detection relationship mapping

## Architecture Overview

The web explorer uses a **comprehensive three-tier architecture** to bridge the gap between web browsers and the MCP protocol:

```
Web Browser → HTTP Proxy Server → MCP Tools (8 Tools) → MITRE ATT&CK Data
```

### Components

1. **Web Explorer (`web_explorer.html`)**: Frontend interface with basic and advanced tool sections
2. **HTTP Proxy (`http_proxy.py`)**: Translates HTTP requests to MCP tool calls for all 8 tools
3. **MCP Server (`main.py`)**: Original MCP protocol server with FastMCP implementation
4. **Data Layer**: Enhanced MITRE ATT&CK data with relationship analysis and caching

### Why the HTTP Proxy?

The MCP protocol uses specialized transports (like streamable-http with Server-Sent Events) that aren't directly compatible with standard web browser requests. The HTTP proxy:

- **Translates Protocols**: Converts HTTP JSON-RPC to MCP tool calls for all 8 tools
- **Handles Complex Parameters**: Supports array inputs and multi-parameter advanced tools
- **Manages Sessions**: Handles MCP session complexity behind the scenes  
- **Provides CORS**: Enables cross-origin requests from the browser
- **Simplifies Integration**: Offers a standard HTTP API for web applications
- **Supports Advanced Analysis**: Handles complex threat modeling workflows

## Quick Start

### Option 1: Automatic Startup (Recommended)
```bash
# Using uv (recommended)
uv run start_explorer.py

# Or using python directly
python start_explorer.py
```
This will:
1. Check and sync dependencies automatically
2. Start the HTTP proxy server in the background
3. Load MITRE ATT&CK data with relationship analysis into memory
4. Automatically open the web explorer in your browser
5. Handle everything for you

### Option 2: Manual Setup
1. **Ensure dependencies are installed**:
   ```bash
   uv sync  # or pip install -r requirements if not using uv
   ```

2. **Configure environment (optional)**:
   ```bash
   cp .env.example .env
   # Edit .env to customize ports if needed
   # MCP_HTTP_PORT=8000
   ```

3. **Start the HTTP Proxy Server**:
   ```bash
   uv run http_proxy.py  # or python http_proxy.py
   ```
   
4. **Open the Web Explorer**:
   - Open `web_explorer.html` in your web browser
   - Or double-click the file to open it

### Option 3: Direct MCP Server (Advanced)
For direct MCP protocol clients, you can still run:
```bash
uv run main.py  # Starts MCP server with streamable-http transport
```

## Usage

### Connection Status
1. **Check Connection**: The top of the interface shows connection status
   - 🟢 Green = Connected to HTTP proxy server
   - 🔴 Red = Disconnected (server not running)

### Basic Tools Section
2. **Execute Basic Tools**:
   - **Simple Tools**: Click buttons like "List All Tactics" to execute immediately
   - **Tools with Input**: Click buttons like "Search ATT&CK Framework" to show input form
   - Enter required parameters and click "Execute Tool"

### Advanced Tools Section
3. **Execute Advanced Tools**:
   - **🎯 Build Attack Path**: Complex form with start/end tactics, optional group and platform filtering
   - **📊 Analyze Coverage Gaps**: Multi-select threat groups, optional technique lists, mitigation exclusions
   - **🔗 Detect Technique Relationships**: Technique analysis with relationship types and depth configuration

4. **View Results**: Tool outputs appear in the right panel with:
   - Success indicators for successful executions
   - Error messages with troubleshooting guidance
   - Formatted, readable output with structured analysis results

## Example Queries

### Basic Tool Examples

#### Search Examples
- `process injection` - Find techniques related to process injection
- `APT29` - Search for information about the APT29 group
- `T1055` - Search for a specific technique ID
- `powershell` - Find all PowerShell-related techniques and mitigations

#### Technique IDs
- `T1055` - Process Injection
- `T1059` - Command and Scripting Interpreter
- `T1003` - OS Credential Dumping
- `T1059.001` - PowerShell

#### Group IDs
- `G0016` - APT29 (Cozy Bear)
- `G0007` - APT1
- `G0050` - APT32

### Advanced Tool Examples

#### Attack Path Construction
- **Start Tactic**: `TA0001` (Initial Access)
- **End Tactic**: `TA0040` (Impact)
- **Group Filter**: `G0016` (APT29)
- **Platform**: `Windows`

#### Coverage Gap Analysis
- **Threat Groups**: `G0016,G0032,G0007` (comma-separated)
- **Exclude Mitigations**: `M1013,M1026` (already implemented)

#### Relationship Discovery
- **Technique**: `T1055` (Process Injection)
- **Relationship Types**: `uses,detects,mitigates` (comma-separated)
- **Depth**: `2` (relationship traversal depth)

## Troubleshooting

### Connection Issues
If you see "Disconnected from MCP Server":

1. **Check if HTTP proxy is running**:
   ```bash
   # In another terminal (using uv)
   uv run http_proxy.py
   
   # Or using python directly
   python http_proxy.py
   ```

2. **Verify dependencies are installed**:
   ```bash
   uv sync  # Ensure all dependencies are available
   ```

3. **Check environment configuration**:
   ```bash
   # Verify .env file if using custom ports
   cat .env
   ```

4. **Verify server port**: The HTTP proxy should start on `http://127.0.0.1:8000` (default)

5. **Check browser console**: Open browser dev tools (F12) for detailed error messages

6. **Test direct connection**:
   ```bash
   curl -X POST http://127.0.0.1:8000/tools -H "Content-Type: application/json"
   ```

### Common Errors

**"Connection Error"**: 
- Make sure `uv run http_proxy.py` (or `python http_proxy.py`) is running
- Check that no other service is using port 8000 (or your configured port)
- Verify dependencies are installed with `uv sync`
- Wait 10-15 seconds for MITRE data to load on first startup

**"Tool execution failed"**:
- Verify the input format (e.g., technique IDs should be like "T1055")
- For advanced tools, check array parameter formatting (comma-separated values)
- Check the HTTP proxy logs for detailed error information
- Ensure MITRE ATT&CK data loaded successfully

**"No results found"**:
- Try different search terms or check spelling
- Verify the data has been loaded successfully
- Use broader search terms (e.g., "injection" instead of "process injection")
- For advanced tools, verify parameter combinations are valid

**"Address already in use"**:
- Another process is using the configured port
- Kill existing processes: `lsof -ti:8000 | xargs kill -9`
- Or change the port in `.env` file: `MCP_HTTP_PORT=3000`

**"Invalid parameter format"**:
- Advanced tools require specific parameter formats
- Array parameters should be comma-separated (e.g., "G0016,G0032")
- Depth parameters should be integers between 1-3
- Check tool-specific parameter requirements

## Technical Details

### Architecture
- **Frontend**: Pure HTML/CSS/JavaScript with advanced form handling (no frameworks required)
- **HTTP Proxy**: Python HTTP server with asyncio for all 8 MCP tool calls
- **Backend**: FastMCP server with comprehensive MITRE ATT&CK data processing
- **Protocol**: HTTP JSON-RPC 2.0 (frontend) → MCP protocol (backend)
- **Data Source**: Official MITRE ATT&CK STIX JSON with relationship analysis

### Enhanced API Format
The web explorer communicates with the HTTP proxy using JSON-RPC 2.0:

#### Basic Tool Example
```json
{
  "jsonrpc": "2.0",
  "id": 123,
  "method": "tools/call",
  "params": {
    "name": "search_attack",
    "arguments": {
      "query": "process injection"
    }
  }
}
```

#### Advanced Tool Example
```json
{
  "jsonrpc": "2.0",
  "id": 124,
  "method": "tools/call",
  "params": {
    "name": "analyze_coverage_gaps",
    "arguments": {
      "threat_groups": ["G0016", "G0032"],
      "exclude_mitigations": ["M1013", "M1026"]
    }
  }
}
```

Response format:
```json
{
  "jsonrpc": "2.0",
  "id": 123,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Analysis results with structured data..."
      }
    ]
  }
}
```

### HTTP Proxy Features
- **CORS Support**: Enables browser requests from file:// URLs
- **Advanced Parameter Handling**: Supports arrays, complex objects, and validation
- **Error Handling**: Graceful error responses with debugging information
- **Session Management**: Handles MCP protocol complexity transparently
- **Data Caching**: Keeps MITRE ATT&CK data with relationships in memory for fast responses
- **Tool Translation**: Maps HTTP requests to appropriate MCP tool functions for all 8 tools
- **Configuration Support**: Environment variable configuration for flexible deployment

### Browser Compatibility
- Modern browsers with ES6+ support
- Chrome, Firefox, Safari, Edge (recent versions)
- JavaScript array handling for advanced tool parameters
- No additional plugins or extensions required
- Works with file:// URLs (no web server required)

## Development

### Customization
You can modify the components:

**Web Explorer (`web_explorer.html`)**:
- Add new tool buttons and forms
- Modify advanced tool parameter handling
- Change the styling/theme
- Add additional functionality
- Integrate with other systems

**HTTP Proxy (`http_proxy.py`)**:
- Add new endpoints
- Modify response formats
- Add authentication
- Change port or CORS settings
- Extend tool parameter validation

### Adding New Tools
When you add new MCP tools to your server:
1. Add the tool function to `src/mcp_server.py` with @app.tool() decorator
2. Add corresponding logic in `http_proxy.py` tools list
3. Add buttons and handlers in `web_explorer.html`
4. Add comprehensive tests for the new tool
5. Test the new functionality through all access methods

### Performance Considerations
- **Data Loading**: MITRE ATT&CK data (~30MB) with relationships loads once at startup
- **Memory Usage**: All data with relationship graphs kept in memory for fast searches
- **Response Time**: Basic tools respond in <100ms, advanced tools in <500ms after data load
- **Concurrent Requests**: HTTP proxy handles multiple simultaneous requests
- **Advanced Analysis**: Complex threat modeling may take 1-2 seconds for deep analysis

## Files

- `web_explorer.html` - Main web interface with basic and advanced tool sections
- `http_proxy.py` - HTTP proxy server that bridges web browser to all 8 MCP tools
- `start_explorer.py` - Automatic startup script with environment configuration
- `main.py` - Original MCP server (for direct MCP clients)
- `src/mcp_server.py` - Core MCP server with all 8 tools implementation
- `.env.example` - Environment variable configuration template
- `WEB_EXPLORER_README.md` - This comprehensive documentation

## Support

If you encounter issues:
1. Check the browser console for JavaScript errors (F12 → Console)
2. Check the HTTP proxy logs for backend errors
3. Verify your HTTP proxy server is properly configured and running
4. Ensure all dependencies are installed (`uv sync`)
5. Test the HTTP proxy directly with curl commands
6. Check that MITRE ATT&CK data loaded successfully (look for "entities loaded" in logs)
7. For advanced tools, verify parameter formats and combinations
8. Test with basic tools first, then progress to advanced tools

## Advanced Usage

### Direct MCP Integration
For applications that support MCP protocol directly:
```bash
uv run main.py  # Starts MCP server on streamable-http transport
```

### Custom HTTP Endpoints
The HTTP proxy can be extended to support additional endpoints or integrate with other systems while maintaining all 8 MCP tool functionality.

### Environment Configuration
```bash
# Custom port configuration
MCP_HTTP_PORT=3000 uv run start_explorer.py

# Custom host configuration
MCP_HTTP_HOST=0.0.0.0 MCP_HTTP_PORT=8080 uv run start_explorer.py
```

### Data Updates
The system automatically downloads the latest MITRE ATT&CK data from the official GitHub repository on each startup. Relationship analysis is performed automatically. No manual data updates required.

### Advanced Tool Workflows
1. **Threat Assessment**: Use coverage gap analysis to identify defensive weaknesses
2. **Attack Simulation**: Build attack paths to understand adversary progression
3. **Attribution Analysis**: Use relationship discovery to map technique→group→campaign connections
4. **Platform Analysis**: Filter all tools by specific platforms (Windows, Linux, macOS)

The web explorer is designed to be both a development/testing tool and a production-ready interface for security analysts - perfect for understanding how LLMs would interact with your comprehensive MCP server through an intuitive web interface with advanced threat modeling capabilities!