
from dataclasses import dataclass
from typing import List
from datetime import datetime
from ..context_snapshot import ContextSnapshot

@dataclass
class ValidationResult:
    """Result of snapshot data validation."""
    valid: bool
    errors: List[str]


@dataclass
class CacheEntry:
    """Entry in the memory cache with access tracking."""
    snapshot: ContextSnapshot
    last_access: datetime
    access_count: int = 0