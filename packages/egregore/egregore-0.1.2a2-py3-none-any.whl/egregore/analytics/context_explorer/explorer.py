"""
Context Explorer - Context State Debugger

A context state debugger that provides step-by-step execution of real conversation
operations with immediate context visualization. Shows exactly what context the LLM
sees at each step to debug AI behavior.
"""

from typing import Any, Optional
from contextlib import contextmanager
from egregore.core.context_management import Context
from egregore.analytics.context_viewer import ContextViewer
from egregore.core.tool_calling.tool_registry import ToolRegistry
from egregore.core.tool_calling.tool_executor import ToolExecutor


class ContextExplorer:
    """
    Context state debugger for step-by-step conversation execution.

    Uses real agents, context, tools, and scaffolds to show exactly what
    context state shapes LLM behavior at each step.
    """

    def __init__(self, context_or_agent=None):
        """
        Initialize ContextExplorer with flexible input.

        Args:
            context_or_agent: None (fresh context), Context instance, or Agent instance
        """
        if context_or_agent is None:
            # Fresh context
            self.context = Context()
            self.agent = None
        elif hasattr(context_or_agent, 'context'):
            # Agent provided - has context, tools, scaffolds, MessageScheduler
            self.agent = context_or_agent
            # Trigger lazy history initialization so ContextHistory is attached
            _ = context_or_agent.history
            # Use raw context for direct property access (same as internal systems)
            self.context = context_or_agent._context
        else:
            # Context provided directly
            self.context = context_or_agent
            self.agent = None
        
        self.viewer = ContextViewer(self.context)
        self.current_turn = "user"  # Track conversation flow
        
        # Tool execution system - use agent's if available, otherwise create standalone
        if self.agent:
            # Use agent's tool registry and executor for full fidelity
            self.tool_registry = self.agent.tool_registry
            self.tool_executor = self.agent.tool_executor
            # Ensure executor has context reference for registry population
            if not self.tool_executor.context:
                self.tool_executor.context = self.context
        else:
            # Create standalone tool execution system for agent-agnostic usage
            self.tool_registry = ToolRegistry()
            self.tool_executor = ToolExecutor(registry=self.tool_registry, context=self.context)

        # Create standalone MessageScheduler for rendering only (not context building)
        from egregore.core.agent.message_scheduler import MessageScheduler
        self.message_scheduler = MessageScheduler(self.context)

    def step(self, operation_type: str, *args, **kwargs) -> None:
        """
        Execute one real operation and show results.

        Args:
            operation_type: Type of operation to execute
            *args, **kwargs: Operation-specific arguments
        """
        # Validate operation is allowed for current turn
        self._validate_turn_operation(operation_type)

        print(f"\n🔄 EXECUTING: {operation_type} {args}")

        # Execute the real operation using actual systems
        result = self._execute_operation(operation_type, *args, **kwargs)

        # Update turn state based on operation
        self._update_turn_state(operation_type)

        # Show results
        self.print()
        
        # Return result for operations that produce output
        return result

    def register_tool(self, tool_declaration) -> None:
        """
        Register a tool for standalone execution.
        
        Args:
            tool_declaration: ToolDeclaration instance
        """
        self.tool_registry.register_tool(tool_declaration)
        print(f"   🔧 Registered tool: {tool_declaration.name}")

    def register_tool_function(self, func) -> None:
        """
        Register a function as a tool for standalone execution.
        
        Args:
            func: Function to register as tool
        """
        from egregore.core.tool_calling.tool_declaration import ToolDeclaration
        tool_declaration = ToolDeclaration.from_callable(func)
        self.register_tool(tool_declaration)

    def print(self, mode: str = "tree") -> None:
        """
        Display current context state using real ContextViewer.
        
        Args:
            mode: Display mode - "tree", "text", "provider", "xml"
        """
        print(f"\n=== CONTEXT STATE (Turn: {self.current_turn}) ===")
        if mode == "tree":
            print(self.viewer.view_tree())
        elif mode == "text":
            print(self.viewer.view_text("full"))
        elif mode == "provider":
            print(self.viewer.view_text("provider"))  # Exact LLM input
        elif mode == "xml":
            print(self.viewer.view_xml())
        else:
            raise ValueError(f"Unknown mode: {mode}. Use: tree, text, provider, xml")

    def _validate_turn_operation(self, operation_type: str) -> None:
        """
        Validate that operation is allowed for current turn.
        
        Args:
            operation_type: Operation to validate
            
        Raises:
            ValueError: If operation is invalid for current turn
        """
        # User turn operations
        user_operations = {"user_message", "tool_call", "execute_tools"}
        
        # Provider turn operations  
        provider_operations = {"assistant_message"}
        
        # Operations allowed anytime (MessageScheduler render operations)
        any_time_operations = {"render", "seal", "user_message", "assistant_message", "stream", "rebuild_context"}
        
        if operation_type in any_time_operations:
            return
        
        if self.current_turn == "user" and operation_type not in user_operations:
            raise ValueError(f"Operation '{operation_type}' not allowed during user turn. "
                           f"Valid operations: {user_operations}")
        
        if self.current_turn == "provider" and operation_type not in provider_operations:
            raise ValueError(f"Operation '{operation_type}' not allowed during provider turn. "
                           f"Valid operations: {provider_operations}")

    def _execute_operation(self, operation_type: str, *args, **kwargs) -> None:
        """
        Execute the real operation using actual systems.
        
        Args:
            operation_type: Type of operation to execute
            *args, **kwargs: Operation arguments
        """
        if operation_type == "user_message":
            # Use proper Context methods for user input (no MessageScheduler needed)
            message = args[0]
            self.context.add_user(message)
            print(f"   💬 Added user message: {message[:50]}{'...' if len(message) > 50 else ''}")
            
            
        elif operation_type == "tool_call":
            # Execute tool using standalone tool execution system (agent-agnostic)
            tool_name = args[0]
            parameters = args[1] if len(args) > 1 else kwargs.get('parameters', {})
            
            # Check if tool exists in our registry
            if not self.tool_registry.tool_exists(tool_name):
                available_tools = list(self.tool_registry.tools.keys())
                raise ValueError(f"Tool '{tool_name}' not found. Available tools: {available_tools}")
            
            # Step 1: Add assistant message with tool call (this is what the LLM would output)
            from egregore.core.messaging import ProviderToolCall
            from egregore.core.tool_calling.context_components import ToolCall
            import uuid
            
            tool_call_id = f"ctx_explorer_{uuid.uuid4().hex[:8]}"
            
            # Create tool call component and add it as assistant message
            tool_call_component = ToolCall(
                tool_name=tool_name,
                tool_call_id=tool_call_id,
                parameters=parameters
            )
            
            # Add assistant message containing the tool call
            assistant_msg = f"I'll help you by calling the {tool_name} tool."
            self.context.add_assistant(assistant_msg)
            
            # Add the tool call to the assistant message container (d0,0,M)
            try:
                self.context.pact_update("d0,0", tool_call_component, mode="append")
                print(f"   🤖 Added assistant message with tool call: {tool_name}")
            except Exception as e:
                print(f"   ❌ Failed to add tool call to assistant message: {e}")
            
            # Step 2: Execute the tool using the ToolCall component
            # Pass the component so registry can track call_component_id
            result_component = self.tool_executor.execute_tool(tool_call_component)
            print(f"   🔧 Tool '{tool_name}' executed successfully")

            # Step 3: Add tool result component directly to context (not ClientToolResponse)
            # The result is already a ToolResult or ScaffoldResult component
            try:
                self.context.pact_update("d0,0", result_component, mode="append")
                print(f"   💬 Added tool result component to context")
            except Exception as e:
                print(f"   ❌ Failed to add tool result: {e}")
                
            # Update turn to provider since we just added a user message
            self.current_turn = "user"
            
        elif operation_type == "assistant_message":
            # Use proper Context methods for assistant input  
            message = args[0]
            self.context.add_assistant(message)
            print(f"   🤖 Added assistant message: {message[:50]}{'...' if len(message) > 50 else ''}")
            
                
        elif operation_type == "render":
            # Use MessageScheduler.render() with BFS + coordinate sorting
            provider_thread = self.message_scheduler.render()
            print(f"   🎨 Context rendered to ProviderThread with {len(provider_thread.messages)} messages")
            
            # Display the actual JSON structure that would be sent to provider
            import json
            
            # Just use the standard ProviderThread serialization
            json_structure = provider_thread.model_dump()
            
            print(f"   📡 Provider JSON Structure:")
            print(json.dumps(json_structure, indent=2))
            
            return provider_thread
                
        elif operation_type == "seal":
            # Seal operation: snapshot context state at cycle boundary
            # Two phases:
            # 1. Before provider call: seal(trigger="before_provider_call")
            # 2. After provider response: add_response() then seal(trigger="after_provider_response")
            provider_response = args[0] if args else kwargs.get('provider_response', None)

            if provider_response:
                # Phase 2: Process provider response then seal
                self.message_scheduler.add_response(provider_response)
                print(f"   📥 Added provider response with {len(provider_response.content)} content blocks")
                trigger = "after_provider_response"
            else:
                # Phase 1: Seal without response (before provider call)
                trigger = "before_provider_call"

            self.context.seal(trigger)
            print(f"   🔒 Context sealed ({trigger})")

        elif operation_type == "stream":
            # Streaming simulation: auto-chunk response and process
            provider_response = args[0] if args else kwargs.get('response', None)

            if not provider_response:
                raise ValueError("stream operation requires a ProviderResponse")

            print(f"🌊 STREAMING: Auto-chunking {len(provider_response.content)} content blocks")

            # Use StreamingSimulator to process
            with self.stream() as stream:
                # Auto-chunk the response
                for content_block in provider_response.content:
                    # Handle text content
                    if hasattr(content_block, 'content') and isinstance(content_block.content, str):
                        # Chunk text into small pieces for realistic streaming
                        text = content_block.content
                        chunk_size = 20  # Characters per chunk
                        for i in range(0, len(text), chunk_size):
                            stream.chunk(text_delta=text[i:i+chunk_size])

                    # Handle tool calls
                    elif hasattr(content_block, 'tool_name'):
                        import json
                        stream.chunk(
                            tool_start=content_block.tool_name,
                            tool_call_id=content_block.tool_call_id
                        )
                        # Chunk arguments JSON
                        args_json = json.dumps(content_block.parameters)
                        chunk_size = 30
                        for i in range(0, len(args_json), chunk_size):
                            stream.chunk(tool_arguments=args_json[i:i+chunk_size])

                # stream.complete() called automatically by context manager

        elif operation_type == "execute_tools":
            # Extract ToolCall components from context and execute them
            # This exposes what Agent.orchestrate_turn() does internally:
            # 1. Extract ToolCall components from context
            # 2. Start new user turn (pushes assistant message to depth 1)
            # 3. Execute tools and add ToolResults to new user message at depth 0

            print(f"🔧 EXECUTING TOOLS: Simulating Agent's orchestrate_turn behavior")

            # This simulates what task_loop_ops.py does
            if self.agent:
                # Use agent's task loop orchestration (the real implementation)
                from egregore.core.messaging import ProviderResponse
                dummy_response = ProviderResponse(content=[])
                result = self.agent._task_loop_ops.orchestrate_turn(dummy_response)
                print(f"   ✅ Agent orchestrated tool execution")
                return result
            else:
                # Standalone mode - manually do what the agent does
                executor = self.tool_executor

                # Extract ToolCall components (only from depth 0 - active turn)
                tool_call_components = self.context.select("(d0) +tool_call")

                if not tool_call_components:
                    print(f"   ⚠️  No ToolCall components found in context")
                    return

                print(f"   Found {len(tool_call_components)} ToolCall components")

                # Start new user turn for tool results
                self.context.add_user("Tool execution results")
                print(f"   🔄 Started new user turn for tool results")

                # Execute and add results
                for tool_call_comp in tool_call_components:
                    tool_name = tool_call_comp.tool_name
                    tool_call_id = tool_call_comp.tool_call_id

                    print(f"   🔧 Executing tool: {tool_name} (call_id: {tool_call_id})")

                    result_component = executor.execute_tool(tool_call_comp)

                    try:
                        self.context.active_message.add_child(result_component)
                        print(f"   ✅ Added ToolResult component for {tool_name}")
                    except Exception as e:
                        print(f"   ❌ Failed to add ToolResult: {e}")

        else:
            raise ValueError(f"Unknown operation '{operation_type}'. Use: user_message, assistant_message, tool_call, execute_tools, render, seal, stream")

    def _update_turn_state(self, operation_type: str) -> None:
        """
        Update turn state based on operation.
        
        Args:
            operation_type: Operation that was executed
        """
        # User message starts/continues user turn
        if operation_type == "user_message":
            self.current_turn = "user"
        
        # Tool calls happen during user turn, so no change needed
        elif operation_type == "tool_call":
            # Stay in user turn - tools execute during user turn
            pass

        # Execute tools - extract ToolCall components from context and execute them
        elif operation_type == "execute_tools":
            # Stay in user turn - tool execution happens during user turn
            pass
            
        # Assistant message starts provider turn
        elif operation_type == "assistant_message":
            self.current_turn = "provider"

    @contextmanager
    def stream(self):
        """
        Context manager for manual streaming simulation.

        Usage:
            with explorer.stream() as stream:
                stream.chunk(text_delta="Hello")
                stream.chunk(tool_start="tool_name", tool_call_id="id")
                stream.chunk(tool_arguments='{"param": "value"}')
                stream.complete()

        Yields:
            StreamingSimulator instance for chunk-by-chunk control
        """
        simulator = StreamingSimulator(self)
        try:
            yield simulator
        finally:
            # Auto-finalize if not already done
            if not simulator.finalized:
                simulator.complete()


class StreamingSimulator:
    """
    Handles manual streaming chunk simulation for ContextExplorer.

    Accumulates chunks and processes them through the real StreamingOrchestrator
    to ensure we're testing actual production streaming behavior.
    """

    def __init__(self, explorer: ContextExplorer):
        """
        Initialize streaming simulator.

        Args:
            explorer: ContextExplorer instance
        """
        self.explorer = explorer
        self.finalized = False

        # Accumulate chunks
        self.text_chunks = []
        self.tool_calls = []  # List of {tool_call_id, tool_name, arguments_chunks}
        self.current_tool = None  # Currently accumulating tool call

        print("🌊 STREAMING START")

    def chunk(self, text_delta: Optional[str] = None,
             tool_start: Optional[str] = None,
             tool_call_id: Optional[str] = None,
             tool_arguments: Optional[str] = None):
        """
        Process a streaming chunk.

        Args:
            text_delta: Text content delta
            tool_start: Start a new tool call with this tool name
            tool_call_id: Tool call ID for tool_start
            tool_arguments: Tool arguments delta (JSON string fragment)
        """
        if self.finalized:
            raise RuntimeError("Cannot add chunks after stream is finalized")

        # Handle text delta
        if text_delta is not None:
            self.text_chunks.append(text_delta)
            print(f"   🌊 text_delta: {repr(text_delta[:50])}")

        # Handle tool call start
        if tool_start is not None:
            # Finalize previous tool if any
            if self.current_tool is not None:
                self.tool_calls.append(self.current_tool)

            # Start new tool
            self.current_tool = {
                'tool_name': tool_start,
                'tool_call_id': tool_call_id or f"stream_{len(self.tool_calls)}",
                'arguments_chunks': []
            }
            print(f"   🌊 tool_start: {tool_start} (id: {self.current_tool['tool_call_id']})")

        # Handle tool arguments delta
        if tool_arguments is not None:
            if self.current_tool is None:
                raise RuntimeError("tool_arguments chunk without tool_start")

            self.current_tool['arguments_chunks'].append(tool_arguments)
            print(f"   🌊 tool_arguments: {repr(tool_arguments[:50])}")

    def complete(self):
        """
        Finalize streaming and process accumulated chunks.

        Creates ProviderResponse from accumulated chunks and processes
        through MessageScheduler.seal() (same as non-streaming path).
        """
        if self.finalized:
            return

        self.finalized = True

        # Finalize current tool if any
        if self.current_tool is not None:
            self.tool_calls.append(self.current_tool)
            self.current_tool = None

        print("   ✅ STREAM COMPLETE")

        # Build ProviderResponse from accumulated chunks
        from egregore.core.messaging import ProviderResponse, ProviderToolCall, TextContent

        content_blocks = []

        # Add text content if any
        if self.text_chunks:
            full_text = "".join(self.text_chunks)
            content_blocks.append(TextContent(content=full_text))

        # Add tool calls
        for tool_data in self.tool_calls:
            # Reconstruct parameters from JSON chunks
            full_arguments = "".join(tool_data['arguments_chunks'])
            try:
                import json
                parameters = json.loads(full_arguments) if full_arguments else {}
            except json.JSONDecodeError:
                print(f"   ⚠️  Warning: Invalid JSON for tool arguments: {full_arguments}")
                parameters = {}

            tool_call = ProviderToolCall(
                tool_name=tool_data['tool_name'],
                tool_call_id=tool_data['tool_call_id'],
                parameters=parameters
            )
            content_blocks.append(tool_call)

        # Create ProviderResponse
        if content_blocks:
            provider_response = ProviderResponse(content=content_blocks)

            # Process through MessageScheduler.seal() (real streaming path)
            self.explorer.message_scheduler.add_response(provider_response)
            self.explorer.context.seal("after_provider_response")

            print(f"   📥 Processed {len(content_blocks)} content blocks through MessageScheduler")