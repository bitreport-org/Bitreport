from functools import reduce

import app.ta.charting.constructors as cts
import app.ta.charting.triangles as ts
import app.ta.charting.triangle as t


class Charting:
    def __init__(self, universe: t.Universe) -> None:
        self._universe = universe

    def __call__(self):
        tops = cts.tops(self._universe.close, self._universe.time)
        bottoms = cts.bottoms(self._universe.close, self._universe.time)
        skews_up = cts.skews(tops)
        skews_down = cts.skews(bottoms)

        asc_triangle = ts.AscTriangle(universe=self._universe,
                                      tops=tops,
                                      skews=skews_down
                                      )

        desc_triangle = ts.DescTriangle(universe=self._universe,
                                        bottoms=bottoms,
                                        skews=skews_up
                                        )

        symm_triangle = ts.SymmetricalTriangle(universe=self._universe,
                                               ups=skews_up,
                                               downs=skews_down)

        charts = [asc_triangle, desc_triangle, symm_triangle]

        # for ch in charts:
        #     if ch:
                # print(ch.setup.score1, ch.setup.score2)

        # TODO: symm triangle is not best when it should be :<

        best = reduce(lambda a, b: t.compare(a, b), charts)

        if best and isinstance(best.setup, t.Setup):
            return best.json()

        return dict(upper_band=[],
                    lower_band=[],
                    info=[])
