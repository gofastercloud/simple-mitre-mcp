"""
STIX format parser for threat intelligence data.

This module provides specialized parsing functionality for STIX 2.1 format
data, specifically optimized for MITRE ATT&CK framework data.
"""

import logging
from typing import Dict, List, Any, Optional, Union

import stix2
from stix2 import Bundle, parse, CourseOfAction
from stix2.base import _STIXBase
from stix2.exceptions import STIXError, InvalidValueError, MissingPropertiesError

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

        # Try to use STIX2 library first, fall back to custom parsing if needed
        try:
            return self._parse_with_stix2_library(stix_data, entity_types)
        except Exception as e:
            logger.warning(f"STIX2 library parsing failed, falling back to custom parsing: {e}")
            return self._parse_with_custom_logic(stix_data, entity_types)

    def _parse_with_stix2_library(self, stix_data: Dict[str, Any], entity_types: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse STIX data using the official STIX2 library.

        Args:
            stix_data: Raw STIX JSON data
            entity_types: List of entity types to extract

        Returns:
            dict: Parsed entities organized by type

        Raises:
            STIXError: When STIX data is malformed or invalid
            InvalidValueError: When STIX object properties are invalid
            MissingPropertiesError: When required STIX properties are missing
        """
        logger.info("Parsing STIX data using official STIX2 library")

        parsed_entities = {entity_type: [] for entity_type in entity_types}

        try:
            # Parse the STIX data using the official library
            if isinstance(stix_data, dict) and 'objects' in stix_data:
                # Handle STIX Bundle format
                bundle = Bundle(allow_custom=True, **stix_data)
                # Access objects from the bundle - check if objects property exists
                if 'objects' in bundle._inner:
                    stix_objects = bundle._inner['objects']
                else:
                    # Handle empty bundles
                    stix_objects = []
            else:
                # Handle single STIX object or other formats
                parsed_data = parse(stix_data, allow_custom=True)
                if hasattr(parsed_data, '__getitem__') and 'objects' in parsed_data:
                    stix_objects = parsed_data['objects']
                else:
                    stix_objects = [parsed_data]

            objects_processed = 0
            entities_extracted = 0
            parsing_errors = 0

            for stix_obj in stix_objects:
                objects_processed += 1

                try:
                    # Determine entity type from STIX object
                    obj_type = stix_obj.type if hasattr(stix_obj, 'type') else stix_obj.get('type', '')
                    entity_type = self._map_stix_type(obj_type)
                    
                    if entity_type and entity_type in entity_types:
                        parsed_entity = self._extract_entity_from_stix_object(stix_obj, entity_type)
                        if parsed_entity:
                            parsed_entities[entity_type].append(parsed_entity)
                            entities_extracted += 1

                except (STIXError, InvalidValueError, MissingPropertiesError) as e:
                    parsing_errors += 1
                    logger.debug(f"STIX library error parsing object {objects_processed}: {e}")
                    # Continue processing other objects
                    continue
                except Exception as e:
                    parsing_errors += 1
                    logger.debug(f"Unexpected error parsing STIX object {objects_processed}: {e}")
                    continue

            logger.info(f"STIX2 library parsing completed: {objects_processed} objects processed, "
                       f"{entities_extracted} entities extracted, {parsing_errors} parsing errors")
            
            for entity_type, entities in parsed_entities.items():
                logger.info(f"  {entity_type}: {len(entities)} entities")

            return parsed_entities

        except STIXError as e:
            logger.error(f"STIX format error: {e}")
            raise
        except InvalidValueError as e:
            logger.error(f"Invalid STIX value: {e}")
            raise
        except MissingPropertiesError as e:
            logger.error(f"Missing required STIX properties: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during STIX2 library parsing: {e}")
            raise

    def _parse_with_custom_logic(self, stix_data: Dict[str, Any], entity_types: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fallback method using custom parsing logic.

        Args:
            stix_data: Raw STIX JSON data
            entity_types: List of entity types to extract

        Returns:
            dict: Parsed entities organized by type
        """
        logger.info("Using fallback custom parsing logic")

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

        logger.info(f"Custom parsing completed: {objects_processed} objects processed, {entities_extracted} entities extracted")
        for entity_type, entities in parsed_entities.items():
            logger.info(f"  {entity_type}: {len(entities)} entities")

        return parsed_entities

    def _map_stix_type(self, stix_type: str) -> str:
        """Map STIX object type to entity type."""
        return self.stix_type_mapping.get(stix_type, '')

    def _extract_entity_from_stix_object(self, stix_obj: Union[_STIXBase, Dict[str, Any]], entity_type: str) -> Optional[Dict[str, Any]]:
        """
        Extract entity data from STIX2 library object.

        Args:
            stix_obj: STIX2 library object or dictionary
            entity_type: Type of entity to extract

        Returns:
            dict: Extracted entity data, or None if extraction fails
        """
        try:
            # Handle both STIX2 library objects and raw dictionaries
            if hasattr(stix_obj, 'name'):
                # STIX2 library object
                name = stix_obj.name
                description = getattr(stix_obj, 'description', '').strip()
                mitre_id = self._extract_mitre_id_from_stix_object(stix_obj)
            else:
                # Raw dictionary (fallback)
                name = stix_obj.get('name', '')
                description = stix_obj.get('description', '').strip()
                mitre_id = self._extract_mitre_id(stix_obj)

            # Extract basic fields common to all entities
            entity_data = {
                'id': mitre_id,
                'name': name,
                'description': description
            }

            # Validate basic required fields
            if not entity_data['id'] or not entity_data['name']:
                logger.debug(f"Skipping {entity_type} entity with missing ID or name")
                return None

            # Extract entity-specific fields using STIX2 library objects
            if entity_type == 'techniques':
                entity_data.update(self._extract_technique_data_from_stix_object(stix_obj))
            elif entity_type == 'groups':
                entity_data.update(self._extract_group_data_from_stix_object(stix_obj))
            elif entity_type == 'tactics':
                entity_data.update(self._extract_tactic_data_from_stix_object(stix_obj))
            elif entity_type == 'mitigations':
                entity_data.update(self._extract_mitigation_data_from_stix_object(stix_obj))

            return entity_data

        except (STIXError, InvalidValueError, MissingPropertiesError) as e:
            logger.debug(f"STIX library error extracting {entity_type} entity: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting {entity_type} entity from STIX object: {e}")
            return None

    def _extract_entity(self, stix_obj: Dict[str, Any], entity_type: str) -> Optional[Dict[str, Any]]:
        """
        Extract entity data from STIX object (legacy method for custom parsing).

        Args:
            stix_obj: STIX object dictionary
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
        """
        Extract technique-specific data from STIX object using STIX2 library.
        
        This method now uses the official STIX2 library for parsing instead of
        raw dictionary access, providing better validation and standards compliance.
        
        Args:
            stix_obj: STIX object dictionary
            
        Returns:
            dict: Technique-specific data
        """
        try:
            # Convert dictionary to STIX2 library AttackPattern object
            stix2_obj = stix2.parse(stix_obj, allow_custom=True)
            
            # Use the STIX2 library-based extraction method
            return self._extract_technique_data_from_stix_object(stix2_obj)
            
        except (STIXError, InvalidValueError, MissingPropertiesError) as e:
            logger.debug(f"STIX2 library parsing failed for technique, falling back to dictionary access: {e}")
            # Fallback to original dictionary-based approach if STIX2 parsing fails
            return self._extract_technique_data_legacy(stix_obj)
        except Exception as e:
            logger.debug(f"Unexpected error parsing technique with STIX2 library, falling back: {e}")
            return self._extract_technique_data_legacy(stix_obj)

    def _extract_technique_data_legacy(self, stix_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy technique data extraction using raw dictionary access.
        
        This method is kept as a fallback for cases where STIX2 library parsing fails.
        
        Args:
            stix_obj: STIX object dictionary
            
        Returns:
            dict: Technique-specific data
        """
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
        """
        Extract group-specific data from STIX object using STIX2 library.
        
        This method now uses the official STIX2 library for parsing instead of
        raw dictionary access, providing better validation and standards compliance.
        
        Args:
            stix_obj: STIX object dictionary
            
        Returns:
            dict: Group-specific data
        """
        try:
            # Convert dictionary to STIX2 library IntrusionSet object
            stix2_obj = stix2.parse(stix_obj, allow_custom=True)
            
            # Use the STIX2 library-based extraction method
            return self._extract_group_data_from_stix_object(stix2_obj)
            
        except (STIXError, InvalidValueError, MissingPropertiesError) as e:
            logger.debug(f"STIX2 library parsing failed for group, falling back to dictionary access: {e}")
            # Fallback to original dictionary-based approach if STIX2 parsing fails
            return self._extract_group_data_legacy(stix_obj)
        except Exception as e:
            logger.debug(f"Unexpected error parsing group with STIX2 library, falling back: {e}")
            return self._extract_group_data_legacy(stix_obj)

    def _extract_group_data_legacy(self, stix_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy group data extraction using raw dictionary access.
        
        This method is kept as a fallback for cases where STIX2 library parsing fails.
        
        Args:
            stix_obj: STIX object dictionary
            
        Returns:
            dict: Group-specific data
        """
        data = {}

        # Extract aliases (excluding the primary name)
        aliases = stix_obj.get('aliases', [])
        primary_name = stix_obj.get('name', '')

        # Handle None aliases gracefully
        if aliases is not None:
            # Filter out the primary name from aliases
            filtered_aliases = [alias for alias in aliases if alias != primary_name]
            if filtered_aliases:
                data['aliases'] = filtered_aliases

        # Initialize empty techniques list (will be populated by relationship analysis)
        data['techniques'] = []

        return data

    def _extract_tactic_data(self, stix_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract tactic-specific data from STIX object using STIX2 library.
        
        This method now uses the official STIX2 library for parsing instead of
        raw dictionary access, providing better validation and standards compliance.
        
        Args:
            stix_obj: STIX object dictionary
            
        Returns:
            dict: Tactic-specific data
        """
        try:
            # Convert dictionary to STIX2 library object
            # For tactics (x-mitre-tactic), we use the generic parse function
            stix2_obj = stix2.parse(stix_obj, allow_custom=True)
            
            # Use the STIX2 library-based extraction method
            return self._extract_tactic_data_from_stix_object(stix2_obj)
            
        except (STIXError, InvalidValueError, MissingPropertiesError) as e:
            logger.debug(f"STIX2 library parsing failed for tactic, falling back to dictionary access: {e}")
            # Fallback to original dictionary-based approach if STIX2 parsing fails
            return self._extract_tactic_data_legacy(stix_obj)
        except Exception as e:
            logger.debug(f"Unexpected error parsing tactic with STIX2 library, falling back: {e}")
            return self._extract_tactic_data_legacy(stix_obj)

    def _extract_tactic_data_legacy(self, stix_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy tactic data extraction using raw dictionary access.
        
        This method is kept as a fallback for cases where STIX2 library parsing fails.
        
        Args:
            stix_obj: STIX object dictionary
            
        Returns:
            dict: Tactic-specific data (empty for tactics)
        """
        # Tactics only have basic fields (id, name, description)
        return {}

    def _extract_mitigation_data(self, stix_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract mitigation-specific data from STIX object using STIX2 library.
        
        This method now uses the official STIX2 library for parsing instead of
        raw dictionary access, providing better validation and standards compliance.
        
        Args:
            stix_obj: STIX object dictionary
            
        Returns:
            dict: Mitigation-specific data
        """
        try:
            # Convert dictionary to STIX2 library CourseOfAction object
            stix2_obj = stix2.parse(stix_obj, allow_custom=True)
            
            # Use the STIX2 library-based extraction method
            return self._extract_mitigation_data_from_stix_object(stix2_obj)
            
        except (STIXError, InvalidValueError, MissingPropertiesError) as e:
            logger.debug(f"STIX2 library parsing failed for mitigation, falling back to dictionary access: {e}")
            # Fallback to original dictionary-based approach if STIX2 parsing fails
            return self._extract_mitigation_data_legacy(stix_obj)
        except Exception as e:
            logger.debug(f"Unexpected error parsing mitigation with STIX2 library, falling back: {e}")
            return self._extract_mitigation_data_legacy(stix_obj)

    def _extract_mitigation_data_legacy(self, stix_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy mitigation data extraction using raw dictionary access.
        
        This method is kept as a fallback for cases where STIX2 library parsing fails.
        
        Args:
            stix_obj: STIX object dictionary
            
        Returns:
            dict: Mitigation-specific data
        """
        data = {}

        # Initialize empty techniques list (will be populated by relationship analysis)
        data['techniques'] = []

        return data

    def _extract_mitre_id_from_stix_object(self, stix_obj: Union[_STIXBase, Dict[str, Any]]) -> str:
        """
        Extract MITRE ATT&CK ID from STIX2 library object's external references.

        Args:
            stix_obj: STIX2 library object or dictionary

        Returns:
            str: MITRE ATT&CK ID, or empty string if not found
        """
        try:
            # Handle STIX2 library objects
            if hasattr(stix_obj, 'external_references'):
                external_refs = stix_obj.external_references
            else:
                # Fallback to dictionary access
                external_refs = stix_obj.get('external_references', [])

            for ref in external_refs:
                # Handle both STIX2 library ExternalReference objects and dictionaries
                if hasattr(ref, 'source_name'):
                    source_name = ref.source_name
                    external_id = getattr(ref, 'external_id', '')
                else:
                    source_name = ref.get('source_name', '')
                    external_id = ref.get('external_id', '')

                if source_name == 'mitre-attack':
                    return external_id

            return ''

        except (STIXError, InvalidValueError, AttributeError) as e:
            logger.debug(f"Error extracting MITRE ID from STIX object: {e}")
            return ''

    def _extract_technique_data_from_stix_object(self, stix_obj: Union[_STIXBase, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract technique-specific data from STIX2 library AttackPattern object.

        This method leverages the official STIX2 library's AttackPattern object
        properties for robust, standards-compliant data extraction.

        Args:
            stix_obj: STIX2 library AttackPattern object or dictionary (fallback)

        Returns:
            dict: Technique-specific data including platforms, tactics, and mitigations
        """
        data = {}

        try:
            # Extract platforms using STIX2 library's x_mitre_platforms property
            # This leverages the library's built-in property validation
            if hasattr(stix_obj, 'x_mitre_platforms'):
                platforms = stix_obj.x_mitre_platforms
            else:
                platforms = stix_obj.get('x_mitre_platforms', [])

            if platforms:
                data['platforms'] = platforms

            # Extract tactics from kill chain phases using STIX2 library's kill_chain_phases property
            # This uses the library's KillChainPhase objects for better validation
            tactics = []
            if hasattr(stix_obj, 'kill_chain_phases'):
                kill_chain_phases = stix_obj.kill_chain_phases
            else:
                kill_chain_phases = stix_obj.get('kill_chain_phases', [])

            for phase in kill_chain_phases:
                # Handle both STIX2 library KillChainPhase objects and dictionaries
                if hasattr(phase, 'kill_chain_name'):
                    kill_chain_name = phase.kill_chain_name
                    phase_name = phase.phase_name
                else:
                    kill_chain_name = phase.get('kill_chain_name', '')
                    phase_name = phase.get('phase_name', '')

                if kill_chain_name == 'mitre-attack':
                    tactic_id = self.phase_to_tactic_id.get(phase_name)
                    if tactic_id:
                        tactics.append(tactic_id)

            if tactics:
                data['tactics'] = tactics

            # Initialize empty mitigations list (will be populated by relationship analysis)
            data['mitigations'] = []

            return data

        except (STIXError, InvalidValueError, AttributeError) as e:
            logger.debug(f"Error extracting technique data from STIX object: {e}")
            return {}

    def _extract_group_data_from_stix_object(self, stix_obj: Union[_STIXBase, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract group-specific data from STIX2 library object.

        Args:
            stix_obj: STIX2 library IntrusionSet object or dictionary

        Returns:
            dict: Group-specific data
        """
        data = {}

        try:
            # Extract aliases using STIX2 library properties
            if hasattr(stix_obj, 'aliases'):
                aliases = stix_obj.aliases
            else:
                aliases = stix_obj.get('aliases', [])

            # Get primary name
            if hasattr(stix_obj, 'name'):
                primary_name = stix_obj.name
            else:
                primary_name = stix_obj.get('name', '')

            # Filter out the primary name from aliases
            filtered_aliases = [alias for alias in aliases if alias != primary_name]
            if filtered_aliases:
                data['aliases'] = filtered_aliases

            # Initialize empty techniques list (will be populated by relationship analysis)
            data['techniques'] = []

            return data

        except (STIXError, InvalidValueError, AttributeError) as e:
            logger.debug(f"Error extracting group data from STIX object: {e}")
            return {}

    def _extract_tactic_data_from_stix_object(self, stix_obj: Union[_STIXBase, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract tactic-specific data from STIX2 library object.

        Args:
            stix_obj: STIX2 library object or dictionary

        Returns:
            dict: Tactic-specific data (empty for tactics)
        """
        # Tactics only have basic fields (id, name, description)
        return {}

    def _extract_mitigation_data_from_stix_object(self, stix_obj: Union[_STIXBase, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract mitigation-specific data from STIX2 library CourseOfAction object.

        This method leverages the official STIX2 library's CourseOfAction object
        properties for robust, standards-compliant data extraction.

        Args:
            stix_obj: STIX2 library CourseOfAction object or dictionary (fallback)

        Returns:
            dict: Mitigation-specific data including techniques list
        """
        data = {}

        try:
            # For mitigations (course-of-action), we primarily need the techniques list
            # which will be populated by relationship analysis
            # The STIX2 library CourseOfAction object provides validation but
            # mitigations don't have additional custom properties like techniques do

            # Initialize empty techniques list (will be populated by relationship analysis)
            data['techniques'] = []

            return data

        except (STIXError, InvalidValueError, AttributeError) as e:
            logger.debug(f"Error extracting mitigation data from STIX object: {e}")
            return {'techniques': []}
