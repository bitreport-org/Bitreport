from app.exchanges import fill_pair, Bitfinex, Bittrex, Binance, Poloniex
from app.services import get_candles
import pytest


class TestFillExchange:
    @staticmethod
    def fill(exchange, pair, influx):
        assert exchange(influx).fetch_candles(pair, '1h'), f'Failed to fill 1h from {exchange.name}'
        assert exchange(influx).fetch_candles(pair, '24h'), f'Failed to fill 24h from {exchange.name}'

        tf = '1h'
        candles = get_candles(influx, pair, tf, 100)

        # asser candles order
        assert candles['date'][-1] - candles['date'][-2] == int(tf[:-1]) * 3600

        assert candles['volume'].size == 100
        assert candles['close'].size == 100
        assert candles['open'].size == 100
        assert candles['high'].size == 100
        assert candles['low'].size == 100

    @pytest.mark.vcr(match_on=['host', 'path'], ignore_localhost=True)
    def test_bitfinex_fill(self, influx):
        self.fill(Bitfinex, 'BTCUSD', influx)

    @pytest.mark.vcr(match_on=['uri'], ignore_localhost=True)
    def test_binance_fill(self, influx):
        self.fill(Binance, 'GASBTC', influx)

    @pytest.mark.vcr(match_on=['uri'], ignore_localhost=True)
    def test_bittrex_fill(self, influx):
        self.fill(Bittrex, 'POLYBTC', influx)

    @pytest.mark.vcr(match_on=['host', 'path'], ignore_localhost=True)
    def test_poloniex_fill(self, influx):
        self.fill(Poloniex, 'SCBTC', influx)


class TestErrorExchange:
    @staticmethod
    def raise_error(exchange, influx):
        status = exchange(influx).fetch_candles('wefsdfwenown', '1h')
        assert status == False

    @pytest.mark.vcr(match_on=['host', 'path'], ignore_localhost=True)
    def test_bitfinex_error(self, influx):
        self.raise_error(Bitfinex, influx)

    @pytest.mark.vcr(match_on=['host', 'path'], ignore_localhost=True)
    def test_binance_error(self, influx):
        self.raise_error(Binance, influx)

    @pytest.mark.vcr(match_on=['host', 'path'], ignore_localhost=True)
    def test_bittrex_error(self, influx):
        self.raise_error(Bittrex, influx)

    @pytest.mark.vcr(match_on=['host', 'path'], ignore_localhost=True)
    def test_poloniex_error(self, influx):
        self.raise_error(Poloniex, influx)



