# -*- coding: utf-8 -*-
import time
import logging
from influxdb import InfluxDBClient

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_influx(kwargs: dict, retries: int = 10) -> InfluxDBClient:
    """
    Using input params establishes connection to influxDB and creates a database.

    Parameters
    ----------
    kwargs: influx.InfluxDBClient kwargs
    retries: number of retries

    Returns
    -------
    client: influx.InfluxDBClient
    """
    # Wait for a connection to InfluxDB
    client = InfluxDBClient(**kwargs)
    success = False

    i = 0
    while i < retries:
        try:
            client.create_database(kwargs['database'])
            logging.info('Successfully connected to InfluxDB.')
            success = True
            break
        except:
            i += 1
            logging.info('Waiting for InfluxDB...')
            time.sleep(3)

    if not success:
        raise ValueError('Max retries exceeded, could not connect to InfluxDB!')

    return client


class Chart(db.Model):
    """
    Model of a Chart instance.
    """
    __tablename__ = 'charting'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pair = db.Column(db.String)
    timeframe = db.Column(db.String)
    last_tsmp = db.Column(db.Integer)
    type = db.Column(db.String)
    params = db.Column(db.JSON)

    def __init__(self, pair: str, timeframe: str, type: str, params: dict):
        """"""
        """
        Creates Chart.

        Parameters
        ----------
        pair: pair name ex. 'BTCUSD'
        timeframe: timeframe ex. '1h'
        type: name of charting setup
        params: params of the setup
        """
        self.pair = pair
        self.timeframe = timeframe
        self.last_tsmp = int(time.time())
        self.type = type
        self.params = params


class Level(db.Model):
    """
    Model of a Level instance.
    """
    __tablename__ = 'levels'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pair = db.Column(db.String)
    timeframe = db.Column(db.String)
    tsmp = db.Column(db.Integer)
    type = db.Column(db.String)
    value = db.Column(db.Integer, index=True, unique=True)

    def __init__(self, pair: str, timeframe: str, type: str, value: float):
        """
        Creates Level.

        Parameters
        ----------
        pair: pair name ex. 'BTCUSD'
        timeframe: timeframe ex. '1h'
        type: name of level type
        value: value of the level
        """
        self.pair = pair
        self.timeframe = timeframe
        self.tsmp = int(time.time())
        self.type = type
        self.value = value

