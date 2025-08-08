#!/usr/bin/env python3
"""
Performance Benchmarking Script

This script measures test execution performance and validates improvements
against baseline requirements and targets.

Requirements addressed:
- 3.1: Test execution time improvements (30% reduction target)
- Performance monitoring and regression detection
"""

import json
import os
import subprocess
import sys
import time
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse


class PerformanceBenchmark:
    """Benchmarks test execution performance."""
    
    def __init__(self, baseline_file: str = "validation/data/performance_baseline.json"):
        self.baseline_file = baseline_file
        self.baseline_data = self._load_baseline()
        self.performance_targets = {
            "unit_tests_max": 30,      # seconds
            "integration_tests_max": 120,  # seconds
            "performance_tests_max": 300,  # seconds
            "full_suite_max": 600,     # seconds
            "improvement_target": 0.30,  # 30% improvement
            "regression_threshold": 0.10  # 10% slower is regression
        }
        
        self.test_categories = {
            "unit": {
                "path": "tests/unit/",
                "markers": ["-m", "unit"],
                "description": "Unit tests (fast, isolated)"
            },
            "integration": {
                "path": "tests/integration/",
                "markers": ["-m", "integration"],
                "description": "Integration tests (moderate speed)"
            },
            "performance": {
                "path": "tests/performance/",
                "markers": ["-m", "performance"],
                "description": "Performance tests (slow)"
            },
            "e2e": {
                "path": "tests/e2e/",
                "markers": ["-m", "e2e"],
                "description": "End-to-end tests (slowest)"
            },
            "full_suite": {
                "path": "tests/",
                "markers": [],
                "description": "Complete test suite"
            }
        }
    
    def _load_baseline(self) -> Dict[str, Any]:
        """Load baseline performance data."""
        if os.path.exists(self.baseline_file):
            try:
                with open(self.baseline_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load baseline data: {e}")
        return {}
    
    def _save_baseline(self, data: Dict[str, Any]):
        """Save baseline performance data."""
        with open(self.baseline_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Baseline data saved to {self.baseline_file}")
    
    def run_single_benchmark(self, category: str, runs: int = 3) -> Dict[str, Any]:
        """Run benchmark for a single test category."""
        if category not in self.test_categories:
            raise ValueError(f"Unknown test category: {category}")
        
        config = self.test_categories[category]
        print(f"Benchmarking {category} tests ({config['description']})...")
        
        execution_times = []
        test_counts = []
        slowest_tests_all = []
        
        for run in range(runs):
            print(f"  Run {run + 1}/{runs}...")
            
            cmd = ["uv", "run", "pytest", config["path"]] + config["markers"] + [
                "--tb=short",
                "-v",
                "--durations=10",
                "--disable-warnings"
            ]
            
            start_time = time.time()
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
                end_time = time.time()
                
                execution_time = end_time - start_time
                execution_times.append(execution_time)
                
                # Extract test count and slowest tests
                test_count = self._extract_test_count(result.stdout)
                test_counts.append(test_count)
                
                slowest_tests = self._extract_slowest_tests(result.stdout)
                slowest_tests_all.extend(slowest_tests)
                
                print(f"    Time: {execution_time:.2f}s, Tests: {test_count}, "
                      f"Result: {'PASS' if result.returncode == 0 else 'FAIL'}")
                
            except subprocess.TimeoutExpired:
                print(f"    TIMEOUT after 900s")
                execution_times.append(900)
                test_counts.append(0)
            except Exception as e:
                print(f"    ERROR: {e}")
                execution_times.append(0)
                test_counts.append(0)
        
        # Calculate statistics
        if execution_times and any(t > 0 for t in execution_times):
            valid_times = [t for t in execution_times if t > 0]
            
            return {
                "category": category,
                "runs": runs,
                "execution_times": execution_times,
                "mean_time": statistics.mean(valid_times),
                "median_time": statistics.median(valid_times),
                "min_time": min(valid_times),
                "max_time": max(valid_times),
                "std_dev": statistics.stdev(valid_times) if len(valid_times) > 1 else 0,
                "test_counts": test_counts,
                "mean_test_count": statistics.mean([c for c in test_counts if c > 0]) if [c for c in test_counts if c > 0] else 0,
                "slowest_tests": self._aggregate_slowest_tests(slowest_tests_all),
                "success": True
            }
        else:
            return {
                "category": category,
                "runs": runs,
                "success": False,
                "error": "No valid execution times recorded"
            }
    
    def _extract_test_count(self, output: str) -> int:
        """Extract test count from pytest output."""
        lines = output.split('\n')
        for line in lines:
            if 'passed' in line and ('failed' in line or 'error' in line or line.strip().endswith('passed')):
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        try:
                            return int(parts[i-1])
                        except ValueError:
                            continue
        return 0
    
    def _extract_slowest_tests(self, output: str) -> List[Dict[str, Any]]:
        """Extract slowest tests from pytest output."""
        slowest_tests = []
        lines = output.split('\n')
        
        in_slowest_section = False
        for line in lines:
            if 'slowest durations' in line.lower():
                in_slowest_section = True
                continue
            
            if in_slowest_section:
                if line.strip() == '' or '=' in line:
                    break
                
                parts = line.strip().split()
                if len(parts) >= 3 and parts[0].endswith('s'):
                    try:
                        duration = float(parts[0][:-1])
                        test_name = ' '.join(parts[2:])
                        slowest_tests.append({
                            "duration": duration,
                            "test": test_name
                        })
                    except ValueError:
                        continue
        
        return slowest_tests
    
    def _aggregate_slowest_tests(self, all_slowest: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate slowest tests across multiple runs."""
        # Group by test name and average durations
        test_durations = {}
        
        for test_info in all_slowest:
            test_name = test_info["test"]
            duration = test_info["duration"]
            
            if test_name not in test_durations:
                test_durations[test_name] = []
            test_durations[test_name].append(duration)
        
        # Calculate average duration for each test
        averaged_tests = []
        for test_name, durations in test_durations.items():
            averaged_tests.append({
                "test": test_name,
                "avg_duration": statistics.mean(durations),
                "max_duration": max(durations),
                "run_count": len(durations)
            })
        
        # Sort by average duration and return top 10
        averaged_tests.sort(key=lambda x: x["avg_duration"], reverse=True)
        return averaged_tests[:10]
    
    def run_all_benchmarks(self, runs: int = 3) -> Dict[str, Dict[str, Any]]:
        """Run benchmarks for all test categories."""
        results = {}
        
        for category in self.test_categories:
            try:
                results[category] = self.run_single_benchmark(category, runs)
            except Exception as e:
                results[category] = {
                    "category": category,
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def validate_performance_targets(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Validate performance against targets."""
        validation = {
            "overall_passed": True,
            "category_results": {},
            "issues": []
        }
        
        # Check each category against targets
        for category, target_time in [
            ("unit", self.performance_targets["unit_tests_max"]),
            ("integration", self.performance_targets["integration_tests_max"]),
            ("performance", self.performance_targets["performance_tests_max"]),
            ("full_suite", self.performance_targets["full_suite_max"])
        ]:
            if category in results and results[category].get("success", False):
                mean_time = results[category]["mean_time"]
                passed = mean_time <= target_time
                
                validation["category_results"][category] = {
                    "mean_time": mean_time,
                    "target_time": target_time,
                    "passed": passed,
                    "margin": target_time - mean_time
                }
                
                if not passed:
                    validation["overall_passed"] = False
                    validation["issues"].append(
                        f"{category} tests took {mean_time:.1f}s, exceeding target {target_time}s"
                    )
        
        return validation
    
    def compare_with_baseline(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Compare current results with baseline."""
        comparison = {
            "has_baseline": bool(self.baseline_data),
            "category_comparisons": {},
            "overall_improvement": 0,
            "regressions": [],
            "improvements": []
        }
        
        if not self.baseline_data:
            return comparison
        
        total_baseline_time = 0
        total_current_time = 0
        
        for category, current_result in results.items():
            if not current_result.get("success", False):
                continue
            
            if category in self.baseline_data:
                baseline_time = self.baseline_data[category].get("mean_time", 0)
                current_time = current_result["mean_time"]
                
                if baseline_time > 0:
                    improvement = (baseline_time - current_time) / baseline_time
                    improvement_percent = improvement * 100
                    
                    comparison["category_comparisons"][category] = {
                        "baseline_time": baseline_time,
                        "current_time": current_time,
                        "improvement": improvement,
                        "improvement_percent": improvement_percent,
                        "is_regression": improvement < -self.performance_targets["regression_threshold"],
                        "meets_target": improvement >= self.performance_targets["improvement_target"]
                    }
                    
                    total_baseline_time += baseline_time
                    total_current_time += current_time
                    
                    # Track regressions and improvements
                    if improvement < -self.performance_targets["regression_threshold"]:
                        comparison["regressions"].append({
                            "category": category,
                            "regression_percent": -improvement_percent,
                            "baseline_time": baseline_time,
                            "current_time": current_time
                        })
                    elif improvement >= self.performance_targets["improvement_target"]:
                        comparison["improvements"].append({
                            "category": category,
                            "improvement_percent": improvement_percent,
                            "baseline_time": baseline_time,
                            "current_time": current_time
                        })
        
        # Calculate overall improvement
        if total_baseline_time > 0:
            comparison["overall_improvement"] = (total_baseline_time - total_current_time) / total_baseline_time
        
        return comparison
    
    def generate_benchmark_report(self, results: Dict[str, Dict[str, Any]],
                                validation: Dict[str, Any],
                                comparison: Dict[str, Any]) -> str:
        """Generate comprehensive benchmark report."""
        
        report = []
        report.append("=" * 80)
        report.append("PERFORMANCE BENCHMARK REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Overall status
        overall_passed = validation.get("overall_passed", False)
        report.append(f"OVERALL STATUS: {'✅ PASSED' if overall_passed else '❌ FAILED'}")
        report.append("")
        
        # Performance summary
        report.append("PERFORMANCE SUMMARY")
        report.append("-" * 40)
        
        for category, result in results.items():
            if result.get("success", False):
                mean_time = result["mean_time"]
                test_count = result.get("mean_test_count", 0)
                
                # Get validation status
                validation_result = validation.get("category_results", {}).get(category, {})
                status = "✅" if validation_result.get("passed", True) else "❌"
                target = validation_result.get("target_time", "N/A")
                
                report.append(f"{status} {category}: {mean_time:.1f}s "
                             f"({test_count:.0f} tests, target: {target}s)")
            else:
                report.append(f"❌ {category}: FAILED - {result.get('error', 'Unknown error')}")
        
        report.append("")
        
        # Baseline comparison
        if comparison.get("has_baseline", False):
            report.append("BASELINE COMPARISON")
            report.append("-" * 40)
            
            overall_improvement = comparison.get("overall_improvement", 0) * 100
            report.append(f"Overall Performance Change: {overall_improvement:+.1f}%")
            report.append("")
            
            for category, comp in comparison.get("category_comparisons", {}).items():
                improvement = comp["improvement_percent"]
                status = "📈" if improvement > 0 else "📉" if improvement < -5 else "➡️"
                
                meets_target = "✅" if comp.get("meets_target", False) else "❌"
                is_regression = "🚨" if comp.get("is_regression", False) else ""
                
                report.append(f"{status} {category}: {improvement:+.1f}% "
                             f"({comp['baseline_time']:.1f}s → {comp['current_time']:.1f}s) "
                             f"{meets_target} {is_regression}")
            
            # Regressions
            if comparison.get("regressions"):
                report.append("")
                report.append("🚨 PERFORMANCE REGRESSIONS:")
                for regression in comparison["regressions"]:
                    report.append(f"  {regression['category']}: "
                                 f"{regression['regression_percent']:.1f}% slower")
            
            # Improvements
            if comparison.get("improvements"):
                report.append("")
                report.append("📈 SIGNIFICANT IMPROVEMENTS:")
                for improvement in comparison["improvements"]:
                    report.append(f"  {improvement['category']}: "
                                 f"{improvement['improvement_percent']:.1f}% faster")
        
        # Slowest tests
        report.append("")
        report.append("SLOWEST TESTS BY CATEGORY")
        report.append("-" * 40)
        
        for category, result in results.items():
            if result.get("success", False) and result.get("slowest_tests"):
                report.append(f"\n{category.upper()} - Top 5 Slowest Tests:")
                for i, test in enumerate(result["slowest_tests"][:5], 1):
                    report.append(f"  {i}. {test['avg_duration']:.2f}s - {test['test']}")
        
        # Issues summary
        issues = validation.get("issues", [])
        if issues:
            report.append("")
            report.append("ISSUES IDENTIFIED")
            report.append("-" * 40)
            for issue in issues:
                report.append(f"❌ {issue}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_as_baseline(self, results: Dict[str, Dict[str, Any]]):
        """Save current results as new baseline."""
        baseline_data = {}
        
        for category, result in results.items():
            if result.get("success", False):
                baseline_data[category] = {
                    "mean_time": result["mean_time"],
                    "median_time": result["median_time"],
                    "test_count": result.get("mean_test_count", 0),
                    "timestamp": time.time()
                }
        
        self._save_baseline(baseline_data)


def main():
    """Main benchmarking function."""
    parser = argparse.ArgumentParser(description="Benchmark test execution performance")
    parser.add_argument("--runs", type=int, default=3,
                       help="Number of benchmark runs per category")
    parser.add_argument("--category", choices=["unit", "integration", "performance", "e2e", "full_suite"],
                       help="Run benchmark for specific category only")
    parser.add_argument("--save-baseline", action="store_true",
                       help="Save current results as new baseline")
    parser.add_argument("--report-file", default="performance_benchmark_report.txt",
                       help="Output file for benchmark report")
    parser.add_argument("--fail-on-regression", action="store_true",
                       help="Exit with error code if performance regressions detected")
    
    args = parser.parse_args()
    
    benchmark = PerformanceBenchmark()
    
    print("Starting performance benchmarking...")
    print(f"Running {args.runs} iterations per category")
    print("")
    
    # Run benchmarks
    if args.category:
        results = {args.category: benchmark.run_single_benchmark(args.category, args.runs)}
    else:
        results = benchmark.run_all_benchmarks(args.runs)
    
    # Validate and compare
    validation = benchmark.validate_performance_targets(results)
    comparison = benchmark.compare_with_baseline(results)
    
    # Generate report
    report = benchmark.generate_benchmark_report(results, validation, comparison)
    
    # Save report
    with open(args.report_file, 'w') as f:
        f.write(report)
    
    print(f"Benchmark report saved to {args.report_file}")
    print("\n" + report)
    
    # Save baseline if requested
    if args.save_baseline:
        benchmark.save_as_baseline(results)
    
    # Exit based on results
    exit_code = 0
    
    if not validation.get("overall_passed", False):
        print("\nPerformance targets not met")
        exit_code = 1
    
    if args.fail_on_regression and comparison.get("regressions"):
        print(f"\nPerformance regressions detected: {len(comparison['regressions'])}")
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()