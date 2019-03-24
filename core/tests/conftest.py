import pytest
from influxdb import InfluxDBClient
import os
import json

from app.services.helpers import get_function_list
from app.ta import indicators
from app.api import create_app
from app.exchanges.helpers import insert_candles
import config


@pytest.fixture(scope="session")
def app(request):
    """Session-wide test application."""
    app = create_app(config.Test)
    client = app.test_client()

    return client


@pytest.fixture(scope='session')
def drop_influx():
    client = InfluxDBClient(**config.Test.INFLUX)
    client.drop_database(config.Test.INFLUX.get('database', 'test'))


@pytest.fixture
def influx():
    client = InfluxDBClient(**config.Test.INFLUX)
    dbname = config.Test.INFLUX.get('database', 'test')
    client.create_database(dbname)

    yield client

    client.drop_database(dbname)


def fill_database(influx):
    rel_dir = os.path.dirname(__file__)
    pair = 'BTCUSD'
    tf = '1h'

    measurement = pair + tf
    path = os.path.join(rel_dir, f'test_data/{measurement}.json')
    with open(path) as data_file:
        points = json.load(data_file)
        insert_candles(influx, points, measurement, 'Bitfinex', time_precision='ms')

    # Add fake pair
    points = points[:120]
    measurement = 'TEST1h'
    for x in points:
        x['measurement'] = measurement

    insert_candles(influx, points, measurement, 'Bitfinex', time_precision='ms')


@pytest.fixture(scope='module')
def filled_influx():
    client = InfluxDBClient(**config.Test.INFLUX)
    dbname = config.Test.INFLUX.get('database', 'test')
    client.create_database(dbname)

    # Add some test points
    fill_database(client)

    yield client

    client.drop_database(dbname)


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
