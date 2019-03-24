from config import BaseConfig

class TestPairExceptions:
    """
    Tests /pair endpoint and the response with price and TA info.
    """
    pair = 'BTCUSD'
    timeframe = '1h'
    limit = 100

    def test_no_timeframe(self, app):
        response = app.get(f'/{self.pair}')
        assert response.status_code == 404, 'Server faliure!'
        assert isinstance(response.get_json(), dict)
        assert 'msg' in response.get_json().keys()

    def test_unknown_timeframe(self, app):
        response = app.get(f'/{self.pair}?timeframe=42h&limit=100')
        assert response.status_code == 404, 'Server faliure!'
        assert isinstance(response.get_json(), dict)
        assert 'msg' in response.get_json().keys()

    def test_no_data(self, app):
        response = app.get(f'/{self.pair}?timeframe={self.timeframe}&limit={self.limit}')
        assert response.status_code == 404, 'Server faliure!'
        assert isinstance(response.get_json(), dict)
        assert 'msg' in response.get_json().keys()
        assert 'No data' in response.get_json().get('msg')

    def test_not_enough_data1h(self, app, filled_influx):
        response = app.get(f'/TEST?timeframe=1h&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert isinstance(response, dict)
        keys = response.keys()
        assert 'dates' in keys
        assert 'indicators' in keys
        assert list(response['indicators']) == ['price', 'volume']
        assert list(response['indicators']['price']) == ['close', 'high', 'info', 'low', 'open']

        assert len(response['indicators']['price']['close']) == self.limit

    def test_not_enough_data12h(self, app, filled_influx):
        response = app.get(f'/TEST?timeframe=12h&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert isinstance(response, dict)
        keys = response.keys()
        assert 'dates' in keys
        assert 'indicators' in keys
        assert list(response['indicators']) == ['price', 'volume']
        assert list(response['indicators']['price']) == ['close', 'high', 'info', 'low', 'open']

        assert len(response['indicators']['price']['close']) == self.limit


class TestPairEndpoint:
    """
    Tests /pair endpoint and the response with price and TA info.
    """
    pair = 'BTCUSD'
    timeframe = '1h'
    limit = 100

    def test_response_json(self, app, filled_influx):
        response = app.get(f'/{self.pair}?timeframe={self.timeframe}&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert  isinstance(response, dict)
        keys = response.keys()
        assert 'dates' in keys
        assert 'indicators' in keys

    def test_tstmps(self, app, filled_influx):
        response = app.get(f'/{self.pair}?timeframe={self.timeframe}&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert isinstance(response, dict)
        assert 'dates' in response.keys(), 'No dates in response.'
        dates = response.get('dates')
        assert len(dates) == self.limit + BaseConfig.MARGIN
        for x, y in zip(dates[:-1], dates[1:]):
            assert y - x == int(self.timeframe[:-1]) * 3600

    def test_indicators_json(self, required_indicators, app, filled_influx):
        response = app.get(f'/{self.pair}?timeframe={self.timeframe}&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert isinstance(response, dict)
        assert 'indicators' in response.keys()

        keys = response['indicators'].keys()
        for k in required_indicators:
            assert k in keys, f'Indicator {k} is absent.'

    def test_price_json(self, app, filled_influx):
        response = app.get(f'/{self.pair}?timeframe={self.timeframe}&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert isinstance(response, dict)
        assert 'indicators' in response.keys()
        assert 'price' in response.get('indicators')
        assert 'volume' in response.get('indicators')

        # Test price
        price = response['indicators']['price']
        keys = price.keys()
        for x in ['open', 'low', 'high', 'close']:
            assert x in keys, f'Key {x} is not present in price'
            assert len(price[x]) == self.limit

        # Test volume
        vol = response['indicators']['volume']
        assert 'volume' in vol.keys()
        assert len(vol['volume']) == self.limit


    def test_indicators_info(self, app, filled_influx):
        response = app.get(f'/{self.pair}?timeframe={self.timeframe}&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert isinstance(response, dict)
        assert 'indicators' in response.keys()
        indctrs = response['indicators']
        for k, i in indctrs.items():
            assert isinstance(i, dict), f'Indicator {k} is not a dictionary'
            assert 'info' in i.keys(), f'Indicator {k} has no info'

    def test_channels(self, charting_names, app, filled_influx):
        response = app.get(f'/{self.pair}?timeframe={self.timeframe}&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert isinstance(response, dict)
        keys = response.keys()
        assert 'indicators' in keys
        for ch in charting_names:
            if ch in keys:
                assert isinstance(ch, dict), 'Indicator is not a dictionary'
                assert 'upper_band' in ch.keys(), 'No upperband in channel!'
                assert 'middle_band' in ch.keys(), 'No middleband in channel!'
                assert 'lower_band' in ch.keys(), 'No lowerband in channel!'



class TestPair12:
    """
    Tests /pair endpoint and the response with price and TA info.
    """
    pair = 'BTCUSD'
    timeframe = '12h'
    limit = 100

    def test_response_json(self, app, filled_influx):
        response = app.get(f'/{self.pair}?timeframe={self.timeframe}&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert  isinstance(response, dict)
        keys = response.keys()
        assert 'dates' in keys
        assert 'indicators' in keys

    def test_tstmps(self, app, filled_influx):
        response = app.get(f'/{self.pair}?timeframe={self.timeframe}&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert isinstance(response, dict)
        assert 'dates' in response.keys(), 'No dates in response.'
        dates = response.get('dates')
        assert len(dates) == self.limit + BaseConfig.MARGIN
        for x, y in zip(dates[:-1], dates[1:]):
            assert y - x == int(self.timeframe[:-1]) * 3600

    def test_indicators_json(self, required_indicators, app, filled_influx):
        response = app.get(f'/{self.pair}?timeframe={self.timeframe}&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert isinstance(response, dict)
        assert 'indicators' in response.keys()

        keys = response['indicators'].keys()
        for k in required_indicators:
            assert k in keys, f'Indicator {k} is absent.'

    def test_price_json(self, app, filled_influx):
        response = app.get(f'/{self.pair}?timeframe={self.timeframe}&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert isinstance(response, dict)
        assert 'indicators' in response.keys()
        assert 'price' in response.get('indicators')
        assert 'volume' in response.get('indicators')

        # Test price
        price = response['indicators']['price']
        keys = price.keys()
        for x in ['open', 'low', 'high', 'close']:
            assert x in keys, f'Key {x} is not present in price'
            assert len(price[x]) == self.limit

        # Test volume
        vol = response['indicators']['volume']
        assert 'volume' in vol.keys()
        assert len(vol['volume']) == self.limit


    def test_indicators_info(self, app, filled_influx):
        response = app.get(f'/{self.pair}?timeframe={self.timeframe}&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert isinstance(response, dict)
        assert 'indicators' in response.keys()
        indctrs = response['indicators']
        for k, i in indctrs.items():
            assert isinstance(i, dict), f'Indicator {k} is not a dictionary'
            assert 'info' in i.keys(), f'Indicator {k} has no info'

    def test_channels(self, charting_names, app, filled_influx):
        response = app.get(f'/{self.pair}?timeframe={self.timeframe}&limit={self.limit}')
        assert response.status_code == 200, 'Server faliure!'
        response = response.get_json()

        assert isinstance(response, dict)
        keys = response.keys()
        assert 'indicators' in keys
        for ch in charting_names:
            if ch in keys:
                assert isinstance(ch, dict), 'Indicator is not a dictionary'
                assert 'upper_band' in ch.keys(), 'No upperband in channel!'
                assert 'middle_band' in ch.keys(), 'No middleband in channel!'
                assert 'lower_band' in ch.keys(), 'No lowerband in channel!'
