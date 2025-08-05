"""
Unit tests for enhanced MITRE ID extraction using STIX2 library validation.

Tests the refactored _extract_mitre_id_from_stix_object() method to ensure
it uses STIX2 library validation, handles edge cases, and maintains
backward compatibility.
"""

import pytest
import uuid
from unittest.mock import Mock, patch

import stix2
from stix2.exceptions import STIXError, InvalidValueError, MissingPropertiesError

from src.parsers.stix_parser import STIXParser


class TestMitreIdExtractionEnhancement:
    """Test enhanced MITRE ID extraction with STIX2 library validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = STIXParser()

    def test_extract_mitre_id_from_valid_stix2_object(self):
        """Test MITRE ID extraction from valid STIX2 library object."""
        # Create a valid STIX2 AttackPattern object
        technique = stix2.AttackPattern(
            name='Test Technique',
            external_references=[
                stix2.ExternalReference(
                    source_name='mitre-attack',
                    external_id='T1234'
                ),
                stix2.ExternalReference(
                    source_name='other-source',
                    external_id='OTHER-123'
                )
            ]
        )
        
        result = self.parser._extract_mitre_id_from_stix_object(technique)
        assert result == 'T1234'

    def test_extract_mitre_id_from_valid_dictionary(self):
        """Test MITRE ID extraction from valid dictionary (fallback)."""
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T1234'
                },
                {
                    'source_name': 'other-source',
                    'external_id': 'OTHER-123'
                }
            ]
        }
        
        result = self.parser._extract_mitre_id_from_stix_object(stix_dict)
        assert result == 'T1234'

    def test_extract_mitre_id_multiple_mitre_references(self):
        """Test extraction when multiple MITRE references exist (should return first valid)."""
        technique = stix2.AttackPattern(
            name='Test Technique',
            external_references=[
                stix2.ExternalReference(
                    source_name='other-source',
                    external_id='OTHER-123'
                ),
                stix2.ExternalReference(
                    source_name='mitre-attack',
                    external_id='T1234'
                ),
                stix2.ExternalReference(
                    source_name='mitre-attack',
                    external_id='T5678'
                )
            ]
        )
        
        result = self.parser._extract_mitre_id_from_stix_object(technique)
        assert result == 'T1234'

    def test_extract_mitre_id_no_mitre_references(self):
        """Test extraction when no MITRE references exist."""
        technique = stix2.AttackPattern(
            name='Test Technique',
            external_references=[
                stix2.ExternalReference(
                    source_name='other-source',
                    external_id='OTHER-123'
                ),
                stix2.ExternalReference(
                    source_name='another-source',
                    external_id='ANOTHER-456'
                )
            ]
        )
        
        result = self.parser._extract_mitre_id_from_stix_object(technique)
        assert result == ''

    def test_extract_mitre_id_empty_external_references(self):
        """Test extraction when external_references is empty."""
        technique = stix2.AttackPattern(
            name='Test Technique',
            external_references=[]
        )
        
        result = self.parser._extract_mitre_id_from_stix_object(technique)
        assert result == ''

    def test_extract_mitre_id_missing_external_references(self):
        """Test extraction when external_references property is missing."""
        # Create a dictionary without external_references
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique'
        }
        
        result = self.parser._extract_mitre_id_from_stix_object(stix_dict)
        assert result == ''

    def test_extract_mitre_id_invalid_external_references_type(self):
        """Test extraction when external_references is not a list."""
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': 'not-a-list'
        }
        
        result = self.parser._extract_mitre_id_from_stix_object(stix_dict)
        assert result == ''

    def test_extract_mitre_id_malformed_reference_dict(self):
        """Test extraction with malformed external reference dictionary."""
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': [
                'not-a-dict',
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T1234'
                }
            ]
        }
        
        result = self.parser._extract_mitre_id_from_stix_object(stix_dict)
        assert result == 'T1234'

    def test_extract_mitre_id_missing_source_name(self):
        """Test extraction when source_name is missing."""
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': [
                {
                    'external_id': 'T1234'
                },
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T5678'
                }
            ]
        }
        
        result = self.parser._extract_mitre_id_from_stix_object(stix_dict)
        assert result == 'T5678'

    def test_extract_mitre_id_missing_external_id(self):
        """Test extraction when external_id is missing."""
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': [
                {
                    'source_name': 'mitre-attack'
                },
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T1234'
                }
            ]
        }
        
        result = self.parser._extract_mitre_id_from_stix_object(stix_dict)
        assert result == 'T1234'

    def test_extract_mitre_id_empty_source_name(self):
        """Test extraction when source_name is empty string."""
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': [
                {
                    'source_name': '',
                    'external_id': 'T1234'
                },
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T5678'
                }
            ]
        }
        
        result = self.parser._extract_mitre_id_from_stix_object(stix_dict)
        assert result == 'T5678'

    def test_extract_mitre_id_empty_external_id(self):
        """Test extraction when external_id is empty string."""
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': ''
                },
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T1234'
                }
            ]
        }
        
        result = self.parser._extract_mitre_id_from_stix_object(stix_dict)
        assert result == 'T1234'

    def test_validate_mitre_id_format_valid_technique(self):
        """Test MITRE ID format validation for valid technique IDs."""
        assert self.parser._validate_mitre_id_format('T1234') == True
        assert self.parser._validate_mitre_id_format('T1234.001') == True
        assert self.parser._validate_mitre_id_format('T9999.999') == True

    def test_validate_mitre_id_format_valid_group(self):
        """Test MITRE ID format validation for valid group IDs."""
        assert self.parser._validate_mitre_id_format('G0001') == True
        assert self.parser._validate_mitre_id_format('G9999') == True

    def test_validate_mitre_id_format_valid_tactic(self):
        """Test MITRE ID format validation for valid tactic IDs."""
        assert self.parser._validate_mitre_id_format('TA0001') == True
        assert self.parser._validate_mitre_id_format('TA9999') == True

    def test_validate_mitre_id_format_valid_mitigation(self):
        """Test MITRE ID format validation for valid mitigation IDs."""
        assert self.parser._validate_mitre_id_format('M1001') == True
        assert self.parser._validate_mitre_id_format('M9999') == True

    def test_validate_mitre_id_format_invalid_ids(self):
        """Test MITRE ID format validation for invalid IDs."""
        assert self.parser._validate_mitre_id_format('') == False
        assert self.parser._validate_mitre_id_format('T123') == False  # Too short
        assert self.parser._validate_mitre_id_format('T12345') == False  # Too long
        assert self.parser._validate_mitre_id_format('T1234.01') == False  # Sub-technique too short
        assert self.parser._validate_mitre_id_format('T1234.0001') == False  # Sub-technique too long
        assert self.parser._validate_mitre_id_format('X1234') == False  # Invalid prefix
        assert self.parser._validate_mitre_id_format('t1234') == False  # Lowercase
        assert self.parser._validate_mitre_id_format('T1234.') == False  # Trailing dot
        assert self.parser._validate_mitre_id_format('T1234.abc') == False  # Non-numeric sub-technique
        assert self.parser._validate_mitre_id_format(None) == False  # None value
        assert self.parser._validate_mitre_id_format(123) == False  # Non-string

    def test_extract_mitre_id_invalid_format_rejected(self):
        """Test that invalid MITRE ID formats are rejected."""
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'INVALID-ID'
                },
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T1234'
                }
            ]
        }
        
        result = self.parser._extract_mitre_id_from_stix_object(stix_dict)
        assert result == 'T1234'

    def test_extract_mitre_id_stix_error_handling(self):
        """Test handling of STIX library errors."""
        # Create a mock STIX object that raises STIXError when accessing external_references
        mock_stix_obj = Mock()
        
        # Mock hasattr to return True so we try to access the property
        with patch('builtins.hasattr', return_value=True):
            # Create a property that raises STIXError when accessed
            def raise_stix_error():
                raise STIXError("Test STIX error")
            
            # Set up the mock to raise STIXError when external_references is accessed
            type(mock_stix_obj).external_references = property(lambda self: raise_stix_error())
            
            with pytest.raises(STIXError):
                self.parser._extract_mitre_id_from_stix_object(mock_stix_obj)

    def test_extract_mitre_id_invalid_value_error_handling(self):
        """Test handling of InvalidValueError from STIX library."""
        # Test with a malformed STIX object that could cause InvalidValueError
        # This tests the error handling path in the method
        malformed_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T1234'
                }
            ]
        }
        
        # Mock the _validate_mitre_id_format to raise InvalidValueError with proper arguments
        with patch.object(self.parser, '_validate_mitre_id_format', 
                         side_effect=InvalidValueError("TestClass", "external_id", "Invalid format")):
            # The method should handle the error gracefully and return empty string
            result = self.parser._extract_mitre_id_from_stix_object(malformed_dict)
            assert result == ''

    def test_extract_mitre_id_backward_compatibility_legacy_method(self):
        """Test that legacy _extract_mitre_id method maintains compatibility."""
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T1234'
                }
            ]
        }
        
        # Test both methods produce same result
        legacy_result = self.parser._extract_mitre_id(stix_dict)
        enhanced_result = self.parser._extract_mitre_id_from_stix_object(stix_dict)
        
        assert legacy_result == enhanced_result == 'T1234'

    def test_extract_mitre_id_legacy_method_validation(self):
        """Test that legacy method now includes validation."""
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'INVALID-ID'
                },
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T1234'
                }
            ]
        }
        
        result = self.parser._extract_mitre_id(stix_dict)
        assert result == 'T1234'

    def test_extract_mitre_id_legacy_method_error_handling(self):
        """Test error handling in legacy method."""
        # Test with invalid external_references type
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': 'not-a-list'
        }
        
        result = self.parser._extract_mitre_id(stix_dict)
        assert result == ''

    def test_extract_mitre_id_all_entity_types(self):
        """Test MITRE ID extraction for all entity types."""
        test_cases = [
            ('T1234', 'attack-pattern'),
            ('T1234.001', 'attack-pattern'),
            ('G0001', 'intrusion-set'),
            ('TA0001', 'x-mitre-tactic'),
            ('M1001', 'course-of-action')
        ]
        
        for mitre_id, stix_type in test_cases:
            stix_dict = {
                'type': stix_type,
                'name': f'Test {stix_type}',
                'external_references': [
                    {
                        'source_name': 'mitre-attack',
                        'external_id': mitre_id
                    }
                ]
            }
            
            result = self.parser._extract_mitre_id_from_stix_object(stix_dict)
            assert result == mitre_id, f"Failed for {stix_type} with ID {mitre_id}"

    def test_extract_mitre_id_unicode_handling(self):
        """Test handling of Unicode characters in external references."""
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'T1234',
                    'description': 'Test with Unicode: 中文 русский العربية'
                }
            ]
        }
        
        result = self.parser._extract_mitre_id_from_stix_object(stix_dict)
        assert result == 'T1234'

    def test_extract_mitre_id_case_sensitivity(self):
        """Test case sensitivity in source_name matching."""
        stix_dict = {
            'type': 'attack-pattern',
            'name': 'Test Technique',
            'external_references': [
                {
                    'source_name': 'MITRE-ATTACK',  # Wrong case
                    'external_id': 'T1234'
                },
                {
                    'source_name': 'mitre-attack',  # Correct case
                    'external_id': 'T5678'
                }
            ]
        }
        
        result = self.parser._extract_mitre_id_from_stix_object(stix_dict)
        assert result == 'T5678'