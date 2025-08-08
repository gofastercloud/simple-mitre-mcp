#!/usr/bin/env python3
"""
Coverage and Performance Validation Script

This script validates that the rationalized test suite meets coverage and performance requirements.
It generates comprehensive reports and implements regression detection.

Requirements addressed:
- 4.1: Code coverage maintenance at or above 90%
- 4.2: Coverage gap identification and addressing
- 4.4: Coverage reporting by test category
- 3.1: Test execution time improvements (30% reduction target)
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any
import argparse


class CoverageValidator:
    """Validates code coverage requirements and generates reports."""
    
    def __init__(self, baseline_file: str = "coverage/data/baseline_coverage.json"):
        self.baseline_file = baseline_file
        self.baseline_coverage = self._load_baseline_coverage()
        self.coverage_requirements = {
            "overall_coverage": 90,
            "category_coverage": {
                "unit": 95,
                "integration": 85,
                "performance": 70,
                "compatibility": 90,
                "deployment": 80,
                "e2e": 60
            },
            "critical_modules": {
                "src/mcp_server.py": 95,
                "src/data_loader.py": 95,
                "src/parsers/": 90
            }
        }
    
    def _load_baseline_coverage(self) -> Dict[str, Any]:
        """Load baseline coverage data if available."""
        if os.path.exists(self.baseline_file):
            try:
                with open(self.baseline_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load baseline coverage: {e}")
        return {}
    
    def run_coverage_by_category(self) -> Dict[str, Dict[str, Any]]:
        """Run coverage tests by category and collect results."""
        categories = ["unit", "integration", "performance", "compatibility", "deployment", "e2e"]
        coverage_results = {}
        
        for category in categories:
            print(f"Running coverage for {category} tests...")
            
            # Run tests for specific category with coverage
            cmd = [
                "uv", "run", "pytest", 
                f"tests/{category}/",
                f"-m", category,
                "--cov=src",
                "--cov-report=json:validation/temp/coverage_temp.json",
                "--cov-report=term-missing",
                "--tb=short",
                "-v"
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                # Load coverage data
                temp_file = "validation/temp/coverage_temp.json"
                if os.path.exists(temp_file):
                    with open(temp_file, 'r') as f:
                        coverage_data = json.load(f)
                    
                    coverage_results[category] = {
                        "coverage_percent": coverage_data.get("totals", {}).get("percent_covered", 0),
                        "covered_lines": coverage_data.get("totals", {}).get("covered_lines", 0),
                        "total_lines": coverage_data.get("totals", {}).get("num_statements", 0),
                        "missing_lines": coverage_data.get("totals", {}).get("missing_lines", 0),
                        "files": coverage_data.get("files", {}),
                        "test_result": result.returncode == 0
                    }
                    
                    # Clean up temp file
                    os.remove(temp_file)
                else:
                    coverage_results[category] = {
                        "coverage_percent": 0,
                        "test_result": False,
                        "error": "No coverage data generated"
                    }
                    
            except subprocess.TimeoutExpired:
                coverage_results[category] = {
                    "coverage_percent": 0,
                    "test_result": False,
                    "error": "Test execution timeout"
                }
            except Exception as e:
                coverage_results[category] = {
                    "coverage_percent": 0,
                    "test_result": False,
                    "error": str(e)
                }
        
        return coverage_results
    
    def run_overall_coverage(self) -> Dict[str, Any]:
        """Run overall coverage across all tests."""
        print("Running overall coverage analysis...")
        
        cmd = [
            "uv", "run", "pytest", 
            "tests/",
            "--cov=src",
            "--cov-report=json:coverage/data/coverage_overall.json",
            "--cov-report=html:coverage/reports/htmlcov",
            "--cov-report=term-missing",
            "--tb=short"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            coverage_file = "coverage/data/coverage_overall.json"
            if os.path.exists(coverage_file):
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                return {
                    "coverage_percent": coverage_data.get("totals", {}).get("percent_covered", 0),
                    "covered_lines": coverage_data.get("totals", {}).get("covered_lines", 0),
                    "total_lines": coverage_data.get("totals", {}).get("num_statements", 0),
                    "missing_lines": coverage_data.get("totals", {}).get("missing_lines", 0),
                    "files": coverage_data.get("files", {}),
                    "test_result": result.returncode == 0,
                    "output": result.stdout
                }
            else:
                return {
                    "coverage_percent": 0,
                    "test_result": False,
                    "error": "No overall coverage data generated"
                }
                
        except Exception as e:
            return {
                "coverage_percent": 0,
                "test_result": False,
                "error": str(e)
            }
    
    def validate_coverage_requirements(self, coverage_results: Dict[str, Dict[str, Any]], 
                                     overall_coverage: Dict[str, Any]) -> Dict[str, Any]:
        """Validate coverage against requirements."""
        validation_results = {
            "overall_passed": True,
            "category_results": {},
            "critical_module_results": {},
            "baseline_comparison": {},
            "issues": []
        }
        
        # Validate overall coverage
        overall_percent = overall_coverage.get("coverage_percent", 0)
        if overall_percent < self.coverage_requirements["overall_coverage"]:
            validation_results["overall_passed"] = False
            validation_results["issues"].append(
                f"Overall coverage {overall_percent:.1f}% below requirement "
                f"{self.coverage_requirements['overall_coverage']}%"
            )
        
        # Validate category coverage
        for category, requirement in self.coverage_requirements["category_coverage"].items():
            if category in coverage_results:
                category_percent = coverage_results[category].get("coverage_percent", 0)
                passed = category_percent >= requirement
                
                validation_results["category_results"][category] = {
                    "coverage_percent": category_percent,
                    "requirement": requirement,
                    "passed": passed
                }
                
                if not passed:
                    validation_results["overall_passed"] = False
                    validation_results["issues"].append(
                        f"{category} coverage {category_percent:.1f}% below requirement {requirement}%"
                    )
        
        # Validate critical modules
        files_data = overall_coverage.get("files", {})
        for module_pattern, requirement in self.coverage_requirements["critical_modules"].items():
            matching_files = [f for f in files_data.keys() if module_pattern in f]
            
            for file_path in matching_files:
                file_coverage = files_data[file_path].get("summary", {}).get("percent_covered", 0)
                passed = file_coverage >= requirement
                
                validation_results["critical_module_results"][file_path] = {
                    "coverage_percent": file_coverage,
                    "requirement": requirement,
                    "passed": passed
                }
                
                if not passed:
                    validation_results["overall_passed"] = False
                    validation_results["issues"].append(
                        f"Critical module {file_path} coverage {file_coverage:.1f}% "
                        f"below requirement {requirement}%"
                    )
        
        # Compare with baseline if available
        if self.baseline_coverage:
            baseline_percent = self.baseline_coverage.get("totals", {}).get("percent_covered", 0)
            current_percent = overall_percent
            
            validation_results["baseline_comparison"] = {
                "baseline_coverage": baseline_percent,
                "current_coverage": current_percent,
                "improvement": current_percent - baseline_percent,
                "maintained": current_percent >= baseline_percent
            }
            
            if current_percent < baseline_percent:
                validation_results["overall_passed"] = False
                validation_results["issues"].append(
                    f"Coverage decreased from baseline: {baseline_percent:.1f}% to {current_percent:.1f}%"
                )
        
        return validation_results


class PerformanceValidator:
    """Validates test execution performance and tracks improvements."""
    
    def __init__(self, baseline_file: str = ".performance_baseline.json"):
        self.baseline_file = baseline_file
        self.baseline_times = self._load_baseline_times()
        self.performance_targets = {
            "unit_tests_max": 30,  # seconds
            "integration_tests_max": 120,  # seconds
            "full_suite_max": 600,  # seconds
            "improvement_target": 0.30  # 30% improvement
        }
    
    def _load_baseline_times(self) -> Dict[str, float]:
        """Load baseline performance times if available."""
        if os.path.exists(self.baseline_file):
            try:
                with open(self.baseline_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load baseline times: {e}")
        return {}
    
    def measure_test_execution_times(self) -> Dict[str, Dict[str, Any]]:
        """Measure execution times for different test categories."""
        test_categories = {
            "unit": ["tests/unit/", "-m", "unit"],
            "integration": ["tests/integration/", "-m", "integration"],
            "performance": ["tests/performance/", "-m", "performance"],
            "full_suite": ["tests/"]
        }
        
        execution_times = {}
        
        for category, test_args in test_categories.items():
            print(f"Measuring execution time for {category} tests...")
            
            cmd = ["uv", "run", "pytest"] + test_args + [
                "--tb=short",
                "-v",
                "--durations=10"
            ]
            
            start_time = time.time()
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                execution_times[category] = {
                    "execution_time": execution_time,
                    "test_result": result.returncode == 0,
                    "test_count": self._extract_test_count(result.stdout),
                    "slowest_tests": self._extract_slowest_tests(result.stdout)
                }
                
            except subprocess.TimeoutExpired:
                execution_times[category] = {
                    "execution_time": 900,  # timeout value
                    "test_result": False,
                    "error": "Test execution timeout"
                }
            except Exception as e:
                execution_times[category] = {
                    "execution_time": 0,
                    "test_result": False,
                    "error": str(e)
                }
        
        return execution_times
    
    def _extract_test_count(self, output: str) -> int:
        """Extract test count from pytest output."""
        lines = output.split('\n')
        for line in lines:
            if 'passed' in line and ('failed' in line or 'error' in line or line.strip().endswith('passed')):
                # Look for patterns like "123 passed" or "120 passed, 3 failed"
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
                
                # Parse lines like "1.23s call tests/test_something.py::test_function"
                parts = line.strip().split()
                if len(parts) >= 3 and parts[0].endswith('s'):
                    try:
                        duration = float(parts[0][:-1])  # Remove 's' suffix
                        test_name = ' '.join(parts[2:])
                        slowest_tests.append({
                            "duration": duration,
                            "test": test_name
                        })
                    except ValueError:
                        continue
        
        return slowest_tests[:10]  # Top 10 slowest
    
    def validate_performance_requirements(self, execution_times: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Validate performance against requirements."""
        validation_results = {
            "overall_passed": True,
            "category_results": {},
            "baseline_comparison": {},
            "issues": []
        }
        
        # Validate category performance targets
        category_targets = {
            "unit": self.performance_targets["unit_tests_max"],
            "integration": self.performance_targets["integration_tests_max"],
            "full_suite": self.performance_targets["full_suite_max"]
        }
        
        for category, target in category_targets.items():
            if category in execution_times:
                execution_time = execution_times[category].get("execution_time", 0)
                passed = execution_time <= target
                
                validation_results["category_results"][category] = {
                    "execution_time": execution_time,
                    "target": target,
                    "passed": passed
                }
                
                if not passed:
                    validation_results["overall_passed"] = False
                    validation_results["issues"].append(
                        f"{category} tests took {execution_time:.1f}s, exceeding target {target}s"
                    )
        
        # Compare with baseline if available
        if self.baseline_times:
            for category in execution_times:
                if category in self.baseline_times:
                    baseline_time = self.baseline_times[category]
                    current_time = execution_times[category].get("execution_time", 0)
                    improvement = (baseline_time - current_time) / baseline_time if baseline_time > 0 else 0
                    
                    validation_results["baseline_comparison"][category] = {
                        "baseline_time": baseline_time,
                        "current_time": current_time,
                        "improvement": improvement,
                        "improvement_percent": improvement * 100,
                        "meets_target": improvement >= self.performance_targets["improvement_target"]
                    }
                    
                    if improvement < self.performance_targets["improvement_target"]:
                        validation_results["issues"].append(
                            f"{category} improvement {improvement*100:.1f}% below target "
                            f"{self.performance_targets['improvement_target']*100:.1f}%"
                        )
        
        return validation_results
    
    def save_baseline_times(self, execution_times: Dict[str, Dict[str, Any]]):
        """Save current execution times as new baseline."""
        baseline_data = {}
        for category, data in execution_times.items():
            if "execution_time" in data:
                baseline_data[category] = data["execution_time"]
        
        with open(self.baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        print(f"Saved performance baseline to {self.baseline_file}")


class RegressionDetector:
    """Detects coverage and performance regressions."""
    
    def __init__(self, history_file: str = "validation/data/validation_history.json"):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load validation history."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return []
    
    def add_validation_result(self, coverage_validation: Dict[str, Any], 
                            performance_validation: Dict[str, Any],
                            coverage_results: Dict[str, Dict[str, Any]],
                            execution_times: Dict[str, Dict[str, Any]]):
        """Add new validation result to history."""
        result = {
            "timestamp": time.time(),
            "coverage_validation": coverage_validation,
            "performance_validation": performance_validation,
            "coverage_summary": {
                category: data.get("coverage_percent", 0) 
                for category, data in coverage_results.items()
            },
            "performance_summary": {
                category: data.get("execution_time", 0) 
                for category, data in execution_times.items()
            }
        }
        
        self.history.append(result)
        
        # Keep only last 50 results
        if len(self.history) > 50:
            self.history = self.history[-50:]
        
        self._save_history()
    
    def _save_history(self):
        """Save validation history."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def detect_regressions(self) -> Dict[str, Any]:
        """Detect regressions in recent validation results."""
        if len(self.history) < 2:
            return {"regressions": [], "message": "Insufficient history for regression detection"}
        
        current = self.history[-1]
        previous = self.history[-2]
        
        regressions = []
        
        # Check coverage regressions
        for category in current["coverage_summary"]:
            if category in previous["coverage_summary"]:
                current_coverage = current["coverage_summary"][category]
                previous_coverage = previous["coverage_summary"][category]
                
                if current_coverage < previous_coverage - 1.0:  # 1% threshold
                    regressions.append({
                        "type": "coverage",
                        "category": category,
                        "current": current_coverage,
                        "previous": previous_coverage,
                        "regression": previous_coverage - current_coverage
                    })
        
        # Check performance regressions
        for category in current["performance_summary"]:
            if category in previous["performance_summary"]:
                current_time = current["performance_summary"][category]
                previous_time = previous["performance_summary"][category]
                
                if current_time > previous_time * 1.1:  # 10% threshold
                    regressions.append({
                        "type": "performance",
                        "category": category,
                        "current": current_time,
                        "previous": previous_time,
                        "regression_percent": ((current_time - previous_time) / previous_time) * 100
                    })
        
        return {
            "regressions": regressions,
            "regression_count": len(regressions)
        }


def generate_comprehensive_report(coverage_validation: Dict[str, Any],
                                performance_validation: Dict[str, Any],
                                coverage_results: Dict[str, Dict[str, Any]],
                                execution_times: Dict[str, Dict[str, Any]],
                                overall_coverage: Dict[str, Any],
                                regression_results: Dict[str, Any]) -> str:
    """Generate comprehensive validation report."""
    
    report = []
    report.append("=" * 80)
    report.append("TEST SUITE RATIONALIZATION - COVERAGE & PERFORMANCE VALIDATION")
    report.append("=" * 80)
    report.append("")
    
    # Overall Status
    overall_passed = (coverage_validation.get("overall_passed", False) and 
                     performance_validation.get("overall_passed", False))
    
    report.append(f"OVERALL STATUS: {'✅ PASSED' if overall_passed else '❌ FAILED'}")
    report.append("")
    
    # Coverage Summary
    report.append("COVERAGE ANALYSIS")
    report.append("-" * 40)
    
    overall_percent = overall_coverage.get("coverage_percent", 0)
    report.append(f"Overall Coverage: {overall_percent:.1f}%")
    
    if "baseline_comparison" in coverage_validation:
        baseline_data = coverage_validation["baseline_comparison"]
        improvement = baseline_data.get("improvement", 0)
        report.append(f"Baseline Comparison: {improvement:+.1f}% change")
    
    report.append("")
    report.append("Coverage by Category:")
    for category, results in coverage_validation.get("category_results", {}).items():
        status = "✅" if results["passed"] else "❌"
        report.append(f"  {status} {category}: {results['coverage_percent']:.1f}% "
                     f"(req: {results['requirement']}%)")
    
    report.append("")
    report.append("Critical Modules:")
    for module, results in coverage_validation.get("critical_module_results", {}).items():
        status = "✅" if results["passed"] else "❌"
        report.append(f"  {status} {module}: {results['coverage_percent']:.1f}% "
                     f"(req: {results['requirement']}%)")
    
    # Performance Summary
    report.append("")
    report.append("PERFORMANCE ANALYSIS")
    report.append("-" * 40)
    
    for category, results in performance_validation.get("category_results", {}).items():
        status = "✅" if results["passed"] else "❌"
        report.append(f"{status} {category}: {results['execution_time']:.1f}s "
                     f"(target: {results['target']}s)")
    
    if "baseline_comparison" in performance_validation:
        report.append("")
        report.append("Performance Improvements:")
        for category, comparison in performance_validation["baseline_comparison"].items():
            improvement = comparison.get("improvement_percent", 0)
            status = "✅" if comparison.get("meets_target", False) else "❌"
            report.append(f"  {status} {category}: {improvement:+.1f}% improvement")
    
    # Regression Detection
    if regression_results.get("regression_count", 0) > 0:
        report.append("")
        report.append("REGRESSION DETECTION")
        report.append("-" * 40)
        
        for regression in regression_results["regressions"]:
            if regression["type"] == "coverage":
                report.append(f"❌ Coverage regression in {regression['category']}: "
                             f"{regression['regression']:.1f}% decrease")
            else:
                report.append(f"❌ Performance regression in {regression['category']}: "
                             f"{regression['regression_percent']:.1f}% slower")
    
    # Issues Summary
    all_issues = (coverage_validation.get("issues", []) + 
                 performance_validation.get("issues", []))
    
    if all_issues:
        report.append("")
        report.append("ISSUES FOUND")
        report.append("-" * 40)
        for issue in all_issues:
            report.append(f"❌ {issue}")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description="Validate coverage and performance improvements")
    parser.add_argument("--save-baseline", action="store_true", 
                       help="Save current results as new baseline")
    parser.add_argument("--report-file", default="validation_report.txt",
                       help="Output file for validation report")
    
    args = parser.parse_args()
    
    print("Starting coverage and performance validation...")
    
    # Initialize validators
    coverage_validator = CoverageValidator()
    performance_validator = PerformanceValidator()
    regression_detector = RegressionDetector()
    
    # Run coverage analysis
    print("\n" + "="*50)
    print("RUNNING COVERAGE ANALYSIS")
    print("="*50)
    
    coverage_results = coverage_validator.run_coverage_by_category()
    overall_coverage = coverage_validator.run_overall_coverage()
    coverage_validation = coverage_validator.validate_coverage_requirements(
        coverage_results, overall_coverage
    )
    
    # Run performance analysis
    print("\n" + "="*50)
    print("RUNNING PERFORMANCE ANALYSIS")
    print("="*50)
    
    execution_times = performance_validator.measure_test_execution_times()
    performance_validation = performance_validator.validate_performance_requirements(execution_times)
    
    # Detect regressions
    regression_results = regression_detector.detect_regressions()
    
    # Add to history
    regression_detector.add_validation_result(
        coverage_validation, performance_validation, coverage_results, execution_times
    )
    
    # Generate report
    report = generate_comprehensive_report(
        coverage_validation, performance_validation, coverage_results, 
        execution_times, overall_coverage, regression_results
    )
    
    # Save report
    with open(args.report_file, 'w') as f:
        f.write(report)
    
    print(f"\nValidation report saved to {args.report_file}")
    print("\n" + report)
    
    # Save baselines if requested
    if args.save_baseline:
        performance_validator.save_baseline_times(execution_times)
        print("Performance baseline updated")
    
    # Exit with appropriate code
    overall_passed = (coverage_validation.get("overall_passed", False) and 
                     performance_validation.get("overall_passed", False))
    
    sys.exit(0 if overall_passed else 1)


if __name__ == "__main__":
    main()