"""
PACT Position Specification (Pos) Class

Provides canonical PACT v0.1.0 selector syntax support for precise component placement
in the context tree. Supports coordinates, keys, types, attributes, and behaviors.
"""

from typing import Optional, Any, Dict
from ..data_structures.coordinates import Coordinates


class Pos:
    """
    Position specification using canonical PACT selector syntax.
    
    Builds PACT v0.1.0 compliant selectors like:
    - "(d0, 1) [ttl=3]" - Coordinate with behavior
    - "#status_bar {priority='5'}" - Key with attributes  
    - ".block {role='user'} [ttl=5]" - Type with attributes and behavior
    - "(d0) {nodeType='summary'}" - Coordinate with attributes
    """
    
    def __init__(self, 
                 *selector_parts: str, 
                 ttl: Optional[int] = None,
                 cad: Optional[int] = None,
                 cadence: Optional[int] = None,
                 **attrs: Any
                 ):
        """
        Create position specification using canonical PACT v0.1.0 selector syntax.
        
        Args:
            *selector_parts: Variable selector components (joined with spaces)
            ttl: Time-to-live in turns (optional)
            cad: Cadence interval in turns (optional)
            cadence: Alias for cad (optional)
            **attrs: PACT attributes as keyword arguments (all values converted to strings)
        
        Examples:
            Pos("d0, 1", ttl=3)                                    # → "(d0, 1) [ttl=3]"
            Pos("d-1", ttl=10, cad=2)                              # → "(d-1) [ttl=10 cad=2]"
            Pos("#status_bar", priority="5")                       # → "#status_bar {priority='5'}"
            Pos(".block", role="user", ttl=5)                      # → ".block {role='user'} [ttl=5]"
            Pos("d0", nodeType="summary")                          # → "(d0) {nodeType='summary'}"
            Pos("d2, 3, 1")                                        # → "(d2, 3, 1)"
        """
        # Store ttl and cadence as attributes
        self.ttl = ttl
        self.cadence = cadence if cadence is not None else cad
        
        # Store attributes
        self.attrs = attrs
        
        # Parse coordinates from selector parts
        self.coordinates = None
        self._coordinate_str = None
        
        # Join selector parts with spaces
        selector_str = " ".join(selector_parts) if selector_parts else ""
        
        # Build base selector with parentheses for coordinates
        if not selector_str:
            # Empty selector is invalid
            raise ValueError("Position selector cannot be empty. Must specify coordinates, key (#), type (.), or attributes {}")
        elif selector_str.startswith(('#', '.', '{')):
            # Key, type, or attribute selectors - use as-is
            base_selector = selector_str
        elif selector_str.startswith('d') or selector_str.startswith('('):
            # Coordinate selectors - ensure proper parentheses and parse coordinates
            if selector_str.startswith('(') and selector_str.endswith(')'):
                base_selector = selector_str  # Already properly formatted
                coord_content = selector_str[1:-1]  # Remove parentheses
            else:
                base_selector = f"({selector_str})"
                coord_content = selector_str
            
            # Parse coordinates from the content
            try:
                # Validate coordinate format strictly
                self._coordinate_str = coord_content
                self.coordinates = Coordinates.validate(coord_content.strip())
            except (ValueError, AttributeError):
                # If coordinate parsing fails, leave coordinates as None
                pass
        else:
            # Other selectors (complex queries, etc.) - validate they're not obviously invalid
            if selector_str and not selector_str.startswith(('#', '.', '@', '^')):
                # If it's not empty and doesn't start with valid selector characters, it's invalid
                raise ValueError(f'Invalid selector format: {selector_str}')
            base_selector = selector_str
        
        # Add attributes if specified
        if attrs:
            attr_parts = []
            for key, value in attrs.items():
                # Convert all values to strings and properly quote them
                if isinstance(value, str):
                    attr_parts.append(f"{key}='{value}'")
                else:
                    attr_parts.append(f"{key}='{str(value)}'")
            attr_string = ", ".join(attr_parts)
            base_selector = f"{base_selector} {{{attr_string}}}"
        
        # Add behaviors if specified
        behaviors = []
        if self.ttl is not None:
            behaviors.append(f"ttl={self.ttl}")
        if self.cadence is not None:
            behaviors.append(f"cad={self.cadence}")
            
        if behaviors:
            behavior_string = " ".join(behaviors)
            self.selector = f"{base_selector} [{behavior_string}]"
        else:
            self.selector = base_selector
    
    def __str__(self) -> str:
        """Return the built PACT selector string."""
        return self.selector
    
    def __repr__(self) -> str:
        """Return debug representation."""
        return f"Pos('{self.selector}')"
    
    @classmethod
    def from_string(cls, selector_string: str) -> 'Pos':
        """
        Create Pos instance from a pre-built PACT selector string.
        
        Args:
            selector_string: Complete PACT selector like "(d0, 1) [ttl=3]"
            
        Returns:
            Pos instance with the selector
        """
        instance = cls.__new__(cls)
        instance.selector = selector_string
        return instance
    
