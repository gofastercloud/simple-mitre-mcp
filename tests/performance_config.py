"""
Performance monitoring configuration and utilities for test execution optimization.

This module provides configuration and utilities for monitoring test performance,
detecting regressions, and optimizing test execution.
"""

import time
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration for different test categories."""
    category: str
    max_duration: float  # Maximum allowed duration in seconds
    warning_duration: float  # Duration that triggers a warning
    target_duration: float  # Target optimal duration


@dataclass
class TestExecutionMetrics:
    """Metrics for test execution performance."""
    test_name: str
    category: str
    duration: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class PerformanceMonitor:
    """Monitor and track test execution performance."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "tests/.performance_config.json"
        self.metrics_file = "tests/.performance_history.json"
        self.thresholds = self._load_thresholds()
        self.metrics_history = self._load_metrics_history()
    
    def _load_thresholds(self) -> Dict[str, PerformanceThreshold]:
        """Load performance thresholds from configuration."""
        default_thresholds = {
            "unit": PerformanceThreshold("unit", 1.0, 0.5, 0.1),
            "integration": PerformanceThreshold("integration", 10.0, 5.0, 2.0),
            "performance": PerformanceThreshold("performance", 60.0, 30.0, 15.0),
            "compatibility": PerformanceThreshold("compatibility", 15.0, 10.0, 5.0),
            "deployment": PerformanceThreshold("deployment", 20.0, 15.0, 8.0),
            "e2e": PerformanceThreshold("e2e", 120.0, 60.0, 30.0)
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    
                for category, data in config_data.get("thresholds", {}).items():
                    if category in default_thresholds:
                        default_thresholds[category] = PerformanceThreshold(
                            category=category,
                            max_duration=data.get("max_duration", default_thresholds[category].max_duration),
                            warning_duration=data.get("warning_duration", default_thresholds[category].warning_duration),
                            target_duration=data.get("target_duration", default_thresholds[category].target_duration)
                        )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load performance config: {e}")
        
        return default_thresholds
    
    def _load_metrics_history(self) -> List[Dict[str, Any]]:
        """Load historical performance metrics."""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return []
    
    def record_test_metrics(self, metrics: TestExecutionMetrics):
        """Record test execution metrics."""
        self.metrics_history.append(asdict(metrics))
        
        # Keep only last 1000 entries to prevent file from growing too large
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        # Save to file
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)
    
    def check_performance_regression(self, test_name: str, current_duration: float) -> Dict[str, Any]:
        """Check if current test duration indicates a performance regression."""
        # Get historical data for this test
        historical_durations = [
            m["duration"] for m in self.metrics_history
            if m["test_name"] == test_name
        ]
        
        if len(historical_durations) < 3:
            return {"regression": False, "reason": "insufficient_history"}
        
        # Calculate baseline (median of last 10 runs)
        recent_durations = historical_durations[-10:]
        baseline = sorted(recent_durations)[len(recent_durations) // 2]
        
        # Check for regression (>50% increase from baseline)
        regression_threshold = baseline * 1.5
        is_regression = current_duration > regression_threshold
        
        return {
            "regression": is_regression,
            "current_duration": current_duration,
            "baseline_duration": baseline,
            "regression_threshold": regression_threshold,
            "increase_percentage": ((current_duration - baseline) / baseline) * 100 if baseline > 0 else 0
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Generate performance summary report."""
        if not self.metrics_history:
            return {"error": "No performance data available"}
        
        # Group by category
        category_stats = {}
        for metric in self.metrics_history:
            category = metric["category"]
            if category not in category_stats:
                category_stats[category] = []
            category_stats[category].append(metric["duration"])
        
        # Calculate statistics for each category
        summary = {}
        for category, durations in category_stats.items():
            if durations:
                summary[category] = {
                    "count": len(durations),
                    "avg_duration": sum(durations) / len(durations),
                    "min_duration": min(durations),
                    "max_duration": max(durations),
                    "median_duration": sorted(durations)[len(durations) // 2],
                    "threshold": asdict(self.thresholds.get(category, self.thresholds["unit"]))
                }
        
        return summary
    
    def generate_optimization_recommendations(self) -> List[str]:
        """Generate recommendations for test execution optimization."""
        recommendations = []
        summary = self.get_performance_summary()
        
        for category, stats in summary.items():
            if "error" in summary:
                continue
                
            threshold = self.thresholds.get(category)
            if not threshold:
                continue
            
            avg_duration = stats["avg_duration"]
            max_duration = stats["max_duration"]
            
            # Check if average exceeds warning threshold
            if avg_duration > threshold.warning_duration:
                recommendations.append(
                    f"{category.title()} tests average {avg_duration:.2f}s "
                    f"(warning threshold: {threshold.warning_duration}s) - consider optimization"
                )
            
            # Check if any tests exceed maximum threshold
            if max_duration > threshold.max_duration:
                recommendations.append(
                    f"{category.title()} tests have maximum duration {max_duration:.2f}s "
                    f"(max threshold: {threshold.max_duration}s) - investigate slow tests"
                )
            
            # Check if tests are much slower than target
            if avg_duration > threshold.target_duration * 2:
                recommendations.append(
                    f"{category.title()} tests are {avg_duration/threshold.target_duration:.1f}x "
                    f"slower than target - significant optimization opportunity"
                )
        
        # General recommendations
        total_tests = sum(stats["count"] for stats in summary.values() if "count" in stats)
        if total_tests > 100:
            recommendations.append(
                f"Large test suite ({total_tests} tests) - consider parallel execution"
            )
        
        return recommendations


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def pytest_runtest_call(pyfuncitem):
    """Hook to monitor individual test performance."""
    start_time = time.time()
    
    # Store start time for later use
    pyfuncitem._perf_start_time = start_time


def pytest_runtest_teardown(item, nextitem):
    """Hook to record test performance metrics."""
    if hasattr(item, '_perf_start_time'):
        duration = time.time() - item._perf_start_time
        
        # Determine test category
        test_path = str(item.fspath)
        category = "other"
        if "/unit/" in test_path:
            category = "unit"
        elif "/integration/" in test_path:
            category = "integration"
        elif "/performance/" in test_path:
            category = "performance"
        elif "/compatibility/" in test_path:
            category = "compatibility"
        elif "/deployment/" in test_path:
            category = "deployment"
        elif "/e2e/" in test_path:
            category = "e2e"
        
        # Record metrics
        metrics = TestExecutionMetrics(
            test_name=f"{item.fspath.basename}::{item.name}",
            category=category,
            duration=duration
        )
        
        performance_monitor.record_test_metrics(metrics)
        
        # Check for regression
        regression_info = performance_monitor.check_performance_regression(
            metrics.test_name, duration
        )
        
        if regression_info["regression"]:
            print(f"\nWARNING: Performance regression detected in {metrics.test_name}")
            print(f"Current: {duration:.3f}s, Baseline: {regression_info['baseline_duration']:.3f}s")
            print(f"Increase: {regression_info['increase_percentage']:.1f}%")


# Export configuration for external use
PERFORMANCE_CONFIG = {
    "thresholds": {
        category: asdict(threshold) 
        for category, threshold in performance_monitor.thresholds.items()
    },
    "parallel_execution": {
        "optimal_workers": "auto",  # Will be calculated based on CPU count
        "distribution_strategy": "worksteal",
        "chunk_size": "auto"
    },
    "optimization_settings": {
        "fixture_scoping": {
            "session": ["test_data_factory", "config_factory", "performance_factory"],
            "module": ["sample_technique", "sample_group", "sample_tactic", "sample_mitigation", 
                      "sample_stix_bundle", "attack_path_data", "coverage_gap_data", 
                      "test_config", "test_env_vars", "mock_data_loader"],
            "function": ["temp_config_file", "temp_stix_file", "isolated_temp_dir"]
        },
        "test_ordering": {
            "priority": ["unit", "integration", "deployment", "compatibility", "performance", "e2e"],
            "fast_first": True
        }
    }
}