import numpy as np

from app.models import Candle, Point, Series
from config import BaseConfig


class TestSeries:
    def test_iteration(self):
        xs = np.array([1, 2, 3, 4])

        candles = Series("pair", "1h", xs, xs, xs, xs, xs, xs)

        idx = 0
        for candle in candles:
            assert isinstance(candle, Candle)
            idx += 1

        assert idx == xs.size

    def test_values(self):
        xs = np.array([1, 2, 3, 4])
        low = 2 * xs
        close = 3 * xs

        candles = Series(
            "pair", "1h", time=xs, close=close, low=low, open=xs, volume=xs, high=xs
        )

        idx = 0
        for point in candles.values():
            assert isinstance(point, Point)
            assert point.x == point.y / 3
            idx += 1
        assert idx == xs.size

        idx = 0
        for point in candles.values("low"):
            assert isinstance(point, Point)
            assert point.x == point.y / 2
            idx += 1
        assert idx == xs.size

    def test_future_time(self):
        xs = np.array([1, 2, 3, 4])

        candles = Series("pair", "1h", 2 * xs, xs, xs, xs, xs, xs)

        assert candles.time.size == xs.size
        assert candles.future_time.size == BaseConfig.MARGIN
        assert candles.date.size == xs.size + BaseConfig.MARGIN
