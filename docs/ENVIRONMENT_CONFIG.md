# Environment Configuration

This document describes the environment variables and configuration options available for the MITRE ATT&CK MCP Web Explorer.

## Environment Variables

### HTTP Server Configuration

#### `MCP_HTTP_HOST`
- **Default**: `localhost`
- **Description**: The hostname or IP address on which the HTTP proxy server will listen
- **Examples**:
  ```bash
  export MCP_HTTP_HOST=localhost     # Local development
  export MCP_HTTP_HOST=0.0.0.0       # Listen on all interfaces
  export MCP_HTTP_HOST=192.168.1.100 # Specific IP address
  ```

#### `MCP_HTTP_PORT`
- **Default**: `8000`
- **Description**: The port number on which the HTTP proxy server will listen
- **Valid Range**: `1-65535`
- **Examples**:
  ```bash
  export MCP_HTTP_PORT=8000  # Default port
  export MCP_HTTP_PORT=3000  # Alternative port
  export MCP_HTTP_PORT=8080  # Common web port
  ```

### Data Configuration

#### `MITRE_ATTACK_DATA_URL` (Optional)
- **Default**: Uses the official MITRE ATT&CK STIX data from GitHub
- **Description**: Override URL for MITRE ATT&CK STIX data source
- **Example**:
  ```bash
  export MITRE_ATTACK_DATA_URL=https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json
  ```

#### `DATA_CACHE_TTL` (Optional)
- **Default**: `3600` (1 hour)
- **Description**: Cache time-to-live in seconds for loaded MITRE ATT&CK data
- **Example**:
  ```bash
  export DATA_CACHE_TTL=7200  # 2 hours
  ```

### Logging Configuration

#### `LOG_LEVEL` (Optional)
- **Default**: `INFO`
- **Description**: Set the logging verbosity level
- **Valid Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Example**:
  ```bash
  export LOG_LEVEL=DEBUG    # Verbose logging
  export LOG_LEVEL=WARNING  # Minimal logging
  ```

#### `LOG_FORMAT` (Optional)
- **Default**: `%(levelname)s:%(name)s:%(message)s`
- **Description**: Python logging format string
- **Example**:
  ```bash
  export LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  ```

### Security Configuration

#### `ALLOWED_ORIGINS` (Optional)
- **Default**: `*` (all origins allowed)
- **Description**: Comma-separated list of allowed CORS origins
- **Example**:
  ```bash
  export ALLOWED_ORIGINS="http://localhost:3000,https://app.example.com"
  ```

#### `ENABLE_SECURITY_HEADERS` (Optional)
- **Default**: `true`
- **Description**: Enable or disable security headers in HTTP responses
- **Example**:
  ```bash
  export ENABLE_SECURITY_HEADERS=false  # Disable security headers
  ```

### Development Configuration

#### `DEVELOPMENT_MODE` (Optional)
- **Default**: `false`
- **Description**: Enable development mode with additional debugging features
- **Example**:
  ```bash
  export DEVELOPMENT_MODE=true
  ```

#### `RELOAD_ON_CHANGE` (Optional)
- **Default**: `false`
- **Description**: Automatically reload the server when code changes (development only)
- **Example**:
  ```bash
  export RELOAD_ON_CHANGE=true
  ```

## Configuration Files

### Docker Environment
For Docker deployments, create a `.env` file:

```env
# Docker environment configuration
MCP_HTTP_HOST=0.0.0.0
MCP_HTTP_PORT=8000
LOG_LEVEL=INFO
ALLOWED_ORIGINS=*
```

### Kubernetes ConfigMap
For Kubernetes deployments:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mitre-mcp-config
data:
  MCP_HTTP_HOST: "0.0.0.0"
  MCP_HTTP_PORT: "8000"
  LOG_LEVEL: "INFO"
  ALLOWED_ORIGINS: "*"
```

### systemd Service
For systemd service configuration:

```ini
[Unit]
Description=MITRE ATT&CK MCP Web Explorer
After=network.target

[Service]
Type=exec
User=mitre-mcp
WorkingDirectory=/opt/mitre-mcp
Environment=MCP_HTTP_HOST=0.0.0.0
Environment=MCP_HTTP_PORT=8000
Environment=LOG_LEVEL=INFO
ExecStart=/opt/mitre-mcp/.venv/bin/python start_explorer.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Deployment Scenarios

### Local Development
```bash
# Minimal setup for local development
export MCP_HTTP_HOST=localhost
export MCP_HTTP_PORT=8000
export LOG_LEVEL=DEBUG

# Start the server
uv run start_explorer.py
```

### Production Server
```bash
# Production configuration
export MCP_HTTP_HOST=0.0.0.0
export MCP_HTTP_PORT=80
export LOG_LEVEL=WARNING
export ALLOWED_ORIGINS="https://yourdomain.com"
export ENABLE_SECURITY_HEADERS=true

# Start with process manager (pm2, supervisor, etc.)
uv run src/http_proxy.py
```

### Load Balancer Setup
```bash
# Behind a load balancer
export MCP_HTTP_HOST=127.0.0.1
export MCP_HTTP_PORT=8000
export ALLOWED_ORIGINS="https://app.yourdomain.com,https://dashboard.yourdomain.com"

# Multiple instances on different ports
MCP_HTTP_PORT=8001 uv run src/http_proxy.py &
MCP_HTTP_PORT=8002 uv run src/http_proxy.py &
MCP_HTTP_PORT=8003 uv run src/http_proxy.py &
```

## Environment Validation

Use the deployment validation script to check your configuration:

```bash
# Validate current environment
./deployment/validate_web_explorer.sh

# Validate with specific environment
MCP_HTTP_PORT=3000 ./deployment/validate_web_explorer.sh
```

## Configuration Priority

Configuration values are resolved in the following priority order (highest to lowest):

1. Environment variables
2. Configuration files (`config/*.yaml`)
3. Command-line arguments
4. Default values

## Security Considerations

### Production Security
- Always set `ALLOWED_ORIGINS` to specific domains in production
- Use HTTPS in production environments
- Consider setting `MCP_HTTP_HOST` to `127.0.0.1` when behind a reverse proxy
- Enable security headers (`ENABLE_SECURITY_HEADERS=true`)

### Network Security
- Use firewalls to restrict access to the MCP port
- Consider VPN or private network access for sensitive deployments
- Implement rate limiting at the network level

### Data Security
- The application loads public MITRE ATT&CK data by default
- No sensitive data is stored or transmitted
- All data processing happens in memory

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   
   # Use a different port
   export MCP_HTTP_PORT=8001
   ```

2. **Permission denied on port < 1024**
   ```bash
   # Use a port > 1024 or run with sudo
   export MCP_HTTP_PORT=8080
   ```

3. **CORS errors**
   ```bash
   # Allow your frontend domain
   export ALLOWED_ORIGINS="https://your-frontend-domain.com"
   ```

4. **Memory issues with large datasets**
   ```bash
   # Reduce cache TTL
   export DATA_CACHE_TTL=1800  # 30 minutes
   ```

### Validation Commands
```bash
# Check environment
env | grep MCP_

# Validate configuration
./deployment/validate_web_explorer.sh

# Test server startup
uv run python -c "from src.http_proxy import create_http_proxy_server; print('OK')"
```