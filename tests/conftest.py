import importlib
import os
from pathlib import Path

import pytest


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    original_root = os.environ.get("WORKSPACE_ROOT")
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    original_cwd = Path.cwd()

    import fs.paths
    import fs.ops
    import core.registry
    import core.router
    import monitor.stats

    importlib.reload(fs.paths)
    importlib.reload(fs.ops)
    importlib.reload(core.registry)
    importlib.reload(core.router)
    importlib.reload(monitor.stats)

    yield tmp_path

    if original_root is None:
        monkeypatch.delenv("WORKSPACE_ROOT", raising=False)
    else:
        monkeypatch.setenv("WORKSPACE_ROOT", original_root)

    importlib.reload(fs.paths)
    importlib.reload(fs.ops)
    importlib.reload(core.registry)
    importlib.reload(core.router)
    importlib.reload(monitor.stats)
