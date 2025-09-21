"""Filesystem command handlers."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, List

from core.errors import AboveRootError, CommandError, RootEscapeError
from core.session import SessionContext
from fs.paths import WORKSPACE_ROOT, resolve_in_root
from ui.render import truncate

__all__ = [
    "pwd_handler",
    "cd_handler",
    "ls_handler",
    "mkdir_handler",
    "rm_handler",
    "mv_handler",
    "cp_handler",
    "touch_handler",
    "cat_handler",
]


def _check_placeholders(args: Iterable[str]) -> None:
    for arg in args:
        if arg and arg.startswith("<") and arg.endswith(">"):
            raise ValueError("Missing required argument.")


def pwd_handler(ctx: SessionContext, args: List[str]) -> str:
    _check_placeholders(args)
    return str(ctx.cwd.resolve())


def cd_handler(ctx: SessionContext, args: List[str]) -> str:
    if not args:
        raise ValueError("Missing required argument.")
    _check_placeholders(args)
    try:
        target = resolve_in_root(args[0], ctx.cwd)
    except RootEscapeError as exc:
        raise AboveRootError("Cannot navigate above workspace root.") from exc
    if not target.exists():
        raise FileNotFoundError(target)
    if not target.is_dir():
        raise NotADirectoryError(target)
    ctx.cwd = target
    return ""


def ls_handler(ctx: SessionContext, args: List[str]) -> str:
    _check_placeholders(args)
    show_all = False
    target_arg = None
    for arg in args:
        if arg in {"--all", "-a"}:
            show_all = True
        elif target_arg is None:
            target_arg = arg
        else:
            raise ValueError("Too many arguments.")

    target = resolve_in_root(target_arg or ".", ctx.cwd)
    if not target.exists():
        raise FileNotFoundError(target)
    if not target.is_dir():
        raise NotADirectoryError(target)

    entries: List[str] = []
    for item in sorted(target.iterdir(), key=lambda p: p.name.lower()):
        if not show_all and item.name.startswith("."):
            continue
        name = f"{item.name}/" if item.is_dir() else item.name
        entries.append(name)

    return "\n".join(entries)


def mkdir_handler(ctx: SessionContext, args: List[str]) -> str:
    if not args:
        raise ValueError("Missing required argument.")
    _check_placeholders(args)
    target = resolve_in_root(args[0], ctx.cwd)
    target.mkdir(parents=True, exist_ok=False)
    return ""


def rm_handler(ctx: SessionContext, args: List[str]) -> str:
    _check_placeholders(args)
    recursive = False
    target_arg = None
    for arg in args:
        if arg in {"-r", "--recursive"}:
            recursive = True
        elif target_arg is None:
            target_arg = arg
        else:
            raise ValueError("Too many arguments.")

    if target_arg is None:
        raise ValueError("Missing required argument.")

    target = resolve_in_root(target_arg, ctx.cwd)
    if not target.exists():
        raise FileNotFoundError(target)

    if target.is_dir():
        if recursive:
            shutil.rmtree(target)
        else:
            if any(target.iterdir()):
                raise CommandError("Directory not empty. Use -r to remove directories recursively.")
            target.rmdir()
    else:
        target.unlink()
    return ""


def mv_handler(ctx: SessionContext, args: List[str]) -> str:
    _check_placeholders(args)
    if len(args) != 2:
        raise ValueError("Usage: mv <src> <dst>")

    src = resolve_in_root(args[0], ctx.cwd)
    if not src.exists():
        raise FileNotFoundError(src)

    dst = resolve_in_root(args[1], ctx.cwd)
    destination = dst / src.name if dst.exists() and dst.is_dir() else dst
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(destination))
    return ""


def cp_handler(ctx: SessionContext, args: List[str]) -> str:
    _check_placeholders(args)
    recursive = False
    positional: List[str] = []
    for arg in args:
        if arg in {"-r", "--recursive"}:
            recursive = True
        else:
            positional.append(arg)

    if len(positional) != 2:
        raise ValueError("Usage: cp <src> <dst> [-r]")

    src_path = resolve_in_root(positional[0], ctx.cwd)
    if not src_path.exists():
        raise FileNotFoundError(src_path)

    dst_path = resolve_in_root(positional[1], ctx.cwd)
    if src_path.is_dir():
        if not recursive:
            raise CommandError("Use -r to copy directories recursively.")
        shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
    else:
        if dst_path.exists() and dst_path.is_dir():
            dst_path = dst_path / src_path.name
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
    return ""


def touch_handler(ctx: SessionContext, args: List[str]) -> str:
    if not args:
        raise ValueError("Missing required argument.")
    _check_placeholders(args)
    target = resolve_in_root(args[0], ctx.cwd)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.touch(exist_ok=True)
    return ""


def cat_handler(ctx: SessionContext, args: List[str]) -> str:
    if not args:
        raise ValueError("Missing required argument.")
    _check_placeholders(args)
    target = resolve_in_root(args[0], ctx.cwd)
    if not target.exists():
        raise FileNotFoundError(target)
    if not target.is_file():
        raise CommandError(f"Not a file: {target}")

    text = target.read_text(encoding="utf-8")
    return truncate(text)
