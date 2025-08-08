# Makefile for optimized test execution and development workflow
# Provides convenient commands for different test execution scenarios

.PHONY: help test test-fast test-parallel test-full test-category test-benchmark install-deps format lint clean

# Default target
help:
	@echo "Available targets:"
	@echo "  test-fast      - Fast unit tests only (development cycle)"
	@echo "  test-parallel  - Parallel test execution with optimal workers"
	@echo "  test-full      - Full test suite with coverage and timing"
	@echo "  test-category  - Run specific test category (specify CATEGORY=unit|integration|etc)"
	@echo "  test-benchmark - Run performance benchmarks"
	@echo "  install-deps   - Install all dependencies including test optimization tools"
	@echo "  format         - Format code with black"
	@echo "  lint           - Run linting with flake8"
	@echo "  clean          - Clean temporary files and caches"

# Install dependencies including test optimization tools
install-deps:
	uv sync
	@echo "Dependencies installed successfully"

# Fast development cycle - unit tests only, no coverage
test-fast:
	@echo "Running fast unit tests..."
	uv run pytest tests/unit/ -m "not slow" --maxfail=5 --tb=short -q

# Parallel test execution with optimal worker count
test-parallel:
	@echo "Running tests in parallel..."
	python scripts/run_tests_optimized.py --mode parallel --timing-report

# Full test suite with all optimizations
test-full:
	@echo "Running full test suite..."
	python scripts/run_tests_optimized.py --mode full

# Category-specific tests (usage: make test-category CATEGORY=unit)
test-category:
	@if [ -z "$(CATEGORY)" ]; then \
		echo "Error: CATEGORY must be specified. Usage: make test-category CATEGORY=unit"; \
		echo "Available categories: unit, integration, performance, compatibility, deployment, e2e"; \
		exit 1; \
	fi
	@echo "Running $(CATEGORY) tests..."
	python scripts/run_tests_optimized.py --mode category --category $(CATEGORY) --timing-report

# Performance benchmarks
test-benchmark:
	@echo "Running performance benchmarks..."
	python scripts/run_tests_optimized.py --mode benchmark

# Alternative pytest commands for direct use
test-unit:
	@echo "Running unit tests..."
	uv run pytest tests/unit/ -v --timing-report

test-integration:
	@echo "Running integration tests..."
	uv run pytest tests/integration/ -v --timing-report

test-performance:
	@echo "Running performance tests..."
	uv run pytest tests/performance/ --benchmark --timing-report -v

test-compatibility:
	@echo "Running compatibility tests..."
	uv run pytest tests/compatibility/ -v --timing-report

test-deployment:
	@echo "Running deployment tests..."
	uv run pytest tests/deployment/ -v --timing-report

test-e2e:
	@echo "Running end-to-end tests..."
	uv run pytest tests/e2e/ -v --timing-report

# Parallel execution with specific worker count (usage: make test-workers WORKERS=4)
test-workers:
	@if [ -z "$(WORKERS)" ]; then \
		echo "Error: WORKERS must be specified. Usage: make test-workers WORKERS=4"; \
		exit 1; \
	fi
	@echo "Running tests with $(WORKERS) workers..."
	uv run pytest tests/ -n$(WORKERS) --dist=worksteal --timing-report

# Coverage-focused test run
test-coverage:
	@echo "Running tests with detailed coverage..."
	uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=html:htmlcov --cov-fail-under=90

# Performance regression testing
test-regression:
	@echo "Running performance regression tests..."
	uv run pytest tests/performance/ --benchmark --timing-report --durations=20

# Code formatting
format:
	@echo "Formatting code with black..."
	uv run black .
	@echo "Code formatted successfully"

# Linting
lint:
	@echo "Running linting with flake8..."
	uv run flake8 .
	@echo "Linting completed"

# Type checking
typecheck:
	@echo "Running type checking with mypy..."
	uv run mypy src/
	@echo "Type checking completed"

# Security scanning
security:
	@echo "Running security scans..."
	uv run bandit -r src/
	uv run safety check
	@echo "Security scanning completed"

# Clean temporary files and caches
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/ 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	rm -rf .mypy_cache/ 2>/dev/null || true
	@echo "Cleanup completed"

# Development workflow - format, lint, and test
dev-check: format lint test-fast
	@echo "Development checks completed successfully"

# CI/CD workflow - full validation
ci-check: format lint typecheck security test-full
	@echo "CI/CD checks completed successfully"

# Performance analysis
perf-analysis:
	@echo "Generating performance analysis..."
	uv run pytest tests/ --timing-report --durations=20 --collect-only
	@echo "Performance analysis completed"

# Show test statistics
test-stats:
	@echo "Test suite statistics:"
	@find tests/ -name "test_*.py" | wc -l | xargs echo "Test files:"
	@find tests/ -name "test_*.py" -exec grep -l "def test_" {} \; | xargs grep "def test_" | wc -l | xargs echo "Test functions:"
	@echo "Test categories:"
	@find tests/ -type d -mindepth 1 -maxdepth 1 | sed 's|tests/||' | sort

# Validate test structure
validate-structure:
	@echo "Validating test structure..."
	@python -c "\
import os; \
import sys; \
required_dirs = ['unit', 'integration', 'performance', 'compatibility', 'deployment', 'e2e']; \
missing_dirs = [d for d in required_dirs if not os.path.exists(f'tests/{d}')]; \
print(f'Missing test directories: {missing_dirs}') if missing_dirs else print('Test structure validation passed'); \
sys.exit(1) if missing_dirs else None"