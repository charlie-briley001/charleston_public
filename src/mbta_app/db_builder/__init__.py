"""
db_builder
===========

Lightweight database connection package.

Exposes :class:`~db_builder.get_conn.GetConnection` as the primary entry
point for obtaining a configured database connector.

**Supported backends**

- **DuckDB** (file-backed or in-memory) via
  :class:`~db_builder.connectors.duckdb_conn.DuckDBConn`.

Example::

    from db_builder import GetConnection

    connector_cls = GetConnection.create_connection(
        GetConnection, connection_type='duckdb'
    )
    conn = connector_cls({'memory': True})
    conn.connect()
    conn.execute_query("SELECT 1 AS value")
    print(conn.fetch_all())  # [(1,)]
    conn.close()
"""

from src.mbta_app.db_builder.get_conn import GetConnection

__all__ = ["GetConnection"]