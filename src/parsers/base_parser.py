"""
Base parser interface for threat intelligence data formats.

This module defines the abstract interface that all data format parsers
must implement to ensure consistent behavior across different formats.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseParser(ABC):
    """
    Abstract base class for threat intelligence data parsers.
    
    All format-specific parsers must inherit from this class and implement
    the required methods to ensure consistent parsing behavior.
    """
    
    @abstractmethod
    def parse(self, raw_data: Dict[str, Any], entity_types: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse raw data and extract specified entity types.
        
        Args:
            raw_data: Raw data in the format-specific structure
            entity_types: List of entity types to extract
            
        Returns:
            dict: Parsed entities organized by type
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement the parse method")
    
    @abstractmethod
    def validate_data(self, raw_data: Dict[str, Any]) -> bool:
        """
        Validate that the raw data is in the expected format.
        
        Args:
            raw_data: Raw data to validate
            
        Returns:
            bool: True if data is valid for this parser
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement the validate_data method")
    
    def get_supported_entity_types(self) -> List[str]:
        """
        Get the list of entity types supported by this parser.
        
        Returns:
            list: List of supported entity type names
        """
        return []
    
    def get_format_name(self) -> str:
        """
        Get the name of the data format handled by this parser.
        
        Returns:
            str: Format name (e.g., 'stix', 'json', 'xml')
        """
        return "unknown"