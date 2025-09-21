import os

import pytest

from core.registry import create_default_registry
from core.router import CommandRouter
from core.session import SessionContext


def make_router(workspace_root) -> CommandRouter:
    return CommandRouter(create_default_registry(), SessionContext(cwd=workspace_root))


def test_path_escape_error(workspace):
    from fs import paths as paths_mod

    router = make_router(paths_mod.WORKSPACE_ROOT)
    response = router.execute("ls ../outside")
    assert response.status == "error"
    assert response.stderr == "Access denied: path escapes workspace root."


def test_rm_non_empty_directory_error(workspace):
    from fs import paths as paths_mod

    (paths_mod.WORKSPACE_ROOT / "data").mkdir()
    (paths_mod.WORKSPACE_ROOT / "data" / "file.txt").write_text("content")
    router = make_router(paths_mod.WORKSPACE_ROOT)
    response = router.execute("rm data")
    assert response.status == "error"
    assert response.stderr == "Directory not empty. Use -r to remove directories recursively."


def test_cat_missing_file_error(workspace):
    from fs import paths as paths_mod

    router = make_router(paths_mod.WORKSPACE_ROOT)
    response = router.execute("cat missing.txt")
    assert response.status == "error"
    assert response.stderr == "File not found: missing.txt"
