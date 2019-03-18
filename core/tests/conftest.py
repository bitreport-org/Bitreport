import pytest
from influxdb import InfluxDBClient

from app.services.helpers import get_function_list
from app.ta import indicators
from app.api import create_app
import config


@pytest.fixture(scope="session")
def app(request):
    """Session-wide test application."""
    app = create_app(config.Test)
    client = app.test_client()

    return client

@pytest.fixture(scope="module")
def filled_app(request):
    """Session-wide test application."""
    app = create_app(config.Test)
    client = app.test_client()

    # Fill the app with sample data
    client.post('/fill?pair=BTCUSD')

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

