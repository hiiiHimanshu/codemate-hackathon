"""Streamlit UI for the secure terminal and system monitor."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

import streamlit as st

from core.registry import create_default_registry
from core.router import CommandRouter
from core.session import SessionContext

# Initialize workspace root
WORKSPACE_ROOT = Path(os.getenv("WORKSPACE_ROOT", "./workspace")).resolve()
WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
from monitor import stats as monitor_stats
from ui.render import emit_stdout, emit_stderr, format_status


def safe_rerun() -> None:
    """Trigger a rerun using whichever Streamlit API is available."""
    rerun = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if callable(rerun):
        rerun()


def _bootstrap_router() -> CommandRouter:
    registry = create_default_registry()
    session = SessionContext(cwd=WORKSPACE_ROOT)
    return CommandRouter(registry, session)


def init_session_state() -> None:
    if "router" not in st.session_state:
        st.session_state.router = _bootstrap_router()
    if "scrollback" not in st.session_state:
        st.session_state.scrollback = []  # list[tuple[str,str]]
    if "last_exec_time" not in st.session_state:
        st.session_state.last_exec_time = 0.0
    if "last_status" not in st.session_state:
        st.session_state.last_status = 0
    if "command_input" not in st.session_state:
        st.session_state.command_input = ""


def execute_command(command: str) -> Dict[str, str]:
    router: CommandRouter = st.session_state.router
    response = router.execute(command)

    exec_ms = float(response.meta.get("exec_ms", 0.0)) if response.meta else 0.0

    if response.new_cwd is not None:
        router.session.cwd = response.new_cwd

    if response.stderr:
        st.session_state.scrollback.append(("err", response.stderr))
    if response.stdout:
        st.session_state.scrollback.append(("out", response.stdout))

    st.session_state.last_exec_time = exec_ms
    st.session_state.last_status = response.status
    st.session_state.router = router

    return {
        "stdout": response.stdout,
        "stderr": response.stderr,
        "status": response.status,
        "exec_ms": exec_ms,
    }


def main() -> None:
    st.set_page_config(page_title="Terminal & System Monitor", page_icon="💻", layout="wide")
    init_session_state()

    router: CommandRouter = st.session_state.router
    cwd_display = router.session.cwd

    if st.session_state.get("_clear_command_input"):
        st.session_state.command_input = ""
        st.session_state.pop("_clear_command_input", None)

    st.title("Terminal & System Monitor")

    col_terminal, col_monitor = st.columns([2, 1])

    with col_terminal:
        st.subheader("Terminal")
        st.markdown(f"**user@host:{cwd_display}$**")

        command = st.text_input("Enter command:", key="command_input", label_visibility="collapsed")
        run_clicked = st.button("Run")

        if run_clicked and command.strip():
            execute_command(command.strip())
            st.session_state._clear_command_input = True
            safe_rerun()

        st.subheader("Output")
        for channel, payload in st.session_state.scrollback:
            if channel == "err":
                block = emit_stderr(payload)
            else:
                block = emit_stdout(payload)
            if block:
                st.markdown(block, unsafe_allow_html=True)

        st.markdown("---")
        st.caption(format_status(st.session_state.last_status, st.session_state.last_exec_time))

    with col_monitor:
        st.subheader("System Monitor")
        st.text(monitor_stats.cpu())
        st.text(monitor_stats.mem())
        st.text(monitor_stats.disk())

        st.subheader("Top Processes")
        st.code(monitor_stats.ps(5) or "No data")


if __name__ == "__main__":
    main()
