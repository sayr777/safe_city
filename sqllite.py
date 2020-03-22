import os
import sqlite3
from grpc_client import get_grpc_states_from_devices
import os
import datetime
import dotenv
# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# dotenv.load_dotenv(dotenv_path)
# gRPC_URL = os.environ['gRPC_URL']
# gRPC_URL = 'rnis-tm.t1-group.ru:18082'

# 1) Инициализировать локальную БД
def int_local_db():
    conn = sqlite3.connect("vehicles.db")  # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor()
    # Создание таблицы
    cursor.execute("""CREATE TABLE albums (title text, artist text, release_date text, publisher text, media_type text)""")
#int_local_db()

db = 'vehicles.db'

# 2) добавить данные в таблицу
def insert_in_db (db,dataset,sql_request):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.executemany(sql_request,dataset)
    conn.commit()
# insert_in_rt_in_db (db,dataset,sql_request)
# sql = "SELECT * FROM vehicles"
# cursor.execute(sql, [("Red")])
# print(cursor.fetchall())  # or use fetchone()
# print("Here's a listing of all the records in the table:")
# Пример запроса
db = 'vehicles.db'

def get_vehicles_dic():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    vehicles = []
    sql = 'SELECT vehicles.uuid, vehicles.state_number, vehicle_types.name, vehicles.release_year,\
       vehicles.vin, vehicle_marks.name, vehicle_models.name, bnso.bnso_number,\
       organization.uuid, organization.inn, organization.name_full, \
       vehicles.component FROM vehicles\
    LEFT JOIN vehicle_types ON vehicles.vehicle_type_uuid = vehicle_types.uuid\
    LEFT JOIN vehicle_marks ON vehicles.vehicle_mark_uuid = vehicle_marks.uuid\
    LEFT JOIN vehicle_models ON vehicles.vehicle_model_uuid = vehicle_models.uuid\
    LEFT JOIN bnso2vehicles ON vehicles.current_bnso_uuid = bnso2vehicles.bnso_uuid\
    LEFT JOIN bnso ON bnso2vehicles.bnso_uuid = bnso.uuid\
    LEFT JOIN organization ON vehicles.unit_uuid = organization.uuid'

    for row in cursor.execute(sql):
        vehicles.append({
            'id': row[0],
            'idDev' : row[7],
            'name' : row[7],
            'groupname': row[11],
            'createts' : row[3],
            'markats' : (str(row[5]) + " " + str(row[6])),
            'typets': row[2],
            'gosnumber' : row[1],
            'vin' : row[4],
            'org_id' : row[8],
            'org_name' : row[10],
            'org_inn' : row[9]
        })

    return vehicles


def get_t_by_device(idDev,gRPC_URL):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    sql = "SELECT vehicles.uuid,\
          bnso.bnso_number, \
          vehicle_types.name, \
          vehicles.state_number, \
          vehicles.vin, organization.uuid, \
          organization.inn, \
          organization.name_full \
          FROM vehicles\
    LEFT JOIN vehicle_types ON vehicles.vehicle_type_uuid = vehicle_types.uuid\
    LEFT JOIN bnso2vehicles ON vehicles.current_bnso_uuid = bnso2vehicles.bnso_uuid\
    LEFT JOIN bnso ON bnso2vehicles.bnso_uuid = bnso.uuid\
    LEFT JOIN organization ON vehicles.unit_uuid = organization.uuid\
    WHERE bnso_number = ?"

    cursor.execute(sql, [(idDev)])
    response = cursor.fetchall()

    tmessage = ({
        'id': response[0][0],
        'idDev': response[0][1],
        'typets': response[0][2],
        'gosnumber': response[0][3],
        'vin': response[0][4],
        'lat': get_grpc_states_from_devices(gRPC_URL,[response[0][1]])[0][3],
        'lon': get_grpc_states_from_devices(gRPC_URL,[response[0][1]])[0][4],
        'speed': get_grpc_states_from_devices(gRPC_URL, [response[0][1]])[0][6],
        'angle' : get_grpc_states_from_devices(gRPC_URL, [response[0][1]])[0][5],
        'date' : datetime.datetime.fromtimestamp(get_grpc_states_from_devices(gRPC_URL, [response[0][1]])[0][1]).strftime('%Y-%m-%d %H:%M:%S'),
        'time' : get_grpc_states_from_devices(gRPC_URL, [response[0][1]])[0][1],
        'org_id': response[0][5],
        'org_name': response[0][7],
        'org_inn': response[0][6]
    })

    return tmessage
# print(get_t_by_device('863591024988663',gRPC_URL))



def get_t_by_org(idOrg,gRPC_URL):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    tmessages = []

    sql = "SELECT vehicles.uuid, \
        bnso.bnso_number, \
        vehicle_types.name, \
        vehicles.state_number, \
        vehicles.vin, \
        organization.uuid, \
        organization.inn, \
        organization.name_full \
        FROM vehicles\
    LEFT JOIN vehicle_types ON vehicles.vehicle_type_uuid = vehicle_types.uuid\
    LEFT JOIN bnso2vehicles ON vehicles.current_bnso_uuid = bnso2vehicles.bnso_uuid\
    LEFT JOIN bnso ON bnso2vehicles.bnso_uuid = bnso.uuid\
    LEFT JOIN organization ON vehicles.unit_uuid = organization.uuid\
    WHERE organization.uuid = ?"

    for row in cursor.execute(sql,[(idOrg)]):

        try:
            grpc_message = get_grpc_states_from_devices(gRPC_URL, [row[1]])[0]
        except:
            grpc_message = ['', '', '', '', '','','']

        try:
            date_time = datetime.datetime.fromtimestamp(grpc_message[1]).strftime('%Y-%m-%d %H:%M:%S')

        except:

            date_time : ''


        tmessages.append({
            'id': row[0],
            'idDev': row[1],
            'typets': row[2],
            'gosnumber': row[3],
            'vin': row[4],
            'lat': grpc_message[3],
            'lon': grpc_message[4],
            'speed': grpc_message[6],
            'angle': grpc_message[5],
            'date': date_time,
            'time': grpc_message[1],
            'org_id': row[5],
            'org_name': row[7],
            'org_inn': row[6]
            })

    return tmessages

# print(get_t_by_org('3dc07dfa-b43f-11e9-8848-029975b11713'))