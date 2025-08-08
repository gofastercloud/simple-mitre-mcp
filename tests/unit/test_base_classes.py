"""Test the base test classes and shared utilities."""

import pytest
from tests.base import BaseTestCase, BaseMCPTestCase
from tests.factories import TestDataFactory


class TestBaseTestCase(BaseTestCase):
    """Test the BaseTestCase functionality."""
    
    def test_assert_valid_response(self):
        """Test response validation utility."""
        response = {
            'status': 'success',
            'data': {'test': 'value'},
            'count': 5
        }
        
        # Should not raise any assertion
        self.assert_valid_response(response, ['status', 'data'])
    
    def test_assert_valid_response_missing_key(self):
        """Test response validation with missing key."""
        response = {'status': 'success'}
        
        with pytest.raises(AssertionError, match="Response missing required key: data"):
            self.assert_valid_response(response, ['status', 'data'])
    
    def test_assert_valid_technique(self):
        """Test technique validation utility."""
        technique = TestDataFactory.create_sample_technique()
        
        # Should not raise any assertion
        self.assert_valid_technique(technique)
    
    def test_create_temp_file(self):
        """Test temporary file creation utility."""
        content = '{"test": "data"}'
        temp_file = self.create_temp_file(content)
        
        # Verify file exists and has correct content
        with open(temp_file, 'r') as f:
            assert f.read() == content
        
        # Cleanup
        self.cleanup_temp_file(temp_file)


class TestBaseMCPTestCase(BaseMCPTestCase):
    """Test the BaseMCPTestCase functionality."""
    
    def test_create_mock_technique(self):
        """Test mock technique creation."""
        technique = self.create_mock_technique("T1234", name="Test Technique")
        
        assert technique['id'] == "T1234"
        assert technique['name'] == "Test Technique"
        assert 'description' in technique
        assert 'tactics' in technique
    
    def test_assert_mcp_tool_response(self):
        """Test MCP tool response validation."""
        response = {
            'status': 'success',
            'results': [{'id': 'T1055', 'name': 'Process Injection'}]
        }
        
        # Should not raise any assertion
        self.assert_mcp_tool_response(response, 'test_tool')
    
    def test_assert_mcp_tool_response_with_error(self):
        """Test MCP tool response validation with error."""
        response = {'error': 'Something went wrong'}
        
        with pytest.raises(Exception, match="test_tool returned error"):
            self.assert_mcp_tool_response(response, 'test_tool')


class TestTestDataFactory:
    """Test the TestDataFactory functionality."""
    
    def test_create_sample_technique(self):
        """Test sample technique creation."""
        technique = TestDataFactory.create_sample_technique()
        
        assert technique['type'] == 'attack-pattern'
        assert 'id' in technique
        assert 'name' in technique
        assert 'description' in technique
        assert 'external_references' in technique
    
    def test_create_sample_group(self):
        """Test sample group creation."""
        group = TestDataFactory.create_sample_group()
        
        assert group['type'] == 'intrusion-set'
        assert 'id' in group
        assert 'name' in group
        assert 'description' in group
        assert 'aliases' in group
    
    def test_create_sample_stix_bundle(self):
        """Test STIX bundle creation."""
        entities = [
            TestDataFactory.create_sample_technique(),
            TestDataFactory.create_sample_group()
        ]
        
        bundle = TestDataFactory.create_sample_stix_bundle(entities)
        
        assert bundle['type'] == 'bundle'
        assert 'id' in bundle
        assert len(bundle['objects']) == 2