# -*- coding: utf-8 -*-
from config import BaseConfig
from logging.config import dictConfig
from flask import Flask, request, jsonify

from app.services import sentry_up, prepare_postgres, connect_influx, data_service
from app.exchanges import fill_pair

# Setup logger
dictConfig(BaseConfig.LOGGER)

def create_app():
    app = Flask(__name__)
    app.logger.info('Welcome to BitReport core!')
    ENV = app.config['ENV']

    # DB connections and Sentry setup
    influx = connect_influx()
    prepare_postgres()
    sentry_up(ENV)

    # API
    @app.route('/<pair>', methods=['GET'])
    def pair_service(pair: str):
        timeframe = request.args.get('timeframe', default='1h', type=str)
        limit = request.args.get('limit', default=15, type=int)

        data = data_service.PairData(influx, pair, timeframe, limit)
        output, code = data.prepare()

        return jsonify(output), code


    @app.route('/fill', methods=['POST'])
    def fill_service():
        pair = request.args.get('pair', default=None, type=str)

        if not pair:
            return jsonify(msg='Pair not provided'), 404

        msg, code = fill_pair(influx, pair)
        return jsonify(msg=msg), code


    @app.route("/")
    def hello():
        return jsonify(msg="Wrong place, is it?")

    return app
