# Project Structure

## Multi-Layer Architecture Overview

This project implements a comprehensive cybersecurity threat intelligence platform with a clean separation of concerns across multiple layers:

```
┌─────────────────────────────────────────────────────────┐
│                 External Interfaces                     │
├──────────────────┬──────────────────┬──────────────────┤
│   AI Assistants  │  Web Browsers    │   CLI Users      │
│   (Claude, etc.) │  (Dashboard)     │   (Scripts)      │
└──────────────────┴──────────────────┴──────────────────┘
        │                   │                    │
        ▼                   ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   MCP Server    │ │  Flask Web App  │ │   CLI Tool      │
│   (Pure AI)     │ │  (Web + Graph)  │ │  (Automation)   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
        │                   │                    │
        └─────────────────────┼────────────────────┘
                             │
                             ▼
                  ┌─────────────────┐
                  │ Middleware APIs │
                  │ (Business Logic)│
                  └─────────────────┘
                             │
                             ▼
                  ┌─────────────────┐
                  │   Data Layer    │
                  │ (STIX + Config) │
                  └─────────────────┘
```

## Directory Organization

```
.
├── README.md               # Project overview and setup instructions
├── pyproject.toml         # UV project configuration and all dependencies
├── .env.example           # Environment variable configuration template
├── config/                # Centralized configuration (shared across all components)
│   ├── data_sources.yaml  # Data source definitions
│   ├── entity_schemas.yaml # Entity type schemas
│   ├── component_config.yaml # Component-specific settings
│   └── tools.yaml         # MCP tool configurations
├── src/                   # Source code directory
│   ├── data/              # Data layer (shared foundation)
│   │   ├── __init__.py
│   │   ├── data_loader.py # STIX data loading and caching
│   │   ├── config_loader.py # Configuration management
│   │   └── parsers/       # Data format parsers
│   │       ├── __init__.py
│   │       ├── stix_parser.py # STIX format parser
│   │       └── base_parser.py # Base parser interface
│   ├── mcp_server/        # Pure MCP server (AI assistant integration)
│   │   ├── __init__.py
│   │   ├── mcp_server.py  # FastMCP server with 8 tools
│   │   ├── main_stdio.py  # STDIO transport entry point
│   │   └── main_http.py   # HTTP transport entry point
│   ├── middleware/        # Business logic and data transformation APIs
│   │   ├── __init__.py
│   │   ├── threat_analysis.py # Threat analysis business logic
│   │   ├── graph_builder.py   # Graph data structure creation
│   │   ├── query_engine.py    # Advanced query processing
│   │   └── cache_manager.py   # Caching and performance optimization
│   ├── web_app/           # Flask web application
│   │   ├── __init__.py
│   │   ├── app.py         # Flask application factory
│   │   ├── api/           # REST API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── threat_intelligence.py # Threat intel endpoints
│   │   │   ├── graph_data.py         # Graph visualization data
│   │   │   └── system_info.py        # System information endpoints
│   │   ├── auth/          # Authentication and authorization
│   │   │   ├── __init__.py
│   │   │   └── auth.py    # Auth logic (if needed)
│   │   ├── static/        # Static files (CSS, JS, images)
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── assets/
│   │   └── templates/     # Jinja2 templates
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       └── graph.html
│   ├── cli/               # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py        # CLI entry point
│   │   ├── commands/      # CLI command modules
│   │   │   ├── __init__.py
│   │   │   ├── search.py  # Search commands
│   │   │   ├── analysis.py # Analysis commands
│   │   │   └── export.py  # Export commands
│   │   └── utils/         # CLI utilities
│   │       ├── __init__.py
│   │       ├── output.py  # Rich output formatting
│   │       └── config.py  # CLI-specific configuration
│   └── shared/            # Shared utilities across components
│       ├── __init__.py
│       ├── models.py      # Shared data models
│       ├── exceptions.py  # Custom exception classes
│       └── utils.py       # Common utility functions
├── tests/                 # Comprehensive test suite (ALL tests in this directory)
│   ├── __init__.py
│   ├── conftest.py        # Shared pytest fixtures
│   ├── data/              # Test data layer
│   │   ├── test_data_loader.py
│   │   ├── test_config_loader.py
│   │   └── test_parsers.py
│   ├── mcp_server/        # Test MCP server functionality
│   │   ├── test_mcp_server.py
│   │   ├── test_tools.py
│   │   └── test_transports.py
│   ├── middleware/        # Test middleware APIs
│   │   ├── test_threat_analysis.py
│   │   ├── test_graph_builder.py
│   │   └── test_query_engine.py
│   ├── web_app/           # Test Flask web application
│   │   ├── test_api_endpoints.py
│   │   ├── test_auth.py
│   │   └── test_web_interface.py
│   ├── cli/               # Test CLI functionality
│   │   ├── test_commands.py
│   │   ├── test_search.py
│   │   └── test_output.py
│   └── integration/       # End-to-end integration tests
│       ├── test_full_workflow.py
│       ├── test_component_integration.py
│       └── test_performance.py
├── scripts/               # Development and deployment scripts
│   ├── start_mcp_server.py   # MCP server launcher
│   ├── start_web_app.py     # Flask web app launcher  
│   ├── start_cli.py         # CLI launcher
│   └── deploy.py           # Deployment script
├── docs/                  # Component-specific documentation
│   ├── mcp_server.md      # MCP server documentation
│   ├── middleware.md      # Middleware API documentation
│   ├── web_app.md         # Flask web app documentation
│   ├── cli.md             # CLI documentation
│   └── deployment.md      # Deployment guide
├── examples/              # Usage examples for each component
│   ├── mcp_examples/      # MCP server usage examples
│   ├── api_examples/      # REST API usage examples
│   └── cli_examples/      # CLI usage examples
└── .kiro/                 # Kiro project management
    ├── specs/             # Project specifications
    └── steering/          # AI assistant guidance
```

## Component Responsibilities

### Data Layer (`src/data/`)
- **STIX data loading and parsing** using official stix2 library
- **Configuration management** shared across all components
- **Data caching** and persistence for performance
- **Framework-agnostic data models** supporting multiple threat intelligence formats

### MCP Server Layer (`src/mcp_server/`)
- **Pure AI assistant integration** using FastMCP
- **8 specialized MCP tools** for threat intelligence analysis
- **STDIO and HTTP transports** for different AI client types
- **No web dependencies** - focused solely on MCP protocol

### Middleware Layer (`src/middleware/`)
- **Business logic APIs** for complex analysis operations
- **Graph data structure creation** for visualization components
- **Query engine** for advanced data retrieval and filtering
- **Cache management** and performance optimization

### Flask Web Application (`src/web_app/`)
- **REST API endpoints** for web clients and external integrations
- **Graph visualization interface** using Cytoscape.js
- **Authentication and authorization** (if required)
- **Static file serving** and web interface hosting

### CLI Layer (`src/cli/`)
- **Command-line automation tools** for scripting and batch operations
- **Rich output formatting** for enhanced terminal experience
- **Export capabilities** for integration with external tools
- **Automation-friendly interfaces** for CI/CD and scripting

## Development Workflow Requirements

> **CRITICAL**: This project has strict branch protection and workflow requirements. ALL changes must follow the patterns in `.kiro/steering/workflow.md` and `CONTRIBUTING.md`.

### Mandatory Workflow
- **Multi-component development** with proper layer separation
- **Component-specific testing** with comprehensive test coverage
- **Use UV package manager** for all dependency management
- **Follow staging-to-main flow** - feature → staging → main (strictly enforced)
- **Test all components** before pushing changes

### Component Development Guidelines
- **Data Layer First**: Always start with data layer changes, then propagate up
- **API Contracts**: Define clear interfaces between middleware and web/CLI layers
- **Independent Testing**: Each component must have comprehensive test coverage
- **Configuration Consistency**: Use centralized configuration management

## Configuration Management

### Environment Variables
```bash
# Data Layer Configuration
MITRE_ATTACK_URL=https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json
CACHE_DIR=./cache
LOG_LEVEL=INFO

# MCP Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=3000

# Flask Web App Configuration
FLASK_HOST=localhost
FLASK_PORT=8000
FLASK_DEBUG=false
SECRET_KEY=your-secret-key

# CLI Configuration
CLI_OUTPUT_FORMAT=rich
CLI_CACHE_ENABLED=true
```

### Component-Specific Configuration Files
- **`config/data_sources.yaml`**: Data source definitions (shared)
- **`config/entity_schemas.yaml`**: Entity type schemas (shared)
- **`config/component_config.yaml`**: Component-specific settings
- **`config/tools.yaml`**: MCP tool configurations

## Extension Guidelines

### Adding New Components
1. Create new directory under `src/` following naming conventions
2. Implement component following separation of concerns principles
3. Create comprehensive tests in `tests/[component]/`
4. Update configuration files as needed
5. Add component documentation in `docs/`

### Adding New Data Sources
1. Define data source in `config/data_sources.yaml`
2. Create parser in `src/data/parsers/` if needed
3. Update entity schemas in `config/entity_schemas.yaml`
4. Test across all components that use the data

### Adding New MCP Tools
1. Define tool in `config/tools.yaml`
2. Implement in `src/mcp_server/mcp_server.py`
3. Add comprehensive tests in `tests/mcp_server/`
4. Update middleware APIs if needed

### Adding New Web Features
1. Create REST API endpoints in `src/web_app/api/`
2. Implement middleware business logic if needed
3. Add frontend components in static files
4. Create comprehensive tests

### Adding New CLI Commands
1. Create command module in `src/cli/commands/`
2. Update CLI main entry point
3. Add help documentation and examples
4. Test command functionality

## Key Principles

### Separation of Concerns
- **Data Layer**: Only data loading, parsing, and caching
- **MCP Server**: Only AI assistant integration and tool execution
- **Middleware**: Only business logic and data transformation
- **Web App**: Only web interfaces, REST APIs, and authentication
- **CLI**: Only command-line automation and scripting

### Component Independence
- Each component can be developed and deployed independently
- Clear API contracts between layers
- Minimal coupling between components
- Shared configuration management

### Library-First Development
- Use official libraries for all standard protocols
- Prefer established, maintained libraries
- Security-focused libraries for external data parsing
- Consistent library usage across components

### Testing Excellence
- **ALL tests must be in `tests/` directory**
- Component-specific test organization
- Integration tests for component interaction
- Performance tests for critical paths
- 400+ comprehensive test coverage target