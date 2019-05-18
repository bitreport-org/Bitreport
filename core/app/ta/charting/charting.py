import numpy as np
from typing import List, Tuple, Union

from app.api.database import Chart
from app.ta.helpers import indicator
from .constructors import tops, bottoms, skews
from .base import Universe, Setup, BaseChart
from .triangles import AscTriangle, DescTriangle, SymmetricalTriangle
from .channel import Channel


class Charting:
    def __init__(self, universe: Universe) -> None:
        self._universe = universe

    @staticmethod
    def select_best(xs: List[BaseChart]) -> Union[BaseChart, None]:
        bests = [x for x in xs if (x and x.setup)]
        bests.sort(key=lambda x: x.setup.score1)
        if bests:
            return bests[-1]
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
            'symmetrical_triangle': SymmetricalTriangle,
            'descending_triangle': DescTriangle
        }

        chart = creataion_map.get(last.type)
        if not chart:
            return None

        chart = chart(self._universe, remake=True, params=last.params)
        if not self.is_actual(chart.setup.up, chart.setup.down):
            return None

        return chart

    @indicator('wedge', ['upper_band', 'lower_band'])
    def __call__(self):
        chart = self.check_last_pattern()
        if chart:
            # TODO: generate actual info
            return chart.json()

        tops_ = tops(self._universe.close, self._universe.time)
        bottoms_ = bottoms(self._universe.close, self._universe.time)
        skews_up = skews(tops_)
        skews_down = skews(bottoms_)

        charts = [
            AscTriangle(universe=self._universe, tops=tops_, skews=skews_down),
            DescTriangle(universe=self._universe, bottoms=bottoms_, skews=skews_up),
            SymmetricalTriangle(universe=self._universe, ups=skews_up, downs=skews_down)
        ]

        best = self.select_best(charts)

        if best and isinstance(best.setup, Setup):
            best.save()
            return best.json()

        # If no triangle, the check if there is channel

        best = Channel(universe=self._universe, ups=skews_up, downs=skews_down)

        if best and isinstance(best.setup, Setup):
            best.save()
            return best.json()

        return dict(upper_band=[],
                    lower_band=[],
                    info=[])
