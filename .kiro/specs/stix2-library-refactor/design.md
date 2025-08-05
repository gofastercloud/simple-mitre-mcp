# Design Document

## Overview

This design document outlines the refactoring of the current custom STIX parser implementation to use the official STIX2 Python library. The refactoring will replace the custom parsing logic in `src/parsers/stix_parser.py` with standards-compliant, battle-tested library calls while maintaining complete backward compatibility for all existing functionality.

The official `stix2` library provides robust STIX 2.1 parsing, validation, and object manipulation capabilities that align with our "library-first development" principles.

## Architecture

### Current Architecture
```
MITRE ATT&CK STIX Data → Custom STIXParser → Parsed Entities → MCP Tools
```

### New Architecture
```
MITRE ATT&CK STIX Data → Official STIX2 Library → STIXParser (Adapter) → Parsed Entities → MCP Tools
```

The new architecture introduces the official `stix2` library as the primary parsing engine, with our `STIXParser` class acting as an adapter that transforms the library's objects into our expected data format.

## Components and Interfaces

### STIX2 Library Integration

#### Library Selection
- **Library**: `stix2` (official OASIS STIX 2.x Python library)
- **Version**: Latest stable version (2.1.x compatible)
- **Installation**: Add to `pyproject.toml` dependencies

#### Key Library Features to Leverage
- **Object Parsing**: `stix2.parse()` for robust STIX object creation
- **Bundle Processing**: `stix2.Bundle` for handling STIX bundles
- **Validation**: Built-in schema validation and error handling
- **Type System**: Strongly-typed STIX objects with proper inheritance
- **Relationship Handling**: Native support for STIX relationships

### Refactored STIXParser Class

#### Class Structure
```python
from stix2 import parse, Bundle
from stix2.base import STIXDomainObject
from stix2.exceptions import STIXError

class STIXParser:
    """
    Adapter class that uses the official STIX2 library for parsing
    while maintaining compatibility with existing data extraction patterns.
    """
    
    def __init__(self):
        # Maintain existing type mappings for compatibility
        self.stix_type_mapping = {
            'x-mitre-tactic': 'tactics',
            'attack-pattern': 'techniques', 
            'intrusion-set': 'groups',
            'course-of-action': 'mitigations'
        }
        
    def parse(self, stix_data: Dict[str, Any], entity_types: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Parse STIX data using official library with backward-compatible output."""
        
    def _parse_with_stix2_library(self, stix_data: Dict[str, Any]) -> List[STIXDomainObject]:
        """Use official library to parse STIX objects."""
        
    def _extract_entity_from_stix_object(self, stix_obj: STIXDomainObject, entity_type: str) -> Dict[str, Any]:
        """Extract entity data from official STIX2 library objects."""
```

#### Method Implementations

**parse() Method**:
- Use `stix2.parse()` or `stix2.Bundle()` to parse the STIX data
- Leverage library's error handling for malformed data
- Maintain existing return format for backward compatibility

**Entity Extraction Methods**:
- Replace custom field extraction with library object property access
- Use library's built-in validation instead of manual checks
- Maintain existing data structure format

### Error Handling Strategy

#### Library Error Integration
```python
from stix2.exceptions import (
    STIXError,
    InvalidValueError, 
    MissingPropertiesError,
    ExtraPropertiesError
)

def _handle_stix_errors(self, stix_data: Dict[str, Any]) -> List[STIXDomainObject]:
    """Robust error handling using official library exceptions."""
    try:
        # Use official library parsing
        bundle = Bundle(stix_data)
        return bundle.objects
    except STIXError as e:
        logger.error(f"STIX validation error: {e}")
        # Graceful degradation - attempt to parse individual objects
        return self._parse_individual_objects(stix_data)
    except Exception as e:
        logger.error(f"Unexpected parsing error: {e}")
        return []
```

#### Validation Strategy
- **Schema Validation**: Use library's built-in STIX schema validation
- **Property Validation**: Leverage library's property type checking
- **Relationship Validation**: Use library's relationship validation
- **Graceful Degradation**: Continue processing valid objects when some fail

### Data Models and Processing

#### STIX Object Type Mapping
```python
# Leverage library's type system
STIX_TYPE_HANDLERS = {
    'x-mitre-tactic': self._process_tactic,
    'attack-pattern': self._process_technique,
    'intrusion-set': self._process_group, 
    'course-of-action': self._process_mitigation
}

def _process_technique(self, stix_obj: AttackPattern) -> Dict[str, Any]:
    """Process technique using library's AttackPattern object."""
    return {
        'id': self._extract_mitre_id(stix_obj),
        'name': stix_obj.name,
        'description': stix_obj.description,
        'platforms': getattr(stix_obj, 'x_mitre_platforms', []),
        'tactics': self._extract_tactics_from_kill_chain(stix_obj.kill_chain_phases),
        'mitigations': []  # Populated by relationship analysis
    }
```

#### Enhanced Data Extraction
- **Type Safety**: Use library's strongly-typed objects
- **Property Access**: Use object properties instead of dictionary access
- **Validation**: Automatic validation through library object creation
- **Extensibility**: Easy addition of new STIX properties

### Relationship Processing Enhancement

#### Current Relationship Handling
```python
# Current custom approach
def _handle_relationship(self, relationship_obj: Dict[str, Any]):
    source_ref = relationship_obj.get('source_ref')
    target_ref = relationship_obj.get('target_ref')
    # Custom relationship processing...
```

#### New Library-Based Approach
```python
from stix2 import Relationship

def _handle_relationship(self, relationship_obj: Relationship):
    """Process relationships using official library objects."""
    return {
        'type': relationship_obj.relationship_type,
        'source_ref': relationship_obj.source_ref,
        'target_ref': relationship_obj.target_ref,
        'created': relationship_obj.created,
        'modified': getattr(relationship_obj, 'modified', None)
    }
```

## Testing Strategy

### Test Migration Approach

#### Existing Test Compatibility
- **No Test Changes**: All existing tests should pass without modification
- **Same Input/Output**: Maintain identical input/output contracts
- **Performance Validation**: Ensure no significant performance degradation

#### New Test Categories

**Library Integration Tests**:
```python
def test_stix2_library_parsing():
    """Test that official library correctly parses STIX data."""
    
def test_stix2_error_handling():
    """Test library's error handling capabilities."""
    
def test_stix2_validation():
    """Test library's validation features."""
```

**Backward Compatibility Tests**:
```python
def test_output_format_unchanged():
    """Ensure refactored parser produces identical output format."""
    
def test_all_mcp_tools_still_work():
    """Verify all 8 MCP tools work with refactored parser."""
```

**Error Handling Tests**:
```python
def test_malformed_stix_handling():
    """Test handling of malformed STIX data using library errors."""
    
def test_graceful_degradation():
    """Test system continues working when some objects fail validation."""
```

### Performance Testing
- **Parsing Speed**: Compare parsing performance before/after
- **Memory Usage**: Ensure library doesn't significantly increase memory usage
- **Response Times**: Verify MCP tool response times remain acceptable

## Implementation Considerations

### Dependency Management

#### Adding STIX2 Library
```toml
# pyproject.toml
dependencies = [
    "stix2>=3.0.0",  # Official STIX 2.x library
    # ... existing dependencies
]
```

#### Version Compatibility
- **Python Compatibility**: Ensure STIX2 library supports Python 3.8+
- **Dependency Conflicts**: Check for conflicts with existing dependencies
- **Security Updates**: Use latest stable version for security patches

### Migration Strategy

#### Phase 1: Library Integration
1. Add `stix2` library to dependencies
2. Create new parsing methods using the library
3. Maintain existing methods as fallback

#### Phase 2: Gradual Migration
1. Replace custom parsing logic method by method
2. Run comprehensive tests after each method replacement
3. Maintain backward compatibility throughout

#### Phase 3: Cleanup
1. Remove custom parsing logic once library integration is complete
2. Update documentation to reflect library usage
3. Add examples of extending functionality using library features

### Code Quality Improvements

#### Type Safety
```python
from stix2 import AttackPattern, IntrusionSet, CourseOfAction
from typing import Union

STIXObject = Union[AttackPattern, IntrusionSet, CourseOfAction]

def _extract_entity_from_stix_object(self, stix_obj: STIXObject, entity_type: str) -> Dict[str, Any]:
    """Type-safe entity extraction using library objects."""
```

#### Error Handling
```python
def parse(self, stix_data: Dict[str, Any], entity_types: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Parse with comprehensive error handling."""
    try:
        return self._parse_with_library(stix_data, entity_types)
    except STIXError as e:
        logger.error(f"STIX parsing error: {e}")
        return self._fallback_parsing(stix_data, entity_types)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {entity_type: [] for entity_type in entity_types}
```

### Future Extensibility

#### Adding New STIX Object Types
```python
# Easy extension using library's type system
from stix2 import Malware, Tool

EXTENDED_TYPE_MAPPING = {
    'malware': 'malware',
    'tool': 'tools'
}

def _process_malware(self, stix_obj: Malware) -> Dict[str, Any]:
    """Process malware objects using library's Malware class."""
    return {
        'id': self._extract_mitre_id(stix_obj),
        'name': stix_obj.name,
        'description': stix_obj.description,
        'labels': stix_obj.labels
    }
```

#### Advanced Relationship Processing
```python
def _build_relationship_graph(self, relationships: List[Relationship]) -> Dict[str, List[str]]:
    """Build relationship graphs using library's relationship objects."""
    graph = defaultdict(list)
    for rel in relationships:
        graph[rel.source_ref].append({
            'target': rel.target_ref,
            'type': rel.relationship_type,
            'confidence': getattr(rel, 'confidence', None)
        })
    return dict(graph)
```

## Security Considerations

### Input Validation
- **Library Validation**: Leverage STIX2 library's built-in validation
- **Schema Compliance**: Ensure all parsed objects comply with STIX 2.1 schema
- **Malicious Data**: Use library's security features to handle potentially malicious STIX data

### Error Information Disclosure
- **Safe Error Messages**: Use library's error handling to avoid information disclosure
- **Logging**: Log detailed errors for debugging while returning safe messages to users
- **Validation Failures**: Handle validation failures gracefully without exposing internal details

## Deployment Considerations

### Backward Compatibility
- **API Compatibility**: All existing API endpoints continue to work unchanged
- **Data Format**: Output data format remains identical
- **Configuration**: No configuration changes required

### Performance Impact
- **Parsing Performance**: Official library may have different performance characteristics
- **Memory Usage**: Monitor memory usage with the new library
- **Caching**: Maintain existing caching strategies

### Rollback Strategy
- **Feature Flags**: Implement feature flag to switch between old/new parser
- **Gradual Rollout**: Deploy to staging first, then production
- **Monitoring**: Monitor error rates and performance metrics during rollout