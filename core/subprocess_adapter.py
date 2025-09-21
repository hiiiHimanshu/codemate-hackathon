"""
Secure subprocess adapter with read-only whitelist and workspace jail.
"""

import subprocess
from pathlib import Path
from typing import List, Optional
from .errors import CommandError
from fs.paths import is_within_workspace, resolve_path


# Whitelist of allowed commands in read-only mode
READONLY_WHITELIST = {
    'whoami', 'date', 'echo', 'uname', 'pwd', 'ls', 'cat', 'head', 'tail',
    'grep', 'find', 'stat', 'basename', 'dirname', 'realpath', 'chmod', 'chown',
    'df', 'du', 'free', 'ps', 'top', 'uptime', 'id', 'groups', 'hostname'
}

# Dangerous commands that should never be allowed
DANGEROUS_COMMANDS = {
    'sudo', 'rm', 'rm -rf', 'curl', 'wget', 'nc', 'netcat', 'python', 'python3',
    'node', 'nodejs', 'bash', 'sh', 'zsh', 'perl', 'ruby', 'php', 'awk', 'sed'
}


def run_secure_command(command: List[str], readonly_mode: bool = False) -> tuple:
    """
    Run a command securely with sandboxing and restrictions.
    
    Args:
        command: Command to execute as a list of arguments
        readonly_mode: If True, enforce read-only restrictions
        
    Returns:
        Tuple of (returncode, stdout, stderr)
        
    Raises:
        CommandError: If command is dangerous or not allowed
    """
    if not command:
        raise CommandError("Empty command")
    
    # Check if command is dangerous
    cmd_name = command[0]
    if cmd_name in DANGEROUS_COMMANDS:
        raise CommandError(f"Dangerous command not allowed: {cmd_name}")
    
    # If in read-only mode, block destructive commands
    if readonly_mode:
        destructive_commands = {'rm', 'mv', 'cp', 'touch'}
        if cmd_name in destructive_commands:
            raise CommandError("Read-only mode enabled. Command not allowed.")
    
    # Check if command is in whitelist (when in read-only mode)
    if readonly_mode and cmd_name not in READONLY_WHITELIST:
        raise CommandError(f"Command not allowed in read-only mode: {cmd_name}")
    
    # Enforce workspace jail for filesystem commands
    if cmd_name in {'ls', 'cat', 'find', 'grep', 'stat', 'chmod', 'chown'}:
        # Validate all path arguments are within workspace
        for arg in command[1:]:
            if arg.startswith('-'):  # Skip flags
                continue
            try:
                path = Path(arg)
                # Resolve the path to check if it's within workspace
                resolved_path = resolve_path(path)
                if not is_within_workspace(resolved_path):
                    raise CommandError(f"Path not within workspace: {arg}")
            except Exception:
                raise CommandError(f"Path not within workspace: {arg}")
    
    # Execute command with shell=False for security
    try:
        result = subprocess.run(
            command,
            shell=False,
            capture_output=True,
            text=True,
            timeout=30  # Prevent hanging
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        raise CommandError("Command timed out")
    except Exception as e:
        raise CommandError(f"Command execution failed: {str(e)}")
