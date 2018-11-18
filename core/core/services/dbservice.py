# -*- coding: utf-8 -*-
import time
import traceback
import config

from influxdb import InfluxDBClient
from sqlalchemy import Column, String, Integer, JSON, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
Conf = config.BaseConfig()

def connect_influx(app):
    # Wait for connection to InfluxDB
    status = True
    while status:
        try:
            client = InfluxDBClient(Conf.HOST, Conf.PORT, 'root', 'root', Conf.DBNAME)
            client.create_database(Conf.DBNAME)
            status = False
        except:
            app.logger.info('Waiting for InfluxDB...')
            time.sleep(4)


class Chart(Base):
    __tablename__ = Conf.CHART_TABLE
    id = Column(Integer, primary_key = True)
    timestamp = Column(Integer)
    pair = Column(String)
    timeframe = Column(String)
    type = Column(String)
    params = Column(JSON)


def prepare_postgres():
    # Postgres setup
    db_uri = Conf.POSTGRES_URI
    engine = create_engine(db_uri)
    # sql = 'DROP TABLE IF EXISTS charting;'
    # result = engine.execute(sql)

    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)


