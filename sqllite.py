import os
import sqlite3
from grpc_client import get_grpc_states_from_devices
import os
import datetime
import json
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
    # print(idDev)
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

    cursor.execute(sql,[idDev])
    response = cursor.fetchall()

    try:

        grpc_message = get_grpc_states_from_devices(gRPC_URL,[response[0][1]])[0]
    except:
        grpc_message = ['', '', '', '', '','','']

    try:
        date_time = datetime.datetime.fromtimestamp(get_grpc_states_from_devices(gRPC_URL, [response[0][1]])[0][1]).strftime('%Y-%m-%d %H:%M:%S')

    except:
        date_time = None
    # print(response)
    id = response[0][0] if response !=[] else None
    idDev = response[0][1] if response !=[] else None
    try:
        typets =  response[0][2] if response !='' else None
    except:
        typets = None
    try:
        gosnumber = response[0][3] if response !='' else None
    except:
        gosnumber = None

    try:
        vin = response[0][4] if response[0][4] !=''  else None
    except:
        vin = None

    lat = grpc_message[3] if grpc_message[3] !='' else None
    lon = grpc_message[4] if grpc_message[4] !='' else None
    speed = grpc_message[6] if grpc_message[6] !='' else None
    angle = grpc_message[5] if grpc_message[5] !='' else None
    time_ = grpc_message[1] if grpc_message[1] !='' else None
    org_id = response[0][5] if response !=[] else None
    org_name = response[0][7] if response !=[] else None
    try:
        org_inn = response[0][6] if response[0][6] !='' else None
    except:
        org_inn = None


    tmessage = ({
        'id': id,
        'idDev': idDev,
        'typets': typets,
        'gosnumber': gosnumber,
        'vin': vin,
        'lat': lat,
        'lon': lon,
        'speed': speed,
        'angle' : angle,
        'date' : date_time,
        'time' : time_,
        'org_id': org_id,
        'org_name': org_name,
        'org_inn': org_inn
    })

    return tmessage

# gRPC_URL = '10.10.21.22:5587'
# print(get_t_by_device('39815425',gRPC_URL))
# gRPC_URL = '10.10.21.22:5587'
# idDev = '39815425'
# print(get_t_by_device(idDev,gRPC_URL))

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

            date_time = ''


        vin = row[4] if row[4] != '' else None
        lat = grpc_message[3] if grpc_message[3] !='' else None
        lon = grpc_message[4] if grpc_message[4] !='' else None
        speed = grpc_message[6] if grpc_message[6] !='' else None
        angle = grpc_message[5] if grpc_message[5] !='' else None
        date = date_time if date_time !='' else None
        time = grpc_message[1] if grpc_message[1] !='' else None
        org_id = row[5] if row[5] !='' else None
        org_name = row[7] if row[7] !='' else None
        org_inn = row[6] if row[6] !='' else None


        tmessages.append({
            'id': row[0],
            'idDev': row[1],
            'typets': row[2],
            'gosnumber': row[3],
            'vin': vin,
            'lat': lat,
            'lon': lon,
            'speed': speed,
            'angle': angle,
            'date': date,
            'time': time,
            'org_id': org_id,
            'org_name': org_name,
            'org_inn': org_inn
        })

    return tmessages



def get_all_t (gRPC_URL):
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
    LEFT JOIN organization ON vehicles.unit_uuid = organization.uuid"

    t_message = cursor.execute(sql)

    for row in t_message:

        try:
            grpc_message = get_grpc_states_from_devices(gRPC_URL, [row[1]])[0]
        except:
            grpc_message = ['', '', '', '', '','','']

        try:
            date_time = datetime.datetime.fromtimestamp(grpc_message[1]).strftime('%Y-%m-%d %H:%M:%S')

        except:

            date_time = ''


        vin = row[4] if row[4] != '' else None
        lat = grpc_message[3] if grpc_message[3] !='' else None
        lon = grpc_message[4] if grpc_message[4] !='' else None
        speed = grpc_message[6] if grpc_message[6] !='' else None
        angle = grpc_message[5] if grpc_message[5] !='' else None
        date = date_time if date_time !='' else None
        time = grpc_message[1] if grpc_message[1] !='' else None
        org_id = row[5] if row[5] !='' else None
        org_name = row[7] if row[7] !='' else None
        org_inn = row[6] if row[6] !='' else None


        tmessages.append({
            'id': row[0],
            'idDev': row[1],
            'typets': row[2],
            'gosnumber': row[3],
            'vin': vin,
            'lat': lat,
            'lon': lon,
            'speed': speed,
            'angle': angle,
            'date': date,
            'time': time,
            'org_id': org_id,
            'org_name': org_name,
            'org_inn': org_inn
        })

    return tmessages

# gRPC_URL = '10.10.21.22:5587'
# print(get_t_by_org('3dc07dfa-b43f-11e9-8848-029975b11713',gRPC_URL))
# gRPC_URL = '10.10.21.22:5587'
# print(get_all_t(gRPC_URL))