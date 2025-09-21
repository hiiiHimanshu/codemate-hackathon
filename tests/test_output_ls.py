import os

from core.session import SessionContext


def test_ls_hides_hidden_and_sorts(workspace):
    from fs.ops import ls_handler
    from fs import paths as paths_mod

    os.chdir(paths_mod.WORKSPACE_ROOT)
    ctx = SessionContext(cwd=paths_mod.WORKSPACE_ROOT)

    visible = workspace / "beta.txt"
    visible.write_text("beta")
    first = workspace / "Alpha"
    first.mkdir()
    hidden = workspace / ".secret"
    hidden.write_text("")

    stdout = ls_handler(ctx, [])
    lines = stdout.splitlines() if stdout else []

    assert lines == ["Alpha/", "beta.txt"]

    stdout_all = ls_handler(ctx, ["--all"])
    all_lines = stdout_all.splitlines() if stdout_all else []
    assert ".secret" in all_lines
    assert "Alpha/" in all_lines
