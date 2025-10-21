"""
Context History Error Classes

Exception hierarchy for context history operations including loading,
snapshot processing, and persistence errors.
"""


class ContextHistoryError(Exception):
    """Base exception for ContextHistory errors"""
    pass


class SnapshotProcessingError(ContextHistoryError):
    """Error during snapshot processing"""
    pass


class PersistenceError(ContextHistoryError):
    """Error during persistence operations"""
    pass


# Context History Load specific errors
class ContextHistoryLoadError(ContextHistoryError):
    """Base exception for context loading errors"""
    pass


class SnapshotNotFoundError(ContextHistoryLoadError):
    """Snapshot not found for given parameters"""
    pass


class SnapshotReconstructionError(ContextHistoryLoadError):
    """Failed to reconstruct context from snapshot"""
    pass


class CorruptedSnapshotError(ContextHistoryLoadError):
    """Snapshot data is corrupted or invalid"""
    pass


class InvalidSnapshotFormatError(ContextHistoryLoadError):
    """Snapshot format is invalid or missing required fields"""
    pass


class AgentMismatchError(ContextHistoryLoadError):
    """Snapshot agent_id doesn't match current agent"""
    pass


class LoaderEngineError(ContextHistoryLoadError):
    """Error in the snapshot loader engine"""
    pass


class ContextReplacementError(ContextHistoryLoadError):
    """Error during context replacement operation"""
    pass