# from core.app.api import create_app, db
import time


class TestApp:
    def test_app_init(self, app):
        rv = app.get('/')
        assert b'Wrong place, is it' in rv.data


class TestFillEndp:
    # TODO: assert some number of candles in influx
    def fill(self, pair, app, influx):
        rs = app.post(f'/fill?pair={pair}')
        assert rs.status_code == 200, 'Server faliure?'
        time.sleep(2)

        msr = [x.get('name') for x in influx.get_list_measurements()]
        for tf in ['1h', '2h', '3h', '6h', '12h', '24h']:
            assert pair + tf in msr, f'Measurement {pair+tf} is not present.'


    def test_no_pair(self, app):
        response = app.post('/fill')
        assert response.status_code == 404, 'Wrong code'

    def test_nonexistent_pair(self, app):
        response = app.post('/fill?pair=ofjwoefwefiubwfiow')
        assert response.status_code == 404, 'Nonexistent pair filled!?'
        assert  isinstance(response.json(), dict)

    def test_bitfinex(self, app, influx_prod):
        self.fill('BTCUSD', app, influx_prod)

    def test_binance(self, app, influx_prod):
        self.fill('GASBTC', app, influx_prod)

    def test_bittrex(self, app, influx_prod):
        self.fill('POLYBTC', app, influx_prod)

    def test_poloniex(self, app, influx_prod):
        self.fill('SCBTC', app, influx_prod)


