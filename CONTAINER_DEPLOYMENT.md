# Container Deployment Guide

This guide covers deploying the MITRE ATT&CK MCP Server using Apple's Container tool for native macOS containerization.

## Prerequisites

### Finch Installation (Recommended)
Finch provides excellent Docker-compatible container support on Apple Silicon:

1. **Install Finch**: Download from [Finch Releases](https://github.com/runfinch/finch/releases)
2. **Initialize VM**: 
   ```bash
   finch vm init
   ```
   **Note**: You may see a warning about network dependencies during VM initialization. This is expected and doesn't affect container functionality. Finch uses Apple's Virtualization.framework which provides excellent network support without requiring additional configuration.

### Apple Container (Alternative)
1. **System Requirements**: Apple silicon Mac with macOS 15 (limited functionality) or macOS 26 beta (recommended)
2. **Download**: Get the signed installer from [Apple Container Releases](https://github.com/apple/container/releases)
3. **Install**: Double-click the package and follow instructions
4. **Start System Service**: 
   ```bash
   container system start
   ```

## Building and Running

### Option 1: Using Finch (Recommended)

**Build and run with Docker Compose:**
```bash
finch compose up -d
```

**Or build and run manually:**
```bash
# Build the image
finch build --tag mitre-attack-mcp .

# Run the container
finch run -d \
  --name mitre-attack-mcp \
  -p 8080:8080 \
  -p 8000:8000 \
  mitre-attack-mcp
```

### Option 2: Using Apple Container CLI

**Build the image:**
```bash
container build --tag mitre-attack-mcp .
```

**Run the container:**
```bash
# Run with local network access
container run -d \
  --name mitre-attack-mcp \
  -p 8080:8080 \
  -p 8000:8000 \
  mitre-attack-mcp
```

### Option 3: Using Docker Compose (Traditional)

If you have Docker Compose available:
```bash
docker-compose up -d
```

**Access the services (all methods):**
- **Web Interface**: http://localhost:8080 (or http://YOUR_LOCAL_IP:8080 from other devices)
- **API Endpoint**: http://localhost:8000 (or http://YOUR_LOCAL_IP:8000 from other devices)

## Network Configuration

### Local Network Access
The container is configured to bind to `0.0.0.0`, making it accessible from other devices on your local network:

1. **Find your Mac's IP address:**
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. **Access from other devices:**
   - Web Interface: `http://YOUR_MAC_IP:8080`
   - API: `http://YOUR_MAC_IP:8000`

### Firewall Configuration
Ensure macOS firewall allows connections on ports 8080 and 8000:
```bash
# Check firewall status
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# If needed, allow connections (macOS will prompt)
# Access the services from another device to trigger the prompt
```

## Container Management

### Basic Commands
```bash
# View running containers
container list

# View logs
container logs mitre-attack-mcp

# Stop container
container stop mitre-attack-mcp

# Remove container
container rm mitre-attack-mcp

# Remove image
container image rm mitre-attack-mcp
```

### Health Monitoring
The container includes health checks for both services:
```bash
# Check container health
container inspect mitre-attack-mcp | grep -A 5 Health
```

## Architecture Overview

### Services Running in Container
1. **Nginx** (port 8080): Serves static web interface files
2. **HTTP Proxy** (port 8000): Provides API access to MITRE ATT&CK data

### Security Features
- Non-root user execution for Python application
- Security headers on web interface
- Limited container filesystem access
- Health checks for service monitoring

### Data Persistence
Logs are persisted outside the container:
```bash
# View logs directory
ls -la ./logs/
```

## Troubleshooting

### Container Won't Start
1. **Check Apple Container service:**
   ```bash
   container system start
   ```

2. **Verify system requirements:**
   ```bash
   uname -m  # Should show arm64 for Apple silicon
   sw_vers   # Check macOS version
   ```

3. **Check build logs:**
   ```bash
   container build --tag mitre-attack-mcp . --no-cache
   ```

### Network Access Issues
1. **Verify port binding:**
   ```bash
   container run -it --rm mitre-attack-mcp curl -f http://localhost:8080/
   ```

2. **Check firewall settings:**
   - System Settings > Network > Firewall
   - Ensure Python and nginx are allowed

3. **Test from another device:**
   ```bash
   # From another device on your network
   curl http://YOUR_MAC_IP:8080/
   curl http://YOUR_MAC_IP:8000/health
   ```

### Service Health Issues
```bash
# Check individual services inside container
container exec mitre-attack-mcp supervisorctl status

# Check nginx configuration
container exec mitre-attack-mcp nginx -t

# Check Python application logs
container logs mitre-attack-mcp
```

## Performance Considerations

### Resource Limits
Apple Container runs containers as lightweight VMs, providing good isolation with minimal overhead on Apple silicon.

### Data Loading
Initial startup takes 10-15 seconds for MITRE ATT&CK data loading. The health check accounts for this with a 60-second start period.

## Uninstallation

### Remove Container Resources
```bash
# Stop and remove container
container stop mitre-attack-mcp
container rm mitre-attack-mcp
container image rm mitre-attack-mcp

# Clean up volumes
rm -rf ./logs
```

### Uninstall Apple Container (if needed)
```bash
# Keep user data
uninstall-container.sh -k

# Remove all data
uninstall-container.sh -d
```