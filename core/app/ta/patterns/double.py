import numpy as np
from app.ta.charting.constructors import Point
from app.ta.charting.base import Universe


def _angle(a: Point, b: Point, c: Point) -> float:
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


def make_double(universe: Universe,
                type_: str = 'top',
                right_margin: int = 15,
                threshold: int = 3) -> dict:
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
    # TODO: assert that middle point is at least at some height?

    x_dates = universe.time
    close = universe.close
    assert x_dates.size == close.size, f'Double pattern, x, y sizes differ: {x_dates.size}, {close.size}'

    if type_ == 'top':
        f, g, sgn = np.argmax, np.argmin, 1
    else:
        f, g, sgn = np.argmin, np.argmax, 0

    # First top
    x = f(close)
    A = Point(int(x), float(close[x]))

    if A.x > close.size - right_margin:
        return {'info': [], 'A': (), 'B': (), 'C': ()}

    # Scale series from Ax to a square [0,1]x[0,1]
    scaled_y = close[A.x+1:]
    scaled_y = (scaled_y - np.min(scaled_y)) / (np.max(scaled_y) - np.min(scaled_y))

    scaled_x = np.arange(scaled_y.size)
    scaled_x = (scaled_x - np.min(scaled_x)) / (np.max(scaled_x) - np.min(scaled_x))

    scaled_y = scaled_y[threshold:]
    scaled_x = scaled_x[threshold:]

    if scaled_x.size < 1:
        return {'info': [], 'A': (), 'B': (), 'C': ()}

    # Calculate slopes
    slopes = (scaled_y[1:] - sgn) / scaled_x[1:]
    slopes = np.degrees(np.arctan(slopes))

    # Select second top
    tmp = A.x + 1 + np.arange(scaled_y.size)
    slopes = [(x, s) for x, s in zip(tmp[threshold + 1:], slopes) if abs(s) < 20]

    # Select only points that are dist points from A
    if not slopes:
        return {'info': [], 'A': (), 'B': (), 'C': ()}

    slopes.sort(key=lambda x: abs(x[1]))

    cx = slopes[0][0]
    C = Point(int(cx), float(close[cx]))

    if (C.x - A.x) > 0.3 * close.size or C.x - A.x < 10:
        return {'info': [], 'A': (), 'B': (), 'C': ()}

    # Find the midpoint
    bx = A.x + g(close[A.x: C.x])
    B = Point(int(bx), float(close[bx]))

    # Scale 3 points to [0,1]x[0,1]
    xs = np.array([A.x, C.x, B.x])
    scaled_x = (xs - C.x) / (A.x - C.x)

    ys = np.array([A.y, C.y, B.y])

    if type_ == 'top':
        scaled_y = (ys - C.y) / (A.y - C.y)
    else:
        scaled_y = (ys - A.y) / (C.y - A.y)

    scaled_a, scaled_b, scaled_c = [Point(x, y) for x, y in zip(scaled_x, scaled_y)]
    alpha = _angle(scaled_a, scaled_b, scaled_c)
    if alpha > 95:
        return {'info': [], 'A': (), 'B': (), 'C': ()}

    dt = {k: (int(x_dates[p.x]), p.y) for k, p in zip('ABC', [A, B, C])}

    dt['info'] = []

    return dt
