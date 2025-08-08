#!/usr/bin/env python3
"""
Coverage Regression Monitoring Script

This script monitors coverage changes and detects regressions by comparing
current coverage with historical baselines and category-specific requirements.

Requirements addressed:
- 4.2: Coverage gap identification and addressing
- 4.4: Coverage reporting by test category
- Regression detection for coverage maintenance
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse


class CoverageRegressionMonitor:
    """Monitors coverage changes and detects regressions."""
    
    def __init__(self, history_file: str = "validation/data/coverage_history.json"):
        self.history_file = history_file
        self.history = self._load_history()
        self.regression_thresholds = {
            "critical_regression": 5.0,  # 5% drop is critical
            "warning_regression": 2.0,   # 2% drop is warning
            "file_regression": 10.0,     # 10% drop in single file
            "new_file_threshold": 80.0   # New files should have 80%+ coverage
        }
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load coverage history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load coverage history: {e}")
        return []
    
    def _save_history(self):
        """Save coverage history to file."""
        # Keep only last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def get_current_coverage(self) -> Optional[Dict[str, Any]]:
        """Get current coverage data by running tests."""
        print("Running tests to get current coverage...")
        
        cmd = [
            "uv", "run", "pytest", 
            "tests/",
            "--cov=src",
            "--cov-report=json:validation/temp/coverage_current.json",
            "--tb=short",
            "-q"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            temp_file = "validation/temp/coverage_current.json"
            if os.path.exists(temp_file):
                with open(temp_file, 'r') as f:
                    coverage_data = json.load(f)
                
                # Clean up temp file
                os.remove(temp_file)
                
                return {
                    "timestamp": time.time(),
                    "overall_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                    "covered_lines": coverage_data.get("totals", {}).get("covered_lines", 0),
                    "total_lines": coverage_data.get("totals", {}).get("num_statements", 0),
                    "files": coverage_data.get("files", {}),
                    "test_success": result.returncode == 0
                }
            else:
                print("Error: No coverage data generated")
                return None
                
        except subprocess.TimeoutExpired:
            print("Error: Test execution timeout")
            return None
        except Exception as e:
            print(f"Error running tests: {e}")
            return None
    
    def detect_overall_regression(self, current: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect overall coverage regressions."""
        regressions = []
        
        if not self.history:
            return regressions
        
        # Compare with most recent entry
        previous = self.history[-1]
        current_coverage = current["overall_coverage"]
        previous_coverage = previous["overall_coverage"]
        
        regression_amount = previous_coverage - current_coverage
        
        if regression_amount >= self.regression_thresholds["critical_regression"]:
            regressions.append({
                "type": "critical_overall_regression",
                "current_coverage": current_coverage,
                "previous_coverage": previous_coverage,
                "regression_amount": regression_amount,
                "severity": "critical",
                "message": f"Critical overall coverage regression: {regression_amount:.1f}% drop"
            })
        elif regression_amount >= self.regression_thresholds["warning_regression"]:
            regressions.append({
                "type": "warning_overall_regression",
                "current_coverage": current_coverage,
                "previous_coverage": previous_coverage,
                "regression_amount": regression_amount,
                "severity": "warning",
                "message": f"Overall coverage regression: {regression_amount:.1f}% drop"
            })
        
        # Check trend over last 5 entries
        if len(self.history) >= 5:
            recent_coverages = [entry["overall_coverage"] for entry in self.history[-5:]]
            recent_coverages.append(current_coverage)
            
            # Check if there's a consistent downward trend
            decreasing_count = 0
            for i in range(1, len(recent_coverages)):
                if recent_coverages[i] < recent_coverages[i-1]:
                    decreasing_count += 1
            
            if decreasing_count >= 4:  # 4 out of 5 decreases
                regressions.append({
                    "type": "trend_regression",
                    "trend_data": recent_coverages,
                    "severity": "warning",
                    "message": "Consistent downward coverage trend detected over last 5 runs"
                })
        
        return regressions
    
    def detect_file_regressions(self, current: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect file-level coverage regressions."""
        regressions = []
        
        if not self.history:
            return regressions
        
        previous = self.history[-1]
        current_files = current.get("files", {})
        previous_files = previous.get("files", {})
        
        # Check existing files for regressions
        for file_path, current_data in current_files.items():
            if file_path in previous_files:
                current_coverage = current_data.get("summary", {}).get("percent_covered", 0)
                previous_coverage = previous_files[file_path].get("summary", {}).get("percent_covered", 0)
                
                regression_amount = previous_coverage - current_coverage
                
                if regression_amount >= self.regression_thresholds["file_regression"]:
                    regressions.append({
                        "type": "file_regression",
                        "file_path": file_path,
                        "current_coverage": current_coverage,
                        "previous_coverage": previous_coverage,
                        "regression_amount": regression_amount,
                        "severity": "warning",
                        "message": f"File {file_path}: {regression_amount:.1f}% coverage drop"
                    })
        
        # Check new files for adequate coverage
        new_files = set(current_files.keys()) - set(previous_files.keys())
        for file_path in new_files:
            file_coverage = current_files[file_path].get("summary", {}).get("percent_covered", 0)
            
            if file_coverage < self.regression_thresholds["new_file_threshold"]:
                regressions.append({
                    "type": "new_file_low_coverage",
                    "file_path": file_path,
                    "coverage": file_coverage,
                    "threshold": self.regression_thresholds["new_file_threshold"],
                    "severity": "warning",
                    "message": f"New file {file_path} has low coverage: {file_coverage:.1f}%"
                })
        
        return regressions
    
    def identify_coverage_gaps(self, current: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific coverage gaps that need attention."""
        gaps = []
        
        current_files = current.get("files", {})
        
        # Identify files with low coverage
        low_coverage_threshold = 70.0
        for file_path, file_data in current_files.items():
            coverage = file_data.get("summary", {}).get("percent_covered", 0)
            
            if coverage < low_coverage_threshold:
                missing_lines = file_data.get("missing_lines", [])
                
                gaps.append({
                    "type": "low_coverage_file",
                    "file_path": file_path,
                    "coverage": coverage,
                    "missing_lines_count": len(missing_lines),
                    "missing_lines": missing_lines[:10],  # First 10 missing lines
                    "severity": "info",
                    "message": f"File {file_path} has low coverage: {coverage:.1f}%"
                })
        
        # Identify functions with no coverage
        for file_path, file_data in current_files.items():
            functions = file_data.get("functions", {})
            
            for func_name, func_data in functions.items():
                if func_name and func_data.get("summary", {}).get("percent_covered", 0) == 0:
                    gaps.append({
                        "type": "uncovered_function",
                        "file_path": file_path,
                        "function_name": func_name,
                        "severity": "info",
                        "message": f"Function {func_name} in {file_path} has no coverage"
                    })
        
        return gaps
    
    def generate_regression_report(self, current: Dict[str, Any], 
                                 overall_regressions: List[Dict[str, Any]],
                                 file_regressions: List[Dict[str, Any]],
                                 coverage_gaps: List[Dict[str, Any]]) -> str:
        """Generate comprehensive regression report."""
        
        report = []
        report.append("=" * 80)
        report.append("COVERAGE REGRESSION MONITORING REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Current status
        current_coverage = current["overall_coverage"]
        report.append(f"Current Overall Coverage: {current_coverage:.1f}%")
        report.append(f"Total Lines: {current['total_lines']}")
        report.append(f"Covered Lines: {current['covered_lines']}")
        report.append("")
        
        # Regression summary
        critical_count = len([r for r in overall_regressions + file_regressions 
                            if r.get("severity") == "critical"])
        warning_count = len([r for r in overall_regressions + file_regressions 
                           if r.get("severity") == "warning"])
        
        if critical_count > 0:
            report.append(f"🚨 CRITICAL REGRESSIONS: {critical_count}")
        if warning_count > 0:
            report.append(f"⚠️  WARNING REGRESSIONS: {warning_count}")
        
        if critical_count == 0 and warning_count == 0:
            report.append("✅ NO REGRESSIONS DETECTED")
        
        report.append("")
        
        # Overall regressions
        if overall_regressions:
            report.append("OVERALL COVERAGE REGRESSIONS")
            report.append("-" * 40)
            for regression in overall_regressions:
                severity_icon = "🚨" if regression["severity"] == "critical" else "⚠️"
                report.append(f"{severity_icon} {regression['message']}")
            report.append("")
        
        # File regressions
        if file_regressions:
            report.append("FILE-LEVEL REGRESSIONS")
            report.append("-" * 40)
            for regression in file_regressions:
                severity_icon = "🚨" if regression["severity"] == "critical" else "⚠️"
                report.append(f"{severity_icon} {regression['message']}")
            report.append("")
        
        # Coverage gaps
        if coverage_gaps:
            report.append("COVERAGE GAPS IDENTIFIED")
            report.append("-" * 40)
            
            # Group by type
            low_coverage_files = [g for g in coverage_gaps if g["type"] == "low_coverage_file"]
            uncovered_functions = [g for g in coverage_gaps if g["type"] == "uncovered_function"]
            
            if low_coverage_files:
                report.append("Low Coverage Files:")
                for gap in low_coverage_files[:10]:  # Top 10
                    report.append(f"  📉 {gap['file_path']}: {gap['coverage']:.1f}% "
                                f"({gap['missing_lines_count']} missing lines)")
                
                if len(low_coverage_files) > 10:
                    report.append(f"  ... and {len(low_coverage_files) - 10} more files")
                report.append("")
            
            if uncovered_functions:
                report.append("Uncovered Functions:")
                for gap in uncovered_functions[:15]:  # Top 15
                    report.append(f"  🔍 {gap['function_name']} in {gap['file_path']}")
                
                if len(uncovered_functions) > 15:
                    report.append(f"  ... and {len(uncovered_functions) - 15} more functions")
                report.append("")
        
        # Historical comparison
        if self.history:
            report.append("HISTORICAL COMPARISON")
            report.append("-" * 40)
            
            if len(self.history) >= 5:
                recent_coverages = [entry["overall_coverage"] for entry in self.history[-5:]]
                recent_coverages.append(current_coverage)
                
                report.append("Recent Coverage Trend:")
                for i, coverage in enumerate(recent_coverages):
                    if i == len(recent_coverages) - 1:
                        report.append(f"  Current: {coverage:.1f}%")
                    else:
                        report.append(f"  Run {i+1}: {coverage:.1f}%")
                
                # Calculate trend
                if len(recent_coverages) >= 2:
                    trend = recent_coverages[-1] - recent_coverages[0]
                    trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
                    report.append(f"  {trend_icon} Trend: {trend:+.1f}% over last 5 runs")
            
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def add_to_history(self, current: Dict[str, Any]):
        """Add current coverage data to history."""
        self.history.append(current)
        self._save_history()
    
    def run_monitoring(self) -> Dict[str, Any]:
        """Run complete coverage regression monitoring."""
        print("Starting coverage regression monitoring...")
        
        # Get current coverage
        current = self.get_current_coverage()
        if not current:
            return {"success": False, "error": "Could not get current coverage data"}
        
        # Detect regressions
        overall_regressions = self.detect_overall_regression(current)
        file_regressions = self.detect_file_regressions(current)
        coverage_gaps = self.identify_coverage_gaps(current)
        
        # Generate report
        report = self.generate_regression_report(
            current, overall_regressions, file_regressions, coverage_gaps
        )
        
        # Add to history
        self.add_to_history(current)
        
        # Determine if there are critical issues
        has_critical = any(r.get("severity") == "critical" 
                          for r in overall_regressions + file_regressions)
        
        return {
            "success": True,
            "current_coverage": current,
            "overall_regressions": overall_regressions,
            "file_regressions": file_regressions,
            "coverage_gaps": coverage_gaps,
            "report": report,
            "has_critical_regressions": has_critical,
            "regression_count": len(overall_regressions) + len(file_regressions)
        }


def main():
    """Main monitoring function."""
    parser = argparse.ArgumentParser(description="Monitor coverage regressions")
    parser.add_argument("--report-file", default="coverage_regression_report.txt",
                       help="Output file for regression report")
    parser.add_argument("--fail-on-regression", action="store_true",
                       help="Exit with error code if regressions detected")
    parser.add_argument("--critical-only", action="store_true",
                       help="Only fail on critical regressions")
    
    args = parser.parse_args()
    
    monitor = CoverageRegressionMonitor()
    results = monitor.run_monitoring()
    
    if not results["success"]:
        print(f"Error: {results['error']}")
        sys.exit(1)
    
    # Save report
    with open(args.report_file, 'w') as f:
        f.write(results["report"])
    
    print(f"Regression monitoring report saved to {args.report_file}")
    print("\n" + results["report"])
    
    # Exit based on regression detection
    if args.fail_on_regression:
        if args.critical_only:
            exit_code = 1 if results["has_critical_regressions"] else 0
        else:
            exit_code = 1 if results["regression_count"] > 0 else 0
        
        if exit_code == 1:
            print(f"\nExiting with error due to detected regressions")
        
        sys.exit(exit_code)
    
    sys.exit(0)


if __name__ == "__main__":
    main()