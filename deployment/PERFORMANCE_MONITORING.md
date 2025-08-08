# Performance Monitoring and Metrics Collection

This guide covers performance monitoring, metrics collection, and optimization strategies for the MITRE ATT&CK MCP Server web explorer.

## Built-in Performance Features

### Memory Management
The web interface includes automatic memory management:
- Event listener cleanup in component destructors
- Automatic result history trimming (10 most recent)
- Connection monitoring with cleanup on page unload
- DOM element cleanup when components are destroyed

### Response Time Tracking
Built-in timing metrics for:
- Tool execution duration
- Data loading times  
- API response times
- Component initialization time

## Monitoring System Performance

### Server-Side Metrics

#### CPU and Memory Usage
```bash
# Monitor Python process
top -p $(pgrep -f start_explorer.py)

# Detailed memory analysis
ps -p $(pgrep -f start_explorer.py) -o pid,ppid,cmd,%mem,%cpu,rss,vsz

# Memory usage over time
while true; do
  echo "$(date): $(ps -p $(pgrep -f start_explorer.py) -o rss= | tr -d ' ') KB"
  sleep 30
done
```

#### HTTP Request Metrics
```bash
# Monitor HTTP connections
netstat -an | grep :8000

# Request rate monitoring
tail -f /var/log/access.log | grep -E "(GET|POST)" --line-buffered | \
  while read line; do echo "$(date): $line"; done
```

### Application-Level Metrics

#### Data Loading Performance
```bash
# Test data loading time
time uv run python -c "
from src.data_loader import DataLoader
import time
start = time.time()
loader = DataLoader()
data = loader.load_data()
print(f'Data loaded in {time.time() - start:.2f}s')
print(f'Techniques: {len(data.get(\"techniques\", []))}')
print(f'Groups: {len(data.get(\"groups\", []))}')
"
```

#### Tool Execution Metrics
```bash
# Test tool response times
curl -s -w "Time: %{time_total}s\n" \
  -X POST http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "search_attack", "parameters": {"query": "attack"}}'
```

#### Endpoint Performance
```bash
# Test all endpoints
endpoints=(
  "/"
  "/tools"  
  "/system_info"
  "/api/groups"
  "/api/tactics"
  "/api/techniques?q=test"
)

for endpoint in "${endpoints[@]}"; do
  echo "Testing $endpoint"
  curl -s -w "Time: %{time_total}s, Size: %{size_download} bytes\n" \
    "http://localhost:8000$endpoint" > /dev/null
done
```

## Client-Side Performance Monitoring

### Browser Performance API
The web interface leverages built-in browser APIs for performance tracking:

```javascript
// Performance timing (automatically tracked in ResultsSection)
const start = performance.now();
// ... operation ...
const duration = performance.now() - start;
console.log(`Operation took ${duration.toFixed(2)}ms`);

// Memory usage (if available)
if (performance.memory) {
  console.log('Used JS heap:', performance.memory.usedJSHeapSize);
  console.log('Total JS heap:', performance.memory.totalJSHeapSize);
}

// Resource timing
performance.getEntriesByType('resource').forEach(entry => {
  if (entry.name.includes('api/')) {
    console.log(`API call ${entry.name}: ${entry.duration.toFixed(2)}ms`);
  }
});
```

### Component Performance Tracking

#### SystemDashboard Component
- Dashboard rendering time tracked
- Data fetch duration recorded
- Card update performance monitored

#### ToolsSection Component
- Form generation time measured
- Validation performance tracked
- Submission response time recorded

#### ResultsSection Component
- Result parsing duration tracked
- Display rendering time measured
- History management performance monitored

## Performance Metrics Collection

### Custom Metrics Implementation

Create a metrics collection module:

```python
# deployment/metrics_collector.py
import time
import psutil
import json
from datetime import datetime
from typing import Dict, Any

class MetricsCollector:
    def __init__(self):
        self.metrics = []
        self.start_time = time.time()
    
    def record_metric(self, metric_name: str, value: float, 
                     tags: Dict[str, str] = None):
        """Record a performance metric"""
        metric = {
            'timestamp': datetime.utcnow().isoformat(),
            'metric': metric_name,
            'value': value,
            'tags': tags or {}
        }
        self.metrics.append(metric)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        process = psutil.Process()
        return {
            'cpu_percent': process.cpu_percent(interval=1),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'memory_percent': process.memory_percent(),
            'open_files': len(process.open_files()),
            'connections': len(process.connections()),
            'uptime': time.time() - self.start_time
        }
    
    def record_request(self, endpoint: str, duration: float, 
                      status_code: int):
        """Record HTTP request metrics"""
        self.record_metric('http_request_duration', duration, {
            'endpoint': endpoint,
            'status': str(status_code)
        })
    
    def record_tool_execution(self, tool_name: str, duration: float, 
                             success: bool):
        """Record MCP tool execution metrics"""
        self.record_metric('tool_execution_duration', duration, {
            'tool': tool_name,
            'success': str(success)
        })
    
    def export_metrics(self, format_type: str = 'json') -> str:
        """Export metrics in specified format"""
        if format_type == 'json':
            return json.dumps({
                'system': self.get_system_metrics(),
                'metrics': self.metrics[-100:]  # Last 100 metrics
            }, indent=2)
        elif format_type == 'prometheus':
            # Convert to Prometheus format
            output = []
            for metric in self.metrics[-100:]:
                tags = ','.join([f'{k}="{v}"' for k, v in metric['tags'].items()])
                line = f"{metric['metric']}"
                if tags:
                    line += f"{{{tags}}}"
                line += f" {metric['value']} {int(time.mktime(datetime.fromisoformat(metric['timestamp']).timetuple()))}"
                output.append(line)
            return '\n'.join(output)
```

### Integration with HTTP Proxy

Add metrics collection to the HTTP proxy:

```python
# In src/http_proxy.py, add metrics collection
from deployment.metrics_collector import MetricsCollector

class HTTPProxy:
    def __init__(self, mcp_server=None):
        self.metrics = MetricsCollector()
        # ... existing initialization ...
    
    async def handle_request(self, request):
        start_time = time.time()
        try:
            response = await self._process_request(request)
            duration = time.time() - start_time
            self.metrics.record_request(
                request.path, duration, response.status
            )
            return response
        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_request(
                request.path, duration, 500
            )
            raise
```

### Metrics Dashboard

Create a metrics endpoint:

```python
async def metrics_endpoint(self, request):
    """Serve performance metrics"""
    format_type = request.query.get('format', 'json')
    metrics_data = self.metrics.export_metrics(format_type)
    
    if format_type == 'prometheus':
        return web.Response(text=metrics_data, 
                          content_type='text/plain')
    else:
        return web.Response(text=metrics_data,
                          content_type='application/json')
```

## Performance Optimization Strategies

### Server-Side Optimizations

#### 1. Data Caching
```python
# Implement smart caching in data_loader.py
import functools
from datetime import datetime, timedelta

@functools.lru_cache(maxsize=128)
def get_cached_techniques(cache_key: str):
    """Cache technique data with TTL"""
    return self._load_techniques()

# Cache invalidation strategy
def invalidate_cache_if_stale(cache_time: datetime, ttl_hours: int = 24):
    if datetime.now() - cache_time > timedelta(hours=ttl_hours):
        get_cached_techniques.cache_clear()
```

#### 2. Async Processing
```python
# Use async processing for heavy operations
import asyncio
from concurrent.futures import ThreadPoolExecutor

class DataProcessor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_large_dataset(self, data):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self._process_sync, data
        )
```

#### 3. Response Compression
```python
# Enable gzip compression for large responses
from aiohttp_compress import compress_middleware

app.middlewares.append(compress_middleware)
```

### Client-Side Optimizations

#### 1. Lazy Loading
```javascript
// Implement lazy loading for large result sets
class ResultsSection {
    displayLargeResults(results) {
        if (results.length > 1000) {
            this.displayPaginated(results, 100);
        } else {
            this.displayAll(results);
        }
    }
    
    displayPaginated(results, pageSize) {
        // Show first page immediately
        this.showPage(results.slice(0, pageSize));
        
        // Load more on scroll/demand
        this.setupInfiniteScroll(results, pageSize);
    }
}
```

#### 2. Debounced Input
```javascript
// Debounce technique autocomplete for better performance
class SmartFormControls {
    setupTechniqueAutocomplete() {
        let timeoutId;
        this.techniqueInput.addEventListener('input', (e) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                this.searchTechniques(e.target.value);
            }, 300); // 300ms debounce
        });
    }
}
```

#### 3. Virtual Scrolling
```javascript
// Virtual scrolling for large lists
class VirtualScrollList {
    constructor(container, items, itemHeight) {
        this.container = container;
        this.items = items;
        this.itemHeight = itemHeight;
        this.visibleStart = 0;
        this.visibleEnd = 0;
        this.setupVirtualScrolling();
    }
    
    render() {
        const containerHeight = this.container.clientHeight;
        const scrollTop = this.container.scrollTop;
        
        this.visibleStart = Math.floor(scrollTop / this.itemHeight);
        this.visibleEnd = Math.min(
            this.items.length,
            this.visibleStart + Math.ceil(containerHeight / this.itemHeight) + 1
        );
        
        this.renderVisibleItems();
    }
}
```

## Performance Benchmarking

### Load Testing Script

```bash
#!/bin/bash
# deployment/load_test.sh

echo "🚀 MITRE ATT&CK MCP Server Load Test"

# Configuration
HOST="http://localhost:8000"
CONCURRENT_USERS=10
TEST_DURATION=60
ENDPOINTS=(
    "/"
    "/tools"
    "/system_info"
    "/api/groups"
    "/api/tactics"
)

# Test function
run_load_test() {
    local endpoint=$1
    local concurrent=$2
    local duration=$3
    
    echo "Testing $endpoint with $concurrent concurrent users for ${duration}s"
    
    # Use wrk if available, otherwise ab
    if command -v wrk >/dev/null 2>&1; then
        wrk -t$concurrent -c$concurrent -d${duration}s "$HOST$endpoint"
    elif command -v ab >/dev/null 2>&1; then
        ab -n 1000 -c $concurrent "$HOST$endpoint"
    else
        echo "Install wrk or ab for load testing"
    fi
}

# Run tests
for endpoint in "${ENDPOINTS[@]}"; do
    run_load_test "$endpoint" $CONCURRENT_USERS $TEST_DURATION
    echo "---"
done

# Test tool execution under load
echo "Testing tool execution under load"
curl -X POST "$HOST/call_tool" \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "search_attack", "parameters": {"query": "test"}}' \
  -s -w "Time: %{time_total}s\n"
```

### Performance Regression Testing

```python
#!/usr/bin/env python3
# deployment/performance_regression_test.py

import time
import statistics
import json
import requests
from typing import List, Dict

class PerformanceTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    def time_request(self, method: str, endpoint: str, 
                    data: dict = None, iterations: int = 10) -> Dict:
        """Time multiple requests and return statistics"""
        times = []
        
        for _ in range(iterations):
            start = time.time()
            try:
                if method.upper() == 'POST':
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data,
                        timeout=30
                    )
                else:
                    response = requests.get(
                        f"{self.base_url}{endpoint}",
                        timeout=30
                    )
                
                response.raise_for_status()
                times.append(time.time() - start)
                
            except Exception as e:
                print(f"Request failed: {e}")
                continue
        
        if not times:
            return {"error": "All requests failed"}
        
        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "std": statistics.stdev(times) if len(times) > 1 else 0,
            "count": len(times)
        }
    
    def run_benchmark_suite(self) -> Dict:
        """Run complete benchmark suite"""
        results = {}
        
        # Test static endpoints
        static_tests = [
            ("GET", "/"),
            ("GET", "/tools"),
            ("GET", "/system_info"),
            ("GET", "/api/groups"),
            ("GET", "/api/tactics"),
        ]
        
        for method, endpoint in static_tests:
            print(f"Testing {method} {endpoint}...")
            results[f"{method}_{endpoint}"] = self.time_request(method, endpoint)
        
        # Test tool execution
        tool_tests = [
            ("search_attack", {"query": "attack"}),
            ("list_tactics", {}),
            ("get_technique", {"technique_id": "T1055"}),
        ]
        
        for tool_name, params in tool_tests:
            print(f"Testing tool {tool_name}...")
            results[f"tool_{tool_name}"] = self.time_request(
                "POST", "/call_tool",
                {"tool_name": tool_name, "parameters": params}
            )
        
        return results

if __name__ == "__main__":
    tester = PerformanceTest()
    results = tester.run_benchmark_suite()
    
    print("\n" + "="*50)
    print("PERFORMANCE BENCHMARK RESULTS")
    print("="*50)
    
    for test_name, stats in results.items():
        if "error" not in stats:
            print(f"{test_name:30} | "
                  f"Mean: {stats['mean']*1000:6.1f}ms | "
                  f"Median: {stats['median']*1000:6.1f}ms | "
                  f"Min: {stats['min']*1000:6.1f}ms | "
                  f"Max: {stats['max']*1000:6.1f}ms")
        else:
            print(f"{test_name:30} | ERROR: {stats['error']}")
```

## Alerting and Monitoring

### Basic Health Check
```bash
#!/bin/bash
# deployment/health_check.sh

HOST="http://localhost:8000"
MAX_RESPONSE_TIME=5  # seconds

check_endpoint() {
    local endpoint=$1
    local response_time
    
    response_time=$(curl -s -w "%{time_total}" "$HOST$endpoint" -o /dev/null)
    
    if (( $(echo "$response_time > $MAX_RESPONSE_TIME" | bc -l) )); then
        echo "⚠️  SLOW: $endpoint took ${response_time}s (> ${MAX_RESPONSE_TIME}s)"
        return 1
    else
        echo "✅ OK: $endpoint (${response_time}s)"
        return 0
    fi
}

# Check critical endpoints
endpoints=("/" "/system_info" "/tools")
failed=0

for endpoint in "${endpoints[@]}"; do
    if ! check_endpoint "$endpoint"; then
        ((failed++))
    fi
done

if [ $failed -gt 0 ]; then
    echo "❌ $failed endpoint(s) failing performance checks"
    exit 1
else
    echo "✅ All endpoints performing within acceptable limits"
    exit 0
fi
```

### Prometheus Integration
```python
# deployment/prometheus_exporter.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active HTTP connections')
TOOL_EXECUTIONS = Counter('tool_executions_total', 'Tool executions', ['tool', 'status'])

class PrometheusExporter:
    def __init__(self, port: int = 9090):
        self.port = port
        start_http_server(port)
    
    def record_request(self, method: str, endpoint: str, duration: float):
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        REQUEST_DURATION.observe(duration)
    
    def record_tool_execution(self, tool_name: str, success: bool):
        status = 'success' if success else 'error'
        TOOL_EXECUTIONS.labels(tool=tool_name, status=status).inc()
```

For production deployments, consider integrating with monitoring systems like Grafana, DataDog, or New Relic for comprehensive performance visibility.