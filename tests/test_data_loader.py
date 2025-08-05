import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import uuid
from datetime import datetime, timezone
import stix2
from stix2 import Relationship
from stix2.exceptions import STIXError, InvalidValueError, MissingPropertiesError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from src.data_loader import DataLoader
from src.config_loader import load_config

"""
Unit tests for the data loading functionality.

Tests the DataLoader class and related components to ensure proper
functionality for downloading, parsing, and processing MITRE ATT&CK data.
"""


# Add src directory to path


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

    @patch("requests.get")
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

    @patch("requests.get")
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
                {"source_name": "mitre-attack", "external_id": "T1055"},
                {"source_name": "other", "external_id": "OTHER123"},
            ]
        }

        result = self.loader._extract_mitre_id_from_stix(stix_obj)
        self.assertEqual(result, "T1055")

    def test_extract_mitre_id_from_stix_missing(self):
        """Test MITRE ID extraction when not present."""
        stix_obj = {
            "external_references": [{"source_name": "other", "external_id": "OTHER123"}]
        }

        result = self.loader._extract_mitre_id_from_stix(stix_obj)
        self.assertEqual(result, "")

    def test_handle_uses_relationship(self):
        """Test handling of 'uses' relationships."""
        parsed_data = {
            "groups": [{"id": "G0001", "name": "Test Group", "techniques": []}],
            "techniques": [{"id": "T1055", "name": "Test Technique"}],
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
            ],
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

    def test_parse_stix_relationship_success(self):
        """Test successful STIX relationship parsing using STIX2 library."""
        # Create a valid STIX relationship dictionary
        rel_dict = {
            "type": "relationship",
            "id": f"relationship--{uuid.uuid4()}",
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            "relationship_type": "uses",
            "source_ref": f"intrusion-set--{uuid.uuid4()}",
            "target_ref": f"attack-pattern--{uuid.uuid4()}",
        }

        result = self.loader._parse_stix_relationship(rel_dict)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "relationship")
        self.assertEqual(result.relationship_type, "uses")
        self.assertEqual(result.source_ref, rel_dict["source_ref"])
        self.assertEqual(result.target_ref, rel_dict["target_ref"])

    def test_parse_stix_relationship_invalid_data(self):
        """Test STIX relationship parsing with invalid data."""
        # Create an invalid STIX relationship dictionary
        rel_dict = {
            "type": "relationship",
            "relationship_type": "uses",
            "source_ref": "invalid-id",  # Invalid STIX ID format
            "target_ref": f"attack-pattern--{uuid.uuid4()}",
        }

        with self.assertRaises((STIXError, InvalidValueError, MissingPropertiesError)):
            self.loader._parse_stix_relationship(rel_dict)

    def test_parse_stix_relationship_not_relationship(self):
        """Test STIX relationship parsing with non-relationship object."""
        # Create a non-relationship STIX object
        obj_dict = {
            "type": "attack-pattern",
            "id": f"attack-pattern--{uuid.uuid4()}",
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            "name": "Test Technique",
        }

        result = self.loader._parse_stix_relationship(obj_dict)
        self.assertIsNone(result)

    def test_process_single_relationship_with_stix2(self):
        """Test processing a single relationship using STIX2 library object."""
        # Create a STIX2 Relationship object
        source_id = f"intrusion-set--{uuid.uuid4()}"
        target_id = f"attack-pattern--{uuid.uuid4()}"

        stix_relationship = Relationship(
            relationship_type="uses", source_ref=source_id, target_ref=target_id
        )

        # Set up test data
        parsed_data = {
            "groups": [{"id": "G0001", "name": "Test Group", "techniques": []}],
            "techniques": [{"id": "T1055", "name": "Test Technique"}],
        }

        stix_id_to_mitre_id = {source_id: "G0001", target_id: "T1055"}

        # Process the relationship
        self.loader._process_single_relationship_with_stix2(
            stix_relationship, parsed_data, stix_id_to_mitre_id
        )

        # Verify the relationship was processed
        self.assertIn("T1055", parsed_data["groups"][0]["techniques"])
        self.assertIn("relationships", parsed_data)
        self.assertEqual(len(parsed_data["relationships"]), 1)

        relationship_record = parsed_data["relationships"][0]
        self.assertEqual(relationship_record["type"], "uses")
        self.assertEqual(relationship_record["source_id"], "G0001")
        self.assertEqual(relationship_record["target_id"], "T1055")
        self.assertIsNotNone(relationship_record["created"])
        self.assertIsNotNone(relationship_record["id"])

        # Verify relationship metadata was added
        self.assertIn("technique_relationships", parsed_data["groups"][0])
        self.assertIn("T1055", parsed_data["groups"][0]["technique_relationships"])

        rel_metadata = parsed_data["groups"][0]["technique_relationships"]["T1055"]
        self.assertEqual(rel_metadata["relationship_type"], "uses")
        self.assertIsNotNone(rel_metadata["created"])

    def test_handle_uses_relationship_with_stix2(self):
        """Test handling 'uses' relationships with STIX2 library metadata."""
        # Create a STIX2 Relationship object
        stix_relationship = Relationship(
            relationship_type="uses",
            source_ref=f"intrusion-set--{uuid.uuid4()}",
            target_ref=f"attack-pattern--{uuid.uuid4()}",
        )

        parsed_data = {
            "groups": [{"id": "G0001", "name": "Test Group", "techniques": []}]
        }

        self.loader._handle_uses_relationship_with_stix2(
            "G0001", "T1055", parsed_data, stix_relationship
        )

        # Verify the relationship was handled
        self.assertIn("T1055", parsed_data["groups"][0]["techniques"])
        self.assertIn("technique_relationships", parsed_data["groups"][0])
        self.assertIn("T1055", parsed_data["groups"][0]["technique_relationships"])

        rel_metadata = parsed_data["groups"][0]["technique_relationships"]["T1055"]
        self.assertEqual(rel_metadata["relationship_type"], "uses")
        self.assertIsNotNone(rel_metadata["created"])

    def test_handle_mitigates_relationship_with_stix2(self):
        """Test handling 'mitigates' relationships with STIX2 library metadata."""
        # Create a STIX2 Relationship object
        stix_relationship = Relationship(
            relationship_type="mitigates",
            source_ref=f"course-of-action--{uuid.uuid4()}",
            target_ref=f"attack-pattern--{uuid.uuid4()}",
        )

        parsed_data = {
            "techniques": [
                {"id": "T1055", "name": "Test Technique", "mitigations": []}
            ],
            "mitigations": [
                {"id": "M1001", "name": "Test Mitigation", "techniques": []}
            ],
        }

        self.loader._handle_mitigates_relationship_with_stix2(
            "M1001", "T1055", parsed_data, stix_relationship
        )

        # Verify the relationship was handled for technique
        self.assertIn("M1001", parsed_data["techniques"][0]["mitigations"])
        self.assertIn("mitigation_relationships", parsed_data["techniques"][0])
        self.assertIn("M1001", parsed_data["techniques"][0]["mitigation_relationships"])

        technique_rel_metadata = parsed_data["techniques"][0][
            "mitigation_relationships"
        ]["M1001"]
        self.assertEqual(technique_rel_metadata["relationship_type"], "mitigates")
        self.assertIsNotNone(technique_rel_metadata["created"])

        # Verify the relationship was handled for mitigation
        self.assertIn("T1055", parsed_data["mitigations"][0]["techniques"])
        self.assertIn("technique_relationships", parsed_data["mitigations"][0])
        self.assertIn("T1055", parsed_data["mitigations"][0]["technique_relationships"])

        mitigation_rel_metadata = parsed_data["mitigations"][0][
            "technique_relationships"
        ]["T1055"]
        self.assertEqual(mitigation_rel_metadata["relationship_type"], "mitigates")
        self.assertIsNotNone(mitigation_rel_metadata["created"])

    def test_process_relationships_with_stix2_library(self):
        """Test complete relationship processing using STIX2 library."""
        # Create test STIX data with relationships
        source_id = f"intrusion-set--{uuid.uuid4()}"
        target_id = f"attack-pattern--{uuid.uuid4()}"
        mitigation_id = f"course-of-action--{uuid.uuid4()}"

        raw_data = {
            "objects": [
                {
                    "type": "intrusion-set",
                    "id": source_id,
                    "name": "Test Group",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "G0001"}
                    ],
                },
                {
                    "type": "attack-pattern",
                    "id": target_id,
                    "name": "Test Technique",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "T1055"}
                    ],
                },
                {
                    "type": "course-of-action",
                    "id": mitigation_id,
                    "name": "Test Mitigation",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "M1001"}
                    ],
                },
                {
                    "type": "relationship",
                    "id": f"relationship--{uuid.uuid4()}",
                    "created": "2023-01-01T00:00:00.000Z",
                    "modified": "2023-01-01T00:00:00.000Z",
                    "relationship_type": "uses",
                    "source_ref": source_id,
                    "target_ref": target_id,
                },
                {
                    "type": "relationship",
                    "id": f"relationship--{uuid.uuid4()}",
                    "created": "2023-01-01T00:00:00.000Z",
                    "modified": "2023-01-01T00:00:00.000Z",
                    "relationship_type": "mitigates",
                    "source_ref": mitigation_id,
                    "target_ref": target_id,
                },
            ]
        }

        parsed_data = {
            "groups": [{"id": "G0001", "name": "Test Group", "techniques": []}],
            "techniques": [
                {"id": "T1055", "name": "Test Technique", "mitigations": []}
            ],
            "mitigations": [
                {"id": "M1001", "name": "Test Mitigation", "techniques": []}
            ],
        }

        result = self.loader._process_relationships(raw_data, parsed_data)

        # Verify relationships were processed
        self.assertIn("relationships", result)
        self.assertEqual(len(result["relationships"]), 2)

        # Verify uses relationship
        self.assertIn("T1055", result["groups"][0]["techniques"])
        self.assertIn("technique_relationships", result["groups"][0])

        # Verify mitigates relationship
        self.assertIn("M1001", result["techniques"][0]["mitigations"])
        self.assertIn("T1055", result["mitigations"][0]["techniques"])
        self.assertIn("mitigation_relationships", result["techniques"][0])
        self.assertIn("technique_relationships", result["mitigations"][0])

    def test_process_relationships_fallback_to_legacy(self):
        """Test relationship processing falls back to legacy method when STIX2 parsing fails."""
        # Create test data with invalid STIX relationship that will cause parsing to fail
        raw_data = {
            "objects": [
                {
                    "type": "intrusion-set",
                    "id": "intrusion-set--valid-uuid",
                    "name": "Test Group",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "G0001"}
                    ],
                },
                {
                    "type": "attack-pattern",
                    "id": "attack-pattern--valid-uuid",
                    "name": "Test Technique",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "T1055"}
                    ],
                },
                {
                    "type": "relationship",
                    "relationship_type": "uses",
                    "source_ref": "intrusion-set--valid-uuid",
                    "target_ref": "attack-pattern--valid-uuid",
                    # Missing required fields like 'id', 'created', 'modified' to trigger STIX2 parsing failure
                },
            ]
        }

        parsed_data = {
            "groups": [{"id": "G0001", "name": "Test Group", "techniques": []}],
            "techniques": [
                {"id": "T1055", "name": "Test Technique", "mitigations": []}
            ],
        }

        # This should not raise an exception and should fall back to legacy processing
        result = self.loader._process_relationships(raw_data, parsed_data)

        # Verify the relationship was still processed using legacy method
        self.assertIn("T1055", result["groups"][0]["techniques"])
        self.assertIn("relationships", result)
        self.assertEqual(len(result["relationships"]), 1)


class TestConfigLoader(unittest.TestCase):
    """Test cases for configuration loading."""

    def test_load_config(self):
        """Test configuration loading."""
        config = load_config()

        # Check required sections
        self.assertIn("data_sources", config)
        self.assertIn("entity_schemas", config)

        # Check MITRE ATT&CK data source
        self.assertIn("mitre_attack", config["data_sources"])
        mitre_config = config["data_sources"]["mitre_attack"]
        self.assertIn("url", mitre_config)
        self.assertIn("format", mitre_config)
        self.assertIn("entity_types", mitre_config)

        # Check entity schemas
        expected_schemas = ["tactic", "technique", "group", "mitigation"]
        for schema in expected_schemas:
            self.assertIn(schema, config["entity_schemas"])


if __name__ == "__main__":
    unittest.main()
