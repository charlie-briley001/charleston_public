import pytest

from src.db_builder import GetConnection
from src.db_builder.connectors.duckdb_conn import DuckDBConn
from src.db_builder.general.exceptions import ConnectorError


def test_get_connection(in_memory_db_init):
    assert isinstance(in_memory_db_init,DuckDBConn)

def test_get_connection_fail():
    with pytest.raises(ConnectorError):
        GetConnection.create_connection(connection_type='')


