# Environment Configuration Guide

This guide covers environment variable configuration for the MITRE ATT&CK MCP Server web explorer interface.

## Environment Variables

### HTTP Server Configuration

#### `MCP_HTTP_HOST`
- **Purpose**: Configures the hostname/IP address the HTTP proxy server binds to
- **Default**: `localhost`
- **Valid Values**: Any valid hostname or IP address
- **Examples**:
  ```bash
  export MCP_HTTP_HOST=localhost        # Local access only (default)
  export MCP_HTTP_HOST=0.0.0.0         # All interfaces (use with caution)
  export MCP_HTTP_HOST=192.168.1.100   # Specific network interface
  ```
- **Security Note**: Using `0.0.0.0` exposes the server to all network interfaces. Only use this in secure environments.

#### `MCP_HTTP_PORT`
- **Purpose**: Configures the port number the HTTP proxy server listens on
- **Default**: `8000`
- **Valid Values**: Integer between 1-65535
- **Examples**:
  ```bash
  export MCP_HTTP_PORT=8000    # Default port
  export MCP_HTTP_PORT=9090    # Alternative port
  export MCP_HTTP_PORT=80      # HTTP standard port (requires root on Unix)
  ```
- **Notes**: Ports below 1024 typically require administrator/root privileges

### Data Source Configuration

#### `MITRE_DATA_URL`
- **Purpose**: Override the default MITRE ATT&CK STIX data source URL
- **Default**: Official MITRE ATT&CK GitHub repository
- **Valid Values**: Valid HTTPS URL to STIX 2.1 bundle
- **Example**:
  ```bash
  export MITRE_DATA_URL=https://custom-server.com/attack-data.json
  ```
- **Use Cases**: 
  - Using cached/local data source
  - Testing with custom threat intelligence data
  - Air-gapped environments

#### `CACHE_DIR`
- **Purpose**: Directory for caching downloaded MITRE data
- **Default**: `~/.cache/mitre-mcp`
- **Valid Values**: Valid directory path
- **Example**:
  ```bash
  export CACHE_DIR=/var/cache/mitre-mcp
  ```

### Development and Debugging

#### `LOG_LEVEL`
- **Purpose**: Controls logging verbosity
- **Default**: `INFO`
- **Valid Values**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Examples**:
  ```bash
  export LOG_LEVEL=DEBUG     # Detailed debugging output
  export LOG_LEVEL=WARNING   # Only warnings and errors
  ```

#### `PYTHONUNBUFFERED`
- **Purpose**: Ensures Python output is not buffered (important for MCP STDIO)
- **Default**: Not set
- **Valid Values**: `1` or any non-empty value
- **Example**:
  ```bash
  export PYTHONUNBUFFERED=1
  ```
- **Required For**: MCP STDIO transport with Claude Desktop integration

## Configuration Methods

### 1. Environment Variables (Runtime)
Set variables before starting the server:
```bash
export MCP_HTTP_HOST=0.0.0.0
export MCP_HTTP_PORT=9090
uv run start_explorer.py
```

### 2. `.env` File (Recommended)
Create a `.env` file in the project root:
```bash
# .env file
MCP_HTTP_HOST=localhost
MCP_HTTP_PORT=8080
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

The application will automatically load these variables.

### 3. Shell Configuration
Add to your shell profile (`.bashrc`, `.zshrc`, etc.):
```bash
# MITRE ATT&CK MCP Configuration
export MCP_HTTP_HOST=localhost
export MCP_HTTP_PORT=8000
export LOG_LEVEL=INFO
```

## Deployment Scenarios

### Local Development
```bash
# .env file for development
MCP_HTTP_HOST=localhost
MCP_HTTP_PORT=8000
LOG_LEVEL=DEBUG
```

### Production Server
```bash
# .env file for production
MCP_HTTP_HOST=0.0.0.0
MCP_HTTP_PORT=80
LOG_LEVEL=WARNING
CACHE_DIR=/var/cache/mitre-mcp
```

### Claude Desktop Integration
```bash
# .env file for MCP client integration
PYTHONUNBUFFERED=1
LOG_LEVEL=WARNING
```

### Docker Container
```dockerfile
ENV MCP_HTTP_HOST=0.0.0.0
ENV MCP_HTTP_PORT=8000
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
```

## Security Considerations

### Network Binding
- **Development**: Use `localhost` to restrict access to local machine
- **Production**: Use specific IP addresses rather than `0.0.0.0` when possible
- **Public Deployment**: Consider using a reverse proxy (nginx, Apache) instead of direct exposure

### Port Selection
- **Development**: Use high-numbered ports (8000+) to avoid privilege requirements
- **Production**: Use standard ports (80, 443) with proper SSL termination
- **Firewall**: Ensure only necessary ports are open in firewall configuration

### Data Sources
- **Verify HTTPS**: Always use HTTPS URLs for remote data sources
- **Certificate Validation**: Ensure SSL certificate validation is enabled
- **Local Cache**: Consider using local cache for air-gapped environments

## Troubleshooting

### Common Issues

#### Port Already in Use
```
Error: [Errno 48] Address already in use
```
**Solution**: Change `MCP_HTTP_PORT` to an available port or stop the service using the port.

#### Permission Denied on Port < 1024
```
Error: [Errno 13] Permission denied
```
**Solution**: Either use a port > 1024 or run with administrator/root privileges.

#### Cannot Bind to Host
```
Error: Cannot assign requested address
```
**Solution**: Ensure the specified `MCP_HTTP_HOST` is valid and available on your system.

### Validation Commands

Test your configuration:
```bash
# Validate environment variables
./deployment/validate_web_explorer.sh

# Test server startup
uv run start_explorer.py --validate

# Check port availability
netstat -an | grep :8000
# or
lsof -i :8000
```

### Debug Mode
Enable debug logging to troubleshoot issues:
```bash
export LOG_LEVEL=DEBUG
uv run start_explorer.py
```

## Migration from Previous Versions

If upgrading from earlier versions:

1. **Check New Variables**: Review new environment variables introduced in recent updates
2. **Update Scripts**: Modify deployment scripts to use new variable names
3. **Test Configuration**: Use the validation script to ensure compatibility
4. **Backup Settings**: Save your current configuration before updating

## Integration Examples

### systemd Service
Create `/etc/systemd/system/mitre-mcp.service`:
```ini
[Unit]
Description=MITRE ATT&CK MCP Server
After=network.target

[Service]
Type=simple
User=mitre-mcp
WorkingDirectory=/opt/mitre-mcp
Environment=MCP_HTTP_HOST=0.0.0.0
Environment=MCP_HTTP_PORT=8000
Environment=LOG_LEVEL=INFO
ExecStart=/opt/mitre-mcp/.venv/bin/uv run start_explorer.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name mitre-attack.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Apache Virtual Host
```apache
<VirtualHost *:80>
    ServerName mitre-attack.yourdomain.com
    
    ProxyPreserveHost On
    ProxyPass / http://localhost:8000/
    ProxyPassReverse / http://localhost:8000/
    
    <Location />
        ProxyPassReverse /
        ProxyHTMLEnable On
        ProxyHTMLURLMap http://localhost:8000/ /
    </Location>
</VirtualHost>
```

For questions or issues with environment configuration, refer to the troubleshooting guide or create an issue in the project repository.