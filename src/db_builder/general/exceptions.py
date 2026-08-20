"""
db_builder.general.exceptions
==============================

Custom exception hierarchy for the ``db_builder`` package.

All package-level exceptions inherit from :class:`DBBuilderError` or
:class:`DBExecutionError`, enabling callers to catch at whichever
granularity suits their error-handling strategy.
"""


class DBBuilderError(Exception):
    """Base exception for all ``db_builder`` connection and configuration errors."""
    pass


class ValidationError(DBBuilderError):
    """
    Raised when connection arguments fail pre-connect validation.

    Specifically, exactly one of ``file_name`` or ``memory`` must be
    provided — not both and not neither.
    """
    def __init__(self):
        message = "Only File_Name or Memory can be None. Not both or neither."
        super().__init__(message)


class DBConnectionError(DBBuilderError):
    """
    Raised when a database connection attempt fails.

    :param message: Human-readable description of the connection failure.
    :type message: str
    """
    def __init__(self, message: str):
        super().__init__(message)


class DBExecutionError(Exception):
    """Base exception for query execution and result-fetching errors."""
    pass


class ExecutionError(DBExecutionError):
    """
    Raised when a SQL statement fails during execution.

    :param message: Human-readable description of the execution failure.
    :type message: str
    """
    def __init__(self, message: str):
        super().__init__(message)


class ConnectionFirstError(DBExecutionError):
    """
    Raised when a query or fetch is attempted before a connection is established.

    :param message: Human-readable description of the error.
    :type message: str
    """
    def __init__(self, message: str):
        super().__init__(message)


class QueryFirstError(DBExecutionError):
    """
    Raised when a result-fetching method is called before any query has been executed.

    :param message: Human-readable description of the error.
    :type message: str
    """
    def __init__(self, message: str):
        super().__init__(message)


class ConnectorError(Exception):
    """
    Raised by :class:`~db_builder.get_conn.GetConnection` when an unsupported
    connection type is requested.

    :param message: Human-readable description of the error.
    :type message: str
    """
    def __init__(self, message: str):
        super().__init__(message)