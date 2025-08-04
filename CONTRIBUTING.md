# Contributing to MITRE ATT&CK MCP Server

Thank you for your interest in contributing to the MITRE ATT&CK MCP Server! This document provides guidelines for both human developers and agentic code assistants.

## 📋 Table of Contents

### For Human Developers
- [Code of Conduct](#code-of-conduct)
- [Getting Started (Human)](#getting-started-human)
- [Development Workflow (Human)](#development-workflow-human)
- [Adding New Features](#adding-new-features)
- [Web Interface Development](#web-interface-development)

### For Agentic Code Assistants
- [🤖 Agentic Workflow Guide](#-agentic-workflow-guide)
- [🔒 Branch Protection Rules](#-branch-protection-rules)
- [⚡ Quick Setup Commands](#-quick-setup-commands)
- [🧪 Testing Requirements](#-testing-requirements)
- [🚀 Deployment Workflow](#-deployment-workflow)

---

# 🤖 For Agentic Code Assistants

## 🤖 Agentic Workflow Guide

> **CRITICAL**: This section provides essential information for AI code assistants. Follow these patterns exactly to ensure successful contributions.

### 📋 Project Overview
- **Language**: Python 3.8+
- **Package Manager**: UV (modern Python package manager)
- **Architecture**: MCP server with 8 tools (5 basic + 3 advanced)
- **Testing**: 202+ comprehensive tests with pytest
- **Branch Strategy**: feature → staging → main (strictly enforced)

### ⚡ Quick Setup Commands

**Initial Setup:**
```bash
# Clone and setup
git clone https://github.com/gofastercloud/simple-mitre-mcp.git
cd simple-mitre-mcp

# Install UV if not available
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Verify installation
uv run pytest tests/ -x --tb=short
```

**Daily Development Pattern:**
```bash
# 1. Always start from staging
git checkout staging && git pull origin staging

# 2. Create feature branch
git checkout -b feature/$(date +%s)-your-change

# 3. Make changes and test
uv run pytest tests/ -x --tb=short

# 4. Commit and push
git add . && git commit -m "feat: your change description"
git push origin feature/$(date +%s)-your-change

# 5. Create PR to staging (NOT main)
gh pr create --base staging --title "Your Change" --body "Description"
```

## 🔒 Branch Protection Rules

**MANDATORY WORKFLOW (Automatically Enforced):**
```
feature/branch → staging → main
     ↓              ↓        ↓
   tests pass   tests pass  all checks + review
```

### ❌ BLOCKED Actions (Will Fail)
```bash
# These commands will be rejected:
git push origin main                    # Direct push to main
gh pr create --base main --head feature # PR from feature to main
git push --force origin main           # Force push to protected branch
```

### ✅ REQUIRED Actions
```bash
# Correct workflow:
git checkout staging && git pull origin staging
git checkout -b feature/your-change
# Make changes
uv run pytest tests/ -x --tb=short     # Tests must pass
git add . && git commit -m "feat: change"
git push origin feature/your-change
gh pr create --base staging            # PR to staging first
```

### 🧪 Required Status Checks (All Must Pass)
1. **Python 3.8-3.12 Tests** - All 202+ tests across 5 Python versions
2. **Security Scanning** - Bandit + Safety vulnerability checks
3. **Integration Testing** - End-to-end functionality verification
4. **Build Verification** - Package building and distribution
5. **Branch Source Validation** - Enforces staging-to-main flow

### 🔧 Troubleshooting Commands
```bash
# Check test failures
uv run pytest tests/ -v --tb=short

# Fix linting issues
uv run black . && uv run flake8 .

# Update branch with latest changes
git checkout staging && git pull origin staging
git checkout your-branch && git merge staging

# Check PR status
gh pr checks $PR_NUMBER
```
## 🧪 Testing Requirements

### Test Execution Commands
```bash
# Run all tests (202+ tests)
uv run pytest tests/

# Run with coverage reporting
uv run pytest tests/ --cov=src --cov-report=term-missing

# Run specific test categories
uv run pytest tests/test_mcp_server.py -v           # Core MCP server
uv run pytest tests/test_build_attack_path.py -v   # Advanced tools
uv run pytest tests/test_web_interface*.py -v      # Web interface

# Fast failure mode (stop on first failure)
uv run pytest tests/ -x --tb=short
```

### Test Requirements for New Code
- **All new features**: Must include comprehensive tests
- **Bug fixes**: Must include regression tests  
- **MCP tools**: Must test both success and error cases
- **Web interface**: Must test HTTP proxy integration
- **Advanced tools**: Must test complex analysis logic

### Code Quality Commands
```bash
# Format code (required)
uv run black .

# Lint code (must pass)
uv run flake8 src/ --count --statistics

# Type checking (recommended)
uv run mypy src/ --ignore-missing-imports

# Security scanning
uv run bandit -r src/ -f json
```

## 🚀 Deployment Workflow

### Feature Development Pattern
```bash
# 1. Setup
git checkout staging && git pull origin staging
git checkout -b feature/your-change

# 2. Development cycle
# Make changes
uv run pytest tests/ -x --tb=short  # Test locally
uv run black . && uv run flake8 .  # Format and lint

# 3. Commit and push
git add . && git commit -m "feat: description"
git push origin feature/your-change

# 4. Create PR to staging
gh pr create --base staging --title "Feature" --body "Description"
```

### Production Release Pattern
```bash
# After feature is merged to staging:
gh pr create --base main --head staging \
  --title "Release: Feature Name" \
  --body "Production release with comprehensive testing"
```

### UV Package Manager Commands
```bash
# Install dependencies
uv sync                    # Install all dependencies
uv sync --dev             # Include development dependencies

# Add new dependencies
uv add requests           # Add runtime dependency
uv add pytest --dev      # Add development dependency

# Run commands
uv run python script.py   # Run Python script
uv run pytest tests/     # Run tests
uv run black .           # Run formatter

# Environment management
uv venv                  # Create virtual environment
uv pip list             # List installed packages
```

---

# 👥 For Human Developers

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started (Human)

### Prerequisites
- Python 3.8 or higher
- UV package manager (recommended) or pip
- Git and GitHub CLI (optional but recommended)

### Fork and Clone
1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/simple-mitre-mcp.git
   cd simple-mitre-mcp
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/gofastercloud/simple-mitre-mcp.git
   ```

## Development Workflow (Human)

### Installation and Setup
```bash
# Install dependencies with UV (recommended)
uv sync

# Or with pip if UV not available
pip install -e .

# Copy environment template
cp .env.example .env

# Edit .env with your preferred settings
# MCP_HTTP_PORT=8000
# MCP_SERVER_PORT=3000

# Verify installation
uv run pytest tests/ -v
```

### Branch Strategy
> **Important**: Always follow the staging-to-main workflow. See [Branch Protection Rules](#-branch-protection-rules) for details.

```bash
# Start from staging branch
git checkout staging
git pull upstream staging

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

## Adding New Features

### Branch Naming Convention
- Features: `feature/description-of-feature`
- Bug fixes: `fix/description-of-fix`
- Documentation: `docs/description-of-change`
- Refactoring: `refactor/description-of-change`
- Web interface: `web/description-of-change`
- Advanced tools: `advanced/description-of-change`

### Development Process
1. **Plan your changes**: Review existing code and tests
2. **Create feature branch**: From staging (never from main)
3. **Implement changes**: Follow existing patterns and conventions
4. **Write tests**: Comprehensive coverage for new functionality
5. **Test locally**: All 202+ tests must pass
6. **Submit PR to staging**: Follow the protected workflow

### Commit Message Format
```
type(scope): brief description

Detailed description of the change (if needed)

- List specific changes
- Include any breaking changes
- Reference issues: Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `web`, `advanced`

### Testing Your Changes
```bash
# Run all tests locally
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Format and lint code
uv run black . && uv run flake8 .

# Test web interface if applicable
uv run start_explorer.py
```

### Pull Request Process
1. **Create PR to staging** (never directly to main)
2. **Ensure all tests pass** (202+ tests across Python 3.8-3.12)
3. **Update documentation** if needed
4. **Wait for automated checks** to pass
5. **Address review feedback**
6. **For main branch**: Requires 1 approving review

### Code Style Guidelines
- Follow PEP 8 with 88-character line length (Black formatter)
- Use type hints for function parameters and return values
- Write clear docstrings with Args, Returns, and Raises sections
- Keep functions focused and small
- Follow existing patterns in the codebase

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
