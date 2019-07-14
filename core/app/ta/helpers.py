import logging
import traceback
import numpy as np
from functools import wraps

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
            except:
                logging.error(f"Indicator {name}, error: /n {traceback.format_exc()}")
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

    lA = np.sqrt(A[0] ** 2 + A[1] ** 2)
    lB = np.sqrt(B[0] ** 2 + B[1] ** 2)
    lC = np.sqrt(C[0] ** 2 + C[1] ** 2)

    d = (lC ** 2 - lA ** 2 - lB ** 2) / (-2 * lA * lB)

    alpha = np.degrees(np.arccos(d))
    return float(alpha)


def nan_to_null(xs: list) -> list:
    return list(map(lambda x: None if np.isnan(x) else x, xs))
