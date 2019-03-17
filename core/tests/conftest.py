import pytest
from influxdb import InfluxDBClient
import requests

from app.services.internal import get_function_list
from app.ta import indicators
from app.api import create_app

import config


@pytest.fixture(scope="module")
def app(request):
    """Session-wide test application."""
    app = create_app(config.Test)
    client = app.test_client()

    return client


@pytest.fixture(scope="session")
def btc_app(request):
    """Session-wide test application."""
    app = create_app(config.Test)
    client = app.test_client()

    client.post('/fill?pair=BTCUSD')

    return client


@pytest.yield_fixture(scope='session')
def drop_influx():
    influx = InfluxDBClient(**config.Test.INFLUX)
    influx.drop_database('test')


@pytest.fixture
def influx_test():
    influx = InfluxDBClient(**config.Test.INFLUX)
    influx.create_database('test')

    yield influx

    influx.drop_database('test')


@pytest.fixture
def influx_prod():
    influx = InfluxDBClient(**config.Test.INFLUX_PROD)
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

