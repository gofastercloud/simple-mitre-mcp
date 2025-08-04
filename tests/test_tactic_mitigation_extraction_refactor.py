"""
Tests for tactic and mitigation extraction refactoring to use STIX2 library.

This module contains unit tests that compare the old (legacy) and new (STIX2 library-based)
extraction methods for tactics and mitigations to ensure backward compatibility.
"""

import pytest
import logging
from unittest.mock import patch, Mock
from src.parsers.stix_parser import STIXParser
import stix2
from stix2.exceptions import STIXError, InvalidValueError, MissingPropertiesError


class TestTacticMitigationExtractionRefactor:
    """Test cases for tactic and mitigation extraction refactoring."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.parser = STIXParser()
        
        # Sample tactic STIX object (x-mitre-tactic)
        self.sample_tactic_stix = {
            "type": "x-mitre-tactic",
            "id": "x-mitre-tactic--ffd5bcee-6e16-4dd2-8eca-7b3beedf33ca",
            "created": "2018-10-17T00:14:20.652Z",
            "modified": "2019-07-19T17:43:41.967Z",
            "name": "Initial Access",
            "description": "The adversary is trying to get into your network. Initial Access consists of techniques that use various entry vectors to gain their initial foothold within a network.",
            "x_mitre_shortname": "initial-access",
            "object_marking_refs": [
                "marking-definition--fa42a846-8d90-4e51-bc29-71d5b4802168"
            ],
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": "TA0001",
                    "url": "https://attack.mitre.org/tactics/TA0001"
                }
            ]
        }
        
        # Sample mitigation STIX object (course-of-action)
        self.sample_mitigation_stix = {
            "type": "course-of-action",
            "id": "course-of-action--90f39ee1-d5a3-4aaa-9f28-3b42815b0d46",
            "created": "2018-10-17T00:14:20.652Z",
            "modified": "2020-03-25T23:10:26.506Z",
            "name": "Behavior Prevention on Endpoint",
            "description": "Use capabilities to prevent suspicious behavior patterns from occurring on endpoint systems. This could include suspicious process, file, API call, etc. behavior.",
            "x_mitre_version": "1.0",
            "x_mitre_deprecated": False,
            "object_marking_refs": [
                "marking-definition--fa42a846-8d90-4e51-bc29-71d5b4802168"
            ],
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": "M1040",
                    "url": "https://attack.mitre.org/mitigations/M1040"
                }
            ]
        }

    def test_tactic_extraction_comparison(self):
        """Test that new STIX2 library-based tactic extraction produces identical output to legacy method."""
        # Test legacy method
        legacy_result = self.parser._extract_tactic_data_legacy(self.sample_tactic_stix)
        
        # Test new STIX2 library-based method
        stix2_result = self.parser._extract_tactic_data(self.sample_tactic_stix)
        
        # Results should be identical
        assert legacy_result == stix2_result
        
        # Both should return empty dict for tactics (only basic fields)
        assert legacy_result == {}
        assert stix2_result == {}

    def test_mitigation_extraction_comparison(self):
        """Test that new STIX2 library-based mitigation extraction produces identical output to legacy method."""
        # Test legacy method
        legacy_result = self.parser._extract_mitigation_data_legacy(self.sample_mitigation_stix)
        
        # Test new STIX2 library-based method
        stix2_result = self.parser._extract_mitigation_data(self.sample_mitigation_stix)
        
        # Results should be identical
        assert legacy_result == stix2_result
        
        # Both should return dict with empty techniques list
        expected_result = {'techniques': []}
        assert legacy_result == expected_result
        assert stix2_result == expected_result

    def test_tactic_extraction_with_stix2_library_object(self):
        """Test tactic extraction directly with STIX2 library object."""
        # Create STIX2 library object
        stix2_obj = stix2.parse(self.sample_tactic_stix, allow_custom=True)
        
        # Test extraction from STIX2 library object
        result = self.parser._extract_tactic_data_from_stix_object(stix2_obj)
        
        # Should return empty dict for tactics
        assert result == {}

    def test_mitigation_extraction_with_stix2_library_object(self):
        """Test mitigation extraction directly with STIX2 library object."""
        # Create STIX2 library object
        stix2_obj = stix2.parse(self.sample_mitigation_stix, allow_custom=True)
        
        # Test extraction from STIX2 library object
        result = self.parser._extract_mitigation_data_from_stix_object(stix2_obj)
        
        # Should return dict with empty techniques list
        expected_result = {'techniques': []}
        assert result == expected_result

    def test_tactic_extraction_fallback_on_stix2_error(self):
        """Test that tactic extraction falls back to legacy method when STIX2 parsing fails."""
        # Mock stix2.parse to raise an exception
        with patch('stix2.parse') as mock_parse, patch('src.parsers.stix_parser.logger') as mock_logger:
            mock_parse.side_effect = STIXError("Mocked STIX parsing error")
            
            malformed_stix = {
                "type": "x-mitre-tactic",
                "id": "test-id",
                "name": "Test Tactic"
            }
            
            result = self.parser._extract_tactic_data(malformed_stix)
            
            # Should still return empty dict (fallback behavior)
            assert result == {}
            
            # Should have logged the fallback
            mock_logger.debug.assert_called()
            debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
            assert any("STIX2 library parsing failed for tactic" in call for call in debug_calls)

    def test_mitigation_extraction_fallback_on_stix2_error(self):
        """Test that mitigation extraction falls back to legacy method when STIX2 parsing fails."""
        # Create malformed STIX object that will cause STIX2 parsing to fail
        malformed_stix = {
            "type": "course-of-action",
            "id": "invalid-id-format",  # Invalid ID format
            "name": "Test Mitigation"
            # Missing required fields
        }
        
        with patch('src.parsers.stix_parser.logger') as mock_logger:
            result = self.parser._extract_mitigation_data(malformed_stix)
            
            # Should still return dict with empty techniques list (fallback behavior)
            expected_result = {'techniques': []}
            assert result == expected_result
            
            # Should have logged the fallback
            mock_logger.debug.assert_called()
            debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
            assert any("STIX2 library parsing failed for mitigation" in call for call in debug_calls)

    def test_tactic_extraction_minimal_data(self):
        """Test tactic extraction with minimal STIX data."""
        minimal_tactic = {
            "type": "x-mitre-tactic",
            "id": "x-mitre-tactic--test",
            "name": "Test Tactic",
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": "TA9999"
                }
            ]
        }
        
        # Test both methods
        legacy_result = self.parser._extract_tactic_data_legacy(minimal_tactic)
        stix2_result = self.parser._extract_tactic_data(minimal_tactic)
        
        # Results should be identical
        assert legacy_result == stix2_result
        assert legacy_result == {}

    def test_mitigation_extraction_minimal_data(self):
        """Test mitigation extraction with minimal STIX data."""
        minimal_mitigation = {
            "type": "course-of-action",
            "id": "course-of-action--test",
            "name": "Test Mitigation",
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": "M9999"
                }
            ]
        }
        
        # Test both methods
        legacy_result = self.parser._extract_mitigation_data_legacy(minimal_mitigation)
        stix2_result = self.parser._extract_mitigation_data(minimal_mitigation)
        
        # Results should be identical
        expected_result = {'techniques': []}
        assert legacy_result == stix2_result
        assert legacy_result == expected_result

    def test_tactic_extraction_with_extra_fields(self):
        """Test tactic extraction with additional STIX fields."""
        tactic_with_extras = self.sample_tactic_stix.copy()
        tactic_with_extras.update({
            "x_mitre_version": "1.0",
            "x_mitre_deprecated": False,
            "created_by_ref": "identity--c78cb6e5-0c4b-4611-8297-d1b8b55e40b5"
        })
        
        # Test both methods
        legacy_result = self.parser._extract_tactic_data_legacy(tactic_with_extras)
        stix2_result = self.parser._extract_tactic_data(tactic_with_extras)
        
        # Results should be identical (extra fields ignored)
        assert legacy_result == stix2_result
        assert legacy_result == {}

    def test_mitigation_extraction_with_extra_fields(self):
        """Test mitigation extraction with additional STIX fields."""
        mitigation_with_extras = self.sample_mitigation_stix.copy()
        mitigation_with_extras.update({
            "x_mitre_domains": ["enterprise-attack"],
            "created_by_ref": "identity--c78cb6e5-0c4b-4611-8297-d1b8b55e40b5"
        })
        
        # Test both methods
        legacy_result = self.parser._extract_mitigation_data_legacy(mitigation_with_extras)
        stix2_result = self.parser._extract_mitigation_data(mitigation_with_extras)
        
        # Results should be identical (extra fields ignored)
        expected_result = {'techniques': []}
        assert legacy_result == stix2_result
        assert legacy_result == expected_result

    def test_integration_with_full_parsing_workflow(self):
        """Test tactic and mitigation extraction within the full parsing workflow."""
        # Create sample STIX bundle with tactic and mitigation
        stix_bundle = {
            "type": "bundle",
            "id": "bundle--test",
            "objects": [
                self.sample_tactic_stix,
                self.sample_mitigation_stix
            ]
        }
        
        # Parse using the full workflow
        result = self.parser.parse(stix_bundle, ['tactics', 'mitigations'])
        
        # Verify results
        assert 'tactics' in result
        assert 'mitigations' in result
        
        # Check tactic
        assert len(result['tactics']) == 1
        tactic = result['tactics'][0]
        assert tactic['id'] == 'TA0001'
        assert tactic['name'] == 'Initial Access'
        assert 'description' in tactic
        
        # Check mitigation
        assert len(result['mitigations']) == 1
        mitigation = result['mitigations'][0]
        assert mitigation['id'] == 'M1040'
        assert mitigation['name'] == 'Behavior Prevention on Endpoint'
        assert 'description' in mitigation
        assert mitigation['techniques'] == []

    def test_error_handling_in_stix2_library_methods(self):
        """Test error handling in STIX2 library-based extraction methods."""
        # Test with None object
        result = self.parser._extract_tactic_data_from_stix_object(None)
        assert result == {}
        
        result = self.parser._extract_mitigation_data_from_stix_object(None)
        assert result == {'techniques': []}
        
        # Test with invalid object
        invalid_obj = {"invalid": "object"}
        result = self.parser._extract_tactic_data_from_stix_object(invalid_obj)
        assert result == {}
        
        result = self.parser._extract_mitigation_data_from_stix_object(invalid_obj)
        assert result == {'techniques': []}

    def test_stix2_library_object_type_validation(self):
        """Test that STIX2 library objects are properly validated."""
        # Create proper STIX2 library objects
        tactic_obj = stix2.parse(self.sample_tactic_stix, allow_custom=True)
        mitigation_obj = stix2.parse(self.sample_mitigation_stix, allow_custom=True)
        
        # Verify object types (STIX2 library may return dicts for custom objects)
        if hasattr(tactic_obj, 'type'):
            assert tactic_obj.type == "x-mitre-tactic"
        else:
            assert tactic_obj.get('type') == "x-mitre-tactic"
            
        if hasattr(mitigation_obj, 'type'):
            assert mitigation_obj.type == "course-of-action"
        else:
            assert mitigation_obj.get('type') == "course-of-action"
        
        # Test extraction with proper objects
        tactic_result = self.parser._extract_tactic_data_from_stix_object(tactic_obj)
        mitigation_result = self.parser._extract_mitigation_data_from_stix_object(mitigation_obj)
        
        assert tactic_result == {}
        assert mitigation_result == {'techniques': []}

    def test_backward_compatibility_with_existing_tests(self):
        """Test that refactored methods maintain compatibility with existing test expectations."""
        # This test ensures that the refactored methods still work with existing test data
        # and produce the expected results for the MCP tools
        
        # Test data similar to what's used in existing tests
        test_tactic = {
            "type": "x-mitre-tactic",
            "id": "x-mitre-tactic--test",
            "name": "Execution",
            "description": "The adversary is trying to run malicious code.",
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": "TA0002"
                }
            ]
        }
        
        test_mitigation = {
            "type": "course-of-action",
            "id": "course-of-action--test",
            "name": "Execution Prevention",
            "description": "Block execution of code on a system.",
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": "M1038"
                }
            ]
        }
        
        # Test extraction
        tactic_result = self.parser._extract_tactic_data(test_tactic)
        mitigation_result = self.parser._extract_mitigation_data(test_mitigation)
        
        # Verify expected format for existing tests
        assert tactic_result == {}  # Tactics only have basic fields
        assert mitigation_result == {'techniques': []}  # Mitigations have techniques list


if __name__ == '__main__':
    pytest.main([__file__])