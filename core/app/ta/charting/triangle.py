import numpy as np
from typing import  Union, Tuple
from collections import namedtuple
from sqlalchemy import cast, String
import json

from app.api.database import Chart, db
from .constructors import Point, Skew

SkewPoint = Union[Point, Skew]
Setup = namedtuple('Setup', ['up', 'down', 'params', 'score'])


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
                 timeframe: str,
                 pair: str,
                 close: np.ndarray,
                 time: np.ndarray,
                 **kwargs) -> None:

        self._timeframe = timeframe
        self._pair = pair
        self._close = close
        self._time = time
        self._last_point = time[-1]

        # Check if there is an setup
        self.setup = self._find(**kwargs)
        if self.setup:
            self._create_info()
            self._save()

    def json(self) -> Union[dict, None]:
        if not self.setup:
            return None

        return dict(upper_band=self.setup.up,
                    lower_band=self.setup.down,
                    info=self._info_json())

    def _info_json(self) -> dict:
        return dict(events=self.events,
                    signal=self.signal,
                    sentiment=self.sentiment)

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
        assert isinstance(a, (Point, Skew))
        assert isinstance(b, (Point, Skew))

        try:
            if isinstance(a, Point) and isinstance(b, Skew):
                cross = (a.y - b.coef) / b.slope
            elif isinstance(b, Point) and isinstance(a, Skew):
                cross = (b.y - a.coef) / a.slope
            else:
                cross = (a.slope - b.slope) / (b.coef - a.coef)
            return cross >= self._last_point

        except ZeroDivisionError:
            return False

    def _include_enough_points(self, up: np.ndarray, down: np.ndarray, threshold: float = 0.85) -> Tuple[bool, float]:
        under = self._close <= up
        above = self._close >= down
        between = sum(a and b for a, b in zip(under, above))
        score = between / self._close.size
        above_threshold = score  >= threshold
        return above_threshold, score

    def _find(self, **kwargs) -> Union[Setup, None]:
        NotImplemented()
        return None

    def _create_info(self) -> None:
        NotImplemented()
        return None
