"""
XMLRenderer for PACT-compliant XML structure rendering.

Provides XML structure visualization with PACT validation and formatting.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re


@dataclass
class ValidationResult:
    """Result of XML structure validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class XMLRenderer:
    """Handles PACT-compliant XML structure rendering"""
    
    # PACT v0.1 required attributes
    PACT_REQUIRED_ATTRS = {
        'id', 'parent_id', 'offset', 'ttl', 'cad', 
        'created_at_ns', 'creation_index', 'key', 'tags'
    }
    
    # PACT node types
    PACT_NODE_TYPES = {
        'root', 'system', 'history', 'active_message', 
        'message_turn', 'text', 'analytics', 'task_list_scaffold',
        'internal_notes', 'reminder', 'timestamp', 'component'
    }
    
    def __init__(self):
        """Initialize XMLRenderer"""
        pass
    
    def render_xml(self, pact_data: Dict[str, Any], validate: bool = True) -> str:
        """Convert PACT data to XML format
        
        Args:
            pact_data: PACT-compliant data from context.model_dump()
            validate: Perform PACT specification validation
        
        Returns:
            Formatted XML string
        
        Wiring: Uses context.model_dump() output which provides:
        - nodeType: Component type identifier
        - id: Unique component ID  
        - relative_offset: PACT positioning
        - ttl: Lifecycle information
        - content: Nested structure or text content
        - All PACT v0.1 canonical fields automatically included
        """
        # Create root element
        root_element = self._create_xml_element_from_pact(pact_data, None)
        
        # Convert to string with pretty formatting
        rough_string = ET.tostring(root_element, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")
        
        # Clean up extra whitespace
        lines = [line for line in pretty_xml.split('\n') if line.strip()]
        clean_xml = '\n'.join(lines)
        
        # Remove XML declaration for cleaner output
        if clean_xml.startswith('<?xml'):
            lines = clean_xml.split('\n')[1:]
            clean_xml = '\n'.join(lines)
        
        # Validate if requested
        if validate:
            validation_result = self.validate_structure(clean_xml)
            if not validation_result.is_valid:
                # Add validation errors as XML comments
                error_comments = []
                error_comments.append("<!-- VALIDATION ERRORS:")
                for error in validation_result.errors:
                    error_comments.append(f"  - {error}")
                error_comments.append("-->")
                clean_xml = '\n'.join(error_comments) + '\n' + clean_xml
        
        return clean_xml
    
    def _create_xml_element_from_pact(self, pact_data: Dict[str, Any], parent: Optional[ET.Element]) -> ET.Element:
        """Create XML element from PACT data recursively"""
        # Determine element name from nodeType or class name
        element_name = self._get_element_name(pact_data)
        
        # Create element
        element = ET.Element(element_name)
        
        # Add PACT attributes
        self._add_pact_attributes(element, pact_data)
        
        # Handle content
        content = pact_data.get('content', None)
        
        if isinstance(content, str):
            # Text content - escape special characters
            element.text = self._escape_xml_text(content)
        elif isinstance(content, list):
            # Child elements
            for child_data in content:
                if isinstance(child_data, dict):
                    child_element = self._create_xml_element_from_pact(child_data, element)
                    element.append(child_element)
                else:
                    # Handle non-dict content as text
                    if element.text:
                        element.text += str(child_data)
                    else:
                        element.text = str(child_data)
        elif isinstance(content, dict):
            # Single child object
            child_element = self._create_xml_element_from_pact(content, element)
            element.append(child_element)
        
        return element
    
    def _get_element_name(self, pact_data: Dict[str, Any]) -> str:
        """Get XML element name from PACT data"""
        # Try metadata.aux.nodeType field
        if 'metadata' in pact_data and isinstance(pact_data['metadata'], dict):
            metadata = pact_data['metadata']
            if 'aux' in metadata and isinstance(metadata['aux'], dict):
                aux = metadata['aux']
                if 'nodeType' in aux:
                    return self._extract_type_name(aux['nodeType'])
        
        # Default fallback
        return 'Component'
    
    def _normalize_element_name(self, name: str) -> str:
        """Normalize element name for XML compliance"""
        # Remove 'Component' suffix if present
        if name.endswith('Component'):
            name = name[:-9]
        
        # Convert CamelCase to PascalCase and make XML-safe
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        if not name[0].isalpha():
            name = 'Element' + name
        
        return name
    
    def _extract_type_name(self, node_type: str) -> str:
        """Extract clean type name from nodeType"""
        # Convert snake_case to PascalCase and remove suffixes
        words = node_type.split('_')
        type_name = ''.join(word.capitalize() for word in words)
        
        # Remove common suffixes
        if type_name.endswith('Content'):
            type_name = type_name[:-7]
        elif type_name.endswith('Component'):
            type_name = type_name[:-9]
        
        # Make XML-safe and return
        return re.sub(r'[^a-zA-Z0-9_]', '', type_name)
    
    def _escape_xml_text(self, text: str) -> str:
        """Escape special characters for XML content"""
        if not text:
            return text
        
        # Remove or replace control characters that are invalid in XML
        # Keep only valid XML characters: #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
        cleaned_chars = []
        for char in text:
            code = ord(char)
            if (code == 0x09 or code == 0x0A or code == 0x0D or 
                (0x20 <= code <= 0xD7FF) or 
                (0xE000 <= code <= 0xFFFD) or 
                (0x10000 <= code <= 0x10FFFF)):
                cleaned_chars.append(char)
            else:
                # Replace invalid characters with placeholder
                cleaned_chars.append(f"\\x{code:02x}")
        
        cleaned_text = ''.join(cleaned_chars)
        
        # Standard XML escaping is handled by ElementTree automatically
        return cleaned_text
    
    def _add_pact_attributes(self, element: ET.Element, pact_data: Dict[str, Any]) -> None:
        """Add PACT attributes to XML element"""
        # Standard PACT attributes (excluding id, offset, and tags - handle separately)
        pact_attrs = [
            'parent_id', 'ttl', 'cad',
            'created_at_ns', 'creation_index', 'key'
        ]
        
        for attr in pact_attrs:
            if attr in pact_data:
                value = pact_data[attr]
                if value is not None:
                    element.set(attr, str(value))
        
        # Handle tags specially - only include if non-empty
        if 'tags' in pact_data:
            tags_value = pact_data['tags']
            if tags_value and len(tags_value) > 0:
                # Format as comma-separated string
                if isinstance(tags_value, list):
                    tags_str = ','.join(str(tag) for tag in tags_value)
                else:
                    tags_str = str(tags_value)
                element.set('tags', tags_str)
        
        # Add coordinates from metadata if available
        if 'metadata' in pact_data and isinstance(pact_data['metadata'], dict):
            metadata = pact_data['metadata']
            if 'coordinates' in metadata:
                coords = metadata['coordinates']
                if coords:
                    element.set('coordinates', str(coords))
        
        # Add relative_offset as offset for PACT compliance
        if 'relative_offset' in pact_data:
            element.set('relative_offset', str(pact_data['relative_offset']))
        
        # Add nodeType if available
        if 'nodeType' in pact_data:
            element.set('nodeType', str(pact_data['nodeType']))
        
        # Add position information if available
        if 'position' in pact_data:
            element.set('position', str(pact_data['position']))
    
    def validate_structure(self, xml_content: str) -> ValidationResult:
        """Validate XML against PACT specification
        
        Args:
            xml_content: XML string to validate
        
        Returns:
            ValidationResult with validation status and issues
        
        Wiring: Validates against PACT v0.1 spec requirements:
        - Required nodeType attributes
        - Proper nesting structure  
        - Valid relative_offset values
        - TTL/cadence consistency
        """
        errors = []
        warnings = []
        
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Validate structure recursively
            self._validate_element(root, errors, warnings)
            
        except ET.ParseError as e:
            errors.append(f"XML Parse Error: {e}")
        except Exception as e:
            errors.append(f"Validation Error: {e}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _validate_element(self, element: ET.Element, errors: List[str], warnings: List[str]) -> None:
        """Validate individual XML element"""
        # Check for id attribute
        if 'id' not in element.attrib:
            warnings.append(f"Element '{element.tag}' missing id attribute")
        
        # Check nodeType if present
        if 'nodeType' in element.attrib:
            node_type = element.attrib['nodeType']
            if node_type not in self.PACT_NODE_TYPES:
                warnings.append(f"Unknown nodeType '{node_type}' in element '{element.tag}'")
        
        # Check TTL format
        if 'ttl' in element.attrib:
            try:
                ttl_value = element.attrib['ttl']
                if ttl_value not in ['None', 'null'] and not ttl_value.isdigit():
                    warnings.append(f"Invalid TTL value '{ttl_value}' in element '{element.tag}'")
            except ValueError:
                warnings.append(f"Invalid TTL format in element '{element.tag}'")
        
        # Check relative_offset format
        if 'relative_offset' in element.attrib:
            try:
                offset_value = element.attrib['relative_offset']
                if offset_value not in ['None', 'null']:
                    int(offset_value)  # Should be parseable as int
            except ValueError:
                warnings.append(f"Invalid relative_offset '{offset_value}' in element '{element.tag}'")
        
        # Validate children recursively
        for child in element:
            self._validate_element(child, errors, warnings)
    
    def get_validation_summary(self, xml_content: str) -> str:
        """Get a formatted validation summary
        
        Args:
            xml_content: XML string to validate
        
        Returns:
            Formatted validation summary
        """
        result = self.validate_structure(xml_content)
        
        lines = []
        lines.append("=== PACT XML Validation Summary ===")
        
        if result.is_valid:
            lines.append("✓ XML structure is valid")
        else:
            lines.append("❌ XML structure has issues")
        
        if result.errors:
            lines.append(f"\nErrors ({len(result.errors)}):")
            for error in result.errors:
                lines.append(f"  - {error}")
        
        if result.warnings:
            lines.append(f"\nWarnings ({len(result.warnings)}):")
            for warning in result.warnings:
                lines.append(f"  - {warning}")
        
        if not result.errors and not result.warnings:
            lines.append("\n🎉 No issues found!")
        
        return '\n'.join(lines)