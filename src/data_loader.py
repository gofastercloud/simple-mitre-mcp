"""
Generic data loading and parsing framework for threat intelligence sources.

This module provides functionality to download, parse, and store threat intelligence
data from various sources in a configuration-driven manner.
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional
from src.config_loader import load_config
from src.parsers.stix_parser import STIXParser

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Generic data loader for threat intelligence frameworks.

    Supports configuration-driven loading of data from various sources
    and formats, with pluggable parsers for different data formats.
    """

    def __init__(self):
        """Initialize the data loader with configuration."""
        self.config = load_config()
        self.data_cache: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
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
        logger.info("Downloading data from: {url}")

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            data = response.json()
            logger.info("Successfully downloaded {len(str(data))} bytes of data")
            return data

        except requests.RequestException as e:
            logger.error("Failed to download data from {url}: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON from {url}: {e}")
            raise

    def load_data_source(self, source_name: str) -> Dict[str, List[Dict[str, Any]]]:
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
        if source_name not in self.config['data_sources']:
            raise ValueError("Data source '{source_name}' not found in configuration")

        source_config = self.config['data_sources'][source_name]

        # Download raw data
        raw_data = self.download_data(source_config['url'])

        # Parse data based on format
        if source_config['format'] == 'stix':
            parsed_data = self.stix_parser.parse(raw_data, source_config['entity_types'])
            # Process relationships between entities
            parsed_data = self._process_relationships(raw_data, parsed_data)
        else:
            raise ValueError("Unsupported data format: {source_config['format']}")

        # Cache the parsed data
        self.data_cache[source_name] = parsed_data

        # Also cache raw relationships for advanced analysis
        raw_relationships = [obj for obj in raw_data.get('objects', []) if obj.get('type') == 'relationship']
        self.data_cache["{source_name}_relationships"] = raw_relationships

        logger.info("Successfully loaded data source '{source_name}'")
        for entity_type, entities in parsed_data.items():
            logger.info("  {entity_type}: {len(entities)} entities")

        return parsed_data

    def _process_relationships(self, raw_data: Dict[str, Any], parsed_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Process STIX relationships to populate entity connections.

        Args:
            raw_data: Original STIX data containing relationship objects
            parsed_data: Parsed entities to enhance with relationships

        Returns:
            dict: Enhanced parsed data with relationships populated
        """
        logger.info("Processing entity relationships")

        # Create lookup maps for entities by their STIX IDs
        entity_lookup = {}
        stix_id_to_mitre_id = {}

        # Build lookup maps from the raw STIX data
        for obj in raw_data.get('objects', []):
            stix_id = obj.get('id', '')
            if not stix_id:
                continue

            # Get MITRE ID for this object
            mitre_id = self._extract_mitre_id_from_stix(obj)
            if mitre_id:
                stix_id_to_mitre_id[stix_id] = mitre_id
                entity_lookup[stix_id] = obj

        # Process relationship objects
        relationships_processed = 0
        for obj in raw_data.get('objects', []):
            if obj.get('type') == 'relationship':
                self._process_single_relationship(obj, parsed_data, stix_id_to_mitre_id)
                relationships_processed += 1

        logger.info("Processed {relationships_processed} relationship objects")
        return parsed_data

    def _extract_mitre_id_from_stix(self, stix_obj: Dict[str, Any]) -> str:
        """Extract MITRE ID from STIX object external references."""
        external_refs = stix_obj.get('external_references', [])
        for ref in external_refs:
            if ref.get('source_name') == 'mitre-attack':
                return ref.get('external_id', '')
        return ''

    def _process_single_relationship(self, rel_obj: Dict[str, Any], parsed_data: Dict[str, List[Dict[str, Any]]], stix_id_to_mitre_id: Dict[str, str]):
        """Process a single STIX relationship object."""
        source_ref = rel_obj.get('source_re', '')
        target_ref = rel_obj.get('target_re', '')
        relationship_type = rel_obj.get('relationship_type', '')

        source_mitre_id = stix_id_to_mitre_id.get(source_ref, '')
        target_mitre_id = stix_id_to_mitre_id.get(target_ref, '')

        if not source_mitre_id or not target_mitre_id:
            return

        # Handle different relationship types
        if relationship_type == 'uses':
            self._handle_uses_relationship(source_mitre_id, target_mitre_id, parsed_data)
        elif relationship_type == 'mitigates':
            self._handle_mitigates_relationship(source_mitre_id, target_mitre_id, parsed_data)

    def _handle_uses_relationship(self, source_id: str, target_id: str, parsed_data: Dict[str, List[Dict[str, Any]]]):
        """Handle 'uses' relationships (e.g., group uses technique)."""
        # Find the source entity (likely a group)
        for group in parsed_data.get('groups', []):
            if group['id'] == source_id:
                if 'techniques' not in group:
                    group['techniques'] = []
                if target_id not in group['techniques']:
                    group['techniques'].append(target_id)
                break

    def _handle_mitigates_relationship(self, source_id: str, target_id: str, parsed_data: Dict[str, List[Dict[str, Any]]]):
        """Handle 'mitigates' relationships (mitigation mitigates technique)."""
        # Add mitigation to technique's mitigations list
        for technique in parsed_data.get('techniques', []):
            if technique['id'] == target_id:
                if 'mitigations' not in technique:
                    technique['mitigations'] = []
                if source_id not in technique['mitigations']:
                    technique['mitigations'].append(source_id)
                break

        # Add technique to mitigation's techniques list
        for mitigation in parsed_data.get('mitigations', []):
            if mitigation['id'] == source_id:
                if 'techniques' not in mitigation:
                    mitigation['techniques'] = []
                if target_id not in mitigation['techniques']:
                    mitigation['techniques'].append(target_id)
                break

    def get_cached_data(self, source_name: str) -> Optional[Dict[str, List[Dict[str, Any]]]]:
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
