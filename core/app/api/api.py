# -*- coding: utf-8 -*-
from logging.config import dictConfig
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config):
    from app.services import sentry_up, data_service
    from .database import connect_influx
    from app.exchanges import fill_pair

    # Configure app
    dictConfig(config.LOGGER)
    app = Flask(__name__)
    app.logger.info('Welcome to BitReport core!')
    app.config.from_object(config)
    sentry_up(config.SENTRY)

    #  Postgres and influx connections
    db.init_app(app)
    influx = connect_influx(config.INFLUX)

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
