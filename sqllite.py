import sqlite3

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
    for row in cursor.execute("SELECT * FROM vehicles"):
        vehicles.append({
            'id': row[0],
            'idDev' : row[23],
            'name' : row[1],
            'groupname': row[27],
            'groupid' : row[27],
            'createts' : row[11],
            'markats' : row[4],
            'typets': row[5],
            'gosnumber' : row[1],
            'vin' : row[12],
            'color' : '',
            'org_id' : row[3],
            'org_name' : row[4],
            'org_inn' : row[5]
        })

    return vehicles

def get_t_by_device(idDev):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    sql = "SELECT * FROM vehicles WHERE uuid=?"
    cursor.execute(sql, [(idDev)])
    response = cursor.fetchall()
    tmessage = ({
        'id': response[0][0],
        'idDev': response[0][2],
        'name': response[0][1],
        'groupname': response[0][27],
        'groupid': response[0][27],
        'createts': response[0][11],
        'markats': response[0][4],
        'typets': response[0][5],
        'gosnumber': response[0][1],
        'vin': response[0][12],
        'color': '',
        'org_id': response[0][3],
        'org_name': response[0][4],
        'org_inn': response[0][5]
    })
    #

    return tmessage


def get_t_by_org(idOrg):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    sql = "SELECT * FROM vehicles WHERE uuid=?"
    cursor.execute(sql, [(idOrg)])
    response = cursor.fetchall()
    tmessage = ({
        'id': response[0][0],
        'idDev': response[0][2],
        'name': response[0][1],
        'groupname': response[0][27],
        'groupid': response[0][27],
        'createts': response[0][11],
        'markats': response[0][4],
        'typets': response[0][5],
        'gosnumber': response[0][1],
        'vin': response[0][12],
        'color': '',
        'org_id': response[0][3],
        'org_name': response[0][4],
        'org_inn': response[0][5]
    })
    #

    return tmessage

# print(get_telematics ('736f7282-97bb-11e7-bd68-42caec24dbaf'))


