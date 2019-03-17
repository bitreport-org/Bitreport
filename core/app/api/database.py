# -*- coding: utf-8 -*-
import time
import logging
from influxdb import InfluxDBClient
from .api import db


def connect_influx(INFLUX):
    # Wait for a connection to InfluxDB
    status = True
    while status:
        try:
            #TODO: check retries option: number of retries your client will try before aborting
            client = InfluxDBClient(**INFLUX)
            client.create_database(INFLUX['database'])
            status = False
            logging.info('Successfully connected to InfluxDB.')
        except:
            logging.info('Waiting for InfluxDB...')
            time.sleep(3)
    return client


class Chart(db.Model):
    __tablename__ = 'charting'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pair = db.Column(db.String)
    timeframe = db.Column(db.String)
    last_tsmp = db.Column(db.Integer)
    type = db.Column(db.String)
    params = db.Column(db.JSON)

    def __init__(self, pair, timeframe, type, params):
        self.pair = pair
        self.timeframe = timeframe
        self.last_tsmp = int(time.time())
        self.type = type
        self.params = params


class Level(db.Model):
    __tablename__ = 'levels'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pair = db.Column(db.String)
    timeframe = db.Column(db.String)
    tsmp = db.Column(db.Integer)
    type = db.Column(db.String)
    value = db.Column(db.Integer, index=True, unique=True)

    def __init__(self, pair, timeframe, last_tsmp, type, value):
        self.pair = pair
        self.timeframe = timeframe
        self.last_tsmp = last_tsmp
        self.type = type
        self.value = value

