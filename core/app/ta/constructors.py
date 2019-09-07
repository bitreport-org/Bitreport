from functools import reduce
from typing import List, Optional

import numpy as np

from app.models import Point, Skew


def _is_peak(xs: np.ndarray, ts: np.ndarray, checker: callable) -> List[Point]:
    """
    Looks for peaks in vector of prices xs:
    Parameters
    ----------
    xs - price array
    ts - time array
    checker - function used for checking if point is a peak

    Returns
    -------
    list of peaks
    """
    lines = []
    radius = 7

    # For each strength level
    for i, (y, t) in enumerate(zip(xs, ts)):
        if i > xs.size - radius:
            continue
        if i < radius:
            continue
        ys = xs[i - radius : i + radius]
        is_peak = reduce(lambda a, b: a and b, checker(ys, np.array([y] * ys.size)))
        if is_peak:
            lines.append(Point(t, float(y)))
    return lines


def _skew(a: Point, b: Point) -> Optional[Skew]:
    """
    Returns skew defined by two points a and b.
    """
    if a == b:
        return None
    slope = (a.y - b.y) / (a.x - b.x)
    coef = b.y - slope * b.x

    if a.x <= b.x:
        start = a
    else:
        start = b

    return Skew(float(slope), float(coef), start)


def tops(close: np.ndarray, time: np.ndarray) -> List[Point]:
    return _is_peak(close, time, lambda x, y: x <= y)


def bottoms(close: np.ndarray, time: np.ndarray) -> List[Point]:
    return _is_peak(close, time, lambda x, y: x >= y)


def hline_up(close: np.ndarray, time: np.ndarray) -> List[Point]:
    return [p.y for p in tops(close, time)]


def hline_down(close: np.ndarray, time: np.ndarray) -> List[Point]:
    return [p.y for p in bottoms(close, time)]


def skews(peaks: list) -> list:
    xs = (_skew(a, b) for i, a in enumerate(peaks) for b in peaks[i:])
    return list(filter(lambda x: x, xs))


def skews_up(close: np.ndarray, time: np.ndarray) -> list:
    return skews(tops(close, time))


def skews_down(close: np.ndarray, time: np.ndarray) -> list:
    return skews(bottoms(close, time))
