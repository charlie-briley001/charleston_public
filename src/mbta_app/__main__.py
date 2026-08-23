"""
src.orchestrator.__main__
=========================

Command-line entry point for the orchestrator package.

Allows the package to be executed directly via::

    python -m src.orchestrator [OPTIONS]

All argument parsing is delegated to :func:`src.orchestrator.cli.main`.
"""
# main.py
import logging
from datetime import datetime

from src.mbta_app.config.logging import setup_logging, get_logger
from src.mbta_app.orchestrator.cli import main

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

setup_logging(
    level=logging.INFO,
    log_dir= f"logs",
    log_file= f"mbta_api_{timestamp}.log"
)

logger = get_logger(__name__)


if __name__ == "__main__":
    logger.info("-----------------Process Started-----------------")
    main()
    logger.info("-----------------Process Ended-----------------")
