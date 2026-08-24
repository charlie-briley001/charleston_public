"""
db_builder.connectors.duckdb_conn
===================================

DuckDB connector implementing
:class:`~db_builder.general.base_builder.DatabaseFoundation`.
"""

import duckdb
import os
from dotenv import load_dotenv

from src.mbta_app.db_builder.general.base_builder import DatabaseFoundation
from src.mbta_app.db_builder.general.exceptions import ValidationError, DBConnectionError, ExecutionError
from src.mbta_app.db_builder.general.utils import find_query_res, check_conn

load_dotenv()

class DuckDBConn(DatabaseFoundation):
    """
    DuckDB database connector.

    Extends :class:`~db_builder.general.base_builder.DatabaseFoundation` to
    provide a file-backed or in-memory DuckDB connection with query execution
    and result-fetching helpers.

    Exactly one of ``file_name`` or ``memory`` must be supplied in ``kwargs``;
    providing both or neither raises
    :class:`~db_builder.general.exceptions.ValidationError` immediately on
    construction.

    :param kwargs: Connection parameters forwarded to
        :class:`~db_builder.general.base_builder.DatabaseFoundation`.
    :type kwargs: dict

    **Additional recognised keys**

    .. list-table::
       :header-rows: 1
       :widths: 20 80

       * - Key
         - Description
       * - ``file_name``
         - Filesystem path for a persistent DuckDB database file. This includes a Motheduck connection.
       * - ``memory``
         - Any truthy value opens an in-memory ``":memory:"`` database.

    :raises ValidationError: If both or neither of ``file_name`` / ``memory``
        are provided.

    Example::

        conn = DuckDBConn({'memory': True})
        conn.connect()
        conn.execute_query("SELECT 42 AS answer")
        print(conn.fetch_all())  # [(42,)]
        conn.close()
    """

    def __init__(self, kwargs: dict):
        super().__init__(kwargs)
        self._qry_res = None
        self._validate_args(kwargs)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_args(self, args: dict) -> None:
        """
        Ensure exactly one of ``file_name`` or ``memory`` is provided.

        :param args: Raw kwargs dict passed to :meth:`__init__`.
        :type args: dict
        :raises ValidationError: If both or neither values are ``None``.
        """
        both_none = self._file_name is None and self._memory is None
        both_set  = self._file_name is not None and self._memory is not None
        if both_none or both_set:
            raise ValidationError

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """
        Open a DuckDB connection.

        Connects to the file specified by ``file_name``, or to an in-memory
        database when ``memory`` is truthy. The live connection is stored in
        ``self._conn``.

        :raises DBConnectionError: If the connection cannot be established.
        """
        try:
            if self._file_name:
                self._conn = duckdb.connect(database=self._file_name)
            elif self._memory:
                self._conn = duckdb.connect(database=':memory:')
            else:
                raise DBConnectionError('Ensure file_name and memory params are defined properly.')
        except Exception as e:
            raise DBConnectionError(f'Connection failed - {e}')

    @check_conn
    def close(self) -> None:
        """
        Close the active DuckDB connection.

        Guarded by :func:`~db_builder.general.utils.check_conn`; raises
        :class:`~db_builder.general.exceptions.ConnectionFirstError` if called
        before :meth:`connect`.
        """
        self._conn.close()

    # ------------------------------------------------------------------
    # Query execution
    # ------------------------------------------------------------------

    @check_conn
    def execute_query(self, query_str: str):
        """
        Execute a SQL statement and cache the result relation.

        The result is stored in ``self._qry_res`` and also returned directly.
        Subsequent calls to result-fetching methods (e.g. :meth:`fetch_all`,
        :meth:`return_df`) operate on this cached relation.

        :param query_str: A valid DuckDB SQL statement.
        :type query_str: str
        :returns: A DuckDB relation object representing the query result.
        :rtype: duckdb.DuckDBPyRelation
        :raises ConnectionFirstError: If called before :meth:`connect`.
        :raises ExecutionError: If DuckDB raises during execution.
        """
        try:
            self._qry_res = self._conn.sql(query_str)
            return self._qry_res
        except Exception as e:
            raise ExecutionError(f'Query could not execute - {e}')

    # ------------------------------------------------------------------
    # Result fetching
    # ------------------------------------------------------------------

    @find_query_res
    def limit_one(self):
        """
        Return the first row of the cached query result.

        :returns: A single row tuple, or ``None`` if the result set is empty.
        :rtype: tuple | None
        :raises QueryFirstError: If called before :meth:`execute_query`.
        """
        return self._qry_res.fetchone()

    @find_query_res
    def return_df(self):
        """
        Return the cached query result as a pandas ``DataFrame``.

        :returns: Query results converted to a ``DataFrame``.
        :rtype: pandas.DataFrame
        :raises QueryFirstError: If called before :meth:`execute_query`.
        """
        return self._qry_res.df()

    @find_query_res
    def fetch_all(self):
        """
        Return all rows of the cached query result.

        :returns: A list of row tuples.
        :rtype: list[tuple]
        :raises QueryFirstError: If called before :meth:`execute_query`.
        """
        return self._qry_res.fetchall()

    @find_query_res
    def return_meta(self) -> dict:
        """
        Return column names and data types for the cached query result.

        :returns: Dictionary with keys ``"columns"`` (list of column name
            strings) and ``"types"`` (list of DuckDB type objects).
        :rtype: dict
        :raises QueryFirstError: If called before :meth:`execute_query`.

        Example output::

            {'columns': ['id', 'name'], 'types': [INTEGER, VARCHAR]}
        """
        return {
            'columns': self._qry_res.columns,
            'types':   self._qry_res.types,
        }
