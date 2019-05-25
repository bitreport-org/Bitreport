import numpy as np
import json
from typing import Union, Iterable
from collections import namedtuple
from sqlalchemy import cast, String

from app.api.database import Chart, db
from app.ta.constructors import Point, Skew
from app.ta.helpers import angle

SkewPoint = Union[Point, Skew]
Setup = namedtuple('Setup', ['up', 'down', 'params', 'include_score', 'fit_score', 'all_score'])
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
                    name=self.__name__,
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

    @staticmethod
    def _cross_point(a: SkewPoint, b: SkewPoint) -> Union[None, Point]:
        assert isinstance(a, (Point, Skew))
        assert isinstance(b, (Point, Skew))

        try:
            if isinstance(a, Point) and isinstance(b, Skew):
                c = (a.y - b.coef) / b.slope
                return Point(c, a.y)

            if isinstance(b, Point) and isinstance(a, Skew):
                c = (b.y - a.coef) / a.slope
                return Point(c, b.y)

            c = (b.coef - a.coef) / (a.slope - b.slope)
            return Point(c, a.slope * c + a.coef)

        except ZeroDivisionError:
            return None

    def _cross_after_last_candle(self, a: SkewPoint, b: SkewPoint) -> bool:
        """
        This also asserts that triangle is getting narrower.
        """
        cross = self._cross_point(a, b)
        if not cross:
            return False
        return cross.x >= self._last_point

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

    def _fits_to_all(self,
                     up: np.ndarray,
                     down: np.ndarray) -> Union[float, None]:

        close, up, down = self._close, up, down
        dist = (close - down) / (up - down)
        score = np.mean(dist)
        return float(score)

    @staticmethod
    def _is_triangle(up: np.ndarray,
                     down: np.ndarray) -> bool:
        width = up - down
        return width[-1] < 0.85 * width[0]

    @staticmethod
    def scale_to_unit(xs: Iterable) -> np.ndarray:
        M, m = np.max(xs), np.min(xs)
        return (xs - m) / (M - m)

    def _is_pointy(self, a: SkewPoint, b: SkewPoint) -> bool:
        cross = self._cross_point(a, b)
        if not cross:
            return False

        if isinstance(a, Point) and isinstance(b, Skew):
            points = [a, cross, b.start]
        elif isinstance(b, Point) and isinstance(a, Skew):
            points = [a.start, cross, b]
        else:
            points = [a.start, cross, b.start]

        xs = self.scale_to_unit([p.x for p in points])
        ys = self.scale_to_unit([p.y for p in points])

        a, b, c = [Point(x, y) for x, y in zip(xs, ys)]
        alpha = angle(a, b, c)

        return alpha <= 65

    # @staticmethod
    def _is_horizontal(self, skew: Skew) -> bool:
        # x1, x2 = self._time[0], self._time[-1]
        # y1 = skew.slope * x1 + skew.coef
        # y2 = skew.slope * x2 + skew.coef
        #
        # M, m = np.max([y1, y2]), np.min([y1, y2])
        # y1, y2 = (y1 - m) / (M - m), (y2 - m) / (M - m)
        #
        # speed = abs(y2-y1 / self._close.size)
        # print(skew.slope, speed)
        # return speed < 0.01
        return skew.slope == 0.0

    @staticmethod
    def _select_best_setup(setups: [Setup]) -> Setup:
        # Sort by number of included points
        setups.sort(key=lambda s: s.all_score, reverse=True)

        # Sort by number of included points since pattern
        top = setups[:8]
        setups.sort(key=lambda s: s.include_score, reverse=True)

        # Sort by mean point position in setup
        top = setups[:4]
        top.sort(key=lambda s: abs(0.5 - s.fit_score))

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
            include_score=self.setup.include_score,
            fit_score=self.setup.fit_score,
            all_score=self.setup.all_score
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
