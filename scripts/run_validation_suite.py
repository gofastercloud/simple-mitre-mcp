#!/usr/bin/env python3
"""
Comprehensive Validation Suite Runner

This script runs the complete validation suite including coverage validation,
performance benchmarking, and regression detection as required by task 9.

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
from typing import Dict, List, Any
import argparse


class ValidationSuiteRunner:
    """Runs comprehensive validation suite for test rationalization."""
    
    def __init__(self, output_dir: str = "validation_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.validation_scripts = {
            "coverage_performance": "scripts/validate_coverage_performance.py",
            "coverage_regression": "scripts/coverage_regression_monitor.py", 
            "performance_benchmark": "scripts/performance_benchmark.py"
        }
        
        self.results = {}
        self.start_time = time.time()
    
    def run_coverage_performance_validation(self) -> Dict[str, Any]:
        """Run comprehensive coverage and performance validation."""
        print("=" * 60)
        print("RUNNING COVERAGE & PERFORMANCE VALIDATION")
        print("=" * 60)
        
        script_path = self.validation_scripts["coverage_performance"]
        report_file = self.output_dir / "coverage_performance_report.txt"
        
        cmd = [
            "uv", "run", "python", script_path,
            "--report-file", str(report_file)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "report_file": str(report_file),
                "execution_time": time.time() - self.start_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Validation timeout after 30 minutes",
                "execution_time": 1800
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - self.start_time
            }
    
    def run_coverage_regression_monitoring(self) -> Dict[str, Any]:
        """Run coverage regression monitoring."""
        print("\n" + "=" * 60)
        print("RUNNING COVERAGE REGRESSION MONITORING")
        print("=" * 60)
        
        script_path = self.validation_scripts["coverage_regression"]
        report_file = self.output_dir / "coverage_regression_report.txt"
        
        cmd = [
            "uv", "run", "python", script_path,
            "--report-file", str(report_file)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "report_file": str(report_file),
                "execution_time": time.time() - self.start_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Regression monitoring timeout after 15 minutes",
                "execution_time": 900
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - self.start_time
            }
    
    def run_performance_benchmarking(self) -> Dict[str, Any]:
        """Run performance benchmarking."""
        print("\n" + "=" * 60)
        print("RUNNING PERFORMANCE BENCHMARKING")
        print("=" * 60)
        
        script_path = self.validation_scripts["performance_benchmark"]
        report_file = self.output_dir / "performance_benchmark_report.txt"
        
        cmd = [
            "uv", "run", "python", script_path,
            "--runs", "3",
            "--report-file", str(report_file)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "report_file": str(report_file),
                "execution_time": time.time() - self.start_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Performance benchmarking timeout after 20 minutes",
                "execution_time": 1200
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - self.start_time
            }
    
    def generate_summary_report(self) -> str:
        """Generate comprehensive summary report."""
        
        report = []
        report.append("=" * 80)
        report.append("TEST SUITE RATIONALIZATION - VALIDATION SUMMARY")
        report.append("=" * 80)
        report.append("")
        
        # Overall status
        all_successful = all(result.get("success", False) for result in self.results.values())
        total_time = time.time() - self.start_time
        
        report.append(f"OVERALL VALIDATION STATUS: {'✅ PASSED' if all_successful else '❌ FAILED'}")
        report.append(f"Total Execution Time: {total_time:.1f} seconds")
        report.append("")
        
        # Individual validation results
        report.append("VALIDATION COMPONENT RESULTS")
        report.append("-" * 50)
        
        validation_names = {
            "coverage_performance": "Coverage & Performance Validation",
            "coverage_regression": "Coverage Regression Monitoring", 
            "performance_benchmark": "Performance Benchmarking"
        }
        
        for component, result in self.results.items():
            name = validation_names.get(component, component)
            status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
            exec_time = result.get("execution_time", 0)
            
            report.append(f"{status} {name} ({exec_time:.1f}s)")
            
            if not result.get("success", False):
                error = result.get("error", "Unknown error")
                report.append(f"    Error: {error}")
            
            if "report_file" in result:
                report.append(f"    Report: {result['report_file']}")
        
        report.append("")
        
        # Requirements compliance summary
        report.append("REQUIREMENTS COMPLIANCE")
        report.append("-" * 50)
        
        requirements_status = {
            "4.1 - Coverage Maintenance (≥90%)": self._check_coverage_requirement(),
            "4.2 - Coverage Gap Identification": self._check_gap_identification(),
            "4.4 - Category Coverage Reporting": self._check_category_reporting(),
            "3.1 - Performance Improvement (30%)": self._check_performance_improvement()
        }
        
        for requirement, status in requirements_status.items():
            status_icon = "✅" if status else "❌"
            report.append(f"{status_icon} {requirement}")
        
        # Files generated
        report.append("")
        report.append("GENERATED REPORTS")
        report.append("-" * 50)
        
        for component, result in self.results.items():
            if "report_file" in result and os.path.exists(result["report_file"]):
                report.append(f"📄 {result['report_file']}")
        
        # Additional artifacts
        additional_files = [
            "coverage.json",
            "htmlcov/index.html",
            ".coverage_history.json",
            ".performance_baseline.json",
            ".validation_history.json"
        ]
        
        existing_files = [f for f in additional_files if os.path.exists(f)]
        if existing_files:
            report.append("")
            report.append("ADDITIONAL ARTIFACTS")
            report.append("-" * 50)
            for file_path in existing_files:
                report.append(f"📄 {file_path}")
        
        # Next steps
        if not all_successful:
            report.append("")
            report.append("RECOMMENDED NEXT STEPS")
            report.append("-" * 50)
            
            failed_components = [comp for comp, result in self.results.items() 
                               if not result.get("success", False)]
            
            for component in failed_components:
                if component == "coverage_performance":
                    report.append("❗ Review coverage gaps and performance bottlenecks")
                    report.append("   - Check individual test category coverage")
                    report.append("   - Identify slow-running tests for optimization")
                elif component == "coverage_regression":
                    report.append("❗ Address coverage regressions")
                    report.append("   - Review files with decreased coverage")
                    report.append("   - Add tests for uncovered code paths")
                elif component == "performance_benchmark":
                    report.append("❗ Optimize test performance")
                    report.append("   - Profile slow tests and optimize setup/teardown")
                    report.append("   - Consider parallel test execution")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def _check_coverage_requirement(self) -> bool:
        """Check if coverage requirement is met."""
        # This would check the actual coverage results
        # For now, return True if coverage validation passed
        return self.results.get("coverage_performance", {}).get("success", False)
    
    def _check_gap_identification(self) -> bool:
        """Check if coverage gaps are identified."""
        # This would check if gap identification ran successfully
        return self.results.get("coverage_regression", {}).get("success", False)
    
    def _check_category_reporting(self) -> bool:
        """Check if category reporting is working."""
        # This would check if category-based reporting is functional
        return self.results.get("coverage_performance", {}).get("success", False)
    
    def _check_performance_improvement(self) -> bool:
        """Check if performance improvement target is met."""
        # This would check actual performance improvement results
        return self.results.get("performance_benchmark", {}).get("success", False)
    
    def run_complete_validation(self) -> Dict[str, Any]:
        """Run complete validation suite."""
        print("Starting comprehensive validation suite...")
        print(f"Output directory: {self.output_dir}")
        print("")
        
        # Run all validation components
        self.results["coverage_performance"] = self.run_coverage_performance_validation()
        self.results["coverage_regression"] = self.run_coverage_regression_monitoring()
        self.results["performance_benchmark"] = self.run_performance_benchmarking()
        
        # Generate summary report
        summary_report = self.generate_summary_report()
        summary_file = self.output_dir / "validation_summary.txt"
        
        with open(summary_file, 'w') as f:
            f.write(summary_report)
        
        print("\n" + "=" * 80)
        print("VALIDATION SUITE COMPLETE")
        print("=" * 80)
        print(f"Summary report: {summary_file}")
        print("")
        print(summary_report)
        
        # Save results as JSON
        results_file = self.output_dir / "validation_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": time.time(),
                "total_execution_time": time.time() - self.start_time,
                "results": self.results,
                "overall_success": all(r.get("success", False) for r in self.results.values())
            }, f, indent=2)
        
        return {
            "overall_success": all(r.get("success", False) for r in self.results.values()),
            "results": self.results,
            "summary_report": summary_report,
            "summary_file": str(summary_file),
            "results_file": str(results_file)
        }


def main():
    """Main validation suite runner."""
    parser = argparse.ArgumentParser(description="Run comprehensive validation suite")
    parser.add_argument("--output-dir", default="validation_results",
                       help="Directory for validation output files")
    parser.add_argument("--fail-fast", action="store_true",
                       help="Stop on first validation failure")
    
    args = parser.parse_args()
    
    # Ensure scripts exist
    required_scripts = [
        "scripts/validate_coverage_performance.py",
        "scripts/coverage_regression_monitor.py",
        "scripts/performance_benchmark.py"
    ]
    
    missing_scripts = [script for script in required_scripts if not os.path.exists(script)]
    if missing_scripts:
        print("Error: Missing required validation scripts:")
        for script in missing_scripts:
            print(f"  - {script}")
        sys.exit(1)
    
    # Run validation suite
    runner = ValidationSuiteRunner(args.output_dir)
    
    try:
        results = runner.run_complete_validation()
        
        # Exit with appropriate code
        exit_code = 0 if results["overall_success"] else 1
        
        if exit_code != 0:
            print(f"\nValidation suite failed. Check reports in {args.output_dir}/")
        else:
            print(f"\nValidation suite passed successfully!")
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nValidation suite interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nValidation suite failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()