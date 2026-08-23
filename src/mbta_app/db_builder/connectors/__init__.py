"""
db_builder.connectors
======================

Database backend connector implementations.

Each module in this sub-package provides a concrete implementation of
:class:`~db_builder.general.base_builder.DatabaseFoundation` for a specific
database engine.

**Available connectors**

- :class:`~db_builder.connectors.duckdb_conn.DuckDBConn` — DuckDB (file-backed or in-memory).
"""