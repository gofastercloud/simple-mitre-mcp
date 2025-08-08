"""Shared pytest fixtures and configuration for the entire test suite."""

import pytest
import tempfile
import os
import json
import time
import threading
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from tests.factories import TestDataFactory, ConfigurationFactory, PerformanceDataFactory
from tests.base import BaseTestCase, BaseMCPTestCase


@pytest.fixture(scope="session")
def test_data_factory():
    """Provide TestDataFactory instance for all tests."""
    return TestDataFactory()


@pytest.fixture(scope="session")
def config_factory():
    """Provide ConfigurationFactory instance for all tests."""
    return ConfigurationFactory()


@pytest.fixture(scope="session")
def performance_factory():
    """Provide PerformanceDataFactory instance for all tests."""
    return PerformanceDataFactory()


@pytest.fixture(scope="module")
def sample_technique():
    """Provide a sample technique for testing."""
    return TestDataFactory.create_sample_technique()


@pytest.fixture(scope="module")
def sample_group():
    """Provide a sample group for testing."""
    return TestDataFactory.create_sample_group()


@pytest.fixture(scope="module")
def sample_tactic():
    """Provide a sample tactic for testing."""
    return TestDataFactory.create_sample_tactic()


@pytest.fixture(scope="module")
def sample_mitigation():
    """Provide a sample mitigation for testing."""
    return TestDataFactory.create_sample_mitigation()


@pytest.fixture(scope="module")
def sample_stix_bundle():
    """Provide a sample STIX bundle with multiple entities."""
    entities = [
        TestDataFactory.create_sample_technique("T1055"),
        TestDataFactory.create_sample_technique("T1003"),
        TestDataFactory.create_sample_group("G0016"),
        TestDataFactory.create_sample_tactic("TA0001"),
        TestDataFactory.create_sample_mitigation("M1013")
    ]
    return TestDataFactory.create_sample_stix_bundle(entities)


@pytest.fixture(scope="module")
def attack_path_data():
    """Provide sample attack path data for testing."""
    return TestDataFactory.create_attack_path_data()


@pytest.fixture(scope="module")
def coverage_gap_data():
    """Provide sample coverage gap data for testing."""
    return TestDataFactory.create_coverage_gap_data()


@pytest.fixture(scope="module")
def test_config():
    """Provide test configuration data."""
    return ConfigurationFactory.create_test_config()


@pytest.fixture(scope="module")
def test_env_vars():
    """Provide test environment variables."""
    return ConfigurationFactory.create_test_environment_vars()


@pytest.fixture
def temp_config_file(test_config):
    """Create a temporary configuration file for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(test_config, temp_file, indent=2)
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    try:
        os.unlink(temp_file.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_stix_file(sample_stix_bundle):
    """Create a temporary STIX file for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(sample_stix_bundle, temp_file, indent=2)
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    try:
        os.unlink(temp_file.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_requests_get():
    """Mock requests.get for HTTP testing."""
    with patch('requests.get') as mock_get:
        yield mock_get


@pytest.fixture(scope="module")
def mock_data_loader():
    """Mock data loader for MCP server testing."""
    mock_loader = Mock()
    
    # Configure default return values
    mock_loader.get_techniques.return_value = [
        TestDataFactory.create_sample_technique("T1055"),
        TestDataFactory.create_sample_technique("T1003")
    ]
    mock_loader.get_groups.return_value = [
        TestDataFactory.create_sample_group("G0016")
    ]
    mock_loader.get_tactics.return_value = [
        TestDataFactory.create_sample_tactic("TA0001")
    ]
    mock_loader.get_mitigations.return_value = [
        TestDataFactory.create_sample_mitigation("M1013")
    ]
    mock_loader.search_entities.return_value = []
    mock_loader.get_relationships.return_value = []
    
    return mock_loader


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for testing."""
    with patch('src.mcp_server.app') as mock_app:
        # Configure mock tools
        mock_app.list_tools.return_value = [
            {"name": "search_attack", "description": "Search MITRE ATT&CK"},
            {"name": "get_technique", "description": "Get technique details"},
            {"name": "list_tactics", "description": "List all tactics"},
            {"name": "get_group_techniques", "description": "Get group techniques"},
            {"name": "get_technique_mitigations", "description": "Get technique mitigations"},
            {"name": "build_attack_path", "description": "Build attack path"},
            {"name": "analyze_coverage_gaps", "description": "Analyze coverage gaps"},
            {"name": "detect_technique_relationships", "description": "Detect relationships"}
        ]
        yield mock_app


@pytest.fixture
def performance_thresholds():
    """Provide performance thresholds for testing."""
    return PerformanceDataFactory.create_performance_thresholds()


@pytest.fixture
def large_test_dataset():
    """Provide large dataset for performance testing."""
    return PerformanceDataFactory.create_large_dataset(100)  # Smaller for faster tests


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables before and after each test."""
    # Store original environment
    original_env = os.environ.copy()
    
    # Set clean test environment
    test_env = ConfigurationFactory.create_test_environment_vars()
    for key, value in test_env.items():
        os.environ[key] = value
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def isolated_temp_dir():
    """Provide isolated temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    
    yield temp_dir
    
    # Cleanup
    os.chdir(original_cwd)
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)


# Pytest configuration hooks
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (moderate speed)"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and benchmark tests (slow)"
    )
    config.addinivalue_line(
        "markers", "compatibility: Backward compatibility tests"
    )
    config.addinivalue_line(
        "markers", "deployment: Deployment validation tests"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (slowest)"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take more than 5 seconds"
    )
    config.addinivalue_line(
        "markers", "fast: Tests that complete in under 1 second"
    )





def pytest_runtest_setup(item):
    """Setup hook for individual test runs."""
    # Skip slow tests if running in fast mode
    if item.config.getoption("--fast", default=False):
        if "slow" in [mark.name for mark in item.iter_markers()]:
            pytest.skip("Skipping slow test in fast mode")
    
    # Skip benchmark tests unless explicitly requested
    if not item.config.getoption("--benchmark", default=False):
        if "benchmark" in [mark.name for mark in item.iter_markers()]:
            pytest.skip("Skipping benchmark test (use --benchmark to run)")
    
    # Record test start time for timing
    item._test_start_time = time.time()


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--fast",
        action="store_true",
        default=False,
        help="Run only fast tests, skip slow tests"
    )
    parser.addoption(
        "--category",
        action="store",
        default=None,
        help="Run tests from specific category (unit, integration, performance, etc.)"
    )
    parser.addoption(
        "--parallel",
        action="store",
        default="auto",
        help="Number of parallel workers (auto, or specific number)"
    )
    parser.addoption(
        "--benchmark",
        action="store_true",
        default=False,
        help="Run performance benchmarks"
    )
    parser.addoption(
        "--timing-report",
        action="store_true",
        default=False,
        help="Generate detailed timing report"
    )


# Global test timing storage
_test_timings = {}
_timing_lock = threading.Lock()


def pytest_runtest_teardown(item, nextitem):
    """Teardown hook for individual test runs."""
    if hasattr(item, '_test_start_time'):
        duration = time.time() - item._test_start_time
        
        # Store timing information
        with _timing_lock:
            # Handle both Path and LocalPath objects
            try:
                if hasattr(item.fspath, 'relative_to'):
                    test_path = str(item.fspath.relative_to(item.config.rootdir))
                else:
                    # For older pytest versions with LocalPath
                    test_path = str(item.fspath).replace(str(item.config.rootdir), "").lstrip("/")
            except (AttributeError, TypeError):
                test_path = str(item.fspath)
            
            test_name = f"{test_path}::{item.name}"
            _test_timings[test_name] = {
                'duration': duration,
                'category': _get_test_category(item),
                'markers': [mark.name for mark in item.iter_markers()]
            }


def pytest_sessionfinish(session, exitstatus):
    """Session finish hook for generating timing reports."""
    if session.config.getoption("--timing-report", default=False):
        _generate_timing_report(session)


def _get_test_category(item):
    """Determine test category from markers or path."""
    test_path = str(item.fspath)
    
    if "/unit/" in test_path:
        return "unit"
    elif "/integration/" in test_path:
        return "integration"
    elif "/performance/" in test_path:
        return "performance"
    elif "/compatibility/" in test_path:
        return "compatibility"
    elif "/deployment/" in test_path:
        return "deployment"
    elif "/e2e/" in test_path:
        return "e2e"
    else:
        return "other"


def _generate_timing_report(session):
    """Generate detailed timing report."""
    if not _test_timings:
        return
    
    print("\n" + "="*80)
    print("TEST EXECUTION TIMING REPORT")
    print("="*80)
    
    # Sort tests by duration (slowest first)
    sorted_tests = sorted(_test_timings.items(), key=lambda x: x[1]['duration'], reverse=True)
    
    # Category statistics
    category_stats = {}
    for test_name, timing in _test_timings.items():
        category = timing['category']
        if category not in category_stats:
            category_stats[category] = {'count': 0, 'total_time': 0, 'avg_time': 0}
        category_stats[category]['count'] += 1
        category_stats[category]['total_time'] += timing['duration']
    
    # Calculate averages
    for category in category_stats:
        stats = category_stats[category]
        stats['avg_time'] = stats['total_time'] / stats['count']
    
    # Print category summary
    print("\nCATEGORY SUMMARY:")
    print("-" * 60)
    print(f"{'Category':<15} {'Count':<8} {'Total (s)':<12} {'Avg (s)':<10}")
    print("-" * 60)
    
    for category, stats in sorted(category_stats.items()):
        print(f"{category:<15} {stats['count']:<8} {stats['total_time']:<12.3f} {stats['avg_time']:<10.3f}")
    
    # Print slowest tests
    print(f"\nSLOWEST TESTS (Top 20):")
    print("-" * 80)
    print(f"{'Duration (s)':<12} {'Category':<12} {'Test'}")
    print("-" * 80)
    
    for test_name, timing in sorted_tests[:20]:
        duration = timing['duration']
        category = timing['category']
        short_name = test_name.split("::")[-1][:50]
        print(f"{duration:<12.3f} {category:<12} {short_name}")
    
    # Performance recommendations
    print(f"\nPERFORMANCE RECOMMENDATIONS:")
    print("-" * 40)
    
    slow_tests = [t for t in sorted_tests if t[1]['duration'] > 5.0]
    if slow_tests:
        print(f"• {len(slow_tests)} tests take >5 seconds - consider optimization")
    
    unit_slow = [t for t in sorted_tests if t[1]['category'] == 'unit' and t[1]['duration'] > 1.0]
    if unit_slow:
        print(f"• {len(unit_slow)} unit tests take >1 second - should be faster")
    
    total_time = sum(t[1]['duration'] for t in sorted_tests)
    print(f"• Total execution time: {total_time:.3f} seconds")
    
    # Parallel execution estimate
    if len(sorted_tests) > 1:
        parallel_estimate = max(t[1]['duration'] for t in sorted_tests)
        speedup = total_time / parallel_estimate
        print(f"• Estimated parallel speedup: {speedup:.1f}x (with unlimited workers)")
    
    print("="*80)


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers and optimize ordering."""
    # Add markers based on test file location
    for item in items:
        test_path = str(item.fspath)
        
        if "/unit/" in test_path:
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.fast)
        elif "/integration/" in test_path:
            item.add_marker(pytest.mark.integration)
        elif "/performance/" in test_path:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.benchmark)
        elif "/compatibility/" in test_path:
            item.add_marker(pytest.mark.compatibility)
        elif "/deployment/" in test_path:
            item.add_marker(pytest.mark.deployment)
        elif "/e2e/" in test_path:
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow)
    
    # Optimize test ordering for better execution flow
    # Fast tests first, then integration, then slow tests
    def test_priority(item):
        test_path = str(item.fspath)
        
        # Priority order: unit (0), integration (1), deployment (2), compatibility (3), performance (4), e2e (5)
        if "/unit/" in test_path:
            return (0, item.name)
        elif "/integration/" in test_path:
            return (1, item.name)
        elif "/deployment/" in test_path:
            return (2, item.name)
        elif "/compatibility/" in test_path:
            return (3, item.name)
        elif "/performance/" in test_path:
            return (4, item.name)
        elif "/e2e/" in test_path:
            return (5, item.name)
        else:
            return (6, item.name)
    
    # Sort items by priority
    items.sort(key=test_priority)