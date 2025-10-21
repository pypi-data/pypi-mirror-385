"""
Token counting operations for Agent class.

This module contains all token counting, storage, and extraction operations
that were previously part of the main Agent class to improve maintainability
and organization.

Key Features:
- Asynchronous token counting with TokenCountingManager
- Token storage in agent state for snapshot capture
- Token extraction from context components and history
- Usage summary aggregation across conversation turns
- Pending token integration with response components

Architecture:
- TokenOperations class with agent reference pattern
- Lazy initialization of TokenCountingManager
- Integration with V2 provider interface and context system
"""

import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class TokenOperations:
    """Token counting operations for agents."""
    
    def __init__(self, agent):
        """
        Initialize with reference to parent agent.
        
        Args:
            agent: Agent instance for accessing provider, state, context, etc.
        """
        self.agent = agent
        self._token_counter = None
    
    async def count_input_tokens_async(self, provider_thread):
        """Count input tokens asynchronously after response is returned"""
        try:
            if not self._token_counter:
                from egregore.providers.core.token_counting import TokenCountingManager
                self._token_counter = TokenCountingManager()
            
            tokens = self._token_counter.count_tokens(
                provider_thread, 
                self.agent.provider.model or 'gpt-4', 
                self.agent.provider.name
            )
            
            # Store in latest message component metadata
            # Will be captured in next context snapshot
            self.store_input_tokens_in_context(tokens)
            
        except Exception as e:
            logger.debug(f"Async input token counting failed: {e}")
    
    def store_input_tokens_in_context(self, tokens: int):
        """Store input tokens in context for snapshot capture"""
        try:
            # Store in agent state store for later retrieval during context operations
            if 'pending_input_tokens' not in self.agent.state.store:
                self.agent.state.store['pending_input_tokens'] = {}
            self.agent.state.store['pending_input_tokens'][self.agent.state.current_turn] = tokens
            logger.debug(f"Stored {tokens} input tokens for turn {self.agent.state.current_turn}")
        except Exception as e:
            logger.debug(f"Failed to store input tokens in context: {e}")

    def add_input_tokens_to_response_component(self, response, input_tokens: int):
        """Add input tokens to response component metadata"""
        try:
            # Access the active message component to find the provider response
            active_message = self.agent.context.active_message
            if active_message and hasattr(active_message, 'content'):
                # Find the most recent provider message component
                for component in reversed(active_message.content):
                    component_type = getattr(component, 'type', None)
                    if component_type and 'provider' in str(component_type).lower():
                        # Add input tokens to component metadata
                        if hasattr(component, 'metadata') and component.metadata:
                            component.metadata.set_input_tokens(input_tokens)
                            logger.debug(f"Added {input_tokens} input tokens to component {component_type}")
                            break
        except Exception as e:
            logger.debug(f"Failed to add input tokens to response component: {e}")
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get token usage summary from context history"""
        if not hasattr(self.agent, 'history') or not self.agent.history or not hasattr(self.agent.history, 'snapshots'):
            return {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
        
        if not self.agent.history.snapshots:
            return {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0}
        
        total_input = 0
        total_output = 0
        
        # Aggregate from snapshots
        for snapshot in self.agent.history.snapshots:
            if hasattr(snapshot, 'full_context') and snapshot.full_context:
                # Extract tokens from context components
                input_tokens, output_tokens = self.extract_tokens_from_context(snapshot.full_context)
                total_input += input_tokens
                total_output += output_tokens
        
        return {
            'input_tokens': total_input,
            'output_tokens': total_output,
            'total_tokens': total_input + total_output
        }
    
    def extract_tokens_from_context(self, context) -> Tuple[int, int]:
        """Extract input and output tokens from context components"""
        input_tokens = 0
        output_tokens = 0
        
        try:
            # Get all components from context
            if hasattr(context, 'get_all_components'):
                components = context.get_all_components()
            elif hasattr(context, 'root') and hasattr(context.root, 'get_all_children_recursive'):
                components = [context.root] + context.root.get_all_children_recursive()
            else:
                components = []
            
            for component in components:
                # Extract input tokens from component metadata
                if hasattr(component, 'metadata') and component.metadata:
                    input_count = component.metadata.get_input_tokens()
                    if input_count:
                        input_tokens += input_count
                
                # Extract output tokens from BaseMessage token_count if it's a message component
                if hasattr(component, 'token_count') and component.token_count:
                    output_tokens += component.token_count
                
        except Exception as e:
            logger.debug(f"Failed to extract tokens from context: {e}")
        
        return input_tokens, output_tokens
    
    def integrate_pending_input_tokens(self, response):
        """Integrate pending input tokens into context components"""
        try:
            # Integrate pending input tokens into context components
            if hasattr(self.agent.state, 'store') and 'pending_input_tokens' in self.agent.state.store:
                current_turn_tokens = self.agent.state.store['pending_input_tokens'].get(self.agent.state.current_turn)
                if current_turn_tokens:
                    # Find the response component and add input tokens
                    self.add_input_tokens_to_response_component(response, current_turn_tokens)
                    # Clean up processed tokens from pending state
                    del self.agent.state.store['pending_input_tokens'][self.agent.state.current_turn]
                    logger.debug(f"Successfully integrated {current_turn_tokens} input tokens for turn {self.agent.state.current_turn}")
        except Exception as e:
            logger.debug(f"Failed to integrate pending input tokens: {e}")