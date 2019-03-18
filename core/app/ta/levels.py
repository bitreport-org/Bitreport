import numpy as np
import statsmodels.api as sm
from scipy.signal import argrelmin, argrelmax

import config
from app.api.database import Level
from app.api import db


class Levels(object):
    def __init__(self, pair: str, timeframe: str, close: np.ndarray, x_dates: np.ndarray):
        self.pair = pair
        self.timeframe = timeframe
        self.close = close
        self.x_dates = x_dates
        self.start = config.BaseConfig.MAGIC_LIMIT

    @staticmethod
    def _sr_levels(close: np.ndarray, r: int=5) -> dict:
        hp_cycle, hp_trend = sm.tsa.filters.hpfilter(close)
        maxs = argrelmax(hp_trend)[0]
        mins = argrelmin(hp_trend)[0]

        resistance, support = [], []
        if np.any(maxs):
            resistance = [np.max(close[p-r:p+r]) for p in maxs]
        if np.any(mins):
            support = [np.min(close[p-r:p+r]) for p in mins]

        levels = dict(resistance=resistance, support=support)

        return levels

    @staticmethod
    def _fib_levels(close: np.ndarray, top: float, bottom: float) -> list:
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

    def _save_levels(self, levels: dict):
        for key, items in levels.items():
            for item in items:
                lvl = Level(pair=self.pair, timeframe=self.timeframe,
                            type=key, value=item)
                db.session.add(lvl)

        db.session.commit()

    def make(self) -> dict:
        start = self.start
        close = self.close[start:]

        # Find levels
        levels = self._sr_levels(close)

        # Check if any levels to make fibs
        resistances, supports = levels.values()
        if resistances and supports:
            # Highest resistance and lowest support
            top = np.max(resistances)
            bottom = np.min(supports)

            # Calculate fib levels
            fib = self._fib_levels(close, top, bottom)

            # Add fibs
            levels.update(fib=fib)

        levels.update(info=[])
        return levels
