# Technology Stack

## Multi-Layer Architecture Technologies

### Core Data Layer
- **Python 3.12+**: Primary programming language for all components
- **STIX2 Library**: Official STIX parsing for secure threat intelligence data processing
- **UV**: Modern Python package manager and project management tool
- **YAML**: Configuration management across all components

### MCP Server Layer
- **FastMCP**: Official MCP server implementation from the `mcp` library
- **Model Context Protocol (MCP)**: Communication protocol for AI assistant integration
- **STDIO/HTTP Transports**: Multiple transport protocols for different AI clients

### Middleware Layer
- **Python Internal APIs**: Business logic and data transformation interfaces
- **Pydantic**: Data validation and type safety across component boundaries
- **In-Memory Caching**: Fast data access and query optimization

### Web Application Layer
- **Flask**: Modern web framework for HTTP APIs and web application serving
- **Flask Extensions**: Authentication, CORS, caching, and middleware support
- **Cytoscape.js**: Interactive graph visualization for MITRE ATT&CK relationships
- **Bootstrap 5**: Responsive UI framework for web interface

### CLI Layer
- **Click**: Command-line interface framework for automation tools
- **Rich**: Enhanced CLI output formatting and progress indicators

## Dependencies

### Component-Specific Dependencies

#### Data Layer Dependencies
- **stix2**: Official STIX 2.x library for secure threat intelligence parsing
- **requests**: HTTP library for downloading threat intelligence data
- **pyyaml**: Configuration file parsing across all components
- **pydantic**: Data validation and settings management

#### MCP Server Dependencies  
- **mcp**: Official Model Context Protocol SDK for Python
- **FastMCP**: MCP server implementation for AI assistant integration

#### Web Application Dependencies
- **Flask**: Web framework for HTTP APIs and static serving
- **Flask-CORS**: Cross-origin resource sharing support
- **Flask-Caching**: Response caching and performance optimization
- **Jinja2**: Template engine for dynamic web content

#### CLI Dependencies
- **Click**: Command-line interface framework
- **Rich**: Enhanced terminal output and progress indicators
- **Typer**: Alternative CLI framework with automatic help generation

#### Visualization Dependencies
- **Cytoscape.js**: Client-side graph visualization library
- **D3.js**: Alternative data visualization library (if needed)

#### Development and Testing
- **pytest**: Testing framework for all components
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Static type checking

### Library Selection Principles
- **Always prefer official libraries** for well-known protocols and formats
- **Use established, maintained libraries** over custom implementations
- **Prioritize security-focused libraries** for parsing external data
- **Choose libraries with active communities** and regular updates

## Multi-Component Configuration Architecture

### Centralized Configuration Management
- **Data Sources**: YAML configuration shared across all components
- **Entity Schemas**: Framework-agnostic entity definitions
- **Component Configuration**: Individual settings for MCP server, Flask app, CLI, and middleware
- **Environment Overrides**: Environment variables for deployment-specific settings

### Component-Specific Configuration
- **MCP Server**: Tool definitions, transport configuration, AI client settings
- **Middleware Layer**: Business logic rules, caching strategies, data transformation settings  
- **Flask Web App**: REST API configuration, authentication settings, graph visualization options
- **CLI Tool**: Command definitions, output formatting, automation settings

## Example Data Source Configuration

```yaml
data_sources:
  mitre_attack:
    url: "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    format: "stix"
    entity_types:
      - tactics
      - techniques
      - groups
      - mitigations
```

## Development Workflow (CRITICAL)

> **MANDATORY**: Before making any changes, read `CONTRIBUTING.md` and follow the branch protection workflow defined in `.kiro/steering/workflow.md`.

### Required Setup Pattern
```bash
# 0. CRITICAL: Verify current branch status
git status && git branch --show-current

# 1. Always start from staging
git checkout staging && git pull origin staging

# 2. Install dependencies with UV
uv sync

# 3. Create feature branch IMMEDIATELY
git checkout -b feature/$(date +%s)-your-change

# 4. Verify you're on the feature branch
git branch --show-current

# 5. Test before any changes
uv run pytest tests/ -x --tb=short
```

### 🚨 Workflow Validation Checklist
Before making any code changes, verify:
- [ ] Current branch is a feature branch (not staging/main)
- [ ] Feature branch name includes timestamp
- [ ] All tests pass on clean branch
- [ ] Dependencies are installed with `uv sync`

### Development Commands (UV Required)
```bash
# Run the MCP server
uv run main.py

# Run tests (REQUIRED before pushing)
uv run pytest tests/ -x --tb=short

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Format code (REQUIRED)
uv run black .

# Lint code (REQUIRED)
uv run flake8 .

# Start web interface
uv run start_explorer.py
```

### Branch Protection Compliance
```bash
# Create PR to staging (NOT main)
gh pr create --base staging --title "Change" --body "Description"

# Check status
gh pr checks $PR_NUMBER
```

### MCP Server Testing
```bash
# Test MCP server using streamable-http transport
# Server runs with official MCP protocol implementation
# Use MCP client tools or test with MCP-compatible clients
```

## Multi-Layer Architecture Approach

### Core Design Principles
- **Separation of Concerns**: Each layer has distinct responsibilities and interfaces
- **Component Independence**: Components can be developed, deployed, and scaled independently
- **Library-First Development**: Use existing, battle-tested libraries for all standard protocols
- **Configuration-Driven**: All components share centralized configuration management
- **Standards-Compliant**: Official libraries for MCP, STIX, Flask, and CLI frameworks

### Layer-Specific Approaches
- **Data Layer**: Centralized STIX parsing and caching with configuration-driven data source management
- **MCP Server**: Pure AI assistant integration using official FastMCP with 8 specialized tools
- **Middleware Layer**: Business logic APIs providing data aggregation and transformation services
- **Flask Web Layer**: Modern web framework with REST APIs, authentication, and graph visualization
- **CLI Layer**: Command-line automation tools with rich output formatting and scripting support

### Inter-Component Communication
- **Data Sharing**: Centralized data layer accessible by all components
- **API Interfaces**: Well-defined internal APIs for middleware business logic
- **Configuration Sync**: Shared configuration system with component-specific overrides
- **Error Propagation**: Consistent error handling and logging across all layers

## Code Quality Standards

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Keep functions focused and single-purpose
- Limit line length to 88 characters (Black formatter default)
- Use type hints for function parameters and return values

### Documentation Requirements
- Include docstrings for all public functions and classes
- Use Google-style docstrings with Args, Returns, and Raises sections
- Add inline comments for complex logic or framework-specific concepts
- Document MCP tool parameters and expected return formats
- Document configuration file schemas and options
- Keep README updated with setup, usage, and extension instructions

### Error Handling
- Implement graceful error handling with informative messages
- Log errors appropriately for debugging
- Return structured error responses for MCP tools
- Validate input parameters and provide clear feedback

### Testing Standards
- **ALL test files must be created in the `tests/` directory**
- Never create test files in the root directory or other locations
- Use pytest as the testing framework
- Follow naming convention: `test_<module_name>.py` for testing `src/<module_name>.py`
- Include comprehensive unit tests for all public functions and classes
- Test both success and failure scenarios
- Use mocking for external dependencies (HTTP requests, file I/O, etc.)
- Maintain high test coverage for critical functionality