"""
db_builder.get_conn
====================

Package-level entry point for creating database connector instances.

Consumers should interact with this module exclusively through
:class:`GetConnection` rather than importing connector classes directly.
"""

from src.mbta_app.db_builder.connectors.duckdb_conn import DuckDBConn
from src.mbta_app.db_builder.general.base_builder import DatabaseFoundation
from src.mbta_app.db_builder.general.exceptions import ConnectorError


class GetConnection:
    """
    Factory class for obtaining a database connector class.

    :cvar OBJECTS: Registry mapping connection-type strings to their
        corresponding connector classes.
    :type OBJECTS: dict[str, type]

    Example::

        connector_cls = GetConnection.create_connection(connection_type='duckdb')
        conn = connector_cls({'memory': True})
        conn.connect()
    """

    OBJECTS: dict = {
        "duckdb":       DuckDBConn,
        "base_builder": DatabaseFoundation,
    }

    @classmethod
    def create_connection(cls, connection_type: str) -> type[DuckDBConn] | type[DatabaseFoundation]:
        """
        Look up and return the connector *class* for the given connection type.

        .. note::
            This method returns the **class itself**, not an instance. The
            caller is responsible for instantiating the returned class with an
            appropriate ``kwargs`` dict.

        :param connection_type: Key identifying the desired backend. Must be
            one of the keys in :attr:`OBJECTS`.
        :type connection_type: str
        :returns: The connector class registered under ``connection_type``.
        :rtype: type[DuckDBConn] | type[DatabaseFoundation]
        :raises ConnectorError: If ``connection_type`` is not a recognised key.
        """
        try:
            return cls.OBJECTS[connection_type]
        except Exception:
            raise ConnectorError(f'Connection must be one of -> {list(cls.OBJECTS.keys())}')