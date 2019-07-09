from app.models import Series, Point
from .helpers import add_event


class Atomics:
    def __init__(self, series: Series):
        self._pair = series.pair
        self._timeframe = series.timeframe
        self.points = list(series.values(key="close"))

    def detect_top(self, peak: Point, neighbours):
        if not neighbours:
            return None
        if not all(peak.y >= p.y for p in neighbours):
            return None

        params = {
            'pair' : self._pair,
            'timeframe': self._timeframe,
            'time': int(peak.x),
            'value': float(peak.y),
            'name': 'TOP'
        }
        return add_event(params)

    def detect_bottom(self, peak: Point, neighbours):
        if not neighbours:
            return None
        if not all(peak.y <= p.y for p in neighbours):
            return None

        params = {
            'pair': self._pair,
            'timeframe': self._timeframe,
            'time': int(peak.x),
            'value': float(peak.y),
            'name': 'BOTTOM'
        }
        return add_event(params)

    @staticmethod
    def neighbourhood(i, xs, n, size: int = 10):
        if (i < size) or (i > n - size):
            return xs[i], None

        return xs[i], xs[i - size:i + size]


    def check_peaks(self, close, last=10):
        close = close[-2*last:]
        n = len(close)

        for i, c in enumerate(close):
            ngbr = self.neighbourhood(i, close, n)
            self.detect_top(*ngbr)
            self.detect_bottom(*ngbr)

    def remake(self):
        for i, p in enumerate(self.points):
            self.check_peaks(self.points[:i])
