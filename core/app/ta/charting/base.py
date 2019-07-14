import numpy as np
import json
from typing import Union, Iterable, List
from collections import namedtuple
from sqlalchemy import cast, String

from app.database.models import Chart, db
from app.ta.constructors import Point, Skew
from app.ta.helpers import angle

SkewPoint = Union[Point, Skew]
Universe = namedtuple("Universe", ["pair", "timeframe", "close", "time", "future_time"])


class Setup:
    def __init__(
        self,
        up: np.ndarray,
        down: np.ndarray,
        params: dict,
        peaks_fit_value: float,
        empty_field_value: float,
        length: int,
        points_between: float,
    ):
        self.down = down
        self.up = up
        self.params = params
        self.peaks_fit_value = peaks_fit_value
        self.empty_field_value = empty_field_value
        self.length = length
        self.points_between = points_between


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

    def __init__(
        self, universe: Universe, peaks: tuple = None, remake: bool = False, **kwargs
    ) -> None:

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
            self._tops, self._bottoms = tuple(map(self._remove_outliers, peaks))
            self.setup = self._find(**kwargs)
            if self.setup:
                self._extend()
                self._create_info()

    def json(self) -> Union[dict, None]:
        if not self.setup:
            return None

        # Remove bands before starting point
        # self._erase_band()
        # return dict(upper_band=nan_to_null(self.setup.up),
        #             lower_band=nan_to_null(self.setup.down),
        #             name=self.__name__,
        #             info=self._info_json())

        return dict(
            upper_band=self.setup.up.tolist(),
            lower_band=self.setup.down.tolist(),
            name=self.__name__,
            info=self._info_json(),
        )

    def _info_json(self) -> dict:
        return []
        # return dict(events=self.events,
        #             signal=self.signal,
        #             sentiment=self.sentiment)

    def save(self) -> None:
        if not self.setup:
            return None

        ch = (
            db.session.query(Chart)
            .filter(
                Chart.pair == self._pair,
                Chart.timeframe == self._timeframe,
                Chart.type == self.__name__,
                cast(Chart.params, String) == json.dumps(self.setup.params),
            )
            .first()
        )

        if not ch:
            ch = Chart(
                pair=self._pair,
                timeframe=self._timeframe,
                type=self.__name__,
                params=self.setup.params,
            )
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

    def _include_enough_points(
        self, start: int, up: np.ndarray, down: np.ndarray, threshold: float = 0.85
    ) -> Union[float, None]:

        idx = np.where(self._time == start)[0][0]
        close, up, down = self._close[idx:], up[idx:], down[idx:]
        under = close <= up
        above = close >= down
        between = sum(a and b for a, b in zip(under, above))
        score = between / close.size
        if score >= threshold:
            return score
        return None

    def _empty_field_score(
        self, start: int, up: np.ndarray, down: np.ndarray
    ) -> Union[float, None]:

        idx = np.where(self._time == start)[0][0]
        close, up, down = self._close[idx:], up[idx:], down[idx:]

        # Look at this as an integral
        sum_up_spaces = np.sum(up - close)
        sum_down_spaces = np.sum(close - down)

        total = sum_down_spaces + sum_up_spaces
        return total

    def _peaks_fit_value(self, up: np.ndarray, down: np.ndarray) -> Union[float, None]:

        up_series = {int(t): v for t, v in zip(self._time, up)}
        down_series = {int(t): v for t, v in zip(self._time, down)}

        tops_fit = [abs(p.y - up_series[int(p.x)]) for p in self._tops]
        bottoms_fit = [abs(p.y - down_series[int(p.x)]) for p in self._bottoms]

        fit = sum(tops_fit + bottoms_fit)

        return fit

    def _length(self, start: int, a: SkewPoint, b: SkewPoint) -> float:
        cross = self._cross_point(a, b)
        if cross is None:
            return 0.0
        return int(cross.x - start)

    @staticmethod
    def _is_triangle(up: np.ndarray, down: np.ndarray) -> bool:
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

    @staticmethod
    def _is_horizontal(skew: Skew) -> bool:
        return skew.slope == 0.0

    @staticmethod
    def _select_best_setup(setups: [Setup]) -> Setup:
        # Sort by number of points between bands
        setups.sort(key=lambda s: s.points_between, reverse=True)
        setups = setups[:20]

        # Sort by fit to peaks
        setups.sort(key=lambda s: s.peaks_fit_value)
        setups = setups[:4]

        # Sort by empty value
        setups.sort(key=lambda s: s.empty_field_value)
        setups = setups[:2]

        # Sort by length
        setups.sort(key=lambda s: s.length)

        return setups[-1]

    def _extend(self):
        ua, ub = self.setup.params["up"]
        da, db = self.setup.params["down"]
        extension_up = ua * self._future_time + ub
        extension_down = da * self._future_time + db

        # till crossing
        i = sum(1 for u, d in zip(extension_up, extension_down) if u >= d)

        self.setup.close = np.concatenate([self.setup.up, extension_up[:i]])
        self.setup.down = np.concatenate([self.setup.down, extension_down[:i]])

    def _erase_band(self):
        start = self.setup.params["start"]
        up = self.setup.up
        down = self.setup.down
        for i, t in enumerate(self._time):
            if t < start - 10:
                up[i] = None
                down[i] = None

        self.setup.down = down
        self.setup.up = up

    @staticmethod
    def _remove_outliers(peaks: List[Point]) -> List[Point]:
        peaks.sort(key=lambda p: p.x)
        if not peaks:
            return []
        return peaks[-4:]

    def _find(self, **kwargs) -> Union[Setup, None]:
        NotImplemented()
        return None

    def _create_info(self) -> None:
        NotImplemented()
        return None

    def _remake(self, **kwargs) -> None:
        NotImplemented()
        return None


def nan_to_null(xs: list) -> list:
    return list(map(lambda x: None if np.isnan(x) else x, xs))
