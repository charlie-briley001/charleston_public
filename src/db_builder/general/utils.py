from functools import wraps

from src.db_builder.general.exceptions import ConnectionFirstError, QueryFirstError


def find_query_res(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._qry_res is None:
            raise QueryFirstError('A query must be run first')
        result = func(self, *args, **kwargs)
        return result
    return wrapper

def check_conn(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._conn is None:
            raise ConnectionFirstError('A connection must be made first')
        result = func(self, *args, **kwargs)
        return result
    return wrapper