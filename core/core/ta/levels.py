import numpy as np
import pandas as pd
import config

import config
config = config.BaseConfig()

def _srLevels(close, threshold: float = .95, check_number: int = 4, similarity: float = 0.02):
    df = []
    data_size = close.size
    
    # It's a kind of magic, magic!
    for point, level in enumerate(close):
        if not point in [0,data_size-1]:
            support = np.sum(close[point:] >= level)/close[point:].size
            resistance = np.sum(close[:point] < level)/close[:point].size    
            df.append([int(point), level, support, resistance])

    df = pd.DataFrame(df, columns=['position', 'level', 'support', 'resistance'])
    
    # Resistances
    resistance = []
    res = df[df.resistance >= threshold][['position','level']].values
    for row in res:
        index, lvl = row
        index = int(index)
        if index < close.size-check_number:
            if np.sum(close[index:index+check_number] < lvl) >= check_number-1:
                resistance.append(lvl)
    
    # Supports
    support = []
    sup = df[df.support >= threshold][['position','level']].values
    for row in sup:
        index, lvl = row
        index = int(index)
        if index > check_number:
            if np.sum(close[index-check_number:index] > lvl) >= check_number-1:
                support.append(lvl)
    
    # Delete similar levels
    def _sim_delete(levels):
        if levels != []:
            levels = np.array(levels)
            sim_value = levels[1:]/levels[:-1]
            for i in np.where(sim_value <= 1 + similarity):
                levels = np.delete(levels, i)
            return levels.tolist()
        else:
            return []
    
    resistance = _sim_delete(resistance)
    support = _sim_delete(support)

    levels = dict(
                resistance = resistance,
                support = support
                )

    return levels

def _fibLevels(close, top: float, bottom: float):
    top_index, = np.where(close==top)
    bottom_index, = np.where(close==bottom)
    
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
    top = np.max(levels['resistance'])
    bottom = np.min(levels['support'])

    # Calculate fib levels
    fib = _fibLevels(close, top, bottom)

    # Add fibs
    levels.update(fib)

    return levels