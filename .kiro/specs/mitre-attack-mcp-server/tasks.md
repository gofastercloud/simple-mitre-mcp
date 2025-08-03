# Implementation Plan

- [x] 1. Set up project structure and dependencies with UV
  - Create Python project directory structure with main server file
  - Initialize UV project with `uv init` and configure pyproject.toml
  - Add Flask, requests, and other needed dependencies using `uv add`
  - Set up basic Flask application skeleton
  - _Requirements: 7.4_

- [x] 2. Implement MITRE ATT&CK data loading functionality
  - Create function to download STIX JSON data from MITRE repository
  - Implement JSON parsing to extract tactics, techniques, groups, and mitigations
  - Create data structures to store parsed ATT&CK entities in memory
  - _Requirements: 1.1, 2.1, 3.1, 6.1_

- [x] 3. Implement MCP server foundation
  - Set up Flask routes to handle MCP protocol requests
  - Create MCP tool registration and discovery functionality
  - Implement basic MCP request/response handling
  - _Requirements: 7.1, 7.4_

- [x] 4. Implement search_attack tool
  - Create function to search across all ATT&CK entities (tactics, techniques, groups, mitigations)
  - Implement basic string matching for search queries
  - Return results with entity type indicators
  - Write unit tests for search functionality
  - _Requirements: 5.1, 5.2_

- [x] 5. Implement get_technique tool
  - Create function to retrieve detailed technique information by ID
  - Include associated tactics, platforms, and mitigations in response
  - Handle invalid technique IDs gracefully
  - Write unit tests for technique retrieval
  - _Requirements: 2.1, 2.2_

- [x] 6. Implement list_tactics tool
  - Create function to return all MITRE ATT&CK tactics
  - Include tactic IDs, names, and descriptions
  - Write unit tests for tactics listing
  - _Requirements: 1.1, 1.2_

- [x] 7. Implement get_group_techniques tool
  - Create function to retrieve all techniques used by a specific threat group
  - Handle group ID validation and lookup
  - Return technique information with basic details
  - Write unit tests for group technique retrieval
  - _Requirements: 6.1, 6.2_

- [x] 8. Implement get_technique_mitigations tool
  - Create function to find mitigations for a specific technique
  - Handle technique ID validation and mitigation lookup
  - Return mitigation details including IDs and descriptions
  - Write unit tests for mitigation retrieval
  - _Requirements: 3.4, 4.2_

- [x] 9. Integrate all tools into MCP server
  - Register all 5 MCP tools with the server
  - Ensure proper tool metadata and parameter definitions
  - Test end-to-end MCP tool execution
  - _Requirements: 7.1, 7.4_

- [x] 10. Create startup script and basic documentation
  - Create main entry point script to start the MCP server using UV
  - Add basic README with UV-based setup and usage instructions
  - Include example MCP tool calls for testing
  - Document how to run with `uv run` command
  - _Requirements: 7.4_

- [x] 11. Implement build_attack_path tool
  - Create function to construct multi-stage attack paths across MITRE tactics
  - Implement kill chain sequencing logic from initial access to impact
  - Support filtering by threat group and platform constraints
  - Include technique dependency analysis and attack progression mapping
  - Write unit tests for attack path construction and validation
  - _Requirements: 2.1, 6.1, 1.1_

- [x] 12. Implement analyze_coverage_gaps tool
  - Create function to analyze defensive coverage gaps against threat groups
  - Implement mitigation coverage calculation across technique sets
  - Support exclusion of already-implemented mitigations from analysis
  - Include coverage percentage reporting and prioritization recommendations
  - Write unit tests for gap analysis and coverage calculations
  - _Requirements: 3.4, 4.2, 6.1_

- [x] 13. Implement detect_technique_relationships tool
  - Create function to discover complex STIX relationships beyond uses/mitigates
  - Implement detection relationship mapping (what detects what techniques)
  - Support subtechnique hierarchy traversal and parent-child relationships
  - Include attribution chain analysis (technique→group→campaign connections)
  - Write unit tests for relationship discovery and traversal logic
  - _Requirements: 2.1, 6.1, 5.1_

- [x] 14. Update HTTP proxy and web explorer for advanced tools
  - Extend `http_proxy.py` HTTP server that currently proxies MCP JSON-RPC calls to HTTP endpoints
    - Add tool definitions for build_attack_path, analyze_coverage_gaps, detect_technique_relationships
    - Update the hardcoded tools list in `handle_tools_list()` method (lines ~90-140)
    - Extend `handle_tool_call()` method to support new tool parameter validation
  - Update `web_explorer.html` interactive web interface that currently supports 5 basic tools
    - Add new tool section "🚀 Advanced Threat Modeling" with buttons for the 3 new tools
    - Create complex input forms for multi-parameter tools (threat group arrays, relationship types)
    - Update JavaScript `showInputForm()` and `executeWithInput()` functions to handle array parameters
    - Add result visualization for attack paths, coverage gaps, and relationship graphs
  - Update `start_explorer.py` launcher script to ensure new tools are available when web interface loads
  - Write integration tests for web interface with new advanced tools
  - _Requirements: 7.1, 7.4_