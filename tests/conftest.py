"""Shared pytest fixtures and configuration for the entire test suite."""

import pytest
import tempfile
import os
import json
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


@pytest.fixture
def sample_technique():
    """Provide a sample technique for testing."""
    return TestDataFactory.create_sample_technique()


@pytest.fixture
def sample_group():
    """Provide a sample group for testing."""
    return TestDataFactory.create_sample_group()


@pytest.fixture
def sample_tactic():
    """Provide a sample tactic for testing."""
    return TestDataFactory.create_sample_tactic()


@pytest.fixture
def sample_mitigation():
    """Provide a sample mitigation for testing."""
    return TestDataFactory.create_sample_mitigation()


@pytest.fixture
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


@pytest.fixture
def attack_path_data():
    """Provide sample attack path data for testing."""
    return TestDataFactory.create_attack_path_data()


@pytest.fixture
def coverage_gap_data():
    """Provide sample coverage gap data for testing."""
    return TestDataFactory.create_coverage_gap_data()


@pytest.fixture
def test_config():
    """Provide test configuration data."""
    return ConfigurationFactory.create_test_config()


@pytest.fixture
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


@pytest.fixture
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


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        test_path = str(item.fspath)
        
        if "/unit/" in test_path:
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.fast)
        elif "/integration/" in test_path:
            item.add_marker(pytest.mark.integration)
        elif "/performance/" in test_path:
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        elif "/compatibility/" in test_path:
            item.add_marker(pytest.mark.compatibility)
        elif "/deployment/" in test_path:
            item.add_marker(pytest.mark.deployment)
        elif "/e2e/" in test_path:
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.slow)


def pytest_runtest_setup(item):
    """Setup hook for individual test runs."""
    # Skip slow tests if running in fast mode
    if item.config.getoption("--fast", default=False):
        if "slow" in [mark.name for mark in item.iter_markers()]:
            pytest.skip("Skipping slow test in fast mode")


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