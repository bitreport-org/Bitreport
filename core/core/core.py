# -*- coding: utf-8 -*-
import traceback
import config
from logging.config import dictConfig

from flask import Flask, request, jsonify
from core.services import dbservice, dataservice, exchanges

# Sentry setup
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


# Config
conf = config.BaseConfig
dictConfig(conf.LOGGER)

print('Prod setup: ', conf.PROD, type(conf.PROD), conf.PROD==True)

if conf.PROD:
    sentry_sdk.init(
        dsn="https://000bf6ba6f0f41a6a1cbb8b74f494d4a@sentry.io/1359679",
        integrations=[FlaskIntegration()]
    )


app = Flask(__name__)

# DB connections
dbservice.connect_influx()
dbservice.prepare_postgres()


# API
@app.route('/<pair>', methods=['GET'])
def data_service(pair: str):
    if request.method == 'GET':
        timeframe = request.args.get('timeframe', default='1h', type=str)
        limit = request.args.get('limit', default=15, type=int)
        untill = request.args.get('untill', default=None, type=int)

        data = dataservice.PairData(pair, timeframe, limit, untill)
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
                return exchanges.pair_fill(pair, exchange, force)
            except:
                app.logger.error(f'Fill failed: {traceback.format_exc()}')
                return 'Request failed', 500
        else:
            return 'Pair or exchange not provided', 500
    else:
        return 404


@app.route("/")
def hello():
    return "Wrong place, is it?"
