# V2 Workflow System with Native Agent Discovery Always Enabled

# Core workflow components with built-in discovery
from egregore.core.workflow.nodes import (
    Node, node, decision, BaseNode, parallel, ParallelNode,
    AsyncNode, AsyncBatchNode, BatchNode, NodeMapper, NodeType
)
from egregore.core.workflow.exceptions import ParallelExecutionError, ParallelTimeoutError
from egregore.core.workflow.state import SharedState, workflow_state
from egregore.core.workflow.sequence.base import Sequence, WorkflowController, WorkflowStoppedException

# Validation System
from egregore.core.workflow.validation import (
    validate_sequence, SequenceValidator, ValidationResult,
    ValidationError, ValidationWarning, ValidationIssue, ValidationSeverity
)
from egregore.core.workflow.validators import (
    CycleDetectionValidator, DependencyValidator, SchemaValidator
)

# Type Checking System
from egregore.core.workflow.type_checking import (
    set_type_checking_mode, get_type_checker, check_node_chain_types,
    WorkflowTypeChecker, TypeInfo, NodeTypeSignature
)

# Reporting System  
from egregore.core.workflow.reporting import (
    WorkflowReportingSystem, WorkflowMetricsCollector, WorkflowMetrics, 
    PerformanceSummary, ExecutionStatus, ErrorReport
)

# Native Agent Discovery - Always Enabled API
from egregore.core.workflow.native_discovery import (
    get_current_agents, get_current_agent_states, interrupt_current_agents,
    apply_policy_to_current_agents, get_agents_in_node, monitor_current_workflow,
    workflow_context, get_workflow_manager
)

# Low-level discovery components (for advanced usage)
from egregore.core.workflow.agent_discovery import AgentDiscoveryRegistry, get_agent_registry
from egregore.core.workflow.agent_interceptor import WorkflowAgentManager

# Agent discovery is natively integrated into the Agent class itself
# No separate initialization needed - discovery works automatically!

# Export main API - discovery is always available
__all__ = [
    # Core workflow components (discovery built-in)
    "Node", "node", "decision", "BaseNode", "parallel", "ParallelNode",
    "AsyncNode", "AsyncBatchNode", "BatchNode", "NodeMapper", "NodeType",
    "ParallelExecutionError", "ParallelTimeoutError",
    "SharedState", "workflow_state",
    "Sequence", "WorkflowController", "WorkflowStoppedException",
    
    # Validation System
    "validate_sequence", "SequenceValidator", "ValidationResult",
    "ValidationError", "ValidationWarning", "ValidationIssue", "ValidationSeverity",
    "CycleDetectionValidator", "DependencyValidator", "SchemaValidator",

    # Type Checking System
    "set_type_checking_mode", "get_type_checker", "check_node_chain_types",
    "WorkflowTypeChecker", "TypeInfo", "NodeTypeSignature",

    # Reporting System
    "WorkflowReportingSystem", "WorkflowMetricsCollector", "WorkflowMetrics",
    "PerformanceSummary", "ExecutionStatus", "ErrorReport",
    
    # Native Agent Discovery API - Always Available
    "get_current_agents",           # Get agents in current workflow
    "get_current_agent_states",     # Get agent states
    "interrupt_current_agents",     # Interrupt all current agents
    "apply_policy_to_current_agents", # Apply policies to current agents
    "get_agents_in_node",          # Get agents in specific node
    "monitor_current_workflow",     # Add monitoring callbacks
    "workflow_context",            # Explicit workflow naming
    "get_workflow_manager",        # Access global workflow manager
    
    # Low-level components (advanced usage)
    "AgentDiscoveryRegistry", "get_agent_registry", "WorkflowAgentManager"
]