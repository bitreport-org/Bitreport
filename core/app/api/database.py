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
    Creates Chart.

    Parameters
    ----------
    pair: pair name ex. 'BTCUSD'
    timeframe: timeframe ex. '1h'
    type: name of charting setup
    params: params of the setup
    """
    __tablename__ = 'charting'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pair = db.Column(db.String)
    timeframe = db.Column(db.String)
    time = db.Column(db.DateTime, default=db.func.current_timestamp())
    type = db.Column(db.String)
    params = db.Column(db.JSON)


class Level(db.Model):
    """
    Creates Level.

    Parameters
    ----------
    pair: pair name ex. 'BTCUSD'
    timeframe: timeframe ex. '1h'
    type: name of level type
    value: value of the level
    """
    __tablename__ = 'levels'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pair = db.Column(db.String)
    timeframe = db.Column(db.String)
    time = db.Column(db.DateTime, default=db.func.current_timestamp())
    type = db.Column(db.String)
    value = db.Column(db.Integer, index=True, unique=True)

