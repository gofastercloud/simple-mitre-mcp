# Web Explorer Troubleshooting Guide

This guide helps diagnose and resolve common issues with the MITRE ATT&CK MCP Server web explorer interface.

## Quick Diagnostic Commands

Run these commands first to identify common issues:

```bash
# 1. Validate deployment
./deployment/validate_web_explorer.sh

# 2. Check dependencies
uv run python -c "import mcp, stix2, aiohttp, aiohttp_cors; print('✅ All imports successful')"

# 3. Test server startup
uv run start_explorer.py --validate

# 4. Check port availability
lsof -i :8000  # macOS/Linux
netstat -an | grep :8000  # All platforms
```

## Common Issues and Solutions

### 1. Import Errors

#### Issue: `ModuleNotFoundError: No module named 'aiohttp'`
**Symptoms:**
```
ImportError: cannot import name 'aiohttp' from 'aiohttp'
ModuleNotFoundError: No module named 'aiohttp_cors'
```

**Solution:**
```bash
# Reinstall dependencies
uv sync --reinstall

# If that fails, clear UV cache
uv cache clean
uv sync

# Verify installation
uv run python -c "import aiohttp; print(f'aiohttp version: {aiohttp.__version__}')"
```

#### Issue: `ModuleNotFoundError: No module named 'stix2'`
**Symptoms:**
```
ModuleNotFoundError: No module named 'stix2'
ImportError: cannot import name 'stix2'
```

**Solution:**
```bash
# Check if STIX2 library is installed
uv run python -c "import stix2; print(f'stix2 version: {stix2.__version__}')"

# Reinstall if missing
uv add stix2
uv sync
```

### 2. Server Startup Issues

#### Issue: Port Already in Use
**Symptoms:**
```
Error: [Errno 48] Address already in use
OSError: [WinError 10048] Only one usage of each socket address
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
export MCP_HTTP_PORT=8080
uv run start_explorer.py
```

#### Issue: Permission Denied on Port < 1024
**Symptoms:**
```
Error: [Errno 13] Permission denied
PermissionError: [WinError 5] Access is denied
```

**Solution:**
```bash
# Use higher port number (recommended)
export MCP_HTTP_PORT=8000
uv run start_explorer.py

# OR run with elevated privileges (not recommended for development)
sudo uv run start_explorer.py  # Linux/macOS
# Run as administrator on Windows
```

#### Issue: Cannot Bind to Host Address
**Symptoms:**
```
Error: Cannot assign requested address
OSError: [Errno 99] Cannot assign requested address
```

**Solution:**
```bash
# Use localhost instead of specific IP
export MCP_HTTP_HOST=localhost

# Or use 0.0.0.0 for all interfaces
export MCP_HTTP_HOST=0.0.0.0

# Verify network configuration
ip addr show  # Linux
ifconfig  # macOS/Linux
ipconfig  # Windows
```

### 3. Web Interface Issues

#### Issue: Web Interface Won't Load
**Symptoms:**
- Browser shows "This site can't be reached"
- Connection timeout or refused

**Diagnosis:**
```bash
# Check if server is running
curl http://localhost:8000
# or
wget -O - http://localhost:8000

# Check server logs
uv run start_explorer.py  # Check console output for errors
```

**Solution:**
```bash
# Ensure all files exist
ls web_interface/index.html
ls web_interface/js/app.js

# Check for JavaScript errors in browser console (F12)
# Restart server with debug logging
export LOG_LEVEL=DEBUG
uv run start_explorer.py
```

#### Issue: 404 Not Found for Static Assets
**Symptoms:**
- Web page loads but styles/scripts missing
- Browser console shows 404 errors for CSS/JS files

**Solution:**
```bash
# Verify file structure
ls -la web_interface/
ls -la web_interface/css/
ls -la web_interface/js/

# Check HTTP proxy static file serving
grep -n "static" src/http_proxy.py

# Test specific asset URLs
curl http://localhost:8000/css/styles.css
curl http://localhost:8000/js/app.js
```

### 4. MCP Tools Not Working

#### Issue: Tools Don't Execute or Return Errors
**Symptoms:**
- Forms submit but no results appear
- Error messages in results area
- HTTP 500 errors in browser console

**Diagnosis:**
```bash
# Test MCP server directly
uv run python -c "
from src.mcp_server import create_mcp_server
from src.data_loader import DataLoader
loader = DataLoader()
data = loader.load_data()
print(f'Loaded {len(data.get(\"techniques\", []))} techniques')
"

# Check data loading
curl http://localhost:8000/system_info
```

**Solution:**
```bash
# Clear data cache and reload
rm -rf ~/.cache/mitre-mcp  # or your CACHE_DIR
uv run start_explorer.py

# Check tool configurations
cat config/tools.yaml

# Test individual endpoints
curl -X POST http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "search_attack", "parameters": {"query": "attack"}}'
```

### 5. Performance Issues

#### Issue: Slow Loading or Timeouts
**Symptoms:**
- Long delays loading web interface
- Timeout errors on tool execution
- High memory usage

**Solution:**
```bash
# Check system resources
top  # Linux/macOS
taskmgr  # Windows

# Monitor network requests
curl -w "@curl-format.txt" http://localhost:8000/system_info

# Optimize cache settings
export CACHE_DIR=/tmp/mitre-mcp-cache  # Use faster storage
```

#### Issue: High Memory Usage
**Symptoms:**
- System becomes sluggish
- Out of memory errors

**Solution:**
```bash
# Check memory usage
ps aux | grep python  # Linux/macOS
wmic process where name="python.exe" get PageFileUsage,WorkingSetSize  # Windows

# Restart server periodically
# Implement memory monitoring in production
```

### 6. Data Loading Issues

#### Issue: MITRE Data Won't Download
**Symptoms:**
```
Error downloading MITRE ATT&CK data
ConnectionError: Failed to establish connection
```

**Solution:**
```bash
# Test network connectivity
curl -I https://github.com/mitre/cti/raw/master/enterprise-attack/enterprise-attack.json

# Check for proxy/firewall issues
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# Use local data file if necessary
export MITRE_DATA_URL=file:///path/to/local/enterprise-attack.json
```

#### Issue: Invalid or Corrupted Data
**Symptoms:**
```
STIX parsing error
Invalid JSON format
```

**Solution:**
```bash
# Clear cache and re-download
rm -rf ~/.cache/mitre-mcp/*
uv run start_explorer.py

# Verify data file manually
curl -s https://github.com/mitre/cti/raw/master/enterprise-attack/enterprise-attack.json | jq . > /dev/null
```

### 7. Browser Compatibility Issues

#### Issue: Interface Doesn't Work in Older Browsers
**Symptoms:**
- JavaScript errors in console
- Forms don't submit
- Styling issues

**Solution:**
- **Chrome/Edge**: Version 88+ recommended
- **Firefox**: Version 85+ recommended  
- **Safari**: Version 14+ recommended

Update your browser or use a modern alternative.

#### Issue: Dark/Light Mode Toggle Not Working
**Symptoms:**
- Button doesn't respond
- Theme doesn't persist

**Solution:**
```bash
# Check browser localStorage support
# Open browser console (F12) and run:
localStorage.setItem('test', 'value');
console.log(localStorage.getItem('test'));

# Clear browser cache and localStorage
# In browser console:
localStorage.clear();
location.reload();
```

## Advanced Debugging

### Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
uv run start_explorer.py
```

### HTTP Request Debugging
```bash
# Monitor HTTP requests
curl -v http://localhost:8000/
curl -v -X POST http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "list_tactics", "parameters": {}}'
```

### Python Exception Debugging
```bash
# Run with Python debugger
uv run python -m pdb start_explorer.py

# Or add debugging prints
uv run python -c "
import traceback
try:
    from src.mcp_server import create_mcp_server
    server = create_mcp_server()
    print('✅ MCP server created successfully')
except Exception as e:
    traceback.print_exc()
    print(f'❌ Error: {e}')
"
```

### JavaScript Console Debugging
Open browser developer tools (F12) and check for:
- JavaScript errors in Console tab
- Network requests in Network tab  
- Failed resource loads
- CORS errors

## Environment-Specific Issues

### Windows-Specific Issues

#### PowerShell Execution Policy
```powershell
# If scripts won't run
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Path Issues
```cmd
# Check Python path
where python
where uv

# Add to PATH if necessary
set PATH=%PATH%;C:\path\to\python;C:\path\to\uv
```

### macOS-Specific Issues

#### Homebrew Python Conflicts
```bash
# Use specific Python version
which python3
uv python install 3.12

# Or use system Python
/usr/bin/python3 -m pip install uv
```

#### Permission Issues
```bash
# Fix file permissions
chmod +x deployment/validate_web_explorer.sh
chmod -R 755 web_interface/
```

### Linux-Specific Issues

#### Missing System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev python3-pip curl

# RHEL/CentOS/Fedora
sudo dnf install python3-devel python3-pip curl
```

## Getting Help

### Before Reporting Issues

1. Run the validation script: `./deployment/validate_web_explorer.sh`
2. Check the test suite: `uv run pytest tests/ -v`
3. Review this troubleshooting guide
4. Check environment variables and configuration

### Information to Include in Bug Reports

```bash
# System information
uv --version
python3 --version
curl --version

# Project state
git log --oneline -5
git status
ls -la web_interface/

# Error output
uv run start_explorer.py 2>&1 | head -50

# Environment
env | grep MCP
env | grep LOG_LEVEL
```

### Common Log Messages

#### Normal Startup
```
INFO: Starting MITRE ATT&CK MCP Server
INFO: Loading MITRE ATT&CK data...
INFO: Loaded 823 techniques, 181 groups, 43 tactics
INFO: HTTP server starting on localhost:8000
INFO: Server running at http://localhost:8000
```

#### Warning Messages
```
WARNING: Using cached data (may be outdated)
WARNING: Network request timeout, retrying...
WARNING: Some browser features may not work in compatibility mode
```

#### Error Messages
```
ERROR: Failed to import required modules
ERROR: Cannot bind to address localhost:8000
ERROR: MITRE data download failed
ERROR: MCP server initialization failed
```

Each error message includes specific guidance on resolution in the application output.

For additional support, create an issue in the project repository with the debugging information listed above.