# Dockerfile for MITRE ATT&CK MCP Server with Apple Container
# Serves static web content on port 8080 and API on port 8000

FROM python:3.12-slim

# Install nginx, curl, and supervisor
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        nginx \
        curl \
        supervisor && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Install UV package manager
RUN pip install uv

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1001 mcpuser

# Set working directory
WORKDIR /app

# Copy dependency files and README (required by pyproject.toml)
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev

# Copy project files with proper ownership
COPY --chown=mcpuser:mcpuser . .

# Fix virtual environment ownership
RUN chown -R mcpuser:mcpuser /app/.venv

# Create nginx configuration for static web content
RUN cat > /etc/nginx/sites-available/mitre-web << 'EOF'
server {
    listen 0.0.0.0:8080;
    server_name _;
    root /app/web_interface;
    index index.html;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Serve static files
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1h;
        add_header Cache-Control "public, immutable";
    }
    
    # Disable nginx version disclosure
    server_tokens off;
}
EOF

# Enable the site and disable default
RUN rm -f /etc/nginx/sites-enabled/default && \
    ln -s /etc/nginx/sites-available/mitre-web /etc/nginx/sites-enabled/mitre-web

# Create supervisor configuration
RUN cat > /etc/supervisor/conf.d/services.conf << 'EOF'
[supervisord]
nodaemon=true
user=root
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:nginx]
command=nginx -g "daemon off;"
autostart=true
autorestart=true
stderr_logfile=/var/log/nginx/error.log
stdout_logfile=/var/log/nginx/access.log

[program:mcp-http-proxy]
command=uv run -m src.http_proxy
directory=/app
user=mcpuser
autostart=true
autorestart=true
stderr_logfile=/app/logs/http_proxy_error.log
stdout_logfile=/app/logs/http_proxy.log
environment=MCP_HTTP_HOST=0.0.0.0,MCP_HTTP_PORT=8000,PYTHONPATH=/app,PYTHONUNBUFFERED=1,UV_CACHE_DIR=/tmp/uv-cache,HOME=/home/mcpuser
EOF

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /var/log/nginx /var/log/supervisor /tmp/uv-cache /var/lib/nginx/body /var/lib/nginx/fastcgi /var/lib/nginx/proxy /var/lib/nginx/scgi /var/lib/nginx/uwsgi && \
    chown -R mcpuser:mcpuser /app/logs /tmp/uv-cache && \
    chown -R www-data:www-data /var/log/nginx /var/lib/nginx && \
    touch /var/run/supervisord.pid

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check for both services
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/ && curl -f http://localhost:8000/health || exit 1

# Expose ports: 8080 for web interface, 8000 for API
EXPOSE 8080 8000

# Start supervisor to manage both nginx and HTTP proxy
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/services.conf"]