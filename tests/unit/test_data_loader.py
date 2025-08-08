"""
Unit tests for the data loading functionality.

Tests the DataLoader class and related components to ensure proper
functionality for downloading, parsing, and processing MITRE ATT&CK data.
"""

import pytest
import uuid
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import stix2
from stix2 import Relationship
from stix2.exceptions import STIXError, InvalidValueError, MissingPropertiesError

from src.data_loader import DataLoader
from src.config_loader import load_config
from tests.base import BaseMCPTestCase


class TestDataLoader(BaseMCPTestCase):
    """Test cases for the DataLoader class."""

    @pytest.fixture
    def data_loader(self):
        """Create a DataLoader instance for testing."""
        return DataLoader()

    def test_init(self, data_loader):
        """Test DataLoader initialization."""
        assert data_loader.config is not None
        assert isinstance(data_loader.data_cache, dict)
        assert data_loader.stix_parser is not None

    @patch("requests.get")
    def test_download_data_success(self, mock_get, data_loader):
        """Test successful data download."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = data_loader.download_data("http://example.com/data.json")

        assert result == {"test": "data"}
        mock_get.assert_called_once_with("http://example.com/data.json", timeout=30)

    @patch("requests.get")
    def test_download_data_failure(self, mock_get, data_loader):
        """Test data download failure."""
        # Mock failed response
        mock_get.side_effect = Exception("Network error")

        with pytest.raises(Exception):
            data_loader.download_data("http://example.com/data.json")

    def test_extract_mitre_id_from_stix(self, data_loader):
        """Test MITRE ID extraction from STIX object."""
        stix_obj = {
            "external_references": [
                {"source_name": "mitre-attack", "external_id": "T1055"},
                {"source_name": "other", "external_id": "OTHER123"},
            ]
        }

        result = data_loader._extract_mitre_id_from_stix(stix_obj)
        assert result == "T1055"

    def test_extract_mitre_id_from_stix_missing(self, data_loader):
        """Test MITRE ID extraction when not present."""
        stix_obj = {
            "external_references": [{"source_name": "other", "external_id": "OTHER123"}]
        }

        result = data_loader._extract_mitre_id_from_stix(stix_obj)
        assert result == ""

    def test_handle_uses_relationship(self, data_loader):
        """Test handling of 'uses' relationships."""
        parsed_data = {
            "groups": [{"id": "G0001", "name": "Test Group", "techniques": []}],
            "techniques": [{"id": "T1055", "name": "Test Technique"}],
        }

        data_loader._handle_uses_relationship("G0001", "T1055", parsed_data)

        assert "T1055" in parsed_data["groups"][0]["techniques"]

    def test_handle_mitigates_relationship(self, data_loader):
        """Test handling of 'mitigates' relationships."""
        parsed_data = {
            "techniques": [
                {"id": "T1055", "name": "Test Technique", "mitigations": []}
            ],
            "mitigations": [
                {"id": "M1001", "name": "Test Mitigation", "techniques": []}
            ],
        }

        data_loader._handle_mitigates_relationship("M1001", "T1055", parsed_data)

        assert "M1001" in parsed_data["techniques"][0]["mitigations"]
        assert "T1055" in parsed_data["mitigations"][0]["techniques"]

    def test_get_cached_data(self, data_loader):
        """Test cached data retrieval."""
        # Set up cache
        test_data = {"tactics": [], "techniques": []}
        data_loader.data_cache["test_source"] = test_data

        result = data_loader.get_cached_data("test_source")
        assert result == test_data

        # Test missing cache
        result = data_loader.get_cached_data("missing_source")
        assert result is None

    def test_clear_cache(self, data_loader):
        """Test cache clearing."""
        # Set up cache
        data_loader.data_cache["source1"] = {"data": "test1"}
        data_loader.data_cache["source2"] = {"data": "test2"}

        # Clear specific source
        data_loader.clear_cache("source1")
        assert "source1" not in data_loader.data_cache
        assert "source2" in data_loader.data_cache

        # Clear all
        data_loader.clear_cache()
        assert len(data_loader.data_cache) == 0

    def test_parse_stix_relationship_success(self, data_loader):
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

        result = data_loader._parse_stix_relationship(rel_dict)

        assert result is not None
        assert result.type == "relationship"
        assert result.relationship_type == "uses"
        assert result.source_ref == rel_dict["source_ref"]
        assert result.target_ref == rel_dict["target_ref"]

    def test_parse_stix_relationship_invalid_data(self, data_loader):
        """Test STIX relationship parsing with invalid data."""
        # Create an invalid STIX relationship dictionary
        rel_dict = {
            "type": "relationship",
            "relationship_type": "uses",
            "source_ref": "invalid-id",  # Invalid STIX ID format
            "target_ref": f"attack-pattern--{uuid.uuid4()}",
        }

        with pytest.raises((STIXError, InvalidValueError, MissingPropertiesError)):
            data_loader._parse_stix_relationship(rel_dict)

    def test_parse_stix_relationship_not_relationship(self, data_loader):
        """Test STIX relationship parsing with non-relationship object."""
        # Create a non-relationship STIX object
        obj_dict = {
            "type": "attack-pattern",
            "id": f"attack-pattern--{uuid.uuid4()}",
            "created": "2023-01-01T00:00:00.000Z",
            "modified": "2023-01-01T00:00:00.000Z",
            "name": "Test Technique",
        }

        result = data_loader._parse_stix_relationship(obj_dict)
        assert result is None

    def test_process_single_relationship_with_stix2(self, data_loader):
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
        data_loader._process_single_relationship_with_stix2(
            stix_relationship, parsed_data, stix_id_to_mitre_id
        )

        # Verify the relationship was processed
        assert "T1055" in parsed_data["groups"][0]["techniques"]
        assert "relationships" in parsed_data
        assert len(parsed_data["relationships"]) == 1

        relationship_record = parsed_data["relationships"][0]
        assert relationship_record["type"] == "uses"
        assert relationship_record["source_id"] == "G0001"
        assert relationship_record["target_id"] == "T1055"
        assert relationship_record["created"] is not None
        assert relationship_record["id"] is not None

        # Verify relationship metadata was added
        assert "technique_relationships" in parsed_data["groups"][0]
        assert "T1055" in parsed_data["groups"][0]["technique_relationships"]

        rel_metadata = parsed_data["groups"][0]["technique_relationships"]["T1055"]
        assert rel_metadata["relationship_type"] == "uses"
        assert rel_metadata["created"] is not None

    def test_handle_uses_relationship_with_stix2(self, data_loader):
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

        data_loader._handle_uses_relationship_with_stix2(
            "G0001", "T1055", parsed_data, stix_relationship
        )

        # Verify the relationship was handled
        assert "T1055" in parsed_data["groups"][0]["techniques"]
        assert "technique_relationships" in parsed_data["groups"][0]
        assert "T1055" in parsed_data["groups"][0]["technique_relationships"]

        rel_metadata = parsed_data["groups"][0]["technique_relationships"]["T1055"]
        assert rel_metadata["relationship_type"] == "uses"
        assert rel_metadata["created"] is not None

    def test_handle_mitigates_relationship_with_stix2(self, data_loader):
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

        data_loader._handle_mitigates_relationship_with_stix2(
            "M1001", "T1055", parsed_data, stix_relationship
        )

        # Verify the relationship was handled for technique
        assert "M1001" in parsed_data["techniques"][0]["mitigations"]
        assert "mitigation_relationships" in parsed_data["techniques"][0]
        assert "M1001" in parsed_data["techniques"][0]["mitigation_relationships"]

        technique_rel_metadata = parsed_data["techniques"][0][
            "mitigation_relationships"
        ]["M1001"]
        assert technique_rel_metadata["relationship_type"] == "mitigates"
        assert technique_rel_metadata["created"] is not None

        # Verify the relationship was handled for mitigation
        assert "T1055" in parsed_data["mitigations"][0]["techniques"]
        assert "technique_relationships" in parsed_data["mitigations"][0]
        assert "T1055" in parsed_data["mitigations"][0]["technique_relationships"]

        mitigation_rel_metadata = parsed_data["mitigations"][0][
            "technique_relationships"
        ]["T1055"]
        assert mitigation_rel_metadata["relationship_type"] == "mitigates"
        assert mitigation_rel_metadata["created"] is not None

    def test_process_relationships_with_stix2_library(self, data_loader):
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

        result = data_loader._process_relationships(raw_data, parsed_data)

        # Verify relationships were processed
        assert "relationships" in result
        assert len(result["relationships"]) == 2

        # Verify uses relationship
        assert "T1055" in result["groups"][0]["techniques"]
        assert "technique_relationships" in result["groups"][0]

        # Verify mitigates relationship
        assert "M1001" in result["techniques"][0]["mitigations"]
        assert "T1055" in result["mitigations"][0]["techniques"]
        assert "mitigation_relationships" in result["techniques"][0]
        assert "technique_relationships" in result["mitigations"][0]

    def test_process_relationships_error_handling(self, data_loader):
        """Test relationship processing handles malformed relationships gracefully."""
        # Create test data with malformed STIX relationship
        raw_data = {
            "objects": [
                {
                    "type": "intrusion-set",
                    "id": f"intrusion-set--{uuid.uuid4()}",
                    "name": "Test Group",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "G0001"}
                    ],
                },
                {
                    "type": "attack-pattern",
                    "id": f"attack-pattern--{uuid.uuid4()}",
                    "name": "Test Technique",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "T1055"}
                    ],
                },
                {
                    "type": "relationship",
                    "id": f"relationship--{uuid.uuid4()}",
                    "relationship_type": "uses",
                    "source_ref": "intrusion-set--nonexistent",  # Reference to non-existent object
                    "target_ref": f"attack-pattern--{uuid.uuid4()}",
                    "created": "2020-01-01T00:00:00.000Z",
                    "modified": "2020-01-01T00:00:00.000Z",
                },
            ]
        }

        parsed_data = {
            "groups": [{"id": "G0001", "name": "Test Group", "techniques": []}],
            "techniques": [
                {"id": "T1055", "name": "Test Technique", "mitigations": []}
            ],
        }

        # This should process successfully and handle invalid relationships gracefully
        result = data_loader._process_relationships(raw_data, parsed_data)

        # Verify basic structure is maintained even with invalid relationships
        assert "groups" in result
        assert "techniques" in result
        assert result["groups"][0]["id"] == "G0001"
        assert result["techniques"][0]["id"] == "T1055"


class TestConfigLoader(BaseMCPTestCase):
    """Test cases for configuration loading."""

    def test_load_config(self):
        """Test configuration loading."""
        config = load_config()

        # Check required sections
        assert "data_sources" in config
        assert "entity_schemas" in config

        # Check MITRE ATT&CK data source
        assert "mitre_attack" in config["data_sources"]
        mitre_config = config["data_sources"]["mitre_attack"]
        assert "url" in mitre_config
        assert "format" in mitre_config
        assert "entity_types" in mitre_config

        # Check entity schemas
        expected_schemas = ["tactic", "technique", "group", "mitigation"]
        for schema in expected_schemas:
            assert schema in config["entity_schemas"]


if __name__ == "__main__":
    pytest.main([__file__])