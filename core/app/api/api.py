# -*- coding: utf-8 -*-
from logging.config import dictConfig
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config):
    """
    Creates BitReport core flask app.

    :param config: configuration object
    :return: flask.Flask app
    """
    from app.services import data_factory, sentry_setup
    from app.exchanges import fill_pair
    from .database import connect_influx

    # Configure app
    dictConfig(config.LOGGER)
    app = Flask(__name__)
    app.config.from_object(config)
    app.logger.info('Welcome to BitReport core!')

    # Sentry setup
    if sentry_setup(config.SENTRY):
        app.logger.info('Sentry is up and running.')

    # Postgres and influx connections
    with app.app_context():
        db.init_app(app)
        db.create_all()

    influx = connect_influx(config.INFLUX)

    # API
    @app.route('/<pair>', methods=['GET'])
    def pair_service(pair: str):
        """
        Main API endpoint. For a given pair it returns response
        with last price, ta and other magic stuff

        :param pair: pair name ex. 'BTCUSD'
        :return: json
        """
        timeframe = request.args.get('timeframe', default=None, type=str)
        limit = request.args.get('limit', default=15, type=int)

        if not timeframe:
            return jsonify(msg='Timeframe not provided'), 404

        data = data_factory.PairData(influx, pair, timeframe, limit)
        output, code = data.prepare()

        return jsonify(output), code


    @app.route('/fill', methods=['POST'])
    def fill_service():
        """
        Endpoint which enables data filling. After a request data
        is retrieved from exchanges and inserted to database.

        In case of a success it returns msg with information about from
        which exchanges data was fetched.

        Otherwise an it returns error message and code of 404.

        :return:
        """
        pair = request.args.get('pair', default=None, type=str)

        if not pair:
            return jsonify(msg='Pair not provided'), 404

        msg, code = fill_pair(influx, pair)
        return jsonify(msg=msg), code


    @app.route("/")
    def hello():
        """
        Test enpoint to check if app is on and working.

        :return:
        """
        return jsonify(msg="Wrong place, is it?")

    return app
