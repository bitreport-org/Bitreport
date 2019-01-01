import numpy as np
import statsmodels.api as sm
import config
from core.services.dbservice import Level, make_session

from scipy.signal import argrelmin, argrelmax

config = config.BaseConfig()
session = make_session()


class Levels(object):
    def __init__(self, pair, timeframe, close, x_dates):
        self.pair = pair
        self.timeframe = timeframe
        self.close = close
        self.x_dates = x_dates
        self.start = config.MAGIC_LIMIT

    def _sr_levels(self, close, r=5):
        hp_cycle, hp_trend = sm.tsa.filters.hpfilter(close)
        maxs = argrelmax(hp_trend)[0]
        mins = argrelmin(hp_trend)[0]

        resistance, support = [], []
        if maxs != []:
            resistance = [np.max(close[p-r:p+r]) for p in maxs]
        if mins != []:
            support = [np.min(close[p-r:p+r]) for p in mins]

        levels = dict(resistance=resistance, support=support)

        return levels

    def _fib_levels(self, close, top: float, bottom: float):
        top_index, = np.where(close == top)
        bottom_index, = np.where(close == bottom)
        top_index = top_index[-1]
        bottom_index = bottom_index[-1]

        height = top - bottom
        fib_lvls = [0.00, .236, .382, .500, .618, 1.00]

        levels = []
        if top_index < bottom_index:
            for lvl in fib_lvls:
                value = bottom + lvl * height
                levels.append(value)
        else:
            for lvl in fib_lvls:
                value = top - lvl * height
                levels.append(value)

        return levels

    def _save_levels(self, levels):

        for key, items in levels.items():
            if items != []:
                for item in items:
                    lvl = Level(pair=self.pair, timeframe=self.timeframe,
                                type=key, value=item, tsmp=100)
                    session.add(lvl)

        session.commit()

    def make(self):
        start = self.start
        close = self.close[start:]

        # Find levels
        levels = self._sr_levels(close)

        # Check if any levels to make fibs
        r, s = levels.values()
        if r != [] and s != []:
            # Highest resistance and lowest support
            top = np.max(r)
            bottom = np.min(levels['support'])

            # Calculate fib levels
            fib = self._fib_levels(close, top, bottom)

            # Add fibs
            levels.update(fib=fib)

        levels.update(info=[])
        return levels
