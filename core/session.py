"""
Session management for command execution context.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class SessionContext:
    """Context for a command execution session."""
    cwd: Path = Path(".").resolve()
    history: List[str] = field(default_factory=list)
    
    def add_to_history(self, command: str) -> None:
        """
        Add a command to the session history.
        
        Args:
            command: Command string to add to history
        """
        token = command.strip()
        if not token:
            return
        self.history.append(token)
        if len(self.history) > 50:
            del self.history[:-50]
