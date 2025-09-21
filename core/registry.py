"""Command registry used by the terminal router."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional

from core.errors import CommandError
from core.session import SessionContext


@dataclass(frozen=True)
class CommandSpec:
    """Specification for a command handler."""

    handler: Callable[[SessionContext, List[str]], str]
    usage: str
    description: str


class CommandRegistry:
    """Maintain a mapping between command names and handlers."""

    def __init__(self) -> None:
        self._commands: Dict[str, CommandSpec] = {}

    def register(self, name: str, handler: Callable[..., dict], usage: str, description: str) -> None:
        self._commands[name] = CommandSpec(handler, usage, description)

    def get(self, name: str) -> Optional[CommandSpec]:
        return self._commands.get(name)

    def list_commands(self) -> List[str]:
        return sorted(self._commands.keys())

    def __contains__(self, name: str) -> bool:  # pragma: no cover - helper
        return name in self._commands


def create_default_registry() -> CommandRegistry:
    """Create a registry populated with built-in commands."""
    from fs import ops as fs_ops
    from monitor import stats as monitor_stats

    registry = CommandRegistry()

    registry.register("pwd", fs_ops.pwd_handler, "pwd", "Print the current working directory.")
    registry.register("cd", fs_ops.cd_handler, "cd <path>", "Change into a directory within the workspace.")
    registry.register("ls", fs_ops.ls_handler, "ls [path] [--all]", "List directory contents.")
    registry.register("mkdir", fs_ops.mkdir_handler, "mkdir <name>", "Create a directory.")
    registry.register(
        "rm",
        fs_ops.rm_handler,
        "rm <path> [-r]",
        "Removes a file. Use -r to remove directories recursively. This action cannot be undone.",
    )
    registry.register("mv", fs_ops.mv_handler, "mv <src> <dst>", "Move or rename files and directories.")
    registry.register("cp", fs_ops.cp_handler, "cp <src> <dst> [-r]", "Copy files and directories.")
    registry.register("touch", fs_ops.touch_handler, "touch <file>", "Create an empty file or update its timestamp.")
    registry.register("cat", fs_ops.cat_handler, "cat <file>", "Show the contents of a file (truncated).")

    def cpu_handler(ctx, args):
        return monitor_stats.cpu()

    def mem_handler(ctx, args):
        return monitor_stats.mem()

    def disk_handler(ctx, args):
        return monitor_stats.disk()

    def ps_handler(ctx, args):
        top = 5
        if args:
            if args[0] in {"--top", "-n"}:
                if len(args) < 2:
                    raise CommandError("Usage: ps [--top <n>]")
                try:
                    top = max(1, int(args[1]))
                except ValueError as exc:
                    raise CommandError("Usage: ps [--top <n>]") from exc
            elif args[0].isdigit():
                top = max(1, int(args[0]))
            else:
                raise CommandError("Usage: ps [--top <n>]")
        return monitor_stats.ps(top)

    registry.register("cpu", cpu_handler, "cpu", "Show CPU utilisation.")
    registry.register("mem", mem_handler, "mem", "Show memory utilisation.")
    registry.register("disk", disk_handler, "disk", "Show disk utilisation.")
    registry.register("ps", ps_handler, "ps [--top <n>]", "List top processes by CPU usage.")

    return registry
