"""
src.orchestrator.cli
====================

Command-line interface for the MBTA orchestrator.

Defines argument parsing and the ``main()`` entry point that wires CLI
arguments into :class:`~src.orchestrator.orchestration.MbtaApiPull`.

Typical usage::

    python -m src.orchestrator --conn_type duckdb --db-file_path data/mbta.db
    python -m src.orchestrator --conn_type duckdb --db-memory

Functions
---------
.. autofunction:: parse_args
.. autofunction:: main
"""

import argparse

from src.config.logging import get_logger
from src.orchestrator.orchestration import MbtaApiPull

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """Parse and return command-line arguments.

    Defines two mutually exclusive database-target options:

    * ``--db-file_path`` — persist to a file-backed DuckDB database.
    * ``--db-memory``    — use an in-memory DuckDB instance (no persistence).

    :returns: Parsed argument namespace with the following attributes:

              * ``conn_type`` *(str)* — database backend (default: ``"duckdb"``).
              * ``db_file_path`` *(str | None)* — path to the DuckDB file.
              * ``db_memory`` *(bool)* — ``True`` when in-memory mode is requested.

    :rtype: :class:`argparse.Namespace`

    .. note::

        ``--db-file_path`` and ``--db-memory`` are mutually exclusive;
        supplying both will cause argparse to exit with an error.
    """
    parser = argparse.ArgumentParser(
        description="Ingest MBTA vehicle position data into a database."
    )

    parser.add_argument(
        "--conn_type",
        type=str,
        default="duckdb",
        help="Database connection type to build (default: duckdb).",
    )

    db_group = parser.add_mutually_exclusive_group()

    db_group.add_argument(
        "--db-file_path",
        type=str,
        dest="db_file_path",
        default=None,
        help="Path to the DuckDB database file.",
    )
    db_group.add_argument(
        "--db-memory",
        # action="store_true",
        dest="db_memory",
        default=None,
        help="Run DuckDB entirely in memory (no file persisted).",
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse CLI arguments and execute the MBTA ingest pipeline.

    Instantiates :class:`~src.orchestrator.orchestration.MbtaApiPull` with
    the parsed arguments, then calls :meth:`~src.orchestrator.orchestration.MbtaApiPull.run`
    to complete the full fetch-and-store cycle.

    :returns: None
    """
    args = parse_args()
    logger.info(
        f"""Arguments identified - {",".join([f'{k} - {v}' for k, v in args.__dict__.items()])}"""
    )
    vehicles = MbtaApiPull(args)
    vehicles.run()