import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.signal import argrelmin, argrelmax

import config
config = config.BaseConfig()

def _srLevels(close, r=5):
    hp_cycle, hp_trend = sm.tsa.filters.hpfilter(close)
    maxs = argrelmax(hp_trend)[0]
    mins = argrelmin(hp_trend)[0]
    
    resistance = [np.max(close[p-r:p+r]) for p in maxs]
    support = [np.min(close[p-r:p+r]) for p in mins]

    levels = dict(resistance = resistance, support = support)

    return levels

def _fibLevels(close, top: float, bottom: float):
    top_index, = np.where(close==top)
    bottom_index, = np.where(close==bottom)
    top_index = top_index[-1]
    bottom_index = bottom_index[-1]

    height = top - bottom
    fib_lvls = [0.00, .236, .382, .500, .618, 1.00]
    
    levels = dict()
    if top_index < bottom_index:
        for lvl in fib_lvls:
            value = bottom + lvl * height
            lvl_name = 'Fib {0:.1f}%'.format(lvl*100)
            levels[lvl_name] = [value]
    else:
        for lvl in fib_lvls:
            value = top - lvl * height
            lvl_name = 'Fib {}'.format(lvl)
            levels[lvl_name] = [value]
    
    return levels

def prepareLevels(data: dict):
    start = config.MAGIC_LIMIT
    close = data.get('close')[start:]
    
    # Find levels
    levels = _srLevels(close)

    # Highest resistance and lowest support
    r, s  = levels.values()
    if r!=[] and s!=[]:
        top = np.max(r)
        bottom = np.min(levels['support'])

        # Calculate fib levels
        fib = _fibLevels(close, top, bottom)

        # Add fibs
        levels.update(fib)

    return levels