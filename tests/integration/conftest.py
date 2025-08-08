"""Integration test specific fixtures and configuration."""

import pytest
import asyncio
import socket
import time
import threading
import logging
from contextlib import contextmanager
from unittest.mock import patch, Mock

# Configure logging for integration tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async integration tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def integration_session_setup():
    """Session-level setup for integration tests."""
    logger.info("Starting integration test session")
    start_time = time.time()
    
    yield
    
    end_time = time.time()
    logger.info(f"Integration test session completed in {end_time - start_time:.2f}s")


@pytest.fixture
def available_port():
    """Find an available port for integration testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


@pytest.fixture
def integration_test_server(available_port):
    """Start a test server for integration testing with optimized setup/teardown."""
    import http.server
    import socketserver
    
    class OptimizedTestHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            # Suppress server logs during testing
            pass
            
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "test": true}')
        
        def do_POST(self):
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(b'{"status": "received", "data": "processed"}')
    
    # Use reusable address to avoid "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", available_port), OptimizedTestHandler) as httpd:
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()
        
        # Optimized server readiness check
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
                    test_socket.settimeout(0.1)
                    result = test_socket.connect_ex(('localhost', available_port))
                    if result == 0:
                        break
            except:
                pass
            time.sleep(0.01)  # Reduced sleep time
        
        yield {
            'host': 'localhost',
            'port': available_port,
            'url': f'http://localhost:{available_port}',
            'server': httpd
        }
        
        # Optimized shutdown
        httpd.shutdown()
        server_thread.join(timeout=1.0)


@pytest.fixture
def integration_timeout():
    """Provide optimized timeout for integration tests."""
    import signal
    import platform
    
    if platform.system() == "Windows":
        # Windows doesn't support SIGALRM, use a different approach
        yield
        return
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Integration test exceeded maximum execution time")
    
    # Reduced timeout for faster feedback
    original_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # Reduced from 60 to 30 seconds
    
    yield
    
    # Restore original handler and clear alarm
    signal.alarm(0)
    signal.signal(signal.SIGALRM, original_handler)


@pytest.fixture
def wait_for_condition():
    """Optimized utility to wait for conditions in integration tests."""
    def _wait_for_condition(condition_func, timeout=5, interval=0.05):
        """Wait for a condition to become true with optimized timing.
        
        Args:
            condition_func: Function that returns True when condition is met
            timeout: Maximum time to wait in seconds (reduced default)
            interval: Check interval in seconds (reduced for faster response)
            
        Returns:
            True if condition was met, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if condition_func():
                    return True
            except Exception:
                # Ignore exceptions during condition checking
                pass
            time.sleep(interval)
        return False
    
    return _wait_for_condition


@pytest.fixture(scope="session")
def mock_external_services():
    """Session-scoped mock external services for integration testing."""
    # Mock external HTTP services at session level for better performance
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('aiohttp.ClientSession.get') as mock_aiohttp_get, \
         patch('aiohttp.ClientSession.post') as mock_aiohttp_post:
        
        # Configure realistic responses for integration tests
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.status = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {
            "type": "bundle",
            "id": "bundle--test-integration",
            "objects": []
        }
        
        # Configure async response mock
        async def async_json():
            return {
                "type": "bundle",
                "id": "bundle--test-integration",
                "objects": []
            }
        
        mock_async_response = Mock()
        mock_async_response.status = 200
        mock_async_response.headers = {'Content-Type': 'application/json'}
        mock_async_response.json = async_json
        
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        mock_aiohttp_get.return_value.__aenter__.return_value = mock_async_response
        mock_aiohttp_post.return_value.__aenter__.return_value = mock_async_response
        
        yield {
            'get': mock_get,
            'post': mock_post,
            'aiohttp_get': mock_aiohttp_get,
            'aiohttp_post': mock_aiohttp_post,
            'response': mock_response,
            'async_response': mock_async_response
        }


@pytest.fixture
def integration_data_loader():
    """Optimized mock data loader for integration tests."""
    from src.data_loader import DataLoader
    
    mock_loader = Mock(spec=DataLoader)
    
    # Pre-configured comprehensive test data
    test_data = {
        "tactics": [
            {"id": "TA0001", "name": "Initial Access", "description": "Initial access tactic"},
            {"id": "TA0002", "name": "Execution", "description": "Execution tactic"},
            {"id": "TA0003", "name": "Persistence", "description": "Persistence tactic"},
        ],
        "techniques": [
            {
                "id": "T1055", "name": "Process Injection", 
                "description": "Process injection technique",
                "tactics": ["TA0002"], "platforms": ["Windows", "Linux"],
                "mitigations": ["M1040"]
            },
            {
                "id": "T1059", "name": "Command and Scripting Interpreter",
                "description": "Command interpreter technique", 
                "tactics": ["TA0002"], "platforms": ["Windows", "Linux", "macOS"],
                "mitigations": ["M1038"]
            },
        ],
        "groups": [
            {
                "id": "G0016", "name": "APT29", "aliases": ["Cozy Bear"],
                "description": "APT29 threat group", "techniques": ["T1055", "T1059"]
            },
        ],
        "mitigations": [
            {
                "id": "M1040", "name": "Behavior Prevention on Endpoint",
                "description": "Endpoint behavior prevention", "techniques": ["T1055"]
            },
            {
                "id": "M1038", "name": "Execution Prevention", 
                "description": "Execution prevention", "techniques": ["T1059"]
            },
        ],
        "relationships": [
            {"type": "uses", "source_id": "G0016", "target_id": "T1055"},
            {"type": "uses", "source_id": "G0016", "target_id": "T1059"},
            {"type": "mitigates", "source_id": "M1040", "target_id": "T1055"},
            {"type": "mitigates", "source_id": "M1038", "target_id": "T1059"},
        ]
    }
    
    mock_loader.get_cached_data.return_value = test_data
    mock_loader.config = {
        "data_sources": {
            "mitre_attack": {
                "url": "https://example.com/test-data.json",
                "format": "stix",
                "entity_types": ["techniques", "groups", "tactics", "mitigations"],
            }
        }
    }
    
    return mock_loader


@pytest.fixture
def performance_monitor():
    """Monitor performance of integration tests."""
    start_time = time.time()
    memory_usage = []
    
    def get_memory_usage():
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0
    
    initial_memory = get_memory_usage()
    
    yield {
        'start_time': start_time,
        'get_memory': get_memory_usage,
        'initial_memory': initial_memory
    }
    
    end_time = time.time()
    final_memory = get_memory_usage()
    execution_time = end_time - start_time
    memory_delta = final_memory - initial_memory
    
    # Log performance metrics
    logger.info(f"Test execution time: {execution_time:.3f}s")
    if memory_delta > 0:
        logger.info(f"Memory usage increase: {memory_delta:.1f}MB")


@pytest.fixture(autouse=True)
def integration_test_cleanup():
    """Automatic cleanup for integration tests."""
    # Pre-test setup
    yield
    
    # Post-test cleanup
    # Clear any global state
    import gc
    gc.collect()
    
    # Reset asyncio event loop if needed
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Cancel any pending tasks
            pending = asyncio.all_tasks(loop)
            for task in pending:
                if not task.done():
                    task.cancel()
    except RuntimeError:
        # No event loop running
        pass