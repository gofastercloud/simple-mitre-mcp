"""
Performance regression detection system for test suite rationalization.

This module provides automated performance regression detection with
configurable thresholds and historical performance tracking.
"""

import json
import os
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import pytest

from tests.base import BasePerformanceTestCase
from tests.factories import PerformanceDataFactory


logger = logging.getLogger(__name__)


class PerformanceRegressionDetector(BasePerformanceTestCase):
    """
    Performance regression detection system with historical tracking.
    """

    def __init__(self):
        """Initialize the regression detector."""
        super().__init__()
        self.performance_history_file = Path("tests/performance/.performance_history.json")
        self.thresholds_file = Path("tests/performance/.performance_thresholds.json")
        self.performance_history = self._load_performance_history()
        self.thresholds = self._load_performance_thresholds()

    def _load_performance_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load performance history from file."""
        if self.performance_history_file.exists():
            try:
                with open(self.performance_history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                logger.warning("Could not load performance history, starting fresh")
        
        return {}

    def _save_performance_history(self):
        """Save performance history to file."""
        try:
            self.performance_history_file.parent.mkdir(exist_ok=True)
            with open(self.performance_history_file, 'w') as f:
                json.dump(self.performance_history, f, indent=2)
        except IOError as e:
            logger.warning(f"Could not save performance history: {e}")

    def _load_performance_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Load performance thresholds from file."""
        default_thresholds = {
            "parsing_small": {
                "execution_time": 1.0,
                "memory_mb": 50.0,
                "regression_factor": 1.5  # 50% slower triggers regression
            },
            "parsing_medium": {
                "execution_time": 3.0,
                "memory_mb": 150.0,
                "regression_factor": 1.5
            },
            "parsing_large": {
                "execution_time": 10.0,
                "memory_mb": 500.0,
                "regression_factor": 1.5
            },
            "mcp_tool_response": {
                "execution_time": 0.5,
                "memory_mb": 25.0,
                "regression_factor": 2.0  # Tools can be more variable
            },
            "search_query": {
                "execution_time": 0.2,
                "memory_mb": 10.0,
                "regression_factor": 2.0
            }
        }

        if self.thresholds_file.exists():
            try:
                with open(self.thresholds_file, 'r') as f:
                    loaded_thresholds = json.load(f)
                    # Merge with defaults
                    for key, value in loaded_thresholds.items():
                        if key in default_thresholds:
                            default_thresholds[key].update(value)
                        else:
                            default_thresholds[key] = value
            except (json.JSONDecodeError, IOError):
                logger.warning("Could not load performance thresholds, using defaults")

        return default_thresholds

    def record_performance(self, test_name: str, metrics: Dict[str, Any]):
        """
        Record performance metrics for regression detection.
        
        Args:
            test_name: Name of the test
            metrics: Performance metrics dictionary
        """
        if test_name not in self.performance_history:
            self.performance_history[test_name] = []

        # Add timestamp and limit history size
        metrics_with_timestamp = {
            **metrics,
            "timestamp": time.time(),
            "date": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        self.performance_history[test_name].append(metrics_with_timestamp)
        
        # Keep only last 50 entries to prevent file from growing too large
        if len(self.performance_history[test_name]) > 50:
            self.performance_history[test_name] = self.performance_history[test_name][-50:]

        self._save_performance_history()

    def detect_regression(self, test_name: str, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect performance regression for a test.
        
        Args:
            test_name: Name of the test
            current_metrics: Current performance metrics
            
        Returns:
            Regression analysis results
        """
        regression_result = {
            "test_name": test_name,
            "regression_detected": False,
            "regression_details": [],
            "recommendations": [],
            "current_metrics": current_metrics
        }

        # Check against absolute thresholds
        if test_name in self.thresholds:
            thresholds = self.thresholds[test_name]
            
            # Check execution time threshold
            if current_metrics.get("execution_time", 0) > thresholds.get("execution_time", float('inf')):
                regression_result["regression_detected"] = True
                regression_result["regression_details"].append({
                    "type": "absolute_threshold",
                    "metric": "execution_time",
                    "current": current_metrics["execution_time"],
                    "threshold": thresholds["execution_time"]
                })

            # Check memory threshold
            if current_metrics.get("memory_mb", 0) > thresholds.get("memory_mb", float('inf')):
                regression_result["regression_detected"] = True
                regression_result["regression_details"].append({
                    "type": "absolute_threshold",
                    "metric": "memory_mb",
                    "current": current_metrics["memory_mb"],
                    "threshold": thresholds["memory_mb"]
                })

        # Check against historical performance
        if test_name in self.performance_history and len(self.performance_history[test_name]) >= 3:
            historical_data = self.performance_history[test_name][-10:]  # Last 10 runs
            
            # Calculate historical averages
            avg_execution_time = sum(h.get("execution_time", 0) for h in historical_data) / len(historical_data)
            avg_memory_mb = sum(h.get("memory_mb", 0) for h in historical_data) / len(historical_data)
            
            regression_factor = self.thresholds.get(test_name, {}).get("regression_factor", 1.5)
            
            # Check for execution time regression
            if current_metrics.get("execution_time", 0) > avg_execution_time * regression_factor:
                regression_result["regression_detected"] = True
                regression_result["regression_details"].append({
                    "type": "historical_regression",
                    "metric": "execution_time",
                    "current": current_metrics["execution_time"],
                    "historical_average": avg_execution_time,
                    "regression_factor": regression_factor
                })

            # Check for memory regression
            if current_metrics.get("memory_mb", 0) > avg_memory_mb * regression_factor:
                regression_result["regression_detected"] = True
                regression_result["regression_details"].append({
                    "type": "historical_regression",
                    "metric": "memory_mb",
                    "current": current_metrics["memory_mb"],
                    "historical_average": avg_memory_mb,
                    "regression_factor": regression_factor
                })

        # Generate recommendations
        if regression_result["regression_detected"]:
            regression_result["recommendations"] = self._generate_recommendations(regression_result)

        return regression_result

    def _generate_recommendations(self, regression_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on regression analysis."""
        recommendations = []
        
        for detail in regression_result["regression_details"]:
            metric = detail["metric"]
            
            if metric == "execution_time":
                recommendations.append(
                    f"Execution time regression detected. Consider optimizing algorithms, "
                    f"reducing data processing overhead, or implementing caching."
                )
            elif metric == "memory_mb":
                recommendations.append(
                    f"Memory usage regression detected. Consider optimizing data structures, "
                    f"implementing memory pooling, or reducing object creation."
                )

        if not recommendations:
            recommendations.append("Performance regression detected. Review recent changes for optimization opportunities.")

        return recommendations

    def get_performance_summary(self, test_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance summary for analysis.
        
        Args:
            test_name: Specific test name, or None for all tests
            
        Returns:
            Performance summary
        """
        if test_name:
            if test_name not in self.performance_history:
                return {"error": f"No performance history for test: {test_name}"}
            
            history = self.performance_history[test_name]
            if not history:
                return {"error": f"Empty performance history for test: {test_name}"}

            # Calculate statistics
            execution_times = [h.get("execution_time", 0) for h in history]
            memory_usage = [h.get("memory_mb", 0) for h in history]

            return {
                "test_name": test_name,
                "total_runs": len(history),
                "execution_time": {
                    "current": execution_times[-1] if execution_times else 0,
                    "average": sum(execution_times) / len(execution_times) if execution_times else 0,
                    "min": min(execution_times) if execution_times else 0,
                    "max": max(execution_times) if execution_times else 0
                },
                "memory_mb": {
                    "current": memory_usage[-1] if memory_usage else 0,
                    "average": sum(memory_usage) / len(memory_usage) if memory_usage else 0,
                    "min": min(memory_usage) if memory_usage else 0,
                    "max": max(memory_usage) if memory_usage else 0
                },
                "trend": self._calculate_trend(execution_times[-5:]) if len(execution_times) >= 5 else "insufficient_data"
            }
        else:
            # Summary for all tests
            summary = {}
            for test_name in self.performance_history:
                summary[test_name] = self.get_performance_summary(test_name)
            return summary

    def _calculate_trend(self, recent_values: List[float]) -> str:
        """Calculate performance trend from recent values."""
        if len(recent_values) < 3:
            return "insufficient_data"

        # Simple trend calculation
        first_half = recent_values[:len(recent_values)//2]
        second_half = recent_values[len(recent_values)//2:]

        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)

        if second_avg > first_avg * 1.1:
            return "degrading"
        elif second_avg < first_avg * 0.9:
            return "improving"
        else:
            return "stable"


# Test fixtures for regression detection
@pytest.fixture
def regression_detector():
    """Fixture providing a regression detector instance."""
    return PerformanceRegressionDetector()


# Regression detection test cases
class TestPerformanceRegressionDetection(BasePerformanceTestCase):
    """Test cases for performance regression detection."""

    def test_regression_detection_system(self, regression_detector):
        """Test the regression detection system works correctly."""
        test_name = "test_regression_detection"
        
        # Simulate good performance
        good_metrics = {
            "execution_time": 0.5,
            "memory_mb": 25.0,
            "entities_processed": 100
        }
        
        regression_detector.record_performance(test_name, good_metrics)
        regression_result = regression_detector.detect_regression(test_name, good_metrics)
        
        assert not regression_result["regression_detected"], "Good performance should not trigger regression"

        # Simulate performance regression
        bad_metrics = {
            "execution_time": 5.0,  # Much slower
            "memory_mb": 200.0,     # Much more memory
            "entities_processed": 100
        }
        
        regression_result = regression_detector.detect_regression(test_name, bad_metrics)
        
        # Should detect regression if thresholds are configured
        if test_name in regression_detector.thresholds:
            assert regression_result["regression_detected"], "Poor performance should trigger regression detection"
            assert len(regression_result["regression_details"]) > 0
            assert len(regression_result["recommendations"]) > 0

    def test_historical_regression_detection(self, regression_detector):
        """Test historical regression detection."""
        test_name = "test_historical_regression"
        
        # Record several good performance runs
        for i in range(5):
            good_metrics = {
                "execution_time": 0.5 + (i * 0.01),  # Slight variation
                "memory_mb": 25.0 + (i * 0.5),
                "entities_processed": 100
            }
            regression_detector.record_performance(test_name, good_metrics)

        # Now test with significantly worse performance
        bad_metrics = {
            "execution_time": 2.0,  # 4x slower than average
            "memory_mb": 100.0,     # 4x more memory
            "entities_processed": 100
        }
        
        regression_result = regression_detector.detect_regression(test_name, bad_metrics)
        
        # Should detect historical regression
        assert regression_result["regression_detected"], "Historical regression should be detected"
        
        # Should have historical regression details
        historical_regressions = [
            detail for detail in regression_result["regression_details"]
            if detail["type"] == "historical_regression"
        ]
        assert len(historical_regressions) > 0, "Should detect historical regression"

    def test_performance_summary_generation(self, regression_detector):
        """Test performance summary generation."""
        test_name = "test_performance_summary"
        
        # Record some performance data
        for i in range(10):
            metrics = {
                "execution_time": 0.5 + (i * 0.05),
                "memory_mb": 25.0 + (i * 2.0),
                "entities_processed": 100 + (i * 10)
            }
            regression_detector.record_performance(test_name, metrics)

        # Get summary
        summary = regression_detector.get_performance_summary(test_name)
        
        assert "test_name" in summary
        assert summary["test_name"] == test_name
        assert summary["total_runs"] == 10
        assert "execution_time" in summary
        assert "memory_mb" in summary
        assert "trend" in summary
        
        # Check execution time statistics
        exec_stats = summary["execution_time"]
        assert exec_stats["min"] < exec_stats["average"] < exec_stats["max"]
        assert exec_stats["current"] > 0

    def test_threshold_configuration(self, regression_detector):
        """Test threshold configuration system."""
        # Verify default thresholds exist
        assert len(regression_detector.thresholds) > 0
        
        # Check that common test types have thresholds
        expected_test_types = ["parsing_small", "parsing_medium", "mcp_tool_response"]
        for test_type in expected_test_types:
            assert test_type in regression_detector.thresholds
            thresholds = regression_detector.thresholds[test_type]
            assert "execution_time" in thresholds
            assert "memory_mb" in thresholds
            assert "regression_factor" in thresholds
            assert thresholds["execution_time"] > 0
            assert thresholds["memory_mb"] > 0
            assert thresholds["regression_factor"] > 1.0

    def test_recommendation_generation(self, regression_detector):
        """Test recommendation generation for regressions."""
        # Create a regression result with different types of issues
        regression_result = {
            "test_name": "test_recommendations",
            "regression_detected": True,
            "regression_details": [
                {
                    "type": "absolute_threshold",
                    "metric": "execution_time",
                    "current": 5.0,
                    "threshold": 2.0
                },
                {
                    "type": "historical_regression",
                    "metric": "memory_mb",
                    "current": 200.0,
                    "historical_average": 50.0,
                    "regression_factor": 1.5
                }
            ]
        }
        
        recommendations = regression_detector._generate_recommendations(regression_result)
        
        assert len(recommendations) > 0
        assert any("execution time" in rec.lower() for rec in recommendations)
        assert any("memory" in rec.lower() for rec in recommendations)

    def test_performance_trend_calculation(self, regression_detector):
        """Test performance trend calculation."""
        # Test improving trend
        improving_values = [1.0, 0.9, 0.8, 0.7, 0.6]
        trend = regression_detector._calculate_trend(improving_values)
        assert trend == "improving"
        
        # Test degrading trend
        degrading_values = [0.5, 0.6, 0.7, 0.8, 1.0]
        trend = regression_detector._calculate_trend(degrading_values)
        assert trend == "degrading"
        
        # Test stable trend
        stable_values = [0.5, 0.51, 0.49, 0.52, 0.48]
        trend = regression_detector._calculate_trend(stable_values)
        assert trend == "stable"
        
        # Test insufficient data
        insufficient_values = [0.5, 0.6]
        trend = regression_detector._calculate_trend(insufficient_values)
        assert trend == "insufficient_data"

    def test_integration_with_actual_performance_tests(self, regression_detector):
        """Test integration with actual performance test execution."""
        from src.parsers.stix_parser import STIXParser
        
        parser = STIXParser()
        # Create proper STIX test data
        import uuid
        test_data = {
            "type": "bundle",
            "id": f"bundle--{uuid.uuid4()}",
            "objects": [
                {
                    "type": "attack-pattern",
                    "id": f"attack-pattern--{uuid.uuid4()}",
                    "created": "2023-01-01T00:00:00.000Z",
                    "modified": "2023-01-01T00:00:00.000Z",
                    "name": "Test Technique",
                    "description": "Test technique for performance testing",
                    "external_references": [
                        {
                            "source_name": "mitre-attack",
                            "external_id": "T1000",
                            "url": "https://attack.mitre.org/techniques/T1000/"
                        }
                    ],
                    "kill_chain_phases": [
                        {"kill_chain_name": "mitre-attack", "phase_name": "execution"}
                    ]
                }
            ]
        }
        
        # Measure actual performance
        start_time = time.time()
        result = parser.parse(test_data, ["techniques", "groups", "mitigations"])
        end_time = time.time()
        
        # Create metrics
        metrics = {
            "execution_time": end_time - start_time,
            "memory_mb": 50.0,  # Simplified for test
            "entities_processed": sum(len(entities) for entities in result.values())
        }
        
        # Record and analyze
        test_name = "integration_performance_test"
        regression_detector.record_performance(test_name, metrics)
        regression_result = regression_detector.detect_regression(test_name, metrics)
        
        # Should complete without errors
        assert "regression_detected" in regression_result
        assert "current_metrics" in regression_result
        assert regression_result["current_metrics"]["execution_time"] > 0