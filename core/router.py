"""Command routing for the Streamlit terminal."""

from __future__ import annotations

import shlex
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from core.errors import AboveRootError, RootEscapeError, CommandError
from core.registry import CommandRegistry
from core.session import SessionContext


@dataclass
class Response:
    stdout: str = ""
    stderr: str = ""
    status: str = "ok"
    new_cwd: Optional[Path] = None
    meta: dict = field(default_factory=dict)


class CommandRouter:
    """Parse and route commands to registered handlers."""

    def __init__(self, registry: CommandRegistry, session: SessionContext) -> None:
        self.registry = registry
        self.session = session

    def parse_input(self, input_str: str) -> tuple[str, List[str]]:
        if not input_str.strip():
            return "", []
        tokens = shlex.split(input_str)
        if not tokens:
            return "", []
        return tokens[0], tokens[1:]

    def execute(self, input_str: str) -> Response:
        trimmed = input_str.strip()
        if not trimmed:
            return Response()

        start = time.perf_counter()
        command_name, args = self.parse_input(trimmed)

        if not command_name:
            elapsed = (time.perf_counter() - start) * 1000
            return Response(meta={"exec_ms": elapsed})

        self.session.add_to_history(trimmed)

        for arg in args:
            if arg.startswith("<") and arg.endswith(">"):
                elapsed = (time.perf_counter() - start) * 1000
                return Response(stderr="Missing required argument.", status="error", meta={"exec_ms": elapsed})

        if command_name == "help":
            try:
                stdout = self._handle_help(args)
                status = "ok"
                stderr = ""
            except CommandError as exc:
                stdout = ""
                stderr = str(exc)
                status = "error"
            elapsed = (time.perf_counter() - start) * 1000
            return Response(stdout=stdout, stderr=stderr, status=status, meta={"exec_ms": elapsed})

        if command_name == "history":
            try:
                stdout = self._handle_history(args)
                status = "ok"
                stderr = ""
            except CommandError as exc:
                stdout = ""
                stderr = str(exc)
                status = "error"
            elapsed = (time.perf_counter() - start) * 1000
            return Response(stdout=stdout, stderr=stderr, status=status, meta={"exec_ms": elapsed})

        spec = self.registry.get(command_name)
        if spec is None:
            elapsed = (time.perf_counter() - start) * 1000
            return Response(
                stderr="Command not found. Try `help`.",
                status="error",
                meta={"exec_ms": elapsed},
            )

        ctx = self.session

        try:
            output = spec.handler(ctx, args)
            stdout = output or ""
            elapsed = (time.perf_counter() - start) * 1000
            return Response(stdout=stdout, status="ok", new_cwd=ctx.cwd, meta={"exec_ms": elapsed})
        except RootEscapeError:
            elapsed = (time.perf_counter() - start) * 1000
            return Response(stderr="Access denied: path escapes workspace root.", status="error", meta={"exec_ms": elapsed})
        except AboveRootError:
            elapsed = (time.perf_counter() - start) * 1000
            return Response(stderr="Cannot navigate above workspace root.", status="error", meta={"exec_ms": elapsed})
        except FileNotFoundError as exc:
            filename = getattr(exc, "filename", None) or (exc.args[0] if exc.args else "file")
            filename_str = Path(filename).name if isinstance(filename, (Path, str)) else str(filename)
            elapsed = (time.perf_counter() - start) * 1000
            return Response(stderr=f"File not found: {filename_str}", status="error", meta={"exec_ms": elapsed})
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            return Response(stderr=str(exc), status="error", meta={"exec_ms": elapsed})

    def _handle_help(self, args: List[str]) -> str:
        if not args:
            lines = ["Available commands:"]
            for name in self.registry.list_commands():
                spec = self.registry.get(name)
                if spec:
                    lines.append(f"  {name}: {spec.description}")
            return "\n".join(lines).rstrip()

        command_name = args[0]
        spec = self.registry.get(command_name)
        if not spec:
            raise CommandError("Command not found. Try `help`.")

        description = spec.description
        if not isinstance(description, str):
            description = " ".join(description)
        return "\n".join([f"Usage: {spec.usage}", description])

    def _handle_history(self, args: List[str]) -> str:
        if args:
            raise CommandError("History command takes no arguments.")

        if not self.session.history:
            return "No command history."

        lines = [f"{idx + 1}  {cmd}" for idx, cmd in enumerate(self.session.history)]
        return "\n".join(lines)
