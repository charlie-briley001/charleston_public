"""
src.config
==========

Public interface for the ``config`` package.

Exposes pre-loaded SQL query strings sourced from
``query_templates.yaml`` so that the rest of the application can import
them without knowing the internal loading mechanism.

Example usage::

    from src.config import CREATE_TABLE, UPDATE_ROW

    cursor.execute(CREATE_TABLE)

Exported names
--------------
.. autosummary::

    CREATE_TABLE
    UPDATE_ROW
"""

from src.config.config import CREATE_TABLE, UPDATE_ROW

__all__ = ["CREATE_TABLE", "UPDATE_ROW"]