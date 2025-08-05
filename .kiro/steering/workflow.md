# Development Workflow and Contribution Guidelines

> **CRITICAL**: This project has strict branch protection rules and workflow requirements. ALL code changes must follow the patterns defined in CONTRIBUTING.md.

## Mandatory Reading

**BEFORE making any changes, you MUST read and follow:**
- `CONTRIBUTING.md` - Complete workflow guide for both humans and AI assistants
- Focus on the "🤖 For Agentic Code Assistants" section for AI-specific guidance

## 🔍 Pre-Work Checklist for AI Assistants

**BEFORE making ANY code changes, complete this checklist:**

- [ ] Check current branch: `git branch --show-current`
- [ ] Ensure on staging: `git checkout staging && git pull origin staging`
- [ ] Create feature branch: `git checkout -b feature/$(date +%s)-task-name`
- [ ] Verify branch created: `git branch --show-current`
- [ ] Run initial tests: `uv run pytest tests/ -x --tb=short`

**Only after completing this checklist should you begin making code changes.**

## Branch Protection Workflow (STRICTLY ENFORCED)

### Required Pattern
```
feature/branch → staging → main
     ↓              ↓        ↓
   tests pass   tests pass  all checks + review
```

### CRITICAL Commands for AI Assistants

> **⚠️ MANDATORY FIRST STEP**: Always check current branch and create feature branch BEFORE making any code changes!

```bash
# 0. CHECK CURRENT BRANCH FIRST (CRITICAL!)
git branch --show-current
# If not on staging, switch immediately:
git checkout staging && git pull origin staging

# 1. Create feature branch with timestamp BEFORE any changes
git checkout -b feature/$(date +%s)-your-change

# 2. Make changes and test locally (REQUIRED)
uv run pytest tests/ -x --tb=short

# 3. Format and lint code (REQUIRED)
uv run black . && uv run flake8 .

# 4. Commit and push to feature branch (REQUIRED AFTER EACH TASK)
git add . && git -c core.pager=cat commit -m "feat: description"
git push origin feature/$(date +%s)-your-change

# 5. Create PR to staging (NOT main)
gh pr create --base staging --title "Change" --body "Description"
```

### 🔄 Task Completion Workflow (MANDATORY)

**AFTER completing each individual task from a spec:**

1. **Update task status** to completed using taskStatus tool
2. **Run full test suite** to ensure no regressions: `uv run pytest tests/ -x --tb=short`
3. **Commit changes immediately** with detailed message describing what was implemented
4. **Push to remote** to preserve work and enable collaboration
5. **Do NOT proceed to next task** until current task is fully committed

```bash
# Required after each task completion
git add .
git -c core.pager=cat commit -m "feat: [task description]

- Detailed bullet points of what was implemented
- Reference to requirements satisfied
- Any important technical details
- Task completion confirmation"
git push origin [current-feature-branch]
```

> **⚠️ CRITICAL**: Use `git -c core.pager=cat` to avoid terminal pager issues during commits!

### 🚨 Common AI Assistant Mistakes to Avoid:
- **Making changes on staging/main directly** - Always create feature branch first
- **Forgetting to check current branch** - Use `git branch --show-current` before starting
- **Starting work without proper branch setup** - Feature branch must exist before any code changes
- **Not committing after each task** - Each completed task must be committed immediately
- **Using git commit without pager config** - Always use `git -c core.pager=cat commit` to avoid terminal issues
- **Proceeding to next task without committing current work** - Commit and push after each task completion

## UV Package Manager (REQUIRED)

This project uses UV as the package manager. Use these commands:

```bash
# Install dependencies
uv sync

# Add new dependencies
uv add package-name

# Run commands
uv run python script.py
uv run pytest tests/
uv run black .
uv run flake8 .

# Start web interface
uv run start_explorer.py
```

## Testing Requirements (MANDATORY)

### All Changes Must Pass
- **202+ tests** across Python 3.12-3.13
- **Security scanning** (Bandit + Safety)
- **Integration testing** with real data
- **Code formatting** (Black)
- **Linting** (Flake8)

### Test Commands
```bash
# Run all tests (REQUIRED before pushing)
uv run pytest tests/ -x --tb=short

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=term-missing

# Test specific modules
uv run pytest tests/test_mcp_server.py -v
uv run pytest tests/test_build_attack_path.py -v
```

## Project Structure Understanding

### Core Components
- **8 MCP Tools**: 5 basic analysis + 3 advanced threat modeling
- **Web Interface**: Interactive browser-based access
- **HTTP Proxy**: Bridge between web and MCP protocol
- **FastMCP Server**: Official MCP protocol implementation

### Key Files to Understand
- `src/mcp_server.py` - Core MCP server with all 8 tools
- `http_proxy.py` - HTTP proxy for web interface
- `web_explorer.html` - Interactive web interface
- `tests/` - ALL tests must be in this directory

## Blocked Actions (Will Fail)

These actions are automatically blocked by branch protection:

```bash
# ❌ BLOCKED - Direct push to main
git push origin main

# ❌ BLOCKED - PR from feature to main
gh pr create --base main --head feature/branch

# ❌ BLOCKED - Force push to protected branches
git push --force origin main
git push --force origin staging
```

## Success Criteria

Your changes are ready when:
- ✅ All 202+ tests pass across Python 3.12-3.13
- ✅ Security scans show no new vulnerabilities
- ✅ Integration tests verify functionality
- ✅ Code is formatted with Black
- ✅ Linting passes with Flake8
- ✅ PR created to staging (not main)
- ✅ All 9 status checks pass in CI/CD

## Troubleshooting Commands

```bash
# Check test failures
uv run pytest tests/ -v --tb=short

# Fix formatting
uv run black .

# Fix linting
uv run flake8 . --count --statistics

# Update branch
git checkout staging && git pull origin staging
git checkout your-branch && git merge staging

# Check PR status
gh pr checks $PR_NUMBER
```

## Emergency Procedures

For critical issues:
1. Create hotfix branch from main (admin override required)
2. Make minimal fix with tests
3. Create PR directly to main (requires admin approval)
4. Sync staging immediately after merge

## Key Principles

1. **Always read CONTRIBUTING.md first**
2. **Use UV for all package management**
3. **Test locally before pushing**
4. **Follow staging-to-main workflow**
5. **Never bypass branch protection**
6. **All tests must be in tests/ directory**
7. **Use official libraries (MCP, STIX2, etc.)**
8. **Maintain 202+ test coverage**

## Reference Files

- `CONTRIBUTING.md` - Complete workflow guide (READ THIS FIRST)
- `README.md` - Project overview and usage
- `.github/workflows/ci.yml` - CI/CD pipeline
- `.github/workflows/branch-protection.yml` - Branch validation