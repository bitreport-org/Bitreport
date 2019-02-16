# -*- coding: utf-8 -*-
import config
from logging.config import dictConfig
from flask import Flask, request, jsonify

from app.services import sentry_up, prepare_postgres, connect_influx, dataservice
from app.exchanges import fill_pair

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

        data = dataservice.PairData(influx, pair, timeframe, limit)
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
