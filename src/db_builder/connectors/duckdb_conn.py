from src.db_builder.general.base_builder import DatabaseFoundation
import duckdb
from src.db_builder.general.utils import find_query_res, check_conn

class DuckDBConn(DatabaseFoundation):

    def __init__(self, kwargs):
        super().__init__(kwargs)
        self._qry_res = None
        self._validate_args(kwargs)

    def _validate_args(self, args):
        """Check that only one attribute between memory and file name are none
        not both or neither
        """
        if self._file_name is None and self._memory is None:
            raise ValueError('Both cannot be None')
        if self._file_name is not None and self._memory is not None:
            raise ValueError('Both cannot cannot have a value')

    def connect(self):
        """Class method to connect to duck db"""
        try:
            if self._file_name is not None:
                self._conn = duckdb.connect(database=self._file_name)
            elif self._memory:
                self._conn = duckdb.connect(database=':memory:')
            else:
                raise ValueError('Connection failed for some reason')
        except Exception as e:
            raise ValueError(f'Connection failed for some reason - {e}')

    @check_conn
    def execute_query(self, query_str: str):
        try:
            self._qry_res = self._conn.sql(query_str)
            return self._qry_res
        except Exception as e:
            raise ValueError(f'error as {e}')

    @find_query_res
    def limit_one(self):
        return self._qry_res.fetchone()

    @find_query_res
    def return_df(self):
        return self._qry_res.df()

    @find_query_res
    def fetch_all(self):
        return self._qry_res.fetchall()

    @find_query_res
    def return_meta(self):
        meta_dict = {
            'columns': self._qry_res.columns,
            'types': self._qry_res.types
        }
        return meta_dict

    @check_conn
    def close(self):
        self._conn.close()