"""Performance test specific fixtures and configuration."""

import pytest
import time
import psutil
import gc
from typing import Dict, Any, Callable


@pytest.fixture
def performance_monitor():
    """Monitor performance metrics during test execution."""
    import threading
    
    class PerformanceMonitor:
        def __init__(self):
            self.process = psutil.Process()
            self.start_time = None
            self.end_time = None
            self.start_memory = None
            self.end_memory = None
            self.peak_memory = None
            self.cpu_percent = []
            self.monitoring = False
            self.monitor_thread = None
        
        def start_monitoring(self):
            """Start performance monitoring."""
            gc.collect()  # Clean up before monitoring
            
            self.start_time = time.time()
            self.start_memory = self.process.memory_info().rss
            self.peak_memory = self.start_memory
            self.cpu_percent = []
            self.monitoring = True
            
            # Start CPU monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_cpu)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
        
        def stop_monitoring(self):
            """Stop performance monitoring and return metrics."""
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=1)
            
            self.end_time = time.time()
            self.end_memory = self.process.memory_info().rss
            
            return {
                'execution_time': self.end_time - self.start_time,
                'memory_start': self.start_memory,
                'memory_end': self.end_memory,
                'memory_peak': self.peak_memory,
                'memory_delta': self.end_memory - self.start_memory,
                'cpu_avg': sum(self.cpu_percent) / len(self.cpu_percent) if self.cpu_percent else 0,
                'cpu_max': max(self.cpu_percent) if self.cpu_percent else 0
            }
        
        def _monitor_cpu(self):
            """Monitor CPU usage in background thread."""
            while self.monitoring:
                try:
                    cpu = self.process.cpu_percent()
                    memory = self.process.memory_info().rss
                    
                    self.cpu_percent.append(cpu)
                    if memory > self.peak_memory:
                        self.peak_memory = memory
                    
                    time.sleep(0.1)
                except Exception:
                    break
    
    return PerformanceMonitor()


@pytest.fixture
def benchmark_timer():
    """Simple benchmark timer for performance tests."""
    class BenchmarkTimer:
        def __init__(self):
            self.times = {}
        
        def time_operation(self, name: str, operation: Callable, *args, **kwargs):
            """Time an operation and store the result."""
            start_time = time.time()
            result = operation(*args, **kwargs)
            end_time = time.time()
            
            self.times[name] = end_time - start_time
            return result
        
        def get_time(self, name: str) -> float:
            """Get the execution time for a named operation."""
            return self.times.get(name, 0.0)
        
        def assert_time_under(self, name: str, threshold: float):
            """Assert that an operation completed under the threshold."""
            actual_time = self.get_time(name)
            assert actual_time <= threshold, (
                f"Operation '{name}' took {actual_time:.3f}s, "
                f"which exceeds threshold of {threshold:.3f}s"
            )
    
    return BenchmarkTimer()


@pytest.fixture
def memory_profiler():
    """Memory profiling utilities for performance tests."""
    class MemoryProfiler:
        def __init__(self):
            self.process = psutil.Process()
            self.snapshots = {}
        
        def take_snapshot(self, name: str):
            """Take a memory snapshot."""
            gc.collect()  # Force garbage collection
            memory_info = self.process.memory_info()
            self.snapshots[name] = {
                'rss': memory_info.rss,
                'vms': memory_info.vms,
                'timestamp': time.time()
            }
        
        def get_memory_delta(self, start_snapshot: str, end_snapshot: str) -> Dict[str, int]:
            """Get memory delta between two snapshots."""
            start = self.snapshots[start_snapshot]
            end = self.snapshots[end_snapshot]
            
            return {
                'rss_delta': end['rss'] - start['rss'],
                'vms_delta': end['vms'] - start['vms'],
                'time_delta': end['timestamp'] - start['timestamp']
            }
        
        def assert_memory_under(self, start_snapshot: str, end_snapshot: str, threshold_mb: float):
            """Assert that memory usage increase is under threshold."""
            delta = self.get_memory_delta(start_snapshot, end_snapshot)
            delta_mb = delta['rss_delta'] / 1024 / 1024
            
            assert delta_mb <= threshold_mb, (
                f"Memory usage increased by {delta_mb:.2f}MB, "
                f"which exceeds threshold of {threshold_mb:.2f}MB"
            )
    
    return MemoryProfiler()


@pytest.fixture
def performance_thresholds():
    """Optimized performance thresholds for different operations."""
    return {
        'parsing_small': 1.0,       # seconds - small dataset parsing
        'parsing_medium': 3.0,      # seconds - medium dataset parsing  
        'parsing_large': 10.0,      # seconds - large dataset parsing
        'search_query': 0.2,        # seconds - search operations
        'technique_lookup': 0.1,    # seconds - single technique lookup
        'mcp_tool_response': 0.5,   # seconds - MCP tool response time
        'memory_per_1k_entities': 50.0,  # MB per 1000 entities
        'startup_time': 2.0,        # seconds - application startup
        'regression_factor': 1.5    # multiplier for regression detection
    }


@pytest.fixture
def large_dataset():
    """Generate large dataset for performance testing."""
    from tests.factories import PerformanceDataFactory
    return PerformanceDataFactory.create_large_dataset(1000)


@pytest.fixture
def performance_test_timeout():
    """Extended timeout for performance tests."""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Performance test exceeded maximum execution time")
    
    # Set 300 second (5 minute) timeout for performance tests
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(300)
    
    yield
    
    # Clear the alarm
    signal.alarm(0)


@pytest.fixture
def regression_detector():
    """Fixture providing performance regression detection."""
    from tests.performance.test_regression_detection import PerformanceRegressionDetector
    return PerformanceRegressionDetector()


@pytest.fixture(autouse=True)
def performance_test_setup():
    """Setup for performance tests with regression detection."""
    # Force garbage collection before test
    gc.collect()
    
    # Set high priority for consistent timing
    try:
        import os
        os.nice(-10)  # Higher priority (requires privileges)
    except (OSError, PermissionError):
        pass  # Ignore if we can't set priority
    
    yield
    
    # Cleanup after test
    gc.collect()