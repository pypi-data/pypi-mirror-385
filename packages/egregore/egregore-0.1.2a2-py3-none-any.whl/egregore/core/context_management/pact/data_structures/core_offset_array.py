"""
CoreOffsetArray - Zero-centered array for PACT stack pushing operations.
"""

from typing import List, Optional, Any, Iterator, Generic, TypeVar

T = TypeVar('T')

class NegativeOffsetStack(List[T]):
    def __setitem__(self, offset: int, value: T) -> None:
        assert offset < 0, f"NegativeOffset only accepts negative offsets, got {offset}"
        index = abs(offset) - 1
        if index == len(self):
            self.append(value)
        else:
            super().__setitem__(index, value)
    
    def __getitem__(self, offset: int) -> T:
        assert offset < 0, f"NegativeOffset only accepts negative offsets, got {offset}"
        index = abs(offset) - 1
        if index >= len(self):
            raise IndexError(f"No item at offset {offset}")
        return super().__getitem__(index)
    
    def __contains__(self, offset: int) -> bool:
        assert offset < 0, f"NegativeOffset only accepts negative offsets, got {offset}"
        index = abs(offset) - 1
        return index < len(self)
    
    def insert(self, offset: int, value: T) -> int:
        """Insert at offset, pushing existing items deeper."""
        assert offset < 0, f"NegativeOffset only accepts negative offsets, got {offset}"
        
        target_index = abs(offset) - 1
        if target_index <= len(self):
            super().insert(target_index, value)
            return offset
        else:
            self.append(value)
            return -(len(self))

class PositiveOffsetStack(List[T]):
    def __setitem__(self, offset: int, value: T) -> None:
        assert offset > 0, f"PositiveOffset only accepts positive offsets, got {offset}"
        index = offset - 1
        if index == len(self):
            self.append(value)
        else:
            super().__setitem__(index, value)
    
    def __getitem__(self, offset: int) -> T:
        assert offset > 0, f"PositiveOffset only accepts positive offsets, got {offset}"
        index = offset - 1
        if index >= len(self):
            raise IndexError(f"No item at offset {offset}")
        return super().__getitem__(index)
    
    def __contains__(self, offset: int) -> bool:
        assert offset > 0, f"PositiveOffset only accepts positive offsets, got {offset}"
        index = offset - 1
        return index < len(self)
    
    def insert(self, offset: int, value: T) -> int:
        """Insert at offset, pushing existing items higher."""
        assert offset > 0, f"PositiveOffset only accepts positive offsets, got {offset}"
        
        target_index = offset - 1
        if target_index <= len(self):
            super().insert(target_index, value)
            return offset
        else:
            self.append(value)
            return len(self)

class CoreOffsetArray(Generic[T]):
    """Zero-centered array with automatic Core Offset Layout Rule enforcement.
    Rule: Position 0 must exist before any other positions.
    """
    def __init__(self) -> None:
        self.pre: NegativeOffsetStack[T] = NegativeOffsetStack()
        self.post: PositiveOffsetStack[T] = PositiveOffsetStack()
        self._parent_component: Optional[Any] = None
        # Core Offset Layout Rule: Position 0 is reserved but not auto-created
        # self.core will be set when first item is added
    
    def __getitem__(self, offset: int) -> T:
        if offset == 0:
            if hasattr(self, 'core'):
                return self.core
            raise KeyError(f"No item at offset {offset}")
        elif offset < 0:
            item = self.pre[offset]
            if item is None:
                raise KeyError(f"No item at offset {offset}")
            return item
        else:
            item = self.post[offset]
            if item is None:
                raise KeyError(f"No item at offset {offset}")
            return item

    def __setitem__(self, requested_offset: int, value: T) -> None:
        """Replace existing item at offset - raises error if offset doesn't exist."""
        if requested_offset == 0:
            if not hasattr(self, 'core'):
                raise KeyError(f"No item at offset {requested_offset}")
            self.core = value
        elif requested_offset < 0:
            if requested_offset not in self.pre:
                raise KeyError(f"No item at offset {requested_offset}")
            self.pre[requested_offset] = value
        else:
            if requested_offset not in self.post:
                raise KeyError(f"No item at offset {requested_offset}")
            self.post[requested_offset] = value
    
    def insert(self, requested_offset: int, value: T) -> int:
        """Stack pushing insertion - pushes existing items away from requested position."""
        if requested_offset == 0:
            if not hasattr(self, 'core'):
                self.core = value
                return 0
            else:
                # Stack pushing: move existing core to post[0], insert new at core
                existing_core = self.core
                self.core = value
                self.post.insert(1, existing_core)  # Insert at position 1, pushing others
                return 0
        else:
            # Core Offset Layout Rule: Position 0 must exist first
            if not hasattr(self, 'core'):
                self.core = value
                return 0
            
            if requested_offset < 0:
                return self.pre.insert(requested_offset, value)
            else:
                return self.post.insert(requested_offset, value)
    
    def append(self, value: T, requested_offset: int = 0) -> int:
        """Bidirectional stack append - append in requested direction."""
        if not hasattr(self, 'core') or self.core is None:
            self.core = value
            # Register component if it has context reference
            self._register_if_has_context(value)
            return 0

        # Bidirectional stack behavior: append in the requested direction
        if requested_offset < 0:
            # Append to negative stack (next available negative position)
            self.pre.append(value)
            # Register component if it has context reference
            self._register_if_has_context(value)
            return -(len(self.pre))
        else:
            # Append to positive stack (next available positive position)
            self.post.append(value)
            # Register component if it has context reference
            self._register_if_has_context(value)
            return len(self.post)

    def _register_if_has_context(self, value: T) -> None:
        """Register component with context registry if it has a context reference."""
        try:
            if hasattr(value, '_context_ref') and value._context_ref is not None:
                context = value._context_ref
                if hasattr(context, '_registry'):
                    context._registry.register_component(value)
        except Exception:
            pass  # Silent fallback - registration is optional

    def __contains__(self, offset: int) -> bool:
        try:
            self[offset]
            return True
        except (KeyError, AssertionError, IndexError):
            return False
    
    def __len__(self) -> int:
        return (1 if hasattr(self, 'core') and self.core is not None else 0) + len(self.pre) + len(self.post)
    
    def __iter__(self) -> Iterator[T]:
        items = []
        for i, item in enumerate(self.pre):
            items.append((-(i + 1), item))
        if hasattr(self, 'core') and self.core is not None:
            items.append((0, self.core))
        for i, item in enumerate(self.post):
            items.append((i + 1, item))
        items.sort()
        return iter(item for _, item in items)
    
    def get_offsets(self) -> List[int]:
        offsets = []
        for i in range(len(self.pre)):
            offsets.append(-(i + 1))
        if hasattr(self, 'core'):
            offsets.append(0)
        for i in range(len(self.post)):
            offsets.append(i + 1)
        return sorted(offsets)
    
    def remove(self, offset: int) -> None:
        """Remove item at offset with automatic shifting."""
        if offset == 0:
            if not hasattr(self, 'core') or self.core is None:
                raise KeyError(f"No item at offset {offset}")
            if len(self.post) > 0:
                self.core = self.post.pop(0)
            else:
                delattr(self, 'core')
        elif offset < 0:
            index = abs(offset) - 1
            if index >= len(self.pre):
                raise KeyError(f"No item at offset {offset}")
            self.pre.pop(index)
        else:
            index = offset - 1
            if index >= len(self.post):
                raise KeyError(f"No item at offset {offset}")
            self.post.pop(index)

    def get_all_items(self) -> List[T]:
        """Get all items in offset order for selector engine traversal."""
        return list(self)