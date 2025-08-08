# Deployment Guide

This guide covers deploying the MITRE ATT&CK MCP Server in various environments.

## Prerequisites

- Python 3.12 or higher
- UV package manager (recommended) or pip
- Network access to download MITRE ATT&CK data
- Minimum 2GB RAM, 1GB disk space

## Quick Deployment

### 1. Install Dependencies
```bash
# Using UV (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Basic Configuration
```bash
# Set environment variables
export MCP_HTTP_HOST=localhost
export MCP_HTTP_PORT=8000
export LOG_LEVEL=INFO
```

### 3. Start the Server
```bash
# Web interface mode
uv run start_explorer.py

# Or HTTP proxy mode
uv run src/http_proxy.py

# Or MCP server mode (for AI assistants)
uv run src/main_stdio.py
```

## Production Deployment

### Environment Setup
```bash
# Create dedicated user
sudo useradd -m -s /bin/bash mitre-mcp
sudo su - mitre-mcp

# Clone repository
git clone https://github.com/gofastercloud/simple-mitre-mcp.git
cd simple-mitre-mcp

# Install dependencies
uv sync --production
```

### Configuration
```bash
# Production environment variables
export MCP_HTTP_HOST=0.0.0.0  # Or specific IP
export MCP_HTTP_PORT=8000
export LOG_LEVEL=INFO
export CACHE_DIR=/var/cache/mitre-mcp
export PYTHONUNBUFFERED=1

# Create cache directory
sudo mkdir -p /var/cache/mitre-mcp
sudo chown mitre-mcp:mitre-mcp /var/cache/mitre-mcp
```

### SystemD Service
```bash
# Create service file
sudo tee /etc/systemd/system/mitre-mcp.service << 'EOF'
[Unit]
Description=MITRE ATT&CK MCP Server
After=network.target

[Service]
Type=simple
User=mitre-mcp
WorkingDirectory=/home/mitre-mcp/simple-mitre-mcp
Environment=MCP_HTTP_HOST=0.0.0.0
Environment=MCP_HTTP_PORT=8000
Environment=LOG_LEVEL=INFO
Environment=CACHE_DIR=/var/cache/mitre-mcp
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/mitre-mcp/simple-mitre-mcp/.venv/bin/python start_explorer.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable mitre-mcp
sudo systemctl start mitre-mcp
```

## Container Deployment

### Docker
```bash
# Build image
docker build -t mitre-mcp .

# Run container
docker run -d \
  --name mitre-mcp \
  -p 8000:8000 \
  -e MCP_HTTP_HOST=0.0.0.0 \
  -e MCP_HTTP_PORT=8000 \
  -v /var/cache/mitre-mcp:/app/cache \
  mitre-mcp
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  mitre-mcp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MCP_HTTP_HOST=0.0.0.0
      - MCP_HTTP_PORT=8000
      - LOG_LEVEL=INFO
      - CACHE_DIR=/app/cache
    volumes:
      - mitre_cache:/app/cache
    restart: unless-stopped

volumes:
  mitre_cache:
```

## Cloud Deployment

### AWS EC2
1. Launch EC2 instance (t3.medium or larger)
2. Configure security groups (port 8000)
3. Install dependencies and deploy
4. Configure Application Load Balancer (optional)
5. Set up CloudWatch monitoring

### Google Cloud Platform
```bash
# Deploy to Cloud Run
gcloud run deploy mitre-mcp \
  --image gcr.io/PROJECT_ID/mitre-mcp \
  --platform managed \
  --port 8000 \
  --memory 2Gi \
  --set-env-vars MCP_HTTP_HOST=0.0.0.0,MCP_HTTP_PORT=8000
```

### Azure Container Instances
```bash
# Deploy to ACI
az container create \
  --resource-group myResourceGroup \
  --name mitre-mcp \
  --image mitre-mcp:latest \
  --ports 8000 \
  --environment-variables MCP_HTTP_HOST=0.0.0.0 MCP_HTTP_PORT=8000
```

## Validation and Testing

### Deployment Validation
```bash
# Run validation script
./deployment/validate_web_explorer.sh

# Manual health checks
curl -f http://localhost:8000/system_info
curl -f http://localhost:8000/tools
```

### Load Testing
```bash
# Install load testing tools
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:8000
```

## Monitoring and Maintenance

### Health Monitoring
```bash
# System health endpoint
curl http://localhost:8000/system_info

# Check service status
systemctl status mitre-mcp

# View logs
journalctl -u mitre-mcp -f
```

### Performance Monitoring
See [Monitoring Guide](MONITORING.md) for detailed performance monitoring setup.

### Updates and Maintenance
```bash
# Update code
git pull origin main
uv sync

# Restart service
sudo systemctl restart mitre-mcp

# Validate update
curl -f http://localhost:8000/system_info
```

## Security Considerations

### Network Security
- Use firewall to restrict access to port 8000
- Consider reverse proxy (nginx/Apache) for HTTPS
- Implement rate limiting for public deployments

### Application Security
- Run as non-privileged user
- Secure file permissions on cache directory
- Monitor logs for security events
- Keep dependencies updated

### Data Security
- MITRE data is public, but validate sources
- Secure any custom data sources
- Monitor for data integrity issues

## Troubleshooting

For common deployment issues, see [Troubleshooting Guide](TROUBLESHOOTING.md).

### Quick Debug Commands
```bash
# Check environment
env | grep MCP_

# Test dependencies
uv run python -c "import aiohttp, stix2, mcp; print('Dependencies OK')"

# Test data loading
uv run python -c "from src.data_loader import DataLoader; dl = DataLoader(); print('Loaded:', len(dl.load_data_source('mitre_attack')))"
```

## Support

- GitHub Issues: Report bugs and feature requests
- Documentation: Check [docs/](../README.md) for detailed guides
- Community: See [Contributing](../developer/CONTRIBUTING.md) for community resources