"""
Minimal rule-based NL parser for mapping English instructions to commands.
"""

import re
from typing import List, Optional, Tuple

from ui.render import emit_stdout, emit_stderr
from core.registry import CommandRegistry
from fs.ops import (
    pwd_handler, cd_handler, ls_handler, mkdir_handler,
    rm_handler, mv_handler, cp_handler, touch_handler, cat_handler
)


class NLParser:
    """Rule-based parser for natural language commands."""
    
    def __init__(self):
        """Initialize the NL parser with regex rules."""
        self.rules = [
            # Create folder rule
            (
                re.compile(r"create (?:a|new) folder (?:called|named) (?P<name>\S+)", re.IGNORECASE),
                lambda match: ["mkdir " + match.group('name')]
            ),
            # Move rule
            (
                re.compile(r"move (?P<src>\S+) (?:to|into) (?P<dst>\S+)", re.IGNORECASE),
                lambda match: ["mv " + match.group('src') + " " + match.group('dst') + "/"]
            ),
            # List files rule
            (
                re.compile(r"list (?:files|everything)(?: in (?P<path>\S+))?", re.IGNORECASE),
                lambda match: ["ls " + (match.group('path') if match.group('path') else "")]
            ),
            # Show file rule
            (
                re.compile(r"show (?P<file>\S+)", re.IGNORECASE),
                lambda match: ["cat " + match.group('file')]
            )
        ]
    
    def classify_as_nl(self, input_str: str) -> bool:
        """
        Heuristic to determine if input should be parsed as NL.
        
        Args:
            input_str: Input string to classify
            
        Returns:
            True if input appears to be natural language, False otherwise
        """
        # Common verbs that indicate NL input (not commands)
        nl_verbs = ['create', 'move', 'list', 'show', 'delete', 'remove', 'copy', 'find']
        
        # Check if input contains NL verbs and doesn't start with a known command
        input_lower = input_str.lower().strip()
        
        # If it starts with a known command, it's likely not NL
        registry = CommandRegistry()
        registry.register("pwd", pwd_handler, "Print working directory", [])
        registry.register("cd", cd_handler, "Change directory", ["path"])
        registry.register("ls", ls_handler, "List directory contents", ["path", "--all"])
        registry.register("mkdir", mkdir_handler, "Create directory", ["name"])
        registry.register("rm", rm_handler, "Remove file or directory", ["path", "-r"])
        registry.register("mv", mv_handler, "Move/rename file or directory", ["src", "dst"])
        registry.register("cp", cp_handler, "Copy file or directory", ["src", "dst", "-r"])
        registry.register("touch", touch_handler, "Create empty file", ["file"])
        registry.register("cat", cat_handler, "Display file contents", ["file"])
        
        commands = registry.list_commands()
        
        # If input starts with a command, it's not NL
        if input_lower.split()[0] in commands:
            return False
            
        # If input contains NL verbs, it's likely NL
        for verb in nl_verbs:
            if verb in input_lower:
                return True
                
        return False
    
    def parse(self, input_str: str) -> Optional[List[str]]:
        """
        Parse natural language input into command plan.
        
        Args:
            input_str: Natural language input
            
        Returns:
            List of commands to execute, or None if no rule matches
        """
        input_lower = input_str.lower().strip()
        
        for pattern, action in self.rules:
            match = pattern.search(input_str)
            if match:
                return action(match)
        
        return None


def execute_plan(commands: List[str], router, cwd: str, history: List[str], 
                scrollback: List[str]) -> Tuple[int, str, str]:
    """
    Execute a plan of commands sequentially and collect results.
    
    Args:
        commands: List of commands to execute
        router: Command router instance
        cwd: Current working directory
        history: Command history
        scrollback: Output scrollback
        
    Returns:
        Tuple of (final_status, stdout, stderr)
    """
    final_status = "ok"
    stdout_chunks: List[str] = []
    stderr_chunks: List[str] = []
    
    for command in commands:
        try:
            # Execute command
            response = router.execute(command)
            
            # Collect output
            if response.stdout:
                block = emit_stdout(response.stdout)
                if block:
                    scrollback.append(block)
                stdout_chunks.append(response.stdout.rstrip())

            if response.stderr:
                block = emit_stderr(response.stderr)
                if block:
                    scrollback.append(block)
                stderr_chunks.append(response.stderr.rstrip())

            if response.status != "ok":
                final_status = response.status
                
        except Exception as e:
            error_msg = f"Error executing command '{command}': {str(e)}"
            error_block = emit_stderr(error_msg)
            if error_block:
                scrollback.append(error_block)
            stderr_chunks.append(error_msg.rstrip())
            final_status = "error"
            break

    stdout = "\n".join(chunk for chunk in stdout_chunks if chunk).rstrip()
    stderr = "\n".join(chunk for chunk in stderr_chunks if chunk).rstrip()
    return final_status, stdout, stderr


# Global parser instance
parser = NLParser()


def parse_and_execute(input_str: str, router, cwd: str, history: List[str], 
                      scrollback: List[str]) -> Tuple[int, str, str]:
    """
    Parse natural language input and execute the resulting plan.
    
    Args:
        input_str: Input string to parse
        router: Command router instance
        cwd: Current working directory
        history: Command history
        scrollback: Output scrollback
        
    Returns:
        Tuple of (final_status, stdout, stderr)
    """
    # Check if input should be treated as NL
    if parser.classify_as_nl(input_str):
        # Try to parse as NL
        plan = parser.parse(input_str)
        if plan:
            # Execute the plan
            return execute_plan(plan, router, cwd, history, scrollback)
    
    # If not NL or no plan found, return None to indicate normal processing
    return None, "", ""
