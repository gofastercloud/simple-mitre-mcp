# MITRE ATT&CK MCP Server

[![CI/CD Pipeline](https://github.com/gofastercloud/simple-mitre-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/gofastercloud/simple-mitre-mcp/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-202%20passing-brightgreen.svg)](https://github.com/gofastercloud/simple-mitre-mcp/actions)
[![MCP Tools](https://img.shields.io/badge/MCP%20Tools-8-blue.svg)](https://github.com/gofastercloud/simple-mitre-mcp)

A comprehensive Model Context Protocol (MCP) server that provides structured access to the MITRE ATT&CK framework for Large Language Models and interactive web-based analysis. This server enables security analysts, threat intelligence researchers, and cybersecurity professionals to perform both basic queries and advanced threat modeling through multiple access methods.

## 🚀 Features

### Basic Analysis Tools
- **Global Search**: Query across all MITRE ATT&CK entities (tactics, techniques, groups, mitigations)
- **Technique Analysis**: Get detailed information about specific techniques with tactics, platforms, and mitigations
- **Tactics Enumeration**: List all MITRE ATT&CK tactics with descriptions
- **Threat Group Profiling**: Analyze techniques used by specific threat groups
- **Mitigation Mapping**: Find mitigations for specific techniques

### Advanced Threat Modeling Tools
- **🎯 Attack Path Construction**: Build multi-stage attack paths through the MITRE ATT&CK kill chain
- **📊 Coverage Gap Analysis**: Analyze defensive coverage gaps against specific threat groups
- **🔗 Relationship Discovery**: Explore complex STIX relationships, attribution chains, and technique hierarchies

### Multiple Access Methods
- **🤖 MCP Protocol**: Direct integration with Large Language Models and AI assistants
- **🌐 Web Interface**: Interactive browser-based interface for non-technical users
- **🔌 HTTP/JSON API**: RESTful access for custom integrations and applications

## 🏃 Quick Start

### Prerequisites

- Python 3.12 or higher
- UV package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/gofastercloud/simple-mitre-mcp.git
cd simple-mitre-mcp
```

2. Install dependencies:
```bash
uv sync
```

### Usage Options

#### Option 1: Web Interface (Recommended for Interactive Use)
```bash
# Start the web interface (opens browser automatically)
uv run start_explorer.py
```
Access the interactive web interface at `http://localhost:8000`

#### Option 2: MCP Server (For AI Assistant Integration)
```bash
# Start the MCP server
uv run main.py
```
The MCP server will start on `stdio` transport for AI assistant integration.

#### Option 3: HTTP API Server
```bash
# Start the HTTP proxy server
uv run http_proxy.py
```
Access the HTTP API at `http://localhost:8000`

## 🛠️ MCP Tools

### Basic Analysis Tools (5 Core Tools)

1. **`search_attack`** - Global search across all ATT&CK entities
   - Parameters: `query` (required)
   - Returns: Mixed results with entity type indicators

2. **`get_technique`** - Get detailed technique information
   - Parameters: `technique_id` (required)
   - Returns: Full technique details including tactics, platforms, mitigations

3. **`list_tactics`** - List all MITRE ATT&CK tactics
   - Parameters: None
   - Returns: Complete list of tactics with IDs, names, and descriptions

4. **`get_group_techniques`** - Get techniques used by threat groups
   - Parameters: `group_id` (required)
   - Returns: List of techniques with basic information

5. **`get_technique_mitigations`** - Get mitigations for techniques
   - Parameters: `technique_id` (required)
   - Returns: List of applicable mitigations

### Advanced Threat Modeling Tools (3 Sophisticated Tools)

6. **`build_attack_path`** - Construct multi-stage attack paths
   - Parameters: `start_tactic` (required), `end_tactic` (required), `group_id` (optional), `platform` (optional)
   - Returns: Structured attack path with technique progression and analysis

7. **`analyze_coverage_gaps`** - Analyze defensive coverage gaps
   - Parameters: `threat_groups` (required array), `technique_list` (optional array), `exclude_mitigations` (optional array)
   - Returns: Coverage gap analysis with percentages and recommendations

8. **`detect_technique_relationships`** - Discover complex relationships
   - Parameters: `technique_id` (required), `relationship_types` (optional array), `depth` (optional, default: 2)
   - Returns: Complex relationship analysis with hierarchies and attribution chains

## ⚙️ Configuration

### Environment Variables

```bash
# MCP Server Configuration
MCP_SERVER_HOST=localhost    # Default: localhost
MCP_SERVER_PORT=3000        # Default: 3000

# HTTP Proxy Configuration  
MCP_HTTP_HOST=localhost     # Default: localhost
MCP_HTTP_PORT=8000         # Default: 8000

# Data Source Configuration
MITRE_ATTACK_URL=https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json
```

### Configuration Files

The server uses YAML configuration files in the `config/` directory:

- `data_sources.yaml` - Define threat intelligence data sources
- `entity_schemas.yaml` - Configure entity type schemas
- `tools.yaml` - Define MCP tool configurations

### Local Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your preferred settings
# Start with custom configuration
MCP_HTTP_PORT=3000 uv run start_explorer.py
```

## 🌐 Web Interface

The web interface provides a comprehensive interactive tool for testing and exploring all MITRE ATT&CK MCP server functionality through an HTTP proxy interface. Perfect for both development and production use.

### 🚀 Quick Start

**Automatic Startup (Recommended):**
```bash
uv run start_explorer.py
```
This automatically:
- Checks and syncs dependencies
- Starts the HTTP proxy server
- Loads MITRE ATT&CK data with relationship analysis
- Opens the web explorer in your browser

**Manual Setup:**
```bash
# Install dependencies
uv sync

# Start HTTP proxy server
uv run http_proxy.py

# Open web_explorer.html in your browser
```

### 🛠️ Available Tools

#### 🔍 Basic Analysis Tools (5 Core Tools)
- **Search ATT&CK Framework**: Global search across all entities
- **List All Tactics**: Get all MITRE ATT&CK tactics with descriptions
- **Get Technique Details**: Detailed technique information with platforms and mitigations
- **Get Group Techniques**: Techniques used by specific threat groups
- **Get Technique Mitigations**: Mitigations for specific techniques

#### 🧠 Advanced Threat Modeling Tools (3 Sophisticated Tools)
- **🎯 Build Attack Path**: Construct multi-stage attack paths through the kill chain
  - Start/end tactic specification
  - Threat group filtering
  - Platform-specific analysis
- **📊 Analyze Coverage Gaps**: Analyze defensive coverage gaps against threat groups
  - Multiple threat group analysis
  - Coverage percentage calculations
  - Prioritized recommendations
- **🔗 Detect Technique Relationships**: Explore complex STIX relationships
  - Multi-depth relationship traversal
  - Attribution chain analysis
  - Subtechnique hierarchy exploration

### 🏗️ Architecture

```
Web Browser → HTTP Proxy Server → MCP Tools (8 Tools) → MITRE ATT&CK Data
```

**Components:**
- **Web Explorer** (`web_explorer.html`): Frontend interface with basic and advanced tool sections
- **HTTP Proxy** (`http_proxy.py`): Translates HTTP requests to MCP tool calls
- **MCP Server** (`main.py`): FastMCP protocol server with comprehensive data processing

### 📝 Example Queries

**Basic Tool Examples:**
- Search: `process injection`, `APT29`, `T1055`, `powershell`
- Technique IDs: `T1055` (Process Injection), `T1059` (Command and Scripting)
- Group IDs: `G0016` (APT29), `G0007` (APT1), `G0050` (APT32)

**Advanced Tool Examples:**
- **Attack Path**: Start `TA0001` → End `TA0040`, Group `G0016`, Platform `Windows`
- **Coverage Gaps**: Groups `G0016,G0032,G0007`, Exclude `M1013,M1026`
- **Relationships**: Technique `T1055`, Types `uses,detects,mitigates`, Depth `2`

### 🔧 Troubleshooting

**Connection Issues:**
```bash
# Check if HTTP proxy is running
uv run http_proxy.py

# Verify dependencies
uv sync

# Test direct connection
curl -X POST http://127.0.0.1:8000/tools -H "Content-Type: application/json"
```

**Common Errors:**
- **"Connection Error"**: Ensure HTTP proxy is running and port 8000 is available
- **"Tool execution failed"**: Verify input format (e.g., technique IDs like "T1055")
- **"No results found"**: Try broader search terms or check spelling
- **"Address already in use"**: Kill existing processes or change port in `.env`

### 🎯 Features
- **Interactive Tool Testing**: Click buttons to execute all 8 MCP tools
- **Real-time Connection Status**: Visual server connectivity indicator
- **Formatted Output**: Clean, readable results with structured formatting
- **Error Handling**: Clear error messages and troubleshooting guidance
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **No Programming Required**: Full functionality through web forms

## 🧪 Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_mcp_server.py
```

### Code Quality

```bash
# Format code
uv run black .

# Lint code
uv run flake8 .

# Type checking
uv run mypy src/
```

### Test Coverage

The project maintains comprehensive test coverage with 167+ automated tests covering:
- All 8 MCP tools with various scenarios
- Data loading and STIX parsing
- Configuration management
- Web interface integration
- Error handling and edge cases

## 🏗️ Architecture

### Core Components

- **FastMCP Server**: Official MCP protocol implementation
- **HTTP Proxy Server**: Web interface and API access layer
- **STIX Data Parser**: Official STIX 2.x library for secure data parsing
- **Configuration System**: YAML-based configuration with environment overrides
- **Web Explorer**: Interactive HTML interface with JavaScript

### Data Processing

1. **Download**: Fetch MITRE ATT&CK STIX data from official repository
2. **Parse**: Use official `stix2` library for secure parsing
3. **Extract**: Process attack-pattern, course-of-action, intrusion-set, and relationship objects
4. **Analyze**: Build relationship graphs for advanced analysis
5. **Cache**: Store processed data in memory for fast access

## 🔧 Extensibility

### Adding New Data Sources
1. Define data source in `config/data_sources.yaml`
2. Create parser in `src/parsers/` if needed
3. Update entity schemas in `config/entity_schemas.yaml`

### Adding New MCP Tools
1. Define tool in `config/tools.yaml`
2. Implement tool logic in `src/mcp_server.py`
3. Add tests in `tests/test_<tool_name>.py`
4. Update web interface if needed

### Framework Support
The architecture supports any structured security framework through configuration:
- MITRE ATT&CK (implemented)
- NIST Cybersecurity Framework (configurable)
- Custom threat intelligence frameworks (extensible)

## 📚 Documentation

- **Requirements**: See `.kiro/specs/mitre-attack-mcp-server/requirements.md`
- **Design**: See `.kiro/specs/mitre-attack-mcp-server/design.md`
- **API Reference**: Tool parameters and responses documented in code
- **Configuration**: All options documented in config files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass: `uv run pytest`
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive tests for new features
- Update documentation for API changes
- Use type hints for function parameters
- Follow the existing code organization patterns

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **MITRE Corporation** for the ATT&CK framework and STIX data format
- **Model Context Protocol** team for the official MCP library
- **STIX Project** for the official STIX 2.x parsing library
- **UV Project** for modern Python package management

---

**🚀 Ready to explore advanced threat modeling with MITRE ATT&CK? Start with the web interface:**

```bash
uv run start_explorer.py
```

### YAML Configuration Files

The server uses YAML configuration files in the `config/` directory:

- `data_sources.yaml` - Define threat intelligence data sources
- `entity_schemas.yaml` - Configure entity type schemas
- `tools.yaml` - Define MCP tool configurations

### Environment Variables

The server supports configuration via environment variables:

```bash
# HTTP Proxy Server Configuration
MCP_HTTP_HOST=localhost    # Default: localhost
MCP_HTTP_PORT=8000        # Default: 8000

# Copy .env.example to .env for local configuration
cp .env.example .env
```

### Web Interface

The web interface is available at `http://localhost:8000` by default. You can customize the host and port using environment variables:

```bash
# Start with custom port
MCP_HTTP_PORT=3000 python start_explorer.py

# Start with custom host and port
MCP_HTTP_HOST=0.0.0.0 MCP_HTTP_PORT=8080 python start_explorer.py
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
uv run flake8 .
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.