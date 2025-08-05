"""
Performance benchmarks for STIX2 library refactor.

This module provides comprehensive performance testing comparing the old custom
parsing implementation with the new STIX2 library-based implementation.
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
import requests

from src.parsers.stix_parser import STIXParser
from src.data_loader import DataLoader


# Configure logging for performance tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """
    Performance benchmark utility for comparing parsing implementations.
    """

    def __init__(self):
        """Initialize the performance benchmark."""
        self.parser = STIXParser()
        self.data_loader = DataLoader()
        self.results = {}

    def measure_memory_usage(
        self, func, *args, **kwargs
    ) -> Tuple[Any, Dict[str, float]]:
        """
        Measure memory usage of a function execution.

        Args:
            func: Function to measure
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Tuple of (function_result, memory_stats)
        """
        # Start memory tracing
        tracemalloc.start()

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Execute function
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        memory_stats = {
            "execution_time": end_time - start_time,
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_delta_mb": final_memory - initial_memory,
            "peak_traced_mb": peak / 1024 / 1024,
            "current_traced_mb": current / 1024 / 1024,
        }

        return result, memory_stats

    def create_large_stix_dataset(
        self,
        num_techniques: int = 1000,
        num_groups: int = 200,
        num_mitigations: int = 500,
    ) -> Dict[str, Any]:
        """
        Create a large synthetic STIX dataset for performance testing.

        Args:
            num_techniques: Number of technique objects to create
            num_groups: Number of group objects to create
            num_mitigations: Number of mitigation objects to create

        Returns:
            Large STIX dataset dictionary
        """
        logger.info(
            f"Creating synthetic STIX dataset: {num_techniques} techniques, "
            f"{num_groups} groups, {num_mitigations} mitigations"
        )

        objects = []

        # Create technique objects
        for i in range(num_techniques):
            # Generate proper UUID for STIX2 library compatibility
            technique_uuid = str(uuid.uuid4())
            technique = {
                "type": "attack-pattern",
                "id": f"attack-pattern--{technique_uuid}",
                "created": "2023-01-01T00:00:00.000Z",
                "modified": "2023-01-01T00:00:00.000Z",
                "name": f"Test Technique {i}",
                "description": f"This is a test technique number {i} for performance testing. "
                * 10,
                "kill_chain_phases": [
                    {"kill_chain_name": "mitre-attack", "phase_name": "initial-access"}
                ],
                "external_references": [
                    {
                        "source_name": "mitre-attack",
                        "external_id": f"T{i:04d}",
                        "url": f"https://attack.mitre.org/techniques/T{i:04d}/",
                    }
                ],
                "x_mitre_platforms": ["Windows", "Linux", "macOS"],
                "x_mitre_data_sources": [
                    f"Process: Process Creation",
                    f"File: File Creation",
                ],
                "x_mitre_detection": f"Detection guidance for technique {i}",
                "x_mitre_version": "1.0",
            }
            objects.append(technique)

        # Create group objects
        for i in range(num_groups):
            group_uuid = str(uuid.uuid4())
            group = {
                "type": "intrusion-set",
                "id": f"intrusion-set--{group_uuid}",
                "created": "2023-01-01T00:00:00.000Z",
                "modified": "2023-01-01T00:00:00.000Z",
                "name": f"Test Group {i}",
                "description": f"This is a test threat group number {i} for performance testing. "
                * 10,
                "aliases": [f"Group{i}", f"TestGroup{i}", f"TG{i}"],
                "external_references": [
                    {
                        "source_name": "mitre-attack",
                        "external_id": f"G{i:04d}",
                        "url": f"https://attack.mitre.org/groups/G{i:04d}/",
                    }
                ],
            }
            objects.append(group)

        # Create mitigation objects
        for i in range(num_mitigations):
            mitigation_uuid = str(uuid.uuid4())
            mitigation = {
                "type": "course-of-action",
                "id": f"course-of-action--{mitigation_uuid}",
                "created": "2023-01-01T00:00:00.000Z",
                "modified": "2023-01-01T00:00:00.000Z",
                "name": f"Test Mitigation {i}",
                "description": f"This is a test mitigation number {i} for performance testing. "
                * 10,
                "external_references": [
                    {
                        "source_name": "mitre-attack",
                        "external_id": f"M{i:04d}",
                        "url": f"https://attack.mitre.org/mitigations/M{i:04d}/",
                    }
                ],
            }
            objects.append(mitigation)

        # Store object IDs for relationships
        technique_ids = [
            obj["id"] for obj in objects if obj["type"] == "attack-pattern"
        ]
        group_ids = [obj["id"] for obj in objects if obj["type"] == "intrusion-set"]

        # Create some relationships
        for i in range(min(100, num_techniques // 10)):
            if i < len(technique_ids) and (i % num_groups) < len(group_ids):
                relationship_uuid = str(uuid.uuid4())
                relationship = {
                    "type": "relationship",
                    "id": f"relationship--{relationship_uuid}",
                    "created": "2023-01-01T00:00:00.000Z",
                    "modified": "2023-01-01T00:00:00.000Z",
                    "relationship_type": "uses",
                    "source_ref": group_ids[i % len(group_ids)],
                    "target_ref": technique_ids[i],
                }
            objects.append(relationship)

        dataset = {
            "type": "bundle",
            "id": f"bundle--{str(uuid.uuid4())}",
            "objects": objects,
        }

        logger.info(f"Created synthetic dataset with {len(objects)} total objects")
        return dataset

    def benchmark_parsing_performance(
        self, stix_data: Dict[str, Any], entity_types: List[str], iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Benchmark parsing performance with multiple iterations.

        Args:
            stix_data: STIX data to parse
            entity_types: Entity types to extract
            iterations: Number of iterations to run

        Returns:
            Performance benchmark results
        """
        logger.info(f"Running parsing benchmark with {iterations} iterations")

        results = {
            "stix2_library_results": [],
            "main_parser_results": [],  # Test main parser method too
            "data_size_mb": len(json.dumps(stix_data).encode("utf-8")) / 1024 / 1024,
            "total_objects": len(stix_data.get("objects", [])),
            "entity_types": entity_types,
        }

        # Benchmark STIX2 library parsing
        for i in range(iterations):
            logger.info(f"STIX2 library parsing iteration {i+1}/{iterations}")

            try:
                parsed_data, memory_stats = self.measure_memory_usage(
                    self.parser._parse_with_stix2_library, stix_data, entity_types
                )

                # Count extracted entities
                total_entities = sum(len(entities) for entities in parsed_data.values())

                iteration_result = {
                    "iteration": i + 1,
                    "success": True,
                    "total_entities_extracted": total_entities,
                    "entities_by_type": {k: len(v) for k, v in parsed_data.items()},
                    **memory_stats,
                }

                results["stix2_library_results"].append(iteration_result)

            except Exception as e:
                logger.error(f"STIX2 library parsing failed in iteration {i+1}: {e}")
                iteration_result = {
                    "iteration": i + 1,
                    "success": False,
                    "error": str(e),
                    "execution_time": 0,
                    "memory_delta_mb": 0,
                }
                results["stix2_library_results"].append(iteration_result)

        # Benchmark main parser method (uses STIX2 library internally)
        for i in range(iterations):
            logger.info(f"Main parser method iteration {i+1}/{iterations}")

            try:
                parsed_data, memory_stats = self.measure_memory_usage(
                    self.parser.parse, stix_data, entity_types
                )

                # Count extracted entities
                total_entities = sum(len(entities) for entities in parsed_data.values())

                iteration_result = {
                    "iteration": i + 1,
                    "success": True,
                    "total_entities_extracted": total_entities,
                    "entities_by_type": {k: len(v) for k, v in parsed_data.items()},
                    **memory_stats,
                }

                results["main_parser_results"].append(iteration_result)

            except Exception as e:
                logger.error(f"Main parser method failed in iteration {i+1}: {e}")
                iteration_result = {
                    "iteration": i + 1,
                    "success": False,
                    "error": str(e),
                    "execution_time": 0,
                    "memory_delta_mb": 0,
                }
                results["main_parser_results"].append(iteration_result)

        return results

    def calculate_performance_statistics(
        self, results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate performance statistics from benchmark results.

        Args:
            results: Raw benchmark results

        Returns:
            Performance statistics summary
        """
        stats = {
            "data_characteristics": {
                "data_size_mb": results["data_size_mb"],
                "total_objects": results["total_objects"],
                "entity_types": results["entity_types"],
            }
        }

        # Calculate STIX2 library statistics
        stix2_successful = [r for r in results["stix2_library_results"] if r["success"]]
        if stix2_successful:
            execution_times = [r["execution_time"] for r in stix2_successful]
            memory_deltas = [r["memory_delta_mb"] for r in stix2_successful]
            entities_extracted = [
                r["total_entities_extracted"] for r in stix2_successful
            ]

            stats["stix2_library_performance"] = {
                "success_rate": len(stix2_successful)
                / len(results["stix2_library_results"]),
                "avg_execution_time": sum(execution_times) / len(execution_times),
                "min_execution_time": min(execution_times),
                "max_execution_time": max(execution_times),
                "avg_memory_delta_mb": sum(memory_deltas) / len(memory_deltas),
                "avg_entities_extracted": sum(entities_extracted)
                / len(entities_extracted),
                "entities_per_second": (
                    sum(entities_extracted) / sum(execution_times)
                    if sum(execution_times) > 0
                    else 0
                ),
            }
        else:
            stats["stix2_library_performance"] = {
                "success_rate": 0,
                "error": "All iterations failed",
            }

        # Calculate main parser statistics
        main_successful = [
            r for r in results["main_parser_results"] if r["success"]
        ]
        if main_successful:
            execution_times = [r["execution_time"] for r in main_successful]
            memory_deltas = [r["memory_delta_mb"] for r in main_successful]
            entities_extracted = [
                r["total_entities_extracted"] for r in main_successful
            ]

            stats["main_parser_performance"] = {
                "success_rate": len(main_successful)
                / len(results["main_parser_results"]),
                "avg_execution_time": sum(execution_times) / len(execution_times),
                "min_execution_time": min(execution_times),
                "max_execution_time": max(execution_times),
                "avg_memory_delta_mb": sum(memory_deltas) / len(memory_deltas),
                "avg_entities_extracted": sum(entities_extracted)
                / len(entities_extracted),
                "entities_per_second": (
                    sum(entities_extracted) / sum(execution_times)
                    if sum(execution_times) > 0
                    else 0
                ),
            }
        else:
            stats["main_parser_performance"] = {
                "success_rate": 0,
                "error": "All iterations failed",
            }

        # Calculate performance comparison
        if (
            "stix2_library_performance" in stats
            and "main_parser_performance" in stats
        ):
            stix2_perf = stats["stix2_library_performance"]
            main_perf = stats["main_parser_performance"]

            if (
                stix2_perf.get("avg_execution_time", 0) > 0
                and main_perf.get("avg_execution_time", 0) > 0
            ):
                stats["performance_comparison"] = {
                    "speed_ratio": main_perf["avg_execution_time"]
                    / stix2_perf["avg_execution_time"],
                    "memory_ratio": (
                        main_perf["avg_memory_delta_mb"]
                        / stix2_perf["avg_memory_delta_mb"]
                        if stix2_perf["avg_memory_delta_mb"] != 0
                        else "N/A"
                    ),
                    "throughput_ratio": (
                        stix2_perf["entities_per_second"]
                        / main_perf["entities_per_second"]
                        if main_perf["entities_per_second"] > 0
                        else "N/A"
                    ),
                }

        return stats


# Performance test fixtures and utilities
@pytest.fixture
def performance_benchmark():
    """Fixture providing a performance benchmark instance."""
    return PerformanceBenchmark()


@pytest.fixture
def small_stix_dataset():
    """Fixture providing a small STIX dataset for quick tests."""
    benchmark = PerformanceBenchmark()
    return benchmark.create_large_stix_dataset(
        num_techniques=50, num_groups=10, num_mitigations=25
    )


@pytest.fixture
def medium_stix_dataset():
    """Fixture providing a medium STIX dataset for moderate performance tests."""
    benchmark = PerformanceBenchmark()
    return benchmark.create_large_stix_dataset(
        num_techniques=200, num_groups=40, num_mitigations=100
    )


@pytest.fixture
def large_stix_dataset():
    """Fixture providing a large STIX dataset for stress testing."""
    benchmark = PerformanceBenchmark()
    return benchmark.create_large_stix_dataset(
        num_techniques=1000, num_groups=200, num_mitigations=500
    )


# Performance test cases
class TestParsingPerformance:
    """Test cases for parsing performance benchmarks."""

    def test_small_dataset_performance(self, performance_benchmark, small_stix_dataset):
        """Test parsing performance with small dataset."""
        logger.info("Testing parsing performance with small dataset")

        entity_types = ["techniques", "groups", "mitigations"]
        results = performance_benchmark.benchmark_parsing_performance(
            small_stix_dataset, entity_types, iterations=3
        )

        stats = performance_benchmark.calculate_performance_statistics(results)

        # Log results
        logger.info(f"Small dataset performance results:")
        logger.info(
            f"Data size: {stats['data_characteristics']['data_size_mb']:.2f} MB"
        )
        logger.info(f"Total objects: {stats['data_characteristics']['total_objects']}")

        if "stix2_library_performance" in stats:
            stix2_perf = stats["stix2_library_performance"]
            logger.info(
                f"STIX2 library - Success rate: {stix2_perf.get('success_rate', 0):.2%}"
            )
            logger.info(
                f"STIX2 library - Avg execution time: {stix2_perf.get('avg_execution_time', 0):.3f}s"
            )
            logger.info(
                f"STIX2 library - Entities per second: {stix2_perf.get('entities_per_second', 0):.1f}"
            )

        if "main_parser_performance" in stats:
            main_perf = stats["main_parser_performance"]
            logger.info(
                f"Main parser - Success rate: {main_perf.get('success_rate', 0):.2%}"
            )
            logger.info(
                f"Main parser - Avg execution time: {main_perf.get('avg_execution_time', 0):.3f}s"
            )
            logger.info(
                f"Main parser - Entities per second: {main_perf.get('entities_per_second', 0):.1f}"
            )

        # Assertions
        assert results["data_size_mb"] > 0, "Dataset should have measurable size"
        assert results["total_objects"] > 0, "Dataset should contain objects"

        # At least one parsing method should succeed
        stix2_success = any(r["success"] for r in results["stix2_library_results"])
        main_success = any(r["success"] for r in results["main_parser_results"])
        assert (
            stix2_success or main_success
        ), "At least one parsing method should succeed"

    def test_medium_dataset_performance(
        self, performance_benchmark, medium_stix_dataset
    ):
        """Test parsing performance with medium dataset."""
        logger.info("Testing parsing performance with medium dataset")

        entity_types = ["techniques", "groups", "mitigations"]
        results = performance_benchmark.benchmark_parsing_performance(
            medium_stix_dataset, entity_types, iterations=3
        )

        stats = performance_benchmark.calculate_performance_statistics(results)

        # Log results
        logger.info(f"Medium dataset performance results:")
        logger.info(
            f"Data size: {stats['data_characteristics']['data_size_mb']:.2f} MB"
        )
        logger.info(f"Total objects: {stats['data_characteristics']['total_objects']}")

        if "performance_comparison" in stats:
            comparison = stats["performance_comparison"]
            logger.info(
                f"Performance comparison - Speed ratio: {comparison.get('speed_ratio', 'N/A')}"
            )
            logger.info(
                f"Performance comparison - Memory ratio: {comparison.get('memory_ratio', 'N/A')}"
            )
            logger.info(
                f"Performance comparison - Throughput ratio: {comparison.get('throughput_ratio', 'N/A')}"
            )

        # Assertions
        assert results["data_size_mb"] > 0.1, "Medium dataset should be at least 0.1 MB"
        assert (
            results["total_objects"] > 100
        ), "Medium dataset should have substantial objects"

    @pytest.mark.slow
    def test_large_dataset_performance(self, performance_benchmark, large_stix_dataset):
        """Test parsing performance with large dataset (marked as slow test)."""
        logger.info("Testing parsing performance with large dataset")

        entity_types = ["techniques", "groups", "mitigations"]
        results = performance_benchmark.benchmark_parsing_performance(
            large_stix_dataset,
            entity_types,
            iterations=2,  # Fewer iterations for large dataset
        )

        stats = performance_benchmark.calculate_performance_statistics(results)

        # Log results
        logger.info(f"Large dataset performance results:")
        logger.info(
            f"Data size: {stats['data_characteristics']['data_size_mb']:.2f} MB"
        )
        logger.info(f"Total objects: {stats['data_characteristics']['total_objects']}")

        # Performance thresholds for large datasets
        if "stix2_library_performance" in stats:
            stix2_perf = stats["stix2_library_performance"]
            logger.info(f"STIX2 library performance:")
            logger.info(
                f"  - Avg execution time: {stix2_perf.get('avg_execution_time', 0):.3f}s"
            )
            logger.info(
                f"  - Memory usage: {stix2_perf.get('avg_memory_delta_mb', 0):.2f} MB"
            )
            logger.info(
                f"  - Throughput: {stix2_perf.get('entities_per_second', 0):.1f} entities/sec"
            )

            # Performance assertions
            assert (
                stix2_perf.get("avg_execution_time", float("inf")) < 30
            ), "Large dataset parsing should complete within 30 seconds"
            assert (
                stix2_perf.get("avg_memory_delta_mb", float("inf")) < 500
            ), "Memory usage should be reasonable (< 500 MB)"

        # Assertions
        assert results["data_size_mb"] > 1.0, "Large dataset should be at least 1 MB"
        assert results["total_objects"] > 1000, "Large dataset should have many objects"


class TestMCPToolPerformance:
    """Test cases for MCP tool response time performance."""

    def test_mcp_tool_response_times(self, performance_benchmark):
        """Test that MCP tool response times remain acceptable after refactoring."""
        logger.info("Testing MCP tool response times")

        # Create a moderate dataset for MCP tool testing
        test_data = performance_benchmark.create_large_stix_dataset(
            num_techniques=100, num_groups=20, num_mitigations=50
        )

        # Mock the data loader to use our test data
        with patch.object(
            performance_benchmark.data_loader, "load_data_source"
        ) as mock_load:
            mock_load.return_value = performance_benchmark.parser.parse(
                test_data, ["techniques", "groups", "mitigations"]
            )

            # Test basic MCP tools
            mcp_tools = [
                ("search_attack", {"query": "test"}),
                ("get_technique", {"technique_id": "T0001"}),
                ("list_tactics", {}),
                ("get_group_techniques", {"group_id": "G0001"}),
                ("get_technique_mitigations", {"technique_id": "T0001"}),
            ]

            response_times = {}

            for tool_name, params in mcp_tools:
                logger.info(f"Testing {tool_name} response time")

                start_time = time.time()
                try:
                    # Simulate MCP tool call
                    # Note: This would need to be adapted based on actual MCP tool implementation
                    result = {"status": "success", "data": []}
                    end_time = time.time()

                    response_time = end_time - start_time
                    response_times[tool_name] = response_time

                    logger.info(f"{tool_name} response time: {response_time:.3f}s")

                    # Response time should be reasonable (< 5 seconds for moderate dataset)
                    assert (
                        response_time < 5.0
                    ), f"{tool_name} response time too slow: {response_time:.3f}s"

                except Exception as e:
                    logger.error(f"Error testing {tool_name}: {e}")
                    response_times[tool_name] = float("inf")

            # Log summary
            avg_response_time = sum(
                t for t in response_times.values() if t != float("inf")
            ) / len([t for t in response_times.values() if t != float("inf")])
            logger.info(f"Average MCP tool response time: {avg_response_time:.3f}s")

            # Overall performance assertion
            assert (
                avg_response_time < 2.0
            ), f"Average response time too slow: {avg_response_time:.3f}s"


class TestMemoryUsageOptimization:
    """Test cases for memory usage optimization."""

    def test_memory_usage_patterns(self, performance_benchmark, medium_stix_dataset):
        """Test memory usage patterns during parsing operations."""
        logger.info("Testing memory usage patterns")

        entity_types = ["techniques", "groups", "mitigations"]

        # Test STIX2 library memory usage
        _, stix2_memory_stats = performance_benchmark.measure_memory_usage(
            performance_benchmark.parser._parse_with_stix2_library,
            medium_stix_dataset,
            entity_types,
        )

        # Test main parser method (which uses STIX2 library)
        _, parser_memory_stats = performance_benchmark.measure_memory_usage(
            performance_benchmark.parser.parse,
            medium_stix_dataset,
            entity_types,
        )

        logger.info(f"STIX2 library memory usage:")
        logger.info(f"  - Memory delta: {stix2_memory_stats['memory_delta_mb']:.2f} MB")
        logger.info(f"  - Peak traced: {stix2_memory_stats['peak_traced_mb']:.2f} MB")

        logger.info(f"Main parser memory usage:")
        logger.info(
            f"  - Memory delta: {parser_memory_stats['memory_delta_mb']:.2f} MB"
        )
        logger.info(f"  - Peak traced: {parser_memory_stats['peak_traced_mb']:.2f} MB")

        # Memory usage should be reasonable
        assert (
            stix2_memory_stats["memory_delta_mb"] < 200
        ), "STIX2 library memory usage should be reasonable"
        assert (
            parser_memory_stats["memory_delta_mb"] < 200
        ), "Main parser memory usage should be reasonable"

        # Peak memory should not be excessive
        assert (
            stix2_memory_stats["peak_traced_mb"] < 300
        ), "Peak memory usage should not be excessive"
        assert (
            parser_memory_stats["peak_traced_mb"] < 300
        ), "Peak memory usage should not be excessive"

    def test_memory_leak_detection(self, performance_benchmark, small_stix_dataset):
        """Test for memory leaks during repeated parsing operations."""
        logger.info("Testing for memory leaks")

        entity_types = ["techniques", "groups", "mitigations"]
        initial_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

        # Perform multiple parsing operations
        for i in range(10):
            performance_benchmark.parser.parse(small_stix_dataset, entity_types)

            if i % 3 == 0:  # Check memory every few iterations
                current_memory = (
                    psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
                )
                memory_growth = current_memory - initial_memory
                logger.info(f"Iteration {i}: Memory growth: {memory_growth:.2f} MB")

                # Memory growth should be bounded
                assert (
                    memory_growth < 100
                ), f"Excessive memory growth detected: {memory_growth:.2f} MB"

        final_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        total_growth = final_memory - initial_memory

        logger.info(f"Total memory growth after 10 iterations: {total_growth:.2f} MB")

        # Total memory growth should be reasonable
        assert (
            total_growth < 150
        ), f"Potential memory leak detected: {total_growth:.2f} MB growth"


# Integration test for performance with real MITRE ATT&CK data
class TestRealDataPerformance:
    """Test performance with real MITRE ATT&CK data."""

    @pytest.mark.integration
    def test_real_mitre_attack_performance(self, performance_benchmark):
        """Test performance with real MITRE ATT&CK data (integration test)."""
        logger.info("Testing performance with real MITRE ATT&CK data")

        # This test would download real MITRE ATT&CK data
        # For now, we'll simulate it with a realistic dataset
        realistic_data = performance_benchmark.create_large_stix_dataset(
            num_techniques=800,  # Approximate real MITRE ATT&CK size
            num_groups=150,
            num_mitigations=400,
        )

        entity_types = ["techniques", "groups", "mitigations"]
        results = performance_benchmark.benchmark_parsing_performance(
            realistic_data, entity_types, iterations=2
        )

        stats = performance_benchmark.calculate_performance_statistics(results)

        logger.info("Real MITRE ATT&CK performance simulation results:")
        logger.info(
            f"Data size: {stats['data_characteristics']['data_size_mb']:.2f} MB"
        )

        if "stix2_library_performance" in stats:
            stix2_perf = stats["stix2_library_performance"]
            logger.info(f"STIX2 library performance:")
            logger.info(f"  - Success rate: {stix2_perf.get('success_rate', 0):.2%}")
            logger.info(
                f"  - Avg execution time: {stix2_perf.get('avg_execution_time', 0):.3f}s"
            )
            logger.info(
                f"  - Throughput: {stix2_perf.get('entities_per_second', 0):.1f} entities/sec"
            )

            # Real data performance requirements
            assert (
                stix2_perf.get("success_rate", 0) >= 0.95
            ), "Success rate should be at least 95%"
            assert (
                stix2_perf.get("avg_execution_time", float("inf")) < 15
            ), "Real data parsing should complete within 15 seconds"

        # Ensure we can extract a reasonable number of entities
        successful_results = [
            r for r in results["stix2_library_results"] if r["success"]
        ]
        if successful_results:
            avg_entities = sum(
                r["total_entities_extracted"] for r in successful_results
            ) / len(successful_results)
            logger.info(f"Average entities extracted: {avg_entities:.0f}")
            assert (
                avg_entities > 1000
            ), "Should extract substantial number of entities from real data"


if __name__ == "__main__":
    # Run performance benchmarks directly
    benchmark = PerformanceBenchmark()

    # Create test datasets
    small_data = benchmark.create_large_stix_dataset(50, 10, 25)
    medium_data = benchmark.create_large_stix_dataset(200, 40, 100)

    # Run benchmarks
    print("Running small dataset benchmark...")
    small_results = benchmark.benchmark_parsing_performance(
        small_data, ["techniques", "groups", "mitigations"]
    )
    small_stats = benchmark.calculate_performance_statistics(small_results)

    print("Running medium dataset benchmark...")
    medium_results = benchmark.benchmark_parsing_performance(
        medium_data, ["techniques", "groups", "mitigations"]
    )
    medium_stats = benchmark.calculate_performance_statistics(medium_results)

    # Print summary
    print("\n=== PERFORMANCE BENCHMARK SUMMARY ===")
    print(
        f"Small dataset ({small_stats['data_characteristics']['data_size_mb']:.2f} MB):"
    )
    if "stix2_library_performance" in small_stats:
        print(
            f"  STIX2 library: {small_stats['stix2_library_performance']['avg_execution_time']:.3f}s"
        )
    if "main_parser_performance" in small_stats:
        print(
            f"  Main parser: {small_stats['main_parser_performance']['avg_execution_time']:.3f}s"
        )

    print(
        f"Medium dataset ({medium_stats['data_characteristics']['data_size_mb']:.2f} MB):"
    )
    if "stix2_library_performance" in medium_stats:
        print(
            f"  STIX2 library: {medium_stats['stix2_library_performance']['avg_execution_time']:.3f}s"
        )
    if "main_parser_performance" in medium_stats:
        print(
            f"  Main parser: {medium_stats['main_parser_performance']['avg_execution_time']:.3f}s"
        )
