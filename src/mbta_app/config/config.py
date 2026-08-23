"""
src.config.config
=================

Loads SQL query templates from ``query_templates.yaml`` and exposes them
as module-level string constants.

The YAML file is read once at import time using :func:`yaml.safe_load`.
All downstream consumers should import the constants rather than
re-opening the file.

.. warning::

    The ``UPDATE_ROW`` query currently uses Python string formatting for
    value substitution.  Prefer parameterized queries at the call site to
    avoid SQL injection.

Constants
---------
.. autodata:: CREATE_TABLE
.. autodata:: UPDATE_ROW
"""

import yaml
from pathlib import Path


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_QUERY_TEMPLATES_PATH: Path = Path(__file__).parent / "query_templates.yaml"
"""Absolute path to the YAML file that stores all SQL templates."""


def _load_queries(path: Path) -> dict:
    """Load and return the parsed ``queries`` mapping from a YAML template file.

    :param path: Filesystem path to the YAML query-template file.
    :type path: :class:`pathlib.Path`
    :returns: The ``queries`` mapping from the YAML document.
    :rtype: dict
    :raises FileNotFoundError: If *path* does not exist.
    :raises KeyError: If the YAML document does not contain a ``queries`` key.
    """
    with open(path, "r") as fh:
        document = yaml.safe_load(fh)

    if "queries" not in document:
        raise KeyError(
            f"Expected a top-level 'queries' key in {path}, "
            f"but found: {list(document.keys())}"
        )

    return document["queries"]


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_QUERIES: dict = _load_queries(_QUERY_TEMPLATES_PATH)

CREATE_TABLE: str = _QUERIES["create_table"]
"""DDL statement that creates the ``vehicles`` table if it does not already exist.

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS vehicles (
        id                     VARCHAR,
        current_status         VARCHAR,
        current_stop_sequence  VARCHAR,
        direction_id           VARCHAR,
        latitude               VARCHAR,
        longitude              VARCHAR,
        updated_at             VARCHAR,
        route                  VARCHAR,
        trip                   VARCHAR
    );
"""

UPDATE_ROW: str = _QUERIES["update_row"]
"""DML statement that inserts a single vehicle record into ``vehicles``.

The query contains ``{field}``-style placeholders that must be filled via
:meth:`str.format` before execution.

Example::

    sql = UPDATE_ROW.format(
        id="v1",
        current_status="IN_TRANSIT_TO",
        current_stop_sequence="3",
        direction_id="0",
        latitude="42.361",
        longitude="-71.057",
        updated_at="2026-08-21T10:00:00",
        route="Red",
        trip="trip-001",
    )
    cursor.execute(sql)

.. warning::

    String-formatting SQL is vulnerable to injection.  Migrate to
    parameterized queries (``?`` placeholders + a value tuple) when
    possible.
"""