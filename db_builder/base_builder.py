
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
    def __init__(self):
        self._connection_type = 'type'
        self._host = 'pass'
        self._port = 'pass'
        self._password = ''
        self._username = ''

    @abstractmethod
    def connect(self) -> list:
       pass

    @abstractmethod
    def close(self, **kwargs):
        pass


class placeHolder(DatabaseFoundation):
    # def __init__(self):
    #     print('Created')

    def connect(self):
        print('connect work')

    def execute_qeury(self):
        print('running query')

    def limit_one(self):
        #I'll build a decorator to check that if there is no execute function prior to this then throw an error
        print('fetching one record')

    def return_df(self):
        print('returning database')

    def return_meta(self):
        print('returning meta_information')

    def write_records(self):
        print('writing_records')

    def close(self):
        print('api works')

if __name__ == '__main__':
    obj = placeHolder()
    print(obj)