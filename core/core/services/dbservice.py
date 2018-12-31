# -*- coding: utf-8 -*-
import time
import traceback
import config

from influxdb import InfluxDBClient
from sqlalchemy import Column, String, Integer, JSON, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import url

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


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
    id = Column(Integer, primary_key=True)
    pair = Column(String)
    timeframe = Column(String)
    last_tsmp = Column(Integer)
    type = Column(String)
    params = Column(JSON)


def prepare_postgres():
    # Postgres setup
    con = connect(user=Conf.POSTGRES_USER, host=Conf.POSTGRES_USER, dbname='postgres')
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    try:
        cur.execute(f'CREATE DATABASE {Conf.POSTGRES_DATABSE}')
    except:
        pass
    cur.close()
    con.close()

    # sql = 'DROP TABLE IF EXISTS charting;'
    # result = engine.execute(sql)
    db_uri = url.URL('postgresql', username=Conf.POSTGRES_USER, host=Conf.POSTGRES_USER, database=Conf.POSTGRES_DATABSE)
    engine = create_engine(db_uri)
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

def make_session():
    db_uri = url.URL('postgresql', username=Conf.POSTGRES_USER, host=Conf.POSTGRES_USER, database=Conf.POSTGRES_DATABSE)
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session


