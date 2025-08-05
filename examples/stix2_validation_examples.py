#!/usr/bin/env python3
"""
STIX2 Library Validation and Error Handling Examples

This module demonstrates how to use the official STIX2 Python library
for robust validation and error handling in threat intelligence parsing.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import json

import stix2
from stix2 import (
    Bundle, 
    AttackPattern, 
    IntrusionSet, 
    CourseOfAction, 
    Relationship,
    CustomObject
)
from stix2.base import _STIXBase, _DomainObject
from stix2.exceptions import (
    STIXError,
    InvalidValueError,
    MissingPropertiesError,
    ExtraPropertiesError,
    ParseError
)
from stix2.properties import StringProperty, ListProperty

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Example 1: Custom STIX Object Definition
@CustomObject('x-mitre-data-source', [
    ('name', StringProperty(required=True)),
    ('description', StringProperty()),
    ('data_components', ListProperty(StringProperty)),
    ('platforms', ListProperty(StringProperty)),
])
class DataSource:
    """Custom STIX object for MITRE ATT&CK Data Sources."""
    pass


def example_basic_stix_parsing():
    """Example 1: Basic STIX parsing with validation."""
    print("\\n=== Example 1: Basic STIX Parsing ===")
    
    # Valid STIX AttackPattern data
    technique_data = {
        "type": "attack-pattern",
        "spec_version": "2.1",
        "id": "attack-pattern--0a3ead4e-6d47-4ccb-854c-a6a4f9d96b22",
        "created": "2023-01-01T00:00:00.000Z",
        "modified": "2023-01-01T00:00:00.000Z",
        "name": "Process Injection",
        "description": "Adversaries may inject code into processes to evade defenses.",
        "external_references": [
            {
                "source_name": "mitre-attack",
                "external_id": "T1055",
                "url": "https://attack.mitre.org/techniques/T1055/"
            }
        ],
        "x_mitre_platforms": ["Windows", "macOS", "Linux"],
        "kill_chain_phases": [
            {
                "kill_chain_name": "mitre-attack",
                "phase_name": "defense-evasion"
            },
            {
                "kill_chain_name": "mitre-attack", 
                "phase_name": "privilege-escalation"
            }
        ]
    }
    
    try:
        # Parse with STIX2 library validation
        stix_obj = stix2.parse(technique_data, allow_custom=True)
        
        print(f"✓ Successfully parsed STIX object: {stix_obj.name}")
        print(f"  Type: {type(stix_obj).__name__}")
        print(f"  ID: {stix_obj.id}")
        print(f"  Platforms: {stix_obj.x_mitre_platforms}")
        print(f"  Kill Chain Phases: {len(stix_obj.kill_chain_phases)}")
        
        # Type-safe property access
        if isinstance(stix_obj, AttackPattern):
            print(f"  ✓ Confirmed AttackPattern object")
            for phase in stix_obj.kill_chain_phases:
                print(f"    - {phase.phase_name}")
        
    except STIXError as e:
        print(f"✗ STIX validation error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def example_error_handling():
    """Example 2: Comprehensive error handling for invalid STIX data."""
    print("\\n=== Example 2: Error Handling ===")
    
    # Test cases with various STIX validation errors
    test_cases = [
        {
            "name": "Missing required properties",
            "data": {
                "type": "attack-pattern",
                "id": "attack-pattern--test-uuid"
                # Missing required 'name' property
            }
        },
        {
            "name": "Invalid property type",
            "data": {
                "type": "attack-pattern",
                "id": "attack-pattern--test-uuid",
                "name": "Test Technique",
                "kill_chain_phases": "invalid-should-be-list"  # Should be list
            }
        },
        {
            "name": "Invalid STIX object type",
            "data": {
                "type": "invalid-stix-type",
                "id": "invalid-type--test-uuid",
                "name": "Invalid Object"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\\nTesting: {test_case['name']}")
        
        try:
            stix_obj = stix2.parse(test_case['data'], allow_custom=True)
            print(f"  ✓ Unexpectedly successful: {stix_obj.name}")
            
        except MissingPropertiesError as e:
            print(f"  ✗ Missing properties: {e}")
            if hasattr(e, 'properties'):
                print(f"    Missing: {e.properties}")
                
        except InvalidValueError as e:
            print(f"  ✗ Invalid value: {e}")
            if hasattr(e, 'prop_name'):
                print(f"    Property: {e.prop_name}")
                
        except STIXError as e:
            print(f"  ✗ STIX error: {e}")
            
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")


def example_bundle_processing():
    """Example 3: STIX Bundle processing with error handling."""
    print("\\n=== Example 3: Bundle Processing ===")
    
    # STIX Bundle with mixed valid and invalid objects
    bundle_data = {
        "type": "bundle",
        "id": "bundle--example-uuid",
        "objects": [
            # Valid AttackPattern
            {
                "type": "attack-pattern",
                "id": "attack-pattern--valid-uuid",
                "name": "Valid Technique",
                "description": "A valid technique object",
                "external_references": [
                    {"source_name": "mitre-attack", "external_id": "T1001"}
                ]
            },
            # Valid IntrusionSet
            {
                "type": "intrusion-set",
                "id": "intrusion-set--valid-uuid",
                "name": "Valid Group",
                "description": "A valid threat group",
                "aliases": ["Group1", "TestGroup"],
                "external_references": [
                    {"source_name": "mitre-attack", "external_id": "G0001"}
                ]
            },
            # Invalid object (missing name)
            {
                "type": "attack-pattern",
                "id": "attack-pattern--invalid-uuid",
                "description": "Missing name property"
            },
            # Valid Relationship
            {
                "type": "relationship",
                "id": "relationship--valid-uuid",
                "relationship_type": "uses",
                "source_ref": "intrusion-set--valid-uuid",
                "target_ref": "attack-pattern--valid-uuid"
            }
        ]
    }
    
    try:
        # Parse bundle with validation
        bundle = Bundle(allow_custom=True, **bundle_data)
        print(f"✓ Successfully parsed bundle with {len(bundle.objects)} objects")
        
        valid_objects = 0
        invalid_objects = 0
        
        # Process each object with individual error handling
        for i, obj in enumerate(bundle.objects):
            try:
                # Validate individual object
                if hasattr(obj, 'name'):
                    name = obj.name
                else:
                    name = f"Object {i+1}"
                
                print(f"  Object {i+1}: {obj.type} - {name}")
                
                # Type-specific processing
                if isinstance(obj, AttackPattern):
                    print(f"    ✓ AttackPattern: {obj.name}")
                    if hasattr(obj, 'external_references'):
                        for ref in obj.external_references:
                            if ref.source_name == "mitre-attack":
                                print(f"      MITRE ID: {ref.external_id}")
                                
                elif isinstance(obj, IntrusionSet):
                    print(f"    ✓ IntrusionSet: {obj.name}")
                    if hasattr(obj, 'aliases'):
                        print(f"      Aliases: {obj.aliases}")
                        
                elif isinstance(obj, Relationship):
                    print(f"    ✓ Relationship: {obj.relationship_type}")
                    print(f"      {obj.source_ref} → {obj.target_ref}")
                    
                valid_objects += 1
                
            except (STIXError, AttributeError) as e:
                print(f"    ✗ Error processing object {i+1}: {e}")
                invalid_objects += 1
                continue
        
        print(f"\\nProcessing summary:")
        print(f"  Valid objects: {valid_objects}")
        print(f"  Invalid objects: {invalid_objects}")
        
    except STIXError as e:
        print(f"✗ Bundle validation failed: {e}")
    except Exception as e:
        print(f"✗ Unexpected bundle error: {e}")


def example_custom_objects():
    """Example 4: Custom STIX objects with validation."""
    print("\\n=== Example 4: Custom STIX Objects ===")
    
    # Create custom DataSource object
    try:
        data_source = DataSource(
            name="Process Monitoring",
            description="Monitor process creation and execution activities",
            data_components=["Process Creation", "Process Termination", "Process Access"],
            platforms=["Windows", "Linux", "macOS"]
        )
        
        print(f"✓ Created custom DataSource: {data_source.name}")
        print(f"  Components: {len(data_source.data_components)}")
        print(f"  Platforms: {data_source.platforms}")
        
        # Convert to dictionary for parsing
        data_source_dict = {
            "type": "x-mitre-data-source",
            "id": "x-mitre-data-source--example-uuid",
            "name": "Network Monitoring",
            "description": "Monitor network traffic and connections",
            "data_components": ["Network Connection Creation", "Network Traffic Flow"],
            "platforms": ["Windows", "Linux"]
        }
        
        # Parse custom object from dictionary
        parsed_obj = stix2.parse(data_source_dict, allow_custom=True)
        
        if isinstance(parsed_obj, DataSource):
            print(f"✓ Parsed custom object: {parsed_obj.name}")
            print(f"  Type: {type(parsed_obj).__name__}")
            
    except MissingPropertiesError as e:
        print(f"✗ Missing required properties: {e}")
    except STIXError as e:
        print(f"✗ STIX validation error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def example_relationship_validation():
    """Example 5: STIX Relationship validation and processing."""
    print("\\n=== Example 5: Relationship Validation ===")
    
    # Valid relationship data
    relationship_data = {
        "type": "relationship",
        "id": "relationship--example-uuid",
        "created": "2023-01-01T00:00:00.000Z",
        "modified": "2023-01-01T00:00:00.000Z",
        "relationship_type": "uses",
        "source_ref": "intrusion-set--source-uuid",
        "target_ref": "attack-pattern--target-uuid",
        "description": "Group uses this technique for initial access"
    }
    
    try:
        # Parse relationship with validation
        relationship = stix2.parse(relationship_data, allow_custom=True)
        
        if isinstance(relationship, Relationship):
            print(f"✓ Valid relationship: {relationship.relationship_type}")
            print(f"  Source: {relationship.source_ref}")
            print(f"  Target: {relationship.target_ref}")
            print(f"  Description: {relationship.description}")
            
            # Validate relationship references
            print(f"\\n  Relationship validation:")
            print(f"    ✓ Source ref format: {'valid' if relationship.source_ref.startswith('intrusion-set--') else 'invalid'}")
            print(f"    ✓ Target ref format: {'valid' if relationship.target_ref.startswith('attack-pattern--') else 'invalid'}")
            print(f"    ✓ Relationship type: {relationship.relationship_type}")
            
    except STIXError as e:
        print(f"✗ Relationship validation failed: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def example_mitre_id_validation():
    """Example 6: MITRE ID validation using STIX external references."""
    print("\\n=== Example 6: MITRE ID Validation ===")
    
    # Test MITRE ID validation patterns
    test_ids = [
        "T1055",      # Valid technique
        "T1055.001",  # Valid sub-technique
        "G0016",      # Valid group
        "TA0005",     # Valid tactic
        "M1013",      # Valid mitigation
        "T99999",     # Invalid technique (too many digits)
        "G999",       # Invalid group (too few digits)
        "INVALID",    # Invalid format
    ]
    
    import re
    mitre_pattern = r"^(T\\d{4}(\\.\\d{3})?|G\\d{4}|TA\\d{4}|M\\d{4})$"
    
    for test_id in test_ids:
        is_valid = bool(re.match(mitre_pattern, test_id))
        status = "✓" if is_valid else "✗"
        
        # Create STIX object with this ID
        test_data = {
            "type": "attack-pattern",
            "id": "attack-pattern--test-uuid",
            "name": f"Test for {test_id}",
            "external_references": [
                {
                    "source_name": "mitre-attack",
                    "external_id": test_id
                }
            ]
        }
        
        try:
            stix_obj = stix2.parse(test_data, allow_custom=True)
            
            # Extract MITRE ID from external references
            mitre_id = None
            for ref in stix_obj.external_references:
                if ref.source_name == "mitre-attack":
                    mitre_id = ref.external_id
                    break
            
            print(f"  {status} {test_id}: {'Valid' if is_valid else 'Invalid'} format - STIX object created")
            
        except STIXError as e:
            print(f"  ✗ {test_id}: STIX validation failed - {e}")


if __name__ == "__main__":
    """Run all STIX2 validation examples."""
    print("STIX2 Library Validation and Error Handling Examples")
    print("=" * 60)
    
    # Run all examples
    example_basic_stix_parsing()
    example_error_handling()
    example_bundle_processing()
    example_custom_objects()
    example_relationship_validation()
    example_mitre_id_validation()
    
    print("\\n" + "=" * 60)
    print("Examples completed! Check the output above for validation results.")
    print("\\nFor more information:")
    print("- STIX2 Library Documentation: https://stix2.readthedocs.io/")
    print("- STIX 2.1 Specification: https://docs.oasis-open.org/cti/stix/v2.1/")
    print("- Project Documentation: docs/stix2_extensibility_guide.md")