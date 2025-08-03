# MITRE ATT&CK MCP Server

A Model Context Protocol (MCP) server that provides structured access to the MITRE ATT&CK framework for Large Language Models. This server enables security analysts, threat intelligence researchers, and cybersecurity professionals to query and explore the MITRE ATT&CK knowledge base through natural language interactions.

## Features

- Query MITRE ATT&CK tactics, techniques, and mitigations
- Search across the entire threat intelligence framework
- Explore threat group TTPs (Tactics, Techniques, and Procedures)
- Access relationships between security entities
- Extensible architecture supporting multiple security frameworks

## Quick Start

### Prerequisites

- Python 3.8 or higher
- UV package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mitre-attack-mcp-server
```

2. Install dependencies:
```bash
uv sync
```

3. Run the server:
```bash
uv run main.py
```

The server will start on `http://127.0.0.1:5000` by default.

## Usage

The MCP server exposes 5 core tools:

1. **search_attack** - Global search across all ATT&CK entities
2. **get_technique** - Get detailed technique information
3. **list_tactics** - List all MITRE ATT&CK tactics
4. **get_group_techniques** - Get techniques used by threat groups
5. **get_technique_mitigations** - Get mitigations for techniques

## Configuration

### YAML Configuration Files

The server uses YAML configuration files in the `config/` directory:

- `data_sources.yaml` - Define threat intelligence data sources
- `entity_schemas.yaml` - Configure entity type schemas
- `tools.yaml` - Define MCP tool configurations

### Environment Variables

The server supports configuration via environment variables:

```bash
# HTTP Proxy Server Configuration
MCP_HTTP_HOST=localhost    # Default: localhost
MCP_HTTP_PORT=8000        # Default: 8000

# Copy .env.example to .env for local configuration
cp .env.example .env
```

### Web Interface

The web interface is available at `http://localhost:8000` by default. You can customize the host and port using environment variables:

```bash
# Start with custom port
MCP_HTTP_PORT=3000 python start_explorer.py

# Start with custom host and port
MCP_HTTP_HOST=0.0.0.0 MCP_HTTP_PORT=8080 python start_explorer.py
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
uv run flake8 .
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.