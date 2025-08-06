# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL WORKFLOW REQUIREMENTS

**BEFORE making ANY code changes, you MUST:**

1. **Check current branch**: `git branch --show-current`
2. **Switch to staging if needed**: `git checkout staging && git pull origin staging`
3. **Create feature branch IMMEDIATELY**: `git checkout -b feature/$(date +%s)-task-name`
4. **Verify you're on feature branch**: `git branch --show-current`
5. **Test before changes**: `uv run pytest tests/ -x --tb=short`

**⚠️ NEVER make changes on staging or main branches directly!**

## Commands

### Development Environment
- Install dependencies: `uv sync`
- Start web interface: `uv run start_explorer.py` (recommended for interactive testing)
- Start MCP server: `uv run main.py` (for AI assistant integration)
- Start HTTP API server: `uv run http_proxy.py`

### Testing (REQUIRED before any commit)
- Run all tests: `uv run pytest tests/ -x --tb=short`
- Run with coverage: `uv run pytest tests/ --cov=src --cov-report=term-missing`
- Run specific test: `uv run pytest tests/test_mcp_server.py -v`

### Code Quality (REQUIRED before any commit)
- Format code: `uv run black .`
- Lint code: `uv run flake8 .`
- Type checking: `uv run mypy src/`

### Task Completion Workflow (MANDATORY)
**CRITICAL: After completing each individual task, you MUST:**

1. **Run all tests**: `uv run pytest tests/ -x --tb=short` (202+ tests must pass)
2. **Code quality checks**: `uv run black . && uv run flake8 .` (must pass)
3. **Commit immediately with detailed message**:
   ```bash
   git add .
   git -c core.pager=cat commit -m "feat: [task description]
   
   - Detailed bullet points of what was implemented
   - Reference to requirements satisfied (e.g., Requirements: 2.1, 4.1)
   - Any important technical details
   - Task completion confirmation"
   ```
4. **Push to remote immediately**: `git push origin [current-feature-branch]`
5. **Update task status** to completed using TodoWrite tool
6. **VERIFY commit succeeded**: `git log --oneline -1` (confirm latest commit exists)
7. **VERIFY push succeeded**: `git status` (should show "up to date with origin")
8. **Do NOT proceed to next task** until current work is committed, pushed, and verified

**⚠️ MANDATORY VERIFICATION COMMANDS:**
```bash
# After each task completion, run these commands in sequence:
git add .
git -c core.pager=cat commit -m "feat: [description]"
git push origin $(git branch --show-current)
git log --oneline -1  # Verify commit exists
git status            # Verify push succeeded
```

**⚠️ Use `git -c core.pager=cat commit` to avoid terminal pager issues!**

## Development Principles

### Library-First Development
- **ALWAYS use official libraries** for well-known protocols (MCP, STIX2, FastMCP)
- **Battle-tested libraries over custom implementations**
- **Security-focused libraries** for parsing external data
- Current key libraries: `mcp`, `stix2`, `requests`, `pyyaml`, `pytest`

### Testing Standards
- **ALL test files MUST be in `tests/` directory** - never create tests elsewhere
- **202+ tests must pass** across Python 3.12-3.13
- Follow naming: `test_<module_name>.py` for testing `src/<module_name>.py`
- Comprehensive unit tests for all functions and error scenarios

### Configuration-Driven Architecture
- **No hardcoded framework logic** - use config files for entity types, schemas, tools
- **Extensible design** - supports any structured security framework, not just MITRE ATT&CK
- **Environment variable overrides** for deployment flexibility

### Extensibility & Reusability Principles
- **Framework-agnostic architecture** - designed to support any structured security framework
- **Multi-framework support** - while built for MITRE ATT&CK, supports other threat intelligence formats
- **Standards-compliant** - uses official MCP protocol and STIX parsing libraries
- **Pluggable data sources** - configuration-driven data source definitions
- **Modular tool system** - easy addition of new MCP tools without core changes

## Architecture Overview

This is a MITRE ATT&CK MCP (Model Context Protocol) server that provides structured access to the MITRE ATT&CK framework through multiple interfaces:

### Core Components
- **FastMCP Server** (`src/mcp_server.py`): Main MCP protocol implementation with 8 tools
- **HTTP Proxy Server** (`http_proxy.py`): Web interface and REST API access layer
- **Data Loader** (`src/data_loader.py`): Downloads and processes MITRE ATT&CK STIX data using official stix2 library
- **STIX Parser** (`src/parsers/stix_parser.py`): Parses STIX 2.x objects into structured data
- **Configuration System** (`src/config_loader.py`): YAML-based configuration with environment overrides

### 8 MCP Tools
**Basic Analysis Tools (5):**
- search_attack, get_technique, list_tactics, get_group_techniques, get_technique_mitigations

**Advanced Threat Modeling Tools (3):**
- build_attack_path, analyze_coverage_gaps, detect_technique_relationships

### Data Flow
1. Data Loader fetches MITRE ATT&CK STIX bundle from official repository
2. STIX Parser processes attack-patterns, courses-of-action, intrusion-sets, and relationships
3. MCP Server provides 8 tools for threat intelligence analysis
4. Web interface and HTTP proxy provide browser-based access

### Access Methods
- **MCP Protocol**: Direct integration with AI assistants via stdio transport
- **Web Interface**: Interactive HTML interface at `http://localhost:8000` via HTTP proxy
- **HTTP/JSON API**: RESTful access for custom integrations

### Configuration
- **Environment Variables**: MCP_HTTP_HOST, MCP_HTTP_PORT for HTTP server configuration
- **YAML Config Files**: `config/data_sources.yaml`, `config/entity_schemas.yaml`, `config/tools.yaml`
- Uses UV package manager for dependency management

## Current Project Status

### Active Specifications
**Web Explorer Improvements:**
- Task 9: Create tools section with enhanced forms (PENDING)
- Task 10: Implement enhanced results display system (PENDING)

**STIX2 Library Refactor (Completed tasks 1-8, remaining):**
- Task 11: Update type hints and improve code quality
- Task 12: Remove deprecated custom parsing logic
- Task 13: Add future extensibility examples and documentation
- Task 14: Integration testing with all MCP tools
- Task 15: Final test cleanup and deprecated test removal

### Key Implementation Details
- Uses official `stix2` library for secure STIX data parsing
- Maintains comprehensive test coverage (202+ tests)
- Configuration-driven design supports extensibility to other security frameworks
- In-memory caching for fast query response
- STIX relationship graph analysis for advanced threat modeling

## Branch Protection Rules & Contribution Guidelines

### Mandatory Workflow Pattern
- **feature → staging → main** (strictly enforced by GitHub branch protection)
- All PRs must target staging first, never main directly
- 202+ tests must pass across Python 3.12-3.13
- Code formatting (Black) and linting (Flake8) required
- Security scanning (Bandit + Safety) must pass
- No direct pushes to protected branches (staging/main)

### Pre-Work Checklist (CRITICAL)
**BEFORE making ANY code changes:**
1. `git status && git branch --show-current` (verify current state)
2. `git checkout staging && git pull origin staging` (ensure on staging)
3. `git checkout -b feature/$(date +%s)-task-name` (create feature branch)
4. `git branch --show-current` (confirm on feature branch)
5. `uv run pytest tests/ -x --tb=short` (verify tests pass before changes)

### Daily Development Commands
```bash
# Complete development cycle
git checkout staging && git pull origin staging
git checkout -b feature/$(date +%s)-your-change
# Make changes
uv run pytest tests/ -x --tb=short
uv run black . && uv run flake8 .
git add . && git -c core.pager=cat commit -m "feat: description"
git push origin feature/$(date +%s)-your-change
gh pr create --base staging --title "Change" --body "Description"
```

### Common Mistakes to Avoid
- Making changes on staging/main directly
- Forgetting to check current branch before starting
- Starting work without creating feature branch
- Not committing after each task completion
- Using `git commit` without pager config (causes terminal issues)
- Creating PRs to main instead of staging

### Status Checks (All Must Pass)
1. **Python 3.12-3.13 Tests** - All 202+ tests
2. **Security Scanning** - Bandit + Safety vulnerability checks  
3. **Integration Testing** - End-to-end functionality verification
4. **Build Verification** - Package building validation
5. **Branch Source Validation** - Enforces staging workflow

### Troubleshooting
```bash
# If on wrong branch with changes
git stash push -m "WIP: work in progress"
git checkout staging && git pull origin staging
git checkout -b feature/$(date +%s)-fix
git stash pop

# Check test failures
uv run pytest tests/ -v --tb=short

# Fix formatting/linting
uv run black . && uv run flake8 .

# Check PR status
gh pr checks $PR_NUMBER
```