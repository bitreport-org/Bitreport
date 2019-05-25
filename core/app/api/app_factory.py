# -*- coding: utf-8 -*-
import time
import traceback
from typing import Type
from flask import Flask, request, jsonify, g
from flask.logging import default_handler
from logging.config import dictConfig

from config import BaseConfig
from .database import db, influx_db
from .admin import configure_admin
from .logger import create_msg, sentry_init


def create_app(config: Type[BaseConfig]) -> Flask:
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

    from app.utils import data_factory
    from app.exchanges import fill_pair

    # Configure app
    dictConfig(config.LOGGER)
    app = Flask(__name__, template_folder='../../templates')
    app.config.from_object(config)
    app.logger.removeHandler(default_handler)

    # Configure flask admin
    configure_admin(app, active=config.ADMIN_ENABLED)

    # Sentry setup
    sentry_init(app)

    # Postgres and influx connections
    with app.app_context():
        influx_db.init_app(app)
        influx_db.database.create(config.INFLUXDB_DATABASE)

        db.init_app(app)
        db.create_all()


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
        """
        timeframe = request.args.get('timeframe', default=None, type=str)
        limit = request.args.get('limit', default=20, type=int)

        if not timeframe:
            return jsonify(msg='Timeframe not provided'), 400

        if timeframe not in ['1h', '2h', '3h', '6h', '12h', '24h']:
            return jsonify(msg='Wrong timeframe.'), 400

        data = data_factory.PairData(pair, timeframe, limit)
        output, code = data.prepare()

        return jsonify(output), code

    @app.route('/fill', methods=['POST'])
    def fill_service():
        """
        Endpoint which enables data filling. After a request data
        is retrieved from exchanges and inserted to database.

        In case of a success it returns msg with information about from
        which exchanges data was fetched.

        Otherwise an it returns error message and code of 400.
        """
        pair = request.args.get('pair', default=None, type=str)

        if not pair:
            return jsonify(msg='Pair not provided'), 400

        msg, code = fill_pair(pair)
        return jsonify(msg=msg), code

    @app.route("/")
    def hello():
        """
        Test endpoint to check if app is on and working.
        """
        return jsonify(msg="Wrong place, is it?")

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify(msg='Wrong place!'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        exc_info = traceback.format_exc()
        app.logger.exception(error, exc_info=exc_info)

        return jsonify(msg='Server is dead',
                       error=str(error)), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        db.session.rollback()
        exc_info = traceback.format_exc()
        app.logger.exception(error, exc_info=exc_info)

        return jsonify(msg='Unhandled exception',
                       error=str(error)), 500

    return app
