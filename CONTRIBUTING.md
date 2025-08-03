# Contributing to MITRE ATT&CK MCP Server

Thank you for your interest in contributing to the MITRE ATT&CK MCP Server! This document provides guidelines and information for contributors.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Adding New MCP Tools](#adding-new-mcp-tools)
- [Web Interface Development](#web-interface-development)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a new branch for your changes
5. Make your changes
6. Test your changes
7. Submit a pull request

## Development Setup

### Prerequisites
- Python 3.8 or higher
- UV package manager

### Installation
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/simple-mitre-mcp.git
cd simple-mitre-mcp

# Install dependencies
uv sync

# Verify installation
uv run pytest tests/ -v
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your preferred settings
# MCP_HTTP_PORT=8000
# MCP_SERVER_PORT=3000

# Create a new branch for your feature
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

## Making Changes

### Branch Naming Convention
- Features: `feature/description-of-feature`
- Bug fixes: `fix/description-of-fix`
- Documentation: `docs/description-of-change`
- Refactoring: `refactor/description-of-change`
- Web interface: `web/description-of-change`
- Advanced tools: `advanced/description-of-change`

### Commit Message Format
```
type(scope): brief description

Detailed description of the change (if needed)

- List specific changes
- Include any breaking changes
- Reference issues: Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `web`, `advanced`

## Testing

### Running Tests
```bash
# Run all tests (167+ comprehensive tests)
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Run specific test categories
uv run pytest tests/test_mcp_server.py -v                    # Core MCP server tests
uv run pytest tests/test_build_attack_path.py -v            # Attack path construction tests
uv run pytest tests/test_analyze_coverage_gaps.py -v        # Coverage gap analysis tests
uv run pytest tests/test_detect_technique_relationships.py -v # Relationship discovery tests
uv run pytest tests/test_web_interface_advanced.py -v       # Web interface integration tests

# Run tests for specific tool types
uv run pytest tests/ -k "basic" -v                          # Basic analysis tools
uv run pytest tests/ -k "advanced" -v                       # Advanced threat modeling tools
```

### Test Requirements
- All new features must include comprehensive tests
- Bug fixes must include regression tests
- Tests should cover both success and error cases
- Integration tests for new MCP tools
- Web interface tests for UI changes
- Advanced tool tests for complex analysis logic
- Maintain or improve code coverage (currently 167+ tests)

### Test Categories
1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test tool interactions with real data
3. **Advanced Tool Tests**: Test complex threat modeling algorithms
4. **Web Interface Tests**: Test HTTP proxy and web UI functionality
5. **End-to-End Tests**: Test complete workflows including web interface
6. **Configuration Tests**: Test environment variable and config file handling

## Submitting Changes

### Pull Request Process
1. Ensure all tests pass locally
2. Update documentation if needed
3. Add/update tests for your changes
4. Run linting and type checking
5. Test web interface if UI changes made
6. Create a pull request with a clear description
7. Link any related issues
8. Wait for review and address feedback

### Pull Request Checklist
- [ ] Tests added/updated and passing (all 167+ tests)
- [ ] Documentation updated (README, docstrings, etc.)
- [ ] Code follows style guidelines
- [ ] No new linting errors
- [ ] Web interface tested if applicable
- [ ] Advanced tools tested if applicable
- [ ] Environment configuration tested
- [ ] Commit messages are clear
- [ ] PR description explains the changes

## Code Style

### Python Style Guidelines
- Follow PEP 8 with line length of 88 characters (Black formatter default)
- Use type hints for all function parameters and return values
- Write clear, descriptive docstrings with Args, Returns, and Raises sections
- Use meaningful variable and function names

### Linting and Formatting
```bash
# Format code
uv run black .

# Run linting
uv run flake8 .

# Run type checking
uv run mypy src/
```

### Code Organization
- Keep functions focused and small
- Use clear separation of concerns
- Follow existing patterns in the codebase
- Add comprehensive error handling
- Use configuration constants instead of hardcoded values

## Adding New MCP Tools

The server currently supports **8 comprehensive MCP tools**:

### Basic Analysis Tools (5 Core Tools)
1. `search_attack` - Global search across all ATT&CK entities
2. `get_technique` - Detailed technique information
3. `list_tactics` - Complete tactics enumeration
4. `get_group_techniques` - Threat group TTP analysis
5. `get_technique_mitigations` - Mitigation mapping

### Advanced Threat Modeling Tools (3 Sophisticated Tools)
6. `build_attack_path` - Multi-stage attack path construction
7. `analyze_coverage_gaps` - Defensive coverage gap analysis
8. `detect_technique_relationships` - Complex STIX relationship discovery

### Tool Development Process
1. **Design**: Plan the tool's functionality and API
2. **Configuration**: Add tool definition to `config/tools.yaml`
3. **Implementation**: Add tool function to `src/mcp_server.py`
4. **Testing**: Create comprehensive test suite
5. **Web Interface**: Add forms and handlers to `web_explorer.html`
6. **HTTP Proxy**: Update `http_proxy.py` tool list
7. **Documentation**: Update README and docstrings
8. **Integration**: Test with all access methods (MCP, web, HTTP API)

### Basic Tool Implementation Template
```python
@app.tool()
async def your_basic_tool(param1: str, param2: int = 10) -> List[TextContent]:
    """
    Brief description of what the tool does.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 with default value
        
    Returns:
        List[TextContent]: Description of return value
    """
    try:
        logger.info(f"Executing your_basic_tool with param1: {param1}")
        
        # Validate data loader
        if not app.data_loader:
            return [TextContent(
                type="text",
                text="Error: Data loader not available."
            )]
        
        # Get cached data
        data = app.data_loader.get_cached_data('mitre_attack')
        if not data:
            return [TextContent(
                type="text",
                text="Error: MITRE ATT&CK data not loaded."
            )]
        
        # Basic tool implementation here
        result_text = "Your basic tool output here"
        
        return [TextContent(
            type="text",
            text=result_text
        )]
        
    except Exception as e:
        logger.error(f"Error in your_basic_tool: {e}")
        return [TextContent(
            type="text",
            text=f"Error in tool execution: {str(e)}"
        )]
```

### Advanced Tool Implementation Template
```python
@app.tool()
async def your_advanced_tool(
    primary_param: str,
    array_param: List[str],
    optional_param: str = "default",
    depth: int = 2
) -> List[TextContent]:
    """
    Advanced tool for complex threat modeling analysis.
    
    Args:
        primary_param: Primary analysis target
        array_param: Array of entities to analyze
        optional_param: Optional configuration parameter
        depth: Analysis depth (1-3, default: 2)
        
    Returns:
        List[TextContent]: Complex analysis results with structured data
    """
    try:
        logger.info(f"Executing advanced tool: {primary_param}, depth: {depth}")
        
        # Validate parameters
        if depth < 1 or depth > 3:
            return [TextContent(
                type="text",
                text="Error: Depth must be between 1 and 3."
            )]
        
        # Validate data loader
        if not app.data_loader:
            return [TextContent(
                type="text",
                text="Error: Data loader not available."
            )]
        
        # Get cached data with relationships
        data = app.data_loader.get_cached_data('mitre_attack')
        if not data:
            return [TextContent(
                type="text",
                text="Error: MITRE ATT&CK data not loaded."
            )]
        
        # Advanced analysis implementation
        analysis_results = perform_complex_analysis(
            data, primary_param, array_param, depth
        )
        
        # Format structured results
        result_text = format_advanced_results(analysis_results)
        
        return [TextContent(
            type="text",
            text=result_text
        )]
        
    except Exception as e:
        logger.error(f"Error in advanced tool: {e}")
        return [TextContent(
            type="text",
            text=f"Error in advanced analysis: {str(e)}"
        )]
```

### Tool Configuration
Add to `config/tools.yaml`:
```yaml
your_advanced_tool:
  description: "Advanced threat modeling analysis tool"
  parameters:
    - name: "primary_param"
      type: "string"
      required: true
      description: "Primary analysis target"
    - name: "array_param"
      type: "array"
      required: true
      description: "Array of entities to analyze"
    - name: "optional_param"
      type: "string"
      required: false
      description: "Optional configuration parameter"
    - name: "depth"
      type: "integer"
      required: false
      description: "Analysis depth (1-3, default: 2)"
```

### Tool Testing Template
```python
class TestYourAdvancedTool:
    @pytest.mark.asyncio
    async def test_advanced_tool_basic(self, mcp_server):
        """Test basic functionality of advanced tool."""
        result, _ = await mcp_server.call_tool('your_advanced_tool', {
            'primary_param': 'T1055',
            'array_param': ['G0016', 'G0032'],
            'depth': 2
        })
        
        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        assert "analysis" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_advanced_tool_edge_cases(self, mcp_server):
        """Test edge cases and error handling."""
        # Test invalid depth
        result, _ = await mcp_server.call_tool('your_advanced_tool', {
            'primary_param': 'T1055',
            'array_param': ['G0016'],
            'depth': 5  # Invalid depth
        })
        
        assert "Error: Depth must be between 1 and 3" in result[0].text
    
    @pytest.mark.asyncio
    async def test_advanced_tool_complex_scenario(self, mcp_server):
        """Test complex analysis scenario."""
        result, _ = await mcp_server.call_tool('your_advanced_tool', {
            'primary_param': 'T1059',
            'array_param': ['G0016', 'G0032', 'G0007'],
            'optional_param': 'Windows',
            'depth': 3
        })
        
        assert result is not None
        assert len(result) > 0
        # Add specific assertions for complex analysis results
```

## Web Interface Development

### Web Interface Architecture
The web interface consists of:
- **`web_explorer.html`**: Interactive HTML interface with JavaScript
- **`http_proxy.py`**: HTTP server that bridges web requests to MCP tools
- **`start_explorer.py`**: Convenient launcher script

### Adding Web Interface Support for New Tools

#### 1. Update `web_explorer.html`
```html
<!-- Add button for your tool -->
<button onclick="showInputForm('your_advanced_tool', [
    {name: 'primary_param', type: 'text', required: true, placeholder: 'Enter primary parameter'},
    {name: 'array_param', type: 'array', required: true, placeholder: 'Enter comma-separated values'},
    {name: 'optional_param', type: 'text', required: false, placeholder: 'Optional parameter'},
    {name: 'depth', type: 'number', required: false, placeholder: 'Analysis depth (1-3)', min: 1, max: 3}
])">🧠 Your Advanced Tool</button>
```

#### 2. Update `http_proxy.py`
```python
# Add your tool to the tools list in handle_tools_list method
{
    "name": "your_advanced_tool",
    "description": "Advanced threat modeling analysis tool",
    "inputSchema": {
        "type": "object",
        "properties": {
            "primary_param": {"type": "string", "description": "Primary analysis target"},
            "array_param": {"type": "array", "items": {"type": "string"}, "description": "Array of entities"},
            "optional_param": {"type": "string", "description": "Optional parameter"},
            "depth": {"type": "integer", "minimum": 1, "maximum": 3, "description": "Analysis depth"}
        },
        "required": ["primary_param", "array_param"]
    }
}
```

#### 3. Test Web Interface
```bash
# Start the web interface
uv run start_explorer.py

# Test your new tool through the web interface
# Verify forms work correctly
# Test error handling
# Verify results display properly
```

### Web Interface Testing
```python
class TestWebInterfaceAdvanced:
    def test_advanced_tool_form_generation(self):
        """Test that advanced tool forms are generated correctly."""
        # Test form HTML generation
        # Test parameter validation
        # Test array input handling
        
    def test_advanced_tool_execution(self):
        """Test advanced tool execution through web interface."""
        # Test HTTP proxy tool execution
        # Test result formatting
        # Test error handling
```

## Environment Configuration

### Configuration Files
- **`.env.example`**: Template for environment variables
- **`config/data_sources.yaml`**: Data source definitions
- **`config/entity_schemas.yaml`**: Entity type schemas
- **`config/tools.yaml`**: MCP tool configurations

### Environment Variables
```bash
# MCP Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=3000

# HTTP Proxy Configuration
MCP_HTTP_HOST=localhost
MCP_HTTP_PORT=8000

# Data Source Configuration
MITRE_ATTACK_URL=https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json
```

### Testing Configuration Changes
```bash
# Test with different ports
MCP_HTTP_PORT=3000 uv run start_explorer.py

# Test configuration validation
uv run pytest tests/test_port_config.py -v
```

## Documentation

### Documentation Requirements
- Update README.md for new features
- Add docstrings to all functions and classes
- Update configuration documentation
- Include usage examples for both MCP and web interface
- Document any breaking changes
- Update .kiro specifications if needed

### Documentation Style
- Use clear, concise language
- Include code examples for both basic and advanced usage
- Explain the "why" not just the "what"
- Keep documentation up to date with code changes
- Use emojis and formatting for better readability

## Questions and Support

- Create an issue for questions about contributing
- Join discussions in existing issues
- Check existing documentation and code examples
- Follow the project's communication guidelines
- Test both MCP protocol and web interface access methods

## Recognition

Contributors will be recognized in the project's documentation and release notes. Thank you for helping make this comprehensive threat intelligence platform better!

---

**🚀 Ready to contribute to advanced threat modeling capabilities? Start with the web interface:**

```bash
uv run start_explorer.py
```
