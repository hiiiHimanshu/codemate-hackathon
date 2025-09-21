"""Workspace-aware path helpers."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Union

from core.errors import RootEscapeError

__all__ = ["WORKSPACE_ROOT", "resolve_in_root", "is_within_workspace"]

_env_root = os.getenv("WORKSPACE_ROOT", "./workspace")
_root = Path(_env_root).expanduser()
if not _root.is_absolute():
    _root = (Path.cwd() / _root).resolve()

WORKSPACE_ROOT: Path = _root
WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)


def _coerce(path: Union[str, Path]) -> Path:
    return path if isinstance(path, Path) else Path(path).expanduser()


def resolve_in_root(raw: Union[str, Path], cwd: Path) -> Path:
    """Resolve *raw* against *cwd* ensuring the result stays within the workspace."""
    base = (
        cwd.resolve(strict=False)
        if cwd.is_absolute()
        else (WORKSPACE_ROOT / cwd).resolve(strict=False)
    )

    candidate = _coerce(raw)
    resolved = (
        candidate.resolve(strict=False)
        if candidate.is_absolute()
        else (base / candidate).resolve(strict=False)
    )

    try:
        resolved.relative_to(WORKSPACE_ROOT)
    except ValueError as exc:
        raise RootEscapeError("Access denied: path escapes workspace root.") from exc

    return resolved


def is_within_workspace(path: Union[str, Path]) -> bool:
    try:
        resolve_in_root(path, WORKSPACE_ROOT)
        return True
    except RootEscapeError:
        return False
