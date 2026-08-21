from src.mbta_connector.api_main import MbtaApi
from src.mbta_connector.data_parsing import Vehicles, Lines, Route
from src.db_builder import GetConnection
# vehicles = Vehicles.api()
# route = Route.api()
#
# lines = Lines.api()
#

class MbtaApiPull:

    def __init__(self, configs):
        self.db_configs = configs
        self.conn_type = configs

    def _run(self):
        self._establish_conn()
        self._api_run()
        self._update_db()

        self._conn.close()


    def _establish_conn(self):

        connector_cls = GetConnection.create_connection(
                connection_type=self.conn_type
            )
        self._conn = connector_cls({'file_name': self.db_configs})
        self._conn.connect()

    def _api_run(self):
        #run api's ad prepare sql statements
        pass

    def _update_db(self):
        #execute record insertion
        pass


