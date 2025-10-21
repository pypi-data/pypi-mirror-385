"""
Formatters utility module for Context Viewer.

Provides shared formatting utilities, box-drawing characters, and styling support.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
import os


class Color(Enum):
    """ANSI color codes for terminal output"""
    # Standard colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    
    # Reset
    RESET = "\033[0m"
    
    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"


class BoxChars:
    """Box-drawing character constants for visual formatting"""
    
    # Single line box characters
    HORIZONTAL = "─"
    VERTICAL = "│"
    TOP_LEFT = "┌"
    TOP_RIGHT = "┐"
    BOTTOM_LEFT = "└"
    BOTTOM_RIGHT = "┘"
    CROSS = "┼"
    T_DOWN = "┬"
    T_UP = "┴"
    T_RIGHT = "├"
    T_LEFT = "┤"
    
    # Double line box characters
    DOUBLE_HORIZONTAL = "═"
    DOUBLE_VERTICAL = "║"
    DOUBLE_TOP_LEFT = "╔"
    DOUBLE_TOP_RIGHT = "╗"
    DOUBLE_BOTTOM_LEFT = "╚"
    DOUBLE_BOTTOM_RIGHT = "╝"
    DOUBLE_CROSS = "╬"
    DOUBLE_T_DOWN = "╦"
    DOUBLE_T_UP = "╩"
    DOUBLE_T_RIGHT = "╠"
    DOUBLE_T_LEFT = "╣"
    
    # Tree characters
    TREE_BRANCH = "├── "
    TREE_LAST_BRANCH = "└── "
    TREE_VERTICAL = "│   "
    TREE_SPACE = "    "
    
    # Heavy box characters
    HEAVY_HORIZONTAL = "━"
    HEAVY_VERTICAL = "┃"
    HEAVY_TOP_LEFT = "┏"
    HEAVY_TOP_RIGHT = "┓"
    HEAVY_BOTTOM_LEFT = "┗"
    HEAVY_BOTTOM_RIGHT = "┛"


class Formatter:
    """Main formatter class with styling and box-drawing utilities"""
    
    def __init__(self, use_colors: bool = None):
        """Initialize formatter
        
        Args:
            use_colors: Enable color output. If None, auto-detect based on terminal
        """
        if use_colors is None:
            # Auto-detect color support
            self.use_colors = self._supports_color()
        else:
            self.use_colors = use_colors
    
    def _supports_color(self) -> bool:
        """Check if terminal supports color output"""
        # Check common environment variables that indicate color support
        term = os.environ.get('TERM', '').lower()
        colorterm = os.environ.get('COLORTERM', '').lower()
        
        # Common terminals that support color
        color_terms = ['xterm', 'xterm-color', 'xterm-256color', 'screen', 'tmux']
        
        if any(ct in term for ct in color_terms):
            return True
        
        if colorterm in ['truecolor', '24bit']:
            return True
        
        # Check if NO_COLOR environment variable is set (respects user preference)
        if os.environ.get('NO_COLOR'):
            return False
        
        # Default to color support for modern terminals
        return True
    
    def colorize(self, text: str, color: Color) -> str:
        """Apply color to text
        
        Args:
            text: Text to colorize
            color: Color to apply
            
        Returns:
            Colored text (or plain text if colors disabled)
        """
        if not self.use_colors:
            return text
        
        return f"{color.value}{text}{Color.RESET.value}"
    
    def bold(self, text: str) -> str:
        """Make text bold"""
        return self.colorize(text, Color.BOLD) if self.use_colors else text
    
    def dim(self, text: str) -> str:
        """Make text dim/faded"""
        return self.colorize(text, Color.DIM) if self.use_colors else text
    
    def italic(self, text: str) -> str:
        """Make text italic"""
        return self.colorize(text, Color.ITALIC) if self.use_colors else text
    
    def underline(self, text: str) -> str:
        """Underline text"""
        return self.colorize(text, Color.UNDERLINE) if self.use_colors else text
    
    def success(self, text: str) -> str:
        """Format success message (green)"""
        return self.colorize(text, Color.GREEN)
    
    def error(self, text: str) -> str:
        """Format error message (red)"""
        return self.colorize(text, Color.RED)
    
    def warning(self, text: str) -> str:
        """Format warning message (yellow)"""
        return self.colorize(text, Color.YELLOW)
    
    def info(self, text: str) -> str:
        """Format info message (blue)"""
        return self.colorize(text, Color.BLUE)
    
    def highlight(self, text: str) -> str:
        """Highlight text (cyan)"""
        return self.colorize(text, Color.CYAN)
    
    def muted(self, text: str) -> str:
        """Muted text (bright black/gray)"""
        return self.colorize(text, Color.BRIGHT_BLACK)


class BoxFormatter:
    """Specialized formatter for box-drawing and containers"""
    
    def __init__(self, formatter: Optional[Formatter] = None):
        """Initialize with optional formatter for styling"""
        self.formatter = formatter or Formatter()
    
    def create_box(
        self, 
        content: str, 
        title: Optional[str] = None,
        width: Optional[int] = None,
        style: str = "single",
        padding: int = 1
    ) -> str:
        """Create a box around content
        
        Args:
            content: Content to box
            title: Optional title for the box
            width: Box width (auto-calculated if None)
            style: Box style ("single", "double", "heavy")
            padding: Internal padding
            
        Returns:
            Formatted box string
        """
        lines = content.split('\n')
        
        # Determine box characters based on style
        if style == "double":
            h_char = BoxChars.DOUBLE_HORIZONTAL
            v_char = BoxChars.DOUBLE_VERTICAL
            tl_char = BoxChars.DOUBLE_TOP_LEFT
            tr_char = BoxChars.DOUBLE_TOP_RIGHT
            bl_char = BoxChars.DOUBLE_BOTTOM_LEFT
            br_char = BoxChars.DOUBLE_BOTTOM_RIGHT
        elif style == "heavy":
            h_char = BoxChars.HEAVY_HORIZONTAL
            v_char = BoxChars.HEAVY_VERTICAL
            tl_char = BoxChars.HEAVY_TOP_LEFT
            tr_char = BoxChars.HEAVY_TOP_RIGHT
            bl_char = BoxChars.HEAVY_BOTTOM_LEFT
            br_char = BoxChars.HEAVY_BOTTOM_RIGHT
        else:  # single
            h_char = BoxChars.HORIZONTAL
            v_char = BoxChars.VERTICAL
            tl_char = BoxChars.TOP_LEFT
            tr_char = BoxChars.TOP_RIGHT
            bl_char = BoxChars.BOTTOM_LEFT
            br_char = BoxChars.BOTTOM_RIGHT
        
        # Calculate width
        if width is None:
            content_width = max(len(line) for line in lines) if lines else 0
            title_width = len(title) if title else 0
            width = max(content_width, title_width) + (padding * 2) + 2
        
        # Create box
        result = []
        
        # Top border with optional title
        if title:
            title_line = f"{tl_char}{h_char} {title} "
            remaining = width - len(title_line) - 1
            title_line += h_char * remaining + tr_char
            result.append(title_line)
        else:
            result.append(tl_char + h_char * (width - 2) + tr_char)
        
        # Content lines
        padding_str = " " * padding
        for line in lines:
            padded_line = f"{v_char}{padding_str}{line}"
            # Pad to width
            remaining = width - len(padded_line) - 1
            padded_line += " " * remaining + v_char
            result.append(padded_line)
        
        # Bottom border
        result.append(bl_char + h_char * (width - 2) + br_char)
        
        return '\n'.join(result)
    
    def create_separator(self, width: int, char: str = None, title: Optional[str] = None) -> str:
        """Create a horizontal separator line
        
        Args:
            width: Width of separator
            char: Character to use (defaults to horizontal line)
            title: Optional title in the middle
            
        Returns:
            Separator string
        """
        if char is None:
            char = BoxChars.HORIZONTAL
        
        if title:
            title_text = f" {title} "
            if len(title_text) >= width:
                return title_text[:width]
            
            # Center the title
            remaining = width - len(title_text)
            left_chars = remaining // 2
            right_chars = remaining - left_chars
            
            return char * left_chars + title_text + char * right_chars
        else:
            return char * width
    
    def indent_block(self, content: str, level: int = 1, char: str = "  ") -> str:
        """Indent a block of text
        
        Args:
            content: Content to indent
            level: Indentation level
            char: Character(s) to use for indentation
            
        Returns:
            Indented content
        """
        indent = char * level
        lines = content.split('\n')
        return '\n'.join(indent + line for line in lines)


class TableFormatter:
    """Formatter for table-like output"""
    
    def __init__(self, formatter: Optional[Formatter] = None):
        """Initialize with optional formatter for styling"""
        self.formatter = formatter or Formatter()
    
    def format_table(
        self, 
        headers: List[str], 
        rows: List[List[str]], 
        style: str = "single"
    ) -> str:
        """Format data as a table
        
        Args:
            headers: Column headers
            rows: Table rows
            style: Border style ("single", "double", "simple")
            
        Returns:
            Formatted table string
        """
        if not headers or not rows:
            return ""
        
        # Calculate column widths
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Choose border characters
        if style == "double":
            h_char = BoxChars.DOUBLE_HORIZONTAL
            v_char = BoxChars.DOUBLE_VERTICAL
            cross_char = BoxChars.DOUBLE_CROSS
        elif style == "simple":
            h_char = "-"
            v_char = "|"
            cross_char = "+"
        else:  # single
            h_char = BoxChars.HORIZONTAL
            v_char = BoxChars.VERTICAL
            cross_char = BoxChars.CROSS
        
        # Build table
        result = []
        
        # Top border
        border_parts = [h_char * (width + 2) for width in col_widths]
        top_border = cross_char.join(border_parts)
        result.append(top_border)
        
        # Header row
        header_cells = [f" {header:<{width}} " for header, width in zip(headers, col_widths)]
        header_row = v_char.join(header_cells)
        result.append(header_row)
        
        # Header separator
        result.append(top_border)
        
        # Data rows
        for row in rows:
            row_cells = []
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    row_cells.append(f" {str(cell):<{col_widths[i]}} ")
                else:
                    row_cells.append(f" {str(cell)} ")
            
            data_row = v_char.join(row_cells)
            result.append(data_row)
        
        # Bottom border
        result.append(top_border)
        
        return '\n'.join(result)
    
    def format_key_value_pairs(
        self, 
        pairs: Dict[str, Any], 
        title: Optional[str] = None
    ) -> str:
        """Format key-value pairs
        
        Args:
            pairs: Dictionary of key-value pairs
            title: Optional title
            
        Returns:
            Formatted key-value string
        """
        if not pairs:
            return ""
        
        # Calculate max key width
        max_key_width = max(len(str(key)) for key in pairs.keys())
        
        lines = []
        if title:
            lines.append(self.formatter.bold(title))
            lines.append("")
        
        for key, value in pairs.items():
            formatted_key = self.formatter.highlight(f"{key}:")
            padded_key = f"{formatted_key:<{max_key_width + 10}}"  # +10 for ANSI codes
            lines.append(f"{padded_key} {value}")
        
        return '\n'.join(lines)


# Convenience instances
default_formatter = Formatter()
box_formatter = BoxFormatter(default_formatter)
table_formatter = TableFormatter(default_formatter)


# Convenience functions
def colorize(text: str, color: Color) -> str:
    """Convenience function for colorizing text"""
    return default_formatter.colorize(text, color)


def create_box(content: str, title: Optional[str] = None, **kwargs) -> str:
    """Convenience function for creating boxes"""
    return box_formatter.create_box(content, title, **kwargs)


def create_separator(width: int, char: str = None, title: Optional[str] = None) -> str:
    """Convenience function for creating separators"""
    return box_formatter.create_separator(width, char, title)


def format_table(headers: List[str], rows: List[List[str]], **kwargs) -> str:
    """Convenience function for formatting tables"""
    return table_formatter.format_table(headers, rows, **kwargs)


def success(text: str) -> str:
    """Convenience function for success messages"""
    return default_formatter.success(text)


def error(text: str) -> str:
    """Convenience function for error messages"""
    return default_formatter.error(text)


def warning(text: str) -> str:
    """Convenience function for warning messages"""
    return default_formatter.warning(text)


def info(text: str) -> str:
    """Convenience function for info messages"""
    return default_formatter.info(text)


def highlight(text: str) -> str:
    """Convenience function for highlighting text"""
    return default_formatter.highlight(text)