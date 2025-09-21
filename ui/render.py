"""Rendering helpers for terminal output formatting."""

from __future__ import annotations

from html import escape
from typing import Iterable, List


def _normalize(text: str) -> str:
    """Return the given text without trailing whitespace."""
    return text.rstrip()


def emit_stdout(text: str) -> str:
    """Return an HTML block for stdout with trimmed trailing whitespace."""
    normalized = _normalize(text)
    if not normalized:
        return ""
    return f"<pre style='color: white; font-family: monospace;'>{escape(normalized)}</pre>"


def emit_stderr(text: str) -> str:
    """Return an HTML block for stderr with trimmed trailing whitespace."""
    normalized = _normalize(text)
    if not normalized:
        return ""
    return f"<pre style='color: red; font-family: monospace;'>{escape(normalized)}</pre>"


def format_table(rows: List[List[str]]) -> str:
    """Format a table using fixed-width, left-aligned columns."""
    if not rows:
        return ""

    col_widths = [max(len(row[idx]) for row in rows) for idx in range(len(rows[0]))]
    formatted_rows = []
    for row in rows:
        cells = [row[idx].ljust(col_widths[idx]) for idx in range(len(col_widths))]
        formatted_rows.append("  ".join(cells).rstrip())
    return "\n".join(formatted_rows)


def humanize_bytes(n: int) -> str:
    """Return a human readable representation of bytes."""
    suffixes = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(n)
    for suffix in suffixes:
        if size < 1024.0 or suffix == suffixes[-1]:
            if suffix == "B":
                return f"{int(size)} {suffix}"
            return f"{size:.2f} {suffix}"
        size /= 1024.0
    return f"{size:.2f} PB"


def truncate(text: str, limit: int = 10_000) -> str:
    """Truncate text to the limit, appending an ellipsis marker when needed."""
    if len(text) <= limit:
        return _normalize(text)
    truncated = text[:limit]
    return _normalize(f"{truncated}… (truncated)")


def format_status(status: str, exec_ms: float) -> str:
    """Return a status footer string using ✔/✖ symbols and milliseconds."""
    symbol = "✔" if status == "ok" else "✖"
    return f"{symbol} {exec_ms:.2f}ms"
