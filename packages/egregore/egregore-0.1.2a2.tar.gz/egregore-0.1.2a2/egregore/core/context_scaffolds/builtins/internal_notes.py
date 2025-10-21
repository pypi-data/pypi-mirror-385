"""
Internal Notes Scaffold - V2 Implementation

LLM working memory for tracking thoughts, findings, and analysis.
"""

from typing import Optional, ClassVar, Dict, List, Tuple, Union, Callable
from datetime import datetime
from pydantic import Field
from ..xml_base import BaseXMLScaffold
from ..data_types import ScaffoldState, StateOperatorResult
from ..decorators import operation
from ..notifications import notification
from ...context_management.pact.components.core import XMLComponent
from ..change_tracking import ChangeTrackingList


class NoteBlock(XMLComponent):
    """Individual note as XMLComponent with clean Pydantic field declarations."""
    type: str = "note"
    content: str = ""
    operation_type: str = "append"
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
    turn: Optional[int] = None
    priority: Optional[str] = None


class NotesState(ScaffoldState):
    """State for internal notes with V2 change detection and structured storage."""
    notes: List[NoteBlock] = Field(default_factory=list)
    utilization: float = 0.0


class InternalNotesScaffold(BaseXMLScaffold):
    """
    Structured LLM working memory scaffold with timestamped note blocks.
    
    Your working memory - track thoughts, findings, and analysis as structured, timestamped notes.
    Each note is a separate component with metadata (timestamp, operation type, priority).
    The current state is ALWAYS visible in the context as structured XML.
    
    Features:
    - Timestamped note blocks with operation tracking (append/update)
    - Token-aware with automatic utilization calculation
    - XML structure: <internal_notes><note timestamp="..." operation_type="...">content</note></internal_notes>
    - V2 enhancements: notifications, operation synonyms, parameter hints, error recovery
    - Automatic change detection: No manual mark_changed() or update_state() calls needed
    
    ## Automatic Change Detection Example
    
    Before (manual state management):
    ```python
    # Old way - required manual change tracking
    self.state.notes.append(new_note)
    self.mark_changed('notes')  # Manual call required
    
    # Or
    self.update_state(notes=updated_notes)  # Full state replacement
    ```
    
    After (automatic change detection):
    ```python
    # New way - automatic change detection
    self.state.notes.append(new_note)  # Automatically triggers scaffold re-rendering
    # No manual calls needed - change detection is automatic!
    ```
    """
    
    type: str = "internal_notes"
    state: NotesState = NotesState()
    
    # =====================================================================
    # HINT CONFIGURATION - Enhanced user experience for InternalNotes
    # =====================================================================
    
    OPERATION_SYNONYMS: ClassVar[Dict[str, List[str]]] = {
        "append": ["add", "write", "insert", "note", "record", "save", "jot"],
        "update": ["replace", "set", "change", "overwrite", "refresh", "rewrite"],
    }
    
    PARAMETER_SUGGESTIONS: ClassVar[Dict[Tuple[str, str], Union[str, Callable]]] = {
        ("append", "content"): lambda self: f"Note text (current: {self.count_tokens(chr(10).join(note.content for note in self.state.notes))}/{self.get_token_limit()} tokens, {self.get_token_limit() - self.count_tokens(chr(10).join(note.content for note in self.state.notes))} available)",
        ("update", "content"): lambda self: f"Replacement text (max {self.get_token_limit()} tokens, currently {self.count_tokens(chr(10).join(note.content for note in self.state.notes))})",
    }
    
    ERROR_RECOVERY_PATTERNS: ClassVar[Dict[str, List[str]]] = {
        r"token.*limit|exceed.*limit": [
            "Consider using update() to replace all content instead of append()",
            "Break content into smaller, more focused notes",
            "Use update() to compress existing content"
        ],
        r"empty.*content|no.*content": [
            "Provide text content for your notes",
            "Content parameter cannot be empty"
        ],
        r"cannot.*append|would.*exceed": [
            "Try using update() to replace existing notes",
            "Consider summarizing existing content to make room",
            "Current notes may be too long for additional content"
        ]
    }
    
    def render(self):
        """Clean BaseXMLScaffold render - return components directly!"""
        total_content = "\n".join(note.content for note in self.state.notes)
        total_tokens = self.count_tokens(total_content)
        max_tokens = self.get_token_limit()
        utilization = (total_tokens / max_tokens) * 100 if max_tokens > 0 else 0
        self.state.utilization = utilization
        
        self.xml.attrs['note_count'] = str(len(self.state.notes))
        self.xml.attrs['utilization'] = f"{utilization:.1f}%"
        
        current_turn = self.agent.context.cad if self.agent and self.agent.context else None
        
        if not self.state.notes:
            return [NoteBlock(content="[No notes yet]", operation_type="placeholder", turn=current_turn)]
        else:
            for note in self.state.notes:
                note.turn = current_turn
            return self.state.notes
    
    @notification
    def utilization_warning(self) -> str:
        if self.state.utilization > 90:
            return "⚠️ Internal notes are nearing capacity! Consider compressing or replacing them."
        elif self.state.utilization > 80:
            return "🚨 Internal notes are at 80% capacity, please compress or replace them."
        return ""

    @operation
    def append(self, content: str) -> StateOperatorResult:
        """
        Append content as new NoteBlock.
        
        Args:
            content: Content to append to notes
        """
        if not content or not content.strip():
            return StateOperatorResult(
                message="Cannot append empty content",
                success=False
            )
        
        current_turn = self.agent.context.cad if self.agent and self.agent.context else None
        new_note = NoteBlock(content=content.strip(), operation_type="append", turn=current_turn)
        
        prospective_notes = self.state.notes + [new_note]
        prospective_content = "\n".join(note.content for note in prospective_notes)
        prospective_tokens = self.count_tokens(prospective_content)
        max_tokens = self.get_token_limit()
        
        if prospective_tokens > max_tokens:
            current_content = "\n".join(note.content for note in self.state.notes)
            current_tokens = self.count_tokens(current_content)
            return StateOperatorResult(
                message=(
                    f"ERROR: Cannot append - would exceed {max_tokens} token limit! "
                    f"Current: {current_tokens}, "
                    f"New content: {prospective_tokens - current_tokens} tokens. "
                    f"Consider using 'update' to replace/compress existing notes."
                ),
                success=False
            )
        
        self.state.notes.append(new_note)
        return StateOperatorResult(message="Added to notes")
    
    @operation
    def update(self, content: str) -> StateOperatorResult:
        """
        Replace all notes with single new NoteBlock.
        
        Args:
            content: New content to replace all notes
        """
        if not content or not content.strip():
            return StateOperatorResult(
                message="Cannot update with empty content",
                success=False
            )
        
        current_turn = self.agent.context.cad if self.agent and self.agent.context else None
        new_note = NoteBlock(content=content.strip(), operation_type="update", turn=current_turn)
        new_tokens = self.count_tokens(content.strip())
        max_tokens = self.get_token_limit()
        
        if new_tokens > max_tokens:
            return StateOperatorResult(
                message=(
                    f"ERROR: Cannot update - would exceed {max_tokens} token limit! "
                    f"New content has {new_tokens} tokens. "
                    f"Please provide a more concise summary."
                ),
                success=False
            )
        
        old_content = "\n".join(note.content for note in self.state.notes)
        old_tokens = self.count_tokens(old_content)
        compression_ratio = ((old_tokens - new_tokens) / old_tokens) * 100 if old_tokens > 0 else 0
        
        # Automatic change detection - just assign the new notes list
        self.state.notes = [new_note]
        
        if old_tokens > 0:
            return StateOperatorResult(
                message=(
                    f"Updated notes (compressed by {compression_ratio:.0f}%: "
                    f"{old_tokens} → {new_tokens} tokens)"
                )
            )
        else:
            return StateOperatorResult(message=f"Notes updated ({new_tokens} tokens)")