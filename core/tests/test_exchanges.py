from app.exchanges import fill_pair, Bitfinex, Bittrex, Binance, Poloniex
from app.services import get_candles


class TestFillExchange:
    def fill_btc(self, exchange, influx):
        pair = 'BTCUSD'
        assert exchange(influx).fetch_candles(pair, '1h'), f'Failed to fill 1h from {exchange.name}'
        assert exchange(influx).fetch_candles(pair, '24h'), f'Failed to fill 24h from {exchange.name}'

        candles = get_candles(influx, pair, '1h', 100)
        assert candles['volume'].size == 100
        assert candles['close'].size == 100
        assert candles['open'].size == 100
        assert candles['high'].size == 100
        assert candles['low'].size == 100

    def test_bitfinex(self, influx_test):
        self.fill_btc(Bitfinex, influx_test)

    def test_binance(self, influx_test):
        self.fill_btc(Binance, influx_test)

    def test_bittrex(self, influx_test):
        self.fill_btc(Bittrex, influx_test)

    def test_poloniex(self, influx_test):
        self.fill_btc(Poloniex, influx_test)



class TestErrorExchange:
    def raise_error(self, exchange, influx):
        status = exchange(influx).fetch_candles('wefsdfwenown', '1h')
        assert status == False

    def test_bitfinex(self, influx_test):
        self.raise_error(Bitfinex, influx_test)

    def test_binance(self, influx_test):
        self.raise_error(Binance, influx_test)

    def test_bittrex(self, influx_test):
        self.raise_error(Bittrex, influx_test)

    def test_poloniex(self, influx_test):
        self.raise_error(Poloniex, influx_test)


class TestFillPair:
    def fill(self, pair, influx):
        status = fill_pair(influx, pair)
        assert status, f'Failed to fill {pair}'
        self.check_influx(pair)

    def check_influx(self, pair, influx):
        msr = [x.get('name') for x in influx.get_list_measurements()]
        for tf in ['1h', '2h', '3h', '6h', '12h', '24h']:
            assert pair + tf in msr, f'Measurement {pair+tf} is not present.'

    def test_bitfinex(self, influx_test):
        self.fill('BTCUSD', influx_test)

    def test_binance(self, influx_test):
        self.fill('GASBTC', influx_test)

    def test_bittrex(self, influx_test):
        self.fill('POLYBTC', influx_test)

    def test_poloniex(self, influx_test):
        self.fill('SCBTC', influx_test)


