import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import time
# con = sqlite3.connect(":memory:")
lite_db = "vehicles.db"
connecting_string = "postgresql://postgres@10.10.21.25:5432/"

# Удалить локальную БД
def delete_db (lite_db):
    import os
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), lite_db)
    os.remove(path)
# delete_db(lite_db)

# Создать локальную БД
def create_db (lite_db):
    con = sqlite3.connect(lite_db)
    cur = con.cursor()
    cur.execute("CREATE TABLE bnso(uuid TEXT,bnso_number TEXT)")
    cur.execute("CREATE TABLE bnso2vehicles(bnso_uuid TEXT,vehicle_uuid TEXT)")
    cur.execute("CREATE TABLE organization(uuid TEXT,name_full TEXT,inn TEXT)")
    cur.execute("CREATE TABLE vehicle_marks(uuid TEXT,name TEXT)")
    cur.execute("CREATE TABLE vehicle_models(uuid TEXT,name TEXT)")
    cur.execute("CREATE TABLE vehicle_types(uuid TEXT,name TEXT)")
    cur.execute("CREATE TABLE vehicles(uuid TEXT,state_number TEXT,\
    vehicle_type_uuid TEXT,release_year INTEGER,vin TEXT,\
    vehicle_mark_uuid TEXT,current_bnso_uuid TEXT,unit_uuid TEXT,\
    component TEXT,vehicle_model_uuid TEXT,idle_time INTEGER,status_change_time TEXT,\
    paid TEXT,vehicle_capacity_integer TEXT)")
    con.close()
# create_db (lite_db)

def update_organization(lite_db, connecting_string):
    engine = create_engine(connecting_string + 'organizational_units')
    sql_query = 'SELECT uuid, name_full, inn FROM public.units'
    organizations = pd.read_sql_query(sql_query,con=engine)
    print('Получено из PGSQL: ' + str(len(organizations)) + ' организаций')
    cnx = sqlite3.connect(lite_db)
    cur = cnx.cursor()
    try:
        cur.execute("DROP TABLE organization")
    except:
        cur.execute("CREATE TABLE organization(uuid TEXT,name_full TEXT,inn TEXT)")
    organizations.astype(str).to_sql('organization', con=cnx, index= False, if_exists='append')
    return str(len(organizations))

# print(update_organization(lite_db, connecting_string))

# Обновить типы ТС
def update_vehicle_types(lite_db, connecting_string):
    engine = create_engine(connecting_string + 'dictionary')
    sql_query = 'SELECT uuid, name FROM public.vehicle_types WHERE deleted_at is NULL'
    vehicle_types = pd.read_sql_query(sql_query,con=engine)
    print('Получено из PGSQL: ' + str(len(vehicle_types)) + ' типов ТС')
    cnx = sqlite3.connect(lite_db)
    cur = cnx.cursor()
    try:
        cur.execute("DROP TABLE vehicle_types")
    except:
        cur.execute("CREATE TABLE vehicle_types(uuid TEXT,name TEXT)")
    vehicle_types.astype(str).to_sql('vehicle_types', con=cnx, index= False, if_exists='append')
    return str(len(vehicle_types))

# print(update_vehicle_types(lite_db, connecting_string))

# Обновить таблицу bnso
def update_bnso(lite_db, connecting_string):
    engine = create_engine(connecting_string + 'vehicles')
    sql_query = 'SELECT uuid, bnso_number FROM public.bnso WHERE deleted_at is NULL'
    bnso = pd.read_sql_query(sql_query,con=engine)
    print('Получено из PGSQL: ' + str(len(bnso)) + ' БНСО')
    cnx = sqlite3.connect(lite_db)
    cur = cnx.cursor()
    try:
        cur.execute("DROP TABLE bnso")
    except:
        cur.execute("CREATE TABLE bnso(uuid TEXT,bnso_number TEXT)")
    bnso.astype(str).to_sql('bnso', con=cnx, index= False, if_exists='append')
    return str(len(bnso))
# print(update_bnso(lite_db, connecting_string))

# Обновить таблицу модели ТС
def update_vehicle_models(lite_db, connecting_string):
    engine = create_engine(connecting_string + 'dictionary')
    sql_query = 'SELECT uuid, name FROM public.vehicle_models WHERE deleted_at is NULL'
    vehicle_models = pd.read_sql_query(sql_query,con=engine)
    print('Получено из PGSQL: ' + str(len(vehicle_models)) + ' моделей ТС')
    cnx = sqlite3.connect(lite_db)
    cur = cnx.cursor()
    try:
        cur.execute("DROP TABLE vehicle_models")
    except:
        cur.execute("CREATE TABLE vehicle_models(uuid TEXT,name TEXT)")
    vehicle_models.astype(str).to_sql('vehicle_models', con=cnx, index= False, if_exists='append')
    return str(len(vehicle_models))
# print(update_vehicle_models(lite_db, connecting_string))

# Обновить таблицу марки ТС
def update_vehicle_marks (lite_db, connecting_string):
    engine = create_engine(connecting_string + 'dictionary')
    sql_query = 'SELECT uuid, name FROM public.vehicle_marks WHERE deleted_at is NULL'
    vehicle_marks = pd.read_sql_query(sql_query,con=engine)
    print('Получено из PGSQL: ' + str(len(vehicle_marks)) + ' марок ТС')
    cnx = sqlite3.connect(lite_db)
    cur = cnx.cursor()
    try:
        cur.execute("DROP TABLE vehicle_marks")
    except:
        cur.execute("CREATE TABLE vehicle_marks(uuid TEXT,name TEXT)")
    vehicle_marks.astype(str).to_sql('vehicle_marks', con=cnx, index= False, if_exists='append')
    return str(len(vehicle_marks))
# print(update_vehicle_marks(lite_db, connecting_string))

# Обновить таблицу БНСО-ТС
def update_bnso2vehicles (lite_db, connecting_string):
    engine = create_engine(connecting_string + 'vehicles')
    sql_query = 'SELECT bnso_uuid, vehicle_uuid FROM public.bnso2vehicles WHERE deleted_at is NULL'
    bnso2vehicles = pd.read_sql_query(sql_query,con=engine)
    print('Получено из PGSQL: ' + str(len(bnso2vehicles)) + ' соответствий ТС - БНСО')
    cnx = sqlite3.connect(lite_db)
    cur = cnx.cursor()
    try:
        cur.execute("DROP TABLE bnso2vehicles")
    except:
        cur.execute("CREATE TABLE bnso2vehicles(bnso_uuid TEXT,vehicle_uuid TEXT)")
    bnso2vehicles.astype(str).to_sql('bnso2vehicles', con=cnx, index= False, if_exists='append')
    return str(len(bnso2vehicles))
# print(update_bnso2vehicles(lite_db, connecting_string))

# Обновить таблицу ТС
def update_vehicles(lite_db, connecting_string):
    engine = create_engine(connecting_string + 'vehicles')
    sql_query = 'SELECT uuid,' \
                'state_number, \
                vehicle_type_uuid, \
                release_year, \
                vin, \
                vehicle_mark_uuid, \
                current_bnso_uuid, \
                unit_uuid, component, \
                vehicle_model_uuid, \
                idle_time, \
                status_change_time,paid, \
                vehicle_capacity_integer \
                FROM public.vehicles WHERE deleted_at is NULL AND current_bnso_uuid is not NULL'

    vehicles = pd.read_sql_query(sql_query,con=engine)

    print('Получено из PGSQL: ' + str(len(vehicles)) + ' ТС из реестра')
    cnx = sqlite3.connect(lite_db)
    cur = cnx.cursor()
    try:
        cur.execute("DROP TABLE vehicles")
    except:
        cur.execute("CREATE TABLE vehicles(uuid TEXT,state_number TEXT,\
    vehicle_type_uuid TEXT,release_year INTEGER,vin TEXT,\
    vehicle_mark_uuid TEXT,current_bnso_uuid TEXT,unit_uuid TEXT,\
    component TEXT,vehicle_model_uuid TEXT,idle_time INTEGER,status_change_time TEXT,\
    paid TEXT,vehicle_capacity_integer TEXT)")
    vehicles.astype(str).to_sql('vehicles', con=cnx, index= False, if_exists='append')
    return str(len(vehicles))
# print(update_vehicles(lite_db, connecting_string))
















