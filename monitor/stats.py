"""Formatted system statistics using psutil."""

from __future__ import annotations

from typing import List

import psutil

from ui.render import format_table, humanize_bytes


def _safe_cpu_percent() -> float:
    try:
        return float(psutil.cpu_percent(interval=0.1))
    except Exception:
        return 0.0


def _safe_cpu_count() -> int:
    try:
        return int(psutil.cpu_count() or 0)
    except Exception:
        return 0


def cpu() -> str:
    """Return CPU utilisation summary."""
    percent = _safe_cpu_percent()
    cores = _safe_cpu_count() or 1
    return f"CPU: {percent:.1f}%  |  Cores: {cores}"


def mem() -> str:
    """Return memory utilisation summary."""
    try:
        info = psutil.virtual_memory()
        used = humanize_bytes(int(info.used))
        total = humanize_bytes(int(info.total))
        return f"Memory: {used} / {total}  ({info.percent:.1f}%)"
    except Exception:
        return "Memory: 0 B / 0 B  (0.0%)"


def disk() -> str:
    """Return disk utilisation summary."""
    try:
        info = psutil.disk_usage(str(psutil.Process().cwd()))
    except Exception:
        info = psutil.disk_usage('/')
    used = humanize_bytes(int(info.used))
    total = humanize_bytes(int(info.total))
    return f"Disk: {used} / {total}  ({info.percent:.1f}%)"


def ps(top_n: int = 5) -> str:
    """Return a table of top processes by CPU usage."""
    rows: List[List[str]] = [["PID", "NAME", "CPU%", "RSS"]]

    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                info = proc.info
                name = info.get('name') or "?"
                rss = info.get('memory_info').rss if info.get('memory_info') else 0
                processes.append(
                    [
                        str(info.get('pid', '?')),
                        name,
                        f"{float(info.get('cpu_percent') or 0.0):.1f}",
                        humanize_bytes(int(rss)),
                    ]
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception:
        processes = []

    processes.sort(key=lambda row: float(row[2]), reverse=True)
    rows.extend(processes[:top_n])
    return format_table(rows)
