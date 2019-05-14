import numpy as np
from collections import namedtuple
from functools import reduce

LevelTuple = namedtuple('LevelTuple', ['type', 'value', 'time', 'strength'])


def is_level(i: int, x: float, xs: np.ndarray, t: int) -> [LevelTuple]:
    """
    Checks if value x is a significant level in series of xs.
    Parameters
    ----------
    i - index of x in xs
    x - price value
    xs - array of price values

    Returns
    -------
    (type, value, strength) or None if x is not a level
    """
    _radius_map = {
        4: 60,
        3: 30,
        2: 20,
        1: 10
    }

    lvls = []

    # For each strength level
    for strength, radius in _radius_map.items():
        if i > xs.size - radius:
            continue
        if i < radius:
            continue
        ys = xs[i - radius: i + radius]
        support = reduce(lambda a, b: a and b, ys >= np.array([x] * ys.size))
        resistance = reduce(lambda a, b: a and b, ys <= np.array([x] * ys.size))
        if support:
            lvl = LevelTuple('support', x, int(t), strength)
            lvls.append(lvl)
        elif resistance:
            lvl = LevelTuple('resistance', x, int(t), strength)
            lvls.append(lvl)

    return lvls
