
from abc import ABC, abstractmethod

## will probably want to push the duckdb implementation into its own module,
# and then have a single endpoint where other code can call "get_connection", etc...

class DatabaseFoundation(ABC):
    #metaclass isn't really needed right now, but expecting to have multiple connection
    # points so just getting ready. I am thinking that for this mini package we will have just one
    # connection implemented (duckdb), then allow other connections to extend off this foundation class
    # but those extensions I want to be implemented into each package that uses the connection. If we see redundancy
    # we can consolidate.
    """
    Description here
    """
    def __init__(self, kwargs):
        self._conn = kwargs.get('conn')
        self._connection_type = kwargs.get('connection_type')
        self._host = kwargs.get('host')
        self._port = kwargs.get('port')
        self._file_name = kwargs.get('file_name')
        self._memory = kwargs.get('memory')
        self._password = kwargs.get('password')
        self._username = kwargs.get('username')

    @abstractmethod
    def connect(self) -> list:
       pass

    @abstractmethod
    def close(self, **kwargs):
        pass