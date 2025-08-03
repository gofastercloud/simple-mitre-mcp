# 🛡️ MITRE ATT&CK MCP Web Explorer

A web-based interactive tool for testing and exploring your MITRE ATT&CK MCP server functionality through an HTTP proxy interface.

## Features

- **Interactive Tool Testing**: Click buttons to execute MCP tools with real-time results
- **Natural Language Interface**: Test how an LLM would interact with your MCP server
- **Real-time Connection Status**: Visual indicator showing server connectivity
- **Formatted Output**: Clean, readable display of tool results
- **Error Handling**: Clear error messages and troubleshooting guidance
- **HTTP Proxy Architecture**: Seamless bridge between web browser and MCP protocol

## Available Tools

### 🔍 Search Tools
- **Search ATT&CK Framework**: Search across all entities (tactics, techniques, groups, mitigations)

### 📋 List Tools  
- **List All Tactics**: Get all MITRE ATT&CK tactics with descriptions

### 🎯 Detail Tools
- **Get Technique Details**: Detailed information about specific techniques
- **Get Group Techniques**: Techniques used by specific threat groups
- **Get Technique Mitigations**: Mitigations for specific techniques

## Architecture Overview

The web explorer uses a **two-tier architecture** to bridge the gap between web browsers and the MCP protocol:

```
Web Browser → HTTP Proxy Server → MCP Tools → MITRE ATT&CK Data
```

### Components

1. **Web Explorer (`web_explorer.html`)**: Frontend interface that makes standard HTTP requests
2. **HTTP Proxy (`http_proxy.py`)**: Translates HTTP requests to MCP tool calls
3. **MCP Server (`main.py`)**: Original MCP protocol server (optional for direct MCP clients)
4. **Data Layer**: MITRE ATT&CK data loaded from official sources

### Why the HTTP Proxy?

The MCP protocol uses specialized transports (like streamable-http with Server-Sent Events) that aren't directly compatible with standard web browser requests. The HTTP proxy:

- **Translates Protocols**: Converts HTTP JSON-RPC to MCP tool calls
- **Handles Sessions**: Manages MCP session complexity behind the scenes  
- **Provides CORS**: Enables cross-origin requests from the browser
- **Simplifies Integration**: Offers a standard HTTP API for web applications

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
3. Load MITRE ATT&CK data into memory
4. Automatically open the web explorer in your browser
5. Handle everything for you

### Option 2: Manual Setup
1. **Ensure dependencies are installed**:
   ```bash
   uv sync  # or pip install -r requirements if not using uv
   ```

2. **Start the HTTP Proxy Server**:
   ```bash
   uv run http_proxy.py  # or python http_proxy.py
   ```
   
3. **Open the Web Explorer**:
   - Open `web_explorer.html` in your web browser
   - Or double-click the file to open it

### Option 3: Direct MCP Server (Advanced)
For direct MCP protocol clients, you can still run:
```bash
uv run main.py  # Starts MCP server with streamable-http transport
```

## Usage

1. **Check Connection**: The top of the interface shows connection status
   - 🟢 Green = Connected to HTTP proxy server
   - 🔴 Red = Disconnected (server not running)

2. **Execute Tools**:
   - **Simple Tools**: Click buttons like "List All Tactics" to execute immediately
   - **Tools with Input**: Click buttons like "Search ATT&CK Framework" to show input form
   - Enter required parameters and click "Execute Tool"

3. **View Results**: Tool outputs appear in the right panel with:
   - Success indicators for successful executions
   - Error messages with troubleshooting guidance
   - Formatted, readable output

## Example Queries

### Search Examples
- `process injection` - Find techniques related to process injection
- `APT29` - Search for information about the APT29 group
- `T1055` - Search for a specific technique ID
- `powershell` - Find all PowerShell-related techniques and mitigations

### Technique IDs
- `T1055` - Process Injection
- `T1059` - Command and Scripting Interpreter
- `T1003` - OS Credential Dumping
- `T1059.001` - PowerShell

### Group IDs
- `G0016` - APT29 (Cozy Bear)
- `G0007` - APT1
- `G0050` - APT32

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

3. **Verify server port**: The HTTP proxy should start on `http://127.0.0.1:8000`

4. **Check browser console**: Open browser dev tools (F12) for detailed error messages

5. **Test direct connection**:
   ```bash
   curl -X POST http://127.0.0.1:8000 -H "Content-Type: application/json" \
        -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
   ```

### Common Errors

**"Connection Error"**: 
- Make sure `uv run http_proxy.py` (or `python http_proxy.py`) is running
- Check that no other service is using port 8000
- Verify dependencies are installed with `uv sync`
- Wait 5-10 seconds for MITRE data to load on first startup

**"Tool execution failed"**:
- Verify the input format (e.g., technique IDs should be like "T1055")
- Check the HTTP proxy logs for detailed error information
- Ensure MITRE ATT&CK data loaded successfully

**"No results found"**:
- Try different search terms or check spelling
- Verify the data has been loaded successfully
- Use broader search terms (e.g., "injection" instead of "process injection")

**"Address already in use"**:
- Another process is using port 8000
- Kill existing processes: `lsof -ti:8000 | xargs kill -9`
- Or change the port in `http_proxy.py`

## Technical Details

### Architecture
- **Frontend**: Pure HTML/CSS/JavaScript (no frameworks required)
- **HTTP Proxy**: Python HTTP server with asyncio for MCP tool calls
- **Backend**: FastMCP server with MITRE ATT&CK data processing
- **Protocol**: HTTP JSON-RPC 2.0 (frontend) → MCP protocol (backend)
- **Data Source**: Official MITRE ATT&CK STIX JSON from GitHub

### API Format
The web explorer communicates with the HTTP proxy using JSON-RPC 2.0:

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

Response format:
```json
{
  "jsonrpc": "2.0",
  "id": 123,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Search results for 'process injection'..."
      }
    ]
  }
}
```

### HTTP Proxy Features
- **CORS Support**: Enables browser requests from file:// URLs
- **Error Handling**: Graceful error responses with debugging information
- **Session Management**: Handles MCP protocol complexity transparently
- **Data Caching**: Keeps MITRE ATT&CK data in memory for fast responses
- **Tool Translation**: Maps HTTP requests to appropriate MCP tool functions

### Browser Compatibility
- Modern browsers with ES6+ support
- Chrome, Firefox, Safari, Edge (recent versions)
- No additional plugins or extensions required
- Works with file:// URLs (no web server required)

## Development

### Customization
You can modify the components:

**Web Explorer (`web_explorer.html`)**:
- Add new tool buttons
- Change the styling/theme
- Add additional functionality
- Integrate with other systems

**HTTP Proxy (`http_proxy.py`)**:
- Add new endpoints
- Modify response formats
- Add authentication
- Change port or CORS settings

### Adding New Tools
When you add new MCP tools to your server:
1. Add the tool function to `src/mcp_server.py`
2. Add corresponding logic in `http_proxy.py`
3. Add buttons and handlers in `web_explorer.html`
4. Test the new functionality

### Performance Considerations
- **Data Loading**: MITRE ATT&CK data (~30MB) loads once at startup
- **Memory Usage**: All data kept in memory for fast searches
- **Response Time**: Typical tool calls respond in <100ms after data load
- **Concurrent Requests**: HTTP proxy handles multiple simultaneous requests

## Files

- `web_explorer.html` - Main web interface
- `http_proxy.py` - HTTP proxy server that bridges web browser to MCP
- `start_explorer.py` - Automatic startup script (uses HTTP proxy)
- `main.py` - Original MCP server (for direct MCP clients)
- `WEB_EXPLORER_README.md` - This documentation

## Support

If you encounter issues:
1. Check the browser console for JavaScript errors (F12 → Console)
2. Check the HTTP proxy logs for backend errors
3. Verify your HTTP proxy server is properly configured and running
4. Ensure all dependencies are installed (`uv sync`)
5. Test the HTTP proxy directly with curl commands
6. Check that MITRE ATT&CK data loaded successfully (look for "entities loaded" in logs)

## Advanced Usage

### Direct MCP Integration
For applications that support MCP protocol directly:
```bash
uv run main.py  # Starts MCP server on streamable-http transport
```

### Custom HTTP Endpoints
The HTTP proxy can be extended to support additional endpoints or integrate with other systems while maintaining the MCP tool functionality.

### Data Updates
The system automatically downloads the latest MITRE ATT&CK data from the official GitHub repository on each startup. No manual data updates required.

The web explorer is designed to be a development and testing tool - perfect for understanding how LLMs would interact with your MCP server through a user-friendly web interface!