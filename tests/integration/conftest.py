"""Integration test specific fixtures and configuration."""

import pytest
import asyncio
import socket
import time
from contextlib import contextmanager


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async integration tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


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
    """Start a test server for integration testing."""
    import threading
    import http.server
    import socketserver
    
    class TestHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "test": true}')
        
        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "received", "data": "processed"}')
    
    with socketserver.TCPServer(("", available_port), TestHandler) as httpd:
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for server to be ready
        time.sleep(0.1)
        
        yield {
            'host': 'localhost',
            'port': available_port,
            'url': f'http://localhost:{available_port}',
            'server': httpd
        }
        
        httpd.shutdown()


@pytest.fixture
def integration_timeout():
    """Provide longer timeout for integration tests."""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Integration test exceeded maximum execution time")
    
    # Set 60 second timeout for integration tests
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(60)
    
    yield
    
    # Clear the alarm
    signal.alarm(0)


@pytest.fixture
def wait_for_condition():
    """Utility to wait for conditions in integration tests."""
    def _wait_for_condition(condition_func, timeout=10, interval=0.1):
        """Wait for a condition to become true.
        
        Args:
            condition_func: Function that returns True when condition is met
            timeout: Maximum time to wait in seconds
            interval: Check interval in seconds
            
        Returns:
            True if condition was met, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        return False
    
    return _wait_for_condition


@pytest.fixture
def mock_external_services():
    """Mock external services for integration testing."""
    from unittest.mock import patch, Mock
    
    # Mock external HTTP services
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        
        # Configure realistic responses for integration tests
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {
            "type": "bundle",
            "id": "bundle--test-integration",
            "objects": []
        }
        
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        
        yield {
            'get': mock_get,
            'post': mock_post,
            'response': mock_response
        }