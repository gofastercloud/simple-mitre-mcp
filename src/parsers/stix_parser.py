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
from stix2.exceptions import (
    STIXError, 
    InvalidValueError, 
    MissingPropertiesError,
    ExtraPropertiesError,
    ParseError,
    ImmutableError,
    DependentPropertiesError
)

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
        Parse STIX data using the official STIX2 library with comprehensive error handling.

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
        error_summary = {
            'stix_errors': 0,
            'invalid_value_errors': 0,
            'missing_properties_errors': 0,
            'extra_properties_errors': 0,
            'parse_errors': 0,
            'other_errors': 0
        }

        try:
            # Parse the STIX data using the official library with enhanced error handling
            stix_objects = self._parse_stix_bundle_with_validation(stix_data)

            objects_processed = 0
            entities_extracted = 0
            total_errors = 0

            for stix_obj in stix_objects:
                objects_processed += 1

                try:
                    # Determine entity type from STIX object with validation
                    obj_type = self._get_stix_object_type_safely(stix_obj)
                    entity_type = self._map_stix_type(obj_type)
                    
                    if entity_type and entity_type in entity_types:
                        parsed_entity = self._extract_entity_from_stix_object_with_validation(stix_obj, entity_type)
                        if parsed_entity:
                            parsed_entities[entity_type].append(parsed_entity)
                            entities_extracted += 1

                except STIXError as e:
                    error_summary['stix_errors'] += 1
                    total_errors += 1
                    logger.debug(f"STIX format error in object {objects_processed}: {e}")
                    self._log_stix_object_context(stix_obj, "STIXError", str(e))
                    continue
                    
                except InvalidValueError as e:
                    error_summary['invalid_value_errors'] += 1
                    total_errors += 1
                    logger.debug(f"Invalid STIX value in object {objects_processed}: {e}")
                    self._log_stix_object_context(stix_obj, "InvalidValueError", str(e))
                    continue
                    
                except MissingPropertiesError as e:
                    error_summary['missing_properties_errors'] += 1
                    total_errors += 1
                    logger.debug(f"Missing STIX properties in object {objects_processed}: {e}")
                    self._log_stix_object_context(stix_obj, "MissingPropertiesError", str(e))
                    continue
                    
                except ExtraPropertiesError as e:
                    error_summary['extra_properties_errors'] += 1
                    total_errors += 1
                    logger.debug(f"Extra STIX properties in object {objects_processed}: {e}")
                    self._log_stix_object_context(stix_obj, "ExtraPropertiesError", str(e))
                    continue
                    
                except ParseError as e:
                    error_summary['parse_errors'] += 1
                    total_errors += 1
                    logger.debug(f"STIX parse error in object {objects_processed}: {e}")
                    self._log_stix_object_context(stix_obj, "ParseError", str(e))
                    continue
                    
                except Exception as e:
                    error_summary['other_errors'] += 1
                    total_errors += 1
                    logger.debug(f"Unexpected error parsing STIX object {objects_processed}: {e}")
                    self._log_stix_object_context(stix_obj, "UnexpectedError", str(e))
                    continue

            # Log comprehensive parsing summary
            logger.info(f"STIX2 library parsing completed: {objects_processed} objects processed, "
                       f"{entities_extracted} entities extracted, {total_errors} total errors")
            
            if total_errors > 0:
                logger.info(f"Error breakdown: STIXError={error_summary['stix_errors']}, "
                           f"InvalidValueError={error_summary['invalid_value_errors']}, "
                           f"MissingPropertiesError={error_summary['missing_properties_errors']}, "
                           f"ExtraPropertiesError={error_summary['extra_properties_errors']}, "
                           f"ParseError={error_summary['parse_errors']}, "
                           f"Other={error_summary['other_errors']}")
            
            for entity_type, entities in parsed_entities.items():
                logger.info(f"  {entity_type}: {len(entities)} entities")

            return parsed_entities

        except STIXError as e:
            logger.error(f"Critical STIX format error - unable to parse bundle: {e}")
            logger.error(f"Error details: {self._get_stix_error_details(e)}")
            raise
            
        except InvalidValueError as e:
            logger.error(f"Critical invalid STIX value - unable to parse bundle: {e}")
            logger.error(f"Error details: {self._get_stix_error_details(e)}")
            raise
            
        except MissingPropertiesError as e:
            logger.error(f"Critical missing STIX properties - unable to parse bundle: {e}")
            logger.error(f"Error details: {self._get_stix_error_details(e)}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected critical error during STIX2 library parsing: {e}")
            logger.error(f"Data type: {type(stix_data)}, Entity types: {entity_types}")
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

    def _parse_stix_bundle_with_validation(self, stix_data: Dict[str, Any]) -> List[Any]:
        """
        Parse STIX bundle with comprehensive validation and error handling.
        
        Args:
            stix_data: Raw STIX JSON data
            
        Returns:
            List of STIX objects
            
        Raises:
            STIXError: When bundle structure is invalid
            InvalidValueError: When bundle properties are invalid
            MissingPropertiesError: When required bundle properties are missing
        """
        try:
            if isinstance(stix_data, dict) and 'objects' in stix_data:
                # Handle STIX Bundle format with validation
                logger.debug("Parsing STIX Bundle format")
                bundle = Bundle(allow_custom=True, **stix_data)
                
                # Access objects from the bundle with validation
                if hasattr(bundle, '_inner') and 'objects' in bundle._inner:
                    stix_objects = bundle._inner['objects']
                    logger.debug(f"Found {len(stix_objects)} objects in bundle")
                elif hasattr(bundle, 'objects'):
                    stix_objects = bundle.objects
                    logger.debug(f"Found {len(stix_objects)} objects in bundle.objects")
                else:
                    # Handle empty bundles
                    logger.warning("Bundle contains no objects")
                    stix_objects = []
                    
            else:
                # Handle single STIX object or other formats
                logger.debug("Parsing single STIX object or non-bundle format")
                parsed_data = parse(stix_data, allow_custom=True)
                
                if hasattr(parsed_data, '__getitem__') and 'objects' in parsed_data:
                    stix_objects = parsed_data['objects']
                    logger.debug(f"Found {len(stix_objects)} objects in parsed data")
                else:
                    stix_objects = [parsed_data]
                    logger.debug("Treating as single STIX object")
                    
            return stix_objects
            
        except STIXError as e:
            logger.error(f"STIX bundle validation failed: {e}")
            raise
        except InvalidValueError as e:
            logger.error(f"Invalid bundle property values: {e}")
            raise
        except MissingPropertiesError as e:
            logger.error(f"Missing required bundle properties: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error parsing STIX bundle: {e}")
            raise STIXError(f"Bundle parsing failed: {e}")

    def _get_stix_object_type_safely(self, stix_obj: Any) -> str:
        """
        Safely extract STIX object type with error handling.
        
        Args:
            stix_obj: STIX object (library object or dictionary)
            
        Returns:
            str: STIX object type, or empty string if not found
        """
        try:
            if hasattr(stix_obj, 'type'):
                obj_type = stix_obj.type
                if not isinstance(obj_type, str):
                    logger.warning(f"STIX object type is not a string: {type(obj_type)}")
                    return ''
                return obj_type
            elif isinstance(stix_obj, dict):
                obj_type = stix_obj.get('type', '')
                if not isinstance(obj_type, str):
                    logger.warning(f"STIX object type in dict is not a string: {type(obj_type)}")
                    return ''
                return obj_type
            else:
                logger.warning(f"Unknown STIX object format: {type(stix_obj)}")
                return ''
        except Exception as e:
            logger.debug(f"Error extracting STIX object type: {e}")
            return ''

    def _extract_entity_from_stix_object_with_validation(self, stix_obj: Union[_STIXBase, Dict[str, Any]], entity_type: str) -> Optional[Dict[str, Any]]:
        """
        Extract entity data from STIX2 library object with comprehensive validation.

        Args:
            stix_obj: STIX2 library object or dictionary
            entity_type: Type of entity to extract

        Returns:
            dict: Extracted entity data, or None if extraction fails
            
        Raises:
            STIXError: When STIX object validation fails
            InvalidValueError: When STIX object properties are invalid
            MissingPropertiesError: When required STIX properties are missing
        """
        try:
            # Validate basic object structure first
            if not self._validate_stix_object_structure(stix_obj):
                logger.debug(f"Invalid STIX object structure for {entity_type}")
                return None

            # Handle both STIX2 library objects and raw dictionaries
            if hasattr(stix_obj, 'name'):
                # STIX2 library object - use validated property access
                name = stix_obj.name
                description = getattr(stix_obj, 'description', '').strip()
                mitre_id = self._extract_mitre_id_from_stix_object_with_validation(stix_obj)
            else:
                # Raw dictionary (fallback) - validate fields
                if not isinstance(stix_obj, dict):
                    raise InvalidValueError("STIX object", "object", "Expected dictionary or STIX object")
                    
                name = stix_obj.get('name', '')
                description = stix_obj.get('description', '').strip()
                mitre_id = self._extract_mitre_id_with_validation(stix_obj)

            # Validate extracted basic fields
            if not isinstance(name, str) or not name.strip():
                logger.debug(f"Invalid or missing name for {entity_type} entity")
                return None
                
            if not isinstance(description, str):
                logger.debug(f"Invalid description type for {entity_type} entity: {type(description)}")
                description = ''

            # Extract basic fields common to all entities
            entity_data = {
                'id': mitre_id,
                'name': name.strip(),
                'description': description
            }

            # Validate basic required fields
            if not entity_data['id'] or not entity_data['name']:
                logger.debug(f"Skipping {entity_type} entity with missing ID or name")
                return None

            # Extract entity-specific fields using STIX2 library objects with validation
            try:
                if entity_type == 'techniques':
                    entity_data.update(self._extract_technique_data_from_stix_object_with_validation(stix_obj))
                elif entity_type == 'groups':
                    entity_data.update(self._extract_group_data_from_stix_object_with_validation(stix_obj))
                elif entity_type == 'tactics':
                    entity_data.update(self._extract_tactic_data_from_stix_object_with_validation(stix_obj))
                elif entity_type == 'mitigations':
                    entity_data.update(self._extract_mitigation_data_from_stix_object_with_validation(stix_obj))
            except (STIXError, InvalidValueError, MissingPropertiesError) as e:
                logger.debug(f"Error extracting {entity_type}-specific data: {e}")
                # Continue with basic entity data if specific extraction fails
                pass

            return entity_data

        except (STIXError, InvalidValueError, MissingPropertiesError) as e:
            logger.debug(f"STIX library error extracting {entity_type} entity: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting {entity_type} entity from STIX object: {e}")
            raise STIXError(f"Entity extraction failed: {e}")

    def _validate_stix_object_structure(self, stix_obj: Any) -> bool:
        """
        Validate basic STIX object structure.
        
        Args:
            stix_obj: STIX object to validate
            
        Returns:
            bool: True if structure is valid, False otherwise
        """
        try:
            if stix_obj is None:
                return False
                
            # Check if it's a STIX2 library object or dictionary
            if hasattr(stix_obj, 'type') or (isinstance(stix_obj, dict) and 'type' in stix_obj):
                return True
                
            logger.debug(f"STIX object missing type field: {type(stix_obj)}")
            return False
            
        except Exception as e:
            logger.debug(f"Error validating STIX object structure: {e}")
            return False

    def _log_stix_object_context(self, stix_obj: Any, error_type: str, error_message: str) -> None:
        """
        Log contextual information about STIX object that caused an error.
        
        Args:
            stix_obj: STIX object that caused the error
            error_type: Type of error that occurred
            error_message: Error message
        """
        try:
            context_info = {
                'error_type': error_type,
                'error_message': error_message,
                'object_type': 'unknown'
            }
            
            # Extract basic object information safely
            if hasattr(stix_obj, 'type'):
                context_info['object_type'] = getattr(stix_obj, 'type', 'unknown')
                context_info['object_id'] = getattr(stix_obj, 'id', 'unknown')
            elif isinstance(stix_obj, dict):
                context_info['object_type'] = stix_obj.get('type', 'unknown')
                context_info['object_id'] = stix_obj.get('id', 'unknown')
                
            logger.debug(f"STIX object error context: {context_info}")
            
        except Exception as e:
            logger.debug(f"Error logging STIX object context: {e}")

    def _get_stix_error_details(self, error: Exception) -> str:
        """
        Extract detailed information from STIX library errors.
        
        Args:
            error: STIX library exception
            
        Returns:
            str: Detailed error information
        """
        try:
            error_details = {
                'error_type': type(error).__name__,
                'error_message': str(error)
            }
            
            # Extract additional details for specific STIX error types
            if isinstance(error, InvalidValueError):
                # InvalidValueError has different attributes in different versions
                if hasattr(error, 'prop_name'):
                    error_details['property'] = error.prop_name
                elif hasattr(error, 'property'):
                    error_details['property'] = error.property
                if hasattr(error, 'reason'):
                    error_details['reason'] = error.reason
                    
            elif isinstance(error, MissingPropertiesError):
                if hasattr(error, 'properties'):
                    error_details['missing_properties'] = error.properties
                    
            elif isinstance(error, ExtraPropertiesError):
                if hasattr(error, 'properties'):
                    error_details['extra_properties'] = error.properties
                    
            return f"STIX Error Details: {error_details}"
            
        except Exception as e:
            return f"Error extracting STIX error details: {e}"

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
        """
        Extract MITRE ATT&CK ID from external references (legacy method).

        This method maintains backward compatibility for dictionary-based parsing
        while incorporating improved validation from the STIX2 library approach.

        Args:
            stix_obj: STIX object dictionary

        Returns:
            str: MITRE ATT&CK ID, or empty string if not found
        """
        try:
            external_refs = stix_obj.get('external_references', [])
            
            # Validate external_references structure
            if not isinstance(external_refs, list):
                logger.warning(f"Invalid external_references type: {type(external_refs)}, expected list")
                return ''
            
            for i, ref in enumerate(external_refs):
                try:
                    # Validate reference structure
                    if not isinstance(ref, dict):
                        logger.debug(f"External reference {i} is not a dictionary: {type(ref)}")
                        continue
                    
                    source_name = ref.get('source_name', '')
                    external_id = ref.get('external_id', '')
                    
                    # Validate required fields
                    if not source_name:
                        logger.debug(f"External reference {i} missing source_name field")
                        continue
                        
                    if not external_id:
                        logger.debug(f"External reference {i} missing external_id field")
                        continue
                    
                    # Check for MITRE ATT&CK reference with validation
                    if source_name == 'mitre-attack':
                        # Use the same validation as the enhanced method
                        if self._validate_mitre_id_format(external_id):
                            return external_id
                        else:
                            logger.warning(f"Invalid MITRE ID format: {external_id}")
                            continue
                            
                except (KeyError, TypeError, AttributeError) as e:
                    logger.debug(f"Error processing external reference {i}: {e}")
                    continue
            
            # No valid MITRE ATT&CK reference found
            return ''
            
        except Exception as e:
            logger.error(f"Unexpected error extracting MITRE ID from dictionary: {e}")
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

    def _extract_mitre_id_from_stix_object_with_validation(self, stix_obj: Union[_STIXBase, Dict[str, Any]]) -> str:
        """
        Extract MITRE ATT&CK ID from STIX2 library object with comprehensive validation.

        Args:
            stix_obj: STIX2 library object or dictionary

        Returns:
            str: MITRE ATT&CK ID, or empty string if not found

        Raises:
            STIXError: When STIX object validation fails
            InvalidValueError: When external reference properties are invalid
        """
        try:
            return self._extract_mitre_id_from_stix_object(stix_obj)
        except (STIXError, InvalidValueError) as e:
            logger.debug(f"STIX library error in MITRE ID extraction: {e}")
            raise
        except Exception as e:
            logger.debug(f"Unexpected error in MITRE ID extraction: {e}")
            return ''

    def _extract_mitre_id_with_validation(self, stix_obj: Dict[str, Any]) -> str:
        """
        Extract MITRE ATT&CK ID from dictionary with validation.

        Args:
            stix_obj: STIX object dictionary

        Returns:
            str: MITRE ATT&CK ID, or empty string if not found
        """
        try:
            return self._extract_mitre_id(stix_obj)
        except Exception as e:
            logger.debug(f"Error in dictionary-based MITRE ID extraction: {e}")
            return ''

    def _extract_mitre_id_from_stix_object(self, stix_obj: Union[_STIXBase, Dict[str, Any]]) -> str:
        """
        Extract MITRE ATT&CK ID from STIX2 library object's external references.

        This method leverages the STIX2 library's external_references handling
        and validation mechanisms for robust, standards-compliant ID extraction.

        Args:
            stix_obj: STIX2 library object or dictionary

        Returns:
            str: MITRE ATT&CK ID, or empty string if not found

        Raises:
            STIXError: When STIX object validation fails
            InvalidValueError: When external reference properties are invalid
        """
        try:
            # Use STIX2 library's external_references property with validation
            if hasattr(stix_obj, 'external_references'):
                # STIX2 library object - use validated property access
                external_refs = stix_obj.external_references
                
                # Validate that external_references is a list
                if not isinstance(external_refs, list):
                    logger.warning(f"Invalid external_references type: {type(external_refs)}, expected list")
                    return ''
                    
            else:
                # Fallback to dictionary access with validation
                external_refs = stix_obj.get('external_references', [])
                
                # Validate external_references structure
                if not isinstance(external_refs, list):
                    logger.warning(f"Invalid external_references in dictionary: {type(external_refs)}, expected list")
                    return ''

            # Process external references with enhanced validation
            for i, ref in enumerate(external_refs):
                try:
                    # Handle STIX2 library ExternalReference objects
                    if hasattr(ref, 'source_name'):
                        # Use library's validated property access
                        source_name = ref.source_name
                        external_id = getattr(ref, 'external_id', None)
                        
                        # Validate required properties using library validation
                        if not source_name:
                            logger.debug(f"External reference {i} missing source_name")
                            continue
                            
                        if external_id is None:
                            logger.debug(f"External reference {i} missing external_id")
                            continue
                            
                    else:
                        # Dictionary fallback with enhanced validation
                        if not isinstance(ref, dict):
                            logger.warning(f"External reference {i} is not a dictionary: {type(ref)}")
                            continue
                            
                        source_name = ref.get('source_name', '')
                        external_id = ref.get('external_id', '')
                        
                        # Validate required fields
                        if not source_name:
                            logger.debug(f"External reference {i} missing source_name field")
                            continue
                            
                        if not external_id:
                            logger.debug(f"External reference {i} missing external_id field")
                            continue

                    # Check for MITRE ATT&CK reference with validation
                    if source_name == 'mitre-attack':
                        # Validate MITRE ID format (basic pattern check)
                        if self._validate_mitre_id_format(external_id):
                            return external_id
                        else:
                            logger.warning(f"Invalid MITRE ID format: {external_id}")
                            continue

                except (STIXError, InvalidValueError) as e:
                    logger.debug(f"STIX library error processing external reference {i}: {e}")
                    continue
                except (AttributeError, KeyError, TypeError) as e:
                    logger.debug(f"Error accessing external reference {i} properties: {e}")
                    continue

            # No valid MITRE ATT&CK reference found
            logger.debug("No valid MITRE ATT&CK external reference found")
            return ''

        except (STIXError, InvalidValueError) as e:
            logger.warning(f"STIX library error extracting MITRE ID: {e}")
            # Re-raise STIX library errors for proper error handling upstream
            raise
        except (AttributeError, TypeError) as e:
            logger.debug(f"Error accessing STIX object properties: {e}")
            return ''
        except Exception as e:
            logger.error(f"Unexpected error extracting MITRE ID from STIX object: {e}")
            return ''

    def _validate_mitre_id_format(self, mitre_id: str) -> bool:
        """
        Validate MITRE ATT&CK ID format using basic pattern matching.

        Args:
            mitre_id: MITRE ID to validate

        Returns:
            bool: True if ID format is valid, False otherwise
        """
        if not isinstance(mitre_id, str) or not mitre_id:
            return False
            
        # Basic MITRE ID format validation
        # Techniques: T1234, T1234.001
        # Groups: G0001
        # Tactics: TA0001
        # Mitigations: M1001
        import re
        
        # Pattern for MITRE ATT&CK IDs
        mitre_pattern = r'^(T\d{4}(\.\d{3})?|G\d{4}|TA\d{4}|M\d{4})$'
        
        return bool(re.match(mitre_pattern, mitre_id))

    def _extract_technique_data_from_stix_object_with_validation(self, stix_obj: Union[_STIXBase, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract technique-specific data from STIX2 library object with validation.

        Args:
            stix_obj: STIX2 library AttackPattern object or dictionary

        Returns:
            dict: Technique-specific data including platforms, tactics, and mitigations

        Raises:
            STIXError: When STIX object validation fails
            InvalidValueError: When technique properties are invalid
        """
        try:
            return self._extract_technique_data_from_stix_object(stix_obj)
        except (STIXError, InvalidValueError, AttributeError) as e:
            logger.debug(f"STIX library error in technique data extraction: {e}")
            raise
        except Exception as e:
            logger.debug(f"Unexpected error in technique data extraction: {e}")
            return {}

    def _extract_group_data_from_stix_object_with_validation(self, stix_obj: Union[_STIXBase, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract group-specific data from STIX2 library object with validation.

        Args:
            stix_obj: STIX2 library IntrusionSet object or dictionary

        Returns:
            dict: Group-specific data

        Raises:
            STIXError: When STIX object validation fails
            InvalidValueError: When group properties are invalid
        """
        try:
            return self._extract_group_data_from_stix_object(stix_obj)
        except (STIXError, InvalidValueError, AttributeError) as e:
            logger.debug(f"STIX library error in group data extraction: {e}")
            raise
        except Exception as e:
            logger.debug(f"Unexpected error in group data extraction: {e}")
            return {}

    def _extract_tactic_data_from_stix_object_with_validation(self, stix_obj: Union[_STIXBase, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract tactic-specific data from STIX2 library object with validation.

        Args:
            stix_obj: STIX2 library object or dictionary

        Returns:
            dict: Tactic-specific data (empty for tactics)

        Raises:
            STIXError: When STIX object validation fails
            InvalidValueError: When tactic properties are invalid
        """
        try:
            return self._extract_tactic_data_from_stix_object(stix_obj)
        except (STIXError, InvalidValueError, AttributeError) as e:
            logger.debug(f"STIX library error in tactic data extraction: {e}")
            raise
        except Exception as e:
            logger.debug(f"Unexpected error in tactic data extraction: {e}")
            return {}

    def _extract_mitigation_data_from_stix_object_with_validation(self, stix_obj: Union[_STIXBase, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract mitigation-specific data from STIX2 library object with validation.

        Args:
            stix_obj: STIX2 library CourseOfAction object or dictionary

        Returns:
            dict: Mitigation-specific data including techniques list

        Raises:
            STIXError: When STIX object validation fails
            InvalidValueError: When mitigation properties are invalid
        """
        try:
            return self._extract_mitigation_data_from_stix_object(stix_obj)
        except (STIXError, InvalidValueError, AttributeError) as e:
            logger.debug(f"STIX library error in mitigation data extraction: {e}")
            raise
        except Exception as e:
            logger.debug(f"Unexpected error in mitigation data extraction: {e}")
            return {'techniques': []}

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
