import logging
import traceback
from functools import wraps

import numpy as np

from app.ta.constructors import Point


def empty(keys: list) -> dict:
    d = {k: [] for k in keys}
    d["info"] = []
    if "name" in keys:
        d["name"] = None

    return d


def indicator(name: str, default: list) -> callable:
    def decorator(func: callable):
        @wraps(func)
        def wraped_function(*args, **kwargs) -> dict:
            try:
                return {name: func(*args, **kwargs)}
            # Broad exception because TA-Lib has low level
            # errors and because there's a lot of magic...
            except:  # pylint:disable=bare-except
                logging.error(
                    "Indicator %s, error: /n %s", name, traceback.format_exc()
                )
                return {name: empty(default)}

        return wraped_function

    return decorator


def angle(a: Point, b: Point, c: Point) -> float:
    """
    Calculates angle between sections AB, BC.

    Returns
    -------
    alpha: the angle in degrees
    """
    A = [a.x - b.x, a.y - b.y]
    B = [c.x - b.x, c.y - b.y]
    C = [c.x - a.x, c.y - a.y]

    length_a = np.sqrt(A[0] ** 2 + A[1] ** 2)
    length_b = np.sqrt(B[0] ** 2 + B[1] ** 2)
    length_c = np.sqrt(C[0] ** 2 + C[1] ** 2)

    d = (length_c ** 2 - length_a ** 2 - length_b ** 2) / (-2 * length_a * length_b)

    return float(np.degrees(np.arccos(d)))


def nan_to_null(xs: list) -> list:
    return [None if np.isnan(x) else x for x in xs]
