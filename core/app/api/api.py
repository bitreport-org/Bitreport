# -*- coding: utf-8 -*-
import config
from logging.config import dictConfig
from flask import Flask, request, jsonify

from app.services import sentry_up, prepare_postgres, connect_influx, dataservice
import app.exchanges as exchanges

# Setup logger
dictConfig(config.BaseConfig.LOGGER)

def create_app():
    # DB connections
    influx = connect_influx()
    prepare_postgres()

    app = Flask(__name__)
    app.logger.info('Welcome to BitReport core!')

    # Enable Sentry in production
    sentry_up(app.config['ENV'])

    # API
    @app.route('/<pair>', methods=['GET'])
    def data_service(pair: str):
        timeframe = request.args.get('timeframe', default='1h', type=str)
        limit = request.args.get('limit', default=15, type=int)
        untill = request.args.get('untill', default=None, type=int)

        data = dataservice.PairData(influx, pair, timeframe, limit, untill)
        output, code = data.prepare()

        return jsonify(output), code


    @app.route('/exchange', methods=['GET'])
    def exchange_service():
        pair = request.args.get('pair', default='BTCUSD', type=str)
        exchange, code = exchanges.check_exchange(influx, pair)
        return jsonify(exchange), code


    @app.route('/fill', methods=['POST'])
    def fill_service():
        pair = request.args.get('pair', default=None, type=str)
        exchange = request.args.get('exchange', default=None, type=str)

        if not pair or not exchange:
            return jsonify(msg='Pair or exchange not provided'), 404

        msg, code = exchanges.fill_pair(influx, pair, exchange)
        return jsonify(msg=msg), code


    @app.route("/")
    def hello():
        return jsonify(msg="Wrong place, is it?")

    return app