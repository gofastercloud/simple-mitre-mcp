# Project Structure

## Directory Organization

```
.
├── main.py                 # Main MCP server entry point
├── http_proxy.py          # HTTP proxy server for web interface access
├── start_explorer.py      # Web interface launcher script
├── web_explorer.html      # Interactive web interface for all MCP tools
├── pyproject.toml         # UV project configuration and dependencies
├── README.md              # Project documentation and setup instructions
├── .env.example           # Environment variable configuration template
├── config/                # Configuration files
│   ├── data_sources.yaml  # Data source definitions
│   ├── entity_schemas.yaml # Entity type schemas
│   └── tools.yaml         # MCP tool configurations
├── src/                   # Source code directory
│   ├── __init__.py
│   ├── mcp_server.py      # FastMCP server implementation with 8 MCP tools
│   ├── config_loader.py   # Configuration file loading
│   ├── data_loader.py     # Generic data loading and parsing with relationship analysis
│   └── parsers/           # Data format parsers
│       ├── __init__.py
│       ├── stix_parser.py # STIX format parser with relationship extraction
│       └── base_parser.py # Base parser interface
├── tests/                 # Unit tests (ALL tests must be in this directory)
│   ├── __init__.py
│   ├── test_mcp_server.py # Test MCP server functionality and all 8 tools
│   ├── test_data_loader.py # Test data loading functionality
│   ├── test_config_loader.py # Test configuration loading
│   ├── test_parsers.py    # Test data parsers
│   ├── test_build_attack_path.py # Test attack path construction tool
│   ├── test_analyze_coverage_gaps.py # Test coverage gap analysis tool
│   ├── test_detect_technique_relationships.py # Test relationship discovery tool
│   ├── test_web_interface_advanced.py # Test web interface integration
│   ├── test_end_to_end_integration.py # Test complete workflows
│   └── test_port_config.py # Test port configuration functionality
└── .kiro/                 # Kiro configuration
    ├── specs/             # Project specifications
    └── steering/          # AI assistant guidance
```

## Code Organization Principles

### Library-First Development
- **Use Official Libraries**: Always prefer official libraries for well-known protocols (MCP, STIX, etc.)
- **Battle-Tested Libraries**: Choose established libraries with security track records
- **Avoid Custom Parsers**: Use existing parsers for standard formats (STIX, JSON, YAML)
- **Security-Focused**: Prefer libraries designed for parsing untrusted external data

### Extensibility Principles
- **No Framework-Specific Logic**: Avoid hardcoding MITRE ATT&CK or any specific framework logic
- **Configuration-Driven**: All entity types, schemas, and data sources defined in config files
- **Generic Tool Design**: Tools should work with any configured entity type
- **Pluggable Architecture**: Support for different data formats through established parsing libraries

### MCP Tools Structure

#### Basic Analysis Tools (5 Core Tools)
- **search_attack**: Global search across all ATT&CK entities
- **get_technique**: Detailed technique information retrieval
- **list_tactics**: Complete tactics enumeration
- **get_group_techniques**: Threat group TTP analysis
- **get_technique_mitigations**: Mitigation mapping for techniques

#### Advanced Threat Modeling Tools (3 Sophisticated Tools)
- **build_attack_path**: Multi-stage attack path construction through kill chain
- **analyze_coverage_gaps**: Defensive coverage gap analysis against threat groups
- **detect_technique_relationships**: Complex STIX relationship discovery and attribution analysis

### Web Interface Architecture

#### HTTP Proxy Server (`http_proxy.py`)
- **Purpose**: Provides HTTP/JSON API bridge to MCP tools for web access
- **Configuration**: Environment variable `MCP_HTTP_PORT` for port configuration
- **Endpoints**: Tool listing, tool execution, and web interface serving
- **Error Handling**: Comprehensive error handling with informative responses

#### Web Explorer Interface (`web_explorer.html`)
- **Design**: Single-page application with sections for basic and advanced tools
- **Basic Tools Section**: Simple forms for fundamental queries
- **Advanced Tools Section**: Complex forms supporting array inputs and multi-parameter analysis
- **JavaScript Functions**: Dynamic form generation and result display
- **Responsive Design**: Cross-browser compatibility and mobile-friendly interface

#### Launcher Script (`start_explorer.py`)
- **Purpose**: Convenient startup script for web interface with automatic browser opening
- **Configuration**: Environment variable support for host/port settings
- **Features**: Server status monitoring and graceful shutdown handling

### Data Models and Processing

#### Enhanced Data Models (Python Dictionaries with Relationships)
- **Techniques**: Include relationship data for attribution and detection analysis
- **Attack Paths**: Structured multi-stage attack progression data
- **Coverage Gaps**: Quantitative analysis results with prioritization
- **Relationship Maps**: Complex STIX relationship traversal results

#### Advanced Data Processing
- **Relationship Extraction**: Parse STIX relationship objects for attribution chains
- **Attack Path Logic**: Implement kill chain progression algorithms
- **Coverage Calculation**: Quantitative gap analysis with percentage calculations
- **Caching Strategy**: In-memory relationship graphs for fast advanced tool execution

### File Naming Conventions
- Use snake_case for Python files and functions
- Use descriptive names that indicate purpose
- Keep module names short but clear
- Prefix private functions with underscore
- Test files follow `test_<module_name>.py` pattern

### Code Readability Standards
- Write self-documenting code with clear variable names
- Break complex operations into smaller, named functions
- **Use configuration constants instead of hardcoded values**
- **Avoid framework-specific terminology in generic code**
- Group related functionality logically within modules
- Maintain consistent indentation and spacing

### Configuration Management

#### Environment Variables
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

#### Configuration Files
- Store all framework-specific data in YAML configuration files
- Use descriptive configuration keys that explain their purpose
- Validate configuration files on startup with clear error messages
- Support environment variable overrides for deployment flexibility
- Document all configuration options in README and inline comments

### Testing Structure

#### Comprehensive Test Coverage (167+ Tests)
- **ALL tests must be placed in the `tests/` directory** - never create test files in the root directory or other locations
- Mirror source structure in tests directory (e.g., `src/data_loader.py` → `tests/test_data_loader.py`)
- One test file per source module with `test_` prefix
- Use descriptive test function names with `test_` prefix
- Include both positive and negative test cases
- Document test scenarios in docstrings
- Use pytest as the testing framework
- Include `__init__.py` in tests directory to make it a proper Python package

#### Advanced Tool Testing
- **Attack Path Testing**: Validate multi-stage attack path construction logic
- **Coverage Gap Testing**: Test quantitative analysis calculations and prioritization
- **Relationship Testing**: Verify complex STIX relationship traversal and attribution chains
- **Web Interface Testing**: Integration tests for HTTP proxy and web interface functionality
- **Configuration Testing**: Environment variable and deployment configuration validation

## Recommended Libraries

### Protocol and Format Libraries
- **stix2**: Official STIX 2.x library for parsing STIX data with relationship support
- **mcp**: Official Model Context Protocol SDK with FastMCP server implementation
- **pydantic**: Data validation and settings management
- **pyyaml**: YAML configuration file parsing
- **requests**: HTTP client for downloading data

### Development and Testing
- **pytest**: Testing framework with comprehensive fixture support
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Static type checking

## Key Files

### Core Server Files
- **main.py**: Entry point that starts the FastMCP server with all 8 tools
- **src/mcp_server.py**: Core MCP protocol handling with basic and advanced tools
- **src/data_loader.py**: Enhanced data loading with relationship analysis
- **src/parsers/stix_parser.py**: STIX parsing with relationship extraction

### Web Interface Files
- **http_proxy.py**: HTTP proxy server providing JSON API access to MCP tools
- **web_explorer.html**: Interactive web interface with basic and advanced tool sections
- **start_explorer.py**: Convenient launcher script with environment configuration

### Configuration Files
- **config/data_sources.yaml**: Data source definitions with relationship support
- **config/entity_schemas.yaml**: Entity type schemas including relationship types
- **config/tools.yaml**: All 8 MCP tool configurations
- **.env.example**: Environment variable configuration template

### Testing Files
- **tests/test_*.py**: Comprehensive test suite covering all functionality
- **tests/test_web_interface_advanced.py**: Web interface integration tests
- **tests/test_build_attack_path.py**: Attack path construction testing
- **tests/test_analyze_coverage_gaps.py**: Coverage gap analysis testing
- **tests/test_detect_technique_relationships.py**: Relationship discovery testing

## Extension Guidelines

### Adding New Data Sources
1. Define data source in `config/data_sources.yaml`
2. Create appropriate parser in `src/parsers/` if needed
3. Update entity schemas in `config/entity_schemas.yaml`
4. No code changes should be required for new frameworks

### Adding New MCP Tools
1. Define tool configuration in `config/tools.yaml`
2. Implement tool logic in `src/mcp_server.py` using @app.tool() decorator
3. Add comprehensive unit tests in `tests/test_<tool_name>.py`
4. Update web interface forms in `web_explorer.html` if needed
5. Update HTTP proxy tool list in `http_proxy.py`

### Adding Advanced Analysis Features
1. Implement analysis logic as separate functions in appropriate modules
2. Create MCP tool wrapper using @app.tool() decorator
3. Add complex form handling to web interface if needed
4. Include comprehensive testing for edge cases and error scenarios
5. Document analysis algorithms and expected input/output formats

### Web Interface Customization
1. Update `web_explorer.html` for new tool forms and result display
2. Modify `http_proxy.py` to support new tool parameters and validation
3. Test across different browsers and devices for compatibility
4. Ensure responsive design principles are maintained