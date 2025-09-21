import os

from core.registry import CommandRegistry
from core.router import CommandRouter
from core.session import SessionContext
from fs.paths import WORKSPACE_ROOT


def test_history_numbering(workspace):
    os.chdir(WORKSPACE_ROOT)
    session = SessionContext(cwd=str(WORKSPACE_ROOT), history=["ls", "pwd"])
    router = CommandRouter(CommandRegistry(), session)

    response = router.execute("history")

    expected = "1  ls\n2  pwd\n3  history"
    assert response.status == "ok"
    assert response.stdout == expected
    assert response.stdout == expected
