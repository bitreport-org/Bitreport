from app.services.helpers import get_candles


class TestFillEndpoint:
    """
    Tests /fill endpoint and influx database filling.
    """
    @staticmethod
    def fill(pair, app, influx):
        rs = app.post(f'/fill?pair={pair}')
        assert rs.status_code == 200, 'Server faliure?'

        msr = [x.get('name') for x in influx.get_list_measurements()]
        for tf in ['1h', '2h', '3h', '6h', '12h', '24h']:
            assert pair + tf in msr, f'Measurement {pair+tf} is not present.'

            close = get_candles(influx, pair, tf, limit=100).get('close')
            assert close.size == 100

    def test_no_pair(self, app):
        response = app.post('/fill')
        assert response.status_code == 404, 'Wrong code'

    def test_nonexistent_pair(self, app):
        response = app.post('/fill?pair=ofjwoefwefiubwfiow')
        assert response.status_code == 404, 'Nonexistent pair filled!?'
        assert  isinstance(response.get_json(), dict)

    def test_bitfinex(self, app, influx):
        self.fill('BTCUSD', app, influx)

