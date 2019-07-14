import numpy as np

from app.ta.helpers import indicator, angle
from app.ta.constructors import Point
from app.ta.charting.base import Universe


@indicator("double_top", ["A", "B", "C"])
def double_top(universe):
    return make_double(universe, type_="top")


@indicator("double_bottom", ["A", "B", "C"])
def double_bottom(universe):
    return make_double(universe, type_="bottom")


@indicator("double_top", ["A", "B", "C"])
def double_top(universe):
    return make_double(universe, type_="top")


@indicator("double_bottom", ["A", "B", "C"])
def double_bottom(universe):
    return make_double(universe, type_="bottom")


def make_double(
    universe: Universe, type_: str = "top", right_margin: int = 15, threshold: int = 3
) -> dict:
    """
    Check if a patter of double top or double bottom can be found in given data

    Parameters
    ----------
    universe: Universe object
    type_: the type of patter to look for, top or bottom
    right_margin: number of last points excluded from search
    threshold: minimal distance between peaks

    Returns
    -------
    dt: dictionary with params A, B, C which represents the following points in the pattern
    """
    DEAFULT = {"info": [], "A": (), "B": (), "C": ()}

    x_dates = universe.time
    close = universe.close
    assert (
        x_dates.size == close.size
    ), f"Double pattern, x, y sizes differ: {x_dates.size}, {close.size}"

    if type_ == "top":
        f, g, sgn = np.argmax, np.argmin, 1
    else:
        f, g, sgn = np.argmin, np.argmax, 0

    # First top
    x = f(close)
    A = Point(int(x), float(close[x]))

    if A.x > close.size - right_margin:
        return DEAFULT

    # Scale series from Ax to a square [0,1]x[0,1]
    scaled_y = close[A.x + 1 :]
    scaled_y = (scaled_y - np.min(scaled_y)) / (np.max(scaled_y) - np.min(scaled_y))

    scaled_x = np.arange(scaled_y.size)
    scaled_x = (scaled_x - np.min(scaled_x)) / (np.max(scaled_x) - np.min(scaled_x))

    scaled_y = scaled_y[threshold:]
    scaled_x = scaled_x[threshold:]

    if scaled_x.size < 1:
        return DEAFULT

    # Calculate slopes
    slopes = (scaled_y[1:] - sgn) / scaled_x[1:]
    slopes = np.degrees(np.arctan(slopes))

    # Select second top
    tmp = A.x + 1 + np.arange(scaled_y.size)
    slopes = [(x, s) for x, s in zip(tmp[threshold + 1 :], slopes) if abs(s) < 2]

    # Select only points that are dist points from A
    if not slopes:
        return DEAFULT

    slopes.sort(key=lambda x: abs(x[1]))

    cx = slopes[0][0]
    C = Point(int(cx), float(close[cx]))

    if (C.x - A.x) > 0.3 * close.size or C.x - A.x < 10:
        return DEAFULT

    # Find the midpoint
    bx = A.x + g(close[A.x : C.x])
    B = Point(int(bx), float(close[bx]))

    # Assert that the pattern is not flat
    h1, h2 = abs(A.y / B.y - 1), abs(C.y / B.y - 1)
    if h1 < 0.02 or h2 < 0.02:
        return DEAFULT

    # Scale 3 points to [0,1]x[0,1]
    xs = np.array([A.x, B.x, C.x])
    ys = np.array([A.y, B.y, C.y])

    scaled_x = (xs - A.x) / (C.x - A.x)

    if type_ == "top":
        scaled_y = (ys - B.y) / (A.y - B.y)
    else:
        scaled_y = (ys - A.y) / (B.y - A.y)

    # The rocket must be pointy!
    scaled_a, scaled_b, scaled_c = [Point(x, y) for x, y in zip(scaled_x, scaled_y)]
    alpha = angle(scaled_a, scaled_b, scaled_c)
    if alpha > 95:
        return DEAFULT

    dt = {k: (int(x_dates[p.x]), p.y) for k, p in zip("ABC", [A, B, C])}

    dt["info"] = []

    return dt
