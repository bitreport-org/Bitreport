import requests
import pytest
from app.services.internal import get_function_list
from app.ta import  indicators

indicators_names = [x.__name__ for x in get_function_list(indicators)]
charting_names = ['wedge', 'levels', 'channel']
required_indicators = ['price', 'volume'] + charting_names + indicators_names


@pytest.fixture(scope="session", autouse=True)
def response():
    pair, tf, limit = 'BTCUSD', '3h', 50
    response = requests.get(f'http://0.0.0.0:5001/{pair}?timeframe={tf}&limit={limit}')
    assert response.status_code == 200, 'Server faliure!'
    return response.json()


class TestTA(object):
    def test_response_json(self, response):
        assert  isinstance(response, dict)
        keys = response.keys()
        assert 'dates' in keys
        assert 'indicators' in keys

    def test_tstmps(self, response):
        assert isinstance(response, dict)
        assert 'dates' in response.keys(), 'No dates in response.'
        dates = response.get('dates')
        assert dates[1] - dates[0] == 3 * 3600

    def test_indicators_json(self, response):
        assert isinstance(response, dict)
        assert 'indicators' in response.keys()

        keys = response['indicators'].keys()
        for k in required_indicators:
            assert k in keys, f'Indicator {k} is absent.'

    def test_price_json(self, response):
        assert isinstance(response, dict)
        assert 'indicators' in response.keys()
        assert 'price' in response.get('indicators')
        price = response['indicators']['price']
        keys = price.keys()
        for x in ['open', 'low', 'high', 'close']:
            assert x in keys, f'Key {x} is not present in price'

    def test_indicators_info(self, response):
        assert isinstance(response, dict)
        assert 'indicators' in response.keys()
        keys = response['indicators'].keys()
        for k in keys:
            assert isinstance(k, dict), f'Indicator {k} is not a dictionary'
            assert 'info' in k.keys()

    def test_channels(self, response):
        assert isinstance(response, dict)
        keys = response.keys()
        assert 'indicators' in keys
        for ch in charting_names:
            if ch in keys:
                assert isinstance(ch, dict), 'Indicator is not a dictionary'
                assert 'upper_band' in ch.keys(), 'No upperband in channel!'
                assert 'middle_band' in ch.keys(), 'No middleband in channel!'
                assert 'lower_band' in ch.keys(), 'No lowerband in channel!'

