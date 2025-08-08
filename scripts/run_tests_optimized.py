#!/usr/bin/env python3
"""
Optimized test execution script with parallel processing and performance monitoring.

This script provides various test execution modes optimized for different scenarios:
- Fast development cycle (unit tests only)
- Parallel execution with optimal worker count
- Performance monitoring and reporting
- Category-based test execution
"""

import os
import sys
import subprocess
import argparse
import multiprocessing
import time
from pathlib import Path


def get_optimal_worker_count():
    """Calculate optimal number of test workers based on system resources."""
    cpu_count = multiprocessing.cpu_count()
    
    # Use 75% of available CPUs, minimum 1, maximum 8
    optimal = max(1, min(8, int(cpu_count * 0.75)))
    
    print(f"System CPUs: {cpu_count}, Using {optimal} test workers")
    return optimal


def run_command(cmd, description):
    """Run a command and track execution time."""
    print(f"\n{'='*60}")
    print(f"RUNNING: {description}")
    print(f"COMMAND: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=False)
    duration = time.time() - start_time
    
    print(f"\n{description} completed in {duration:.2f} seconds")
    print(f"Exit code: {result.returncode}")
    
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Optimized test execution")
    parser.add_argument(
        "--mode",
        choices=["fast", "parallel", "full", "benchmark", "category"],
        default="parallel",
        help="Test execution mode"
    )
    parser.add_argument(
        "--category",
        choices=["unit", "integration", "performance", "compatibility", "deployment", "e2e"],
        help="Test category to run (used with --mode category)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of parallel workers (auto-detected if not specified)"
    )
    parser.add_argument(
        "--timing-report",
        action="store_true",
        help="Generate detailed timing report"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Include coverage reporting"
    )
    
    args = parser.parse_args()
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Base pytest command
    base_cmd = ["uv", "run", "pytest"]
    
    # Configure based on mode
    if args.mode == "fast":
        # Fast development cycle - unit tests only, no coverage
        cmd = base_cmd + [
            "tests/unit/",
            "-m", "not slow",
            "--maxfail=5",
            "--tb=short",
            "-q"
        ]
        success = run_command(cmd, "Fast Development Tests")
        
    elif args.mode == "parallel":
        # Parallel execution with optimal worker count
        workers = args.workers or get_optimal_worker_count()
        cmd = base_cmd + [
            f"-n{workers}",
            "--dist=worksteal",  # Dynamic work distribution
            "tests/",
        ]
        
        if args.coverage:
            cmd.extend(["--cov=src", "--cov-report=term-missing"])
        
        if args.timing_report:
            cmd.append("--timing-report")
            
        success = run_command(cmd, f"Parallel Tests ({workers} workers)")
        
    elif args.mode == "full":
        # Full test suite with all optimizations
        workers = args.workers or get_optimal_worker_count()
        cmd = base_cmd + [
            f"-n{workers}",
            "--dist=worksteal",
            "tests/",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--timing-report",
            "--durations=20"
        ]
        success = run_command(cmd, f"Full Test Suite ({workers} workers)")
        
    elif args.mode == "benchmark":
        # Performance benchmarks
        cmd = base_cmd + [
            "tests/performance/",
            "--benchmark",
            "--timing-report",
            "-v"
        ]
        success = run_command(cmd, "Performance Benchmarks")
        
    elif args.mode == "category":
        # Category-specific tests
        if not args.category:
            print("ERROR: --category must be specified when using --mode category")
            sys.exit(1)
            
        cmd = base_cmd + [
            f"tests/{args.category}/",
            "-v"
        ]
        
        if args.coverage:
            cmd.extend(["--cov=src", "--cov-report=term-missing"])
            
        if args.timing_report:
            cmd.append("--timing-report")
            
        success = run_command(cmd, f"{args.category.title()} Tests")
    
    # Print execution summary
    print(f"\n{'='*60}")
    print("EXECUTION SUMMARY")
    print(f"{'='*60}")
    print(f"Mode: {args.mode}")
    if args.category:
        print(f"Category: {args.category}")
    print(f"Status: {'PASSED' if success else 'FAILED'}")
    
    if not success:
        print("\nSome tests failed. Check the output above for details.")
        sys.exit(1)
    else:
        print("\nAll tests passed successfully!")


if __name__ == "__main__":
    main()