# Developer Guide - MITRE ATT&CK MCP Web Explorer

This guide is for developers who want to understand, modify, or extend the MITRE ATT&CK MCP Web Explorer.

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                          Web Browser                            │
├─────────────────────────────────────────────────────────────────┤
│  HTML + CSS + JavaScript (Bootstrap 5.3 + Custom Components)   │
└─────────────────────────────────────────────────────────────────┘
                                  │ HTTP/JSON
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                       HTTP Proxy Server                        │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │   Middleware    │  │   API Endpoints  │  │  Static Files  │ │
│  │  • Security     │  │  • Tool calls    │  │  • HTML/CSS/JS │ │
│  │  • Error        │  │  • Data endpoints│  │  • Assets      │ │
│  │  • CORS         │  │  • System info   │  │                │ │
│  └─────────────────┘  └──────────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                  │ MCP Protocol
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                         MCP Server                             │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │   Tool Registry │  │   Data Loader    │  │  STIX Parser   │ │
│  │  • 8 MCP Tools  │  │  • MITRE Data    │  │  • Attack      │ │
│  │  • Validation   │  │  • Caching       │  │    Patterns    │ │
│  │  • Execution    │  │  • Refreshing    │  │  • Groups      │ │
│  └─────────────────┘  └──────────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend**:
- **Python 3.12+**: Core runtime
- **FastMCP**: MCP protocol implementation
- **aiohttp**: Async HTTP server and client
- **stix2**: Official STIX 2.x parsing library
- **PyYAML**: Configuration file parsing

**Frontend**:
- **HTML5**: Semantic markup
- **Bootstrap 5.3**: UI framework and components
- **Vanilla JavaScript**: No framework dependencies
- **CSS Custom Properties**: Theme system
- **Bootstrap Icons**: Icon system

**Development Tools**:
- **uv**: Package management and virtual environments
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Type checking

## Project Structure

```
simple-mitre-mcp/
├── src/                          # Core Python modules
│   ├── mcp_server.py            # MCP server implementation
│   ├── http_proxy.py            # HTTP proxy server
│   ├── data_loader.py           # MITRE ATT&CK data loading
│   ├── config_loader.py         # Configuration management
│   └── parsers/
│       ├── base_parser.py       # Base parser interface
│       └── stix_parser.py       # STIX 2.x parser
├── web_interface/               # Frontend assets
│   ├── index.html              # Main HTML template
│   ├── css/
│   │   ├── styles.css          # Base styles
│   │   └── components.css      # Component styles
│   └── js/
│       ├── app.js              # Main application class
│       ├── api.js              # API communication layer
│       ├── SystemDashboard.js  # Dashboard component
│       ├── ToolsSection.js     # Tools form component
│       ├── ResultsSection.js   # Results display component
│       ├── SmartFormControls.js # Form enhancement component
│       └── ThemeToggle.js      # Theme switching component
├── config/                     # Configuration files
│   ├── data_sources.yaml      # Data source definitions
│   ├── entity_schemas.yaml    # Entity schema definitions
│   └── tools.yaml            # Tool definitions
├── tests/                     # Test suites
├── docs/                      # Documentation
├── deployment/               # Deployment utilities
└── examples/                # Example configurations
```

## Core Components

### 1. MCP Server (`src/mcp_server.py`)

The MCP server implements the Model Context Protocol and provides 8 tools:

```python
# Tool categories
BASIC_TOOLS = [
    "search_attack",
    "list_tactics", 
    "get_technique",
    "get_group_techniques",
    "get_technique_mitigations"
]

ADVANCED_TOOLS = [
    "build_attack_path",
    "analyze_coverage_gaps", 
    "detect_technique_relationships"
]
```

**Key Classes**:
- `MCPServer`: Main server implementation
- Tool handlers for each of the 8 tools

**Extension Points**:
- Add new tools by implementing handler functions
- Modify existing tools by updating handler logic
- Extend data processing in individual handlers

### 2. HTTP Proxy (`src/http_proxy.py`)

The HTTP proxy bridges web requests to the MCP server:

```python
class HTTPProxy:
    def __init__(self, mcp_server=None):
        self.mcp_server = mcp_server
        self.app = web.Application(middlewares=[
            self.error_handling_middleware,
            self.security_headers_middleware
        ])
```

**Key Features**:
- **Middleware system**: Security, error handling, CORS
- **API endpoints**: Tool execution, data population, system info
- **Static file serving**: Web interface assets
- **Input validation**: Comprehensive request validation

**Extension Points**:
- Add new API endpoints in `setup_routes()`
- Modify middleware behavior
- Enhance security headers and validation

### 3. Data Loader (`src/data_loader.py`)

Handles MITRE ATT&CK data loading and caching:

```python
class DataLoader:
    def load_data_source(self, source_name: str) -> Dict[str, Any]:
        # Loads and caches MITRE ATT&CK data
        # Returns structured data for MCP tools
```

**Key Features**:
- **Caching system**: In-memory caching with TTL
- **Data validation**: STIX 2.x validation
- **Error handling**: Graceful failure and retry
- **Configuration driven**: YAML-based data source config

### 4. STIX Parser (`src/parsers/stix_parser.py`)

Parses STIX 2.x data from MITRE ATT&CK:

```python
class STIXParser(BaseParser[ParsedEntityData]):
    def parse_attack_patterns(self, bundle: List[Any]) -> List[Dict[str, Any]]:
        # Parse attack patterns (techniques)
        
    def parse_courses_of_action(self, bundle: List[Any]) -> List[Dict[str, Any]]:
        # Parse courses of action (mitigations)
        
    def parse_intrusion_sets(self, bundle: List[Any]) -> List[Dict[str, Any]]:
        # Parse intrusion sets (groups)
```

## Frontend Architecture

### Component System

The frontend uses a modular component architecture without frameworks:

```javascript
// Main application orchestrator
class App {
    constructor() {
        this.components = {
            systemDashboard: null,
            toolsSection: null,
            resultsSection: null,
            smartFormControls: null,
            themeToggle: null
        };
        this.eventBus = new EventTarget();
    }
}
```

### Component Communication

Components communicate through an event bus system:

```javascript
// Publishing events
this.eventBus.dispatchEvent(new CustomEvent('toolExecutionRequested', {
    detail: { toolName, parameters, title }
}));

// Subscribing to events
this.eventBus.addEventListener('toolExecutionRequested', (event) => {
    this.handleToolExecution(event.detail);
});
```

### State Management

State is managed at the application level:

```javascript
this.state = {
    initialized: false,
    connected: false,
    currentTool: null,
    errors: []
};
```

## Development Workflow

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd simple-mitre-mcp

# Install dependencies
uv sync

# Verify installation
uv run pytest tests/ --tb=short

# Start development server
uv run start_explorer.py
```

### 2. Code Formatting and Quality

```bash
# Format code
uv run black .

# Lint code
uv run flake8 .

# Type checking
uv run mypy src/

# Run tests
uv run pytest tests/ -v
```

### 3. Frontend Development

**File Watching** (if using external tools):
```bash
# Watch CSS changes (if you have a CSS preprocessor)
sass --watch web_interface/scss:web_interface/css

# Watch JS changes (if using a bundler)
webpack --watch
```

**Browser Testing**:
```bash
# Start server
uv run start_explorer.py

# Open browser
open http://localhost:8000
```

## Adding New Features

### 1. Adding a New MCP Tool

**Step 1**: Define tool in `config/tools.yaml`:
```yaml
my_new_tool:
  description: "Description of what the tool does"
  input_schema:
    type: object
    properties:
      parameter_name:
        type: string
        description: "Parameter description"
    required: ["parameter_name"]
```

**Step 2**: Implement handler in `src/mcp_server.py`:
```python
@mcp_server.call_tool()
async def handle_my_new_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    # Validate input
    parameter_value = arguments.get("parameter_name")
    if not parameter_value:
        raise ValueError("parameter_name is required")
    
    # Perform tool logic
    result = perform_analysis(parameter_value)
    
    # Return formatted result
    return [TextContent(type="text", text=format_result(result))]
```

**Step 3**: Add to HTTP proxy tools list in `src/http_proxy.py`:
```python
valid_tools = {
    "search_attack", "list_tactics", "get_technique", 
    "get_group_techniques", "get_technique_mitigations",
    "build_attack_path", "analyze_coverage_gaps", 
    "detect_technique_relationships", "my_new_tool"  # Add here
}
```

**Step 4**: Update frontend form generation in `web_interface/js/ToolsSection.js`:
```javascript
// Form will be automatically generated from tool schema
// No changes needed unless custom UI is required
```

### 2. Adding a New API Endpoint

**Step 1**: Add route in `src/http_proxy.py`:
```python
def setup_routes(self):
    # ... existing routes ...
    self.app.router.add_get("/api/my_endpoint", self.handle_my_endpoint)
```

**Step 2**: Implement handler:
```python
async def handle_my_endpoint(self, request: web_request.Request) -> Response:
    try:
        # Validate input
        param = request.query.get("param")
        if not param:
            return web.json_response({"error": "param required"}, status=400)
        
        # Process request
        result = process_request(param)
        
        return web.json_response({"data": result})
    except Exception as e:
        logger.error(f"Error in my_endpoint: {e}")
        return web.json_response({"error": str(e)}, status=500)
```

### 3. Adding a New Frontend Component

**Step 1**: Create component file `web_interface/js/MyComponent.js`:
```javascript
class MyComponent {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.render();
    }
    
    render() {
        this.container.innerHTML = `
            <div class="my-component">
                <h3>My Component</h3>
                <button id="my-button">Click Me</button>
            </div>
        `;
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        const button = document.getElementById('my-button');
        button.addEventListener('click', () => {
            this.handleClick();
        });
    }
    
    handleClick() {
        console.log('Button clicked!');
    }
    
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Export for both Node.js and browser
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MyComponent;
} else {
    window.MyComponent = MyComponent;
}
```

**Step 2**: Include in HTML template `web_interface/index.html`:
```html
<script src="/js/MyComponent.js"></script>
```

**Step 3**: Initialize in App class `web_interface/js/app.js`:
```javascript
async initializeMyComponent() {
    if (typeof MyComponent === 'undefined') {
        throw new Error('MyComponent class not available');
    }
    
    this.components.myComponent = new MyComponent('my-component-container');
}
```

## Testing

### 1. Backend Testing

**Unit Tests**:
```python
# tests/test_my_feature.py
import pytest
from src.my_module import MyClass

class TestMyClass:
    def test_basic_functionality(self):
        instance = MyClass()
        result = instance.do_something()
        assert result == expected_value
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        instance = MyClass()
        result = await instance.do_something_async()
        assert result == expected_value
```

**Integration Tests**:
```python
# tests/test_integration.py
import pytest
from aiohttp.test_utils import AioHTTPTestCase
from src.http_proxy import HTTPProxy

class TestAPIIntegration(AioHTTPTestCase):
    async def get_application(self):
        proxy = HTTPProxy()
        return proxy.app
    
    async def test_api_endpoint(self):
        resp = await self.client.request("GET", "/api/my_endpoint?param=test")
        self.assertEqual(resp.status, 200)
        data = await resp.json()
        self.assertIn("data", data)
```

### 2. Frontend Testing

**Component Tests**:
```javascript
// tests/test_my_component.js (if using a JS testing framework)
describe('MyComponent', () => {
    it('should render correctly', () => {
        document.body.innerHTML = '<div id="test-container"></div>';
        const component = new MyComponent('test-container');
        
        expect(document.getElementById('my-button')).toBeTruthy();
    });
    
    it('should handle clicks', () => {
        document.body.innerHTML = '<div id="test-container"></div>';
        const component = new MyComponent('test-container');
        
        const button = document.getElementById('my-button');
        const spy = jest.spyOn(component, 'handleClick');
        
        button.click();
        expect(spy).toHaveBeenCalled();
    });
});
```

**Manual Testing**:
1. Load interface in different browsers
2. Test responsive design on mobile
3. Verify error handling scenarios
4. Test all tool combinations

## Configuration

### 1. YAML Configuration

**Data Sources** (`config/data_sources.yaml`):
```yaml
my_data_source:
  type: http
  url: https://example.com/data.json
  format: json
  cache_ttl: 3600
  retry_attempts: 3
```

**Entity Schemas** (`config/entity_schemas.yaml`):
```yaml
my_entity:
  fields:
    - name: id
      type: string
      required: true
    - name: description
      type: string
      required: false
```

### 2. Environment Variables

See `docs/ENVIRONMENT_CONFIG.md` for complete environment variable documentation.

### 3. Runtime Configuration

```python
# Access configuration in code
from src.config_loader import ConfigLoader

config = ConfigLoader()
data_sources = config.load_data_sources()
my_source = data_sources.get('my_data_source')
```

## Performance Optimization

### 1. Backend Performance

**Caching**:
- Use in-memory caching for frequently accessed data
- Implement TTL-based cache invalidation
- Cache tool results when appropriate

**Async Operations**:
```python
# Use async/await for I/O operations
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

**Connection Pooling**:
- Reuse HTTP connections
- Configure appropriate timeouts
- Limit concurrent connections

### 2. Frontend Performance

**Component Optimization**:
```javascript
// Use event delegation
document.addEventListener('click', (event) => {
    if (event.target.matches('.my-button')) {
        handleButtonClick(event);
    }
});

// Clean up event listeners
destroy() {
    if (this.eventListener) {
        document.removeEventListener('click', this.eventListener);
    }
}
```

**Memory Management**:
- Remove event listeners in destroy methods
- Clear intervals and timeouts
- Avoid memory leaks in closures

**Lazy Loading**:
- Load components only when needed
- Defer non-critical operations
- Use intersection observers for visibility

## Security Considerations

### 1. Input Validation

**Backend Validation**:
```python
def validate_technique_id(technique_id: str) -> bool:
    # Validate format: T#### or T####.###
    import re
    return bool(re.match(r'^T\d{4}(\.\d{3})?$', technique_id))
```

**Frontend Validation**:
```javascript
function validateInput(value, type) {
    switch(type) {
        case 'technique_id':
            return /^T\d{4}(\.\d{3})?$/.test(value);
        case 'group_id':
            return /^G\d{4}$/.test(value);
        default:
            return true;
    }
}
```

### 2. Security Headers

Security headers are automatically applied via middleware:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy: ...`

### 3. CORS Configuration

```python
# Configure CORS for specific origins in production
cors = aiohttp_cors.setup(self.app, defaults={
    "https://yourdomain.com": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
        allow_methods="*",
    )
})
```

## Deployment

### 1. Production Configuration

```python
# Use production settings
import os

# Security
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')
ENABLE_SECURITY_HEADERS = os.getenv('ENABLE_SECURITY_HEADERS', 'true').lower() == 'true'

# Performance
CACHE_TTL = int(os.getenv('CACHE_TTL', '7200'))  # 2 hours
MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS', '100'))
```

### 2. Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync --frozen

EXPOSE 8000
CMD ["uv", "run", "src/http_proxy.py"]
```

### 3. Monitoring

```python
# Add metrics collection
import time
import logging

class MetricsMiddleware:
    async def __call__(self, request, handler):
        start_time = time.time()
        try:
            response = await handler(request)
            duration = time.time() - start_time
            logging.info(f"Request: {request.path} - {response.status} - {duration:.3f}s")
            return response
        except Exception as e:
            duration = time.time() - start_time
            logging.error(f"Request failed: {request.path} - {str(e)} - {duration:.3f}s")
            raise
```

## Debugging

### 1. Backend Debugging

**Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def my_function():
    logger.debug("Starting function")
    # ... function logic ...
    logger.info(f"Processed {count} items")
```

**Python Debugger**:
```python
import pdb; pdb.set_trace()  # Breakpoint
```

### 2. Frontend Debugging

**Console Debugging**:
```javascript
console.log('Debug info:', { variable1, variable2 });
console.error('Error occurred:', error);
console.trace('Call stack');
```

**Browser DevTools**:
- Use Network tab to monitor HTTP requests
- Use Console tab for JavaScript errors
- Use Elements tab to inspect DOM changes
- Use Application tab to check localStorage

## Contributing

### 1. Code Style

Follow the established patterns:
- **Python**: PEP 8 with black formatting
- **JavaScript**: ESLint recommended rules
- **HTML/CSS**: Semantic markup and BEM naming

### 2. Testing Requirements

- All new features must include tests
- Tests should cover both happy path and error cases
- Integration tests for API endpoints
- Manual testing for UI components

### 3. Documentation

- Update relevant documentation files
- Include inline code comments for complex logic
- Add examples for new APIs
- Update user guide for new features

### 4. Pull Request Process

1. Create feature branch from main
2. Implement changes with tests
3. Run full test suite
4. Update documentation
5. Create pull request with clear description

## Troubleshooting

For detailed troubleshooting information, see `docs/TROUBLESHOOTING.md`.

## Support

- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Latest documentation updates  
- **Community**: Discussion forums

---

This developer guide provides the foundation for understanding and extending the MITRE ATT&CK MCP Web Explorer. The modular architecture and comprehensive documentation make it straightforward to add new features and customize the system for specific needs.