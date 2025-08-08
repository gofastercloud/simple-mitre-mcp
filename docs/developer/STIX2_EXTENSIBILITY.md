# STIX2 Library Extensibility Guide

## Overview

This guide demonstrates how to extend the MITRE ATT&CK MCP Server's STIX parsing capabilities using the official STIX2 Python library. The server leverages the library's robust validation, type safety, and extensibility features for standards-compliant threat intelligence processing.

## Architecture Overview

The STIX parser (`src/parsers/stix_parser.py`) uses the official STIX2 library for:
- **Type-safe parsing**: Uses library objects (AttackPattern, IntrusionSet, CourseOfAction)
- **Built-in validation**: Leverages library's comprehensive error handling
- **Standards compliance**: Ensures compatibility with STIX 2.1 specification
- **Extensibility**: Easy addition of custom STIX object types

## Adding New STIX Object Types

### 1. Define Custom STIX Objects

```python
from stix2 import CustomObject
from stix2.properties import StringProperty, ListProperty, TimestampProperty

@CustomObject('x-mitre-data-source', [
    ('name', StringProperty(required=True)),
    ('description', StringProperty()),
    ('data_components', ListProperty(StringProperty)),
    ('platforms', ListProperty(StringProperty)),
    ('collection_layers', ListProperty(StringProperty)),
])
class DataSource:
    """Custom STIX object for MITRE ATT&CK Data Sources."""
    pass

@CustomObject('x-mitre-detection', [
    ('name', StringProperty(required=True)),
    ('description', StringProperty()),
    ('data_sources', ListProperty(StringProperty)),
    ('analytic_type', StringProperty()),
    ('applicable_platforms', ListProperty(StringProperty)),
])
class Detection:
    """Custom STIX object for detection analytics."""
    pass
```

### 2. Extend the Parser

```python
class ExtendedSTIXParser(STIXParser):
    """Extended STIX parser with custom object support."""
    
    def __init__(self):
        super().__init__()
        # Add custom type mappings
        self.stix_type_mapping.update({
            "x-mitre-data-source": "data_sources",
            "x-mitre-detection": "detections",
        })
    
    def _extract_data_source_data_from_stix_object(
        self, stix_obj: Union[DataSource, Dict[str, Any]]
    ) -> ParsedEntityData:
        """Extract data source-specific data from STIX2 library object."""
        data = {}
        
        try:
            # Use STIX2 library properties with validation
            if hasattr(stix_obj, 'data_components'):
                data["data_components"] = stix_obj.data_components
            else:
                data["data_components"] = stix_obj.get("data_components", [])
            
            if hasattr(stix_obj, 'platforms'):
                data["platforms"] = stix_obj.platforms
            else:
                data["platforms"] = stix_obj.get("platforms", [])
                
            if hasattr(stix_obj, 'collection_layers'):
                data["collection_layers"] = stix_obj.collection_layers
            else:
                data["collection_layers"] = stix_obj.get("collection_layers", [])
            
            return data
            
        except (STIXError, InvalidValueError, AttributeError) as e:
            logger.debug(f"Error extracting data source data: {e}")
            return {}
    
    def _extract_detection_data_from_stix_object(
        self, stix_obj: Union[Detection, Dict[str, Any]]
    ) -> ParsedEntityData:
        """Extract detection-specific data from STIX2 library object."""
        data = {}
        
        try:
            # Use STIX2 library properties with validation
            if hasattr(stix_obj, 'data_sources'):
                data["data_sources"] = stix_obj.data_sources
            else:
                data["data_sources"] = stix_obj.get("data_sources", [])
            
            if hasattr(stix_obj, 'analytic_type'):
                data["analytic_type"] = stix_obj.analytic_type
            else:
                data["analytic_type"] = stix_obj.get("analytic_type", "")
                
            if hasattr(stix_obj, 'applicable_platforms'):
                data["applicable_platforms"] = stix_obj.applicable_platforms
            else:
                data["applicable_platforms"] = stix_obj.get("applicable_platforms", [])
            
            return data
            
        except (STIXError, InvalidValueError, AttributeError) as e:
            logger.debug(f"Error extracting detection data: {e}")
            return {}
```

### 3. Update Entity Extraction Logic

```python
def _extract_entity_from_stix_object_with_validation(
    self, stix_obj: STIXObjectOrDict, entity_type: str
) -> Optional[ParsedEntityData]:
    """Extended entity extraction with custom object support."""
    # ... existing code ...
    
    # Add custom entity type handling
    try:
        if entity_type == "data_sources":
            entity_data.update(
                self._extract_data_source_data_from_stix_object(stix_obj)
            )
        elif entity_type == "detections":
            entity_data.update(
                self._extract_detection_data_from_stix_object(stix_obj)
            )
        # ... existing entity types ...
    except (STIXError, InvalidValueError, MissingPropertiesError) as e:
        logger.debug(f"Error extracting {entity_type}-specific data: {e}")
        pass
    
    return entity_data
```

## Advanced Relationship Processing

### 1. Enhanced Relationship Analysis

```python
from stix2 import Relationship, Bundle
from typing import List, Dict, Set

class RelationshipAnalyzer:
    """Advanced relationship analysis using STIX2 library."""
    
    def __init__(self, stix_parser: STIXParser):
        self.parser = stix_parser
        
    def analyze_complex_relationships(
        self, 
        bundle_data: Dict[str, Any], 
        source_id: str,
        max_depth: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze multi-level relationships using STIX2 library objects."""
        
        try:
            # Parse bundle with STIX2 library validation
            bundle = Bundle(allow_custom=True, **bundle_data)
            
            # Extract relationships with type safety
            relationships = []
            entities = {}
            
            for obj in bundle.objects:
                if obj.type == "relationship":
                    # Use STIX2 Relationship object properties
                    rel = Relationship(**obj._inner) if hasattr(obj, '_inner') else obj
                    relationships.append({
                        "type": rel.relationship_type,
                        "source": rel.source_ref,
                        "target": rel.target_ref,
                        "created": rel.created,
                        "modified": rel.modified
                    })
                else:
                    # Store entities for reference resolution
                    entities[obj.id] = {
                        "type": obj.type,
                        "name": getattr(obj, 'name', ''),
                        "id": obj.id
                    }
            
            # Build relationship graph
            return self._build_relationship_graph(
                relationships, entities, source_id, max_depth
            )
            
        except STIXError as e:
            logger.error(f"STIX validation error in relationship analysis: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error analyzing relationships: {e}")
            return {}
    
    def _build_relationship_graph(
        self, 
        relationships: List[Dict[str, Any]], 
        entities: Dict[str, Dict[str, Any]],
        source_id: str,
        max_depth: int
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Build multi-level relationship graph."""
        
        def traverse_relationships(current_id: str, depth: int, visited: Set[str]) -> List[Dict[str, Any]]:
            if depth >= max_depth or current_id in visited:
                return []
            
            visited.add(current_id)
            results = []
            
            for rel in relationships:
                if rel["source"] == current_id:
                    target_entity = entities.get(rel["target"])
                    if target_entity:
                        relationship_data = {
                            "relationship_type": rel["type"],
                            "target": target_entity,
                            "depth": depth,
                            "children": traverse_relationships(rel["target"], depth + 1, visited.copy())
                        }
                        results.append(relationship_data)
            
            return results
        
        return {
            "source": entities.get(source_id, {}),
            "relationships": traverse_relationships(source_id, 0, set())
        }
```

### 2. STIX Bundle Processing

```python
def process_stix_bundle_with_relationships(
    self, 
    bundle_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Process STIX bundle with comprehensive relationship analysis."""
    
    try:
        # Parse with STIX2 library validation
        bundle = Bundle(allow_custom=True, **bundle_data)
        
        processed_data = {
            "entities": {},
            "relationships": [],
            "statistics": {}
        }
        
        # Process each object with type safety
        for obj in bundle.objects:
            try:
                if obj.type == "relationship":
                    # Process relationships with validation
                    rel_data = self._process_relationship_object(obj)
                    if rel_data:
                        processed_data["relationships"].append(rel_data)
                        
                elif obj.type in ["attack-pattern", "intrusion-set", "course-of-action"]:
                    # Process entities with STIX2 library objects
                    entity_data = self._process_entity_object(obj)
                    if entity_data:
                        processed_data["entities"][obj.id] = entity_data
                        
            except (STIXError, InvalidValueError) as e:
                logger.warning(f"Error processing STIX object {obj.id}: {e}")
                continue
        
        # Generate statistics
        processed_data["statistics"] = self._generate_bundle_statistics(processed_data)
        
        return processed_data
        
    except STIXError as e:
        logger.error(f"STIX bundle validation failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing STIX bundle: {e}")
        raise

def _process_relationship_object(self, rel_obj: Relationship) -> Optional[Dict[str, Any]]:
    """Process STIX relationship object with validation."""
    try:
        return {
            "id": rel_obj.id,
            "type": rel_obj.relationship_type,
            "source_ref": rel_obj.source_ref,
            "target_ref": rel_obj.target_ref,
            "created": rel_obj.created.isoformat() if rel_obj.created else None,
            "modified": rel_obj.modified.isoformat() if rel_obj.modified else None,
            "description": getattr(rel_obj, 'description', ''),
            "external_references": self._extract_external_references(rel_obj)
        }
    except (AttributeError, STIXError) as e:
        logger.debug(f"Error processing relationship object: {e}")
        return None

def _extract_external_references(self, stix_obj: STIXObject) -> List[Dict[str, str]]:
    """Extract external references with STIX2 library validation."""
    try:
        if hasattr(stix_obj, 'external_references'):
            refs = []
            for ref in stix_obj.external_references:
                ref_data = {
                    "source_name": ref.source_name,
                    "external_id": getattr(ref, 'external_id', ''),
                    "url": getattr(ref, 'url', ''),
                    "description": getattr(ref, 'description', '')
                }
                refs.append(ref_data)
            return refs
        return []
    except (AttributeError, STIXError) as e:
        logger.debug(f"Error extracting external references: {e}")
        return []
```

## Error Handling and Validation

### 1. Comprehensive Error Handling

```python
from stix2.exceptions import (
    STIXError, InvalidValueError, MissingPropertiesError,
    ExtraPropertiesError, ParseError
)

def robust_stix_parsing_with_error_handling(
    self, 
    stix_data: Dict[str, Any]
) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
    """Parse STIX data with comprehensive error handling and reporting."""
    
    parsed_data = {}
    error_log = []
    
    try:
        # Attempt to parse with STIX2 library
        stix_objects = self._parse_stix_bundle_with_validation(stix_data)
        
        for i, obj in enumerate(stix_objects):
            try:
                # Validate object structure
                if not self._validate_stix_object_structure(obj):
                    error_log.append({
                        "object_index": i,
                        "error_type": "ValidationError",
                        "message": "Invalid STIX object structure",
                        "object_id": getattr(obj, 'id', 'unknown')
                    })
                    continue
                
                # Process object with specific error handling
                processed_obj = self._process_stix_object_with_validation(obj)
                if processed_obj:
                    parsed_data[obj.id] = processed_obj
                    
            except STIXError as e:
                error_log.append({
                    "object_index": i,
                    "error_type": "STIXError",
                    "message": str(e),
                    "object_id": getattr(obj, 'id', 'unknown'),
                    "details": self._get_stix_error_details(e)
                })
                continue
                
            except InvalidValueError as e:
                error_log.append({
                    "object_index": i,
                    "error_type": "InvalidValueError",
                    "message": str(e),
                    "object_id": getattr(obj, 'id', 'unknown'),
                    "property": getattr(e, 'prop_name', 'unknown')
                })
                continue
                
            except MissingPropertiesError as e:
                error_log.append({
                    "object_index": i,
                    "error_type": "MissingPropertiesError",
                    "message": str(e),
                    "object_id": getattr(obj, 'id', 'unknown'),
                    "missing_properties": getattr(e, 'properties', [])
                })
                continue
    
    except Exception as e:
        error_log.append({
            "error_type": "CriticalError",
            "message": f"Failed to parse STIX bundle: {str(e)}",
            "traceback": traceback.format_exc()
        })
    
    return parsed_data, error_log

def _process_stix_object_with_validation(self, stix_obj: STIXObject) -> Optional[Dict[str, Any]]:
    """Process STIX object with validation and type checking."""
    try:
        # Type-specific processing with validation
        if isinstance(stix_obj, AttackPattern):
            return self._process_attack_pattern(stix_obj)
        elif isinstance(stix_obj, IntrusionSet):
            return self._process_intrusion_set(stix_obj)
        elif isinstance(stix_obj, CourseOfAction):
            return self._process_course_of_action(stix_obj)
        elif isinstance(stix_obj, Relationship):
            return self._process_relationship(stix_obj)
        else:
            logger.debug(f"Unknown STIX object type: {type(stix_obj)}")
            return None
            
    except (STIXError, AttributeError) as e:
        logger.debug(f"Error processing STIX object: {e}")
        return None
```

### 2. Validation Utilities

```python
def validate_mitre_id_comprehensive(self, mitre_id: str) -> Tuple[bool, Dict[str, Any]]:
    """Comprehensive MITRE ID validation with detailed feedback."""
    
    validation_result = {
        "is_valid": False,
        "id_type": None,
        "format_issues": [],
        "suggestions": []
    }
    
    if not isinstance(mitre_id, str) or not mitre_id:
        validation_result["format_issues"].append("ID must be a non-empty string")
        return False, validation_result
    
    # Enhanced pattern matching with detailed feedback
    import re
    
    patterns = {
        "technique": r"^T\d{4}(\.\d{3})?$",
        "group": r"^G\d{4}$",
        "tactic": r"^TA\d{4}$",
        "mitigation": r"^M\d{4}$",
        "data_source": r"^DS\d{4}$",
        "data_component": r"^DC\d{4}$"
    }
    
    for id_type, pattern in patterns.items():
        if re.match(pattern, mitre_id):
            validation_result["is_valid"] = True
            validation_result["id_type"] = id_type
            return True, validation_result
    
    # Provide suggestions for malformed IDs
    if mitre_id.upper().startswith('T'):
        validation_result["suggestions"].append("Technique IDs should be in format T#### or T####.###")
    elif mitre_id.upper().startswith('G'):
        validation_result["suggestions"].append("Group IDs should be in format G####")
    elif mitre_id.upper().startswith('TA'):
        validation_result["suggestions"].append("Tactic IDs should be in format TA####")
    elif mitre_id.upper().startswith('M'):
        validation_result["suggestions"].append("Mitigation IDs should be in format M####")
    else:
        validation_result["suggestions"].append("Unknown ID format. Expected T####, G####, TA####, or M####")
    
    validation_result["format_issues"].append(f"Invalid MITRE ID format: {mitre_id}")
    return False, validation_result
```

## Testing Custom Extensions

### 1. Unit Tests for Custom Objects

```python
import pytest
from unittest.mock import Mock, patch
import stix2

class TestCustomSTIXObjects:
    """Test suite for custom STIX object extensions."""
    
    def test_data_source_object_creation(self):
        """Test custom DataSource STIX object creation."""
        data_source = DataSource(
            name="Process Monitoring",
            description="Monitor process creation and execution",
            data_components=["Process Creation", "Process Termination"],
            platforms=["Windows", "Linux", "macOS"],
            collection_layers=["Host", "Network"]
        )
        
        assert data_source.name == "Process Monitoring"
        assert len(data_source.data_components) == 2
        assert "Windows" in data_source.platforms
    
    def test_data_source_stix_validation(self):
        """Test STIX validation for custom DataSource objects."""
        # Valid object
        valid_data = {
            "type": "x-mitre-data-source",
            "id": "x-mitre-data-source--uuid-here",
            "name": "Test Data Source",
            "data_components": ["Component 1"]
        }
        
        data_source = stix2.parse(valid_data, allow_custom=True)
        assert isinstance(data_source, DataSource)
        
        # Invalid object (missing required name)
        invalid_data = {
            "type": "x-mitre-data-source",
            "id": "x-mitre-data-source--uuid-here",
            "data_components": ["Component 1"]
        }
        
        with pytest.raises(stix2.exceptions.MissingPropertiesError):
            stix2.parse(invalid_data, allow_custom=True)
    
    def test_extended_parser_integration(self):
        """Test integration of custom objects with extended parser."""
        parser = ExtendedSTIXParser()
        
        test_bundle = {
            "type": "bundle",
            "id": "bundle--test-uuid",
            "objects": [
                {
                    "type": "x-mitre-data-source",
                    "id": "x-mitre-data-source--test-uuid",
                    "name": "Test Data Source",
                    "description": "Test description",
                    "data_components": ["Component 1", "Component 2"],
                    "external_references": [
                        {
                            "source_name": "mitre-attack",
                            "external_id": "DS0001"
                        }
                    ]
                }
            ]
        }
        
        result = parser.parse(test_bundle, ["data_sources"])
        
        assert "data_sources" in result
        assert len(result["data_sources"]) == 1
        assert result["data_sources"][0]["id"] == "DS0001"
        assert result["data_sources"][0]["name"] == "Test Data Source"
        assert len(result["data_sources"][0]["data_components"]) == 2
```

### 2. Integration Tests

```python
class TestSTIX2Integration:
    """Integration tests for STIX2 library features."""
    
    def test_relationship_processing_with_validation(self):
        """Test relationship processing with STIX2 library validation."""
        parser = ExtendedSTIXParser()
        analyzer = RelationshipAnalyzer(parser)
        
        test_bundle = {
            "type": "bundle",
            "id": "bundle--test-uuid",
            "objects": [
                {
                    "type": "attack-pattern",
                    "id": "attack-pattern--uuid1",
                    "name": "Test Technique",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "T1001"}
                    ]
                },
                {
                    "type": "intrusion-set",
                    "id": "intrusion-set--uuid2",
                    "name": "Test Group",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "G0001"}
                    ]
                },
                {
                    "type": "relationship",
                    "id": "relationship--uuid3",
                    "relationship_type": "uses",
                    "source_ref": "intrusion-set--uuid2",
                    "target_ref": "attack-pattern--uuid1"
                }
            ]
        }
        
        result = analyzer.analyze_complex_relationships(
            test_bundle, "intrusion-set--uuid2", max_depth=2
        )
        
        assert "source" in result
        assert result["source"]["id"] == "intrusion-set--uuid2"
        assert len(result["relationships"]) == 1
        assert result["relationships"][0]["relationship_type"] == "uses"
    
    def test_error_handling_comprehensive(self):
        """Test comprehensive error handling with invalid STIX data."""
        parser = ExtendedSTIXParser()
        
        # Bundle with various errors
        problematic_bundle = {
            "type": "bundle",
            "id": "bundle--test-uuid",
            "objects": [
                # Valid object
                {
                    "type": "attack-pattern",
                    "id": "attack-pattern--valid-uuid",
                    "name": "Valid Technique",
                    "external_references": [
                        {"source_name": "mitre-attack", "external_id": "T1001"}
                    ]
                },
                # Missing required properties
                {
                    "type": "attack-pattern",
                    "id": "attack-pattern--invalid-uuid1"
                    # Missing required 'name' property
                },
                # Invalid property values
                {
                    "type": "attack-pattern",
                    "id": "attack-pattern--invalid-uuid2",
                    "name": "Invalid Technique",
                    "kill_chain_phases": "invalid-should-be-list"
                }
            ]
        }
        
        parsed_data, error_log = parser.robust_stix_parsing_with_error_handling(
            problematic_bundle
        )
        
        # Should successfully parse valid object
        assert len(parsed_data) >= 1
        
        # Should log errors for invalid objects
        assert len(error_log) >= 2
        assert any(error["error_type"] == "MissingPropertiesError" for error in error_log)
        assert any(error["error_type"] == "InvalidValueError" for error in error_log)
```

## Best Practices

### 1. Type Safety

- Always use STIX2 library objects when possible
- Implement proper type hints for custom extensions
- Use isinstance() checks for type validation
- Handle both library objects and dictionary fallbacks

### 2. Error Handling

- Catch specific STIX2 library exceptions
- Provide detailed error context and suggestions
- Log errors at appropriate levels
- Implement graceful degradation for parsing failures

### 3. Validation

- Leverage STIX2 library's built-in validation
- Implement custom validation for domain-specific requirements
- Validate MITRE ID formats comprehensively
- Provide helpful error messages and suggestions

### 4. Performance

- Use library's efficient parsing methods
- Implement caching for frequently accessed data
- Consider memory usage with large STIX bundles
- Profile custom extensions for performance impact

### 5. Testing

- Write comprehensive unit tests for custom objects
- Test error conditions and edge cases
- Validate STIX compliance of custom extensions
- Include integration tests with real data

This guide provides a comprehensive foundation for extending the STIX parser with new object types, advanced relationship processing, and robust error handling using the official STIX2 Python library.