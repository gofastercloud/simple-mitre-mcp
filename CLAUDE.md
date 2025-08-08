# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the multi-layered cybersecurity threat intelligence platform in this repository.

## 🚨 CRITICAL WORKFLOW REQUIREMENTS

**BEFORE making ANY code changes, you MUST:**

1. **Check current branch**: `git branch --show-current`
2. **Switch to staging if needed**: `git checkout staging && git pull origin staging`
3. **Create feature branch IMMEDIATELY**: `git checkout -b feature/$(date +%s)-task-name`
4. **Verify you're on feature branch**: `git branch --show-current`
5. **Test before changes**: `uv run pytest tests/ -x --tb=short`

**⚠️ NEVER make changes on staging or main branches directly!**

## Multi-Layer Architecture Overview

This project implements a comprehensive cybersecurity threat intelligence platform with clean separation of concerns:

```
AI Assistants → MCP Server (Pure AI Integration)
Web Browsers → Flask Web App (Web + Graph Visualization)
CLI Users → CLI Tool (Automation & Scripting)
                ↓
        Middleware APIs (Business Logic)
                ↓
        Data Layer (STIX + Configuration)
```

### Component-Specific Commands

#### Data Layer Development
```bash
# Test data layer components
uv run pytest tests/data/ -v

# Start with data layer changes first
# All components depend on this foundation
```

#### MCP Server Development (Pure AI Integration)
```bash
# Test MCP server (NO web dependencies)
uv run pytest tests/mcp_server/ -v

# Start MCP server for AI assistants
uv run python src/mcp_server/main_stdio.py  # STDIO transport
uv run python src/mcp_server/main_http.py   # HTTP transport
```

#### Flask Web Application Development
```bash
# Test Flask web app
uv run pytest tests/web_app/ -v

# Start Flask development server
uv run python src/web_app/app.py

# Access web interface at http://localhost:8000
```

#### CLI Development
```bash
# Test CLI components
uv run pytest tests/cli/ -v

# Run CLI commands
uv run python src/cli/main.py --help
uv run python src/cli/main.py search "technique name"
```

#### Middleware Development
```bash
# Test middleware APIs
uv run pytest tests/middleware/ -v

# Test middleware integration
uv run pytest tests/integration/ -v
```

## Development Principles

### Multi-Layer Development Approach
- **Data Layer First**: Always implement data layer changes before higher layers
- **Component Independence**: Each layer can be developed and tested independently
- **Clear API Contracts**: Well-defined interfaces between middleware and consumer layers
- **Separation of Concerns**: Each component has distinct responsibilities

### Component-Specific Principles

#### Data Layer (`src/data/`)
- **STIX2 Library Integration**: Use official stix2 library for all threat intelligence parsing
- **Configuration-Driven**: Support multiple frameworks through YAML configuration
- **Caching Strategy**: Implement efficient data caching for performance
- **Framework Agnostic**: Support any STIX-compatible security framework

#### MCP Server Layer (`src/mcp_server/`)
- **Pure AI Integration**: NO web dependencies or HTTP serving logic
- **Official FastMCP**: Use only official MCP protocol implementation
- **8 Specialized Tools**: Maintain focus on threat intelligence analysis
- **Transport Flexibility**: Support both STDIO and HTTP transports for different AI clients

#### Middleware Layer (`src/middleware/`)
- **Business Logic Only**: Complex analysis operations and data transformation
- **Graph Data Structures**: Create visualization-ready data for web components
- **Query Optimization**: Advanced query processing and filtering
- **Performance Focus**: Caching and optimization for high-throughput scenarios

#### Flask Web App (`src/web_app/`)
- **Modern Flask Patterns**: Use Flask application factory and blueprints
- **REST API Design**: Clean, RESTful endpoints for web clients
- **Graph Visualization**: Cytoscape.js integration for interactive network visualization
- **Authentication Ready**: Structure for future authentication and authorization

#### CLI Layer (`src/cli/`)
- **Rich Output**: Use Rich library for enhanced terminal experience
- **Automation Focus**: Design for scripting and CI/CD integration
- **Command Structure**: Logical command grouping and clear help documentation
- **Export Capabilities**: Support multiple output formats for external integration

### Testing Standards
- **Component-Specific Testing**: Each layer has dedicated test directories
- **Integration Testing**: Test component interactions in `tests/integration/`
- **Test Coverage Target**: 400+ comprehensive tests across all components
- **Layer Isolation**: Test each component independently before integration testing

### Configuration Architecture
- **Centralized Configuration**: Shared configuration management across all components
- **Component-Specific Settings**: Individual configuration for each layer
- **Environment Overrides**: Environment variables for deployment-specific settings
- **Framework Support**: Configuration-driven support for multiple threat intelligence frameworks

## Task Completion Workflow (MANDATORY)

**CRITICAL: After completing each individual task, you MUST:**

1. **Test affected components**: 
   ```bash
   # Test specific component
   uv run pytest tests/[component]/ -x --tb=short
   
   # Test integration if multiple components affected
   uv run pytest tests/integration/ -x --tb=short
   
   # Full test suite for major changes
   uv run pytest tests/ -x --tb=short
   ```

2. **Code quality checks**: `uv run black . && uv run flake8 .` (must pass)

3. **Commit immediately with detailed message**:
   ```bash
   git add .
   git -c core.pager=cat commit -m "feat: [component] - [task description]
   
   - Detailed bullet points of what was implemented
   - Component(s) affected: [data/mcp_server/middleware/web_app/cli]
   - Reference to requirements satisfied (e.g., Requirements: 2.1, 4.1)
   - Any important technical details
   - Task completion confirmation"
   ```

4. **Push to remote immediately**: `git push origin [current-feature-branch]`
5. **Update task status** to completed using TodoWrite tool
6. **VERIFY commit succeeded**: `git log --oneline -1`
7. **VERIFY push succeeded**: `git status`

## Component Dependencies and Development Order

### Recommended Development Sequence
1. **Data Layer** - Foundation for all other components
2. **Middleware APIs** - Business logic that higher layers consume
3. **MCP Server** - Pure AI integration (independent of web)
4. **Flask Web App** - Web interface and REST APIs
5. **CLI Tool** - Command-line automation (can be developed in parallel with web)

### Inter-Component Dependencies
- **All components depend on Data Layer**
- **Web App and CLI consume Middleware APIs**
- **MCP Server is independent** (only uses Data Layer directly)
- **Integration tests verify component interaction**

## Architecture Guidelines

### What Goes Where
- **Data Layer**: STIX parsing, configuration, caching, data models
- **MCP Server**: FastMCP tools, AI assistant integration, MCP protocol
- **Middleware**: Graph builders, query engines, threat analysis, business logic
- **Flask Web App**: REST APIs, web serving, authentication, static files
- **CLI**: Command definitions, Rich output, automation interfaces

### Common Mistakes to Avoid
- **Mixing responsibilities**: Keep components focused on their specific role
- **Web dependencies in MCP server**: MCP server must remain pure for AI integration
- **Business logic in web layer**: Complex logic belongs in middleware
- **Direct data access**: Higher layers should use middleware APIs when possible
- **Configuration duplication**: Use centralized configuration management

## Project Specifications and Tasks

### Source of Truth for Project Management
**IMPORTANT: All project specifications, requirements, designs, and task lists are maintained in the `.kiro/` directory.**
- **Task Lists**: Check `.kiro/specs/[project-name]/tasks.md` for current task status
- **Requirements**: Check `.kiro/specs/[project-name]/requirements.md` for detailed requirements
- **Design Documents**: Check `.kiro/specs/[project-name]/design.md` for technical specifications
- **DO NOT maintain duplicate task information in this CLAUDE.md file**
- **Always reference .kiro as the authoritative source for project specifications**

### Current Project Status
This project is transitioning to a multi-layered architecture:
- 🔄 **Architecture Refactor**: Migrating from monolithic to component-based design
- ✅ **Data Layer**: Existing STIX2 library integration and data loading
- 🔄 **Component Separation**: Breaking apart mixed responsibilities into focused layers

## Branch Protection Rules & Contribution Guidelines

### Mandatory Workflow Pattern
- **feature → staging → main** (strictly enforced by GitHub branch protection)
- All PRs must target staging first, never main directly
- Component-specific testing must pass
- Integration testing for multi-component changes
- Code formatting (Black) and linting (Flake8) required

### Pre-Work Checklist (CRITICAL)
**BEFORE making ANY code changes:**
1. `git status && git branch --show-current` (verify current state)
2. `git checkout staging && git pull origin staging` (ensure on staging)
3. `git checkout -b feature/$(date +%s)-task-name` (create feature branch)
4. `git branch --show-current` (confirm on feature branch)
5. `uv run pytest tests/ -x --tb=short` (verify tests pass before changes)

### Component-Specific Development Flow
```bash
# Complete multi-component development cycle
git checkout staging && git pull origin staging
git checkout -b feature/$(date +%s)-your-change

# Make changes following layer dependencies:
# 1. Data layer changes first
# 2. Middleware changes second  
# 3. Consumer layer changes (MCP/Web/CLI) last

# Test each component as you go
uv run pytest tests/data/ -x --tb=short
uv run pytest tests/middleware/ -x --tb=short
uv run pytest tests/[affected-components]/ -x --tb=short

# Test integration for multi-component changes
uv run pytest tests/integration/ -x --tb=short

# Code quality
uv run black . && uv run flake8 .

# Commit and push
git add . && git -c core.pager=cat commit -m "feat: [component] - description"
git push origin feature/$(date +%s)-your-change

# Create PR to staging
gh pr create --base staging --title "Change" --body "Description"
```

**⚠️ Use `git -c core.pager=cat commit` to avoid terminal pager issues!**