# Troubleshooting Guide

This guide helps diagnose and resolve common issues with the MITRE ATT&CK MCP Web Explorer.

## Quick Diagnostics

### Health Check Commands
```bash
# 1. Validate deployment
./deployment/validate_web_explorer.sh

# 2. Test server startup
uv run python -c "from src.http_proxy import HTTPProxy; print('HTTP proxy OK')"

# 3. Test MCP server
uv run python -c "from src.mcp_server import create_mcp_server; print('MCP server OK')"

# 4. Run basic tests
uv run pytest tests/test_mcp_server.py tests/test_http_proxy_config.py -v
```

## Common Issues and Solutions

### 1. Server Won't Start

#### Symptom: "ModuleNotFoundError" or import errors
```
ModuleNotFoundError: No module named 'mcp'
```

**Solution:**
```bash
# Install dependencies
uv sync

# Verify installation
uv run python -c "import mcp, stix2, aiohttp; print('Dependencies OK')"
```

#### Symptom: "Port already in use"
```
OSError: [Errno 48] Address already in use
```

**Solutions:**
```bash
# Find what's using the port
lsof -i :8000

# Kill the process
sudo kill -9 <PID>

# Or use a different port
export MCP_HTTP_PORT=8001
uv run start_explorer.py
```

#### Symptom: "Permission denied" on port
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**
```bash
# Use unprivileged port (>1024)
export MCP_HTTP_PORT=8080

# Or run with elevated privileges (not recommended)
sudo uv run start_explorer.py
```

### 2. Web Interface Issues

#### Symptom: Blank page or "404 Not Found"
**Check:**
1. Web interface files exist:
   ```bash
   ls -la web_interface/index.html
   ls -la web_interface/css/
   ls -la web_interface/js/
   ```

2. HTTP proxy serving correct path:
   ```bash
   curl http://localhost:8000/
   ```

**Solution:**
```bash
# Verify file structure
./deployment/validate_web_explorer.sh

# Check HTTP proxy logs
uv run start_explorer.py  # Look for file serving errors
```

#### Symptom: JavaScript errors in browser console
```
ReferenceError: SystemDashboard is not defined
```

**Solutions:**
1. Check JavaScript file loading:
   ```bash
   curl http://localhost:8000/js/SystemDashboard.js
   ```

2. Verify all JS files are present:
   ```bash
   ls -la web_interface/js/*.js
   ```

3. Check for syntax errors:
   ```bash
   # If you have node.js installed
   node -c web_interface/js/app.js
   ```

#### Symptom: Styling issues or broken CSS
**Check CSS loading:**
```bash
curl http://localhost:8000/css/styles.css
curl http://localhost:8000/css/components.css
```

### 3. API and Tool Execution Issues

#### Symptom: "MCP server not available" errors
**Diagnosis:**
```bash
# Test MCP server creation
uv run python -c "
from src.mcp_server import create_mcp_server
from src.data_loader import DataLoader
server = create_mcp_server(DataLoader())
print('MCP server created successfully')
"
```

**Solutions:**
1. Ensure data loader works:
   ```bash
   uv run python -c "
   from src.data_loader import DataLoader
   loader = DataLoader()
   data = loader.load_data_source('mitre_attack')
   print(f'Loaded {len(data.get(\"techniques\", []))} techniques')
   "
   ```

2. Check network connectivity for data download:
   ```bash
   curl -I https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json
   ```

#### Symptom: Tool execution returns errors
```
{"error": "Tool execution failed: ..."}
```

**Debugging:**
1. Test individual tools:
   ```bash
   curl -X POST http://localhost:8000/call_tool \
     -H "Content-Type: application/json" \
     -d '{"tool_name": "list_tactics", "parameters": {}}'
   ```

2. Check tool parameters:
   ```bash
   curl http://localhost:8000/tools | jq '.'
   ```

3. Verify MITRE data loading:
   ```bash
   uv run python -c "
   from src.data_loader import DataLoader
   loader = DataLoader()
   data = loader.load_data_source('mitre_attack')
   print('Techniques:', len(data.get('techniques', [])))
   print('Groups:', len(data.get('groups', [])))
   print('Tactics:', len(data.get('tactics', [])))
   "
   ```

### 4. Data Loading Issues

#### Symptom: "MITRE ATT&CK data not loaded"
**Diagnosis:**
```bash
# Test data loading manually
uv run python -c "
import requests
url = 'https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json'
response = requests.get(url)
print(f'Status: {response.status_code}')
print(f'Size: {len(response.content)} bytes')
"
```

**Solutions:**
1. Check network connectivity
2. Verify firewall settings
3. Use alternative data source:
   ```bash
   export MITRE_ATTACK_DATA_URL="https://your-mirror.com/enterprise-attack.json"
   ```

#### Symptom: Slow data loading
**Optimization:**
```bash
# Increase cache TTL
export DATA_CACHE_TTL=7200  # 2 hours

# Pre-load data
uv run python -c "
from src.data_loader import DataLoader
loader = DataLoader()
loader.load_data_source('mitre_attack')
print('Data pre-loaded')
"
```

### 5. Performance Issues

#### Symptom: High memory usage
**Diagnosis:**
```bash
# Monitor memory usage
ps aux | grep python
top -p <PID>
```

**Solutions:**
1. Reduce cache time:
   ```bash
   export DATA_CACHE_TTL=1800  # 30 minutes
   ```

2. Restart service periodically (systemd):
   ```ini
   [Service]
   RuntimeMaxSec=3600  # Restart after 1 hour
   ```

#### Symptom: Slow response times
**Diagnosis:**
```bash
# Test response times
time curl http://localhost:8000/tools
time curl http://localhost:8000/system_info
```

**Solutions:**
1. Enable caching headers (already enabled by default)
2. Use a reverse proxy (nginx, Apache)
3. Monitor server resources

### 6. Browser Compatibility Issues

#### Symptom: Web interface doesn't work in older browsers
**Requirements:**
- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

**Check JavaScript compatibility:**
```javascript
// Open browser console and test
typeof fetch !== 'undefined'  // Should be true
typeof Promise !== 'undefined'  // Should be true  
typeof EventTarget !== 'undefined'  // Should be true
```

#### Symptom: CORS errors in browser
```
Access to fetch at 'http://localhost:8000/tools' from origin 'null' has been blocked by CORS policy
```

**Solutions:**
```bash
# Allow specific origins
export ALLOWED_ORIGINS="http://localhost:3000,https://your-domain.com"

# For development only - allow all origins
export ALLOWED_ORIGINS="*"
```

### 7. Security and Access Issues

#### Symptom: Security header warnings
**Check security headers:**
```bash
curl -I http://localhost:8000/
# Should include X-Content-Type-Options, X-Frame-Options, etc.
```

#### Symptom: CSP violations in browser console
**Solutions:**
1. Check Content Security Policy in HTTP proxy
2. Ensure all resources load from allowed sources
3. Update CSP if using additional external resources

### 8. Testing and Validation Issues

#### Symptom: Tests failing
```bash
# Run specific test suites
uv run pytest tests/test_mcp_server.py -v
uv run pytest tests/test_data_loader.py -v  
uv run pytest tests/test_http_proxy_config.py -v
```

**Common fixes:**
1. Ensure test environment is clean:
   ```bash
   uv run pytest --cache-clear
   ```

2. Check for port conflicts in tests
3. Verify test data availability

## Debugging Tools

### 1. Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
uv run start_explorer.py
```

### 2. Use Python Debugger
```python
# Add to any Python file for debugging
import pdb; pdb.set_trace()
```

### 3. Browser Developer Tools
- **Console**: Check for JavaScript errors
- **Network**: Monitor HTTP requests and responses
- **Application**: Check localStorage and session storage

### 4. HTTP Debugging
```bash
# Test HTTP endpoints
curl -v http://localhost:8000/
curl -v http://localhost:8000/tools
curl -v http://localhost:8000/system_info

# Test API endpoints  
curl -v http://localhost:8000/api/groups
curl -v http://localhost:8000/api/tactics
curl -v "http://localhost:8000/api/techniques?q=attack"
```

## Log Analysis

### Important Log Patterns
```bash
# Successful startup
grep "Starting HTTP proxy server" logs.txt

# Data loading
grep "Loaded.*entities" logs.txt

# Tool execution
grep "Executing tool" logs.txt

# Errors
grep "ERROR" logs.txt
grep "FAILED" logs.txt
```

### Log Locations
- **Console output**: Default logging destination
- **System logs**: `/var/log/` (if using systemd)
- **Application logs**: Configure with `LOG_FILE` environment variable

## Performance Monitoring

### Key Metrics to Monitor
1. **Response times**: HTTP endpoint latency
2. **Memory usage**: Python process memory consumption
3. **CPU usage**: Processing overhead
4. **Network I/O**: Data loading and API responses
5. **Error rates**: Failed requests and tool executions

### Monitoring Commands
```bash
# System resources
htop
iostat -x 1

# Network connections
netstat -tulpn | grep :8000

# HTTP response times
curl -w "@curl-format.txt" http://localhost:8000/system_info
```

## Getting Help

### Before Requesting Support
1. Run the deployment validation script:
   ```bash
   ./deployment/validate_web_explorer.sh
   ```

2. Collect system information:
   ```bash
   python --version
   uv --version
   curl --version
   cat /etc/os-release  # Linux
   sw_vers  # macOS
   ```

3. Gather logs:
   ```bash
   export LOG_LEVEL=DEBUG
   uv run start_explorer.py > debug.log 2>&1
   ```

### Support Channels
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check latest documentation updates
- **Community**: Discussion forums and community support

### Information to Include
1. **Environment**: OS, Python version, package versions
2. **Configuration**: Environment variables, config files
3. **Error messages**: Full error traces and logs
4. **Steps to reproduce**: Detailed reproduction steps
5. **Expected behavior**: What should happen vs. what actually happens