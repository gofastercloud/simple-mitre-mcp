"""
Tests for group extraction refactoring to use STIX2 library objects.

This module tests the refactored group extraction functionality to ensure
backward compatibility while leveraging the official STIX2 library.
"""

import pytest
import stix2
from src.parsers.stix_parser import STIXParser


class TestGroupExtractionRefactor:
    """Test group extraction refactoring with STIX2 library objects."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = STIXParser()

    def test_group_extraction_with_aliases(self):
        """Test group extraction with aliases using STIX2 library."""
        # Create test data as dictionary (simulating legacy input)
        group_dict = {
            'type': 'intrusion-set',
            'id': 'intrusion-set--f40eb8ce-2a74-4e56-89a1-227021410142',
            'name': 'APT1',
            'description': 'APT1 is a threat group',
            'aliases': ['APT1', 'Comment Crew', 'PLA Unit 61398'],
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'G0006'
                }
            ]
        }

        # Test the refactored method
        result = self.parser._extract_group_data(group_dict)

        # Verify the output format matches expectations
        assert isinstance(result, dict)
        assert 'aliases' in result
        assert 'techniques' in result
        
        # Verify aliases are properly filtered (primary name excluded)
        assert 'Comment Crew' in result['aliases']
        assert 'PLA Unit 61398' in result['aliases']
        assert 'APT1' not in result['aliases']  # Primary name should be filtered out
        
        # Verify techniques list is initialized
        assert result['techniques'] == []

    def test_group_extraction_without_aliases(self):
        """Test group extraction without aliases."""
        group_dict = {
            'type': 'intrusion-set',
            'id': 'intrusion-set--simple-group',
            'name': 'Simple Group',
            'description': 'Group without aliases',
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'G9999'
                }
            ]
        }

        result = self.parser._extract_group_data(group_dict)

        # Should handle missing aliases gracefully
        assert 'aliases' not in result
        assert result['techniques'] == []

    def test_group_extraction_empty_aliases(self):
        """Test group extraction with empty aliases list."""
        group_dict = {
            'type': 'intrusion-set',
            'id': 'intrusion-set--empty-aliases',
            'name': 'Empty Aliases Group',
            'description': 'Group with empty aliases',
            'aliases': [],
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'G8888'
                }
            ]
        }

        result = self.parser._extract_group_data(group_dict)

        # Should handle empty aliases gracefully
        assert 'aliases' not in result
        assert result['techniques'] == []

    def test_group_extraction_aliases_only_primary_name(self):
        """Test group extraction where aliases only contains the primary name."""
        group_dict = {
            'type': 'intrusion-set',
            'id': 'intrusion-set--primary-only',
            'name': 'Primary Only Group',
            'description': 'Group where aliases only contains primary name',
            'aliases': ['Primary Only Group'],
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'G7777'
                }
            ]
        }

        result = self.parser._extract_group_data(group_dict)

        # Should filter out primary name, leaving no aliases
        assert 'aliases' not in result
        assert result['techniques'] == []

    def test_group_extraction_mixed_aliases(self):
        """Test group extraction with mixed aliases including primary name."""
        group_dict = {
            'type': 'intrusion-set',
            'id': 'intrusion-set--mixed-aliases',
            'name': 'Mixed Group',
            'description': 'Group with mixed aliases',
            'aliases': ['Mixed Group', 'Alternative Name', 'Another Alias', 'Mixed Group'],
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'G6666'
                }
            ]
        }

        result = self.parser._extract_group_data(group_dict)

        # Should filter out all instances of primary name
        assert 'aliases' in result
        assert 'Alternative Name' in result['aliases']
        assert 'Another Alias' in result['aliases']
        assert 'Mixed Group' not in result['aliases']
        assert len(result['aliases']) == 2
        assert result['techniques'] == []

    def test_group_extraction_fallback_to_legacy(self):
        """Test fallback to legacy parsing when STIX2 library parsing fails."""
        # Create malformed data that might cause STIX2 library to fail
        malformed_group = {
            'type': 'intrusion-set',
            # Missing required 'id' field to trigger STIX2 library error
            'name': 'Malformed Group',
            'description': 'Group with malformed data',
            'aliases': ['Malformed Group', 'Bad Data Group'],
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'G5555'
                }
            ]
        }

        # Should still work via fallback mechanism
        result = self.parser._extract_group_data(malformed_group)

        assert isinstance(result, dict)
        assert 'aliases' in result
        assert 'Bad Data Group' in result['aliases']
        assert 'Malformed Group' not in result['aliases']
        assert result['techniques'] == []

    def test_compare_old_vs_new_extraction_output(self):
        """Compare output between old legacy method and new STIX2 library method."""
        group_dict = {
            'type': 'intrusion-set',
            'id': 'intrusion-set--comparison-test',
            'name': 'Comparison Group',
            'description': 'Group for comparing extraction methods',
            'aliases': ['Comparison Group', 'Test Group', 'Legacy Group'],
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'G4444'
                }
            ]
        }

        # Get results from both methods
        new_result = self.parser._extract_group_data(group_dict)
        legacy_result = self.parser._extract_group_data_legacy(group_dict)

        # Results should be identical
        assert new_result == legacy_result
        assert set(new_result['aliases']) == set(legacy_result['aliases'])
        assert new_result['techniques'] == legacy_result['techniques']

    def test_group_extraction_with_stix2_object_directly(self):
        """Test that the method works with STIX2 library objects directly."""
        # Create a STIX2 IntrusionSet object
        group = stix2.IntrusionSet(
            name="Direct STIX2 Group",
            description="Group created as STIX2 object",
            aliases=["Direct STIX2 Group", "STIX2 Test", "Library Group"],
            external_references=[
                stix2.ExternalReference(
                    source_name="mitre-attack",
                    external_id="G3333"
                )
            ]
        )

        # Convert to dictionary format (simulating how it would come from JSON)
        group_dict = dict(group)

        result = self.parser._extract_group_data(group_dict)

        assert 'aliases' in result
        assert 'STIX2 Test' in result['aliases']
        assert 'Library Group' in result['aliases']
        assert 'Direct STIX2 Group' not in result['aliases']
        assert result['techniques'] == []

    def test_group_extraction_error_handling(self):
        """Test error handling in group extraction."""
        # Test with completely invalid data
        invalid_data = {
            'invalid_field': 'invalid_value'
        }

        # Should handle gracefully and return empty result
        result = self.parser._extract_group_data(invalid_data)

        assert isinstance(result, dict)
        assert result['techniques'] == []
        # Should not have aliases since none were provided
        assert 'aliases' not in result

    def test_group_extraction_maintains_backward_compatibility(self):
        """Test that refactored method maintains backward compatibility."""
        # Test various edge cases that the original method handled
        test_cases = [
            # Normal case with aliases
            {
                'type': 'intrusion-set',
                'id': 'intrusion-set--f40eb8ce-2a74-4e56-89a1-227021410141',
                'name': 'Normal Group',
                'aliases': ['Normal Group', 'Alias1', 'Alias2'],
                'external_references': [{'source_name': 'mitre-attack', 'external_id': 'G1111'}]
            },
            # Case with no aliases field
            {
                'type': 'intrusion-set',
                'id': 'intrusion-set--f40eb8ce-2a74-4e56-89a1-227021410142',
                'name': 'No Aliases Group',
                'external_references': [{'source_name': 'mitre-attack', 'external_id': 'G2222'}]
            },
            # Case with None aliases
            {
                'type': 'intrusion-set',
                'id': 'intrusion-set--f40eb8ce-2a74-4e56-89a1-227021410143',
                'name': 'None Aliases Group',
                'aliases': None,
                'external_references': [{'source_name': 'mitre-attack', 'external_id': 'G3333'}]
            }
        ]

        for i, test_case in enumerate(test_cases):
            # Test both methods produce same result
            try:
                new_result = self.parser._extract_group_data(test_case)
                legacy_result = self.parser._extract_group_data_legacy(test_case)
                
                # Results should be equivalent
                assert new_result == legacy_result, f"Test case {i} failed: {test_case}"
                
            except Exception as e:
                pytest.fail(f"Test case {i} raised exception: {e}")

    def test_group_extraction_with_unicode_aliases(self):
        """Test group extraction with Unicode characters in aliases."""
        group_dict = {
            'type': 'intrusion-set',
            'id': 'intrusion-set--unicode-test',
            'name': 'Unicode Group',
            'description': 'Group with Unicode aliases',
            'aliases': ['Unicode Group', '中文别名', 'Русский псевдоним', 'العربية'],
            'external_references': [
                {
                    'source_name': 'mitre-attack',
                    'external_id': 'G9998'
                }
            ]
        }

        result = self.parser._extract_group_data(group_dict)

        assert 'aliases' in result
        assert '中文别名' in result['aliases']
        assert 'Русский псевдоним' in result['aliases']
        assert 'العربية' in result['aliases']
        assert 'Unicode Group' not in result['aliases']
        assert result['techniques'] == []