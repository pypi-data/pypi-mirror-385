"""
Mermaid diagram renderer for workflow sequences.
Provides clean separation of diagram generation logic from core sequence functionality.
"""

import re
from typing import Dict, Set, Tuple, Any, List, Optional
from egregore.core.workflow.nodes import BaseNode, Decision, NodeType
from egregore.core.workflow.sequence.base import Sequence


class MermaidRenderer:
    """Renders workflow sequences as Mermaid diagrams"""
    def __init__(self):
        self.node_ids: Dict[BaseNode, str] = {}
        self.visited = set()
        
    def render(self, sequence: 'Sequence', mode: str = "overview") -> str:
        """Generate a Mermaid diagram of the workflow pipeline

        Args:
            sequence: The sequence to render
            mode: "overview" for high-level view, "full" for detailed expansion
        """
        if not sequence.start:
            return "```mermaid\ngraph TD\n    EmptySequence[\"Empty Sequence\"]\n```"

        # Build custom JSON that handles parallel_branches architecture
        json_data = self._build_json_for_mermaid(sequence)

        return self._render_from_json(json_data, mode=mode)

    def _build_json_for_mermaid(self, sequence: 'Sequence') -> Dict:
        """Build JSON representation that handles both parallel_branches and parallel_nodes"""
        nodes = []
        connections = []
        visited = set()
        node_usage_count = {}  # Track how many times each node name is used

        # Build a map from node guid to its downstream node using ChainSpec
        node_downstream_map = {}
        if hasattr(sequence, '_chain_spec') and sequence._chain_spec:
            chain_spec = sequence._chain_spec
            # Edges are (source_idx, target_idx) tuples
            for source_idx, target_idx in chain_spec.edges:
                source_spec = chain_spec.nodes[source_idx]
                target_spec = chain_spec.nodes[target_idx]
                # Get the actual node instance if it exists
                if hasattr(source_spec, '_node_type_ref'):
                    source_node = source_spec._node_type_ref
                    if hasattr(source_node, 'node_instance'):
                        source_node = source_node.node_instance
                else:
                    source_node = None
                if hasattr(target_spec, '_node_type_ref'):
                    target_node = target_spec._node_type_ref
                    if hasattr(target_node, 'node_instance'):
                        target_node = target_node.node_instance
                else:
                    target_node = None

                # Store the mapping using guid
                if source_node and target_node and hasattr(source_node, 'guid') and hasattr(target_node, 'guid'):
                    node_downstream_map[source_node.guid] = target_node

        def process_node(node, downstream=None):
            if not node:
                return

            # Don't check visited for node reuse - allow multiple appearances
            # But track to avoid infinite loops
            if node.guid in visited:
                return
            visited.add(node.guid)

            node_name = getattr(node, 'name', str(node))
            node_guid = node.guid
            node_type = self._get_node_type_from_instance(node)

            # For parallel nodes, create unique ID based on guid
            if node_type == 'parallel':
                # Use guid suffix for unique parallel node IDs
                unique_node_id = f"{node_name}_{node_guid[:8]}"
            else:
                unique_node_id = node_name

            # Add node
            node_data = {
                'id': unique_node_id,
                'name': node_name,
                'type': node_type,
                'guid': node_guid,
                'alias': getattr(node, 'alias_name', None),
                'canonical_name': getattr(node, 'canonical_name', node_name) or node_name,
                'effective_name': getattr(node, 'effective_name', node_name)
            }

            # Handle parallel_branches (new architecture)
            if hasattr(node, 'parallel_branches'):
                node_data['type'] = 'parallel'
                node_data['children'] = []

                # Determine downstream target for terminal nodes
                # This is the node that comes after the parallel node
                # Try: 1) parameter, 2) node.next_node, 3) ChainSpec map
                target_downstream = downstream or (node.next_node if hasattr(node, 'next_node') else None)
                if not target_downstream and node.guid in node_downstream_map:
                    target_downstream = node_downstream_map[node.guid]

                # Process the downstream aggregator node first so it's in the nodes list
                if target_downstream and target_downstream.guid not in visited:
                    process_node(target_downstream, downstream=None)

                from egregore.core.workflow.chain_builder import ChainBuilder
                for chain_builder in node.parallel_branches:
                    chain_spec = chain_builder.to_spec()
                    if not chain_spec.nodes:
                        continue

                    # Track node usage for reuse visualization
                    branch_visited_specs = set()

                    # Map spec GUIDs to actual node GUIDs for parallel nodes
                    spec_to_node_guid = {}

                    # Process ALL nodes in branch
                    for spec in chain_spec.nodes:
                        spec_name = getattr(spec, 'node_name', 'unknown')
                        spec_guid = getattr(spec, 'node_guid', str(id(spec)))

                        # For node reuse: create unique ID per usage
                        if spec_guid in branch_visited_specs:
                            # Already seen in this branch - skip to avoid duplicate within same branch
                            continue
                        branch_visited_specs.add(spec_guid)

                        # Always use original name (no _2, _3 suffixes for loops)
                        unique_spec_name = spec_name

                        # Check if this spec represents a parallel or decision node
                        is_parallel = False
                        is_decision = False
                        if hasattr(spec, '_node_type_ref'):
                            if hasattr(spec._node_type_ref, 'parallel_branches'):
                                is_parallel = True
                            elif isinstance(spec._node_type_ref, Decision):
                                is_decision = True

                        # Only add to nodes if NOT a parallel or decision (they're added by recursive process_node)
                        if not is_parallel and not is_decision:
                            nodes.append({
                                'id': unique_spec_name,
                                'name': spec_name,  # Keep original name for display
                                'type': 'node',
                                'guid': spec_guid,
                                'alias': getattr(spec, 'alias_name', None),
                                'canonical_name': getattr(spec, 'canonical_name', spec_name),
                                'effective_name': getattr(spec, 'effective_name', spec_name)
                            })

                        # If this is a nested parallel or decision, recursively process it
                        if (is_parallel or is_decision) and hasattr(spec, '_node_type_ref'):
                            # For ParallelNode/_decision, _node_type_ref IS the node (not a wrapper)
                            nested_node = spec._node_type_ref
                            if hasattr(nested_node, 'node_instance'):
                                nested_node = nested_node.node_instance

                            # Map spec GUID to actual node GUID for correct unique ID
                            if nested_node:
                                spec_to_node_guid[spec_guid] = nested_node.guid

                            # Determine downstream for this nested parallel/decision
                            # Find next node in chain or use target_downstream
                            spec_index = chain_spec.nodes.index(spec)
                            if spec_index < len(chain_spec.nodes) - 1:
                                # Next node in chain becomes downstream
                                next_spec = chain_spec.nodes[spec_index + 1]
                                if hasattr(next_spec, '_node_type_ref'):
                                    next_node_instance = next_spec._node_type_ref
                                    if hasattr(next_node_instance, 'node_instance'):
                                        next_node_instance = next_node_instance.node_instance
                                else:
                                    next_node_instance = None

                                # Recursively process with correct downstream
                                if nested_node and nested_node.guid not in visited:
                                    process_node(nested_node, downstream=next_node_instance)
                            else:
                                # Terminal parallel/decision uses target_downstream
                                if nested_node and nested_node.guid not in visited:
                                    process_node(nested_node, downstream=target_downstream)

                    # Add connections within branch (need to track unique names)
                    branch_spec_to_unique = {}  # Map spec_guid to unique_name
                    for i, spec in enumerate(chain_spec.nodes):
                        spec_name = getattr(spec, 'node_name', 'unknown')
                        spec_guid = getattr(spec, 'node_guid', str(id(spec)))

                        # Get the unique name for this spec
                        if spec_guid not in branch_spec_to_unique:
                            # Check if this is a parallel node (needs unique ID)
                            is_spec_parallel = hasattr(spec, '_node_type_ref') and hasattr(spec._node_type_ref, 'parallel_branches')

                            if is_spec_parallel:
                                # Use actual node GUID if mapped, otherwise spec GUID
                                actual_guid = spec_to_node_guid.get(spec_guid, spec_guid)
                                # Parallel nodes use unique ID format
                                branch_spec_to_unique[spec_guid] = f"{spec_name}_{actual_guid[:8]}"
                            else:
                                # Find which unique name was assigned for regular nodes
                                matching_nodes = [n for n in nodes if n['guid'] == spec_guid and n['name'] == spec_name]
                                if matching_nodes:
                                    branch_spec_to_unique[spec_guid] = matching_nodes[-1]['id']  # Use last added
                                else:
                                    branch_spec_to_unique[spec_guid] = spec_name

                        unique_name = branch_spec_to_unique[spec_guid]

                        # Connection from parallel to first node in branch
                        if i == 0:
                            connections.append({
                                'id': f"conn_{unique_node_id}_{unique_name}",
                                'from': unique_node_id,
                                'to': unique_name,
                                'type': 'parallel'
                            })
                            node_data['children'].append({
                                'id': unique_name,
                                'name': spec_name,
                                'type': 'node'
                            })

                        # Internal chain connections
                        if i < len(chain_spec.nodes) - 1:
                            next_spec = chain_spec.nodes[i + 1]
                            next_name = getattr(next_spec, 'node_name', 'unknown')
                            next_guid = getattr(next_spec, 'node_guid', str(id(next_spec)))

                            # SKIP connections FROM parallel nodes - their branches handle downstream
                            is_current_parallel = hasattr(spec, '_node_type_ref') and hasattr(spec._node_type_ref, 'parallel_branches')
                            if is_current_parallel:
                                continue  # Don't create connection from parallel to next node

                            if next_guid not in branch_spec_to_unique:
                                # Check if next spec is a parallel node (needs unique ID)
                                is_next_parallel = hasattr(next_spec, '_node_type_ref') and hasattr(next_spec._node_type_ref, 'parallel_branches')

                                if is_next_parallel:
                                    # Use actual node GUID if mapped, otherwise spec GUID
                                    actual_next_guid = spec_to_node_guid.get(next_guid, next_guid)
                                    # Parallel nodes use unique ID format
                                    branch_spec_to_unique[next_guid] = f"{next_name}_{actual_next_guid[:8]}"
                                else:
                                    # Find which unique name was assigned for regular nodes
                                    matching_nodes = [n for n in nodes if n['guid'] == next_guid and n['name'] == next_name]
                                    if matching_nodes:
                                        branch_spec_to_unique[next_guid] = matching_nodes[-1]['id']
                                    else:
                                        branch_spec_to_unique[next_guid] = next_name

                            next_unique_name = branch_spec_to_unique[next_guid]

                            connections.append({
                                'id': f"conn_{unique_name}_{next_unique_name}",
                                'from': unique_name,
                                'to': next_unique_name,
                                'type': 'sequence'
                            })

                    # Connect terminal node to downstream
                    if target_downstream:
                        terminal_spec = chain_spec.nodes[-1]
                        terminal_guid = getattr(terminal_spec, 'node_guid', str(id(terminal_spec)))
                        terminal_unique_name = branch_spec_to_unique.get(terminal_guid, getattr(terminal_spec, 'node_name', 'unknown'))

                        # SKIP if terminal is parallel or decision - their branches handle downstream
                        is_terminal_parallel = hasattr(terminal_spec, '_node_type_ref') and hasattr(terminal_spec._node_type_ref, 'parallel_branches')
                        is_terminal_decision = hasattr(terminal_spec, '_node_type_ref') and isinstance(terminal_spec._node_type_ref, Decision)
                        if is_terminal_parallel or is_terminal_decision:
                            continue  # Don't create connection from parallel/decision to downstream

                        downstream_name = getattr(target_downstream, 'name', str(target_downstream))

                        # If downstream is parallel, use unique ID
                        downstream_type = self._get_node_type_from_instance(target_downstream)
                        if downstream_type == 'parallel':
                            downstream_id = f"{downstream_name}_{target_downstream.guid[:8]}"
                        else:
                            downstream_id = downstream_name

                        connections.append({
                            'id': f"conn_{terminal_unique_name}_{downstream_id}",
                            'from': terminal_unique_name,
                            'to': downstream_id,
                            'type': 'sequence'
                        })

            # Handle legacy parallel_nodes
            elif hasattr(node, 'parallel_nodes'):
                node_data['type'] = 'parallel'
                node_data['children'] = []
                for child in node.parallel_nodes:
                    child_name = getattr(child, 'name', str(child))
                    connections.append({
                        'id': f"conn_{unique_node_id}_{child_name}",
                        'from': unique_node_id,
                        'to': child_name,
                        'type': 'parallel'
                    })
                    node_data['children'].append({'id': child_name, 'name': child_name, 'type': 'node'})
                    process_node(child, downstream)

            # Handle decision nodes - expand branches like we do for parallel
            elif isinstance(node, Decision):
                node_data['type'] = 'decision'
                # Try to get downstream from: 1) parameter, 2) node.next_node, 3) ChainSpec map
                target_downstream = downstream or (node.next_node if hasattr(node, 'next_node') else None)
                if not target_downstream and node.guid in node_downstream_map:
                    target_downstream = node_downstream_map[node.guid]

                # Process the downstream node first so it's in the nodes list
                if target_downstream and target_downstream.guid not in visited:
                    process_node(target_downstream, downstream=None)

                from egregore.core.workflow.chain_builder import ChainBuilder
                # Process each pattern branch
                for pattern in node.patterns:
                    branch_chain = pattern.target_node

                    # Skip if not a ChainBuilder (old code path)
                    if not isinstance(branch_chain, ChainBuilder):
                        continue

                    chain_spec = branch_chain.to_spec()
                    if not chain_spec.nodes:
                        continue

                    # Process ALL nodes in this decision branch
                    branch_visited_specs = set()
                    spec_to_node_guid = {}

                    for spec in chain_spec.nodes:
                        spec_name = getattr(spec, 'node_name', 'unknown')
                        spec_guid = getattr(spec, 'node_guid', str(id(spec)))

                        if spec_guid in branch_visited_specs:
                            continue
                        branch_visited_specs.add(spec_guid)

                        # Always use original name (no _2, _3 suffixes for loops)
                        unique_spec_name = spec_name

                        # Check if this is a parallel or decision node
                        is_parallel = hasattr(spec, '_node_type_ref') and hasattr(spec._node_type_ref, 'parallel_branches')
                        is_decision = hasattr(spec, '_node_type_ref') and isinstance(spec._node_type_ref, Decision)

                        if not is_parallel and not is_decision:
                            nodes.append({
                                'id': unique_spec_name,
                                'name': spec_name,
                                'type': 'node',
                                'guid': spec_guid,
                                'alias': getattr(spec, 'alias_name', None),
                                'canonical_name': getattr(spec, 'canonical_name', spec_name),
                                'effective_name': getattr(spec, 'effective_name', spec_name)
                            })

                        # If nested parallel or decision, process it recursively
                        if (is_parallel or is_decision) and hasattr(spec, '_node_type_ref'):
                            nested_node = spec._node_type_ref
                            if hasattr(nested_node, 'node_instance'):
                                nested_node = nested_node.node_instance

                            if nested_node:
                                spec_to_node_guid[spec_guid] = nested_node.guid

                            spec_index = chain_spec.nodes.index(spec)
                            if spec_index < len(chain_spec.nodes) - 1:
                                next_spec = chain_spec.nodes[spec_index + 1]
                                if hasattr(next_spec, '_node_type_ref'):
                                    next_node_instance = next_spec._node_type_ref
                                    if hasattr(next_node_instance, 'node_instance'):
                                        next_node_instance = next_node_instance.node_instance
                                else:
                                    next_node_instance = None

                                if nested_node and nested_node.guid not in visited:
                                    process_node(nested_node, downstream=next_node_instance)
                            else:
                                if nested_node and nested_node.guid not in visited:
                                    process_node(nested_node, downstream=target_downstream)

                    # Add connections within this decision branch
                    branch_spec_to_unique = {}
                    for i, spec in enumerate(chain_spec.nodes):
                        spec_name = getattr(spec, 'node_name', 'unknown')
                        spec_guid = getattr(spec, 'node_guid', str(id(spec)))

                        if spec_guid not in branch_spec_to_unique:
                            is_spec_parallel = hasattr(spec, '_node_type_ref') and hasattr(spec._node_type_ref, 'parallel_branches')

                            if is_spec_parallel:
                                actual_guid = spec_to_node_guid.get(spec_guid, spec_guid)
                                branch_spec_to_unique[spec_guid] = f"{spec_name}_{actual_guid[:8]}"
                            else:
                                matching_nodes = [n for n in nodes if n['guid'] == spec_guid and n['name'] == spec_name]
                                if matching_nodes:
                                    branch_spec_to_unique[spec_guid] = matching_nodes[-1]['id']
                                else:
                                    branch_spec_to_unique[spec_guid] = spec_name

                        unique_name = branch_spec_to_unique[spec_guid]

                        # Connection from decision to first node in branch
                        if i == 0:
                            # Get clean condition label for this pattern
                            from egregore.core.workflow.nodes.decision.patterns import ValuePattern, DefaultPattern
                            if isinstance(pattern, ValuePattern):
                                condition_label = repr(pattern.value)
                            elif isinstance(pattern, DefaultPattern):
                                condition_label = "'_'"  # Show as "_" for default pattern
                            else:
                                condition_label = str(pattern)
                            connections.append({
                                'id': f"conn_{unique_node_id}_{unique_name}",
                                'from': unique_node_id,
                                'to': unique_name,
                                'type': 'decision',
                                'condition': condition_label
                            })

                        # Internal chain connections
                        if i < len(chain_spec.nodes) - 1:
                            next_spec = chain_spec.nodes[i + 1]
                            next_name = getattr(next_spec, 'node_name', 'unknown')
                            next_guid = getattr(next_spec, 'node_guid', str(id(next_spec)))

                            # SKIP connections FROM parallel nodes - their branches handle downstream
                            is_current_parallel = hasattr(spec, '_node_type_ref') and hasattr(spec._node_type_ref, 'parallel_branches')
                            if is_current_parallel:
                                continue  # Don't create connection from parallel to next node

                            if next_guid not in branch_spec_to_unique:
                                is_next_parallel = hasattr(next_spec, '_node_type_ref') and hasattr(next_spec._node_type_ref, 'parallel_branches')

                                if is_next_parallel:
                                    actual_next_guid = spec_to_node_guid.get(next_guid, next_guid)
                                    branch_spec_to_unique[next_guid] = f"{next_name}_{actual_next_guid[:8]}"
                                else:
                                    matching_nodes = [n for n in nodes if n['guid'] == next_guid and n['name'] == next_name]
                                    if matching_nodes:
                                        branch_spec_to_unique[next_guid] = matching_nodes[-1]['id']
                                    else:
                                        branch_spec_to_unique[next_guid] = next_name

                            next_unique_name = branch_spec_to_unique[next_guid]

                            connections.append({
                                'id': f"conn_{unique_name}_{next_unique_name}",
                                'from': unique_name,
                                'to': next_unique_name,
                                'type': 'sequence'
                            })

                    # Connect terminal node to downstream
                    if target_downstream:
                        terminal_spec = chain_spec.nodes[-1]
                        terminal_guid = getattr(terminal_spec, 'node_guid', str(id(terminal_spec)))
                        terminal_unique_name = branch_spec_to_unique.get(terminal_guid, getattr(terminal_spec, 'node_name', 'unknown'))

                        # SKIP if terminal is parallel or decision - their branches handle downstream
                        is_terminal_parallel = hasattr(terminal_spec, '_node_type_ref') and hasattr(terminal_spec._node_type_ref, 'parallel_branches')
                        is_terminal_decision = hasattr(terminal_spec, '_node_type_ref') and isinstance(terminal_spec._node_type_ref, Decision)
                        if is_terminal_parallel or is_terminal_decision:
                            continue  # Don't create connection from parallel/decision to downstream

                        downstream_name = getattr(target_downstream, 'name', str(target_downstream))

                        downstream_type = self._get_node_type_from_instance(target_downstream)
                        if downstream_type == 'parallel':
                            downstream_id = f"{downstream_name}_{target_downstream.guid[:8]}"
                        else:
                            downstream_id = downstream_name

                        # Decision branch terminals use 'conditional' type for thick arrows
                        connections.append({
                            'id': f"conn_{terminal_unique_name}_{downstream_id}",
                            'from': terminal_unique_name,
                            'to': downstream_id,
                            'type': 'conditional'  # Use thick arrow for decision paths
                        })

            # Always append node_data
            nodes.append(node_data)

            # Handle next_node - but SKIP if current node is parallel or decision
            # Parallel/decision nodes should NOT connect directly to downstream
            # Their terminal branch nodes handle downstream connections
            if hasattr(node, 'next_node') and node.next_node:
                is_parallel_node = hasattr(node, 'parallel_branches') or hasattr(node, 'parallel_nodes')
                is_decision_node = isinstance(node, Decision)

                if not is_parallel_node and not is_decision_node:
                    # Regular nodes connect to next_node
                    next_name = getattr(node.next_node, 'name', str(node.next_node))
                    next_type = self._get_node_type_from_instance(node.next_node)
                    if next_type == 'parallel':
                        next_id = f"{next_name}_{node.next_node.guid[:8]}"
                    else:
                        next_id = next_name
                    connections.append({
                        'id': f"conn_{unique_node_id}_{next_id}",
                        'from': unique_node_id,
                        'to': next_id,
                        'type': 'sequence'
                    })

                    # Continue processing next_node in chain for regular nodes
                    process_node(node.next_node, downstream=None)

        if sequence.start:
            process_node(sequence.start)

        return {
            'workflow_id': sequence.workflow_id,
            'name': sequence.name,
            'type': 'sequence',
            'nodes': nodes,
            'connections': connections
        }

    def _get_node_type_from_instance(self, node) -> str:
        """Determine node type from instance"""
        from egregore.core.workflow.sequence.base import Sequence

        if hasattr(node, 'parallel_branches') or hasattr(node, 'parallel_nodes'):
            return 'parallel'
        elif isinstance(node, Decision):
            return 'decision'
        elif hasattr(node, 'agent'):
            return 'agent'
        elif isinstance(node, Sequence):
            return 'sequence'
        else:
            return 'node'
    
    def _render_from_json(self, json_data: Dict, mode: str = "overview") -> str:
        """Render Mermaid diagram from JSON workflow representation
        
        Args:
            json_data: The JSON representation of the workflow
            mode: "overview" for high-level view, "full" for detailed expansion
        """
        mermaid = ["```mermaid", "graph TD"]
        
        if mode == "full":
            # Full mode: expand nested sequences and show all internal nodes
            self._render_full_expansion(json_data, mermaid)
        else:
            # Overview mode: high-level view (current behavior) 
            self._render_overview(json_data, mermaid)
        
        mermaid.append("```")
        return "\n".join(mermaid)
    
    def _render_overview(self, json_data: Dict, mermaid: List[str]) -> None:
        """Render overview mode (current behavior)"""
        # Track node rendering order to detect loops
        rendered_nodes = set()
        node_order = []

        # Process nodes from JSON
        nodes = json_data.get('nodes', [])
        for node_data in nodes:
            node_id = self._sanitize_json_id(node_data['id'])
            node_name = node_data['name']
            node_type = node_data['type']

            # Generate appropriate shape based on type
            shape = self._get_json_node_shape(node_id, node_name, node_type, node_data)
            mermaid.append(f'    {shape}')

            # Add styling with alias information
            style = self._get_json_node_style(node_type, node_data)  # Phase 4: Pass node_data for alias styling
            mermaid.append(f'    classDef {node_id}_style {style}')
            mermaid.append(f'    class {node_id} {node_id}_style')

            # Track node rendering order
            if node_id not in rendered_nodes:
                rendered_nodes.add(node_id)
                node_order.append(node_id)

        # Process connections from JSON
        connections = json_data.get('connections', [])
        for conn_data in connections:
            from_id = self._sanitize_json_id(conn_data['from'])
            to_id = self._sanitize_json_id(conn_data['to'])
            conn_type = conn_data['type']

            # Detect loop: connection points back to an earlier node
            # Only applies to sequence connections (not decision branches or parallel forks)
            is_loop = False
            if conn_type == 'sequence' and from_id in node_order and to_id in node_order:
                from_index = node_order.index(from_id)
                to_index = node_order.index(to_id)
                if to_index < from_index:
                    is_loop = True

            if conn_type == 'sequence':
                arrow = '-.->' if is_loop else '==>'
                mermaid.append(f'    {from_id} {arrow} {to_id}')
            elif conn_type == 'parallel':
                mermaid.append(f'    {from_id} --> {to_id}')
            elif conn_type == 'decision':
                condition = conn_data.get('condition', '')
                # Decision branches use dotted arrow with condition label
                mermaid.append(f'    {from_id} -.->|"{condition}"| {to_id}')
            elif conn_type == 'conditional':
                # Conditional paths (decision branch terminals) also use dotted arrows
                mermaid.append(f'    {from_id} -.-> {to_id}')
    
    def _render_full_expansion(self, json_data: Dict, mermaid: List[str]) -> None:
        """Render full expansion mode showing all nested sequence internals"""
        processed_sequences = set()
        sequence_boundaries = {}  # Maps sequence_id -> (first_node_id, last_node_id)
        id_mapping = {}  # Maps original JSON IDs to readable Mermaid IDs
        
        # First create ID mapping for all nodes
        self._create_id_mapping(json_data, id_mapping)
        
        # First pass: render all nodes, expanding nested sequences
        nodes = json_data.get('nodes', [])
        for node_data in nodes:
            self._render_node_full(node_data, mermaid, processed_sequences, sequence_boundaries, id_mapping)
        
        # Second pass: render all connections, including internal sequence connections
        connections = json_data.get('connections', [])
        rendered_connections = set()  # Track rendered connections to avoid duplicates
        for conn_data in connections:
            self._render_connection_full(conn_data, mermaid, processed_sequences, sequence_boundaries, id_mapping, rendered_connections)
    
    def _render_node_full(self, node_data: Dict, mermaid: List[str], processed_sequences: set, sequence_boundaries: dict, id_mapping: dict) -> None:
        """Render a single node in full expansion mode"""
        original_id = node_data['id']
        node_id = id_mapping.get(original_id, self._sanitize_json_id(original_id))
        node_name = node_data['name']
        node_type = node_data['type']
        
        if node_type == 'sequence' and 'nested_workflow' in node_data:
            # Expand nested sequence
            if node_id not in processed_sequences:
                processed_sequences.add(node_id)
                
                # Add a subgraph for the nested sequence
                mermaid.append(f'    subgraph {node_id}_cluster ["{node_name}"]')
                
                # Recursively render the nested workflow nodes
                nested_workflow = node_data['nested_workflow']
                nested_nodes = nested_workflow.get('nodes', [])
                
                # Find entry and exit points based on connections
                first_node_id, exit_node_ids = self._find_sequence_boundaries(nested_workflow, id_mapping)
                
                for nested_node_data in nested_nodes:
                    nested_original_id = nested_node_data['id']
                    nested_node_id = id_mapping.get(nested_original_id, self._sanitize_json_id(nested_original_id))
                    nested_node_name = nested_node_data['name']
                    nested_node_type = nested_node_data['type']
                    
                    # Render nested node
                    shape = self._get_json_node_shape(nested_node_id, nested_node_name, nested_node_type, nested_node_data)
                    mermaid.append(f'        {shape}')
                    
                    # Add styling
                    style = self._get_json_node_style(nested_node_type, nested_node_data)
                    mermaid.append(f'        classDef {nested_node_id}_style {style}')
                    mermaid.append(f'        class {nested_node_id} {nested_node_id}_style')
                
                # Store boundary information
                sequence_boundaries[node_id] = (first_node_id, exit_node_ids)
                
                # Add internal connections for nested sequence
                nested_connections = nested_workflow.get('connections', [])
                nested_rendered_connections = set()  # Track nested connections separately
                for nested_conn_data in nested_connections:
                    nested_from_original = nested_conn_data['from']
                    nested_to_original = nested_conn_data['to']
                    nested_from_id = id_mapping.get(nested_from_original, self._sanitize_json_id(nested_from_original))
                    nested_to_id = id_mapping.get(nested_to_original, self._sanitize_json_id(nested_to_original))
                    nested_conn_type = nested_conn_data['type']
                    
                    nested_connection_key = (nested_from_id, nested_to_id, nested_conn_type)
                    if nested_connection_key not in nested_rendered_connections:
                        if nested_conn_type == 'sequence':
                            mermaid.append(f'        {nested_from_id} --> {nested_to_id}')
                        elif nested_conn_type == 'parallel':
                            mermaid.append(f'        {nested_from_id} -.-> {nested_to_id}')
                        nested_rendered_connections.add(nested_connection_key)
                
                mermaid.append('    end')
        
        elif node_type == 'parallel' and 'children' in node_data:
            # Render parallel node and its children
            shape = self._get_json_node_shape(node_id, node_name, node_type, node_data)
            mermaid.append(f'    {shape}')
            
            # Add styling
            style = self._get_json_node_style(node_type, node_data)
            mermaid.append(f'    classDef {node_id}_style {style}')
            mermaid.append(f'    class {node_id} {node_id}_style')
            
            # Render parallel children as individual nodes
            for child_data in node_data['children']:
                child_original_id = child_data['id']
                child_id = id_mapping.get(child_original_id, self._sanitize_json_id(child_original_id))
                child_name = child_data['name']
                child_type = child_data['type']
                
                child_shape = self._get_json_node_shape(child_id, child_name, child_type, child_data)
                mermaid.append(f'    {child_shape}')
                
                child_style = self._get_json_node_style(child_type, child_data)
                mermaid.append(f'    classDef {child_id}_style {child_style}')
                mermaid.append(f'    class {child_id} {child_id}_style')
                
                # Add parallel connections
                mermaid.append(f'    {node_id} -.-> {child_id}')
        
        else:
            # Regular node
            shape = self._get_json_node_shape(node_id, node_name, node_type, node_data)
            mermaid.append(f'    {shape}')
            
            # Add styling
            style = self._get_json_node_style(node_type, node_data)
            mermaid.append(f'    classDef {node_id}_style {style}')
            mermaid.append(f'    class {node_id} {node_id}_style')
    
    def _render_connection_full(self, conn_data: Dict, mermaid: List[str], processed_sequences: set, sequence_boundaries: dict, id_mapping: dict, rendered_connections: set) -> None:
        """Render connections in full expansion mode"""
        from_original = conn_data['from']
        to_original = conn_data['to']
        from_id = id_mapping.get(from_original, self._sanitize_json_id(from_original))
        to_id = id_mapping.get(to_original, self._sanitize_json_id(to_original))
        conn_type = conn_data['type']
        
        # Skip parallel connections as they're handled in _render_node_full
        if conn_type == 'parallel':
            return
        
        # Handle sequence connections with boundary resolution
        if conn_type == 'sequence':
            # Check if from/to are sequences that were expanded
            from_node_ids = [from_id]
            to_node_id = to_id
            
            # If from is a sequence, use its exit nodes (could be multiple for parallel)
            if from_id in sequence_boundaries:
                _, exit_node_ids = sequence_boundaries[from_id]
                from_node_ids = exit_node_ids
            
            # If to is a sequence, use its first node
            if to_id in sequence_boundaries:
                to_node_id, _ = sequence_boundaries[to_id]
            
            # Create connections from all exit nodes to the target
            for actual_from_id in from_node_ids:
                if actual_from_id and to_node_id:
                    connection_key = (actual_from_id, to_node_id, 'sequence')
                    if connection_key not in rendered_connections:
                        mermaid.append(f'    {actual_from_id} --> {to_node_id}')
                        rendered_connections.add(connection_key)
                
        elif conn_type == 'decision':
            condition = conn_data.get('condition', '')
            # Apply same boundary resolution for decision connections
            from_node_ids = [from_id]
            to_node_id = to_id
            
            if from_id in sequence_boundaries:
                _, exit_node_ids = sequence_boundaries[from_id]
                from_node_ids = exit_node_ids
            
            if to_id in sequence_boundaries:
                to_node_id, _ = sequence_boundaries[to_id]
            
            # Create decision connections from all exit nodes to the target
            for actual_from_id in from_node_ids:
                if actual_from_id and to_node_id:
                    connection_key = (actual_from_id, to_node_id, f'decision_{condition}')
                    if connection_key not in rendered_connections:
                        mermaid.append(f'    {actual_from_id} -->|"{condition}"| {to_node_id}')
                        rendered_connections.add(connection_key)
    
    def _find_sequence_boundaries(self, nested_workflow: Dict, id_mapping: dict) -> Tuple[Optional[str], list]:
        """Find the entry and exit nodes of a sequence workflow
        
        Returns:
            Tuple of (first_node_id, exit_node_ids)
            where exit_node_ids is a list because parallel nodes have multiple exits
        """
        nodes = nested_workflow.get('nodes', [])
        connections = nested_workflow.get('connections', [])
        
        if not nodes:
            return None, []
        
        # If only one node, it's both first and last
        if len(nodes) == 1:
            original_id = nodes[0]['id']
            node_id = id_mapping.get(original_id, self._sanitize_json_id(original_id))
            return node_id, [node_id]
        
        # Find nodes that are not targets of any connection (entry points)
        all_original_ids = {node['id'] for node in nodes}
        target_original_ids = {conn['to'] for conn in connections}
        source_original_ids = {conn['from'] for conn in connections}
        
        # Entry nodes have no incoming connections
        entry_original_ids = all_original_ids - target_original_ids
        first_original_id = next(iter(entry_original_ids)) if entry_original_ids else nodes[0]['id']
        first_node_id = id_mapping.get(first_original_id, self._sanitize_json_id(first_original_id))
        
        # For exit nodes, we need to handle parallel nodes specially
        exit_node_ids = []
        
        # Check each node to see if it's an exit point
        for node_data in nodes:
            node_original_id = node_data['id']
            node_type = node_data.get('type', '')
            
            if node_type == 'parallel' and 'children' in node_data:
                # For parallel nodes, the exit points are the children, not the parallel node itself
                for child_data in node_data['children']:
                    child_original_id = child_data['id']
                    child_id = id_mapping.get(child_original_id, self._sanitize_json_id(child_original_id))
                    exit_node_ids.append(child_id)
            elif node_original_id not in source_original_ids:
                # Regular exit node (has no outgoing connections)
                node_id = id_mapping.get(node_original_id, self._sanitize_json_id(node_original_id))
                exit_node_ids.append(node_id)
        
        # If no exit nodes found, use the last node
        if not exit_node_ids:
            last_original_id = nodes[-1]['id']
            last_node_id = id_mapping.get(last_original_id, self._sanitize_json_id(last_original_id))
            exit_node_ids.append(last_node_id)
        
        return first_node_id, exit_node_ids
    
    def _create_id_mapping(self, json_data: Dict, id_mapping: dict) -> None:
        """Create mapping from JSON IDs to readable Mermaid IDs"""
        nodes = json_data.get('nodes', [])
        for node_data in nodes:
            original_id = node_data['id']
            readable_id = self._create_mermaid_id(node_data)
            id_mapping[original_id] = readable_id
            
            # Recursively map nested nodes
            if node_data.get('type') == 'sequence' and 'nested_workflow' in node_data:
                self._create_id_mapping(node_data['nested_workflow'], id_mapping)
            elif node_data.get('type') == 'parallel' and 'children' in node_data:
                for child_data in node_data['children']:
                    child_id = child_data['id']
                    child_readable_id = self._create_mermaid_id(child_data)
                    id_mapping[child_id] = child_readable_id
    
    def _create_mermaid_id(self, node_data: Dict) -> str:
        """Create a readable Mermaid ID from node data, preferring names over IDs"""
        node_name = node_data.get('name', '')
        node_id = node_data.get('id', '')
        node_type = node_data.get('type', '')
        
        # Prefer name if available and meaningful
        if node_name and not node_name.startswith('node_') and not node_name.startswith('parallel_'):
            base_name = node_name
        elif node_type == 'parallel':
            # For parallel nodes, use a generic readable name
            base_name = 'parallel_execution'
        else:
            base_name = node_id
            
        # Sanitize for Mermaid compatibility
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
        if re.match(r'^[0-9]+', sanitized):
            sanitized = f'N_{sanitized}'
        return sanitized
    
    def _sanitize_json_id(self, json_id: str) -> str:
        """Sanitize JSON node ID for Mermaid compatibility (legacy)"""
        import re
        # Replace any non-alphanumeric characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', json_id)
        if re.match(r'^[0-9]+', sanitized):
            sanitized = f'N_{sanitized}'
        return sanitized
    
    def _get_json_node_shape(self, node_id: str, node_name: str, node_type: str, node_data: Dict) -> str:
        """Get Mermaid shape based on JSON node type with Phase 4 alias visualization"""
        # Phase 4: Enhanced display name with alias information
        display_name = node_name

        # Transform parallel_{id} to just "parallel" for clean display
        # Handle both the node_name and the unique node_id formats
        if node_type == 'parallel':
            # Always show "parallel" for parallel nodes regardless of internal ID
            display_name = 'parallel'

        # Phase 4: Add alias information to display name for better visualization
        effective_name = node_data.get('effective_name', node_name)
        alias = node_data.get('alias')
        canonical_name = node_data.get('canonical_name', node_name)

        # Skip alias logic for parallel nodes - they should always show "parallel"
        if node_type != 'parallel':
            if alias:
                # For aliased nodes, show: "alias (canonical_name)"
                display_name = f"{effective_name} ({canonical_name})"
            else:
                # For original nodes, just use the name
                display_name = effective_name

        # For decision nodes, sanitize the display name to avoid mermaid syntax errors
        if node_type == 'decision':
            # Remove parentheses, quotes, and replace with safe text
            # Decision('A', 'B') -> decision
            display_name = 'decision'

        if node_type == 'sequence':
            return f'{node_id}[["{display_name}"]]'
        elif node_type == 'parallel':
            return f'{node_id}{{{{{display_name}}}}}'
        elif node_type == 'decision':
            return f'{node_id}{{{{{display_name}}}}}'
        elif node_type == 'agent':
            return f'{node_id}["{display_name}"]'
        else:
            return f'{node_id}["{display_name}"]'
    
    def _get_json_node_style(self, node_type: str, node_data: Optional[Dict] = None) -> str:
        """Get Mermaid styling based on JSON node type with Phase 4 alias styling"""
        base_style = ""
        
        if node_type == 'sequence':
            base_style = "fill:#e1f5fe,stroke:#01579b,stroke-width:2px"
        elif node_type == 'parallel':
            base_style = "fill:#f3e5f5,stroke:#4a148c,stroke-width:2px"
        elif node_type == 'decision':
            base_style = "fill:#fff3e0,stroke:#e65100,stroke-width:2px"
        elif node_type == 'agent':
            base_style = "fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px"
        else:
            base_style = "fill:#f5f5f5,stroke:#424242,stroke-width:1px"
        
        # Phase 4: Add special styling for aliased nodes
        if node_data and node_data.get('alias'):
            # Make aliased nodes have a dashed border to distinguish them
            base_style = base_style.replace("stroke-width:2px", "stroke-width:2px,stroke-dasharray: 5 5")
            base_style = base_style.replace("stroke-width:1px", "stroke-width:2px,stroke-dasharray: 5 5")
        
        return base_style
    
    def _sanitize_mermaid_id(self, node: BaseNode) -> str:
        """Create a clean Mermaid-compatible ID for a node"""
        name_part = getattr(node, 'name', str(node))
        # Enhanced sanitization for better readability
        name_part = re.sub(r'[^a-zA-Z0-9_]', '_', name_part)
        if re.match(r'^[0-9]+$', name_part):
            name_part = f'N_{name_part}'
        return f"{name_part}_{id(node) % 10000}"  # Shorter IDs
    
    def _get_node_style(self, node: BaseNode) -> str:
        """Get Mermaid styling based on node type"""
        # Import here to avoid circular imports
        from egregore.core.workflow.sequence.base import Sequence
        
        if isinstance(node, Sequence):
            return "fill:#e1f5fe,stroke:#01579b,stroke-width:2px"
        elif hasattr(node, 'parallel_branches'):  # ParallelNode (new architecture)
            return "fill:#f3e5f5,stroke:#4a148c,stroke-width:2px"
        elif hasattr(node, 'parallel_nodes'):  # ParallelNode (legacy)
            return "fill:#f3e5f5,stroke:#4a148c,stroke-width:2px"
        elif isinstance(node, Decision):
            return "fill:#fff3e0,stroke:#e65100,stroke-width:2px"
        elif hasattr(node, 'agent'):  # AgentNode
            return "fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px"
        else:
            return "fill:#f5f5f5,stroke:#424242,stroke-width:1px"
    
    def _collect_all_nodes(self, node: BaseNode) -> None:
        """First pass: Collect all nodes and assign IDs without generating output"""
        if not node or id(node) in self.visited:
            return
        self.visited.add(id(node))
        
        # Assign ID to this node
        node_id = self._sanitize_mermaid_id(node)
        self.node_ids[node] = node_id
        print(f"DEBUG: Collected node {node} -> ID {node_id}")
        
        # Recursively collect all connected nodes
        # Sequential connections
        if hasattr(node, 'next_node') and node.next_node:
            self._collect_all_nodes(node.next_node)
        
        # Parallel node children (new architecture - no instantiation needed here)
        if hasattr(node, 'parallel_branches'):
            # New architecture stores ChainBuilders - skip for now
            # JSON serialization path will handle these properly
            pass
        elif hasattr(node, 'parallel_nodes'):  # Legacy
            for child in node.parallel_nodes:  # type: ignore[attr-defined]
                self._collect_all_nodes(child)
        
        # Decision node branches
        if isinstance(node, Decision):
            for map_item in node.maps:
                target_node = map_item.node
                if isinstance(target_node, NodeType):
                    target_node = target_node.node_instance
                self._collect_all_nodes(target_node)
        
        # Nested sequences
        from egregore.core.workflow.sequence.base import Sequence
        if isinstance(node, Sequence) and node.start:
            self._collect_all_nodes(node.start)
    
    def _generate_node_definitions(self) -> List[str]:
        """Generate Mermaid node definition lines for all collected nodes"""
        node_lines = []
        
        for node, node_id in self.node_ids.items():
            node_name = getattr(node, 'name', str(node))
            
            # Get appropriate shape for node type
            shape = self._get_node_shape(node, node_id, node_name)
            node_lines.append(f'    {shape}')
            
            # Add styling
            style = self._get_node_style(node)
            node_lines.append(f'    classDef {node_id}_style {style}')
            node_lines.append(f'    class {node_id} {node_id}_style')
        
        return node_lines

    def _get_node_shape(self, node: BaseNode, node_id: str, node_name: str) -> str:
        """Get the appropriate Mermaid shape for different node types"""
        # Import here to avoid circular imports
        from egregore.core.workflow.sequence.base import Sequence

        # Transform parallel_{id} to just "parallel" for clean display
        display_name = node_name
        if (hasattr(node, 'parallel_branches') or hasattr(node, 'parallel_nodes')) and node_name.startswith('parallel_'):
            display_name = 'parallel'

        if isinstance(node, Sequence):
            return f'{node_id}[["{display_name}"]]'
        elif hasattr(node, 'parallel_branches'):  # ParallelNode (new architecture)
            return f'{node_id}{{{{{display_name}}}}}'
        elif hasattr(node, 'parallel_nodes'):  # ParallelNode (legacy)
            return f'{node_id}{{{{{display_name}}}}}'
        elif isinstance(node, Decision):
            return f'{node_id}{{{{{display_name}}}}}'
        elif hasattr(node, 'agent'):  # AgentNode
            return f'{node_id}["{display_name}"]'
        else:
            return f'{node_id}["{display_name}"]'
    
    def _traverse_and_collect(self, node: BaseNode, depth: int = 0) -> List[str]:
        """Recursively traverse and collect all nodes"""
        mermaid_lines = []
        
        if not node or id(node) in self.visited:
            return mermaid_lines
        self.visited.add(id(node))
        
        node_id = self._sanitize_mermaid_id(node)
        self.node_ids[node] = node_id
        node_name = getattr(node, 'name', str(node))
        
        # Get appropriate shape for node type
        shape = self._get_node_shape(node, node_id, node_name)
        mermaid_lines.append(f'    {shape}')
        
        # Add styling
        style = self._get_node_style(node)
        mermaid_lines.append(f'    classDef {node_id}_style {style}')
        mermaid_lines.append(f'    class {node_id} {node_id}_style')
        
        # Handle different node types
        parallel_lines = self._handle_parallel_nodes(node, depth)
        mermaid_lines.extend(parallel_lines)
        
        decision_lines = self._handle_decision_nodes(node, depth)
        mermaid_lines.extend(decision_lines)
        
        nested_lines = self._handle_nested_sequences(node, depth) 
        mermaid_lines.extend(nested_lines)
        
        # Continue with next node
        if hasattr(node, 'next_node') and node.next_node:
            child_lines = self._traverse_and_collect(node.next_node, depth)
            mermaid_lines.extend(child_lines)
        
        return mermaid_lines
    
    def _handle_parallel_nodes(self, node: BaseNode, depth: int) -> List[str]:
        """Handle parallel node children"""
        lines = []
        if hasattr(node, 'parallel_branches'):  # New architecture - no action needed
            # New architecture stores ChainBuilders - JSON path handles these
            pass
        elif hasattr(node, 'parallel_nodes'):  # Legacy
            for child in node.parallel_nodes:  # type: ignore[attr-defined]
                child_lines = self._traverse_and_collect(child, depth + 1)
                lines.extend(child_lines)
        return lines
    
    def _handle_decision_nodes(self, node: BaseNode, depth: int) -> List[str]:
        """Handle decision node branches"""
        lines = []
        if isinstance(node, Decision):
            for map_item in node.maps:
                target_node = map_item.node
                if isinstance(target_node, NodeType):
                    target_node = target_node.node_instance
                child_lines = self._traverse_and_collect(target_node, depth + 1)
                lines.extend(child_lines)
        return lines
    
    def _handle_nested_sequences(self, node: BaseNode, depth: int) -> List[str]:
        """Handle nested sequence traversal"""
        # Import here to avoid circular imports
        from egregore.core.workflow.sequence.base import Sequence
        
        lines = []
        if isinstance(node, Sequence) and node.start:
            child_lines = self._traverse_and_collect(node.start, depth + 1)
            lines.extend(child_lines)
        return lines
    
    def _add_connections(self, mermaid: List[str]) -> None:
        """Add connections between nodes based on collected nodes"""
        connections_added = set()
        
        # Create connections for all collected nodes
        for node in list(self.node_ids.keys()):
            node_id = self.node_ids[node]
            
            self._add_sequential_connections(node, node_id, connections_added, mermaid)
            self._add_parallel_connections(node, node_id, connections_added, mermaid)
            self._add_decision_connections(node, node_id, connections_added, mermaid)
            self._add_nested_sequence_connections(node, node_id, connections_added, mermaid)
    
    def _add_sequential_connections(self, node: BaseNode, node_id: str, 
                                  connections_added: Set[Tuple], mermaid: List[str]) -> None:
        """Add sequential node connections"""
        print(f"DEBUG: Checking sequential connections for {node_id} ({node})")
        print(f"  - has_next_node: {hasattr(node, 'next_node')}")
        if hasattr(node, 'next_node'):
            print(f"  - next_node: {node.next_node}")
            print(f"  - next_node_exists: {node.next_node is not None}")
            if node.next_node:
                print(f"  - next_node_id_in_dict: {id(node.next_node) in self.node_ids}")
                
        if hasattr(node, 'next_node') and node.next_node and id(node.next_node) in self.node_ids:
            next_id = self.node_ids[node.next_node]
            conn_key = (node_id, next_id)
            if conn_key not in connections_added:
                connection_line = f'    {node_id} --> {next_id}'
                mermaid.append(connection_line)
                connections_added.add(conn_key)
                print(f"DEBUG: Added sequential connection: {connection_line}")
            else:
                print(f"DEBUG: Connection already exists: {conn_key}")
        else:
            print(f"DEBUG: No sequential connection for {node_id}")
    
    def _add_parallel_connections(self, node: BaseNode, node_id: str,
                                connections_added: Set[Tuple], mermaid: List[str]) -> None:
        """Add parallel node connections"""
        if hasattr(node, 'parallel_branches'):  # New architecture - no action needed
            # New architecture stores ChainBuilders - JSON path handles these
            pass
        elif hasattr(node, 'parallel_nodes'):  # Legacy
            for child in node.parallel_nodes:  # type: ignore[attr-defined]
                if id(child) in self.node_ids:
                    child_id = self.node_ids[child]
                    # Parallel fork
                    fork_key = (node_id, child_id)
                    if fork_key not in connections_added:
                        mermaid.append(f'    {node_id} -.-> {child_id}')
                        connections_added.add(fork_key)
                    # Parallel join back (optional - can be removed for cleaner diagrams)
                    # join_key = (child_id, node_id)
                    # if join_key not in connections_added:
                    #     mermaid.append(f'    {child_id} -.-> {node_id}')
                    #     connections_added.add(join_key)
    
    def _add_decision_connections(self, node: BaseNode, node_id: str,
                                connections_added: Set[Tuple], mermaid: List[str]) -> None:
        """Add decision node connections"""
        if isinstance(node, Decision):
            for map_item in node.maps:
                target_node = map_item.node
                if isinstance(target_node, NodeType):
                    target_node = target_node.node_instance
                if id(target_node) in self.node_ids:
                    target_id = self.node_ids[target_node]
                    condition = str(map_item.condition)
                    decision_key = (node_id, target_id, condition)
                    if decision_key not in connections_added:
                        mermaid.append(f'    {node_id} -->|"{condition}"| {target_id}')
                        connections_added.add(decision_key)
    
    def _add_nested_sequence_connections(self, node: BaseNode, node_id: str,
                                       connections_added: Set[Tuple], mermaid: List[str]) -> None:
        """Add nested sequence connections"""
        # Import here to avoid circular imports
        from egregore.core.workflow.sequence.base import Sequence
        
        if isinstance(node, Sequence) and node.start and id(node.start) in self.node_ids:
            start_id = self.node_ids[node.start]
            nested_key = (node_id, start_id)
            if nested_key not in connections_added:
                mermaid.append(f'    {node_id} --> {start_id}')
                connections_added.add(nested_key)


def render_mermaid_schema(sequence: 'Sequence', mode: str = "overview") -> str:
    """Convenience function to render a sequence as Mermaid diagram
    
    Args:
        sequence: The sequence to render
        mode: "overview" for high-level view, "full" for detailed expansion
    """
    renderer = MermaidRenderer()
    return renderer.render(sequence, mode=mode)


# Legacy compatibility function
def sequence_to_mermaid(sequence: 'Sequence') -> str:
    """Legacy function for backward compatibility"""
    return render_mermaid_schema(sequence)