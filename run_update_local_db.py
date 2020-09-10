import os
import time
import datetime
import dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

from update_local_db import update_organization
from update_local_db import update_vehicle_types
from update_local_db import update_bnso
from update_local_db import update_vehicle_models
from update_local_db import update_vehicle_marks
from update_local_db import update_bnso2vehicles
from update_local_db import update_vehicles

API_TOKEN = os.environ['API_TOKEN']
pSQL_URL = os.environ['pSQL_URL']
PGSQL_PERIOD = os.environ['PGSQL_PERIOD']
LITE_DB = os.environ['LITE_DB']

#------------------------------------------------------
# Create schedule
#------------------------------------------------------
def run_update_local_db():
    try:
        print("Updating local db in ", datetime.datetime.now().strftime('%b %d %Y %I:%M%p %s'))
        update_organization(LITE_DB, pSQL_URL)
        update_vehicle_types(LITE_DB, pSQL_URL)
        update_bnso(LITE_DB, pSQL_URL)
        update_vehicle_models(LITE_DB, pSQL_URL)
        update_vehicle_marks (LITE_DB, pSQL_URL)
        update_bnso2vehicles (LITE_DB, pSQL_URL)
        update_vehicles (LITE_DB, pSQL_URL)
    except Exception as exp:
        print(str(exp))





while True:
    run_update_local_db()
    time.sleep(int(PGSQL_PERIOD))
