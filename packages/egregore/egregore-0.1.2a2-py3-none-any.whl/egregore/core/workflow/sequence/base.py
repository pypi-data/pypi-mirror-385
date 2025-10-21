import asyncio
import uuid
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, TYPE_CHECKING

from egregore.core.workflow.nodes import BaseNode, NodeType, Node, Decision, node_factory
from egregore.core.workflow.state import SharedState, WorkflowStateContext
node = node_factory
from egregore.core.workflow.sequence.controller import WorkflowController, WorkflowStoppedException

if TYPE_CHECKING:
    from egregore.core.workflow.chain_builder import ChainSpec


class HooksProxy:
    def __init__(self, controller: 'WorkflowController'):
        self._controller = controller

    @property
    def pre_execution(self):
        return self._controller._create_hook_decorator('pre_execution')

    @property
    def post_execution(self):
        return self._controller._create_hook_decorator('post_execution')

    @property
    def on_error(self):
        return self._controller._create_hook_decorator('on_error')

    @property
    def pre_sequence(self):
        return self._controller._create_hook_decorator('pre_sequence')

    @property
    def post_sequence(self):
        return self._controller._create_hook_decorator('post_sequence')

    @property
    def on_sequence_error(self):
        return self._controller._create_hook_decorator('on_sequence_error')


class Sequence(Node):
    def __init__(self, chain_result, name: Optional[str] = None, max_steps: int = 1000):
        desired_name = name or f"Sequence_{uuid.uuid4().hex[:8]}"
        super().__init__(label=desired_name)
        self.name = desired_name
        self._produces_data = False
        self.state = SharedState(instance_name=self.name)
        self.state.workflow = self
        self._owns_state = True

        self.max_steps = max_steps
        self.workflow_id = str(uuid.uuid4())
        self.created_at = datetime.now()

        from egregore.core.workflow.nodes.registry import NodeRegistry
        from egregore.core.workflow.chain_builder import ChainBuilder, ChainSpec
        self._local_node_registry = NodeRegistry()

        if isinstance(chain_result, ChainSpec):
            self._chain_spec = chain_result
        elif isinstance(chain_result, ChainBuilder):
            self._chain_spec = chain_result.to_spec()
        elif chain_result is None:
            self._chain_spec = ChainSpec()
        else:
            if hasattr(chain_result, 'node'):
                builder = ChainBuilder.from_single(chain_result)
            else:
                builder = ChainBuilder(
                    node_types=[chain_result],
                    edges=[],
                    alias_map={}
                )
            self._chain_spec = builder.to_spec()

        self.start = None
        self._graph = None
        self._graph_built = False
        self.controller = WorkflowController(self)
        self._hooks_proxy = None

    def enable_loop_control(self, max_iterations: int = 10, max_nested_loops: int = 5):
        self.state.max_loop_iterations = max_iterations
        self.state.max_nested_loops = max_nested_loops
        self.state.loop_detection_enabled = True
        return self

    @property
    def hooks(self) -> HooksProxy:
        if self._hooks_proxy is None:
            self._hooks_proxy = HooksProxy(self.controller)
        return self._hooks_proxy

    def _get_first_node_in_chain(self) -> BaseNode:
        if self.start is None:
            return self
        return self.start

    def _build_graph(self):
        from egregore.core.workflow.graph import GraphBuilder

        if self._graph_built:
            return

        graph_builder = GraphBuilder()
        self._graph = graph_builder.build_from_sequence(self)
        self._graph_built = True
        self._sync_router_flags_to_specs()

    def _sync_router_flags_to_specs(self):
        if not self._graph:
            return

        for graph_node in self._graph.nodes.values():
            node_spec = graph_node.node_instance
            if hasattr(node_spec, 'is_router'):
                node_spec.is_router = graph_node.is_router

                if hasattr(node_spec, '_node_type_ref') and node_spec._node_type_ref:
                    node_ref = node_spec._node_type_ref
                    node_ref._is_router = graph_node.is_router

    def _set_graph_on_nodes(self, node_instances):
        """Set graph reference on instantiated nodes after they're created.

        Args:
            node_instances: List of instantiated BaseNode objects
        """
        if not self._graph:
            return

        for instance in node_instances:
            instance._graph = self._graph

            for graph_node in self._graph.nodes.values():
                node_spec = graph_node.node_instance
                if hasattr(node_spec, 'node_name') and hasattr(instance, 'name'):
                    if node_spec.node_name == instance.name:
                        instance._graph_node = graph_node
                        break

    def _instantiate_from_spec(self, chain_spec: 'ChainSpec') -> BaseNode:
        """Create fresh node instances from ChainSpec (full deferred instantiation).

        Called at the START of each execute() to ensure complete isolation.
        All Sequences now use this path exclusively.

        Args:
            chain_spec: ChainSpec with NodeSpec/SequenceSpec objects

        Returns:
            Fresh start node with complete chain of fresh instances
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.debug(f"[INSTANTIATE_FROM_SPEC] Creating fresh instances from ChainSpec")
        logger.debug(f"[INSTANTIATE_FROM_SPEC] ChainSpec has {len(chain_spec.nodes)} nodes, {len(chain_spec.edges)} edges")

        instances = []
        for idx, node_spec in enumerate(chain_spec.nodes):
            instance = node_spec.instantiate()
            instances.append(instance)
            logger.debug(f"[INSTANTIATE_FROM_SPEC] Created instance {idx}: {instance.name} (guid={instance.guid[:8]})")

            self._local_node_registry.register_node(instance)

            if self._graph:
                instance._graph = self._graph  # type: ignore[attr-defined]
                for graph_node in self._graph.nodes.values():
                    if graph_node.node_instance == node_spec:
                        instance._graph_node = graph_node  # type: ignore[attr-defined]
                        instance._is_router = graph_node.is_router  # type: ignore[attr-defined]
                        logger.debug(f"[INSTANTIATE_FROM_SPEC] Set graph ref for {instance.name}, is_router={graph_node.is_router}")
                        break

            if isinstance(instance, Sequence):
                instance.state = self.state
                instance.state.workflow = self
                instance._owns_state = False
                logger.debug(f"[INSTANTIATE_FROM_SPEC] Injected state into nested Sequence: {instance.name}")

        for source_idx, target_idx in chain_spec.edges:
            source = instances[source_idx]
            target = instances[target_idx]
            source.next_node = target
            logger.debug(f"[INSTANTIATE_FROM_SPEC] Connected: {source.name} -> {target.name}")

        start_idx = chain_spec.get_start_node_idx()
        start_node = instances[start_idx]
        logger.debug(f"[INSTANTIATE_FROM_SPEC] Start node: {start_node.name}")

        return start_node


    def execute(self, *args, config: Optional[Dict] = None, **kwargs):
        """Execute workflow synchronously - required for Node inheritance

        Args:
            *args: Positional arguments (initial input)
            config: Optional configuration dict containing:
                - error_config: Error handling configuration
                  - strategy: "default" | "strict" | "permissive"
                  - max_retries: int (default 3)
                  - base_delay: float (default 1.0)
                  - max_delay: float (default 30.0)
            **kwargs: Additional keyword arguments
        """
        return asyncio.run(self.async_execute(*args, config=config, **kwargs))

    async def async_execute(self, *args, config: Optional[Dict] = None, **kwargs):
        """Execute workflow asynchronously with controller support

        Args:
            *args: Positional arguments (initial input)
            config: Optional configuration dict containing:
                - error_config: Error handling configuration
                  - strategy: "default" | "strict" | "permissive"
                  - max_retries: int (default 3)
                  - base_delay: float (default 1.0)
                  - max_delay: float (default 30.0)
            **kwargs: Additional keyword arguments
        """
        if not self._graph_built:
            self._build_graph()

        if self.start is None and hasattr(self, '_chain_spec'):
            self.start = self._instantiate_from_spec(self._chain_spec)

        # Store config for _run_sequence_async
        self._execution_config = config

        with WorkflowStateContext(self.state):
            try:
                self.controller._state = 'running'

                await self.controller._execute_hooks('pre_sequence', {
                    'sequence': self,
                    'target_name': self.name
                })

                if hasattr(self.state, '_notify_state_change'):
                    self.state._notify_state_change('workflow_started', self.name, {
                        'timestamp': time.time(),
                        'workflow_id': self.workflow_id
                    })

                input_data = None

                if not self._owns_state:
                    input_data = self.state.get_previous_output() if hasattr(self.state, 'get_previous_output') else None
                elif self.state and hasattr(self.state, 'executions') and self.state.executions:
                    input_data = self.state[-1]
                elif args:
                    input_data = args[0]
                    self.state.initial_input = input_data
                    if hasattr(self.state, '_legacy_initial_input'):
                        self.state._legacy_initial_input.execute = input_data
                    self.state.set_previous_output(input_data)

                result = await self._run_sequence_async(*args, **kwargs)

                self.controller._state = 'completed'

                await self.controller._execute_hooks('post_sequence', {
                    'sequence': self,
                    'result': result,
                    'target_name': self.name
                })

                if hasattr(self.state, '__setitem__'):
                    self.state[self.name] = result

                if hasattr(self.state, '_notify_state_change'):
                    self.state._notify_state_change('workflow_completed', self.name, {
                        'timestamp': time.time(),
                        'result': str(result)[:100] if result else None
                    })

                return result
                
            except WorkflowStoppedException:
                return None
            except Exception as e:
                self.controller._state = 'error'

                await self.controller._execute_hooks('on_sequence_error', {
                    'sequence': self,
                    'error': e,
                    'target_name': self.name
                })

                if hasattr(self.state, '_notify_state_change'):
                    self.state._notify_state_change('workflow_error', self.name, {
                        'timestamp': time.time(),
                        'error': str(e)
                    })
                raise
            finally:
                if hasattr(self.state, 'clear_store') and self._owns_state:
                    self.state.clear_store()

    async def _run_sequence_async(self, *args, **kwargs):
        """Run sequence using graph-driven execution."""
        from egregore.core.workflow.graph_controller import GraphExecutionController
        from egregore.core.workflow.error_handler import create_error_handler

        # Extract error config from execution config
        config = getattr(self, '_execution_config', None)
        error_config = (config or {}).get("error_config") if config else None

        # Create error handler if error_config provided
        error_handler = None
        if error_config:
            strategy = error_config.get("strategy", "default")
            max_retries = error_config.get("max_retries", 3)
            base_delay = error_config.get("base_delay", 1.0)
            max_delay = error_config.get("max_delay", 30.0)

            error_handler = create_error_handler(
                strategy_type=strategy,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay
            )

        controller = GraphExecutionController(
            self._graph,
            state=self.state,
            execution_history=self.controller.execution_history,
            workflow_controller=self.controller,
            error_handler=error_handler,
            error_config=error_config or {}
        )

        initial_input = None
        if args:
            initial_input = args[0]
        elif hasattr(self.state, 'get_previous_output'):
            initial_input = self.state.get_previous_output()

        result = await controller.execute_graph(self._graph.root_node, initial_input)
        return result

    def get_schema(self, format: str = "mermaid", mode: str = "overview") -> str:
        """Generate a schema representation of the workflow pipeline
        
        Args:
            format: The schema format ("mermaid", "json", "text")
            mode: The detail mode for mermaid format ("overview", "full")
                  - "overview": High-level view showing sequences as single blocks
                  - "full": Detailed view expanding all nested sequences and nodes
            
        Returns:
            Schema representation as a string
        """
        if format.lower() == "mermaid":
            from .mermaid_renderer import render_mermaid_schema
            return render_mermaid_schema(self, mode=mode)
        elif format.lower() == "json":
            return json.dumps(self.to_json(), indent=2)
        elif format.lower() == "text":
            return self._generate_text_schema()
        else:
            raise ValueError(f"Unsupported schema format: {format}. Supported formats: mermaid, json, text")
    
    def _graph_get_instance_for_node(self, node_id: str):
        """Get instantiated node from graph controller cache.

        Args:
            node_id: Graph node ID

        Returns:
            Node instance or None
        """


        if hasattr(self, '_graph') and self._graph:

            graph_node = self._graph.nodes.get(node_id)
            if graph_node:

                if hasattr(graph_node.node_instance, 'instantiate'):
                    return graph_node.node_instance.instantiate()
                return graph_node.node_instance
        return None

    def _generate_text_schema(self) -> str:
        """Generate a text-based schema representation"""
        if not self.start:
            return f"Empty Sequence: {self.name}"

        lines = [f"Workflow Schema: {self.name}"]
        lines.append("=" * (20 + len(self.name)))
        lines.append("")

        visited = set()
        
        def traverse_text(node, depth=0, prefix=""):

            if not node or node.guid in visited:
                return
            visited.add(node.guid)
            
            indent = "  " * depth
            node_name = getattr(node, 'name', str(node))
            

            if isinstance(node, Sequence):
                icon = "🔄"
                node_type = "Sequence"
            elif hasattr(node, 'parallel_branches'):
                icon = "⚡"
                node_type = "Parallel"
            elif isinstance(node, Decision):
                icon = "❓"
                node_type = "Decision"
            elif hasattr(node, 'agent'):
                icon = "🤖"
                node_type = "Agent"
            else:
                icon = "📋"
                node_type = "Node"
            
            lines.append(f"{indent}{prefix}{icon} {node_name} ({node_type})")
            

            if hasattr(node, 'parallel_branches'):
                if self._graph and hasattr(node, '_graph_node') and node._graph_node:  # type: ignore[attr-defined]
                    subgraphs = self._graph.get_subgraphs(node._graph_node)  # type: ignore[attr-defined]
                    if subgraphs:
                        for i, subgraph in enumerate(subgraphs):

                            if subgraph.terminal_node:
                                terminal_instance = self._graph_get_instance_for_node(subgraph.terminal_node.id)
                                if terminal_instance:
                                    child_prefix = f"├─ " if i < len(subgraphs) - 1 else "└─ "
                                    traverse_text(terminal_instance, depth + 1, child_prefix)
            

            elif isinstance(node, Decision):
                for i, map_item in enumerate(node.maps):
                    target_node = map_item.node
                    if isinstance(target_node, NodeType):
                        target_node = target_node.node_instance
                    condition = str(map_item.condition)
                    branch_prefix = f"├─ [{condition}] " if i < len(node.maps) - 1 else f"└─ [{condition}] "
                    traverse_text(target_node, depth + 1, branch_prefix)
            

            elif isinstance(node, Sequence) and node.start:
                traverse_text(node.start, depth + 1, "└─ ")
            

            if hasattr(node, 'next_node') and node.next_node:
                traverse_text(node.next_node, depth, "")
        
        traverse_text(self.start)
        

        lines.append("")
        lines.append("Metadata:")
        lines.append(f"  - Workflow ID: {self.workflow_id}")
        lines.append(f"  - Created: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"  - Max Steps: {self.max_steps}")
        lines.append(f"  - Controller State: {self.controller.state}")
        
        return "\n".join(lines)


    def run(self, *args, **kwargs):
        """Legacy run method for backward compatibility"""
        return self.execute(*args, **kwargs)

    async def run_async(self, *args, **kwargs):
        """Legacy async run method for backward compatibility"""
        return await self.async_execute(*args, **kwargs)

    def __call__(self, *args, reset_state=True, **kwargs):
        """Legacy callable interface for backward compatibility"""
        if reset_state:
            self.state = SharedState(instance_name=self.name)
            self.state.workflow = self
        return self.execute(*args, **kwargs)

    def to_json(self) -> Dict[str, Any]:
        """Serialize workflow structure to JSON for Cerebrum visual builder"""
        return {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'type': 'sequence',
            'nodes': self._serialize_nodes(),
            'connections': self._serialize_connections(),
            'metadata': {
                'created_at': self.created_at.isoformat(),
                'version': '1.0',
                'max_steps': self.max_steps,
                'description': getattr(self, 'description', '')
            }
        }

    def _serialize_nodes(self) -> List[Dict[str, Any]]:
        """Serialize all nodes in the workflow"""
        nodes = []
        visited = set()
        position_x = 0
        
        def serialize_node_recursive(node):
            nonlocal position_x

            if node.guid in visited:
                return
            visited.add(node.guid)
            
            node_id = f"node_{node.guid}"
            node_name = getattr(node, 'name', str(node))
            node_data = {
                'id': node_id,
                'name': node_name,
                'type': self._get_node_type(node),
                'position': {'x': position_x, 'y': 100},

                'guid': node.guid,
                'alias': node.alias_name,
                'canonical_name': node.canonical_name or node.name,
                'effective_name': node.effective_name
            }
            

            if hasattr(node, 'parallel_branches'):
                node_data['type'] = 'parallel'

                node_data['children'] = []
                child_position_y = 50


                if self._graph and hasattr(node, '_graph_node') and node._graph_node:
                    subgraphs = self._graph.get_subgraphs(node._graph_node)
                    if subgraphs:
                        for i, subgraph in enumerate(subgraphs):

                            if subgraph.terminal_node:
                                terminal_instance = self._graph_get_instance_for_node(subgraph.terminal_node.id)
                                if terminal_instance:
                                    child_data = {
                                        'id': f"node_{terminal_instance.guid}",
                                        'name': getattr(terminal_instance, 'name', str(terminal_instance)),
                                        'type': self._get_node_type(terminal_instance),
                                        'guid': terminal_instance.guid,
                                        'alias': terminal_instance.alias_name,
                                        'canonical_name': terminal_instance.canonical_name or terminal_instance.name,
                                        'effective_name': terminal_instance.effective_name
                                    }
                                    node_data['children'].append(child_data)


                                    child_node_data = {
                                        'id': f"node_{terminal_instance.guid}",
                                        'name': getattr(terminal_instance, 'name', str(terminal_instance)),
                                        'type': self._get_node_type(terminal_instance),
                                        'position': {'x': position_x + 100, 'y': child_position_y + (i * 100)},
                                        'guid': terminal_instance.guid,
                                        'alias': terminal_instance.alias_name,
                                        'canonical_name': terminal_instance.canonical_name or terminal_instance.name,
                                        'effective_name': terminal_instance.effective_name
                                    }
                                    nodes.append(child_node_data)
                                    visited.add(terminal_instance.guid)
                    
            elif isinstance(node, Decision):
                node_data['type'] = 'decision'
                node_data['conditions'] = {}
                for map_item in node.maps:
                    condition_key = str(map_item.condition)
                    target_node = map_item.node
                    if isinstance(target_node, NodeType):
                        target_node = target_node.node_instance
                    node_data['conditions'][condition_key] = {
                        'target_id': f"node_{target_node.guid}",
                        'target_name': getattr(target_node, 'name', str(target_node))
                    }
                    
            elif hasattr(node, 'agent'):
                node_data['type'] = 'agent'
                node_data['agent_config'] = {
                    'name': getattr(node, 'node_name', 'unknown'),
                    'run_type': getattr(node, 'run_type', 'call'),
                    'kwargs': getattr(node, 'call_kwargs', {})
                }
                
            elif isinstance(node, Sequence):
                node_data['type'] = 'sequence'
                node_data['nested_workflow'] = node.to_json()
            
            nodes.append(node_data)
            position_x += 200
            

            if hasattr(node, 'next_node') and node.next_node:
                serialize_node_recursive(node.next_node)
        

        if self.start:
            serialize_node_recursive(self.start)
        
        return nodes

    def _serialize_connections(self) -> List[Dict[str, Any]]:
        """Serialize connections between nodes"""
        connections = []
        visited = set()
        
        def serialize_connections_recursive(node):

            if node.guid in visited:
                return
            visited.add(node.guid)
            
            node_id = f"node_{node.guid}"
            

            if hasattr(node, 'next_node') and node.next_node:
                connection = {
                    'id': f"conn_{node.guid}_{node.next_node.guid}",
                    'from': node_id,
                    'to': f"node_{node.next_node.guid}",
                    'type': 'sequence'
                }
                connections.append(connection)
                serialize_connections_recursive(node.next_node)
                
            elif hasattr(node, 'parallel_branches'):

                if self._graph and hasattr(node, '_graph_node') and node._graph_node:
                    subgraphs = self._graph.get_subgraphs(node._graph_node)
                    if subgraphs:
                        for subgraph in subgraphs:
                            if subgraph.terminal_node:
                                terminal_instance = self._graph_get_instance_for_node(subgraph.terminal_node.id)
                                if terminal_instance:
                                    connection = {
                                        'id': f"conn_{node.guid}_{terminal_instance.guid}",
                                        'from': node_id,
                                        'to': f"node_{terminal_instance.guid}",
                                        'type': 'parallel'
                                    }
                                    connections.append(connection)
                    
            elif isinstance(node, Decision):
                for map_item in node.maps:
                    target_node = map_item.node
                    if isinstance(target_node, NodeType):
                        target_node = target_node.node_instance
                    connection = {
                        'id': f"conn_{node.guid}_{target_node.guid}",
                        'from': node_id,
                        'to': f"node_{target_node.guid}",
                        'type': 'decision',
                        'condition': str(map_item.condition)
                    }
                    connections.append(connection)
                    serialize_connections_recursive(target_node)
        
        if self.start:
            serialize_connections_recursive(self.start)
        
        return connections

    def _get_node_type(self, node) -> str:
        """Determine node type for serialization"""
        if hasattr(node, 'parallel_branches'):
            return 'parallel'
        elif isinstance(node, Decision):
            return 'decision'
        elif hasattr(node, 'agent'):
            return 'agent'
        elif isinstance(node, Sequence):
            return 'sequence'
        else:
            return 'node'

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> 'Sequence':
        """Reconstruct Sequence from JSON for Cerebrum workflow builder"""


        
        name = json_data.get('name', 'Reconstructed')
        workflow_id = json_data.get('workflow_id')
        


        instance = cls(None, name=name)
        instance.workflow_id = workflow_id
        
        return instance

    def __repr__(self):
        return f"Sequence({self.name})"

    def _repr_markdown_(self):
        """Jupyter notebook representation"""
        return f"**Sequence: {self.name}**\n\nWorkflow ID: `{self.workflow_id}`\n\nController State: `{self.controller.state}`"