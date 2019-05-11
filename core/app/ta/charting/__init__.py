import numpy as np
from functools import reduce

import app.ta.charting.constructors as cts
import app.ta.charting.triangles as ts
import app.ta.charting.triangle as t
from config import BaseConfig


class Charting:
    def __init__(self,
                 pair: str,
                 timeframe: str,
                 close: np.ndarray,
                 time: np.ndarray) -> None:

        if close.size != time.size:
            time = time[:-BaseConfig.MARGIN]

        self._universe = t.Universe(
            pair=pair,
            timeframe=timeframe,
            close=close,
            time=time
        )

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


        charts = [asc_triangle, desc_triangle]
        best = reduce(lambda a,b : t.compare(a,b), charts)

        if best and isinstance(best.setup, t.Setup):
            return best.json()

        return dict(upper_band=[],
                    lower_band=[],
                    info=[])
