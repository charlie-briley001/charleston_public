from api_main import MbtaApi
from data_parsing import Vehicles
# api = MbtaApi()
# vehicles = api.get_data('vehicles')
# print(vehicles)

vehicles = Vehicles.api()
for v in vehicles:
    print(f"{v.id}: ({v.latitude}, {v.longitude}) on {v.route}")