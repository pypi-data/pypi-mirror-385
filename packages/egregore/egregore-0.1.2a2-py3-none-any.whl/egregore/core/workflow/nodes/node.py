from typing import Any, Union, List, Optional
from egregore.core.workflow.nodes.base import BaseNode
import warnings
from egregore.core.workflow.nodes.node_types import NodeType



class NodeMapper:
    """A node that maps a condition to a node.

    Fully deferred architecture: stores only ChainBuilder metadata,
    no node instances. Enables distributed execution where chains
    are instantiated on target machines.
    """
    def __init__(self, condition:Any, node:Union[BaseNode, "NodeType", "ChainBuilder"]):
        self.condition = condition

        # Import ChainBuilder here to avoid circular dependency
        from egregore.core.workflow.chain_builder import ChainBuilder

        # Convert ALL node types to ChainBuilder for deferred instantiation
        # This ensures NodeMapper stores only metadata, not instances
        if isinstance(node, ChainBuilder):
            # Already a ChainBuilder - store as-is
            self._chain_builder = node
        elif isinstance(node, NodeType):
            # Convert NodeType to ChainBuilder
            self._chain_builder = ChainBuilder.from_single(node)
        elif hasattr(node, 'start'):  # Sequence object
            # Wrap Sequence instance in ChainBuilder
            self._chain_builder = ChainBuilder(
                node_types=[node],
                edges=[],
                alias_map={}
            )
        else:
            # BaseNode instance (Decision, custom nodes, etc.)
            # Wrap in ChainBuilder
            self._chain_builder = ChainBuilder(
                node_types=[node],
                edges=[],
                alias_map={}
            )

        # Legacy attributes for backwards compatibility (unused in new architecture)
        self.node = None
        self._chain_end_node = None
        self._complete_chain = []

    def __repr__(self):
        return f"CASE ({self.condition} >> {self.node})"

    def __rshift__(self, other: Union["BaseNode", "NodeType", "ChainBuilder"]):
        """Chain this NodeMapper's target with another node.

        Fully deferred: chains ChainBuilders together without creating instances.
        Example: 'process' >> step1 >> step2 >> step3
        Creates: ChainBuilder(step1) >> ChainBuilder(step2) >> ChainBuilder(step3)

        Args:
            other: NodeType, ChainBuilder, or BaseNode to chain with

        Returns:
            self (for method chaining)
        """
        from egregore.core.workflow.chain_builder import ChainBuilder

        # Convert other to ChainBuilder
        if isinstance(other, NodeType):
            other_builder = ChainBuilder.from_single(other)
        elif isinstance(other, ChainBuilder):
            other_builder = other
        elif isinstance(other, BaseNode):
            # Wrap BaseNode instance in ChainBuilder
            other_builder = ChainBuilder(
                node_types=[other],
                edges=[],
                alias_map={}
            )
        else:
            raise TypeError(
                f"Cannot chain NodeMapper with {type(other).__name__}. "
                f"Expected NodeType, ChainBuilder, or BaseNode."
            )

        # Chain our ChainBuilder with the other ChainBuilder
        # This uses ChainBuilder.from_chain() to combine metadata
        self._chain_builder = ChainBuilder.from_chain(self._chain_builder, other_builder)

        return self 

    
class Node(BaseNode):
    """Core Node class used to build the action graph."""
    def __init__(self,  label:Optional[str] = None,*args, **kwargs):
        
        if label is not None:
            class_name = self.__class__.__name__ 
            self.name = f"{class_name}({label})"
        else:
            self.name = self.__class__.__name__ 
        kwargs['name'] = self.name
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return self.name




class BatchNode(Node):
    """
    A node designed to process a batch of items.
    Subclasses should implement _execute_item for individual item logic.
    """
    def __init__(self, label: Optional[str] = None, *args, **kwargs):
        super().__init__(label=label or "Batch", *args, **kwargs)

    def _execute_item(self, item: Any, *args, **kwargs) -> Any:
        """Process a single item from the batch."""
        raise NotImplementedError(f"_execute_item is not implemented for {self.name}")

    def execute(self, *args, **kwargs) -> List[Any]:
        """
        Executes _execute_item for each item in the input batch.
        Expects the batch to be the first argument or retrieved from state.
        """
        items = self.state.get_previous_output() # Default to previous output
        # Allow overriding via direct args if needed, simplistic check:
        if args and isinstance(args[0], (list, tuple)):
             items = args[0]
             args = args[1:] # Adjust args for _execute_item


        if not isinstance(items, (list, tuple)):
            warnings.warn(f"{self.name} received non-iterable input for batch processing: {type(items)}. Returning empty list.")
            return []

        results = []
        for item in items:
            try:
                # Pass remaining args and all kwargs to item execution
                result = self._execute_item(item, *args, **kwargs)
                results.append(result)
            except Exception as e:
                # Decide error handling: append None, raise, skip? Append None for now.
                results.append(None)
        return results