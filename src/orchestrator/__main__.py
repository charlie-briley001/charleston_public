"""
src.orchestrator.__main__
=========================

Command-line entry point for the orchestrator package.

Allows the package to be executed directly via::

    python -m src.orchestrator [OPTIONS]

All argument parsing is delegated to :func:`src.orchestrator.cli.main`.
"""

from src.orchestrator.cli import main

if __name__ == "__main__":
    main()