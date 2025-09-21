from pathlib import Path

import pytest

from core.errors import RootEscapeError
from fs import paths as paths_mod


def test_resolve_path_within_workspace(workspace):
    target = paths_mod.resolve_in_root("sample.txt", paths_mod.WORKSPACE_ROOT)
    assert target == paths_mod.WORKSPACE_ROOT / "sample.txt"


def test_resolve_absolute_path(workspace):
    absolute = paths_mod.WORKSPACE_ROOT / "file.txt"
    assert paths_mod.resolve_in_root(str(absolute), paths_mod.WORKSPACE_ROOT) == absolute


def test_resolve_path_escape_blocked(workspace):
    with pytest.raises(RootEscapeError):
        paths_mod.resolve_in_root("../outside.txt", paths_mod.WORKSPACE_ROOT)


def test_is_within_workspace(workspace):
    inside = paths_mod.WORKSPACE_ROOT / "item"
    outside = Path("/etc/passwd")
    assert paths_mod.is_within_workspace(inside)
    assert not paths_mod.is_within_workspace(outside)
