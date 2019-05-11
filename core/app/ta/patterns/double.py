import numpy as np
from app.ta.charting.constructors import Point
from app.ta.charting.triangle import Universe


def _angle(a: Point, b: Point, c: Point) -> float:
    """
    Calculates angle between sections AB, BC.

    Returns
    -------
    alpha: the angle in degrees
    """

    A = [a.x - b.x, a.y - b.y]
    B = [c.x - b.x, c.y - c.y]

    lA = np.sqrt(A[0] ** 2 + A[1] ** 2)
    lB = np.sqrt(B[0] ** 2 + B[1] ** 2)

    alpha = np.degrees(np.arccos(np.dot(A, B) / (lA * lB)))
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

    bx = slopes[0][0]
    B = Point(int(bx), float(close[bx]))

    if (B.x - A.x) > 0.3 * close.size:
        return {'info': []}

    # Find the midpoint
    cx = A.x + g(close[A.x: B.x])
    C = Point(int(cx), float(close[cx]))

    # Scale 3 points to [0,1]x[0,1]
    xs = np.array([A.x, B.x, C.x])
    scaled_x = (xs - B.x) / (A.x - B.x)

    ys = np.array([A.y, B.y, C.y])

    if type_ == 'top':
        scaled_y = (ys - B.y) / (A.y - B.y)
    else:
        scaled_y = (ys - A.y) / (B.y - A.y)

    sA, sB, sC = [Point(x, y) for x, y in zip(scaled_x, scaled_y)]
    alpha = _angle(sA, sB, sC)
    if alpha > 95:
        return {'info': [], 'A': (), 'B': (), 'C': ()}

    # Here we change points order from A, C, B to A, B, C
    dt = {k: (int(x_dates[p.x]), p.y) for k, p in zip('ACB', [A, B, C])}

    dt['info'] = []

    return dt
