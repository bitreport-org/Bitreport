from app.exchanges import Bitfinex, Bittrex, Binance, Poloniex
from app.utils import get_candles
import pytest
import numpy as np

from app.exchanges.helpers import check_exchanges, downsample
from app.utils.helpers import get_all_pairs


class TestFiller:
    def test_all_pairs(self, filled_influx):
        pairs = get_all_pairs(filled_influx)
        assert isinstance(pairs, list)
        assert len(pairs) == 2
        pairs.sort()
        assert pairs == ['BTCUSD', 'TEST']

    def test_check_exchanges(self, filled_influx):
        exchanges = check_exchanges(filled_influx, 'BTCUSD')
        assert isinstance(exchanges, list)
        assert len(exchanges) == 4
        assert exchanges == ['binance', 'bitfinex', 'bittrex', 'poloniex']

    def test_no_exchange(self, filled_influx):
        exchanges = check_exchanges(filled_influx, 'TESTSMTH')
        assert isinstance(exchanges, list)
        assert len(exchanges) == 0


class TestFillExchange:
    @staticmethod
    def check_candles_structure(influx, pair, tf='1h'):
        limit = 100
        candles = get_candles(influx, pair, tf, limit)

        # assert structure and types
        assert isinstance(candles, dict)
        assert 'date' in candles.keys()
        assert isinstance(candles['date'], list)
        assert len(candles['date']) > 0

        for x in ['volume', 'close', 'open', 'high', 'low']:
            assert x in candles.keys()
            assert isinstance(candles[x], np.ndarray)

        # assert candles order
        assert candles['date'][-1] - candles['date'][-2] == int(tf[:-1]) * 3600

        # assert result size
        assert len(candles['date']) == limit
        assert candles['volume'].size == limit
        assert candles['close'].size == limit
        assert candles['open'].size == limit
        assert candles['high'].size == limit
        assert candles['low'].size == limit

    @pytest.mark.vcr(match_on=['host', 'path'], ignore_localhost=True)
    def test_bitfinex_fill(self, influx):
        pair = 'BTCUSD'
        result = Bitfinex(influx).fill(pair), f'Failed to fill from Bitfinex'
        assert result
        self.check_candles_structure(influx, pair)

    @pytest.mark.vcr(match_on=['uri'], ignore_localhost=True)
    def test_binance_fill(self, influx):
        pair = 'GASBTC'
        Binance(influx).fill(pair), f'Failed to fill from Binance'
        self.check_candles_structure(influx, pair)

    @pytest.mark.vcr(match_on=['uri'], ignore_localhost=True)
    def test_bittrex_fill(self, influx):
        pair = 'POLYBTC'
        Bittrex(influx).fill(pair), f'Failed to fill from Bittrex'
        self.check_candles_structure(influx, pair)

    @pytest.mark.vcr(match_on=['uri'], ignore_localhost=True)
    def test_poloniex_fill(self, influx):
        pair = 'SCBTC'
        Poloniex(influx).fill(pair), f'Failed to fill from Poloniex'
        downsample(influx, pair, '30m', '1h')
        self.check_candles_structure(influx, pair)


class TestErrorExchange:
    @staticmethod
    def raise_error(exchange, influx):
        status = exchange(influx).fetch_candles('wefsdfwenown', '1h')
        assert not status

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
