from sqlalchemy import desc
import numpy as np

from app.models import Event, Series
from app.ta.helpers import indicator, nan_to_null


def make_line(p: Event, q: Event):
    slope = (p.value - q.value) / (p.time - q.time)
    coef = p.value - slope * p.time

    return lambda time: slope * time + coef


@indicator('wedge', ['name', 'upper_band', 'lower_band', 'middle_band'])
def simple_wedge(series: Series):
    output = {'name': 'wedge', 'upper_band': [],
              'lower_band': [], 'middle_band': [], 'info': []}

    last_tops = Event.query.\
        filter_by(timeframe=series.timeframe,
                  pair=series.pair,
                  name="TOP").\
        order_by(desc(Event.time)).\
        limit(2).all()

    last_bottoms = Event.query.\
        filter_by(timeframe=series.timeframe,
                  pair=series.pair,
                  name="BOTTOM").\
        order_by(desc(Event.time)).\
        limit(2).all()

    if len(last_bottoms) != 2 and len(last_tops) != 2:
        return output


    min_threshold = min(p.time for p in last_tops + last_bottoms)
    xs = np.array([x if x >= min_threshold else np.nan for x in series.time])

    line = make_line(*last_tops)
    output.update(upper_band=nan_to_null(line(xs)))

    line = make_line(*last_bottoms)
    output.update(lower_band=nan_to_null(line(xs)))

    return output


