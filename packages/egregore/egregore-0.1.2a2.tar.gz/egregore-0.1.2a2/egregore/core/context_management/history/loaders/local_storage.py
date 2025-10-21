"""
Snapshot Loader Engine - Pluggable storage backends for context snapshots

Provides abstract base class and implementations for loading snapshots from various
storage systems (files, Redis, SQL, Web, etc.).
"""

import json
import logging
import os
import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from threading import Lock

from ..context_snapshot import ContextSnapshot
from ..errors import (
    SnapshotNotFoundError, CorruptedSnapshotError,
    LoaderEngineError
)
from .data_models import ValidationResult
from .base import SnapshotLoaderEngine
from ..loader_settings import LocalLoaderSettings

logger = logging.getLogger(__name__)



class LocalSnapshotLoader(SnapshotLoaderEngine):
    """Smart local filesystem snapshot storage with memory management."""

    def __init__(self, settings: LocalLoaderSettings, **kwargs):
        """Initialize local snapshot loader.

        Args:
            settings: LocalLoaderSettings configuration
            **kwargs: Passed to parent SnapshotLoaderEngine
        """
        super().__init__(settings=settings, **kwargs)

        # Type hint for IDE
        self.settings: LocalLoaderSettings = settings

        # Setup storage directory from settings
        self.base_dir = settings.base_dir
        self.storage_path = settings.base_dir

        # Create directories
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"LocalSnapshotLoader initialized: {self.storage_path}, format={settings.format}, compress={settings.compress}")
        logger.info(f"LocalSnapshotLoader using directory: {self.base_dir}, agent_id: {settings.agent_id}")
    
    def _persist_to_storage(self, snapshot: ContextSnapshot) -> bool:
        """Persist snapshot to local filesystem."""
        try:
            agent_dir = self.base_dir / (snapshot.agent_id or "default")
            agent_dir.mkdir(exist_ok=True)
            
            snapshot_file = agent_dir / f"{snapshot.id}.json"
            
            # Convert snapshot to dict for JSON serialization
            snapshot_data = snapshot.model_dump()
            
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, indent=2, default=str)
            
            logger.debug(f"Persisted snapshot {snapshot.id} to {snapshot_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to persist snapshot {snapshot.id}: {e}")
            return False
    
    def _load_from_storage(self, identifier: str) -> Optional[ContextSnapshot]:
        """Load snapshot from local filesystem.
        
        Args:
            identifier: Can be either:
                - snapshot_id: loads from agent's directory  
                - full_path: loads from specific file path
        """
        try:
            # Check if identifier is a full path
            if os.path.sep in identifier or identifier.endswith('.json'):
                return self._load_from_path(identifier)
            
            # Otherwise, treat as snapshot_id and search agent directories
            return self._load_by_snapshot_id(identifier)
            
        except Exception as e:
            logger.error(f"Failed to load snapshot {identifier}: {e}")
            return None
    
    def _load_from_path(self, path: str) -> Optional[ContextSnapshot]:
        """Load snapshot from local file path.
        
        Args:
            path: File path to snapshot JSON file
            
        Returns:
            ContextSnapshot if file exists and is valid, None otherwise
            
        Raises:
            SnapshotNotFoundError: If file doesn't exist
            CorruptedSnapshotError: If JSON is invalid or file is corrupted
            InvalidSnapshotFormatError: If snapshot format is invalid
            LoaderEngineError: For other loading errors
        """
        try:
            file_path = Path(path)
            
            # Check if file exists
            if not file_path.exists():
                logger.warning(f"Snapshot file not found: {path}")
                raise SnapshotNotFoundError(f"Snapshot file not found: {path}")
                
            # Check if path is actually a file
            if not file_path.is_file():
                logger.error(f"Snapshot path is not a file: {path}")
                raise LoaderEngineError(f"Path is not a file: {path}")
            
            # Check file size (basic corruption check)
            file_size = file_path.stat().st_size
            if file_size == 0:
                logger.error(f"Snapshot file is empty: {path}")
                raise CorruptedSnapshotError(f"Snapshot file is empty: {path}")
            
            # Check file permissions
            if not os.access(file_path, os.R_OK):
                logger.error(f"Permission denied reading snapshot file: {path}")
                raise LoaderEngineError(f"Permission denied reading file: {path}")
            
            # Read and parse JSON with detailed error handling
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    snapshot_data = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in snapshot file {path}: {e}")
                raise CorruptedSnapshotError(f"Invalid JSON in snapshot file {path}: {e}")
            except UnicodeDecodeError as e:
                logger.error(f"Invalid encoding in snapshot file {path}: {e}")
                raise CorruptedSnapshotError(f"Invalid encoding in snapshot file {path}: {e}")
            
            # Validate snapshot data structure
            validation_result = self._validate_snapshot_data(snapshot_data)
            if not validation_result.valid:
                logger.error(f"Invalid snapshot format in {path}: {validation_result.errors}")
                return None
            
            # Create ContextSnapshot object with error handling
            try:
                snapshot = ContextSnapshot(**snapshot_data)
                logger.info(f"Successfully loaded snapshot from: {path}")
                return snapshot
            except Exception as e:
                logger.error(f"Failed to create ContextSnapshot from {path}: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load snapshot from {path}: {e}")
            return None
    
    def _load_by_snapshot_id(self, snapshot_id: str) -> Optional[ContextSnapshot]:
        """Load snapshot by searching agent directories."""
        # Search in all agent directories for the snapshot file
        for agent_dir in self.base_dir.iterdir():
            if agent_dir.is_dir():
                snapshot_file = agent_dir / f"{snapshot_id}.json"
                if snapshot_file.exists():
                    return self._load_from_path(str(snapshot_file))
        
        logger.warning(f"Snapshot {snapshot_id} not found in any agent directory")
        return None
    
    def _validate_snapshot_data(self, data: dict) -> ValidationResult:
        """Validate that snapshot data has required fields."""
        required_fields = ['id', 'message_cycle', 'trigger', 'turn_id', 'timestamp']
        errors = []
        
        if not isinstance(data, dict):
            errors.append(f"Snapshot data must be a dictionary, got {type(data)}")
            return ValidationResult(valid=False, errors=errors)
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif data[field] is None:
                errors.append(f"Required field is None: {field}")
        
        # Validate field types
        if 'message_cycle' in data and not isinstance(data['message_cycle'], int):
            errors.append(f"message_cycle must be an integer, got {type(data['message_cycle'])}")
        
        if 'id' in data and not isinstance(data['id'], str):
            errors.append(f"id must be a string, got {type(data['id'])}")
        
        return ValidationResult(valid=len(errors) == 0, errors=errors)
    
    def _serialize_snapshot(self, snapshot: ContextSnapshot) -> Dict:
        """Serialize ContextSnapshot to dict format for storage.
        
        Args:
            snapshot: ContextSnapshot to serialize
            
        Returns:
            Dict representation of the snapshot
            
        Raises:
            ValueError: If snapshot serialization fails
        """
        try:
            return snapshot.model_dump()
        except Exception as e:
            logger.error(f"Failed to serialize snapshot {snapshot.id}: {e}")
            raise ValueError(f"Snapshot serialization failed: {e}")
    
    # === History Operations Implementation (NEW) ===
    
    def save_history(self, snapshots: List[ContextSnapshot], groups_data: Dict) -> str:
        """Save complete history state with all snapshots and metadata.
        
        Args:
            snapshots: List of all context snapshots to save
            groups_data: Metadata including execution_groups, groups_by_snapshot, etc.
            
        Returns:
            str: Filename of saved history file
            
        Raises:
            ContextHistoryError: On save failures, permission issues, etc.
        """
        try:
            # Create timestamp and filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"history_{self.settings.agent_id or 'default'}_{timestamp}.json"
            full_path = self.storage_path / filename
            
            # Prepare data for serialization (adapted from ContextHistory.save_to_disk)
            save_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'agent_id': self.settings.agent_id,
                'snapshots': [],
                'execution_groups': groups_data.get('execution_groups', {}),
                'groups_by_snapshot': groups_data.get('groups_by_snapshot', {}),
                'groups_by_turn': groups_data.get('groups_by_turn', {}),
                'metadata': {
                    'total_snapshots': len(snapshots),
                    'total_execution_groups': len(groups_data.get('execution_groups', {})),
                    'include_full_context': groups_data.get('include_full_context', True)
                }
            }
            
            # Serialize snapshots using our helper method
            for snapshot in snapshots:
                snapshot_data = self._serialize_snapshot(snapshot)
                save_data['snapshots'].append(snapshot_data)
            
            # Ensure directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, default=str, ensure_ascii=False)

            logger.info(f"Saved history to {filename} with {len(snapshots)} snapshots")
            return str(full_path)  # Return full path for easy loading
            
        except Exception as e:
            from ..errors import ContextHistoryError
            logger.error(f"Failed to save history: {e}")
            raise ContextHistoryError(f"Failed to save history: {e}")
    
    def load_history(self, identifier: str, merge: bool = False) -> Dict:
        """Load complete history state from storage.
        
        Args:
            identifier: Storage identifier (filename or path)
            merge: Whether to merge with existing snapshots or replace
            
        Returns:
            Dict containing structured history data
            
        Raises:
            ContextHistoryError: On load failures, missing files, corruption
        """
        try:
            # Construct full path
            full_path = self.storage_path / identifier
            
            # Check if file exists
            if not full_path.exists():
                from ..errors import ContextHistoryError
                raise ContextHistoryError(f"History file not found: {identifier}")
            
            # Determine format and load accordingly
            if full_path.suffix == '.json' or identifier.endswith('.json'):
                return self._load_history_json(full_path, merge)
            else:
                # Assume pickle format
                return self._load_history_pickle(full_path, merge)
                
        except Exception as e:
            from ..errors import ContextHistoryError
            logger.error(f"Failed to load history {identifier}: {e}")
            raise ContextHistoryError(f"Failed to load history {identifier}: {e}")
    
    def _load_history_json(self, file_path: Path, merge: bool = False) -> Dict:
        """Load history from JSON file (adapted from ContextHistory.load_from_disk).
        
        Args:
            file_path: Path to JSON file
            merge: Whether to merge with existing data
            
        Returns:
            Dict containing structured history data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Return structured data instead of modifying instance state
            return {
                'snapshots': data.get('snapshots', []),
                'execution_groups': data.get('execution_groups', {}),
                'groups_by_snapshot': data.get('groups_by_snapshot', {}),
                'groups_by_turn': data.get('groups_by_turn', {}),
                'metadata': data.get('metadata', {}),
                'format': 'json',
                'timestamp': data.get('timestamp', ''),
                'version': data.get('version', '1.0'),
                'agent_id': data.get('agent_id', self.settings.agent_id)
            }
            
        except Exception as e:
            logger.error(f"Failed to load JSON history from {file_path}: {e}")
            raise
    
    def _load_history_pickle(self, file_path: Path, merge: bool = False) -> Dict:
        """Load history from pickle file (adapted from ContextHistory.load_snapshots_pickle).
        
        Args:
            file_path: Path to pickle file
            merge: Whether to merge with existing data
            
        Returns:
            Dict containing structured history data
        """
        try:
            import pickle
            
            with open(file_path, 'rb') as f:
                pickle_data = pickle.load(f)
            
            # Convert pickle data to structured format matching JSON
            snapshots_data = []
            if 'snapshots' in pickle_data:
                # Convert ContextSnapshot objects to dict format
                for snapshot in pickle_data['snapshots']:
                    if hasattr(snapshot, 'model_dump'):
                        # Pydantic model
                        snapshots_data.append(snapshot.model_dump())
                    elif hasattr(snapshot, '__dict__'):
                        # Regular object - extract attributes
                        snapshots_data.append(vars(snapshot))
                    else:
                        # Fallback - try to serialize as-is
                        snapshots_data.append(snapshot)
            
            # Return structured data format matching JSON format
            return {
                'snapshots': snapshots_data,
                'execution_groups': pickle_data.get('execution_groups', {}),
                'groups_by_snapshot': pickle_data.get('groups_by_snapshot', {}),
                'groups_by_turn': pickle_data.get('groups_by_turn', {}),
                'metadata': pickle_data.get('metadata', {}),
                'format': 'pickle',
                'timestamp': pickle_data.get('metadata', {}).get('timestamp', ''),
                'version': '1.0',  # Pickle files don't typically have version info
                'agent_id': self.settings.agent_id  # Use loader's agent_id
            }
            
        except Exception as e:
            logger.error(f"Failed to load pickle history from {file_path}: {e}")
            raise
    
    def list_saved_histories(self, agent_id: str) -> List[Dict]:
        """List all saved histories for an agent.
        
        Args:
            agent_id: Agent ID to list histories for
            
        Returns:
            List of dicts with keys: 'identifier', 'timestamp', 'snapshot_count'
        """
        try:
            histories = []
            
            # Scan storage directory for history files
            pattern = f"history_{agent_id}_*.json"
            for file_path in self.storage_path.glob(pattern):
                try:
                    # Extract metadata from file
                    history_info = self._extract_history_metadata(file_path)
                    if history_info:
                        histories.append(history_info)
                except Exception as e:
                    logger.warning(f"Failed to process history file {file_path}: {e}")
                    continue
            
            # Also check for pickle files (legacy format)
            pickle_pattern = f"*{agent_id}*.pkl"
            for file_path in self.storage_path.glob(pickle_pattern):
                try:
                    history_info = self._extract_history_metadata(file_path)
                    if history_info:
                        histories.append(history_info)
                except Exception as e:
                    logger.warning(f"Failed to process pickle file {file_path}: {e}")
                    continue
            
            # Sort by timestamp (newest first)
            histories.sort(key=lambda x: x['timestamp'], reverse=True)
            return histories
            
        except Exception as e:
            logger.error(f"Failed to list saved histories for agent {agent_id}: {e}")
            return []
    
    def delete_history(self, identifier: str) -> bool:
        """Delete saved history by identifier.
        
        Args:
            identifier: History identifier (filename) to delete
            
        Returns:
            bool: True if successfully deleted, False otherwise
        """
        try:
            file_path = self.storage_path / identifier
            
            if not file_path.exists():
                logger.warning(f"History file not found for deletion: {identifier}")
                return False
            
            # Safety check - only delete files that look like history files
            if not (identifier.startswith('history_') or identifier.endswith('.pkl')):
                logger.error(f"Refusing to delete file that doesn't look like a history file: {identifier}")
                return False
            
            # Delete the file
            file_path.unlink()
            logger.info(f"Successfully deleted history file: {identifier}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete history {identifier}: {e}")
            return False
    
    def _extract_history_metadata(self, file_path: Path) -> Optional[Dict]:
        """Extract metadata from a history file.
        
        Args:
            file_path: Path to history file
            
        Returns:
            Dict with metadata or None if extraction fails
        """
        try:
            if file_path.suffix == '.json':
                # Extract from JSON file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                return {
                    'identifier': file_path.name,
                    'timestamp': data.get('timestamp', ''),
                    'snapshot_count': data.get('metadata', {}).get('total_snapshots', 0),
                    'format': 'json',
                    'size_bytes': file_path.stat().st_size,
                    'agent_id': data.get('agent_id', '')
                }
            
            elif file_path.suffix == '.pkl':
                # Extract from pickle file
                import pickle
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                
                metadata = data.get('metadata', {})
                timestamp = metadata.get('timestamp', '')
                if hasattr(timestamp, 'isoformat'):
                    timestamp = timestamp.isoformat()
                
                return {
                    'identifier': file_path.name,
                    'timestamp': str(timestamp),
                    'snapshot_count': len(data.get('snapshots', [])),
                    'format': 'pickle',
                    'size_bytes': file_path.stat().st_size,
                    'agent_id': self.settings.agent_id or ''
                }
            
            else:
                logger.warning(f"Unknown file format for history metadata extraction: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")
            return None