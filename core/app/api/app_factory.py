# -*- coding: utf-8 -*-
from logging.config import dictConfig
from flask import Flask, request, jsonify, g
import time

from .database import db
from .admin import configure_admin
from .logger import create_msg
from flask.logging import default_handler
from influxdb import InfluxDBClient


def create_app(config, influx: InfluxDBClient):
    """
    Creates BitReport core flask app.

    Parameters
    ----------
    config : configuration object
    influx: connection to influx

    Returns
    -------
    app: flask.Flask app
    """

    from app.services import data_factory, sentry_setup
    from app.exchanges import fill_pair

    # Configure app
    dictConfig(config.LOGGER)
    app = Flask(__name__)
    app.config.from_object(config)
    app.logger.removeHandler(default_handler)

    # Configure flask admin
    configure_admin(app, active=config.ADMIN_ENABLED)

    app.logger.info('Sentry is up and running.')
    # Sentry setup
    if sentry_setup(config.SENTRY):
        app.logger.info('Sentry is up and running.')

    # Postgres and influx connections
    with app.app_context():
        db.init_app(app)
        db.create_all()

    # influx = connect_influx(config.INFLUX)

    # API
    @app.before_request
    def request_timer():
        g.start = time.time()

    @app.after_request
    def request_log(response):
        app.logger.info(create_msg(response))
        return response

    @app.route('/<pair>', methods=['GET'])
    def pair_service(pair: str):
        """
        Main API endpoint. For a given pair it returns response
        with last price, ta and other magic stuff

        Parameters
        ----------
        pair : pair name ex. 'BTCUSD'

        Returns
        -------
        response
        """
        timeframe = request.args.get('timeframe', default=None, type=str)
        limit = request.args.get('limit', default=20, type=int)

        if not timeframe:
            return jsonify(msg='Timeframe not provided'), 404

        if timeframe not in ['1h', '2h', '3h', '6h', '12h', '24h']:
            return jsonify(msg='Wrong timeframe.'), 404

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

        Returns
        -------
        response
        """
        pair = request.args.get('pair', default=None, type=str)

        if not pair:
            return jsonify(msg='Pair not provided'), 404

        msg, code = fill_pair(influx, pair)
        return jsonify(msg=msg), code

    @app.route("/")
    def hello():
        """
        Test endpoint to check if app is on and working.

        Returns
        -------
        response
        """
        return jsonify(msg="Wrong place, is it?")

    @app.route('/test/bad/error')
    def error():
        x = 1/0
        return 'Error 1/0', 200

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify(msg='Wrong place!'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify(msg='Server is dead :( '), 500

    return app
