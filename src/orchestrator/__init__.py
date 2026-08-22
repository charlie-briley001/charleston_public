"""
src.orchestrator
================

Orchestration package for the MBTA data pipeline.

This package coordinates the full ingest cycle:

1. Fetch live vehicle-position data from the MBTA API.
2. Format each record into a SQL statement.
3. Persist the records to a configured database connection.

The primary entry point for programmatic use is :class:`MbtaApiPull`.
To run from the command line invoke the package directly::

    python -m src.orchestrator --conn_type duckdb --db-file_path data/mbta.db

Exported names
--------------
.. autosummary::

    MbtaApiPull
"""

from src.orchestrator.orchestration import MbtaApiPull

__all__ = ["MbtaApiPull"]