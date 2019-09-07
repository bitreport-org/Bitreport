from collections import namedtuple

import numpy as np
from numpy.random import normal

from app.models.influx import insert_candles
from app.ta.constructors import Point
from config import BaseConfig

Sample = namedtuple("Sample", ["close", "points"])


def make_sample(points: list) -> np.ndarray:
    assert len(points) > 2
    close = np.array([])
    for a, b in zip(points[:-1], points[1:]):
        close = np.concatenate([close, np.linspace(a.y, b.y, int(b.x - a.x))])
    return close


def sample_from_lists(xs: list, ys: list) -> np.ndarray:
    return make_sample([Point(float(x), float(y)) for x, y in zip(xs, ys)])


# ==== TRIANGLES === =#


def asc_triangle() -> Sample:
    xs = [0, 40, 70, 100, 130, 160, 190]
    ys = [60, 0, 100, 30, 100, 60, 100]
    points = [Point(float(x), float(y)) for x, y in zip(xs, ys)]
    return Sample(make_sample(points), points)


def desc_triangle() -> Sample:
    xs = [0, 40, 70, 100, 130, 160, 190]
    ys = [40, 100, 0, 60, 0, 30, 0]
    points = [Point(float(x), float(y)) for x, y in zip(xs, ys)]
    return Sample(make_sample(points), points)


def symm_triangle() -> Sample:
    xs = [0, 40, 70, 100, 130, 160, 190]
    ys = [40, 100, 0, 80, 20, 60, 40]
    points = [Point(float(x), float(y)) for x, y in zip(xs, ys)]
    return Sample(make_sample(points), points)


# ==== PATTERNS === =#


def double_top() -> Sample:
    xs = [0, 40, 80, 100, 120, 160, 200]
    ys = [0, 50, 100, 80, 100, 50, 0]
    points = [Point(float(x), float(y)) for x, y in zip(xs, ys)]
    return Sample(make_sample(points), points)


def double_bottom() -> Sample:
    xs = [0, 40, 80, 100, 120, 160, 200]
    ys = [100, 50, 0, 20, 0, 50, 100]
    points = [Point(float(x), float(y)) for x, y in zip(xs, ys)]
    return Sample(make_sample(points), points)


# ==== CHANNELS === =#


def channel() -> Sample:
    xs = [0, 40, 70, 100, 130, 160, 190]
    ys = [0, 40, 20, 60, 40, 80, 60]
    points = [Point(float(x), float(y)) for x, y in zip(xs, ys)]
    return Sample(make_sample(points), points)


# ==== HELPERS === =#


def prepend_new(s: Sample, ys: np.ndarray) -> Sample:
    d = s.points[-1].x - s.points[-2].x
    points = s.points + [Point((-i - 1) * d, y) for i, y in enumerate(ys)]

    close = np.concatenate([ys, s.close])[: s.close.size]
    points = points[: s.close.size]
    return Sample(close=close, points=points)


def append_new(s: Sample, ys: np.ndarray) -> Sample:
    d = s.points[-1].x - s.points[-2].x
    points = s.points + [Point((i + 1) * d, y) for i, y in enumerate(ys)]
    close = np.concatenate([s.close, ys])[-s.close.size :]
    points = points[-s.close.size :]
    return Sample(close=close, points=points)


def break_up(s: Sample) -> Sample:
    last = s.close[-1]
    growth = [1.02] * 12 + [0.99] * 7 + [1.02] * 8
    growth = np.cumproduct(growth)
    ys = growth * last
    return append_new(s, ys)


def break_down(s: Sample) -> Sample:
    last = float(s.close[-1])
    if last == 0.0:
        last = -10
    ys = [last * (1 - i * 0.1) for i in range(30)]
    ys = ys + ys[-10:][::-1]
    return append_new(s, ys[::-1])


def start_slope_down(s: Sample) -> Sample:
    last = float(s.close[0])
    ys = [last * (1 + i * 0.1) for i in range(30)]
    ys = ys + ys[-10:][::-1]
    return prepend_new(s, ys[::-1])


def start_slope_up(s: Sample) -> Sample:
    last = float(s.close[0])
    ys = [last * (1 - i * 0.1) for i in range(30)]
    ys = ys + ys[-10:][::-1]
    return prepend_new(s, ys[::-1])


def _sample_dict(measurement: str, i: int, x: float) -> dict:
    timestamp = 1550207200
    noise = lambda: float(normal(0, 5))
    json_body = {
        "measurement": "TEST" + measurement.upper() + "BTC1h",
        "tags": {"exchange": "bitfinex"},
        "time": timestamp + (i * 3600),
        "fields": {
            "open": float(x) + noise(),
            "close": float(x),
            "high": float(x) + noise(),
            "low": float(x) + noise(),
            "volume": float(x) + noise(),
        },
    }
    return json_body


def save_sample(sample: Sample, name: str) -> bool:
    margin = np.array([sample.close[0]] * BaseConfig.MAGIC_LIMIT)
    points = np.concatenate([margin, sample.close])
    points = [_sample_dict(name, i, x) for i, x in enumerate(points)]
    return insert_candles(points, "s")


def init_samples() -> None:
    samples = [
        ("asc", asc_triangle()),
        ("ascbreak", break_up(asc_triangle())),
        ("ascslopedown", start_slope_down(asc_triangle())),
        ("ascslopeup", start_slope_up(asc_triangle())),
        ("desc", desc_triangle()),
        ("descbreak", break_down(desc_triangle())),
        ("descslopedown", start_slope_down(desc_triangle())),
        ("descslopeup", start_slope_up(desc_triangle())),
        ("symm", symm_triangle()),
        ("dt", double_top()),
        ("db", double_bottom()),
        ("chan", channel()),
    ]

    for name, sample in samples:
        save_sample(sample, name)
