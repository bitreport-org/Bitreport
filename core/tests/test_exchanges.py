from app.exchanges import fill_pair, Bitfinex, Bittrex, Binance, Poloniex
from app.services import get_candles


class TestFillExchange:
    @staticmethod
    def fill_btc(exchange, influx):
        pair = 'BTCUSD'
        assert exchange(influx).fetch_candles(pair, '1h'), f'Failed to fill 1h from {exchange.name}'
        assert exchange(influx).fetch_candles(pair, '24h'), f'Failed to fill 24h from {exchange.name}'

        candles = get_candles(influx, pair, '1h', 100)
        assert candles['volume'].size == 100
        assert candles['close'].size == 100
        assert candles['open'].size == 100
        assert candles['high'].size == 100
        assert candles['low'].size == 100

    def test_bitfinex(self, influx):
        self.fill_btc(Bitfinex, influx)

    def test_binance(self, influx):
        self.fill_btc(Binance, influx)

    def test_bittrex(self, influx):
        self.fill_btc(Bittrex, influx)

    def test_poloniex(self, influx):
        self.fill_btc(Poloniex, influx)


class TestErrorExchange:
    @staticmethod
    def raise_error(exchange, influx):
        status = exchange(influx).fetch_candles('wefsdfwenown', '1h')
        assert status == False

    def test_bitfinex(self, influx):
        self.raise_error(Bitfinex, influx)

    def test_binance(self, influx):
        self.raise_error(Binance, influx)

    def test_bittrex(self, influx):
        self.raise_error(Bittrex, influx)

    def test_poloniex(self, influx):
        self.raise_error(Poloniex, influx)


class TestFillPair:
    @staticmethod
    def check_influx(pair, influx):
        msr = [x.get('name') for x in influx.get_list_measurements()]
        for tf in ['1h', '2h', '3h', '6h', '12h', '24h']:
            assert pair + tf in msr, f'Measurement {pair+tf} is not present.'

    def fill(self, pair, influx):
        status = fill_pair(influx, pair)
        assert status, f'Failed to fill {pair}'
        self.check_influx(pair, influx)

    def test_bitfinex(self, influx):
        self.fill('BTCUSD', influx)

    def test_binance(self, influx):
        self.fill('GASBTC', influx)

    def test_bittrex(self, influx):
        self.fill('POLYBTC', influx)

    def test_poloniex(self, influx):
        self.fill('SCBTC', influx)


