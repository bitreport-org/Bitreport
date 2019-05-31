import numpy as np
from typing import List, Union

from app.database.models import Chart
from app.ta.helpers import indicator
from app.ta.constructors import tops, bottoms, skews
from .base import Universe, BaseChart, Setup
from .triangles import AscTriangle, DescTriangle, SymmetricalTriangle
from .channel import Channel


class Charting:
    DEFAULT = dict(upper_band=[], lower_band=[], info=[])

    def __init__(self, universe: Universe) -> None:
        self._universe = universe

        # Universe information
        self.max = np.max(self._universe.close)
        self.min = np.min(self._universe.close)
        self.field = (self.max - self.min) * self._universe.close.size

    def _not_empty_pattern(self, setup: Setup) -> Union[float, None]:
        margin = self._universe.close.size
        close, up, down = self._universe.close, setup.up[:margin], setup.down[:margin]
        # Look at this as an integral
        sum_up = up - close
        sum_down = close - down
        sum_up = sum(x for x in sum_up if x >= 0)
        sum_down = sum(x for x in sum_down if x >= 0)
        s = sum_up + sum_down
        condition = s < 0.8 * self.field
        return condition

    def select_best(self, xs: List[BaseChart]) -> Union[BaseChart, None]:
        bests = [x for x in xs if (x and x.setup)
                 if self._not_empty_pattern(x.setup)]

        bests.sort(key=lambda x: x.setup.peaks_fit_value)
        if bests:
            return bests[0]
        return None

    def is_actual(self, up: np.ndarray, down: np.ndarray, threshold: float = 0.6) -> bool:
        close = self._universe.close
        n = sum(1 for c, u, d in zip(close, up, down) if d <= c <= u) / close.size
        return n > threshold

    def check_last_pattern(self) -> Union[BaseChart, None]:
        last = Chart.query.filter_by(
            timeframe=self._universe.timeframe,
            pair=self._universe.pair).\
            order_by(Chart.time.desc()).first()
        if not last:
            return None

        creataion_map = {
            'ascending_triangle': AscTriangle,
            'descending_triangle': DescTriangle,
            'channel': Channel
            # 'symmetrical_triangle': SymmetricalTriangle,
        }

        chart = creataion_map.get(last.type)
        if not chart:
            return None

        chart = chart(self._universe, remake=True, params=last.params)
        if not self.is_actual(chart.setup.up, chart.setup.down):
            return None

        return chart

    @indicator('wedge', ['upper_band', 'lower_band', 'name'])
    def __call__(self):
        chart = self.check_last_pattern()

        if chart:
            # TODO: generate actual info
            return chart.json()

        tops_ = tops(self._universe.close, self._universe.time)
        bottoms_ = bottoms(self._universe.close, self._universe.time)
        skews_up = skews(tops_)
        skews_down = skews(bottoms_)

        peaks = (tops_, bottoms_)

        charts = [
            AscTriangle(universe=self._universe, peaks=peaks, tops=tops_, skews=skews_down),
            DescTriangle(universe=self._universe, peaks=peaks, bottoms=bottoms_, skews=skews_up),
            # SymmetricalTriangle(universe=self._universe, ups=skews_up, downs=skews_down)
        ]

        for c in charts:
            if c.setup:
                print(c.__name__, c.setup.peaks_fit_value)

        best = self.select_best(charts)

        channel = Channel(universe=self._universe, peaks=peaks, ups=skews_up, downs=skews_down)

        # No triangle but channel
        if best is None and channel.setup is not None:
            channel.save()
            return channel.json()

        # No triangle, no channel
        if channel.setup is None:
            return self.DEFAULT

        # Triangle or channel
        if channel.setup is not None:
            score = channel.setup.peaks_fit_value / best.setup.peaks_fit_value
            if score < 0.85:
                best = channel

        best.save()
        return best.json()
