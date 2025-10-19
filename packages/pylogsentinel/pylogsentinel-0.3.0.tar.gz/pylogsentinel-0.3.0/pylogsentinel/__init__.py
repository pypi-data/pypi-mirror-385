"""
pylogsentinel package.

A lightweight log monitoring utility driven by a simple INI-style configuration.
See README.md and pylogsentinel.conf.example for full usage details.

Public API (stable):
- __version__
- get_version()
"""

from __future__ import annotations

__all__ = ["__version__", "get_version"]

# Semantic version of the library.
# Bump this when publishing to PyPI.
__version__ = "0.1.0"


def get_version() -> str:
    """
    Return the library version.

    Provided as a function to mirror common patterns and allow
    future logic (e.g., dynamic dev version tags) without changing call sites.
    """
    return __version__
