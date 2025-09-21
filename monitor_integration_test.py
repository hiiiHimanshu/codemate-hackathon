#!/usr/bin/env python3
"""Manual smoke test for monitor/stats outputs."""

from monitor import stats


def test_function_signatures() -> None:
    print("CPU:", stats.cpu())
    print("Memory:", stats.mem())
    print("Disk:", stats.disk())
    print("Processes:\n", stats.ps(5))


if __name__ == "__main__":
    test_function_signatures()
