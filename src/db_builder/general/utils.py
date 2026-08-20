"""
db_builder.general.utils
=========================

Decorator utilities used to enforce connection and query pre-conditions
across connector methods.

These decorators are designed to be applied to instance methods of any class
that stores its live connection in ``self._conn`` and its most recent query
result in ``self._qry_res``.
"""

from functools import wraps

from src.db_builder.general.exceptions import ConnectionFirstError, QueryFirstError


def find_query_res(func):
    """
    Guard decorator for result-fetching methods.

    Raises :class:`~db_builder.general.exceptions.QueryFirstError` if the
    decorated method is called before :meth:`execute_query` has stored a result
    in ``self._qry_res``.

    :param func: The instance method to wrap.
    :type func: callable
    :returns: The wrapped method.
    :rtype: callable
    :raises QueryFirstError: If ``self._qry_res`` is ``None`` at call time.

    Example::

        @find_query_res
        def fetch_all(self):
            return self._qry_res.fetchall()
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._qry_res is None:
            raise QueryFirstError('A query must be run first.')
        return func(self, *args, **kwargs)
    return wrapper


def check_conn(func):
    """
    Guard decorator for connection-dependent methods.

    Raises :class:`~db_builder.general.exceptions.ConnectionFirstError` if the
    decorated method is called before :meth:`connect` has stored a live
    connection in ``self._conn``.

    :param func: The instance method to wrap.
    :type func: callable
    :returns: The wrapped method.
    :rtype: callable
    :raises ConnectionFirstError: If ``self._conn`` is ``None`` at call time.

    Example::

        @check_conn
        def execute_query(self, query_str: str):
            ...
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._conn is None:
            raise ConnectionFirstError('A connection must be made first.')
        return func(self, *args, **kwargs)
    return wrapper