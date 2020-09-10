import os
import sqlite3
from grpc_client import get_grpc_states_from_devices
import datetime
import json
import dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)
# Объявить переменные
gRPC_URL = os.environ['gRPC_URL']
db = os.environ['LITE_DB']

# 1) Инициализировать локальную БД
def int_local_db():
    conn = sqlite3.connect("vehicles.db")  # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor()
    # Создание таблицы
    cursor.execute("""CREATE TABLE albums (title text, artist text, release_date text, publisher text, media_type text)""")

# 2) добавить данные в таблицу
def insert_in_db (db,dataset,sql_request):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.executemany(sql_request,dataset)
    conn.commit()

def get_vehicles_dic(db):
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

    vehicles = []
   
    for row in cursor.execute(sql):
        id =  row[0]
        idDev =  row[7]
        name  =  row[7]
        groupname =  row[11]
        createts  =  row[3][:4] if len(row[3])>3 else None
        markats = str(row[5] if row[5] is not None else '') + " " + str(row[6] if row[6] is not None else '')
        if markats is ' ': markats = None
        typets =  row[2]
        gosnumber = row[1] if len(row[1]) > 4 else None
        vin = row[4] if len(row[4])>4 else None
        org_id = row[8] if len(row[8])>4 else None
        org_name = row[10] if len(row[10])>4 else None
        org_inn = row[9] if len(row[9])>4 else None
         # Response structure
        vehicles.append({
            'id': id,
            'idDev' : idDev,
            'name' : name,
            'groupname': groupname,
            'createts' : createts,
            'markats' : markats,
            'typets': typets,
            'gosnumber' : gosnumber,
            'vin' : vin,
            'org_id' : org_id,
            'org_name' : org_name,
            'org_inn' : org_inn
        })

    print(len(vehicles))
    return vehicles

# Получить список всех БНСО
def get_all_bnso_numbers():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    sql = "SELECT bnso.bnso_number\
        FROM vehicles\
        LEFT JOIN vehicle_types ON vehicles.vehicle_type_uuid = vehicle_types.uuid\
        LEFT JOIN bnso2vehicles ON vehicles.current_bnso_uuid = bnso2vehicles.bnso_uuid\
        LEFT JOIN bnso ON bnso2vehicles.bnso_uuid = bnso.uuid\
        LEFT JOIN organization ON vehicles.unit_uuid = organization.uuid;"

    try:
        all_bnso = cursor.execute(sql).fetchall()
    except Exception as exp:
        print(str(exp))

    bnso_list = []
    for row in all_bnso:
        bnso_list.append(str(row)[2:-3])
    return bnso_list

# Получить всю имющуюся телематику
def get_telematics(bnso_list):
    try:
        grpc_messages_array = get_grpc_states_from_devices(gRPC_URL, bnso_list)
    except Exception as exp:
        print(exp)
    return grpc_messages_array

# Получить атрибутивную информацию по всем ТС
def get_all_info():
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    sql = "SELECT \
          vehicles.uuid, \
          bnso.bnso_number, \
          vehicle_types.name, \
          vehicles.state_number, \
          vehicles.vin, \
          organization.uuid, \
          organization.inn, \
          organization.name_full \
        FROM vehicles \
        LEFT JOIN vehicle_types ON vehicles.vehicle_type_uuid = vehicle_types.uuid\
        LEFT JOIN bnso2vehicles ON vehicles.current_bnso_uuid = bnso2vehicles.bnso_uuid\
        LEFT JOIN bnso ON bnso2vehicles.bnso_uuid = bnso.uuid\
        LEFT JOIN organization ON vehicles.unit_uuid = organization.uuid"

    try:
        vehicles_info = cursor.execute(sql).fetchall()

    except Exception as exp:
        print(str(exp))

    return vehicles_info

# Получить из массива телематики телематическое сообщение по одному OID
def get_telematics_for_bnso (grpc_messages_array,bnso_number):
    for element in grpc_messages_array:
        if element[0] != bnso_number:
            telematics_message = [None, None, None, None, None, None,None]
        else:
            telematics_message = element
            break

    return telematics_message

# Получить всю телематику с атрибутами
def get_all_t (gRPC_URL):

    # 1) получить все номера БНСО в системе
    bnso_list = get_all_bnso_numbers()
    # 2) получить всю телематику по всем БНСО в системе
    telematics_array = get_telematics(bnso_list)
    print('Телематика с %s устройств' %(len(telematics_array)))
    # 2) получить всю атрибутику по ТС
    vehicles_info_array = get_all_info()
    # Перебираемт все элементы масива и формируем словарь
    all_vehicles_array = [] #
    for row in vehicles_info_array :
        id = row[0]
        idDev = row[1]
        typets = row[2]
        gosnumber = row[3]
        vin = row[4] if len(row[4])>4 else None
        org_id = row[5] if row[5] !='' else None
        org_inn = row[6] if len(row[6])>4 else None
        org_name = row[7] if row[7] !='' else None
        element = get_telematics_for_bnso(telematics_array,idDev)
        lat = element[4]
        lon = element[3]
        speed = element[6]
        angle = element[5]
        time = element[1]
        date = datetime.datetime.fromtimestamp(element[1]).strftime('%Y-%m-%d %H:%M:%S') if element[1] is not None else None

        all_vehicles_array.append({
            'id': id,
            'idDev': idDev,
            'typets': typets,
            'gosnumber': gosnumber,
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

    return all_vehicles_array

# Получить телематику по OID
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

    try:
        cursor.execute(sql,[idDev])
        vehicles_attrib = cursor.fetchall()
    except Exception as exp:
        print(str(exp))
    # print(vehicles_attrib)
    # print(str(idDev).split())
    try:
        grpc_message = get_telematics(str(idDev).split())
    except Exception as exp:
        print(str(exp))
    # print(grpc_message)

    id = vehicles_attrib[0][0]
    idDev = vehicles_attrib[0][1]
    typets = vehicles_attrib[0][2] if len(vehicles_attrib[0][2]) > 2 else None
    gosnumber = vehicles_attrib[0][3] if len(vehicles_attrib[0][3]) > 4 else None
    vin = vehicles_attrib[0][4] if len(vehicles_attrib[0][4])>4 else None
    org_id = vehicles_attrib[0][5] if vehicles_attrib[0][5] !='' else None
    org_inn = vehicles_attrib[0][6] if len(vehicles_attrib[0][6])>4 else None
    org_name = vehicles_attrib[0][7] if vehicles_attrib[0][7] !='' else None
    lat = grpc_message[0][4]
    lon = grpc_message[0][3]
    speed = grpc_message[0][6]
    angle = grpc_message[0][5]
    time = grpc_message[0][1]
    date = datetime.datetime.fromtimestamp(grpc_message[0][1]).strftime('%Y-%m-%d %H:%M:%S') if grpc_message[0][1] is not None else None

    response = []
    response.append({
        'id': id,
        'idDev': idDev,
        'typets': typets,
        'gosnumber': gosnumber,
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
    return response

# Получить телематику по организации
def get_t_by_org(idOrg,gRPC_URL):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
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

    # Получить атрибуты ТС по организации
    cursor.execute(sql,[(idOrg)])
    vehicles_attrib = cursor.fetchall()
    # print(vehicles_attrib)

    # 1) получить все номера БНСО в системе
    bnso_list = get_all_bnso_numbers()
    # 2) получить всю телематику по всем БНСО в системе
    telematics_array = get_telematics(bnso_list)
    # print(telematics_array)

    tmessages = []

    for row in vehicles_attrib:

        id = row[0]
        idDev = row[1] if len(row[1]) > 2 else None
        typets = row[2]
        gosnumber = row[3]
        vin = row[4] if len(row[4]) > 4 else None

        grpc_message = get_telematics_for_bnso(telematics_array,idDev)
        # print(grpc_message)
        lat = grpc_message[4]
        lon = grpc_message[3]
        speed = grpc_message[6]
        angle = grpc_message[5]
        time = grpc_message[1]
        date = datetime.datetime.fromtimestamp(grpc_message[1]).strftime('%Y-%m-%d %H:%M:%S') if grpc_message [1] is not None else None
        org_id = row[5]
        org_name = row[7]
        org_inn = row[6]

        tmessages.append({
            'id': id,
            'idDev': idDev,
            'typets': typets,
            'gosnumber': gosnumber,
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




