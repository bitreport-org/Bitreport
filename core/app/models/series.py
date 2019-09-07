from collections import namedtuple
from typing import Iterable

import numpy as np

from app.models.point import Point
from config import BaseConfig

Candle = namedtuple("Candle", ["time", "open", "close", "high", "low", "volume"])

EMPTY = np.array([])


class Series:
    def __init__(
        self,
        pair: str,
        timeframe: str,
        time: np.ndarray = EMPTY,
        open: np.ndarray = EMPTY,  # pylint:disable=redefined-builtin
        close: np.ndarray = EMPTY,
        high: np.ndarray = EMPTY,
        low: np.ndarray = EMPTY,
        volume: np.ndarray = EMPTY,
    ):
        self._iter_index = 0
        self._size = time.size

        for array in [open, close, high, low, volume]:
            assert array.size == self._size

        self.time = time
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = volume
        self.pair = pair
        self.timeframe = timeframe

        self.future_time = self._generate_times()

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index >= self._size:
            raise StopIteration

        candle = Candle(
            time=self.time[self._iter_index],
            close=self.close[self._iter_index],
            open=self.open[self._iter_index],
            high=self.high[self._iter_index],
            low=self.low[self._iter_index],
            volume=self.volume[self._iter_index],
        )
        self._iter_index += 1
        return candle

    def values(self, key: str = "close") -> Iterable:
        return (Point(x, y) for x, y in zip(self.time, getattr(self, key)))

    def _generate_times(self) -> np.ndarray:
        """
        Generates next n timestamps in interval of a given timeframe
        """
        if self.time.size < 1:
            return np.array([])

        margin = BaseConfig.MARGIN
        _map = {"m": 60, "h": 3600, "W": 648000}
        dt = _map[self.timeframe[-1]] * int(self.timeframe[:-1])
        new_times = [self.time[-1] + (i + 1) * dt for i in range(margin)]
        return np.array(new_times)

    @property
    def date(self):
        return np.concatenate([self.time, self.future_time])
