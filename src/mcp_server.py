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


def _get_entity_name(entity_id: str, data: Dict[str, List[Dict[str, Any]]]) -> str:
    """Get the name of an entity by its ID."""
    for entity_type in ['techniques', 'groups', 'mitigations', 'tactics']:
        for entity in data.get(entity_type, []):
            if entity.get('id') == entity_id:
                return entity.get('name', 'Unknown')
    return 'Unknown'


def _get_entity_type(entity_id: str) -> str:
    """Determine entity type from ID prefix."""
    if entity_id.startswith('T'):
        return 'Technique'
    elif entity_id.startswith('G'):
        return 'Group'
    elif entity_id.startswith('M'):
        return 'Mitigation'
    elif entity_id.startswith('TA'):
        return 'Tactic'
    elif entity_id.startswith('S'):
        return 'Software'
    elif entity_id.startswith('C'):
        return 'Campaign'
    else:
        return 'Unknown'


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
            
            # Get entity fields
            entity_id = entity.get('id', '').lower()
            entity_name = entity.get('name', '').lower()

            # Search in entity ID
            if query in entity_id:
                matches.append(f"ID contains '{query}'")

            # Search in entity name
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
            logger.info("Executing search_attack with query: {query}")

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
                entity_type = result['entity_type'].title()
                entity_id = result['id']
                entity_name = result['name']
                match_reason = result['match_reason']

                result_text += f"[{entity_type}] {entity_id}: {entity_name}\n"
                result_text += f"  Match: {match_reason}\n"

                # Add description preview if available
                if 'description' in result and result['description']:
                    desc = result['description']
                    desc_preview = desc[:100] + "..." if len(desc) > 100 else desc
                    result_text += f"  Description: {desc_preview}\n"

                result_text += "\n"

            return [TextContent(
                type="text",
                text=result_text
            )]

        except Exception:
            logger.error("Error in search_attack: {e}")
            return [TextContent(
                type="text",
                text="Error executing search: {str(e)}"
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
            logger.info("Executing get_technique with ID: {technique_id}")

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
                    text="Technique '{technique_id}' not found. Please verify the technique ID is correct."
                )]

            # Build detailed response
            result_text = "TECHNIQUE DETAILS\n"
            result_text += "================\n\n"
            result_text += "ID: {technique.get('id', 'N/A')}\n"
            result_text += "Name: {technique.get('name', 'N/A')}\n\n"

            # Description
            description = technique.get('description', 'No description available')
            result_text += "Description:\n{description}\n\n"

            # Associated tactics
            tactics = technique.get('tactics', [])
            if tactics:
                result_text += "Associated Tactics ({len(tactics)}):\n"
                # Look up tactic names
                tactic_details = []
                for tactic_id in tactics:
                    for tactic in data.get('tactics', []):
                        if tactic.get('id') == tactic_id:
                            tactic_details.append("  - {tactic_id}: {tactic.get('name', 'Unknown')}")
                            break
                    else:
                        tactic_details.append("  - {tactic_id}: (Name not found)")
                result_text += "\n".join(tactic_details) + "\n\n"
            else:
                result_text += "Associated Tactics: None\n\n"

            # Platforms
            platforms = technique.get('platforms', [])
            if platforms:
                result_text += "Platforms ({len(platforms)}):\n"
                result_text += "  " + ", ".join(platforms) + "\n\n"
            else:
                result_text += "Platforms: Not specified\n\n"

            # Mitigations
            mitigations = technique.get('mitigations', [])
            if mitigations:
                result_text += "Mitigations ({len(mitigations)}):\n"
                # Look up mitigation names
                mitigation_details = []
                for mitigation_id in mitigations:
                    for mitigation in data.get('mitigations', []):
                        if mitigation.get('id') == mitigation_id:
                            mitigation_details.append("  - {mitigation_id}: {mitigation.get('name', 'Unknown')}")
                            break
                    else:
                        mitigation_details.append("  - {mitigation_id}: (Name not found)")
                result_text += "\n".join(mitigation_details) + "\n\n"
            else:
                result_text += "Mitigations: None available\n\n"

            # Additional metadata
            if technique.get('data_sources'):
                result_text += "Data Sources: {', '.join(technique['data_sources'])}\n"

            if technique.get('detection'):
                result_text += "\nDetection:\n{technique['detection']}\n"

            return [TextContent(
                type="text",
                text=result_text
            )]

        except Exception:
            logger.error("Error in get_technique: {e}")
            return [TextContent(
                type="text",
                text="Error retrieving technique: {str(e)}"
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
            result_text = "MITRE ATT&CK TACTICS\n"
            result_text += "===================\n\n"
            result_text += "Total tactics: {len(sorted_tactics)}\n\n"

            for tactic in sorted_tactics:
                tactic_id = tactic.get('id', 'N/A')
                tactic_name = tactic.get('name', 'N/A')
                tactic_description = tactic.get('description', 'No description available')

                result_text += "ID: {tactic_id}\n"
                result_text += "Name: {tactic_name}\n"
                result_text += "Description: {tactic_description}\n"
                result_text += "{'-' * 50}\n\n"

            return [TextContent(
                type="text",
                text=result_text
            )]

        except Exception:
            logger.error("Error in list_tactics: {e}")
            return [TextContent(
                type="text",
                text="Error listing tactics: {str(e)}"
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
            logger.info("Executing get_group_techniques with ID: {group_id}")

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
                    text="Group '{group_id}' not found. Please verify the group ID is correct."
                )]

            # Get techniques used by this group
            group_techniques = group.get('techniques', [])

            if not group_techniques:
                return [TextContent(
                    type="text",
                    text="No techniques found for group '{group_id}' ({group.get('name', 'Unknown')})."
                )]

            # Build detailed response
            result_text = "GROUP TECHNIQUES\n"
            result_text += "================\n\n"
            result_text += "Group ID: {group.get('id', 'N/A')}\n"
            result_text += "Group Name: {group.get('name', 'N/A')}\n"

            # Add aliases if available
            aliases = group.get('aliases', [])
            if aliases:
                result_text += "Aliases: {', '.join(aliases)}\n"

            result_text += "\nDescription:\n{group.get('description', 'No description available')}\n\n"

            result_text += "Techniques Used ({len(group_techniques)}):\n"
            result_text += "{'-' * 40}\n\n"

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
                result_text += "{i}. {tech['id']}: {tech['name']}\n"

                # Add description preview
                desc = tech['description']
                if len(desc) > 150:
                    desc = desc[:150] + "..."
                result_text += "   Description: {desc}\n"

                # Add tactics if available
                if tech['tactics']:
                    tactic_names = []
                    for tactic_id in tech['tactics']:
                        # Look up tactic name
                        for tactic in data.get('tactics', []):
                            if tactic.get('id') == tactic_id:
                                tactic_names.append("{tactic_id} ({tactic.get('name', 'Unknown')})")
                                break
                        else:
                            tactic_names.append("{tactic_id} (Name not found)")
                    result_text += "   Tactics: {', '.join(tactic_names)}\n"

                # Add platforms if available
                if tech['platforms']:
                    result_text += "   Platforms: {', '.join(tech['platforms'])}\n"

                result_text += "\n"

            return [TextContent(
                type="text",
                text=result_text
            )]

        except Exception:
            logger.error("Error in get_group_techniques: {e}")
            return [TextContent(
                type="text",
                text="Error retrieving group techniques: {str(e)}"
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
            logger.info("Executing get_technique_mitigations with ID: {technique_id}")

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
                    text="Technique '{technique_id}' not found. Please verify the technique ID is correct."
                )]

            # Get mitigations for this technique
            technique_mitigations = technique.get('mitigations', [])

            if not technique_mitigations:
                return [TextContent(
                    type="text",
                    text="No mitigations found for technique '{technique_id}' ({technique.get('name', 'Unknown')})."
                )]

            # Build detailed response
            result_text = "TECHNIQUE MITIGATIONS\n"
            result_text += "====================\n\n"
            result_text += "Technique ID: {technique.get('id', 'N/A')}\n"
            result_text += "Technique Name: {technique.get('name', 'N/A')}\n\n"

            # Add technique description preview
            description = technique.get('description', 'No description available')
            if len(description) > 200:
                description = description[:200] + "..."
            result_text += "Description: {description}\n\n"

            result_text += "Mitigations ({len(technique_mitigations)}):\n"
            result_text += "{'-' * 40}\n\n"

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
                result_text += "{i}. {mitigation['id']}: {mitigation['name']}\n"

                # Add description
                desc = mitigation['description']
                if len(desc) > 300:
                    desc = desc[:300] + "..."
                result_text += "   Description: {desc}\n\n"

            return [TextContent(
                type="text",
                text=result_text
            )]

        except Exception:
            logger.error("Error in get_technique_mitigations: {e}")
            return [TextContent(
                type="text",
                text="Error retrieving technique mitigations: {str(e)}"
            )]

    # Register build_attack_path tool
    @app.tool()
    async def build_attack_path(start_tactic: str = "TA0001", end_tactic: str = "TA0040", group_id: str = "", platform: str = "") -> List[TextContent]:
        """
        Build complete attack paths from initial access to objectives, showing technique sequences across tactics.

        Args:
            start_tactic: Starting tactic ID (default: TA0001 - Initial Access)
            end_tactic: Target tactic ID (default: TA0040 - Impact)
            group_id: Filter paths to techniques used by specific group (e.g., G0016)
            platform: Filter to specific platform (Windows, Linux, macOS)

        Returns:
            List[TextContent]: Attack path with technique sequences across tactics
        """
        try:
            logger.info("Executing build_attack_path from {start_tactic} to {end_tactic}")

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

            # Normalize inputs
            start_tactic = start_tactic.upper().strip()
            end_tactic = end_tactic.upper().strip()
            group_id = group_id.upper().strip() if group_id else ""
            platform = platform.strip() if platform else ""

            # Validate tactic IDs
            valid_tactics = {tactic.get('id') for tactic in data.get('tactics', [])}
            if start_tactic not in valid_tactics:
                return [TextContent(
                    type="text",
                    text="Error: Start tactic '{start_tactic}' not found. Valid tactics: {', '.join(sorted(valid_tactics))}"
                )]

            if end_tactic not in valid_tactics:
                return [TextContent(
                    type="text",
                    text="Error: End tactic '{end_tactic}' not found. Valid tactics: {', '.join(sorted(valid_tactics))}"
                )]

            # Validate group ID if provided
            if group_id:
                group_exists = any(group.get('id') == group_id for group in data.get('groups', []))
                if not group_exists:
                    return [TextContent(
                        type="text",
                        text="Error: Group '{group_id}' not found. Please verify the group ID is correct."
                    )]

            # Define the standard MITRE ATT&CK kill chain order
            kill_chain_order = [
                'TA0043',  # Reconnaissance
                'TA0042',  # Resource Development
                'TA0001',  # Initial Access
                'TA0002',  # Execution
                'TA0003',  # Persistence
                'TA0004',  # Privilege Escalation
                'TA0005',  # Defense Evasion
                'TA0006',  # Credential Access
                'TA0007',  # Discovery
                'TA0008',  # Lateral Movement
                'TA0009',  # Collection
                'TA0011',  # Command and Control
                'TA0010',  # Exfiltration
                'TA0040'   # Impact
            ]

            # Find start and end positions in kill chain
            try:
                start_index = kill_chain_order.index(start_tactic)
                end_index = kill_chain_order.index(end_tactic)
            except ValueError:
                return [TextContent(
                    type="text",
                    text="Error: Tactic not found in kill chain order: {e}"
                )]

            if start_index >= end_index:
                return [TextContent(
                    type="text",
                    text="Error: Start tactic must come before end tactic in the kill chain. Start: {start_tactic}, End: {end_tactic}"
                )]

            # Get tactics in the path
            path_tactics = kill_chain_order[start_index:end_index + 1]

            # Build technique mapping by tactic
            techniques_by_tactic = {}
            for technique in data.get('techniques', []):
                technique_id = technique.get('id', '')
                technique_tactics = technique.get('tactics', [])
                technique_platforms = technique.get('platforms', [])

                # Apply group filter if specified
                if group_id:
                    group_techniques = set()
                    for group in data.get('groups', []):
                        if group.get('id') == group_id:
                            group_techniques = set(group.get('techniques', []))
                            break

                    if technique_id not in group_techniques:
                        continue

                # Apply platform filter if specified
                if platform and technique_platforms:
                    if platform not in technique_platforms:
                        continue

                # Add technique to relevant tactics
                for tactic_id in technique_tactics:
                    if tactic_id in path_tactics:
                        if tactic_id not in techniques_by_tactic:
                            techniques_by_tactic[tactic_id] = []
                        techniques_by_tactic[tactic_id].append(technique)

            # Build attack path
            result_text = "ATTACK PATH CONSTRUCTION\\n"
            result_text += "========================\\n\\n"
            result_text += "Path Configuration:\\n"
            result_text += "  Start Tactic: {start_tactic}\\n"
            result_text += "  End Tactic: {end_tactic}\\n"

            if group_id:
                group_name = "Unknown"
                for group in data.get('groups', []):
                    if group.get('id') == group_id:
                        group_name = group.get('name', 'Unknown')
                        break
                result_text += "  Group Filter: {group_id} ({group_name})\\n"

            if platform:
                result_text += "  Platform Filter: {platform}\\n"

            result_text += "\\n"

            # Generate path for each tactic
            total_techniques = 0
            path_complete = True

            for i, tactic_id in enumerate(path_tactics):
                # Find tactic name
                tactic_name = "Unknown"
                tactic_description = ""
                for tactic in data.get('tactics', []):
                    if tactic.get('id') == tactic_id:
                        tactic_name = tactic.get('name', 'Unknown')
                        tactic_description = tactic.get('description', '')
                        break

                result_text += "STEP {i + 1}: {tactic_id} - {tactic_name}\\n"
                result_text += "{'=' * (len(f'STEP {i + 1}: {tactic_id} - {tactic_name}'))}\\n"

                if tactic_description:
                    # Truncate long descriptions
                    if len(tactic_description) > 100:
                        tactic_description = tactic_description[:100] + "..."
                    result_text += "Description: {tactic_description}\\n"

                # List available techniques for this tactic
                tactic_techniques = techniques_by_tactic.get(tactic_id, [])

                if tactic_techniques:
                    result_text += "Available Techniques ({len(tactic_techniques)}): \\n"

                    # Sort techniques by ID for consistent output
                    tactic_techniques.sort(key=lambda x: x.get('id', ''))

                    # Show up to 10 techniques per tactic to keep output manageable
                    for j, technique in enumerate(tactic_techniques[:10]):
                        technique_id = technique.get('id', 'Unknown')
                        technique_name = technique.get('name', 'Unknown')
                        platforms = technique.get('platforms', [])

                        result_text += "  • {technique_id}: {technique_name}"
                        if platforms:
                            result_text += " (Platforms: {', '.join(platforms[:3])})"
                        result_text += "\\n"

                    if len(tactic_techniques) > 10:
                        result_text += "  ... and {len(tactic_techniques) - 10} more techniques\\n"

                    total_techniques += len(tactic_techniques)
                else:
                    result_text += "⚠️  No techniques available for this tactic"
                    if group_id or platform:
                        result_text += " with current filters"
                    result_text += "\\n"
                    path_complete = False

                result_text += "\\n"

            # Path summary
            result_text += "ATTACK PATH SUMMARY\\n"
            result_text += "==================\\n"
            result_text += "Total Tactics in Path: {len(path_tactics)}\\n"
            result_text += "Total Available Techniques: {total_techniques}\\n"
            result_text += "Path Completeness: {'✅ Complete' if path_complete else '⚠️  Incomplete (some tactics have no techniques)'}\\n"

            if not path_complete:
                result_text += "\\nNote: Some tactics in the path have no available techniques with the current filters.\\n"
                result_text += "Consider removing filters or selecting different tactics to build a complete path.\\n"

            if total_techniques == 0:
                result_text += "\\nNo techniques found for the specified path and filters.\\n"
                result_text += "This could indicate that the selected group doesn't use techniques in this tactic sequence,\\n"
                result_text += "or the platform filter is too restrictive.\\n"

            return [TextContent(
                type="text",
                text=result_text
            )]

        except Exception:
            logger.error("Error in build_attack_path: {e}")
            return [TextContent(
                type="text",
                text="Error building attack path: {str(e)}"
            )]

    # Register analyze_coverage_gaps tool
    @app.tool()
    async def analyze_coverage_gaps(threat_groups: list = None, technique_list: list = None, exclude_mitigations: list = None) -> List[TextContent]:
        """
        Analyze defensive coverage gaps against threat groups or technique sets.

        Args:
            threat_groups: List of group IDs to analyze (e.g., ['G0016', 'G0032'])
            technique_list: Specific techniques to analyze coverage for (e.g., ['T1055', 'T1059'])
            exclude_mitigations: Mitigations already implemented to exclude from analysis (e.g., ['M1040', 'M1038'])

        Returns:
            List[TextContent]: Coverage gap analysis with prioritization recommendations
        """
        try:
            logger.info("Executing analyze_coverage_gaps with groups: {threat_groups}, techniques: {technique_list}")

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

            # Initialize parameters with defaults
            threat_groups = threat_groups or []
            technique_list = technique_list or []
            exclude_mitigations = exclude_mitigations or []

            # Normalize inputs to uppercase
            threat_groups = [group.upper().strip() for group in threat_groups]
            technique_list = [tech.upper().strip() for tech in technique_list]
            exclude_mitigations = [mit.upper().strip() for mit in exclude_mitigations]

            # Validate that at least one analysis target is provided
            if not threat_groups and not technique_list:
                return [TextContent(
                    type="text",
                    text="Error: Please provide either threat_groups or technique_list to analyze coverage gaps."
                )]

            # Build technique set to analyze
            techniques_to_analyze = set()

            # Add techniques from threat groups
            if threat_groups:
                for group_id in threat_groups:
                    group = None
                    for grp in data.get('groups', []):
                        if grp.get('id', '').upper() == group_id:
                            group = grp
                            break

                    if not group:
                        return [TextContent(
                            type="text",
                            text="Error: Group '{group_id}' not found. Please verify the group ID is correct."
                        )]

                    group_techniques = group.get('techniques', [])
                    techniques_to_analyze.update(group_techniques)

            # Add specific techniques
            if technique_list:
                # Validate technique IDs exist
                valid_technique_ids = {tech.get('id') for tech in data.get('techniques', [])}
                for tech_id in technique_list:
                    if tech_id not in valid_technique_ids:
                        return [TextContent(
                            type="text",
                            text="Error: Technique '{tech_id}' not found. Please verify the technique ID is correct."
                        )]

                techniques_to_analyze.update(technique_list)

            if not techniques_to_analyze:
                return [TextContent(
                    type="text",
                    text="No techniques found for the specified threat groups or technique list."
                )]

            # Analyze coverage for each technique
            coverage_analysis = []
            total_techniques = len(techniques_to_analyze)
            techniques_with_mitigations = 0
            techniques_without_mitigations = 0
            all_available_mitigations = set()
            excluded_mitigations_found = set()

            for technique_id in techniques_to_analyze:
                # Find technique details
                technique = None
                for tech in data.get('techniques', []):
                    if tech.get('id') == technique_id:
                        technique = tech
                        break

                if not technique:
                    continue

                # Get mitigations for this technique
                technique_mitigations = technique.get('mitigations', [])

                # Filter out excluded mitigations
                available_mitigations = []
                for mit_id in technique_mitigations:
                    if mit_id in exclude_mitigations:
                        excluded_mitigations_found.add(mit_id)
                    else:
                        available_mitigations.append(mit_id)

                all_available_mitigations.update(available_mitigations)

                # Categorize technique coverage
                if available_mitigations:
                    techniques_with_mitigations += 1
                    coverage_status = "COVERED"
                else:
                    techniques_without_mitigations += 1
                    if technique_mitigations:
                        coverage_status = "GAP"  # Has mitigations but all excluded
                    else:
                        coverage_status = "NO_MITIGATIONS"  # No mitigations available

                coverage_analysis.append({
                    'technique_id': technique_id,
                    'technique_name': technique.get('name', 'Unknown'),
                    'tactics': technique.get('tactics', []),
                    'platforms': technique.get('platforms', []),
                    'total_mitigations': len(technique_mitigations),
                    'available_mitigations': available_mitigations,
                    'excluded_mitigations': [mit for mit in technique_mitigations if mit in exclude_mitigations],
                    'coverage_status': coverage_status
                })

            # Sort analysis by coverage status (gaps first) and then by technique ID
            coverage_analysis.sort(key=lambda x: (x['coverage_status'] != 'GAP', x['technique_id']))

            # Build detailed response
            result_text = "COVERAGE GAP ANALYSIS\\n"
            result_text += "====================\\n\\n"

            # Analysis parameters
            if threat_groups:
                group_names = []
                for group_id in threat_groups:
                    for grp in data.get('groups', []):
                        if grp.get('id') == group_id:
                            group_names.append("{group_id} ({grp.get('name', 'Unknown')})")
                            break
                    else:
                        group_names.append("{group_id} (Name not found)")
                result_text += "Threat Groups Analyzed: {', '.join(group_names)}\\n"

            if technique_list:
                result_text += "Specific Techniques: {', '.join(technique_list)}\\n"

            if exclude_mitigations:
                result_text += "Excluded Mitigations: {', '.join(exclude_mitigations)}\\n"

            result_text += "Total Techniques Analyzed: {total_techniques}\\n\\n"

            # Coverage statistics
            coverage_percentage = (techniques_with_mitigations / total_techniques * 100) if total_techniques > 0 else 0
            result_text += "COVERAGE STATISTICS\\n"
            result_text += "==================\\n"
            result_text += "Techniques with Available Mitigations: {techniques_with_mitigations} ({coverage_percentage:.1f}%)\\n"
            result_text += "Techniques with Coverage Gaps: {techniques_without_mitigations} ({100-coverage_percentage:.1f}%)\\n"
            result_text += "Total Available Mitigations: {len(all_available_mitigations)}\\n"

            if excluded_mitigations_found:
                result_text += "Excluded Mitigations Found: {len(excluded_mitigations_found)}\\n"

            result_text += "\\n"

            # Detailed gap analysis
            gaps_found = [analysis for analysis in coverage_analysis if analysis['coverage_status'] in ['GAP', 'NO_MITIGATIONS']]

            if gaps_found:
                result_text += "DETAILED GAP ANALYSIS\\n"
                result_text += "====================\\n"
                result_text += "Techniques Requiring Attention ({len(gaps_found)}):\\n\\n"

                for i, analysis in enumerate(gaps_found[:20], 1):  # Limit to 20 for readability
                    result_text += "{i}. {analysis['technique_id']} - {analysis['technique_name']}\\n"
                    result_text += "   Status: {analysis['coverage_status']}\\n"
                    result_text += "   Tactics: {', '.join(analysis['tactics'])}\\n"
                    result_text += "   Platforms: {', '.join(analysis['platforms']) if analysis['platforms'] else 'Not specified'}\\n"

                    if analysis['coverage_status'] == 'GAP':
                        result_text += "   Issue: All {analysis['total_mitigations']} mitigations are excluded\\n"
                        result_text += "   Excluded: {', '.join(analysis['excluded_mitigations'])}\\n"
                    else:
                        result_text += "   Issue: No mitigations available in MITRE ATT&CK\\n"

                    result_text += "\\n"

                if len(gaps_found) > 20:
                    result_text += "... and {len(gaps_found) - 20} more techniques with gaps\\n\\n"

            # Prioritization recommendations
            result_text += "PRIORITIZATION RECOMMENDATIONS\\n"
            result_text += "=============================\\n"

            if coverage_percentage >= 80:
                result_text += "✅ GOOD: Coverage is strong at {coverage_percentage:.1f}%\\n"
                result_text += "Focus on addressing the remaining {techniques_without_mitigations} techniques with gaps.\\n"
            elif coverage_percentage >= 60:
                result_text += "⚠️  MODERATE: Coverage needs improvement at {coverage_percentage:.1f}%\\n"
                result_text += "Priority: Address the {techniques_without_mitigations} techniques without coverage.\\n"
            else:
                result_text += "🚨 CRITICAL: Coverage is insufficient at {coverage_percentage:.1f}%\\n"
                result_text += "Urgent: Implement mitigations for {techniques_without_mitigations} uncovered techniques.\\n"

            # Top mitigation recommendations
            if all_available_mitigations:
                result_text += "\\nTop Mitigation Recommendations:\\n"
                mitigation_counts = {}
                for analysis in coverage_analysis:
                    for mit_id in analysis['available_mitigations']:
                        mitigation_counts[mit_id] = mitigation_counts.get(mit_id, 0) + 1

                # Sort by frequency
                top_mitigations = sorted(mitigation_counts.items(), key=lambda x: x[1], reverse=True)[:5]

                for mit_id, count in top_mitigations:
                    # Find mitigation name
                    mit_name = "Unknown"
                    for mitigation in data.get('mitigations', []):
                        if mitigation.get('id') == mit_id:
                            mit_name = mitigation.get('name', 'Unknown')
                            break

                    result_text += "  • {mit_id}: {mit_name} (covers {count} techniques)\\n"

            return [TextContent(
                type="text",
                text=result_text
            )]

        except Exception:
            logger.error("Error in analyze_coverage_gaps: {e}")
            return [TextContent(
                type="text",
                text="Error analyzing coverage gaps: {str(e)}"
            )]

    # Register detect_technique_relationships tool
    @app.tool()
    async def detect_technique_relationships(technique_id: str, relationship_types: list = None, depth: int = 2) -> List[TextContent]:
        """
        Discover complex relationships between techniques, including detection, attribution, and subtechnique hierarchies.

        Args:
            technique_id: Primary technique to analyze relationships for (e.g., T1055)
            relationship_types: Types to include: ['detects', 'subtechnique-o', 'attributed-to', 'uses', 'mitigates'] (default: all)
            depth: Relationship traversal depth (default: 2, max: 3)

        Returns:
            List[TextContent]: Complex relationship analysis with hierarchies and attribution chains
        """
        try:
            logger.info("Executing detect_technique_relationships for {technique_id} with depth {depth}")

            if not app.data_loader:
                return [TextContent(
                    type="text",
                    text="Error: Data loader not available. Please ensure MITRE ATT&CK data is loaded."
                )]

            # Get cached data
            data = app.data_loader.get_cached_data('mitre_attack')
            relationships = app.data_loader.get_cached_data('mitre_attack_relationships')

            if not data or not relationships:
                return [TextContent(
                    type="text",
                    text="Error: MITRE ATT&CK data not loaded. Please load data first."
                )]

            # Normalize and validate inputs
            technique_id = technique_id.upper().strip()
            depth = max(1, min(depth, 3))  # Limit depth to prevent excessive computation

            # Default relationship types if not specified
            if relationship_types is None:
                relationship_types = ['detects', 'subtechnique-o', 'attributed-to', 'uses', 'mitigates']

            # Normalize relationship types
            relationship_types = [rt.lower().strip() for rt in relationship_types]
            valid_types = ['detects', 'subtechnique-o', 'attributed-to', 'uses', 'mitigates', 'revoked-by']
            relationship_types = [rt for rt in relationship_types if rt in valid_types]

            if not relationship_types:
                return [TextContent(
                    type="text",
                    text="Error: No valid relationship types specified. Valid types: detects, subtechnique-of, attributed-to, uses, mitigates, revoked-by"
                )]

            # Validate technique exists
            technique = None
            for tech in data.get('techniques', []):
                if tech.get('id', '').upper() == technique_id:
                    technique = tech
                    break

            if not technique:
                return [TextContent(
                    type="text",
                    text="Technique '{technique_id}' not found. Please verify the technique ID is correct."
                )]

            # Download raw data to get STIX ID mappings
            raw_data = app.data_loader.download_data(app.data_loader.config['data_sources']['mitre_attack']['url'])

            # Build proper STIX ID to MITRE ID mapping
            stix_to_mitre = {}
            mitre_to_stix = {}
            entity_lookup = {}

            for obj in raw_data.get('objects', []):
                stix_id = obj.get('id', '')
                if stix_id:
                    # Extract MITRE ID from external references
                    mitre_id = ''
                    for ref in obj.get('external_references', []):
                        if ref.get('source_name') == 'mitre-attack':
                            mitre_id = ref.get('external_id', '')
                            break

                    if mitre_id:
                        stix_to_mitre[stix_id] = mitre_id
                        mitre_to_stix[mitre_id] = stix_id
                        entity_lookup[stix_id] = obj

            # Find our technique's STIX ID
            target_stix_id = mitre_to_stix.get(technique_id)
            if not target_stix_id:
                return [TextContent(
                    type="text",
                    text="Could not find STIX ID for technique '{technique_id}'. This may indicate a data processing issue."
                )]

            # Find all relationships involving our technique
            discovered_relationships = {}
            for rel_type in relationship_types:
                discovered_relationships[rel_type] = {
                    'incoming': [],  # Relationships where our technique is the target
                    'outgoing': []   # Relationships where our technique is the source
                }

            for rel in relationships:
                rel_type = rel.get('relationship_type', '')
                source_ref = rel.get('source_re', '')
                target_ref = rel.get('target_re', '')

                if rel_type in relationship_types:
                    if target_ref == target_stix_id:
                        # Our technique is the target
                        source_mitre_id = stix_to_mitre.get(source_ref, '')
                        if source_mitre_id:
                            discovered_relationships[rel_type]['incoming'].append({
                                'entity_id': source_mitre_id,
                                'entity_stix_id': source_ref,
                                'relationship': rel
                            })
                    elif source_ref == target_stix_id:
                        # Our technique is the source
                        target_mitre_id = stix_to_mitre.get(target_ref, '')
                        if target_mitre_id:
                            discovered_relationships[rel_type]['outgoing'].append({
                                'entity_id': target_mitre_id,
                                'entity_stix_id': target_ref,
                                'relationship': rel
                            })

            # Build detailed response
            result_text = "TECHNIQUE RELATIONSHIP ANALYSIS\\n"
            result_text += "==============================\\n\\n"
            result_text += "Primary Technique: {technique_id} - {technique.get('name', 'Unknown')}\\n"
            result_text += "Analysis Depth: {depth}\\n"
            result_text += "Relationship Types: {', '.join(relationship_types)}\\n\\n"

            # Add technique description
            description = technique.get('description', 'No description available')
            if len(description) > 200:
                description = description[:200] + "..."
            result_text += "Description: {description}\\n\\n"

            # Analyze each relationship type
            total_relationships = 0
            for rel_type in relationship_types:
                incoming = discovered_relationships[rel_type]['incoming']
                outgoing = discovered_relationships[rel_type]['outgoing']

                if incoming or outgoing:
                    result_text += "{rel_type.upper().replace('-', ' ')} RELATIONSHIPS\\n"
                    result_text += "{'=' * (len(rel_type.replace('-', ' ')) + 14)}\\n\\n"

                    if incoming:
                        result_text += "Incoming {rel_type} relationships ({len(incoming)}): \\n"
                        for rel_info in incoming[:10]:  # Limit to 10 per type
                            result_text += "  • {entity_id} ({entity_type}): {entity_name}\\n"

                        if len(incoming) > 10:
                            result_text += "  ... and {len(incoming) - 10} more\\n"
                        result_text += "\\n"
                        total_relationships += len(incoming)

                    if outgoing:
                        result_text += "Outgoing {rel_type} relationships ({len(outgoing)}): \\n"
                        for rel_info in outgoing[:10]:  # Limit to 10 per type
                            result_text += "  • {entity_id} ({entity_type}): {entity_name}\\n"

                        if len(outgoing) > 10:
                            result_text += "  ... and {len(outgoing) - 10} more\\n"
                        result_text += "\\n"
                        total_relationships += len(outgoing)

            # Special analysis for subtechniques
            if 'subtechnique-o' in relationship_types:
                subtechniques = discovered_relationships['subtechnique-o']['incoming']
                parent_techniques = discovered_relationships['subtechnique-o']['outgoing']

                if subtechniques or parent_techniques:
                    result_text += "TECHNIQUE HIERARCHY\\n"
                    result_text += "==================\\n\\n"

                    if parent_techniques:
                        result_text += "Parent Techniques:\\n"
                        for rel_info in parent_techniques:
                            parent_id = rel_info['entity_id']
                            parent_name = _get_entity_name(parent_id, data)
                            result_text += "  ↑ {parent_id}: {parent_name}\\n"
                        result_text += "\\n"

                    if subtechniques:
                        result_text += "Subtechniques ({len(subtechniques)}): \\n"
                        for rel_info in subtechniques[:15]:  # Show more subtechniques
                            sub_id = rel_info['entity_id']
                            sub_name = _get_entity_name(sub_id, data)
                            result_text += "  ↓ {sub_id}: {sub_name}\\n"

                        if len(subtechniques) > 15:
                            result_text += "  ... and {len(subtechniques) - 15} more subtechniques\\n"
                        result_text += "\\n"

            # Attribution analysis
            if 'uses' in relationship_types:
                using_groups = discovered_relationships['uses']['incoming']
                if using_groups:
                    result_text += "ATTRIBUTION ANALYSIS\\n"
                    result_text += "===================\\n\\n"
                    result_text += "Threat Groups Using This Technique ({len(using_groups)}): \\n"

                    for rel_info in using_groups[:10]:
                        group_id = rel_info['entity_id']
                        group_name = _get_entity_name(group_id, data)

                        # Get group aliases if available
                        group_aliases = []
                        for group in data.get('groups', []):
                            if group.get('id') == group_id:
                                group_aliases = group.get('aliases', [])
                                break

                        result_text += "  • {group_id}: {group_name}\\n"
                        if group_aliases:
                            result_text += "    Aliases: {', '.join(group_aliases[:3])}\\n"

                    if len(using_groups) > 10:
                        result_text += "  ... and {len(using_groups) - 10} more groups\\n"
                    result_text += "\\n"

            # Detection analysis
            if 'detects' in relationship_types:
                detecting_entities = discovered_relationships['detects']['incoming']
                if detecting_entities:
                    result_text += "DETECTION ANALYSIS\\n"
                    result_text += "=================\\n\\n"
                    result_text += "Entities That Can Detect This Technique ({len(detecting_entities)}): \\n"

                    for rel_info in detecting_entities:
                        detector_id = rel_info['entity_id']
                        detector_name = _get_entity_name(detector_id, data)
                        detector_type = _get_entity_type(detector_id)
                        result_text += "  • {detector_id} ({detector_type}): {detector_name}\\n"
                    result_text += "\\n"

            # Summary
            result_text += "RELATIONSHIP SUMMARY\\n"
            result_text += "===================\\n"
            result_text += "Total Relationships Found: {total_relationships}\\n"
            result_text += "Relationship Types Analyzed: {len([rt for rt in relationship_types if discovered_relationships[rt]['incoming'] or discovered_relationships[rt]['outgoing']])}\\n"
            result_text += "Analysis Completed at Depth: {depth}\\n\\n"

            if total_relationships == 0:
                result_text += "No relationships found for technique {technique_id} with the specified relationship types.\\n"
                result_text += "This could indicate the technique is isolated or the relationship types don't apply.\\n"

            return [TextContent(
                type="text",
                text=result_text
            )]

        except Exception:
            logger.error("Error in detect_technique_relationships: {e}")
            return [TextContent(
                type="text",
                text="Error analyzing technique relationships: {str(e)}"
            )]

    logger.info("Registered 8 MCP tools successfully")
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
        logger.info("Starting MCP server with {transport} transport")
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
