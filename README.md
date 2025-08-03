# MITRE ATT&CK MCP Server

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

- Python 3.8 or higher
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

The web interface provides an intuitive way to interact with all MCP tools without programming knowledge:

### Basic Tools Section
- Simple forms for fundamental MITRE ATT&CK queries
- Real-time search and technique lookup
- Group analysis and mitigation mapping

### Advanced Tools Section
- **🧠 Advanced Threat Modeling** with complex multi-parameter forms
- Attack path visualization and analysis
- Coverage gap assessment with quantitative results
- Relationship discovery with attribution chains

### Features
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-Time Results**: Immediate analysis results with formatted output
- **No Programming Required**: Full functionality accessible through web forms
- **Cross-Browser Compatible**: Works with modern web browsers

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