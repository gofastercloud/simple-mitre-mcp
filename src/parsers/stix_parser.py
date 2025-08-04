"""
STIX format parser for threat intelligence data.

This module provides specialized parsing functionality for STIX 2.1 format
data, specifically optimized for MITRE ATT&CK framework data.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class STIXParser:
    """
    Parser for STIX 2.1 format threat intelligence data.

    Handles extraction and normalization of MITRE ATT&CK entities
    from STIX JSON format.
    """

    def __init__(self):
        """Initialize the STIX parser."""
        self.stix_type_mapping = {
            'x-mitre-tactic': 'tactics',
            'attack-pattern': 'techniques',
            'intrusion-set': 'groups',
            'course-of-action': 'mitigations'
        }

        # MITRE ATT&CK kill chain phase to tactic ID mapping
        self.phase_to_tactic_id = {
            'initial-access': 'TA0001',
            'execution': 'TA0002',
            'persistence': 'TA0003',
            'privilege-escalation': 'TA0004',
            'defense-evasion': 'TA0005',
            'credential-access': 'TA0006',
            'discovery': 'TA0007',
            'lateral-movement': 'TA0008',
            'collection': 'TA0009',
            'command-and-control': 'TA0011',
            'exfiltration': 'TA0010',
            'impact': 'TA0040'
        }

    def parse(self, stix_data: Dict[str, Any], entity_types: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse STIX data and extract specified entity types.

        Args:
            stix_data: Raw STIX JSON data
            entity_types: List of entity types to extract

        Returns:
            dict: Parsed entities organized by type
        """
        logger.info("Starting STIX data parsing")

        parsed_entities = {entity_type: [] for entity_type in entity_types}

        if 'objects' not in stix_data:
            logger.warning("No 'objects' field found in STIX data")
            return parsed_entities

        objects_processed = 0
        entities_extracted = 0

        for obj in stix_data['objects']:
            objects_processed += 1

            # Determine entity type from STIX object
            obj_type = obj.get('type', '')
            entity_type = self._map_stix_type(obj_type)
            
            if entity_type and entity_type in entity_types:
                parsed_entity = self._extract_entity(obj, entity_type)
                if parsed_entity:
                    parsed_entities[entity_type].append(parsed_entity)
                    entities_extracted += 1

        logger.info(f"Processed {objects_processed} STIX objects, extracted {entities_extracted} entities")
        for entity_type, entities in parsed_entities.items():
            logger.info(f"  {entity_type}: {len(entities)} entities")

        return parsed_entities

    def _map_stix_type(self, stix_type: str) -> str:
        """Map STIX object type to entity type."""
        return self.stix_type_mapping.get(stix_type, '')

    def _extract_entity(self, stix_obj: Dict[str, Any], entity_type: str) -> Optional[Dict[str, Any]]:
        """
        Extract entity data from STIX object.

        Args:
            stix_obj: STIX object
            entity_type: Type of entity to extract

        Returns:
            dict: Extracted entity data, or None if extraction fails
        """
        try:
            # Extract basic fields common to all entities
            entity_data = {
                'id': self._extract_mitre_id(stix_obj),
                'name': stix_obj.get('name', ''),
                'description': stix_obj.get('description', '').strip()
            }

            # Validate basic required fields
            if not entity_data['id'] or not entity_data['name']:
                logger.debug(f"Skipping {entity_type} entity with missing ID or name")
                return None

            # Extract entity-specific fields
            if entity_type == 'techniques':
                entity_data.update(self._extract_technique_data(stix_obj))
            elif entity_type == 'groups':
                entity_data.update(self._extract_group_data(stix_obj))
            elif entity_type == 'tactics':
                entity_data.update(self._extract_tactic_data(stix_obj))
            elif entity_type == 'mitigations':
                entity_data.update(self._extract_mitigation_data(stix_obj))

            return entity_data

        except Exception as e:
            logger.error(f"Error extracting {entity_type} entity: {e}")
            return None

    def _extract_mitre_id(self, stix_obj: Dict[str, Any]) -> str:
        """Extract MITRE ATT&CK ID from external references."""
        external_refs = stix_obj.get('external_references', [])
        for ref in external_refs:
            if ref.get('source_name') == 'mitre-attack':
                return ref.get('external_id', '')
        return ''

    def _extract_technique_data(self, stix_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Extract technique-specific data from STIX object."""
        data = {}

        # Extract platforms
        platforms = stix_obj.get('x_mitre_platforms', [])
        if platforms:
            data['platforms'] = platforms

        # Extract tactics from kill chain phases
        tactics = []
        kill_chain_phases = stix_obj.get('kill_chain_phases', [])
        for phase in kill_chain_phases:
            if phase.get('kill_chain_name') == 'mitre-attack':
                phase_name = phase.get('phase_name', '')
                tactic_id = self.phase_to_tactic_id.get(phase_name)
                if tactic_id:
                    tactics.append(tactic_id)

        if tactics:
            data['tactics'] = tactics

        # Initialize empty mitigations list (will be populated by relationship analysis)
        data['mitigations'] = []

        return data

    def _extract_group_data(self, stix_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Extract group-specific data from STIX object."""
        data = {}

        # Extract aliases (excluding the primary name)
        aliases = stix_obj.get('aliases', [])
        primary_name = stix_obj.get('name', '')

        # Filter out the primary name from aliases
        filtered_aliases = [alias for alias in aliases if alias != primary_name]
        if filtered_aliases:
            data['aliases'] = filtered_aliases

        # Initialize empty techniques list (will be populated by relationship analysis)
        data['techniques'] = []

        return data

    def _extract_tactic_data(self, stix_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tactic-specific data from STIX object."""
        # Tactics only have basic fields (id, name, description)
        return {}

    def _extract_mitigation_data(self, stix_obj: Dict[str, Any]) -> Dict[str, Any]:
        """Extract mitigation-specific data from STIX object."""
        data = {}

        # Initialize empty techniques list (will be populated by relationship analysis)
        data['techniques'] = []

        return data
