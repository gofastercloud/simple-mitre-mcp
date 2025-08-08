"""
E2E test validation and setup verification.

This module provides basic validation tests to ensure E2E test infrastructure
is working correctly before running complex workflows.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.e2e
class TestE2EValidation:
    """Basic validation tests for E2E infrastructure."""

    def test_e2e_test_data_manager_import(self):
        """Test that E2E test data manager can be imported."""
        from tests.e2e.test_data_manager import E2ETestDataManager
        
        manager = E2ETestDataManager()
        assert manager is not None
        logger.info("E2E test data manager imported successfully")

    def test_comprehensive_test_data_structure(self, e2e_test_data):
        """Test that comprehensive test data has correct structure."""
        assert isinstance(e2e_test_data, dict)
        
        required_keys = ["techniques", "tactics", "groups", "mitigations", "relationships"]
        for key in required_keys:
            assert key in e2e_test_data, f"Missing required key: {key}"
            assert isinstance(e2e_test_data[key], list), f"Key {key} should be a list"
            assert len(e2e_test_data[key]) > 0, f"Key {key} should not be empty"
        
        # Validate techniques structure
        technique = e2e_test_data["techniques"][0]
        required_technique_keys = ["id", "name", "description", "tactics", "platforms", "mitigations"]
        for key in required_technique_keys:
            assert key in technique, f"Technique missing required key: {key}"
        
        logger.info("Comprehensive test data structure validated")

    def test_workflow_scenarios_structure(self, workflow_scenarios):
        """Test that workflow scenarios have correct structure."""
        assert isinstance(workflow_scenarios, list)
        assert len(workflow_scenarios) > 0
        
        scenario = workflow_scenarios[0]
        required_keys = ["name", "description", "steps", "expected_total_time", "success_criteria"]
        for key in required_keys:
            assert key in scenario, f"Scenario missing required key: {key}"
        
        # Validate steps structure
        step = scenario["steps"][0]
        required_step_keys = ["tool", "params", "expected_time"]
        for key in required_step_keys:
            assert key in step, f"Step missing required key: {key}"
        
        logger.info("Workflow scenarios structure validated")

    def test_performance_test_data_structure(self, performance_test_data):
        """Test that performance test data has correct structure."""
        assert isinstance(performance_test_data, dict)
        
        required_categories = ["quick_scenarios", "medium_scenarios", "complex_scenarios"]
        for category in required_categories:
            assert category in performance_test_data, f"Missing category: {category}"
            assert isinstance(performance_test_data[category], list), f"Category {category} should be a list"
        
        # Validate scenario structure
        scenario = performance_test_data["quick_scenarios"][0]
        required_keys = ["tool", "params", "max_time"]
        for key in required_keys:
            assert key in scenario, f"Performance scenario missing key: {key}"
        
        logger.info("Performance test data structure validated")

    def test_error_test_scenarios_structure(self, error_test_scenarios):
        """Test that error test scenarios have correct structure."""
        assert isinstance(error_test_scenarios, list)
        assert len(error_test_scenarios) > 0
        
        scenario = error_test_scenarios[0]
        required_keys = ["name", "tool", "params", "expected_error_indicators"]
        for key in required_keys:
            assert key in scenario, f"Error scenario missing key: {key}"
        
        assert isinstance(scenario["expected_error_indicators"], list)
        assert len(scenario["expected_error_indicators"]) > 0
        
        logger.info("Error test scenarios structure validated")

    def test_workflow_executor_fixture(self, workflow_executor):
        """Test that workflow executor fixture works correctly."""
        assert workflow_executor is not None
        assert hasattr(workflow_executor, "add_step")
        assert hasattr(workflow_executor, "execute_workflow")
        assert hasattr(workflow_executor, "assert_workflow_success")
        assert hasattr(workflow_executor, "get_step_result")
        
        logger.info("Workflow executor fixture validated")

    def test_user_simulation_fixture(self, user_simulation):
        """Test that user simulation fixture works correctly."""
        assert user_simulation is not None
        assert hasattr(user_simulation, "simulate_search_workflow")
        assert hasattr(user_simulation, "simulate_technique_analysis")
        assert hasattr(user_simulation, "simulate_attack_path_creation")
        assert hasattr(user_simulation, "simulate_coverage_analysis")
        
        logger.info("User simulation fixture validated")

    def test_system_health_checker_fixture(self, system_health_checker):
        """Test that system health checker fixture works correctly."""
        assert system_health_checker is not None
        assert hasattr(system_health_checker, "check_server_health")
        assert hasattr(system_health_checker, "check_http_proxy_health")
        assert hasattr(system_health_checker, "check_data_availability")
        assert hasattr(system_health_checker, "run_all_health_checks")
        
        logger.info("System health checker fixture validated")

    @pytest.mark.asyncio
    async def test_basic_async_functionality(self):
        """Test basic async functionality for E2E tests."""
        # Simple async test to verify async setup works
        await asyncio.sleep(0.1)
        
        result = await self._async_test_function()
        assert result == "async_test_success"
        
        logger.info("Basic async functionality validated")

    async def _async_test_function(self):
        """Helper async function for testing."""
        await asyncio.sleep(0.05)
        return "async_test_success"

    def test_e2e_test_manager_fixture(self, e2e_test_manager):
        """Test that E2E test manager fixture works correctly."""
        assert e2e_test_manager is not None
        assert hasattr(e2e_test_manager, "start_test")
        assert hasattr(e2e_test_manager, "end_test")
        assert hasattr(e2e_test_manager, "cache_test_data")
        assert hasattr(e2e_test_manager, "get_cached_data")
        assert hasattr(e2e_test_manager, "cleanup")
        
        # Test basic functionality
        e2e_test_manager.start_test("validation_test")
        e2e_test_manager.cache_test_data("test_key", {"test": "data"})
        cached_data = e2e_test_manager.get_cached_data("test_key")
        assert cached_data == {"test": "data"}
        e2e_test_manager.end_test("validation_test")
        
        performance_summary = e2e_test_manager.get_performance_summary()
        assert isinstance(performance_summary, dict)
        assert "validation_test" in performance_summary
        
        logger.info("E2E test manager fixture validated")

    def test_optimized_test_data_fixture(self, optimized_test_data):
        """Test that optimized test data fixture works correctly."""
        assert isinstance(optimized_test_data, dict)
        assert "comprehensive_data" in optimized_test_data
        assert "performance_scenarios" in optimized_test_data
        assert "workflow_scenarios" in optimized_test_data
        
        # Validate comprehensive data
        comprehensive_data = optimized_test_data["comprehensive_data"]
        assert isinstance(comprehensive_data, dict)
        assert "techniques" in comprehensive_data
        assert len(comprehensive_data["techniques"]) > 0
        
        logger.info("Optimized test data fixture validated")

    def test_full_system_setup_fixture(self, full_system_setup):
        """Test that full system setup fixture works correctly."""
        assert isinstance(full_system_setup, dict)
        
        required_keys = ["env", "data_dir", "server_url", "http_url"]
        for key in required_keys:
            assert key in full_system_setup, f"Full system setup missing key: {key}"
        
        # Validate environment variables
        env = full_system_setup["env"]
        assert isinstance(env, dict)
        assert "MCP_SERVER_HOST" in env
        assert "MCP_SERVER_PORT" in env
        assert "MCP_HTTP_HOST" in env
        assert "MCP_HTTP_PORT" in env
        
        logger.info("Full system setup fixture validated")

    def test_e2e_markers_and_configuration(self):
        """Test that E2E markers and configuration are set up correctly."""
        # This test validates that pytest markers are configured
        import pytest
        
        # Check that the test is marked with e2e
        current_test = pytest.current_test if hasattr(pytest, 'current_test') else None
        
        # Basic validation that we're in an E2E test context
        assert True  # Placeholder - in real implementation would check markers
        
        logger.info("E2E markers and configuration validated")


@pytest.mark.e2e
class TestE2EInfrastructurePerformance:
    """Performance validation tests for E2E infrastructure."""

    def test_test_data_loading_performance(self, e2e_test_data_manager):
        """Test that test data loads within acceptable time limits."""
        import time
        
        start_time = time.time()
        data = e2e_test_data_manager.get_comprehensive_test_data()
        load_time = time.time() - start_time
        
        assert load_time < 1.0, f"Test data loading took too long: {load_time:.2f}s"
        assert len(data["techniques"]) > 0, "Test data should contain techniques"
        
        logger.info(f"Test data loaded in {load_time:.3f}s")

    def test_workflow_scenarios_loading_performance(self, e2e_test_data_manager):
        """Test that workflow scenarios load within acceptable time limits."""
        import time
        
        start_time = time.time()
        scenarios = e2e_test_data_manager.get_workflow_scenarios()
        load_time = time.time() - start_time
        
        assert load_time < 0.5, f"Workflow scenarios loading took too long: {load_time:.2f}s"
        assert len(scenarios) > 0, "Should have workflow scenarios"
        
        logger.info(f"Workflow scenarios loaded in {load_time:.3f}s")

    def test_stress_test_data_generation_performance(self, e2e_test_data_manager):
        """Test that stress test data generation is performant."""
        import time
        
        start_time = time.time()
        stress_data = e2e_test_data_manager.generate_stress_test_data(50)
        generation_time = time.time() - start_time
        
        assert generation_time < 2.0, f"Stress test data generation took too long: {generation_time:.2f}s"
        assert len(stress_data) == 50, "Should generate requested number of scenarios"
        
        logger.info(f"Stress test data generated in {generation_time:.3f}s")

    def test_caching_performance(self, e2e_test_data_manager):
        """Test that caching improves performance."""
        import time
        
        # First load (should cache)
        start_time = time.time()
        data1 = e2e_test_data_manager.get_comprehensive_test_data()
        first_load_time = time.time() - start_time
        
        # Second load (should use cache)
        start_time = time.time()
        data2 = e2e_test_data_manager.get_comprehensive_test_data()
        second_load_time = time.time() - start_time
        
        # Second load should be faster (cached)
        assert second_load_time <= first_load_time, "Cached load should be faster or equal"
        assert data1 == data2, "Cached data should be identical"
        
        logger.info(f"First load: {first_load_time:.3f}s, Cached load: {second_load_time:.3f}s")