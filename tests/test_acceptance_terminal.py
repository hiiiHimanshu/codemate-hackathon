import os
from pathlib import Path

import pytest

from core.registry import create_default_registry
from core.router import CommandRouter
from core.session import SessionContext


@pytest.fixture
def terminal(workspace):
    from fs import paths as paths_mod

    registry = create_default_registry()
    session = SessionContext(cwd=paths_mod.WORKSPACE_ROOT)
    return CommandRouter(registry, session)


def run(router: CommandRouter, command: str):
    response = router.execute(command)
    return response.stdout, response.stderr, response.status


def test_acceptance_script(terminal):
    from fs import paths as paths_mod

    router = terminal
    root = str(paths_mod.WORKSPACE_ROOT)
    outputs = []

    commands = [
        "pwd",
        "ls",
        "mkdir testlab",
        "cd testlab",
        "pwd",
        "touch a.txt",
        "mkdir data",
        "ls",
        "mv a.txt data/",
        "ls",
        "ls data",
        "cp -r data data_copy",
        "ls",
        "rm data",
        "rm -r data",
        "ls",
        "touch .gitignore",
        "ls",
        "ls --all",
        "history",
        "help rm",
        f"cd {root}",
        "cd ..",
        "ls ../",
        "cpu",
        "mem",
        "disk",
        "ps --top 5",
    ]

    for cmd in commands:
        stdout, stderr, status = run(router, cmd)
        outputs.append((cmd, stdout, stderr, status))

    # 1 pwd
    assert outputs[0][1] == root

    # 2 ls empty
    assert outputs[1][1] == ""

    # 5 pwd after cd
    assert outputs[4][1] == f"{root}/testlab"

    # 8 ls showing files
    assert outputs[7][1] == "a.txt\ndata/"

    # 10 ls after move
    assert outputs[9][1] == "data/"

    # 11 ls data
    assert outputs[10][1] == "a.txt"

    # 13 ls after copy
    assert outputs[12][1] == "data/\ndata_copy/"

    # 14 rm data error
    assert outputs[13][2] == "Directory not empty. Use -r to remove directories recursively."

    # 16 ls after removing data
    assert outputs[15][1] == "data_copy/"

    # 18 ls hides dotfiles
    assert outputs[17][1] == "data_copy/"

    # 19 ls --all shows hidden
    assert outputs[18][1] == ".gitignore\ndata_copy/"

    # 20 history format
    history_lines = outputs[19][1].splitlines()
    history_index = commands.index("history")
    assert history_lines[0] == "1  pwd"
    assert history_lines[1] == "2  ls"
    assert history_lines[2] == "3  mkdir testlab"
    assert history_lines[history_index] == f"{history_index + 1}  history"
    assert len(history_lines) == history_index + 1

    # 21 help rm
    assert outputs[20][1] == (
        "Usage: rm <path> [-r]\n"
        "Removes a file. Use -r to remove directories recursively. This action cannot be undone."
    )

    # 23 cd .. error
    assert outputs[22][2] == "Cannot navigate above workspace root."

    # 24 ls ../ error
    assert outputs[23][2] == "Access denied: path escapes workspace root."

    # 25-27 monitor commands contain labels
    assert outputs[24][1].startswith("CPU: ")
    assert outputs[25][1].startswith("Memory: ")
    assert outputs[26][1].startswith("Disk: ")

    # 28 ps table header
    ps_output = outputs[27][1]
    assert ps_output.splitlines()[0].startswith("PID")
