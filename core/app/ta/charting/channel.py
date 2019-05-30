from typing import Union, Tuple
import numpy as np

from app.ta.constructors import Skew
from .base import BaseChart, Setup


class Channel(BaseChart):
    """
             *
        *
    *        *
        *
    *
    """
    __name__ = "channel"

    def _remake(self, params: dict) -> None:
        (slope, coef), shift = params.values()
        band = self._time * slope + coef
        if shift > 0:
            down = band
            up = band + shift
        else:
            down = band + shift
            up = band
        self.setup = Setup(up, down, params, 1, 1, 1)
        self._extend()

    def _extend(self) -> None:
        slope, coef = self.setup.params['band']
        shift = self.setup.params['shift']
        if shift > 0:
            extension_down = slope * self._future_time + coef
            extension_up = extension_down + shift
        else:
            extension_up = slope * self._future_time + coef
            extension_down = extension_up + shift

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

    def _make_bands(self, skew: Skew, shift: float) -> Tuple[np.ndarray, np.ndarray]:
        band = self._time * skew.slope + skew.coef
        shifted_band = band + shift

        # return up, down
        if shift < 0.0:
            return band, shifted_band

        return shifted_band, band

    def _shifts(self, type_: str) -> np.ndarray:
        width = np.max(self._close) - np.min(self._close)
        shifts = np.linspace(0, 0.6 * width, 50)
        if type_ == 'up':
            return -1 * shifts
        return shifts

    @staticmethod
    def _params(skew: Skew, shift: float) -> dict:
        params = {
            'band': (skew.slope, skew.coef),
            'shift': shift,
            'start': float(skew.start.x)
        }
        return params

    def _helper(self, skews: [Skew], type_: str) -> [Setup]:
        setups = []
        for skew in skews:
            for shift in self._shifts(type_):
                up, down = self._make_bands(skew, shift)

                start_index = skew.start.x
                include_score = self._include_enough_points(start_index, up, down)
                if not include_score:
                    continue

                fit_score = self._fits_enough(start_index, up, down)
                if not fit_score:
                    continue

                all_score = self._fits_to_all(up, down)
                params = self._params(skew, shift)
                setups.append(Setup(up, down, params, include_score, fit_score, all_score))
        return setups

    def _find(self, ups: [Skew], downs: [Skew]) -> Union[Setup, None]:
        setups = self._helper(ups, type_='up')
        setups += self._helper(downs, type_='down')

        if not setups:
            return None

        return self._select_best_setup(setups)

    def _create_info(self) -> None:
        self.events = [None]
        self.sentiment = "None"
        self.signal = (None, None)

    @staticmethod
    def _select_best_setup(setups: [Setup]) -> Setup:
        # Sort by number of included points
        setups.sort(key=lambda s: s.all_score, reverse=True)

        # Sort by number of included points since pattern
        top = setups[:8]
        top.sort(key=lambda s: s.include_score, reverse=True)

        # Sort by mean point position in setup
        top = setups[:4]
        top.sort(key=lambda s: abs(0.5 - s.fit_score))

        m = abs(0.5 - top[0].fit_score)
        top = [t for t in top if abs(0.5 - t.fit_score) == m]

        # Select channel with minimal width
        top.sort(key=lambda s: s.params['shift'])

        return top[0]
