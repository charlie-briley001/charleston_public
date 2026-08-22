"""
src.orchestrator.orchestration
==============================

Core orchestration logic for the MBTA data pipeline.

Defines :class:`MbtaApiPull`, which coordinates three steps in sequence:

1. **Connect** — obtain a database connection via :class:`~src.db_builder.GetConnection`.
2. **Fetch**   — pull live vehicle positions from the MBTA API.
3. **Persist** — ensure the target table exists, then insert all records.

The database connection is always closed in a ``finally`` block so that
resources are released even when an earlier step raises.

Classes
-------
.. autoclass:: MbtaApiPull
   :members:
   :private-members:
"""

from src.config import CREATE_TABLE, UPDATE_ROW
from src.config.logging import get_logger
from src.db_builder import GetConnection
from src.mbta_connector.data_parsing import Vehicles

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class MbtaApiPull:
    """Orchestrates a single MBTA vehicle-position ingest cycle.

    Fetches the current snapshot of vehicle positions from the MBTA API,
    formats each record as a SQL statement, and writes them to the
    configured database.

    :param configs: Parsed CLI arguments (or any object whose ``__dict__``
        contains ``conn_type``, ``db_file_path``, and ``db_memory``).
    :type configs: :class:`argparse.Namespace`

    Example::

        import argparse
        from src.orchestrator import MbtaApiPull

        args = argparse.Namespace(
            conn_type="duckdb",
            db_file_path="data/mbta.db",
            db_memory=False,
        )
        MbtaApiPull(args).run()
    """

    def __init__(self, configs) -> None:
        """Initialise the orchestrator from a configuration namespace.

        Extracts connection settings from *configs* and stores them for use
        by :meth:`_establish_conn`.

        :param configs: Namespace produced by :func:`~src.orchestrator.cli.parse_args`
            (or equivalent).  Expected keys: ``conn_type``, ``db_file_path``,
            ``db_memory``.
        :type configs: :class:`argparse.Namespace`
        """
        self.conn_type  = configs.__dict__.get("conn_type")
        self._db_file   = configs.__dict__.get("db_file_path")
        self._db_memory = configs.__dict__.get("db_memory")

        self._db_configs = {
            "file_name": self._db_file,
            "memory":    self._db_memory,
        }

        self._conn        = None
        self._query_store = []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Execute the full ingest cycle.

        Runs the three pipeline steps in order:

        1. :meth:`_establish_conn` — open the database connection.
        2. :meth:`_api_run`        — fetch data and build SQL statements.
        3. :meth:`_update_db`      — write records to the database.

        The connection is closed in a ``finally`` block regardless of
        whether an earlier step succeeds or raises.

        :returns: None
        :raises Exception: Re-raises any unexpected error after printing a
            diagnostic message and closing the connection.
        """
        try:
            self._establish_conn()
            self._api_run()
            self._update_db()
        except Exception as e:
            logger.error(f"Unexpected error during ingest: {e}")
        finally:
            if self._conn is not None:
                self._conn.close()
                logger.info('database connection closed.')

    # ------------------------------------------------------------------
    # Private pipeline steps
    # ------------------------------------------------------------------

    def _establish_conn(self) -> None:
        """Open and store the database connection.

        Uses :class:`~src.db_builder.GetConnection` to resolve the correct
        connector class for :attr:`conn_type`, then instantiates and connects
        it with :attr:`_db_configs`.

        :returns: None
        :raises Exception: Propagates any connection error raised by the
            underlying connector.
        """
        connector_cls = GetConnection.create_connection(
            connection_type=self.conn_type
        )
        self._conn = connector_cls(self._db_configs)
        self._conn.connect()
        logger.info(f'Database connection established to {self.conn_type}')

    def _api_run(self) -> None:
        """Fetch vehicle positions and prepare SQL insert statements.

        Calls :meth:`~src.mbta_connector.data_parsing.Vehicles.api` to
        retrieve the current vehicle snapshot, then formats each
        :class:`~src.mbta_connector.data_parsing.Vehicles` object into a
        SQL string using :data:`~src.config.UPDATE_ROW`.

        The resulting statements are stored in :attr:`_query_store` for
        consumption by :meth:`_update_db`.

        :returns: None

        .. warning::

            SQL statements are built via :meth:`str.format`.  Migrate to
            parameterized queries to eliminate the SQL injection risk.
        """
        vehicles_store = Vehicles.api()
        self._query_store = [
            UPDATE_ROW.format(**v.__dict__)
            for v in vehicles_store
        ]
        logger.info(f'{len(self._query_store)} have been identified')

    def _update_db(self) -> None:
        """Ensure the target table exists and insert all queued records.

        Executes :data:`~src.config.CREATE_TABLE` first (idempotent DDL),
        then iterates over :attr:`_query_store` and executes each insert
        statement individually.

        :returns: None
        :raises Exception: Propagates any error raised by the underlying
            ``execute_query`` call.
        """
        self._conn.execute_query(CREATE_TABLE)

        for row in self._query_store:
            self._conn.execute_query(str(row))

        logger.info(f"Inserted {len(self._query_store)} vehicle records.")
        logger.info('Database has been updated successfully!')