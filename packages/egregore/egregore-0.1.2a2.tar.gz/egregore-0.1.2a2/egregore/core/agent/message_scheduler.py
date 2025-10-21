"""
MessageScheduler - Pure Context to ProviderThread conversion.

The MessageScheduler is responsible for ONLY:
- Converting Context tree to ProviderThread format using traverse API
- Converting ContextComponents to appropriate ContentBlocks
- Maintaining proper message ordering and structure

All temporal processing, scaffold management, and cycle handling
has been moved to the Agent level for correct timing.
"""

from typing import (
    TYPE_CHECKING,
    List,
    Optional,
    Union,
)
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..context_scaffolds import BaseContextScaffold
    from ...providers.core.structured_output import StructuredResponse
    from ..context_management.pact.components.core import PACTCore as ContextComponent
from ..messaging import (
    ProviderThread,
    TextContent,
    ProviderToolCall,
    ClientToolResponse,
    ProviderResponse,
)
from ..tool_calling.context_components import (
    ToolCall,
    ScaffoldCall,
)
from ..tool_calling.tool_declaration import ScaffoldOpDeclaration
from ..context_management.pact.context import Context

# Note: Multimedia ContextComponents (Image, Audio, Video, Document) exist in the V2 system
# But multimedia input conversion happens at provider level based on model capabilities
# MessageScheduler just handles basic text input conversion for now


class MessageScheduler:
    """Context session controller managing complete Context ↔ Provider cycle."""

    def __init__(self, context: Context):
        """Initialize MessageScheduler bound to specific context.
        
        Args:
            context: The Context instance this scheduler will manage
        """
        self.context = context

    # Note: update_temporal_state() REMOVED - temporal processing moved to Agent level
    # Note: _create_new_message_turn removed - Context.add_user()/add_assistant()
    # handle PACT depth management automatically via ContextOperations

    def render(self) -> ProviderThread:
        """
        Convert bound Context tree to ProviderThread using traverse API.

        Core algorithm:
        1. PREEMPTIVE CYCLE: Increment episode for performance optimization
        2. Iterate depths in canonical order (d-1, dN...d1, d0)
        3. For each depth, collect ALL components using traverse_branch()
        4. Convert each component to appropriate ContentBlock
        5. Create one message per depth with all content blocks
        6. Return ProviderThread with proper message types

        Returns:
            ProviderThread ready for provider consumption
        """
        from ..messaging import (
            ProviderThread,
            TextContent,
            SystemHeader,
            ClientRequest,
            ProviderResponse,
        )

        # PREEMPTIVE CYCLE: Increment episode preemptively for performance
        # (combines tree traversal with TTL cleanup in single pass)
        old_episode = self.context.current_episode
        print(f"[RENDER DEBUG] BEFORE episode increment, context tree:")
        for depth_comp in self.context.content:
            print(f"[RENDER DEBUG]   Depth {getattr(depth_comp, 'depth', '?')}: {type(depth_comp).__name__}")

        self.context.current_episode += 1
        print(f"[EPISODE DEBUG] Incremented episode: {old_episode} -> {self.context.current_episode}")

        print(f"[RENDER DEBUG] AFTER episode increment (TTL processing done), context tree:")
        for depth_comp in self.context.content:
            print(f"[RENDER DEBUG]   Depth {getattr(depth_comp, 'depth', '?')}: {type(depth_comp).__name__}")

        # Enforce retention capacity limits (keep max N operations per type)
        self._enforce_retention_limits()

        messages = []

        try:
            # Each depth = One message, All components at depth = Content blocks in that message
            for depth_component in self.context.content:  # Iterates in canonical order: d-1, dN...d1, d0
                content_blocks = []

                # Get the actual depth integer from the component
                depth = getattr(depth_component, 'depth', -1)

                # Determine role first so we can pass it to conversion
                role = 'user'  # default
                if depth != -1:
                    try:
                        role = getattr(depth_component, 'role', 'user')
                    except Exception:
                        pass

                # Collect ALL components at this depth using traverse API
                for component in self.context.traverse_branch(depth):
                    # Convert each component to appropriate ContentBlock with role context
                    content_block = self._convert_component_to_content_block(component, role)
                    if content_block:  # Only add non-None blocks
                        content_blocks.append(content_block)

                # Create one message for this depth if we have content
                if content_blocks:
                    if depth == -1:
                        # System header
                        messages.append(SystemHeader(content=content_blocks))
                    else:
                        # Create right message type based on role
                        if role == "assistant":
                            messages.append(ProviderResponse(content=content_blocks))
                        else:
                            messages.append(ClientRequest(content=content_blocks))

            return ProviderThread(messages=messages)

        except Exception as e:
            print(f"Error in render: {e}")
            import traceback
            traceback.print_exc()
            # Return empty thread on error
            return ProviderThread(messages=[])

    def seal(self, trigger: Optional[str] = None) -> None:
        """Seal the bound context with appropriate trigger.
        
        Args:
            trigger: Seal trigger (auto-determined if None)
        """
        if trigger is None:
            # Auto-determine trigger based on scheduler state
            trigger = "scheduler_seal"
        
        self.context.seal(trigger=trigger)

    def add_response(self, response: Union[ProviderResponse, "StructuredResponse"]) -> None:
        """Convert provider response to PACT components and add to bound context.
        
        Args:
            response: ProviderResponse or StructuredResponse from provider.call()
        """
        try:
            # Convert ProviderResponse content to ContextComponents
            components = self._convert_response_to_components(response)
            
            if components:
                # Create single assistant message with first component
                self.context.add_assistant(components[0])

                # Add remaining components to the same message container
                if len(components) > 1:
                    for component in components[1:]:
                        # Append to the active message's message container (dN,0,M)
                        self.context.pact_update("d0,0", component, mode="append")
            
        except Exception as e:
            print(f"Error incorporating response: {e}")

    def _convert_response_to_components(self, response: Union[ProviderResponse, "StructuredResponse"]) -> List["ContextComponent"]:
        """Convert ProviderResponse content to list of ContextComponents.

        Args:
            response: ProviderResponse object

        Returns:
            List of ContextComponents ready for context.add_assistant()
        """
        from ..context_management.pact.components.core import TextContent
        components = []

        try:
            if TYPE_CHECKING:
                from ...providers.core.structured_output import StructuredResponse

            # Handle StructuredResponse first
            if hasattr(response, 'parsed_result') and hasattr(response, 'raw_response'):
                # StructuredResponse - convert parsed result to text
                from ..context_management.pact.components.core import TextContent
                content_text = str(response.parsed_result)  # type: ignore
                component = TextContent(content=content_text)
                components.append(component)
            
            # Handle ProviderResponse with content list
            elif hasattr(response, 'content'):
                if isinstance(response.content, list):  # type: ignore
                    for content_block in response.content:  # type: ignore
                        component = self._convert_content_block_to_component(content_block)
                        if component:
                            components.append(component)
                
                # Handle simple text response
                elif isinstance(response.content, str):  # type: ignore
                    from ..context_management.pact.components.core import TextContent
                    component = TextContent(content=response.content)  # type: ignore
                    components.append(component)
            
            # Handle dict response
            elif isinstance(response, dict) and 'content' in response:
                from ..context_management.pact.components.core import TextContent
                component = TextContent(content=str(response['content']))
                components.append(component)
                
        except Exception as e:
            print(f"Error converting response to components: {e}")
        
        return components

    def _convert_content_block_to_component(self, content_block) -> Optional["ContextComponent"]:
        """Convert individual ContentBlock to ContextComponent.
        
        Args:
            content_block: ContentBlock from ProviderResponse
            
        Returns:
            ContextComponent or None
        """
        from ..messaging import TextContent as MessagingTextContent, ProviderToolCall
        from ..context_management.pact.components.core import TextContent

        try:
            # Convert MessagingTextContent to PACT TextContent component
            if isinstance(content_block, MessagingTextContent):
                return TextContent(content=content_block.content)
            
            # Convert ProviderToolCall to ToolCall using existing method
            elif isinstance(content_block, ProviderToolCall):
                return self._convert_provider_tool_call_to_component(content_block)
            
            # Handle other content types as text fallback
            elif hasattr(content_block, 'content'):
                return TextContent(content=str(content_block.content))
                
        except Exception as e:
            print(f"Error converting content block: {e}")
        
        return None



    def _get_tool_declaration(self, tool_name):
        """Get tool declaration from agent's tool registry."""
        try:
            # Access agent via context if available (dereference weak ref)
            agent_ref = getattr(self.context, "agent", None)
            agent = agent_ref() if callable(agent_ref) else agent_ref
            if agent and hasattr(agent, "tool_registry"):
                return agent.tool_registry.get_tool(tool_name)
            return None
        except Exception as e:
            print(f"Warning: Could not access tool registry for {tool_name}: {e}")
            return None

    def _convert_provider_tool_call_to_component(self, provider_tool_call):
        """
        Convert ProviderToolCall to ToolCall or ScaffoldCall based on registry lookup.

        Component Creation Process:
        1. Extract tool metadata from ProviderToolCall (tool_name, tool_call_id, parameters)
        2. Query agent's tool registry for tool declaration
        3. Detect tool type via isinstance(tool_decl, ScaffoldOpDeclaration)
        4. Create appropriate component:
           - ScaffoldCall: For scaffold operations with metadata
           - ToolCall: For regular tools
        5. Components inherit JSON content strategy and universal +tool_call tag

        Scaffold Detection Logic:
        - Uses ScaffoldOpDeclaration type detection (not pattern-based)
        - Extracts scaffold_id, scaffold_type, operation_name from declaration
        - Sets is_operation=True for scaffold components

        Args:
            provider_tool_call: ProviderToolCall object from LLM response

        Returns:
            ToolCall or ScaffoldCall, or None if conversion fails
        """
        try:
            # Extract data from ProviderToolCall
            tool_name = provider_tool_call.tool_name
            tool_call_id = provider_tool_call.tool_call_id
            parameters = provider_tool_call.parameters

            # Get tool declaration for type detection
            tool_decl = self._get_tool_declaration(tool_name)

            # Create appropriate component based on tool type
            if tool_decl and isinstance(tool_decl, ScaffoldOpDeclaration):
                # Scaffold operation - create ScaffoldCall with metadata
                return ScaffoldCall(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    parameters=parameters,
                    scaffold_id=getattr(tool_decl, "scaffold_id", "unknown"),
                    scaffold_type=getattr(tool_decl, "scaffold_type", "unknown"),
                    operation_name=getattr(tool_decl, "operation_name", tool_name),
                )
            else:
                # Regular tool - create ToolCall
                return ToolCall(
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    parameters=parameters,
                )
        except Exception as e:
            print(f"Warning: Could not convert ProviderToolCall to component: {e}")
            return None

    def _reset_active_head(self) -> None:
        """Reset the active_message to an empty state with a fresh/empty mc@0."""
        try:
            active_head = self.context.active_message
            # Keep the existing mc if present; just ensure it's empty and the only child
            active_mc = active_head.get_message_container()

            # Clear content in the core message container
            if isinstance(active_mc.content, list):
                for child in list(active_mc.content):
                    active_mc.remove_child(child)

            # Remove any non-core children from active head
            if hasattr(active_head, "content"):
                # Use CoreOffsetArray methods to clear properly
                if hasattr(active_head.content, "get_offsets"):
                    # Remove all children first, then add the message container
                    for offset in list(active_head.content.get_offsets()):
                        if offset != 0:  # Keep offset 0 for the core message container
                            # Use remove method if available
                            if hasattr(active_head.content, "remove"):
                                active_head.content.remove(offset)
                    # Ensure message container is at offset 0
                    active_head.content[0] = active_mc
                elif isinstance(active_head.content, list):
                    # Handle regular list content
                    active_head.content.clear()
                    active_head.content.append(active_mc)
                # Update navigation cache: keep only active_mc
                active_head.metadata.children = [active_mc]
                active_mc.metadata.parent = active_head
        except Exception as e:
            print(f"Warning: Failed to reset active head: {e}")

    # Temporal processing methods
    # Note: _process_temporal_lifecycle removed - components handle TTL via _is_expired() method

    # Note: _build_context_from_inputs and _convert_inputs_to_components removed
    # Use Context.add_user()/add_assistant() for message building

    def _get_component_text(self, component) -> str:
        """Extract text content from a component - just handle strings"""
        if not component:
            return ""

        # If component has string content, return it
        if hasattr(component, "content") and isinstance(component.content, str):
            return component.content

        # If component has nested content, extract text from children
        if hasattr(component, "content") and hasattr(component.content, "get_offsets"):
            text_parts = []
            offsets = component.content.get_offsets()
            for offset in offsets:
                child = component.content[offset]
                if hasattr(child, "content") and isinstance(child.content, str):
                    text_parts.append(child.content)

            return " ".join(text_parts).strip()

        return ""

    def _convert_component_to_content_block(self, component, turn_role=None):
        """Convert a ContextComponent to appropriate MessagePart for providers"""
        if not component:
            return None

        # Skip container components - they don't have their own content, only organize children
        from ..context_management.pact.components.core import (
            PACTContainer,
            MessageContainer,
            SystemHeader,
            MessageTurn
        )

        if isinstance(component, (PACTContainer, MessageContainer, SystemHeader, MessageTurn)):
            return None

        # Handle ToolCall - convert to ProviderToolCall
        from ..tool_calling.context_components import ToolCall
        if isinstance(component, ToolCall):
            return ProviderToolCall(
                tool_name=component.tool_name,
                tool_call_id=component.tool_call_id,
                parameters=component.parameters or {},
            )

        # Handle ToolResult - always convert to ClientToolResponse
        if hasattr(component, "tool_call_id") and hasattr(component, "success"):
            tool_name = getattr(component, "tool_name", "unknown")
            content_text = self._get_component_text(component)
            return ClientToolResponse(
                tool_call_id=component.tool_call_id,
                tool_name=tool_name,
                success=component.success,
                message=content_text or f"Tool {tool_name} execution result",
            )

        # Handle multimedia components
        # Note: These would need proper media data/URL handling in real implementation
        if hasattr(component, "media_type") or hasattr(component, "mime_type"):
            media_type = getattr(
                component, "media_type", getattr(component, "mime_type", "unknown")
            )

            # Create appropriate multimedia content based on type
            if "image" in media_type.lower():
                # For now, create placeholder ImageContent - would need real media data
                return TextContent(content=f"📷 Image: {media_type}")
            elif "audio" in media_type.lower():
                return TextContent(content=f"🎵 Audio: {media_type}")
            elif "video" in media_type.lower():
                return TextContent(content=f"🎬 Video: {media_type}")
            elif "document" in media_type.lower() or "pdf" in media_type.lower():
                return TextContent(content=f"📄 Document: {media_type}")
            else:
                return TextContent(content=f"📎 Media: {media_type}")

        # Handle standard text components
        text_content = self._get_component_text(component)
        if text_content:
            return TextContent(content=text_content)

        return None

    def _enforce_retention_limits(self) -> None:
        """
        Enforce retention capacity limits for scaffold operations and tool results.

        Retention capacity limits prevent context bloat by keeping only the N most
        recent operations per type. When limits are exceeded, oldest call+result
        pairs are deleted together to maintain registry consistency.

        Called automatically during render() after TTL expiry.
        """
        try:
            # Enforce scaffold operation retention
            self._enforce_scaffold_retention()

            # Enforce tool result retention (for regular tools)
            self._enforce_tool_retention()

        except Exception as e:
            # Log but don't fail rendering if retention enforcement has issues
            logger.warning(f"Retention enforcement failed: {e}")

    def _enforce_scaffold_retention(self) -> None:
        """Enforce retention limits for scaffold operations."""
        # Get agent reference from context (dereference weak ref)
        agent_ref = getattr(self.context, 'agent', None)
        agent = agent_ref() if callable(agent_ref) else agent_ref
        if not agent:
            return  # No agent = no scaffolds to enforce

        # Get scaffold results from active message only (depth 0)
        # Historical results at depth 1+ should not be deleted again
        scaffold_results = self.context.select("(d0) .scaffold_result")
        if not scaffold_results:
            return  # No scaffold results to enforce

        # Group results by (scaffold_id, operation_name)
        from collections import defaultdict
        groups = defaultdict(list)

        for result in scaffold_results:
            scaffold_id = getattr(result, 'scaffold_id', None)
            operation_name = getattr(result, 'operation_name', None)
            if scaffold_id and operation_name:
                groups[(scaffold_id, operation_name)].append(result)

        # For each group, enforce retention limit
        for (scaffold_id, operation_name), results in groups.items():
            # Get scaffold instance to check retention limit
            scaffold = agent._get_scaffold_by_id(scaffold_id)
            if not scaffold:
                continue

            # Get retention limit for this operation
            retention_limit = scaffold._get_operation_retention(operation_name)

            # If over limit, delete oldest pairs
            if len(results) > retention_limit:
                # Sort by execution_time (oldest first)
                results.sort(key=lambda r: getattr(r, 'execution_time', 0))

                # Calculate how many to remove
                excess_count = len(results) - retention_limit
                results_to_remove = results[:excess_count]

                # Delete each result and its paired call
                for result in results_to_remove:
                    self._remove_paired_scaffold_operation(result)

    def _enforce_tool_retention(self) -> None:
        """Enforce retention limits for regular tool results using registry tracking."""
        # Get agent reference for tool retention config
        # Context.agent is a weakref.ref, need to call it to get actual agent
        agent_ref = getattr(self.context, 'agent', None)
        if agent_ref is None:
            print("[RETENTION DEBUG] No agent ref, skipping retention")
            return

        # Dereference weak reference (returns None if GC'd)
        agent = agent_ref() if callable(agent_ref) else agent_ref
        if not agent:
            print("[RETENTION DEBUG] Agent ref expired, skipping retention")
            return

        # Get tool retention config (use operation_retention for tools)
        tool_retention = getattr(agent, 'operation_retention', None)
        if not tool_retention:
            print("[RETENTION DEBUG] No tool_retention config, skipping")
            return

        # Handle dict-based retention (use default if dict)
        if isinstance(tool_retention, dict):
            tool_retention = max(tool_retention.values()) if tool_retention else None
            if not tool_retention:
                print("[RETENTION DEBUG] Empty dict, skipping")
                return

        print(f"[RETENTION DEBUG] Starting retention enforcement: limit={tool_retention}")
        logger.debug(f"Tool retention enforcement: limit={tool_retention}")

        # Use registry execution tracking (no selects needed)
        tool_executions = self.context._registry._tool_executions
        print(f"[RETENTION DEBUG] Tool executions: {dict(tool_executions)}")

        # Iterate over copy to avoid modification-during-iteration issues
        for tool_name in list(tool_executions.keys()):
            call_ids = tool_executions[tool_name]
            list_id_before = id(self.context._registry._tool_executions[tool_name])
            print(f"[RETENTION DEBUG] Checking tool '{tool_name}': {len(call_ids)} executions vs limit {tool_retention}")
            print(f"[RETENTION DEBUG] call_ids is same object as registry list? {call_ids is self.context._registry._tool_executions[tool_name]}")
            print(f"[RETENTION DEBUG] List ID before: {list_id_before}")
            if len(call_ids) > tool_retention:
                # Keep last N, delete rest - make a copy of the list to avoid modification during iteration
                to_delete = list(call_ids[:-tool_retention])
                print(f"[RETENTION DEBUG] Will delete {len(to_delete)} oldest: {to_delete}")
                logger.debug(f"Tool '{tool_name}': {len(call_ids)} executions, deleting {len(to_delete)} oldest")

                for tool_call_id in to_delete:
                    print(f"[RETENTION DEBUG] Calling _remove_paired_tool_operation for {tool_call_id}")
                    self._remove_paired_tool_operation(tool_call_id)

                list_id_after = id(self.context._registry._tool_executions[tool_name])
                print(f"[RETENTION DEBUG] List ID after: {list_id_after}, Same object? {list_id_before == list_id_after}")
                print(f"[RETENTION DEBUG] call_ids after loop: {call_ids}, ID: {id(call_ids)}")
                print(f"[RETENTION DEBUG] Registry list after: {self.context._registry._tool_executions.get(tool_name, [])}, ID: {id(self.context._registry._tool_executions[tool_name])}")
                print(f"[RETENTION DEBUG] Are they the same object? {id(call_ids) == id(self.context._registry._tool_executions[tool_name])}")
                logger.debug(f"Retention enforcement complete for '{tool_name}'")

    def _remove_paired_scaffold_operation(self, result) -> None:
        """Remove a scaffold result and its paired call component."""
        tool_call_id = getattr(result, 'tool_call_id', None)
        if not tool_call_id:
            # No tool_call_id = can't find pair, just delete result
            self.context.pact_delete(f"{{id={result.id}}}")
            return

        # Get paired call and result IDs from registry
        pair = self.context._registry.get_tool_pair(tool_call_id)

        if pair:
            call_id, result_id = pair
            # Delete both components
            self.context.pact_delete(f"{{id={call_id}}}")
            self.context.pact_delete(f"{{id={result_id}}}")
            # Clean up registry
            self._unregister_tool_pair(tool_call_id)
        else:
            # No pair found, just delete result
            self.context.pact_delete(f"{{id={result.id}}}")

    def _remove_paired_tool_operation(self, tool_call_id: str) -> None:
        """Remove a tool call/result pair by tool_call_id."""
        print(f"[REMOVE DEBUG] _remove_paired_tool_operation called for {tool_call_id}")
        pair = self.context._registry.get_tool_pair(tool_call_id)
        print(f"[REMOVE DEBUG] get_tool_pair returned: {pair}")

        if pair:
            call_id, result_id = pair
            print(f"[REMOVE DEBUG] About to delete components: call_id={call_id}, result_id={result_id}")
            logger.debug(f"Deleting tool pair: call={call_id}, result={result_id}")

            # Delete components - deletion handler will automatically unregister the pair
            # Note: If components don't exist, deletion will fail silently
            print(f"[REMOVE DEBUG] Calling pact_delete for call_id={call_id}")
            self.context.pact_delete(f"{{id={call_id}}}")
            print(f"[REMOVE DEBUG] Calling pact_delete for result_id={result_id}")
            self.context.pact_delete(f"{{id={result_id}}}")
            print(f"[REMOVE DEBUG] Both components deleted from context")

            # Always unregister from registry, even if components don't exist
            # This handles test cases where registry is populated without actual components
            print(f"[REMOVE DEBUG] Ensuring registry cleanup for {tool_call_id}")
            self.context._registry.unregister_tool_pair(tool_call_id)
        else:
            print(f"[REMOVE DEBUG] No pair found in registry for {tool_call_id}")
            logger.debug(f"No registry pair found for tool_call_id={tool_call_id}")
