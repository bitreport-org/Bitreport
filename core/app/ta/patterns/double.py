import numpy as np


def _angle(a, b, c):
    ax, ay = a
    bx, by = b
    cx, cy = c
    A = [ax - bx, ay - by]
    B = [cx - bx, cy - cy]

    lA = np.sqrt(A[0] ** 2 + A[1] ** 2)
    lB = np.sqrt(B[0] ** 2 + B[1] ** 2)

    alfa = np.degrees(np.arccos(np.dot(A, B) / (lA * lB)))
    return alfa


def make_double(x_dates, close, type ='top', right_margin=5, threshold=3):
    assert x_dates.size == close.size, f'Double pattern, x, y sizes differ: {x_dates.size}, {close.size}'

    if type == 'top':
        f, g, sgn = np.argmax, np.argmin, 1
    else:
        f, g, sgn = np.argmin, np.argmax, 0

    # First top
    Ax = f(close)
    Ay = close[Ax]

    if Ax > close.size - right_margin:
        return {'info':[]}

    # Scale series from Ax to a square [0,1]x[0,1]
    scaled_y = close[Ax:]
    scaled_y = (scaled_y - np.min(scaled_y)) / (np.max(scaled_y) - np.min(scaled_y))

    scaled_x = np.arange(scaled_y.size)
    scaled_x = (scaled_x - np.min(scaled_x)) / (np.max(scaled_x) - np.min(scaled_x))

    scaled_y = scaled_y[threshold:]
    scaled_x = scaled_x[threshold:]

    if scaled_x.size < 1:
        return {'info':[]}

    # Calculate slopes
    slopes = (scaled_y[1:] - sgn) / scaled_x[1:]
    slopes = np.degrees(np.arctan(slopes))

    # Select second top
    tmp = Ax + np.arange(scaled_y.size)
    slopes = [(x, s) for x, s in zip(tmp[threshold + 1:], slopes) if abs(s) < 20]
    if not slopes:
        return {'info':[]}

    slopes.sort(key=lambda x: x[1])

    Bx = slopes[-1][0]
    By = close[Bx]

    if (Bx - Ax) > 0.3 * close.size:
        return {'info':[]}

    # Find the midpoint
    Cx = Ax + g(close[Ax: Bx])
    Cy = close[Cx]

    # Scale 3 points to [0,1]x[0,1]
    xs = np.array([Ax, Bx, Cx])
    ax, bx, cx = (xs - Bx) / (Ax - Bx)

    ys = np.array([Ay, By, Cy])

    if type == 'top':
        ay, by, cy = (ys - By) / (Ay - By)
    else:
        ay, by, cy = (ys - Ay) / (By - Ay)

    alpha = _angle((ax, ay), (bx, by), (cx, cy))
    if alpha > 95:
        return {}

    Ax = x_dates[Ax]
    Bx = x_dates[Bx]
    Cx = x_dates[Cx]

    # Here we change points order from A, C, B to A, B, C
    dt = {
        'A' : (int(Ax), float(Ay)),
        'B': (int(Cx), float(Cy)),
        'C': (int(Bx), float(By)),
        'info': []
    }

    return dt

