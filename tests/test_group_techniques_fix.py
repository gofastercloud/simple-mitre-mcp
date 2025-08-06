"""
Test for the group techniques fix to ensure S-prefixed software IDs are not included.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.data_loader import DataLoader


class TestGroupTechniquesFix:
    """Test the fix for group techniques showing S-prefixed software IDs."""

    @pytest.fixture
    def data_loader(self):
        """Create a data loader instance."""
        return DataLoader()

    @pytest.fixture
    def loaded_data(self, data_loader):
        """Load MITRE ATT&CK data for testing."""
        return data_loader.load_data_source("mitre_attack")

    def test_group_techniques_only_contain_t_prefixed_ids(self, loaded_data):
        """Test that group techniques only contain T-prefixed technique IDs."""
        groups = loaded_data.get("groups", [])
        assert len(groups) > 0, "No groups found in loaded data"

        # Check all groups for proper technique ID filtering
        for group in groups:
            group_id = group.get("id", "")
            techniques = group.get("techniques", [])

            # All technique IDs should start with 'T'
            s_prefixed = [t for t in techniques if t.startswith("S")]
            t_prefixed = [t for t in techniques if t.startswith("T")]

            assert (
                len(s_prefixed) == 0
            ), f"Group {group_id} contains S-prefixed IDs (software/malware): {s_prefixed[:5]}"

            # If there are techniques, they should all be T-prefixed
            if techniques:
                assert len(t_prefixed) == len(techniques), (
                    f"Group {group_id} has non-T-prefixed technique IDs: "
                    f"{[t for t in techniques if not t.startswith('T')]}"
                )

    def test_apt29_specific_fix(self, loaded_data):
        """Test the specific APT29 case that was reported."""
        groups = loaded_data.get("groups", [])

        # Find APT29 (G0016)
        apt29 = None
        for group in groups:
            if group.get("id") == "G0016":
                apt29 = group
                break

        assert apt29 is not None, "APT29 (G0016) not found in loaded data"

        techniques = apt29.get("techniques", [])
        assert len(techniques) > 0, "APT29 should have techniques"

        # All techniques should be T-prefixed
        s_prefixed = [t for t in techniques if t.startswith("S")]
        t_prefixed = [t for t in techniques if t.startswith("T")]

        assert (
            len(s_prefixed) == 0
        ), f"APT29 still contains S-prefixed IDs: {s_prefixed}"
        assert len(t_prefixed) == len(
            techniques
        ), "Not all APT29 techniques are T-prefixed"

        # The count should be reasonable (less than the original 115 that included software)
        assert (
            len(techniques) < 100
        ), f"APT29 technique count seems too high: {len(techniques)}"
        assert (
            len(techniques) > 30
        ), f"APT29 technique count seems too low: {len(techniques)}"

    def test_techniques_can_be_resolved(self, loaded_data):
        """Test that all group techniques can be resolved in the techniques list."""
        groups = loaded_data.get("groups", [])
        techniques_list = loaded_data.get("techniques", [])

        # Create a lookup set for technique IDs
        technique_ids = {tech.get("id") for tech in techniques_list}

        # Check a few major groups
        test_groups = ["G0016", "G0007", "G0032"]  # APT29, APT1, APT28

        for group_id in test_groups:
            group = None
            for g in groups:
                if g.get("id") == group_id:
                    group = g
                    break

            if not group:
                continue  # Skip if group not found

            group_techniques = group.get("techniques", [])

            # All group techniques should be resolvable
            unresolvable = [t for t in group_techniques if t not in technique_ids]

            assert (
                len(unresolvable) == 0
            ), f"Group {group_id} has unresolvable technique IDs: {unresolvable[:5]}"

    def test_no_name_not_found_in_resolved_techniques(self, loaded_data):
        """Test that resolved techniques don't have '(Name not found)' entries."""
        groups = loaded_data.get("groups", [])
        techniques_list = loaded_data.get("techniques", [])

        # Create a lookup dict for technique details
        technique_lookup = {tech.get("id"): tech for tech in techniques_list}

        # Test APT29 specifically
        apt29 = None
        for group in groups:
            if group.get("id") == "G0016":
                apt29 = group
                break

        if apt29:
            group_techniques = apt29.get("techniques", [])

            for tech_id in group_techniques:
                tech_info = technique_lookup.get(tech_id)
                assert (
                    tech_info is not None
                ), f"Technique {tech_id} not found in techniques list"

                tech_name = tech_info.get("name", "")
                assert (
                    tech_name != "(Name not found)"
                ), f"Technique {tech_id} has '(Name not found)'"
                assert tech_name != "", f"Technique {tech_id} has empty name"
                assert (
                    "not available" not in tech_name.lower()
                ), f"Technique {tech_id} has placeholder name: {tech_name}"
