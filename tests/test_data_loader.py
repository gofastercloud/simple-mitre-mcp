"""
Unit tests for the data loading functionality.

Tests the DataLoader class and related components to ensure proper
functionality for downloading, parsing, and processing MITRE ATT&CK data.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import DataLoader
from config_loader import load_config


class TestDataLoader(unittest.TestCase):
    """Test cases for the DataLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = DataLoader()

    def test_init(self):
        """Test DataLoader initialization."""
        self.assertIsNotNone(self.loader.config)
        self.assertIsInstance(self.loader.data_cache, dict)
        self.assertIsNotNone(self.loader.stix_parser)

    @patch('requests.get')
    def test_download_data_success(self, mock_get):
        """Test successful data download."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.loader.download_data("http://example.com/data.json")

        self.assertEqual(result, {"test": "data"})
        mock_get.assert_called_once_with("http://example.com/data.json", timeout=30)

    @patch('requests.get')
    def test_download_data_failure(self, mock_get):
        """Test data download failure."""
        # Mock failed response
        mock_get.side_effect = Exception("Network error")

        with self.assertRaises(Exception):
            self.loader.download_data("http://example.com/data.json")

    def test_extract_mitre_id_from_stix(self):
        """Test MITRE ID extraction from STIX object."""
        stix_obj = {
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": "T1055"
                },
                {
                    "source_name": "other",
                    "external_id": "OTHER123"
                }
            ]
        }

        result = self.loader._extract_mitre_id_from_stix(stix_obj)
        self.assertEqual(result, "T1055")

    def test_extract_mitre_id_from_stix_missing(self):
        """Test MITRE ID extraction when not present."""
        stix_obj = {
            "external_references": [
                {
                    "source_name": "other",
                    "external_id": "OTHER123"
                }
            ]
        }

        result = self.loader._extract_mitre_id_from_stix(stix_obj)
        self.assertEqual(result, "")

    def test_handle_uses_relationship(self):
        """Test handling of 'uses' relationships."""
        parsed_data = {
            "groups": [
                {"id": "G0001", "name": "Test Group", "techniques": []}
            ],
            "techniques": [
                {"id": "T1055", "name": "Test Technique"}
            ]
        }

        self.loader._handle_uses_relationship("G0001", "T1055", parsed_data)

        self.assertIn("T1055", parsed_data["groups"][0]["techniques"])

    def test_handle_mitigates_relationship(self):
        """Test handling of 'mitigates' relationships."""
        parsed_data = {
            "techniques": [
                {"id": "T1055", "name": "Test Technique", "mitigations": []}
            ],
            "mitigations": [
                {"id": "M1001", "name": "Test Mitigation", "techniques": []}
            ]
        }

        self.loader._handle_mitigates_relationship("M1001", "T1055", parsed_data)

        self.assertIn("M1001", parsed_data["techniques"][0]["mitigations"])
        self.assertIn("T1055", parsed_data["mitigations"][0]["techniques"])

    def test_get_cached_data(self):
        """Test cached data retrieval."""
        # Set up cache
        test_data = {"tactics": [], "techniques": []}
        self.loader.data_cache["test_source"] = test_data

        result = self.loader.get_cached_data("test_source")
        self.assertEqual(result, test_data)

        # Test missing cache
        result = self.loader.get_cached_data("missing_source")
        self.assertIsNone(result)

    def test_clear_cache(self):
        """Test cache clearing."""
        # Set up cache
        self.loader.data_cache["source1"] = {"data": "test1"}
        self.loader.data_cache["source2"] = {"data": "test2"}

        # Clear specific source
        self.loader.clear_cache("source1")
        self.assertNotIn("source1", self.loader.data_cache)
        self.assertIn("source2", self.loader.data_cache)

        # Clear all
        self.loader.clear_cache()
        self.assertEqual(len(self.loader.data_cache), 0)


class TestConfigLoader(unittest.TestCase):
    """Test cases for configuration loading."""

    def test_load_config(self):
        """Test configuration loading."""
        config = load_config()

        # Check required sections
        self.assertIn('data_sources', config)
        self.assertIn('entity_schemas', config)

        # Check MITRE ATT&CK data source
        self.assertIn('mitre_attack', config['data_sources'])
        mitre_config = config['data_sources']['mitre_attack']
        self.assertIn('url', mitre_config)
        self.assertIn('format', mitre_config)
        self.assertIn('entity_types', mitre_config)

        # Check entity schemas
        expected_schemas = ['tactic', 'technique', 'group', 'mitigation']
        for schema in expected_schemas:
            self.assertIn(schema, config['entity_schemas'])


if __name__ == '__main__':
    unittest.main()
