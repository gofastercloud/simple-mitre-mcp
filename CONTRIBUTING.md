# Contributing to MITRE ATT&CK MCP Server

Thank you for your interest in contributing to the MITRE ATT&CK MCP Server! This document provides guidelines and information for contributors.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Branch Protection & Workflow](#branch-protection--workflow)
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

## Branch Protection & Workflow

> **🤖 For Code Assistants & Agentic Workflows**: This section defines the mandatory workflow that all code changes must follow. These rules are enforced by GitHub branch protection and automated checks.

### 🔒 **CRITICAL: Branch Protection Rules**

This repository enforces a **strict staging-to-main workflow** with automated protection:

```
main (production) ← ONLY from staging via PR
  ↑
staging (integration) ← from feature branches  
  ↑
feature/* (development)
```

### ⚠️ **MANDATORY WORKFLOW FOR ALL CHANGES**

**Step 1: Create Feature Branch from Staging**
```bash
# ALWAYS start from staging, never from main
git checkout staging
git pull origin staging
git checkout -b feature/your-feature-name
```

**Step 2: Make Changes and Push to Feature Branch**
```bash
# Make your changes
git add .
git commit -m "feat: your changes"
git push origin feature/your-feature-name
```

**Step 3: Create PR to Staging (NOT main)**
```bash
# Create PR to staging first
gh pr create --base staging --head feature/your-feature-name \
  --title "Your Feature" --body "Description"
```

**Step 4: After Staging Merge, Create PR to Main**
```bash
# Only after feature is merged to staging
gh pr create --base main --head staging \
  --title "Release: Your Feature" --body "Production release"
```

### 🚫 **BLOCKED ACTIONS (Will Fail)**

These actions are **automatically blocked** by branch protection:

❌ **Direct pushes to main branch**
```bash
git push origin main  # ← BLOCKED
```

❌ **PRs from feature branches to main**
```bash
gh pr create --base main --head feature/branch  # ← BLOCKED
```

❌ **Force pushes to protected branches**
```bash
git push --force origin main     # ← BLOCKED
git push --force origin staging  # ← BLOCKED
```

❌ **Merging with failing tests**
- Any failing CI/CD check blocks merge
- All 9 required status checks must pass

### ✅ **REQUIRED STATUS CHECKS (All Must Pass)**

Before any merge to main, these checks are **mandatory**:

1. **`CI/CD Pipeline/test (3.8)`** - Python 3.8 tests (202+ tests)
2. **`CI/CD Pipeline/test (3.9)`** - Python 3.9 tests  
3. **`CI/CD Pipeline/test (3.10)`** - Python 3.10 tests
4. **`CI/CD Pipeline/test (3.11)`** - Python 3.11 tests
5. **`CI/CD Pipeline/test (3.12)`** - Python 3.12 tests
6. **`CI/CD Pipeline/security`** - Security vulnerability scanning
7. **`CI/CD Pipeline/integration`** - Integration testing
8. **`CI/CD Pipeline/build`** - Package building verification
9. **`Branch Protection/validate-source-branch`** - Enforces staging-only merges

### 🤖 **For Agentic Workflows: Automated Compliance**

**Pre-flight Checklist for Code Assistants:**
```bash
# 1. Verify current branch is staging
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "staging" ]; then
  echo "❌ Must start from staging branch"
  git checkout staging && git pull origin staging
fi

# 2. Create feature branch
git checkout -b feature/$(date +%s)-automated-change

# 3. Make changes (your code here)

# 4. Run tests locally before pushing
uv run pytest tests/ -x --tb=short
if [ $? -ne 0 ]; then
  echo "❌ Tests failed - fix before pushing"
  exit 1
fi

# 5. Push and create PR to staging
git add . && git commit -m "feat: automated change"
git push origin feature/$(date +%s)-automated-change
gh pr create --base staging --title "Automated Change" --body "Description"
```

**Status Check Validation:**
```bash
# Check if all required checks pass
gh pr checks $PR_NUMBER --json state,conclusion \
  --jq '.[] | select(.conclusion != "SUCCESS") | .name'

# If any checks fail, the merge is blocked
```

### 🔧 **Troubleshooting Branch Protection**

**Error: "Required status checks are failing"**
```bash
# Check which tests are failing
gh pr checks $PR_NUMBER

# Run failing tests locally
uv run pytest tests/test_specific_module.py -v

# Fix issues and push again
git add . && git commit -m "fix: resolve test failures"
git push origin your-branch
```

**Error: "Branch is not up to date"**
```bash
# Update your branch with latest changes
git checkout staging
git pull origin staging
git checkout your-feature-branch
git merge staging  # or git rebase staging
git push origin your-feature-branch
```

**Error: "Only staging branch can merge to main"**
```bash
# You tried to create PR from feature branch to main
# SOLUTION: Merge to staging first
gh pr create --base staging --head your-feature-branch
# After staging merge, then create staging → main PR
```

**Error: "Pull request reviews required"**
```bash
# Main branch requires 1 approving review
# Request review from team member:
gh pr review $PR_NUMBER --request-reviewer @username
```

### 📊 **Branch Protection Status**

**Main Branch Protection:**
- ✅ Pull requests required (no direct pushes)
- ✅ 1 approving review required
- ✅ 9 status checks required (all must pass)
- ✅ Up-to-date branches required
- ✅ Conversation resolution required
- ✅ Source branch validation (staging only)
- ✅ Force push blocked
- ✅ Branch deletion blocked
- ✅ Admin enforcement enabled

**Staging Branch Protection:**
- ✅ Status checks required (tests must pass)
- ✅ Force push blocked
- ⚠️ Direct pushes allowed (for faster iteration)
- ⚠️ No review required (development branch)

### 🚨 **Emergency Procedures**

**For Critical Hotfixes:**
1. Create hotfix branch from main (admin override required)
2. Make minimal fix with comprehensive tests
3. Create PR directly to main (requires admin approval)
4. After merge, sync staging immediately

**Admin Override Process:**
- Only for critical production issues
- Requires documentation in PR comments
- Must be followed by immediate staging sync
- Triggers post-incident review

### 🎯 **Success Criteria for Code Assistants**

Your changes are ready for production when:
- ✅ All 202+ tests pass across Python 3.8-3.12
- ✅ Security scans show no new vulnerabilities  
- ✅ Integration tests verify end-to-end functionality
- ✅ Build process completes successfully
- ✅ Branch source validation passes
- ✅ Code review approval received
- ✅ All PR conversations resolved

**Validation Command:**
```bash
# Verify everything is ready
uv run pytest tests/ --cov=src --cov-report=term-missing
uv run flake8 src/ --count --statistics
uv run bandit -r src/ -f json
gh pr checks $PR_NUMBER --json state,conclusion
```

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

> **⚠️ IMPORTANT**: All changes must follow the [Branch Protection & Workflow](#branch-protection--workflow) rules above. Feature branches must merge to staging first, then staging merges to main.

### Branch Naming Convention
- Features: `feature/description-of-feature`
- Bug fixes: `fix/description-of-fix`
- Documentation: `docs/description-of-change`
- Refactoring: `refactor/description-of-change`
- Web interface: `web/description-of-change`
- Advanced tools: `advanced/description-of-change`

### Required Workflow Steps
1. **Start from staging**: `git checkout staging && git pull origin staging`
2. **Create feature branch**: `git checkout -b feature/your-change`
3. **Make changes and test**: Ensure all 202+ tests pass
4. **Push to feature branch**: `git push origin feature/your-change`
5. **Create PR to staging**: `gh pr create --base staging`
6. **After staging merge**: Create PR from staging to main

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

> **🔒 CRITICAL**: All PRs must comply with [Branch Protection Rules](#branch-protection--workflow). PRs to main are only allowed from staging branch.

### Pull Request Process
1. **Follow branch protection workflow** (feature → staging → main)
2. **Ensure all tests pass locally** (202+ tests across Python 3.8-3.12)
3. **Update documentation** if needed
4. **Add/update tests** for your changes
5. **Run linting and type checking** (must pass flake8, mypy)
6. **Test web interface** if UI changes made
7. **Create PR to staging first** (never directly to main from feature branch)
8. **Wait for all 9 status checks** to pass
9. **Get required review approval** (for main branch PRs)
10. **Address feedback** and resolve conversations

### Automated Validation
Every PR triggers these **mandatory checks**:
- ✅ Python 3.8, 3.9, 3.10, 3.11, 3.12 test suites
- ✅ Security vulnerability scanning
- ✅ Integration testing with real data
- ✅ Package build verification
- ✅ Branch source validation (staging-only for main)

**All checks must pass before merge is allowed.**

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
