# Product Overview

This project is a comprehensive cybersecurity threat intelligence platform that provides multi-layered access to the MITRE ATT&CK framework and other security frameworks. The platform consists of a pure MCP (Model Context Protocol) server for AI assistant integration, a middleware API layer for business logic, a Flask web application for human-friendly interfaces, and a CLI tool for automation - enabling security analysts, threat intelligence researchers, and cybersecurity professionals to analyze threats through multiple access methods optimized for different use cases.

## Key Features

### Basic Analysis Capabilities
- Query security framework tactics, techniques, and mitigations
- Search across entire threat intelligence frameworks
- Explore threat group TTPs (Tactics, Techniques, and Procedures)
- Access relationships between security entities
- Provide structured cybersecurity threat intelligence data

### Advanced Threat Modeling Capabilities
- **Attack Path Construction**: Build multi-stage attack paths through the MITRE ATT&CK kill chain
- **Coverage Gap Analysis**: Analyze defensive coverage gaps against specific threat groups
- **Complex Relationship Discovery**: Explore STIX relationships, attribution chains, and technique hierarchies
- **Threat Group Profiling**: Deep analysis of threat actor techniques and patterns
- **Platform-Specific Analysis**: Filter and analyze techniques by target platforms

### Multi-Layer Platform Architecture
- **Pure MCP Server**: Dedicated AI assistant integration with 8 specialized tools
- **Middleware API Layer**: Business logic and data transformation services
- **Flask Web Application**: Modern web interface with graph visualization capabilities
- **Command-Line Interface**: Automation-friendly CLI for scripting and batch operations
- **Multiple Access Methods**: REST APIs, MCP protocol, web interface, and CLI - each optimized for specific use cases

## Target Users

### Primary Users
- **Security analysts** investigating threats and building defensive strategies
- **Threat intelligence researchers** conducting deep-dive analysis of adversary TTPs
- **Security architects** designing comprehensive defense-in-depth strategies
- **Incident responders** and threat hunters analyzing attack patterns
- **Security operations managers** prioritizing security investments and gap remediation

### Secondary Users
- **Cybersecurity educators** teaching threat modeling and defensive strategies
- **Security tool developers** integrating threat intelligence into security platforms
- **Compliance teams** mapping security controls to threat frameworks
- **Executive stakeholders** understanding threat landscape and risk exposure

## Extensibility Design

This MCP server is designed to be **extensible and reusable**:

### Framework Agnostic Architecture
- **Multi-Framework Support**: While initially built for MITRE ATT&CK, the architecture supports any structured security framework
- **Configuration-Driven**: Data sources, entity types, and tool definitions are externalized to configuration files
- **Pluggable Data Sources**: Support for different threat intelligence formats and sources through configuration
- **Standards-Compliant**: Uses official MCP protocol and STIX parsing libraries

### Modular Tool System
- **8 Comprehensive Tools**: 5 basic analysis tools + 3 advanced threat modeling tools
- **Easy Tool Addition**: New MCP tools can be easily added without modifying core server logic
- **Consistent Interfaces**: All tools follow the same parameter and response patterns
- **Flexible Deployment**: Tools accessible via both MCP protocol and HTTP/JSON API

### Component-Specific Access Patterns
- **MCP Server**: STDIO/HTTP transports for Claude Desktop, ChatGPT, and other AI assistants
- **Middleware APIs**: Internal Python interfaces for business logic and data aggregation
- **Flask Web Server**: REST APIs for web applications, authentication, graph visualization endpoints
- **CLI Tool**: Command-line interface for automation, scripting, and batch operations
- **Configuration Management**: Centralized configuration system supporting all components

## Value Proposition

### For Security Teams
- **Accelerated Threat Analysis**: Quickly understand adversary TTPs and build defensive strategies
- **Data-Driven Decisions**: Make informed security investments based on threat intelligence
- **Comprehensive Coverage**: Analyze both individual techniques and complex attack patterns
- **Accessible Interface**: No programming skills required for advanced threat modeling

### For Organizations
- **Risk Reduction**: Identify and remediate security coverage gaps before they're exploited
- **Cost Optimization**: Prioritize security investments based on actual threat actor behavior
- **Compliance Support**: Map security controls to recognized threat frameworks
- **Knowledge Sharing**: Enable cross-team collaboration on threat intelligence

### For Developers
- **Standards-Based Integration**: Official MCP protocol support for AI assistant integration
- **Flexible APIs**: Multiple access methods for different integration scenarios
- **Extensible Architecture**: Easy to extend with custom analysis tools and data sources
- **Production-Ready**: Comprehensive testing, error handling, and deployment support

## Development Guidelines

> **IMPORTANT**: Before contributing to this project, you must read and follow the workflow defined in `CONTRIBUTING.md`. This project has strict branch protection rules and testing requirements.

### Key Requirements for Contributors
- **Follow branch protection workflow** - feature → staging → main
- **Use UV package manager** - Required for all dependency management  
- **Maintain 202+ test coverage** - All tests must pass across Python 3.12-3.13
- **Use official libraries** - MCP, STIX2, FastMCP for standards compliance
- **Test locally before pushing** - Prevents CI/CD failures

## Technical Differentiators

### Advanced Threat Modeling
- **Kill Chain Analysis**: Construct realistic multi-stage attack paths
- **Attribution Intelligence**: Discover complex relationships between techniques, groups, and campaigns
- **Defensive Gap Analysis**: Quantitative analysis of security coverage against specific threats
- **Platform-Aware Analysis**: Filter analysis by target platforms and environments

### User Experience Excellence
- **Dual Interface Design**: Both programmatic (MCP) and interactive (web) access methods
- **Intelligent Defaults**: Sensible default parameters with advanced customization options
- **Real-Time Results**: Fast in-memory data processing for immediate analysis results
- **Comprehensive Documentation**: Clear setup instructions and usage examples

### Enterprise-Ready Features
- **Configurable Deployment**: Environment variable support for different deployment scenarios
- **Robust Error Handling**: Graceful failure handling with informative error messages
- **Comprehensive Testing**: 167+ automated tests ensuring reliability and correctness
- **Security-First Design**: Official libraries for parsing external data and input validation

The server acts as a comprehensive bridge between the MITRE ATT&CK framework and both AI assistants and human analysts, making advanced threat intelligence analysis accessible, actionable, and scalable across different user types and deployment scenarios.