#!/usr/bin/env python3
"""
Performance optimization script for STIX2 library refactor.

This script identifies performance bottlenecks and provides optimization
recommendations for the STIX parser implementation.
"""

import json
import logging
import time
import cProfile
import pstats
import io
from typing import Dict, List, Any, Tuple
from pathlib import Path

from test_performance_benchmarks import PerformanceBenchmark


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """
    Performance optimization utility for STIX parser.
    """
    
    def __init__(self):
        """Initialize the performance optimizer."""
        self.benchmark = PerformanceBenchmark()
        self.optimization_results = {}
    
    def profile_parsing_methods(self, stix_data: Dict[str, Any], entity_types: List[str]) -> Dict[str, Any]:
        """
        Profile parsing methods to identify bottlenecks.
        
        Args:
            stix_data: STIX data to parse
            entity_types: Entity types to extract
            
        Returns:
            Profiling results with performance insights
        """
        logger.info("Profiling parsing methods for performance bottlenecks")
        
        results = {
            'stix2_library_profile': None,
            'custom_fallback_profile': None,
            'bottlenecks': [],
            'recommendations': []
        }
        
        # Profile STIX2 library parsing
        logger.info("Profiling STIX2 library parsing...")
        stix2_profile = self._profile_function(
            self.benchmark.parser._parse_with_stix2_library,
            stix_data, entity_types
        )
        results['stix2_library_profile'] = stix2_profile
        
        # Profile custom fallback parsing
        logger.info("Profiling custom fallback parsing...")
        custom_profile = self._profile_function(
            self.benchmark.parser._parse_with_custom_logic,
            stix_data, entity_types
        )
        results['custom_fallback_profile'] = custom_profile
        
        # Analyze bottlenecks
        results['bottlenecks'] = self._identify_bottlenecks(stix2_profile, custom_profile)
        results['recommendations'] = self._generate_optimization_recommendations(results['bottlenecks'])
        
        return results
    
    def _profile_function(self, func, *args, **kwargs) -> Dict[str, Any]:
        """
        Profile a function execution and return detailed statistics.
        
        Args:
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Profiling statistics
        """
        # Create profiler
        profiler = cProfile.Profile()
        
        # Profile the function
        profiler.enable()
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        end_time = time.time()
        profiler.disable()
        
        # Collect statistics
        stats_stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stats_stream)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions
        
        # Parse statistics
        top_functions = self._parse_profile_stats(stats)
        
        return {
            'success': success,
            'error': error,
            'execution_time': end_time - start_time,
            'total_calls': stats.total_calls,
            'top_functions': top_functions,
            'profile_output': stats_stream.getvalue()
        }
    
    def _parse_profile_stats(self, stats: pstats.Stats) -> List[Dict[str, Any]]:
        """
        Parse profiling statistics into structured data.
        
        Args:
            stats: pstats.Stats object
            
        Returns:
            List of top function statistics
        """
        top_functions = []
        
        # Get sorted statistics
        stats.sort_stats('cumulative')
        
        # Extract top functions (limit to avoid excessive data)
        for func_info, (cc, nc, tt, ct, callers) in list(stats.stats.items())[:20]:
            filename, line_num, func_name = func_info
            
            top_functions.append({
                'function': func_name,
                'filename': Path(filename).name if filename else 'unknown',
                'line_number': line_num,
                'call_count': cc,
                'total_time': tt,
                'cumulative_time': ct,
                'time_per_call': tt / cc if cc > 0 else 0,
                'cumulative_per_call': ct / cc if cc > 0 else 0
            })
        
        return top_functions
    
    def _identify_bottlenecks(self, stix2_profile: Dict[str, Any], 
                            custom_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify performance bottlenecks from profiling data.
        
        Args:
            stix2_profile: STIX2 library profiling results
            custom_profile: Custom fallback profiling results
            
        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []
        
        # Analyze STIX2 library bottlenecks
        if stix2_profile['success'] and stix2_profile['top_functions']:
            for func in stix2_profile['top_functions'][:5]:  # Top 5 time consumers
                if func['cumulative_time'] > 0.1:  # Functions taking more than 100ms
                    bottlenecks.append({
                        'type': 'stix2_library',
                        'function': func['function'],
                        'filename': func['filename'],
                        'cumulative_time': func['cumulative_time'],
                        'call_count': func['call_count'],
                        'severity': 'high' if func['cumulative_time'] > 0.5 else 'medium'
                    })
        
        # Analyze custom fallback bottlenecks
        if custom_profile['success'] and custom_profile['top_functions']:
            for func in custom_profile['top_functions'][:5]:
                if func['cumulative_time'] > 0.1:
                    bottlenecks.append({
                        'type': 'custom_fallback',
                        'function': func['function'],
                        'filename': func['filename'],
                        'cumulative_time': func['cumulative_time'],
                        'call_count': func['call_count'],
                        'severity': 'high' if func['cumulative_time'] > 0.5 else 'medium'
                    })
        
        # Compare execution times
        if (stix2_profile['success'] and custom_profile['success'] and 
            stix2_profile['execution_time'] > custom_profile['execution_time'] * 1.5):
            bottlenecks.append({
                'type': 'performance_regression',
                'description': 'STIX2 library parsing is significantly slower than custom fallback',
                'stix2_time': stix2_profile['execution_time'],
                'custom_time': custom_profile['execution_time'],
                'slowdown_factor': stix2_profile['execution_time'] / custom_profile['execution_time'],
                'severity': 'high'
            })
        
        return bottlenecks
    
    def _generate_optimization_recommendations(self, bottlenecks: List[Dict[str, Any]]) -> List[str]:
        """
        Generate optimization recommendations based on identified bottlenecks.
        
        Args:
            bottlenecks: List of identified bottlenecks
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Analyze bottlenecks and generate recommendations
        stix2_bottlenecks = [b for b in bottlenecks if b.get('type') == 'stix2_library']
        custom_bottlenecks = [b for b in bottlenecks if b.get('type') == 'custom_fallback']
        regression_bottlenecks = [b for b in bottlenecks if b.get('type') == 'performance_regression']
        
        if stix2_bottlenecks:
            recommendations.append(
                "STIX2 library parsing shows performance bottlenecks. Consider:\n"
                "  - Implementing object caching for frequently accessed STIX objects\n"
                "  - Using lazy loading for large STIX bundles\n"
                "  - Optimizing validation steps by pre-validating bundle structure"
            )
        
        if custom_bottlenecks:
            recommendations.append(
                "Custom fallback parsing has bottlenecks. Consider:\n"
                "  - Implementing more efficient dictionary access patterns\n"
                "  - Using list comprehensions instead of loops where possible\n"
                "  - Caching frequently accessed entity mappings"
            )
        
        if regression_bottlenecks:
            for bottleneck in regression_bottlenecks:
                recommendations.append(
                    f"Performance regression detected (STIX2 library is {bottleneck['slowdown_factor']:.1f}x slower). Consider:\n"
                    "  - Implementing selective STIX2 library usage for complex objects only\n"
                    "  - Using hybrid approach: STIX2 library for validation, custom parsing for extraction\n"
                    "  - Investigating STIX2 library configuration options for better performance"
                )
        
        # General recommendations
        high_severity_bottlenecks = [b for b in bottlenecks if b.get('severity') == 'high']
        if high_severity_bottlenecks:
            recommendations.append(
                "High-severity performance issues detected. General optimizations:\n"
                "  - Implement result caching for repeated parsing operations\n"
                "  - Use streaming parsing for very large STIX bundles\n"
                "  - Consider parallel processing for independent entity types\n"
                "  - Profile memory allocation patterns to reduce garbage collection overhead"
            )
        
        if not recommendations:
            recommendations.append("No significant performance bottlenecks detected. Current implementation is well-optimized.")
        
        return recommendations
    
    def run_comprehensive_optimization_analysis(self) -> Dict[str, Any]:
        """
        Run comprehensive performance optimization analysis.
        
        Returns:
            Complete optimization analysis results
        """
        logger.info("Starting comprehensive performance optimization analysis")
        
        # Create test datasets of different sizes
        datasets = {
            'small': self.benchmark.create_large_stix_dataset(50, 10, 25),
            'medium': self.benchmark.create_large_stix_dataset(200, 40, 100),
            'large': self.benchmark.create_large_stix_dataset(500, 100, 250)
        }
        
        entity_types = ['techniques', 'groups', 'mitigations']
        analysis_results = {}
        
        for dataset_name, dataset in datasets.items():
            logger.info(f"Analyzing {dataset_name} dataset...")
            
            # Run performance benchmarks
            benchmark_results = self.benchmark.benchmark_parsing_performance(
                dataset, entity_types, iterations=3
            )
            benchmark_stats = self.benchmark.calculate_performance_statistics(benchmark_results)
            
            # Run profiling analysis
            profile_results = self.profile_parsing_methods(dataset, entity_types)
            
            analysis_results[dataset_name] = {
                'dataset_size_mb': len(json.dumps(dataset).encode('utf-8')) / 1024 / 1024,
                'total_objects': len(dataset.get('objects', [])),
                'benchmark_results': benchmark_stats,
                'profile_results': profile_results
            }
        
        # Generate overall recommendations
        overall_recommendations = self._generate_overall_recommendations(analysis_results)
        
        return {
            'analysis_results': analysis_results,
            'overall_recommendations': overall_recommendations,
            'summary': self._generate_optimization_summary(analysis_results)
        }
    
    def _generate_overall_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """
        Generate overall optimization recommendations across all dataset sizes.
        
        Args:
            analysis_results: Analysis results for all datasets
            
        Returns:
            List of overall recommendations
        """
        recommendations = []
        
        # Analyze performance trends across dataset sizes
        stix2_times = []
        custom_times = []
        
        for dataset_name, results in analysis_results.items():
            benchmark = results.get('benchmark_results', {})
            stix2_perf = benchmark.get('stix2_library_performance', {})
            custom_perf = benchmark.get('custom_fallback_performance', {})
            
            if stix2_perf.get('avg_execution_time'):
                stix2_times.append((dataset_name, stix2_perf['avg_execution_time']))
            if custom_perf.get('avg_execution_time'):
                custom_times.append((dataset_name, custom_perf['avg_execution_time']))
        
        # Check for scaling issues
        if len(stix2_times) >= 2:
            small_time = next((t for name, t in stix2_times if name == 'small'), None)
            large_time = next((t for name, t in stix2_times if name == 'large'), None)
            
            if small_time and large_time:
                scaling_factor = large_time / small_time
                if scaling_factor > 20:  # Non-linear scaling
                    recommendations.append(
                        f"STIX2 library shows poor scaling (factor: {scaling_factor:.1f}). "
                        "Consider implementing streaming or chunked processing for large datasets."
                    )
        
        # Check for consistent performance regressions
        regression_count = 0
        for results in analysis_results.values():
            profile_results = results.get('profile_results', {})
            bottlenecks = profile_results.get('bottlenecks', [])
            if any(b.get('type') == 'performance_regression' for b in bottlenecks):
                regression_count += 1
        
        if regression_count >= 2:
            recommendations.append(
                "Consistent performance regressions detected across multiple dataset sizes. "
                "Consider implementing a hybrid parsing approach or optimizing STIX2 library usage."
            )
        
        # Memory usage recommendations
        recommendations.append(
            "Memory optimization recommendations:\n"
            "  - Implement object pooling for frequently created STIX objects\n"
            "  - Use generators instead of lists for large entity collections\n"
            "  - Clear intermediate parsing results to reduce memory pressure"
        )
        
        return recommendations
    
    def _generate_optimization_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate optimization summary with key metrics.
        
        Args:
            analysis_results: Analysis results for all datasets
            
        Returns:
            Optimization summary
        """
        summary = {
            'datasets_analyzed': len(analysis_results),
            'total_bottlenecks': 0,
            'high_severity_bottlenecks': 0,
            'performance_regressions': 0,
            'average_stix2_performance': 0,
            'average_custom_performance': 0
        }
        
        stix2_times = []
        custom_times = []
        
        for results in analysis_results.values():
            # Count bottlenecks
            profile_results = results.get('profile_results', {})
            bottlenecks = profile_results.get('bottlenecks', [])
            summary['total_bottlenecks'] += len(bottlenecks)
            summary['high_severity_bottlenecks'] += len([b for b in bottlenecks if b.get('severity') == 'high'])
            summary['performance_regressions'] += len([b for b in bottlenecks if b.get('type') == 'performance_regression'])
            
            # Collect performance times
            benchmark = results.get('benchmark_results', {})
            stix2_perf = benchmark.get('stix2_library_performance', {})
            custom_perf = benchmark.get('custom_fallback_performance', {})
            
            if stix2_perf.get('avg_execution_time'):
                stix2_times.append(stix2_perf['avg_execution_time'])
            if custom_perf.get('avg_execution_time'):
                custom_times.append(custom_perf['avg_execution_time'])
        
        # Calculate averages
        if stix2_times:
            summary['average_stix2_performance'] = sum(stix2_times) / len(stix2_times)
        if custom_times:
            summary['average_custom_performance'] = sum(custom_times) / len(custom_times)
        
        return summary


def main():
    """Main function to run performance optimization analysis."""
    logger.info("Starting STIX2 library performance optimization analysis")
    
    optimizer = PerformanceOptimizer()
    
    try:
        # Run comprehensive analysis
        results = optimizer.run_comprehensive_optimization_analysis()
        
        # Print summary
        print("\n" + "="*80)
        print("STIX2 LIBRARY PERFORMANCE OPTIMIZATION ANALYSIS")
        print("="*80)
        
        summary = results['summary']
        print(f"Datasets analyzed: {summary['datasets_analyzed']}")
        print(f"Total bottlenecks found: {summary['total_bottlenecks']}")
        print(f"High-severity bottlenecks: {summary['high_severity_bottlenecks']}")
        print(f"Performance regressions: {summary['performance_regressions']}")
        print(f"Average STIX2 library performance: {summary['average_stix2_performance']:.3f}s")
        print(f"Average custom fallback performance: {summary['average_custom_performance']:.3f}s")
        
        # Print recommendations
        print("\nOVERALL OPTIMIZATION RECOMMENDATIONS:")
        print("-" * 50)
        for i, recommendation in enumerate(results['overall_recommendations'], 1):
            print(f"{i}. {recommendation}")
        
        # Print detailed results for each dataset
        print("\nDETAILED ANALYSIS RESULTS:")
        print("-" * 50)
        for dataset_name, dataset_results in results['analysis_results'].items():
            print(f"\n{dataset_name.upper()} DATASET:")
            print(f"  Size: {dataset_results['dataset_size_mb']:.2f} MB")
            print(f"  Objects: {dataset_results['total_objects']}")
            
            benchmark = dataset_results['benchmark_results']
            if 'stix2_library_performance' in benchmark:
                stix2_perf = benchmark['stix2_library_performance']
                print(f"  STIX2 library: {stix2_perf.get('avg_execution_time', 0):.3f}s")
            
            if 'custom_fallback_performance' in benchmark:
                custom_perf = benchmark['custom_fallback_performance']
                print(f"  Custom fallback: {custom_perf.get('avg_execution_time', 0):.3f}s")
            
            # Print specific recommendations for this dataset
            profile_results = dataset_results['profile_results']
            if profile_results.get('recommendations'):
                print(f"  Recommendations for {dataset_name} dataset:")
                for rec in profile_results['recommendations']:
                    print(f"    - {rec}")
        
        print("\n" + "="*80)
        print("Analysis complete. Review recommendations above for optimization opportunities.")
        
    except Exception as e:
        logger.error(f"Error during optimization analysis: {e}")
        raise


if __name__ == "__main__":
    main()