import requests
from influxdb import InfluxDBClient

influx = InfluxDBClient('0.0.0.0', 5002, 'root', 'root', 'pairs')

class TestFillEndp():
    # TODO: assert some number of candles in influx
    def fill(self, pair, exchange):
        rs = requests.post(f'http://0.0.0.0:5001/fill?pair={pair}&exchange={exchange}')
        assert rs.status_code == 200, 'Server faliure?'
        self.check_influx(pair)

    def check_influx(self, pair):
        msr = [x.get('name') for x in influx.get_list_measurements()]
        for tf in ['1h', '2h', '3h', '6h', '12h', '24h']:
            assert pair + tf in msr, f'Measurement {pair+tf} is not present.'

    def test_no_pair(self):
        response = requests.post('http://0.0.0.0:5001/fill?exchange=bitfinex')
        assert response.status_code==404, 'Wrong code'

    def test_no_exchange(self):
        response = requests.post('http://0.0.0.0:5001/fill?pair=BTCUSD')
        assert response.status_code==404, 'Wrong code'

    def test_bitfinex(self):
        self.fill('BTCUSD', 'bitfinex')

    def test_binance(self):
        self.fill('GASBTC', 'binance')

    def test_bittrex(self):
        self.fill('POLYBTC', 'bittrex')

    def test_poloniex(self):
        self.fill('SCBTC', 'poloniex')


