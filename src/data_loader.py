"""
Generic data loading and parsing framework for threat intelligence sources.

This module provides functionality to download, parse, and store threat intelligence
data from various sources in a configuration-driven manner.
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union
import stix2
from stix2 import Relationship, parse
from stix2.base import _STIXBase, _DomainObject
from stix2.exceptions import STIXError, InvalidValueError, MissingPropertiesError
from src.config_loader import load_config
from src.parsers.stix_parser import STIXParser, ParsedEntitiesDict, ParsedEntityData

logger = logging.getLogger(__name__)

# Type aliases for data loader
STIXRelationshipObject = Union[Relationship, _STIXBase, _DomainObject]
RelationshipData = Dict[str, Any]


class DataLoader:
    """
    Generic data loader for threat intelligence frameworks using official STIX2 library.

    This loader supports configuration-driven loading of data from various sources
    and formats, with pluggable parsers for different data formats. It leverages
    the official STIX2 library for robust relationship processing and validation.

    The loader processes STIX relationships using STIX2 library objects (Relationship)
    for type-safe relationship analysis and enhanced metadata extraction, with
    fallback to dictionary-based processing for compatibility.
    """

    def __init__(self):
        """Initialize the data loader with configuration."""
        self.config = load_config()
        self.data_cache: Dict[
            str, Union[ParsedEntitiesDict, List[RelationshipData]]
        ] = {}
        self.stix_parser = STIXParser()

    def download_data(self, url: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Download JSON data from a URL.

        Args:
            url: The URL to download data from
            timeout: Request timeout in seconds

        Returns:
            dict: Downloaded JSON data

        Raises:
            requests.RequestException: If download fails
            json.JSONDecodeError: If JSON parsing fails
        """
        logger.info(f"Downloading data from: {url}")

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            data: Dict[str, Any] = response.json()
            logger.info(f"Successfully downloaded {len(str(data))} bytes of data")
            return data

        except requests.RequestException as e:
            logger.error(f"Failed to download data from {url}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {url}: {e}")
            raise

    def load_data_source(self, source_name: str) -> ParsedEntitiesDict:
        """
        Load and parse data from a configured data source.

        Args:
            source_name: Name of the data source from configuration

        Returns:
            dict: Parsed data organized by entity type

        Raises:
            ValueError: If data source is not configured
            Exception: If data loading or parsing fails
        """
        if source_name not in self.config["data_sources"]:
            raise ValueError("Data source '{source_name}' not found in configuration")

        source_config = self.config["data_sources"][source_name]

        # Download raw data
        raw_data = self.download_data(source_config["url"])

        # Parse data based on format
        if source_config["format"] == "stix":
            parsed_data = self.stix_parser.parse(
                raw_data, source_config["entity_types"]
            )
            # Process relationships between entities
            parsed_data = self._process_relationships(raw_data, parsed_data)
        else:
            raise ValueError("Unsupported data format: {source_config['format']}")

        # Cache the parsed data
        self.data_cache[source_name] = parsed_data

        # Also cache raw relationships for advanced analysis
        raw_relationships: List[RelationshipData] = [
            obj
            for obj in raw_data.get("objects", [])
            if obj.get("type") == "relationship"
        ]
        self.data_cache[f"{source_name}_relationships"] = raw_relationships

        logger.info(f"Successfully loaded data source '{source_name}'")
        for entity_type, entities in parsed_data.items():
            logger.info(f"  {entity_type}: {len(entities)} entities")

        return parsed_data

    def _process_relationships(
        self, raw_data: Dict[str, Any], parsed_data: ParsedEntitiesDict
    ) -> ParsedEntitiesDict:
        """
        Process STIX relationships to populate entity connections using STIX2 library.

        Args:
            raw_data: Original STIX data containing relationship objects
            parsed_data: Parsed entities to enhance with relationships

        Returns:
            dict: Enhanced parsed data with relationships populated
        """
        logger.info("Processing entity relationships using STIX2 library")

        # Create lookup maps for entities by their STIX IDs
        entity_lookup: Dict[str, Dict[str, Any]] = {}
        stix_id_to_mitre_id: Dict[str, str] = {}

        # Build lookup maps from the raw STIX data
        for obj in raw_data.get("objects", []):
            stix_id = obj.get("id", "")
            if not stix_id:
                continue

            # Get MITRE ID for this object
            mitre_id = self._extract_mitre_id_from_stix(obj)
            if mitre_id:
                stix_id_to_mitre_id[stix_id] = mitre_id
                entity_lookup[stix_id] = obj

        # Process relationship objects using STIX2 library
        relationships_processed = 0
        parsing_errors = 0

        for obj in raw_data.get("objects", []):
            if obj.get("type") == "relationship":
                try:
                    # Parse relationship using STIX2 library
                    stix_relationship = self._parse_stix_relationship(obj)
                    if stix_relationship:
                        self._process_single_relationship_with_stix2(
                            stix_relationship, parsed_data, stix_id_to_mitre_id
                        )
                        relationships_processed += 1
                except (STIXError, InvalidValueError, MissingPropertiesError) as e:
                    parsing_errors += 1
                    logger.debug(f"STIX library error parsing relationship: {e}")
                    # Fallback to dictionary-based processing
                    try:
                        self._process_single_relationship_legacy(
                            obj, parsed_data, stix_id_to_mitre_id
                        )
                        relationships_processed += 1
                    except Exception as fallback_error:
                        logger.warning(
                            f"Failed to process relationship with both STIX2 library and fallback: {fallback_error}"
                        )
                except Exception as e:
                    parsing_errors += 1
                    logger.debug(
                        f"Unexpected error parsing relationship with STIX2 library: {e}"
                    )
                    # Fallback to dictionary-based processing
                    try:
                        self._process_single_relationship_legacy(
                            obj, parsed_data, stix_id_to_mitre_id
                        )
                        relationships_processed += 1
                    except Exception as fallback_error:
                        logger.warning(
                            f"Failed to process relationship with both STIX2 library and fallback: {fallback_error}"
                        )

        logger.info(
            f"Processed {relationships_processed} relationship objects using STIX2 library"
        )
        if parsing_errors > 0:
            logger.info(
                f"Encountered {parsing_errors} parsing errors, used fallback processing where possible"
            )
        return parsed_data

    def _parse_stix_relationship(
        self, rel_obj: Dict[str, Any]
    ) -> Optional[STIXRelationshipObject]:
        """
        Parse a STIX relationship object using the official STIX2 library.

        Args:
            rel_obj: Raw STIX relationship object dictionary

        Returns:
            Union[Relationship, _STIXBase]: STIX2 library Relationship object, or None if parsing fails

        Raises:
            STIXError: When STIX relationship data is malformed
            InvalidValueError: When relationship properties are invalid
            MissingPropertiesError: When required relationship properties are missing
        """
        try:
            # Use STIX2 library to parse the relationship object
            stix_relationship = parse(rel_obj, allow_custom=True)

            # Verify it's actually a Relationship object (check for relationship type)
            if (
                hasattr(stix_relationship, "type")
                and stix_relationship.type == "relationship"
            ):
                return stix_relationship
            else:
                logger.debug(
                    f"Parsed object is not a relationship: {type(stix_relationship)}, type: {getattr(stix_relationship, 'type', 'unknown')}"
                )
                return None

        except (STIXError, InvalidValueError, MissingPropertiesError) as e:
            logger.debug(f"STIX2 library failed to parse relationship: {e}")
            raise
        except Exception as e:
            logger.debug(
                f"Unexpected error parsing relationship with STIX2 library: {e}"
            )
            raise

    def _extract_mitre_id_from_stix(self, stix_obj: Dict[str, Any]) -> str:
        """Extract MITRE ID from STIX object external references."""
        external_refs = stix_obj.get("external_references", [])
        for ref in external_refs:
            if ref.get("source_name") == "mitre-attack":
                external_id = ref.get("external_id", "")
                return str(external_id) if external_id else ""
        return ""

    def _process_single_relationship_with_stix2(
        self,
        stix_relationship: STIXRelationshipObject,
        parsed_data: ParsedEntitiesDict,
        stix_id_to_mitre_id: Dict[str, str],
    ) -> None:
        """
        Process a single STIX relationship using STIX2 library object properties.

        Args:
            stix_relationship: STIX2 library Relationship object
            parsed_data: Parsed entities to enhance with relationships
            stix_id_to_mitre_id: Mapping from STIX IDs to MITRE IDs
        """
        # Use STIX2 library's validated property access
        source_ref = stix_relationship.source_ref
        target_ref = stix_relationship.target_ref
        relationship_type = stix_relationship.relationship_type

        source_mitre_id = stix_id_to_mitre_id.get(source_ref, "")
        target_mitre_id = stix_id_to_mitre_id.get(target_ref, "")

        if not source_mitre_id or not target_mitre_id:
            logger.debug(
                f"Skipping relationship {relationship_type}: missing MITRE IDs for {source_ref} -> {target_ref}"
            )
            return

        # Store the relationship for later analysis using STIX2 library properties
        if "relationships" not in parsed_data:
            parsed_data["relationships"] = []

        # Create relationship record with additional STIX2 library properties
        relationship_record = {
            "type": relationship_type,
            "source_ref": source_ref,
            "target_ref": target_ref,
            "source_id": source_mitre_id,
            "target_id": target_mitre_id,
            "created": (
                stix_relationship.created.isoformat()
                if hasattr(stix_relationship, "created")
                else None
            ),
            "modified": (
                stix_relationship.modified.isoformat()
                if hasattr(stix_relationship, "modified")
                else None
            ),
            "id": stix_relationship.id if hasattr(stix_relationship, "id") else None,
        }

        parsed_data["relationships"].append(relationship_record)

        # Handle different relationship types using STIX2 library validated data
        if relationship_type == "uses":
            self._handle_uses_relationship_with_stix2(
                source_mitre_id, target_mitre_id, parsed_data, stix_relationship
            )
        elif relationship_type == "mitigates":
            self._handle_mitigates_relationship_with_stix2(
                source_mitre_id, target_mitre_id, parsed_data, stix_relationship
            )

    def _process_single_relationship_legacy(
        self,
        rel_obj: Dict[str, Any],
        parsed_data: ParsedEntitiesDict,
        stix_id_to_mitre_id: Dict[str, str],
    ) -> None:
        """
        Process a single STIX relationship object using legacy dictionary access.

        This method is kept as a fallback for cases where STIX2 library parsing fails.
        """
        source_ref = rel_obj.get("source_ref", "")
        target_ref = rel_obj.get("target_ref", "")
        relationship_type = rel_obj.get("relationship_type", "")

        source_mitre_id = stix_id_to_mitre_id.get(source_ref, "")
        target_mitre_id = stix_id_to_mitre_id.get(target_ref, "")

        if not source_mitre_id or not target_mitre_id:
            return

        # Store the relationship for later analysis
        if "relationships" not in parsed_data:
            parsed_data["relationships"] = []

        parsed_data["relationships"].append(
            {
                "type": relationship_type,
                "source_ref": source_ref,
                "target_ref": target_ref,
                "source_id": source_mitre_id,
                "target_id": target_mitre_id,
            }
        )

        # Handle different relationship types
        if relationship_type == "uses":
            self._handle_uses_relationship(
                source_mitre_id, target_mitre_id, parsed_data
            )
        elif relationship_type == "mitigates":
            self._handle_mitigates_relationship(
                source_mitre_id, target_mitre_id, parsed_data
            )

    def _handle_uses_relationship_with_stix2(
        self,
        source_id: str,
        target_id: str,
        parsed_data: ParsedEntitiesDict,
        stix_relationship: STIXRelationshipObject,
    ) -> None:
        """
        Handle 'uses' relationships using STIX2 library object properties.

        Args:
            source_id: MITRE ID of the source entity
            target_id: MITRE ID of the target entity
            parsed_data: Parsed entities to enhance with relationships
            stix_relationship: STIX2 library Relationship object with additional metadata
        """
        # Find the source entity (likely a group) and add relationship metadata
        for group in parsed_data.get("groups", []):
            if group["id"] == source_id:
                if "techniques" not in group:
                    group["techniques"] = []
                if target_id not in group["techniques"]:
                    group["techniques"].append(target_id)

                # Add relationship metadata using STIX2 library properties
                if "technique_relationships" not in group:
                    group["technique_relationships"] = {}

                group["technique_relationships"][target_id] = {
                    "relationship_type": stix_relationship.relationship_type,
                    "created": (
                        stix_relationship.created.isoformat()
                        if hasattr(stix_relationship, "created")
                        else None
                    ),
                    "modified": (
                        stix_relationship.modified.isoformat()
                        if hasattr(stix_relationship, "modified")
                        else None
                    ),
                    "confidence": getattr(stix_relationship, "confidence", None),
                }
                break

    def _handle_mitigates_relationship_with_stix2(
        self,
        source_id: str,
        target_id: str,
        parsed_data: ParsedEntitiesDict,
        stix_relationship: STIXRelationshipObject,
    ) -> None:
        """
        Handle 'mitigates' relationships using STIX2 library object properties.

        Args:
            source_id: MITRE ID of the source entity (mitigation)
            target_id: MITRE ID of the target entity (technique)
            parsed_data: Parsed entities to enhance with relationships
            stix_relationship: STIX2 library Relationship object with additional metadata
        """
        # Add mitigation to technique's mitigations list with metadata
        for technique in parsed_data.get("techniques", []):
            if technique["id"] == target_id:
                if "mitigations" not in technique:
                    technique["mitigations"] = []
                if source_id not in technique["mitigations"]:
                    technique["mitigations"].append(source_id)

                # Add relationship metadata using STIX2 library properties
                if "mitigation_relationships" not in technique:
                    technique["mitigation_relationships"] = {}

                technique["mitigation_relationships"][source_id] = {
                    "relationship_type": stix_relationship.relationship_type,
                    "created": (
                        stix_relationship.created.isoformat()
                        if hasattr(stix_relationship, "created")
                        else None
                    ),
                    "modified": (
                        stix_relationship.modified.isoformat()
                        if hasattr(stix_relationship, "modified")
                        else None
                    ),
                    "confidence": getattr(stix_relationship, "confidence", None),
                }
                break

        # Add technique to mitigation's techniques list with metadata
        for mitigation in parsed_data.get("mitigations", []):
            if mitigation["id"] == source_id:
                if "techniques" not in mitigation:
                    mitigation["techniques"] = []
                if target_id not in mitigation["techniques"]:
                    mitigation["techniques"].append(target_id)

                # Add relationship metadata using STIX2 library properties
                if "technique_relationships" not in mitigation:
                    mitigation["technique_relationships"] = {}

                mitigation["technique_relationships"][target_id] = {
                    "relationship_type": stix_relationship.relationship_type,
                    "created": (
                        stix_relationship.created.isoformat()
                        if hasattr(stix_relationship, "created")
                        else None
                    ),
                    "modified": (
                        stix_relationship.modified.isoformat()
                        if hasattr(stix_relationship, "modified")
                        else None
                    ),
                    "confidence": getattr(stix_relationship, "confidence", None),
                }
                break

    def _handle_uses_relationship(
        self, source_id: str, target_id: str, parsed_data: ParsedEntitiesDict
    ) -> None:
        """
        Handle 'uses' relationships using legacy dictionary access.

        This method is kept as a fallback for cases where STIX2 library processing fails.
        """
        # Find the source entity (likely a group)
        for group in parsed_data.get("groups", []):
            if group["id"] == source_id:
                if "techniques" not in group:
                    group["techniques"] = []
                if target_id not in group["techniques"]:
                    group["techniques"].append(target_id)
                break

    def _handle_mitigates_relationship(
        self, source_id: str, target_id: str, parsed_data: ParsedEntitiesDict
    ) -> None:
        """
        Handle 'mitigates' relationships using legacy dictionary access.

        This method is kept as a fallback for cases where STIX2 library processing fails.
        """
        # Add mitigation to technique's mitigations list
        for technique in parsed_data.get("techniques", []):
            if technique["id"] == target_id:
                if "mitigations" not in technique:
                    technique["mitigations"] = []
                if source_id not in technique["mitigations"]:
                    technique["mitigations"].append(source_id)
                break

        # Add technique to mitigation's techniques list
        for mitigation in parsed_data.get("mitigations", []):
            if mitigation["id"] == source_id:
                if "techniques" not in mitigation:
                    mitigation["techniques"] = []
                if target_id not in mitigation["techniques"]:
                    mitigation["techniques"].append(target_id)
                break

    def get_cached_data(
        self, source_name: str
    ) -> Optional[Union[ParsedEntitiesDict, List[RelationshipData]]]:
        """
        Get cached data for a data source.

        Args:
            source_name: Name of the data source

        Returns:
            dict: Cached data, or None if not cached
        """
        return self.data_cache.get(source_name)

    def clear_cache(self, source_name: Optional[str] = None):
        """
        Clear cached data.

        Args:
            source_name: Specific source to clear, or None to clear all
        """
        if source_name:
            self.data_cache.pop(source_name, None)
        else:
            self.data_cache.clear()
