# -*- coding: utf-8 -*-
import time
import traceback
from logging.config import dictConfig
from typing import Type

from flask import Flask, g, jsonify, request
from flask.logging import default_handler

from app.api.admin import configure_admin
from app.api.logger import create_msg, sentry_init
from app.models import db, Chart, Event
from config import BaseConfig


def create_app(config: Type[BaseConfig]) -> Flask:
    """
    Creates BitReport core flask app.
    """

    from app.ta import data_factory
    from app.exchanges import fill_pair

    # Configure app
    dictConfig(config.LOGGER)
    app = Flask(__name__, template_folder="../../templates")
    app.config.from_object(config)  # pylint:disable=no-member
    app.logger.removeHandler(default_handler)  # pylint:disable=no-member

    # Configure flask admin
    configure_admin(app, active=config.ADMIN_ENABLED)

    # Sentry setup
    sentry_init(app)

    # Postgres and influx connections
    with app.app_context():
        db.init_app(app)
        db.create_all()

    @app.shell_context_processor
    def make_shell_context():  # pylint:disable=unused-variable
        return dict(app=app, db=db, Chart=Chart, Event=Event)

    # API
    @app.before_request
    def request_timer():  # pylint:disable=unused-variable
        g.start = time.time()

    @app.after_request
    def request_log(response):  # pylint:disable=unused-variable
        app.logger.info(create_msg(response))  # pylint:disable=no-member
        return response

    @app.route("/<pair>", methods=["GET"])
    def pair_service(pair: str):  # pylint:disable=unused-variable
        """
        Main API endpoint. For a given pair it returns response
        with last price, ta and other magic stuff

        Parameters
        ----------
        pair : pair name ex. 'BTCUSD'
        """
        timeframe = request.args.get("timeframe", default=None, type=str)
        limit = request.args.get("limit", default=20, type=int)
        last_timestamp = request.args.get("last_timestamp", default=None, type=int)

        if not timeframe:
            return jsonify(msg="Timeframe not provided"), 400

        if timeframe not in ["1h", "2h", "3h", "6h", "12h", "24h"]:
            return jsonify(msg="Wrong timeframe."), 400

        data = data_factory.PairData(pair, timeframe, limit, last_timestamp)
        output, code = data.prepare()

        return jsonify(output), code

    @app.route("/fill", methods=["POST"])
    def fill_service():  # pylint:disable=unused-variable
        """
        Endpoint which enables data filling. After a request data
        is retrieved from exchanges and inserted to database.

        In case of a success it returns msg with information about from
        which exchanges data was fetched.

        Otherwise an it returns error message and code of 400.
        """
        pair = request.args.get("pair", default=None, type=str)

        if not pair:
            return jsonify(msg="Pair not provided"), 400

        msg, code = fill_pair(pair)
        return jsonify(msg=msg), code

    @app.route("/")
    def hello():  # pylint:disable=unused-variable
        """
        Test endpoint to check if app is on and working.
        """
        return jsonify(msg="Wrong place, is it?")

    @app.errorhandler(404)
    def not_found_error(error):  # pylint:disable=unused-variable,unused-argument
        return jsonify(msg="Wrong place!"), 404

    @app.errorhandler(500)
    def internal_error(error):  # pylint:disable=unused-variable
        db.session.rollback()
        exc_info = traceback.format_exc()
        app.logger.error(error, exc_info=exc_info)  # pylint:disable=no-member

        return jsonify(msg="Server is dead", error=str(error)), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):  # pylint:disable=unused-variable
        db.session.rollback()
        exc_info = traceback.format_exc()
        app.logger.error(error, exc_info=exc_info)  # pylint:disable=no-member

        return jsonify(msg="Unhandled exception", error=str(error)), 500

    return app
