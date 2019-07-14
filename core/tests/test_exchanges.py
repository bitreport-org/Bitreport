from app.exchanges import Bitfinex, Bittrex, Binance, Poloniex
import pytest
import numpy as np

from app.exchanges.helpers import check_exchanges, downsample
from app.database.helpers import get_all_pairs, get_candles


class TestFiller:
    def test_all_pairs(self, app, filled_influx):
        with app.ctx:
            pairs = get_all_pairs()
        assert isinstance(pairs, list)
        assert len(pairs) == 1
        pairs.sort()
        assert pairs == ["BTCUSD"]

    def test_check_exchanges(self, app, filled_influx):
        with app.ctx:
            exchanges = check_exchanges("BTCUSD")
        assert isinstance(exchanges, list)
        assert len(exchanges) == 1
        assert exchanges == ["bitfinex"]

    def test_no_exchange(self, app, filled_influx):
        with app.ctx:
            exchanges = check_exchanges("TESTSMTH")
        assert isinstance(exchanges, list)
        assert not exchanges


class TestFillExchange:
    @staticmethod
    def check_candles_structure(pair, tf="1h"):
        limit = 100

        candles = get_candles(pair, tf, limit)

        # assert structure and types
        assert isinstance(candles, dict)
        assert "date" in candles.keys()
        assert isinstance(candles["date"], list)
        assert candles["date"]

        for x in ["volume", "close", "open", "high", "low"]:
            assert x in candles.keys()
            assert isinstance(candles[x], np.ndarray)

        # assert candles order
        assert candles["date"][-1] - candles["date"][-2] == int(tf[:-1]) * 3600

        # assert result size
        assert len(candles["date"]) == limit
        assert candles["volume"].size == limit
        assert candles["close"].size == limit
        assert candles["open"].size == limit
        assert candles["high"].size == limit
        assert candles["low"].size == limit

    @pytest.mark.vcr(match_on=["host", "path"], ignore_localhost=True)
    def test_bitfinex_fill(self, app, influx):
        pair = "BTCUSD"
        result = Bitfinex().fill(app.ctx, pair), f"Failed to fill from Bitfinex"
        assert result

        with app.ctx:
            self.check_candles_structure(pair)

    @pytest.mark.vcr(match_on=["uri"], ignore_localhost=True)
    def test_binance_fill(self, app, influx):
        pair = "GASBTC"
        result = Binance().fill(app.ctx, pair), f"Failed to fill from Binance"
        assert result

        with app.ctx:
            self.check_candles_structure(pair)

    @pytest.mark.vcr(match_on=["uri"], ignore_localhost=True)
    def test_bittrex_fill(self, app, influx):
        pair = "POLYBTC"
        result = Bittrex().fill(app.ctx, pair), f"Failed to fill from Bittrex"
        assert result

        with app.ctx:
            self.check_candles_structure(pair)

    @pytest.mark.vcr(match_on=["uri"], ignore_localhost=True)
    def test_poloniex_fill(self, app, influx):
        pair = "SCBTC"
        result = Poloniex().fill(app.ctx, pair), f"Failed to fill from Poloniex"
        assert result

        with app.ctx:
            downsample(pair, "30m", "1h")
            self.check_candles_structure(pair)


class TestErrorExchange:
    @staticmethod
    def raise_error(exchange):
        status = exchange().fetch_candles("wefsdfwenown", "1h")
        assert not status

    @pytest.mark.vcr(match_on=["host", "path"], ignore_localhost=True)
    def test_bitfinex_error(self, app, influx):
        with app.ctx:
            self.raise_error(Bitfinex)

    @pytest.mark.vcr(match_on=["host", "path"], ignore_localhost=True)
    def test_binance_error(self, app):
        with app.ctx:
            self.raise_error(Binance)

    @pytest.mark.vcr(match_on=["host", "path"], ignore_localhost=True)
    def test_bittrex_error(self, app):
        with app.ctx:
            self.raise_error(Bittrex)

    @pytest.mark.vcr(match_on=["host", "path"], ignore_localhost=True)
    def test_poloniex_error(self, app, influx):
        with app.ctx:
            self.raise_error(Poloniex)
