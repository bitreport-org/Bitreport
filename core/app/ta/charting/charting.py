from functools import reduce

from .constructors import tops, bottoms, skews
from .triangle import compare, Universe, Setup
from .triangles import AscTriangle, DescTriangle, SymmetricalTriangle


class Charting:
    def __init__(self, universe: Universe) -> None:
        self._universe = universe

    def __call__(self):
        tops_ = tops(self._universe.close, self._universe.time)
        bottoms_ = bottoms(self._universe.close, self._universe.time)
        skews_up = skews(tops_)
        skews_down = skews(bottoms_)

        asc_triangle = AscTriangle(universe=self._universe,
                                   tops=tops_,
                                   skews=skews_down)

        desc_triangle = DescTriangle(universe=self._universe,
                                     bottoms=bottoms_,
                                     skews=skews_up)

        symm_triangle = SymmetricalTriangle(universe=self._universe,
                                            ups=skews_up,
                                            downs=skews_down)

        charts = [asc_triangle, desc_triangle, symm_triangle]

        best = reduce(lambda a, b: compare(a, b), charts)

        if best and isinstance(best.setup, Setup):
            return best.json()

        return dict(upper_band=[],
                    lower_band=[],
                    info=[])
