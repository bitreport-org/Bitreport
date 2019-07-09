from collections import namedtuple
from typing import Iterable

import numpy as np

from config import BaseConfig

Skew = namedtuple('Skew', ['slope', 'coef', 'start'])

Candle = namedtuple('Candle', ['time', 'open', 'close', 'high', 'low', 'volume'])

empty = np.array([])

class Series:
    def __init__(self,
                 pair: str,
                 timeframe: str,
                 time: np.ndarray = empty,
                 open: np.ndarray = empty,
                 close: np.ndarray = empty,
                 high: np.ndarray = empty,
                 low: np.ndarray = empty,
                 volume: np.ndarray = empty):

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

    def values(self, key: str ="close") -> Iterable:
        return (Point(x, y) for x, y in zip(self.time, getattr(self, key)))


    def _generate_times(self) -> np.ndarray:
        """
        Generates next n timestamps in interval of a given timeframe
        """
        if self.time.size < 1:
            return np.array([])

        n = BaseConfig.MARGIN
        _map = {'m': 60, 'h': 3600, 'W': 648000}
        dt = _map[self.timeframe[-1]] * int(self.timeframe[:-1])
        new_times = [self.time[-1] + (i + 1) * dt for i, x in enumerate(range(n))]
        return np.array(new_times)

    @property
    def date(self):
        return np.concatenate([self.time, self.future_time])


class Point:
    info = None

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point({self.x}, {self.y}), {self.info}'

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def add_info(self, info: str):
        self.info = info

