import numpy as np
import json
from typing import Union
from collections import namedtuple
from sqlalchemy import cast, String

from app.api.database import Chart, db
from .constructors import Point, Skew

SkewPoint = Union[Point, Skew]
Setup = namedtuple('Setup', ['up', 'down', 'params', 'score1', 'score2'])
Universe = namedtuple('Universe', ['pair', 'timeframe', 'close', 'time', 'future_time'])


class BaseChart:
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
                 remake: bool = False,
                 **kwargs) -> None:

        assert universe.close.size == universe.time.size

        self._timeframe = universe.timeframe
        self._pair = universe.pair
        self._close = universe.close
        self._time = universe.time
        self._last_point = universe.time[-1]
        self._future_time = universe.future_time

        # Check if there is an setup
        if remake:
            self._remake(**kwargs)
        else:
            self.setup = self._find(**kwargs)
            if self.setup:
                self._extend()
                self._create_info()

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

    def save(self) -> None:
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
                     threshold_down: float = 0.47,
                     threshold_up: float = 0.55) -> Union[float, None]:

        idx = np.where(self._time == start)[0][0]
        close, up, down = self._close[idx:], up[idx:], down[idx:]
        dist = (close - down) / (up - down)
        score = np.mean(dist)
        if threshold_down <= score <= threshold_up:
            return float(score)
        return None

    @staticmethod
    def _is_triangle(up: np.ndarray,
                     down: np.ndarray) -> bool:
        width = up - down
        return width[-1] < 0.85 * width[0]

    # @staticmethod
    def _is_horizontal(self, skew: Skew) -> bool:
        a = np.degrees(np.arctan(skew.slope))
        # TODO: this should scale skew to [0,1] x [0,1]... otherwise the slope is ~ 0
        return skew.coef == 0.0

    @staticmethod
    def _select_best_setup(setups: [Setup]) -> Setup:
        # Sort by number of included points
        setups.sort(key=lambda s: s.score1, reverse=True)

        # Sort by mean point position in setup
        top = setups[:4]
        top.sort(key=lambda s: abs(0.5 - s.score1))

        return top[0]

    def _extend(self):
        ua, ub = self.setup.params['up']
        da, db = self.setup.params['down']
        extension_up = ua * self. _future_time + ub
        extension_down = da * self._future_time + db

        # till crossing
        i = sum(1 for u, d in zip(extension_up, extension_down) if u >= d)

        self.setup = Setup(
            up=np.concatenate([self.setup.up, extension_up[:i]]),
            down=np.concatenate([self.setup.down, extension_down[:i]]),
            params=self.setup.params,
            score1=self.setup.score1,
            score2=self.setup.score2
        )

    def _find(self, **kwargs) -> Union[Setup, None]:
        NotImplemented()
        return None

    def _create_info(self) -> None:
        NotImplemented()
        return None

    def _remake(self, **kwargs) -> None:
        NotImplemented()
        return None
