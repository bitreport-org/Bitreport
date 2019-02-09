from influxdb import InfluxDBClient
from app.exchanges import check_exchange, fill_pair, Bitfinex, Bittrex, Binance
from app.services import get_candles

influx = InfluxDBClient('0.0.0.0', 5002, 'root', 'root', 'test')

class TestFillExchange():
    def fill_btc(self, exchange):
        # Drop and create a new, clean db
        influx.drop_database('test')
        influx.create_database('test')


        pair = 'BTCUSD'
        assert exchange(influx).get_candles(pair, '1h'), f'Failed to fill 1h from {exchange.name}'
        assert exchange(influx).get_candles(pair, '24h'), f'Failed to fill 24h from {exchange.name}'

        candles = get_candles(influx, pair, '1h', 100)
        assert candles['volume'].size == 100
        assert candles['close'].size == 100
        assert candles['open'].size == 100
        assert candles['high'].size == 100
        assert candles['low'].size == 100


    def test_bitfinex_btc(self):
        self.fill_btc(Bitfinex)

    def test_binance_btc(self):
        self.fill_btc(Binance)

    def test_bittrex_btc(self):
        self.fill_btc(Bittrex)

class TestErrorExchange():
    def raise_error(self, exchange):
        influx.create_database('test')
        status = exchange(influx).get_candles('wefsdfwenown', '1h')
        assert status==False
        influx.drop_database('test')

    def test_bitfinex_error(self):
        self.raise_error(Bitfinex)

    def test_binance_error(self):
        self.raise_error(Binance)

    def test_bittrex_error(self):
        self.raise_error(Bittrex)

class TestFillPair():
    def fill(self, pair):
        influx.drop_database('test')
        influx.create_database('test')

        ex = check_exchange(pair)
        status = fill_pair(influx, pair, ex)
        assert status, f'Failed to fill {pair}'

    def test_bitfinex(self):
        self.fill('BTCUSD')

    def test_binance(self):
        self.fill('GASBTC')

    def test_bittrex(self):
        self.fill('POLYBTC')


