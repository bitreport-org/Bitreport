import numpy as np
from typing import List, Tuple, Union

from .constructors import Point, Skew
from .base import BaseChart, Setup


def _find(self, peaks: List[Point], skews: List[Skew]) -> Union[Setup, None]:
    setups = []
    for peak in peaks:
        for skew in skews:
            if not self._cross_after_last_candle(peak, skew):
                continue
            up, down = self._make_bands(peak, skew)
            start_index = min(peak.x, skew.start.x)
            score1 = self._include_enough_points(start_index, up, down)
            if not score1:
                continue
            score2 = self._fits_enough(start_index, up, down)
            if not score2:
                continue

            setups.append(_make_setup(peak, skew, up, down, score1, score2))

    if not setups:
        return None

    return _select_best_setup(setups)


def _make_setup(peak: Point, skew: Skew,
                up: np.ndarray, down: np.ndarray,
                score1: float, score2: float) -> Setup:
    params = {
        'hline': peak.y,
        'slope': skew.slope,
        'coef': skew.coef
    }
    return Setup(up, down, params, score1, score2)


def _select_best_setup(setups: List[Setup]) -> Setup:
    # Sort by number of included points
    setups.sort(key=lambda s: s.score1, reverse=True)

    # Sort by mean point position in setup
    top = setups[:4]
    top.sort(key=lambda s: abs(0.5 - s.score1))

    return top[0]


class AscTriangle(BaseChart):
    """
    *   *   *
        *
    *
    """
    __name__ = "ascending_triangle"

    def _remake(self, params: dict) -> None:
        up, slope, coef = params.values()
        down = slope * self._time + coef
        up = np.array([up] * down.size)
        self.setup = Setup(up, down, params, 1, 1)
        self._extend()

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

    def _extend(self) -> None:
        hline = self.setup.params['hline']
        slope = self.setup.params['slope']
        coef = self.setup.params['coef']
        extension_up = np.array([hline] * self._future_time.size)
        extension_down = slope * self._future_time + coef

        # till crossing
        i = sum(1 for u, d in zip(extension_up, extension_down) if u >= d)

        self.setup = Setup(
            up=np.concatenate([self.setup.up, extension_up[:i]]),
            down=np.concatenate([self.setup.down, extension_down[:i]]),
            params=self.setup.params,
            score1=self.setup.score1,
            score2=self.setup.score2
        )


class DescTriangle(BaseChart):
    """
    *
        *
    *   *   *
    """
    __name__ = "descending_triangle"

    def _remake(self, params: dict) -> None:
        down, slope, coef = params.values()
        up = slope * self._time + coef
        down = np.array([down] * up.size)
        self.setup = Setup(up, down, params, 1, 1)
        self._extend()

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

    def _extend(self) -> None:
        hline = self.setup.params['hline']
        slope = self.setup.params['slope']
        coef = self.setup.params['coef']
        extension_down = np.array([hline] * self._future_time.size)
        extension_up = slope * self._future_time + coef

        # till crossing
        i = sum(1 for u, d in zip(extension_up, extension_down) if u >= d)

        self.setup = Setup(
            up=np.concatenate([self.setup.up, extension_up[:i]]),
            down=np.concatenate([self.setup.down, extension_down[:i]]),
            params=self.setup.params,
            score1=self.setup.score1,
            score2=self.setup.score2
        )


class SymmetricalTriangle(BaseChart):
    """
    *
        *
            *
        *
    *
    """
    __name__ = "symmetrical_triangle"

    def _remake(self, params: dict) -> None:
        (sup, cup), (sdown, cdown) = params.values()
        up = sup * self._time + cup
        down = sdown * self._time + cdown
        self.setup = Setup(up, down, params, 1, 1)
        self._extend()

    def _make_bands(self, skew_up: Skew, skew_down: Skew) -> Tuple[np.ndarray, np.ndarray]:
        do = lambda s: self._time * s.slope + s.coef
        up = do(skew_up)
        down = do(skew_down)
        return up, down

    @staticmethod
    def _params(up_skew: Skew, down_skew: Skew) -> dict:
        params = {
            'up': (up_skew.slope, up_skew.coef),
            'down': (down_skew.slope, down_skew.coef)
        }
        return params

    def _find(self, ups: List[Skew], downs: List[Skew]) -> Union[Setup, None]:
        setups = []
        for up_skew in ups:
            for down_skew in downs:
                if not self._cross_after_last_candle(up_skew, down_skew):
                    continue
                up, down = self._make_bands(up_skew, down_skew)

                start_index = min(down_skew.start.x, up_skew.start.x)
                score1 = self._include_enough_points(start_index, up, down)
                if not score1:
                    continue
                score2 = self._fits_enough(start_index, up, down)
                if not score2:
                    continue

                params = self._params(up_skew, down_skew)
                setups.append(Setup(up, down, params, score1, score2))

        if not setups:
            return None

        return _select_best_setup(setups)

    def _create_info(self) -> None:
        self.events = [None]
        self.sentiment = "None"
        self.signal = (None, None)
