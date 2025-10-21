from typing import List,  Tuple, Iterator


class Coordinates:
    """
    PACT coordinate system with arbitrary depth and arithmetic operations.
    Replaces component.metadata.coordinates tuple.
    
    Examples:
        Coordinates(-1, 0)       # system_header.content[0]
        Coordinates(0, 2)        # active_message.content[2]
        Coordinates(1, 0, 3, 2)  # conversation[0].content[3].content[2]
    """
    
    def __init__(self, *coords: int):
        """
        Create PACT coordinates with arbitrary depth.
        
        Args:
            *coords: Variable number of integer coordinates
        """
        self.coords = tuple(c if isinstance(c, tuple) else int(c) for c in coords)
    
    # Array-like interface for backward compatibility
    def __getitem__(self, index: int) -> int:
        """Get coordinate at specific index."""
        return self.coords[index]
    
    def __len__(self) -> int:
        """Get number of coordinates."""
        return len(self.coords)
    
    def __iter__(self) -> Iterator[int]:
        """Iterate over coordinates."""
        return iter(self.coords)
    
    def __eq__(self, other) -> bool:
        """Compare with other Coordinates, tuple, or list."""
        if isinstance(other, Coordinates):
            return self.coords == other.coords
        if isinstance(other, (tuple, list)):
            return self.coords == tuple(other)
        return False
    
    def __lt__(self, other) -> bool:
        """Less than comparison for sorting."""
        if isinstance(other, Coordinates):
            return self.coords < other.coords
        if isinstance(other, (tuple, list)):
            return self.coords < tuple(other)
        return NotImplemented
    
    def __le__(self, other) -> bool:
        """Less than or equal comparison."""
        return self == other or self < other
    
    def __gt__(self, other) -> bool:
        """Greater than comparison."""
        if isinstance(other, Coordinates):
            return self.coords > other.coords
        if isinstance(other, (tuple, list)):
            return self.coords > tuple(other)
        return NotImplemented
    
    def __ge__(self, other) -> bool:
        """Greater than or equal comparison."""
        return self == other or self > other
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"Coordinates{self.coords}"
    
    def __str__(self) -> str:
        """Human-readable representation."""
        if not self.coords:
            return "()"
        
        # Handle first coordinate (depth) which may be a range tuple
        first_coord_raw = self.coords[0]
        if isinstance(first_coord_raw, tuple):
            # Range syntax: (start, end)
            start, end = first_coord_raw
            if end == '*':  # Special "last" marker
                first_coord = f"d{start}..d*"
            else:
                first_coord = f"d{start}..d{end}"
        else:
            # Single depth
            first_coord = f"d{first_coord_raw}"
        
        rest_coords = map(str, self.coords[1:])
        all_coords = [first_coord] + list(rest_coords)
        return f"({','.join(all_coords)})"
    
    # PACT arithmetic operations
    def increment_depth(self, depth_index: int = 0) -> 'Coordinates':
        """
        ODI increment: (0,1,0) -> (1,1,0) when demoting component.
        
        Args:
            depth_index: Which coordinate index to increment (default: 0)
            
        Returns:
            New Coordinates with incremented depth
        """
        new_coords = list(self.coords)
        if depth_index < len(new_coords):
            new_coords[depth_index] += 1
        return Coordinates(*new_coords)
    
    def decrement_depth(self, depth_index: int = 0) -> 'Coordinates':
        """
        ODI decrement: (1,1,0) -> (0,1,0) when promoting component.
        
        Args:
            depth_index: Which coordinate index to decrement (default: 0)
            
        Returns:
            New Coordinates with decremented depth
        """
        new_coords = list(self.coords)
        if depth_index < len(new_coords):
            new_coords[depth_index] -= 1
        return Coordinates(*new_coords)
    
    def shift_positions(self, amount: int, start_index: int = 1) -> 'Coordinates':
        """
        Shift positions when inserting: (0,1,0) -> (0,2,0).
        
        Args:
            amount: How much to shift by
            start_index: Start shifting from this index (default: 1)
            
        Returns:
            New Coordinates with shifted positions
        """
        new_coords = list(self.coords)
        for i in range(start_index, len(new_coords)):
            new_coords[i] += amount
        return Coordinates(*new_coords)
    
    def with_child(self, *child_coords: int) -> 'Coordinates':
        """
        Extend coordinate chain: (0,1) + (2,3) = (0,1,2,3).
        
        Args:
            *child_coords: Coordinates to append
            
        Returns:
            New Coordinates with child coordinates appended
        """
        return Coordinates(*(self.coords + child_coords))
    
    def parent(self) -> 'Coordinates':
        """
        Get parent coordinates: (0,1,2,3) -> (0,1,2).
        
        Returns:
            New Coordinates representing parent (all but last coordinate)
        """
        return Coordinates(*self.coords[:-1]) if self.coords else Coordinates()
    
    # Pydantic serialization support
    @classmethod
    def __get_validators__(cls):
        """Pydantic validator registration."""
        yield cls.validate
    
    @classmethod
    def validate(cls, value, validation_info=None) -> 'Coordinates':
        """
        Convert various inputs to Coordinates.
        
        Args:
            value: Input to convert (Coordinates, list, tuple, string)
            
        Returns:
            Coordinates object
            
        Raises:
            ValueError: If value cannot be converted
        """
        if isinstance(value, cls):
            return value
        if isinstance(value, (list, tuple)):
            return cls(*value)
        if isinstance(value, str):
            # Parse "(0,1,2)" or "0,1,2" with strict validation
            original_value = value
            value = value.strip()
            
            # Reject empty strings
            if not value:
                raise ValueError(f'Cannot convert empty string to Coordinates')
            
            # Validate no tabs or newlines in input
            if '\t' in value:
                raise ValueError(f'Tabs not allowed in coordinate string: {original_value}')
            if '\n' in value or '\r' in value:
                raise ValueError(f'Newlines not allowed in coordinate string: {original_value}')
            
            # Handle parenthesized format: "(d0,1,2)"
            if value.startswith('(') and value.endswith(')'):
                # Validate proper parentheses pairing
                if value.count('(') != 1 or value.count(')') != 1:
                    raise ValueError(f'Invalid parentheses in coordinate string: {original_value}')
                coords_str = value[1:-1]  # Remove outer parentheses
            elif value.startswith('(') or value.endswith(')'):
                # Mismatched parentheses
                raise ValueError(f'Mismatched parentheses in coordinate string: {original_value}')
            else:
                # Non-parenthesized format: "d0,1,2"
                coords_str = value
            
            # Reject empty coordinate content
            if not coords_str.strip():
                raise ValueError(f'Empty coordinate content in: {original_value}')
            
            # Parse coordinates with PACT depth validation
            try:
                coord_parts = coords_str.split(',')
                coords = []
                
                # Handle special case: "dN" alone behavior depends on parentheses
                if len(coord_parts) == 1:
                    part = coord_parts[0].strip()
                    if part.startswith('d'):
                        # Check if original had parentheses - shorthand expansion only for parenthesized form
                        if original_value.strip().startswith('(') and original_value.strip().endswith(')'):
                            # "(dN)" format expands to (dN, 0, 0) - message container shorthand
                            depth_str = part[1:]
                            if not depth_str:
                                raise ValueError(f'Depth missing number after "d": {part}')
                            if not depth_str.lstrip('-').isdigit():
                                raise ValueError(f'Invalid depth number "{depth_str}" in: {part}')
                            # dN shorthand expands to (dN, 0, 0) - message container for turn N
                            return cls(int(depth_str), 0, 0)
                        else:
                            # "dN" format (without parentheses) is invalid - must have positions
                            raise ValueError(f'Single depth coordinate is invalid, must include positions: {original_value}')
                    else:
                        # Raw integer format is invalid - must have "d" prefix
                        raise ValueError(f'Coordinates must start with depth "d" prefix, got: {part}')
                
                # Handle multi-coordinate case: "dN,pos1,pos2,..." ONLY
                for i, part in enumerate(coord_parts):
                    # Allow reasonable whitespace
                    part = part.strip()
                    if not part:  # Empty part from double comma, trailing comma, etc.
                        raise ValueError(f'Empty coordinate part in: {original_value}')
                    
                    # First coordinate MUST be depth with "d" prefix
                    if i == 0:
                        if not part.startswith('d'):
                            raise ValueError(f'First coordinate must be depth with "d" prefix, got: {part}')
                        depth_str = part[1:]  # Remove 'd' prefix
                        if not depth_str:
                            raise ValueError(f'Depth missing number after "d": {part}')
                        
                        # Check for range syntax: d0..d* or d0..d5
                        if '..' in depth_str:
                            range_parts = depth_str.split('..')
                            if len(range_parts) != 2:
                                raise ValueError(f'Invalid depth range syntax in: {part}')
                            
                            start_str, end_str = range_parts
                            
                            # Validate start depth
                            if not start_str.lstrip('-').isdigit():
                                raise ValueError(f'Invalid start depth "{start_str}" in range: {part}')
                            start_depth = int(start_str)
                            
                            # Handle end depth - can be number or '*' for last element
                            if end_str == '*':
                                # Special marker for "last element" - store as string '*'
                                end_depth = '*'
                            elif end_str == 'd*':
                                # Also handle 'd*' format
                                end_depth = '*'
                            elif end_str.startswith('d'):
                                # Remove 'd' prefix from end depth
                                end_num_str = end_str[1:]
                                if not end_num_str.lstrip('-').isdigit():
                                    raise ValueError(f'Invalid end depth number "{end_num_str}" in range: {part}')
                                end_depth = int(end_num_str)
                            elif end_str.lstrip('-').isdigit():
                                end_depth = int(end_str)
                            else:
                                raise ValueError(f'Invalid end depth "{end_str}" in range: {part}')
                            
                            # Store as a special range tuple in coords
                            coords.append((start_depth, end_depth))
                        else:
                            # Single depth number
                            if not depth_str.lstrip('-').isdigit():
                                raise ValueError(f'Invalid depth number "{depth_str}" in: {part}')
                            coords.append(int(depth_str))
                    else:
                        # Other coordinates are regular integers
                        if not part.lstrip('-').isdigit():
                            raise ValueError(f'Invalid coordinate part "{part}" in: {original_value}')
                        coords.append(int(part))
                
                if not coords:  # Should not happen but double-check
                    raise ValueError(f'No valid coordinates found in: {original_value}')
                    
                return cls(*coords)
            except ValueError as e:
                if 'invalid literal for int()' in str(e):
                    raise ValueError(f'Invalid coordinate format in: {original_value}')
                raise  # Re-raise our custom ValueError messages
        raise ValueError(f'Cannot convert {type(value)} to Coordinates')
    
    def resolve_depth_range(self, max_depth: int) -> 'Coordinates':
        """
        Resolve depth ranges like (d0..d*) to actual coordinates using the current max depth.
        
        Args:
            max_depth: The maximum depth available in the current DepthArray
            
        Returns:
            New Coordinates with resolved depth range
        """
        if not self.coords:
            return self
            
        first_coord = self.coords[0]
        if isinstance(first_coord, tuple):
            start, end = first_coord
            if end == '*':
                # Resolve '*' to actual max depth
                resolved_end = max_depth
            else:
                resolved_end = end
            
            # For now, return with the start depth (could expand to multiple depths later)
            # This is a simple implementation - could be enhanced to return multiple coordinates
            resolved_coords = [start] + list(self.coords[1:])
            return Coordinates(*resolved_coords)
        else:
            # No range to resolve
            return self
    
    def is_depth_range(self) -> bool:
        """Check if this coordinate contains a depth range."""
        return len(self.coords) > 0 and isinstance(self.coords[0], tuple)
    
    def get_depth_range(self):
        """Get the depth range tuple if it exists."""
        if self.is_depth_range():
            return self.coords[0]
        return None

    def serialize(self) -> List[int]:
        """
        Serialize to JSON-compatible list.
        
        Returns:
            List of coordinate integers
        """
        return list(self.coords)
    
    # Properties for backward compatibility with tests
    @property
    def depth(self) -> int:
        """Get the depth (first coordinate)."""
        return self.coords[0] if self.coords else 0
    
    @property
    def positions(self) -> Tuple[int, ...]:
        """Get the positions (all coordinates except the first)."""
        return self.coords[1:] if len(self.coords) > 1 else ()
    
    # PACT depth resolution methods
    def resolve_depth_to_context_index(self) -> int:
        """
        Resolve PACT depth coordinate to actual Context.content index.
        
        PACT depth mapping:
        - d-1 → Context.content[0] (system_header)
        - d0  → Context.content[2] (active_message)  
        - d1+ → Context.content[1] (conversation_history)
        
        Returns:
            Context.content index for the depth
            
        Raises:
            ValueError: If depth is invalid or coordinates are empty
        """
        if len(self.coords) == 0:
            raise ValueError("Cannot resolve depth from empty coordinates")
        
        depth = self.coords[0]
        
        if depth == -1:
            return 0  # system_header
        elif depth == 0:
            return 2  # active_message
        elif depth >= 1:
            return 1  # conversation_history
        else:
            raise ValueError(f"Invalid PACT depth: {depth}. Must be >= -1")
    
    def to_absolute_coordinates(self) -> 'Coordinates':
        """
        Convert PACT coordinates to absolute Context coordinates.
        
        Transforms:
        - (-1, 0) → (0, 0)     # system_header.content[0]
        - (0, 1)  → (2, 1)     # active_message.content[1]
        - (1, 2)  → (1, 2)     # conversation_history.content[2]
        
        Returns:
            New Coordinates with absolute positioning
        """
        if len(self.coords) == 0:
            return Coordinates()
        
        context_index = self.resolve_depth_to_context_index()
        
        # Replace depth with absolute context index
        absolute_coords = (context_index,) + self.coords[1:]
        return Coordinates(*absolute_coords)
    
    def from_absolute_coordinates(self, absolute_coords: 'Coordinates') -> 'Coordinates':
        """
        Convert absolute Context coordinates back to PACT coordinates.
        
        Transforms:
        - (0, 0) → (-1, 0)     # system_header.content[0]
        - (2, 1) → (0, 1)      # active_message.content[1] 
        - (1, 2) → (1, 2)      # conversation_history.content[2]
        
        Args:
            absolute_coords: Coordinates with absolute positioning
            
        Returns:
            New Coordinates with PACT depth positioning
        """
        if len(absolute_coords.coords) == 0:
            return Coordinates()
        
        context_index = absolute_coords.coords[0]
        
        # Map context index back to PACT depth
        if context_index == 0:
            pact_depth = -1  # system_header
        elif context_index == 2:
            pact_depth = 0   # active_message
        elif context_index == 1:
            pact_depth = 1   # conversation_history
        else:
            # Unknown context index, keep as-is
            return absolute_coords
        
        # Replace context index with PACT depth
        pact_coords = (pact_depth,) + absolute_coords.coords[1:]
        return Coordinates(*pact_coords)
    
    @classmethod
    def from_pact_depth(cls, depth: int, *positions: int) -> 'Coordinates':
        """
        Create Coordinates from PACT depth and positions.
        
        Args:
            depth: PACT depth (-1, 0, 1+)
            *positions: Additional coordinate positions
            
        Returns:
            New Coordinates object
            
        Example:
            Coordinates.from_pact_depth(-1, 0)     # system_header.content[0]
            Coordinates.from_pact_depth(0, 1, 2)   # active_message.content[1].content[2]
        """
        return cls(depth, *positions)