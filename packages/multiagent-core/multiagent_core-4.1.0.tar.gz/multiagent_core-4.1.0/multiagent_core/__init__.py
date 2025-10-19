"""Multi-Agent Core Framework

Foundation framework with intelligent directory management for multi-agent development.
"""
from __future__ import annotations

try:
    from importlib.metadata import version as _pkg_version
except ImportError:  # pragma: no cover - Python <3.8
    from importlib_metadata import version as _pkg_version

__author__ = "Multi-Agent Template Framework"

try:
    __version__ = _pkg_version("multiagent-core")
except Exception:  # pragma: no cover - during local dev with pip install -e .
    __version__ = "unknown"


def main() -> None:
    """Entry point for the `multiagent` console script."""
    from .cli import main as cli_main

    cli_main()


from .config import config  # noqa: E402

__all__ = [
    "main",
    "config",
]
