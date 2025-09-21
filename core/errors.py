"""Error hierarchy and mapping helpers for command execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class CommandError(Exception):
    """Base exception for command-related failures."""


class RootEscapeError(CommandError):
    """Raised when a path escapes the workspace root."""


class AboveRootError(CommandError):
    """Raised when attempting to navigate above the workspace root."""


class ArgumentError(CommandError):
    """Raised when command arguments are invalid."""


def map_exception_to_message(exception: Exception) -> str:
    """Translate exceptions into user-facing error strings."""
    if isinstance(exception, CommandError):
        return str(exception)
    if isinstance(exception, FileNotFoundError):
        filename = getattr(exception, "filename", None)
        if not filename and exception.args:
            filename = exception.args[0]
        name = filename.name if hasattr(filename, "name") else filename or "file"
        return f"File not found: {name}"
    if isinstance(exception, PermissionError):
        filename = getattr(exception, "filename", None)
        return f"Permission denied: {filename or exception}".rstrip()
    if isinstance(exception, ValueError):
        return str(exception)
    return "An unexpected error occurred."
