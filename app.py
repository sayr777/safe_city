import os
import json
import flask
from flask import abort
from flask import Flask
from sqllite import get_vehicles_dic
from sqllite import get_t_by_device
from sqllite import get_t_by_org
from sqllite import get_all_t
app = Flask(__name__)

from update_local_db import update_organization
from update_local_db import update_vehicle_types
from update_local_db import update_bnso
from update_local_db import update_vehicle_models
from update_local_db import update_vehicle_marks
from update_local_db import update_bnso2vehicles
from update_local_db import update_vehicles

import dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

# DEBUG_METRICS = os.environ['DEBUG_METRICS']
PROMETHEUS_PORT = os.environ['PROMETHEUS_PORT']
# DEBUG_METRICS = os.environ['DEBUG_METRICS']

from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app=None, path='/metrics')

gRPC_URL = os.environ['gRPC_URL']
print(" * gRPC_URL: %s" % gRPC_URL)

pSQL_URL = os.environ['pSQL_URL']
print(" * pSQL_URL: %s" % pSQL_URL)

API_TOKEN = os.environ['API_TOKEN']
print(" * API_TOKEN: %s" % API_TOKEN)

pSQL_URL = os.environ['pSQL_URL']
print(" * PGSQL_URL: %s" % pSQL_URL)

lite_db = 'vehicles.db'

#Метод получения информации о сервере
@app.route('/info/<path:token>')
def hello(token):
    if token == API_TOKEN:
        from flask import render_template
        # return 'ok'
        return flask.Response(
            status=200,
            mimetype=("application/json; charset=utf-8"),
            response="{'info': 'API интеграциии РНИС Нижегородской области с АПК Безопасный город'}")
    else:
        return flask.Response(
            status=403,
            mimetype=("application/json; charset=utf-8"),
            response="'[{\"error\":\"7\"},\n {\"info\": \"Предоставлен некорректный ключ\"}]'")

#Метод обновления справочников ТС, огранизаций, типов ТС, БНСО
@app.route('/v.1/update_dics/<path:token>', methods=['GET'])
def update_dics(token):
    if token == API_TOKEN:
        response_ = {}
        response_['обновлено организаций'] = update_organization(lite_db, pSQL_URL)
        response_['обновлено типов ТС'] = update_vehicle_types(lite_db, pSQL_URL)
        response_['обновлено БНСО'] = update_bnso(lite_db, pSQL_URL)
        response_['обновлено моделей ТС'] = update_vehicle_models(lite_db, pSQL_URL)
        response_['обновлено марок ТС'] = update_vehicle_marks (lite_db, pSQL_URL)
        response_['обновлено связок ТС-БНСО'] = update_bnso2vehicles (lite_db, pSQL_URL)
        response_['обновлено ТС'] = update_vehicles (lite_db, pSQL_URL)
        return response_
    else :
        return flask.Response(
            status=403,
            mimetype=("application/json; charset=utf-8"),
            response="'[{\"error\":\"7\"},\n {\"info\": \"Предоставлен некорректный ключ\"}]'")

#Метод получения словаря ТС
@app.route('/v.1/vehicles_dic/<path:token>', methods=['GET'])
def get_vehicles(token):
    if token == API_TOKEN:
        return flask.Response(
            status=200,
            mimetype=("application/json; charset=utf-8"),
            response=json.dumps(get_vehicles_dic(lite_db)))
    else :
        return flask.Response(
            status=403,
            mimetype=("application/json; charset=utf-8"),
            response="'[{\"error\":\"7\"},\n {\"info\": \"Предоставлен некорректный ключ\"}]'")

#Метод получения последнего телематического сообщения по DeviceCode
@app.route('/v.1/messages/idDev:<path:idDev>/<path:token>', methods=['GET'])
def get_telematics_by_device(idDev,token):
    if idDev == '':
        abort(404)
    if token == API_TOKEN:
        return flask.Response(
            status=200,
            mimetype=("application/json; charset=utf-8"),
            response=json.dumps(get_t_by_device(idDev,gRPC_URL)))


    else :
        return flask.Response(
            status=403,
            mimetype=("application/json; charset=utf-8"),
            response="'[{\"error\":\"7\"},\n {\"info\": \"Предоставлен некорректный ключ\"}]'")

#Метод получения телематических сообщений по uuid предприятия
@app.route('/v.1/messages/idOrg:<path:idOrg>/<path:token>', methods=['GET'])
def get_telematics_by_org(idOrg,token):
    if idOrg == '':
        abort(404)
    if token == API_TOKEN:
        return flask.Response(
            status=200,
            mimetype=("application/json; charset=utf-8"),
            response=json.dumps(get_t_by_org(idOrg,gRPC_URL)))

    else :
        return flask.Response(
            status=403,
            mimetype=("application/json; charset=utf-8"),
            response="'[{\"error\":\"7\"},\n {\"info\": \"Предоставлен некорректный ключ\"}]'")

#Метод получения телематических сообщений по uuid предприятия
@app.route('/v.1/messages/all/<path:token>', methods=['GET'])
def get_telematics_all(token):

    if token == API_TOKEN:
        return flask.Response(
            status=200,
            mimetype=("application/json; charset=utf-8"),
            response=json.dumps(get_all_t(gRPC_URL)))

    else :
        return flask.Response(
            status=403,
            mimetype=("application/json; charset=utf-8"),
            response="'[{\"error\":\"7\"},\n {\"info\": \"Предоставлен некорректный ключ\"}]'")

if __name__ == '__main__':
    metrics.init_app(app)
    app.run(debug=True, host='0.0.0.0', port=8891)
