"""Python file to build, hold, and return logger object"""
import logging
import sys
from pathlib import Path


def setup_logging(level=logging.INFO, log_dir: str = "logs", log_file: str = "log_1.log",):
    """Create and format logger to be used"""
    # Create logs folder
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Format
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    # Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(
        filename=log_path / log_file,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Make Global
    logging.basicConfig(
        level=level,
        handlers=[console_handler, file_handler]
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)