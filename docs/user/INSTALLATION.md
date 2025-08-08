# Installation Guide

This guide will help you install and set up the MITRE ATT&CK MCP Server.

## System Requirements

- **Python**: 3.12 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 2GB RAM
- **Storage**: 1GB free disk space
- **Network**: Internet connection for downloading MITRE ATT&CK data

## Installation Methods

### Method 1: Using UV (Recommended)

UV is a fast Python package manager that handles virtual environments automatically.

#### 1. Install UV
```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: using pip
pip install uv
```

#### 2. Clone and Install
```bash
# Clone the repository
git clone https://github.com/gofastercloud/simple-mitre-mcp.git
cd simple-mitre-mcp

# Install dependencies (creates virtual environment automatically)
uv sync
```

#### 3. Verify Installation
```bash
# Run tests to verify everything works
uv run python -m pytest tests/ -x --tb=short

# Start the web interface
uv run start_explorer.py
```

### Method 2: Using Pip and Virtual Environment

#### 1. Set Up Virtual Environment
```bash
# Clone repository
git clone https://github.com/gofastercloud/simple-mitre-mcp.git
cd simple-mitre-mcp

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

#### 2. Install Dependencies
```bash
# Install the package and dependencies
pip install -e .
```

#### 3. Verify Installation
```bash
# Run tests
python -m pytest tests/ -x --tb=short

# Start the web interface
python start_explorer.py
```

## Quick Start

### 1. Start the Web Interface
```bash
# Using UV (recommended)
uv run start_explorer.py

# Using pip installation
python start_explorer.py
```

You should see output like:
```
INFO: Loading MITRE ATT&CK data...
INFO: Loaded 823 techniques, 181 groups, 268 mitigations
INFO: Starting HTTP proxy server on http://localhost:8000
```

### 2. Access the Web Interface
Open your browser and navigate to: http://localhost:8000

### 3. Try the MCP Tools
- **Search**: Try searching for "process injection"
- **Get Technique**: Enter technique ID like "T1055"
- **List Tactics**: View all MITRE ATT&CK tactics
- **Group Techniques**: Enter group ID like "G0016" (APT29)

## Usage Modes

The MCP server can run in three different modes:

### Web Interface Mode (Recommended for New Users)
```bash
uv run start_explorer.py
```
- Interactive web browser interface
- Easy-to-use forms for all tools
- Formatted results with deep links to MITRE
- Great for exploration and learning

### HTTP Proxy Mode (For Programmatic Access)
```bash
uv run src/http_proxy.py
```
- REST API endpoints
- JSON responses
- Suitable for integration with other tools
- Command-line friendly

### MCP Server Mode (For AI Assistants)
```bash
uv run src/main_stdio.py
```
- Model Context Protocol (MCP) interface
- Designed for AI assistant integration (Claude Desktop, etc.)
- STDIO transport for real-time communication

## Configuration

### Environment Variables
```bash
# HTTP server configuration
export MCP_HTTP_HOST=localhost  # Change to 0.0.0.0 for network access
export MCP_HTTP_PORT=8000       # Change port if needed

# Logging level
export LOG_LEVEL=INFO           # DEBUG for detailed logs
```

### Configuration Files
The server uses YAML configuration files in the `config/` directory:
- `data_sources.yaml` - Data source URLs
- `entity_schemas.yaml` - STIX entity schemas
- `tools.yaml` - Tool configurations

## AI Assistant Integration

### Claude Desktop
1. Add this to your Claude Desktop config:
```json
{
  "mcpServers": {
    "simple-mitre-mcp": {
      "command": "uv",
      "args": ["run", "src/main_stdio.py"],
      "cwd": "/path/to/simple-mitre-mcp"
    }
  }
}
```

2. Restart Claude Desktop
3. You'll now have access to MITRE ATT&CK tools in Claude!

### Other MCP Clients
See the [examples/](../../examples/) directory for configuration examples for different MCP clients.

## Verification

### Test All Components
```bash
# Run the validation script
./deployment/validate_web_explorer.sh

# Or run individual checks:
uv run python -c "from src.data_loader import DataLoader; dl = DataLoader(); print(f'Loaded {len(dl.load_data_source(\"mitre_attack\"))} entities')"
```

### Test Web Interface
1. Visit http://localhost:8000
2. Click on "System Dashboard" to see loaded data statistics
3. Try the "Search Attack" tool with query "persistence"
4. Verify results are displayed properly

### Test MCP Integration
```bash
# Test MCP server directly
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | uv run src/main_stdio.py
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Check Python version
python --version  # Should be 3.12+

# Reinstall dependencies
uv sync --reinstall
```

#### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Use a different port
export MCP_HTTP_PORT=8001
```

#### Data Loading Fails
```bash
# Check internet connection
curl -I https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json

# Clear cache and retry
rm -rf ~/.cache/simple-mitre-mcp/
```

#### Permission Denied
```bash
# Check file permissions
ls -la start_explorer.py

# Make executable if needed
chmod +x start_explorer.py
```

### Getting Help

1. **Documentation**: Check the [User Guide](USER_GUIDE.md) for detailed usage instructions
2. **Troubleshooting**: See [Troubleshooting Guide](../deployment/TROUBLESHOOTING.md) for technical issues
3. **GitHub Issues**: Report bugs or request features
4. **Examples**: Check [examples/](../../examples/) for configuration examples

## Next Steps

- Read the [User Guide](USER_GUIDE.md) for detailed usage instructions
- Explore [examples/](../../examples/) for integration examples
- Check out [Developer Guide](../developer/DEVELOPER_GUIDE.md) if you want to contribute
- See [Deployment Guide](../deployment/DEPLOYMENT.md) for production deployment