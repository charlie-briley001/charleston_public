"""package end point"""
from src.db_builder.connectors.duckdb_conn import DuckDBConn
from src.db_builder.general.base_builder import DatabaseFoundation
from src.db_builder.general.exceptions import ConnectorError


class GetConnection:
    OBJECTS = {
        "duckdb": DuckDBConn,
        "base_builder": DatabaseFoundation
    }
    @staticmethod
    def create_connection(cls,connection_type: str) -> DuckDBConn | DatabaseFoundation | None:
        try:
            return cls.OBJECTS.get(connection_type)
        except:
            raise ConnectorError(f'Connection must be -> {cls.OBJECTS.keys()}')
