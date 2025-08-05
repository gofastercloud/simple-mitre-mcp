"""
Unit tests for STIX2 library error handling and validation.

Tests comprehensive error handling scenarios including STIXError, InvalidValueError,
MissingPropertiesError, and graceful degradation when STIX objects fail validation.
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import sys
import os
import pytest

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import stix2
from stix2.exceptions import (
    STIXError, 
    InvalidValueError, 
    MissingPropertiesError,
    ExtraPropertiesError,
    ParseError
)

from src.parsers.stix_parser import STIXParser


class TestSTIXErrorHandling(unittest.TestCase):
    """Test cases for STIX2 library error handling and validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = STIXParser()

    def test_stix_error_handling_in_bundle_parsing(self):
        """Test handling of STIXError during bundle parsing."""
        malformed_bundle = {
            "type": "bundle",
            "id": "bundle--invalid-id-format",  # Invalid UUID format
            "objects": []
        }

        with patch('stix2.Bundle') as mock_bundle:
            mock_bundle.side_effect = STIXError("Invalid bundle ID format")
            
            with pytest.raises(STIXError):
                self.parser._parse_stix_bundle_with_validation(malformed_bundle)

    def test_invalid_value_error_handling_in_bundle_parsing(self):
        """Test handling of InvalidValueError during bundle parsing."""
        invalid_bundle = {
            "type": "bundle",
            "id": "bundle--12345678-1234-1234-1234-123456789012",
            "spec_version": "invalid_version",  # Invalid spec version
            "objects": []
        }

        with patch('stix2.Bundle') as mock_bundle:
            mock_bundle.side_effect = InvalidValueError("Bundle", "spec_version", "Invalid version format")
            
            with pytest.raises(InvalidValueError):
                self.parser._parse_stix_bundle_with_validation(invalid_bundle)

    def test_missing_properties_error_handling_in_bundle_parsing(self):
        """Test handling of MissingPropertiesError during bundle parsing."""
        incomplete_bundle = {
            "type": "bundle",
            # Missing required 'id' field
            "objects": []
        }

        # Mock the Bundle constructor to raise MissingPropertiesError
        with patch('src.parsers.stix_parser.Bundle') as mock_bundle:
            # Create a proper MissingPropertiesError with a class object
            from stix2.v21.bundle import Bundle
            mock_bundle.side_effect = MissingPropertiesError(Bundle, ["id"])
            
            with pytest.raises(MissingPropertiesError):
                self.parser._parse_stix_bundle_with_validation(incomplete_bundle)

    def test_graceful_degradation_with_individual_object_errors(self):
        """Test graceful degradation when individual STIX objects fail validation."""
        # Create a bundle with mixed valid and invalid objects
        mixed_bundle = {
            "type": "bundle",
            "id": "bundle--12345678-1234-1234-1234-123456789012",
            "objects": [
                # Valid technique object
                {
                    "type": "attack-pattern",
                    "id": "attack-pattern--12345678-1234-1234-1234-123456789012",
                    "name": "Valid Technique",
                    "description": "A valid technique",
                    "external_references": [
                        {
                            "source_name": "mitre-attack",
                            "external_id": "T1055"
                        }
                    ]
                },
                # Invalid technique object (will cause error)
                {
                    "type": "attack-pattern",
                    "id": "invalid-id-format",  # Invalid ID format
                    "name": "Invalid Technique"
                }
            ]
        }

        # Mock the bundle parsing to succeed but individual object parsing to fail for second object
        with patch.object(self.parser, '_parse_stix_bundle_with_validation') as mock_parse_bundle:
            mock_parse_bundle.return_value = mixed_bundle["objects"]
            
            with patch.object(self.parser, '_extract_entity_from_stix_object_with_validation') as mock_extract:
                # First call succeeds, second call raises STIXError
                mock_extract.side_effect = [
                    {"id": "T1055", "name": "Valid Technique", "description": "A valid technique"},
                    STIXError("Invalid object ID format")
                ]
                
                result = self.parser._parse_with_stix2_library(mixed_bundle, ['techniques'])
                
                # Should have extracted only the valid technique
                self.assertEqual(len(result['techniques']), 1)
                self.assertEqual(result['techniques'][0]['id'], 'T1055')

    def test_stix_error_logging_with_context(self):
        """Test that STIX errors are logged with proper context information."""
        invalid_object = {
            "type": "attack-pattern",
            "id": "attack-pattern--0cbb1c7b-471e-4fee-8f0b-5aaf18906d94",
            "name": "Test Technique"
        }

        with patch('src.parsers.stix_parser.logger') as mock_logger:
            with patch.object(self.parser, '_extract_entity_from_stix_object_with_validation') as mock_extract:
                mock_extract.side_effect = STIXError("Invalid object format")
                
                result = self.parser._parse_with_stix2_library(
                    {"type": "bundle", "id": "bundle--55fe156d-93f5-40bd-9970-86398dc421be", "objects": [invalid_object]}, 
                    ['techniques']
                )
                
                # Verify error was logged with context
                mock_logger.debug.assert_called()
                debug_calls = [call for call in mock_logger.debug.call_args_list if 'STIX format error' in str(call)]
                self.assertTrue(len(debug_calls) > 0)

    def test_invalid_value_error_in_entity_extraction(self):
        """Test handling of InvalidValueError during entity extraction."""
        technique_object = {
            "type": "attack-pattern",
            "id": "attack-pattern--12345678-1234-1234-1234-123456789012",
            "name": "Test Technique",
            "x_mitre_platforms": "invalid_platforms_format"  # Should be list, not string
        }

        with patch.object(self.parser, '_extract_technique_data_from_stix_object_with_validation') as mock_extract:
            mock_extract.side_effect = InvalidValueError("AttackPattern", "x_mitre_platforms", "Expected list")
            
            result = self.parser._extract_entity_from_stix_object_with_validation(technique_object, 'techniques')
            
            # Should return None due to validation error
            self.assertIsNone(result)

    def test_missing_properties_error_in_entity_extraction(self):
        """Test handling of MissingPropertiesError during entity extraction."""
        incomplete_technique = {
            "type": "attack-pattern",
            "id": "attack-pattern--12345678-1234-1234-1234-123456789012",
            # Missing required 'name' field
            "description": "A technique without a name"
        }

        with patch.object(self.parser, '_validate_stix_object_structure', return_value=True):
            result = self.parser._extract_entity_from_stix_object_with_validation(incomplete_technique, 'techniques')
            
            # Should return None due to missing name
            self.assertIsNone(result)

    def test_extra_properties_error_handling(self):
        """Test handling of ExtraPropertiesError during parsing."""
        technique_with_extra_props = {
            "type": "attack-pattern",
            "id": "attack-pattern--f79a4c27-23b4-4a32-a8b9-3b0e8b2c4d5e",
            "name": "Test Technique",
            "description": "A technique with extra properties",
            "custom_property": "not_allowed",  # Extra property
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": "T1055"
                }
            ]
        }

        bundle_data = {
            "type": "bundle",
            "id": "bundle--f79a4c27-23b4-4a32-a8b9-3b0e8b2c4d5e",
            "objects": [technique_with_extra_props]
        }

        with patch.object(self.parser, '_parse_stix_bundle_with_validation') as mock_parse_bundle:
            mock_parse_bundle.return_value = [technique_with_extra_props]
            
            with patch.object(self.parser, '_extract_entity_from_stix_object_with_validation') as mock_extract:
                # Create a proper ExtraPropertiesError with a class object
                from stix2.v21.sdo import AttackPattern
                mock_extract.side_effect = ExtraPropertiesError(AttackPattern, ["custom_property"])
                
                result = self.parser._parse_with_stix2_library(bundle_data, ['techniques'])
                
                # Should handle error gracefully and return empty results
                self.assertEqual(len(result['techniques']), 0)

    def test_parse_error_handling(self):
        """Test handling of ParseError during STIX parsing."""
        malformed_json = {
            "type": "bundle",
            "id": "bundle--12345678-1234-1234-1234-123456789012",
            "objects": [
                {
                    "type": "attack-pattern",
                    "malformed_json": "{"  # Malformed JSON structure
                }
            ]
        }

        with patch.object(self.parser, '_parse_stix_bundle_with_validation') as mock_parse_bundle:
            mock_parse_bundle.return_value = malformed_json["objects"]
            
            with patch.object(self.parser, '_extract_entity_from_stix_object_with_validation') as mock_extract:
                mock_extract.side_effect = ParseError("Malformed JSON in STIX object")
                
                result = self.parser._parse_with_stix2_library(malformed_json, ['techniques'])
                
                # Should handle parse error gracefully
                self.assertEqual(len(result['techniques']), 0)

    def test_error_summary_logging(self):
        """Test that error summary is properly logged with breakdown by error type."""
        bundle_with_various_errors = {
            "type": "bundle",
            "id": "bundle--f79a4c27-23b4-4a32-a8b9-3b0e8b2c4d5e",
            "objects": [
                {"type": "attack-pattern", "id": "1"},  # Will cause STIXError
                {"type": "attack-pattern", "id": "2"},  # Will cause InvalidValueError
                {"type": "attack-pattern", "id": "3"},  # Will cause MissingPropertiesError
                {"type": "attack-pattern", "id": "4"},  # Will cause ExtraPropertiesError
                {"type": "attack-pattern", "id": "5"},  # Will cause ParseError
            ]
        }

        with patch.object(self.parser, '_parse_stix_bundle_with_validation') as mock_parse_bundle:
            mock_parse_bundle.return_value = bundle_with_various_errors["objects"]
            
            with patch.object(self.parser, '_extract_entity_from_stix_object_with_validation') as mock_extract:
                # Create proper STIX error objects with class references
                from stix2.v21.sdo import AttackPattern
                mock_extract.side_effect = [
                    STIXError("STIX format error"),
                    InvalidValueError(AttackPattern, "property", "Invalid value"),
                    MissingPropertiesError(AttackPattern, ["name"]),
                    ExtraPropertiesError(AttackPattern, ["extra_prop"]),
                    ParseError("Parse error")
                ]
                
                with patch('src.parsers.stix_parser.logger') as mock_logger:
                    result = self.parser._parse_with_stix2_library(bundle_with_various_errors, ['techniques'])
                    
                    # Verify error summary was logged
                    info_calls = [call for call in mock_logger.info.call_args_list 
                                 if 'Error breakdown' in str(call)]
                    self.assertTrue(len(info_calls) > 0)

    def test_stix_object_type_extraction_error_handling(self):
        """Test error handling in STIX object type extraction."""
        # Test with None object
        result = self.parser._get_stix_object_type_safely(None)
        self.assertEqual(result, '')

        # Test with object missing type
        invalid_object = {"name": "Test", "description": "No type field"}
        result = self.parser._get_stix_object_type_safely(invalid_object)
        self.assertEqual(result, '')

        # Test with non-string type
        invalid_type_object = {"type": 123, "name": "Test"}
        result = self.parser._get_stix_object_type_safely(invalid_type_object)
        self.assertEqual(result, '')

    def test_stix_object_structure_validation(self):
        """Test STIX object structure validation."""
        # Test with None
        self.assertFalse(self.parser._validate_stix_object_structure(None))

        # Test with valid STIX object
        valid_object = {"type": "attack-pattern", "id": "test-id"}
        self.assertTrue(self.parser._validate_stix_object_structure(valid_object))

        # Test with STIX2 library object
        mock_stix_obj = Mock()
        mock_stix_obj.type = "attack-pattern"
        self.assertTrue(self.parser._validate_stix_object_structure(mock_stix_obj))

        # Test with invalid object
        invalid_object = {"name": "No type field"}
        self.assertFalse(self.parser._validate_stix_object_structure(invalid_object))

    def test_stix_error_details_extraction(self):
        """Test extraction of detailed information from STIX errors."""
        # Test with InvalidValueError - use proper class object
        from stix2.v21.sdo import AttackPattern
        invalid_error = InvalidValueError(AttackPattern, "test_prop", "Invalid value")
        details = self.parser._get_stix_error_details(invalid_error)
        self.assertIn("InvalidValueError", details)

        # Test with MissingPropertiesError - use proper class object
        missing_error = MissingPropertiesError(AttackPattern, ["prop1", "prop2"])
        details = self.parser._get_stix_error_details(missing_error)
        self.assertIn("MissingPropertiesError", details)
        self.assertIn("prop1", details)

        # Test with generic STIXError
        stix_error = STIXError("Generic STIX error")
        details = self.parser._get_stix_error_details(stix_error)
        self.assertIn("STIXError", details)
        self.assertIn("Generic STIX error", details)

    def test_mitre_id_extraction_with_validation_errors(self):
        """Test MITRE ID extraction with various validation errors."""
        # Test with object that has invalid external references structure
        invalid_stix_obj = {
            "external_references": None  # Invalid - should be list
        }
        
        # This should not raise an error but return empty string
        result = self.parser._extract_mitre_id_from_stix_object_with_validation(invalid_stix_obj)
        self.assertEqual(result, '')

        # Test with object that has malformed external references
        malformed_stix_obj = {
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": None  # Invalid - should be string
                }
            ]
        }
        
        result = self.parser._extract_mitre_id_from_stix_object_with_validation(malformed_stix_obj)
        self.assertEqual(result, '')

    def test_comprehensive_error_handling_integration(self):
        """Test comprehensive error handling in a realistic scenario with mixed data."""
        # Mock objects representing different error scenarios
        valid_technique = {
            "type": "attack-pattern",
            "id": "attack-pattern--9aa68173-3078-4ad3-a37a-200823741269",
            "name": "Valid Technique",
            "description": "A properly formatted technique"
        }
        
        invalid_technique_1 = {
            "type": "attack-pattern", 
            "id": "attack-pattern--e5a90081-96bc-4e1d-b44f-3701e6727a97",
            "name": "Invalid Technique 1"
        }
        
        invalid_technique_2 = {
            "type": "attack-pattern",
            "id": "attack-pattern--f094a152-d07c-43fa-b84b-5f3fafe87252",
            "name": "Invalid Technique 2"
        }

        # Mock the bundle parsing to return our test objects
        with patch.object(self.parser, '_parse_stix_bundle_with_validation') as mock_parse_bundle:
            mock_parse_bundle.return_value = [valid_technique, invalid_technique_1, invalid_technique_2]
            
            # Mock entity extraction to simulate different error types
            with patch.object(self.parser, '_extract_entity_from_stix_object_with_validation') as mock_extract:
                # First call succeeds, second and third fail with different errors
                mock_extract.side_effect = [
                    {"id": "T1055", "name": "Valid Technique", "description": "A properly formatted technique"},
                    STIXError("STIX format error"),
                    InvalidValueError(stix2.v21.sdo.AttackPattern, "property", "Invalid value")
                ]
                
                bundle_data = {"type": "bundle", "id": "bundle--34c90093-7826-4441-a345-56ade5141173", "objects": []}
                result = self.parser._parse_with_stix2_library(bundle_data, ['techniques'])
                
                # Should have extracted only the valid technique
                self.assertEqual(len(result['techniques']), 1)
                self.assertEqual(result['techniques'][0]['id'], 'T1055')
                self.assertEqual(result['techniques'][0]['name'], 'Valid Technique')


if __name__ == '__main__':
    unittest.main()