"""
Context Snapshot - Immutable Context State Snapshots

ContextSnapshot provides immutable snapshots of Context state taken before provider calls.
Supports both full snapshots and diff-based storage for efficiency.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Union, TYPE_CHECKING, Any
from typing_extensions import TypedDict
from datetime import datetime
from copy import deepcopy

if TYPE_CHECKING:
    from pydantic._internal._model_construction import complete_model_class

from ..pact.context import Context
from ..pact.components.core import PACTCore


class PACTOrgData(TypedDict, total=False):
    """Organization-specific custom attributes for PACT nodes"""
    role: Optional[str]  # "user" | "assistant"
    text: Optional[str]  # Message content text
    priority: Optional[str]  # "high" | "medium" | "low"
    source: Optional[str]  # Scaffold name for source tracking
    metadata: Optional[Dict[str, str]]  # Additional custom data
    context_type: Optional[str]  # "conversation"
    agent_id: Optional[str]  # Agent identifier
    episode: Optional[int]  # Episode number
    # Scaffold state persistence
    scaffold_state: Optional[str]  # JSON-serialized scaffold state
    scaffold_id_data: Optional[str]  # Scaffold ID for state restoration
    scaffold: Optional[str]  # Scaffold marker ("true")
    # Component metadata
    component_type: Optional[str]  # "container" | "content"
    base_block: Optional[str]  # Component class type
    props: Optional[Dict[str, Any]]  # Component properties
    # Runtime metadata
    message_cycle: Optional[int]  # Message cycle
    active: Optional[bool]  # Component active state
    kind: Optional[str]  # Component kind
    # Render lifecycle
    render_lifecycle_stages: Optional[Any]  # Lifecycle stages
    render_current_stage_index: Optional[int]  # Current stage index
    render_cycle_behavior: Optional[Any]  # Cycle behavior
    render_cycles_completed: Optional[int]  # Cycles completed


class PACTDataNode(TypedDict, total=False):
    """PACT v0.1 compliant node data structure"""
    id: str
    nodeType: str
    parent_id: Optional[str]
    offset: int
    ttl: Optional[int]
    priority: int
    cycle: int
    created_at_ns: int
    created_at_iso: str
    creation_index: int
    children: List['PACTDataNode']
    key: Optional[str]
    tag: Optional[List[str]]
    org: Optional[PACTOrgData]


class PACTDataTree(TypedDict, total=False):
    """PACT tree root data structure"""
    id: str
    nodeType: str
    parent_id: Optional[str]
    offset: int
    ttl: Optional[int]
    priority: int
    cycle: int
    created_at_ns: int
    created_at_iso: str
    creation_index: int
    children: List[PACTDataNode]
    key: Optional[str]
    tag: Optional[List[str]]
    org: Optional[PACTOrgData]


# Note: ComponentDiff and ContextDiff classes removed
# PACT v0.1 compliant approach uses direct PACT tree comparison by node IDs
# See compare_pact_trees() and PACTDiffResult instead


class ContextSnapshot(BaseModel):
    """Immutable snapshot of Context state using PACT v0.1 compliant storage"""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Required fields first (Pydantic requirement)
    id: str = Field(..., description="Unique snapshot identifier")
    message_cycle: int = Field(..., description="Message cycle when snapshot was taken")
    trigger: str = Field(..., description="What triggered this snapshot (e.g., 'before_provider_call')")
    turn_id: str = Field(..., description="Turn identifier for grouping")
    
    # Optional fields with defaults
    timestamp: datetime = Field(default_factory=datetime.now)
    pact_tree: Optional[PACTDataTree] = Field(None, description="PACT-compliant context tree")
    full_context: Optional[Any] = Field(None, description="Full Context object (for backward compatibility)")
    provider_name: Optional[str] = Field(None, description="Provider that received this context")
    context_size_bytes: Optional[int] = Field(None, description="Estimated context size in bytes")
    component_count: Optional[int] = Field(None, description="Total number of components in context")
    agent_id: Optional[str] = Field(None, description="Agent identifier for session tracking")
    is_full_snapshot: bool = Field(True, description="Whether this is a full snapshot or diff")
    previous_snapshot_id: Optional[str] = Field(None, description="ID of previous snapshot for diffs")
    
    @property
    def has_pact_tree(self) -> bool:
        """Check if this snapshot has a PACT tree"""
        return self.pact_tree is not None
    
    def get_context_size_mb(self) -> float:
        """Get context size in megabytes"""
        if self.context_size_bytes:
            return self.context_size_bytes / (1024 * 1024)
        return 0.0
    
    def to_summary(self) -> Dict[str, Union[str, int, float, Optional[str]]]:
        """Generate summary information for this snapshot"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "message_cycle": self.message_cycle,
            "trigger": self.trigger,
            "turn_id": self.turn_id,
            "provider_name": self.provider_name,
            "snapshot_type": "full" if self.is_full_snapshot else "diff",
            "context_size_bytes": self.context_size_bytes,
            "context_size_mb": round(self.get_context_size_mb(), 2),
            "component_count": self.component_count,
            "previous_snapshot_id": self.previous_snapshot_id,
        }
    


# Factory functions for creating snapshots

def create_full_snapshot(context: Context, snapshot_id: str, trigger: str, **metadata) -> ContextSnapshot:
    """Create a full context snapshot using PACT tree"""
    return ContextSnapshot(
        id=snapshot_id,
        message_cycle=getattr(context, 'cadence', 0),
        trigger=trigger,
        turn_id=metadata.get('turn_id', f"turn_{getattr(context, 'cadence', 0)}"),
        pact_tree=context.to_pact(),  # Use PACT serialization
        is_full_snapshot=True,
        previous_snapshot_id=None,
        provider_name=metadata.get('provider_name'),
        context_size_bytes=_estimate_context_size(context),
        component_count=_count_components(context),
        agent_id=metadata.get('agent_id'),
    )


# Note: create_diff_snapshot() removed 
# PACT v0.1 compliant approach: all snapshots are full snapshots with PACT trees
# Diffs are computed on-demand using compare_pact_trees() function


# Utility functions

def _estimate_context_size(context: Context) -> int:
    """Estimate context size in bytes using PACT tree serialization"""
    try:
        # Use PACT-compliant JSON serialization
        pact_tree = context.to_pact()
        import json
        context_str = json.dumps(pact_tree)
        return len(context_str.encode('utf-8'))
    except Exception:
        return 0


def _count_components(context: Context) -> int:
    """Count total components in context tree using PACT tree"""
    try:
        # Use PACT tree to recursively count all nodes
        pact_tree = context.to_pact()
        return _count_pact_nodes(pact_tree)
    except Exception:
        return 0


def _count_pact_nodes(node: Union[PACTDataTree, Dict[str, Any]]) -> int:
    """Recursively count nodes in PACT tree"""
    count = 1  # Count this node

    # Count all children recursively
    if "children" in node and isinstance(node["children"], list):
        for child in node["children"]:
            count += _count_pact_nodes(child)

    return count


class PACTDiffResult(BaseModel):
    """PACT v0.1 compliant diff result comparing two snapshots by node id"""
    
    base_snapshot_id: str = Field(..., description="ID of the previous snapshot")
    new_snapshot_id: str = Field(..., description="ID of the newer snapshot")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # PACT v0.1 compliant diff fields (per 02-invariants.md §9.3)
    added: List[str] = Field(default_factory=list, description="Node IDs that were added")
    removed: List[str] = Field(default_factory=list, description="Node IDs that were removed")
    changed: List[str] = Field(default_factory=list, description="Node IDs that were modified")
    
    # Optional structural move tracking
    children_added: Dict[str, List[str]] = Field(default_factory=dict, description="Parent ID -> list of child IDs added")
    children_removed: Dict[str, List[str]] = Field(default_factory=dict, description="Parent ID -> list of child IDs removed")


def compare_pact_trees(old_tree: Optional[PACTDataTree], new_tree: Optional[PACTDataTree]) -> PACTDiffResult:
    """
    Compare two PACT trees by node IDs to create PACT v0.1 compliant diff.
    
    Per PACT spec 02-invariants.md §9.3:
    - Detect changes by node `id` 
    - Report `added`, `removed`, and `changed` nodes
    - Track structural moves (re-parenting)
    """
    if old_tree is None and new_tree is None:
        raise ValueError("Both trees cannot be None")
    
    # Extract all node IDs and data from both trees
    old_nodes = _extract_all_nodes(old_tree) if old_tree else {}
    new_nodes = _extract_all_nodes(new_tree) if new_tree else {}
    
    old_ids = set(old_nodes.keys())
    new_ids = set(new_nodes.keys())
    
    # PACT v0.1 compliant diff detection
    added = list(new_ids - old_ids)
    removed = list(old_ids - new_ids)
    
    # Check for changes in existing nodes
    changed = []
    children_added = {}
    children_removed = {}
    
    for node_id in old_ids & new_ids:  # Intersection - nodes present in both
        old_node = old_nodes[node_id]
        new_node = new_nodes[node_id]
        
        # Check if any PACT fields changed (excluding children - handled separately)
        if _node_fields_changed(old_node, new_node):
            changed.append(node_id)
        
        # Track structural changes (re-parenting)
        old_children = set(_get_child_ids(old_node))
        new_children = set(_get_child_ids(new_node))
        
        if old_children != new_children:
            if new_children - old_children:  # Children added
                children_added[node_id] = list(new_children - old_children)
            if old_children - new_children:  # Children removed
                children_removed[node_id] = list(old_children - new_children)
    
    return PACTDiffResult(
        base_snapshot_id=old_tree.get("id", "unknown") if old_tree else "none",
        new_snapshot_id=new_tree.get("id", "unknown") if new_tree else "none",
        added=sorted(added),  # Sort for deterministic output
        removed=sorted(removed),
        changed=sorted(changed),
        children_added=children_added,
        children_removed=children_removed
    )


def _extract_all_nodes(tree: PACTDataTree) -> Dict[str, Dict]:
    """Recursively extract all nodes from PACT tree indexed by ID"""
    nodes = {}
    
    def visit_node(node):
        if isinstance(node, dict) and "id" in node:
            nodes[node["id"]] = node
            # Recursively visit children
            if "children" in node and isinstance(node["children"], list):
                for child in node["children"]:
                    visit_node(child)
    
    visit_node(tree)
    return nodes


def _node_fields_changed(old_node: Dict, new_node: Dict) -> bool:
    """Check if PACT node fields changed (excluding children and timestamps)"""
    # PACT v0.1 structural/content fields to compare
    # Exclude timestamps and creation_index since they vary between snapshots
    fields_to_check = [
        "nodeType", "parent_id", "offset", "ttl", "priority", "cycle",
        "key", "tag", "org"
    ]
    
    for field in fields_to_check:
        if old_node.get(field) != new_node.get(field):
            return True
    
    return False


def _get_child_ids(node: Dict[str, Any]) -> List[str]:
    """Extract child node IDs from a PACT node"""
    if "children" in node and isinstance(node["children"], list):
        child_ids: List[str] = []
        for child in node["children"]:
            if isinstance(child, dict) and "id" in child:
                child_id = child.get("id")
                if child_id is not None:
                    child_ids.append(child_id)
        return child_ids
    return []


def diff_snapshots(before: ContextSnapshot, after: ContextSnapshot) -> PACTDiffResult:
    """
    Compare two ContextSnapshots using PACT v0.1 compliant tree comparison.
    
    This replaces the need for separate diff data structures by directly
    comparing PACT trees using node IDs as specified in 02-invariants.md §9.3.
    """
    if not before.pact_tree or not after.pact_tree:
        raise ValueError("Both snapshots must have PACT trees for comparison")
    
    return compare_pact_trees(before.pact_tree, after.pact_tree)


class PACTDiffEntry(TypedDict, total=False):
    """Single diff entry between two snapshots with resolved PACT nodes"""
    from_snapshot: str
    to_snapshot: str
    timestamp: str
    added: List[PACTDataNode]
    removed: List[PACTDataNode]
    changed: List[PACTDataNode]
    children_added: Dict[str, List[str]]
    children_removed: Dict[str, List[str]]


class RangeDiffLatestResult(BaseModel):
    """
    PACT v0.1 compliant result for range selectors like @t0..@t-5.
    
    Per PACT spec 04-queries.md, range selectors return:
    - Original query string
    - Resolved snapshots sorted DESC (newest to oldest) 
    - Pairwise diffs with actual PACT nodes (not just IDs)
    """
    
    query: str = Field(..., description="Original range selector query")
    snapshots: List[str] = Field(default_factory=list, description="Snapshot IDs sorted newest→oldest") 
    diffs: List[PACTDiffEntry] = Field(default_factory=list, description="Pairwise diffs with resolved PACT nodes")
    mode: Optional[str] = Field(None, description="Query mode (latest, changes, stable)")
    limits: Optional[Dict[str, int]] = Field(None, description="Applied limits (count, size, etc.)")


def create_range_diff_result(
    query: str,
    snapshots: List[ContextSnapshot], 
    resolve_nodes: bool = True
) -> RangeDiffLatestResult:
    """
    Create RangeDiffLatestResult from snapshots with resolved PACT nodes.
    
    Args:
        query: Original range selector query
        snapshots: List of ContextSnapshot objects
        resolve_nodes: Whether to resolve node IDs to actual PACT nodes
        
    Returns:
        RangeDiffLatestResult with usable PACT node content
    """
    # Sort snapshots newest to oldest (DESC by timestamp)
    sorted_snapshots = sorted(snapshots, key=lambda s: s.timestamp, reverse=True)
    
    # Create pairwise diffs
    pairwise_diffs = []
    for i in range(len(sorted_snapshots) - 1):
        newer_snapshot = sorted_snapshots[i]
        older_snapshot = sorted_snapshots[i + 1]
        
        # Get basic diff with node IDs
        diff_result = diff_snapshots(older_snapshot, newer_snapshot)
        
        # Resolve node IDs to actual PACT nodes if requested
        if resolve_nodes:
            resolved_diff: PACTDiffEntry = {
                "from_snapshot": older_snapshot.id,
                "to_snapshot": newer_snapshot.id,
                "timestamp": diff_result.timestamp.isoformat(),
                "added": _resolve_node_ids(diff_result.added, newer_snapshot.pact_tree),
                "removed": _resolve_node_ids(diff_result.removed, older_snapshot.pact_tree),
                "changed": _resolve_node_ids(diff_result.changed, newer_snapshot.pact_tree),
                "children_added": diff_result.children_added,
                "children_removed": diff_result.children_removed
            }
        else:
            # Just use node IDs (for debugging/testing) - create empty nodes for type safety
            resolved_diff: PACTDiffEntry = {
                "from_snapshot": older_snapshot.id,
                "to_snapshot": newer_snapshot.id,
                "timestamp": diff_result.timestamp.isoformat(),
                "added": [],
                "removed": [],
                "changed": [],
                "children_added": diff_result.children_added,
                "children_removed": diff_result.children_removed
            }
        
        pairwise_diffs.append(resolved_diff)
    
    return RangeDiffLatestResult(
        query=query,
        snapshots=[s.id for s in sorted_snapshots],
        diffs=pairwise_diffs
    )


def _resolve_node_ids(node_ids: List[str], pact_tree: Optional[PACTDataTree]) -> List[PACTDataNode]:
    """
    Resolve node IDs to actual PACT node objects from tree.
    
    This makes the diff result actually usable instead of just string references.
    """
    if not pact_tree or not node_ids:
        return []
    
    # Extract all nodes from tree indexed by ID
    all_nodes = _extract_all_nodes(pact_tree)
    
    # Resolve IDs to actual node objects
    resolved_nodes = []
    for node_id in node_ids:
        if node_id in all_nodes:
            node = all_nodes[node_id].copy()
            # Remove children to avoid deep nesting in diff output
            if "children" in node:
                node["children_count"] = len(node["children"])
                del node["children"]
            resolved_nodes.append(node)
    
    return resolved_nodes