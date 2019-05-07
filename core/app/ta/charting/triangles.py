import numpy as np
from typing import List, Tuple, Union

from .constructors import Point, Skew
from .triangle import Triangle, Setup


def _find(self, peaks: List[Point], skews: List[Skew]) -> Union[Setup, None]:
    setups = []
    for peak in peaks:
        for skew in skews:
            if not self._cross_after_last_candle(peak, skew):
                continue

            up, down = self._make_bands(peak, skew)
            rule, score = self._include_enough_points(up, down)
            if not rule:
                continue
            setups.append(_make_setup(peak, skew, up, down, score))

    if not setups:
        return None

    return _select_best_setup(setups)


def _make_setup(peak: Point, skew: Skew,
                up: np.ndarray, down: np.ndarray, score: float) -> Setup:
    params = {
        'hline': peak.y,
        'slope': skew.slope,
        'coef': skew.coef
    }
    return Setup(up, down, params, score)


def _select_best_setup(setups: List[Setup]) -> Setup:
    # TODO: something more sophisticated...
    setups.sort(key=lambda s: s.score)
    return setups[-1]


class AscendingTriangle(Triangle):
    """
    *   *   *
        *
    *
    """
    __name__ = "ascending_triangle"

    def _make_bands(self, top: Point, skew: Skew) -> Tuple[np.ndarray, np.ndarray]:
        up = np.full(self._close.size, top.y)
        down = self._time * skew.slope + skew.coef
        return up, down

    def _find(self, tops: List[Point], skews: List[Skew]) -> Union[Setup, None]:
        return _find(self, tops, skews)

    def _create_info(self) -> None:
        self.events = [None]
        self.sentiment = "None"
        self.signal = (None, None)


class DescendingTriangle(Triangle):
    """
    *
        *
    *   *   *
    """
    __name__ = "descending_triangle"

    def _make_bands(self, bottom: Point, skew: Skew) -> Tuple[np.ndarray, np.ndarray]:
        down = np.full(self._close.size, bottom.y)
        up = self._time * skew.slope + skew.coef
        return up, down

    def _find(self, bottoms: List[Point], skews: List[Skew]) -> Union[Setup, None]:
        return _find(self, bottoms, skews)

    def _create_info(self) -> None:
        self.events = [None]
        self.sentiment = "None"
        self.signal = (None, None)


class SymmetricalTriangle(Triangle):
    """
    *
        *
            *
        *
    *
    """
    __name__ = "symmetrical_triangle"

