from typing import Optional, List, Dict, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from egregore.core.workflow.nodes.base import BaseNode

class NodeRegistry:
    """Central registry for all workflow nodes with GUID-based tracking"""
    
    def __init__(self):
        self.nodes: Dict[str, 'BaseNode'] = {}  # guid -> node
        self.aliases: Dict[str, str] = {}     # alias -> guid  
        self.canonical_map: Dict[str, List[str]] = {}  # canonical_name -> [guids]
        
    def register_node(self, node: 'BaseNode') -> str:
        """Register node and return its GUID"""
        if not node.guid:
            node.guid = str(uuid.uuid4())
            
        self.nodes[node.guid] = node
        
        # Track canonical mappings
        canonical = node.canonical_name or node.name
        if canonical:
            if canonical not in self.canonical_map:
                self.canonical_map[canonical] = []
            self.canonical_map[canonical].append(node.guid)
        
        # Track aliases
        if node.alias_name:
            self.aliases[node.alias_name] = node.guid
            
        return node.guid
    
    def get_node_by_guid(self, guid: str) -> Optional['BaseNode']:
        """Get node by GUID"""
        return self.nodes.get(guid)
    
    def get_nodes_by_canonical(self, canonical_name: str) -> List['BaseNode']:
        """Get all nodes (including aliases) for a canonical component"""
        guids = self.canonical_map.get(canonical_name, [])
        return [self.nodes[guid] for guid in guids if guid in self.nodes]
    
    def resolve_reference(self, node_ref: str) -> Optional['BaseNode']:
        """Resolve node reference (name, alias, or GUID)"""
        # Try alias first
        if node_ref in self.aliases:
            return self.nodes[self.aliases[node_ref]]
        
        # Try GUID
        if node_ref in self.nodes:
            return self.nodes[node_ref]
        
        # Try canonical name (return first match)
        for node in self.nodes.values():
            if node.name == node_ref or node.canonical_name == node_ref:
                return node
                
        return None
