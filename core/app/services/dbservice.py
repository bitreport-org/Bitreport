# -*- coding: utf-8 -*-
import time
import config
import logging

from influxdb import InfluxDBClient
from sqlalchemy import Column, String, Integer, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import  url

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


Base = declarative_base()
Conf = config.BaseConfig()

def connect_influx():
    # Wait for connection to InfluxDB
    status = True
    while status:
        try:
            client = InfluxDBClient(Conf.HOST, Conf.PORT, 'root', 'root', Conf.DBNAME)
            client.create_database(Conf.DBNAME)
            status = False
        except:
            print('Waiting for InfluxDB...')
            time.sleep(4)
    return client


class Chart(Base):
    __tablename__ = Conf.CHART_TABLE
    id = Column(Integer, primary_key=True, autoincrement=True)
    pair = Column(String)
    timeframe = Column(String)
    last_tsmp = Column(Integer)
    type = Column(String)
    params = Column(JSON)


class Level(Base):
    __tablename__ = Conf.LVL_TABLE
    id = Column(Integer, primary_key=True, autoincrement=True)
    pair = Column(String)
    timeframe = Column(String)
    tsmp = Column(Integer)
    type = Column(String)
    value = Column(Integer, index=True, unique=True)


def prepare_postgres():
    print('Preparing database')

    # Postgres setup
    con = connect(user=Conf.POSTGRES_USER, host=Conf.POSTGRES_USER, dbname='postgres')
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    cur.execute(f"select exists( \
                SELECT datname FROM pg_catalog.pg_database WHERE lower(datname) = lower('{Conf.POSTGRES_DATABSE}') \
                );")
    status, = cur.fetchone()

    if not status:
        cur.execute(f'CREATE DATABASE {Conf.POSTGRES_DATABSE}')
        logging.info(f'Database {Conf.POSTGRES_DATABSE} created')
    else:
        logging.info(f'Database {Conf.POSTGRES_DATABSE} already exists')

    # cur.execute('DROP TABLE IF EXISTS charting;')
    cur.close()
    con.close()

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


