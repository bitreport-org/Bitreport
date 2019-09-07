from typing import NamedTuple, Union

import numpy as np

from app.models.point import Point


class Skew(NamedTuple):
    slope: float
    coef: float
    start: int

    def eval(self, x: Union[float, int, np.ndarray]) -> Union[float, np.ndarray]:
        return self.slope * x + self.coef

    @classmethod
    def from_events(cls, a, b):
        """
        Creates Skew from Events

        :type a: Event
        :type b: Event
        """
        if a.time == b.time:
            return cls(0.0, a.value, a.time)
        slope = (a.value - b.value) / (a.time - b.time)
        coef = b.value - slope * b.time
        start = min(a.time, b.time)
        return cls(slope, coef, start)

    @classmethod
    def from_points(cls, a: Point, b: Point):
        if a.x == b.x:
            return cls(0.0, a.y, a.x)
        slope = (a.y - b.y) / (a.x - b.x)
        coef = b.y - slope * b.x
        start = min(a.x, b.x)
        return cls(slope, coef, start)
