# Configuration Reference

This document provides a comprehensive reference for all configuration options available in the MITRE ATT&CK MCP Server.

## Environment Variables

### HTTP Server Configuration

#### `MCP_HTTP_HOST`
- **Purpose**: Configures the hostname/IP address the HTTP proxy server binds to
- **Default**: `localhost`
- **Examples**: 
  - `localhost` - Local development
  - `0.0.0.0` - Listen on all interfaces (production)
  - `192.168.1.10` - Specific IP address
- **Security Note**: Use `localhost` for development, specific IPs for production

#### `MCP_HTTP_PORT`
- **Purpose**: Port number for the HTTP proxy server
- **Default**: `8000`
- **Valid Range**: 1024-65535 (recommended: 3000-9999)
- **Examples**: `8000`, `3000`, `8080`

### Data Source Configuration

#### `MITRE_DATA_URL`
- **Purpose**: URL for downloading MITRE ATT&CK data
- **Default**: https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json
- **Usage**: Override for custom data sources or local mirrors
- **Format**: Must be a valid HTTP/HTTPS URL returning STIX JSON

#### `CACHE_DIR`
- **Purpose**: Directory for caching downloaded MITRE data
- **Default**: System temporary directory
- **Usage**: Set for persistent caching across restarts
- **Example**: `/var/cache/mitre-mcp` or `./cache`

### Logging and Debug Configuration

#### `LOG_LEVEL`
- **Purpose**: Controls logging verbosity
- **Default**: `INFO`
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Development**: Use `DEBUG` for detailed logs
- **Production**: Use `INFO` or `WARNING`

#### `PYTHONUNBUFFERED`
- **Purpose**: Forces Python stdout/stderr to be unbuffered
- **Default**: Not set
- **Usage**: Set to `1` for real-time logging in containers
- **MCP Integration**: Required for proper STDIO transport

## Configuration Files

### Data Sources (`config/data_sources.yaml`)
```yaml
data_sources:
  mitre_attack:
    url: "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
    format: "stix2"
    cache_ttl: 3600
```

### Entity Schemas (`config/entity_schemas.yaml`)
```yaml
schemas:
  attack-pattern:
    required_fields: ["name", "description", "external_references"]
  intrusion-set:
    required_fields: ["name", "description"]
```

### Tools Configuration (`config/tools.yaml`)
```yaml
tools:
  search_attack:
    enabled: true
    max_results: 50
  get_technique:
    enabled: true
    include_subtechniques: true
```

## Deployment Scenarios

### Local Development
```bash
export MCP_HTTP_HOST=localhost
export MCP_HTTP_PORT=8000
export LOG_LEVEL=DEBUG
```

### Production Server
```bash
export MCP_HTTP_HOST=0.0.0.0
export MCP_HTTP_PORT=8000
export LOG_LEVEL=INFO
export CACHE_DIR=/var/cache/mitre-mcp
```

### Claude Desktop Integration
```bash
export PYTHONUNBUFFERED=1
export LOG_LEVEL=WARNING
```

### Container Deployment
```bash
export MCP_HTTP_HOST=0.0.0.0
export MCP_HTTP_PORT=8000
export PYTHONUNBUFFERED=1
export CACHE_DIR=/app/cache
```

## Security Considerations

### Network Binding
- **Development**: Use `localhost` to prevent external access
- **Production**: Use specific IP addresses, not `0.0.0.0` unless needed
- **Firewall**: Configure firewall rules for the chosen port

### Data Sources
- **Validation**: Always validate external data source URLs
- **HTTPS**: Use HTTPS URLs for data sources when possible
- **Caching**: Secure cache directory with appropriate permissions

### Logging
- **Sensitive Data**: Avoid logging sensitive information
- **Log Rotation**: Configure log rotation for production
- **Monitoring**: Monitor logs for security events

## Validation

### Configuration Validation Script
```bash
# Validate configuration
./deployment/validate_web_explorer.sh --config-only

# Test HTTP server binding
curl -f http://${MCP_HTTP_HOST}:${MCP_HTTP_PORT}/system_info
```

### Health Checks
```bash
# MCP server health
uv run python src/main_web.py --validate

# HTTP proxy health
curl -f http://localhost:8000/system_info
```

## Troubleshooting Configuration Issues

### Common Problems
1. **Port already in use**: Change `MCP_HTTP_PORT` or stop conflicting service
2. **Permission denied**: Check file permissions for cache directory
3. **Network unreachable**: Verify firewall and network configuration
4. **Data loading fails**: Check `MITRE_DATA_URL` and network connectivity

### Debug Commands
```bash
# Test environment variables
env | grep MCP_

# Validate configuration
uv run python -c "from src.config_loader import ConfigLoader; print(ConfigLoader().validate())"

# Test data loading
uv run python -c "from src.data_loader import DataLoader; dl = DataLoader(); print(dl.load_data_source('mitre_attack'))"
```

For deployment-specific troubleshooting, see [Troubleshooting Guide](TROUBLESHOOTING.md).