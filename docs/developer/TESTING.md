# Testing Guide

This guide covers testing practices, running tests, and writing new tests for the MITRE ATT&CK MCP Server.

## Test Overview

The project maintains a comprehensive test suite with **493+ tests** across multiple categories:
- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: Tests for component interactions
- **Performance Tests**: Benchmarks and performance validation
- **Deployment Tests**: Configuration and deployment validation
- **End-to-End Tests**: Complete workflow validation

## Running Tests

### Quick Test Commands

```bash
# Run all tests (recommended for development)
uv run python -m pytest tests/ -x --tb=short

# Run with coverage report
uv run python -m pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
uv run python -m pytest tests/test_mcp_server.py -v

# Run specific test method
uv run python -m pytest tests/test_search_attack.py::TestSearchAttack::test_search_basic -v
```

### Optimized Test Execution

The project includes several optimization features for faster and more efficient test execution:

#### Parallel Test Execution
```bash
# Run tests in parallel with optimal worker count (auto-detected)
uv run pytest tests/ -nauto --dist=worksteal

# Run with specific number of workers
uv run pytest tests/ -n4 --dist=worksteal

# Use the optimized test script
python scripts/run_tests_optimized.py --mode parallel
```

#### Fast Development Cycle
```bash
# Fast unit tests only (development workflow)
make test-fast
# or
python scripts/run_tests_optimized.py --mode fast

# Skip slow tests during development
uv run pytest tests/ -m "not slow" --maxfail=5 --tb=short -q
```

#### Test Execution with Timing Reports
```bash
# Generate detailed timing report
uv run pytest tests/ --timing-report --durations=10

# Full test suite with all optimizations
make test-full
# or
python scripts/run_tests_optimized.py --mode full
```

#### Category-Specific Execution
```bash
# Run specific test categories with optimization
make test-category CATEGORY=unit
make test-category CATEGORY=integration
make test-category CATEGORY=performance

# Using the optimization script
python scripts/run_tests_optimized.py --mode category --category unit --timing-report
```

#### Performance Benchmarks
```bash
# Run performance benchmarks
make test-benchmark
# or
python scripts/run_tests_optimized.py --mode benchmark

# Run with benchmark reporting
uv run pytest tests/performance/ --benchmark --timing-report
```

### Makefile Commands

The project includes a comprehensive Makefile with optimized test commands:

```bash
# Available test commands
make help                    # Show all available commands
make test-fast              # Fast unit tests only
make test-parallel          # Parallel execution with optimal workers
make test-full              # Full test suite with coverage and timing
make test-category CATEGORY=unit  # Run specific category
make test-benchmark         # Performance benchmarks
make test-coverage          # Detailed coverage reporting
make test-regression        # Performance regression testing

# Development workflow commands
make dev-check              # Format, lint, and fast test
make ci-check               # Full CI/CD validation
make perf-analysis          # Performance analysis
make test-stats             # Show test suite statistics
```

### Test Categories

#### Unit Tests (Fast - ~30 seconds)
```bash
# Run only unit tests
uv run python -m pytest tests/unit/ -v

# Run unit tests for specific tools
uv run python -m pytest tests/unit/test_tools/ -v
```

#### Integration Tests (~2 minutes) 
```bash
# Run integration tests
uv run python -m pytest tests/integration/ -v

# Test HTTP interface integration
uv run python -m pytest tests/integration/test_http_interface.py -v
```

#### Performance Tests (~5 minutes)
```bash
# Run performance benchmarks
uv run python -m pytest tests/performance/ -v

# Run performance tests with benchmarks
uv run python -m pytest tests/test_performance_benchmarks.py -v --benchmark-only
```

### Test Markers

Use pytest markers to run specific types of tests:

```bash
# Skip slow tests (development workflow)
uv run python -m pytest -m "not slow"

# Run only fast tests 
uv run python -m pytest -m "fast"

# Run specific categories
uv run python -m pytest -m "unit"
uv run python -m pytest -m "integration" 
uv run python -m pytest -m "performance"
```

## Test Structure

### Directory Organization
```
tests/
├── unit/                    # Unit tests
│   ├── test_mcp_server.py
│   ├── test_data_loader.py
│   ├── test_parsers.py
│   └── test_tools/          # Tool-specific tests
│       ├── test_search_attack.py
│       ├── test_get_technique.py
│       └── ...
├── integration/             # Integration tests
│   ├── test_http_interface.py
│   ├── test_mcp_integration.py
│   └── test_web_interface.py
├── performance/             # Performance tests
│   └── test_performance_benchmarks.py
├── deployment/              # Deployment tests
│   └── test_deployment_validation.py
├── e2e/                     # End-to-end tests
│   └── test_complete_workflows.py
├── conftest.py             # Shared fixtures
├── factories.py            # Test data factories
└── base.py                 # Base test classes
```

### Base Test Classes

```python
# tests/base.py
import pytest
from unittest.mock import MagicMock

class BaseTestCase:
    """Base test class with common utilities."""
    
    @pytest.fixture(autouse=True)
    def setup_logging(self, caplog):
        """Configure test logging."""
        caplog.set_level("INFO")
    
    def assert_valid_mitre_id(self, mitre_id, expected_type="technique"):
        """Validate MITRE ID format."""
        if expected_type == "technique":
            assert mitre_id.startswith("T")
        elif expected_type == "group":
            assert mitre_id.startswith("G")
        elif expected_type == "tactic":
            assert mitre_id.startswith("TA")

class BaseMCPTestCase(BaseTestCase):
    """Base class for MCP tool tests."""
    
    @pytest.fixture
    def mock_data_loader(self):
        """Shared mock data loader fixture."""
        mock_loader = MagicMock()
        # Set up common mock data
        mock_loader.get_cached_data.return_value = {
            "techniques": [
                {"id": "T1055", "name": "Process Injection"},
                {"id": "T1059", "name": "Command and Scripting Interpreter"}
            ],
            "groups": [
                {"id": "G0016", "name": "APT29"},
                {"id": "G0032", "name": "Lazarus Group"}
            ]
        }
        return mock_loader
```

### Test Data Factories

```python
# tests/factories.py
class TestDataFactory:
    """Factory for creating consistent test data."""
    
    @staticmethod
    def create_sample_technique(technique_id="T1055", **overrides):
        """Create sample technique data."""
        base_technique = {
            "id": technique_id,
            "name": "Process Injection",
            "description": "Adversaries may inject code into processes...",
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": technique_id,
                    "url": f"https://attack.mitre.org/techniques/{technique_id}/"
                }
            ]
        }
        base_technique.update(overrides)
        return base_technique
    
    @staticmethod  
    def create_sample_group(group_id="G0016", **overrides):
        """Create sample group data."""
        base_group = {
            "id": group_id,
            "name": "APT29",
            "aliases": ["Cozy Bear", "The Dukes"],
            "description": "APT29 is a threat group...",
            "external_references": [
                {
                    "source_name": "mitre-attack", 
                    "external_id": group_id,
                    "url": f"https://attack.mitre.org/groups/{group_id}/"
                }
            ]
        }
        base_group.update(overrides)
        return base_group
```

## Writing New Tests

### Unit Test Example

```python
# tests/unit/test_tools/test_new_tool.py
import pytest
from unittest.mock import MagicMock, patch
from tests.base import BaseMCPTestCase
from tests.factories import TestDataFactory

class TestNewTool(BaseMCPTestCase):
    """Test cases for new tool functionality."""
    
    @pytest.fixture
    def tool_instance(self, mock_data_loader):
        """Create tool instance with mock data."""
        from src.tools.new_tool import NewTool
        return NewTool(mock_data_loader)
    
    def test_new_tool_basic_functionality(self, tool_instance):
        """Test basic tool operation."""
        # Arrange
        test_input = "test_query"
        expected_result = "expected_output"
        
        # Act
        result = tool_instance.execute(test_input)
        
        # Assert
        assert result is not None
        assert "expected_content" in result
    
    def test_new_tool_with_invalid_input(self, tool_instance):
        """Test tool handles invalid input gracefully."""
        # Arrange
        invalid_input = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid input"):
            tool_instance.execute(invalid_input)
    
    @pytest.mark.parametrize("input_value,expected", [
        ("input1", "output1"),
        ("input2", "output2"),
        ("input3", "output3"),
    ])
    def test_new_tool_parametrized(self, tool_instance, input_value, expected):
        """Test tool with various inputs."""
        result = tool_instance.execute(input_value)
        assert expected in result
```

### Integration Test Example

```python
# tests/integration/test_new_integration.py
import pytest
import asyncio
from aiohttp.test_utils import AioHTTPTestCase
from tests.base import BaseTestCase

class TestNewIntegration(AioHTTPTestCase, BaseTestCase):
    """Integration tests for new functionality."""
    
    async def get_application(self):
        """Create test application."""
        from src.http_proxy import HTTPProxy
        mock_mcp_server = self.create_mock_mcp_server()
        proxy = HTTPProxy(mock_mcp_server)
        return proxy.app
    
    def create_mock_mcp_server(self):
        """Create mock MCP server for testing."""
        mock_server = MagicMock()
        mock_server.call_tool = AsyncMock(return_value=(
            [MagicMock(text="Test result")], None
        ))
        return mock_server
    
    async def test_new_endpoint_integration(self):
        """Test new endpoint integration."""
        resp = await self.client.request("GET", "/new_endpoint")
        self.assertEqual(resp.status, 200)
        
        data = await resp.json()
        self.assertIn("expected_field", data)
```

### Performance Test Example

```python
# tests/performance/test_new_performance.py
import pytest
import time
from tests.base import BaseMCPTestCase

class TestNewPerformance(BaseMCPTestCase):
    """Performance tests for new functionality."""
    
    @pytest.mark.slow
    def test_new_tool_performance(self, mock_data_loader):
        """Test tool performance meets requirements."""
        from src.tools.new_tool import NewTool
        tool = NewTool(mock_data_loader)
        
        # Warm up
        tool.execute("warmup")
        
        # Measure performance
        start_time = time.time()
        for _ in range(100):
            tool.execute("test_query")
        end_time = time.time()
        
        # Assert performance requirements
        avg_time = (end_time - start_time) / 100
        assert avg_time < 0.1, f"Tool too slow: {avg_time:.3f}s per call"
    
    @pytest.mark.benchmark
    def test_new_tool_benchmark(self, benchmark, mock_data_loader):
        """Benchmark tool performance."""
        from src.tools.new_tool import NewTool
        tool = NewTool(mock_data_loader)
        
        result = benchmark(tool.execute, "benchmark_query")
        assert result is not None
```

## Test Configuration

### pytest.ini Configuration
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --tb=short
    --no-cov-on-fail
    --cov-fail-under=90
    --timeout=300
    --timeout-method=thread
    --benchmark-skip
    --durations=10
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (moderate speed)
    performance: Performance and benchmark tests (slow)
    slow: Tests that take more than 5 seconds
    fast: Tests that complete in under 1 second
    benchmark: Benchmark tests (requires pytest-benchmark)
    order: Test execution order priority
```

### Test Execution Optimization

#### Parallel Execution Configuration
The project uses `pytest-xdist` for parallel test execution with the following optimizations:

- **Worker Distribution**: Uses `worksteal` strategy for dynamic load balancing
- **Optimal Worker Count**: Auto-detects based on CPU cores (75% of available CPUs, max 8)
- **Fixture Scoping**: Optimized fixture scopes to reduce setup/teardown overhead

#### Performance Monitoring
Test execution includes comprehensive performance monitoring:

```python
# Performance thresholds by category
PERFORMANCE_THRESHOLDS = {
    "unit": {"max": 1.0, "warning": 0.5, "target": 0.1},
    "integration": {"max": 10.0, "warning": 5.0, "target": 2.0},
    "performance": {"max": 60.0, "warning": 30.0, "target": 15.0},
    "e2e": {"max": 120.0, "warning": 60.0, "target": 30.0}
}
```

#### Test Ordering Optimization
Tests are automatically ordered for optimal execution flow:

1. **Unit tests** (fastest, run first)
2. **Integration tests** (moderate speed)
3. **Deployment tests** (setup-heavy)
4. **Compatibility tests** (environment-specific)
5. **Performance tests** (resource-intensive)
6. **End-to-end tests** (slowest, run last)

#### Fixture Optimization
Fixtures are scoped for maximum efficiency:

```python
# Session-scoped (created once per test session)
@pytest.fixture(scope="session")
def test_data_factory():
    return TestDataFactory()

# Module-scoped (created once per test module)
@pytest.fixture(scope="module")
def sample_technique():
    return TestDataFactory.create_sample_technique()

# Function-scoped (created for each test)
@pytest.fixture
def temp_config_file():
    # Temporary files that need cleanup
    pass
```

### Coverage Configuration
```ini
[tool:coverage.run]
source = src
omit = 
    tests/*
    .venv/*
    */venv/*

[tool:coverage.report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## Mocking Best Practices

### Mock External Dependencies
```python
@patch('src.data_loader.requests.get')
def test_data_loading_with_network_mock(self, mock_get):
    """Test data loading with mocked network requests."""
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = {"objects": []}
    mock_get.return_value = mock_response
    
    # Act
    from src.data_loader import DataLoader
    loader = DataLoader()
    result = loader.load_data_source("test_source")
    
    # Assert
    mock_get.assert_called_once()
    assert result is not None
```

### Mock Async Operations
```python
@pytest.mark.asyncio
async def test_async_tool_execution(self):
    """Test async tool execution."""
    # Arrange
    mock_server = MagicMock()
    mock_server.call_tool = AsyncMock(return_value=(
        [MagicMock(text="Async result")], None
    ))
    
    # Act
    result = await mock_server.call_tool("test_tool", {})
    
    # Assert
    assert result[0][0].text == "Async result"
```

## Test Data Management

### Test Data Location
```
tests/
├── data/                    # Test data files
│   ├── sample_stix.json    # Sample STIX data
│   ├── test_techniques.yaml # Test technique data
│   └── mock_responses/      # Mock HTTP responses
│       ├── mitre_data.json
│       └── api_responses.json
└── fixtures/               # Pytest fixtures
    ├── __init__.py
    └── data_fixtures.py
```

### Loading Test Data
```python
import json
from pathlib import Path

def load_test_data(filename):
    """Load test data from tests/data directory."""
    test_data_dir = Path(__file__).parent / "data"
    with open(test_data_dir / filename) as f:
        return json.load(f)

@pytest.fixture
def sample_mitre_data():
    """Load sample MITRE data for testing."""
    return load_test_data("sample_mitre.json")
```

## Continuous Integration

### GitHub Actions Testing
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install UV
      uses: astral-sh/setup-uv@v3
    
    - name: Install dependencies
      run: uv sync
    
    - name: Run tests
      run: uv run python -m pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

## Debugging Tests

### Running Tests in Debug Mode
```bash
# Run with verbose output
uv run python -m pytest tests/test_failing.py -v -s

# Run with PDB debugger
uv run python -m pytest tests/test_failing.py --pdb

# Run with print statements
uv run python -m pytest tests/test_failing.py -s --capture=no
```

### Common Debugging Techniques
```python
def test_debug_example(caplog):
    """Example test with debugging helpers."""
    import logging
    
    # Enable debug logging
    caplog.set_level(logging.DEBUG)
    
    # Your test code here
    result = some_function()
    
    # Check logs
    assert "Expected log message" in caplog.text
    
    # Debug print (use -s flag to see output)
    print(f"Debug result: {result}")
```

## Test Maintenance

### Regular Test Maintenance Tasks
1. **Remove obsolete tests** when functionality changes
2. **Update mock data** to match current MITRE ATT&CK structure
3. **Review performance tests** to ensure thresholds are appropriate
4. **Check test coverage** and add tests for uncovered code
5. **Update documentation** when test structure changes

### Test Quality Checklist
- [ ] Tests are independent (no order dependencies)
- [ ] Tests use appropriate fixtures and factories
- [ ] Tests have clear arrange/act/assert structure
- [ ] Tests include both positive and negative cases
- [ ] Performance tests have reasonable thresholds
- [ ] Integration tests cover key workflows
- [ ] Tests are properly categorized with markers

## Test Execution Optimization Tools

### Optimization Script (`scripts/run_tests_optimized.py`)

The project includes a comprehensive test execution optimization script with multiple modes:

```bash
# Fast development cycle (unit tests only)
python scripts/run_tests_optimized.py --mode fast

# Parallel execution with auto-detected workers
python scripts/run_tests_optimized.py --mode parallel

# Full test suite with all optimizations
python scripts/run_tests_optimized.py --mode full

# Category-specific execution
python scripts/run_tests_optimized.py --mode category --category unit

# Performance benchmarks
python scripts/run_tests_optimized.py --mode benchmark

# Custom worker count
python scripts/run_tests_optimized.py --mode parallel --workers 4

# With timing reports
python scripts/run_tests_optimized.py --mode parallel --timing-report

# With coverage reporting
python scripts/run_tests_optimized.py --mode parallel --coverage
```

### Performance Monitoring and Reporting

#### Timing Reports
The test suite generates detailed timing reports showing:

- **Category Summary**: Test count, total time, and average time per category
- **Slowest Tests**: Top 20 slowest tests with durations
- **Performance Recommendations**: Optimization suggestions based on execution patterns
- **Parallel Speedup Estimates**: Potential performance gains from parallel execution

Example timing report output:
```
================================================================================
TEST EXECUTION TIMING REPORT
================================================================================

CATEGORY SUMMARY:
------------------------------------------------------------
Category        Count    Total (s)    Avg (s)   
------------------------------------------------------------
unit            128      0.161        0.001     
integration     45       2.340        0.052     
performance     12       15.670       1.306     

SLOWEST TESTS (Top 20):
--------------------------------------------------------------------------------
Duration (s) Category     Test
--------------------------------------------------------------------------------
5.234        performance  test_large_dataset_processing
2.156        integration  test_full_workflow_integration
1.890        performance  test_concurrent_operations

PERFORMANCE RECOMMENDATIONS:
----------------------------------------
• 3 tests take >5 seconds - consider optimization
• Total execution time: 18.171 seconds
• Estimated parallel speedup: 3.2x (with unlimited workers)
================================================================================
```

#### Performance Regression Detection
The system automatically detects performance regressions by:

- Tracking historical test execution times
- Comparing current runs against baseline performance
- Alerting when tests exceed 50% of historical average
- Providing detailed regression analysis

### Test Dependencies and Requirements

#### Required Packages for Optimization
```toml
# pyproject.toml dev-dependencies
[tool.uv]
dev-dependencies = [
    "pytest-xdist>=3.5.0",      # Parallel execution
    "pytest-benchmark>=4.0.0",   # Performance benchmarking
    "pytest-timeout>=2.3.1",     # Test timeouts
    "pytest-order>=1.2.0",       # Test ordering
    # ... other dependencies
]
```

#### Environment Variables
```bash
# Parallel execution configuration
export PYTEST_XDIST_WORKER_COUNT=4    # Override auto-detection
export PYTEST_TIMEOUT=300             # Global test timeout

# Performance monitoring
export PYTEST_BENCHMARK_DISABLE=1     # Disable benchmarks in parallel mode
export PYTEST_TIMING_REPORT=1         # Enable timing reports
```

## Advanced Testing

### Property-Based Testing
```python
from hypothesis import given, strategies as st

class TestPropertyBased:
    """Property-based tests using Hypothesis."""
    
    @given(st.text(min_size=1, max_size=100))
    def test_search_with_random_input(self, search_query):
        """Test search handles arbitrary input."""
        from src.tools.search_attack import SearchAttack
        tool = SearchAttack(mock_data_loader)
        
        # Should not crash with any input
        result = tool.execute(search_query)
        assert isinstance(result, str)
```

### Load Testing Integration
```python
import locust
from locust import HttpUser, task

class MCPServerUser(HttpUser):
    """Load test user for MCP server."""
    wait_time = locust.between(1, 3)
    
    @task
    def search_attack(self):
        """Load test search functionality."""
        self.client.post("/call_tool", json={
            "tool_name": "search_attack",
            "parameters": {"query": "persistence"}
        })
    
    @task(3)  # 3x weight
    def get_system_info(self):
        """Load test system info endpoint."""
        self.client.get("/system_info")
```

This testing guide provides comprehensive coverage of testing practices, from basic unit tests to advanced performance and property-based testing. Use it as a reference for maintaining and expanding the test suite.