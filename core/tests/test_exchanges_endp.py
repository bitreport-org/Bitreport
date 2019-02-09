import requests

def make_request(pair):
    return requests.get(f'http://0.0.0.0:5001/exchange?pair={pair}')

class TestExchangesEndp():
    def test_btc(self):
        response = make_request('BTCUSD')
        assert response.status_code == 200, 'Server faliure!'
        assert  isinstance(response.json(), str)
        assert response.json() in ['bitfinex', 'binance', 'poloniex', 'bittrex', 'poloniex']

    def test_error(self):
        response = make_request('btcweuewrwerwewsd')
        assert response.status_code == 404, 'Server faliure!'
        assert  isinstance(response.json(), str)


