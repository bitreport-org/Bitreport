# -*- coding: utf-8 -*-
import logging
import traceback
import config

from flask import Flask, request, jsonify
from core.services import dbservice, dataservice, exchanges

app = Flask(__name__)

# Logger
logging.basicConfig(level=logging.DEBUG,
                    filename='app.log',
                    format='%(asctime)s - core - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - core - %(levelname)s - %(message)s')
console.setFormatter(formatter)
app.logger.addHandler(console)


# Config
conf = config.BaseConfig()
dbservice.connect_influx(app)
dbservice.prepare_postgres()


# API
@app.route('/<pair>', methods=['GET'])
def data_service(pair: str):
    if request.method == 'GET':
        timeframe = request.args.get('timeframe', default='1h', type=str)
        limit = request.args.get('limit', default=15, type=int)
        untill = request.args.get('untill', default=None, type=int)

        app.logger.info(f'Request for {pair} {timeframe} limit {limit} untill {untill}')

        data = dataservice.PairData(app, pair, timeframe, limit, untill)
        output, code = data.prepare()

        return jsonify(output), code
    else:
        return 404


@app.route('/exchange', methods=['GET'])
def exchange_service():
    if request.method == 'GET':
        pair = request.args.get('pair', default='BTCUSD', type=str)
        exchange = exchanges.check_exchange(pair)
        return jsonify(exchange)
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
                return exchanges.pair_fill(app, pair, exchange, force)
            except:
                app.logger.warning(traceback.format_exc())
                return 'Request failed', 500
        else:
            return 'Pair or exchange not provided', 500
    else:
        return 404


@app.route("/")
def hello():
    return "Wrong place, is it?"
