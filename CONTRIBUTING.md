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
uv sync --dev

# Verify installation
uv run pytest tests/ -v
```

### Environment Setup
```bash
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

### Commit Message Format
```
type(scope): brief description

Detailed description of the change (if needed)

- List specific changes
- Include any breaking changes
- Reference issues: Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Testing

### Running Tests
```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_specific_file.py

# Run tests for specific tool
uv run pytest tests/test_search_attack.py -v
```

### Test Requirements
- All new features must include tests
- Bug fixes must include regression tests
- Tests should cover both success and error cases
- Integration tests for new MCP tools
- Maintain or improve code coverage

### Test Categories
1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test tool interactions with real data
3. **End-to-End Tests**: Test complete workflows
4. **Web Interface Tests**: Test HTTP proxy and web UI

## Submitting Changes

### Pull Request Process
1. Ensure all tests pass locally
2. Update documentation if needed
3. Add/update tests for your changes
4. Run linting and type checking
5. Create a pull request with a clear description
6. Link any related issues
7. Wait for review and address feedback

### Pull Request Checklist
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] No new linting errors
- [ ] Commit messages are clear
- [ ] PR description explains the changes

## Code Style

### Python Style Guidelines
- Follow PEP 8 with line length of 120 characters
- Use type hints for all function parameters and return values
- Write clear, descriptive docstrings
- Use meaningful variable and function names

### Linting and Formatting
```bash
# Run linting
uv run flake8 src/ tests/

# Run type checking
uv run mypy src/

# Run security checks
uv run bandit -r src/
```

### Code Organization
- Keep functions focused and small
- Use clear separation of concerns
- Follow existing patterns in the codebase
- Add comprehensive error handling

## Adding New MCP Tools

### Tool Development Process
1. **Design**: Plan the tool's functionality and API
2. **Configuration**: Add tool definition to `config/tools.yaml`
3. **Implementation**: Add tool function to `src/mcp_server.py`
4. **Testing**: Create comprehensive test suite
5. **Documentation**: Update README and docstrings
6. **Integration**: Test with web interface

### Tool Implementation Template
```python
@app.tool()
async def your_new_tool(param1: str, param2: int = 10) -> List[TextContent]:
    """
    Brief description of what the tool does.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 with default value
        
    Returns:
        List[TextContent]: Description of return value
    """
    try:
        logger.info(f"Executing your_new_tool with param1: {param1}")
        
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
        
        # Tool implementation here
        result_text = "Your tool output here"
        
        return [TextContent(
            type="text",
            text=result_text
        )]
        
    except Exception as e:
        logger.error(f"Error in your_new_tool: {e}")
        return [TextContent(
            type="text",
            text=f"Error in tool execution: {str(e)}"
        )]
```

### Tool Configuration
Add to `config/tools.yaml`:
```yaml
your_new_tool:
  description: "Brief description of the tool"
  parameters:
    - name: "param1"
      type: "string"
      required: true
      description: "Description of parameter 1"
    - name: "param2"
      type: "integer"
      required: false
      description: "Description of parameter 2"
```

### Tool Testing Template
```python
class TestYourNewTool:
    @pytest.mark.asyncio
    async def test_your_new_tool_basic(self, mcp_server):
        """Test basic functionality of your new tool."""
        result, _ = await mcp_server.call_tool('your_new_tool', {
            'param1': 'test_value'
        })
        
        assert result is not None
        assert len(result) > 0
        assert result[0].type == "text"
        assert "expected_content" in result[0].text
```

## Documentation

### Documentation Requirements
- Update README.md for new features
- Add docstrings to all functions and classes
- Update configuration documentation
- Include usage examples
- Document any breaking changes

### Documentation Style
- Use clear, concise language
- Include code examples
- Explain the "why" not just the "what"
- Keep documentation up to date with code changes

## Questions and Support

- Create an issue for questions about contributing
- Join discussions in existing issues
- Check existing documentation and code examples
- Follow the project's communication guidelines

## Recognition

Contributors will be recognized in the project's documentation and release notes. Thank you for helping make this project better!
