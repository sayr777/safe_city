from sqllite import get_vehicles_dic
from sqllite import get_t_by_device
from sqllite import get_t_by_org
import json
from flask import abort
from flask import Flask
app = Flask(__name__)


# app.run()
@app.route('/')
def hello():
    return 'API интеграциии РНИС Нижегородской области с АПК "Безопасный город"'

#Метод обновления справочников ТС, огранизаций, типов ТС, БНСО
@app.route('/v.1/update_dics', methods=['GET'])
def update_dics():
    return 'Ок'

#Метод получения словаря ТС
@app.route('/v.1/vehicles_dic', methods=['GET'])
def get_vehicles():
    return json.dumps(get_vehicles_dic())


#Метод получения последнего телематического сообщения по DeviceCode
@app.route('/v.1/messages/idDev:<path:idDev>', methods=['GET'])
def get_telematics_by_device(idDev):
    if idDev == '':
        abort(404)
    return get_t_by_device(idDev)


#Метод получения телематических сообщений по uuid предприятия
@app.route('/v.1/messages/idOrg:<path:idOrg>', methods=['GET'])
def get_telematics_by_org(idOrg):
    if idOrg == '':
        abort(404)
    return get_t_by_device(idOrg)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)