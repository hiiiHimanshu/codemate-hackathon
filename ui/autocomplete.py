"""
Autocomplete and history functionality for the terminal UI.
"""

import streamlit as st
from pathlib import Path
from typing import List, Dict, Any
from core.registry import CommandRegistry
from fs.ops import (
    pwd_handler, cd_handler, ls_handler, mkdir_handler,
    rm_handler, mv_handler, cp_handler, touch_handler, cat_handler
)


def get_command_suggestions(command: str, registry: CommandRegistry, cwd: Path) -> List[str]:
    """
    Get command suggestions based on input.
    
    Args:
        command: Current command input
        registry: Command registry
        cwd: Current working directory
        
    Returns:
        List of command suggestions
    """
    suggestions = []
    
    # Split command into tokens
    tokens = command.strip().split()
    
    if len(tokens) == 0:
        # No tokens - suggest all commands
        commands = registry.list_commands()
        suggestions.extend(commands)
    elif len(tokens) == 1:
        # Single token - partial match commands
        first_token = tokens[0]
        commands = registry.list_commands()
        matching_commands = [cmd for cmd in commands if cmd.startswith(first_token)]
        suggestions.extend(matching_commands[:5])  # Top 5 suggestions
    else:
        # Multiple tokens - suggest filesystem entries for current argument
        # Get the last token (current argument being typed)
        current_arg = tokens[-1] if tokens[-1] else ""
        
        # Determine if we're suggesting for a path
        if len(tokens) >= 2:
            # Check if the command supports path arguments
            command_name = tokens[0]
            if command_name in ['cd', 'ls', 'rm', 'mv', 'cp', 'cat']:
                # Get the path to complete
                path_to_complete = current_arg
                
                # If path starts with '/', use absolute path, otherwise relative to cwd
                if path_to_complete.startswith('/'):
                    target_path = Path(path_to_complete)
                else:
                    target_path = cwd / path_to_complete
                
                # Try to resolve the path
                try:
                    if target_path.exists():
                        # If it's a directory, list its contents
                        if target_path.is_dir():
                            # Get directory contents
                            contents = []
                            for item in target_path.iterdir():
                                if item.is_dir():
                                    contents.append(f"{item.name}/")
                                else:
                                    contents.append(item.name)
                            # Sort directories first, then files
                            dirs = [c for c in contents if c.endswith('/')]
                            files = [c for c in contents if not c.endswith('/')]
                            suggestions.extend(sorted(dirs) + sorted(files))
                        else:
                            # If it's a file, suggest the file itself
                            suggestions.append(target_path.name)
                except Exception:
                    # If we can't resolve the path, suggest nothing
                    pass
    
    return suggestions


def render_autocomplete_suggestions(command: str, registry: CommandRegistry, cwd: Path, 
                                   key_prefix: str = "auto") -> None:
    """
    Render autocomplete suggestions below the input field.
    
    Args:
        command: Current command input
        registry: Command registry
        cwd: Current working directory
        key_prefix: Prefix for Streamlit component keys
    """
    suggestions = get_command_suggestions(command, registry, cwd)
    
    if suggestions:
        st.write("Suggestions:")
        for i, suggestion in enumerate(suggestions):
            if st.button(suggestion, key=f"{key_prefix}_suggestion_{i}"):
                # This will be handled by the calling function to update the input
                # We'll return the suggestion so the caller can handle it
                return suggestion
    return None


def get_history_suggestions(history: List[str]) -> List[str]:
    """
    Get history suggestions (last 50 commands).
    
    Args:
        history: List of command history
        
    Returns:
        List of history suggestions (latest on top)
    """
    # Return last 50 commands (latest on top)
    return history[-50:] if history else []


def render_history_display(history: List[str]) -> None:
    """
    Render history as a numbered list.
    
    Args:
        history: List of command history
    """
    if history:
        st.subheader("Command History")
        # Display with newest at top
        for i, cmd in enumerate(reversed(history[-50:])):
            st.write(f"{len(history)-i}. {cmd}")
    else:
        st.write("No command history.")


def handle_command_execution(command: str, registry: CommandRegistry, cwd: Path, 
                           history: List[str], scrollback: List[str]) -> Dict[str, Any]:
    """
    Handle command execution with history management.
    
    Args:
        command: Command to execute
        registry: Command registry
        cwd: Current working directory
        history: Command history
        scrollback: Output scrollback
        
    Returns:
        Execution result dictionary
    """
    # Add to history
    history.append(command)
    # Keep only last 50 commands
    if len(history) > 50:
        history = history[-50:]
    
    # Add command to scrollback
    scrollback.append(f"user@host:{cwd}$ {command}")
    
    # Special handling for 'history' command
    if command.strip() == "history":
        # Display history in scrollback
        scrollback.append("Command History:")
        for i, cmd in enumerate(reversed(history[-50:])):
            scrollback.append(f"{len(history)-i}. {cmd}")
        return {
            "status": 0,
            "stdout": "",
            "stderr": "",
            "history": history,
            "scrollback": scrollback
        }
    
    # For other commands, proceed with normal execution
    # (This would normally call the router, but we're keeping this simplified)
    return {
        "status": 0,
        "stdout": "",
        "stderr": "",
        "history": history,
        "scrollback": scrollback
    }
