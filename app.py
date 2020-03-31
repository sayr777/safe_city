import os
import json
from flask import abort
from flask import Flask
from sqllite import get_vehicles_dic
from sqllite import get_t_by_device
from sqllite import get_t_by_org
app = Flask(__name__)

# import dotenv
# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
# dotenv.load_dotenv(dotenv_path)


# DEBUG_METRICS = os.environ['DEBUG_METRICS']
from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app=None, path='/metrics')


gRPC_URL = os.environ['gRPC_URL']
print(" * gRPC_URL: %s" % gRPC_URL)

pSQL_URL = os.environ['pSQL_URL']
print(" * pSQL_URL: %s" % pSQL_URL)



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
    return get_t_by_device(idDev,gRPC_URL)

#Метод получения телематических сообщений по uuid предприятия
@app.route('/v.1/messages/idOrg:<path:idOrg>', methods=['GET'])
def get_telematics_by_org(idOrg):
    if idOrg == '':
        abort(404)
    return json.dumps(get_t_by_org(idOrg,gRPC_URL))

if __name__ == '__main__':
    metrics.init_app(app)
    app.run(debug=True, host='0.0.0.0', port=8000)

