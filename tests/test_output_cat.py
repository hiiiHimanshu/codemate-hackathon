import os

from core.session import SessionContext


def test_cat_truncates_large_file(workspace):
    from fs.ops import cat_handler
    from fs import paths as paths_mod

    os.chdir(paths_mod.WORKSPACE_ROOT)
    ctx = SessionContext(cwd=paths_mod.WORKSPACE_ROOT)
    large_file = workspace / "huge.txt"
    large_file.write_text("A" * 15000)

    output = cat_handler(ctx, ["huge.txt"])
    assert "… (truncated)" in output
    assert len(output) <= 10000 + len("… (truncated)")
