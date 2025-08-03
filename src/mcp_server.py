"""
MCP Server Implementation

This module implements the core MCP protocol handling using the official MCP library
for the MITRE ATT&CK MCP server.
"""

import logging
from typing import Any, Dict, List
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from src.config_loader import ConfigLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _search_entities(query: str, data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Search across all entity types for matching entries.
    
    Args:
        query: Lowercase search query
        data: Dictionary containing all entity types and their data
        
    Returns:
        List of matching entities with entity type indicators
    """
    results = []
    
    # Define entity types to search
    entity_types = ['tactics', 'techniques', 'groups', 'mitigations']
    
    for entity_type in entity_types:
        entities = data.get(entity_type, [])
        
        for entity in entities:
            matches = []
            
            # Search in entity ID
            entity_id = entity.get('id', '').lower()
            if query in entity_id:
                matches.append(f"ID contains '{query}'")
            
            # Search in entity name
            entity_name = entity.get('name', '').lower()
            if query in entity_name:
                matches.append(f"name contains '{query}'")
            
            # Search in description
            entity_desc = entity.get('description', '').lower()
            if query in entity_desc:
                matches.append(f"description contains '{query}'")
            
            # Search in aliases (for groups)
            if entity_type == 'groups' and 'aliases' in entity:
                for alias in entity.get('aliases', []):
                    if query in alias.lower():
                        matches.append(f"alias '{alias}' contains '{query}'")
                        break
            
            # If we found matches, add to results
            if matches:
                result_entity = {
                    'entity_type': entity_type[:-1],  # Remove 's' to get singular form
                    'id': entity.get('id', ''),
                    'name': entity.get('name', ''),
                    'description': entity.get('description', ''),
                    'match_reason': ', '.join(matches)
                }
                
                # Add entity-specific fields
                if entity_type == 'groups' and 'aliases' in entity:
                    result_entity['aliases'] = entity['aliases']
                elif entity_type == 'techniques':
                    result_entity['tactics'] = entity.get('tactics', [])
                    result_entity['platforms'] = entity.get('platforms', [])
                
                results.append(result_entity)
    
    # Sort results by entity type and then by ID
    results.sort(key=lambda x: (x['entity_type'], x['id']))
    
    return results


def create_mcp_server(data_loader=None):
    """
    Create and configure the MCP server with all tools registered.
    
    Args:
        data_loader: DataLoader instance with loaded threat intelligence data
    
    Returns:
        FastMCP: Configured MCP server application instance
    """
    # Initialize FastMCP server
    app = FastMCP(
        name="mitre-attack-mcp-server",
        instructions="A Model Context Protocol server providing access to MITRE ATT&CK framework data",
        debug=True,
        log_level="INFO"
    )
    
    # Store data loader for use in tool handlers
    app.data_loader = data_loader
    
    # Load tools configuration
    config_loader = ConfigLoader()
    tools_config = config_loader.load_tools_config()
    
    logger.info("Registering MCP tools...")
    
    # Register search_attack tool
    @app.tool()
    async def search_attack(query: str) -> List[TextContent]:
        """
        Search across all ATT&CK entities (tactics, techniques, groups, mitigations).
        
        Args:
            query: Search term to find matching entities
            
        Returns:
            List[TextContent]: Search results with entity type indicators
        """
        try:
            logger.info(f"Executing search_attack with query: {query}")
            
            if not app.data_loader:
                return [TextContent(
                    type="text",
                    text="Error: Data loader not available. Please ensure MITRE ATT&CK data is loaded."
                )]
            
            # Get cached data
            data = app.data_loader.get_cached_data('mitre_attack')
            if not data:
                return [TextContent(
                    type="text",
                    text="Error: MITRE ATT&CK data not loaded. Please load data first."
                )]
            
            # Perform search across all entity types
            search_results = _search_entities(query.lower(), data)
            
            if not search_results:
                return [TextContent(
                    type="text",
                    text=f"No results found for query: '{query}'"
                )]
            
            # Format results
            result_text = f"Search results for '{query}' ({len(search_results)} matches):\n\n"
            
            for result in search_results:
                entity_type = result['entity_type'].upper()
                entity_id = result['id']
                entity_name = result['name']
                match_reason = result['match_reason']
                
                result_text += f"[{entity_type}] {entity_id}: {entity_name}\n"
                result_text += f"  Match: {match_reason}\n"
                
                # Add description preview if available
                if 'description' in result and result['description']:
                    desc_preview = result['description'][:100] + "..." if len(result['description']) > 100 else result['description']
                    result_text += f"  Description: {desc_preview}\n"
                
                result_text += "\n"
            
            return [TextContent(
                type="text",
                text=result_text
            )]
            
        except Exception as e:
            logger.error(f"Error in search_attack: {e}")
            return [TextContent(
                type="text",
                text=f"Error executing search: {str(e)}"
            )]
    
    # Register get_technique tool
    @app.tool()
    async def get_technique(technique_id: str) -> List[TextContent]:
        """
        Get detailed information about a specific technique.
        
        Args:
            technique_id: MITRE technique ID (e.g., T1055)
            
        Returns:
            List[TextContent]: Technique details including tactics, platforms, and mitigations
        """
        try:
            logger.info(f"Executing get_technique with ID: {technique_id}")
            
            if not app.data_loader:
                return [TextContent(
                    type="text",
                    text="Error: Data loader not available. Please ensure MITRE ATT&CK data is loaded."
                )]
            
            # Get cached data
            data = app.data_loader.get_cached_data('mitre_attack')
            if not data:
                return [TextContent(
                    type="text",
                    text="Error: MITRE ATT&CK data not loaded. Please load data first."
                )]
            
            # Normalize technique ID (ensure uppercase)
            technique_id = technique_id.upper().strip()
            
            # Find the technique
            technique = None
            for tech in data.get('techniques', []):
                if tech.get('id', '').upper() == technique_id:
                    technique = tech
                    break
            
            if not technique:
                return [TextContent(
                    type="text",
                    text=f"Technique '{technique_id}' not found. Please verify the technique ID is correct."
                )]
            
            # Build detailed response
            result_text = f"TECHNIQUE DETAILS\n"
            result_text += f"================\n\n"
            result_text += f"ID: {technique.get('id', 'N/A')}\n"
            result_text += f"Name: {technique.get('name', 'N/A')}\n\n"
            
            # Description
            description = technique.get('description', 'No description available')
            result_text += f"Description:\n{description}\n\n"
            
            # Associated tactics
            tactics = technique.get('tactics', [])
            if tactics:
                result_text += f"Associated Tactics ({len(tactics)}):\n"
                # Look up tactic names
                tactic_details = []
                for tactic_id in tactics:
                    for tactic in data.get('tactics', []):
                        if tactic.get('id') == tactic_id:
                            tactic_details.append(f"  - {tactic_id}: {tactic.get('name', 'Unknown')}")
                            break
                    else:
                        tactic_details.append(f"  - {tactic_id}: (Name not found)")
                result_text += "\n".join(tactic_details) + "\n\n"
            else:
                result_text += "Associated Tactics: None\n\n"
            
            # Platforms
            platforms = technique.get('platforms', [])
            if platforms:
                result_text += f"Platforms ({len(platforms)}):\n"
                result_text += "  " + ", ".join(platforms) + "\n\n"
            else:
                result_text += "Platforms: Not specified\n\n"
            
            # Mitigations
            mitigations = technique.get('mitigations', [])
            if mitigations:
                result_text += f"Mitigations ({len(mitigations)}):\n"
                # Look up mitigation names
                mitigation_details = []
                for mitigation_id in mitigations:
                    for mitigation in data.get('mitigations', []):
                        if mitigation.get('id') == mitigation_id:
                            mitigation_details.append(f"  - {mitigation_id}: {mitigation.get('name', 'Unknown')}")
                            break
                    else:
                        mitigation_details.append(f"  - {mitigation_id}: (Name not found)")
                result_text += "\n".join(mitigation_details) + "\n\n"
            else:
                result_text += "Mitigations: None available\n\n"
            
            # Additional metadata
            if technique.get('data_sources'):
                result_text += f"Data Sources: {', '.join(technique['data_sources'])}\n"
            
            if technique.get('detection'):
                result_text += f"\nDetection:\n{technique['detection']}\n"
            
            return [TextContent(
                type="text",
                text=result_text
            )]
            
        except Exception as e:
            logger.error(f"Error in get_technique: {e}")
            return [TextContent(
                type="text",
                text=f"Error retrieving technique: {str(e)}"
            )]
    
    # Register list_tactics tool
    @app.tool()
    async def list_tactics() -> List[TextContent]:
        """
        Get all MITRE ATT&CK tactics.
        
        Returns:
            List[TextContent]: List of all tactics with IDs, names, and descriptions
        """
        try:
            logger.info("Executing list_tactics")
            
            if not app.data_loader:
                return [TextContent(
                    type="text",
                    text="Error: Data loader not available. Please ensure MITRE ATT&CK data is loaded."
                )]
            
            # Get cached data
            data = app.data_loader.get_cached_data('mitre_attack')
            if not data:
                return [TextContent(
                    type="text",
                    text="Error: MITRE ATT&CK data not loaded. Please load data first."
                )]
            
            # Get all tactics
            tactics = data.get('tactics', [])
            
            if not tactics:
                return [TextContent(
                    type="text",
                    text="No tactics found in the loaded data."
                )]
            
            # Sort tactics by ID for consistent ordering
            sorted_tactics = sorted(tactics, key=lambda x: x.get('id', ''))
            
            # Build formatted response
            result_text = f"MITRE ATT&CK TACTICS\n"
            result_text += f"===================\n\n"
            result_text += f"Total tactics: {len(sorted_tactics)}\n\n"
            
            for tactic in sorted_tactics:
                tactic_id = tactic.get('id', 'N/A')
                tactic_name = tactic.get('name', 'N/A')
                tactic_description = tactic.get('description', 'No description available')
                
                result_text += f"ID: {tactic_id}\n"
                result_text += f"Name: {tactic_name}\n"
                result_text += f"Description: {tactic_description}\n"
                result_text += f"{'-' * 50}\n\n"
            
            return [TextContent(
                type="text",
                text=result_text
            )]
            
        except Exception as e:
            logger.error(f"Error in list_tactics: {e}")
            return [TextContent(
                type="text",
                text=f"Error listing tactics: {str(e)}"
            )]
    
    # Register get_group_techniques tool
    @app.tool()
    async def get_group_techniques(group_id: str) -> List[TextContent]:
        """
        Get all techniques used by a specific threat group.
        
        Args:
            group_id: MITRE group ID (e.g., G0016)
            
        Returns:
            List[TextContent]: List of techniques with basic details used by the group
        """
        try:
            logger.info(f"Executing get_group_techniques with ID: {group_id}")
            
            if not app.data_loader:
                return [TextContent(
                    type="text",
                    text="Error: Data loader not available. Please ensure MITRE ATT&CK data is loaded."
                )]
            
            # Get cached data
            data = app.data_loader.get_cached_data('mitre_attack')
            if not data:
                return [TextContent(
                    type="text",
                    text="Error: MITRE ATT&CK data not loaded. Please load data first."
                )]
            
            # Normalize group ID (ensure uppercase)
            group_id = group_id.upper().strip()
            
            # Find the group
            group = None
            for grp in data.get('groups', []):
                if grp.get('id', '').upper() == group_id:
                    group = grp
                    break
            
            if not group:
                return [TextContent(
                    type="text",
                    text=f"Group '{group_id}' not found. Please verify the group ID is correct."
                )]
            
            # Get techniques used by this group
            group_techniques = group.get('techniques', [])
            
            if not group_techniques:
                return [TextContent(
                    type="text",
                    text=f"No techniques found for group '{group_id}' ({group.get('name', 'Unknown')})."
                )]
            
            # Build detailed response
            result_text = f"GROUP TECHNIQUES\n"
            result_text += f"================\n\n"
            result_text += f"Group ID: {group.get('id', 'N/A')}\n"
            result_text += f"Group Name: {group.get('name', 'N/A')}\n"
            
            # Add aliases if available
            aliases = group.get('aliases', [])
            if aliases:
                result_text += f"Aliases: {', '.join(aliases)}\n"
            
            result_text += f"\nDescription:\n{group.get('description', 'No description available')}\n\n"
            
            result_text += f"Techniques Used ({len(group_techniques)}):\n"
            result_text += f"{'-' * 40}\n\n"
            
            # Look up technique details
            technique_details = []
            for technique_id in group_techniques:
                # Find technique details
                technique_info = None
                for tech in data.get('techniques', []):
                    if tech.get('id') == technique_id:
                        technique_info = tech
                        break
                
                if technique_info:
                    technique_details.append({
                        'id': technique_id,
                        'name': technique_info.get('name', 'Unknown'),
                        'description': technique_info.get('description', 'No description available'),
                        'tactics': technique_info.get('tactics', []),
                        'platforms': technique_info.get('platforms', [])
                    })
                else:
                    technique_details.append({
                        'id': technique_id,
                        'name': '(Name not found)',
                        'description': 'Technique details not available',
                        'tactics': [],
                        'platforms': []
                    })
            
            # Sort techniques by ID for consistent ordering
            technique_details.sort(key=lambda x: x['id'])
            
            # Format technique details
            for i, tech in enumerate(technique_details, 1):
                result_text += f"{i}. {tech['id']}: {tech['name']}\n"
                
                # Add description preview
                desc = tech['description']
                if len(desc) > 150:
                    desc = desc[:150] + "..."
                result_text += f"   Description: {desc}\n"
                
                # Add tactics if available
                if tech['tactics']:
                    tactic_names = []
                    for tactic_id in tech['tactics']:
                        # Look up tactic name
                        for tactic in data.get('tactics', []):
                            if tactic.get('id') == tactic_id:
                                tactic_names.append(f"{tactic_id} ({tactic.get('name', 'Unknown')})")
                                break
                        else:
                            tactic_names.append(f"{tactic_id} (Name not found)")
                    result_text += f"   Tactics: {', '.join(tactic_names)}\n"
                
                # Add platforms if available
                if tech['platforms']:
                    result_text += f"   Platforms: {', '.join(tech['platforms'])}\n"
                
                result_text += "\n"
            
            return [TextContent(
                type="text",
                text=result_text
            )]
            
        except Exception as e:
            logger.error(f"Error in get_group_techniques: {e}")
            return [TextContent(
                type="text",
                text=f"Error retrieving group techniques: {str(e)}"
            )]
    
    # Register get_technique_mitigations tool
    @app.tool()
    async def get_technique_mitigations(technique_id: str) -> List[TextContent]:
        """
        Get mitigations for a specific technique.
        
        Args:
            technique_id: MITRE technique ID (e.g., T1055)
            
        Returns:
            List[TextContent]: List of applicable mitigations for the technique
        """
        try:
            logger.info(f"Executing get_technique_mitigations with ID: {technique_id}")
            
            if not app.data_loader:
                return [TextContent(
                    type="text",
                    text="Error: Data loader not available. Please ensure MITRE ATT&CK data is loaded."
                )]
            
            # Get cached data
            data = app.data_loader.get_cached_data('mitre_attack')
            if not data:
                return [TextContent(
                    type="text",
                    text="Error: MITRE ATT&CK data not loaded. Please load data first."
                )]
            
            # Normalize technique ID (ensure uppercase)
            technique_id = technique_id.upper().strip()
            
            # Find the technique
            technique = None
            for tech in data.get('techniques', []):
                if tech.get('id', '').upper() == technique_id:
                    technique = tech
                    break
            
            if not technique:
                return [TextContent(
                    type="text",
                    text=f"Technique '{technique_id}' not found. Please verify the technique ID is correct."
                )]
            
            # Get mitigations for this technique
            technique_mitigations = technique.get('mitigations', [])
            
            if not technique_mitigations:
                return [TextContent(
                    type="text",
                    text=f"No mitigations found for technique '{technique_id}' ({technique.get('name', 'Unknown')})."
                )]
            
            # Build detailed response
            result_text = f"TECHNIQUE MITIGATIONS\n"
            result_text += f"====================\n\n"
            result_text += f"Technique ID: {technique.get('id', 'N/A')}\n"
            result_text += f"Technique Name: {technique.get('name', 'N/A')}\n\n"
            
            # Add technique description preview
            description = technique.get('description', 'No description available')
            if len(description) > 200:
                description = description[:200] + "..."
            result_text += f"Description: {description}\n\n"
            
            result_text += f"Mitigations ({len(technique_mitigations)}):\n"
            result_text += f"{'-' * 40}\n\n"
            
            # Look up mitigation details
            mitigation_details = []
            for mitigation_id in technique_mitigations:
                # Find mitigation details
                mitigation_info = None
                for mitigation in data.get('mitigations', []):
                    if mitigation.get('id') == mitigation_id:
                        mitigation_info = mitigation
                        break
                
                if mitigation_info:
                    mitigation_details.append({
                        'id': mitigation_id,
                        'name': mitigation_info.get('name', 'Unknown'),
                        'description': mitigation_info.get('description', 'No description available')
                    })
                else:
                    mitigation_details.append({
                        'id': mitigation_id,
                        'name': '(Name not found)',
                        'description': 'Mitigation details not available'
                    })
            
            # Sort mitigations by ID for consistent ordering
            mitigation_details.sort(key=lambda x: x['id'])
            
            # Format mitigation details
            for i, mitigation in enumerate(mitigation_details, 1):
                result_text += f"{i}. {mitigation['id']}: {mitigation['name']}\n"
                
                # Add description
                desc = mitigation['description']
                if len(desc) > 300:
                    desc = desc[:300] + "..."
                result_text += f"   Description: {desc}\n\n"
            
            return [TextContent(
                type="text",
                text=result_text
            )]
            
        except Exception as e:
            logger.error(f"Error in get_technique_mitigations: {e}")
            return [TextContent(
                type="text",
                text=f"Error retrieving technique mitigations: {str(e)}"
            )]
    
    logger.info("Registered 5 MCP tools successfully")
    return app


class MCPServer:
    """
    MCP Server wrapper class for easier management.
    """
    
    def __init__(self, data_loader=None):
        """
        Initialize the MCP server.
        
        Args:
            data_loader: DataLoader instance with loaded threat intelligence data
        """
        self.data_loader = data_loader
        self.app = create_mcp_server(data_loader)
    
    def get_app(self):
        """
        Get the FastMCP application instance.
        
        Returns:
            FastMCP: The configured MCP server application
        """
        return self.app
    
    def run(self, transport: str = "streamable-http"):
        """
        Run the MCP server.
        
        Args:
            transport: Transport protocol to use ("stdio", "sse", or "streamable-http")
        """
        logger.info(f"Starting MCP server with {transport} transport")
        self.app.run(transport=transport)


def create_app(data_loader=None):
    """
    Create and configure the MCP server application.
    
    Args:
        data_loader: DataLoader instance with loaded threat intelligence data
    
    Returns:
        FastMCP: Configured MCP server application instance
    """
    return create_mcp_server(data_loader)