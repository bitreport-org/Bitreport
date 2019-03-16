import pytest
from influxdb import InfluxDBClient
import requests

from app.api.internal import get_function_list
from app.ta import  indicators

import config


@pytest.yield_fixture(scope='session')
def drop_influx():
    influx = InfluxDBClient('0.0.0.0',
                            5002,
                            config.Test.INFLUX_USER,
                            config.Test.INFLUX_PASSWORD,
                            config.Test.INFLUX_DBNAME)
    influx.drop_database('test')


@pytest.fixture
def influx_test():
    influx = InfluxDBClient('0.0.0.0',
                            5002,
                            config.Test.INFLUX_USER,
                            config.Test.INFLUX_PASSWORD,
                            config.Test.INFLUX_DBNAME)
    influx.create_database('test')

    yield influx

    influx.drop_database('test')


@pytest.fixture
def influx_prod():
    influx = InfluxDBClient('0.0.0.0',
                            5002,
                            config.Production.INFLUX_USER,
                            config.Production.INFLUX_PASSWORD,
                            config.Production.INFLUX_DBNAME)
    influx.create_database('test')

    yield influx

    influx.drop_database('test')


@pytest.fixture
def response():
    pair, tf, limit = 'BTCUSD', '3h', 50
    response = requests.get(f'http://0.0.0.0:5001/{pair}?timeframe={tf}&limit={limit}')
    assert response.status_code == 200, 'Server faliure!'
    return response.json()


@pytest.fixture
def indicators_names():
    return [x.__name__ for x in get_function_list(indicators)]


@pytest.fixture
def charting_names():
    return ['wedge', 'levels', 'channel', 'double_top', 'double_bottom']


@pytest.fixture
def required_indicators():
    return [x.__name__ for x in get_function_list(indicators)] + ['price', 'volume', 'wedge',
                                                                  'levels', 'channel', 'double_top',
                                                                  'double_bottom']

