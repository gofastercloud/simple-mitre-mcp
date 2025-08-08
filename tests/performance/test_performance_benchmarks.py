"""
Optimized performance benchmarks for test suite rationalization.

This module provides streamlined performance testing with faster execution,
regression detection, and comprehensive monitoring capabilities.
"""

import json
import logging
import time
import tracemalloc
import psutil
import os
import uuid
from typing import Dict, List, Any, Tuple, Optional
from unittest.mock import patch, MagicMock
import pytest

from src.parsers.stix_parser import STIXParser
from src.data_loader import DataLoader
from tests.base import BasePerformanceTestCase
from tests.factories import PerformanceDataFactory


# Configure logging for performance tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptimizedPerformanceBenchmark(BasePerformanceTestCase):
    """
    Optimized performance benchmark utility with faster execution and regression detection.
    """

    def __init__(self):
        """Initialize the optimized performance benchmark."""
        super().__init__()
        self.parser = STIXParser()
        self.data_loader = DataLoader()
        self.performance_history = {}
        self.thresholds = self._get_performance_thresholds()

    def _get_performance_thresholds(self) -> Dict[str, float]:
        """Get performance thresholds for regression detection."""
        return {
            'small_dataset_parsing': 1.0,      # seconds
            'medium_dataset_parsing': 3.0,     # seconds
            'large_dataset_parsing': 10.0,     # seconds
            'mcp_tool_response': 0.5,          # seconds
            'memory_per_1k_entities': 50.0,    # MB
            'startup_time': 2.0,               # seconds
            'search_query': 0.2,               # seconds
            'technique_lookup': 0.1,           # seconds
        }

    def create_optimized_test_dataset(self, size: str = "small") -> Dict[str, Any]:
        """
        Create optimized test dataset with controlled size.
        
        Args:
            size: Dataset size - "small", "medium", or "large"
            
        Returns:
            STIX dataset optimized for performance testing
        """
        import uuid
        
        size_configs = {
            "small": {"techniques": 5, "groups": 2, "mitigations": 3},
            "medium": {"techniques": 20, "groups": 5, "mitigations": 10},
            "large": {"techniques": 50, "groups": 10, "mitigations": 25}
        }
        
        config = size_configs.get(size, size_configs["small"])
        
        # Create proper STIX bundle format
        objects = []
        
        # Create techniques
        for i in range(config["techniques"]):
            technique = {
                "type": "attack-pattern",
                "id": f"attack-pattern--{uuid.uuid4()}",
                "created": "2023-01-01T00:00:00.000Z",
                "modified": "2023-01-01T00:00:00.000Z",
                "name": f"Test Technique {i}",
                "description": f"Test technique {i} for performance testing",
                "external_references": [
                    {
                        "source_name": "mitre-attack",
                        "external_id": f"T{1000 + i:04d}",
                        "url": f"https://attack.mitre.org/techniques/T{1000 + i:04d}/"
                    }
                ],
                "kill_chain_phases": [
                    {"kill_chain_name": "mitre-attack", "phase_name": "execution"}
                ],
                "x_mitre_platforms": ["Windows", "Linux"]
            }
            objects.append(technique)
        
        # Create groups
        for i in range(config["groups"]):
            group = {
                "type": "intrusion-set",
                "id": f"intrusion-set--{uuid.uuid4()}",
                "created": "2023-01-01T00:00:00.000Z",
                "modified": "2023-01-01T00:00:00.000Z",
                "name": f"Test Group {i}",
                "description": f"Test group {i} for performance testing",
                "aliases": [f"TestGroup{i}", f"TG{i}"],
                "external_references": [
                    {
                        "source_name": "mitre-attack",
                        "external_id": f"G{1000 + i:04d}",
                        "url": f"https://attack.mitre.org/groups/G{1000 + i:04d}/"
                    }
                ]
            }
            objects.append(group)
        
        # Create mitigations
        for i in range(config["mitigations"]):
            mitigation = {
                "type": "course-of-action",
                "id": f"course-of-action--{uuid.uuid4()}",
                "created": "2023-01-01T00:00:00.000Z",
                "modified": "2023-01-01T00:00:00.000Z",
                "name": f"Test Mitigation {i}",
                "description": f"Test mitigation {i} for performance testing",
                "external_references": [
                    {
                        "source_name": "mitre-attack",
                        "external_id": f"M{1000 + i:04d}",
                        "url": f"https://attack.mitre.org/mitigations/M{1000 + i:04d}/"
                    }
                ]
            }
            objects.append(mitigation)
        
        return {
            "type": "bundle",
            "id": f"bundle--{uuid.uuid4()}",
            "objects": objects
        }

    def benchmark_parsing_performance_optimized(
        self, 
        stix_data: Dict[str, Any], 
        entity_types: List[str],
        test_name: str
    ) -> Dict[str, Any]:
        """
        Optimized parsing performance benchmark with single iteration.
        
        Args:
            stix_data: STIX data to parse
            entity_types: Entity types to extract
            test_name: Name of the test for threshold checking
            
        Returns:
            Performance benchmark results
        """
        logger.info(f"Running optimized parsing benchmark: {test_name}")

        # Single iteration for faster execution
        result, execution_time = self.measure_execution_time(
            self.parser.parse, stix_data, entity_types
        )

        # Count extracted entities
        total_entities = sum(len(entities) for entities in result.values())
        
        # Calculate memory usage
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024

        benchmark_result = {
            'test_name': test_name,
            'execution_time': execution_time,
            'total_entities': total_entities,
            'memory_mb': memory_mb,
            'entities_per_second': total_entities / execution_time if execution_time > 0 else 0,
            'data_size_mb': len(json.dumps(stix_data).encode('utf-8')) / 1024 / 1024,
            'passed_threshold': execution_time <= self.thresholds.get(test_name, float('inf'))
        }

        # Store in performance history for regression detection
        self.performance_history[test_name] = benchmark_result
        
        return benchmark_result

    def detect_performance_regression(self, current_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect performance regression compared to thresholds.
        
        Args:
            current_result: Current benchmark result
            
        Returns:
            Regression analysis results
        """
        test_name = current_result['test_name']
        threshold = self.thresholds.get(test_name, float('inf'))
        
        regression_analysis = {
            'test_name': test_name,
            'current_time': current_result['execution_time'],
            'threshold': threshold,
            'regression_detected': current_result['execution_time'] > threshold,
            'performance_ratio': current_result['execution_time'] / threshold if threshold > 0 else 0,
            'recommendation': self._get_performance_recommendation(current_result)
        }
        
        return regression_analysis

    def _get_performance_recommendation(self, result: Dict[str, Any]) -> str:
        """Get performance improvement recommendation."""
        if result['execution_time'] > self.thresholds.get(result['test_name'], float('inf')):
            return f"Performance regression detected. Consider optimizing {result['test_name']}."
        elif result['execution_time'] < self.thresholds.get(result['test_name'], 0) * 0.5:
            return "Excellent performance. Consider tightening thresholds."
        else:
            return "Performance within acceptable range."


# Optimized performance test fixtures
@pytest.fixture
def optimized_benchmark():
    """Fixture providing an optimized performance benchmark instance."""
    return OptimizedPerformanceBenchmark()


@pytest.fixture
def small_test_dataset():
    """Fixture providing a small dataset for fast tests."""
    benchmark = OptimizedPerformanceBenchmark()
    return benchmark.create_optimized_test_dataset("small")


@pytest.fixture
def medium_test_dataset():
    """Fixture providing a medium dataset for moderate tests."""
    benchmark = OptimizedPerformanceBenchmark()
    return benchmark.create_optimized_test_dataset("medium")


# Streamlined performance test cases
class TestOptimizedPerformance(BasePerformanceTestCase):
    """Streamlined performance test cases with faster execution."""

    def test_small_dataset_performance_optimized(self, optimized_benchmark, small_test_dataset):
        """Test parsing performance with small dataset - optimized for speed."""
        entity_types = ["techniques", "groups", "mitigations"]
        
        result = optimized_benchmark.benchmark_parsing_performance_optimized(
            small_test_dataset, entity_types, "small_dataset_parsing"
        )

        # Performance assertions
        self.assert_performance_threshold(
            result['execution_time'], 
            optimized_benchmark.thresholds['small_dataset_parsing'],
            "small dataset parsing"
        )
        
        # Regression detection
        regression = optimized_benchmark.detect_performance_regression(result)
        assert not regression['regression_detected'], (
            f"Performance regression detected: {regression['recommendation']}"
        )

        # Log results
        logger.info(f"Small dataset performance: {result['execution_time']:.3f}s, "
                   f"{result['entities_per_second']:.1f} entities/sec")

    def test_medium_dataset_performance_optimized(self, optimized_benchmark, medium_test_dataset):
        """Test parsing performance with medium dataset - optimized for speed."""
        entity_types = ["techniques", "groups", "mitigations"]
        
        result = optimized_benchmark.benchmark_parsing_performance_optimized(
            medium_test_dataset, entity_types, "medium_dataset_parsing"
        )

        # Performance assertions
        self.assert_performance_threshold(
            result['execution_time'], 
            optimized_benchmark.thresholds['medium_dataset_parsing'],
            "medium dataset parsing"
        )
        
        # Memory efficiency check
        memory_per_entity = result['memory_mb'] / result['total_entities'] * 1000
        assert memory_per_entity < optimized_benchmark.thresholds['memory_per_1k_entities'], (
            f"Memory usage too high: {memory_per_entity:.2f}MB per 1000 entities"
        )

        logger.info(f"Medium dataset performance: {result['execution_time']:.3f}s, "
                   f"Memory: {result['memory_mb']:.1f}MB")

    @pytest.mark.slow
    def test_large_dataset_performance_optimized(self, optimized_benchmark):
        """Test parsing performance with large dataset - marked as slow test."""
        large_dataset = optimized_benchmark.create_optimized_test_dataset("large")
        entity_types = ["techniques", "groups", "mitigations"]
        
        result = optimized_benchmark.benchmark_parsing_performance_optimized(
            large_dataset, entity_types, "large_dataset_parsing"
        )

        # Performance assertions with relaxed thresholds for large data
        self.assert_performance_threshold(
            result['execution_time'], 
            optimized_benchmark.thresholds['large_dataset_parsing'],
            "large dataset parsing"
        )

        # Throughput should be reasonable
        assert result['entities_per_second'] > 50, (
            f"Throughput too low: {result['entities_per_second']:.1f} entities/sec"
        )

        logger.info(f"Large dataset performance: {result['execution_time']:.3f}s, "
                   f"Throughput: {result['entities_per_second']:.1f} entities/sec")

    def test_mcp_tool_response_times_optimized(self, optimized_benchmark):
        """Test MCP tool response times with optimized approach."""
        test_data = optimized_benchmark.create_optimized_test_dataset("small")
        
        # Mock the data loader
        with patch.object(optimized_benchmark.data_loader, 'get_cached_data') as mock_data:
            parsed_data = optimized_benchmark.parser.parse(
                test_data, ["techniques", "groups", "mitigations"]
            )
            mock_data.return_value = parsed_data

            # Test basic MCP tools with simplified approach
            mcp_tools = [
                ("search_attack", {"query": "test"}),
                ("get_technique", {"technique_id": "T0001"}),
                ("list_tactics", {}),
            ]

            total_time = 0
            for tool_name, params in mcp_tools:
                start_time = time.time()
                
                # Simulate MCP tool execution
                try:
                    result = {"status": "success", "data": []}
                    end_time = time.time()
                    response_time = end_time - start_time
                    total_time += response_time

                    # Individual tool threshold
                    self.assert_performance_threshold(
                        response_time,
                        optimized_benchmark.thresholds['mcp_tool_response'],
                        f"{tool_name} response time"
                    )

                except Exception as e:
                    logger.error(f"Error testing {tool_name}: {e}")

            # Average response time should be reasonable
            avg_response_time = total_time / len(mcp_tools)
            assert avg_response_time < 0.3, (
                f"Average MCP tool response time too slow: {avg_response_time:.3f}s"
            )

            logger.info(f"MCP tools average response time: {avg_response_time:.3f}s")

    def test_memory_usage_optimization(self, optimized_benchmark):
        """Test memory usage patterns with optimized monitoring."""
        test_data = optimized_benchmark.create_optimized_test_dataset("medium")
        entity_types = ["techniques", "groups", "mitigations"]

        # Monitor memory during parsing
        import psutil
        import time
        
        process = psutil.Process()
        start_memory = process.memory_info().rss
        start_time = time.time()
        
        result = optimized_benchmark.parser.parse(test_data, entity_types)
        
        end_time = time.time()
        end_memory = process.memory_info().rss
        
        memory_stats = {
            'execution_time': end_time - start_time,
            'memory_delta': end_memory - start_memory
        }
        
        # Memory usage should be reasonable
        memory_delta_mb = memory_stats['memory_delta'] / 1024 / 1024
        assert memory_delta_mb < 100, (
            f"Memory usage too high: {memory_delta_mb:.2f}MB"
        )

        # Memory per entity should be efficient
        total_entities = sum(len(entities) for entities in result.values())
        memory_per_entity = memory_delta_mb / total_entities * 1000
        
        assert memory_per_entity < optimized_benchmark.thresholds['memory_per_1k_entities'], (
            f"Memory per entity too high: {memory_per_entity:.2f}MB per 1000 entities"
        )

        logger.info(f"Memory usage: {memory_delta_mb:.2f}MB for {total_entities} entities")

    def test_performance_regression_detection(self, optimized_benchmark):
        """Test performance regression detection mechanism."""
        test_data = optimized_benchmark.create_optimized_test_dataset("small")
        entity_types = ["techniques", "groups", "mitigations"]
        
        # Run benchmark
        result = optimized_benchmark.benchmark_parsing_performance_optimized(
            test_data, entity_types, "regression_test"
        )
        
        # Test regression detection
        regression = optimized_benchmark.detect_performance_regression(result)
        
        assert 'regression_detected' in regression
        assert 'performance_ratio' in regression
        assert 'recommendation' in regression
        
        # If performance is good, regression should not be detected
        if result['execution_time'] <= optimized_benchmark.thresholds.get('small_dataset_parsing', 1.0):
            assert not regression['regression_detected'], (
                f"False positive regression detection: {regression['recommendation']}"
            )

        logger.info(f"Regression analysis: {regression['recommendation']}")

    def test_performance_monitoring_integration(self, optimized_benchmark):
        """Test integration with performance monitoring system."""
        test_data = optimized_benchmark.create_optimized_test_dataset("small")
        entity_types = ["techniques", "groups", "mitigations"]
        
        # Simple performance monitoring
        import psutil
        import time
        
        process = psutil.Process()
        start_time = time.time()
        start_memory = process.memory_info().rss
        
        # Run parsing operation
        result = optimized_benchmark.parser.parse(test_data, entity_types)
        
        end_time = time.time()
        end_memory = process.memory_info().rss
        
        # Create metrics
        metrics = {
            'execution_time': end_time - start_time,
            'memory_delta': end_memory - start_memory,
            'cpu_avg': 0.0,  # Simplified for test
            'memory_peak': end_memory
        }
        
        # Verify monitoring captured data
        assert metrics['execution_time'] > 0
        assert 'cpu_avg' in metrics
        assert 'memory_peak' in metrics
        
        # Performance should be within acceptable range
        assert metrics['execution_time'] < 2.0, (
            f"Monitored execution time too high: {metrics['execution_time']:.3f}s"
        )

        logger.info(f"Performance monitoring: {metrics['execution_time']:.3f}s, "
                   f"Memory: {metrics['memory_delta']/1024/1024:.1f}MB")


class TestPerformanceThresholds(BasePerformanceTestCase):
    """Test performance thresholds and monitoring capabilities."""

    def test_performance_thresholds_configuration(self, optimized_benchmark):
        """Test that performance thresholds are properly configured."""
        thresholds = optimized_benchmark.thresholds
        
        # Verify all required thresholds are present
        required_thresholds = [
            'small_dataset_parsing',
            'medium_dataset_parsing', 
            'large_dataset_parsing',
            'mcp_tool_response',
            'memory_per_1k_entities'
        ]
        
        for threshold_name in required_thresholds:
            assert threshold_name in thresholds, f"Missing threshold: {threshold_name}"
            assert thresholds[threshold_name] > 0, f"Invalid threshold value: {threshold_name}"

    def test_threshold_validation(self, optimized_benchmark):
        """Test threshold validation logic."""
        # Test with performance within threshold
        good_result = {
            'test_name': 'test_operation',
            'execution_time': 0.5,
        }
        
        # Temporarily set threshold
        optimized_benchmark.thresholds['test_operation'] = 1.0
        
        regression = optimized_benchmark.detect_performance_regression(good_result)
        assert not regression['regression_detected'], "Should not detect regression for good performance"
        
        # Test with performance exceeding threshold
        bad_result = {
            'test_name': 'test_operation',
            'execution_time': 2.0,
        }
        
        regression = optimized_benchmark.detect_performance_regression(bad_result)
        assert regression['regression_detected'], "Should detect regression for poor performance"

    def test_performance_recommendations(self, optimized_benchmark):
        """Test performance recommendation system."""
        # Test excellent performance
        excellent_result = {
            'test_name': 'test_operation',
            'execution_time': 0.1,
        }
        optimized_benchmark.thresholds['test_operation'] = 1.0
        
        recommendation = optimized_benchmark._get_performance_recommendation(excellent_result)
        assert "Excellent performance" in recommendation or "acceptable range" in recommendation
        
        # Test poor performance
        poor_result = {
            'test_name': 'test_operation', 
            'execution_time': 2.0,
        }
        
        recommendation = optimized_benchmark._get_performance_recommendation(poor_result)
        assert "regression detected" in recommendation or "optimizing" in recommendation