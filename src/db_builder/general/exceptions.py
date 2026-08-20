"""add exceptions class"""

class DBBuilderError(Exception):
    pass

class ValidationError(DBBuilderError):
    def __init__(self):
        message = """Only File_Name or Memory can be None. Not both or neither"""
        super().__init__(message)

class DBConnectionError(DBBuilderError):
    def __init__(self, message):
        super().__init__(message)

class DBExecutionError(Exception):
    pass

class ExecutionError(DBExecutionError):
    def __init__(self, message):
        super().__init__(message)

class ConnectionFirstError(DBExecutionError):
    def __init__(self, message):
        super().__init__(message)

class QueryFirstError(DBExecutionError):
    def __init__(self, message):
        super().__init__(message)

class ConnectorError(Exception):
    def __init__(self, message):
        super().__init__(message)
