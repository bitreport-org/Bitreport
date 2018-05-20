# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import time
import logging
import traceback
from influxdb import InfluxDBClient

# Internal import
from core.services import dbservice, dataservice
import config

app = Flask(__name__)

# Logger
handler = logging.FileHandler('app.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)


# Config
conf = config.BaseConfig()

# Wait for connection to InfluxDB
status = True
while status:
    try:
        client = InfluxDBClient(conf.HOST, conf.PORT, 'root', 'root', conf.DBNAME)
        client.create_database(conf.DBNAME)
        status = False
    except:
        app.logger.warning('Waiting for InfluxDB...')
        time.sleep(4)

# API

@app.route('/<pair>', methods=['GET'])
def data_service(pair: str):
    if request.method == 'GET':
        timeframe = request.args.get('timeframe', default='1h', type=str)
        limit = request.args.get('limit', default=15, type=int)
        untill = request.args.get('untill', default=None, type=int)

        app.logger.warning('Request for {} {} limit {} untill {}'.format(pair, timeframe, limit, untill))

        data = dataservice.PairData(app, pair, timeframe, limit, untill)
        output, code = data.prepare()

        return jsonify(output), code
    else:
        return 404


events_list = []
@app.route('/events', methods=['GET'])
def event_service():
    if request.method == 'GET':
        return jsonify(events_list)
    else:
        return 404


@app.route('/fill', methods=['POST'])
def fill_service():
    if request.method == 'POST':
        pair = request.args.get('pair', default=None, type=str)
        force = request.args.get('force', default=False, type=bool)
        exchange = request.args.get('exchange', default=None, type=str)

        if pair and exchange:
            try:
                return dbservice.pair_fill(app, pair, exchange, force)
            except:
                app.logger.warning(traceback.format_exc())
                return 'Request failed', 500
        else:
            return 'Pair or exchange not provided', 500
    else:
        return 404


@app.route('/log', methods=['GET'])
def log_service():
    if request.method == 'GET':
        try:
            with open('app.log') as log:
                text = ""
                for i, line in enumerate(log):
                    text += line
            return '<pre>{}</pre>'.format(text)
        except:
            return 'No logfile', 500
    else:
        return 404


@app.route("/")
def hello():
    return "Wrong place, is it?"
