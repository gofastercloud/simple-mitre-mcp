"""Unit test specific fixtures and configuration."""

import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def mock_file_system():
    """Mock file system operations for unit tests."""
    with patch('builtins.open', create=True) as mock_open, \
         patch('os.path.exists') as mock_exists, \
         patch('os.path.isfile') as mock_isfile:
        
        mock_exists.return_value = True
        mock_isfile.return_value = True
        
        yield {
            'open': mock_open,
            'exists': mock_exists,
            'isfile': mock_isfile
        }


@pytest.fixture
def mock_network_requests():
    """Mock network requests for unit tests."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        
        # Configure default successful responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_response.text = '{"test": "data"}'
        
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        
        yield {
            'get': mock_get,
            'post': mock_post,
            'response': mock_response
        }


@pytest.fixture
def isolated_unit_test():
    """Ensure complete isolation for unit tests."""
    # Patch any external dependencies that might be imported
    patches = []
    
    # Mock external services
    patches.append(patch('socket.socket'))
    patches.append(patch('subprocess.run'))
    patches.append(patch('time.sleep'))
    
    # Start all patches
    mocks = {}
    for p in patches:
        mock = p.start()
        mocks[p.attribute] = mock
    
    yield mocks
    
    # Stop all patches
    for p in patches:
        p.stop()


@pytest.fixture
def unit_test_timeout():
    """Provide timeout for unit tests to ensure they complete quickly."""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Unit test exceeded maximum execution time")
    
    # Set 10 second timeout for unit tests
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)
    
    yield
    
    # Clear the alarm
    signal.alarm(0)