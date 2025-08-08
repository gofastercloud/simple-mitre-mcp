"""Test data factories for creating consistent test data across the test suite."""

import json
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class TestDataFactory:
    """Factory for creating consistent test data for MITRE ATT&CK entities."""
    
    @staticmethod
    def create_sample_technique(
        technique_id: str = "T1055",
        name: Optional[str] = None,
        **overrides
    ) -> Dict[str, Any]:
        """Create sample technique data.
        
        Args:
            technique_id: The technique ID (e.g., "T1055")
            name: Optional technique name
            **overrides: Additional fields to override
            
        Returns:
            Dictionary representing a technique
        """
        if name is None:
            name = f"Process Injection {technique_id}"
        
        technique = {
            "type": "attack-pattern",
            "id": f"attack-pattern--{TestDataFactory._generate_uuid()}",
            "created": "2017-05-31T21:30:19.735Z",
            "modified": "2023-04-14T16:46:06.044Z",
            "name": name,
            "description": f"Adversaries may inject code into processes in order to evade process-based defenses as well as possibly elevate privileges. Process injection is a method of executing arbitrary code in the address space of a separate live process. Running code in the context of another process may allow access to the process's memory, system/network resources, and possibly elevated privileges. Execution via process injection may also evade detection from security products since the execution is masked under a legitimate process. This is test data for {technique_id}.",
            "kill_chain_phases": [
                {
                    "kill_chain_name": "mitre-attack",
                    "phase_name": "defense-evasion"
                },
                {
                    "kill_chain_name": "mitre-attack", 
                    "phase_name": "privilege-escalation"
                }
            ],
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "url": f"https://attack.mitre.org/techniques/{technique_id}",
                    "external_id": technique_id
                }
            ],
            "object_marking_refs": [
                "marking-definition--fa42a846-8d90-4e51-bc29-71d5b4802168"
            ],
            "x_mitre_attack_spec_version": "3.1.0",
            "x_mitre_data_sources": [
                "Process: Process Access",
                "Process: Process Modification",
                "Process: OS API Execution"
            ],
            "x_mitre_detection": "Monitoring Windows API calls indicative of the various types of code injection may generate a significant amount of data and may not be directly actionable.",
            "x_mitre_domains": ["enterprise-attack"],
            "x_mitre_is_subtechnique": False,
            "x_mitre_platforms": ["Linux", "macOS", "Windows"],
            "x_mitre_version": "1.3"
        }
        
        technique.update(overrides)
        return technique
    
    @staticmethod
    def create_sample_group(
        group_id: str = "G0016",
        name: Optional[str] = None,
        **overrides
    ) -> Dict[str, Any]:
        """Create sample group data.
        
        Args:
            group_id: The group ID (e.g., "G0016")
            name: Optional group name
            **overrides: Additional fields to override
            
        Returns:
            Dictionary representing a threat group
        """
        if name is None:
            name = f"APT29 {group_id}"
        
        group = {
            "type": "intrusion-set",
            "id": f"intrusion-set--{TestDataFactory._generate_uuid()}",
            "created": "2017-05-31T21:31:52.748Z",
            "modified": "2023-03-22T03:18:53.462Z",
            "name": name,
            "description": f"[{name}](https://attack.mitre.org/groups/{group_id}) is threat group that has been attributed to Russia's Foreign Intelligence Service (SVR). This is test data for {group_id}.",
            "aliases": [name, "YTTRIUM", "The Dukes", "Cozy Bear"],
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "url": f"https://attack.mitre.org/groups/{group_id}",
                    "external_id": group_id
                }
            ],
            "object_marking_refs": [
                "marking-definition--fa42a846-8d90-4e51-bc29-71d5b4802168"
            ],
            "x_mitre_attack_spec_version": "3.1.0",
            "x_mitre_domains": ["enterprise-attack"],
            "x_mitre_version": "4.0"
        }
        
        group.update(overrides)
        return group
    
    @staticmethod
    def create_sample_tactic(
        tactic_id: str = "TA0001",
        name: Optional[str] = None,
        **overrides
    ) -> Dict[str, Any]:
        """Create sample tactic data.
        
        Args:
            tactic_id: The tactic ID (e.g., "TA0001")
            name: Optional tactic name
            **overrides: Additional fields to override
            
        Returns:
            Dictionary representing a tactic
        """
        if name is None:
            name = "Initial Access"
        
        tactic = {
            "type": "x-mitre-tactic",
            "id": f"x-mitre-tactic--{TestDataFactory._generate_uuid()}",
            "created": "2018-10-17T00:14:20.652Z",
            "modified": "2019-07-19T17:43:41.967Z",
            "name": name,
            "description": f"The adversary is trying to get into your network. {name} consists of techniques that use various entry vectors to gain their initial foothold within a network. This is test data for {tactic_id}.",
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "url": f"https://attack.mitre.org/tactics/{tactic_id}",
                    "external_id": tactic_id
                }
            ],
            "object_marking_refs": [
                "marking-definition--fa42a846-8d90-4e51-bc29-71d5b4802168"
            ],
            "x_mitre_shortname": name.lower().replace(" ", "-"),
            "x_mitre_attack_spec_version": "3.1.0",
            "x_mitre_domains": ["enterprise-attack"],
            "x_mitre_version": "1.0"
        }
        
        tactic.update(overrides)
        return tactic
    
    @staticmethod
    def create_sample_mitigation(
        mitigation_id: str = "M1013",
        name: Optional[str] = None,
        **overrides
    ) -> Dict[str, Any]:
        """Create sample mitigation data.
        
        Args:
            mitigation_id: The mitigation ID (e.g., "M1013")
            name: Optional mitigation name
            **overrides: Additional fields to override
            
        Returns:
            Dictionary representing a mitigation
        """
        if name is None:
            name = "Application Developer Guidance"
        
        mitigation = {
            "type": "course-of-action",
            "id": f"course-of-action--{TestDataFactory._generate_uuid()}",
            "created": "2018-10-17T00:14:20.652Z",
            "modified": "2022-03-08T21:17:27.266Z",
            "name": name,
            "description": f"This mitigation describes any guidance or training given to developers of applications to avoid introducing security weaknesses that an adversary may be able to take advantage of. This is test data for {mitigation_id}.",
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "url": f"https://attack.mitre.org/mitigations/{mitigation_id}",
                    "external_id": mitigation_id
                }
            ],
            "object_marking_refs": [
                "marking-definition--fa42a846-8d90-4e51-bc29-71d5b4802168"
            ],
            "x_mitre_attack_spec_version": "3.1.0",
            "x_mitre_domains": ["enterprise-attack"],
            "x_mitre_version": "1.0"
        }
        
        mitigation.update(overrides)
        return mitigation
    
    @staticmethod
    def create_sample_relationship(
        source_ref: str,
        target_ref: str,
        relationship_type: str = "uses",
        **overrides
    ) -> Dict[str, Any]:
        """Create sample relationship data.
        
        Args:
            source_ref: Source object reference
            target_ref: Target object reference
            relationship_type: Type of relationship
            **overrides: Additional fields to override
            
        Returns:
            Dictionary representing a relationship
        """
        relationship = {
            "type": "relationship",
            "id": f"relationship--{TestDataFactory._generate_uuid()}",
            "created": "2017-05-31T21:33:27.071Z",
            "modified": "2020-03-16T15:38:37.650Z",
            "relationship_type": relationship_type,
            "source_ref": source_ref,
            "target_ref": target_ref,
            "external_references": [
                {
                    "source_name": "test-reference",
                    "description": "Test relationship reference"
                }
            ],
            "object_marking_refs": [
                "marking-definition--fa42a846-8d90-4e51-bc29-71d5b4802168"
            ]
        }
        
        relationship.update(overrides)
        return relationship
    
    @staticmethod
    def create_sample_stix_bundle(entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a STIX bundle containing multiple entities.
        
        Args:
            entities: List of STIX entities to include in the bundle
            
        Returns:
            Dictionary representing a STIX bundle
        """
        return {
            "type": "bundle",
            "id": f"bundle--{TestDataFactory._generate_uuid()}",
            "spec_version": "2.1",
            "objects": entities
        }
    
    @staticmethod
    def create_attack_path_data() -> List[Dict[str, Any]]:
        """Create sample data for attack path testing.
        
        Returns:
            List of techniques representing an attack path
        """
        return [
            TestDataFactory.create_sample_technique("T1566", "Phishing"),
            TestDataFactory.create_sample_technique("T1204", "User Execution"),
            TestDataFactory.create_sample_technique("T1055", "Process Injection"),
            TestDataFactory.create_sample_technique("T1003", "OS Credential Dumping"),
            TestDataFactory.create_sample_technique("T1021", "Remote Services")
        ]
    
    @staticmethod
    def create_coverage_gap_data() -> Dict[str, Any]:
        """Create sample data for coverage gap analysis testing.
        
        Returns:
            Dictionary with group and technique data for gap analysis
        """
        group = TestDataFactory.create_sample_group("G0016", "APT29")
        techniques = [
            TestDataFactory.create_sample_technique("T1566", "Phishing"),
            TestDataFactory.create_sample_technique("T1204", "User Execution"),
            TestDataFactory.create_sample_technique("T1055", "Process Injection")
        ]
        
        return {
            "group": group,
            "techniques": techniques,
            "coverage": {
                "T1566": {"covered": True, "controls": ["Email Security"]},
                "T1204": {"covered": False, "controls": []},
                "T1055": {"covered": True, "controls": ["EDR", "Process Monitoring"]}
            }
        }
    
    @staticmethod
    def create_mock_http_response(status_code: int = 200, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Create mock HTTP response data.
        
        Args:
            status_code: HTTP status code
            data: Response data
            
        Returns:
            Mock response dictionary
        """
        if data is None:
            data = {"message": "Test response"}
        
        return {
            "status_code": status_code,
            "json": lambda: data,
            "text": json.dumps(data),
            "headers": {"Content-Type": "application/json"}
        }
    
    @staticmethod
    def _generate_uuid() -> str:
        """Generate a UUID for test objects.
        
        Returns:
            UUID string
        """
        import uuid
        return str(uuid.uuid4())


class ConfigurationFactory:
    """Factory for creating test configuration data."""
    
    @staticmethod
    def create_test_config() -> Dict[str, Any]:
        """Create test configuration data.
        
        Returns:
            Test configuration dictionary
        """
        return {
            "data_sources": {
                "mitre_attack": {
                    "url": "https://example.com/test-data.json",
                    "format": "stix",
                    "entity_types": ["tactics", "techniques", "groups", "mitigations"]
                }
            },
            "server": {
                "host": "localhost",
                "port": 3001,
                "debug": True
            },
            "http_proxy": {
                "host": "localhost", 
                "port": 8001,
                "cors_enabled": True
            }
        }
    
    @staticmethod
    def create_test_environment_vars() -> Dict[str, str]:
        """Create test environment variables.
        
        Returns:
            Dictionary of environment variables for testing
        """
        return {
            "MCP_SERVER_HOST": "localhost",
            "MCP_SERVER_PORT": "3001",
            "MCP_HTTP_HOST": "localhost",
            "MCP_HTTP_PORT": "8001",
            "MITRE_ATTACK_URL": "https://example.com/test-data.json"
        }


class PerformanceDataFactory:
    """Factory for creating performance test data."""
    
    @staticmethod
    def create_large_dataset(size: int = 1000) -> List[Dict[str, Any]]:
        """Create a large dataset for performance testing.
        
        Args:
            size: Number of entities to create
            
        Returns:
            List of test entities
        """
        entities = []
        
        for i in range(size):
            if i % 4 == 0:
                entities.append(TestDataFactory.create_sample_technique(f"T{1000 + i}"))
            elif i % 4 == 1:
                entities.append(TestDataFactory.create_sample_group(f"G{1000 + i}"))
            elif i % 4 == 2:
                entities.append(TestDataFactory.create_sample_tactic(f"TA{1000 + i}"))
            else:
                entities.append(TestDataFactory.create_sample_mitigation(f"M{1000 + i}"))
        
        return entities
    
    @staticmethod
    def create_performance_thresholds() -> Dict[str, float]:
        """Create performance threshold data for testing.
        
        Returns:
            Dictionary of performance thresholds in seconds
        """
        return {
            "data_loading": 2.0,
            "search_query": 0.5,
            "technique_lookup": 0.1,
            "group_analysis": 1.0,
            "attack_path_construction": 3.0,
            "coverage_gap_analysis": 2.0,
            "relationship_discovery": 1.5
        }