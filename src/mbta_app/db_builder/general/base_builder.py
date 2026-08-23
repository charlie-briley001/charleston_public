"""
db_builder.general.base_builder
================================

Abstract base class defining the contract for all database connectors
in the ``db_builder`` package.
"""

from abc import ABC, abstractmethod


class DatabaseFoundation(ABC):
    """
    Abstract base class for all ``db_builder`` database connectors.

    Subclasses implement :meth:`connect` and :meth:`close` for their specific
    database backend. Additional backends beyond
    :class:`~db_builder.connectors.duckdb_conn.DuckDBConn` are expected to be
    defined in the packages that consume them; shared implementations are
    consolidated here only when redundancy warrants it.

    :param kwargs: Dictionary of connection parameters.
    :type kwargs: dict

    **Recognised keys**

    .. list-table::
       :header-rows: 1
       :widths: 20 80

       * - Key
         - Description
       * - ``conn``
         - An existing raw connection object (optional).
       * - ``connection_type``
         - String identifier for the backend (e.g. ``"duckdb"``).
       * - ``host``
         - Hostname for network-based backends.
       * - ``port``
         - Port number for network-based backends.
       * - ``file_name``
         - Path to a file-backed database (mutually exclusive with ``memory``).
       * - ``memory``
         - Truthy value to open an in-memory database (mutually exclusive with ``file_name``).
       * - ``password``
         - Authentication password.
       * - ``username``
         - Authentication username.
    """

    def __init__(self, kwargs: dict):
        self._conn            = kwargs.get('conn')
        self._connection_type = kwargs.get('connection_type')
        self._host            = kwargs.get('host')
        self._port            = kwargs.get('port')
        self._file_name       = kwargs.get('file_name')
        self._memory          = kwargs.get('memory')
        self._password        = kwargs.get('password')
        self._username        = kwargs.get('username')

    @abstractmethod
    def connect(self) -> None:
        """
        Open the database connection and assign it to ``self._conn``.

        :raises DBConnectionError: If the connection cannot be established.
        """
        pass

    @abstractmethod
    def close(self, **kwargs) -> None:
        """
        Close the active database connection.

        :raises ConnectionFirstError: If no connection is open.
        """
        pass