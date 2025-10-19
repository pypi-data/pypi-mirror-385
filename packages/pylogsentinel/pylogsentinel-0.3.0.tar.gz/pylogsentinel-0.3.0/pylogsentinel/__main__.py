"""
Module entry-point for `python -m pylogsentinel`.

This delegates to `pylogsentinel.core.main` so that:
    python -m pylogsentinel [...]
behaves the same as invoking the installed console script
(or calling pylogsentinel.core.main() directly).

The core.main function already handles argument parsing, configuration
loading, locking, and execution flow.
"""

from __future__ import annotations

from .core import main as core_main


def main() -> int:
    """Thin wrapper calling the real core main function."""
    return core_main()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
