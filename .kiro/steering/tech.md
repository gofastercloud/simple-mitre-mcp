# Technology Stack

## Core Technologies

- **Python 3**: Primary programming language
- **FastMCP**: Official MCP server implementation from the `mcp` library
- **UV**: Modern Python package manager and project management tool
- **Model Context Protocol (MCP)**: Communication protocol for AI tool integration

## Dependencies

### Core Libraries (Prefer Existing, Battle-Tested Libraries)
- **mcp**: Official Model Context Protocol SDK for Python - provides FastMCP server implementation
- **stix2**: Official STIX 2.x library for parsing STIX data formats
- **requests**: HTTP library for downloading threat intelligence data
- **pyyaml**: Configuration file parsing (YAML format)
- **pytest**: Testing framework
- **pydantic**: Data validation and settings management

### Library Selection Principles
- **Always prefer official libraries** for well-known protocols and formats
- **Use established, maintained libraries** over custom implementations
- **Prioritize security-focused libraries** for parsing external data
- **Choose libraries with active communities** and regular updates

## Configuration-Driven Architecture

- **Data Sources**: Configured via YAML files, not hardcoded
- **Entity Schemas**: Defined in configuration to support different frameworks
- **Tool Definitions**: MCP tools configured externally for easy extension
- **URL Endpoints**: Data source URLs specified in configuration files

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

## Architecture Approach

- **Library-First Development**: Use existing, battle-tested libraries for standard protocols and formats
- **Extensible Design**: Framework-agnostic architecture supporting multiple security data sources
- **Configuration-Driven**: All data sources, schemas, and tools defined in external config files
- **Standards-Compliant**: Use official MCP library (FastMCP) and STIX data parsing libraries
- **In-memory data storage** for fast access with configurable data loading
- **Pluggable data parsers** using established parsing libraries
- **Security-Focused**: Prefer libraries with security track records for parsing external data
- **Modular tool system** allowing easy addition of new MCP tools

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