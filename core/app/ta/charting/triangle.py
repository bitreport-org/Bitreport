import numpy as np
import json
from typing import Union
from collections import namedtuple
from sqlalchemy import cast, String

from app.api.database import Chart, db
from .constructors import Point, Skew

SkewPoint = Union[Point, Skew]
Setup = namedtuple('Setup', ['up', 'down', 'params', 'score1', 'score2'])
Universe = namedtuple('Universe', ['pair', 'timeframe', 'close', 'time'])


class Triangle:
    # Universe setup
    _timeframe: str
    _pair: str
    _close: np.ndarray
    _time: np.ndarray
    _last_point: int

    # Setup information
    __name__: str
    setup: Union[Setup, None] = None
    events: list
    sentiment: str
    signal: tuple

    def __init__(self,
                 universe: Universe,
                 **kwargs) -> None:

        assert universe.close.size == universe.time.size

        self._timeframe = universe.timeframe
        self._pair = universe.pair
        self._close = universe.close
        self._time = universe.time
        self._last_point = universe.time[-1]

        # Check if there is an setup
        self.setup = self._find(**kwargs)
        if self.setup:
            self._create_info()

            # TODO: only selected patterns will be
            #  saved so this should be out if init?
            self._save()

    def json(self) -> Union[dict, None]:
        if not self.setup:
            return None

        return dict(upper_band=self.setup.up.tolist(),
                    lower_band=self.setup.down.tolist(),
                    info=self._info_json())

    def _info_json(self) -> dict:
        return []
        # return dict(events=self.events,
        #             signal=self.signal,
        #             sentiment=self.sentiment)

    def _save(self) -> None:
        if not self.setup:
            return None

        ch = db.session.query(Chart).filter(
            Chart.pair == self._pair,
            Chart.timeframe == self._timeframe,
            Chart.type == self.__name__,
            cast(Chart.params, String) == json.dumps(self.setup.params)).first()

        if not ch:
            ch = Chart(
                pair=self._pair,
                timeframe=self._timeframe,
                type=self.__name__,
                params=self.setup.params)
            db.session.add(ch)

        db.session.commit()

    def _cross_after_last_candle(self, a: SkewPoint, b: SkewPoint) -> bool:
        """
        This also asserts that triangle is getting narrower.
        """
        assert isinstance(a, (Point, Skew))
        assert isinstance(b, (Point, Skew))

        try:
            if isinstance(a, Point) and isinstance(b, Skew):
                cross = (a.y - b.coef) / b.slope
            elif isinstance(b, Point) and isinstance(a, Skew):
                cross = (b.y - a.coef) / a.slope
            else:
                cross = (b.coef - a.coef) / (a.slope - b.slope)
            return cross >= self._last_point

        except ZeroDivisionError:
            return False

    def _include_enough_points(self,
                               start: int,
                               up: np.ndarray,
                               down: np.ndarray,
                               threshold: float = 0.85) -> Union[float, None]:

        idx = np.where(self._time == start)[0][0]
        close, up, down = self._close[idx:], up[idx:], down[idx:]
        under = close <= up
        above = close >= down
        between = sum(a and b for a, b in zip(under, above))
        score = between / close.size
        if score >= threshold:
            return score
        return None

    def _fits_enough(self,
                     start: int,
                     up: np.ndarray,
                     down: np.ndarray,
                     threshold_down: float = 0.4,
                     threshold_up: float = 0.6) -> Union[float, None]:

        idx = np.where(self._time == start)[0][0]
        close, up, down = self._close[idx:], up[idx:], down[idx:]
        dist = (close - down) / (up - down)
        score = np.mean(dist)
        if threshold_down <= score <= threshold_up:
            return float(score)
        return None

    def _find(self, **kwargs) -> Union[Setup, None]:
        NotImplemented()
        return None

    def _create_info(self) -> None:
        NotImplemented()
        return None


def compare(t1: Triangle, t2: Triangle) -> Union[Triangle, None]:
    if t1 and t2:
        if t1.setup and t2.setup:
            if t1.setup.score1 >= t2.setup.score1:
                return t1
            return t2

        if t1.setup:
            return t1

        if t2.setup:
            return t2

    return None
