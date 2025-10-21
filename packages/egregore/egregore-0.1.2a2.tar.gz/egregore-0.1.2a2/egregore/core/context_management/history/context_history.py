"""
ContextHistory - Immutable historical record of Context evolution

ContextHistory provides immutable snapshots of Context state taken before provider calls,
with asynchronous execution to minimize latency. It serves as the historical record for
debugging, analysis, and rollback capabilities.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import os
import time
import json
import pickle
import logging
from pathlib import Path
from queue import Queue, Empty
from threading import Thread, Lock

from platformdirs import user_data_dir

from .context_snapshot import ContextSnapshot, create_full_snapshot
from .loaders import LocalSnapshotLoader, SnapshotLoaderEngine
from .errors import (
    ContextHistoryError, SnapshotNotFoundError, CorruptedSnapshotError, AgentMismatchError, 
    InvalidSnapshotFormatError, SnapshotProcessingError, PersistenceError
)
from ..pact.context import Context
from ...tool_calling.tool_execution_group import ToolExecutionGroup


# Cross-platform snapshots directory
# Linux/macOS: ~/.local/share/egregore/snapshots  
# Windows: %USERPROFILE%\AppData\Local\egregore\snapshots
SNAPSHOTS_BASE_DIR = os.path.join(user_data_dir("egregore"), "snapshots")

# Configure logger for ContextHistory
logger = logging.getLogger(__name__)


class ContextHistory:
    """Immutable historical record of Context evolution"""
    
    def __init__(self, folder: str = "default", max_retries: int = 3, enable_logging: bool = True,
                 agent_id: Optional[str] = None, loader: Optional["SnapshotLoaderEngine"] = None, agent=None):
        """Initialize ContextHistory with agent-level snapshot storage

        Args:
            folder: Folder name for this agent's snapshots (for session isolation)
            max_retries: Maximum retries for failed operations
            enable_logging: Whether to enable detailed logging
            agent_id: Unique identifier for the agent (for session tracking)
            loader: Snapshot loader engine (defaults to LocalSnapshotLoader with default settings)
            agent: Reference to the agent (for context replacement)
        """
        # Configuration
        self.folder_name = folder
        self.max_retries = max_retries
        self.enable_logging = enable_logging
        self.agent_id = agent_id
        self.agent = agent

        # Initialize smart loader engine (defaults to local file loading)
        if loader is None:
            from .loader_settings import LocalLoaderSettings
            from .loaders import LocalSnapshotLoader

            # Create default LocalSnapshotLoader with settings
            snapshot_folder = Path(SNAPSHOTS_BASE_DIR) / folder
            settings = LocalLoaderSettings(
                base_dir=snapshot_folder,
                agent_id=agent_id,
                format="json",
                compress=False,
                include_full_tree=True,
                include_metadata=True,
                enable_logging=enable_logging
            )
            self.loader = LocalSnapshotLoader(settings=settings)
        else:
            self.loader = loader
            
        # Agent-level snapshot storage configuration - cross-platform
        self.snapshot_folder = os.path.join(SNAPSHOTS_BASE_DIR, folder)
        
        # Ensure directory exists with error handling
        try:
            os.makedirs(self.snapshot_folder, exist_ok=True)
        except (OSError, PermissionError) as e:
            if self.enable_logging:
                logger.error(f"Failed to create snapshot folder {self.snapshot_folder}: {e}")
            raise ContextHistoryError(f"Cannot create snapshot directory: {e}")
        
        # Core storage with thread safety
        self._storage_lock = Lock()
        self.snapshots: List[ContextSnapshot] = []
        self._snapshots_by_id: Dict[str, ContextSnapshot] = {}
        
        # ToolExecutionGroup tracking
        self.execution_groups: Dict[str, ToolExecutionGroup] = {}  # group_id -> group
        self.groups_by_snapshot: Dict[str, List[str]] = {}  # snapshot_id -> [group_ids]
        self.groups_by_turn: Dict[str, List[str]] = {}  # turn_id -> [group_ids]
        
        # Async snapshot processing with error tracking
        self._pending_snapshots: Queue = Queue()
        self._snapshot_processor: Optional[Thread] = None
        self._processing_enabled: bool = True
        self._failed_snapshots: List[Dict[str, Any]] = []  # Track failed snapshot attempts
        self._total_processed: int = 0
        self._total_failed: int = 0
    
    def __getitem__(self, index: int) -> ContextSnapshot:
        """Access snapshots with history[3] syntax using intelligent delegation"""
        # Try loader first
        try:
            if not self.agent_id:
                raise ContextHistoryError("agent_id is required but not set")
            agent_id = self.agent_id
            loader_snapshots = self.loader.list_snapshots(agent_id)
            if loader_snapshots:
                return loader_snapshots[index]
        except ContextHistoryError:
            # Don't catch ContextHistoryError - let it bubble up as a configuration error
            raise
        except Exception as e:
            if self.enable_logging:
                logger.debug(f"Loader getitem failed, falling back to local: {e}")
        
        # Fallback to local storage
        return self.snapshots[index]
    
    def __len__(self) -> int:
        """Number of snapshots using intelligent delegation"""
        # Try loader first  
        try:
            agent_id = self.agent_id or "default"
            loader_snapshots = self.loader.list_snapshots(agent_id)
            if loader_snapshots:
                return len(loader_snapshots)
        except ContextHistoryError:
            # Don't catch ContextHistoryError - let it bubble up as a configuration error
            raise
        except Exception as e:
            if self.enable_logging:
                logger.debug(f"Loader len failed, falling back to local: {e}")
        
        # Fallback to local storage
        return len(self.snapshots)
    
    def get_snapshot_by_id(self, snapshot_id: str) -> Optional[ContextSnapshot]:
        """Get snapshot by ID"""
        return self._snapshots_by_id.get(snapshot_id)
    
    def _add_snapshot_directly(self, snapshot: ContextSnapshot) -> None:
        """Add a snapshot directly to storage (bypassing async processing)"""
        with self._storage_lock:
            # Add to local storage
            self.snapshots.append(snapshot)
            self._snapshots_by_id[snapshot.id] = snapshot
            
        # Try to add to persistent storage, but don't fail if it doesn't work
        try:
            self.loader.add_snapshot(snapshot)
            if self.enable_logging:
                logger.debug(f"Added snapshot {snapshot.id} to loader engine")
        except Exception as loader_error:
            if self.enable_logging:
                logger.warning(f"Failed to add snapshot {snapshot.id} to loader: {loader_error}")
        
        # Try to auto-save, but don't fail if it doesn't work
        try:
            self.save(include_full_context=True)
            if self.enable_logging:
                logger.debug(f"Auto-saved snapshot {snapshot.id} to disk")
        except Exception as save_error:
            if self.enable_logging:
                logger.warning(f"Failed to auto-save snapshot {snapshot.id}: {save_error}")
    
    async def create_diff(self, snapshot1: ContextSnapshot, context_or_snapshot2) -> 'PACTDiffResult':
        """Create diff between a snapshot and current context or another snapshot"""
        import asyncio
        from .context_snapshot import diff_snapshots, create_full_snapshot
        import time
        
        async def _create_diff_task():
            # If second argument is a Context, create a temporary snapshot
            if hasattr(context_or_snapshot2, 'to_pact'):  # It's a Context
                temp_snapshot_id = f"temp_diff_{int(time.time() * 1000000)}"
                snapshot2 = create_full_snapshot(
                    context=context_or_snapshot2,
                    snapshot_id=temp_snapshot_id,
                    trigger="temp_diff"
                )
            else:
                # It's already a snapshot
                snapshot2 = context_or_snapshot2
            
            return diff_snapshots(snapshot1, snapshot2)
        
        # Run in separate task
        return await _create_diff_task()
    
    def create_snapshot(self, context: Context, trigger: str, **metadata) -> str:
        """Create snapshot asynchronously (non-blocking) and return snapshot_id immediately
        
        Args:
            context: Context to snapshot
            trigger: What triggered this snapshot (e.g., 'before_provider_call')
            **metadata: Additional metadata (turn_id, provider_name, etc.)
            
        Returns:
            snapshot_id: Unique identifier for the snapshot
            
        Raises:
            ContextHistoryError: If context is invalid or processing is disabled
        """
        # Input validation
        if context is None:
            raise ContextHistoryError("Cannot create snapshot from None context")
        
        if not isinstance(context, Context):
            raise ContextHistoryError(f"Expected Context object, got {type(context)}")
        
        if not trigger or not isinstance(trigger, str):
            raise ContextHistoryError("Trigger must be a non-empty string")
        
        if not self._processing_enabled:
            if self.enable_logging:
                logger.warning("Snapshot processing is disabled, snapshot will not be created")
            # Still return a valid ID for consistency, but don't queue
            return f"disabled_snapshot_{int(time.time())}"
        
        try:
            with self._storage_lock:
                snapshot_id = f"snapshot_{len(self.snapshots)}_{int(time.time())}"

            # Inject scaffold states before capturing context (automatic persistence)
            # Update scaffolds in agent._scaffold_list (they're not statically mounted in the tree)
            logger.info(f"[SCAFFOLD STATE] Starting state injection")
            if self.agent and hasattr(self.agent, '_scaffold_list'):
                try:
                    scaffolds = self.agent._scaffold_list
                    logger.info(f"[SCAFFOLD STATE] Injecting state for {len(scaffolds)} scaffolds from agent._scaffold_list")

                    for scaffold in scaffolds:
                        if hasattr(scaffold, '_update_scaffold_state_field'):
                            try:
                                scaffold._update_scaffold_state_field()
                                scaffold_id = getattr(scaffold, 'id', 'unknown')
                                logger.info(f"[SCAFFOLD STATE] Injected state for scaffold {scaffold_id}, object_id={id(scaffold)}")

                                # Verify it worked (state is now in metadata.aux)
                                if 'scaffold_state' not in scaffold.metadata.aux:
                                    logger.warning(f"[SCAFFOLD STATE] scaffold_state not in metadata.aux for {scaffold_id}")
                                if 'scaffold_id_data' not in scaffold.metadata.aux:
                                    logger.warning(f"[SCAFFOLD STATE] scaffold_id_data not in metadata.aux for {scaffold_id}")

                                # DEBUG: Find the scaffold in the context tree and inject state there too
                                if hasattr(self.agent, 'context'):
                                    try:
                                        # Traverse depth -1 to find all scaffolds
                                        for component in self.agent.context.traverse_branch(-1):
                                            if getattr(component, 'id', None) == scaffold_id:
                                                logger.info(f"[SCAFFOLD STATE] Found scaffold in tree: id={scaffold_id}, list_obj={id(scaffold)}, tree_obj={id(component)}")

                                                if id(component) != id(scaffold):
                                                    logger.warning(f"[SCAFFOLD STATE] ⚠️ DIFFERENT OBJECTS - injecting state into tree object")
                                                    # Inject state into the tree object too
                                                    if hasattr(component, '_update_scaffold_state_field'):
                                                        component.state = scaffold.state  # Copy state
                                                        component._update_scaffold_state_field()
                                                        logger.info(f"[SCAFFOLD STATE] Copied state to tree object")
                                                else:
                                                    logger.info(f"[SCAFFOLD STATE] ✅ Same object in list and tree")
                                                break
                                    except Exception as e:
                                        logger.warning(f"[SCAFFOLD STATE] Could not check/update tree object: {e}", exc_info=True)
                            except Exception as e:
                                logger.error(f"[SCAFFOLD STATE] Failed to inject state for scaffold: {e}", exc_info=True)
                except Exception as e:
                    logger.error(f"[SCAFFOLD STATE] Error during scaffold state injection: {e}", exc_info=True)
            else:
                logger.warning(f"[SCAFFOLD STATE] No agent or no scaffolds for state injection")

            # Capture context state with error handling
            try:
                context_state = self._capture_context_state(context)
            except Exception as e:
                if self.enable_logging:
                    logger.error(f"Failed to capture context state for snapshot {snapshot_id}: {e}")
                raise SnapshotProcessingError(f"Context capture failed: {e}")
            
            # Queue snapshot creation for async processing
            snapshot_task = {
                'snapshot_id': snapshot_id,
                'context_state': context_state,
                'trigger': trigger,
                'timestamp': datetime.now(),
                'metadata': metadata,
                'retry_count': 0
            }
            
            self._pending_snapshots.put(snapshot_task)
            
            # Start processor if not running
            if self._snapshot_processor is None or not self._snapshot_processor.is_alive():
                self._start_snapshot_processor()
            
            if self.enable_logging:
                logger.debug(f"Queued snapshot {snapshot_id} for processing")
            
            # Return ID immediately - snapshot will be available shortly
            return snapshot_id
            
        except Exception as e:
            if self.enable_logging:
                logger.error(f"Failed to queue snapshot: {e}")
            raise SnapshotProcessingError(f"Snapshot queuing failed: {e}")
    
    def _capture_context_state(self, context: Context) -> Dict[str, Any]:
        """Capture PACT tree data as JSON-serializable snapshot"""
        try:
            # Store agent identifiers
            original_agent = getattr(context, 'agent', None)
            agent_id = getattr(original_agent, 'agent_id', None) if original_agent else None
            agent_name = getattr(original_agent, 'name', None) or (original_agent.__class__.__name__ if original_agent else None)

            # CRITICAL: Capture PACT tree IMMEDIATELY, not later!
            # If we store the context reference, all snapshots will point to the same (changing) context
            pact_tree = context.to_pact()  # Create independent copy NOW

            # Extract JSON-serializable PACT tree structure
            context_data = {
                'cadence': getattr(context, 'cadence', 0),
                'components': self._serialize_components(context),
                'system_header': self._serialize_message(context.system_header) if hasattr(context, 'system_header') and context.system_header else None,
                'conversation_history': self._serialize_conversation_history(context) if hasattr(context, 'conversation_history') else None,
                'active_message': self._serialize_message(context.active_message) if hasattr(context, 'active_message') and context.active_message else None,
            }

            return {
                'context': None,  # Don't store context reference - it's mutable!
                'pact_tree': pact_tree,  # Store immutable PACT tree captured at this moment
                'context_data': context_data,  # Keep serialized data for fallback/debugging
                'agent_id': agent_id,
                'agent_name': agent_name,
                'system_header': context_data['system_header'],
                'conversation_history': context_data['conversation_history'],
                'active_message': context_data['active_message'],
                'message_cycle': context_data['cadence'],
                'component_count': len(context_data['components']) if context_data['components'] else 0
            }
                    
        except Exception as e:
            # Fallback to minimal state
            return {
                'context': None,
                'agent_id': None,
                'agent_name': None,
                'system_header': None,
                'conversation_history': None, 
                'active_message': None,
                'message_cycle': 0,
                'component_count': 0,
                'error': f"Context capture failed: {str(e)}"
            }
    
    def _serialize_components(self, context: Context) -> List[Dict[str, Any]]:
        """Serialize context components to JSON-serializable format"""
        try:
            components = []
            # Context has system_header, conversation_history, and active_message
            context_components = [
                context.system_header,
                context.conversation_history, 
                context.active_message
            ]
            
            for component in context_components:
                if component:
                    comp_data = {
                        'type': component.__class__.__name__,
                        'id': getattr(component, 'id', None),
                    }
                    # Add content if it's JSON-serializable
                    if hasattr(component, 'content'):
                        try:
                            import json
                            json.dumps(component.content)  # Test if serializable
                            comp_data['content'] = component.content
                        except:
                            comp_data['content'] = str(component.content) if component.content else None
                    
                    components.append(comp_data)
            return components
        except Exception:
            return []
    
    def _serialize_message(self, message) -> Optional[Dict[str, Any]]:
        """Serialize a message object to JSON format"""
        try:
            if not message:
                return None
            return {
                'type': message.__class__.__name__,
                'content': str(message) if hasattr(message, '__str__') else None,
            }
        except Exception:
            return None
    
    def _serialize_conversation_history(self, context: Context) -> List[Dict[str, Any]]:
        """Serialize conversation history to JSON format"""
        try:
            history = []
            if hasattr(context, 'conversation_history') and context.conversation_history:
                for item in context.conversation_history:
                    if item:
                        history.append(self._serialize_message(item))
            return history
        except Exception:
            return []
    
    def _is_pickleable(self, obj) -> bool:
        """Check if an object is pickleable"""
        try:
            import pickle
            pickle.dumps(obj)
            return True
        except Exception:
            return False
    
    def _count_components(self, context: Context) -> int:
        """Count total components in context tree"""
        try:
            return context.get_message_count() if hasattr(context, 'get_message_count') else 0
        except Exception:
            return 0
    
    def _start_snapshot_processor(self):
        """Start background thread for snapshot processing"""
        self._snapshot_processor = Thread(
            target=self._process_snapshots_background,
            daemon=True,
            name="ContextHistory-SnapshotProcessor"
        )
        self._snapshot_processor.start()
    
    def _process_snapshots_background(self):
        """Background processing of snapshot creation with retry logic"""
        if self.enable_logging:
            logger.info("Starting snapshot background processor")
        
        while self._processing_enabled:
            try:
                # Get next snapshot task (blocks until available)
                task = self._pending_snapshots.get(timeout=1.0)
                
                try:
                    # Process the snapshot task
                    self._process_single_snapshot(task)
                    self._total_processed += 1
                    
                    if self.enable_logging:
                        logger.debug(f"Successfully processed snapshot {task['snapshot_id']}")
                
                except Exception as e:
                    # Handle failed snapshot processing with retry logic
                    self._handle_snapshot_failure(task, e)
                
                finally:
                    # Always mark task as done to prevent blocking
                    self._pending_snapshots.task_done()
                
            except Empty:
                # No snapshots to process, continue
                continue
            except Exception as e:
                # Unexpected error in main loop
                if self.enable_logging:
                    logger.error(f"Unexpected error in snapshot processor: {e}")
                # Don't crash the processor
                continue
        
        if self.enable_logging:
            logger.info(f"Snapshot processor stopped. Processed: {self._total_processed}, Failed: {self._total_failed}")
    
    def _process_single_snapshot(self, task: Dict[str, Any]) -> None:
        """Process a single snapshot task

        Args:
            task: Snapshot task dictionary

        Raises:
            Exception: If snapshot processing fails
        """
        # Create snapshot from pre-captured PACT tree
        from .context_snapshot import ContextSnapshot

        if not self.agent_id:
            raise SnapshotProcessingError("agent_id is required but not set")

        # Use pre-captured pact_tree from context_state
        pact_tree = task['context_state'].get('pact_tree')

        snapshot = ContextSnapshot(
            id=task['snapshot_id'],
            agent_id=self.agent_id,
            timestamp=task['timestamp'],
            message_cycle=task['context_state'].get('message_cycle', 0),
            trigger=task['trigger'],
            turn_id=task['metadata'].get('turn_id', f"turn_{task['context_state'].get('message_cycle', 0)}"),
            pact_tree=pact_tree,  # Use pre-captured tree, not current context state!
            previous_snapshot_id=None,
            provider_name=task['metadata'].get('provider_name'),
            context_size_bytes=task['context_state'].get('context_size_bytes', 0),
            component_count=task['context_state'].get('component_count', 0),
            is_full_snapshot=True
        )

        # Dual storage: Add to both local storage and loader engine
        try:
            with self._storage_lock:
                # Add to local storage
                self.snapshots.append(snapshot)
                self._snapshots_by_id[snapshot.id] = snapshot
                
            # Add to loader engine for persistent storage
            try:
                self.loader.add_snapshot(snapshot)
                if self.enable_logging:
                    logger.debug(f"Added snapshot {snapshot.id} to loader engine")
            except Exception as loader_error:
                # Don't fail the snapshot if loader fails, just log it
                if self.enable_logging:
                    logger.warning(f"Failed to add snapshot {snapshot.id} to loader: {loader_error}")
                
            # Auto-save to disk after each snapshot (PACT spec: seal on each cycle)
            try:
                self.save(include_full_context=True)
                if self.enable_logging:
                    logger.debug(f"Auto-saved snapshot {snapshot.id} to disk")
            except Exception as save_error:
                # Don't fail the snapshot if saving fails, just log it
                if self.enable_logging:
                    logger.warning(f"Failed to auto-save snapshot {snapshot.id}: {save_error}")
                    
        except Exception as e:
            raise SnapshotProcessingError(f"Failed to store snapshot: {e}")
    
    def _handle_snapshot_failure(self, task: Dict[str, Any], error: Exception) -> None:
        """Handle failed snapshot processing with retry logic
        
        Args:
            task: Failed snapshot task
            error: Exception that caused the failure
        """
        task['retry_count'] = task.get('retry_count', 0) + 1
        
        if task['retry_count'] <= self.max_retries:
            # Retry the task
            if self.enable_logging:
                logger.warning(f"Retrying snapshot {task['snapshot_id']} (attempt {task['retry_count']}/{self.max_retries}): {error}")
            
            # Add back to queue for retry
            self._pending_snapshots.put(task)
        else:
            # Max retries exceeded, record failure
            self._total_failed += 1
            
            failure_record = {
                'snapshot_id': task['snapshot_id'],
                'trigger': task['trigger'],
                'error': str(error),
                'timestamp': task['timestamp'],
                'retry_count': task['retry_count'],
                'final_error_time': datetime.now()
            }
            
            self._failed_snapshots.append(failure_record)
            
            if self.enable_logging:
                logger.error(f"Snapshot {task['snapshot_id']} failed permanently after {task['retry_count']} retries: {error}")
            
            # Optionally, create a placeholder snapshot to maintain ID consistency
            try:
                self._create_failure_placeholder(task, error)
            except Exception as placeholder_error:
                if self.enable_logging:
                    logger.error(f"Failed to create failure placeholder for {task['snapshot_id']}: {placeholder_error}")
    
    def _create_failure_placeholder(self, task: Dict[str, Any], error: Exception) -> None:
        """Create a placeholder snapshot for failed processing
        
        Args:
            task: Failed snapshot task
            error: Exception that caused the failure
        """
        from .context_snapshot import ContextSnapshot
        
        if not self.agent_id:
            raise SnapshotProcessingError("agent_id is required but not set")
        
        placeholder = ContextSnapshot(
            id=task['snapshot_id'],
            agent_id=self.agent_id,
            timestamp=task['timestamp'],
            message_cycle=0,
            trigger=f"FAILED_{task['trigger']}",
            turn_id=task['metadata'].get('turn_id', 'unknown'),
            full_context=None,
            diff_from_previous=None,
            previous_snapshot_id=None,
            provider_name=task['metadata'].get('provider_name'),
            context_size_bytes=0,
            component_count=0
        )
        
        with self._storage_lock:
            self.snapshots.append(placeholder)
            self._snapshots_by_id[placeholder.id] = placeholder
    
    def wait_for_snapshots(self, timeout: Optional[float] = None):
        """Wait for all pending snapshots to be processed
        
        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)
        """
        try:
            if timeout:
                self._pending_snapshots.join()  # Wait for all tasks to complete
            else:
                self._pending_snapshots.join()
        except Exception:
            pass
    
    def stop_processing(self):
        """Stop background snapshot processing"""
        self._processing_enabled = False

        if self._snapshot_processor and self._snapshot_processor.is_alive():
            self._snapshot_processor.join(timeout=2.0)

    def flush(self, timeout: float = 5.0) -> None:
        """
        Wait for all pending snapshots to be written to storage.

        This blocks until the snapshot queue is empty or timeout is reached.

        Args:
            timeout: Maximum seconds to wait for pending snapshots

        Raises:
            TimeoutError: If pending snapshots don't complete within timeout
        """
        import time

        if not self._processing_enabled:
            return  # Nothing to flush if processing is disabled

        start_time = time.time()
        while not self._pending_snapshots.empty():
            if time.time() - start_time > timeout:
                pending_count = self._pending_snapshots.qsize()
                raise TimeoutError(f"Flush timeout: {pending_count} snapshots still pending after {timeout}s")

            time.sleep(0.1)  # Small sleep to avoid busy-waiting

        # Wait for any in-progress snapshot to complete
        self._pending_snapshots.join()

    def get_latest_snapshot(self) -> Optional[ContextSnapshot]:
        """Get most recent snapshot using intelligent delegation"""
        # Try loader first
        try:
            if not self.agent_id:
                raise ContextHistoryError("agent_id is required but not set")
            agent_id = self.agent_id
            loader_snapshots = self.loader.list_snapshots(agent_id)
            if loader_snapshots:
                return loader_snapshots[-1]  # Latest from loader
        except ContextHistoryError:
            # Don't catch ContextHistoryError - let it bubble up as a configuration error
            raise
        except Exception as e:
            if self.enable_logging:
                logger.debug(f"Loader query failed, falling back to local: {e}")
        
        # Fallback to local storage
        return self.snapshots[-1] if self.snapshots else None

    # --- Snapshot addressing helpers for PACT selectors ---
    def get_snapshot_by_offset(self, offset: int) -> Optional[Context]:
        """
        Get snapshot context by relative offset (@t-N). @t-1 means previous snapshot.

        Returns the full_context if available; otherwise, None.
        """
        # Try loader first
        try:
            if not self.agent_id:
                raise ContextHistoryError("agent_id is required but not set")
            agent_id = self.agent_id
            snapshot = self.loader.get_snapshot_by_offset(agent_id, offset)
            if snapshot:
                return snapshot.full_context if snapshot.full_context else None
        except ContextHistoryError:
            # Don't catch ContextHistoryError - let it bubble up as a configuration error
            raise
        except Exception as e:
            if self.enable_logging:
                logger.debug(f"Loader offset query failed, falling back to local: {e}")
        
        # Fallback to local storage
        try:
            if offset <= 0 or offset > len(self.snapshots):
                return None
            target = self.snapshots[-(offset + 1)]  # -1 is latest, so -(offset+1)
            return target.full_context if target and target.full_context else None
        except Exception:
            return None

    def get_snapshot_by_cycle(self, cycle: int) -> Optional[Context]:
        """
        Get snapshot context by absolute message cycle (@cN). Returns latest match.

        Returns the full_context if available; otherwise, None.
        """
        # Try loader first
        try:
            if not self.agent_id:
                raise ContextHistoryError("agent_id is required but not set")
            agent_id = self.agent_id
            snapshot = self.loader.get_snapshot_by_cycle(agent_id, cycle)
            if snapshot:
                return snapshot.full_context if snapshot.full_context else None
        except ContextHistoryError:
            # Don't catch ContextHistoryError - let it bubble up as a configuration error
            raise
        except Exception as e:
            if self.enable_logging:
                logger.debug(f"Loader cycle query failed, falling back to local: {e}")
        
        # Fallback to local storage
        try:
            for snap in reversed(self.snapshots):
                if getattr(snap, 'message_cycle', None) == cycle:
                    return snap.full_context if snap.full_context else None
            return None
        except Exception:
            return None
    
    def get_snapshots_by_trigger(self, trigger: str) -> List[ContextSnapshot]:
        """Get all snapshots with specific trigger using intelligent delegation"""
        # Try loader first
        try:
            if not self.agent_id:
                raise ContextHistoryError("agent_id is required but not set")
            agent_id = self.agent_id
            loader_snapshots = self.loader.get_snapshots_by_trigger(agent_id, trigger)
            if loader_snapshots:
                return loader_snapshots
        except ContextHistoryError:
            # Don't catch ContextHistoryError - let it bubble up as a configuration error
            raise
        except Exception as e:
            if self.enable_logging:
                logger.debug(f"Loader trigger query failed, falling back to local: {e}")
        
        # Fallback to local storage
        return [s for s in self.snapshots if s.trigger == trigger]
    
    def get_snapshots_in_range(self, start_time: datetime, end_time: datetime) -> List[ContextSnapshot]:
        """Get snapshots within time range (newest first)"""
        range_snapshots = [s for s in self.snapshots if start_time <= s.timestamp <= end_time]
        # Sort newest→older (descending timestamp)  
        return sorted(range_snapshots, key=lambda s: s.timestamp, reverse=True)
    
    def get_snapshots_for_turn_range(self, start_turn: int, end_turn: int) -> List[ContextSnapshot]:
        """Get snapshots within turn range (newest first)"""
        range_snapshots = [s for s in self.snapshots if start_turn <= s.message_cycle <= end_turn]
        # Sort newest→older (descending timestamp, highest turn number first)
        return sorted(range_snapshots, key=lambda s: (s.timestamp, s.message_cycle), reverse=True)
    
    def get_all_historical_contexts(self) -> List[Context]:
        """Get all historical snapshot contexts (t-1, t-2, ..., t-N) excluding current t0.
        
        Returns:
            List of Context objects from all historical snapshots, ordered newest→oldest
        """
        contexts = []
        # Process snapshots in reverse chronological order (newest first)
        for snapshot in sorted(self.snapshots, key=lambda s: s.timestamp, reverse=True):
            if snapshot.full_context:
                contexts.append(snapshot.full_context)
        return contexts
    
    
    # ToolExecutionGroup integration methods
    
    def add_execution_group(self, group: ToolExecutionGroup, snapshot_id: str):
        """Add execution group linked to snapshot
        
        Args:
            group: ToolExecutionGroup to add
            snapshot_id: ID of snapshot that triggered this execution group
        """
        self.execution_groups[group.id] = group
        
        # Link to snapshot for point-in-time correlation
        if snapshot_id not in self.groups_by_snapshot:
            self.groups_by_snapshot[snapshot_id] = []
        self.groups_by_snapshot[snapshot_id].append(group.id)
        
        # Link to turn for chronological analysis
        if group.cycle_id not in self.groups_by_turn:
            self.groups_by_turn[group.cycle_id] = []
        self.groups_by_turn[group.cycle_id].append(group.id)
    
    def get_groups_for_snapshot(self, snapshot_id: str) -> List[ToolExecutionGroup]:
        """Get all execution groups for a specific snapshot
        
        Args:
            snapshot_id: Snapshot ID to query
            
        Returns:
            List of ToolExecutionGroup objects linked to this snapshot
        """
        group_ids = self.groups_by_snapshot.get(snapshot_id, [])
        return [self.execution_groups[gid] for gid in group_ids if gid in self.execution_groups]
    
    def get_groups_for_turn(self, turn_id: str) -> List[ToolExecutionGroup]:
        """Get all execution groups for a specific turn
        
        Args:
            turn_id: Turn ID to query
            
        Returns:
            List of ToolExecutionGroup objects for this turn
        """
        group_ids = self.groups_by_turn.get(turn_id, [])
        return [self.execution_groups[gid] for gid in group_ids if gid in self.execution_groups]
    
    def get_all_execution_groups(self) -> List[ToolExecutionGroup]:
        """Get all execution groups"""
        return list(self.execution_groups.values())
    
    def get_execution_group_by_id(self, group_id: str) -> Optional[ToolExecutionGroup]:
        """Get execution group by ID"""
        return self.execution_groups.get(group_id)
    
    # Context state extraction utilities
    
    def _extract_all_components(self, snapshot: ContextSnapshot) -> List[Dict[str, Any]]:
        """Extract all components from a snapshot for analysis
        
        Args:
            snapshot: ContextSnapshot to analyze
            
        Returns:
            List of component dictionaries with metadata
        """
        components = []
        
        if not snapshot.full_context:
            return components
        
        context = snapshot.full_context
        
        try:
            # Extract system header components
            if (hasattr(context, 'system_header') and 
                context.system_header and 
                hasattr(context.system_header, 'content') and 
                isinstance(context.system_header.content, list)):
                
                for comp in context.system_header.content:
                    components.append({
                        'type': 'system_header',
                        'component': comp,
                        'content': getattr(comp, 'content', None),
                        'id': getattr(comp.metadata, 'id', None) if hasattr(comp, 'metadata') else None,
                        'source': getattr(comp.metadata, 'source', None) if hasattr(comp, 'metadata') else None,
                    })
            
            # Extract conversation history components
            if (hasattr(context, 'conversation_history') and 
                context.conversation_history and 
                hasattr(context.conversation_history, 'content') and 
                isinstance(context.conversation_history.content, list)):
                
                for comp in context.conversation_history.content:
                    components.append({
                        'type': 'conversation_history',
                        'component': comp,
                        'content': getattr(comp, 'content', None),
                        'id': getattr(comp.metadata, 'id', None) if hasattr(comp, 'metadata') else None,
                        'source': getattr(comp.metadata, 'source', None) if hasattr(comp, 'metadata') else None,
                    })
            
            # Extract active message components
            if (hasattr(context, 'active_message') and 
                context.active_message and 
                hasattr(context.active_message, 'content') and 
                isinstance(context.active_message.content, list)):
                
                for i, section in enumerate(context.active_message.content):
                    section_name = ['pre_message', 'message', 'post_message'][i] if i < 3 else f'section_{i}'
                    
                    if (hasattr(section, 'content') and 
                        section.content and 
                        isinstance(section.content, list)):
                        
                        for comp in section.content:
                            components.append({
                                'type': f'active_message_{section_name}',
                                'component': comp,
                                'content': getattr(comp, 'content', None),
                                'id': getattr(comp.metadata, 'id', None) if hasattr(comp, 'metadata') else None,
                                'source': getattr(comp.metadata, 'source', None) if hasattr(comp, 'metadata') else None,
                            })
                            
        except Exception as e:
            # Log error but don't fail completely
            pass
        
        return components
    
    def _extract_user_messages_from_snapshot(self, snapshot: ContextSnapshot) -> List[Dict[str, Any]]:
        """Extract user messages from a snapshot
        
        Args:
            snapshot: ContextSnapshot to analyze
            
        Returns:
            List of user message dictionaries
        """
        user_messages = []
        
        components = self._extract_all_components(snapshot)
        
        for comp_data in components:
            # Look for user messages in active message area
            if comp_data['type'] == 'active_message_message':
                comp = comp_data['component']
                # Check if this looks like a user message (simple heuristic)
                if hasattr(comp, 'content') and isinstance(comp.content, str):
                    user_messages.append({
                        'snapshot_id': snapshot.id,
                        'timestamp': snapshot.timestamp,
                        'turn': snapshot.message_cycle,
                        'content': comp.content,
                        'component_id': comp_data['id'],
                        'source': comp_data.get('source', 'user'),
                    })
        
        return user_messages
    
    def _calculate_snapshot_size(self, snapshot: ContextSnapshot) -> int:
        """Calculate the size of a snapshot in bytes
        
        Args:
            snapshot: ContextSnapshot to measure
            
        Returns:
            Estimated size in bytes
        """
        if snapshot.context_size_bytes:
            return snapshot.context_size_bytes
        
        try:
            if snapshot.full_context:
                return len(str(snapshot.full_context).encode('utf-8'))
            else:
                # Estimate size for diff snapshots
                return len(str(snapshot.diff_from_previous).encode('utf-8')) if snapshot.diff_from_previous else 0
        except Exception:
            return 0
    
    # Advanced analysis queries
    
    def get_user_message_timeline(self) -> List[Dict[str, Any]]:
        """Get timeline of all user messages across snapshots
        
        Returns:
            List of user message dictionaries with timeline information
        """
        timeline = []
        
        for snapshot in self.snapshots:
            user_messages = self._extract_user_messages_from_snapshot(snapshot)
            timeline.extend(user_messages)
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])
        
        return timeline
    
    def get_tool_usage_patterns(self) -> Dict[str, Any]:
        """Analyze tool usage patterns across conversation
        
        Returns:
            Dictionary with tool usage statistics and patterns
        """
        tool_stats = {}
        total_executions = 0
        total_successful = 0
        
        for group in self.execution_groups.values():
            for execution in group.executions:
                tool_name = execution.tool_name
                total_executions += 1
                
                if tool_name not in tool_stats:
                    tool_stats[tool_name] = {
                        'count': 0,
                        'success_count': 0,
                        'success_rate': 0.0,
                        'avg_duration_ms': 0.0,
                        'turns_used': set(),
                        'total_duration_ms': 0,
                    }
                
                tool_stats[tool_name]['count'] += 1
                tool_stats[tool_name]['turns_used'].add(group.cycle_id)
                
                if execution.success:
                    tool_stats[tool_name]['success_count'] += 1
                    total_successful += 1
                
                if execution.duration_ms:
                    tool_stats[tool_name]['total_duration_ms'] += execution.duration_ms
        
        # Calculate success rates and averages
        for tool_name, stats in tool_stats.items():
            if stats['count'] > 0:
                stats['success_rate'] = stats['success_count'] / stats['count']
                stats['avg_duration_ms'] = stats['total_duration_ms'] / stats['count']
            
            # Convert set to list for JSON serialization
            stats['turns_used'] = list(stats['turns_used'])
            stats['unique_turns'] = len(stats['turns_used'])
        
        return {
            'tools': tool_stats,
            'summary': {
                'total_tools_used': len(tool_stats),
                'total_executions': total_executions,
                'total_successful': total_successful,
                'overall_success_rate': total_successful / total_executions if total_executions > 0 else 0.0,
                'most_used_tool': max(tool_stats.keys(), key=lambda k: tool_stats[k]['count']) if tool_stats else None,
                'least_reliable_tool': min(tool_stats.keys(), key=lambda k: tool_stats[k]['success_rate']) if tool_stats else None,
            }
        }
    
    def get_context_growth_analysis(self) -> List[Dict[str, Any]]:
        """Analyze how context size grows over time
        
        Returns:
            List of context growth data points
        """
        growth_data = []
        
        for i, snapshot in enumerate(self.snapshots):
            size_bytes = self._calculate_snapshot_size(snapshot)
            
            growth_point = {
                'snapshot_id': snapshot.id,
                'timestamp': snapshot.timestamp.isoformat(),
                'turn': snapshot.message_cycle,
                'size_bytes': size_bytes,
                'size_mb': round(size_bytes / (1024 * 1024), 6),
                'component_count': snapshot.component_count or 0,
                'trigger': snapshot.trigger,
                'sequence_number': i,
            }
            
            # Calculate growth metrics if this isn't the first snapshot
            if i > 0:
                prev_snapshot = self.snapshots[i-1]
                prev_size = self._calculate_snapshot_size(prev_snapshot)
                
                growth_point['size_growth_bytes'] = size_bytes - prev_size
                growth_point['size_growth_percent'] = ((size_bytes - prev_size) / prev_size * 100) if prev_size > 0 else 0.0
                
                time_diff = (snapshot.timestamp - prev_snapshot.timestamp).total_seconds()
                growth_point['time_since_previous_seconds'] = time_diff
                growth_point['growth_rate_bytes_per_second'] = growth_point['size_growth_bytes'] / time_diff if time_diff > 0 else 0
            else:
                growth_point['size_growth_bytes'] = 0
                growth_point['size_growth_percent'] = 0.0
                growth_point['time_since_previous_seconds'] = 0.0
                growth_point['growth_rate_bytes_per_second'] = 0.0
            
            growth_data.append(growth_point)
        
        return growth_data
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get high-level conversation summary
        
        Returns:
            Dictionary with conversation overview and metrics
        """
        if not self.snapshots:
            return {'total_snapshots': 0}
        
        latest = self.snapshots[-1]
        first = self.snapshots[0]
        
        # Basic metrics
        conversation_duration = latest.timestamp - first.timestamp
        
        # Tool execution metrics
        total_tool_executions = sum(len(group.executions) for group in self.execution_groups.values())
        successful_executions = sum(
            sum(1 for exec in group.executions if exec.success)
            for group in self.execution_groups.values()
        )
        
        unique_tools_used = set()
        for group in self.execution_groups.values():
            for execution in group.executions:
                unique_tools_used.add(execution.tool_name)
        
        # Size metrics
        first_size = self._calculate_snapshot_size(first)
        latest_size = self._calculate_snapshot_size(latest)
        context_size_growth = latest_size - first_size
        
        # Calculate average snapshot size
        total_size = sum(self._calculate_snapshot_size(s) for s in self.snapshots)
        avg_snapshot_size = total_size / len(self.snapshots) if self.snapshots else 0
        
        # Trigger analysis
        trigger_counts = {}
        for snapshot in self.snapshots:
            trigger = snapshot.trigger
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        return {
            'total_snapshots': len(self.snapshots),
            'conversation_duration_seconds': conversation_duration.total_seconds(),
            'conversation_duration_formatted': str(conversation_duration),
            'total_turns': latest.message_cycle,
            'first_snapshot': {
                'id': first.id,
                'timestamp': first.timestamp.isoformat(),
                'size_bytes': first_size,
            },
            'latest_snapshot': {
                'id': latest.id,
                'timestamp': latest.timestamp.isoformat(),
                'size_bytes': latest_size,
            },
            'context_metrics': {
                'size_growth_bytes': context_size_growth,
                'size_growth_mb': round(context_size_growth / (1024 * 1024), 6),
                'avg_snapshot_size_bytes': round(avg_snapshot_size),
                'avg_snapshot_size_mb': round(avg_snapshot_size / (1024 * 1024), 6),
            },
            'tool_metrics': {
                'total_execution_groups': len(self.execution_groups),
                'total_tool_executions': total_tool_executions,
                'successful_executions': successful_executions,
                'tool_success_rate': successful_executions / total_tool_executions if total_tool_executions > 0 else 0.0,
                'unique_tools_used': len(unique_tools_used),
                'tools_list': list(unique_tools_used),
            },
            'snapshot_triggers': trigger_counts,
            'most_common_trigger': max(trigger_counts, key=lambda k: trigger_counts[k]) if trigger_counts else None,
        }
    
    # Diff creation system is now handled above by create_diff() method
    
    def _extract_all_components_from_context(self, context: Context) -> Dict[str, Any]:
        """Extract PACT-compliant JSON representation of context
        
        Args:
            context: Live Context to analyze
            
        Returns:
            PACT-compliant dictionary representation
        """
        try:
            # Use PACT model_dump for complete serialization
            return context.model_dump()
        except Exception:
            # Fail gracefully with empty context
            return {}
    
    def _create_component_diff(self, prev_comp_data: Dict[str, Any], curr_comp_data: Dict[str, Any]):
        """Create diff for a single component
        
        Args:
            prev_comp_data: Previous component data dictionary
            curr_comp_data: Current component data dictionary
            
        Returns:
            ComponentDiff object
        """
        from .context_snapshot import ComponentDiff
        
        comp_id = curr_comp_data['id']
        diff = ComponentDiff(component_id=comp_id)
        
        prev_comp = prev_comp_data['component']
        curr_comp = curr_comp_data['component']
        
        # Check content changes
        prev_content = prev_comp_data.get('content')
        curr_content = curr_comp_data.get('content')
        
        if prev_content != curr_content:
            diff.content_changed = True
            if isinstance(curr_content, list):
                # Store child IDs for list content
                diff.new_content = [getattr(child, 'id', str(child)) for child in curr_content]
            else:
                diff.new_content = curr_content
        
        # Check TTL changes
        prev_ttl = getattr(prev_comp, 'ttl', None)
        curr_ttl = getattr(curr_comp, 'ttl', None)
        
        if prev_ttl != curr_ttl:
            diff.ttl_changed = True
            diff.new_ttl = curr_ttl
        
        # Check metadata changes
        if hasattr(prev_comp, 'metadata') and hasattr(curr_comp, 'metadata'):
            prev_meta = prev_comp.metadata
            curr_meta = curr_comp.metadata
            
            metadata_fields = ['message_cycle', 'priority', 'active']
            for field in metadata_fields:
                prev_val = getattr(prev_meta, field, None)
                curr_val = getattr(curr_meta, field, None)
                if prev_val != curr_val:
                    diff.metadata_changes[field] = curr_val
            
            # Check children structure changes
            prev_children = getattr(prev_meta, 'children', []) or []
            curr_children = getattr(curr_meta, 'children', []) or []
            
            prev_child_ids = set(getattr(child, 'id', str(child)) for child in prev_children)
            curr_child_ids = set(getattr(child, 'id', str(child)) for child in curr_children)
            
            diff.children_added = list(curr_child_ids - prev_child_ids)
            diff.children_removed = list(prev_child_ids - curr_child_ids)
        
        return diff
    
    def _has_changes(self, component_diff) -> bool:
        """Check if a component diff has any actual changes
        
        Args:
            component_diff: ComponentDiff to check
            
        Returns:
            True if there are changes, False otherwise
        """
        return (
            component_diff.content_changed or
            component_diff.ttl_changed or
            bool(component_diff.metadata_changes) or
            bool(component_diff.children_added) or
            bool(component_diff.children_removed)
        )
    
    # Persistence layer
    
    def save(self, include_full_context: bool = True) -> str:
        """Save complete history state to configured storage engine.
        
        Args:
            include_full_context: Whether to include full context in snapshots (default True)
            
        Returns:
            str: Unique identifier for saved history (filename, key, ID, etc.)
            
        Raises:
            ContextHistoryError: If agent_id is missing or save fails
        """
        if not self.agent_id:
            raise ContextHistoryError("Agent ID required for saving history")
        
        # Prepare groups data (matching the format expected by storage engine)
        execution_groups_data = {}
        for group_id, group in self.execution_groups.items():
            execution_groups_data[group_id] = {
                'id': group.id,
                'cycle_id': group.cycle_id,
                'snapshot_id': group.snapshot_id,
                'created_at': group.created_at.isoformat(),
                'completed_at': group.completed_at.isoformat() if group.completed_at else None,
                'total_duration_ms': group.total_duration_ms,
                'execution_count': len(group.executions)
            }
        
        groups_data = {
            'execution_groups': execution_groups_data,
            'groups_by_snapshot': self.groups_by_snapshot,
            'groups_by_turn': self.groups_by_turn,
            'include_full_context': include_full_context
        }
        
        # Delegate to storage engine 
        return self.loader.save_history(self.snapshots, groups_data)
    
    def load_history(self, identifier: str, merge: bool = False) -> bool:
        """Load complete history state from configured storage engine.
        
        Args:
            identifier: Storage identifier (from save_history return value)
            merge: Whether to merge with existing snapshots or replace
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ContextHistoryError: If agent_id is missing or load fails
        """
        if not self.agent_id:
            raise ContextHistoryError("Agent ID required for loading history")
        
        try:
            # Get data from storage engine
            data = self.loader.load_history(identifier, merge)
            
            # Restore state (this will be implemented in Task 3.3)
            return self._restore_from_data(data, merge)
            
        except Exception as e:
            logger.error(f"Failed to load history {identifier}: {e}")
            return False
    
    def _restore_from_data(self, data: Dict[str, Any], merge: bool) -> bool:
        """Helper to restore state from loaded data.
        
        Args:
            data: Structured history data from loader
            merge: Whether to merge with existing data or replace
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Restoration logic for loading history from storage
            
            if not merge:
                # Clear existing data
                self.snapshots.clear()
                self._snapshots_by_id.clear()
                self.execution_groups.clear()
                self.groups_by_snapshot.clear()
                self.groups_by_turn.clear()
            
            # Restore snapshots
            if 'snapshots' in data:
                for snapshot_data in data['snapshots']:
                    try:
                        # Skip if snapshot already exists when merging
                        if merge and snapshot_data['id'] in self._snapshots_by_id:
                            continue
                            
                        # Handle timestamp conversion - could be datetime object or ISO string
                        timestamp = snapshot_data['timestamp']
                        if isinstance(timestamp, str):
                            timestamp = datetime.fromisoformat(timestamp)
                        elif not isinstance(timestamp, datetime):
                            # Fallback - try to convert
                            timestamp = datetime.fromisoformat(str(timestamp))
                        
                        # Create snapshot from dict data
                        snapshot = ContextSnapshot(
                            id=snapshot_data['id'],
                            agent_id=self.agent_id,
                            timestamp=timestamp,
                            message_cycle=snapshot_data['message_cycle'],
                            trigger=snapshot_data['trigger'],
                            turn_id=snapshot_data.get('turn_id', f"turn_{snapshot_data['message_cycle']}"),
                            pact_tree=snapshot_data.get('pact_tree'),  # Restore PACT tree from persistence
                            previous_snapshot_id=snapshot_data.get('previous_snapshot_id'),
                            provider_name=snapshot_data.get('provider_name'),
                            context_size_bytes=snapshot_data.get('context_size_bytes'),
                            component_count=snapshot_data.get('component_count'),
                            is_full_snapshot=snapshot_data.get('is_full_snapshot', True),
                        )
                        
                        self.snapshots.append(snapshot)
                        self._snapshots_by_id[snapshot.id] = snapshot
                    except Exception as e:
                        logger.warning(f"Failed to restore snapshot {snapshot_data.get('id', 'unknown')}: {e}")
                        continue
            
            # Restore execution groups
            if 'execution_groups' in data:
                for group_id, group_data in data['execution_groups'].items():
                    try:
                        # Skip if group already exists when merging
                        if merge and group_id in self.execution_groups:
                            continue
                            
                        # Handle datetime conversion for completed_at
                        completed_at = None
                        if group_data.get('completed_at'):
                            ts = group_data['completed_at']
                            if isinstance(ts, str):
                                completed_at = datetime.fromisoformat(ts)
                            elif isinstance(ts, datetime):
                                completed_at = ts
                            else:
                                completed_at = datetime.fromisoformat(str(ts))
                        
                        # Create ToolExecutionGroup from serialized data
                        group = ToolExecutionGroup(
                            id=group_data['id'],
                            cycle_id=group_data['cycle_id'],
                            snapshot_id=group_data['snapshot_id'],
                            completed_at=completed_at,
                            total_duration_ms=group_data.get('total_duration_ms'),
                            provider_name=None,  # Not stored in persistence
                            context_size_before=None,  # Not stored in persistence
                            context_size_after=None  # Not stored in persistence
                        )
                        
                        # Restore timestamps - handle created_at datetime conversion
                        created_at = group_data['created_at']
                        if isinstance(created_at, str):
                            group.created_at = datetime.fromisoformat(created_at)
                        elif isinstance(created_at, datetime):
                            group.created_at = created_at
                        else:
                            group.created_at = datetime.fromisoformat(str(created_at))
                        
                        self.execution_groups[group_id] = group
                    except Exception as e:
                        logger.warning(f"Failed to restore execution group {group_id}: {e}")
                        continue
            
            # Restore group mappings
            if 'groups_by_snapshot' in data:
                self.groups_by_snapshot.update(data['groups_by_snapshot'])
            if 'groups_by_turn' in data:
                self.groups_by_turn.update(data['groups_by_turn'])

            # Restore scaffold state from most recent snapshot with pact_tree
            if self.agent and self.snapshots:
                logger.info(f"[LOAD_HISTORY] Looking for most recent snapshot with PACT tree")
                # Find most recent snapshot with pact_tree
                for snapshot in reversed(self.snapshots):
                    if snapshot.pact_tree:
                        logger.info(f"[LOAD_HISTORY] Found snapshot {snapshot.id} with PACT tree - restoring scaffolds")
                        self._restore_scaffolds_from_pact(snapshot.pact_tree)
                        # Also restore context if available
                        if snapshot.full_context and hasattr(self.agent, 'context'):
                            self._replace_agent_context(snapshot.full_context)
                        break
                else:
                    logger.warning(f"[LOAD_HISTORY] No snapshots with PACT tree found")

            return True
            
        except Exception as e:
            logger.error(f"Failed to restore data: {e}")
            return False
    
    def save_snapshots_pickle(self, filename: Optional[str] = None) -> str:
        """Save snapshots using pickle for complete object preservation
        
        Args:
            filename: Optional filename (default: auto-generated)
            
        Returns:
            Path to the saved pickle file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"snapshots_{timestamp}.pkl"
        
        filepath = os.path.join(self.snapshot_folder, filename)
        
        # Prepare data for pickling
        pickle_data = {
            'snapshots': self.snapshots,
            'execution_groups': self.execution_groups,
            'groups_by_snapshot': self.groups_by_snapshot,
            'groups_by_turn': self.groups_by_turn,
            'metadata': {
                'version': '1.0',
                'timestamp': datetime.now(),
                'folder': os.path.basename(self.snapshot_folder),
                'total_snapshots': len(self.snapshots),
                'total_execution_groups': len(self.execution_groups),
            }
        }
        
        # Save with pickle
        with open(filepath, 'wb') as f:
            pickle.dump(pickle_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        return filepath
    
    def load(self, file_path: str) -> bool:
        """Load external snapshot using loader engine with validation
        
        Args:
            file_path: Path to snapshot file to load
            
        Returns:
            True if successful, False if validation fails
            
        Raises:
            SnapshotNotFoundError: If file doesn't exist
            CorruptedSnapshotError: If file is corrupted/invalid JSON
            AgentMismatchError: If snapshot agent_id doesn't match this history's agent_id
            InvalidSnapshotFormatError: If snapshot format is invalid
        """
        try:
            # Check if file exists first
            if not os.path.exists(file_path):
                raise SnapshotNotFoundError(f"Snapshot file not found: {file_path}")
            
            # Try to read and parse the file to check for corruption
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                raise CorruptedSnapshotError(f"Invalid JSON in snapshot file {file_path}: {e}")
            except Exception as e:
                raise CorruptedSnapshotError(f"Cannot read snapshot file {file_path}: {e}")
            
            # Use loader engine to load and validate external snapshot
            snapshot = self.loader.load_external(file_path)
            
            # Check if snapshot was successfully loaded
            if snapshot is None:
                # If file exists but couldn't be loaded, it's a validation failure
                return False
            
            # Additional validation: check agent_id match
            if not self.agent_id:
                raise ContextHistoryError("agent_id is required but not set")
            
            if snapshot.agent_id != self.agent_id:
                raise AgentMismatchError(
                    f"Snapshot agent_id '{snapshot.agent_id}' doesn't match history agent_id '{self.agent_id}'"
                )
            
            # Replace agent context if we have an agent reference
            logger.info(f"[LOAD] Replacing agent context")
            if self.agent and hasattr(self.agent, 'context') and snapshot.full_context:
                self._replace_agent_context(snapshot.full_context)
                logger.info(f"[LOAD] Context replaced successfully")
            else:
                logger.warning(f"[LOAD] Context replacement skipped - agent: {bool(self.agent)}, has_context: {hasattr(self.agent, 'context') if self.agent else False}, full_context: {bool(snapshot.full_context)}")

            # Restore scaffold state from PACT tree
            logger.info(f"[LOAD] Checking for scaffold restoration - pact_tree exists: {bool(snapshot.pact_tree)}")
            if self.agent and snapshot.pact_tree:
                logger.info(f"[LOAD] Calling _restore_scaffolds_from_pact()")
                self._restore_scaffolds_from_pact(snapshot.pact_tree)
            else:
                logger.warning(f"[LOAD] Scaffold restoration skipped - agent: {bool(self.agent)}, pact_tree: {bool(snapshot.pact_tree) if hasattr(snapshot, 'pact_tree') else 'N/A'}")

            # Add snapshot to local storage for immediate access
            with self._storage_lock:
                self.snapshots.append(snapshot)
                self._snapshots_by_id[snapshot.id] = snapshot
            
            if self.enable_logging:
                logger.info(f"Successfully loaded external snapshot {snapshot.id} from {file_path}")
            
            return True
            
        except (SnapshotNotFoundError, CorruptedSnapshotError, AgentMismatchError, InvalidSnapshotFormatError):
            # Let these exceptions bubble up to caller
            raise
        except Exception as e:
            # Validation or other errors - return False
            if self.enable_logging:
                logger.warning(f"Failed to load snapshot from {file_path}: {e}")
            return False
    
    def _replace_agent_context(self, new_context: Context) -> None:
        """Replace agent's context with loaded context

        Args:
            new_context: Context to replace with
        """
        if self.agent and hasattr(self.agent, 'context'):
            self.agent.context = new_context
            if self.enable_logging:
                logger.debug("Replaced agent context with loaded snapshot context")

    def _restore_scaffolds_from_pact(self, pact_tree: Dict[str, Any]) -> None:
        """
        Restore scaffold state from PACT tree org namespace.

        Called after loading context from snapshot to restore scaffold state
        for all scaffolds that have persisted state.

        Args:
            pact_tree: PACT tree data structure from snapshot
        """
        logger.info(f"[SCAFFOLD RESTORE] Starting scaffold state restoration")

        if not self.agent or not hasattr(self.agent, '_scaffold_list'):
            logger.warning(f"[SCAFFOLD RESTORE] No agent or no scaffolds found - skipping restoration")
            return

        logger.info(f"[SCAFFOLD RESTORE] Agent has {len(self.agent._scaffold_list)} scaffolds")

        # Find all nodes with scaffold_state in org
        scaffold_nodes = self._find_scaffold_nodes(pact_tree)
        logger.info(f"[SCAFFOLD RESTORE] Found {len(scaffold_nodes)} scaffold nodes in PACT tree")

        if not scaffold_nodes:
            logger.warning(f"[SCAFFOLD RESTORE] No scaffold state found in PACT tree")
            return

        # Build map of scaffold instances by type
        scaffold_map_by_type = {}
        for scaffold in self.agent._scaffold_list:
            if hasattr(scaffold, 'type') and scaffold.type:
                scaffold_map_by_type[scaffold.type] = scaffold
                logger.debug(f"[SCAFFOLD RESTORE] Mapped scaffold type={scaffold.type}, current_id={getattr(scaffold, 'id', 'unknown')}")

        logger.info(f"[SCAFFOLD RESTORE] Built scaffold map with {len(scaffold_map_by_type)} scaffold types")

        # Restore each scaffold - restore ID AND state
        restored_count = 0
        for node in scaffold_nodes:
            org = node.get('org', {})
            scaffold_type = node.get('nodeType')  # Use nodeType from PACT tree
            saved_id = node.get('id')  # Get the saved ID from PACT node
            logger.debug(f"[SCAFFOLD RESTORE] Processing node with type={scaffold_type}, saved_id={saved_id}")

            if scaffold_type and scaffold_type in scaffold_map_by_type:
                scaffold = scaffold_map_by_type[scaffold_type]
                state_json = org.get('scaffold_state')

                # First, restore the scaffold's ID so it matches the saved one
                if saved_id:
                    old_id = scaffold.id
                    scaffold.id = saved_id
                    logger.info(f"[SCAFFOLD RESTORE] Restored scaffold ID: {old_id} → {saved_id}")

                # Then restore the state
                if state_json:
                    try:
                        logger.debug(f"[SCAFFOLD RESTORE] Parsing state JSON for {saved_id}")
                        state_dict = json.loads(state_json)
                        logger.debug(f"[SCAFFOLD RESTORE] State dict keys: {list(state_dict.keys())}")

                        # Restore state using model_validate and set via private attribute
                        # (state is a property without setter, backed by _scaffold_state)
                        restored_state = scaffold.state.__class__.model_validate(state_dict)
                        scaffold._scaffold_state = restored_state
                        restored_count += 1
                        logger.info(f"[SCAFFOLD RESTORE] ✅ Restored state for scaffold {saved_id}")
                        logger.debug(f"[SCAFFOLD RESTORE] Restored state: {scaffold.state}")
                    except Exception as e:
                        logger.error(f"[SCAFFOLD RESTORE] ❌ Failed to restore scaffold type={scaffold_type}: {e}", exc_info=True)
                else:
                    logger.warning(f"[SCAFFOLD RESTORE] No scaffold_state in org for type={scaffold_type}")
                    # Still count as restored if we at least restored the ID
                    if saved_id:
                        restored_count += 1
            else:
                logger.warning(f"[SCAFFOLD RESTORE] Scaffold type={scaffold_type} not found in scaffold map")

        logger.info(f"[SCAFFOLD RESTORE] Successfully restored {restored_count}/{len(scaffold_nodes)} scaffold(s)")

    def _find_scaffold_nodes(self, tree: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Recursively find nodes with scaffold_state in org namespace.

        Args:
            tree: PACT tree or subtree to search

        Returns:
            List of nodes containing scaffold_state in their org namespace
        """
        results = []

        def visit(node):
            if isinstance(node, dict):
                org = node.get('org', {})
                if 'scaffold_state' in org:
                    results.append(node)
                # Recursively visit children
                for child in node.get('children', []):
                    visit(child)

        visit(tree)
        return results

    def list_saved_files(self) -> List[Dict[str, Any]]:
        """List all saved history files in the snapshot folder
        
        Returns:
            List of file information dictionaries
        """
        files = []
        
        if not os.path.exists(self.snapshot_folder):
            return files
        
        for filename in os.listdir(self.snapshot_folder):
            if filename.endswith(('.json', '.pkl')):
                filepath = os.path.join(self.snapshot_folder, filename)
                stat = os.stat(filepath)
                
                file_info = {
                    'filename': filename,
                    'filepath': filepath,
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 3),
                    'modified_time': datetime.fromtimestamp(stat.st_mtime),
                    'file_type': 'pickle' if filename.endswith('.pkl') else 'json',
                }
                
                # Try to read metadata from JSON files
                if filename.endswith('.json'):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if 'metadata' in data:
                            file_info['metadata'] = data['metadata']
                    except Exception:
                        file_info['metadata'] = {'error': 'Could not read metadata'}
                
                files.append(file_info)
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified_time'], reverse=True)
        
        return files
    
    def cleanup_old_files(self, keep_count: int = 10, max_age_days: int = 30) -> int:
        """Clean up old saved files
        
        Args:
            keep_count: Number of most recent files to keep
            max_age_days: Maximum age in days for files to keep
            
        Returns:
            Number of files deleted
        """
        from datetime import timedelta
        
        files = self.list_saved_files()
        
        if len(files) <= keep_count:
            return 0
        
        deleted_count = 0
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        
        # Delete files beyond keep_count or older than max_age_days
        for file_info in files[keep_count:]:
            if file_info['modified_time'] < cutoff_time:
                try:
                    os.remove(file_info['filepath'])
                    deleted_count += 1
                except Exception:
                    pass  # Ignore errors during cleanup
        
        return deleted_count
    
    # Error handling and health monitoring
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get snapshot processing statistics
        
        Returns:
            Dictionary with processing statistics
        """
        return {
            'total_processed': self._total_processed,
            'total_failed': self._total_failed,
            'success_rate': self._total_processed / (self._total_processed + self._total_failed) if (self._total_processed + self._total_failed) > 0 else 0.0,
            'pending_snapshots': self._pending_snapshots.qsize(),
            'processor_running': self._snapshot_processor is not None and self._snapshot_processor.is_alive(),
            'processing_enabled': self._processing_enabled,
            'failed_snapshots_count': len(self._failed_snapshots)
        }
    
    def get_failed_snapshots(self) -> List[Dict[str, Any]]:
        """Get list of failed snapshot attempts
        
        Returns:
            List of failure records
        """
        return self._failed_snapshots.copy()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status of ContextHistory
        
        Returns:
            Dictionary with health information
        """
        stats = self.get_processing_stats()
        
        # Determine health status
        if not stats['processing_enabled']:
            status = 'disabled'
        elif stats['total_failed'] == 0:
            status = 'healthy'
        elif stats['success_rate'] >= 0.95:
            status = 'good'
        elif stats['success_rate'] >= 0.8:
            status = 'degraded'
        else:
            status = 'unhealthy'
        
        return {
            'status': status,
            'message': self._get_health_message(status, stats),
            'statistics': stats,
            'recommendations': self._get_health_recommendations(status, stats)
        }
    
    def _get_health_message(self, status: str, stats: Dict[str, Any]) -> str:
        """Get human-readable health message"""
        if status == 'disabled':
            return "Snapshot processing is disabled"
        elif status == 'healthy':
            return f"All systems operational ({stats['total_processed']} snapshots processed)"
        elif status == 'good':
            return f"Minor issues detected (success rate: {stats['success_rate']:.1%})"
        elif status == 'degraded':
            return f"Performance degraded (success rate: {stats['success_rate']:.1%})"
        else:
            return f"System unhealthy (success rate: {stats['success_rate']:.1%})"
    
    def _get_health_recommendations(self, status: str, stats: Dict[str, Any]) -> List[str]:
        """Get health improvement recommendations"""
        recommendations = []
        
        if not stats['processing_enabled']:
            recommendations.append("Enable snapshot processing")
        
        if not stats['processor_running'] and stats['processing_enabled']:
            recommendations.append("Restart snapshot processor")
        
        if stats['pending_snapshots'] > 100:
            recommendations.append("High pending snapshot queue - consider increasing processing capacity")
        
        if stats['success_rate'] < 0.9 and stats['total_failed'] > 0:
            recommendations.append("Investigate failed snapshot causes")
        
        if stats['failed_snapshots_count'] > 50:
            recommendations.append("Clear old failed snapshot records")
        
        return recommendations
    
    def clear_failed_snapshots(self) -> int:
        """Clear failed snapshot records
        
        Returns:
            Number of records cleared
        """
        count = len(self._failed_snapshots)
        self._failed_snapshots.clear()
        return count
    
    def restart_processor(self) -> bool:
        """Restart the snapshot processor
        
        Returns:
            True if successfully restarted, False otherwise
        """
        try:
            # Stop current processor
            self.stop_processing()
            time.sleep(0.5)  # Give it time to stop
            
            # Re-enable and restart
            self._processing_enabled = True
            self._start_snapshot_processor()
            
            if self.enable_logging:
                logger.info("Snapshot processor restarted")
            
            return True
            
        except Exception as e:
            if self.enable_logging:
                logger.error(f"Failed to restart processor: {e}")
            return False
    
    def force_process_pending(self, max_items: int = 10) -> int:
        """Force process pending snapshots synchronously (for emergency recovery)
        
        Args:
            max_items: Maximum number of items to process
            
        Returns:
            Number of items processed
        """
        processed = 0
        
        try:
            while processed < max_items and not self._pending_snapshots.empty():
                try:
                    task = self._pending_snapshots.get_nowait()
                    self._process_single_snapshot(task)
                    self._pending_snapshots.task_done()
                    processed += 1
                    
                except Empty:
                    break
                except Exception as e:
                    if self.enable_logging:
                        logger.error(f"Failed to force process snapshot: {e}")
                    # Continue with next item
                    continue
            
            if self.enable_logging:
                logger.info(f"Force processed {processed} pending snapshots")
            
        except Exception as e:
            if self.enable_logging:
                logger.error(f"Error during force processing: {e}")
        
        return processed
    
    def get_memory_usage_estimate(self) -> Dict[str, Any]:
        """Estimate memory usage of ContextHistory
        
        Returns:
            Dictionary with memory usage estimates
        """
        try:
            import sys
            
            # Estimate snapshot memory usage
            snapshot_memory = sum(sys.getsizeof(snapshot) for snapshot in self.snapshots)
            
            # Estimate execution group memory
            group_memory = sum(sys.getsizeof(group) for group in self.execution_groups.values())
            
            # Estimate index memory
            index_memory = sys.getsizeof(self._snapshots_by_id) + sys.getsizeof(self.groups_by_snapshot) + sys.getsizeof(self.groups_by_turn)
            
            total_memory = snapshot_memory + group_memory + index_memory
            
            return {
                'total_bytes': total_memory,
                'total_mb': round(total_memory / (1024 * 1024), 2),
                'snapshot_memory_bytes': snapshot_memory,
                'group_memory_bytes': group_memory,
                'index_memory_bytes': index_memory,
                'snapshots_count': len(self.snapshots),
                'groups_count': len(self.execution_groups),
                'avg_snapshot_size_bytes': snapshot_memory // len(self.snapshots) if self.snapshots else 0
            }
            
        except Exception as e:
            if self.enable_logging:
                logger.warning(f"Failed to calculate memory usage: {e}")
            
            return {
                'error': str(e),
                'snapshots_count': len(self.snapshots),
                'groups_count': len(self.execution_groups)
            }
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.stop_processing()
        except AttributeError:
            # Object not fully initialized
            pass
